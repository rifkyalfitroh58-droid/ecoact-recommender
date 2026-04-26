"""
EcoAct v1.3 — Progress Tracker Page (Streamlit multi-page)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))
import streamlit as st

st.set_page_config(page_title="Progress Tracker — EcoAct", page_icon="📊", layout="wide")

from pages.progress import show_progress_page
show_progress_page()
