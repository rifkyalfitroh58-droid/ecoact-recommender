"""
EcoAct v1.3 — Storage Engine
Simpan dan baca data progress pengguna ke/dari JSON file.
Mendukung Streamlit Cloud (st.session_state) dan lokal (file JSON).
"""

import json
import os
from datetime import datetime, date

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "user_data.json")

# ── Struktur data default per user ──────────────────────────────────────────
def default_user(username: str, profile: dict) -> dict:
    return {
        "username"        : username,
        "profile"         : profile,
        "created_at"      : datetime.now().isoformat(),
        "last_active"     : datetime.now().isoformat(),
        "co2_log"         : [],          # [{date, action_id, nama_aksi, co2, kategori}]
        "streak"          : 0,           # hari berturut-turut aktif
        "streak_last_date": None,        # tanggal terakhir check-in
        "longest_streak"  : 0,
        "badges_earned"   : [],          # list badge_id yang sudah diraih
        "total_co2_saved" : 0.0,         # kg total CO2 yang sudah dihemat
        "actions_done"    : [],          # list action_id yang pernah dilakukan
    }

# ── Load semua data ────────────────────────────────────────────────────────
def load_all() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

# ── Save semua data ────────────────────────────────────────────────────────
def save_all(data: dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── Get/create user ────────────────────────────────────────────────────────
def get_user(username: str, profile: dict = None) -> dict:
    all_data = load_all()
    key = username.lower().strip()
    if key not in all_data:
        all_data[key] = default_user(username, profile or {})
        save_all(all_data)
    else:
        # Update last_active dan profile jika diberikan
        all_data[key]["last_active"] = datetime.now().isoformat()
        if profile:
            all_data[key]["profile"] = profile
        save_all(all_data)
    return all_data[key]

# ── Log aksi harian ────────────────────────────────────────────────────────
def log_action(username: str, action_id: str, nama_aksi: str,
               co2_saved: float, kategori: str) -> dict:
    """
    Catat aksi yang sudah dilakukan pengguna hari ini.
    Return user data terbaru (sudah termasuk badge baru jika earned).
    """
    all_data = load_all()
    key = username.lower().strip()
    if key not in all_data:
        return {}

    user = all_data[key]
    today = date.today().isoformat()

    # Cek duplikasi hari ini untuk aksi yang sama
    already_logged_today = any(
        log["date"] == today and log["action_id"] == action_id
        for log in user["co2_log"]
    )
    if already_logged_today:
        return user  # tidak dicatat dua kali

    # Tambah ke log
    user["co2_log"].append({
        "date"     : today,
        "action_id": action_id,
        "nama_aksi": nama_aksi,
        "co2"      : co2_saved,
        "kategori" : kategori,
    })

    # Update total
    user["total_co2_saved"] = round(user["total_co2_saved"] + co2_saved, 2)
    if action_id not in user["actions_done"]:
        user["actions_done"].append(action_id)

    # Update streak
    user = _update_streak(user, today)

    save_all(all_data)
    return user


def _update_streak(user: dict, today: str) -> dict:
    last = user.get("streak_last_date")
    if last is None:
        user["streak"] = 1
    else:
        last_dt = date.fromisoformat(last)
        today_dt = date.fromisoformat(today)
        delta = (today_dt - last_dt).days
        if delta == 0:
            pass  # hari yang sama, tidak update streak
        elif delta == 1:
            user["streak"] += 1
        else:
            user["streak"] = 1  # streak putus
    user["streak_last_date"] = today
    user["longest_streak"] = max(user.get("longest_streak", 0), user["streak"])
    return user


# ── Leaderboard ────────────────────────────────────────────────────────────
def get_leaderboard(top_n: int = 10) -> list:
    """Return list user diurutkan berdasarkan total CO2 saved (descending)."""
    all_data = load_all()
    board = []
    for key, user in all_data.items():
        board.append({
            "username"       : user["username"],
            "total_co2_saved": user["total_co2_saved"],
            "streak"         : user.get("streak", 0),
            "badges_count"   : len(user.get("badges_earned", [])),
            "actions_count"  : len(user.get("actions_done", [])),
        })
    board.sort(key=lambda x: x["total_co2_saved"], reverse=True)
    return board[:top_n]


def get_weekly_co2(username: str) -> float:
    """Hitung total CO2 yang dihemat user dalam 7 hari terakhir."""
    from datetime import timedelta
    all_data = load_all()
    key = username.lower().strip()
    if key not in all_data:
        return 0.0
    user = all_data[key]
    cutoff = (date.today() - timedelta(days=7)).isoformat()
    return round(sum(
        log["co2"] for log in user["co2_log"] if log["date"] >= cutoff
    ), 2)


# ── Statistik user ─────────────────────────────────────────────────────────
def get_user_stats(username: str) -> dict:
    """Return statistik lengkap seorang user untuk ditampilkan di UI."""
    all_data = load_all()
    key = username.lower().strip()
    if key not in all_data:
        return {}
    user = all_data[key]

    # CO2 per bulan (30 hari terakhir)
    from datetime import timedelta
    cutoff_month = (date.today() - timedelta(days=30)).isoformat()
    co2_month = round(sum(
        log["co2"] for log in user["co2_log"] if log["date"] >= cutoff_month
    ), 2)

    # CO2 per minggu
    co2_week = get_weekly_co2(username)

    # Kategori favorit
    from collections import Counter
    cats = [log["kategori"] for log in user["co2_log"]]
    top_cat = Counter(cats).most_common(1)[0][0] if cats else "-"

    # Aktivitas per hari (untuk chart)
    daily = {}
    for log in user["co2_log"]:
        d = log["date"]
        daily[d] = round(daily.get(d, 0) + log["co2"], 2)

    return {
        "total_co2"   : user["total_co2_saved"],
        "co2_month"   : co2_month,
        "co2_week"    : co2_week,
        "streak"      : user.get("streak", 0),
        "longest"     : user.get("longest_streak", 0),
        "badges"      : user.get("badges_earned", []),
        "actions_done": user.get("actions_done", []),
        "top_category": top_cat,
        "daily_co2"   : daily,
        "log"         : user["co2_log"][-20:][::-1],  # 20 aksi terakhir
        "trees"       : int(user["total_co2_saved"] / 1.5),
    }


# ── TEST ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== TEST Storage Engine ===")
    profile = {"transportasi":"motor","tempat_tinggal":"kos","konsumsi_listrik":"sedang",
               "pola_makan":"banyak_daging","lokasi_kota":"kota_besar"}

    # Buat user demo
    for name in ["budi", "ani", "doni", "sari"]:
        u = get_user(name, profile)
        # Log beberapa aksi
        import random
        actions = [
            ("A01","Beralih ke transportasi umum",42.0,"transportasi"),
            ("A04","Kurangi konsumsi daging merah",20.0,"makanan"),
            ("A08","Pasang solar panel",35.0,"energi"),
            ("A03","Gunakan sepeda",15.0,"transportasi"),
            ("A09","Pisahkan sampah",6.0,"sampah"),
        ]
        for aid, nama, co2, kat in random.sample(actions, random.randint(2,4)):
            log_action(name, aid, nama, co2, kat)

    lb = get_leaderboard(5)
    print("\nLeaderboard Top-5:")
    for i, u in enumerate(lb, 1):
        print(f"  #{i} {u['username']:10} | CO2: {u['total_co2_saved']:5.1f} kg | Streak: {u['streak']} hari")

    stats = get_user_stats("budi")
    print(f"\nStats Budi: total={stats['total_co2']}kg | streak={stats['streak']} | trees={stats['trees']}")
    print("✅ Storage Engine berjalan sempurna!")
