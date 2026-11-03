import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.meshcore_client import MeshCoreClient


def test_parse_meshcore_bme280_telemetry():
    payload = {
        "lpp": [
            {"channel": 1, "type": "temperature", "value": 21.75},
            {"channel": 1, "type": "humidity", "value": 48.5},
            {"channel": 1, "type": "barometer", "value": 1012.3},
        ]
    }

    assert MeshCoreClient._parse_telemetry(payload) == {
        "temperature": 21.75,
        "humidity": 48.5,
        "pressure": 1012.3,
    }


def test_parse_meshcore_bme280_numeric_lpp_types():
    payload = {"lpp": [
        {"type": 103, "value": 20.0},
        {"type": 104, "value": 50.0},
        {"type": 115, "value": 1008.0},
    ]}

    assert MeshCoreClient._parse_telemetry(payload)["pressure"] == 1008.0
