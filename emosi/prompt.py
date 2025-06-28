import json
import pandas as pd
import re
from pathlib import Path

def generate_prompt_file(json_path: str) -> Path:
    base_output = Path("emosi/output")

    # Ekstrak video_id dari nama file JSON
    match = re.search(r"comments_(\d+)\.json", json_path)
    if not match:
        raise ValueError(f"Gagal mengekstrak video_id dari path: {json_path}")
    video_id = match.group(1)

    # Load JSON
    json_file = Path(json_path)
    if not json_file.exists():
        raise FileNotFoundError(f"File komentar tidak ditemukan: {json_path}")

    with open(json_file, encoding="utf-8") as f:
        raw_data = json.load(f)

    caption = raw_data.get("caption", "Konten tanpa deskripsi")
    comments = raw_data.get("comments", [])

    # Load CSV emosi
    csv_path = base_output / f"comments_with_emotion_{video_id}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"File hasil emosi tidak ditemukan: {csv_path}")
    df = pd.read_csv(csv_path)

    # Distribusi emosi
    emotion_dist = df["emotion"].value_counts(normalize=True) * 100
    emotion_stats = "\n".join([f"- {emo}: {round(percent, 2)}%" for emo, percent in emotion_dist.items()])

    # Contoh komentar
    sample_comments = "\n".join([f"- {row['comment']}" for _, row in df.sample(n=min(5, len(df))).iterrows()])

    # PROMPT BARU (struktur JSON-like untuk hasil yang bisa diparse)
    prompt_text = f"""
Analisis komentar TikTok berikut ini berdasarkan caption dan hasil emosi.

📌 Caption Video:
{caption}

📊 Distribusi Emosi (%):
{emotion_stats}

💬 Contoh Komentar:
{sample_comments}

Berikan penjelasan dalam bentuk JSON dengan struktur seperti ini:
{{
  "bar_emotion": "Narasi untuk grafik distribusi 28 emosi",
  "pie_emotion": "Narasi untuk pie chart sentimen",
  "wordcloud": "Narasi untuk WordCloud komentar",
  "time_series": "Narasi untuk time series komentar",
  "stacked_emotion_by_hour": "Narasi untuk stacked emosi berdasarkan waktu",
  "top_commenters": "Narasi untuk top komentator",
  "hist_char_count": "Narasi untuk panjang komentar",
  "comment_vs_reply": "Narasi untuk emosi komentar vs balasan",
  "insight": "Kesimpulan umum tentang suasana komentar dan rekomendasi ke depan"
}}

Tuliskan dalam bahasa Indonesia yang singkat, jelas, mudah dimengerti orang awam dan human-friendly.
""".strip()

    prompt_path = base_output / f"prompt_{video_id}.txt"
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt_text)

    print(f"[✅ PROMPT GENERATED] → {prompt_path.name}")
    return prompt_path
