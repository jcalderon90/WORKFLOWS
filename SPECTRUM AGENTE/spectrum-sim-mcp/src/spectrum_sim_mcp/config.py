"""Carga y valida la configuración del servidor desde variables de entorno (.env)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _find_env() -> Path | None:
    """Busca .env subiendo desde el cwd y desde el archivo del servidor."""
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent.parent / ".env",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def _load_env() -> None:
    env_path = _find_env()
    if env_path is not None:
        load_dotenv(env_path)


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Falta variable de entorno requerida: {name}. "
            f"Copia .env.example a .env y llena los valores."
        )
    return value


def _optional(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip() or default


@dataclass(frozen=True)
class Config:
    n8n_base_url: str
    n8n_webhook_url: str
    n8n_api_key: str
    mongo_uri: str  # vacío = tools de Mongo deshabilitadas
    mongo_db: str
    default_page_id: str
    webhook_timeout: float
    allow_reset: bool

    @property
    def mongo_enabled(self) -> bool:
        return bool(self.mongo_uri)

    @classmethod
    def load(cls) -> "Config":
        _load_env()
        return cls(
            n8n_base_url=_required("N8N_BASE_URL").rstrip("/"),
            n8n_webhook_url=_required("N8N_WEBHOOK_URL"),
            n8n_api_key=_required("N8N_API_KEY"),
            mongo_uri=_optional("MONGO_URI"),
            mongo_db=_optional("MONGO_DB", "Centralizado"),
            default_page_id=_optional("DEFAULT_PAGE_ID", "page_spectrum_test"),
            webhook_timeout=float(_optional("WEBHOOK_TIMEOUT", "35")),
            allow_reset=_optional("MONGO_ALLOW_RESET", "false").lower() == "true",
        )


WORKFLOW_IDS: dict[str, str] = {
    "AGENT PRINCIPAL": "iXaptKTUXaXrP7aF",
    "Sync_CRM": "TTVNRX38pPoPmK2X",
    "Lead Collector": "SHPFhvoal7k1Rqf9",
    "KB SEARCH": "D3LKuNi6CmMIdvzg",
    "RSVP": "TjFPzHs5aimxILH7",
    "Send Media": "NtTiyrNy2LHimE7u",
    "Notifications Master": "r1Jf5vwrkBrT4dEu",
    "Vectorizar los KBs": "LLiVnT0M6xvDKive",
}
