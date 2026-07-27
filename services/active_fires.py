"""
Service de suivi des feux actifs — Détecte les incendies en cours.
Utilise les données de la NASA (FIRMS) et des sources locales françaises.
"""

import logging
from typing import List, Optional
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# NASA FIRMS API (Active Fires)
# Nécessite une clé API (gratuite sur firms.modaps.eosdis.nasa.gov)
# En l'absence de clé, on peut utiliser les fichiers CSV/JSON publics de la NASA
NASA_FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
# Coordonnées approximatives de la France (Bounding Box)
FRANCE_BBOX = "-5.5,41.3,9.6,51.1"

# Sources alternatives (flux RSS feuxdeforet.fr si disponible)
FEUX_DE_FORET_RSS = "https://feuxdeforet.fr/feed/"

REQUEST_TIMEOUT = 15

class ActiveFiresService:
    """
    Service pour suivre les feux actifs en temps réel.
    """

    def __init__(self, nasa_api_key: Optional[str] = None):
        from bot.config import NASA_API_KEY
        self.api_key = nasa_api_key or NASA_API_KEY

    def get_active_fires_near(self, latitude: float, longitude: float, radius_km: int = 50) -> List[dict]:
        """
        Récupère les feux actifs dans un rayon donné autour d'une position.
        """
        # 1. Tentative via NASA FIRMS (données satellites MODIS/VIIRS)
        fires = self._fetch_nasa_firms(latitude, longitude, radius_km)
        
        # 2. On peut aussi croiser avec des signalements RSS
        # (À implémenter si une source fiable est trouvée)
        
        return fires

    def _fetch_nasa_firms(self, lat: float, lon: float, radius: int) -> List[dict]:
        """Récupère les feux actifs via l'API NASA FIRMS."""
        if not self.api_key:
            logger.warning("NASA FIRMS API Key manquante. Suivi limité.")
            return []

        try:
            # L'API NASA FIRMS permet de récupérer les feux par zone
            # Format: area/csv/[KEY]/[SOURCE]/[BBOX]/[DAY_RANGE]
            url = f"{NASA_FIRMS_URL}/{self.api_key}/VIIRS_SNPP_NRT/{FRANCE_BBOX}/1"
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            # Parsing simplifié du CSV
            lines = response.text.strip().split('\n')
            if len(lines) <= 1:
                return []

            header = lines[0].split(',')
            fire_list = []
            
            for line in lines[1:]:
                values = line.split(',')
                fire_lat = float(values[header.index('latitude')])
                fire_lon = float(values[header.index('longitude')])
                
                # Calcul de distance rudimentaire
                dist = self._calculate_distance(lat, lon, fire_lat, fire_lon)
                if dist <= radius:
                    fire_list.append({
                        "latitude": fire_lat,
                        "longitude": fire_lon,
                        "distance": round(dist, 1),
                        "confidence": values[header.index('confidence')],
                        "time": values[header.index('acq_time')],
                        "date": values[header.index('acq_date')]
                    })
            
            return sorted(fire_list, key=lambda x: x['distance'])

        except Exception as e:
            logger.error(f"Erreur NASA FIRMS : {e}")
            return []

    def format_fires_message(self, fires: List[dict], location_name: str) -> str:
        """Formate le message de suivi des feux."""
        if not fires:
            return f"✅ Aucun feu actif détecté par satellite dans un rayon de 50km autour de {location_name}."

        lines = [f"🔥 {len(fires)} FEU(S) ACTIF(S) DÉTECTÉ(S) (Rayon 50km de {location_name}) :"]
        
        # Limiter à 5 feux pour la taille du message Meshtastic
        for fire in fires[:5]:
            conf = fire['confidence']
            conf_str = "Élevée" if conf == 'h' else ("Normale" if conf == 'n' else "Faible")
            lines.append(f"• {fire['distance']}km | Confiance: {conf_str} | Obs: {fire['time']}")

        lines.append("Source: NASA FIRMS (Données Satellites)")
        lines.append("⚠️ Prudence. Ne vous approchez pas.")
        return "\n".join(lines)

    @staticmethod
    def _calculate_distance(lat1, lon1, lat2, lon2):
        """Calcul de distance Haversine simplifié."""
        import math
        R = 6371  # Rayon de la Terre en km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
