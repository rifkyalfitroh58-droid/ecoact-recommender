"""
EcoAct Recommender v1.1 — Hybrid: CB vs CF Side-by-Side
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recommender    import recommend
from cf_recommender import cf_recommend

st.set_page_config(
    page_title="EcoAct Recommender",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.block-container { padding-top: 1.8rem; }

.hero-title  { font-size: 2rem; font-weight: 700; color: #1a3a1a; line-height: 1.2; margin-bottom: 0.2rem; }
.hero-sub    { font-size: 0.95rem; color: #4a6a4a; margin-bottom: 1.5rem; }
.version-badge { display:inline-block; background:#EAF3DE; color:#3B6D11; border-radius:20px; padding:2px 12px; font-size:0.75rem; font-weight:700; margin-bottom:1rem; }

.col-header-cb { background:#085041; color:white; border-radius:12px 12px 0 0; padding:0.8rem 1.2rem; font-size:0.9rem; font-weight:700; }
.col-header-cf { background:#854F0B; color:white; border-radius:12px 12px 0 0; padding:0.8rem 1.2rem; font-size:0.9rem; font-weight:700; }
.col-sub { font-size:0.75rem; opacity:0.85; font-weight:400; }

.rec-card-cb { background:white; padding:1rem 1.2rem; margin-bottom:8px; border-left:4px solid #1D9E75; box-shadow:0 1px 6px rgba(0,0,0,0.05); }
.rec-card-cf { background:white; padding:1rem 1.2rem; margin-bottom:8px; border-left:4px solid #BA7517; box-shadow:0 1px 6px rgba(0,0,0,0.05); }
.rec-rank-cb { font-size:0.7rem; font-weight:700; color:#1D9E75; text-transform:uppercase; letter-spacing:0.08em; }
.rec-rank-cf { font-size:0.7rem; font-weight:700; color:#BA7517; text-transform:uppercase; letter-spacing:0.08em; }
.rec-name    { font-size:1rem; font-weight:700; color:#1a3a1a; margin:3px 0 5px; }
.co2-badge-cb { display:inline-block; background:#E1F5EE; color:#0F6E56; border-radius:20px; padding:2px 10px; font-size:0.75rem; font-weight:700; }
.co2-badge-cf { display:inline-block; background:#FAEEDA; color:#854F0B; border-radius:20px; padding:2px 10px; font-size:0.75rem; font-weight:700; }

.chip { display:inline-block; padding:1px 8px; border-radius:20px; font-size:0.68rem; font-weight:500; margin-left:6px; vertical-align:middle; }
.k-transportasi{background:#E6F1FB;color:#185FA5} .k-energi{background:#FAEEDA;color:#854F0B}
.k-makanan{background:#FCEBEB;color:#A32D2D}      .k-sampah{background:#EAF3DE;color:#3B6D11}
.k-alam{background:#E1F5EE;color:#0F6E56}         .k-air{background:#EEEDFE;color:#534AB7}
.k-konsumsi{background:#FBEAF0;color:#993556}

.total-cb { background:#085041; color:white; border-radius:10px; padding:1rem 1.2rem; text-align:center; margin-top:8px; }
.total-cf { background:#633806; color:white; border-radius:10px; padding:1rem 1.2rem; text-align:center; margin-top:8px; }
.total-num-cb { font-size:2rem; font-weight:700; color:#5DCAA5; }
.total-num-cf { font-size:2rem; font-weight:700; color:#FAC775; }
.total-lbl    { font-size:0.8rem; opacity:0.85; margin-top:3px; }

.compare-box  { background:#f4f7f2; border:1px solid #C0DD97; border-radius:10px; padding:1rem 1.2rem; margin-top:1.5rem; }
.compare-title{ font-size:0.85rem; font-weight:700; color:#27500A; margin-bottom:0.5rem; }
.divider { border:none; border-top:1px solid #dce8d4; margin:1.2rem 0; }
.footer  { font-size:0.72rem; color:#9aa; text-align:center; margin-top:1.5rem; }

div[data-testid="stButton"] button { background:#639922 !important; color:white !important; border:none !important; border-radius:10px !important; padding:0.5rem 1.5rem !important; font-weight:700 !important; font-size:0.95rem !important; width:100%; }
div[data-testid="stButton"] button:hover { background:#3B6D11 !important; }
div[data-testid="stSelectbox"] label { font-weight:500; color:#1a3a1a; font-size:0.9rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-title">🌿 EcoAct Recommender</div>', unsafe_allow_html=True)
st.markdown('<span class="version-badge">v1.1 — Hybrid Model</span>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Bandingkan dua pendekatan: <b>Content-Based</b> (berdasarkan profilmu) vs <b>Collaborative Filtering</b> (berdasarkan pola orang yang mirip kamu).</div>', unsafe_allow_html=True)

with st.expander("📋 Isi Profil Gaya Hidupmu", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        transportasi = st.selectbox("🚗 Transportasi",
            ["motor","mobil","angkot/bus","jalan_kaki","sepeda"],
            format_func=lambda x: {"motor":"🏍️ Motor","mobil":"🚗 Mobil","angkot/bus":"🚌 Angkot/Bus","jalan_kaki":"🚶 Jalan Kaki","sepeda":"🚲 Sepeda"}[x])
        konsumsi_listrik = st.selectbox("⚡ Konsumsi listrik",
            ["rendah","sedang","tinggi"], index=1,
            format_func=lambda x: {"rendah":"🔋 Rendah","sedang":"⚡ Sedang","tinggi":"🔌 Tinggi"}[x])
    with c2:
        tempat_tinggal = st.selectbox("🏠 Tempat tinggal",
            ["kos","rumah_pribadi","apartemen","rumah_kontrakan"],
            format_func=lambda x: {"kos":"🛏️ Kos","rumah_pribadi":"🏡 Rumah Pribadi","apartemen":"🏢 Apartemen","rumah_kontrakan":"🏘️ Kontrakan"}[x])
        pola_makan = st.selectbox("🍽️ Pola makan",
            ["banyak_daging","campuran","vegetarian"], index=1,
            format_func=lambda x: {"banyak_daging":"🥩 Banyak Daging","campuran":"🍱 Campuran","vegetarian":"🥦 Vegetarian"}[x])
    with c3:
        lokasi_kota = st.selectbox("📍 Lokasi",
            ["kota_besar","kota_kecil","pedesaan"],
            format_func=lambda x: {"kota_besar":"🏙️ Kota Besar","kota_kecil":"🌆 Kota Kecil","pedesaan":"🌾 Pedesaan"}[x])
        top_n = st.slider("📊 Jumlah rekomendasi", 2, 5, 3)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

if st.button("🌱 Tampilkan & Bandingkan Rekomendasiku"):
    user_profile = {
        "transportasi": transportasi, "tempat_tinggal": tempat_tinggal,
        "konsumsi_listrik": konsumsi_listrik, "pola_makan": pola_makan,
        "lokasi_kota": lokasi_kota,
    }

    with st.spinner("Menjalankan dua model sekaligus..."):
        cb_recs = recommend(**user_profile, top_n=top_n)
        cf_recs = cf_recommend(user_profile, top_n=top_n)

    cat_cls = {
        "transportasi":"k-transportasi","energi":"k-energi","makanan":"k-makanan",
        "sampah":"k-sampah","alam":"k-alam","air":"k-air","konsumsi":"k-konsumsi"
    }

    col_cb, col_cf = st.columns(2)

    with col_cb:
        st.markdown('<div class="col-header-cb">🎯 Content-Based Filtering<div class="col-sub">Cocok berdasarkan profil gaya hidupmu</div></div>', unsafe_allow_html=True)
        total_cb = 0
        for i, row in cb_recs.iterrows():
            cc = cat_cls.get(row["kategori"], "k-alam")
            total_cb += row["co2_hemat_kg_per_bulan"]
            st.markdown(f"""
            <div class="rec-card-cb">
                <div class="rec-rank-cb">#{i+1} · Relevansi {row['skor_relevansi']}%</div>
                <div class="rec-name">{row['nama_aksi']}<span class="chip {cc}">{row['kategori'].upper()}</span></div>
                <span class="co2-badge-cb">🌿 {row['co2_hemat_kg_per_bulan']} kg CO₂/bln</span>
            </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="total-cb"><div class="total-num-cb">~{total_cb:.0f} kg</div><div class="total-lbl">CO₂ bisa dihemat/bulan (CB)<br>≈ {int(total_cb/1.5)} pohon 🌳</div></div>', unsafe_allow_html=True)

    with col_cf:
        st.markdown('<div class="col-header-cf">👥 Collaborative Filtering<div class="col-sub">Dilakukan orang dengan profil serupa kamu</div></div>', unsafe_allow_html=True)
        total_cf = 0
        for i, row in cf_recs.iterrows():
            cc = cat_cls.get(row["kategori"], "k-alam")
            total_cf += row["co2_hemat_kg_per_bulan"]
            st.markdown(f"""
            <div class="rec-card-cf">
                <div class="rec-rank-cf">#{i+1} · Skor CF {row['cf_score']}%</div>
                <div class="rec-name">{row['nama_aksi']}<span class="chip {cc}">{row['kategori'].upper()}</span></div>
                <span class="co2-badge-cf">🌿 {row['co2_hemat_kg_per_bulan']} kg CO₂/bln</span>
            </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="total-cf"><div class="total-num-cf">~{total_cf:.0f} kg</div><div class="total-lbl">CO₂ bisa dihemat/bulan (CF)<br>≈ {int(total_cf/1.5)} pohon 🌳</div></div>', unsafe_allow_html=True)

    # Comparison insight
    cb_names = set(cb_recs["nama_aksi"].tolist())
    cf_names = set(cf_recs["nama_aksi"].tolist())
    overlap  = cb_names & cf_names
    only_cb  = cb_names - cf_names
    only_cf  = cf_names - cb_names

    st.markdown('<div class="compare-box"><div class="compare-title">🔍 Analisis Perbandingan</div>', unsafe_allow_html=True)
    if overlap:
        st.markdown(f"✅ **Keduanya setuju:** {', '.join(overlap)}")
    if only_cb:
        st.markdown(f"🎯 **Hanya CB:** {', '.join(only_cb)}")
    if only_cf:
        st.markdown(f"👥 **Hanya CF:** {', '.join(only_cf)}")
    diff = abs(total_cb - total_cf)
    if diff < 5:
        st.markdown(f"⚖️ Potensi CO₂ **hampir sama** — {total_cb:.0f} kg (CB) vs {total_cf:.0f} kg (CF) per bulan")
    elif total_cb > total_cf:
        st.markdown(f"🌿 CB punya dampak CO₂ lebih besar — {total_cb:.0f} vs {total_cf:.0f} kg/bln")
    else:
        st.markdown(f"👥 CF punya dampak CO₂ lebih besar — {total_cf:.0f} vs {total_cb:.0f} kg/bln")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">EcoAct v1.1 · Hybrid: Content-Based + Collaborative Filtering · 🇮🇩</div>', unsafe_allow_html=True)

else:
    st.info("👆 Lengkapi profil di atas, lalu klik tombol untuk membandingkan dua model!")
