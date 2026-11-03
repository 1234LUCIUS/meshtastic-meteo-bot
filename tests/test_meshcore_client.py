import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.meshcore_client import MeshCoreClient


def test_meshcore_simulation_matches_client_contract():
    received = []
    client = MeshCoreClient(
        on_message=lambda sender, text, packet: received.append((sender, text, packet)),
        simulation_mode=True,
    )

    assert client.connect() is True
    assert client.connected is True
    assert client.send_text("Bonjour") is True
    assert client.send_alert("Alerte") is True
    client.disconnect()
    assert client.connected is False


def test_meshcore_message_splitting_is_utf8_safe():
    parts = MeshCoreClient._split_message("é" * 250, max_length=40)

    assert len(parts) > 1
    assert all(len(part.encode("utf-8")) <= 40 for part in parts)
    assert parts[0].startswith("(1/")
