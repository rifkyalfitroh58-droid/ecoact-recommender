"""
EcoAct v1.1 — Generate Interaction Matrix
Membuat data interaksi pengguna: rating (1-5) + implicit feedback (klik/lakukan)
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)

users   = pd.read_csv("data/users.csv")
actions = pd.read_csv("data/actions_processed.csv")

USER_IDS   = users["user_id"].tolist()
ACTION_IDS = actions["action_id"].tolist()
N_USERS    = len(USER_IDS)
N_ACTIONS  = len(ACTION_IDS)

# ── Aturan relevansi aksi per profil (untuk simulasi realistis) ──────────────
def relevance_score(user_row, action_row):
    """Hitung skor relevansi dasar antara user dan aksi (0–1)."""
    score = 0.0
    # Transportasi
    tr = user_row["transportasi"]
    cat = action_row["kategori"]
    if cat == "transportasi":
        if tr in ["motor", "mobil"]:      score += 0.8
        elif tr == "angkot/bus":          score += 0.3
        else:                             score += 0.1
    # Listrik
    kl = user_row["konsumsi_listrik"]
    if cat == "energi":
        if kl == "tinggi":  score += 0.9
        elif kl == "sedang": score += 0.6
        else:                score += 0.3
    # Makanan
    pm = user_row["pola_makan"]
    if cat == "makanan":
        if pm == "banyak_daging": score += 0.9
        elif pm == "campuran":    score += 0.6
        else:                     score += 0.2
    # Sampah, alam, air — relevan untuk semua
    if cat in ["sampah", "alam", "air", "konsumsi"]:
        score += 0.5
    return min(score, 1.0)

# ── Build interaction records ────────────────────────────────────────────────
records = []
for _, user in users.iterrows():
    # Setiap user berinteraksi dengan subset acak aksi (3–10 aksi)
    n_interact = np.random.randint(3, 11)
    # Pilih aksi berdasarkan probabilitas relevansi
    rel_scores = [relevance_score(user, act) for _, act in actions.iterrows()]
    probs = np.array(rel_scores) + 0.15          # baseline agar semua punya peluang
    probs = probs / probs.sum()
    chosen_idx = np.random.choice(N_ACTIONS, size=n_interact, replace=False, p=probs)

    for idx in chosen_idx:
        action = actions.iloc[idx]
        base_rel = rel_scores[idx]

        # Rating (1–5): berdasarkan relevansi + noise
        raw_rating = base_rel * 5 + np.random.normal(0, 0.8)
        rating = int(np.clip(round(raw_rating), 1, 5))

        # Implicit: klik (selalu True jika ada interaksi), lakukan (prob ~ relevansi)
        clicked  = True
        done     = bool(np.random.rand() < (base_rel * 0.7 + 0.1))

        # Combined score: rating dinormalisasi + bobot implicit
        implicit_score = (1.0 if done else 0.4)
        combined = 0.7 * (rating / 5.0) + 0.3 * implicit_score

        records.append({
            "user_id"       : user["user_id"],
            "action_id"     : action["action_id"],
            "rating"        : rating,
            "clicked"       : int(clicked),
            "done"          : int(done),
            "combined_score": round(combined, 4),
        })

interactions = pd.DataFrame(records)
interactions.to_csv("data/interactions.csv", index=False)

print("✅ Interaction matrix selesai!")
print(f"   Total interaksi : {len(interactions)}")
print(f"   Rata-rata per user : {len(interactions)/N_USERS:.1f}")
print(f"   Density matrix : {len(interactions)/(N_USERS*N_ACTIONS)*100:.1f}%")
print(f"   Rating distribution:\n{interactions['rating'].value_counts().sort_index().to_string()}")
print(f"\n{interactions.head(6).to_string()}")
