import os

# ── 🔑 KONFIGURASI APIFY & MULTI-TOKEN REDUNDANSI ────────────────────
# Ambil dari .streamlit/secrets.toml atau environment variable
APIFY_TOKENS = []

try:
    import streamlit as st
    if hasattr(st, "secrets") and "APIFY_TOKENS" in st.secrets:
        APIFY_TOKENS = list(st.secrets["APIFY_TOKENS"])
except Exception:
    pass

if not APIFY_TOKENS:
    env_tokens = os.getenv("APIFY_TOKENS", "")
    if env_tokens:
        APIFY_TOKENS = [t.strip() for t in env_tokens.split(",") if t.strip()]
