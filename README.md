# 📡 Meshtastic Météo Bot (Spécial Normandie & Résilience)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Meshtastic](https://img.shields.io/badge/Meshtastic-2.3.14-green)](https://meshtastic.org)

Un bot Python autonome et ultra-résilient, conçu pour transformer votre réseau Meshtastic en une véritable passerelle de sécurité civile pour la **Normandie**. Il fonctionne même en cas de coupure internet totale.

---

## 🌟 Fonctionnalités Avancées

### 🛡️ Résilience Hors-Ligne (Mode Crise)
-   **Cache Local SQLite** : Sauvegarde automatique de la dernière météo, des vigilances et des actualités. En cas de coupure réseau, le bot diffuse les dernières infos connues (marquées par ⌛).
-   **Consignes de Sécurité Civile (`!urgence`)** : Accès instantané à des fiches de secours statiques (Inondation, Tempête, Incendie, Séisme) conformes aux directives officielles de la Sécurité Civile, pesant moins de 200 caractères.
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
-   Un **nœud Meshtastic** connecté en USB/Série, TCP ou BLE.

### 2. Installation

```bash
# Cloner le dépôt
git clone https://github.com/1234LUCIUS/meshtastic-meteo-bot.git
cd meshtastic-meteo-bot

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration

```bash
cp .env.example .env
# Éditer .env avec votre port COM et localisation
```

**Lancement :** `python main.py`

---

## 🏗️ Architecture du Projet

-   `bot/` : Cœur du système (Client Meshtastic, Commandes, Scheduler).
-   `services/` : Modules spécialisés (Météo, Vigilance, Web Search, Emergency).
-   `data/` : Base de données SQLite pour le cache hors-ligne.
-   `tests/` : Suite de tests de validation (Résilience, Télémétrie, Formatage).

---

## 🤝 Contribution & Sécurité

Ce bot est un outil expérimental de sécurité civile. Les contributions pour ajouter des sources locales normandes ou améliorer la résilience sont les bienvenues.

**Licence** : MIT
**Auteur** : Manus AI (pour 1234LUCIUS)
