"""Client MeshCore — pont synchrone vers l'API asynchrone meshcore."""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from typing import Callable, Optional

try:
    from meshcore import EventType, MeshCore

    MESHCORE_AVAILABLE = True
except ImportError:  # pragma: no cover - dépendance optionnelle
    EventType = None
    MeshCore = None
    MESHCORE_AVAILABLE = False

from bot.config import (
    ALERT_CHANNEL,
    BROADCAST_CHANNEL,
    MESHCORE_BAUDRATE,
    MESHCORE_BLE_ADDRESS,
    MESHCORE_BLE_PIN,
    MESHCORE_CONNECTION_TYPE,
    MESHCORE_TCP_HOST,
    MESHCORE_TCP_PORT,
    MESHCORE_SERIAL_PORT,
)

logger = logging.getLogger(__name__)


class MeshCoreClient:
    """Expose la même interface utile que :class:`MeshtasticClient`.

    MeshCore repose sur asyncio alors que le bot actuel et son planificateur
    sont synchrones. Un event loop dédié est donc exécuté dans un thread afin
    de ne pas imposer une réécriture du contrôleur.
    """

    def __init__(self, on_message: Optional[Callable] = None, simulation_mode: bool = False):
        self.meshcore = None
        self.on_message_callback = on_message
        self.simulation_mode = simulation_mode
        self.connected = False
        self.broadcast_channel = BROADCAST_CHANNEL
        self.local_telemetry = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._ready = threading.Event()
        self._subscriptions = []

    def connect(self) -> bool:
        if self.simulation_mode:
            logger.warning("Mode simulation MeshCore activé — aucun matériel requis.")
            self.connected = True
            return True
        if not MESHCORE_AVAILABLE:
            logger.error("La bibliothèque 'meshcore' n'est pas installée.")
            return False

        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="MeshCoreLoop")
        self._thread.start()
        if not self._ready.wait(timeout=30):
            logger.error("Délai dépassé lors du démarrage de la boucle MeshCore.")
            return False
        try:
            return bool(self._submit(self._connect_async).result(timeout=30))
        except Exception as exc:
            logger.error("Échec de la connexion MeshCore : %s", exc)
            return False

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._ready.set()
        self._loop.run_forever()
        pending = asyncio.all_tasks(self._loop)
        for task in pending:
            task.cancel()
        if pending:
            self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        self._loop.close()

    async def _connect_async(self) -> bool:
        try:
            if MESHCORE_CONNECTION_TYPE == "tcp":
                self.meshcore = await MeshCore.create_tcp(
                    MESHCORE_TCP_HOST, MESHCORE_TCP_PORT, auto_reconnect=True
                )
            elif MESHCORE_CONNECTION_TYPE == "ble":
                self.meshcore = await MeshCore.create_ble(
                    MESHCORE_BLE_ADDRESS or None,
                    pin=MESHCORE_BLE_PIN or None,
                    auto_reconnect=True,
                )
            else:
                self.meshcore = await MeshCore.create_serial(
                    MESHCORE_SERIAL_PORT,
                    MESHCORE_BAUDRATE,
                    auto_reconnect=True,
                )

            if self.meshcore is None:
                return False

            self._subscriptions.append(
                self.meshcore.subscribe(EventType.CHANNEL_MSG_RECV, self._on_channel_message)
            )
            await self.meshcore.start_auto_message_fetching()
            self.connected = True
            logger.info("Connexion MeshCore établie avec succès (%s).", MESHCORE_CONNECTION_TYPE)
            return True
        except Exception:
            logger.exception("Échec de l'initialisation MeshCore")
            self.connected = False
            return False

    def _submit(self, coroutine_factory, *args):
        if not self._loop or not self._loop.is_running():
            raise RuntimeError("La boucle MeshCore n'est pas active")
        return asyncio.run_coroutine_threadsafe(coroutine_factory(*args), self._loop)

    async def _on_channel_message(self, event):
        data = event.payload or {}
        text = str(data.get("text", "")).strip()
        if not text or not self.on_message_callback:
            return
        sender = data.get("pubkey_prefix", "unknown")
        packet = {
            "fromId": sender,
            "channel": data.get("channel_idx"),
            "meshcore": True,
            "payload": data,
        }
        try:
            self.on_message_callback(sender, text, packet)
        except Exception:
            logger.exception("Erreur dans le callback de message MeshCore")

    def send_text(
        self,
        text: str,
        destination: str = "^all",
        channel_index: Optional[int] = None,
        want_ack: bool = False,
    ) -> bool:
        if self.simulation_mode:
            logger.info("[SIMULATION MESHCORE] %s", text)
            return True
        if not self.connected or not self.meshcore:
            return False
        channel = channel_index if channel_index is not None else self.broadcast_channel
        try:
            return bool(self._submit(self._send_text_async, text, channel).result(timeout=30))
        except Exception as exc:
            logger.error("Erreur d'envoi MeshCore : %s", exc)
            return False

    async def _send_text_async(self, text: str, channel: int) -> bool:
        for part in self._split_message(text):
            result = await self.meshcore.commands.send_chan_msg(channel, part)
            if result.type == EventType.ERROR:
                logger.error("MeshCore a refusé le message : %s", result.payload)
                return False
        return True

    def send_alert(self, text: str, destination: str = "^all") -> bool:
        return self.send_text(text, channel_index=ALERT_CHANNEL)

    def disconnect(self):
        if self.simulation_mode:
            self.connected = False
            return
        if not self._loop or not self._loop.is_running():
            self.connected = False
            return
        try:
            self._submit(self._disconnect_async).result(timeout=10)
        except Exception as exc:
            logger.warning("Erreur lors de la fermeture MeshCore : %s", exc)
        finally:
            self.connected = False
            self._loop.call_soon_threadsafe(self._loop.stop)
            if self._thread and self._thread is not threading.current_thread():
                self._thread.join(timeout=10)

    async def _disconnect_async(self):
        if self.meshcore:
            try:
                await self.meshcore.stop_auto_message_fetching()
            except Exception:
                logger.debug("Arrêt de la récupération automatique MeshCore impossible", exc_info=True)
            await self.meshcore.disconnect()
        self.meshcore = None

    def get_local_node_info(self) -> dict:
        return {"id": "!simulation", "latitude": 48.8566, "longitude": 2.3522} if self.simulation_mode else {}

    @staticmethod
    def _split_message(text: str, max_length: int = 200) -> list[str]:
        if len(text.encode("utf-8")) <= max_length:
            return [text]
        parts, current = [], ""
        for word in text.split():
            if len(word.encode("utf-8")) > max_length - 8:
                if current:
                    parts.append(current)
                    current = ""
                chunk = ""
                for character in word:
                    candidate = chunk + character
                    if len(candidate.encode("utf-8")) <= max_length - 8:
                        chunk = candidate
                    else:
                        parts.append(chunk)
                        chunk = character
                if chunk:
                    parts.append(chunk)
                continue
            candidate = f"{current} {word}".strip()
            if len(candidate.encode("utf-8")) <= max_length - 8:
                current = candidate
            else:
                if current:
                    parts.append(current)
                current = word
        if current:
            parts.append(current)
        total = len(parts)
        return [f"({i}/{total}) {part}" for i, part in enumerate(parts, 1)]
