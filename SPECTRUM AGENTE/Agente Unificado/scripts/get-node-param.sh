#!/bin/bash
# Extrae un parámetro de un nodo n8n. Busca en .parameters y .parameters.options.*
# Uso: ./scripts/get-node-param.sh <archivo.json> <nombre-nodo> <parametro>
# Ejemplos:
#   ./scripts/get-node-param.sh "AGENT PRINCIPAL.json" "PRINCIPAL" "systemMessage"
#   ./scripts/get-node-param.sh "AGENT PRINCIPAL.json" "PRINCIPAL" "text"
#   ./scripts/get-node-param.sh "AGENT PRINCIPAL.json" "Hay Cambios?" "jsCode"

FILE="$1"
NODE="$2"
PARAM="$3"

if [[ -z "$FILE" || -z "$NODE" || -z "$PARAM" ]]; then
  echo "Uso: $0 <archivo.json> <nombre-nodo> <parametro>" >&2
  echo "Parámetros comunes: systemMessage, text, jsCode, assignments, conditions, query, jsonBody" >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: jq no está instalado. Ejecuta: brew install jq" >&2
  exit 1
fi

# 1. Busca en .parameters directamente
RESULT=$(jq --arg name "$NODE" --arg param "$PARAM" \
  '.nodes[] | select(.name == $name) | .parameters[$param]' "$FILE" 2>/dev/null)

# 2. Si no, busca en .parameters.options.*
if [[ -z "$RESULT" || "$RESULT" == "null" ]]; then
  RESULT=$(jq --arg name "$NODE" --arg param "$PARAM" \
    '.nodes[] | select(.name == $name) | .parameters.options[$param]' "$FILE" 2>/dev/null)
fi

# 3. Si no, búsqueda profunda en cualquier nivel de .parameters
if [[ -z "$RESULT" || "$RESULT" == "null" ]]; then
  RESULT=$(jq --arg name "$NODE" --arg param "$PARAM" \
    '.nodes[] | select(.name == $name) | .parameters | .. | objects | .[$param] | select(. != null)' \
    "$FILE" 2>/dev/null | head -1)
fi

if [[ -z "$RESULT" || "$RESULT" == "null" ]]; then
  echo "Parámetro '$PARAM' no encontrado en '$NODE'." >&2
  echo "Parámetros disponibles:" >&2
  jq --arg name "$NODE" \
    '.nodes[] | select(.name == $name) | .parameters | to_entries[] | "  \(.key)" , (.value | if type == "object" then "    options: \(keys)" else empty end)' \
    "$FILE" 2>/dev/null >&2
  exit 1
fi

echo "$RESULT"
