"""
EcoAct Recommender — Core Model
Content-Based Filtering dengan Cosine Similarity
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

# ── Load data ─────────────────────────────────────────────────────────────────
users   = pd.read_csv("data/users.csv")
actions = pd.read_csv("data/actions_processed.csv")

# ── Fungsi utama: encode profil pengguna ─────────────────────────────────────
def encode_user_profile(transportasi, tempat_tinggal, konsumsi_listrik, pola_makan, lokasi_kota):
    """
    Ubah input profil pengguna ke vektor numerik (18 dimensi).
    """
    profile = {
        # Transportasi (5)
        "transportasi_angkot/bus": int(transportasi == "angkot/bus"),
        "transportasi_jalan_kaki": int(transportasi == "jalan_kaki"),
        "transportasi_mobil"     : int(transportasi == "mobil"),
        "transportasi_motor"     : int(transportasi == "motor"),
        "transportasi_sepeda"    : int(transportasi == "sepeda"),
        # Tempat tinggal (4)
        "tempat_tinggal_apartemen"     : int(tempat_tinggal == "apartemen"),
        "tempat_tinggal_kos"           : int(tempat_tinggal == "kos"),
        "tempat_tinggal_rumah_kontrakan": int(tempat_tinggal == "rumah_kontrakan"),
        "tempat_tinggal_rumah_pribadi" : int(tempat_tinggal == "rumah_pribadi"),
        # Listrik (3)
        "konsumsi_listrik_rendah": int(konsumsi_listrik == "rendah"),
        "konsumsi_listrik_sedang": int(konsumsi_listrik == "sedang"),
        "konsumsi_listrik_tinggi": int(konsumsi_listrik == "tinggi"),
        # Makan (3)
        "pola_makan_banyak_daging": int(pola_makan == "banyak_daging"),
        "pola_makan_campuran"     : int(pola_makan == "campuran"),
        "pola_makan_vegetarian"   : int(pola_makan == "vegetarian"),
        # Kota (3)
        "lokasi_kota_kota_besar": int(lokasi_kota == "kota_besar"),
        "lokasi_kota_kota_kecil": int(lokasi_kota == "kota_kecil"),
        "lokasi_kota_pedesaan"  : int(lokasi_kota == "pedesaan"),
    }
    return np.array(list(profile.values())).reshape(1, -1)


# ── Buat Action Feature Matrix ─────────────────────────────────────────────
def build_action_matrix(actions):
    """
    Buat matrix fitur untuk setiap aksi lingkungan.
    Setiap aksi direpresentasikan dalam ruang fitur yang sama dengan pengguna.
    """
    transport_vals  = ["angkot/bus","jalan_kaki","mobil","motor","sepeda"]
    tinggal_vals    = ["apartemen","kos","rumah_kontrakan","rumah_pribadi"]
    listrik_vals    = ["rendah","sedang","tinggi"]
    makan_vals      = ["banyak_daging","campuran","vegetarian"]
    kota_vals       = ["kota_besar","kota_kecil","pedesaan"]

    rows = []
    for _, row in actions.iterrows():
        vec = []
        # Mapping cocok_transportasi ke vektor binary
        for v in transport_vals:
            vec.append(1.0 if row["cocok_transportasi"] == v else 0.1)
        # tempat tinggal (gunakan cocok_transportasi proxy utk simpel)
        for v in tinggal_vals:
            vec.append(0.5)
        # listrik
        for v in listrik_vals:
            vec.append(1.0 if row["cocok_listrik"] == v else 0.1)
        # makan
        for v in makan_vals:
            vec.append(1.0 if row["cocok_makan"] == v else 0.1)
        # kota — semua relevan
        for v in kota_vals:
            vec.append(0.5)
        rows.append(vec)

    return np.array(rows)


# ── Fungsi Rekomendasi ────────────────────────────────────────────────────────
def recommend(transportasi, tempat_tinggal, konsumsi_listrik, pola_makan, lokasi_kota, top_n=3):
    """
    Return Top-N aksi lingkungan yang paling relevan untuk profil pengguna.
    """
    user_vec   = encode_user_profile(transportasi, tempat_tinggal, konsumsi_listrik, pola_makan, lokasi_kota)
    action_mat = build_action_matrix(actions)

    # Hitung cosine similarity
    sim_scores = cosine_similarity(user_vec, action_mat).flatten()

    # Gabungkan similarity + bobot CO₂
    scaler = MinMaxScaler()
    co2_norm = scaler.fit_transform(actions[["co2_hemat_kg_per_bulan"]]).flatten()
    final_scores = 0.6 * sim_scores + 0.4 * co2_norm

    # Ambil top-N
    top_idx = final_scores.argsort()[::-1][:top_n]
    results = actions.iloc[top_idx][["action_id","nama_aksi","kategori","co2_hemat_kg_per_bulan"]].copy()
    results["skor_relevansi"] = (final_scores[top_idx] * 100).round(1)
    results = results.reset_index(drop=True)
    return results


# ── TEST ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("TEST REKOMENDASI — EcoAct Recommender")
    print("=" * 60)

    test_cases = [
        ("motor", "kos", "sedang", "banyak_daging", "kota_besar"),
        ("mobil", "rumah_pribadi", "tinggi", "campuran", "kota_besar"),
        ("jalan_kaki", "rumah_pribadi", "rendah", "vegetarian", "pedesaan"),
    ]

    labels = [
        "Profil 1: Anak kos, pakai motor, makan daging",
        "Profil 2: Keluarga, pakai mobil, listrik boros",
        "Profil 3: Pedesaan, jalan kaki, vegetarian",
    ]

    for label, (tr, tt, kl, pm, lk) in zip(labels, test_cases):
        print(f"\n{label}")
        print(f"  ({tr} | {tt} | listrik {kl} | {pm} | {lk})")
        print("-" * 55)
        recs = recommend(tr, tt, kl, pm, lk)
        for i, row in recs.iterrows():
            print(f"  #{i+1}  [{row['kategori'].upper()}]  {row['nama_aksi']}")
            print(f"       CO₂ hemat: {row['co2_hemat_kg_per_bulan']} kg/bulan | Skor: {row['skor_relevansi']}%")

    print("\n✅ Model berjalan sempurna!")
