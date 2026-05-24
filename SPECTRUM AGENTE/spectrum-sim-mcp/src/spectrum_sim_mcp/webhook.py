"""Envío de mensajes al webhook del orquestador Sof-IA.

Construye el payload tipo ManyChat que espera AGENT PRINCIPAL y devuelve la
respuesta sincrónica (el flujo n8n incluye un Wait de ~10s antes de procesar,
por lo que el timeout por defecto es 35s).
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any

import httpx

DEFAULT_PHONE = "+50212345678"


def new_test_user_id() -> str:
    """Genera un manychat_id único con prefijo `test_` (compatible con reset_user)."""
    return f"test_{uuid.uuid4().hex[:8]}"


def build_payload(
    user_id: str,
    text: str,
    *,
    page_id: str,
    canal: str = "WhatsApp",
    proyecto_interes: str = "",
    whatsapp_phone: str = DEFAULT_PHONE,
) -> dict[str, Any]:
    """Construye el payload exacto que ManyChat envía al webhook de Sof-IA."""
    return {
        "key": user_id,
        "body": {
            "id": user_id,
            "page_id": page_id,
            "custom_fields": {
                "canal_ingreso": canal,
                "proyecto_interes": proyecto_interes,
            },
            "last_input_text": text,
            "whatsapp_phone": whatsapp_phone,
        },
    }


async def send_message(
    *,
    webhook_url: str,
    timeout: float,
    user_id: str,
    text: str,
    page_id: str,
    canal: str = "WhatsApp",
    proyecto_interes: str = "",
    whatsapp_phone: str = DEFAULT_PHONE,
) -> dict[str, Any]:
    """Envía un mensaje al webhook y retorna respuesta + telemetría.

    Returns:
        dict con keys: success (bool), status_code (int|None), elapsed_ms (int),
        data (dict|str — JSON parseado si fue posible, raw text si no),
        error (str, sólo si success=False).
    """
    payload = build_payload(
        user_id,
        text,
        page_id=page_id,
        canal=canal,
        proyecto_interes=proyecto_interes,
        whatsapp_phone=whatsapp_phone,
    )
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
        elapsed_ms = int((time.monotonic() - start) * 1000)
        try:
            data: Any = resp.json() if resp.content else {}
        except json.JSONDecodeError:
            data = {"raw": resp.text}
        return {
            "success": resp.is_success,
            "status_code": resp.status_code,
            "elapsed_ms": elapsed_ms,
            "data": data,
        }
    except httpx.TimeoutException as e:
        return {
            "success": False,
            "status_code": None,
            "elapsed_ms": int((time.monotonic() - start) * 1000),
            "error": f"timeout tras {timeout}s: {e}",
        }
    except httpx.HTTPError as e:
        return {
            "success": False,
            "status_code": None,
            "elapsed_ms": int((time.monotonic() - start) * 1000),
            "error": f"{type(e).__name__}: {e}",
        }
