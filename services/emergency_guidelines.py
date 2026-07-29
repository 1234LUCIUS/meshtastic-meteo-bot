"""
Module de consignes d'urgence statiques (accessibles hors-ligne).
"""

EMERGENCY_GUIDELINES = {
    "inondation": (
        "🌊 INONDATION :\n"
        "1. Coupez gaz/élec.\n"
        "2. Montez aux étages.\n"
        "3. Ne prenez pas votre voiture.\n"
        "4. Écoutez la radio (France Bleu).\n"
        "📞 Urgence : 112 ou 18"
    ),
    "tempête": (
        "🌪️ TEMPÊTE / VENT :\n"
        "1. Restez à l'abri.\n"
        "2. Rangez les objets exposés.\n"
        "3. Ne touchez pas aux fils tombés.\n"
        "4. Évitez les zones boisées.\n"
        "📞 Urgence : 112"
    ),
    "incendie": (
        "🔥 INCENDIE :\n"
        "1. Évacuez vers zone dégagée.\n"
        "2. Fermez portes/fenêtres.\n"
        "3. Arrosez les abords (si possible).\n"
        "4. Suivez les ordres des Pompiers.\n"
        "📞 Pompiers : 18"
    ),
    "canicule": (
        "☀️ CANICULE :\n"
        "1. Buvez de l'eau (1.5L).\n"
        "2. Restez au frais.\n"
        "3. Fermez volets le jour.\n"
        "4. Prenez des nouvelles des aînés.\n"
        "📞 SOS Médecins : 3624"
    ),
    "numeros": (
        "☎️ NUMÉROS D'URGENCE :\n"
        "• 112 : Urgence Européenne\n"
        "• 15 : SAMU\n"
        "• 17 : Gendarmerie/Police\n"
        "• 18 : Pompiers\n"
        "• 114 : SMS (Sourd/Malent.)"
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
