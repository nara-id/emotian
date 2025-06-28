from fpdf import FPDF
import pandas as pd
from pathlib import Path

# Fungsi untuk filter teks agar aman untuk PDF (hapus emoji dan karakter non-Latin-1)
def safe_text(text: str) -> str:
    return text.encode("latin-1", "ignore").decode("latin-1")

def generate_pdf(caption: str, insight_dict: dict, video_id: str):
    base_path = Path("emosi/output")

    # File paths
    csv_path = base_path / f"comments_with_emotion_{video_id}.csv"
    out_pdf = base_path / f"laporan_emosi_tiktok_{video_id}.pdf"

    # Gambar visualisasi + id tag untuk ambil narasi dari LLM
    visual_files = [
        ("Distribusi 28 Emosi", "bar_emotion", base_path / f"bar_emotion_{video_id}.png"),
        ("Distribusi Sentimen", "pie_emotion", base_path / f"pie_emotion_{video_id}.png"),
        ("WordCloud dari Komentar", "wordcloud", base_path / f"wordcloud_{video_id}.png"),
        ("Jumlah Komentar vs Waktu", "time_series", base_path / f"time_series_{video_id}.png"),
        ("Distribusi Emosi Berdasarkan Waktu", "stacked_emotion_by_hour", base_path / f"stacked_emotion_by_hour_{video_id}.png"),
        ("Top Komentator (Paling Aktif)", "top_commenters", base_path / f"top_commenters_{video_id}.png"),
        ("Distribusi Panjang Komentar", "hist_char_count", base_path / f"hist_char_count_{video_id}.png"),
        ("Perbandingan Emosi Komentar vs Balasan", "comment_vs_reply", base_path / f"comment_vs_reply_{video_id}.png"),
    ]

    # Load CSV
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV tidak ditemukan: {csv_path}")
    df = pd.read_csv(csv_path)

    # Inisialisasi PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Judul
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Laporan Analisis Komentar TikTok", ln=True, align='C')
    pdf.ln(8)

    # Caption Video
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Caption Video:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, safe_text(caption))
    pdf.ln(5)

    # Statistik Dasar
    num_comments = len(df)
    num_replies = df["is_reply"].sum() if "is_reply" in df.columns else 0

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Statistik Komentar:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.cell(0, 8, f"Jumlah Komentar: {num_comments}", ln=True)
    pdf.cell(0, 8, f"Jumlah Balasan: {num_replies}", ln=True)
    pdf.ln(5)

    # Tambahkan visualisasi + penjelasan dari insight_dict
    for title, key, img_path in visual_files:
        if img_path.exists():
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, safe_text(title), ln=True)
            try:
                pdf.image(str(img_path.resolve()), x=15, w=180)
            except RuntimeError:
                pdf.set_font("Arial", size=11)
                pdf.cell(0, 10, "(Gagal menampilkan gambar)", ln=True)

            # Tambahkan narasi LLM jika tersedia
            explanation = insight_dict.get(key, "").strip()
            if explanation:
                pdf.set_font("Arial", size=11)
                pdf.multi_cell(0, 8, safe_text(explanation))
            else:
                pdf.set_font("Arial", size=11)
                pdf.multi_cell(0, 8, "(Narasi tidak tersedia)")
            pdf.ln(10)
        else:
            pdf.set_font("Arial", size=11)
            pdf.cell(0, 10, f"(Gambar tidak tersedia: {title})", ln=True)

    # Insight Umum dari LLM
    general = insight_dict.get("insight", "").strip()
    if general:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Insight Keseluruhan:", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 8, safe_text(general))

    # Simpan PDF
    pdf.output(str(out_pdf))
