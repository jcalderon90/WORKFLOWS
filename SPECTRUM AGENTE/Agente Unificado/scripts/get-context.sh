#!/bin/bash
# Muestra un nodo y sus conexiones de entrada/salida en una sola llamada.
# Útil para entender el flujo alrededor de un nodo sin múltiples consultas.
# Uso: ./scripts/get-context.sh <archivo.json> <nombre-nodo>

FILE="$1"
NODE="$2"

if [[ -z "$FILE" || -z "$NODE" ]]; then
  echo "Uso: $0 <archivo.json> <nombre-nodo>" >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: jq no está instalado. Ejecuta: brew install jq" >&2
  exit 1
fi

# Verificar que el nodo existe
EXISTS=$(jq --arg name "$NODE" '.nodes[] | select(.name == $name) | .name' "$FILE" 2>/dev/null)
if [[ -z "$EXISTS" ]]; then
  echo "Nodo '$NODE' no encontrado en '$FILE'." >&2
  jq -r '.nodes[].name' "$FILE" | sort >&2
  exit 1
fi

echo "══════════════════════════════════════════════════════"
echo "NODO: $NODE"
echo "══════════════════════════════════════════════════════"

# Tipo
TYPE=$(jq -r --arg name "$NODE" '.nodes[] | select(.name == $name) | .type | split(".") | last' "$FILE")
echo "Tipo: $TYPE"
echo ""

# Parámetros (slim)
echo "── Parámetros ────────────────────────────────────────"
jq --arg name "$NODE" \
  '.nodes[] | select(.name == $name) | del(.position, .id, .typeVersion, .credentials, .retryOnFail, .alwaysOutputData, .onError, .name, .type) | .parameters' \
  "$FILE"

echo ""
echo "── Entradas (quién conecta a este nodo) ──────────────"
jq -r --arg node "$NODE" '
  .connections | to_entries[] |
  .key as $src |
  (.value.main // [])[][]? |
  select(.node == $node) |
  "  ← \($src)"
' "$FILE" 2>/dev/null | sort -u

echo ""
echo "── Salidas (a quién conecta este nodo) ───────────────"
jq -r --arg node "$NODE" '
  .connections[$node].main[][]? | "  → \(.node) [port \(.index)]"
' "$FILE" 2>/dev/null

echo "══════════════════════════════════════════════════════"
