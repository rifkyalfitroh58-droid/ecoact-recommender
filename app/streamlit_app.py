"""
EcoAct Recommender — Streamlit App
Aplikasi rekomendasi aksi ramah lingkungan yang dipersonalisasi
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recommender import recommend

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EcoAct Recommender",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── CSS Custom ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .main { background: #f4f7f2; }
    .block-container { padding-top: 2rem; max-width: 700px; }

    .hero-title {
        font-size: 2.2rem; font-weight: 700; color: #1a3a1a;
        line-height: 1.2; margin-bottom: 0.3rem;
    }
    .hero-sub {
        font-size: 1rem; color: #4a6a4a; margin-bottom: 2rem;
    }

    .rec-card {
        background: white;
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #639922;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }
    .rec-rank { font-size: 0.75rem; font-weight: 700; color: #639922; text-transform: uppercase; letter-spacing: 0.08em; }
    .rec-name { font-size: 1.1rem; font-weight: 700; color: #1a3a1a; margin: 4px 0; }
    .rec-meta { font-size: 0.85rem; color: #6a8a6a; }
    .co2-badge {
        display: inline-block;
        background: #EAF3DE; color: #3B6D11;
        border-radius: 20px; padding: 3px 12px;
        font-size: 0.8rem; font-weight: 700;
        margin-top: 6px;
    }
    .total-box {
        background: #1a3a1a; color: white;
        border-radius: 14px; padding: 1.2rem 1.5rem;
        text-align: center; margin-top: 1.5rem;
    }
    .total-num { font-size: 2.5rem; font-weight: 700; color: #97C459; }
    .total-label { font-size: 0.9rem; color: #9FE1CB; margin-top: 4px; }

    .kategori-chip {
        display: inline-block;
        padding: 2px 10px; border-radius: 20px;
        font-size: 0.72rem; font-weight: 500;
        margin-left: 8px; vertical-align: middle;
    }
    .k-transportasi { background: #E6F1FB; color: #185FA5; }
    .k-energi       { background: #FAEEDA; color: #854F0B; }
    .k-makanan      { background: #FCEBEB; color: #A32D2D; }
    .k-sampah        { background: #EAF3DE; color: #3B6D11; }
    .k-alam          { background: #E1F5EE; color: #0F6E56; }
    .k-air           { background: #EEEDFE; color: #534AB7; }
    .k-konsumsi      { background: #FBEAF0; color: #993556; }

    div[data-testid="stSelectbox"] label { font-weight: 500; color: #1a3a1a; }
    div[data-testid="stButton"] button {
        background: #639922 !important; color: white !important;
        border: none !important; border-radius: 10px !important;
        padding: 0.6rem 2rem !important; font-weight: 700 !important;
        font-size: 1rem !important; width: 100%;
    }
    div[data-testid="stButton"] button:hover { background: #3B6D11 !important; }

    .divider { border: none; border-top: 1px solid #dce8d4; margin: 1.5rem 0; }
    .footer { font-size: 0.75rem; color: #9aa; text-align: center; margin-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🌿 EcoAct Recommender</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Temukan aksi nyata yang paling cocok buat kamu — dipersonalisasi berdasarkan gaya hidupmu.</div>', unsafe_allow_html=True)

# ── Form Input ────────────────────────────────────────────────────────────────
st.markdown("### 📋 Profil Gaya Hidupmu")

col1, col2 = st.columns(2)
with col1:
    transportasi = st.selectbox(
        "🚗 Transportasi sehari-hari",
        ["motor", "mobil", "angkot/bus", "jalan_kaki", "sepeda"],
        format_func=lambda x: {
            "motor": "🏍️ Motor", "mobil": "🚗 Mobil",
            "angkot/bus": "🚌 Angkot / Bus", "jalan_kaki": "🚶 Jalan Kaki",
            "sepeda": "🚲 Sepeda"
        }[x]
    )
    konsumsi_listrik = st.selectbox(
        "⚡ Konsumsi listrik",
        ["rendah", "sedang", "tinggi"],
        index=1,
        format_func=lambda x: {
            "rendah": "🔋 Rendah (< 50 kWh/bulan)",
            "sedang": "⚡ Sedang (50–150 kWh/bulan)",
            "tinggi": "🔌 Tinggi (> 150 kWh/bulan)"
        }[x]
    )
    pola_makan = st.selectbox(
        "🍽️ Pola makan",
        ["banyak_daging", "campuran", "vegetarian"],
        index=1,
        format_func=lambda x: {
            "banyak_daging": "🥩 Banyak Daging",
            "campuran": "🍱 Campuran",
            "vegetarian": "🥦 Vegetarian / Vegan"
        }[x]
    )

with col2:
    tempat_tinggal = st.selectbox(
        "🏠 Tempat tinggal",
        ["kos", "rumah_pribadi", "apartemen", "rumah_kontrakan"],
        format_func=lambda x: {
            "kos": "🛏️ Kos-kosan",
            "rumah_pribadi": "🏡 Rumah Pribadi",
            "apartemen": "🏢 Apartemen",
            "rumah_kontrakan": "🏘️ Rumah Kontrakan"
        }[x]
    )
    lokasi_kota = st.selectbox(
        "📍 Lokasi kota",
        ["kota_besar", "kota_kecil", "pedesaan"],
        format_func=lambda x: {
            "kota_besar": "🏙️ Kota Besar (Jakarta, Surabaya...)",
            "kota_kecil": "🌆 Kota Kecil / Menengah",
            "pedesaan": "🌾 Pedesaan / Pinggiran"
        }[x]
    )
    top_n = st.slider("📊 Jumlah rekomendasi", min_value=2, max_value=5, value=3)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Submit ────────────────────────────────────────────────────────────────────
if st.button("🌱 Tampilkan Rekomendasiku"):
    with st.spinner("Menganalisis profil kamu..."):
        recs = recommend(transportasi, tempat_tinggal, konsumsi_listrik, pola_makan, lokasi_kota, top_n=top_n)

    st.markdown(f"### 🎯 Top-{top_n} Aksi Lingkungan Untukmu")

    cat_colors = {
        "transportasi": "k-transportasi",
        "energi"      : "k-energi",
        "makanan"     : "k-makanan",
        "sampah"      : "k-sampah",
        "alam"        : "k-alam",
        "air"         : "k-air",
        "konsumsi"    : "k-konsumsi",
    }

    total_co2 = 0
    for i, row in recs.iterrows():
        cat_class = cat_colors.get(row['kategori'], 'k-alam')
        total_co2 += row['co2_hemat_kg_per_bulan']
        st.markdown(f"""
        <div class="rec-card">
            <div class="rec-rank">Rekomendasi #{i+1} &nbsp;•&nbsp; Relevansi {row['skor_relevansi']}%</div>
            <div class="rec-name">
                {row['nama_aksi']}
                <span class="kategori-chip {cat_class}">{row['kategori'].upper()}</span>
            </div>
            <div class="rec-meta">Mulai dari langkah kecil setiap harinya</div>
            <div class="co2-badge">🌿 Hemat {row['co2_hemat_kg_per_bulan']} kg CO₂ / bulan</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="total-box">
        <div class="total-num">~{total_co2:.0f} kg</div>
        <div class="total-label">Total CO₂ yang bisa kamu kurangi per bulan<br>
        Setara menanam <strong>{int(total_co2 / 1.5)} pohon</strong> 🌳</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="footer">EcoAct v1.0 · Data emisi berbasis laporan IEA & IPCC · Dibuat untuk studi kasus nyata Indonesia 🇮🇩</div>', unsafe_allow_html=True)

else:
    st.info("👆 Lengkapi profilmu di atas, lalu klik tombol untuk melihat rekomendasimu!")
