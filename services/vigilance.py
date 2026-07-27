"""
Service de vigilance météo — Récupère les alertes Météo-France.

Utilise deux sources complémentaires :
  1. La bibliothèque `meteofrance-api` (API mobile non publique, sans clé).
  2. L'API publique data.gouv.fr en fallback.
"""

import logging
from typing import Optional

import requests

from bot.config import VIGILANCE_LEVELS, VIGILANCE_PHENOMENA, METEOFRANCE_API_KEY

logger = logging.getLogger(__name__)

# URL de l'API publique Météo-France (nécessite un compte gratuit sur portail-api.meteofrance.fr)
MF_VIGILANCE_URL = "https://portail-api.meteofrance.fr/public/DPVigilance/v1/cartevigilance/encours"

# Fallback : API data.gouv.fr (open data, sans clé)
DATAGOUV_VIGILANCE_URL = (
    "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/"
    "weatherref-france-vigilance-meteo-national/records"
)

REQUEST_TIMEOUT = 10


class VigilanceService:
    """
    Service d'accès aux alertes de vigilance météorologique de Météo-France.
    """

    def get_vigilance_by_department(self, department: str) -> Optional[dict]:
        """
        Récupère le niveau de vigilance pour un département donné.

        :param department: Code du département (ex: "75", "13", "2A").
        :return: Dictionnaire avec le niveau et les phénomènes, ou None.
        """
        # Tentative avec la bibliothèque meteofrance-api
        result = self._fetch_via_meteofrance_lib(department)
        if result:
            return result

        # Fallback : API publique data.gouv.fr
        return self._fetch_via_datagouv(department)

    def get_all_active_alerts(self) -> list:
        """
        Récupère toutes les alertes actives au niveau national.
        Retourne une liste de dicts {department, max_level, phenomena, summary}.
        """
        results = []

        # Tentative avec la bibliothèque meteofrance-api
        try:
            from meteofrance_api import MeteoFranceClient
            client = MeteoFranceClient()
            
            # Dans la v1.2.0, get_warning_full_france n'existe pas
            # On utilise get_warning_current_phenomenons avec depth=1 pour tous les depts
            warnings = client.get_warning_current_phenomenons(domain="france", depth=1)

            # Note: Dans la v1.2.0, l'objet retourné contient les phénomènes par domaine
            # La structure est simplifiée par rapport à la version mobile full
            if hasattr(warnings, "phenomenons_max_colors"):
                # Si on n'a que le national, on bascule sur le fallback pour avoir le détail par département
                # car depth=1 ne semble pas toujours retourner une liste de domaines dans cette version
                logger.info("Données nationales reçues, passage au fallback pour les détails départementaux.")
            
        except ImportError:
            logger.warning("meteofrance-api non disponible, utilisation du fallback.")
        except Exception as e:
            logger.error(f"Erreur meteofrance-api (alertes nationales) : {e}")

        # Fallback : On utilise data.gouv pour avoir le détail de tous les départements sans clé API
        return self._fetch_all_via_datagouv()

    def _fetch_all_via_datagouv(self) -> list:
        """Récupère toutes les alertes via l'API Open Data (sans limite de département)."""
        try:
            # On récupère tous les enregistrements récents (environ 101 départements)
            params = {
                "limit": 101,
                "order_by": "update_time DESC"
            }
            response = requests.get(
                DATAGOUV_VIGILANCE_URL, params=params, timeout=REQUEST_TIMEOUT
            )
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
                        "summary": self._build_summary(dept, max_level, phenomena),
                    })
            return results
        except Exception as e:
            logger.error(f"Erreur fallback global data.gouv : {e}")
            return []

    def format_vigilance_message(self, department: str, data: Optional[dict]) -> str:
        """
        Formate un message de vigilance pour un département.
        """
        if not data:
            return (
                f"Vigilance Météo-France pour le dept {department} :\n"
                f"Données indisponibles. Consultez vigilance.meteofrance.fr"
            )

        level = data.get("max_level", 1)
        level_info = VIGILANCE_LEVELS.get(level, VIGILANCE_LEVELS[1])
        phenomena = data.get("phenomena", [])

        if level == 1:
            return (
                f"🟢 VIGILANCE VERTE — Dept {department}\n"
                f"Pas de vigilance particulière.\n"
                f"vigilance.meteofrance.fr"
            )

        phenomena_str = "\n".join(f"  • {p}" for p in phenomena) if phenomena else "  • Non précisé"

        return (
            f"{level_info['emoji']} VIGILANCE {level_info['name']} — Dept {department}\n"
            f"{level_info['label']}\n"
            f"Phénomènes :\n{phenomena_str}\n"
            f"Détails : vigilance.meteofrance.fr/fr/{department}"
        )

    def format_national_summary(self, alerts: list) -> str:
        """
        Formate un résumé national des alertes actives.
        """
        if not alerts:
            return (
                "🟢 Pas d'alerte active sur le territoire national.\n"
                "Source : vigilance.meteofrance.fr"
            )

        # Trier par niveau décroissant
        alerts_sorted = sorted(alerts, key=lambda x: x.get("max_level", 1), reverse=True)

        lines = ["⚠️ ALERTES MÉTÉO ACTIVES :"]
        for alert in alerts_sorted[:8]:  # Limiter pour la taille du message
            level = alert.get("max_level", 1)
            level_info = VIGILANCE_LEVELS.get(level, VIGILANCE_LEVELS[1])
            dept = alert.get("department", "?")
            phenomena = ", ".join(alert.get("phenomena", []))
            lines.append(f"{level_info['emoji']} Dept {dept}: {phenomena}")

        if len(alerts_sorted) > 8:
            lines.append(f"... et {len(alerts_sorted) - 8} autre(s) département(s).")

        lines.append("vigilance.meteofrance.fr")
        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # Sources de données
    # -------------------------------------------------------------------------

    def _fetch_via_meteofrance_lib(self, department: str) -> Optional[dict]:
        """Utilise la bibliothèque meteofrance-api."""
        try:
            from meteofrance_api import MeteoFranceClient
            client = MeteoFranceClient()
            
            # Tentative de détection de la fonction disponible selon la version
            if hasattr(client, "get_warning_current_phenomenons"):
                warning = client.get_warning_current_phenomenons(department)
            elif hasattr(client, "get_warning"):
                warning = client.get_warning(department)
            else:
                return None

            if not warning:
                return None

            max_level = 1
            phenomena = []

            # Gestion des deux formats possibles de l'API
            phenom_data = None
            if hasattr(warning, "phenomenons_max_colors"):
                phenom_data = warning.phenomenons_max_colors
            elif hasattr(warning, "raw_data") and isinstance(warning.raw_data, dict):
                phenom_data = warning.raw_data.get("phenomenons_max_colors", {})

            if phenom_data:
                if isinstance(phenom_data, dict):
                    items = phenom_data.items()
                elif isinstance(phenom_data, list):
                    items = [(p.get("phenomenon_id", ""), p.get("phenomenon_max_color_id", 1))
                             for p in phenom_data]
                else:
                    items = []

                for phenom_id, level in items:
                    if not isinstance(level, int):
                        try:
                            level = int(level)
                        except (TypeError, ValueError):
                            continue
                    if level > max_level:
                        max_level = level
                    if level >= 2:
                        phenom_name = VIGILANCE_PHENOMENA.get(str(phenom_id), str(phenom_id))
                        if phenom_name not in phenomena:
                            phenomena.append(phenom_name)

            return {
                "department": department,
                "max_level": max_level,
                "phenomena": phenomena,
                "summary": self._build_summary(department, max_level, phenomena),
            }

        except ImportError:
            return None
        except Exception as e:
            logger.error(f"Erreur meteofrance-api pour dept {department} : {e}")
            return None

    def _fetch_via_datagouv(self, department: str) -> Optional[dict]:
        """Fallback via l'API open data opendatasoft."""
        try:
            # Correction de la syntaxe de filtrage pour opendatasoft v2.1
            params = {
                "where": f'dep_code = "{department}"',
                "limit": 1,
                "order_by": "update_time DESC"
            }
            response = requests.get(
                DATAGOUV_VIGILANCE_URL, params=params, timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur API data.gouv ({response.status_code}) : {response.text}")
                return None
                
            data = response.json()
            records = data.get("results", [])

            if not records:
                return {"department": department, "max_level": 1, "phenomena": [], "summary": ""}

            record = records[0]
            max_level = int(record.get("max_color_id", 1))
            phenomena = []

            # Extraire les phénomènes depuis les champs disponibles
            for key, label in VIGILANCE_PHENOMENA.items():
                field = f"color_{key.lower()}"
                level = int(record.get(field, 1))
                if level >= 2:
                    phenomena.append(label)

            return {
                "department": department,
                "max_level": max_level,
                "phenomena": phenomena,
                "summary": self._build_summary(department, max_level, phenomena),
            }

        except Exception as e:
            logger.error(f"Erreur fallback data.gouv pour dept {department} : {e}")
            return None

    def _fetch_national_via_portail(self) -> list:
        """Fallback via l'API portail Météo-France (nécessite une clé API)."""
        if not METEOFRANCE_API_KEY:
            logger.warning(
                "Pas de clé API Météo-France configurée. "
                "Inscrivez-vous sur portail-api.meteofrance.fr pour accéder aux alertes."
            )
            return []

        try:
            headers = {
                "apikey": METEOFRANCE_API_KEY,
                "Accept": "application/json",
            }
            response = requests.get(
                MF_VIGILANCE_URL, headers=headers, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for dept_data in data.get("product", {}).get("periods", []):
                for timelap in dept_data.get("timelaps", []):
                    dept = str(timelap.get("domain_id", ""))
                    if not dept or len(dept) > 3:
                        continue

                    max_level = 1
                    phenomena = []
                    for item in timelap.get("timelaps_items", []):
                        level = item.get("color_id", 1)
                        if level > max_level:
                            max_level = level
                        if level >= 2:
                            phenom_name = VIGILANCE_PHENOMENA.get(
                                item.get("phenomenon_id", ""), "Inconnu"
                            )
                            phenomena.append(phenom_name)

                    if max_level >= 2:
                        results.append({
                            "department": dept,
                            "max_level": max_level,
                            "phenomena": phenomena,
                            "summary": self._build_summary(dept, max_level, phenomena),
                        })

            return results

        except Exception as e:
            logger.error(f"Erreur API portail Météo-France : {e}")
            return []

    @staticmethod
    def _build_summary(department: str, level: int, phenomena: list) -> str:
        """Construit un résumé textuel de l'alerte."""
        level_info = VIGILANCE_LEVELS.get(level, VIGILANCE_LEVELS[1])
        if not phenomena:
            return f"Vigilance {level_info['name']} pour le département {department}."
        phenomena_str = ", ".join(phenomena)
        return (
            f"Vigilance {level_info['name']} pour le département {department} : "
            f"{phenomena_str}."
        )
