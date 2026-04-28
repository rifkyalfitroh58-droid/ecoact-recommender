"""
EcoAct v1.4 — Content-Based Recommender (52 aksi, atribut baru)
Formula: 0.40×sim + 0.25×CO₂ + 0.15×env + 0.10×kesulitan_inv + 0.10×waktu_freq
"""
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _load_actions():
    v14 = os.path.join(BASE_DIR, "data", "actions_v14.csv")
    v10 = os.path.join(BASE_DIR, "data", "actions_processed.csv")
    if os.path.exists(v14):
        df = pd.read_csv(v14)
        if "co2_norm" not in df.columns:
            from sklearn.preprocessing import MinMaxScaler as MMS
            df["co2_norm"] = MMS().fit_transform(df[["co2_hemat_kg_per_bulan"]])
        if "kesulitan_num" not in df.columns:
            df["kesulitan_num"] = df["kesulitan"].map({"mudah":0.0,"sedang":0.5,"sulit":1.0})
        if "waktu_num" not in df.columns:
            df["waktu_num"] = df["waktu"].map({"harian":1.0,"mingguan":0.7,"bulanan":0.4,"sekali":0.3})
        return df
    return pd.read_csv(v10)

actions = _load_actions()

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

def build_action_matrix(df):
    rows = []
    for _, row in df.iterrows():
        vec = []
        for v in ["angkot/bus","jalan_kaki","mobil","motor","sepeda"]:
            vec.append(1.0 if row.get("cocok_transportasi","")==v else 0.1)
        for _ in ["apartemen","kos","rumah_kontrakan","rumah_pribadi"]: vec.append(0.5)
        for v in ["rendah","sedang","tinggi"]:
            vec.append(1.0 if row.get("cocok_listrik","")==v else 0.1)
        for v in ["banyak_daging","campuran","vegetarian"]:
            vec.append(1.0 if row.get("cocok_makan","")==v else 0.1)
        for _ in ["kota_besar","kota_kecil","pedesaan"]: vec.append(0.5)
        rows.append(vec)
    return np.array(rows)

def recommend(transportasi, tempat_tinggal, konsumsi_listrik, pola_makan, lokasi_kota,
              top_n=5, env_modifiers=None,
              filter_kesulitan=None, filter_biaya=None, filter_waktu=None,
              filter_kategori=None):
    """
    Rekomendasikan aksi dengan CB + atribut baru.

    Filter opsional:
    - filter_kesulitan : list, e.g. ["mudah","sedang"]
    - filter_biaya     : list, e.g. ["gratis","murah"]
    - filter_waktu     : list, e.g. ["harian","mingguan"]
    - filter_kategori  : list, e.g. ["transportasi","energi"]
    """
    df = actions.copy()

    # Terapkan filter
    if filter_kesulitan:
        df = df[df["kesulitan"].isin(filter_kesulitan)]
    if filter_biaya:
        df = df[df["biaya"].isin(filter_biaya)]
    if filter_waktu:
        df = df[df["waktu"].isin(filter_waktu)]
    if filter_kategori:
        df = df[df["kategori"].isin(filter_kategori)]

    if df.empty:
        return pd.DataFrame()

    user_vec   = encode_user_profile(transportasi, tempat_tinggal, konsumsi_listrik, pola_makan, lokasi_kota)
    action_mat = build_action_matrix(df)
    sim_scores = cosine_similarity(user_vec, action_mat).flatten()

    scaler   = MinMaxScaler()
    co2_norm = scaler.fit_transform(df[["co2_hemat_kg_per_bulan"]]).flatten()

    # Env modifier
    env_boost = np.ones(len(df))
    if env_modifiers:
        for i, (_, row) in enumerate(df.iterrows()):
            env_boost[i] = env_modifiers.get(row["action_id"], 1.0)
    env_norm = np.clip((env_boost - 0.5) / 0.8, 0, 1)

    # Kesulitan: invers — aksi lebih mudah mendapat skor lebih tinggi sebagai default
    # (tapi bisa difilter langsung jika user ingin yang sulit)
    kes_num = df["kesulitan_num"].values if "kesulitan_num" in df.columns else np.full(len(df), 0.5)
    kes_inv = 1.0 - kes_num   # mudah=1.0, sedang=0.5, sulit=0.0

    # Waktu: frekuensi lebih tinggi = lebih relevan untuk kebiasaan harian
    wak_num = df["waktu_num"].values if "waktu_num" in df.columns else np.full(len(df), 0.7)

    # Formula v1.4
    final_scores = (
        0.40 * sim_scores +
        0.25 * co2_norm   +
        0.15 * env_norm   +
        0.10 * kes_inv    +
        0.10 * wak_num
    )

    top_idx = final_scores.argsort()[::-1][:top_n]
    result  = df.iloc[top_idx][[
        "action_id","nama_aksi","kategori","sub_kategori",
        "co2_hemat_kg_per_bulan","kesulitan","biaya","waktu"
    ]].copy()
    result["skor_relevansi"] = (final_scores[top_idx] * 100).round(1)
    result["env_modifier"]   = [round(env_boost[i], 2) for i in top_idx]
    return result.reset_index(drop=True)
