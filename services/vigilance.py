"""
Service de vigilance météo — Récupère les alertes Météo-France.
Version ultra-robuste utilisant prioritairement l'Open Data.
"""

import logging
import requests
from typing import Optional
from bot.config import VIGILANCE_LEVELS, VIGILANCE_PHENOMENA, METEOFRANCE_API_KEY

logger = logging.getLogger(__name__)

# Fallback : API data.gouv.fr (open data, sans clé) via Opendatasoft v2.1
DATAGOUV_VIGILANCE_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/weatherref-france-vigilance-meteo-national/records"
REQUEST_TIMEOUT = 10

class VigilanceService:
    """
    Service d'accès aux alertes de vigilance météorologique de Météo-France.
    """

    def get_vigilance_by_department(self, department: str) -> Optional[dict]:
        """Récupère le niveau de vigilance pour un département avec fallback cache."""
        from services.storage import StorageService
        storage = StorageService()
        cache_key = f"vigilance_{department}"

        # Tentative réseau
        data = self._fetch_via_datagouv(department)
        if data and not data.get("error"):
            storage.save(cache_key, data)
            return data
        
        # Fallback cache
        cached_data, timestamp = storage.get(cache_key)
        if cached_data:
            cached_data["is_cached"] = True
            cached_data["cache_age"] = storage.get_formatted_age(timestamp)
            return cached_data
            
        return data # Retourne le dernier résultat (éventuellement None)

    def get_all_active_alerts(self) -> list:
        """Récupère toutes les alertes actives au niveau national."""
        return self._fetch_all_via_datagouv()

    def _fetch_via_datagouv(self, department: str) -> Optional[dict]:
        """Récupère les données via l'API Open Data."""
        try:
            params = {
                "where": f'dep_code = "{department}"',
                "limit": 1
            }
            response = requests.get(DATAGOUV_VIGILANCE_URL, params=params, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                return None
            
            data = response.json()
            records = data.get("results", [])
            
            if not records:
                return {"department": department, "max_level": 1, "phenomena": [], "summary": ""}
            
            record = records[0]
            max_level = int(record.get("max_color_id", 1))
            phenomena = []
            
            for key, label in VIGILANCE_PHENOMENA.items():
                field = f"color_{key.lower()}"
                level = int(record.get(field, 1))
                if level >= 2:
                    phenomena.append(label)
            
            return {
                "department": department,
                "max_level": max_level,
                "phenomena": phenomena,
                "summary": f"Vigilance {max_level} en cours"
            }
        except Exception as e:
            logger.error(f"Erreur Vigilance data.gouv : {e}")
            return None

    def _fetch_all_via_datagouv(self) -> list:
        """Récupère toutes les alertes via l'API Open Data."""
        try:
            # On retire order_by qui semble poser problème sur certains environnements
            params = {
                "limit": 100
            }
            response = requests.get(DATAGOUV_VIGILANCE_URL, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            records = data.get("results", [])

            results = []
            for record in records:
                dept = record.get("dep_code")
                max_level = int(record.get("max_color_id", 1))
                if max_level >= 2:
                    phenomena = []
                    for key, label in VIGILANCE_PHENOMENA.items():
                        field = f"color_{key.lower()}"
                        level = int(record.get(field, 1))
                        if level >= 2:
                            phenomena.append(label)
                    
                    results.append({
                        "department": dept,
                        "max_level": max_level,
                        "phenomena": phenomena,
                        "summary": f"Vigilance {max_level} en cours",
                    })
            return results
        except Exception as e:
            logger.error(f"Erreur Global Vigilance : {e}")
            return []

    def format_vigilance_message(self, department: str, data: Optional[dict]) -> str:
        """Formate un message de vigilance avec indication de cache."""
        if not data: return f"⚠️ Vigilance {department}: Indisponible"
        
        level = data.get("max_level", 1)
        # Indicateur de cache
        age_str = f" (⌛ {data['cache_age']})" if data.get("is_cached") else ""
        
        if level == 1: return f"🟢 Dept {department}: RAS{age_str}"
        
        level_info = VIGILANCE_LEVELS.get(level, VIGILANCE_LEVELS[1])
        phenoms = ",".join(data.get("phenomena", []))
        return f"{level_info['emoji']} ALERTE {level_info['name']} ({department}){age_str}\nRisque: {phenoms}\nPrudence requise."[:199]

    def format_national_summary(self, alerts: list) -> str:
        """Formate un résumé national des alertes actives."""
        if not alerts:
            return "🟢 Pas d'alerte active en France.\nSource : Météo-France"

        alerts_sorted = sorted(alerts, key=lambda x: x.get("max_level", 1), reverse=True)
        lines = ["⚠️ ALERTES MÉTÉO ACTIVES :"]
        for alert in alerts_sorted[:8]:
            level = alert.get("max_level", 1)
            level_info = VIGILANCE_LEVELS.get(level, VIGILANCE_LEVELS[1])
            dept = alert.get("department", "?")
            phenomena = ", ".join(alert.get("phenomena", []))
            lines.append(f"{level_info['emoji']} Dept {dept}: {phenomena}")

        lines.append("vigilance.meteofrance.fr")
        return "\n".join(lines)
