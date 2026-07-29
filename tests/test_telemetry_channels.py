
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.controller import BotController
from unittest.mock import MagicMock

def test_telemetry_and_channels():
    # Mock du client Meshtastic
    mock_client = MagicMock()
    mock_client.broadcast_channel = 0
    mock_client.local_telemetry = {}
    
    controller = BotController(mock_client)
    
    print("--- TEST TÉLÉMÉTRIE ET CANAUX ---")
    
    # 1. Simulation de réception de télémétrie
    print("\n1. Simulation réception BME280...")
    # On simule ce que ferait _on_receive
    mock_client.local_telemetry["local"] = {
        "temperature": 22.5,
        "humidity": 45,
        "pressure": 1013,
        "timestamp": 123456789
    }
    
    # 2. Test de la commande !meteo avec données locales
    print("\n2. Test !meteo avec données locales...")
    m1 = controller.get_weather_for_city("Caen")
    print(f"Résultat:\n{m1}")
    
    # 3. Test du changement de canal
    print("\n3. Test commande !canal...")
    r1 = controller.set_broadcast_channel("2")
    print(f"Changement vers 2: {r1}")
    print(f"Canal dans le client: {mock_client.broadcast_channel}")
    
    r2 = controller.set_broadcast_channel("invalid")
    print(f"Changement invalide: {r2}")

if __name__ == "__main__":
    test_telemetry_and_channels()
