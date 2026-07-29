"""
Service de stockage local (SQLite) pour la résilience hors-ligne.
Permet de mettre en cache les dernières données connues.
"""

import sqlite3
import json
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "bot_cache.db")

class StorageService:
    def __init__(self):
        # Créer le dossier data s'il n'existe pas
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialise la base de données et les tables."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    timestamp DATETIME
                )
            """)
            conn.commit()

    def save(self, key: str, value: any):
        """Sauvegarde une valeur dans le cache."""
        try:
            serialized_value = json.dumps(value)
            now = datetime.now().isoformat()
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO cache (key, value, timestamp) VALUES (?, ?, ?)",
                    (key, serialized_value, now)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Erreur sauvegarde cache ({key}): {e}")

    def get(self, key: str) -> tuple:
        """Récupère une valeur et son timestamp depuis le cache."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value, timestamp FROM cache WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0]), datetime.fromisoformat(row[1])
        except Exception as e:
            logger.error(f"Erreur lecture cache ({key}): {e}")
        return None, None

    def get_formatted_age(self, timestamp: datetime) -> str:
        """Retourne l'âge de la donnée de façon lisible."""
        if not timestamp: return "Inconnu"
        diff = datetime.now() - timestamp
        minutes = int(diff.total_seconds() / 60)
        if minutes < 60:
            return f"{minutes}m"
        hours = minutes // 60
        if hours < 24:
            return f"{hours}h"
        return f"{hours // 24}j"
