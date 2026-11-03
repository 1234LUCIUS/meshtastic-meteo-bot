import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import bot.network as network


class FakeClient:
    firmware = "fake"

    def __init__(self, on_message=None, simulation_mode=False):
        self.on_message_callback = on_message
        self.simulation_mode = simulation_mode
        self.connected = False
        self.disconnected = False

    def connect(self):
        self.connected = self.firmware == "meshcore"
        return self.connected

    def disconnect(self):
        self.disconnected = True


class FakeMeshCore(FakeClient):
    firmware = "meshcore"


class FakeMeshtastic(FakeClient):
    firmware = "meshtastic"


def test_auto_detection_selects_meshcore_first(monkeypatch):
    monkeypatch.setattr(network, "MeshCoreClient", FakeMeshCore)
    monkeypatch.setattr(network, "MeshtasticClient", FakeMeshtastic)

    client = network.connect_network_client("auto")

    assert client.firmware == "meshcore"
    assert client.connected is True
