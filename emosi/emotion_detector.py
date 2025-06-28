import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import json
import re
from tqdm import tqdm
import os
import streamlit as st

hf_token = st.secrets["HF_TOKEN"]
MODEL_REPO = st.secrets["MODEL_REPO"]

tokenizer = AutoTokenizer.from_pretrained(MODEL_REPO, token=hf_token)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_REPO, token=hf_token)



label_map = {i: label for i, label in enumerate([
    "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion", "curiosity",
    "desire", "disappointment", "disapproval", "disgust", "embarrassment", "excitement", "fear",
    "gratitude", "grief", "joy", "love", "nervousness", "optimism", "pride", "realization",
    "relief", "remorse", "sadness", "surprise", "neutral"
])}

def detect_emotion(json_path: str):
    # Ekstrak video_id dari nama file JSON
    video_id_match = re.search(r'comments_(\d+)\.json', json_path)
    video_id = video_id_match.group(1) if video_id_match else "unknown"

    # Load file JSON
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    # Gabungkan komentar utama dan reply
    records = []
    for c in data["comments"]:
        records.append({
            "comment_id": c["comment_id"],
            "comment": c["comment"],
            "create_time": c["create_time"],
            "is_reply": False,
            "username": c["username"],
            "like_count": c.get("like_count", 0)
        })
        for r in c.get("replies", []):
            records.append({
                "comment_id": r["comment_id"],
                "comment": r["comment"],
                "create_time": r["create_time"],
                "is_reply": True,
                "username": r["username"],
                "like_count": r.get("like_count", 0)
            })

    df = pd.DataFrame(records)

    # Deteksi emosi untuk tiap komentar
    predictions = []
    for text in tqdm(df["comment"], desc="🧠 Mendeteksi emosi"):
        inputs = tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = model(**inputs)
        pred = torch.argmax(outputs.logits, dim=1).item()
        predictions.append(label_map[pred])

    # Gabungkan hasil emosi
    df["emotion"] = predictions
    df["create_time"] = pd.to_datetime(df["create_time"])

    # Simpan ke CSV
    output_csv = f"emosi/output/comments_with_emotion_{video_id}.csv"
    df.to_csv(output_csv, index=False)

    return df, video_id
