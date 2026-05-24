"""Cliente para la API pública de n8n.

Documentación: https://docs.n8n.io/api/api-reference/

Header de autenticación: `X-N8N-API-KEY`.
"""

from __future__ import annotations

from typing import Any

import httpx


class N8nApiError(RuntimeError):
    """Error devuelto por la API n8n (no-2xx)."""

    def __init__(self, status: int, body: str):
        super().__init__(f"n8n API {status}: {body[:300]}")
        self.status = status
        self.body = body


class N8nClient:
    def __init__(self, base_url: str, api_key: str, *, timeout: float = 30.0):
        self._base = base_url.rstrip("/")
        self._headers = {
            "X-N8N-API-KEY": api_key,
            "Accept": "application/json",
        }
        self._timeout = timeout

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self._base}/api/v1{path}"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(url, headers=self._headers, params=params or {})
        if not resp.is_success:
            raise N8nApiError(resp.status_code, resp.text)
        return resp.json()

    async def list_workflows(self, *, active: bool | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if active is not None:
            params["active"] = "true" if active else "false"
        data = await self._get("/workflows", params=params)
        return data.get("data", [])

    async def list_executions(
        self,
        *,
        workflow_id: str | None = None,
        status: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
        include_data: bool = False,
    ) -> dict[str, Any]:
        """Lista ejecuciones. `status` ∈ {error, success, waiting} (opcional).

        Returns el dict crudo de la API: { data: [...], nextCursor: "..." }.
        Nota: la API no soporta filtrar por user_id directamente — eso se hace
        en el lado del MCP server inspeccionando el payload del primer nodo.
        """
        params: dict[str, Any] = {"limit": min(max(limit, 1), 250)}
        if workflow_id:
            params["workflowId"] = workflow_id
        if status:
            params["status"] = status
        if cursor:
            params["cursor"] = cursor
        if include_data:
            params["includeData"] = "true"
        return await self._get("/executions", params=params)

    async def get_execution(self, execution_id: str, *, include_data: bool = True) -> dict[str, Any]:
        """Trae el detalle de una ejecución, opcionalmente con data nodo-por-nodo."""
        params = {"includeData": "true" if include_data else "false"}
        return await self._get(f"/executions/{execution_id}", params=params)
