#!/bin/bash
# Busca nodos que contengan una keyword en sus parámetros o nombre.
# Útil para localizar dónde se usa una expresión, campo o valor específico.
# Uso: ./scripts/search-nodes.sh <archivo.json> <keyword>
# Ejemplos:
#   ./scripts/search-nodes.sh "AGENT PRINCIPAL.json" "consulta_pendiente"
#   ./scripts/search-nodes.sh "AGENT PRINCIPAL.json" "transferir_agente"
#   ./scripts/search-nodes.sh "Lead Collector.json" "tel_sistema"

FILE="$1"
KEYWORD="$2"

if [[ -z "$FILE" || -z "$KEYWORD" ]]; then
  echo "Uso: $0 <archivo.json> <keyword>" >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: jq no está instalado. Ejecuta: brew install jq" >&2
  exit 1
fi

echo "Buscando '$KEYWORD' en: $FILE"
echo "─────────────────────────────────────────────────────────"

MATCHES=$(jq -r --arg kw "$KEYWORD" \
  '.nodes[] | select(tostring | ascii_downcase | contains($kw | ascii_downcase)) | .name' \
  "$FILE")

if [[ -z "$MATCHES" ]]; then
  echo "Sin resultados para '$KEYWORD'."
  exit 0
fi

echo "$MATCHES" | while read -r name; do
  TYPE=$(jq -r --arg n "$name" '.nodes[] | select(.name == $n) | .type | split(".") | last' "$FILE")
  printf "  %-45s [%s]\n" "$name" "$TYPE"
done

echo "─────────────────────────────────────────────────────────"
COUNT=$(echo "$MATCHES" | wc -l | tr -d ' ')
echo "Encontrados: $COUNT nodos"
