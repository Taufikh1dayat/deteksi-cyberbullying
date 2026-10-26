import streamlit as st
import pandas as pd
import pickle
import os
import json
import hashlib
import requests
import time
from pathlib import Path

# ── 🔄 MULTI-PLATFORM SCRAPER (HOT RELOAD) ───────────────────────────────────
import importlib
import scrapers
import scrapers.config
import scrapers.tiktok
import scrapers.twitter
import scrapers.instagram
import scrapers.manager

importlib.reload(scrapers.config)
importlib.reload(scrapers.tiktok)
importlib.reload(scrapers.twitter)
importlib.reload(scrapers.instagram)
importlib.reload(scrapers.manager)
importlib.reload(scrapers)

from scrapers import scrape_data

# ── 🧼 IMPORT PREPROCESSOR ──────────────────────────────────────────────────
try:
    from preprocessor import cuci_teks_super as clean_text
except ImportError:
    def clean_text(text): return str(text).lower()

# ── 🔑 CONFIGURASI HALAMAN STREAMLIT ──────────────────────────────────────────
st.set_page_config(
    page_title="CyberShield — Deteksi Cyberbullying Real-Time",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── 🎨 MODERN STYLESHEET INJECTION (COMPACT & PADDED UP) ──────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
/* ── COMPACT CONTAINER FIX (Menghapus ruang kosong atas bawaan Streamlit) ── */
.block-container {
  padding-top: 1.25rem !important;
  padding-bottom: 2rem !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
  max-width: 100% !important;
}

header[data-testid="stHeader"] {
  height: 2.5rem !important;
  background: transparent !important;
}

div[data-testid="stToolbar"] {
  top: 0.25rem !important;
  right: 1rem !important;
}

:root {
  --font-main: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  --bg-app: #080c14;
  --bg-card: #0f172a;
  --bg-card-alt: #162035;
  --border-card: rgba(255, 255, 255, 0.08);

  --accent-svm: #38bdf8;
  --accent-nb: #fbbf24;
  --color-toxic: #f43f5e;
  --color-safe: #10b981;
}

html, body, [class*="css"] {
  font-family: var(--font-main);
}

/* Header Container */
.dash-header {
  padding: 0 0 12px 0;
  border-bottom: 1px solid var(--border-card);
  margin-bottom: 16px;
}

.dash-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #f8fafc;
  margin: 0 0 4px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dash-subtitle {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

/* Badge Pill */
.badge-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 8px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 600;
  font-family: var(--font-mono);
  letter-spacing: 0.02em;
}
.badge-pill-cyan { background: rgba(56, 189, 248, 0.12); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
.badge-pill-amber { background: rgba(251, 191, 36, 0.12); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); }
.badge-pill-rose { background: rgba(244, 63, 94, 0.12); color: #f43f5e; border: 1px solid rgba(244, 63, 94, 0.3); }
.badge-pill-emerald { background: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }

/* Glassmorphism Card */
.modern-card {
  background: linear-gradient(180deg, #111a2e 0%, #0b111e 100%);
  border: 1px solid var(--border-card);
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
  margin-bottom: 12px;
}

.modern-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-card);
}

.modern-card-title {
  font-size: 14px;
  font-weight: 600;
  color: #f1f5f9;
}

/* Metric Deck */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-top: 8px;
}

.kpi-box {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--border-card);
  border-radius: 8px;
  padding: 10px;
  text-align: center;
}

.kpi-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  margin-bottom: 2px;
}

.kpi-value {
  font-family: var(--font-mono);
  font-size: 17px;
  font-weight: 700;
  color: #f8fafc;
}

/* Toxicity Meter Bar */
.toxicity-bar-container {
  margin: 10px 0 16px 0;
  background: #0f172a;
  border-radius: 8px;
  padding: 10px 14px;
  border: 1px solid var(--border-card);
}

.toxicity-bar {
  display: flex;
  height: 10px;
  border-radius: 5px;
  overflow: hidden;
  margin: 6px 0 4px 0;
  background: #1e293b;
}

.bar-safe { background: #10b981; }
.bar-toxic { background: #f43f5e; }

/* XAI Highlighted Words */
.highlight-box {
  background: #0b111e;
  border: 1px solid var(--border-card);
  border-radius: 8px;
  padding: 14px;
  line-height: 2;
  min-height: 120px;
  color: #cbd5e1;
  font-size: 13px;
}

.token-word {
  display: inline-block;
  padding: 1px 6px;
  margin: 2px 2px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 12px;
}
.token-toxic {
  background: rgba(244, 63, 94, 0.18);
  border: 1px solid rgba(244, 63, 94, 0.5);
  color: #fda4af;
}
.token-safe {
  background: rgba(16, 185, 129, 0.18);
  border: 1px solid rgba(16, 185, 129, 0.5);
  color: #6ee7b7;
}

/* AI Narrative Glass Box */
.ai-narrative-card {
  background: linear-gradient(135deg, #111a30 0%, #0a1120 100%);
  border-radius: 10px;
  padding: 18px;
  border: 1px solid rgba(56, 189, 248, 0.25);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
  position: relative;
  overflow: hidden;
  margin-top: 16px;
}

.ai-narrative-card::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #38bdf8, #818cf8, #f43f5e);
}

.ai-narrative-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.ai-narrative-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #38bdf8;
}

.ai-narrative-body {
  font-size: 14px;
  line-height: 1.7;
  color: #e2e8f0;
  font-style: italic;
  margin: 0;
}
</style>
""", unsafe_allow_html=True)

# ── 💾 DYNAMIC CACHE & OPENROUTER CONFIGURATION ──────────────────────────────
CACHE_FILE = Path("ai_cache.json")

OPENROUTER_API_KEY = ""
if hasattr(st, "secrets") and "OPENROUTER_API_KEY" in st.secrets:
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
else:
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

MODEL_NAME = "openrouter/free"
FALLBACK_MODEL = "liquid/lfm-2.5-2.6b:free"

def muat_cache_disk_lokal() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def simpan_cache_disk_lokal(cache_data: dict):
    try:
        CACHE_FILE.write_text(json.dumps(cache_data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

def buat_kunci_cache_lokal(tweet: str, model: str, prompt: str) -> str:
    gabungan = f"{model}::{tweet}::{prompt}"
    return hashlib.sha256(gabungan.encode("utf-8")).hexdigest()

def ambil_narasi_openrouter_live(prompt: str) -> str:
    if not OPENROUTER_API_KEY or "GANTI_DENGAN" in OPENROUTER_API_KEY:
        raise ValueError("API Key OpenRouter belum dikonfigurasi di secrets.toml")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "CyberShield Live Hybrid"
    }

    daftar_model = [MODEL_NAME, FALLBACK_MODEL]
    last_status = None

    for model_target in daftar_model:
        try:
            payload = {
                "model": model_target,
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'].strip()
            else:
                last_status = response.status_code
        except Exception:
            continue

    raise RuntimeError(f"Server Cloud Error (Code: {last_status})")

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
    st.error(f"⚠️ Gagal load model .pkl! Detail: {e}")
    model_ready = False

@st.cache_resource
def get_lime_explainer():
    from lime.lime_text import LimeTextExplainer
    return LimeTextExplainer(class_names=['Aman', 'Cyberbullying'])

# ── 🛠️ ENGINE FALLBACK LOKAL ─────────────────────────────────────────────────
def buat_analisis_forensik_lokal(label, bobot_list):
    try:
        kata_top = [f"'{item[0]}'" for item in bobot_list[:2]]
        kata_str = " dan ".join(kata_top)
    except Exception:
        kata_str = "fitur kata dominan"

    return f"Berdasarkan analisis Linguistik Forensik, konstruksi semantik konten ini secara signifikan dipengaruhi oleh kemunculan kata kunci seperti {kata_str}. Pola interaksi antar kata tersebut membentuk bobot kontekstual ekstrem yang menjustifikasi keputusan model ke dalam kelompok [{label}]."

# ── 💾 SESSION STATE ─────────────────────────────────────────────────────────
if 'df_master' not in st.session_state:
    st.session_state.df_master = None
if 'benchmark_data' not in st.session_state:
    st.session_state.benchmark_data = None

# ── 🌟 HEADER DASHBOARD (RINGKAS & TIDAK MAKAN TEMPAT) ────────────────────────
st.markdown("""
<div class="dash-header">
  <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
    <div>
      <h1 class="dash-title">🛡️ CyberShield Dashboard</h1>
      <p class="dash-subtitle">Sistem Deteksi Cyberbullying Real-Time · Komparasi SVM vs Naïve Bayes · XAI (LIME)</p>
    </div>
    <div style="display: flex; gap: 6px; flex-wrap: wrap;">
      <span class="badge-pill badge-pill-cyan">SVM 86.75%</span>
      <span class="badge-pill badge-pill-amber">NB 84.62%</span>
      <span class="badge-pill badge-pill-emerald">11.897 TF-IDF</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── 🔍 SIDEBAR PARAMETER ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Parameter Scraping")
    platform_pilihan = st.selectbox(
        "Platform Sumber Data:",
        ["Twitter / X", "TikTok", "Instagram"]
    )

    if platform_pilihan == "Twitter / X":
        input_target = st.text_input("Kata Kunci / Keyword:", value="Prabowo", help="Cari tweet terbaru berdasarkan kata kunci")
        slider_label = "Jumlah Tweet:"
    elif platform_pilihan == "TikTok":
        input_target = st.text_input(
            "Kata Kunci atau URL Video TikTok:",
            value="Prabowo",
            placeholder="Contoh: Prabowo ATAU https://www.tiktok.com/@.../video/...",
            help="Bisa kata kunci pencarian umum atau link spesifik video TikTok"
        )
        slider_label = "Jumlah Data:"
    else:
        input_target = st.text_input(
            "URL Postingan / Reels Instagram:",
            placeholder="https://www.instagram.com/p/... ATAU /reel/...",
            help="Masukkan tautan postingan atau Reels Instagram yang ingin dianalisis komentarnya"
        )
        slider_label = "Jumlah Komentar:"

    jumlah_data = st.slider(slider_label, min_value=5, max_value=50, value=10, step=5)
    st.markdown("---")
    tombol_scrape = st.button("🚀 Tarik & Analisis Data", use_container_width=True, type="primary")

# ── 🚀 LOGIKA SCRAPING & PREDIKSI ─────────────────────────────────────────────
if tombol_scrape:
    if not input_target.strip():
        st.warning("⚠️ Masukkan kata kunci atau URL terlebih dahulu!")
    else:
        with st.status(f"Mengeruk data dari {platform_pilihan}...", expanded=True) as status:
            st.write(f"📡 Menghubungi cloud actor Apify untuk target: **'{input_target}'**...")
            df_raw = scrape_data(platform=platform_pilihan, target=input_target, max_results=jumlah_data)

            if not df_raw.empty:
                st.write(f"✨ Berhasil memanen **{len(df_raw)}** data. Menjalankan pipeline NLP & inferensi...")
                if model_ready:
                    t_prep_start = time.perf_counter()
                    df_raw['cleaned_text'] = df_raw['text'].apply(clean_text)
                    tfidf_matrix = vectorizer.transform(df_raw['cleaned_text'])
                    t_prep = (time.perf_counter() - t_prep_start) * 1000

                    t_svm_start = time.perf_counter()
                    df_raw['prediksi_svm'] = model_svm.predict(tfidf_matrix)
                    t_svm = (time.perf_counter() - t_svm_start) * 1000

                    t_nb_start = time.perf_counter()
                    df_raw['prediksi_nb'] = model_nb.predict(tfidf_matrix)
                    t_nb = (time.perf_counter() - t_nb_start) * 1000

                    st.session_state.benchmark_data = {
                        'n_tweets': len(df_raw),
                        't_prep': t_prep,
                        't_svm': t_svm,
                        't_nb': t_nb,
                        'avg_svm': t_svm / len(df_raw) if len(df_raw) > 0 else 0,
                        'avg_nb': t_nb / len(df_raw) if len(df_raw) > 0 else 0,
                        'speedup': (t_svm / t_nb) if t_nb > 0 else 1.0
                    }

                st.session_state.df_master = df_raw
                status.update(label=f"✅ Selesai! {len(df_raw)} data berhasil dianalisis.", state="complete")
            else:
                status.update(label="❌ Gagal memanen data. Periksa token atau target pencarian.", state="error")

# ── 🖥️ RENDER HASIL & ANALISIS DENGAN TABEL SISTEM TAB ─────────────────────────
if st.session_state.df_master is not None:
    df_hasil = st.session_state.df_master
    n_total = len(df_hasil)

    # Hitung ringkasan statistik
    n_toxic_svm = (df_hasil['prediksi_svm'] == 1).sum() if 'prediksi_svm' in df_hasil.columns else 0
    n_safe_svm = n_total - n_toxic_svm
    pct_toxic_svm = (n_toxic_svm / n_total * 100) if n_total > 0 else 0
    pct_safe_svm = 100 - pct_toxic_svm

    # KPI Summary Row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-box" style="border-left: 3px solid #38bdf8;">
          <div class="kpi-label">Total Data</div>
          <div class="kpi-value">{n_total}</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-box" style="border-left: 3px solid #f43f5e;">
          <div class="kpi-label">Cyberbullying</div>
          <div class="kpi-value" style="color: #f43f5e;">{n_toxic_svm} <span style="font-size: 12px; font-weight: normal;">({pct_toxic_svm:.0f}%)</span></div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-box" style="border-left: 3px solid #10b981;">
          <div class="kpi-label">Konten Aman</div>
          <div class="kpi-value" style="color: #10b981;">{n_safe_svm} <span style="font-size: 12px; font-weight: normal;">({pct_safe_svm:.0f}%)</span></div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        speedup_val = st.session_state.benchmark_data['speedup'] if st.session_state.benchmark_data else 1.0
        st.markdown(f"""
        <div class="kpi-box" style="border-left: 3px solid #fbbf24;">
          <div class="kpi-label">Speedup NB vs SVM</div>
          <div class="kpi-value" style="color: #fbbf24;">{speedup_val:.1f}x</div>
        </div>
        """, unsafe_allow_html=True)

    # Toxicity Distribution Visual Bar
    st.markdown(f"""
    <div class="toxicity-bar-container">
      <div style="display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8;">
        <span>Rasio Toksisitas Konten (SVM)</span>
        <span><b>{pct_safe_svm:.1f}%</b> Aman &nbsp;|&nbsp; <b>{pct_toxic_svm:.1f}%</b> Cyberbullying</span>
      </div>
      <div class="toxicity-bar">
        <div class="bar-safe" style="width: {pct_safe_svm}%;"></div>
        <div class="bar-toxic" style="width: {pct_toxic_svm}%;"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 📑 SISTEM TAB MODERN UNTUK MENGHEMAT RUANG VERTIKAL ────────────────────
    tab_tabel, tab_xai, tab_benchmark = st.tabs([
        "📋 Tabel Hasil Klasifikasi",
        "🔬 Forensik XAI & AI Narrative",
        "⚡ Benchmark Latensi & Metrik Model"
    ])

    # ── TAB 1: TABEL HASIL ────────────────────────────────────────────────────
    with tab_tabel:
        kolom_tampilan = (['platform'] if 'platform' in df_hasil.columns else []) + ['username', 'created_at', 'text']
        if model_ready:
            kolom_tampilan += ['prediksi_svm', 'prediksi_nb']

        df_display = df_hasil[kolom_tampilan].copy()
        if model_ready:
            df_display['prediksi_svm'] = df_display['prediksi_svm'].map({0: "🟢 Aman", 1: "🚨 Cyberbullying"})
            df_display['prediksi_nb'] = df_display['prediksi_nb'].map({0: "🟢 Aman", 1: "🚨 Cyberbullying"})

        st.dataframe(
            df_display,
            use_container_width=True,
            column_config={
                "platform": st.column_config.TextColumn("Platform", width="small"),
                "username": st.column_config.TextColumn("User", width="medium"),
                "created_at": st.column_config.TextColumn("Waktu", width="small"),
                "text": st.column_config.TextColumn("Teks Konten", width="large"),
                "prediksi_svm": st.column_config.TextColumn("SVM", width="small"),
                "prediksi_nb": st.column_config.TextColumn("Naïve Bayes", width="small"),
            },
            hide_index=True
        )

    # ── TAB 2: XAI & AI NARRATIVE ─────────────────────────────────────────────
    with tab_xai:
        pilihan_indeks = st.selectbox(
            "Pilih Baris Data untuk Dibedah Keputusannya:",
            options=df_hasil.index,
            format_func=lambda idx: f"#{idx} [{df_hasil.loc[idx, 'platform'] if 'platform' in df_hasil.columns else 'Post'}] @{df_hasil.loc[idx, 'username']}: {str(df_hasil.loc[idx, 'text'])[:70]}..."
        )

        if pilihan_indeks is not None:
            teks_target = str(df_hasil.loc[pilihan_indeks, 'text'])

            pilihan_model = st.radio(
                "Pilih Algoritma Model:",
                ["🛡️ Support Vector Machine (SVM)", "📊 Multinomial Naïve Bayes"],
                horizontal=True
            )

            explainer = get_lime_explainer()

            if "SVM" in pilihan_model:
                def predict_proba_svm(texts):
                    cleaned = [clean_text(t) for t in texts]
                    matrix = vectorizer.transform(cleaned)
                    return model_svm.predict_proba(matrix)

                with st.spinner("LIME membedah sensitivitas kata pada SVM..."):
                    exp_model = explainer.explain_instance(teks_target, predict_proba_svm, num_features=5)
                    bobot_features = exp_model.as_list()
                    probabilitas = predict_proba_svm([teks_target])[0]
                    prob_aman, prob_cyber = probabilitas[0], probabilitas[1]
            else:
                def predict_proba_nb(texts):
                    cleaned = [clean_text(t) for t in texts]
                    matrix = vectorizer.transform(cleaned)
                    return model_nb.predict_proba(matrix)

                with st.spinner("LIME membedah sensitivitas kata pada Naïve Bayes..."):
                    exp_model = explainer.explain_instance(teks_target, predict_proba_nb, num_features=5)
                    bobot_features = exp_model.as_list()
                    probabilitas = predict_proba_nb([teks_target])[0]
                    prob_aman, prob_cyber = probabilitas[0], probabilitas[1]

            label_prediksi = "Cyberbullying" if prob_cyber > prob_aman else "Aman"

            # Probability Gauge Cards
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.markdown(f"""
                <div class="kpi-box" style="border-left: 3px solid #10b981; text-align: left; padding: 12px;">
                  <div class="kpi-label">Probabilitas Aman</div>
                  <div style="font-family: var(--font-mono); font-size: 20px; font-weight: 700; color: #10b981;">{prob_aman*100:.2f}%</div>
                  <div style="height: 5px; background: #1e293b; border-radius: 3px; overflow: hidden; margin-top: 6px;">
                    <div style="height: 100%; width: {prob_aman*100}%; background: #10b981;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with col_p2:
                st.markdown(f"""
                <div class="kpi-box" style="border-left: 3px solid #f43f5e; text-align: left; padding: 12px;">
                  <div class="kpi-label">Probabilitas Cyberbullying</div>
                  <div style="font-family: var(--font-mono); font-size: 20px; font-weight: 700; color: #f43f5e;">{prob_cyber*100:.2f}%</div>
                  <div style="height: 5px; background: #1e293b; border-radius: 3px; overflow: hidden; margin-top: 6px;">
                    <div style="height: 100%; width: {prob_cyber*100}%; background: #f43f5e;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            # LIME Weights + Highlighter
            col_grafik, col_teks = st.columns([5, 5])

            with col_grafik:
                st.markdown("<div style='font-size: 12px; font-weight: 600; color: #cbd5e1; margin: 12px 0 8px 0;'>Top 5 Kata Kunci Dominan (Bobot LIME):</div>", unsafe_allow_html=True)
                max_bobot = max([abs(b) for _, b in bobot_features]) if bobot_features else 1.0

                for kata, bobot in bobot_features:
                    lebar_bar = max(min(int(abs(bobot) / max_bobot * 100), 100), 10) if max_bobot > 0 else 10
                    warna_bar = "#f43f5e" if bobot > 0 else "#10b981"
                    st.markdown(f"""
                    <div style='display: flex; align-items: center; margin-bottom: 8px; background: #0f172a; padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.06);'>
                      <div style='width: 90px; font-weight: 600; color: #f8fafc; font-size: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;'>{kata}</div>
                      <div style='flex: 1; background: #1e293b; border-radius: 3px; height: 8px; margin: 0 10px; overflow: hidden;'>
                        <div style='background: {warna_bar}; width: {lebar_bar}%; height: 100%; border-radius: 3px;'></div>
                      </div>
                      <div style='width: 65px; text-align: right; color: {warna_bar}; font-family: var(--font-mono); font-weight: 600; font-size: 11px;'>{bobot:+.4f}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_teks:
                st.markdown("<div style='font-size: 12px; font-weight: 600; color: #cbd5e1; margin: 12px 0 8px 0;'>Konteks Penyorotan Kata (Linguistik Forensik):</div>", unsafe_allow_html=True)
                words = teks_target.split()
                highlighted_html = ""
                feature_dict = {k.lower(): b for k, b in bobot_features}

                for word in words:
                    clean_word = word.strip(".,;:!?\"'()[]{}—-_").lower()
                    if clean_word in feature_dict:
                        w = feature_dict[clean_word]
                        cls = "token-toxic" if w > 0 else "token-safe"
                        highlighted_html += f'<span class="token-word {cls}">{word}</span> '
                    else:
                        highlighted_html += f'<span style="color: #cbd5e1; margin: 0 2px;">{word}</span> '

                st.markdown(f"""
                <div class="highlight-box">
                  {highlighted_html}
                </div>
                """, unsafe_allow_html=True)

            # AI Narrative Layer
            str_bobot = ", ".join([f"'{k}' ({b:+.4f})" for k, b in bobot_features])
            prompt_skenario = f"""
            Teks Cuitan Konten: "{teks_target}"
            Model Klasifikasi: {pilihan_model}
            Hasil Prediksi Akhir: [{label_prediksi}]
            Nilai Key-Features LIME: {str_bobot}
            Bertindaklah sebagai pakar Linguistik Forensik Siber. Jelaskan dalam 2 atau 3 kalimat santun bahasa Indonesia,
            keterkaitan makna kata kunci di atas sehingga memutuskan sebagai {label_prediksi} dan sanggah jika terdapat kesalahan.
            """

            db_cache_lokal = muat_cache_disk_lokal()
            kunci_pencarian = buat_kunci_cache_lokal(teks_target, pilihan_model, prompt_skenario)

            if kunci_pencarian in db_cache_lokal:
                gemini_text = db_cache_lokal[kunci_pencarian]
                cache_badge = '<span class="badge-pill badge-pill-emerald">⚡ Cache Hit (Disk)</span>'
            else:
                try:
                    with st.spinner("Menghubungi OpenRouter Cloud..."):
                        gemini_text = ambil_narasi_openrouter_live(prompt_skenario)
                    db_cache_lokal[kunci_pencarian] = gemini_text
                    simpan_cache_disk_lokal(db_cache_lokal)
                    cache_badge = '<span class="badge-pill badge-pill-cyan">☁️ Live Saved</span>'
                except Exception:
                    gemini_text = buat_analisis_forensik_lokal(label_prediksi, bobot_features)
                    cache_badge = '<span class="badge-pill badge-pill-amber">🛡️ Local Fallback</span>'

            st.markdown(f"""
            <div class="ai-narrative-card">
              <div class="ai-narrative-header">
                <span class="ai-narrative-title">✨ Telaah Linguistik Forensik AI ({'SVM' if 'SVM' in pilihan_model else 'Naïve Bayes'})</span>
                {cache_badge}
              </div>
              <p class="ai-narrative-body">
                "{gemini_text}"
              </p>
            </div>
            """, unsafe_allow_html=True)

    # ── TAB 3: BENCHMARK & METRIK MODEL ───────────────────────────────────────
    with tab_benchmark:
        if 'benchmark_data' in st.session_state and st.session_state.benchmark_data is not None:
            bm = st.session_state.benchmark_data
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("📦 Preprocessing + TF-IDF", f"{bm['t_prep']:.1f} ms", f"{bm['t_prep']/bm['n_tweets']:.2f} ms/item")
            b2.metric("🛡️ Latensi Total SVM", f"{bm['t_svm']:.2f} ms", f"{bm['avg_svm']:.3f} ms/item")
            b3.metric("📊 Latensi Total NB", f"{bm['t_nb']:.2f} ms", f"{bm['avg_nb']:.3f} ms/item")
            label_speed = f"{bm['speedup']:.2f}x Lebih Cepat" if bm['speedup'] >= 1 else f"{1/bm['speedup']:.2f}x Lebih Lambat"
            b4.metric("⚡ Keunggulan NB", label_speed, "Naïve Bayes vs SVM")

        st.markdown("---")
        st.markdown("#### 🏆 Kinerja Model Hasil Pelatihan (Dataset Latih 13.165 Baris Data)")

        col_svm, col_nb = st.columns(2)
        with col_svm:
            st.markdown("""
            <div class="modern-card" style="border-left: 3px solid #38bdf8;">
              <div class="modern-card-header">
                <span class="modern-card-title">🛡️ Support Vector Machine (SVM)</span>
                <span class="badge-pill badge-pill-cyan">Akurasi Unggul</span>
              </div>
              <div class="kpi-row">
                <div class="kpi-box"><div class="kpi-label">Accuracy</div><div class="kpi-value" style="color: #38bdf8;">86.75%</div></div>
                <div class="kpi-box"><div class="kpi-label">Precision</div><div class="kpi-value">86.47%</div></div>
                <div class="kpi-box"><div class="kpi-label">Recall</div><div class="kpi-value">86.59%</div></div>
                <div class="kpi-box"><div class="kpi-label">F1-Score</div><div class="kpi-value">86.53%</div></div>
              </div>
              <p style="font-size: 11px; color: #64748b; margin: 8px 0 0 0;">Optimal pada kestabilan margin linier untuk teks implisit.</p>
            </div>
            """, unsafe_allow_html=True)

        with col_nb:
            st.markdown("""
            <div class="modern-card" style="border-left: 3px solid #fbbf24;">
              <div class="modern-card-header">
                <span class="modern-card-title">📊 Multinomial Naïve Bayes (NB)</span>
                <span class="badge-pill badge-pill-amber">Kecepatan Unggul</span>
              </div>
              <div class="kpi-row">
                <div class="kpi-box"><div class="kpi-label">Accuracy</div><div class="kpi-value" style="color: #fbbf24;">84.62%</div></div>
                <div class="kpi-box"><div class="kpi-label">Precision</div><div class="kpi-value">86.27%</div></div>
                <div class="kpi-box"><div class="kpi-label">Recall</div><div class="kpi-value">83.04%</div></div>
                <div class="kpi-box"><div class="kpi-label">F1-Score</div><div class="kpi-value">83.76%</div></div>
              </div>
              <p style="font-size: 11px; color: #64748b; margin: 8px 0 0 0;">Komputasi ringan berbasis perkalian frekuensi probabilitas.</p>
            </div>
            """, unsafe_allow_html=True)

else:
    # TAMPILAN AWAL (SEBELUM ADA DATA DISCRAPE) - RINGKAS & TEPAT DI ATAS
    c_left, c_right = st.columns([5, 5])
    with c_left:
        st.markdown("""
        <div class="modern-card">
          <div class="modern-card-header">
            <span class="modern-card-title">💡 Petunjuk Penggunaan</span>
          </div>
          <ol style="font-size: 13px; color: #94a3b8; padding-left: 20px; line-height: 1.8;">
            <li>Pilih platform sumber data di sidebar kiri (<b>Twitter / X</b>, <b>TikTok</b>, atau <b>Instagram</b>).</li>
            <li>Ketikkan kata kunci pencarian atau link postingan/Reels/video spesifik.</li>
            <li>Tentukan jumlah data (5 s.d 50 data) lalu tekan tombol <b>🚀 Tarik & Analisis Data</b>.</li>
            <li>Hasil deteksi, rasio toksisitas, dan analisis XAI LIME akan tampil otomatis.</li>
          </ol>
        </div>
        """, unsafe_allow_html=True)

    with c_right:
        st.markdown("""
        <div class="modern-card" style="border-left: 3px solid #38bdf8;">
          <div class="modern-card-header">
            <span class="modern-card-title">🛡️ Status Model Machine Learning</span>
            <span class="badge-pill badge-pill-emerald">Aktif & Siap</span>
          </div>
          <div style="font-size: 13px; color: #94a3b8; line-height: 1.7;">
            <div>• <b>Support Vector Machine (Linear):</b> Akurasi 86.75% · F1-Score 86.53%</div>
            <div>• <b>Multinomial Naïve Bayes:</b> Akurasi 84.62% · F1-Score 83.76%</div>
            <div>• <b>Feature Extractor:</b> TF-IDF (11.897 kosakata dasar)</div>
            <div>• <b>Explainability:</b> LIME Text Explainer + Contextual AI (OpenRouter)</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
