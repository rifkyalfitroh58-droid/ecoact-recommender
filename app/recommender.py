"""
EcoAct v1.2 — Content-Based Recommender (dengan Environmental Modifier)
Final score = 0.5×cosine_sim + 0.3×CO₂_norm + 0.2×env_norm
"""
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
users   = pd.read_csv(os.path.join(BASE_DIR, "data", "users.csv"))
actions = pd.read_csv(os.path.join(BASE_DIR, "data", "actions_processed.csv"))

def encode_user_profile(transportasi, tempat_tinggal, konsumsi_listrik, pola_makan, lokasi_kota):
    profile = {
        "transportasi_angkot/bus": int(transportasi=="angkot/bus"),
        "transportasi_jalan_kaki": int(transportasi=="jalan_kaki"),
        "transportasi_mobil"     : int(transportasi=="mobil"),
        "transportasi_motor"     : int(transportasi=="motor"),
        "transportasi_sepeda"    : int(transportasi=="sepeda"),
        "tempat_tinggal_apartemen"      : int(tempat_tinggal=="apartemen"),
        "tempat_tinggal_kos"            : int(tempat_tinggal=="kos"),
        "tempat_tinggal_rumah_kontrakan": int(tempat_tinggal=="rumah_kontrakan"),
        "tempat_tinggal_rumah_pribadi"  : int(tempat_tinggal=="rumah_pribadi"),
        "konsumsi_listrik_rendah": int(konsumsi_listrik=="rendah"),
        "konsumsi_listrik_sedang": int(konsumsi_listrik=="sedang"),
        "konsumsi_listrik_tinggi": int(konsumsi_listrik=="tinggi"),
        "pola_makan_banyak_daging": int(pola_makan=="banyak_daging"),
        "pola_makan_campuran"     : int(pola_makan=="campuran"),
        "pola_makan_vegetarian"   : int(pola_makan=="vegetarian"),
        "lokasi_kota_kota_besar": int(lokasi_kota=="kota_besar"),
        "lokasi_kota_kota_kecil": int(lokasi_kota=="kota_kecil"),
        "lokasi_kota_pedesaan"  : int(lokasi_kota=="pedesaan"),
    }
    return np.array(list(profile.values())).reshape(1, -1)

def build_action_matrix(actions):
    rows = []
    for _, row in actions.iterrows():
        vec = []
        for v in ["angkot/bus","jalan_kaki","mobil","motor","sepeda"]:
            vec.append(1.0 if row["cocok_transportasi"]==v else 0.1)
        for _ in ["apartemen","kos","rumah_kontrakan","rumah_pribadi"]: vec.append(0.5)
        for v in ["rendah","sedang","tinggi"]:
            vec.append(1.0 if row["cocok_listrik"]==v else 0.1)
        for v in ["banyak_daging","campuran","vegetarian"]:
            vec.append(1.0 if row["cocok_makan"]==v else 0.1)
        for _ in ["kota_besar","kota_kecil","pedesaan"]: vec.append(0.5)
        rows.append(vec)
    return np.array(rows)

def recommend(transportasi, tempat_tinggal, konsumsi_listrik, pola_makan, lokasi_kota,
              top_n=3, env_modifiers: dict = None):
    user_vec   = encode_user_profile(transportasi, tempat_tinggal, konsumsi_listrik, pola_makan, lokasi_kota)
    action_mat = build_action_matrix(actions)
    sim_scores = cosine_similarity(user_vec, action_mat).flatten()
    scaler     = MinMaxScaler()
    co2_norm   = scaler.fit_transform(actions[["co2_hemat_kg_per_bulan"]]).flatten()
    env_boost  = np.ones(len(actions))
    if env_modifiers:
        for i, row in actions.iterrows():
            env_boost[i] = env_modifiers.get(row["action_id"], 1.0)
    env_norm     = np.clip((env_boost - 0.5) / 0.8, 0, 1)
    final_scores = 0.50 * sim_scores + 0.30 * co2_norm + 0.20 * env_norm
    top_idx      = final_scores.argsort()[::-1][:top_n]
    results      = actions.iloc[top_idx][["action_id","nama_aksi","kategori","co2_hemat_kg_per_bulan"]].copy()
    results["skor_relevansi"] = (final_scores[top_idx] * 100).round(1)
    results["env_modifier"]   = [round(env_boost[i], 2) for i in top_idx]
    return results.reset_index(drop=True)
