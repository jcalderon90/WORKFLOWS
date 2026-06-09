#!/bin/bash
# Extrae un nodo de un workflow n8n por nombre exacto.
# Uso: ./scripts/get-node.sh [--slim] <archivo.json> <nombre-nodo>
# --slim: omite position, id, typeVersion, credentials (salida compacta)

SLIM=false
if [[ "$1" == "--slim" ]]; then
  SLIM=true
  shift
fi

FILE="$1"
NODE="$2"

if [[ -z "$FILE" || -z "$NODE" ]]; then
  echo "Uso: $0 [--slim] <archivo.json> <nombre-nodo>" >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: jq no está instalado. Ejecuta: brew install jq" >&2
  exit 1
fi

RESULT=$(jq --arg name "$NODE" '.nodes[] | select(.name == $name)' "$FILE")

if [[ -z "$RESULT" ]]; then
  echo "Nodo '$NODE' no encontrado en '$FILE'." >&2
  echo "Nodos disponibles:" >&2
  jq -r '.nodes[].name' "$FILE" | sort >&2
  exit 1
fi

if $SLIM; then
  echo "$RESULT" | jq 'del(.position, .id, .typeVersion, .credentials, .retryOnFail, .alwaysOutputData, .onError)'
else
  echo "$RESULT"
fi
