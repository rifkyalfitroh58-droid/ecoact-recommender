"""
EcoAct v1.3 — Badge System
12 badge dengan kondisi pencapaian berbeda-beda.
"""

from dataclasses import dataclass
from typing import List

@dataclass
class Badge:
    id       : str
    nama     : str
    deskripsi: str
    icon     : str   # emoji representatif
    warna    : str   # hex untuk UI
    kategori : str   # co2 / streak / aksi / kategori

# ── Definisi 12 badge ─────────────────────────────────────────────────────
ALL_BADGES = [
    # CO2 Milestones
    Badge("co2_10",   "Langkah Pertama",    "Hemat 10 kg CO2 pertamamu",       "🌱", "#97C459", "co2"),
    Badge("co2_50",   "Pejuang Hijau",      "Hemat 50 kg CO2 total",           "🌿", "#639922", "co2"),
    Badge("co2_100",  "Ksatria Bumi",       "Hemat 100 kg CO2 total",          "🌍", "#27500A", "co2"),
    Badge("co2_250",  "Pahlawan Iklim",     "Hemat 250 kg CO2 total",          "🏆", "#085041", "co2"),
    Badge("co2_500",  "Legenda Lingkungan", "Hemat 500 kg CO2 total",          "👑", "#1D9E75", "co2"),
    # Streak
    Badge("streak_3", "Konsisten 3 Hari",   "Aktif 3 hari berturut-turut",     "🔥", "#BA7517", "streak"),
    Badge("streak_7", "Seminggu Penuh",     "Aktif 7 hari berturut-turut",     "⚡", "#854F0B", "streak"),
    Badge("streak_30","Bulan Tanpa Henti",  "Aktif 30 hari berturut-turut",    "💎", "#633806", "streak"),
    # Variasi aksi
    Badge("aksi_5",   "Mulai Beragam",      "Lakukan 5 jenis aksi berbeda",    "🎯", "#378ADD", "aksi"),
    Badge("aksi_10",  "Eksplorasi Penuh",   "Lakukan 10 jenis aksi berbeda",   "🚀", "#0C447C", "aksi"),
    # Kategori khusus
    Badge("transport","Pejalan Hijau",       "Lakukan 5 aksi transportasi",    "🚌", "#534AB7", "kategori"),
    Badge("energi",   "Hemat Energi",        "Lakukan 5 aksi energi",          "💡", "#993556", "kategori"),
]

BADGE_MAP = {b.id: b for b in ALL_BADGES}

# ── Cek badge baru yang diperoleh ─────────────────────────────────────────
def check_new_badges(user: dict) -> List[Badge]:
    """
    Bandingkan kondisi user dengan semua badge.
    Return list badge BARU yang baru saja diraih (belum ada di earned list).
    """
    earned    = set(user.get("badges_earned", []))
    total_co2 = user.get("total_co2_saved", 0)
    streak    = user.get("streak", 0)
    actions   = user.get("actions_done", [])
    logs      = user.get("co2_log", [])

    # Hitung aksi per kategori
    from collections import Counter
    cat_counts = Counter(log["kategori"] for log in logs)

    new_badges = []
    conditions = {
        "co2_10"   : total_co2 >= 10,
        "co2_50"   : total_co2 >= 50,
        "co2_100"  : total_co2 >= 100,
        "co2_250"  : total_co2 >= 250,
        "co2_500"  : total_co2 >= 500,
        "streak_3" : streak >= 3,
        "streak_7" : streak >= 7,
        "streak_30": streak >= 30,
        "aksi_5"   : len(set(actions)) >= 5,
        "aksi_10"  : len(set(actions)) >= 10,
        "transport": cat_counts.get("transportasi", 0) >= 5,
        "energi"   : cat_counts.get("energi", 0) >= 5,
    }

    for badge_id, condition in conditions.items():
        if condition and badge_id not in earned:
            new_badges.append(BADGE_MAP[badge_id])

    return new_badges


def award_badges(user: dict) -> tuple[dict, List[Badge]]:
    """
    Award badge baru ke user. Return (updated_user, list_badge_baru).
    """
    new_badges = check_new_badges(user)
    for badge in new_badges:
        if badge.id not in user["badges_earned"]:
            user["badges_earned"].append(badge.id)
    return user, new_badges


def get_badge_progress(user: dict) -> dict:
    """
    Return progress menuju badge berikutnya untuk ditampilkan di UI.
    """
    total_co2 = user.get("total_co2_saved", 0)
    streak    = user.get("streak", 0)
    n_actions = len(set(user.get("actions_done", [])))
    earned    = set(user.get("badges_earned", []))

    progress = []

    # CO2 milestones
    for threshold, badge_id in [(10,"co2_10"),(50,"co2_50"),(100,"co2_100"),(250,"co2_250"),(500,"co2_500")]:
        if badge_id not in earned:
            pct = min(total_co2 / threshold * 100, 100)
            progress.append({
                "badge"   : BADGE_MAP[badge_id],
                "current" : total_co2,
                "target"  : threshold,
                "pct"     : round(pct, 1),
                "unit"    : "kg CO2"
            })
            break  # hanya tampilkan yang terdekat

    # Streak
    for threshold, badge_id in [(3,"streak_3"),(7,"streak_7"),(30,"streak_30")]:
        if badge_id not in earned:
            pct = min(streak / threshold * 100, 100)
            progress.append({
                "badge"   : BADGE_MAP[badge_id],
                "current" : streak,
                "target"  : threshold,
                "pct"     : round(pct, 1),
                "unit"    : "hari"
            })
            break

    # Aksi
    for threshold, badge_id in [(5,"aksi_5"),(10,"aksi_10")]:
        if badge_id not in earned:
            pct = min(n_actions / threshold * 100, 100)
            progress.append({
                "badge"   : BADGE_MAP[badge_id],
                "current" : n_actions,
                "target"  : threshold,
                "pct"     : round(pct, 1),
                "unit"    : "jenis aksi"
            })
            break

    return progress
