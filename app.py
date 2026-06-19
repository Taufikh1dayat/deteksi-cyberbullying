import streamlit as st
import pandas as pd  # <-- TETAP WAJIB ADA untuk ngurus DataFrame & tabel!
import pickle
import os
import importlib

# ── 🔄 ANTI-CACHE MECHANISM (Biar kodingan scraper terbaru langsung kebaca) ──
import scraper_apify
importlib.reload(scraper_apify)
from scraper_apify import scrape_tweets_apify
# ─────────────────────────────────────────────────────────────────────────────

# ── 🔑 CONFIGURASI HALAMAN STREAMLIT ─────────────────
st.set_page_config(
    page_title="Dashboard Sentimen Analisis Twitter",
    page_icon="📊",
    layout="wide"
)

# ── Judul & Subjudul ───────────────────────────────
st.title("📊 Dashboard Sentimen Real-time Analisis Twitter")
st.subheader("Komparasi Algoritma SVM & Naive Bayes dengan Pendekatan XAI (LIME)")
st.markdown("---")

# ── Input panel (sidebar) ───────────────────────────────

st.sidebar.header("🔍 Parameter Pencarian")

# kolom input untuk keyword pencarian
keyword_input = st.sidebar.text_input(
    "Masukkan Kata Kunci/Keyword:", 
    value="Prabowo",
    help="Contoh: Prabowo,IKN, Gibran, Subsidi BBM, dll."
)

# Slider untuk menentukan jumlah data yang ingin ditarik
jumlah_tweets = st.sidebar.slider(
    "Jumlah Tweet yang Ditarik:", 
    min_value=5, 
    max_value=100, 
    value=10, 
    step=5,
    help="Aktor Cloud Apify mewajibkan minimal penarikan 20 data (akan dipotong otomatis sesuai slider)."
)

# Tombol Eksekusi
tombol_scrape = st.sidebar.button("🚀 Tarik Data Real-Time")

# ── 🖥️ KONTEN UTAMA (DASHBOARD) ───────────────────────────────────────
if tombol_scrape:
    st.info(f"⏳ Sedang mengirim perintah ke Cloud Apify untuk keyword: **'{keyword_input}'**...")
    
    # Memanggil fungsi scraper cloud dari file scraper_apify.py
    with st.spinner("Memanen data dari server cloud Apify... Mohon tunggu..."):
        df_hasil = scrape_tweets_apify(query=keyword_input, max_results=jumlah_tweets)
    
    # Cek apakah data berhasil didapatkan
    if not df_hasil.empty:
        st.success(f"🎉 Berhasil mengambil **{len(df_hasil)}** tweet terpopuler seputar '{keyword_input}'!")
        
        # Menampilkan data dalam bentuk tabel interaktif Streamlit
        st.dataframe(
            df_hasil[['username', 'created_at', 'text', 'like_count', 'retweet_count']], 
            use_container_width=True
        )
        
        # Fitur opsional untuk unduh data ke CSV
        csv_data = df_hasil.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Unduh Dataset sebagai CSV",
            data=csv_data,
            file_name=f"dataset_realtime_{keyword_input.lower()}.csv",
            mime="text/csv"
        )
    else:
        st.error("❌ Gagal mendapatkan data. Pastikan token Apify aktif atau coba keyword lain.")
else:
    # Tampilan awal saat user baru membuka dashboard
    st.write("💡 **Petunjuk Penggunaan:**")
    st.write("1. Masukkan kata kunci yang ingin kamu teliti di panel sebelah kiri.")
    st.write("2. Tentukan jumlah tweet yang ingin kamu ambil.")
    st.write("3. Klik tombol **Tarik Data Real-Time** untuk melihat sihir cloud bekerja!")