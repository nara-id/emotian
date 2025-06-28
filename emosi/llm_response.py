import os
import json
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI  # versi baru OpenAI SDK

# === Load API Key ===
load_dotenv("emosi/API_Keys.env")
api_key = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

def generate_llm_insight(prompt_path: str) -> dict:
    """
    Mengirim prompt ke LLM dan mengembalikan hasil narasi per grafik + insight dalam bentuk dict.
    """
    video_id = Path(prompt_path).stem.replace("prompt_", "")

    with open(prompt_path, encoding="utf-8") as f:
        prompt = f.read()

    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=[
            {"role": "system", "content": "Kamu adalah analis media sosial profesional."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )

    content = response.choices[0].message.content

    # Simpan hasil mentah
    output_txt = Path("emosi/output") / f"llm_insight_{video_id}.txt"
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(content)

    # Parsing hasil JSON dari string → dict
    try:
        insight_dict = json.loads(content)
    except json.JSONDecodeError:
        insight_dict = {"insight": content}

    return insight_dict
