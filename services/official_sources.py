"""
Service des sources officielles — Intègre Vigicrues, les flux RSS des préfectures,
des mairies et d'autres organismes gouvernementaux.

Sources intégrées :
  - Vigicrues (vigicrues.gouv.fr) : Alertes crues en temps réel
  - Géorisques (georisques.gouv.fr) : Risques naturels et technologiques
  - Flux RSS préfectures (configurable par département)
  - Service-public.fr : Informations officielles générales
"""

import logging
from datetime import datetime
from typing import Optional

import requests
import feedparser

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10

# ============================================================
# API Vigicrues
# ============================================================
VIGICRUES_API_BASE = "http://www.vigicrues.gouv.fr/services/v1.1"
VIGICRUES_GEOJSON_URL = "http://www.vigicrues.gouv.fr/services/1/InfoVigiCru.geojson"

# ============================================================
# Flux RSS officiels
# Clé : identifiant, Valeur : (nom, URL du flux RSS)
# ============================================================
OFFICIAL_RSS_FEEDS = {
    "gouvernement": (
        "Gouvernement.fr",
        "https://www.gouvernement.fr/feed/actualites.rss",
    ),
    "securite_civile": (
        "Sécurité Civile",
        "https://www.interieur.gouv.fr/rss/actualites.xml",
    ),
    "meteo_france_news": (
        "Météo-France Actualités",
        "https://meteofrance.com/feed/actualites.rss",
    ),
    "georisques": (
        "Géorisques",
        "https://www.georisques.gouv.fr/actualites.rss",
    ),
}

# Flux RSS préfectures par département (exemples — à compléter)
PREFECTURE_RSS_FEEDS = {
    "75": ("Préfecture de Paris", "https://www.prefecturedepolice.interieur.gouv.fr/rss.xml"),
    "13": ("Préfecture des Bouches-du-Rhône", "https://www.bouches-du-rhone.gouv.fr/rss.xml"),
    "69": ("Préfecture du Rhône", "https://www.rhone.gouv.fr/rss.xml"),
    "33": ("Préfecture de la Gironde", "https://www.gironde.gouv.fr/rss.xml"),
    "31": ("Préfecture de la Haute-Garonne", "https://www.haute-garonne.gouv.fr/rss.xml"),
    "06": ("Préfecture des Alpes-Maritimes", "https://www.alpes-maritimes.gouv.fr/rss.xml"),
    "59": ("Préfecture du Nord", "https://www.nord.gouv.fr/rss.xml"),
    "67": ("Préfecture du Bas-Rhin", "https://www.bas-rhin.gouv.fr/rss.xml"),
    "44": ("Préfecture de Loire-Atlantique", "https://www.loire-atlantique.gouv.fr/rss.xml"),
    "34": ("Préfecture de l'Hérault", "https://www.herault.gouv.fr/rss.xml"),
}

# URL de la carte Vigicrues
VIGICRUES_MAP_URL = "https://www.vigicrues.gouv.fr/"


class OfficialSourcesService:
    """
    Service d'agrégation des sources officielles françaises.
    """

    def get_vigicrues_national(self) -> list:
        """
        Récupère les alertes crues actives au niveau national via l'API GeoJSON Vigicrues.

        :return: Liste de dicts {id, name, river, level, level_name, department}.
        """
        try:
            response = requests.get(
                VIGICRUES_GEOJSON_URL, timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            alerts = []
            features = data.get("features", [])

            for feature in features:
                props = feature.get("properties", {})
                level = props.get("NivSituVigiCruEnt", 1)
                if level >= 2:
                    alerts.append({
                        "id": props.get("CdEntVigiCru", ""),
                        "name": props.get("LbEntVigiCru", "Tronçon inconnu"),
                        "river": props.get("LbCoursEau", ""),
                        "level": level,
                        "level_name": self._vigicrues_level_name(level),
                        "department": props.get("CdDepartement", ""),
                    })

            return sorted(alerts, key=lambda x: x["level"], reverse=True)

        except Exception as e:
            logger.error(f"Erreur API Vigicrues (GeoJSON) : {e}")
            # Fallback : API TronEntVigiCru
            return self._fetch_vigicrues_fallback()

    def _fetch_vigicrues_fallback(self) -> list:
        """Fallback via l'endpoint TronEntVigiCru de Vigicrues."""
        try:
            url = f"{VIGICRUES_API_BASE}/TronEntVigiCru.json"
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            alerts = []
            troncons = data.get("TronEntVigiCru", [])

            for troncon in troncons:
                level = troncon.get("NivSituVigiCruEnt", 1)
                if level >= 2:
                    alerts.append({
                        "id": troncon.get("CdEntVigiCru", ""),
                        "name": troncon.get("LbEntVigiCru", "Tronçon inconnu"),
                        "river": troncon.get("LbCoursEau", ""),
                        "level": level,
                        "level_name": self._vigicrues_level_name(level),
                        "department": troncon.get("CdDepartement", ""),
                    })

            return sorted(alerts, key=lambda x: x["level"], reverse=True)

        except Exception as e:
            logger.error(f"Erreur API Vigicrues (fallback) : {e}")
            return []

    def get_vigicrues_by_department(self, department_code: str) -> list:
        """
        Récupère les alertes crues pour un département spécifique.
        """
        all_alerts = self.get_vigicrues_national()
        return [a for a in all_alerts if a.get("department") == department_code]

    def format_vigicrues_message(self, alerts: list) -> str:
        """
        Formate les alertes Vigicrues en message Meshtastic.
        """
        if not alerts:
            return (
                "🟢 VIGICRUES : Pas d'alerte crue active.\n"
                f"Carte : {VIGICRUES_MAP_URL}"
            )

        lines = [f"🌊 VIGICRUES — {len(alerts)} alerte(s) active(s) :"]
        for alert in alerts[:6]:
            emoji = "🟡" if alert["level"] == 2 else ("🟠" if alert["level"] == 3 else "🔴")
            river = f" ({alert['river']})" if alert["river"] else ""
            lines.append(
                f"{emoji} Dept {alert['department']}: {alert['name']}{river} "
                f"— {alert['level_name']}"
            )

        if len(alerts) > 6:
            lines.append(f"... +{len(alerts) - 6} autre(s) tronçon(s).")

        lines.append(f"Carte : {VIGICRUES_MAP_URL}")
        return "\n".join(lines)

    def get_official_news(self, max_items: int = 3) -> list:
        """
        Récupère les dernières actualités des sources officielles via RSS.

        :param max_items: Nombre maximum d'articles à retourner.
        :return: Liste de dicts {source, title, date, url}.
        """
        news = []
        for feed_id, (source_name, feed_url) in OFFICIAL_RSS_FEEDS.items():
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:2]:
                    title = entry.get("title", "Sans titre")
                    link = entry.get("link", "")
                    published = entry.get("published", "")

                    # Filtrer les articles liés à la météo/sécurité
                    keywords = [
                        "météo", "alerte", "vigilance", "inondation", "crue",
                        "tempête", "canicule", "neige", "verglas", "vent",
                        "sécurité", "urgence", "risque", "catastrophe",
                    ]
                    title_lower = title.lower()
                    if any(kw in title_lower for kw in keywords):
                        news.append({
                            "source": source_name,
                            "title": title,
                            "date": published,
                            "url": link,
                        })

            except Exception as e:
                logger.debug(f"Erreur RSS {source_name} : {e}")

        return news[:max_items]

    def get_prefecture_news(self, department_code: str, max_items: int = 2) -> list:
        """
        Récupère les actualités de la préfecture du département.
        """
        if department_code not in PREFECTURE_RSS_FEEDS:
            return []

        source_name, feed_url = PREFECTURE_RSS_FEEDS[department_code]
        news = []

        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:max_items]:
                news.append({
                    "source": source_name,
                    "title": entry.get("title", "Sans titre"),
                    "date": entry.get("published", ""),
                    "url": entry.get("link", ""),
                })
        except Exception as e:
            logger.debug(f"Erreur RSS préfecture {department_code} : {e}")

        return news

    def format_official_summary(self, department_code: Optional[str] = None) -> str:
        """
        Formate un résumé des informations officielles.
        """
        lines = ["📢 SOURCES OFFICIELLES :"]

        # Actualités filtrées météo/sécurité
        news = self.get_official_news(max_items=3)
        if news:
            for item in news:
                lines.append(f"• [{item['source']}] {item['title']}")
        else:
            lines.append("• Pas d'actualité récente filtrée.")

        # Actualités de la préfecture si département connu
        if department_code:
            pref_news = self.get_prefecture_news(department_code, max_items=2)
            if pref_news:
                lines.append(f"--- Préfecture dept {department_code} ---")
                for item in pref_news:
                    lines.append(f"• {item['title']}")

        lines.append("---")
        lines.append("vigilance.meteofrance.fr")
        lines.append("vigicrues.gouv.fr")
        lines.append("georisques.gouv.fr")

        return "\n".join(lines)

    def get_georisques_info(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Récupère les informations de risques naturels pour une position (API Géorisques).
        """
        try:
            url = "https://www.georisques.gouv.fr/api/v1/gaspar/risques"
            params = {
                "latlon": f"{longitude},{latitude}",
                "rayon": 1000,
            }
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            risques = data.get("data", [])
            if not risques:
                return None

            risque_names = [r.get("libelle_risque_jo", "") for r in risques[:5] if r.get("libelle_risque_jo")]
            if risque_names:
                return "Risques recensés : " + ", ".join(risque_names)
            return None

        except Exception as e:
            logger.debug(f"Erreur API Géorisques : {e}")
            return None

    # -------------------------------------------------------------------------
    # Utilitaires
    # -------------------------------------------------------------------------

    @staticmethod
    def _vigicrues_level_name(level: int) -> str:
        """Retourne le nom du niveau Vigicrues."""
        levels = {
            1: "Vigilance verte",
            2: "Vigilance jaune",
            3: "Vigilance orange",
            4: "Vigilance rouge",
        }
        return levels.get(level, f"Niveau {level}")
