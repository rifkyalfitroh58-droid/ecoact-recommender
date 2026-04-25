# 🌿 EcoAct Recommender

> Sistem rekomendasi aksi ramah lingkungan yang dipersonalisasi berdasarkan profil gaya hidup pengguna.

## Tentang Project

**Masalah:** Banyak orang mau berkontribusi ke lingkungan, tapi bingung mulai dari mana.
Saran lingkungan biasanya generik — tidak mempertimbangkan siapa orangnya dan bagaimana gaya hidupnya.

**Solusi:** EcoAct merekomendasikan **Top-N aksi konkret** yang paling relevan berdasarkan profil pengguna,
lengkap dengan estimasi **penghematan CO₂** per bulan.

## Struktur Project

```
ecoact/
├── data/
│   ├── generate_dataset.py     # Membuat synthetic dataset
│   ├── users.csv               # 500 profil pengguna
│   ├── users_encoded.csv       # Fitur setelah one-hot encoding
│   └── actions_processed.csv   # 15 aksi lingkungan + skor CO₂
├── notebooks/
│   ├── eda_and_features.py     # EDA + Feature Engineering
│   └── eda_output.png          # Visualisasi EDA
├── app/
│   ├── recommender.py          # Core model (Content-Based Filtering)
│   └── streamlit_app.py        # UI aplikasi
├── requirements.txt
└── README.md
```

## Cara Menjalankan

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate dataset
```bash
cd ecoact
python data/generate_dataset.py
```

### 3. Jalankan EDA & Feature Engineering
```bash
python notebooks/eda_and_features.py
```

### 4. Test model
```bash
python app/recommender.py
```

### 5. Jalankan aplikasi Streamlit
```bash
streamlit run app/streamlit_app.py
```

## Metode: Content-Based Filtering

Model bekerja dengan cara:
1. **Encode** profil pengguna → vektor biner 18 dimensi (one-hot encoding)
2. **Build** action matrix → setiap aksi punya profil "pengguna ideal"
3. **Cosine Similarity** → ukur kecocokan profil pengguna dengan setiap aksi
4. **Weighted Score** → 60% similarity + 40% dampak CO₂ (normalized)
5. **Top-N** → ambil aksi dengan skor tertinggi

## Data & Referensi

- Estimasi penghematan CO₂ berbasis laporan **IEA** dan **IPCC**
- Dataset sintetis (500 pengguna) dibuat dengan distribusi realistis kondisi Indonesia
- Studi kasus relevan untuk kota-kota seperti Pasuruan, Surabaya, Jakarta

## Pengembangan Lanjutan

- [ ] Tambah collaborative filtering (user-based)
- [ ] Integrasikan data cuaca & polusi udara real-time
- [ ] Gamification: tracking progress CO₂ pengguna
- [ ] Expand ke 50+ aksi dengan sub-kategori
- [ ] Deploy ke Streamlit Cloud / HuggingFace Spaces
