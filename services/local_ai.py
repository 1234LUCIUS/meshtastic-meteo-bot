"""
Service d'IA locale hors-ligne pour Meshtastic Météo Bot.
Utilise llama-cpp-python pour l'inférence locale.
"""

import logging
import os
from llama_cpp import Llama
from services.storage import StorageService

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")

class LocalAIService:
    def __init__(self):
        self.llm = None
        self.storage = StorageService()
        self._load_model()

    def _load_model(self):
        """Charge le modèle en mémoire."""
        try:
            if os.path.exists(MODEL_PATH):
                logger.info(f"Chargement du modèle IA local : {MODEL_PATH}")
                self.llm = Llama(
                    model_path=MODEL_PATH,
                    n_ctx=512,
                    n_threads=4,
                    verbose=False
                )
            else:
                logger.error(f"Modèle introuvable à l'emplacement : {MODEL_PATH}")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle LLM : {e}")

    def ask(self, question: str) -> str:
        """Pose une question à l'IA locale."""
        if not self.llm:
            return "❌ IA locale indisponible (modèle non chargé)."

        context = self._build_context()
        
        # Prompt amélioré pour forcer le français et la brièveté
        prompt = (
            f"<|system|>\nTu es un assistant météo et sécurité pour Meshtastic en Normandie. "
            f"Réponds TOUJOURS en FRANÇAIS. Réponse TRÈS COURTE (max 150 caractères). "
            f"Données actuelles: {context}</s>\n"
            f"<|user|>\n{question}</s>\n"
            f"<|assistant|>\n"
        )

        try:
            output = self.llm(
                prompt,
                max_tokens=60,
                temperature=0.3, # Réduit pour plus de cohérence
                stop=["</s>", "<|user|>", "\n"],
                echo=False
            )
            response = output["choices"][0]["text"].strip()
            
            # Si la réponse est vide ou bizarre, on donne une réponse par défaut
            if not response or len(response) < 2:
                return "Je n'ai pas pu générer de réponse. Réessayez."
                
            return response[:199]
        except Exception as e:
            logger.error(f"Erreur lors de l'inférence IA : {e}")
            return "❌ Erreur de traitement IA."

    def _build_context(self) -> str:
        """Construit un résumé des données actuelles."""
        summary = []
        try:
            from bot.config import DEFAULT_LATITUDE, DEFAULT_LONGITUDE, DEFAULT_DEPARTMENT
            m_data, _ = self.storage.get(f"meteo_{round(DEFAULT_LATITUDE, 2)}_{round(DEFAULT_LONGITUDE, 2)}")
            if m_data:
                curr = m_data.get("current", {})
                summary.append(f"Météo: {curr.get('temperature_2m')}°C, {curr.get('description')}.")
            
            v_data, _ = self.storage.get(f"vigilance_{DEFAULT_DEPARTMENT}")
            if v_data:
                summary.append(f"Vigilance Dept {DEFAULT_DEPARTMENT}: Niveau {v_data.get('max_level')}.")
        except:
            pass
            
        return " ".join(summary) if summary else "Données météo non disponibles."
