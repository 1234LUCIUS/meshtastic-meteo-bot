"""
Contrôleur principal du bot — Orchestre tous les services et gère la logique métier.
"""

import logging
from typing import Optional

from bot.config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_DEPARTMENT
from services.meteo import MeteoService
from services.vigilance import VigilanceService
from services.geocoding import GeocodingService
from services.official_sources import OfficialSourcesService

logger = logging.getLogger(__name__)


class BotController:
    """
    Contrôleur central qui coordonne les services météo, vigilance, géocodage
    et sources officielles.
    """

    def __init__(self, meshtastic_client):
        self.client = meshtastic_client
        self.meteo_service = MeteoService()
        self.vigilance_service = VigilanceService()
        self.geocoding_service = GeocodingService()
        self.official_sources_service = OfficialSourcesService()

    # =========================================================================
    # Météo
    # =========================================================================

    def get_weather_for_city(self, city_name: str) -> str:
        """Retourne la météo pour une ville donnée par son nom."""
        logger.info(f"Météo demandée pour la ville : {city_name}")

        location = self.geocoding_service.geocode_city(city_name)
        if not location:
            return f"Ville '{city_name}' introuvable. Vérifiez l'orthographe."

        lat = location["latitude"]
        lon = location["longitude"]
        display_name = location.get("city") or city_name

        forecast = self.meteo_service.get_forecast(lat, lon, location_name=display_name)
        return self.meteo_service.format_current_weather(forecast)

    def get_weather_for_position(self, latitude: float, longitude: float) -> str:
        """Retourne la météo pour une position GPS."""
        logger.info(f"Météo demandée pour GPS ({latitude}, {longitude})")

        city_name = self.geocoding_service.get_city_name(latitude, longitude)
        forecast = self.meteo_service.get_forecast(latitude, longitude, location_name=city_name)
        return self.meteo_service.format_current_weather(forecast)

    def get_weather_default(self) -> str:
        """Retourne la météo pour la position par défaut configurée."""
        logger.info("Météo demandée pour la position par défaut.")
        city_name = self.geocoding_service.get_city_name(DEFAULT_LATITUDE, DEFAULT_LONGITUDE)
        forecast = self.meteo_service.get_forecast(
            DEFAULT_LATITUDE, DEFAULT_LONGITUDE, location_name=city_name
        )
        return self.meteo_service.format_current_weather(forecast)

    def get_weather_broadcast_message(self) -> str:
        """Génère le message de diffusion météo périodique."""
        city_name = self.geocoding_service.get_city_name(DEFAULT_LATITUDE, DEFAULT_LONGITUDE)
        forecast = self.meteo_service.get_forecast(
            DEFAULT_LATITUDE, DEFAULT_LONGITUDE, location_name=city_name
        )
        return self.meteo_service.format_broadcast_message(forecast)

    # =========================================================================
    # Vigilance Météo-France
    # =========================================================================

    def get_vigilance_summary(self, department: Optional[str] = None) -> str:
        """Retourne le résumé de vigilance pour un département ou le national."""
        dept = department or DEFAULT_DEPARTMENT

        if dept:
            data = self.vigilance_service.get_vigilance_by_department(dept)
            return self.vigilance_service.format_vigilance_message(dept, data)
        else:
            alerts = self.vigilance_service.get_all_active_alerts()
            return self.vigilance_service.format_national_summary(alerts)

    def fetch_all_vigilance_alerts(self) -> list:
        """Récupère toutes les alertes actives (utilisé par le scheduler)."""
        return self.vigilance_service.get_all_active_alerts()

    def get_department_from_position(
        self, latitude: float, longitude: float
    ) -> Optional[str]:
        """Retourne le code département pour une position GPS."""
        return self.geocoding_service.get_department_code(latitude, longitude)

    # =========================================================================
    # Vigicrues
    # =========================================================================

    def get_vigicrues_summary(self, department: Optional[str] = None) -> str:
        """Retourne le résumé des alertes crues."""
        if department:
            alerts = self.official_sources_service.get_vigicrues_by_department(department)
        else:
            alerts = self.official_sources_service.get_vigicrues_national()
        return self.official_sources_service.format_vigicrues_message(alerts)

    # =========================================================================
    # Sources officielles
    # =========================================================================

    def get_official_sources_summary(self, department: Optional[str] = None) -> str:
        """Retourne un résumé des informations des sources officielles."""
        dept = department or DEFAULT_DEPARTMENT
        return self.official_sources_service.format_official_summary(dept)

    # =========================================================================
    # Réponse aux messages entrants
    # =========================================================================

    def handle_incoming_message(self, sender_id: str, text: str, packet: dict):
        """
        Traite un message entrant et envoie la réponse appropriée.
        Appelé par le client Meshtastic.
        """
        from bot.commands import CommandParser
        parser = CommandParser(self)
        response = parser.handle(sender_id, text, packet)

        if response:
            # Répondre directement à l'expéditeur
            self.client.send_text(response, destination=sender_id)
