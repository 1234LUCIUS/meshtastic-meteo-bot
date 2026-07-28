"""
Service de recherche active sur le web — Extrait les infos des sites officiels normands.
Cible la Région Normandie, les Préfectures et les grandes Mairies.
"""

import logging
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

# Liste des sites officiels normands à scanner
OFFICIAL_SITES = {
    "Région Normandie": "https://www.normandie.fr/actualites",
    "Préfet Normandie": "https://www.prefectures-regions.gouv.fr/normandie/Actualites",
    "Ville de Caen": "https://caen.fr/actualites",
    "Ville de Rouen": "https://rouen.fr/actualites",
    "Ville du Havre": "https://www.lehavre.fr/actualites",
}

REQUEST_TIMEOUT = 15

class OfficialWebSearchService:
    """
    Service qui scanne les sites officiels pour extraire les dernières nouvelles.
    """

    def get_latest_official_news(self, limit_per_site: int = 2) -> str:
        """
        Scanne les sites officiels et retourne un résumé des derniers titres.
        """
        news_summary = []
        now_str = datetime.now().strftime("%d/%m %H:%M")
        
        news_summary.append(f"🏛️ INFOS OFFICIELLES NORMANDIE [{now_str}]")

        for site_name, url in OFFICIAL_SITES.items():
            try:
                titles = self._scrape_site(url, limit_per_site)
                if titles:
                    news_summary.append(f"\n[{site_name}]")
                    for title in titles:
                        news_summary.append(f"• {title}")
            except Exception as e:
                logger.warning(f"Erreur scan {site_name} : {e}")

        if len(news_summary) <= 1:
            return "❌ Aucune information officielle récente trouvée sur le web."

        return "\n".join(news_summary)

    def _scrape_site(self, url: str, limit: int) -> List[str]:
        """Scrape sommairement les titres d'un site (basé sur les balises h2/h3)."""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            titles = []
            
            # Stratégie générique : on cherche les titres h2 ou h3 qui contiennent souvent les actus
            for tag in soup.find_all(['h2', 'h3']):
                title_text = tag.get_text().strip()
                # On filtre les titres trop courts ou génériques
                if len(title_text) > 20 and title_text not in titles:
                    titles.append(title_text)
                    if len(titles) >= limit:
                        break
            
            return titles
        except:
            return []
