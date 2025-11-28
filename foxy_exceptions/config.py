from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class NotifierConfig:
    endpoint_url: str
    dedupe_ttl: int = 60
    retry_attempts: int = 3
    retry_delay: float = 0.5
    max_queue_size: int = 1000
    http_headers: Optional[Dict[str, str]] = None
    timeout: float = 5.0
    enabled: bool = True
    enrich_payload: bool = True
    project: Optional[str] = None
    environment: Optional[str] = None

    def enriched(self, payload: dict) -> dict:
        if not self.enrich_payload:
            return payload

        extra = {}

        if self.project:
            extra["project"] = self.project
        if self.environment:
            extra["environment"] = self.environment

        return {**payload, **extra}
