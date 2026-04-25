"""
EcoAct v1.2 — Environmental Context Engine
Mengubah data cuaca & polusi menjadi modifier yang mempengaruhi skor rekomendasi.

Logic:
- AQI buruk → aksi outdoor (sepeda, jalan kaki) mendapat penalti skor
- Hujan deras → aksi outdoor mendapat penalti besar
- Panas terik (UV tinggi) → aksi hemat energi (solar panel, AC) mendapat bonus
- Angin kencang → aksi sepeda dapat penalti ringan
- Udara bersih → aksi outdoor mendapat bonus kecil
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict

# ── Kategori aksi berdasarkan tipe outdoor/indoor ────────────────────────────
# Ini digunakan untuk menentukan modifier mana yang berlaku pada tiap aksi
ACTION_TYPE: Dict[str, str] = {
    "A01": "outdoor_transport",   # Beralih ke transportasi umum
    "A02": "outdoor_transport",   # Carpooling
    "A03": "outdoor_cycling",     # Gunakan sepeda
    "A04": "indoor_food",         # Kurangi daging
    "A05": "indoor_food",         # Diet plant-based
    "A06": "indoor_energy",       # Matikan lampu
    "A07": "indoor_energy",       # Ganti lampu LED
    "A08": "outdoor_home",        # Solar panel
    "A09": "indoor_waste",        # Pisah sampah
    "A10": "indoor_shopping",     # Tas kain
    "A11": "indoor_energy",       # Kurangi AC
    "A12": "indoor_shopping",     # Beli produk lokal
    "A13": "indoor_water",        # Hemat air mandi
    "A14": "outdoor_home",        # Composting
    "A15": "outdoor_home",        # Tanam pohon
}


@dataclass
class EnvScore:
    """Representasi kondisi lingkungan dalam bentuk skor terstruktur."""
    aqi:          int   = 50
    temp:         float = 28.0
    rain_1h:      float = 0.0
    wind_speed:   float = 2.0
    uv_index:     int   = 6
    humidity:     float = 70.0

    # Computed scores (diisi oleh compute())
    air_quality_score:  float = field(default=0.0, init=False)
    rain_severity:      float = field(default=0.0, init=False)
    heat_severity:      float = field(default=0.0, init=False)
    wind_severity:      float = field(default=0.0, init=False)
    overall_env_score:  float = field(default=0.0, init=False)
    env_label:          str   = field(default="", init=False)
    env_emoji:          str   = field(default="", init=False)

    def compute(self) -> "EnvScore":
        """Hitung semua skor turunan dari data mentah."""
        # Air quality: normalize AQI 0–300 → 0–1 (semakin tinggi = semakin buruk)
        self.air_quality_score = min(self.aqi / 300.0, 1.0)

        # Rain: 0 = tidak hujan, 1 = hujan lebat
        self.rain_severity = min(self.rain_1h / 10.0, 1.0)

        # Heat: UV > 7 mulai berbahaya, normalize 0–13 → 0–1
        self.heat_severity = min(max(self.uv_index - 3, 0) / 10.0, 1.0)

        # Wind: > 10 m/s mulai mengganggu bersepeda
        self.wind_severity = min(max(self.wind_speed - 5, 0) / 15.0, 1.0)

        # Overall: gabungan tertimbang
        self.overall_env_score = (
            0.45 * self.air_quality_score +
            0.25 * self.rain_severity +
            0.20 * self.heat_severity +
            0.10 * self.wind_severity
        )

        # Label deskriptif
        if self.overall_env_score < 0.2:
            self.env_label = "Kondisi Ideal untuk Aksi Outdoor"
            self.env_emoji = "🌿"
        elif self.overall_env_score < 0.4:
            self.env_label = "Kondisi Cukup Baik"
            self.env_emoji = "🌤️"
        elif self.overall_env_score < 0.6:
            self.env_label = "Perhatikan Kondisi Udara"
            self.env_emoji = "⚠️"
        elif self.overall_env_score < 0.8:
            self.env_label = "Kurangi Aktivitas Outdoor"
            self.env_emoji = "😷"
        else:
            self.env_label = "Sangat Disarankan Tetap di Dalam Ruangan"
            self.env_emoji = "🚫"
        return self


def compute_action_modifiers(env: EnvScore) -> Dict[str, float]:
    """
    Hitung modifier skor untuk setiap aksi berdasarkan kondisi lingkungan.
    Return dict: {action_id → modifier} — nilai antara 0.5 (penalti besar) dan 1.3 (bonus besar)
    """
    modifiers = {}

    for action_id, action_type in ACTION_TYPE.items():
        mod = 1.0  # default: tidak ada perubahan

        if action_type == "outdoor_cycling":
            # Sepeda: sangat sensitif terhadap hujan, AQI, dan angin
            if env.aqi > 150:       mod -= 0.30
            elif env.aqi > 100:     mod -= 0.15
            elif env.aqi < 50:      mod += 0.10   # udara bersih = bonus
            if env.rain_1h > 5:     mod -= 0.40
            elif env.rain_1h > 1:   mod -= 0.20
            if env.wind_speed > 10: mod -= 0.15

        elif action_type == "outdoor_transport":
            # Transportasi umum/carpooling: penalti ringan saat AQI buruk/hujan
            if env.aqi > 150:       mod -= 0.15
            elif env.aqi < 50:      mod += 0.05
            if env.rain_1h > 5:     mod -= 0.15
            elif env.rain_1h > 1:   mod -= 0.05

        elif action_type == "outdoor_home":
            # Solar panel, composting, tanam pohon
            if action_id == "A08":  # solar panel → panas terik = bagus!
                mod += 0.10 * env.heat_severity
                if env.rain_1h > 3: mod -= 0.10
            else:
                if env.rain_1h > 5: mod -= 0.20
                if env.aqi > 150:   mod -= 0.10

        elif action_type == "indoor_energy":
            # Hemat listrik, LED, kurangi AC
            if action_id == "A11":  # kurangi AC → sangat relevan saat panas
                mod += 0.20 * env.heat_severity
            if env.aqi > 100:   mod += 0.05   # indoor = lebih penting saat polusi

        elif action_type in ["indoor_food", "indoor_waste", "indoor_shopping", "indoor_water"]:
            # Aksi dalam ruangan: mendapat bonus saat kondisi outdoor buruk
            outdoor_badness = (
                0.5 * env.air_quality_score +
                0.3 * env.rain_severity +
                0.2 * env.heat_severity
            )
            mod += 0.10 * outdoor_badness

        # Clamp modifier ke range yang masuk akal
        modifiers[action_id] = round(max(0.50, min(1.30, mod)), 3)

    return modifiers


def get_env_context(env_data: dict) -> tuple[EnvScore, Dict[str, float]]:
    """
    Entry point utama: ambil data dari weather_api, return EnvScore + modifiers.

    env_data: output dari weather_api.fetch_env_data()
    Returns: (EnvScore, {action_id: modifier})
    """
    w = env_data["weather"]
    a = env_data["air"]

    env = EnvScore(
        aqi        = a["aqi"],
        temp       = w["temp"],
        rain_1h    = w["rain_1h"],
        wind_speed = w["wind_speed"],
        uv_index   = w["uv_index"],
        humidity   = w["humidity"],
    ).compute()

    modifiers = compute_action_modifiers(env)
    return env, modifiers


# ── TEST ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from weather_api import fetch_env_data

    print("=" * 55)
    print("TEST — Environmental Context Engine")
    print("=" * 55)

    for lokasi in ["kota_besar", "kota_kecil", "pedesaan"]:
        data = fetch_env_data(lokasi)
        env, mods = get_env_context(data)
        print(f"\n📍 {lokasi.upper()}")
        print(f"   AQI: {env.aqi} | Hujan: {env.rain_1h}mm | UV: {env.uv_index} | Angin: {env.wind_speed}m/s")
        print(f"   Env Score   : {env.overall_env_score:.2f}")
        print(f"   Status      : {env.env_emoji} {env.env_label}")
        print(f"   Modifier sepeda   : {mods['A03']:.2f}x")
        print(f"   Modifier angkot   : {mods['A01']:.2f}x")
        print(f"   Modifier solar    : {mods['A08']:.2f}x")
        print(f"   Modifier kurangi AC: {mods['A11']:.2f}x")
        print(f"   Modifier hemat air : {mods['A13']:.2f}x")

    print("\n✅ Environmental Context Engine berjalan sempurna!")
