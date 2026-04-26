"""
EcoAct Recommender v1.3 — Hybrid + Real-Time + Gamification
Login username → Rekomendasi → Progress Tracker (halaman terpisah)
"""
import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recommender    import recommend
from cf_recommender import cf_recommend
from weather_api    import fetch_env_data
from env_context    import get_env_context
from storage        import get_user, log_action, load_all, save_all
from badges         import award_badges

st.set_page_config(page_title="EcoAct Recommender", page_icon="🌿", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.block-container{padding-top:1.5rem;}
.hero-title{font-size:1.9rem;font-weight:700;color:#1a3a1a;line-height:1.2;margin-bottom:0.2rem;}
.hero-sub{font-size:0.9rem;color:#4a6a4a;margin-bottom:1rem;}
.version-badge{display:inline-block;background:#EAF3DE;color:#3B6D11;border-radius:20px;padding:2px 12px;font-size:0.72rem;font-weight:700;margin-bottom:.8rem;}
.login-box{background:#f4f7f2;border:1px solid #C0DD97;border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem;}
.user-pill{display:inline-block;background:#EAF3DE;color:#27500A;border-radius:20px;padding:3px 14px;font-size:.82rem;font-weight:700;}
.env-panel{background:#f4f7f2;border:1px solid #C0DD97;border-radius:12px;padding:.9rem 1.2rem;margin-bottom:1rem;}
.env-title{font-size:0.78rem;font-weight:700;color:#27500A;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:.5rem;}
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
.compare-box{background:#f4f7f2;border:1px solid #C0DD97;border-radius:10px;padding:.9rem 1.1rem;margin-top:1rem;}
.mod-up{display:inline-block;background:#EAF3DE;color:#27500A;border-radius:10px;padding:0px 6px;font-size:.65rem;font-weight:700;}
.mod-dn{display:inline-block;background:#FCEBEB;color:#A32D2D;border-radius:10px;padding:0px 6px;font-size:.65rem;font-weight:700;}
.mod-eq{display:inline-block;background:#F1EFE8;color:#5F5E5A;border-radius:10px;padding:0px 6px;font-size:.65rem;font-weight:700;}
.divider{border:none;border-top:1px solid #dce8d4;margin:1rem 0;}
.footer{font-size:.7rem;color:#9aa;text-align:center;margin-top:1.2rem;}
div[data-testid="stButton"] button{background:#639922 !important;color:white !important;border:none !important;border-radius:10px !important;padding:.5rem 1.5rem !important;font-weight:700 !important;font-size:.93rem !important;width:100%;}
</style>
""", unsafe_allow_html=True)

# ── LOGIN ──────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🌿 EcoAct Recommender</div>', unsafe_allow_html=True)
st.markdown('<span class="version-badge">v1.3 — Gamification</span>', unsafe_allow_html=True)

if "username" not in st.session_state or not st.session_state["username"]:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("**👤 Masuk dengan Username**")
    st.markdown("Username digunakan untuk menyimpan progress CO₂ dan badge kamu.")
    col_u, col_b = st.columns([3,1])
    with col_u:
        uname = st.text_input("Username", placeholder="contoh: budi123", label_visibility="collapsed")
    with col_b:
        if st.button("Masuk"):
            if uname.strip():
                st.session_state["username"] = uname.strip()
                st.rerun()
            else:
                st.error("Username tidak boleh kosong!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

username = st.session_state["username"]
st.markdown(f'<div class="hero-sub">Halo, <span class="user-pill">👤 {username}</span> &nbsp;|&nbsp; Rekomendasi dipengaruhi cuaca & polusi real-time di kotamu.</div>', unsafe_allow_html=True)

if st.button("🚪 Logout", key="logout"):
    st.session_state["username"] = ""
    st.rerun()

# ── FORM PROFIL ────────────────────────────────────────────────────────────
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
    profile = {"transportasi":transportasi,"tempat_tinggal":tempat_tinggal,
               "konsumsi_listrik":konsumsi_listrik,"pola_makan":pola_makan,"lokasi_kota":lokasi_kota}
    get_user(username, profile)

    with st.spinner("Mengambil data cuaca & polusi..."):
        env_data            = fetch_env_data(lokasi_kota)
        env_score, env_mods = get_env_context(env_data)
    with st.spinner("Menjalankan dua model..."):
        cb_recs = recommend(**profile, top_n=top_n, env_modifiers=env_mods)
        cf_recs = cf_recommend(profile, top_n=top_n, env_modifiers=env_mods)

    # ENV PANEL
    w = env_data["weather"]; a = env_data["air"]
    is_mock = env_data["is_mock"]
    mock_lbl = ' <span style="font-size:.68rem;background:#FAEEDA;color:#854F0B;border-radius:10px;padding:1px 8px;margin-left:6px">Demo Data</span>' if is_mock else ""
    aqi_col_map = {"Baik":"#00B050","Sedang":"#FFC000","Tidak Sehat untuk Kelompok Sensitif":"#FF7E00","Tidak Sehat":"#FF0000","Sangat Tidak Sehat":"#8F3F97","Berbahaya":"#7E0023"}
    aqi_col = aqi_col_map.get(a["aqi_label"],"#888")

    st.markdown(f'<div class="env-panel"><div class="env-title">🌍 Kondisi Real-Time — {lokasi_kota.replace("_"," ").title()}{mock_lbl}</div></div>', unsafe_allow_html=True)
    m1,m2,m3,m4,m5,m6 = st.columns(6)
    for col,label,val,sub in [
        (m1,"Suhu",f"{w['temp']}°C",f"Terasa {w['feels_like']}°C"),
        (m2,"Kondisi",w['condition'],f"Hujan {w['rain_1h']}mm/jam"),
        (m3,"Kelembaban",f"{w['humidity']}%",f"Angin {w['wind_speed']} m/s"),
        (m4,"UV Index",str(w['uv_index']),"Tinggi" if w['uv_index']>=8 else "Sedang" if w['uv_index']>=4 else "Rendah"),
        (m5,"AQI",str(a['aqi']),a['aqi_label']),
        (m6,"PM2.5",f"{a['pm25']} µg/m³",f"PM10: {a['pm10']}"),
    ]:
        col.markdown(f'<div style="font-size:.7rem;color:#6a8a6a">{label}</div><div style="font-size:1.05rem;font-weight:700;color:#1a3a1a">{val}</div><div style="font-size:.68rem;color:#888">{sub}</div>', unsafe_allow_html=True)

    st.markdown(f'<div style="margin-top:.6rem;font-size:.82rem;color:#4a6a4a;background:white;border-radius:8px;padding:.5rem .8rem;border-left:3px solid #639922">{env_score.env_emoji} <b>{env_score.env_label}</b></div>', unsafe_allow_html=True)

    # REKOMENDASI
    cat_cls = {"transportasi":"k-transportasi","energi":"k-energi","makanan":"k-makanan","sampah":"k-sampah","alam":"k-alam","air":"k-air","konsumsi":"k-konsumsi"}
    def mod_b(m): return f'<span class="mod-up">▲{m:.2f}x</span>' if m>1.05 else f'<span class="mod-dn">▼{m:.2f}x</span>' if m<0.95 else f'<span class="mod-eq">—{m:.2f}x</span>'

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    col_cb, col_cf = st.columns(2)

    with col_cb:
        st.markdown('<div class="col-header-cb">🎯 Content-Based<div class="col-sub">Cocok berdasarkan profil + cuaca</div></div>', unsafe_allow_html=True)
        total_cb = 0
        for i, row in cb_recs.iterrows():
            cc = cat_cls.get(row["kategori"],"k-alam")
            total_cb += row["co2_hemat_kg_per_bulan"]
            logged = st.checkbox(f"Sudah dilakukan ✓", key=f"cb_{row['action_id']}", label_visibility="collapsed")
            if logged:
                result = log_action(username, row["action_id"], row["nama_aksi"], row["co2_hemat_kg_per_bulan"], row["kategori"])
                all_d = load_all(); usr = all_d.get(username.lower(),{}); usr, nb = award_badges(usr); all_d[username.lower()]=usr; save_all(all_d)
                if nb:
                    st.balloons()
                    for b in nb: st.success(f"🎉 Badge baru: {b.icon} {b.nama}!")
            st.markdown(f"""<div class="rec-card-cb">
                <div class="rec-rank-cb">#{i+1} · {row['skor_relevansi']}% &nbsp;{mod_b(row['env_modifier'])}</div>
                <div class="rec-name">{row['nama_aksi']}<span class="chip {cc}">{row['kategori'].upper()}</span></div>
                <span class="co2-badge-cb">🌿 {row['co2_hemat_kg_per_bulan']} kg CO₂/bln</span>
            </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="total-cb"><div class="total-num-cb">~{total_cb:.0f} kg</div><div class="total-lbl">CO₂ hemat/bulan · ≈{int(total_cb/1.5)} pohon 🌳</div></div>', unsafe_allow_html=True)

    with col_cf:
        st.markdown('<div class="col-header-cf">👥 Collaborative Filtering<div class="col-sub">Pola komunitas + cuaca</div></div>', unsafe_allow_html=True)
        total_cf = 0
        for i, row in cf_recs.iterrows():
            cc = cat_cls.get(row["kategori"],"k-alam")
            total_cf += row["co2_hemat_kg_per_bulan"]
            logged = st.checkbox(f"Sudah dilakukan ✓", key=f"cf_{row['action_id']}", label_visibility="collapsed")
            if logged:
                log_action(username, row["action_id"], row["nama_aksi"], row["co2_hemat_kg_per_bulan"], row["kategori"])
            st.markdown(f"""<div class="rec-card-cf">
                <div class="rec-rank-cf">#{i+1} · {row['cf_score']}% &nbsp;{mod_b(row['env_modifier'])}</div>
                <div class="rec-name">{row['nama_aksi']}<span class="chip {cc}">{row['kategori'].upper()}</span></div>
                <span class="co2-badge-cf">🌿 {row['co2_hemat_kg_per_bulan']} kg CO₂/bln</span>
            </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="total-cf"><div class="total-num-cf">~{total_cf:.0f} kg</div><div class="total-lbl">CO₂ hemat/bulan · ≈{int(total_cf/1.5)} pohon 🌳</div></div>', unsafe_allow_html=True)

    # Comparison
    cb_names = set(cb_recs["nama_aksi"]); cf_names = set(cf_recs["nama_aksi"])
    overlap = cb_names & cf_names; only_cb = cb_names-cf_names; only_cf = cf_names-cb_names
    st.markdown('<div class="compare-box">', unsafe_allow_html=True)
    if overlap: st.markdown(f"✅ **Keduanya setuju:** {', '.join(overlap)}")
    if only_cb: st.markdown(f"🎯 **Hanya CB:** {', '.join(only_cb)}")
    if only_cf: st.markdown(f"👥 **Hanya CF:** {', '.join(only_cf)}")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="footer">EcoAct v1.3 · Lihat progress lengkapmu di halaman <b>Progress Tracker</b> (menu kiri) 📊</div>', unsafe_allow_html=True)

else:
    st.info("👆 Lengkapi profil di atas, lalu klik tombol untuk melihat rekomendasimu!")
