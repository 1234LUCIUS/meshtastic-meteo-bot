"""
Tests unitaires des services du Meshtastic Météo Bot.
Utilise des mocks pour éviter les appels réseau réels.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMeteoService(unittest.TestCase):
    """Tests du service météo."""

    def setUp(self):
        from services.meteo import MeteoService
        self.service = MeteoService()

    def test_wind_direction_str(self):
        """Teste la conversion d'angle en direction cardinale."""
        from services.meteo import MeteoService
        self.assertEqual(MeteoService._wind_direction_str(0), "N")
        self.assertEqual(MeteoService._wind_direction_str(90), "E")
        self.assertEqual(MeteoService._wind_direction_str(180), "S")
        self.assertEqual(MeteoService._wind_direction_str(270), "O")
        self.assertEqual(MeteoService._wind_direction_str(45), "NE")

    def test_split_message_short(self):
        """Un message court ne doit pas être découpé."""
        from bot.meshtastic_client import MeshtasticClient
        text = "Hello Mesh!"
        parts = MeshtasticClient._split_message(text)
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0], text)

    def test_split_message_long(self):
        """Un message long doit être découpé en plusieurs parties."""
        from bot.meshtastic_client import MeshtasticClient
        # 300 mots de 1 caractère séparés par des espaces = bien plus de 228 octets
        text = " ".join(["A"] * 300)
        parts = MeshtasticClient._split_message(text)
        self.assertGreater(len(parts), 1)
        for part in parts:
            self.assertLessEqual(len(part.encode("utf-8")), 228)

    @patch("services.meteo.requests.get")
    def test_get_forecast_success(self, mock_get):
        """Teste la récupération des prévisions avec une réponse simulée."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "timezone": "Europe/Paris",
            "current": {
                "temperature_2m": 22.5,
                "apparent_temperature": 21.0,
                "relative_humidity_2m": 65,
                "wind_speed_10m": 15.0,
                "wind_direction_10m": 270,
                "precipitation": 0.0,
                "pressure_msl": 1013.0,
                "weather_code": 1,
            },
            "daily": {
                "time": ["2026-07-27", "2026-07-28", "2026-07-29"],
                "weather_code": [1, 3, 61],
                "temperature_2m_max": [28.0, 25.0, 20.0],
                "temperature_2m_min": [18.0, 16.0, 14.0],
                "precipitation_sum": [0.0, 0.0, 5.2],
                "wind_speed_10m_max": [20.0, 25.0, 30.0],
                "sunrise": ["2026-07-27T06:15", "2026-07-28T06:16", "2026-07-29T06:17"],
                "sunset": ["2026-07-27T21:45", "2026-07-28T21:44", "2026-07-29T21:43"],
            },
            "hourly": {
                "time": [],
                "temperature_2m": [],
                "weather_code": [],
                "precipitation_probability": [],
                "wind_speed_10m": [],
            },
        }
        mock_get.return_value = mock_response

        forecast = self.service.get_forecast(48.8566, 2.3522, "Paris")
        self.assertIsNotNone(forecast)
        self.assertEqual(forecast["location"], "Paris")
        self.assertEqual(forecast["current"]["temperature"], 22.5)
        self.assertEqual(forecast["current"]["description"], "Principalement dégagé")

    @patch("services.meteo.requests.get")
    def test_get_forecast_failure(self, mock_get):
        """Teste la gestion d'une erreur réseau."""
        import requests
        mock_get.side_effect = requests.RequestException("Connexion refusée")
        forecast = self.service.get_forecast(48.8566, 2.3522)
        self.assertIsNone(forecast)

    def test_format_current_weather_none(self):
        """Teste le formatage avec des données None."""
        result = self.service.format_current_weather(None)
        self.assertEqual(result, "Météo indisponible.")


class TestGeocodingService(unittest.TestCase):
    """Tests du service de géocodage."""

    def setUp(self):
        from services.geocoding import GeocodingService
        self.service = GeocodingService()

    def test_parse_address_paris(self):
        """Teste le parsing d'une adresse parisienne."""
        from services.geocoding import GeocodingService
        address = {
            "city": "Paris",
            "county": "Paris",
            "postcode": "75001",
            "country": "France",
        }
        result = GeocodingService._parse_address(address)
        self.assertEqual(result["city"], "Paris")
        self.assertEqual(result["department_code"], "75")
        self.assertEqual(result["country"], "France")

    def test_parse_address_marseille(self):
        """Teste le parsing d'une adresse marseillaise."""
        from services.geocoding import GeocodingService
        address = {
            "city": "Marseille",
            "county": "Bouches-du-Rhône",
            "postcode": "13001",
            "country": "France",
        }
        result = GeocodingService._parse_address(address)
        self.assertEqual(result["city"], "Marseille")
        self.assertEqual(result["department_code"], "13")

    @patch("services.geocoding.requests.get")
    def test_geocode_city_not_found(self, mock_get):
        """Teste le cas où la ville n'est pas trouvée."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = self.service.geocode_city("VilleInexistante123")
        self.assertIsNone(result)


class TestMeshtasticClient(unittest.TestCase):
    """Tests du client Meshtastic en mode simulation."""

    def setUp(self):
        from bot.meshtastic_client import MeshtasticClient
        self.client = MeshtasticClient(simulation_mode=True)

    def test_connect_simulation(self):
        """La connexion en mode simulation doit toujours réussir."""
        result = self.client.connect()
        self.assertTrue(result)
        self.assertTrue(self.client.connected)

    def test_send_text_simulation(self):
        """L'envoi en mode simulation doit toujours réussir."""
        result = self.client.send_text("Test message")
        self.assertTrue(result)

    def test_get_local_node_info_simulation(self):
        """Les infos du nœud local en simulation doivent retourner des données."""
        info = self.client.get_local_node_info()
        self.assertIn("latitude", info)
        self.assertIn("longitude", info)


class TestCommandParser(unittest.TestCase):
    """Tests du parseur de commandes."""

    def setUp(self):
        from bot.meshtastic_client import MeshtasticClient
        from bot.controller import BotController
        from bot.commands import CommandParser

        client = MeshtasticClient(simulation_mode=True)
        client.connect()
        self.controller = BotController(client)
        self.parser = CommandParser(self.controller)

    def test_ping_command(self):
        """La commande !ping doit retourner 'Pong!'."""
        response = self.parser.handle("!node1", "!ping", {})
        self.assertIsNotNone(response)
        self.assertIn("Pong", response)

    def test_aide_command(self):
        """La commande !aide doit retourner l'aide."""
        response = self.parser.handle("!node1", "!aide", {})
        self.assertIsNotNone(response)
        self.assertIn("!meteo", response)

    def test_unknown_command(self):
        """Une commande inconnue doit retourner un message d'erreur."""
        response = self.parser.handle("!node1", "!inconnu", {})
        self.assertIsNotNone(response)
        self.assertIn("inconnue", response.lower())

    def test_non_command_message(self):
        """Un message sans '!' ne doit pas être traité."""
        response = self.parser.handle("!node1", "Bonjour tout le monde", {})
        self.assertIsNone(response)


class TestVigilanceLevels(unittest.TestCase):
    """Tests des niveaux de vigilance."""

    def test_vigilance_levels_defined(self):
        """Tous les niveaux de vigilance doivent être définis."""
        from bot.config import VIGILANCE_LEVELS
        for level in [1, 2, 3, 4]:
            self.assertIn(level, VIGILANCE_LEVELS)
            self.assertIn("name", VIGILANCE_LEVELS[level])
            self.assertIn("label", VIGILANCE_LEVELS[level])

    def test_vigilance_phenomena_defined(self):
        """Les phénomènes météo doivent être définis."""
        from bot.config import VIGILANCE_PHENOMENA
        self.assertIn("WIND", VIGILANCE_PHENOMENA)
        self.assertIn("THUNDERSTORM", VIGILANCE_PHENOMENA)
        self.assertIn("FLOOD", VIGILANCE_PHENOMENA)


if __name__ == "__main__":
    unittest.main(verbosity=2)
