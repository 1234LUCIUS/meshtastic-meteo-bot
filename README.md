# 📡 Bot météo MT/MC (Spécial Normandie & Résilience)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Meshtastic](https://img.shields.io/badge/Meshtastic-2.3.14-green)](https://meshtastic.org)
[![MeshCore](https://img.shields.io/badge/MeshCore-2.3.17-green)](https://github.com/meshcore-dev/meshcore_py)

Un bot Python autonome et ultra-résilient, conçu pour transformer votre réseau Meshtastic ou MeshCore en une véritable passerelle de sécurité civile pour la **Normandie**. Il fonctionne même en cas de coupure internet totale.

Le même contrôleur métier fonctionne avec les deux réseaux. Par défaut, le bot détecte automatiquement le firmware du matériel connecté : il essaie le protocole MeshCore puis Meshtastic. Le backend peut aussi être forcé avec `MESH_NETWORK=meshtastic`, `MESH_NETWORK=meshcore` ou les options `--network auto|meshtastic|meshcore`. MeshCore utilise son API Python officielle et ses messages de canal ; les valeurs `BROADCAST_CHANNEL` et `ALERT_CHANNEL` correspondent aux index de canaux MeshCore.

La documentation est séparée par firmware : [options Meshtastic](docs/meshtastic.md), [options MeshCore](docs/meshcore.md) et [commandes communes](docs/README.md).

---

## 🌟 Fonctionnalités Avancées

### 🧩 Deux backends radio
-   **Meshtastic** : connexion série/USB ou TCP, messages texte, GPS et télémétrie environnementale.
-   **MeshCore** : connexion série/USB, TCP ou BLE, messages de canal et réponse sur le canal d’origine.
-   **Détection automatique** : le firmware est testé au démarrage et affiché dans les logs.

### 🛡️ Résilience Hors-Ligne (Mode Crise)
-   **Cache Local SQLite** : Sauvegarde automatique de la dernière météo, des vigilances et des actualités. En cas de coupure réseau, le bot diffuse les dernières infos connues (marquées par ⌛).
-   **Consignes de Sécurité Civile (`!urgence`)** : Accès instantané à des fiches de secours statiques (Inondation, Tempête, Incendie, Séisme) conformes aux directives officielles, pesant moins de 200 caractères.
-   **Capteurs Locaux (BME280)** : Intégration en temps réel des données de télémétrie de votre module. Affiche la température, l'humidité et la pression locales réelles dans le bulletin météo.

### 🌤️ Météo & Vigilance Haute Précision
-   **Modèle AROME** : Prévisions ultra-locales via Météo-France.
-   **Vigilance Automatisée** : Surveillance des 5 départements normands (14, 27, 50, 61, 76) avec reporting horaire en cas d'alerte Orange/Rouge.
-   **Multi-Risques** : Vigicrues (inondations), Météo des Forêts (incendies) et suivi satellite NASA FIRMS (feux actifs).

### 📰 Actualités & Réseaux Sociaux
-   **Commande `!actu <ville>`** : Extraction intelligente et condensée des infos importantes (presse locale + sites municipaux) avec liens courts.
-   **Commande `!normandie`** : Scan priorisé des SDIS et Préfectures pour les alertes de sécurité.
-   **Gestion des Canaux (`!canal`)** : Basculement dynamique du canal de diffusion pour ne pas surcharger le canal principal de secours.

---

## 🔌 Mode Hors-Ligne & Survie

Le Bot météo MT/MC est conçu pour être votre allié indispensable même dans les situations les plus critiques, lorsque les infrastructures de communication traditionnelles sont défaillantes. Toutes les fonctionnalités suivantes sont opérationnelles sans aucune connexion internet :

-   **Base de Connaissances Statique (`!urgence`)** : Accès immédiat aux fiches de sécurité officielles, ultra-compactes et pré-enregistrées.
-   **Données Capteurs Locaux (`!meteo`)** : Les relevés de température, humidité et pression de votre module BME280 sont toujours disponibles, offrant une météo hyper-locale en temps réel.
-   **Cache de Résilience** : Les dernières informations (météo, vigilances, actualités) sont stockées localement et peuvent être consultées, même si elles ne sont plus à jour, avec une indication claire de leur ancienneté.

---

## ⚙️ Commandes Clés

| Commande | Description |
|---|---|
| `!meteo [ville]` | Météo locale (Capteur BME280 + Prévisions) |
| `!urgence <thème>` | **Consignes de sécurité (Hors-ligne)** |
| `!alertes` | Vigilance Météo-France (Cache si hors-ligne) |
| `!actu <ville>` | Actualités locales importantes + Liens courts |
| `!normandie` | Scan SDIS et Préfectures (Sécurité) |
| `!canal <0-7>` | Change le canal de diffusion périodique |
| `!aide` | Liste complète des commandes |

---

## 🚀 Installation Rapide

### 1. Prérequis
-   **Python 3.10 ou supérieur**
-   Un **nœud Meshtastic** connecté en USB/Série ou TCP, ou un **nœud MeshCore companion** connecté en Série, TCP ou BLE.

### 2. Installation

```bash
# Cloner le dépôt
git clone https://github.com/1234LUCIUS/meshtastic-meteo-bot.git
cd meshtastic-meteo-bot

# Installer les dépendances (inclut llama-cpp-python)
pip install -r requirements.txt
```

### 3. Configuration

```bash
cp .env.example .env
# Éditer .env avec votre port COM et localisation
```

### 4. Téléchargement du modèle IA (une seule fois)

```bash
mkdir -p models
wget -O models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf?download=true
```

**Lancement avec détection automatique :** configurez le type de connexion et les paramètres associés dans `.env`, puis exécutez `python main.py`. Le firmware détecté est affiché dans les logs et dans le message de démarrage du bot.

**Lancement MeshCore forcé :** configurez `MESHCORE_CONNECTION_TYPE` et les paramètres associés dans `.env`, puis exécutez `python main.py --network meshcore`.

---

## 🏗️ Architecture du Projet

-   `bot/` : Cœur du système (clients Meshtastic/MeshCore, Commandes, Scheduler).
-   `docs/` : Guides séparés des options Meshtastic, MeshCore et des commandes communes.
-   `services/` : Modules spécialisés (Météo, Vigilance, Web Search, Emergency, **Local AI**).
-   `data/` : Base de données SQLite pour le cache hors-ligne.
-   `models/` : Contient le modèle GGUF de l'IA locale.
-   `tests/` : Suite de tests de validation (Résilience, Télémétrie, Formatage, **IA Locale**).

---

## 🤝 Contribution & Sécurité

Ce bot est un outil expérimental de sécurité civile. Les contributions pour ajouter des sources locales normandes ou améliorer la résilience sont les bienvenues.

**Licence** : MIT
**Auteur** : Manus AI et 1234LUCIUS 
