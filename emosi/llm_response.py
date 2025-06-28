import openai
import json
from pathlib import Path
import streamlit as st

# === Load API Key dan Base URL dari secrets ===
api_key = st.secrets["OPENROUTER_API_KEY"]
openai.api_key = api_key
openai.api_base = "https://openrouter.ai/api/v1"

def generate_llm_insight(prompt_path: str) -> dict:
    """
    Kirim prompt ke Mistral LLM via OpenRouter dan kembalikan insight dalam bentuk dict.
    """
    video_id = Path(prompt_path).stem.replace("prompt_", "")

    with open(prompt_path, encoding="utf-8") as f:
        prompt = f.read()

    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "system", "content": "Kamu adalah analis media sosial profesional."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        content = response["choices"][0]["message"]["content"]
    except Exception as e:
        return {"error": f"Gagal menghubungi model: {e}"}

    # Simpan hasil mentah
    output_txt = Path("emosi/output") / f"llm_insight_{video_id}.txt"
    output_txt.parent.mkdir(parents=True, exist_ok=True)
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(content)

    # Parsing JSON → dict (fallback jika bukan JSON)
    try:
        insight_dict = json.loads(content)
    except json.JSONDecodeError:
        insight_dict = {"insight": content}

    return insight_dict
