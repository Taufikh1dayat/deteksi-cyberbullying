import streamlit as st
import pandas as pd
import pickle
import os
import importlib

# ── 🔄 ANTI-CACHE MECHANISM ──────────────────────────────────────────────────
import scraper_apify
importlib.reload(scraper_apify)
from scraper_apify import scrape_tweets_apify

# ── 🧼 IMPORT PREPROCESSOR ──────────────────────────────────────────────────
try:
    from preprocessor import cuci_teks_super as clean_text
except ImportError:
    def clean_text(text): return str(text).lower()

# ── 🔑 CONFIGURASI HALAMAN STREAMLIT ──────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Sentimen Analisis Twitter",
    page_icon="📊",
    layout="wide"
)

# ── 📦 UNPICKLE ML COMPONENTS ────────────────────────────────────────────────
@st.cache_resource
def load_ml_components():
    try:
        with open('tfidf_vectorizer.pkl', 'rb') as f:
            vectorizer = pickle.load(f)
        with open('model_svm.pkl', 'rb') as f:
            model_svm = pickle.load(f)
        with open('model_nb.pkl', 'rb') as f:
            model_nb = pickle.load(f)
        return vectorizer, model_svm, model_nb
    except Exception:
        import joblib
        vectorizer = joblib.load('tfidf_vectorizer.pkl')
        model_svm = joblib.load('model_svm.pkl')
        model_nb = joblib.load('model_nb.pkl')
        return vectorizer, model_svm, model_nb

try:
    vectorizer, model_svm, model_nb = load_ml_components()
    model_ready = True
except Exception as e:
    st.error(f"⚠️ Gagal load file .pkl! Detail: {e}")
    model_ready = False

# ── 💾 INSIALISASI SESSION STATE (Agar Data Tidak Hilang Saat Klik Widget) ──
if 'df_master' not in st.session_state:
    st.session_state.df_master = None

# ── UI Header ─────────────────────────────────────────────────────────────────
st.title("📊 Dashboard Sentimen Real-time Analisis Twitter")
st.subheader("Komparasi Algoritma SVM & Naive Bayes dengan Pendekatan XAI (LIME)")
st.markdown("---")

# ── 🏆 TAHAP 1: VISUALISASI METRIK EVALUASI MODEL KUSTOM ──────────────────────
with st.expander("🏆 Kinerja & Metrik Evaluasi Komparasi Model (Hasil Pelatihan)", expanded=True):
    st.markdown("""
        <p style='color: #a0aec0; font-size: 14px; margin-bottom: 25px;'>
        Berikut adalah perbandingan performa objektif antara model linear dan model probabilistik yang diuji menggunakan dataset latih berkapasitas 13.165 baris data cuitan.
        </p>
    """, unsafe_allow_html=True)
    
    kolom_kiri, kolom_kanan = st.columns(2)
    
    with kolom_kiri:
        st.markdown("""
            <div style='background-color: #151922; border-left: 5px solid #4FFFB0; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
                <h4 style='margin-top: 0; color: #4FFFB0; font-family: sans-serif; display: flex; align-items: center; gap: 8px;'>🛡️ Support Vector Machine (SVM)</h4>
                <div style='display: flex; gap: 12px; justify-content: space-between; margin-top: 15px;'>
                    <div style='background: #1e2330; padding: 10px; border-radius: 6px; flex: 1; text-align: center;'>
                        <span style='font-size: 11px; color: #a0aec0; text-transform: uppercase;'>Accuracy</span>
                        <div style='font-size: 20px; font-weight: bold; color: #ffffff; margin-top: 2px;'>86.75%</div>
                    </div>
                    <div style='background: #1e2330; padding: 10px; border-radius: 6px; flex: 1; text-align: center;'>
                        <span style='font-size: 11px; color: #a0aec0; text-transform: uppercase;'>Precision</span>
                        <div style='font-size: 20px; font-weight: bold; color: #ffffff; margin-top: 2px;'>87.10%</div>
                    </div>
                    <div style='background: #1e2330; padding: 10px; border-radius: 6px; flex: 1; text-align: center;'>
                        <span style='font-size: 11px; color: #a0aec0; text-transform: uppercase;'>Recall</span>
                        <div style='font-size: 20px; font-weight: bold; color: #ffffff; margin-top: 2px;'>86.20%</div>
                    </div>
                    <div style='background: #1e2330; padding: 10px; border-radius: 6px; flex: 1; text-align: center;'>
                        <span style='font-size: 11px; color: #a0aec0; text-transform: uppercase;'>F1-Score</span>
                        <div style='font-size: 20px; font-weight: bold; color: #ffffff; margin-top: 2px;'>86.65%</div>
                    </div>
                </div>
                <div style='margin-top: 12px; font-size: 12px; color: #4FFFB0; font-weight: bold;'>✔ Unggul pada kestabilan generalisasi data teks</div>
            </div>
        """, unsafe_allow_html=True)
        
    with kolom_kanan:
        st.markdown("""
            <div style='background-color: #151922; border-left: 5px solid #FF4F4F; border-radius: 8px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
                <h4 style='margin-top: 0; color: #FF4F4F; font-family: sans-serif; display: flex; align-items: center; gap: 8px;'>📊 Multinomial Naïve Bayes</h4>
                <div style='display: flex; gap: 12px; justify-content: space-between; margin-top: 15px;'>
                    <div style='background: #1e2330; padding: 10px; border-radius: 6px; flex: 1; text-align: center;'>
                        <span style='font-size: 11px; color: #a0aec0; text-transform: uppercase;'>Accuracy</span>
                        <div style='font-size: 20px; font-weight: bold; color: #ffffff; margin-top: 2px;'>84.62%</div>
                    </div>
                    <div style='background: #1e2330; padding: 10px; border-radius: 6px; flex: 1; text-align: center;'>
                        <span style='font-size: 11px; color: #a0aec0; text-transform: uppercase;'>Precision</span>
                        <div style='font-size: 20px; font-weight: bold; color: #ffffff; margin-top: 2px;'>85.00%</div>
                    </div>
                    <div style='background: #1e2330; padding: 10px; border-radius: 6px; flex: 1; text-align: center;'>
                        <span style='font-size: 11px; color: #a0aec0; text-transform: uppercase;'>Recall</span>
                        <div style='font-size: 20px; font-weight: bold; color: #ffffff; margin-top: 2px;'>84.10%</div>
                    </div>
                    <div style='background: #1e2330; padding: 10px; border-radius: 6px; flex: 1; text-align: center;'>
                        <span style='font-size: 11px; color: #a0aec0; text-transform: uppercase;'>F1-Score</span>
                        <div style='font-size: 20px; font-weight: bold; color: #ffffff; margin-top: 2px;'>84.54%</div>
                    </div>
                </div>
                <div style='margin-top: 12px; font-size: 12px; color: #FF4F4F; font-weight: bold;'>⚡ Unggul pada efisiensi kecepatan waktu training</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Input panel (sidebar) ─────────────────────────────────────────────────────
st.sidebar.header("🔍 Parameter Pencarian")
keyword_input = st.sidebar.text_input("Masukkan Kata Kunci/Keyword:", value="Prabowo")
jumlah_tweets = st.sidebar.slider("Jumlah Tweet yang Ditarik:", min_value=5, max_value=100, value=10, step=5)
tombol_scrape = st.sidebar.button("🚀 Tarik Data Real-Time")

# Trigger aksi penarikan data baru
if tombol_scrape:
    st.info(f"⏳ Sedang mengirim perintah ke Cloud Apify untuk keyword: **'{keyword_input}'**...")
    with st.spinner("Memanen data dari server cloud Apify... Mohon tunggu..."):
        df_raw = scrape_tweets_apify(query=keyword_input, max_results=jumlah_tweets)
    
    if not df_raw.empty:
        if model_ready:
            with st.spinner("Melakukan preprocessing & prediksi model ML..."):
                df_raw['cleaned_text'] = df_raw['text'].apply(clean_text)
                tfidf_matrix = vectorizer.transform(df_raw['cleaned_text'])
                df_raw['prediksi_svm'] = model_svm.predict(tfidf_matrix)
                df_raw['prediksi_nb'] = model_nb.predict(tfidf_matrix)
        
        # Simpan hasil akhir ke dalam session state global
        st.session_state.df_master = df_raw
        st.success(f"🎉 Berhasil mengambil **{len(df_raw)}** tweet terpopuler seputar '{keyword_input}'!")
    else:
        st.error("❌ Gagal mendapatkan data. Pastikan token Apify aktif atau coba keyword lain.")

# ── 🖥️ RENDER KONTEN DASHBOARD (BERBASIS SESSION STATE) ───────────────────────
if st.session_state.df_master is not None:
    df_hasil = st.session_state.df_master
    
    kolom_tampilan = ['username', 'created_at', 'text']
    if model_ready:
        kolom_tampilan += ['prediksi_svm', 'prediksi_nb']
        
    df_display = df_hasil[kolom_tampilan].copy()
    if model_ready:
        df_display['prediksi_svm'] = df_display['prediksi_svm'].map({0: "🟢 Aman", 1: "🚨 Cyberbullying"})
        df_display['prediksi_nb'] = df_display['prediksi_nb'].map({0: "🟢 Aman", 1: "🚨 Cyberbullying"})
        
    # Render tabel utama data real-time
    st.dataframe(df_display, use_container_width=True)

    # PANEL AREA XAI LAYER
    st.markdown("---")
    st.markdown("<h3 style='color: #ffffff; font-family: sans-serif;'>🔍 Analisis Transparansi Keputusan Model (XAI Layer)</h3>", unsafe_allow_html=True)
    st.write("Pilih salah satu nomor indeks tweet di atas untuk membedah bobot keputusan fitur kata secara real-time.")

    pilihan_indeks = st.selectbox(
        "Pilih Baris Tweet untuk Dianalisis:", 
        options=df_hasil.index,
        format_func=lambda idx: f"Tweet #{idx} - @{df_hasil.loc[idx, 'username']}: {str(df_hasil.loc[idx, 'text'])[:60]}..."
    )

    if pilihan_indeks is not None:
        teks_target = df_hasil.loc[pilihan_indeks, 'text']
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ── 💡 SOLUSI ANTI-CRASH: Gunakan Radio Button Ganti dari Komponen Tabs Bawaan ──
        pilihan_model = st.radio(
            "Pilih Model Algoritma untuk Ditampilkan Eksplanasinya:",
            ["🛡️ Support Vector Machine (SVM)", "📊 Multinomial Naïve Bayes"],
            horizontal=True
        )
        
        from lime.lime_text import LimeTextExplainer
        import streamlit.components.v1 as components
        explainer = LimeTextExplainer(class_names=['Aman', 'Cyberbullying'])

        # Kondisi A: Render HANYA untuk SVM
        # Kondisi A: Render REKONSTRUKSI VISUAL UTUK SVM
        if "SVM" in pilihan_model:
            st.markdown("<h4 style='color: #4FFFB0; margin-top: 10px;'>🛡️ Interpretasi Lokal - Support Vector Machine</h4>", unsafe_allow_html=True)
            
            def predict_proba_svm(texts):
                cleaned = [clean_text(t) for t in texts]
                matrix = vectorizer.transform(cleaned)
                return model_svm.predict_proba(matrix)
            
            with st.spinner("LIME sedang membedah tingkat sensitivitas kata pada SVM..."):
                exp_svm = explainer.explain_instance(teks_target, predict_proba_svm, num_features=5)
                bobot_features = exp_svm.as_list()
                probabilitas = predict_proba_svm([teks_target])[0]
                prob_aman, prob_cyber = probabilitas[0], probabilitas[1]

            # 1. SCORECARD PROBABILITAS KUSTOM
            st.markdown(f"""
                <div style="display: flex; gap: 15px; margin-bottom: 25px; margin-top: 10px;">
                    <div style="flex: 1; background: #151922; padding: 15px; border-radius: 8px; border-left: 4px solid #4FFFB0; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                        <span style="color: #a0aec0; font-size: 11px; text-transform: uppercase; font-weight: bold;">Probabilitas Aman</span>
                        <div style="font-size: 26px; font-weight: bold; color: #4FFFB0; margin-top: 5px;">{prob_aman*100:.2f}%</div>
                    </div>
                    <div style="flex: 1; background: #151922; padding: 15px; border-radius: 8px; border-left: 4px solid #FF4F4F; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                        <span style="color: #a0aec0; font-size: 11px; text-transform: uppercase; font-weight: bold;">Probabilitas Cyberbullying</span>
                        <div style="font-size: 26px; font-weight: bold; color: #FF4F4F; margin-top: 5px;">{prob_cyber*100:.2f}%</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # 2. GRID INTERAKTIF (KIRI: GRAFIK BATANG, KANAN: HIGHLIGHT TEKS)
            col_grafik, col_teks = st.columns([4, 6])
            
            with col_grafik:
                st.markdown("<p style='color: #a0aec0; font-size: 13px; font-weight: bold; margin-bottom: 15px;'>📊 Kontribusi 5 Fitur Kata Teratas (SVM):</p>", unsafe_allow_html=True)
                for kata, bobot in bobot_features:
                    lebar_bar = min(abs(bobot) * 500, 100)
                    warna_bar = "#FF4F4F" if bobot > 0 else "#4FFFB0"
                    st.markdown(f"""
                        <div style='display: flex; align-items: center; margin-bottom: 12px; background-color: #151922; padding: 12px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                            <div style='width: 100px; font-weight: bold; color: #ffffff; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;'>{kata}</div>
                            <div style='flex-grow: 1; background-color: #1e2330; border-radius: 4px; height: 14px; margin: 0 12px; overflow: hidden;'>
                                <div style='background-color: {warna_bar}; width: {lebar_bar}%; height: 100%; border-radius: 4px;'></div>
                            </div>
                            <div style='width: 65px; text-align: right; color: {warna_bar}; font-family: monospace; font-weight: bold; font-size: 13px;'>{bobot:+.4f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
            with col_teks:
                st.markdown("<p style='color: #a0aec0; font-size: 13px; font-weight: bold; margin-bottom: 15px;'>📝 Konteks Penyorotan Kata (Linguistik Forensik):</p>", unsafe_allow_html=True)
                
                words = teks_target.split()
                highlighted_html = ""
                feature_dict = {k.lower(): b for k, b in bobot_features}
                
                for word in words:
                    clean_word = word.strip(".,;:!?\"'()[]{}—-_").lower()
                    if clean_word in feature_dict:
                        w = feature_dict[clean_word]
                        bg = "rgba(255, 79, 79, 0.25)" if w > 0 else "rgba(79, 255, 176, 0.25)"
                        lbl_color = "#FF4F4F" if w > 0 else "#4FFFB0"
                        highlighted_html += f'<span style="background-color: {bg}; border: 1px solid {lbl_color}; padding: 2px 6px; border-radius: 4px; display: inline-block; margin: 2px 1px; color: #ffffff; font-weight: bold; font-size: 14px;">{word}</span> '
                    else:
                        highlighted_html += f'<span style="color: #e2e8f0; display: inline-block; margin: 2px 1px; font-size: 14px;">{word}</span> '
                        
                st.markdown(f"""
                    <div style="background-color: #151922; padding: 20px; border-radius: 8px; min-height: 165px; border: 1px solid #1e2330; line-height: 2; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                        {highlighted_html}
                    </div>
                """, unsafe_allow_html=True)

        # Kondisi B: Render REKONSTRUKSI VISUAL UNTUK NAÏVE BAYES
        else:
            st.markdown("<h4 style='color: #FF4F4F; margin-top: 10px;'>📊 Interpretasi Lokal - Multinomial Naïve Bayes</h4>", unsafe_allow_html=True)
            
            def predict_proba_nb(texts):
                cleaned = [clean_text(t) for t in texts]
                matrix = vectorizer.transform(cleaned)
                return model_nb.predict_proba(matrix)
            
            with st.spinner("LIME sedang membedah tingkat sensitivitas kata pada Naïve Bayes..."):
                exp_nb = explainer.explain_instance(teks_target, predict_proba_nb, num_features=5)
                bobot_features = exp_nb.as_list()
                probabilitas = predict_proba_nb([teks_target])[0]
                prob_aman, prob_cyber = probabilitas[0], probabilitas[1]

            # 1. SCORECARD PROBABILITAS KUSTOM
            st.markdown(f"""
                <div style="display: flex; gap: 15px; margin-bottom: 25px; margin-top: 10px;">
                    <div style="flex: 1; background: #151922; padding: 15px; border-radius: 8px; border-left: 4px solid #4FFFB0; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                        <span style="color: #a0aec0; font-size: 11px; text-transform: uppercase; font-weight: bold;">Probabilitas Aman</span>
                        <div style="font-size: 26px; font-weight: bold; color: #4FFFB0; margin-top: 5px;">{prob_aman*100:.2f}%</div>
                    </div>
                    <div style="flex: 1; background: #151922; padding: 15px; border-radius: 8px; border-left: 4px solid #FF4F4F; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                        <span style="color: #a0aec0; font-size: 11px; text-transform: uppercase; font-weight: bold;">Probabilitas Cyberbullying</span>
                        <div style="font-size: 26px; font-weight: bold; color: #FF4F4F; margin-top: 5px;">{prob_cyber*100:.2f}%</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # 2. GRID INTERAKTIF (KIRI: GRAFIK BATANG, KANAN: HIGHLIGHT TEKS)
            col_grafik, col_teks = st.columns([4, 6])
            
            with col_grafik:
                st.markdown("<p style='color: #a0aec0; font-size: 13px; font-weight: bold; margin-bottom: 15px;'>📊 Kontribusi 5 Fitur Kata Teratas (Naïve Bayes):</p>", unsafe_allow_html=True)
                for kata, bobot in bobot_features:
                    lebar_bar = min(abs(bobot) * 500, 100)
                    warna_bar = "#FF4F4F" if bobot > 0 else "#4FFFB0"
                    st.markdown(f"""
                        <div style='display: flex; align-items: center; margin-bottom: 12px; background-color: #151922; padding: 12px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                            <div style='width: 100px; font-weight: bold; color: #ffffff; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;'>{kata}</div>
                            <div style='flex-grow: 1; background-color: #1e2330; border-radius: 4px; height: 14px; margin: 0 12px; overflow: hidden;'>
                                <div style='background-color: {warna_bar}; width: {lebar_bar}%; height: 100%; border-radius: 4px;'></div>
                            </div>
                            <div style='width: 65px; text-align: right; color: {warna_bar}; font-family: monospace; font-weight: bold; font-size: 13px;'>{bobot:+.4f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
            with col_teks:
                st.markdown("<p style='color: #a0aec0; font-size: 13px; font-weight: bold; margin-bottom: 15px;'>📝 Konteks Penyorotan Kata (Linguistik Forensik):</p>", unsafe_allow_html=True)
                
                words = teks_target.split()
                highlighted_html = ""
                feature_dict = {k.lower(): b for k, b in bobot_features}
                
                for word in words:
                    clean_word = word.strip(".,;:!?\"'()[]{}—-_").lower()
                    if clean_word in feature_dict:
                        w = feature_dict[clean_word]
                        bg = "rgba(255, 79, 79, 0.25)" if w > 0 else "rgba(79, 255, 176, 0.25)"
                        lbl_color = "#FF4F4F" if w > 0 else "#4FFFB0"
                        highlighted_html += f'<span style="background-color: {bg}; border: 1px solid {lbl_color}; padding: 2px 6px; border-radius: 4px; display: inline-block; margin: 2px 1px; color: #ffffff; font-weight: bold; font-size: 14px;">{word}</span> '
                    else:
                        highlighted_html += f'<span style="color: #e2e8f0; display: inline-block; margin: 2px 1px; font-size: 14px;">{word}</span> '
                        
                st.markdown(f"""
                    <div style="background-color: #151922; padding: 20px; border-radius: 8px; min-height: 165px; border: 1px solid #1e2330; line-height: 2; box-shadow: 0 4px 6px rgba(0,0,0,0.2);">
                        {highlighted_html}
                    </div>
                """, unsafe_allow_html=True)

    # Tombol Unduh Berkas CSV
    st.markdown("---")
    csv_data = df_hasil.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Unduh Dataset sebagai CSV",
        data=csv_data,
        file_name=f"dataset_realtime_{keyword_input.lower()}.csv",
        mime="text/csv"
    )
else:
    st.write("💡 **Petunjuk Penggunaan:**")
    st.write("1. Masukkan kata kunci yang ingin kamu teliti di panel sebelah kiri.")
    st.write("2. Tentukan jumlah tweet yang ingin kamu ambil.")
    st.write("3. Klik tombol **Tarik Data Real-Time** untuk melihat hasil komparasi ML bekerja!")