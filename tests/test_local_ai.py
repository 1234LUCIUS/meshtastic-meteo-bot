
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.local_ai import LocalAIService

def test_ai():
    print("--- TEST IA LOCALE HORS-LIGNE ---")
    print("Chargement du service (cela peut prendre quelques secondes)...")
    ai = LocalAIService()
    
    questions = [
        "Quel temps fait-il ?",
        "Donne-moi un conseil pour la pluie.",
        "Qui es-tu ?"
    ]
    
    for q in questions:
        print(f"\nQuestion: {q}")
        response = ai.ask(q)
        print(f"IA: {response}")
        print(f"Longueur: {len(response)} chars")

if __name__ == "__main__":
    test_ai()
