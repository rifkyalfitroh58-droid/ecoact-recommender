"""
EcoAct Recommender v1.3 — Single Page dengan Tab
Tab 1: Rekomendasi | Tab 2: Progress Tracker
"""
import streamlit as st
import pandas as pd
import sys, os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recommender    import recommend, actions as all_actions
from cf_recommender import cf_recommend
from weather_api    import fetch_env_data
from env_context    import get_env_context
from storage        import get_user, log_action, load_all, save_all, get_user_stats, get_leaderboard
from badges         import award_badges, get_badge_progress, ALL_BADGES

st.set_page_config(page_title="EcoAct Recommender", page_icon="🌿", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.block-container{padding-top:1.5rem;}

.hero-title{font-size:1.9rem;font-weight:700;color:#1a3a1a;line-height:1.2;margin-bottom:.2rem;}
.version-badge{display:inline-block;background:#EAF3DE;color:#3B6D11;border-radius:20px;padding:2px 12px;font-size:.72rem;font-weight:700;margin-bottom:.8rem;}
.user-pill{display:inline-block;background:#EAF3DE;color:#27500A;border-radius:20px;padding:3px 14px;font-size:.82rem;font-weight:700;}
.login-box{background:#f4f7f2;border:1px solid #C0DD97;border-radius:12px;padding:1.2rem 1.5rem;margin-bottom:1rem;}

/* ENV */
.env-panel{background:#f4f7f2;border:1px solid #C0DD97;border-radius:12px;padding:.9rem 1.2rem;margin-bottom:1rem;}
.env-title{font-size:.78rem;font-weight:700;color:#27500A;text-transform:uppercase;letter-spacing:.06em;margin-bottom:.5rem;}

/* REC CARDS */
.col-header-cb{background:#085041;color:white;border-radius:12px 12px 0 0;padding:.75rem 1.1rem;font-size:.88rem;font-weight:700;}
.col-header-cf{background:#854F0B;color:white;border-radius:12px 12px 0 0;padding:.75rem 1.1rem;font-size:.88rem;font-weight:700;}
.col-sub{font-size:.72rem;opacity:.85;font-weight:400;}
.rec-card-cb{background:white;padding:.9rem 1.1rem;margin-bottom:4px;border-left:4px solid #1D9E75;box-shadow:0 1px 5px rgba(0,0,0,.05);}
.rec-card-cf{background:white;padding:.9rem 1.1rem;margin-bottom:4px;border-left:4px solid #BA7517;box-shadow:0 1px 5px rgba(0,0,0,.05);}
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

/* PROGRESS */
.stat-card{background:white;border:1px solid #dce8d4;border-radius:12px;padding:1rem 1.2rem;text-align:center;}
.stat-num{font-size:2rem;font-weight:700;color:#27500A;line-height:1.1;}
.stat-lbl{font-size:.78rem;color:#6a8a6a;margin-top:4px;}
.streak-box{background:#FAEEDA;border:1px solid #EF9F27;border-radius:10px;padding:.8rem 1.2rem;text-align:center;}
.streak-num{font-size:2.5rem;font-weight:700;color:#633806;}
.streak-lbl{font-size:.8rem;color:#854F0B;margin-top:2px;}
.badge-card{background:white;border:1px solid #dce8d4;border-radius:10px;padding:.8rem;text-align:center;}
.badge-card.earned{border-color:#639922;background:#f4f9ed;}
.badge-card.locked{opacity:0.45;filter:grayscale(60%);}
.badge-icon{font-size:1.8rem;margin-bottom:4px;}
.badge-name{font-size:.75rem;font-weight:700;color:#27500A;}
.badge-desc{font-size:.68rem;color:#6a8a6a;margin-top:2px;}
.log-item{background:white;border-left:3px solid #639922;padding:.6rem .9rem;margin-bottom:6px;border-radius:0 8px 8px 0;font-size:.82rem;}
.lb-row{display:flex;align-items:center;gap:12px;padding:.55rem .9rem;border-radius:8px;margin-bottom:5px;background:white;border:1px solid #dce8d4;}
.lb-rank{font-size:1.1rem;font-weight:700;color:#639922;min-width:28px;}
.lb-name{flex:1;font-size:.88rem;font-weight:500;color:#1a3a1a;}
.lb-co2{font-size:.88rem;font-weight:700;color:#27500A;}
.lb-streak{font-size:.75rem;color:#888;margin-left:8px;}
.lb-you{background:#EAF3DE;border-color:#97C459;}
.progress-bar-bg{background:#f0f0f0;border-radius:20px;height:8px;margin:6px 0 2px;}
.progress-bar-fill{height:8px;border-radius:20px;background:linear-gradient(90deg,#97C459,#27500A);}
.section-title{font-size:1rem;font-weight:700;color:#1a3a1a;margin:1.2rem 0 .6rem;padding-bottom:.3rem;border-bottom:2px solid #EAF3DE;}
.new-badge-banner{background:#EAF3DE;border:1.5px solid #639922;border-radius:10px;padding:.8rem 1.2rem;margin-bottom:1rem;text-align:center;}

.divider{border:none;border-top:1px solid #dce8d4;margin:.8rem 0;}
.footer{font-size:.7rem;color:#9aa;text-align:center;margin-top:1.2rem;}
div[data-testid="stButton"] button{background:#639922 !important;color:white !important;border:none !important;border-radius:10px !important;padding:.5rem 1.5rem !important;font-weight:700 !important;font-size:.93rem !important;width:100%;}
</style>
""", unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🌿 EcoAct Recommender</div>', unsafe_allow_html=True)
st.markdown('<span class="version-badge">v1.3 — Gamification</span>', unsafe_allow_html=True)

# ── LOGIN ──────────────────────────────────────────────────────────────────
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
col_h1, col_h2 = st.columns([5,1])
with col_h1:
    st.markdown(f'Halo, <span class="user-pill">👤 {username}</span>', unsafe_allow_html=True)
with col_h2:
    if st.button("🚪 Logout"):
        for k in ["username","cb_recs","cf_recs","env_data","env_score","env_mods"]:
            st.session_state.pop(k, None)
        st.rerun()

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# TAB
# ══════════════════════════════════════════════════════
tab1, tab2 = st.tabs(["🌱 Rekomendasi", "📊 Progress & Badge"])

# ══════════════════════════════════════════════════════
# TAB 1 — REKOMENDASI
# ══════════════════════════════════════════════════════
with tab1:
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

with st.expander("🔍 Filter Aksi (Opsional)", expanded=False):
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        filter_kesulitan = st.multiselect("Kesulitan",["mudah","sedang","sulit"],
            default=["mudah","sedang","sulit"],
            format_func=lambda x:{"mudah":"🟢 Mudah","sedang":"🟡 Sedang","sulit":"🔴 Sulit"}[x])
    with fc2:
        filter_biaya = st.multiselect("Biaya",["gratis","murah","investasi"],
            default=["gratis","murah","investasi"],
            format_func=lambda x:{"gratis":"🆓 Gratis","murah":"💰 Murah","investasi":"💳 Investasi"}[x])
    with fc3:
        filter_waktu = st.multiselect("Waktu",["harian","mingguan","bulanan","sekali"],
            default=["harian","mingguan","bulanan","sekali"],
            format_func=lambda x:{"harian":"📅 Harian","mingguan":"📆 Mingguan","bulanan":"🗓️ Bulanan","sekali":"⚡ Sekali"}[x])
    with fc4:
        semua_kat = sorted(all_actions["kategori"].unique().tolist())
        filter_kategori = st.multiselect("Kategori",semua_kat,default=semua_kat)

    if st.button("🌱 Tampilkan & Bandingkan Rekomendasiku"):
        profile = {"transportasi":transportasi,"tempat_tinggal":tempat_tinggal,
                   "konsumsi_listrik":konsumsi_listrik,"pola_makan":pola_makan,"lokasi_kota":lokasi_kota}
        get_user(username, profile)
        with st.spinner("Mengambil data cuaca & polusi..."):
            env_data            = fetch_env_data(lokasi_kota)
            env_score, env_mods = get_env_context(env_data)
        with st.spinner("Menjalankan dua model..."):
            cb_recs = recommend(**profile, top_n=top_n, env_modifiers=env_mods,
                            filter_kesulitan=filter_kesulitan if filter_kesulitan else None,
                            filter_biaya=filter_biaya if filter_biaya else None,
                            filter_waktu=filter_waktu if filter_waktu else None,
                            filter_kategori=filter_kategori if filter_kategori else None)
            cf_recs = cf_recommend(profile, top_n=top_n, env_modifiers=env_mods)

        if cb_recs is None or cb_recs.empty:
            st.warning("Tidak ada aksi yang cocok dengan filter yang dipilih. Coba longgarkan filter kesulitan, biaya, waktu, atau kategori.")
            st.stop()

        st.session_state["cb_recs"]   = cb_recs
        st.session_state["cf_recs"]   = cf_recs
        st.session_state["env_data"]  = env_data
        st.session_state["env_score"] = env_score
        st.session_state["env_mods"]  = env_mods

    if "cb_recs" in st.session_state:
        cb_recs   = st.session_state["cb_recs"]
        cf_recs   = st.session_state["cf_recs"]
        env_data  = st.session_state["env_data"]
        env_score = st.session_state["env_score"]

        # ENV PANEL
        w = env_data["weather"]; a = env_data["air"]
        is_mock  = env_data["is_mock"]
        mock_lbl = ' <span style="font-size:.68rem;background:#FAEEDA;color:#854F0B;border-radius:10px;padding:1px 8px;margin-left:6px">Demo Data</span>' if is_mock else ""
        aqi_col_map = {"Baik":"#00B050","Sedang":"#FFC000","Tidak Sehat untuk Kelompok Sensitif":"#FF7E00","Tidak Sehat":"#FF0000","Sangat Tidak Sehat":"#8F3F97","Berbahaya":"#7E0023"}

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
                kes_emoji = {"mudah":"🟢","sedang":"🟡","sulit":"🔴"}.get(row.get("kesulitan",""),"")
                biaya_emoji = {"gratis":"🆓","murah":"💰","investasi":"💳"}.get(row.get("biaya",""),"")
                waktu_emoji = {"harian":"📅","mingguan":"📆","bulanan":"🗓️","sekali":"⚡"}.get(row.get("waktu",""),"")
                subkat = row.get("sub_kategori","")
                st.markdown(f"""<div class="rec-card-cb">
                    <div class="rec-rank-cb">#{i+1} · {row['skor_relevansi']}% &nbsp;{mod_b(row['env_modifier'])}</div>
                    <div class="rec-name">{row['nama_aksi']}<span class="chip {cc}">{row['kategori'].upper()}</span></div>
                    <div style="font-size:.7rem;color:#888;margin:3px 0">{subkat.replace('_',' ')}</div>
                    <span class="co2-badge-cb">🌿 {row['co2_hemat_kg_per_bulan']} kg CO₂/bln</span>
                    &nbsp;<span style="font-size:.7rem;color:#888">{kes_emoji} {row.get('kesulitan','')} &nbsp;{biaya_emoji} {row.get('biaya','')} &nbsp;{waktu_emoji} {row.get('waktu','')}</span>
                </div>""", unsafe_allow_html=True)
                if st.checkbox("✓ Sudah saya lakukan hari ini", key=f"cb_{row['action_id']}"):
                    log_action(username, row["action_id"], row["nama_aksi"], row["co2_hemat_kg_per_bulan"], row["kategori"])
                    all_d = load_all(); usr = all_d.get(username.lower(),{}); usr, nb = award_badges(usr); all_d[username.lower()]=usr; save_all(all_d)
                    if nb:
                        st.balloons()
                        for b in nb: st.success(f"🎉 Badge baru: {b.icon} {b.nama}!")
            st.markdown(f'<div class="total-cb"><div class="total-num-cb">~{total_cb:.0f} kg</div><div class="total-lbl">CO₂ hemat/bulan · ≈{int(total_cb/1.5)} pohon 🌳</div></div>', unsafe_allow_html=True)

        with col_cf:
            st.markdown('<div class="col-header-cf">👥 Collaborative Filtering<div class="col-sub">Pola komunitas + cuaca</div></div>', unsafe_allow_html=True)
            total_cf = 0
            for i, row in cf_recs.iterrows():
                cc = cat_cls.get(row["kategori"],"k-alam")
                total_cf += row["co2_hemat_kg_per_bulan"]
                kes_emoji2 = {"mudah":"🟢","sedang":"🟡","sulit":"🔴"}.get(row.get("kesulitan",""),"")
                biaya_emoji2 = {"gratis":"🆓","murah":"💰","investasi":"💳"}.get(row.get("biaya",""),"")
                waktu_emoji2 = {"harian":"📅","mingguan":"📆","bulanan":"🗓️","sekali":"⚡"}.get(row.get("waktu",""),"")
                subkat2 = row.get("sub_kategori","")
                st.markdown(f"""<div class="rec-card-cf">
                    <div class="rec-rank-cf">#{i+1} · {row['cf_score']}% &nbsp;{mod_b(row['env_modifier'])}</div>
                    <div class="rec-name">{row['nama_aksi']}<span class="chip {cc}">{row['kategori'].upper()}</span></div>
                    <div style="font-size:.7rem;color:#888;margin:3px 0">{subkat2.replace('_',' ')}</div>
                    <span class="co2-badge-cf">🌿 {row['co2_hemat_kg_per_bulan']} kg CO₂/bln</span>
                    &nbsp;<span style="font-size:.7rem;color:#888">{kes_emoji2} {row.get('kesulitan','')} &nbsp;{biaya_emoji2} {row.get('biaya','')} &nbsp;{waktu_emoji2} {row.get('waktu','')}</span>
                </div>""", unsafe_allow_html=True)
                if st.checkbox("✓ Sudah saya lakukan hari ini", key=f"cf_{row['action_id']}"):
                    log_action(username, row["action_id"], row["nama_aksi"], row["co2_hemat_kg_per_bulan"], row["kategori"])
            st.markdown(f'<div class="total-cf"><div class="total-num-cf">~{total_cf:.0f} kg</div><div class="total-lbl">CO₂ hemat/bulan · ≈{int(total_cf/1.5)} pohon 🌳</div></div>', unsafe_allow_html=True)

        cb_names = set(cb_recs["nama_aksi"]); cf_names = set(cf_recs["nama_aksi"])
        overlap = cb_names & cf_names; only_cb = cb_names-cf_names; only_cf = cf_names-cb_names
        st.markdown('<div class="compare-box">', unsafe_allow_html=True)
        if overlap: st.markdown(f"✅ **Keduanya setuju:** {', '.join(overlap)}")
        if only_cb: st.markdown(f"🎯 **Hanya CB:** {', '.join(only_cb)}")
        if only_cf: st.markdown(f"👥 **Hanya CF:** {', '.join(only_cf)}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="footer">EcoAct v1.3 · Pindah ke tab 📊 untuk lihat progress & badge kamu!</div>', unsafe_allow_html=True)
    else:
        st.info("👆 Lengkapi profil di atas, lalu klik tombol untuk melihat rekomendasimu!")

# ══════════════════════════════════════════════════════
# TAB 2 — PROGRESS & BADGE
# ══════════════════════════════════════════════════════
with tab2:
    stats    = get_user_stats(username)
    all_data = load_all()
    user     = all_data.get(username.lower(), {})

    # Cek badge baru
    user, new_badges = award_badges(user)
    if new_badges:
        all_data[username.lower()] = user
        save_all(all_data)
        for b in new_badges:
            st.markdown(f'<div class="new-badge-banner">🎉 Badge baru: <b>{b.icon} {b.nama}</b> — {b.deskripsi}</div>', unsafe_allow_html=True)

    # STAT CARDS
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.markdown(f'<div class="stat-card"><div class="stat-num">{stats.get("total_co2",0):.1f}</div><div class="stat-lbl">kg CO₂ Total</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-card"><div class="stat-num">{stats.get("co2_month",0):.1f}</div><div class="stat-lbl">kg CO₂ Bulan Ini</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="stat-card"><div class="stat-num">{stats.get("co2_week",0):.1f}</div><div class="stat-lbl">kg CO₂ Minggu Ini</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="stat-card"><div class="stat-num">{stats.get("trees",0)}</div><div class="stat-lbl">Pohon Setara 🌳</div></div>', unsafe_allow_html=True)
    with c5: st.markdown(f'<div class="stat-card"><div class="stat-num">{len(stats.get("actions_done",[]))}</div><div class="stat-lbl">Jenis Aksi</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # STREAK + CHART
    col_l, col_r = st.columns([1,2])
    with col_l:
        streak  = stats.get("streak",0)
        longest = stats.get("longest",0)
        st.markdown(f"""<div class="streak-box">
            <div style="font-size:2rem">{"🔥" if streak>0 else "💤"}</div>
            <div class="streak-num">{streak}</div>
            <div class="streak-lbl">hari streak aktif</div>
            <div style="font-size:.72rem;color:#888;margin-top:6px">Terpanjang: {longest} hari</div>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="section-title">14 Hari Terakhir</div>', unsafe_allow_html=True)
        daily   = stats.get("daily_co2", {})
        cols7   = st.columns(7)
        today   = date.today()
        for i in range(14):
            d   = (today - timedelta(days=13-i)).isoformat()
            co2 = daily.get(d, 0)
            lbl = (today - timedelta(days=13-i)).strftime("%d")
            if co2 > 0:
                clr = "#27500A" if co2>=30 else "#639922" if co2>=10 else "#97C459"
                cols7[i%7].markdown(f'<div style="background:{clr};border-radius:4px;padding:4px;text-align:center;margin-bottom:4px"><span style="font-size:.7rem;color:white;font-weight:700">{lbl}</span></div>', unsafe_allow_html=True)
            else:
                cols7[i%7].markdown(f'<div style="background:#f0f0f0;border-radius:4px;padding:4px;text-align:center;margin-bottom:4px"><span style="font-size:.7rem;color:#aaa">{lbl}</span></div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="section-title">CO₂ Harian (30 Hari Terakhir)</div>', unsafe_allow_html=True)
        if daily:
            dates = sorted(daily.keys())[-30:]
            df_chart = pd.DataFrame({"Tanggal": dates, "CO₂ (kg)": [daily[d] for d in dates]})
            st.bar_chart(df_chart.set_index("Tanggal"), color="#639922", height=200)
        else:
            st.info("Belum ada data. Centang aksi di tab Rekomendasi untuk mulai mencatat!")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # BADGE GALLERY
    st.markdown('<div class="section-title">🏅 Badge Pencapaian</div>', unsafe_allow_html=True)
    earned_ids = set(stats.get("badges",[]))
    badge_cols = st.columns(6)
    for i, badge in enumerate(ALL_BADGES):
        is_earned = badge.id in earned_ids
        with badge_cols[i%6]:
            st.markdown(f"""<div class="badge-card {"earned" if is_earned else "locked"}">
                <div class="badge-icon">{badge.icon if is_earned else "🔒"}</div>
                <div class="badge-name">{badge.nama}</div>
                <div class="badge-desc">{badge.deskripsi}</div>
            </div>""", unsafe_allow_html=True)

    progress = get_badge_progress(user)
    if progress:
        st.markdown('<div class="section-title">🎯 Menuju Badge Berikutnya</div>', unsafe_allow_html=True)
        for prog in progress[:3]:
            b = prog["badge"]; pct = prog["pct"]
            st.markdown(f"""<div style="background:white;border:1px solid #dce8d4;border-radius:10px;padding:.8rem 1.2rem;margin-bottom:.5rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-size:.88rem;font-weight:700;color:#1a3a1a">{b.icon} {b.nama}</span>
                    <span style="font-size:.78rem;color:#639922;font-weight:700">{prog['current']} / {prog['target']} {prog['unit']}</span>
                </div>
                <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%"></div></div>
                <div style="font-size:.7rem;color:#888;margin-top:3px">{pct:.0f}% selesai</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # LOG + INPUT + LEADERBOARD
    col_log, col_input, col_lb = st.columns([1.5,1,1])

    with col_log:
        st.markdown('<div class="section-title">📋 Riwayat Aksi</div>', unsafe_allow_html=True)
        log = stats.get("log",[])
        if log:
            for item in log[:10]:
                st.markdown(f'<div class="log-item"><span style="color:#888;font-size:.7rem">{item["date"]}</span> · {item["nama_aksi"]} · <span style="color:#27500A;font-weight:700">+{item["co2"]} kg CO₂</span></div>', unsafe_allow_html=True)
        else:
            st.info("Belum ada aksi tercatat.")

    with col_input:
        st.markdown('<div class="section-title">✅ Catat Aksi Hari Ini</div>', unsafe_allow_html=True)
        try:
            BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            acts_df = pd.read_csv(os.path.join(BASE,"data","actions_processed.csv"))
            aksi_opts = dict(zip(acts_df["nama_aksi"], zip(acts_df["action_id"],acts_df["co2_hemat_kg_per_bulan"],acts_df["kategori"])))
            chosen  = st.selectbox("Pilih aksi:", list(aksi_opts.keys()), label_visibility="collapsed")
            if st.button("✅ Catat"):
                aid, co2, kat = aksi_opts[chosen]
                log_action(username, aid, chosen, co2, kat)
                all_d = load_all(); usr = all_d.get(username.lower(),{}); usr, nb = award_badges(usr); all_d[username.lower()]=usr; save_all(all_d)
                st.success(f"+{co2} kg CO₂ 🌿")
                if nb:
                    st.balloons()
                    for b in nb: st.success(f"🎉 {b.icon} {b.nama}!")
                st.rerun()
        except Exception as e:
            st.error(str(e))

    with col_lb:
        st.markdown('<div class="section-title">🏆 Leaderboard</div>', unsafe_allow_html=True)
        lb     = get_leaderboard(10)
        medals = ["🥇","🥈","🥉"]
        for i, u in enumerate(lb):
            rank_icon = medals[i] if i<3 else f"#{i+1}"
            is_you    = u["username"].lower() == username.lower()
            you_tag   = ' <span style="font-size:.65rem;background:#639922;color:white;border-radius:10px;padding:1px 6px">Kamu</span>' if is_you else ""
            st.markdown(f"""<div class="{"lb-row lb-you" if is_you else "lb-row"}">
                <span class="lb-rank">{rank_icon}</span>
                <span class="lb-name">{u["username"]}{you_tag}</span>
                <span class="lb-co2">{u["total_co2_saved"]:.1f}kg</span>
                <span class="lb-streak">🔥{u["streak"]}</span>
            </div>""", unsafe_allow_html=True)
