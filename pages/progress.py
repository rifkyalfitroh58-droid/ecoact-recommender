"""
EcoAct v1.3 — Halaman Progress Tracker
Halaman terpisah: CO2 chart, badge gallery, streak calendar, leaderboard, log aksi.
"""

import streamlit as st
import pandas as pd
import sys, os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.storage import get_user_stats, get_leaderboard, log_action, get_user, load_all, save_all
from app.badges  import award_badges, get_badge_progress, BADGE_MAP, ALL_BADGES

# ── CSS ────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.block-container{padding-top:1.5rem;}

.stat-card{background:white;border:1px solid #dce8d4;border-radius:12px;padding:1rem 1.2rem;text-align:center;height:100%;}
.stat-num{font-size:2rem;font-weight:700;color:#27500A;line-height:1.1;}
.stat-lbl{font-size:0.78rem;color:#6a8a6a;margin-top:4px;}

.badge-card{background:white;border:1px solid #dce8d4;border-radius:10px;padding:.8rem;text-align:center;}
.badge-card.earned{border-color:#639922;background:#f4f9ed;}
.badge-card.locked{opacity:0.45;filter:grayscale(60%);}
.badge-icon{font-size:1.8rem;margin-bottom:4px;}
.badge-name{font-size:.75rem;font-weight:700;color:#27500A;}
.badge-desc{font-size:.68rem;color:#6a8a6a;margin-top:2px;}

.log-item{background:white;border-left:3px solid #639922;padding:.6rem .9rem;margin-bottom:6px;border-radius:0 8px 8px 0;font-size:.82rem;}
.log-date{color:#888;font-size:.7rem;}
.log-co2{color:#27500A;font-weight:700;}

.lb-row{display:flex;align-items:center;gap:12px;padding:.55rem .9rem;border-radius:8px;margin-bottom:5px;background:white;border:1px solid #dce8d4;}
.lb-rank{font-size:1.1rem;font-weight:700;color:#639922;min-width:28px;}
.lb-name{flex:1;font-size:.88rem;font-weight:500;color:#1a3a1a;}
.lb-co2{font-size:.88rem;font-weight:700;color:#27500A;}
.lb-streak{font-size:.75rem;color:#888;margin-left:8px;}
.lb-you{background:#EAF3DE;border-color:#97C459;}

.progress-bar-bg{background:#f0f0f0;border-radius:20px;height:8px;margin:6px 0 2px;}
.progress-bar-fill{height:8px;border-radius:20px;background:linear-gradient(90deg,#97C459,#27500A);}

.streak-box{background:#FAEEDA;border:1px solid #EF9F27;border-radius:10px;padding:.8rem 1.2rem;text-align:center;}
.streak-num{font-size:2.5rem;font-weight:700;color:#633806;}
.streak-lbl{font-size:.8rem;color:#854F0B;margin-top:2px;}

.section-title{font-size:1rem;font-weight:700;color:#1a3a1a;margin:1.2rem 0 .6rem;padding-bottom:.3rem;border-bottom:2px solid #EAF3DE;}
.new-badge-banner{background:#EAF3DE;border:1.5px solid #639922;border-radius:10px;padding:.8rem 1.2rem;margin-bottom:1rem;text-align:center;}
.divider{border:none;border-top:1px solid #dce8d4;margin:.8rem 0;}

div[data-testid="stButton"] button{background:#639922 !important;color:white !important;border:none !important;border-radius:8px !important;padding:.4rem 1.2rem !important;font-weight:700 !important;}
</style>""", unsafe_allow_html=True)


# ── Halaman utama Progress Tracker ────────────────────────────────────────
def show_progress_page():
    inject_css()

    username = st.session_state.get("username", "")
    if not username:
        st.warning("Silakan login dulu dari halaman Rekomendasi.")
        return

    # Ambil stats terbaru
    stats  = get_user_stats(username)
    all_data = load_all()
    user   = all_data.get(username.lower(), {})

    # Cek badge baru
    user, new_badges = award_badges(user)
    if new_badges:
        all_data[username.lower()] = user
        save_all(all_data)
        for b in new_badges:
            st.markdown(f"""<div class="new-badge-banner">
                🎉 Badge baru diraih: <b>{b.icon} {b.nama}</b> — {b.deskripsi}
            </div>""", unsafe_allow_html=True)

    # ── HEADER ─────────────────────────────────────────────────────────────
    st.markdown(f"### 📊 Progress Tracker — {username}")

    # ── STAT CARDS ─────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{stats.get("total_co2",0):.1f}</div><div class="stat-lbl">kg CO₂ Total</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{stats.get("co2_month",0):.1f}</div><div class="stat-lbl">kg CO₂ Bulan Ini</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{stats.get("co2_week",0):.1f}</div><div class="stat-lbl">kg CO₂ Minggu Ini</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{stats.get("trees",0)}</div><div class="stat-lbl">Pohon Setara 🌳</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{len(stats.get("actions_done",[]))}</div><div class="stat-lbl">Jenis Aksi Dilakukan</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── STREAK + CO2 CHART ─────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 2])

    with col_left:
        streak = stats.get("streak", 0)
        longest = stats.get("longest", 0)
        st.markdown(f"""<div class="streak-box">
            <div style="font-size:2rem">{"🔥" if streak>0 else "💤"}</div>
            <div class="streak-num">{streak}</div>
            <div class="streak-lbl">hari streak aktif</div>
            <div style="font-size:.72rem;color:#888;margin-top:6px">Terpanjang: {longest} hari</div>
        </div>""", unsafe_allow_html=True)

        # Calendar heatmap sederhana (14 hari terakhir)
        st.markdown('<div class="section-title">14 Hari Terakhir</div>', unsafe_allow_html=True)
        daily = stats.get("daily_co2", {})
        cols = st.columns(7)
        today = date.today()
        for i in range(14):
            d = (today - timedelta(days=13-i)).isoformat()
            co2 = daily.get(d, 0)
            col_idx = i % 7
            day_label = (today - timedelta(days=13-i)).strftime("%d")
            if co2 > 0:
                color = "#27500A" if co2 >= 30 else "#639922" if co2 >= 10 else "#97C459"
                cols[col_idx].markdown(f'<div style="background:{color};border-radius:4px;padding:4px;text-align:center;margin-bottom:4px;"><span style="font-size:.7rem;color:white;font-weight:700">{day_label}</span></div>', unsafe_allow_html=True)
            else:
                cols[col_idx].markdown(f'<div style="background:#f0f0f0;border-radius:4px;padding:4px;text-align:center;margin-bottom:4px;"><span style="font-size:.7rem;color:#aaa">{day_label}</span></div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-title">CO₂ Harian (30 Hari Terakhir)</div>', unsafe_allow_html=True)
        daily = stats.get("daily_co2", {})
        if daily:
            dates = sorted(daily.keys())[-30:]
            vals  = [daily[d] for d in dates]
            df_chart = pd.DataFrame({"Tanggal": dates, "CO₂ (kg)": vals})
            st.bar_chart(df_chart.set_index("Tanggal"), color="#639922", height=200)
        else:
            st.info("Belum ada data. Mulai catat aksimu di tab Rekomendasi!")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── BADGE GALLERY ──────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🏅 Badge Pencapaian</div>', unsafe_allow_html=True)

    earned_ids = set(stats.get("badges", []))
    badge_cols = st.columns(6)
    for i, badge in enumerate(ALL_BADGES):
        is_earned = badge.id in earned_ids
        status    = "earned" if is_earned else "locked"
        with badge_cols[i % 6]:
            st.markdown(f"""<div class="badge-card {status}">
                <div class="badge-icon">{badge.icon if is_earned else "🔒"}</div>
                <div class="badge-name">{badge.nama}</div>
                <div class="badge-desc">{badge.deskripsi}</div>
            </div>""", unsafe_allow_html=True)

    # Progress ke badge berikutnya
    progress = get_badge_progress(user)
    if progress:
        st.markdown('<div class="section-title">🎯 Menuju Badge Berikutnya</div>', unsafe_allow_html=True)
        for prog in progress[:3]:
            b = prog["badge"]
            pct = prog["pct"]
            st.markdown(f"""
            <div style="background:white;border:1px solid #dce8d4;border-radius:10px;padding:.8rem 1.2rem;margin-bottom:.5rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-size:.88rem;font-weight:700;color:#1a3a1a">{b.icon} {b.nama}</span>
                    <span style="font-size:.78rem;color:#639922;font-weight:700">{prog['current']} / {prog['target']} {prog['unit']}</span>
                </div>
                <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%"></div></div>
                <div style="font-size:.7rem;color:#888;margin-top:3px">{pct:.0f}% selesai</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── LOG AKSI HARIAN + INPUT BARU ──────────────────────────────────────
    col_log, col_input = st.columns([1.5, 1])

    with col_log:
        st.markdown('<div class="section-title">📋 Riwayat Aksi Terbaru</div>', unsafe_allow_html=True)
        log = stats.get("log", [])
        if log:
            for item in log[:10]:
                st.markdown(f"""<div class="log-item">
                    <span class="log-date">{item['date']}</span>
                    &nbsp;·&nbsp; {item['nama_aksi']}
                    &nbsp;·&nbsp; <span class="log-co2">+{item['co2']} kg CO₂</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Belum ada aksi yang dicatat.")

    with col_input:
        st.markdown('<div class="section-title">✅ Catat Aksi Hari Ini</div>', unsafe_allow_html=True)
        # Load daftar aksi
        
        try:
            acts_df = pd.read_csv(os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", "actions_processed.csv"
            ))
            aksi_opts = dict(zip(acts_df["nama_aksi"], zip(acts_df["action_id"], acts_df["co2_hemat_kg_per_bulan"], acts_df["kategori"])))
            chosen = st.selectbox("Pilih aksi yang sudah kamu lakukan:", list(aksi_opts.keys()))
            if st.button("✅ Catat Aksi Ini"):
                aid, co2, kat = aksi_opts[chosen]
                result = log_action(username, aid, chosen, co2, kat)
                all_data2 = load_all()
                user2 = all_data2.get(username.lower(), {})
                user2, new_b = award_badges(user2)
                all_data2[username.lower()] = user2
                save_all(all_data2)
                st.success(f"Tercatat! +{co2} kg CO₂ dihemat 🌿")
                if new_b:
                    for b in new_b:
                        st.balloons()
                        st.success(f"🎉 Badge baru: {b.icon} {b.nama}!")
                st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── LEADERBOARD ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🏆 Leaderboard — Top 10</div>', unsafe_allow_html=True)
    lb = get_leaderboard(10)
    medals = ["🥇","🥈","🥉"]
    for i, u in enumerate(lb):
        rank_icon = medals[i] if i < 3 else f"#{i+1}"
        is_you    = u["username"].lower() == username.lower()
        you_tag   = ' <span style="font-size:.7rem;background:#639922;color:white;border-radius:10px;padding:1px 7px;margin-left:4px">Kamu</span>' if is_you else ""
        cls       = "lb-row lb-you" if is_you else "lb-row"
        st.markdown(f"""<div class="{cls}">
            <span class="lb-rank">{rank_icon}</span>
            <span class="lb-name">{u['username']}{you_tag}</span>
            <span class="lb-co2">{u['total_co2_saved']:.1f} kg CO₂</span>
            <span class="lb-streak">🔥 {u['streak']} hari</span>
            <span class="lb-streak">🏅 {u['badges_count']} badge</span>
        </div>""", unsafe_allow_html=True)
