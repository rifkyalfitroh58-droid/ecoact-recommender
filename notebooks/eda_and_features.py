"""
EcoAct Recommender — EDA + Feature Engineering
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

# ── Load ──────────────────────────────────────────────────────────────────────
users   = pd.read_csv("data/users.csv")
actions = pd.read_csv("data/actions.csv")

os.makedirs("notebooks", exist_ok=True)

# ── Palette ───────────────────────────────────────────────────────────────────
GREENS = ["#639922", "#97C459", "#C0DD97", "#EAF3DE"]
BLUES  = ["#185FA5", "#378ADD", "#85B7EB", "#B5D4F4"]
TEALS  = ["#0F6E56", "#1D9E75", "#5DCAA5", "#9FE1CB"]
AMBERS = ["#854F0B", "#BA7517", "#EF9F27", "#FAC775"]

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("EcoAct — Exploratory Data Analysis", fontsize=14, fontweight="bold", y=1.01)
fig.patch.set_facecolor("#F8F9FA")

# Plot 1: Distribusi Transportasi
ax1 = axes[0, 0]
counts = users["transportasi"].value_counts()
bars = ax1.barh(counts.index, counts.values, color=GREENS[:len(counts)])
ax1.set_title("Moda Transportasi Pengguna", fontsize=12, fontweight="bold")
ax1.set_xlabel("Jumlah Pengguna")
ax1.spines[["top","right"]].set_visible(False)
for bar, val in zip(bars, counts.values):
    ax1.text(val + 3, bar.get_y() + bar.get_height()/2, str(val), va="center", fontsize=10)

# Plot 2: Distribusi Pola Makan × Kota
ax2 = axes[0, 1]
cross = pd.crosstab(users["lokasi_kota"], users["pola_makan"])
cross.plot(kind="bar", ax=ax2, color=TEALS[:3], width=0.6, edgecolor="white")
ax2.set_title("Pola Makan per Lokasi Kota", fontsize=12, fontweight="bold")
ax2.set_xlabel("")
ax2.set_ylabel("Jumlah Pengguna")
ax2.tick_params(axis="x", rotation=15)
ax2.spines[["top","right"]].set_visible(False)
ax2.legend(fontsize=9, framealpha=0)

# Plot 3: CO₂ Savings per Aksi
ax3 = axes[1, 0]
act_sorted = actions.sort_values("co2_hemat_kg_per_bulan", ascending=True)
colors_bar = [GREENS[0] if x >= 20 else GREENS[1] if x >= 10 else GREENS[2] for x in act_sorted["co2_hemat_kg_per_bulan"]]
bars3 = ax3.barh(act_sorted["nama_aksi"], act_sorted["co2_hemat_kg_per_bulan"], color=colors_bar)
ax3.set_title("Potensi Penghematan CO₂ per Aksi", fontsize=12, fontweight="bold")
ax3.set_xlabel("kg CO₂ / bulan")
ax3.spines[["top","right"]].set_visible(False)
legend_patches = [
    mpatches.Patch(color=GREENS[0], label="Dampak tinggi (≥20 kg)"),
    mpatches.Patch(color=GREENS[1], label="Dampak sedang (10–19 kg)"),
    mpatches.Patch(color=GREENS[2], label="Dampak rendah (<10 kg)"),
]
ax3.legend(handles=legend_patches, fontsize=8, framealpha=0)

# Plot 4: Distribusi Konsumsi Listrik
ax4 = axes[1, 1]
listrik_counts = users["konsumsi_listrik"].value_counts()
wedges, texts, autotexts = ax4.pie(
    listrik_counts.values, labels=listrik_counts.index,
    autopct="%1.1f%%", colors=BLUES[:3],
    startangle=90, pctdistance=0.75,
    wedgeprops={"edgecolor":"white","linewidth":2}
)
for at in autotexts:
    at.set_fontsize(10)
    at.set_color("white")
    at.set_fontweight("bold")
ax4.set_title("Distribusi Konsumsi Listrik", fontsize=12, fontweight="bold")

plt.tight_layout()
plt.savefig("notebooks/eda_output.png", dpi=150, bbox_inches="tight", facecolor="#F8F9FA")
plt.close()
print("✅ EDA chart disimpan → notebooks/eda_output.png")

# ── FEATURE ENGINEERING ───────────────────────────────────────────────────────
print("\n🔧 Feature Engineering...")

# Encode profil pengguna
user_enc = pd.get_dummies(users, columns=["transportasi","tempat_tinggal","konsumsi_listrik","pola_makan","lokasi_kota"])
user_enc = user_enc.drop(columns=["user_id"])

# Buat profil aksi (mapping ke fitur yang sama)
transport_map  = {"angkot/bus":0,"mobil":1,"sepeda":2,"motor":3,"kos":4}
listrik_map    = {"rendah":0,"sedang":1,"tinggi":2}
makan_map      = {"campuran":0,"banyak_daging":1,"vegetarian":2}

# Normalisasi CO₂ savings sebagai bobot
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
actions["co2_norm"] = scaler.fit_transform(actions[["co2_hemat_kg_per_bulan"]])

print(f"   Fitur pengguna setelah encoding: {user_enc.shape[1]} kolom")
print(f"   Shape matrix pengguna: {user_enc.shape}")

# Simpan encoded features
user_enc.to_csv("data/users_encoded.csv", index=False)
actions.to_csv("data/actions_processed.csv", index=False)
users.to_csv("data/users.csv", index=False)

print("\n✅ Feature Engineering selesai!")
print("   Semua data tersimpan di /data/")
