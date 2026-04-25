"""
EcoAct v1.2 — Environment Config
Kelola API keys dengan aman menggunakan .env file
"""

import os
from dotenv import load_dotenv

# Coba load dari .env (untuk lokal)
load_dotenv()

# Coba baca dari Streamlit Secrets (untuk cloud deployment)
try:
    import streamlit as st
    OPENWEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY", "")
    AIRVISUAL_API_KEY   = st.secrets.get("AIRVISUAL_API_KEY", "")
except Exception:
    # Fallback ke environment variable dari .env
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    AIRVISUAL_API_KEY   = os.getenv("AIRVISUAL_API_KEY", "")

USE_MOCK_DATA = not (OPENWEATHER_API_KEY and AIRVISUAL_API_KEY)

if USE_MOCK_DATA:
    print("⚠️  API key tidak ditemukan — menggunakan mock data.")