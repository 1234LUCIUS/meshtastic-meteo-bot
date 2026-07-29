
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.controller import BotController
from unittest.mock import MagicMock

def test_offline_flow():
    # Mock du client Meshtastic
    mock_client = MagicMock()
    controller = BotController(mock_client)
    
    print("--- TEST RÉSILIENCE HORS-LIGNE ---")
    
    # 1. Premier passage (remplit le cache)
    print("\n1. Premier passage (avec réseau)...")
    m1 = controller.get_weather_for_city("Caen")
    print(f"Résultat: {m1}")
    
    # 2. Simulation de coupure réseau
    # On va modifier l'URL pour simuler une erreur
    import services.meteo
    services.meteo.OPEN_METEO_URL = "https://invalid-url-for-test.com"
    
    print("\n2. Deuxième passage (simulation coupure réseau)...")
    m2 = controller.get_weather_for_city("Caen")
    print(f"Résultat: {m2}")
    
    # 3. Test des consignes d'urgence (statiques)
    print("\n3. Test consignes d'urgence (statiques)...")
    u1 = controller.get_emergency_guidelines("inondation")
    print(f"Résultat: {u1}")

if __name__ == "__main__":
    test_offline_flow()
