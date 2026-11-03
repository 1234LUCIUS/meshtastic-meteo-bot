# 📡 Meshtastic / MeshCore Météo Bot (Spécial Normandie & Résilience)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Meshtastic](https://img.shields.io/badge/Meshtastic-2.3.14-green)](https://meshtastic.org)
[![MeshCore](https://img.shields.io/badge/MeshCore-2.3.17-green)](https://github.com/meshcore-dev/meshcore_py)

Un bot Python autonome et ultra-résilient, conçu pour transformer votre réseau Meshtastic ou MeshCore en une véritable passerelle de sécurité civile pour la **Normandie**. Il fonctionne même en cas de coupure internet totale.

Le même contrôleur métier fonctionne avec les deux réseaux. Choisissez le backend avec `MESH_NETWORK=meshtastic` ou `MESH_NETWORK=meshcore` dans `.env`, ou utilisez `python main.py --network meshcore`. MeshCore utilise son API Python officielle et ses messages de canal ; les valeurs `BROADCAST_CHANNEL` et `ALERT_CHANNEL` correspondent aux index de canaux MeshCore.

---

## 🌟 Fonctionnalités Avancées

### 🧠 IA Locale Hors-Ligne (`!ia`)
-   **Raisonnement Autonome** : Intègre un modèle de langage léger (TinyLlama-1.1B) pour répondre intelligemment aux questions des utilisateurs, même sans connexion internet.
-   **Contexte Local** : L'IA utilise les données du cache (météo, alertes, capteurs BME280) pour fournir des réponses pertinentes et concises.
-   **Optimisé Meshtastic** : Réponses en français, limitées à moins de 200 caractères pour une diffusion efficace sur le réseau.

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

Le Meshtastic Météo Bot est conçu pour être votre allié indispensable même dans les situations les plus critiques, lorsque les infrastructures de communication traditionnelles sont défaillantes. Toutes les fonctionnalités suivantes sont opérationnelles sans aucune connexion internet :

-   **Cerveau Local (`!ia`)** : L'IA embarquée répond à vos questions en utilisant les données locales et les consignes de sécurité, sans dépendre d'un cloud externe.
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
| `!ia <question>` | **Question à l'IA locale (Hors-ligne)** |
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

**Lancement Meshtastic :** `python main.py`

**Lancement MeshCore :** configurez `MESHCORE_CONNECTION_TYPE` et les paramètres associés dans `.env`, puis exécutez `python main.py --network meshcore`.

---

## 🏗️ Architecture du Projet

-   `bot/` : Cœur du système (clients Meshtastic/MeshCore, Commandes, Scheduler).
-   `services/` : Modules spécialisés (Météo, Vigilance, Web Search, Emergency, **Local AI**).
-   `data/` : Base de données SQLite pour le cache hors-ligne.
-   `models/` : Contient le modèle GGUF de l'IA locale.
-   `tests/` : Suite de tests de validation (Résilience, Télémétrie, Formatage, **IA Locale**).

---

## 🤝 Contribution & Sécurité

Ce bot est un outil expérimental de sécurité civile. Les contributions pour ajouter des sources locales normandes ou améliorer la résilience sont les bienvenues.

**Licence** : MIT
**Auteur** : Manus AI et 1234LUCIUS 
