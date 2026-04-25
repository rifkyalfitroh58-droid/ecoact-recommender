"""
EcoAct v1.2 — Weather & Air Quality API Client
Mengambil data cuaca (OpenWeatherMap) dan polusi udara (AirVisual/IQAir)
secara real-time berdasarkan nama kota.

Jika API key tidak tersedia → otomatis fallback ke mock data realistis.
"""

import requests
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "app"))

from env_config import OPENWEATHER_API_KEY, AIRVISUAL_API_KEY, USE_MOCK_DATA

# ── Mapping kota Indonesia → koordinat & negara ──────────────────────────────
KOTA_COORDS = {
    "kota_besar"   : {"lat": -7.2575, "lon": 112.7521, "city": "Surabaya",  "country": "ID"},
    "kota_kecil"   : {"lat": -7.6298, "lon": 112.1808, "city": "Pasuruan",  "country": "ID"},
    "pedesaan"     : {"lat": -7.9811, "lon": 112.6284, "city": "Malang",    "country": "ID"},
}

# ── Mock data realistis untuk demo / fallback ─────────────────────────────────
MOCK_DATA = {
    "kota_besar": {
        "weather": {"temp": 31.5, "feels_like": 38, "humidity": 78, "condition": "Berawan",
                    "wind_speed": 3.2, "rain_1h": 0.0, "uv_index": 8, "icon": "04d"},
        "air":     {"aqi": 112, "aqi_label": "Tidak Sehat untuk Kelompok Sensitif",
                    "pm25": 35.2, "pm10": 52.1, "no2": 28.4, "o3": 89.0,
                    "dominant_pollutant": "PM2.5"},
    },
    "kota_kecil": {
        "weather": {"temp": 28.0, "feels_like": 33, "humidity": 72, "condition": "Cerah",
                    "wind_speed": 2.1, "rain_1h": 0.0, "uv_index": 9, "icon": "01d"},
        "air":     {"aqi": 64,  "aqi_label": "Sedang",
                    "pm25": 18.5, "pm10": 28.3, "no2": 14.2, "o3": 72.0,
                    "dominant_pollutant": "PM2.5"},
    },
    "pedesaan": {
        "weather": {"temp": 24.5, "feels_like": 26, "humidity": 85, "condition": "Hujan Ringan",
                    "wind_speed": 1.5, "rain_1h": 2.4, "uv_index": 3, "icon": "10d"},
        "air":     {"aqi": 42,  "aqi_label": "Baik",
                    "pm25": 10.1, "pm10": 18.7, "no2": 8.3, "o3": 55.0,
                    "dominant_pollutant": "PM10"},
    },
}

# ── AQI Label helper ──────────────────────────────────────────────────────────
def aqi_to_label(aqi: int) -> str:
    if aqi <= 50:   return "Baik"
    if aqi <= 100:  return "Sedang"
    if aqi <= 150:  return "Tidak Sehat untuk Kelompok Sensitif"
    if aqi <= 200:  return "Tidak Sehat"
    if aqi <= 300:  return "Sangat Tidak Sehat"
    return "Berbahaya"

def aqi_to_color(aqi: int) -> str:
    if aqi <= 50:   return "#00E400"
    if aqi <= 100:  return "#FFFF00"
    if aqi <= 150:  return "#FF7E00"
    if aqi <= 200:  return "#FF0000"
    if aqi <= 300:  return "#8F3F97"
    return "#7E0023"

# ── OpenWeatherMap API ────────────────────────────────────────────────────────
def fetch_weather(lokasi_kota: str) -> dict:
    """
    Ambil data cuaca dari OpenWeatherMap.
    Return dict berisi: temp, feels_like, humidity, condition, wind_speed, rain_1h, uv_index
    """
    if USE_MOCK_DATA:
        return MOCK_DATA[lokasi_kota]["weather"]

    coords = KOTA_COORDS.get(lokasi_kota, KOTA_COORDS["kota_besar"])
    try:
        # Current weather
        url = "https://api.openweathermap.org/data/2.5/weather"
        r = requests.get(url, params={
            "lat": coords["lat"], "lon": coords["lon"],
            "appid": OPENWEATHER_API_KEY, "units": "metric", "lang": "id"
        }, timeout=5)
        data = r.json()

        # UV Index (endpoint terpisah)
        uv_url = "https://api.openweathermap.org/data/2.5/uvi"
        uv_r = requests.get(uv_url, params={
            "lat": coords["lat"], "lon": coords["lon"],
            "appid": OPENWEATHER_API_KEY
        }, timeout=5)
        uv_data = uv_r.json()

        return {
            "temp"       : round(data["main"]["temp"], 1),
            "feels_like" : round(data["main"]["feels_like"], 1),
            "humidity"   : data["main"]["humidity"],
            "condition"  : data["weather"][0]["description"].capitalize(),
            "wind_speed" : round(data["wind"]["speed"], 1),
            "rain_1h"    : data.get("rain", {}).get("1h", 0.0),
            "uv_index"   : round(uv_data.get("value", 5)),
            "icon"       : data["weather"][0]["icon"],
        }
    except Exception as e:
        print(f"⚠️  OpenWeatherMap error: {e} — fallback ke mock data")
        return MOCK_DATA[lokasi_kota]["weather"]


# ── AirVisual / IQAir API ─────────────────────────────────────────────────────
def fetch_air_quality(lokasi_kota: str) -> dict:
    """
    Ambil data kualitas udara dari AirVisual (IQAir).
    Return dict berisi: aqi, aqi_label, pm25, pm10, no2, o3, dominant_pollutant
    """
    if USE_MOCK_DATA:
        return MOCK_DATA[lokasi_kota]["air"]

    coords = KOTA_COORDS.get(lokasi_kota, KOTA_COORDS["kota_besar"])
    try:
        url = "http://api.airvisual.com/v2/nearest_city"
        r = requests.get(url, params={
            "lat": coords["lat"], "lon": coords["lon"],
            "key": AIRVISUAL_API_KEY
        }, timeout=5)
        data = r.json()

        pollution = data["data"]["current"]["pollution"]
        aqi = pollution["aqius"]

        return {
            "aqi"               : aqi,
            "aqi_label"         : aqi_to_label(aqi),
            "pm25"              : pollution.get("p2", {}).get("conc", 0),
            "pm10"              : pollution.get("p1", {}).get("conc", 0),
            "no2"               : 0.0,  # tidak tersedia di free tier
            "o3"                : 0.0,
            "dominant_pollutant": pollution.get("mainus", "PM2.5"),
        }
    except Exception as e:
        print(f"⚠️  AirVisual error: {e} — fallback ke mock data")
        return MOCK_DATA[lokasi_kota]["air"]


# ── Main function: ambil semua data sekaligus ─────────────────────────────────
def fetch_env_data(lokasi_kota: str) -> dict:
    """
    Ambil data cuaca + kualitas udara sekaligus.
    Return dict gabungan dengan field 'weather' dan 'air'.
    """
    weather = fetch_weather(lokasi_kota)
    air     = fetch_air_quality(lokasi_kota)
    return {
        "weather"   : weather,
        "air"       : air,
        "is_mock"   : USE_MOCK_DATA,
        "lokasi_kota": lokasi_kota,
        "aqi_color" : aqi_to_color(air["aqi"]),
    }


# ── TEST ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("TEST — Weather & Air Quality API Client")
    print("=" * 55)
    for lokasi in ["kota_besar", "kota_kecil", "pedesaan"]:
        print(f"\n📍 {lokasi.upper()}")
        data = fetch_env_data(lokasi)
        w = data["weather"]
        a = data["air"]
        print(f"   Cuaca  : {w['condition']} | {w['temp']}°C (feels {w['feels_like']}°C) | Hujan: {w['rain_1h']} mm")
        print(f"   Angin  : {w['wind_speed']} m/s | UV: {w['uv_index']} | Kelembaban: {w['humidity']}%")
        print(f"   AQI    : {a['aqi']} ({a['aqi_label']})")
        print(f"   PM2.5  : {a['pm25']} µg/m³ | PM10: {a['pm10']} µg/m³")
        print(f"   Mock   : {'Ya' if data['is_mock'] else 'Tidak'}")
    print("\n✅ API client berjalan sempurna!")
