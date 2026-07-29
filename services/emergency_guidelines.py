"""
Module de consignes d'urgence statiques (accessibles hors-ligne).
"""

EMERGENCY_GUIDELINES = {
    "inondation": (
        "🌊 INONDATION (Séc. Civile):\n"
        "1. Informez-vous (Radio/Vigicrues)\n"
        "2. Coupez gaz/élec\n"
        "3. Montez en hauteur\n"
        "4. N'utilisez pas votre voiture\n"
        "5. Ne descendez pas en sous-sol"
    ),
    "tempete": (
        "🌪️ TEMPÊTE (Séc. Civile):\n"
        "1. Restez à l'abri (bâtiment dur)\n"
        "2. Fermez/Verrouillez portes/fenêtres\n"
        "3. Évitez déplacements/zones boisées\n"
        "4. Fixez objets extérieurs\n"
        "5. Ne touchez pas fils électriques"
    ),
    "incendie": (
        "🔥 FEU DE FORÊT (Séc. Civile):\n"
        "1. Témoin? Appelez le 18 ou 112\n"
        "2. Éloignez-vous du feu\n"
        "3. Respirez à travers linge humide\n"
        "4. Maison? Fermez volets/fenêtres\n"
        "5. Suivez consignes d'évacuation"
    ),
    "canicule": (
        "☀️ CANICULE (Santé Publique):\n"
        "1. Buvez régulièrement (eau)\n"
        "2. Mouillez-vous le corps\n"
        "3. Mangez en quantité suffisante\n"
        "4. Pas d'alcool\n"
        "5. Maintenez maison au frais"
    ),
    "seisme": (
        "🫨 SÉISME (Séc. Civile):\n"
        "1. Intérieur? Abritez-vous sous table\n"
        "2. Extérieur? Éloignez-vous édifices\n"
        "3. Voiture? Arrêtez-vous loin ponts\n"
        "4. Après? Coupez gaz/élec\n"
        "5. Évacuez prudemment"
    ),
    "numeros": (
        "☎️ URGENCES :\n"
        "• 112 : Urgence Européenne\n"
        "• 18 : Pompiers\n"
        "• 15 : SAMU\n"
        "• 17 : Police/Gend.\n"
        "• 114 : SMS (Urgence)"
    )
}

def get_emergency_help() -> str:
    """Retourne la liste des thèmes disponibles."""
    themes = ", ".join(EMERGENCY_GUIDELINES.keys())
    return f"🛡️ URGENCES (HORS-LIGNE):\nTapez !urgence <thème>\nThèmes: {themes}"

def get_guideline(theme: str) -> str:
    """Retourne les consignes pour un thème donné."""
    theme = theme.lower().strip()
    return EMERGENCY_GUIDELINES.get(theme, get_emergency_help())
