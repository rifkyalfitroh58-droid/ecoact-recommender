"""
EcoAct v1.5 — Model Evaluator
Metrik: Precision@K, Recall@K, F1@K, NDCG@K, Coverage, Diversity
Benchmark: CB vs CF vs Random vs Popularity-based
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "app"))

from recommender    import recommend
from cf_recommender import cf_recommend

# ── Load data ─────────────────────────────────────────────────────────────
interactions = pd.read_csv(os.path.join(BASE_DIR, "data", "interactions.csv"))
users        = pd.read_csv(os.path.join(BASE_DIR, "data", "users.csv"))

# Coba load actions_v14, fallback ke lama
v14_path = os.path.join(BASE_DIR, "data", "actions_v14.csv")
old_path = os.path.join(BASE_DIR, "data", "actions_processed.csv")
actions  = pd.read_csv(v14_path if os.path.exists(v14_path) else old_path)
ALL_ACTION_IDS = actions["action_id"].tolist()
N_ACTIONS      = len(ALL_ACTION_IDS)

# ── Ground Truth: aksi relevan per user ────────────────────────────────────
def build_ground_truth(threshold: float = 0.6) -> dict:
    """
    Definisi 'relevan': combined_score >= threshold.
    Return: {user_id: set(action_id)}
    """
    gt = {}
    for _, row in interactions.iterrows():
        uid = row["user_id"]
        if row["combined_score"] >= threshold:
            gt.setdefault(uid, set()).add(row["action_id"])
    return gt

# ── Metrics ────────────────────────────────────────────────────────────────
def precision_at_k(recommended: list, relevant: set, k: int) -> float:
    recs_k = recommended[:k]
    if not recs_k: return 0.0
    return len(set(recs_k) & relevant) / k

def recall_at_k(recommended: list, relevant: set, k: int) -> float:
    if not relevant: return 0.0
    recs_k = recommended[:k]
    return len(set(recs_k) & relevant) / len(relevant)

def f1_at_k(recommended: list, relevant: set, k: int) -> float:
    p = precision_at_k(recommended, relevant, k)
    r = recall_at_k(recommended, relevant, k)
    if p + r == 0: return 0.0
    return 2 * p * r / (p + r)

def ndcg_at_k(recommended: list, relevant: set, k: int) -> float:
    """NDCG@K — mempertimbangkan urutan rekomendasi."""
    recs_k  = recommended[:k]
    dcg     = sum(1.0 / np.log2(i + 2) for i, item in enumerate(recs_k) if item in relevant)
    ideal_k = min(len(relevant), k)
    idcg    = sum(1.0 / np.log2(i + 2) for i in range(ideal_k))
    return dcg / idcg if idcg > 0 else 0.0

def coverage(all_recommendations: list) -> float:
    """Catalog coverage: berapa % aksi yang pernah direkomendasikan."""
    unique_recs = set(item for recs in all_recommendations for item in recs)
    return len(unique_recs) / N_ACTIONS

def diversity_score(recommended: list) -> float:
    """
    Intra-list diversity: rata-rata dissimilarity antar pasangan aksi.
    Menggunakan kategori aksi sebagai fitur.
    """
    if len(recommended) < 2: return 0.0
    cats = actions.set_index("action_id")["kategori"].to_dict()
    rec_cats = [cats.get(a, "unknown") for a in recommended]
    pairs    = [(rec_cats[i], rec_cats[j])
                for i in range(len(rec_cats))
                for j in range(i+1, len(rec_cats))]
    if not pairs: return 0.0
    diverse  = sum(1 for a, b in pairs if a != b)
    return diverse / len(pairs)

# ── Model wrappers ─────────────────────────────────────────────────────────
def get_cb_recs(user_row: pd.Series, k: int) -> list:
    try:
        recs = recommend(
            transportasi     = user_row["transportasi"],
            tempat_tinggal   = user_row["tempat_tinggal"],
            konsumsi_listrik = user_row["konsumsi_listrik"],
            pola_makan       = user_row["pola_makan"],
            lokasi_kota      = user_row["lokasi_kota"],
            top_n=k
        )
        return recs["action_id"].tolist() if not recs.empty else []
    except Exception:
        return []

def get_cf_recs(user_row: pd.Series, k: int) -> list:
    try:
        profile = {
            "transportasi"    : user_row["transportasi"],
            "tempat_tinggal"  : user_row["tempat_tinggal"],
            "konsumsi_listrik": user_row["konsumsi_listrik"],
            "pola_makan"      : user_row["pola_makan"],
            "lokasi_kota"     : user_row["lokasi_kota"],
        }
        recs = cf_recommend(profile, top_n=k)
        return recs["action_id"].tolist() if not recs.empty else []
    except Exception:
        return []

def get_random_recs(k: int) -> list:
    return list(np.random.choice(ALL_ACTION_IDS, size=min(k, N_ACTIONS), replace=False))

def get_popularity_recs(k: int) -> list:
    """Rekomendasikan aksi paling populer (paling sering di-interact)."""
    pop = interactions.groupby("action_id")["combined_score"].mean().sort_values(ascending=False)
    return pop.index.tolist()[:k]

# ── Evaluasi utama ─────────────────────────────────────────────────────────
def evaluate_all(k_values: list = [3, 5, 10],
                 n_users: int = 100,
                 gt_threshold: float = 0.6,
                 random_seed: int = 42) -> dict:
    """
    Evaluasi semua model untuk semua K.
    Return: dict berisi hasil metrik per model per K.
    """
    np.random.seed(random_seed)
    ground_truth = build_ground_truth(gt_threshold)

    # Ambil user yang punya ground truth
    eligible_users = [uid for uid, gt in ground_truth.items() if len(gt) >= 1]
    sample_size    = min(n_users, len(eligible_users))
    sampled_users  = np.random.choice(eligible_users, size=sample_size, replace=False)

    models = ["CB", "CF", "Random", "Popularity"]
    results = {m: {k: {"precision":[], "recall":[], "f1":[], "ndcg":[], "diversity":[]}
                   for k in k_values}
               for m in models}
    all_recs_cb  = []
    all_recs_cf  = []
    all_recs_rnd = []
    all_recs_pop = []

    pop_recs = {k: get_popularity_recs(k) for k in k_values}

    for uid in sampled_users:
        relevant = ground_truth.get(uid, set())
        if not relevant: continue

        user_row = users[users["user_id"] == uid]
        if user_row.empty: continue
        user_row = user_row.iloc[0]

        for k in k_values:
            cb_recs  = get_cb_recs(user_row, k)
            cf_recs  = get_cf_recs(user_row, k)
            rnd_recs = get_random_recs(k)
            pop_recs_k = pop_recs[k]

            for model_name, recs in [("CB",cb_recs),("CF",cf_recs),
                                      ("Random",rnd_recs),("Popularity",pop_recs_k)]:
                results[model_name][k]["precision"].append(precision_at_k(recs, relevant, k))
                results[model_name][k]["recall"].append(recall_at_k(recs, relevant, k))
                results[model_name][k]["f1"].append(f1_at_k(recs, relevant, k))
                results[model_name][k]["ndcg"].append(ndcg_at_k(recs, relevant, k))
                results[model_name][k]["diversity"].append(diversity_score(recs))

            if k == k_values[0]:
                all_recs_cb.append(cb_recs); all_recs_cf.append(cf_recs)
                all_recs_rnd.append(rnd_recs); all_recs_pop.append(pop_recs_k)

    # Agregasi rata-rata
    summary = {}
    for model in models:
        summary[model] = {}
        for k in k_values:
            d = results[model][k]
            summary[model][k] = {
                "precision" : round(np.mean(d["precision"]), 4),
                "recall"    : round(np.mean(d["recall"]),    4),
                "f1"        : round(np.mean(d["f1"]),        4),
                "ndcg"      : round(np.mean(d["ndcg"]),      4),
                "diversity" : round(np.mean(d["diversity"]), 4),
            }

    # Coverage (hanya K=5)
    k5 = k_values[1] if len(k_values) > 1 else k_values[0]
    summary["_coverage"] = {
        "CB"        : round(coverage(all_recs_cb),  4),
        "CF"        : round(coverage(all_recs_cf),  4),
        "Random"    : round(coverage(all_recs_rnd), 4),
        "Popularity": round(coverage(all_recs_pop), 4),
    }
    summary["_meta"] = {
        "n_users_evaluated": sample_size,
        "gt_threshold"     : gt_threshold,
        "k_values"         : k_values,
        "n_actions"        : N_ACTIONS,
    }
    return summary


# ── Pretty print ───────────────────────────────────────────────────────────
def print_results(summary: dict):
    k_values = summary["_meta"]["k_values"]
    models   = ["CB", "CF", "Random", "Popularity"]
    metrics  = ["precision", "recall", "f1", "ndcg", "diversity"]

    for k in k_values:
        print(f"\n{'='*62}")
        print(f"  K = {k}")
        print(f"{'='*62}")
        header = f"{'Model':12}" + "".join(f"{m:>12}" for m in metrics)
        print(header)
        print("-"*62)
        for model in models:
            row = summary[model][k]
            vals = "".join(f"{row[m]:>12.4f}" for m in metrics)
            print(f"{model:12}{vals}")

    print(f"\n{'='*62}")
    print("  Catalog Coverage (K=5)")
    print(f"{'='*62}")
    for model, cov in summary["_coverage"].items():
        bar = "█" * int(cov * 30)
        print(f"  {model:12} {cov:.1%}  {bar}")

    meta = summary["_meta"]
    print(f"\n  Evaluasi pada {meta['n_users_evaluated']} user")
    print(f"  Ground truth threshold: combined_score >= {meta['gt_threshold']}")
    print(f"  Total aksi di katalog  : {meta['n_actions']}")


if __name__ == "__main__":
    print("Menjalankan evaluasi lengkap...")
    print("(100 user, K=[3,5,10], semua metrik)\n")
    results = evaluate_all(k_values=[3,5,10], n_users=100)
    print_results(results)
    print("\n✅ Evaluasi selesai!")
