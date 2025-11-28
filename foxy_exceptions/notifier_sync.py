import threading
import queue
import time
import traceback
from typing import Optional

from .config import NotifierConfig
from .dedupe import ErrorDedupe
from .http_client import SyncHTTPClient
from .logger import logger


class SyncErrorNotifier:
    _SENTINEL = object()

    def __init__(self, config: NotifierConfig):
        self.config = config

        self.queue = queue.Queue(maxsize=config.max_queue_size)
        self.dedupe = ErrorDedupe(ttl=config.dedupe_ttl)
        self.http = SyncHTTPClient(
            timeout=config.timeout,
            headers=config.http_headers,
        )

        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._running = False

    def start(self):
        if not self._running:
            self._running = True
            self._thread.start()
            logger.debug("ErrorNotifierSync worker thread started")

    def stop(self, timeout: float = 2.0):
        if not self._running:
            return

        self._running = False
        self.queue.put(self._SENTINEL)

        self._thread.join(timeout)
        if self._thread.is_alive():
            logger.warning("ErrorNotifierSync: thread did not exit in time")

        logger.debug("ErrorNotifierSync worker thread stopped")

    def notify(self, source: str, exc: Exception, meta: Optional[dict] = None):
        if not self.config.enabled:
            return

        text = f"{exc.__class__.__name__}: {exc}"

        if not self.dedupe.should_send(text):
            return

        payload = {
            "source": source,
            "error": text,
            "traceback": "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
            "meta": meta,
        }

        enriched = self.config.enriched(payload)

        try:
            self.queue.put_nowait(enriched)
        except queue.Full:
            logger.warning("ErrorNotifierSync queue overflow — dropping error")

    def _worker(self):
        while True:
            payload = self.queue.get()

            if payload is self._SENTINEL:
                break

            try:
                self._send_with_retry(payload)
            except Exception as e:
                logger.exception(f"Unhandled in sync worker: {e}")

    def _send_with_retry(self, payload: dict):
        logger.debug(f"[sync] Sending error payload to {self.config.endpoint_url}")

        for attempt in range(1, self.config.retry_attempts + 1):
            ok = self.http.post_json(self.config.endpoint_url, payload)

            if ok:
                return

            logger.warning(f"[sync] Send failed (attempt {attempt})")
            time.sleep(self.config.retry_delay)

        logger.error("[sync] Failed to send error after all retry attempts")
