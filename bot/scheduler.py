"""
Planificateur de tâches — Gère les diffusions périodiques et le reporting d'alertes.

Tâches planifiées :
  - Vérification des alertes Météo-France toutes les N minutes.
  - Diffusion météo de routine toutes les N heures.
  - Reporting horaire si une alerte grave est en cours.
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Optional

import schedule

from bot.config import (
    METEO_BROADCAST_INTERVAL,
    ALERT_CHECK_INTERVAL,
    ALERT_REPORT_INTERVAL,
    ALERT_TRIGGER_LEVEL,
    VIGILANCE_LEVELS,
    NORMANDIE_DEPTS,
    ENABLE_NORMANDIE_ALERTS,
    BROADCAST_CHANNEL,
    ALERT_CHANNEL
)

logger = logging.getLogger(__name__)


class AlertState:
    """Représente l'état d'une alerte active."""

    def __init__(self, level: int, phenomena: list, department: str, summary: str):
        self.level = level
        self.phenomena = phenomena
        self.department = department
        self.summary = summary
        self.started_at = datetime.now()
        self.last_reported_at: Optional[datetime] = None
        self.report_count = 0

    @property
    def duration_str(self) -> str:
        delta = datetime.now() - self.started_at
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        if hours > 0:
            return f"{hours}h{minutes:02d}min"
        return f"{minutes} min"

    def __repr__(self):
        return (
            f"AlertState(dept={self.department}, level={self.level}, "
            f"phenomena={self.phenomena}, started={self.started_at})"
        )


class BotScheduler:
    """
    Planificateur principal du bot.
    Gère les tâches périodiques et le suivi des alertes actives.
    """

    def __init__(self, bot_controller):
        """
        :param bot_controller: Instance du BotController.
        """
        self.controller = bot_controller
        self.active_alerts: dict[str, AlertState] = {}  # dept -> AlertState
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Démarre le planificateur dans un thread dédié."""
        if self._running:
            logger.warning("Le planificateur est déjà en cours d'exécution.")
            return

        self._setup_jobs()
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="BotScheduler")
        self._thread.start()
        logger.info("Planificateur démarré.")

    def stop(self):
        """Arrête le planificateur."""
        self._running = False
        schedule.clear()
        # On n'attend pas le thread pour éviter de bloquer l'arrêt sur Windows
        logger.info("Planificateur arrêté.")

    def _setup_jobs(self):
        """Configure les tâches planifiées."""
        schedule.clear()

        # Vérification des alertes
        schedule.every(ALERT_CHECK_INTERVAL).minutes.do(self._job_check_alerts)

        # Diffusion météo de routine
        schedule.every(METEO_BROADCAST_INTERVAL).minutes.do(self._job_broadcast_weather)

        # Reporting des alertes actives (vérifié toutes les minutes)
        schedule.every(1).minutes.do(self._job_report_active_alerts)

        logger.info(
            f"Tâches planifiées : alertes toutes les {ALERT_CHECK_INTERVAL} min, "
            f"météo toutes les {METEO_BROADCAST_INTERVAL} min, "
            f"reporting alertes actives toutes les {ALERT_REPORT_INTERVAL} min."
        )

    def _run_loop(self):
        """Boucle principale du planificateur."""
        # Exécuter immédiatement au démarrage
        self._job_check_alerts()
        self._job_broadcast_weather()

        while self._running:
            try:
                schedule.run_pending()
            except Exception as e:
                logger.error(f"Erreur dans la boucle du planificateur : {e}")
            time.sleep(30)

    # -------------------------------------------------------------------------
    # Jobs planifiés
    # -------------------------------------------------------------------------

    def _job_check_alerts(self):
        """Vérifie les nouvelles alertes (Météo, Normandie, Feux, Préfectures)."""
        logger.debug("Vérification globale des alertes...")
        try:
            # 1. Alertes Météo-France Nationales
            alerts = self.controller.fetch_all_vigilance_alerts()
            
            # Traitement des alertes pour la Normandie
            if ENABLE_NORMANDIE_ALERTS:
                normandie_alerts = [a for a in alerts if a.get("department") in NORMANDIE_DEPTS]
                self._process_alerts(normandie_alerts, prefix="[NORMANDIE] ")

            # 2. Alertes Locales
            from bot.config import DEFAULT_DEPARTMENT
            local_alerts = [a for a in alerts if a.get("department") == DEFAULT_DEPARTMENT]
            self._process_alerts(local_alerts)

            # 3. Vérification des Feux de Forêt en Normandie
            if ENABLE_NORMANDIE_ALERTS:
                for dept in NORMANDIE_DEPTS:
                    self._check_forest_fire_alert(dept)

            # 4. Vérification des actualités Préfectures / SDIS / Web Officiel
            if ENABLE_NORMANDIE_ALERTS:
                self._check_official_news_alerts()
                self._check_sdis_urgent_alerts()

        except Exception as e:
            logger.error(f"Erreur lors de la vérification des alertes : {e}")

    def _check_official_news_alerts(self):
        """Vérifie les actualités officielles et diffuse si alerte détectée."""
        try:
            news_summary = self.controller.get_normandie_web_summary()
            # Si le résumé contient des mots-clés d'alerte, on diffuse
            keywords = ["ALERTE", "DANGER", "RESTRICTION", "INTERDICTION", "EVACUATION", "FR-ALERT"]
            if any(k in news_summary.upper() for k in keywords):
                logger.warning("Information critique détectée sur le web officiel Normandie.")
                # Formatage ultra-court
                alert_msg = f"🏛️ INFO OFFICIELLE\n{news_summary[:150]}..."
                self.controller.client.send_text(alert_msg)
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des infos web : {e}")

    def _check_sdis_urgent_alerts(self):
        """Vérifie les alertes urgentes des SDIS."""
        try:
            urgent_alerts = self.controller.official_web_service.check_for_urgent_alerts()
            for alert in urgent_alerts:
                logger.warning(f"Alerte SDIS détectée : {alert}")
                self.controller.client.send_text(alert)
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des alertes SDIS : {e}")

    def _check_forest_fire_alert(self, dept: str):
        """Vérifie le risque d'incendie pour un département."""
        mdf_data = self.controller.meteo_forets_service.get_forest_fire_danger(dept)
        if mdf_data and mdf_data.get("level", 1) >= ALERT_TRIGGER_LEVEL:
            alert_id = f"MDF_{dept}"
            if alert_id not in self.active_alerts:
                level_info = self.controller.meteo_forets_service.MDF_LEVELS.get(mdf_data["level"])
                message = (
                    f"🔥 ALERTE INCENDIE [NORMANDIE] — Dept {dept}\n"
                    f"Danger : {level_info['name']}\n"
                    f"Risque élevé détecté. Prudence extrême.\n"
                    f"Source: Météo-France (Météo des Forêts)"
                )
                self.controller.client.send_alert(message)
                # On ajoute à active_alerts pour éviter les doublons
                self.active_alerts[alert_id] = AlertState(
                    mdf_data["level"], ["Incendie"], dept, "Danger d'incendie élevé"
                )

    def _job_broadcast_weather(self):
        """Diffuse la météo de routine sur le canal principal."""
        logger.info("Diffusion météo de routine...")
        try:
            weather_msg = self.controller.get_weather_default()
            logger.info(f"Message météo généré : {weather_msg[:50]}...")
            
            success = self.controller.client.send_text(weather_msg, channel_index=BROADCAST_CHANNEL)
            if success:
                logger.info("Message météo envoyé avec succès sur le réseau.")
            else:
                logger.error("Échec de l'envoi du message météo sur le réseau.")
                
        except Exception as e:
            logger.error(f"Erreur lors de la diffusion météo : {e}")

    def _job_report_active_alerts(self):
        """Envoie un rapport horaire pour chaque alerte grave active."""
        now = datetime.now()
        for dept, alert in list(self.active_alerts.items()):
            if alert.level < ALERT_TRIGGER_LEVEL:
                continue

            should_report = (
                alert.last_reported_at is None
                or (now - alert.last_reported_at) >= timedelta(minutes=ALERT_REPORT_INTERVAL)
            )

            if should_report:
                self._send_alert_report(dept, alert)
                alert.last_reported_at = now
                alert.report_count += 1

    # -------------------------------------------------------------------------
    # Gestion des alertes
    # -------------------------------------------------------------------------

    def _process_alerts(self, alerts: list, prefix: str = ""):
        """
        Compare les nouvelles alertes avec l'état actuel.
        Déclenche les notifications pour les nouvelles alertes ou les changements de niveau.
        """
        current_depts = set()

        for alert_data in alerts:
            dept = alert_data.get("department")
            level = alert_data.get("max_level", 1)
            phenomena = alert_data.get("phenomena", [])
            summary = alert_data.get("summary", "")

            if not dept or level < ALERT_TRIGGER_LEVEL:
                # Lever l'alerte si elle était active
                if dept in self.active_alerts:
                    self._send_alert_lifted(dept, self.active_alerts[dept])
                    del self.active_alerts[dept]
                continue

            current_depts.add(dept)

            if dept not in self.active_alerts:
                # Nouvelle alerte
                state = AlertState(level, phenomena, dept, summary)
                self.active_alerts[dept] = state
                self._send_new_alert(dept, state, prefix=prefix)
            else:
                existing = self.active_alerts[dept]
                if level != existing.level or set(phenomena) != set(existing.phenomena):
                    # Mise à jour de l'alerte
                    existing.level = level
                    existing.phenomena = phenomena
                    existing.summary = summary
                    self._send_alert_update(dept, existing, prefix=prefix)

        # Lever les alertes qui ne sont plus présentes
        for dept in list(self.active_alerts.keys()):
            if dept not in current_depts:
                self._send_alert_lifted(dept, self.active_alerts[dept])
                del self.active_alerts[dept]

    def _send_new_alert(self, dept: str, alert: AlertState, prefix: str = ""):
        """Envoie une notification de nouvelle alerte."""
        level_info = VIGILANCE_LEVELS.get(alert.level, VIGILANCE_LEVELS[3])
        phenomena_str = ", ".join(alert.phenomena) if alert.phenomena else "Phénomène non précisé"

        message = (
            f"🚨 {prefix}ALERTE MÉTÉO — VIGILANCE {level_info['name']}\n"
            f"Dept: {dept}\n"
            f"Phénomène(s): {phenomena_str}\n"
            f"{alert.summary}\n"
            f"Source: vigilance.meteofrance.fr\n"
            f"⚠️ Suivez les consignes de sécurité."
        )
        logger.warning(f"Nouvelle alerte {level_info['name']} pour {dept}: {phenomena_str}")
        self.controller.client.send_alert(message)

    def _send_alert_update(self, dept: str, alert: AlertState, prefix: str = ""):
        """Envoie une notification de mise à jour d'alerte."""
        level_info = VIGILANCE_LEVELS.get(alert.level, VIGILANCE_LEVELS[3])
        phenomena_str = ", ".join(alert.phenomena) if alert.phenomena else "Non précisé"

        message = (
            f"🔄 {prefix}MAJ ALERTE — VIGILANCE {level_info['name']}\n"
            f"Dept: {dept} | Durée: {alert.duration_str}\n"
            f"Phénomène(s): {phenomena_str}\n"
            f"Source: vigilance.meteofrance.fr"
        )
        logger.warning(f"Mise à jour alerte {dept}: niveau {level_info['name']}")
        self.controller.client.send_alert(message)

    def _send_alert_lifted(self, dept: str, alert: AlertState, prefix: str = ""):
        """Envoie une notification de fin d'alerte."""
        level_info = VIGILANCE_LEVELS.get(alert.level, VIGILANCE_LEVELS[3])
        message = (
            f"✅ {prefix}FIN D'ALERTE — {level_info['name']} levée\n"
            f"Dept: {dept} | Durée totale: {alert.duration_str}\n"
            f"Retour à la normale."
        )
        logger.info(f"Alerte levée pour {dept}")
        self.controller.client.send_alert(message)

    def _send_alert_report(self, dept: str, alert: AlertState, prefix: str = ""):
        """Envoie un rapport horaire pour une alerte active."""
        level_info = VIGILANCE_LEVELS.get(alert.level, VIGILANCE_LEVELS[3])
        phenomena_str = ", ".join(alert.phenomena) if alert.phenomena else "Non précisé"
        now_str = datetime.now().strftime("%H:%M")

        message = (
            f"🔴 {prefix}POINT SITUATION [{now_str}] — ALERTE {level_info['name']}\n"
            f"Dept: {dept} | En cours depuis: {alert.duration_str}\n"
            f"Phénomène(s): {phenomena_str}\n"
            f"{alert.summary}\n"
            f"Prochain point dans {ALERT_REPORT_INTERVAL} min.\n"
            f"vigilance.meteofrance.fr"
        )
        logger.warning(f"Rapport horaire alerte {dept} (rapport #{alert.report_count + 1})")
        self.controller.client.send_alert(message)
