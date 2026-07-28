"""
Client Meshtastic — Gestion de la connexion (Serial/TCP/BLE) et envoi/réception de messages.
"""

import logging
import time
from typing import Callable, Optional

try:
    import meshtastic
    import meshtastic.serial_interface
    import meshtastic.tcp_interface
    from pubsub import pub
    MESHTASTIC_AVAILABLE = True
except ImportError:
    MESHTASTIC_AVAILABLE = False

from bot.config import (
    MESHTASTIC_CONNECTION_TYPE,
    MESHTASTIC_SERIAL_PORT,
    MESHTASTIC_TCP_HOST,
    BROADCAST_CHANNEL,
    ALERT_CHANNEL,
)

logger = logging.getLogger(__name__)

# Longueur maximale d'un message Meshtastic (en octets UTF-8)
MAX_MESSAGE_LENGTH = 228


class MeshtasticClient:
    """
    Gère la connexion à un nœud Meshtastic et l'envoi/réception de messages.
    Supporte les connexions Serial, TCP et un mode simulation pour les tests.
    """

    def __init__(self, on_message: Optional[Callable] = None, simulation_mode: bool = False):
        """
        Initialise le client.

        :param on_message: Callback appelé à chaque réception de message texte.
                           Signature : on_message(sender_id, text, packet)
        :param simulation_mode: Si True, simule la connexion sans matériel réel.
        """
        self.interface = None
        self.on_message_callback = on_message
        self.simulation_mode = simulation_mode
        self.connected = False
        self._node_info_cache = {}

    def connect(self) -> bool:
        """Établit la connexion au nœud Meshtastic."""
        if self.simulation_mode:
            logger.warning("Mode simulation activé — aucun matériel Meshtastic requis.")
            self.connected = True
            return True

        if not MESHTASTIC_AVAILABLE:
            logger.error("La bibliothèque 'meshtastic' n'est pas installée.")
            return False

        try:
            if MESHTASTIC_CONNECTION_TYPE == "tcp":
                logger.info(f"Connexion TCP à {MESHTASTIC_TCP_HOST}...")
                self.interface = meshtastic.tcp_interface.TCPInterface(
                    hostname=MESHTASTIC_TCP_HOST
                )
            else:
                logger.info(f"Connexion série sur {MESHTASTIC_SERIAL_PORT}...")
                self.interface = meshtastic.serial_interface.SerialInterface(
                    devPath=MESHTASTIC_SERIAL_PORT
                )

            # Abonnement aux événements
            pub.subscribe(self._on_receive, "meshtastic.receive")
            pub.subscribe(self._on_connection, "meshtastic.connection.established")
            pub.subscribe(self._on_disconnect, "meshtastic.connection.lost")

            self.connected = True
            logger.info("Connexion Meshtastic établie avec succès.")
            return True

        except Exception as e:
            logger.error(f"Échec de la connexion Meshtastic : {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Ferme proprement la connexion."""
        if self.interface:
            try:
                self.interface.close()
                logger.info("Connexion Meshtastic fermée.")
            except Exception as e:
                logger.warning(f"Erreur lors de la fermeture : {e}")
        self.connected = False

    def send_text(
        self,
        text: str,
        destination: str = "^all",
        channel_index: int = BROADCAST_CHANNEL,
        want_ack: bool = False,
    ) -> bool:
        """Envoie un message texte (version simplifiée)."""
        if self.simulation_mode:
            logger.info(f"[SIMULATION] {text}")
            return True

        if not self.interface:
            return False

        try:
            # Envoi direct sans découpage pour les tests de fiabilité
            self.interface.sendText(
                text=text,
                destinationId=destination,
                channelIndex=channel_index,
                wantAck=want_ack
            )
            return True
        except Exception as e:
            logger.error(f"Erreur d'envoi direct : {e}")
            return False

    def send_alert(self, text: str, destination: str = "^all") -> bool:
        """Envoie un message d'alerte sur le canal d'alertes."""
        return self.send_text(text, destination=destination, channel_index=ALERT_CHANNEL)

    def get_local_node_info(self) -> dict:
        """Retourne les informations du nœud local (position, ID, etc.)."""
        if self.simulation_mode:
            return {
                "id": "!simulation",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "altitude": 35,
            }
        if self.interface:
            try:
                node = self.interface.getNode("^local")
                pos = node.localConfig.position if node else None
                return {
                    "id": self.interface.myInfo.my_node_num if self.interface.myInfo else None,
                    "latitude": pos.lat if pos else None,
                    "longitude": pos.lon if pos else None,
                }
            except Exception as e:
                logger.warning(f"Impossible de récupérer les infos du nœud local : {e}")
        return {}

    def get_node_position(self, node_id: str) -> Optional[dict]:
        """Retourne la position d'un nœud spécifique."""
        if self.simulation_mode:
            return {"latitude": 48.8566, "longitude": 2.3522}
        if self.interface:
            try:
                nodes = self.interface.nodes
                if nodes and node_id in nodes:
                    node = nodes[node_id]
                    pos = node.get("position", {})
                    if pos:
                        return {
                            "latitude": pos.get("latitude"),
                            "longitude": pos.get("longitude"),
                        }
            except Exception as e:
                logger.warning(f"Impossible de récupérer la position du nœud {node_id} : {e}")
        return None

    # -------------------------------------------------------------------------
    # Callbacks internes
    # -------------------------------------------------------------------------

    def _on_receive(self, packet, interface):
        """Appelé à chaque réception d'un paquet."""
        try:
            # Log de debug pour voir tous les paquets entrants
            logger.debug(f"Paquet reçu : {packet.get('id')} de {packet.get('fromId')}")
            
            decoded = packet.get("decoded", {})
            portnum = decoded.get("portnum", "")

            # Certains firmwares utilisent des entiers pour portnum
            # TEXT_MESSAGE_APP correspond à 1
            is_text = (portnum == "TEXT_MESSAGE_APP" or portnum == 1)

            if is_text:
                text = decoded.get("text", "")
                if isinstance(text, bytes):
                    text = text.decode("utf-8", errors="replace")
                text = text.strip()
                
                sender = packet.get("fromId", "unknown")
                logger.info(f"Message reçu de {sender}: {text}")

                if self.on_message_callback:
                    self.on_message_callback(sender, text, packet)
            else:
                logger.debug(f"Paquet ignoré (portnum: {portnum})")

        except Exception as e:
            logger.error(f"Erreur lors du traitement du paquet : {e}")

    def _on_connection(self, interface, topic=None):
        """Appelé lors de l'établissement de la connexion."""
        logger.info("Événement : connexion Meshtastic établie.")
        self.connected = True

    def _on_disconnect(self, interface, topic=None):
        """Appelé lors de la perte de connexion."""
        logger.warning("Événement : connexion Meshtastic perdue.")
        self.connected = False

    # -------------------------------------------------------------------------
    # Utilitaires
    # -------------------------------------------------------------------------

    @staticmethod
    def _split_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list:
        """
        Découpe un message en plusieurs parties si nécessaire.
        Respecte les mots pour éviter les coupures en milieu de mot.
        """
        if len(text.encode("utf-8")) <= max_length:
            return [text]

        parts = []
        words = text.split(" ")
        current = ""

        for word in words:
            test = f"{current} {word}".strip()
            if len(test.encode("utf-8")) <= max_length - 6:  # Réserve pour "(x/y)"
                current = test
            else:
                if current:
                    parts.append(current)
                current = word

        if current:
            parts.append(current)

        # Ajouter les numéros de partie
        total = len(parts)
        if total > 1:
            parts = [f"({i+1}/{total}) {p}" for i, p in enumerate(parts)]

        return parts
