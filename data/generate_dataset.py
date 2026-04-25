"""
EcoAct Recommender — Dataset Generator
Membuat synthetic dataset realistis berbasis data emisi karbon nyata
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)
N_USERS = 500

# ── 1. PROFIL PENGGUNA ──────────────────────────────────────────────────────

transportasi_opts   = ["motor", "mobil", "angkot/bus", "jalan_kaki", "sepeda"]
tempat_tinggal_opts = ["kos", "rumah_pribadi", "apartemen", "rumah_kontrakan"]
listrik_opts        = ["rendah", "sedang", "tinggi"]
makan_opts          = ["banyak_daging", "campuran", "vegetarian"]
kota_opts           = ["kota_besar", "kota_kecil", "pedesaan"]

users = pd.DataFrame({
    "user_id"         : [f"U{i:04d}" for i in range(N_USERS)],
    "transportasi"    : np.random.choice(transportasi_opts,   N_USERS, p=[0.45, 0.20, 0.15, 0.12, 0.08]),
    "tempat_tinggal"  : np.random.choice(tempat_tinggal_opts, N_USERS, p=[0.30, 0.35, 0.15, 0.20]),
    "konsumsi_listrik": np.random.choice(listrik_opts,        N_USERS, p=[0.25, 0.50, 0.25]),
    "pola_makan"      : np.random.choice(makan_opts,          N_USERS, p=[0.40, 0.45, 0.15]),
    "lokasi_kota"     : np.random.choice(kota_opts,           N_USERS, p=[0.50, 0.35, 0.15]),
})

# ── 2. AKSI LINGKUNGAN + PROFIL CO₂ ─────────────────────────────────────────
# Setiap aksi punya "profil ideal" pengguna yang paling relevan
# dan estimasi CO₂ yang bisa dihemat (kg/bulan) — berbasis data IEA & IPCC

actions = pd.DataFrame({
    "action_id"   : [f"A{i:02d}" for i in range(1, 16)],
    "nama_aksi"   : [
        "Beralih ke transportasi umum",
        "Carpooling / nebeng bareng",
        "Gunakan sepeda untuk jarak dekat",
        "Kurangi konsumsi daging merah",
        "Pilih diet plant-based 3x seminggu",
        "Matikan lampu & cabut charger idle",
        "Ganti lampu ke LED hemat energi",
        "Pasang solar panel skala rumah",
        "Pisahkan sampah daur ulang",
        "Gunakan tas belanja kain",
        "Kurangi penggunaan AC 1 jam/hari",
        "Beli produk lokal & musiman",
        "Hemat air mandi (shower < 5 menit)",
        "Composting sampah organik",
        "Tanam pohon / tanaman di rumah",
    ],
    "kategori"    : [
        "transportasi","transportasi","transportasi",
        "makanan","makanan",
        "energi","energi","energi",
        "sampah","sampah",
        "energi",
        "konsumsi",
        "air",
        "sampah",
        "alam",
    ],
    "co2_hemat_kg_per_bulan": [
        42.0, 28.0, 15.0,
        20.0, 16.0,
        5.0, 8.0, 35.0,
        6.0, 2.0,
        12.0,
        4.0,
        3.0,
        5.0,
        7.0,
    ],
    # Profil ideal pengguna (untuk content-based matching)
    "cocok_transportasi"    : ["angkot/bus","mobil","sepeda","motor","motor","kos","rumah_pribadi","rumah_pribadi","kos","kos","apartemen","kota_besar","kos","rumah_pribadi","rumah_pribadi"],
    "cocok_listrik"         : ["rendah","rendah","rendah","rendah","rendah","tinggi","tinggi","tinggi","sedang","sedang","tinggi","rendah","tinggi","sedang","rendah"],
    "cocok_makan"           : ["campuran","campuran","campuran","banyak_daging","banyak_daging","campuran","campuran","campuran","campuran","campuran","campuran","campuran","campuran","banyak_daging","vegetarian"],
})

# ── 3. SIMPAN ────────────────────────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
users.to_csv("data/users.csv", index=False)
actions.to_csv("data/actions.csv", index=False)

print("✅ Dataset berhasil dibuat!")
print(f"   users.csv    : {len(users)} baris × {len(users.columns)} kolom")
print(f"   actions.csv  : {len(actions)} baris × {len(actions.columns)} kolom")
print()
print(users.head(3).to_string())
print()
print(actions[["action_id","nama_aksi","co2_hemat_kg_per_bulan"]].to_string())
