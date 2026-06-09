#!/bin/bash
# Lista todos los nodos de un workflow n8n con nombre y tipo.
# Uso: ./scripts/list-nodes.sh <archivo.json>
# Ejemplo: ./scripts/list-nodes.sh "AGENT PRINCIPAL.json"

FILE="$1"

if [[ -z "$FILE" ]]; then
  echo "Uso: $0 <archivo.json>" >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: jq no está instalado. Ejecuta: brew install jq" >&2
  exit 1
fi

echo "Nodos en: $FILE"
echo "─────────────────────────────────────────────────────────"
printf "%-45s %s\n" "NOMBRE" "TIPO"
echo "─────────────────────────────────────────────────────────"
jq -r '.nodes[] | [.name, (.type | split(".") | last)] | @tsv' "$FILE" \
  | sort \
  | awk -F'\t' '{ printf "%-45s %s\n", $1, $2 }'
echo "─────────────────────────────────────────────────────────"
echo "Total: $(jq '.nodes | length' "$FILE") nodos"
