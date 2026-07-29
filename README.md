# 📡 Meshtastic Météo Bot (Spécial Normandie)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Météo-France](https://img.shields.io/badge/Source-M%C3%A9t%C3%A9o--France-0078D4)](https://vigilance.meteofrance.fr)
[![Vigicrues](https://img.shields.io/badge/Source-Vigicrues-1E90FF)](https://vigicrues.gouv.fr)

Un bot Python autonome et robuste, entièrement optimisé pour la **Normandie**, compatible **Windows**, **Linux** et **macOS**. Il transforme votre réseau Meshtastic en une véritable sentinelle d'informations locales et d'alertes de sécurité civile.

---

## 🌟 Fonctionnalités Clés

### 🌤️ Météo Locale Ultra-Compacte
-   **Prévisions Précises** : Basées sur le modèle AROME de Météo-France via l'API [Open-Meteo](https://open-meteo.com) (gratuite, sans clé).
-   **Météo Géolocalisée** : Météo automatique selon la position GPS du nœud Meshtastic expéditeur.
-   **Météo à la Demande** : Commande `!meteo <ville>` pour n'importe quelle ville française.
-   **Diffusion Périodique** : Bulletin météo ultra-compact diffusé automatiquement toutes les 6 heures (configurable) avec la localisation précise (ex: `📍 Caen`).

### 🚨 Alertes d'Urgence et Sécurité Civile (Spécial Normandie)
Le bot surveille en temps réel les risques pour les **5 départements normands** (Calvados, Eure, Manche, Orne, Seine-Maritime) et diffuse des alertes structurées et concises.

-   **Vigilance Météo-France** : Surveillance continue des niveaux (Orange/Rouge) pour les phénomènes météorologiques dangereux.
-   **Météo des Forêts** : Suivi du danger d'incendie par département (Météo-France).
-   **Vigicrues** : Alertes crues en temps réel pour les bassins normands.
-   **Suivi des Feux Actifs** : Détection satellite en temps réel via la **NASA (FIRMS)** pour les incendies en cours.
-   **Alertes Préfectures & SDIS** : Surveillance active des sites officiels des Préfectures et des Services Départementaux d'Incendie et de Secours (SDIS) de Normandie.
-   **Réseaux Sociaux Officiels** : Scan ciblé des comptes X (Twitter) et Facebook des autorités (Préfets, Gendarmerie, Police) pour les informations d'urgence.
-   **Format d'Alerte Strict (Qui, Quoi, Consigne, Quand, Lien)** : Les alertes sont formatées pour une compréhension immédiate et incluent les consignes de sécurité (Évacuation, Confinement, Évitez le secteur) et un lien vers la source.
-   **Reporting Horaire** : En cas d'alerte grave, un point de situation est diffusé toutes les heures.

### 📰 Actualités Locales & Événements
-   **Commande `!actu <ville>`** : Obtenez les dernières actualités et événements importants (articles de moins de 48h) des sites officiels (Mairies, Région) pour une ville spécifique (ex: `!actu Rouen`).

---

## ⚙️ Commandes Disponibles

| Commande | Description |
|---|---|
| `!meteo` | Météo pour votre position GPS actuelle |
| `!meteo <ville>` | Météo pour une ville spécifique (ex: `!meteo Lyon`) |
| `!alertes` | Vigilances Météo-France actives (département auto-détecté) |
| `!crues` | Alertes Vigicrues nationales |
| `!feux` | Météo des Forêts (danger incendie) |
| `!suivi_feux` | Suivi des feux actifs (NASA satellites) |
| `!normandie` | Scan web officiel Normandie (Préfectures, Mairies, SDIS) |
| `!actu <ville>` | Actualités et événements récents (<48h) pour une ville |
| `!officiel` | Informations des sources officielles (Vigicrues, Géorisques, Préfectures) |
| `!aide` | Affiche la liste des commandes |
| `!ping` | Vérifie que le bot est actif |

---

## 🚀 Démarrage Rapide

### 1. Prérequis
-   **Python 3.10 ou supérieur** (Recommandé)
-   Un **nœud Meshtastic** connecté en USB/Série, TCP ou BLE.
-   Connexion internet pour récupérer les données.

### 2. Installation

```bash
# Téléchargez le projet (via git clone ou en téléchargeant le ZIP depuis GitHub)
git clone https://github.com/1234LUCIUS/meshtastic-meteo-bot.git
cd meshtastic-meteo-bot

# Installez les dépendances (utilisez --user si vous avez des problèmes de droits)
pip install -r requirements.txt
```

### 3. Configuration

Créez votre fichier de configuration `.env` à partir du modèle et adaptez-le :

```bash
cp .env.example .env
# Ouvrez .env avec un éditeur de texte (Bloc-notes, VS Code) et modifiez :
```

**Paramètres clés dans `.env` :**

```ini
# Type de connexion : serial, tcp ou ble
MESHTASTIC_CONNECTION_TYPE=serial
MESHTASTIC_SERIAL_PORT=COM3 # Ou /dev/ttyUSB0 sur Linux

# Localisation par défaut (Normandie / Caen)
DEFAULT_DEPARTMENT=14
DEFAULT_LATITUDE=49.1833
DEFAULT_LONGITUDE=-0.37

# Niveau d'alerte minimum (3=Orange, 4=Rouge)
ALERT_TRIGGER_LEVEL=3

# Surveillance Normandie (14, 27, 50, 61, 76)
ENABLE_NORMANDIE_ALERTS=True

# Clé API NASA FIRMS (optionnelle pour un suivi des feux plus précis)
NASA_API_KEY=VOTRE_CLE_NASA
```

### 4. Lancer le bot

```powershell
python main.py
```

---

## 🛠️ Dépannage & Tests

-   **Problèmes d'installation (`pip`)** : Si vous rencontrez des erreurs `Accès refusé`, utilisez `pip install --user -r requirements.txt`.
-   **Problèmes de connexion au module** : Vérifiez le port COM dans le Gestionnaire de périphériques et mettez à jour `MESHTASTIC_SERIAL_PORT` dans `.env`.
-   **Tester sans matériel** : Utilisez `python main.py --simulate` ou les commandes de test spécifiques (ex: `python main.py --test-meteo --ville Caen`).

---

## 🗺️ Sources de Données Intégrées

| Source | Type | URL | Clé API |
|---|---|---|---|
| Open-Meteo (AROME) | Prévisions météo | [open-meteo.com](https://open-meteo.com) | Non requise |
| NASA FIRMS | Suivi feux actifs | [firms.modaps.eosdis.nasa.gov](https://firms.modaps.eosdis.nasa.gov) | Requise (gratuite) |
| Météo des Forêts | Danger incendie | [meteofrance.com/meteo-des-forets](https://meteofrance.com/meteo-des-forets) | Non requise |
| Vigicrues | Alertes crues | [vigicrues.gouv.fr](https://vigicrues.gouv.fr) | Non requise |
| Géorisques | Risques naturels | [georisques.gouv.fr](https://georisques.gouv.fr) | Non requise |
| Nominatim/OSM | Géocodage | [nominatim.openstreetmap.org](https://nominatim.openstreetmap.org) | Non requise |
| Préfectures Normandie | Actualités & Alertes | [prefectures-regions.gouv.fr/normandie](https://www.prefectures-regions.gouv.fr/normandie) | Non requise |
| SDIS Normandie | Alertes Sapeurs-Pompiers | [sdis14.fr](https://www.sdis14.fr), [sdis27.fr](https://www.sdis27.fr), etc. | Non requise |
| Mairies Normandie | Actualités locales | [caen.fr](https://caen.fr), [rouen.fr](https://rouen.fr), [lehavre.fr](https://www.lehavre.fr) | Non requise |
| Réseaux Sociaux | Alertes officielles (X, Facebook) | Comptes officiels | Non requise (via scraping public) |

---

## 🏗️ Architecture du Projet

```
meshtastic-meteo-bot/
├── main.py                    # Point d'entrée principal
├── requirements.txt           # Dépendances Python
├── .env.example               # Modèle de configuration
├── Dockerfile                 # Image Docker
├── docker-compose.yml         # Orchestration Docker
│
├── bot/
│   ├── config.py              # Configuration centrale (chargement .env)
│   ├── meshtastic_client.py   # Client Meshtastic (Serial/TCP/BLE)
│   ├── commands.py            # Parseur et handlers de commandes
│   ├── controller.py          # Contrôleur principal (orchestration)
│   └── scheduler.py           # Planificateur (alertes, diffusion périodique)
│
├── services/
│   ├── meteo.py               # API Open-Meteo (prévisions Météo-France) & SYNOP
│   ├── vigilance.py           # Alertes Vigilance Météo-France (via Open Data)
│   ├── geocoding.py           # Géocodage GPS ↔ Ville (Nominatim/OSM)
│   ├── official_sources.py    # Vigicrues, Géorisques
│   ├── meteo_forets.py        # Météo des Forêts
│   ├── active_fires.py        # Suivi des feux actifs (NASA FIRMS)
│   └── official_web_search.py # Recherche active SDIS, Préfectures, Mairies, RS
│
└── tests/
    └── test_services.py       # Tests unitaires
```

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Merci de :
1.  Forker le dépôt.
2.  Créer une branche (`git checkout -b feature/ma-fonctionnalite`).
3.  Commiter vos changements (`git commit -m 'Ajout de ma fonctionnalité'`).
4.  Pousser la branche (`git push origin feature/ma-fonctionnalite`).
5.  Ouvrir une Pull Request.

---

## 📄 Licence

Ce projet est sous licence [MIT](LICENSE).

---

## 🔗 Ressources Utiles

-   [Documentation Meshtastic Python](https://python.meshtastic.org/)
-   [Vigilance Météo-France](https://vigilance.meteofrance.fr)
-   [API Open-Meteo Météo-France](https://open-meteo.com/en/docs/meteofrance-api)
-   [Vigicrues API](https://www.vigicrues.gouv.fr/services/v1.1)
-   [Portail API Météo-France](https://portail-api.meteofrance.fr)
-   [Géorisques](https://www.georisques.gouv.fr)
