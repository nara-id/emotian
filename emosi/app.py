import streamlit as st
import os  # Diperlukan untuk path file yang robust
import json
import re
from tiktok_comment_scrapper.scraper import scrape_tiktok_comments
from emotion_detector import detect_emotion
from llm_response import generate_llm_insight
from generate_report import generate_pdf
from plot_emotion import generate_charts
from prompt import generate_prompt_file

# --- Konfigurasi Halaman & CSS ---
st.set_page_config(page_title="Analisis Emosi TikTok", layout="wide", initial_sidebar_state="expanded")

def load_css(file_name):
    """
    Fungsi untuk memuat file CSS kustom.
    Ini menggunakan path absolut untuk memastikan file selalu ditemukan,
    tidak peduli dari mana skrip dijalankan. Ini adalah perbaikan untuk error FileNotFoundError.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(current_dir, file_name)
    
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        st.error(f"Peringatan: File '{file_name}' tidak ditemukan di direktori yang sama dengan app.py.")

# Memanggil fungsi untuk memuat CSS
load_css("style.css")

# --- Sidebar untuk Input ---
with st.sidebar:
    # Ganti URL gambar ini jika Anda punya logo sendiri
    st.image(os.path.join("emosi", "emosi.png"), width=210)
    st.header("⚙️ Kontrol Analisis")
    video_url = st.text_input("🔗 Masukkan URL video TikTok:", placeholder="https://www.tiktok.com/@user/video/123...")
    process_button = st.button("🔍 Analisis Sekarang", use_container_width=True)

# --- Judul Utama ---
st.title("🎭 Analisis Emosi Komentar TikTok")
st.markdown("Selamat datang! Masukkan URL video TikTok di sidebar untuk memulai analisis emosi dan mendapatkan insight percakapan.")
st.markdown("---")

# --- Logika Proses (dipicu oleh tombol di sidebar) ---
if process_button:
    if not video_url or not video_url.startswith("https://"):
        st.warning("Harap masukkan URL video TikTok yang valid terlebih dahulu.")
    else:
        try:
            # Membersihkan session state sebelumnya agar analisis baru tidak tercampur
            for key in list(st.session_state.keys()):
                if key not in ['video_url']:
                    del st.session_state[key]
            
            with st.spinner("🔄 Mengambil komentar dari video..."):
                json_path = scrape_tiktok_comments(video_url)
                match = re.search(r"comments_(\d+)\.json", json_path)
                video_id = match.group(1) if match else "unknown"

                with open(json_path, encoding="utf-8") as f:
                    data = json.load(f)
                caption = data.get("caption", "-")
                st.session_state.update({
                    "caption": caption,
                    "video_id": video_id,
                    "json_path": json_path
                })

            with st.spinner("🧠 Mendeteksi emosi di setiap komentar..."):
                df, video_id = detect_emotion(st.session_state["json_path"])
                generate_charts(df, video_id)
                st.session_state["df"] = df

            with st.spinner("📡 Menganalisis narasi dengan LLM..."):
                prompt_path = generate_prompt_file(st.session_state["json_path"])
                insight_dict = generate_llm_insight(prompt_path)
                st.session_state["insight"] = insight_dict

            st.toast("✅ Analisis berhasil diselesaikan!", icon="🎉")
            # st.balloons() # Efek tambahan yang menyenangkan, bisa diaktifkan jika suka
        except Exception as e:
            st.error(f"Terjadi kesalahan selama proses: {e}")
            st.error("Pastikan URL TikTok valid, koneksi internet stabil, dan coba lagi.")

# --- Tampilan Output (hanya ditampilkan jika analisis selesai) ---
if "df" in st.session_state:
    df = st.session_state["df"]
    caption = st.session_state["caption"]
    insight = st.session_state["insight"]
    video_id = st.session_state["video_id"]
    
    tab1, tab2, tab3 = st.tabs(["📊 Ringkasan", "📈 Visualisasi Detail", "📄 Data & Laporan"])

    with tab1:
        st.header("🎬 Caption Video")
        st.info(caption)

        st.header("✨ Statistik Utama")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-card-title">💬 Jumlah Komentar Ditemukan</div>
                    <div class="metric-card-value">{len(df)}</div>
                </div>
                """, unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-card-title">🔁 Jumlah Balasan (Replies)</div>
                    <div class="metric-card-value">{df["is_reply"].sum()}</div>
                </div>
                """, unsafe_allow_html=True
            )
        
        st.header("💡 Insight Umum dari LLM")
        st.text_area(
            "Ringkasan Insight", 
            value=insight.get("insight", "Insight tidak dapat dibuat."), 
            height=250,
            key="insight_textarea"
        )
        
        st.header("❤️ Komentar Paling Populer")
        with st.expander("Tampilkan 10 komentar dengan 'Like' terbanyak"):
            top_comments = df.sort_values("like_count", ascending=False).head(10)
            st.dataframe(top_comments[["comment", "like_count", "emotion"]], height=350, use_container_width=True)

    with tab2:
        st.header("📊 Visualisasi Analisis Emosi")
        st.markdown("Klik pada setiap judul di bawah ini untuk melihat grafik visualisasi beserta narasinya.")

        visual_map = [
            ("bar_emotion", "Distribusi 28 Emosi", "bar_emotion"),
            ("pie_emotion", "Distribusi Sentimen Positif, Negatif, Netral", "pie_emotion"),
            ("wordcloud", "WordCloud dari Komentar", "wordcloud"),
            ("time_series", "Aktivitas Komentar Berdasarkan Waktu", "time_series"),
            ("stacked_emotion_by_hour", "Distribusi Emosi Setiap Jam", "stacked_emotion_by_hour"),
            ("top_commenters", "Top 10 Komentator Paling Aktif", "top_commenters"),
            ("hist_char_count", "Distribusi Panjang Karakter Komentar", "hist_char_count"),
            ("comment_vs_reply", "Perbandingan Emosi Komentar vs Balasan", "comment_vs_reply"),
        ]

        for file_key, caption_text, narasi_key in visual_map:
            img_path = f"emosi/output/{file_key}_{video_id}.png"
            if os.path.exists(img_path):
                with st.expander(f"🖼️ {caption_text}"):
                    st.image(img_path, use_container_width=True)
                    if narasi_key in insight:
                        st.markdown(f"**📝 Narasi:** {insight[narasi_key]}")
                    else:
                        st.markdown("_Narasi tidak tersedia untuk grafik ini._")

    with tab3:
        st.header("⬇️ Unduh Data & Laporan")
        
        st.subheader("📄 Laporan PDF Lengkap")
        st.markdown("Unduh laporan lengkap dalam format PDF yang berisi semua insight dan visualisasi.")
        pdf_path = f"emosi/output/laporan_emosi_tiktok_{video_id}.pdf"
        
        if st.button("🖨️ Buat & Unduh Laporan PDF", use_container_width=True):
            with st.spinner("Membuat laporan PDF..."):
                generate_pdf(caption, insight, video_id)
                st.toast("PDF berhasil dibuat!", icon="📄")
        
        if os.path.exists(pdf_path):
             with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Unduh PDF yang Sudah Ada",
                    data=f.read(),
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    use_container_width=True
                )
        
        st.subheader("📊 Data Mentah (CSV)")
        st.markdown("Unduh semua data komentar beserta label emosinya dalam format CSV untuk analisis lebih lanjut.")
        csv_path = f"emosi/output/comments_with_emotion_{video_id}.csv"
        if os.path.exists(csv_path):
            with open(csv_path, "rb") as f:
                st.download_button(
                    label="📥 Unduh Data CSV", 
                    data=f.read(), 
                    file_name=os.path.basename(csv_path), 
                    mime="text/csv",
                    use_container_width=True
                )
        
        st.subheader("Tabel Data Komentar")
        st.dataframe(df, use_container_width=True)
