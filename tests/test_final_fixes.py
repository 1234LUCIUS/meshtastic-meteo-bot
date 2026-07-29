
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.controller import BotController
from unittest.mock import MagicMock

def test_final_fixes():
    mock_client = MagicMock()
    controller = BotController(mock_client)
    
    print("--- TEST DES CORRECTIONS FINALES ---")
    
    # 1. Test Vigilance (Correction du département)
    print("\n1. Test Vigilance (Dept 14)...")
    v1 = controller.get_vigilance_summary("14")
    print(f"Résultat: {v1}")
    
    # 2. Test Consignes Officielles
    print("\n2. Test Consignes Sécurité Civile...")
    u1 = controller.get_emergency_guidelines("inondation")
    print(f"Résultat:\n{u1}")
    
    # 3. Test Commande !normandie optimisée
    print("\n3. Test Commande !normandie (Compacte)...")
    n1 = controller.get_normandie_web_summary()
    print(f"Résultat:\n{n1}")
    print(f"Longueur: {len(n1)} caractères")

if __name__ == "__main__":
    test_final_fixes()
