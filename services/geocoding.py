"""
Service de géocodage — Convertit des coordonnées GPS en nom de ville/département
et des noms de villes en coordonnées GPS.

Utilise l'API Nominatim d'OpenStreetMap (gratuite, sans clé).
"""

import logging
import time
from typing import Optional

import requests

logger = logging.getLogger(__name__)

NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
REQUEST_TIMEOUT = 10
USER_AGENT = "MeshtasticMeteoBotFrance/1.0 (github.com/meshtastic-meteo-bot)"

# Cache simple pour éviter les requêtes répétées
_geocode_cache: dict = {}
_reverse_cache: dict = {}


class GeocodingService:
    """
    Service de géocodage utilisant l'API Nominatim d'OpenStreetMap.
    Respecte les limites d'utilisation : 1 requête/seconde maximum.
    """

    def __init__(self):
        self._last_request_time = 0.0

    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[dict]:
        """
        Convertit des coordonnées GPS en informations de localisation.

        :param latitude: Latitude en degrés décimaux.
        :param longitude: Longitude en degrés décimaux.
        :return: Dictionnaire avec city, department, department_code, country, ou None.
        """
        cache_key = f"{round(latitude, 3)},{round(longitude, 3)}"
        if cache_key in _reverse_cache:
            return _reverse_cache[cache_key]

        self._rate_limit()

        try:
            params = {
                "lat": latitude,
                "lon": longitude,
                "format": "jsonv2",
                "addressdetails": 1,
                "accept-language": "fr",
            }
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(
                f"{NOMINATIM_BASE_URL}/reverse",
                params=params,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            result = self._parse_address(data.get("address", {}))
            _reverse_cache[cache_key] = result
            return result

        except Exception as e:
            logger.error(f"Erreur géocodage inverse ({latitude}, {longitude}) : {e}")
            return None

    def geocode_city(self, city_name: str, country: str = "France") -> Optional[dict]:
        """
        Convertit un nom de ville en coordonnées GPS.

        :param city_name: Nom de la ville ou de la zone.
        :param country: Pays (défaut : France).
        :return: Dictionnaire avec latitude, longitude, display_name, department_code.
        """
        cache_key = f"{city_name.lower().strip()}_{country.lower()}"
        if cache_key in _geocode_cache:
            return _geocode_cache[cache_key]

        self._rate_limit()

        try:
            params = {
                "q": f"{city_name}, {country}",
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": 1,
                "accept-language": "fr",
                "countrycodes": "fr",
            }
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(
                f"{NOMINATIM_BASE_URL}/search",
                params=params,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            results = response.json()

            if not results:
                logger.warning(f"Aucun résultat pour '{city_name}'")
                return None

            data = results[0]
            address = data.get("address", {})
            location_info = self._parse_address(address)

            result = {
                "latitude": float(data.get("lat", 0)),
                "longitude": float(data.get("lon", 0)),
                "display_name": data.get("display_name", city_name),
                "city": location_info.get("city", city_name),
                "department": location_info.get("department"),
                "department_code": location_info.get("department_code"),
                "country": location_info.get("country"),
            }

            _geocode_cache[cache_key] = result
            return result

        except Exception as e:
            logger.error(f"Erreur géocodage '{city_name}' : {e}")
            return None

    def get_department_code(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Retourne le code du département pour une position GPS.

        :return: Code département (ex: "75", "13", "2A") ou None.
        """
        location = self.reverse_geocode(latitude, longitude)
        if location:
            return location.get("department_code")
        return None

    def get_city_name(self, latitude: float, longitude: float) -> str:
        """
        Retourne le nom de la ville pour une position GPS.
        """
        location = self.reverse_geocode(latitude, longitude)
        if location:
            return location.get("city") or location.get("display_name", "Position inconnue")
        return "Position inconnue"

    # -------------------------------------------------------------------------
    # Utilitaires internes
    # -------------------------------------------------------------------------

    def _rate_limit(self):
        """Respecte la limite d'1 requête par seconde de Nominatim."""
        elapsed = time.time() - self._last_request_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self._last_request_time = time.time()

    @staticmethod
    def _parse_address(address: dict) -> dict:
        """Parse les données d'adresse Nominatim."""
        # Nom de la ville (plusieurs champs possibles selon le niveau)
        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
            or address.get("county")
            or ""
        )

        # Département
        department = address.get("county") or address.get("state_district") or ""

        # Code département (extrait du code postal ou du champ ISO)
        postcode = address.get("postcode", "")
        dept_code = ""
        if postcode and len(postcode) >= 2:
            prefix = postcode[:2]
            # Cas spéciaux : Corse (2A, 2B), DOM-TOM
            if prefix == "20":
                dept_code = "20"  # Sera affiné si nécessaire
            elif prefix in ("97", "98"):
                dept_code = postcode[:3]
            else:
                dept_code = prefix

        # Fallback : utiliser le code ISO de la région
        if not dept_code:
            iso = address.get("ISO3166-2-lvl6", "")
            if iso and "-" in iso:
                dept_code = iso.split("-")[-1]

        return {
            "city": city,
            "department": department,
            "department_code": dept_code,
            "country": address.get("country", ""),
            "postcode": postcode,
        }
