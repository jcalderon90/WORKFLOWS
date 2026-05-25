"""Acceso a MongoDB Atlas para observar y limpiar estado de simulación.

Operaciones de lectura: `users`, `appointments`, `chat_histories`, `chat_histories_rsvp`.
Operación de escritura (`reset_test_user`): borra docs de un usuario test_*; está
gated por la flag `MONGO_ALLOW_RESET=true` y rechaza cualquier manychat_id que
no comience con `test_`.
"""

from __future__ import annotations

import dns.resolver
from typing import Any

from pymongo import MongoClient

# Workaround documentado en CLAUDE.md: ECONNREFUSED al resolver SRV de Atlas
# desde algunas redes; forzar DNS de Google evita el bloqueo.
try:
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ["8.8.8.8", "8.8.4.4"]
except Exception:
    # Si dnspython no está disponible o falla, dejamos que pymongo use el resolver del SO.
    pass


TEST_PREFIX = "test_"


class ResetNotAllowedError(RuntimeError):
    """Se intentó borrar pero MONGO_ALLOW_RESET no está activo, o el id no es test_*."""


class MongoStore:
    def __init__(self, uri: str, db_name: str, *, allow_reset: bool = False):
        self._client: MongoClient = MongoClient(uri, serverSelectionTimeoutMS=10_000)
        self._db = self._client[db_name]
        self._allow_reset = allow_reset

    def ping(self) -> bool:
        self._client.admin.command("ping")
        return True

    # ----- lectura -----

    def get_user(self, manychat_id: str, page_id: str | None = None) -> dict[str, Any] | None:
        query: dict[str, Any] = {"manychat_id": manychat_id}
        if page_id:
            query["page_id"] = page_id
        doc = self._db["users"].find_one(query)
        return _stringify_ids(doc)

    def get_appointments(self, manychat_id: str, proyecto: str | None = None) -> list[dict[str, Any]]:
        query: dict[str, Any] = {"manychat_id": manychat_id}
        if proyecto:
            query["proyecto"] = proyecto.upper()
        cursor = self._db["appointments"].find(query).limit(20)
        return [_stringify_ids(d) for d in cursor]

    def get_chat_history(
        self,
        manychat_id: str,
        *,
        kind: str = "main",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Devuelve las últimas N entradas de chat_histories.

        kind: "main" → `chat_histories`, "rsvp" → `chat_histories_rsvp`.
        """
        collection_name = "chat_histories_rsvp" if kind == "rsvp" else "chat_histories"
        cursor = (
            self._db[collection_name]
            .find({"sessionId": manychat_id})
            .sort("_id", -1)
            .limit(max(1, min(limit, 100)))
        )
        return [_stringify_ids(d) for d in cursor]

    # ----- escritura acotada -----

    def reset_test_user(self, manychat_id: str) -> dict[str, int]:
        """Borra docs de un usuario test_* en colecciones de simulación.

        Falla si:
          - MONGO_ALLOW_RESET no está activo, o
          - el manychat_id no comienza con `test_`.
        """
        if not self._allow_reset:
            raise ResetNotAllowedError(
                "MONGO_ALLOW_RESET no está activo. Reinicia el servidor con la flag en .env."
            )
        if not manychat_id.startswith(TEST_PREFIX):
            raise ResetNotAllowedError(
                f"Por seguridad, sólo se permite borrar manychat_id con prefijo '{TEST_PREFIX}'."
            )

        result = {
            "users": self._db["users"].delete_many({"manychat_id": manychat_id}).deleted_count,
            "appointments": self._db["appointments"]
            .delete_many({"manychat_id": manychat_id})
            .deleted_count,
            "chat_histories": self._db["chat_histories"]
            .delete_many({"sessionId": manychat_id})
            .deleted_count,
            "chat_histories_rsvp": self._db["chat_histories_rsvp"]
            .delete_many({"sessionId": manychat_id})
            .deleted_count,
        }
        return result

    def close(self) -> None:
        self._client.close()


def _stringify_ids(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    """Convierte ObjectId a str para que sea serializable en JSON (recursivo)."""
    if doc is None:
        return None

    def _convert(obj: Any) -> Any:
        if obj is None:
            return None
        # ObjectId → str
        if str(type(obj).__name__) == "ObjectId":
            return str(obj)
        # dict → recursivo
        if isinstance(obj, dict):
            return {k: _convert(v) for k, v in obj.items()}
        # list → recursivo
        if isinstance(obj, list):
            return [_convert(item) for item in obj]
        return obj

    return _convert(doc)
