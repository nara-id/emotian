import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from collections import Counter
from pathlib import Path
from wordcloud import WordCloud
import seaborn as sns

# Pastikan create_time sudah dalam format datetime
# Jika belum, jalankan baris ini di dalam fungsi atau sebelumnya:
# df['create_time'] = pd.to_datetime(df['create_time'], unit='s') 
# (Asumsi create_time adalah Unix timestamp)

SENTIMENT_MAP = {
    "admiration": "positive", "amusement": "positive", "approval": "positive", "caring": "positive",
    "curiosity": "positive", "desire": "positive", "excitement": "positive", "gratitude": "positive",
    "joy": "positive", "love": "positive", "optimism": "positive", "pride": "positive",
    "relief": "positive", "surprise": "positive",
    "anger": "negative", "annoyance": "negative", "confusion": "negative", "disappointment": "negative",
    "disapproval": "negative", "disgust": "negative", "embarrassment": "negative", "fear": "negative",
    "grief": "negative", "nervousness": "negative", "remorse": "negative", "sadness": "negative",
    "realization": "neutral", "neutral": "neutral"
}

def generate_charts(df: pd.DataFrame, video_id: str):
    output_dir = Path("emosi/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    df["sentiment"] = df["emotion"].map(SENTIMENT_MAP)
    # Pastikan tipe data datetime jika belum
    if not pd.api.types.is_datetime64_any_dtype(df['create_time']):
        df['create_time'] = pd.to_datetime(df['create_time'], unit='s')


    # ==============================================================================
    # 🎨 PENGATURAN GAYA & WARNA MODERN SECARA GLOBAL 🎨
    # ==============================================================================
    plt.style.use('seaborn-v0_8-whitegrid')
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['font.sans-serif'] = ['Inter', 'Arial', 'Helvetica'] # Menggunakan font Inter jika ada
    mpl.rcParams['figure.facecolor'] = '#F8F9FA'
    mpl.rcParams['axes.facecolor'] = '#FFFFFF'
    mpl.rcParams['axes.edgecolor'] = '#dee2e6'
    mpl.rcParams['axes.labelcolor'] = '#495057'
    mpl.rcParams['xtick.color'] = '#495057'
    mpl.rcParams['ytick.color'] = '#495057'
    mpl.rcParams['text.color'] = '#212529'
    mpl.rcParams['axes.titlepad'] = 20
    mpl.rcParams['axes.titlesize'] = 16
    mpl.rcParams['axes.titleweight'] = 'bold'

    # Definisikan Palet Warna
    PRIMARY_COLOR = "#007BFF"
    SENTIMENT_COLORS = {"positive": "#28a745", "negative": "#dc3545", "neutral": "#6c757d"}
    # Palet warna kategorikal yang lebih lembut dari Seaborn
    CATEGORICAL_PALETTE = sns.color_palette("viridis", 28)


    # --- Fungsi Bantuan untuk Menghilangkan Bingkai Atas & Kanan ---
    def clean_spines(ax):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#ced4da')
        ax.spines['bottom'].set_color('#ced4da')

    # 🔹 1. Bar Chart: Distribusi 28 Emosi (Desain Baru)
    plt.figure(figsize=(12, 7))
    emotion_counts = df["emotion"].value_counts()
    ax = sns.barplot(x=emotion_counts.index, y=emotion_counts.values, palette=CATEGORICAL_PALETTE, width=0.8)
    ax.set_title("Distribusi Emosi dalam Komentar")
    ax.set_xlabel("Tipe Emosi", fontsize=12)
    ax.set_ylabel("Jumlah Komentar", fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    clean_spines(ax)
    plt.tight_layout()
    plt.savefig(output_dir / f"bar_emotion_{video_id}.png", dpi=120)
    plt.close()

    # 🔸 2. Donut Chart: Distribusi Sentimen (Alternatif Modern untuk Pie Chart)
    sentiment_counts = df["sentiment"].value_counts()
    ordered_labels = ["positive", "negative", "neutral"]
    ordered_counts = [sentiment_counts.get(label, 0) for label in ordered_labels]
    ordered_colors = [SENTIMENT_COLORS[label] for label in ordered_labels]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(ordered_counts, labels=ordered_labels, autopct="%1.1f%%", colors=ordered_colors, 
           startangle=90, wedgeprops=dict(width=0.4, edgecolor='w'))
    ax.set_title("Proporsi Sentimen Komentar")
    p = plt.gcf()
    p.gca().add_artist(plt.Circle((0, 0), 0.2, color='#F8F9FA')) # Lingkaran tengah
    plt.tight_layout()
    plt.savefig(output_dir / f"pie_emotion_{video_id}.png", dpi=120)
    plt.close()

    # ☁️ 3. WordCloud dengan Colormap Modern
    text = " ".join(df["comment"].astype(str))
    wordcloud = WordCloud(width=800, height=400, background_color="#F8F9FA", 
                          colormap='viridis', max_words=150).generate(text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_dir / f"wordcloud_{video_id}.png", dpi=120)
    plt.close()

    # 📈 4. Time Series Komentar (Desain Baru)
    df["hour"] = df["create_time"].dt.floor("H")
    time_series = df.groupby("hour").size()

    plt.figure(figsize=(12, 5))
    ax = sns.lineplot(data=time_series, marker='o', color=PRIMARY_COLOR, markersize=5)
    ax.set_title("Aktivitas Komentar per Jam")
    ax.set_xlabel("Waktu", fontsize=12)
    ax.set_ylabel("Jumlah Komentar", fontsize=12)
    plt.fill_between(time_series.index, time_series.values, color=PRIMARY_COLOR, alpha=0.1)
    clean_spines(ax)
    plt.xticks(rotation=15, ha="right")
    plt.grid(axis='x', linestyle='--', alpha=0.0) # Sembunyikan grid vertikal
    plt.tight_layout()
    plt.savefig(output_dir / f"time_series_{video_id}.png", dpi=120)
    plt.close()

    # 📊 5. Stacked Bar: Emosi per 3 Jam (Desain Baru)
    df["hour_3h"] = df["create_time"].dt.floor("3H").dt.strftime('%d %b, %H:%M')
    pivot = df.pivot_table(index="hour_3h", columns="sentiment", aggfunc="size", fill_value=0)
    pivot = pivot[ordered_labels] # urutkan kolom

    ax = pivot.plot(kind="bar", stacked=True, figsize=(12, 6), 
                    color=[SENTIMENT_COLORS[col] for col in pivot.columns], width=0.8)
    ax.set_title("Dinamika Sentimen dari Waktu ke Waktu")
    ax.set_xlabel("Interval Waktu (3 Jam)", fontsize=12)
    ax.set_ylabel("Jumlah Komentar", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    ax.legend(title="Sentimen")
    clean_spines(ax)
    plt.tight_layout()
    plt.savefig(output_dir / f"stacked_emotion_by_hour_{video_id}.png", dpi=120)
    plt.close()

    # 👤 6. Top Komentator (Desain Baru)
    top_users = df["username"].value_counts().head(10)
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=top_users.values, y=top_users.index, color=PRIMARY_COLOR, orient='h')
    ax.set_title("Top 10 Komentator Paling Aktif")
    ax.set_xlabel("Total Komentar", fontsize=12)
    ax.set_ylabel("Nama Pengguna", fontsize=12)
    # Tambahkan label angka di ujung bar
    for container in ax.containers:
        ax.bar_label(container, padding=3, fontsize=10)
    clean_spines(ax)
    plt.tight_layout()
    plt.savefig(output_dir / f"top_commenters_{video_id}.png", dpi=120)
    plt.close()

    # 💬 7. Distribusi Panjang Komentar (Desain Baru)
    df["char_count"] = df["comment"].str.len()
    plt.figure(figsize=(10, 5))
    ax = sns.histplot(df["char_count"], bins=30, color=PRIMARY_COLOR, kde=True)
    ax.set_title("Distribusi Panjang Komentar (berdasarkan Karakter)")
    ax.set_xlabel("Jumlah Karakter per Komentar", fontsize=12)
    ax.set_ylabel("Frekuensi", fontsize=12)
    clean_spines(ax)
    plt.tight_layout()
    plt.savefig(output_dir / f"hist_char_count_{video_id}.png", dpi=120)
    plt.close()
    
    # 📚 8. Perbandingan Emosi Komentar vs Balasan (Desain Baru)
    comparison = df.groupby(["is_reply", "sentiment"]).size().unstack(fill_value=0)
    comparison = comparison[ordered_labels]
    
    ax = comparison.plot(kind="bar", figsize=(8, 6), 
                         color=[SENTIMENT_COLORS[col] for col in comparison.columns])
    ax.set_title("Perbandingan Sentimen: Komentar Utama vs. Balasan")
    ax.set_xlabel("Tipe Interaksi", fontsize=12)
    ax.set_ylabel("Jumlah", fontsize=12)
    plt.xticks(ticks=[0, 1], labels=["Komentar Utama", "Balasan"], rotation=0)
    ax.legend(title="Sentimen")
    clean_spines(ax)
    plt.tight_layout()
    plt.savefig(output_dir / f"comment_vs_reply_{video_id}.png", dpi=120)
    plt.close()