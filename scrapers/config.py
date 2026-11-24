import os
from pathlib import Path

# ── 🔑 KONFIGURASI APIFY & MULTI-TOKEN REDUNDANSI ──────────────────
# Prioritas pemuatan:
# 1. Streamlit Secrets (jika dijalankan via streamlit)
# 2. File .streamlit/secrets.toml lokal (jika dijalankan via standalone script)
# 3. Environment Variable APIFY_TOKENS

APIFY_TOKENS = []

# 1. Coba dari Streamlit Secrets
try:
    import streamlit as st
    if hasattr(st, "secrets") and "APIFY_TOKENS" in st.secrets:
        tokens_from_sec = list(st.secrets["APIFY_TOKENS"])
        if tokens_from_sec:
            APIFY_TOKENS = [t for t in tokens_from_sec if t and "apify_api_" in t]
except Exception:
    pass

# 2. Coba dari file .streamlit/secrets.toml lokal
if not APIFY_TOKENS:
    secrets_file = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"
    if secrets_file.exists():
        try:
            import tomllib
            with open(secrets_file, "rb") as f:
                sec_data = tomllib.load(f)
                tokens_from_file = sec_data.get("APIFY_TOKENS", [])
                if tokens_from_file:
                    APIFY_TOKENS = [t for t in tokens_from_file if t and "apify_api_" in t]
        except Exception:
            pass

# 3. Coba dari Environment Variable
if not APIFY_TOKENS:
    env_tokens = os.getenv("APIFY_TOKENS", "")
    if env_tokens:
        APIFY_TOKENS = [t.strip() for t in env_tokens.split(",") if t.strip()]
