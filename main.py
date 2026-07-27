#!/usr/bin/env python3
"""
Meshtastic Météo Bot — Point d'entrée principal.

Lance le bot en mode normal (avec matériel Meshtastic) ou en mode simulation.

Usage :
    python main.py                  # Mode normal (Serial par défaut)
    python main.py --simulate       # Mode simulation (sans matériel)
    python main.py --test-meteo     # Test du service météo uniquement
    python main.py --test-alertes   # Test du service vigilance uniquement
"""

import argparse
import signal
import sys
import time

from bot.config import setup_logging
from bot.meshtastic_client import MeshtasticClient
from bot.controller import BotController
from bot.scheduler import BotScheduler

logger = setup_logging()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Meshtastic Météo Bot — Diffusion météo et alertes sur réseau mesh."
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Démarre en mode simulation (sans matériel Meshtastic réel).",
    )
    parser.add_argument(
        "--test-meteo",
        action="store_true",
        help="Teste le service météo et affiche le résultat.",
    )
    parser.add_argument(
        "--test-alertes",
        action="store_true",
        help="Teste le service vigilance et affiche le résultat.",
    )
    parser.add_argument(
        "--test-crues",
        action="store_true",
        help="Teste le service Vigicrues et affiche le résultat.",
    )
    parser.add_argument(
        "--test-officiel",
        action="store_true",
        help="Teste les sources officielles et affiche le résultat.",
    )
    parser.add_argument(
        "--test-feux",
        action="store_true",
        help="Teste le service Météo des Forêts et affiche le résultat.",
    )
    parser.add_argument(
        "--test-suivi-feux",
        action="store_true",
        help="Teste le suivi des feux actifs et affiche le résultat.",
    )
    parser.add_argument(
        "--ville",
        type=str,
        default="",
        help="Ville à utiliser pour les tests (ex: --ville Paris).",
    )
    return parser.parse_args()


def run_tests(args, controller: BotController):
    """Exécute les tests des services sans démarrer le bot complet."""
    if args.test_meteo:
        logger.info("=== TEST SERVICE MÉTÉO ===")
        if args.ville:
            result = controller.get_weather_for_city(args.ville)
        else:
            result = controller.get_weather_default()
        print("\n" + result + "\n")

    if args.test_alertes:
        logger.info("=== TEST SERVICE VIGILANCE ===")
        result = controller.get_vigilance_summary()
        print("\n" + result + "\n")

    if args.test_crues:
        logger.info("=== TEST SERVICE VIGICRUES ===")
        result = controller.get_vigicrues_summary()
        print("\n" + result + "\n")

    if args.test_officiel:
        logger.info("=== TEST SOURCES OFFICIELLES ===")
        result = controller.get_official_sources_summary()
        print("\n" + result + "\n")

    if args.test_feux:
        logger.info("=== TEST MÉTÉO DES FORÊTS ===")
        result = controller.get_forest_fire_summary()
        print("\n" + result + "\n")

    if args.test_suivi_feux:
        logger.info("=== TEST SUIVI DES FEUX ACTIFS ===")
        from bot.config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE
        result = controller.get_active_fires_summary(DEFAULT_LATITUDE, DEFAULT_LONGITUDE)
        print("\n" + result + "\n")


def main():
    args = parse_args()

    logger.info("=" * 60)
    logger.info("  Meshtastic Météo Bot — Démarrage")
    logger.info("=" * 60)

    # Initialisation du client Meshtastic
    simulation = args.simulate or any([
        args.test_meteo, args.test_alertes, args.test_crues, args.test_officiel
    ])

    client = MeshtasticClient(simulation_mode=simulation)

    # Initialisation du contrôleur
    controller = BotController(client)

    # Enregistrement du callback de réception de messages
    client.on_message_callback = controller.handle_incoming_message

    # Mode test : exécuter les tests et quitter
    if any([args.test_meteo, args.test_alertes, args.test_crues, args.test_officiel]):
        run_tests(args, controller)
        return

    # Connexion au nœud Meshtastic
    if not client.connect():
        if not simulation:
            logger.error(
                "Impossible de se connecter au nœud Meshtastic. "
                "Vérifiez la connexion ou utilisez --simulate pour le mode test."
            )
            sys.exit(1)

    # Initialisation du planificateur
    scheduler = BotScheduler(controller)

    # Gestion du signal d'arrêt (Ctrl+C, SIGTERM)
    def shutdown(signum, frame):
        logger.info("Signal d'arrêt reçu. Arrêt du bot...")
        scheduler.stop()
        client.disconnect()
        logger.info("Bot arrêté proprement.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    # SIGTERM n'est pas disponible sur Windows, donc on ne l'enregistre pas
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, shutdown)

    # Démarrage du planificateur
    scheduler.start()

    # Message de démarrage sur le réseau
    startup_msg = (
        "📡 Météo-Bot actif ! Commandes : "
        "!meteo [ville] | !alertes | !crues | !officiel | !aide"
    )
    client.send_text(startup_msg)

    logger.info("Bot démarré. En attente de messages et d'événements planifiés...")
    logger.info("Appuyez sur Ctrl+C pour arrêter.")

    # Boucle principale
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown(None, None)


if __name__ == "__main__":
    main()
