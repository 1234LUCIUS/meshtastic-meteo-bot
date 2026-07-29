
from services.emergency_guidelines import EMERGENCY_GUIDELINES

print("--- VÉRIFICATION LONGUEUR CONSIGNES ---")
for theme, text in EMERGENCY_GUIDELINES.items():
    length = len(text)
    print(f"Thème: {theme:12} | Longueur: {length:3} chars | {'✅ OK' if length <= 200 else '❌ TROP LONG'}")
    if length > 200:
        print(f"  > {text}")
