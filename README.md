# 📡 Meshtastic Météo Bot (Spécial Normandie)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Météo-France](https://img.shields.io/badge/Source-M%C3%A9t%C3%A9o--France-0078D4)](https://vigilance.meteofrance.fr)
[![Vigicrues](https://img.shields.io/badge/Source-Vigicrues-1E90FF)](https://vigicrues.gouv.fr)

Un bot Python autonome optimisé pour la **Normandie**, compatible **Windows**, **Linux** et **macOS**. Il diffuse la météo régionale, surveille les **5 départements normands** pour les alertes urgentes (météo, feux, crues) et intègre les sources officielles locales (Préfectures de Caen, Rouen, Évreux, Alençon et Saint-Lô).

---

## Fonctionnalités

### Météo locale
- Prévisions basées sur le **modèle AROME de Météo-France** via l'API [Open-Meteo](https://open-meteo.com) (gratuite, sans clé).
- Météo automatique selon la **position GPS** du nœud Meshtastic expéditeur.
- Météo à la demande pour **n'importe quelle ville française** via la commande `!meteo <ville>`.
- Diffusion périodique configurable (toutes les N heures).

### Alertes urgentes et Surveillance Régionale
- **Vigilance Météo-France** : Surveillance continue (Vert/Jaune/Orange/Rouge).
- **Spécial Normandie** : Surveillance automatique et prioritaire des 5 départements normands (14, 27, 50, 61, 76).
- **Multi-Risques** : Alertes automatiques pour les **incendies** (Météo des Forêts) et **catastrophes naturelles**.
- **Reporting horaire** : Diffusion automatique d'un point de situation tant qu'une alerte grave est active.
- **Priorité** : Notification immédiate sur le canal mesh pour tout danger élevé.

### Sources officielles
- **Suivi des Feux Actifs** : Détection satellite en temps réel via la **NASA (FIRMS)**.
- **Météo des Forêts** ([meteofrance.com/meteo-des-forets](https://meteofrance.com/meteo-des-forets)) : Niveau de danger d'incendie par département.
- **Vigicrues** ([vigicrues.gouv.fr](https://vigicrues.gouv.fr)) : Alertes crues en temps réel.
- **Géorisques** ([georisques.gouv.fr](https://georisques.gouv.fr)) : Risques naturels et technologiques.
- **Scan Web Normandie** : Recherche active sur les sites de la Région, des Préfectures et des Mairies (Caen, Rouen, Le Havre).
- **Flux RSS préfectures** : Actualités filtrées météo/sécurité par département.
- **Gouvernement.fr** et **Sécurité Civile** : Actualités officielles.

---

## Commandes disponibles

| Commande | Description |
|---|---|
| `!meteo` | Météo pour votre position GPS actuelle |
| `!meteo <ville>` | Météo pour une ville spécifique (ex: `!meteo Lyon`) |
| `!alertes` | Vigilances Météo-France actives (département auto-détecté) |
| `!crues` | Alertes Vigicrues nationales |
| `!feux` | Météo des Forêts (danger incendie) |
| `!suivi_feux` | Suivi des feux actifs (NASA satellites) |
| `!normandie` | Scan en temps réel des sites officiels normands (Région, Préfectures, Mairies) |
| `!officiel` | Informations des sources officielles |
| `!aide` | Affiche la liste des commandes |
| `!ping` | Vérifie que le bot est actif |

---

## Prérequis

- **Python 3.10 ou supérieur** (Recommandé)
  - *Note : Le bot est compatible avec Python 3.9 via la version 2.3.14 de l'API Meshtastic.*
- Un **nœud Meshtastic** connecté en USB/Série, TCP ou BLE
- Connexion internet pour récupérer les données météo

---

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-utilisateur/meshtastic-meteo-bot.git
cd meshtastic-meteo-bot
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configurer le bot

```bash
cp .env.example .env
nano .env  # Adapter les paramètres à votre configuration
```

Paramètres clés dans `.env` :

```ini
# Type de connexion : serial, tcp ou ble
MESHTASTIC_CONNECTION_TYPE=serial
MESHTASTIC_SERIAL_PORT=/dev/ttyUSB0

# Localisation par défaut (Normandie / Caen)
DEFAULT_DEPARTMENT=14
DEFAULT_LATITUDE=49.1833
DEFAULT_LONGITUDE=-0.37

# Niveau d'alerte minimum (3=Orange, 4=Rouge)
ALERT_TRIGGER_LEVEL=3

# Surveillance Normandie (14, 27, 50, 61, 76)
ENABLE_NORMANDIE_ALERTS=True
```

### 4. Lancer le bot

Sur **Windows** :
```powershell
python main.py
```

Sur **Linux/macOS** :
```bash
python3 main.py
```

---

## Utilisation avec un module physique

Le bot est conçu pour fonctionner avec un module Meshtastic physique (Heltec, T-Beam, etc.).

### Connexion USB (Série)
1. Branchez votre module en USB.
2. Identifiez le port (ex: `COM3` sur Windows, `/dev/ttyUSB0` sur Linux).
3. Dans le fichier `.env`, réglez `MESHTASTIC_CONNECTION_TYPE=serial` et `MESHTASTIC_SERIAL_PORT=COM3`.

### Connexion WiFi (TCP)
1. Activez le WiFi sur votre module Meshtastic.
2. Identifiez son adresse IP sur votre réseau local.
3. Dans le fichier `.env`, réglez `MESHTASTIC_CONNECTION_TYPE=tcp` et `MESHTASTIC_TCP_HOST=192.168.1.x`.

---

## Déploiement avec Docker

### Connexion TCP (nœud Meshtastic sur le réseau local)

```bash
# Éditer docker-compose.yml pour configurer l'IP du nœud
docker-compose up -d meteo-bot
```

### Connexion série (Raspberry Pi / Linux)

Décommenter le service `meteo-bot-serial` dans `docker-compose.yml` :

```bash
docker-compose up -d meteo-bot-serial
```

---

## Mode test (sans matériel)

Tester les services sans nœud Meshtastic physique :

```bash
# Test météo pour Paris
python main.py --test-meteo --ville Paris

# Test des alertes Météo-France
python main.py --test-alertes

# Test Vigicrues
python main.py --test-crues

# Test des sources officielles
python main.py --test-officiel

# Mode simulation complet
python main.py --simulate
```

---

## Architecture du projet

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
│   └── scheduler.py          # Planificateur (alertes, diffusion périodique)
│
├── services/
│   ├── meteo.py               # API Open-Meteo (prévisions Météo-France)
│   ├── vigilance.py           # Alertes Vigilance Météo-France
│   ├── geocoding.py           # Géocodage GPS ↔ Ville (Nominatim/OSM)
│   └── official_sources.py   # Vigicrues, Géorisques, RSS préfectures
│
└── tests/
    └── test_services.py       # Tests unitaires
```

---

## Sources de données

| Source | Type | URL | Clé API |
|---|---|---|---|
| Open-Meteo (AROME) | Prévisions météo | [open-meteo.com](https://open-meteo.com) | Non requise |
| Météo-France API | Vigilance météo | [portail-api.meteofrance.fr](https://portail-api.meteofrance.fr) | Optionnelle (gratuite) |
| NASA FIRMS | Suivi feux actifs | [firms.modaps.eosdis.nasa.gov](https://firms.modaps.eosdis.nasa.gov) | Requise (gratuite) |
| Météo des Forêts | Danger incendie | [meteofrance.com/meteo-des-forets](https://meteofrance.com/meteo-des-forets) | Non requise |
| Vigicrues | Alertes crues | [vigicrues.gouv.fr](https://vigicrues.gouv.fr) | Non requise |
| Géorisques | Risques naturels | [georisques.gouv.fr](https://georisques.gouv.fr) | Non requise |
| Nominatim/OSM | Géocodage | [nominatim.openstreetmap.org](https://nominatim.openstreetmap.org) | Non requise |
| Préfectures | Flux RSS | Voir `official_sources.py` | Non requise |

### Clé API Météo-France (optionnelle)

Pour accéder à l'API officielle Météo-France (meilleure fiabilité) :
1. Créer un compte gratuit sur [portail-api.meteofrance.fr](https://portail-api.meteofrance.fr)
2. Souscrire à l'API **DPVigilance**
3. Renseigner la clé dans `.env` : `METEOFRANCE_API_KEY=votre_clé`

Sans clé, le bot utilise la bibliothèque `meteofrance-api` (API mobile non publique) et l'open data comme fallback.

---

## Exemple de messages diffusés

### Météo de routine
```
📡 MÉTÉO [14:30] Paris —
Principalement dégagé, 26°C, Vent 12 km/h | Auj: 18°/28°C
```

### Alerte urgente
```
🚨 ALERTE MÉTÉO — VIGILANCE ORANGE
Dept: 13
Phénomène(s): Orages, Pluie-inondation
Des orages violents sont attendus dans l'après-midi.
Source: vigilance.meteofrance.fr
⚠️ Suivez les consignes de sécurité.
```

### Reporting horaire (alerte active)
```
🔴 POINT SITUATION [15:00] — ALERTE ORANGE
Dept: 13 | En cours depuis: 1h30min
Phénomène(s): Orages, Pluie-inondation
Prochain point dans 60 min.
vigilance.meteofrance.fr
```

### Fin d'alerte
```
✅ FIN D'ALERTE — ORANGE levée
Dept: 13 | Durée totale: 3h15min
Retour à la normale.
```

---

## Exécution des tests

```bash
python -m pytest tests/ -v
```

---

## Contribution

Les contributions sont les bienvenues ! Merci de :
1. Forker le dépôt
2. Créer une branche (`git checkout -b feature/ma-fonctionnalite`)
3. Commiter vos changements (`git commit -m 'Ajout de ma fonctionnalité'`)
4. Pousser la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrir une Pull Request

---

## Licence

Ce projet est sous licence [MIT](LICENSE).

---

## Ressources utiles

- [Documentation Meshtastic Python](https://python.meshtastic.org/)
- [Vigilance Météo-France](https://vigilance.meteofrance.fr)
- [API Open-Meteo Météo-France](https://open-meteo.com/en/docs/meteofrance-api)
- [Vigicrues API](https://www.vigicrues.gouv.fr/services/v1.1)
- [Portail API Météo-France](https://portail-api.meteofrance.fr)
- [Géorisques](https://www.georisques.gouv.fr)
