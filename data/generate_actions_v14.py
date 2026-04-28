"""
EcoAct v1.4 — Expanded Dataset Generator
52 aksi lingkungan (15 lama + 37 baru) dengan:
- Sub-kategori
- Tingkat kesulitan (mudah/sedang/sulit)
- Estimasi biaya (gratis/murah/investasi)
- Waktu yang dibutuhkan (harian/mingguan/sekali)
"""

import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

# ── 52 AKSI LINGKUNGAN LENGKAP ─────────────────────────────────────────────
# Format: action_id, nama_aksi, kategori, sub_kategori,
#         co2_hemat_kg_per_bulan, kesulitan, biaya, waktu,
#         cocok_transportasi, cocok_listrik, cocok_makan

ACTIONS = [

    # ════════════════════════════════════════════
    # TRANSPORTASI (9 aksi)
    # ════════════════════════════════════════════
    ("A01","Beralih ke transportasi umum","transportasi","kendaraan_umum",
     42.0,"sedang","gratis","harian","angkot/bus","sedang","campuran"),
    ("A02","Carpooling / nebeng bareng","transportasi","kendaraan_umum",
     28.0,"mudah","gratis","harian","mobil","sedang","campuran"),
    ("A03","Gunakan sepeda untuk jarak dekat","transportasi","aktif",
     15.0,"mudah","murah","harian","sepeda","rendah","campuran"),
    ("A16","Jalan kaki untuk jarak < 1 km","transportasi","aktif",
     8.0,"mudah","gratis","harian","jalan_kaki","rendah","campuran"),
    ("A17","Servis rutin kendaraan agar efisien","transportasi","kendaraan_pribadi",
     10.0,"sedang","murah","bulanan","motor","sedang","campuran"),
    ("A18","Matikan mesin saat parkir > 1 menit","transportasi","kendaraan_pribadi",
     5.0,"mudah","gratis","harian","mobil","sedang","campuran"),
    ("A19","Hindari jam macet — berangkat lebih awal","transportasi","kendaraan_pribadi",
     7.0,"sedang","gratis","harian","motor","sedang","campuran"),
    ("A20","Pertimbangkan kendaraan listrik / motor listrik","transportasi","kendaraan_listrik",
     50.0,"sulit","investasi","sekali","mobil","tinggi","campuran"),
    ("A21","Gabung komunitas sepeda / car-free day","transportasi","aktif",
     12.0,"mudah","gratis","mingguan","sepeda","rendah","campuran"),

    # ════════════════════════════════════════════
    # ENERGI (10 aksi)
    # ════════════════════════════════════════════
    ("A06","Matikan lampu & cabut charger idle","energi","hemat_listrik",
     5.0,"mudah","gratis","harian","motor","tinggi","campuran"),
    ("A07","Ganti lampu ke LED hemat energi","energi","hemat_listrik",
     8.0,"mudah","murah","sekali","motor","tinggi","campuran"),
    ("A08","Pasang solar panel skala rumah","energi","energi_terbarukan",
     35.0,"sulit","investasi","sekali","mobil","tinggi","campuran"),
    ("A11","Kurangi penggunaan AC 1 jam/hari","energi","hemat_listrik",
     12.0,"mudah","gratis","harian","motor","tinggi","campuran"),
    ("A22","Gunakan kipas angin sebagai pengganti AC","energi","hemat_listrik",
     18.0,"mudah","murah","harian","motor","tinggi","campuran"),
    ("A23","Cuci baju dengan air dingin","energi","hemat_listrik",
     4.0,"mudah","gratis","mingguan","kos","sedang","campuran"),
    ("A24","Cabut perangkat elektronik saat tidak dipakai","energi","hemat_listrik",
     6.0,"mudah","gratis","harian","kos","tinggi","campuran"),
    ("A25","Gunakan timer otomatis untuk perangkat listrik","energi","hemat_listrik",
     7.0,"sedang","murah","sekali","kos","tinggi","campuran"),
    ("A26","Pasang pemanas air surya","energi","energi_terbarukan",
     22.0,"sulit","investasi","sekali","rumah_pribadi","tinggi","campuran"),
    ("A27","Pilih peralatan rumah tangga berenergi rendah","energi","hemat_listrik",
     15.0,"sedang","investasi","sekali","rumah_pribadi","tinggi","campuran"),

    # ════════════════════════════════════════════
    # MAKANAN (8 aksi)
    # ════════════════════════════════════════════
    ("A04","Kurangi konsumsi daging merah","makanan","pola_makan",
     20.0,"sedang","gratis","harian","motor","sedang","banyak_daging"),
    ("A05","Pilih diet plant-based 3x seminggu","makanan","pola_makan",
     16.0,"sedang","gratis","mingguan","motor","sedang","banyak_daging"),
    ("A28","Masak sendiri daripada pesan makanan","makanan","kebiasaan_masak",
     9.0,"sedang","gratis","harian","kos","sedang","campuran"),
    ("A29","Kurangi food waste — habiskan makanan","makanan","kebiasaan_masak",
     8.0,"mudah","gratis","harian","kos","sedang","campuran"),
    ("A30","Pilih produk ikan laut berkelanjutan","makanan","pola_makan",
     11.0,"sedang","murah","mingguan","motor","sedang","campuran"),
    ("A31","Kurangi konsumsi minuman dalam kemasan","makanan","kebiasaan_konsumsi",
     5.0,"mudah","murah","harian","kos","sedang","campuran"),
    ("A32","Simpan makanan dengan benar agar tidak terbuang","makanan","kebiasaan_masak",
     6.0,"mudah","gratis","harian","kos","sedang","campuran"),
    ("A33","Beli bahan makanan secukupnya — meal planning","makanan","kebiasaan_konsumsi",
     10.0,"sedang","gratis","mingguan","kos","sedang","campuran"),

    # ════════════════════════════════════════════
    # SAMPAH (8 aksi)
    # ════════════════════════════════════════════
    ("A09","Pisahkan sampah daur ulang","sampah","daur_ulang",
     6.0,"mudah","gratis","harian","kos","sedang","campuran"),
    ("A10","Gunakan tas belanja kain","sampah","kurangi_plastik",
     2.0,"mudah","murah","harian","kos","sedang","campuran"),
    ("A14","Composting sampah organik","sampah","organik",
     5.0,"sedang","murah","mingguan","rumah_pribadi","sedang","campuran"),
    ("A34","Bawa tumbler / botol minum sendiri","sampah","kurangi_plastik",
     3.0,"mudah","murah","harian","kos","sedang","campuran"),
    ("A35","Hindari produk sekali pakai (sedotan, piring plastik)","sampah","kurangi_plastik",
     4.0,"mudah","gratis","harian","kos","sedang","campuran"),
    ("A36","Jual / donasikan barang bekas daripada dibuang","sampah","daur_ulang",
     7.0,"sedang","gratis","bulanan","kos","sedang","campuran"),
    ("A37","Gunakan produk isi ulang (refill)","sampah","kurangi_plastik",
     5.0,"mudah","murah","mingguan","kos","sedang","campuran"),
    ("A38","Cetak dokumen dua sisi (duplex printing)","sampah","kertas",
     2.0,"mudah","gratis","harian","kos","sedang","campuran"),

    # ════════════════════════════════════════════
    # AIR (7 aksi)
    # ════════════════════════════════════════════
    ("A13","Hemat air mandi (shower < 5 menit)","air","hemat_air",
     3.0,"mudah","gratis","harian","kos","sedang","campuran"),
    ("A39","Perbaiki keran yang bocor","air","hemat_air",
     8.0,"sedang","murah","sekali","rumah_pribadi","sedang","campuran"),
    ("A40","Tampung air hujan untuk menyiram tanaman","air","konservasi_air",
     5.0,"sedang","murah","mingguan","rumah_pribadi","rendah","campuran"),
    ("A41","Matikan keran saat gosok gigi / cuci muka","air","hemat_air",
     2.0,"mudah","gratis","harian","kos","sedang","campuran"),
    ("A42","Gunakan mesin cuci hanya saat penuh","air","hemat_air",
     4.0,"mudah","gratis","mingguan","kos","sedang","campuran"),
    ("A43","Daur ulang air bekas cucian untuk menyiram","air","konservasi_air",
     6.0,"sedang","murah","harian","rumah_pribadi","rendah","campuran"),
    ("A44","Pasang shower hemat air","air","hemat_air",
     7.0,"sedang","murah","sekali","kos","sedang","campuran"),

    # ════════════════════════════════════════════
    # ALAM (6 aksi)
    # ════════════════════════════════════════════
    ("A15","Tanam pohon / tanaman di rumah","alam","penghijauan",
     7.0,"mudah","murah","mingguan","rumah_pribadi","rendah","vegetarian"),
    ("A45","Ikut kegiatan penanaman pohon komunitas","alam","penghijauan",
     10.0,"mudah","gratis","bulanan","jalan_kaki","rendah","campuran"),
    ("A46","Buat taman mini / rooftop garden","alam","penghijauan",
     9.0,"sedang","murah","mingguan","rumah_pribadi","rendah","campuran"),
    ("A47","Dukung produk bersertifikat ramah lingkungan","alam","konservasi",
     6.0,"mudah","murah","mingguan","kos","sedang","campuran"),
    ("A48","Kurangi penggunaan pestisida kimia","alam","konservasi",
     4.0,"sedang","gratis","mingguan","rumah_pribadi","rendah","campuran"),
    ("A49","Buat lubang biopori di halaman","alam","konservasi",
     5.0,"sedang","murah","sekali","rumah_pribadi","rendah","campuran"),

    # ════════════════════════════════════════════
    # KONSUMSI (4 aksi)
    # ════════════════════════════════════════════
    ("A12","Beli produk lokal & musiman","konsumsi","belanja_bijak",
     4.0,"mudah","gratis","mingguan","kos","sedang","campuran"),
    ("A50","Pilih produk dengan kemasan minimal","konsumsi","belanja_bijak",
     3.0,"mudah","gratis","mingguan","kos","sedang","campuran"),
    ("A51","Beli barang second-hand / preloved","konsumsi","circular_economy",
     12.0,"sedang","murah","bulanan","kos","sedang","campuran"),
    ("A52","Perbaiki barang rusak sebelum beli baru","konsumsi","circular_economy",
     8.0,"sedang","murah","bulanan","kos","sedang","campuran"),
]

columns = [
    "action_id","nama_aksi","kategori","sub_kategori",
    "co2_hemat_kg_per_bulan","kesulitan","biaya","waktu",
    "cocok_transportasi","cocok_listrik","cocok_makan"
]

actions_df = pd.DataFrame(ACTIONS, columns=columns)

# Normalisasi CO2
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
actions_df["co2_norm"] = scaler.fit_transform(actions_df[["co2_hemat_kg_per_bulan"]])

# Encode kesulitan → numeric (untuk model)
kesulitan_map = {"mudah": 0.0, "sedang": 0.5, "sulit": 1.0}
actions_df["kesulitan_num"] = actions_df["kesulitan"].map(kesulitan_map)

# Encode waktu → numeric
waktu_map = {"harian": 1.0, "mingguan": 0.7, "bulanan": 0.4, "sekali": 0.3}
actions_df["waktu_num"] = actions_df["waktu"].map(waktu_map)

# Simpan
out_path = os.path.join(BASE_DIR, "data", "actions_v14.csv")
actions_df.to_csv(out_path, index=False)

print("✅ Dataset v1.4 berhasil dibuat!")
print(f"   Total aksi      : {len(actions_df)}")
print(f"   Kategori        : {actions_df['kategori'].nunique()}")
print(f"   Sub-kategori    : {actions_df['sub_kategori'].nunique()}")
print(f"   Kesulitan mudah : {(actions_df['kesulitan']=='mudah').sum()}")
print(f"   Kesulitan sedang: {(actions_df['kesulitan']=='sedang').sum()}")
print(f"   Kesulitan sulit : {(actions_df['kesulitan']=='sulit').sum()}")
print(f"   Biaya gratis    : {(actions_df['biaya']=='gratis').sum()}")
print(f"   Biaya murah     : {(actions_df['biaya']=='murah').sum()}")
print(f"   Biaya investasi : {(actions_df['biaya']=='investasi').sum()}")
print(f"\n   CO2 tertinggi   : {actions_df['co2_hemat_kg_per_bulan'].max()} kg/bln ({actions_df.loc[actions_df['co2_hemat_kg_per_bulan'].idxmax(),'nama_aksi']})")
print(f"   CO2 terendah    : {actions_df['co2_hemat_kg_per_bulan'].min()} kg/bln ({actions_df.loc[actions_df['co2_hemat_kg_per_bulan'].idxmin(),'nama_aksi']})")
print(f"\n{actions_df[['action_id','nama_aksi','kategori','sub_kategori','kesulitan','biaya','waktu']].to_string()}")
