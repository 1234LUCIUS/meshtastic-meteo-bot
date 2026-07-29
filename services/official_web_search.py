"""
Service de recherche active sur le web — Extrait les infos des sites officiels et journaux locaux normands.
Cible la Région Normandie, les Préfectures, les Mairies, les SDIS et la presse locale.
"""

import logging
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

# Liste des sites officiels normands à scanner
OFFICIAL_SITES = {
    "Région Normandie": "https://www.normandie.fr/actualites",
    "Préfet Normandie": "https://www.prefectures-regions.gouv.fr/normandie/Actualites",
    "Ville de Caen": "https://caen.fr/actualites",
    "Ville de Rouen": "https://rouen.fr/actualites",
    "Ville du Havre": "https://www.lehavre.fr/actualites",
}

# Sources SDIS Normandie
SDIS_SOURCES = {
    "SDIS 14 (Calvados)": "https://www.sdis14.fr/actualites",
    "SDIS 27 (Eure)": "https://www.sdis27.fr/actualites",
    "SDIS 50 (Manche)": "https://www.sdis50.fr/actualites",
    "SDIS 61 (Orne)": "https://www.sdis61.fr/actualites",
    "SDIS 76 (Seine-Maritime)": "https://www.sdis76.fr/actualites"
}

# Sources de presse locale normande (Actu.fr, Paris-Normandie, Ouest-France, La Manche Libre)
PRESS_SOURCES = {
    "Actu Normandie": "https://actu.fr/normandie/",
    "Paris Normandie": "https://www.paris-normandie.fr/fil-info",
    "Ouest-France Normandie": "https://www.ouest-france.fr/normandie/",
    "La Manche Libre": "https://www.lamanchelibre.fr/actualites-actualites.html"
}

REQUEST_TIMEOUT = 15

class OfficialWebSearchService:
    """
    Service qui scanne les sites officiels et la presse locale pour extraire les dernières nouvelles.
    """

    def get_latest_official_news(self, limit_per_site: int = 2) -> str:
        """
        Scanne les sites officiels et retourne un résumé des derniers titres.
        """
        news_summary = []
        now_str = datetime.now().strftime("%d/%m %H:%M")
        
        news_summary.append(f"🏛️ INFOS NORMANDIE [{now_str}]")

        # 1. Sites Institutionnels (Mairies, Région)
        for site_name, url in list(OFFICIAL_SITES.items())[:3]:
            try:
                titles = self._scrape_site(url, 1)
                if titles:
                    news_summary.append(f"\n[{site_name}]")
                    for title in titles:
                        news_summary.append(f"• {title[:80]}")
            except: pass

        # 2. Presse Locale (Nouveau)
        news_summary.append("\n📰 [PRESSE LOCALE]")
        for press_name, url in list(PRESS_SOURCES.items())[:2]:
            try:
                titles = self._scrape_site(url, 1)
                if titles:
                    news_summary.append(f"• {press_name}: {titles[0][:80]}")
            except: pass

        # 3. SDIS (Pompiers)
        news_summary.append("\n🚒 [SDIS / POMPIERS]")
        for sdis_name, url in SDIS_SOURCES.items():
            try:
                titles = self._scrape_site(url, 1)
                if titles:
                    news_summary.append(f"• {sdis_name.split(' ')[1]}: {titles[0][:80]}")
            except: pass

        if len(news_summary) <= 4:
            return "❌ Aucune information récente trouvée."

        full_text = "\n".join(news_summary)
        if len(full_text) > 400:
            return full_text[:397] + "..."
        return full_text

    def _scrape_site(self, url: str, limit: int, filter_keywords: Optional[List[str]] = None) -> List[str]:
        """Scrape les titres d'un site avec filtrage optionnel."""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200: return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            titles = []
            
            # Recherche des titres h1, h2 ou h3 ou classes spécifiques
            for tag in soup.find_all(['h1', 'h2', 'h3', 'a']):
                title_text = tag.get_text().strip()
                
                # Critères de qualité pour un titre
                if 25 < len(title_text) < 150:
                    # Si des mots-clés sont fournis, on filtre
                    if filter_keywords:
                        if not any(kw.lower() in title_text.lower() for kw in filter_keywords):
                            continue
                    
                    # Nettoyage
                    clean_title = re.sub(r'\s+', ' ', title_text).strip()
                    if clean_title not in titles:
                        titles.append(clean_title)
                    
                    if len(titles) >= limit:
                        break
            
            return titles
        except:
            return []

    def check_for_urgent_alerts(self) -> List[str]:
        """
        Scanne les sources pour trouver uniquement les alertes d'urgence grave.
        """
        urgent_alerts = []
        grave_keywords = ["ALERTE ROUGE", "DANGER IMMÉDIAT", "FR-ALERT", "INCENDIE MAJEUR", "ACCIDENT GRAVE", "ÉVACUATION", "URGENCE ABSOLUE", "COUVRE-FEU"]
        
        # On scanne officiels + presse pour les alertes
        all_sources = {**OFFICIAL_SITES, **SDIS_SOURCES, **PRESS_SOURCES}
        
        for source_name, url in all_sources.items():
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
                if response.status_code != 200: continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                for tag in soup.find_all(['h1', 'h2', 'h3']):
                    title = tag.get_text().strip().upper()
                    if any(kw in title for kw in grave_keywords):
                        qui = source_name.replace("SDIS", "Pompiers")
                        quoi = title[:60]
                        quand = datetime.now().strftime("%H:%M")
                        
                        instructions = "Prudence"
                        page_text = soup.get_text().upper()
                        if any(k in page_text for k in ["ÉVACUATION", "EVACUER"]):
                            instructions = "ÉVACUATION IMMÉDIATE"
                        elif any(k in page_text for k in ["CONFINEMENT", "RESTER CHEZ SOI"]):
                            instructions = "CONFINEMENT / À L'ABRI"
                        elif any(k in page_text for k in ["ÉVITER LE SECTEUR", "PÉRIMÈTRE"]):
                            instructions = "ÉVITEZ LE SECTEUR"
                        
                        msg = (
                            f"🚨 ALERTE\n"
                            f"👤 {qui}\n"
                            f"📝 {quoi}\n"
                            f"🛡️ {instructions}\n"
                            f"⏰ {quand}\n"
                            f"🔗 {url[:30]}..."
                        )
                        urgent_alerts.append(msg[:199])
                        break
            except: continue
            
        return urgent_alerts

    def _compact_title(self, title: str) -> str:
        """Raccourcit un titre pour ne garder que l'essentiel."""
        # Supprimer les guillemets et articles de début
        t = re.sub(r'^["«\s]+', '', title)
        t = re.sub(r'["»\s]+$', '', t)
        
        # Supprimer les mots de liaison trop longs ou inutiles au début
        t = re.sub(r'^(L\'|Le |La |Les |Un |Une |Des |Cette |Ce |Ces )', '', t, flags=re.IGNORECASE)
        
        # Remplacer certains mots par des abréviations
        replacements = {
            "Gendarmerie": "Gend.",
            "Sapeurs-Pompiers": "Pompiers",
            "Département": "Dept",
            "Président": "Prés.",
            "Gouvernement": "Gouv.",
            "Information": "Info",
            "Inondation": "Inond.",
            "Accident": "Accid.",
            "Circulation": "Circu.",
            "Manifestation": "Manif.",
            "Association": "Asso.",
            "Établissement": "Étab.",
            "Région": "Rég.",
            "Commune": "Com.",
            "Mairie": "Mair.",
            "Préfecture": "Préf.",
        }
        for word, sub in replacements.items():
            t = re.sub(rf'\b{word}\b', sub, t, flags=re.IGNORECASE)
            
        return t

    def get_city_news(self, city: str) -> str:
        """
        Recherche les actualités de moins de 48h pour une ville spécifique.
        Formatage ultra-compact pour Meshtastic.
        """
        try:
            city_news = []
            city_clean = city.strip().capitalize()
            
            # Sources presse
            for press_name, url in PRESS_SOURCES.items():
                titles = self._scrape_site(url, 2, filter_keywords=[city])
                for t in titles:
                    compact = self._compact_title(t)
                    # On garde un préfixe court pour la source
                    src = "Actu" if "Actu" in press_name else press_name[:4]
                    city_news.append(f"•[{src}] {compact}")

            # Sources officielles
            for site_name, url in OFFICIAL_SITES.items():
                if city.lower() in site_name.lower() or "normandie" in site_name.lower():
                    titles = self._scrape_site(url, 2, filter_keywords=[city])
                    for t in titles:
                        compact = self._compact_title(t)
                        city_news.append(f"•[Off] {compact}")

            if not city_news:
                return f"📍 Pas d'actu récente pour {city_clean}."

            # Construction du message final (strictement optimisé)
            res = f"📰 {city_clean.upper()}:\n"
            
            # On essaie d'ajouter le plus de news possible sans dépasser 200 chars
            for n in city_news:
                # Si l'ajout de la news dépasse la limite, on s'arrête
                if len(res) + len(n) + 1 > 195:
                    # On tronque la dernière si elle est vraiment importante ou on arrête
                    break
                res += f"{n}\n"
            
            return res.strip()
        except Exception as e:
            logger.error(f"Erreur actu {city}: {e}")
            return f"❌ Erreur actu {city}."
