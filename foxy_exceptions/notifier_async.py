import asyncio
import traceback
from typing import Optional, Any

from .base_notifier import BaseNotifier
from .config import NotifierConfig
from .dedupe import ErrorDedupe
from .http_client import AsyncHTTPClient
from .logger import logger


class AsyncErrorNotifier(BaseNotifier):
    _SENTINEL = object()

    def __init__(self, config: NotifierConfig):
        self.config = config
        self.queue = asyncio.Queue(maxsize=config.max_queue_size)
        self.dedupe = ErrorDedupe(ttl=config.dedupe_ttl)
        self.http = AsyncHTTPClient(timeout=config.timeout, headers=config.http_headers)
        self._worker_task: Optional[asyncio.Task] = None

    def start(self):
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())
            logger.debug("AsyncErrorNotifier worker started")

    async def stop(self, timeout: float = 2.0):
        if not self._worker_task:
            return

        await self.queue.put(self._SENTINEL)

        try:
            await asyncio.wait_for(self._worker_task, timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning("AsyncErrorNotifier stop timeout — cancelling worker")
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

        logger.debug("AsyncErrorNotifier worker stopped")

    async def notify(self, source: Any, exc: Exception, meta: Optional[dict] = None):
        if not self.config.enabled:
            return

        src = self._normalize_source(source)
        text = f"{exc.__class__.__name__}: {exc}"

        if not self.dedupe.should_send(text):
            logger.debug(f"Dedupe: skip repeated error: {text}")
            return

        payload = {
            "source": src,
            "error": text,
            "traceback": "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
            "meta": meta,
        }

        enriched = self.config.enriched(payload)

        try:
            self.queue.put_nowait(enriched)
        except asyncio.QueueFull:
            logger.warning("AsyncErrorNotifier queue overflow — dropping error")

    async def _worker(self):
        while True:
            payload = await self.queue.get()
            if payload is self._SENTINEL:
                break

            try:
                await self._send_with_retry(payload)
            except Exception as e:
                logger.exception(f"Unhandled in worker: {e}")

    async def _send_with_retry(self, payload: dict):
        logger.debug(f"Sending error payload to {self.config.endpoint_url}")

        for attempt in range(1, self.config.retry_attempts + 1):
            ok = await self.http.post_json(self.config.endpoint_url, payload)

            if ok:
                return

            logger.warning(f"Send failed (attempt {attempt}). Retrying...")
            await asyncio.sleep(self.config.retry_delay)

        logger.error("Failed to send error after all retry attempts")
