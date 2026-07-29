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

    def _scrape_site_with_links(self, url: str, limit: int, filter_keywords: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """Scrape les titres et les liens d'un site avec filtrage optionnel."""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200: return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = []
            
            # Mots-clés d'importance (priorité haute)
            priority_keywords = ["accident", "incendie", "feu", "fermeture", "alerte", "travaux", "danger", "évacuation", "coupure", "météo", "vigilance", "bloqué", "mort", "décès"]
            
            # On cherche les liens qui contiennent du texte (souvent les titres sont dans des <a> ou englobent des hx)
            for tag in soup.find_all('a'):
                title_text = tag.get_text().strip()
                link = tag.get('href', '')
                
                if 25 < len(title_text) < 150 and link:
                    # Normalisation du lien
                    if link.startswith('/'):
                        from urllib.parse import urljoin
                        link = urljoin(url, link)
                    
                    # Filtrage par ville (si spécifié)
                    if filter_keywords:
                        if not any(kw.lower() in title_text.lower() for kw in filter_keywords):
                            continue
                    
                    # Calcul de la priorité
                    priority = 1
                    if any(kw in title_text.lower() for kw in priority_keywords):
                        priority = 10 # Priorité haute pour la sécurité/travaux
                    
                    clean_title = re.sub(r'\s+', ' ', title_text).strip()
                    
                    # Éviter les doublons
                    if not any(a['title'] == clean_title for a in articles):
                        articles.append({
                            "title": clean_title,
                            "link": link,
                            "priority": priority
                        })
            
            # Trier par priorité (décroissant)
            articles.sort(key=lambda x: x['priority'], reverse=True)
            return articles[:limit]
        except:
            return []

    def _scrape_site(self, url: str, limit: int, filter_keywords: Optional[List[str]] = None) -> List[str]:
        """Ancienne méthode pour compatibilité, appelle la nouvelle."""
        results = self._scrape_site_with_links(url, limit, filter_keywords)
        return [r['title'] for r in results]

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
        Sélectionne les plus importantes et inclut les liens.
        """
        try:
            all_articles = []
            city_clean = city.strip().capitalize()
            
            # 1. Sources presse
            for press_name, url in PRESS_SOURCES.items():
                articles = self._scrape_site_with_links(url, 3, filter_keywords=[city])
                for a in articles:
                    a['source'] = "Actu" if "Actu" in press_name else press_name[:4]
                    all_articles.append(a)

            # 2. Sources officielles
            for site_name, url in OFFICIAL_SITES.items():
                if city.lower() in site_name.lower() or "normandie" in site_name.lower():
                    articles = self._scrape_site_with_links(url, 2, filter_keywords=[city])
                    for a in articles:
                        a['source'] = "Off"
                        all_articles.append(a)

            if not all_articles:
                return f"📍 Pas d'actu pour {city_clean}."

            # Trier toutes les sources confondues par priorité
            all_articles.sort(key=lambda x: x['priority'], reverse=True)

            # Construction du message final
            res = f"📰 {city_clean.upper()}:\n"
            
            for a in all_articles:
                compact_t = self._compact_title(a['title'])
                # Lien court (on garde juste la fin ou on tronque intelligemment)
                # Note: Sur Meshtastic, les liens longs sont pénibles, mais nécessaires.
                # On essaie de garder le lien le plus court possible.
                link = a['link']
                if len(link) > 40:
                    # On essaie de simplifier le lien si c'est un lien connu
                    if "actu.fr" in link:
                        # Garder juste l'ID à la fin si possible
                        match = re.search(r'_(\d+)\.html', link)
                        if match:
                            link = f"actu.fr/i/{match.group(1)}"
                
                line = f"•[{a['source']}] {compact_t}\n🔗 {link}"
                
                # Vérifier la limite de 200 caractères
                if len(res) + len(line) + 1 > 200:
                    if len(res) > 20: # Si on a déjà au moins une news
                        break
                    else:
                        # Si même la première news est trop longue, on la tronque violemment
                        line = line[:195] + "..."
                
                res += line + "\n"
            
            return res.strip()
        except Exception as e:
            logger.error(f"Erreur actu {city}: {e}")
            return f"❌ Erreur actu {city}."
