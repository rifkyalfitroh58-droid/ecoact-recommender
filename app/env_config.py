"""
EcoAct v1.2 — Environment Config
Kelola API keys dengan aman menggunakan .env file
"""

import os

# Coba load .env untuk lokal (opsional, tidak wajib ada)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Coba baca dari Streamlit Secrets dulu (untuk cloud)
try:
    import streamlit as st
    OPENWEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY", "")
    AIRVISUAL_API_KEY   = st.secrets.get("AIRVISUAL_API_KEY", "")
except Exception:
    # Fallback ke .env / environment variable (untuk lokal)
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    AIRVISUAL_API_KEY   = os.getenv("AIRVISUAL_API_KEY", "")

USE_MOCK_DATA = not (OPENWEATHER_API_KEY and AIRVISUAL_API_KEY)