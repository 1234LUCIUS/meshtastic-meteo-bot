"""
Parseur et gestionnaire de commandes Meshtastic.
Toutes les commandes commencent par '!' (ex: !meteo, !alertes, !crues).
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Aide affichée à l'utilisateur
HELP_TEXT = (
    "=== METEO-BOT ===\n"
    "!meteo          -> Météo locale (GPS)\n"
    "!meteo <ville>  -> Météo d'une ville\n"
    "!alertes        -> Vigilances Météo-France\n"
    "!crues          -> Alertes Vigicrues\n"
    "!feux           -> Météo des Forêts (danger)\n"
    "!suivi_feux     -> Feux actifs (satellites)\n"
    "!normandie      -> Scan web officiel Normandie\n"
    "!officiel       -> Infos sources officielles\n"
    "!aide           -> Cette aide"
)


class CommandParser:
    """
    Analyse les messages reçus et dispatche les commandes aux handlers appropriés.
    """

    def __init__(self, bot_controller):
        """
        :param bot_controller: Instance du BotController qui contient les services.
        """
        self.controller = bot_controller
        self._commands = {
            "!meteo": self._cmd_meteo,
            "!météo": self._cmd_meteo,
            "!alertes": self._cmd_alertes,
            "!alerte": self._cmd_alertes,
            "!crues": self._cmd_crues,
            "!crue": self._cmd_crues,
            "!feux": self._cmd_feux,
            "!feu": self._cmd_feux,
            "!mdf": self._cmd_feux,
            "!suivi_feux": self._cmd_suivi_feux,
            "!suivifeux": self._cmd_suivi_feux,
            "!incendie": self._cmd_suivi_feux,
            "!normandie": self._cmd_normandie,
            "!officiel": self._cmd_officiel,
            "!officiels": self._cmd_officiel,
            "!aide": self._cmd_aide,
            "!help": self._cmd_aide,
            "!ping": self._cmd_ping,
        }

    def handle(self, sender_id: str, text: str, packet: dict) -> Optional[str]:
        """
        Traite un message reçu.

        :param sender_id: ID du nœud expéditeur.
        :param text: Texte du message.
        :param packet: Paquet Meshtastic complet.
        :return: Réponse à envoyer, ou None si pas de commande reconnue.
        """
        if not text.startswith("!"):
            return None

        parts = text.strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1].strip() if len(parts) > 1 else ""

        handler = self._commands.get(command)
        if handler:
            logger.info(f"Commande '{command}' reçue de {sender_id} (args: '{args}')")
            try:
                return handler(sender_id, args, packet)
            except Exception as e:
                logger.error(f"Erreur lors du traitement de '{command}' : {e}")
                return f"Erreur interne lors du traitement de '{command}'."
        else:
            return f"Commande inconnue : '{command}'. Tapez !aide pour la liste."

    # -------------------------------------------------------------------------
    # Handlers de commandes
    # -------------------------------------------------------------------------

    def _cmd_meteo(self, sender_id: str, args: str, packet: dict) -> str:
        """Commande !meteo [ville]"""
        if args:
            # Météo pour une ville spécifique
            return self.controller.get_weather_for_city(args)
        else:
            # Météo basée sur la position GPS du nœud expéditeur
            position = self._extract_position(packet)
            if position:
                return self.controller.get_weather_for_position(
                    position["latitude"], position["longitude"]
                )
            else:
                # Fallback sur la position par défaut
                return self.controller.get_weather_default()

    def _cmd_alertes(self, sender_id: str, args: str, packet: dict) -> str:
        """Commande !alertes [département]"""
        dept = args.strip() if args else None
        if not dept:
            # Essayer de déduire le département depuis la position GPS
            position = self._extract_position(packet)
            if position:
                dept = self.controller.get_department_from_position(
                    position["latitude"], position["longitude"]
                )
        return self.controller.get_vigilance_summary(dept)

    def _cmd_crues(self, sender_id: str, args: str, packet: dict) -> str:
        """Commande !crues"""
        return self.controller.get_vigicrues_summary()

    def _cmd_feux(self, sender_id: str, args: str, packet: dict) -> str:
        """Commande !feux [département]"""
        dept = args.strip() if args else None
        if not dept:
            position = self._extract_position(packet)
            if position:
                dept = self.controller.get_department_from_position(
                    position["latitude"], position["longitude"]
                )
        return self.controller.get_forest_fire_summary(dept)

    def _cmd_suivi_feux(self, sender_id: str, args: str, packet: dict) -> str:
        """Commande !suivi_feux"""
        position = self._extract_position(packet)
        if not position:
            from bot.config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE
            position = {"latitude": DEFAULT_LATITUDE, "longitude": DEFAULT_LONGITUDE}
        
        return self.controller.get_active_fires_summary(
            position["latitude"], position["longitude"]
        )

    def _cmd_officiel(self, sender_id: str, args: str, packet: dict) -> str:
        """Commande !officiel"""
        return self.controller.get_official_sources_summary()

    def _cmd_normandie(self, sender_id: str, args: str, packet: dict) -> str:
        """Commande !normandie"""
        return self.controller.get_normandie_web_summary()

    def _cmd_aide(self, sender_id: str, args: str, packet: dict) -> str:
        """Commande !aide"""
        return HELP_TEXT

    def _cmd_ping(self, sender_id: str, args: str, packet: dict) -> str:
        """Commande !ping"""
        return f"Pong! Météo-Bot actif. [{sender_id}]"

    # -------------------------------------------------------------------------
    # Utilitaires
    # -------------------------------------------------------------------------

    @staticmethod
    def _extract_position(packet: dict) -> Optional[dict]:
        """Extrait la position GPS depuis un paquet Meshtastic si disponible."""
        try:
            decoded = packet.get("decoded", {})
            position = decoded.get("position", {})
            lat = position.get("latitude") or position.get("latitudeI")
            lon = position.get("longitude") or position.get("longitudeI")

            if lat and lon:
                # Les coordonnées peuvent être en degrés × 1e7
                if abs(lat) > 180:
                    lat = lat / 1e7
                    lon = lon / 1e7
                return {"latitude": lat, "longitude": lon}
        except Exception:
            pass
        return None
