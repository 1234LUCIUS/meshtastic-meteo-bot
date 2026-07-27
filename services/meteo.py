"""
Service météo — Récupère les prévisions via l'API Open-Meteo (gratuite, sans clé).
Utilise le modèle AROME de Météo-France pour la France.
"""

import logging
from datetime import datetime
from typing import Optional

import requests

from bot.config import WMO_CODES, DEFAULT_LATITUDE, DEFAULT_LONGITUDE

logger = logging.getLogger(__name__)

# API Open-Meteo — Gratuite, sans clé, basée sur les modèles Météo-France
OPEN_METEO_URL = "https://api.open-meteo.com/v1/meteofrance"

# Timeout des requêtes HTTP
REQUEST_TIMEOUT = 10


class MeteoService:
    """
    Service de prévisions météo utilisant l'API Open-Meteo avec le modèle Météo-France.
    """

    def get_forecast(
        self,
        latitude: float,
        longitude: float,
        location_name: str = "",
    ) -> Optional[dict]:
        """
        Récupère les prévisions météo pour une position GPS.

        :param latitude: Latitude en degrés décimaux.
        :param longitude: Longitude en degrés décimaux.
        :param location_name: Nom du lieu (pour l'affichage).
        :return: Dictionnaire de prévisions ou None en cas d'erreur.
        """
        params = {
            "latitude": round(latitude, 4),
            "longitude": round(longitude, 4),
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "weather_code",
                "wind_speed_10m",
                "wind_direction_10m",
                "precipitation",
                "pressure_msl",
            ],
            "hourly": [
                "temperature_2m",
                "weather_code",
                "precipitation_probability",
                "wind_speed_10m",
            ],
            "daily": [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "wind_speed_10m_max",
                "sunrise",
                "sunset",
            ],
            "forecast_days": 3,
            "timezone": "Europe/Paris",
        }

        try:
            response = requests.get(OPEN_METEO_URL, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            return self._parse_forecast(data, location_name)
        except requests.RequestException as e:
            logger.error(f"Erreur API Open-Meteo : {e}")
            return None

    def format_current_weather(self, forecast: dict) -> str:
        """
        Formate les données météo actuelles en message Meshtastic (court).

        :param forecast: Données retournées par get_forecast().
        :return: Message texte formaté.
        """
        if not forecast:
            return "Météo indisponible."

        current = forecast.get("current", {})
        location = forecast.get("location", "")
        daily = forecast.get("daily", [])

        loc_str = f" — {location}" if location else ""
        time_str = datetime.now().strftime("%d/%m %H:%M")

        # Ligne principale
        lines = [
            f"🌤 MÉTÉO{loc_str} [{time_str}]",
            f"{current.get('description', 'N/A')}",
            f"Temp: {current.get('temperature', 'N/A')}°C "
            f"(ressenti {current.get('apparent_temperature', 'N/A')}°C)",
            f"Vent: {current.get('wind_speed', 'N/A')} km/h {current.get('wind_direction_str', '')}",
            f"Humidité: {current.get('humidity', 'N/A')}% | "
            f"Pression: {current.get('pressure', 'N/A')} hPa",
        ]

        if current.get("precipitation", 0) > 0:
            lines.append(f"Précip: {current.get('precipitation', 0)} mm")

        # Prévisions J+1 et J+2
        if len(daily) >= 2:
            lines.append("--- Prévisions ---")
            for day in daily[:3]:
                lines.append(
                    f"{day['date_str']}: {day['description']} "
                    f"{day['temp_min']}°/{day['temp_max']}°C"
                )

        lines.append("Source: Météo-France via open-meteo.com")
        return "\n".join(lines)

    def format_broadcast_message(self, forecast: dict) -> str:
        """
        Formate un message de diffusion périodique (plus concis).
        """
        if not forecast:
            return "Météo indisponible."

        current = forecast.get("current", {})
        location = forecast.get("location", "")
        daily = forecast.get("daily", [])

        loc_str = f"{location} — " if location else ""
        time_str = datetime.now().strftime("%H:%M")

        msg = (
            f"📡 MÉTÉO [{time_str}] {loc_str}"
            f"{current.get('description', '')}, "
            f"{current.get('temperature', 'N/A')}°C, "
            f"Vent {current.get('wind_speed', 'N/A')} km/h"
        )

        if daily:
            today = daily[0]
            msg += (
                f" | Auj: {today['temp_min']}°/{today['temp_max']}°C"
            )

        return msg

    # -------------------------------------------------------------------------
    # Parsing interne
    # -------------------------------------------------------------------------

    def _parse_forecast(self, data: dict, location_name: str) -> dict:
        """Parse la réponse de l'API Open-Meteo."""
        current_data = data.get("current", {})
        hourly_data = data.get("hourly", {})
        daily_data = data.get("daily", {})

        # Données actuelles
        current = {
            "temperature": round(current_data.get("temperature_2m", 0), 1),
            "apparent_temperature": round(current_data.get("apparent_temperature", 0), 1),
            "humidity": current_data.get("relative_humidity_2m"),
            "wind_speed": round(current_data.get("wind_speed_10m", 0), 1),
            "wind_direction": current_data.get("wind_direction_10m"),
            "wind_direction_str": self._wind_direction_str(
                current_data.get("wind_direction_10m", 0)
            ),
            "precipitation": current_data.get("precipitation", 0),
            "pressure": round(current_data.get("pressure_msl", 0), 0),
            "weather_code": current_data.get("weather_code", 0),
            "description": WMO_CODES.get(current_data.get("weather_code", 0), "Inconnu"),
        }

        # Prévisions journalières
        daily = []
        dates = daily_data.get("time", [])
        for i, date_str in enumerate(dates[:3]):
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                day_names = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
                day_name = day_names[date_obj.weekday()]

                daily.append({
                    "date": date_str,
                    "date_str": f"{day_name} {date_obj.strftime('%d/%m')}",
                    "description": WMO_CODES.get(
                        daily_data.get("weather_code", [0])[i], "Inconnu"
                    ),
                    "temp_max": round(daily_data.get("temperature_2m_max", [0])[i], 1),
                    "temp_min": round(daily_data.get("temperature_2m_min", [0])[i], 1),
                    "precipitation": round(daily_data.get("precipitation_sum", [0])[i], 1),
                    "wind_max": round(daily_data.get("wind_speed_10m_max", [0])[i], 1),
                    "sunrise": daily_data.get("sunrise", [""])[i],
                    "sunset": daily_data.get("sunset", [""])[i],
                })
            except (IndexError, ValueError) as e:
                logger.debug(f"Erreur parsing jour {i}: {e}")

        return {
            "location": location_name,
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone"),
            "current": current,
            "daily": daily,
        }

    @staticmethod
    def _wind_direction_str(degrees: float) -> str:
        """Convertit un angle en direction cardinale."""
        if degrees is None:
            return ""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                      "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"]
        idx = round(degrees / 22.5) % 16
        return directions[idx]
