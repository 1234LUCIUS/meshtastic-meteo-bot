"""
Module de configuration central.
Charge les paramètres depuis le fichier .env et fournit des valeurs par défaut.
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

# --- Connexion Meshtastic ---
MESHTASTIC_CONNECTION_TYPE = os.getenv("MESHTASTIC_CONNECTION_TYPE", "serial").lower()
MESHTASTIC_SERIAL_PORT = os.getenv("MESHTASTIC_SERIAL_PORT", "/dev/ttyUSB0")
MESHTASTIC_TCP_HOST = os.getenv("MESHTASTIC_TCP_HOST", "localhost")

# --- Paramètres météo ---
DEFAULT_DEPARTMENT = os.getenv("DEFAULT_DEPARTMENT", "75")
DEFAULT_LATITUDE = float(os.getenv("DEFAULT_LATITUDE", "48.8566"))
DEFAULT_LONGITUDE = float(os.getenv("DEFAULT_LONGITUDE", "2.3522"))

# --- Canaux Meshtastic ---
BROADCAST_CHANNEL = int(os.getenv("BROADCAST_CHANNEL", "0"))
ALERT_CHANNEL = int(os.getenv("ALERT_CHANNEL", "0"))

# --- Clé API Météo-France ---
METEOFRANCE_API_KEY = os.getenv("METEOFRANCE_API_KEY", "")
NASA_API_KEY = os.getenv("NASA_API_KEY", "")

# --- Intervalles (en minutes) ---
METEO_BROADCAST_INTERVAL = int(os.getenv("METEO_BROADCAST_INTERVAL", "360"))
ALERT_CHECK_INTERVAL = int(os.getenv("ALERT_CHECK_INTERVAL", "15"))
ALERT_REPORT_INTERVAL = int(os.getenv("ALERT_REPORT_INTERVAL", "60"))

# --- Niveau minimum d'alerte pour déclenchement ---
ALERT_TRIGGER_LEVEL = int(os.getenv("ALERT_TRIGGER_LEVEL", "3"))

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "logs/bot.log")

# Couleurs / niveaux de vigilance Météo-France
VIGILANCE_LEVELS = {
    1: {"name": "VERT", "label": "Pas de vigilance particulière", "emoji": "🟢"},
    2: {"name": "JAUNE", "label": "Soyez attentif", "emoji": "🟡"},
    3: {"name": "ORANGE", "label": "Soyez très vigilant", "emoji": "🟠"},
    4: {"name": "ROUGE", "label": "Vigilance absolue", "emoji": "🔴"},
}

# Phénomènes météo surveillés
VIGILANCE_PHENOMENA = {
    "WIND": "Vent violent",
    "RAIN_FLOOD": "Pluie-inondation",
    "THUNDERSTORM": "Orages",
    "FLOOD": "Crues",
    "SNOW_ICE": "Neige-verglas",
    "HEAT_WAVE": "Canicule",
    "COLD_WAVE": "Grand froid",
    "AVALANCHE": "Avalanches",
    "COAST_FLOOD": "Vagues-submersion",
}

# Correspondance codes WMO -> description météo
WMO_CODES = {
    0: "Ciel dégagé",
    1: "Principalement dégagé",
    2: "Partiellement nuageux",
    3: "Couvert",
    45: "Brouillard",
    48: "Brouillard givrant",
    51: "Bruine légère",
    53: "Bruine modérée",
    55: "Bruine dense",
    61: "Pluie légère",
    63: "Pluie modérée",
    65: "Pluie forte",
    71: "Neige légère",
    73: "Neige modérée",
    75: "Neige forte",
    77: "Grains de neige",
    80: "Averses légères",
    81: "Averses modérées",
    82: "Averses violentes",
    85: "Averses de neige légères",
    86: "Averses de neige fortes",
    95: "Orage",
    96: "Orage avec grêle légère",
    99: "Orage avec grêle forte",
}


def setup_logging():
    """Configure le système de logging."""
    import os
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    log_level = getattr(logging, LOG_LEVEL, logging.INFO)

    handlers = [logging.StreamHandler()]
    if LOG_FILE:
        # Utiliser os.path.normpath pour la compatibilité des chemins Windows/Linux
        log_path = os.path.normpath(LOG_FILE)
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
    return logging.getLogger("meshtastic_meteo_bot")
