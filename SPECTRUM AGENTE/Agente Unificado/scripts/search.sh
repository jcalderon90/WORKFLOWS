#!/bin/bash
# Búsqueda unificada: conceptos curados + nodos de todos los workflows + docs.
# Pensado para consulta rápida por modelos de IA con salida compacta.
# Uso: ./scripts/search.sh <término>
# Ejemplos:
#   ./scripts/search.sh fase_2
#   ./scripts/search.sh "proyecto_interes"
#   ./scripts/search.sh soap
#   ./scripts/search.sh rsvp

KEYWORD="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKFLOWS_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(dirname "$WORKFLOWS_DIR")"
CONCEPTS_FILE="$SCRIPT_DIR/concepts.json"

if [[ -z "$KEYWORD" ]]; then
  echo "Uso: $0 <término>" >&2
  echo "Busca en: conceptos curados, nodos de workflows, docs/" >&2
  exit 1
fi

KW_LOWER=$(echo "$KEYWORD" | tr '[:upper:]' '[:lower:]')

echo "🔍 Buscando: '$KEYWORD'"
echo "══════════════════════════════════════════════════════"

# ── 1. CONCEPTOS CURADOS ──────────────────────────────────
if [[ -f "$CONCEPTS_FILE" ]] && command -v jq &>/dev/null; then
  CONCEPT_MATCHES=$(jq -r --arg kw "$KW_LOWER" '
    .concepts[] |
    select(
      (.id | ascii_downcase | contains($kw)) or
      (.titulo | ascii_downcase | contains($kw)) or
      (.descripcion | ascii_downcase | contains($kw)) or
      ((.campos_clave // []) | map(ascii_downcase) | any(contains($kw))) or
      ((.colecciones // {}) | to_entries[] | .key | ascii_downcase | contains($kw))
    ) |
    "CONCEPTO: \(.titulo)\n  \(.descripcion[0:200])...\n  Workflows: \([ (.workflows // [])[] | "\(.archivo) → \(.nodos | join(", "))" ] | join(" | "))\n  Docs: \((.docs // []) | join(", "))"
  ' "$CONCEPTS_FILE" 2>/dev/null)

  if [[ -n "$CONCEPT_MATCHES" ]]; then
    echo ""
    echo "── Conceptos ─────────────────────────────────────────"
    echo "$CONCEPT_MATCHES"
  fi
fi

# ── 2. NODOS EN WORKFLOWS ─────────────────────────────────
NODE_FOUND=false
for FILE in "$WORKFLOWS_DIR"/*.json; do
  WNAME=$(basename "$FILE")
  MATCHES=$(jq -r --arg kw "$KW_LOWER" \
    '.nodes[] | select(tostring | ascii_downcase | contains($kw)) |
     [.name, (.type | split(".") | last)] | @tsv' \
    "$FILE" 2>/dev/null)

  if [[ -n "$MATCHES" ]]; then
    if ! $NODE_FOUND; then
      echo ""
      echo "── Nodos en workflows ────────────────────────────────"
      NODE_FOUND=true
    fi
    echo "📄 $WNAME"
    echo "$MATCHES" | while IFS=$'\t' read -r node_name node_type; do
      printf "   %-42s [%s]\n" "$node_name" "$node_type"
    done
  fi
done

# ── 3. DOCS ───────────────────────────────────────────────
DOCS_DIR="$REPO_ROOT/docs"
if [[ -d "$DOCS_DIR" ]]; then
  DOC_MATCHES=$(grep -ril "$KEYWORD" "$DOCS_DIR" 2>/dev/null)
  if [[ -n "$DOC_MATCHES" ]]; then
    echo ""
    echo "── Documentos ────────────────────────────────────────"
    while IFS= read -r doc; do
      DNAME=$(basename "$doc")
      LINES=$(grep -in "$KEYWORD" "$doc" | head -3 | sed 's/^/   /')
      echo "📝 $DNAME"
      echo "$LINES"
    done <<< "$DOC_MATCHES"
  fi
fi

# ── 4. KBs ────────────────────────────────────────────────
KBS_DIR="$REPO_ROOT/KBs"
if [[ -d "$KBS_DIR" ]]; then
  KB_MATCHES=$(grep -ril "$KEYWORD" "$KBS_DIR" 2>/dev/null)
  if [[ -n "$KB_MATCHES" ]]; then
    echo ""
    echo "── Knowledge Bases ───────────────────────────────────"
    while IFS= read -r kb; do
      echo "📚 $(basename "$kb")"
    done <<< "$KB_MATCHES"
  fi
fi

echo ""
echo "══════════════════════════════════════════════════════"
