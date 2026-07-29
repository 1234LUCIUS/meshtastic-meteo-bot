"""
Consignes d'urgence statiques ultra-compactes (<200 chars).
Sources: Sécurité Civile / Ministère de l'Intérieur.
"""

EMERGENCY_GUIDELINES = {
    "inondation": (
        "🌊 INONDATION:\n"
        "1.Suivre Radio/Vigicrues\n"
        "2.Couper gaz/élec\n"
        "3.Monter en hauteur\n"
        "4.Pas de voiture/sous-sol\n"
        "5.Ne pas aller chercher enfants école\n"
        "📞112"
    ),
    "tempete": (
        "🌪️ TEMPÊTE:\n"
        "1.Rester à l'abri (dur)\n"
        "2.Fermer portes/fenêtres\n"
        "3.Éviter déplacements/forêts\n"
        "4.Fixer objets ext.\n"
        "5.Pas toucher fils élec tombés\n"
        "📞112"
    ),
    "incendie": (
        "🔥 FEU FORÊT:\n"
        "1.Appeler 18/112\n"
        "2.S'éloigner du feu\n"
        "3.Respirer via linge humide\n"
        "4.Maison: fermer volets/fenêtres\n"
        "5.Suivre ordres évacuation\n"
        "📞18"
    ),
    "canicule": (
        "☀️ CANICULE:\n"
        "1.Boire eau régulièrement\n"
        "2.Mouiller corps/ventiler\n"
        "3.Manger assez/Pas d'alcool\n"
        "4.Maison au frais (volets clos)\n"
        "5.Aider les aînés\n"
        "📞15"
    ),
    "seisme": (
        "🫨 SÉISME:\n"
        "1.Dedans: sous table solide\n"
        "2.Dehors: loin édifices/ponts\n"
        "3.Auto: s'arrêter loin arbres\n"
        "4.Après: couper gaz/élec\n"
        "5.Évacuer prudemment\n"
        "📞112"
    ),
    "numeros": (
        "☎️ URGENCES:\n"
        "•112: Urgence Europ.\n"
        "•18: Pompiers\n"
        "•15: SAMU\n"
        "•17: Police/Gend.\n"
        "•114: SMS Urgence\n"
        "•3624: SOS Médecins"
    )
}

def get_emergency_help() -> str:
    """Liste des thèmes."""
    t = ", ".join(EMERGENCY_GUIDELINES.keys())
    return f"🛡️ AIDE HORS-LIGNE:\nTapez !urgence <thème>\n{t}"[:199]

def get_guideline(theme: str) -> str:
    """Consignes par thème."""
    return EMERGENCY_GUIDELINES.get(theme.lower().strip(), get_emergency_help())
