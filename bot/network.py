"""Sélection et détection du backend radio utilisé par le bot."""

import logging
from typing import Callable, Optional, Type

from bot.meshcore_client import MeshCoreClient
from bot.meshtastic_client import MeshtasticClient

logger = logging.getLogger(__name__)


CLIENT_TYPES: dict[str, Type] = {
    "meshtastic": MeshtasticClient,
    "meshcore": MeshCoreClient,
}


def connect_network_client(
    network: str = "auto",
    on_message: Optional[Callable] = None,
    simulation_mode: bool = False,
):
    """Connecte le backend demandé, ou détecte le firmware automatiquement.

    En mode automatique, MeshCore est essayé en premier car son handshake
    compagnon est explicite. En cas d'échec, le client Meshtastic est essayé
    sur le même port ou endpoint. Chaque client nettoie sa tentative avant le
    passage au protocole suivant.
    """
    requested = (network or "auto").lower()
    if requested not in ("auto", *CLIENT_TYPES):
        raise ValueError(f"Backend réseau inconnu : {network}")

    candidates = [CLIENT_TYPES[requested]] if requested != "auto" else [
        MeshCoreClient,
        MeshtasticClient,
    ]

    if simulation_mode:
        # La simulation historique reste Meshtastic par défaut, mais accepte
        # explicitement --network meshcore pour tester ce backend.
        candidates = [MeshtasticClient] if requested == "auto" else candidates[:1]

    for client_type in candidates:
        client = client_type(on_message=on_message, simulation_mode=simulation_mode)
        logger.info("Tentative de connexion avec le backend %s.", client.firmware)
        if client.connect():
            logger.info("Firmware détecté : %s.", client.firmware)
            return client
        client.disconnect()

    return None
