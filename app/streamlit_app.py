"""
EcoAct Recommender v1.2 — Real-Time Weather & Air Quality Integration
Panel cuaca + polusi real-time, skor CB & CF dipengaruhi kondisi lingkungan
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recommender    import recommend
from cf_recommender import cf_recommend
from weather_api    import fetch_env_data
from env_context    import get_env_context

st.set_page_config(page_title="EcoAct Recommender", page_icon="🌿", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.block-container{padding-top:1.5rem;}

.hero-title{font-size:1.9rem;font-weight:700;color:#1a3a1a;line-height:1.2;margin-bottom:0.2rem;}
.hero-sub{font-size:0.9rem;color:#4a6a4a;margin-bottom:1rem;}
.version-badge{display:inline-block;background:#EAF3DE;color:#3B6D11;border-radius:20px;padding:2px 12px;font-size:0.72rem;font-weight:700;margin-bottom:.8rem;}

/* Weather panel */
.env-panel{background:#f4f7f2;border:1px solid #C0DD97;border-radius:12px;padding:1rem 1.2rem;margin-bottom:1rem;}
.env-title{font-size:0.8rem;font-weight:700;color:#27500A;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:.6rem;}
.env-metric-label{font-size:0.7rem;color:#6a8a6a;margin-bottom:2px;}
.env-metric-val{font-size:1.1rem;font-weight:700;color:#1a3a1a;}
.aqi-pill{display:inline-block;border-radius:20px;padding:3px 12px;font-size:0.78rem;font-weight:700;color:white;}
.env-status{font-size:0.82rem;color:#4a6a4a;margin-top:.5rem;padding:.5rem .8rem;background:white;border-radius:8px;border-left:3px solid #639922;}

/* modifier badge */
.mod-up{display:inline-block;background:#EAF3DE;color:#27500A;border-radius:10px;padding:0px 6px;font-size:0.68rem;font-weight:700;}
.mod-dn{display:inline-block;background:#FCEBEB;color:#A32D2D;border-radius:10px;padding:0px 6px;font-size:0.68rem;font-weight:700;}
.mod-eq{display:inline-block;background:#F1EFE8;color:#5F5E5A;border-radius:10px;padding:0px 6px;font-size:0.68rem;font-weight:700;}

/* column headers */
.col-header-cb{background:#085041;color:white;border-radius:12px 12px 0 0;padding:.75rem 1.1rem;font-size:.88rem;font-weight:700;}
.col-header-cf{background:#854F0B;color:white;border-radius:12px 12px 0 0;padding:.75rem 1.1rem;font-size:.88rem;font-weight:700;}
.col-sub{font-size:.72rem;opacity:.85;font-weight:400;}
.rec-card-cb{background:white;padding:.9rem 1.1rem;margin-bottom:7px;border-left:4px solid #1D9E75;box-shadow:0 1px 5px rgba(0,0,0,.05);}
.rec-card-cf{background:white;padding:.9rem 1.1rem;margin-bottom:7px;border-left:4px solid #BA7517;box-shadow:0 1px 5px rgba(0,0,0,.05);}
.rec-rank-cb{font-size:.68rem;font-weight:700;color:#1D9E75;text-transform:uppercase;letter-spacing:.08em;}
.rec-rank-cf{font-size:.68rem;font-weight:700;color:#BA7517;text-transform:uppercase;letter-spacing:.08em;}
.rec-name{font-size:.97rem;font-weight:700;color:#1a3a1a;margin:3px 0 5px;}
.co2-badge-cb{display:inline-block;background:#E1F5EE;color:#0F6E56;border-radius:20px;padding:2px 9px;font-size:.72rem;font-weight:700;}
.co2-badge-cf{display:inline-block;background:#FAEEDA;color:#854F0B;border-radius:20px;padding:2px 9px;font-size:.72rem;font-weight:700;}
.chip{display:inline-block;padding:1px 7px;border-radius:20px;font-size:.65rem;font-weight:500;margin-left:5px;vertical-align:middle;}
.k-transportasi{background:#E6F1FB;color:#185FA5} .k-energi{background:#FAEEDA;color:#854F0B}
.k-makanan{background:#FCEBEB;color:#A32D2D}      .k-sampah{background:#EAF3DE;color:#3B6D11}
.k-alam{background:#E1F5EE;color:#0F6E56}         .k-air{background:#EEEDFE;color:#534AB7}
.k-konsumsi{background:#FBEAF0;color:#993556}
.total-cb{background:#085041;color:white;border-radius:10px;padding:.9rem 1.1rem;text-align:center;margin-top:7px;}
.total-cf{background:#633806;color:white;border-radius:10px;padding:.9rem 1.1rem;text-align:center;margin-top:7px;}
.total-num-cb{font-size:1.9rem;font-weight:700;color:#5DCAA5;}
.total-num-cf{font-size:1.9rem;font-weight:700;color:#FAC775;}
.total-lbl{font-size:.78rem;opacity:.85;margin-top:3px;}
.compare-box{background:#f4f7f2;border:1px solid #C0DD97;border-radius:10px;padding:.9rem 1.1rem;margin-top:1.2rem;}
.compare-title{font-size:.82rem;font-weight:700;color:#27500A;margin-bottom:.4rem;}
.divider{border:none;border-top:1px solid #dce8d4;margin:1rem 0;}
.footer{font-size:.7rem;color:#9aa;text-align:center;margin-top:1.2rem;}
.mock-badge{display:inline-block;background:#FAEEDA;color:#854F0B;border-radius:20px;padding:2px 10px;font-size:.7rem;font-weight:600;margin-left:8px;}
div[data-testid="stButton"] button{background:#639922 !important;color:white !important;border:none !important;border-radius:10px !important;padding:.5rem 1.5rem !important;font-weight:700 !important;font-size:.93rem !important;width:100%;}
div[data-testid="stButton"] button:hover{background:#3B6D11 !important;}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🌿 EcoAct Recommender</div>', unsafe_allow_html=True)
st.markdown('<span class="version-badge">v1.2 — Real-Time Environment</span>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Rekomendasi dipengaruhi kondisi cuaca & kualitas udara <b>real-time</b> di kotamu — CB vs CF side-by-side.</div>', unsafe_allow_html=True)

# ── Form Input ─────────────────────────────────────────────────────────────────
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
        lokasi_kota = st.selectbox("📍 Lokasi kota",
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

    with st.spinner("Mengambil data cuaca & polusi real-time..."):
        env_data              = fetch_env_data(lokasi_kota)
        env_score, env_mods   = get_env_context(env_data)

    with st.spinner("Menjalankan dua model + env modifier..."):
        cb_recs = recommend(**user_profile, top_n=top_n, env_modifiers=env_mods)
        cf_recs = cf_recommend(user_profile, top_n=top_n, env_modifiers=env_mods)

    # ── ENV INFO PANEL ──────────────────────────────────────────────────────────
    w = env_data["weather"]
    a = env_data["air"]
    is_mock = env_data["is_mock"]
    mock_label = '<span class="mock-badge">Demo Data</span>' if is_mock else ''

    aqi_color_map = {
        "Baik": "#00B050",
        "Sedang": "#FFC000",
        "Tidak Sehat untuk Kelompok Sensitif": "#FF7E00",
        "Tidak Sehat": "#FF0000",
        "Sangat Tidak Sehat": "#8F3F97",
        "Berbahaya": "#7E0023",
    }
    aqi_col = aqi_color_map.get(a["aqi_label"], "#888")

    st.markdown(f'<div class="env-panel">', unsafe_allow_html=True)
    st.markdown(f'<div class="env-title">🌍 Kondisi Lingkungan Real-Time — {lokasi_kota.replace("_"," ").title()} {mock_label}</div>', unsafe_allow_html=True)

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        st.markdown(f'<div class="env-metric-label">Suhu</div><div class="env-metric-val">{w["temp"]}°C</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:.7rem;color:#888">Terasa {w["feels_like"]}°C</div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="env-metric-label">Kondisi</div><div class="env-metric-val" style="font-size:.92rem">{w["condition"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:.7rem;color:#888">Hujan: {w["rain_1h"]} mm/jam</div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="env-metric-label">Kelembaban</div><div class="env-metric-val">{w["humidity"]}%</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:.7rem;color:#888">Angin: {w["wind_speed"]} m/s</div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="env-metric-label">UV Index</div><div class="env-metric-val">{w["uv_index"]}</div>', unsafe_allow_html=True)
        uv_desc = "Rendah" if w["uv_index"]<3 else "Sedang" if w["uv_index"]<6 else "Tinggi" if w["uv_index"]<8 else "Sangat Tinggi"
        st.markdown(f'<div style="font-size:.7rem;color:#888">{uv_desc}</div>', unsafe_allow_html=True)
    with m5:
        st.markdown(f'<div class="env-metric-label">AQI</div><div class="env-metric-val">{a["aqi"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="aqi-pill" style="background:{aqi_col};font-size:.65rem;">{a["aqi_label"]}</span>', unsafe_allow_html=True)
    with m6:
        st.markdown(f'<div class="env-metric-label">PM2.5</div><div class="env-metric-val">{a["pm25"]} µg/m³</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:.7rem;color:#888">PM10: {a["pm10"]} µg/m³</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="env-status">{env_score.env_emoji} <b>{env_score.env_label}</b> — Env Score: {env_score.overall_env_score:.2f} &nbsp;|&nbsp; Rekomendasi aksi disesuaikan dengan kondisi ini secara otomatis.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── DAFTAR REKOMENDASI ──────────────────────────────────────────────────────
    cat_cls = {
        "transportasi":"k-transportasi","energi":"k-energi","makanan":"k-makanan",
        "sampah":"k-sampah","alam":"k-alam","air":"k-air","konsumsi":"k-konsumsi"
    }

    def mod_badge(m):
        if m > 1.05:   return f'<span class="mod-up">▲ {m:.2f}x</span>'
        elif m < 0.95: return f'<span class="mod-dn">▼ {m:.2f}x</span>'
        else:          return f'<span class="mod-eq">— {m:.2f}x</span>'

    col_cb, col_cf = st.columns(2)

    with col_cb:
        st.markdown('<div class="col-header-cb">🎯 Content-Based<div class="col-sub">Cocok berdasarkan profil + kondisi cuaca kotamu</div></div>', unsafe_allow_html=True)
        total_cb = 0
        for i, row in cb_recs.iterrows():
            cc = cat_cls.get(row["kategori"], "k-alam")
            total_cb += row["co2_hemat_kg_per_bulan"]
            st.markdown(f"""
            <div class="rec-card-cb">
                <div class="rec-rank-cb">#{i+1} · Skor {row['skor_relevansi']}% &nbsp; {mod_badge(row['env_modifier'])}</div>
                <div class="rec-name">{row['nama_aksi']}<span class="chip {cc}">{row['kategori'].upper()}</span></div>
                <span class="co2-badge-cb">🌿 {row['co2_hemat_kg_per_bulan']} kg CO₂/bln</span>
            </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="total-cb"><div class="total-num-cb">~{total_cb:.0f} kg</div><div class="total-lbl">CO₂ hemat/bulan (CB)<br>≈ {int(total_cb/1.5)} pohon 🌳</div></div>', unsafe_allow_html=True)

    with col_cf:
        st.markdown('<div class="col-header-cf">👥 Collaborative Filtering<div class="col-sub">Pola komunitas + kondisi cuaca kotamu</div></div>', unsafe_allow_html=True)
        total_cf = 0
        for i, row in cf_recs.iterrows():
            cc = cat_cls.get(row["kategori"], "k-alam")
            total_cf += row["co2_hemat_kg_per_bulan"]
            st.markdown(f"""
            <div class="rec-card-cf">
                <div class="rec-rank-cf">#{i+1} · Skor {row['cf_score']}% &nbsp; {mod_badge(row['env_modifier'])}</div>
                <div class="rec-name">{row['nama_aksi']}<span class="chip {cc}">{row['kategori'].upper()}</span></div>
                <span class="co2-badge-cf">🌿 {row['co2_hemat_kg_per_bulan']} kg CO₂/bln</span>
            </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="total-cf"><div class="total-num-cf">~{total_cf:.0f} kg</div><div class="total-lbl">CO₂ hemat/bulan (CF)<br>≈ {int(total_cf/1.5)} pohon 🌳</div></div>', unsafe_allow_html=True)

    # ── Comparison ─────────────────────────────────────────────────────────────
    cb_names = set(cb_recs["nama_aksi"]); cf_names = set(cf_recs["nama_aksi"])
    overlap  = cb_names & cf_names; only_cb = cb_names - cf_names; only_cf = cf_names - cb_names

    st.markdown('<div class="compare-box"><div class="compare-title">🔍 Analisis Perbandingan</div>', unsafe_allow_html=True)
    if overlap:   st.markdown(f"✅ **Keduanya setuju:** {', '.join(overlap)}")
    if only_cb:   st.markdown(f"🎯 **Hanya CB:** {', '.join(only_cb)}")
    if only_cf:   st.markdown(f"👥 **Hanya CF:** {', '.join(only_cf)}")

    # Dampak env modifier
    penalized = [aid for aid, m in env_mods.items() if m < 0.9]
    boosted   = [aid for aid, m in env_mods.items() if m > 1.1]
    if penalized:
        from app.env_context import ACTION_TYPE
        penalized_names = []
        try:
            import pandas as pd 
            acts = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "actions_processed.csv"))
            penalized_names = acts[acts["action_id"].isin(penalized)]["nama_aksi"].tolist()
        except: pass
        if penalized_names:
            st.markdown(f"⚠️ **Kondisi cuaca pengaruhi:** {', '.join(penalized_names[:3])} mendapat penalti skor hari ini")

    diff = abs(total_cb - total_cf)
    if diff < 5:   st.markdown(f"⚖️ Dampak CO₂ hampir sama — {total_cb:.0f} kg (CB) vs {total_cf:.0f} kg (CF) per bulan")
    elif total_cb > total_cf: st.markdown(f"🌿 CB punya dampak lebih besar hari ini — {total_cb:.0f} vs {total_cf:.0f} kg/bln")
    else:          st.markdown(f"👥 CF punya dampak lebih besar hari ini — {total_cf:.0f} vs {total_cb:.0f} kg/bln")
    st.markdown('</div>', unsafe_allow_html=True)

    mock_note = " · Data cuaca: Demo Mode (tambah API key di .env untuk real-time)" if is_mock else " · Data cuaca: Real-Time ✅"
    st.markdown(f'<div class="footer">EcoAct v1.2 · Hybrid + Real-Time Environment · 🇮🇩{mock_note}</div>', unsafe_allow_html=True)

else:
    st.info("👆 Lengkapi profil di atas, lalu klik tombol untuk melihat rekomendasi yang disesuaikan dengan cuaca & polusi hari ini!")
