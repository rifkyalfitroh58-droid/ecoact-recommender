"""
EcoAct v1.1 — User-Based Collaborative Filtering
Menemukan K nearest neighbors berdasarkan pola interaksi,
lalu mengagregasi skor mereka untuk rekomendasi.
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Load data ─────────────────────────────────────────────────────────────────
users        = pd.read_csv(os.path.join(BASE_DIR, "data", "users.csv"))
interactions = pd.read_csv(os.path.join(BASE_DIR, "data", "interactions.csv"))
_v14 = os.path.join(BASE_DIR, "data", "actions_v14.csv")
_v10 = os.path.join(BASE_DIR, "data", "actions_processed.csv")
actions = pd.read_csv(_v14 if os.path.exists(_v14) else _v10)

USER_IDS   = users["user_id"].tolist()
ACTION_IDS = actions["action_id"].tolist()

# ── Build User–Item Matrix ────────────────────────────────────────────────────
def build_user_item_matrix():
    """
    Pivot interactions → matrix (users × actions).
    Nilai: combined_score (0–1), NaN jika tidak ada interaksi.
    """
    matrix = interactions.pivot_table(
        index="user_id",
        columns="action_id",
        values="combined_score",
        aggfunc="mean"
    )
    # Pastikan semua action_id ada sebagai kolom
    for aid in ACTION_IDS:
        if aid not in matrix.columns:
            matrix[aid] = np.nan
    matrix = matrix[ACTION_IDS]   # urutan konsisten
    return matrix

# ── CF Recommender ────────────────────────────────────────────────────────────
def cf_recommend(user_profile: dict, top_n: int = 3, k_neighbors: int = 20, env_modifiers: dict = None):
    """
    Rekomendasikan aksi menggunakan User-Based CF.

    Alur:
    1. Cari user existing yang paling mirip profil (gunakan encoded features)
    2. Dari K neighbors, ambil aksi yang belum pernah mereka interaksikan
       (atau yang paling tinggi rata-rata combined_score-nya)
    3. Return top-N aksi beserta skor CF

    user_profile: dict dengan kunci transportasi, tempat_tinggal,
                  konsumsi_listrik, pola_makan, lokasi_kota
    """
    matrix = build_user_item_matrix()

    # ── Encode profil input ke vektor (sama persis dengan CB encoder) ─────────
    transport_vals = ["angkot/bus","jalan_kaki","mobil","motor","sepeda"]
    tinggal_vals   = ["apartemen","kos","rumah_kontrakan","rumah_pribadi"]
    listrik_vals   = ["rendah","sedang","tinggi"]
    makan_vals     = ["banyak_daging","campuran","vegetarian"]
    kota_vals      = ["kota_besar","kota_kecil","pedesaan"]

    def encode(profile):
        vec = []
        for v in transport_vals: vec.append(int(profile["transportasi"] == v))
        for v in tinggal_vals:   vec.append(int(profile["tempat_tinggal"] == v))
        for v in listrik_vals:   vec.append(int(profile["konsumsi_listrik"] == v))
        for v in makan_vals:     vec.append(int(profile["pola_makan"] == v))
        for v in kota_vals:      vec.append(int(profile["lokasi_kota"] == v))
        return np.array(vec, dtype=float)

    # Encode semua existing users
    user_vecs = []
    for _, row in users.iterrows():
        user_vecs.append(encode({
            "transportasi"    : row["transportasi"],
            "tempat_tinggal"  : row["tempat_tinggal"],
            "konsumsi_listrik": row["konsumsi_listrik"],
            "pola_makan"      : row["pola_makan"],
            "lokasi_kota"     : row["lokasi_kota"],
        }))
    user_matrix = np.array(user_vecs)

    # Encode input user
    input_vec = encode(user_profile).reshape(1, -1)

    # Hitung similarity antara input user dan semua existing users
    sims = cosine_similarity(input_vec, user_matrix).flatten()

    # Ambil K neighbors terdekat (exclude skor 0)
    k = min(k_neighbors, len(sims))
    neighbor_idx = sims.argsort()[::-1][:k]
    neighbor_ids = [users.iloc[i]["user_id"] for i in neighbor_idx]
    neighbor_sims = sims[neighbor_idx]

    # ── Agregasi skor dari neighbors ─────────────────────────────────────────
    cf_scores = {}
    for aid in ACTION_IDS:
        weighted_sum = 0.0
        weight_total = 0.0
        for uid, sim in zip(neighbor_ids, neighbor_sims):
            if uid in matrix.index:
                score = matrix.loc[uid, aid]
                if not np.isnan(score) and sim > 0:
                    weighted_sum += sim * score
                    weight_total += sim
        if weight_total > 0:
            cf_scores[aid] = weighted_sum / weight_total
        else:
            cf_scores[aid] = 0.0

    # ── Gabungkan dengan info aksi ────────────────────────────────────────────
    result_rows = []
    for _, act in actions.iterrows():
        aid = act["action_id"]
        result_rows.append({
            "action_id"             : aid,
            "nama_aksi"             : act["nama_aksi"],
            "kategori"              : act["kategori"],
            "sub_kategori"          : act.get("sub_kategori", ""),
            "co2_hemat_kg_per_bulan": act["co2_hemat_kg_per_bulan"],
            "kesulitan"             : act.get("kesulitan", ""),
            "biaya"                 : act.get("biaya", ""),
            "waktu"                 : act.get("waktu", ""),
            "cf_score"              : round(cf_scores.get(aid, 0.0) * 100, 1),
        })

    # Terapkan env modifier ke setiap aksi
    for r in result_rows:
        mod = env_modifiers.get(r["action_id"], 1.0) if env_modifiers else 1.0
        r["cf_score"]     = round(r["cf_score"] * mod, 1)
        r["env_modifier"] = round(float(mod), 2)

    df = pd.DataFrame(result_rows)
    df = df.sort_values("cf_score", ascending=False).head(top_n).reset_index(drop=True)
    return df


# ── TEST ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("TEST — User-Based Collaborative Filtering")
    print("=" * 60)

    test_profiles = [
        {
            "transportasi": "motor", "tempat_tinggal": "kos",
            "konsumsi_listrik": "sedang", "pola_makan": "banyak_daging",
            "lokasi_kota": "kota_besar", "label": "Anak kos + motor + daging"
        },
        {
            "transportasi": "mobil", "tempat_tinggal": "rumah_pribadi",
            "konsumsi_listrik": "tinggi", "pola_makan": "campuran",
            "lokasi_kota": "kota_besar", "label": "Keluarga kota + mobil + listrik boros"
        },
    ]

    for p in test_profiles:
        label = p.pop("label")
        print(f"\n🧑 Profil: {label}")
        print("-" * 50)
        recs = cf_recommend(p, top_n=3)
        for i, row in recs.iterrows():
            print(f"  #{i+1}  [{row['kategori'].upper()}]  {row['nama_aksi']}")
            print(f"       CO₂: {row['co2_hemat_kg_per_bulan']} kg/bln | CF score: {row['cf_score']}%")

    print("\n✅ CF model berjalan sempurna!")
