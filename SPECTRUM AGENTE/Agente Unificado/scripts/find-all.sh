#!/bin/bash
# Busca una keyword en TODOS los workflows del folder Agente Unificado.
# Muestra: archivo → nodo → tipo para cada coincidencia.
# Uso: ./scripts/find-all.sh <keyword>

KEYWORD="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKFLOWS_DIR="$(dirname "$SCRIPT_DIR")"

if [[ -z "$KEYWORD" ]]; then
  echo "Uso: $0 <keyword>" >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: jq no está instalado. Ejecuta: brew install jq" >&2
  exit 1
fi

echo "Buscando '$KEYWORD' en todos los workflows..."
echo "══════════════════════════════════════════════════════"

TOTAL=0
for FILE in "$WORKFLOWS_DIR"/*.json; do
  NAME=$(basename "$FILE")
  MATCHES=$(jq -r --arg kw "$KEYWORD" \
    '.nodes[] | select(tostring | ascii_downcase | contains($kw | ascii_downcase)) |
     [.name, (.type | split(".") | last)] | @tsv' \
    "$FILE" 2>/dev/null)

  if [[ -n "$MATCHES" ]]; then
    echo ""
    echo "📄 $NAME"
    echo "$MATCHES" | while IFS=$'\t' read -r node_name node_type; do
      printf "   %-40s [%s]\n" "$node_name" "$node_type"
      ((TOTAL++)) 2>/dev/null || true
    done
  fi
done

echo ""
echo "══════════════════════════════════════════════════════"
echo "Búsqueda completada."
