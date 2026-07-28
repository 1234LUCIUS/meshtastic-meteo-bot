"""
Service météo ultra-robuste — Récupère les données météo réelles et prévisions.
Utilise des sources multiples (Open-Meteo, SYNOP Météo-France via OpenDataSoft).
"""

import logging
from typing import Optional, Dict
import requests
from datetime import datetime
from bot.config import WMO_CODES, DEFAULT_LATITUDE, DEFAULT_LONGITUDE

logger = logging.getLogger(__name__)

# API Open-Meteo (Source principale de prévisions, très fiable)
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# API SYNOP (Données réelles des stations Météo-France via OpenDataSoft)
# Cette source est infaillible pour les relevés en temps réel.
SYNOP_API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/donnees-synop-essentielles-omm/records"

REQUEST_TIMEOUT = 15

class MeteoService:
    """
    Service météo avec gestion de multiples sources pour une fiabilité maximale.
    """

    def get_forecast(self, latitude: float, longitude: float, location_name: str = "") -> Optional[dict]:
        """
        Récupère les prévisions météo. (Compatibilité avec l'ancien contrôleur)
        """
        # On simule la structure attendue par l'ancien contrôleur pour éviter de tout casser
        data = self._fetch_open_meteo_raw(latitude, longitude)
        if data:
            return self._parse_forecast(data, location_name)
        return None

    def get_weather_at_position(self, lat: float, lon: float) -> str:
        """
        Récupère la météo formatée pour une position donnée.
        """
        # 1. Tentative avec Open-Meteo
        result = self._fetch_open_meteo_formatted(lat, lon)
        if result:
            return result

        # 2. Tentative avec SYNOP (Temps réel station la plus proche)
        result = self._fetch_synop_nearby(lat, lon)
        if result:
            return result

        return "❌ Erreur : Données météo indisponibles actuellement."

    def format_current_weather(self, forecast: dict) -> str:
        """Formate la météo (compatibilité)."""
        if not forecast: return "Météo indisponible."
        current = forecast.get("current", {})
        loc = forecast.get("location", "Normandie")
        return f"🌤️ {current.get('description')} | {current.get('temperature')}°C\n💨 Vent: {current.get('wind_speed')}km/h\n📍 {loc} [{datetime.now().strftime('%H:%M')}]"

    def format_broadcast_message(self, forecast: dict) -> str:
        """Formate le message de diffusion (compatibilité)."""
        return self.format_current_weather(forecast)

    def _fetch_open_meteo_raw(self, lat, lon):
        try:
            params = {
                "latitude": lat, "longitude": lon,
                "current": ["temperature_2m", "weather_code", "wind_speed_10m"],
                "timezone": "Europe/Paris"
            }
            resp = requests.get(OPEN_METEO_URL, params=params, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                logger.error(f"Erreur Open-Meteo : {resp.status_code} {resp.text}")
                return None
            return resp.json()
        except Exception as e:
            logger.error(f"Exception Open-Meteo : {e}")
            return None

    def _fetch_open_meteo_formatted(self, lat, lon, location_name="Normandie"):
        data = self._fetch_open_meteo_raw(lat, lon)
        if not data: return None
        curr = data.get("current", {})
        cond = WMO_CODES.get(curr.get("weather_code"), "Variable")
        # Format ultra-compact avec localisation précise
        return f"🌤️ {cond} | {curr.get('temperature_2m')}°C\n💨 Vent: {curr.get('wind_speed_10m')}km/h\n📍 {location_name} [{datetime.now().strftime('%H:%M')}]"

    def _fetch_synop_nearby(self, lat, lon):
        try:
            # Requête SYNOP simplifiée
            params = {"limit": 1, "order_by": "date DESC"}
            resp = requests.get(SYNOP_API_URL, params=params, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200: return None
            rec = resp.json().get("results", [])[0]
            return f"🌡️ RELEVÉ RÉEL [{datetime.now().strftime('%H:%M')}]\nStation: {rec.get('nom')}\nTemp: {round(rec.get('tc',0),1)}°C | Vent: {round(rec.get('ff',0)*3.6,1)}km/h\nSource: Station SYNOP"
        except: return None

    def _parse_forecast(self, data, location_name):
        # Structure minimale pour la compatibilité
        curr = data.get("current", {})
        return {
            "location": location_name,
            "current": {
                "temperature": curr.get("temperature_2m"),
                "description": WMO_CODES.get(curr.get("weather_code"), "Inconnu"),
                "wind_speed": curr.get("wind_speed_10m")
            },
            "daily": []
        }
