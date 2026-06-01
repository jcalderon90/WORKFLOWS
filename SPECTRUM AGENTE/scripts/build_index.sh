#!/usr/bin/env bash
# build_index.sh — Regenera el inventario de nodos por workflow dentro de INDEX.md.
# Reemplaza el bloque entre los marcadores AUTO-NODES. El resto del INDEX.md (escrito
# a mano) no se toca. Requiere: jq.
#
# Uso:  ./scripts/build_index.sh          (desde la raíz del repo)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WF_DIR="$ROOT/Agente Unificado"
INDEX="$ROOT/INDEX.md"
BEGIN="<!-- BEGIN AUTO-NODES -->"
END="<!-- END AUTO-NODES -->"

command -v jq >/dev/null || { echo "ERROR: jq no está instalado"; exit 1; }
[ -f "$INDEX" ] || { echo "ERROR: no existe $INDEX"; exit 1; }

gen_block() {
  echo "$BEGIN"
  echo "<!-- Generado por scripts/build_index.sh — NO editar a mano -->"
  echo ""
  for f in "$WF_DIR"/*.json; do
    name="$(basename "$f")"
    n="$(jq -r '.nodes | length' "$f" 2>/dev/null || echo '?')"
    echo "#### $name ($n nodos)"
    jq -r '[.nodes[].name] | join(" · ")' "$f" 2>/dev/null || echo "(no parseable)"
    echo ""
  done
  echo "$END"
}

b_line="$(grep -n -F "$BEGIN" "$INDEX" | head -1 | cut -d: -f1)"
e_line="$(grep -n -F "$END" "$INDEX" | head -1 | cut -d: -f1)"
if [ -z "$b_line" ] || [ -z "$e_line" ]; then
  echo "ERROR: no se encontraron los marcadores AUTO-NODES en INDEX.md"; exit 1
fi

TMP="$(mktemp)"
head -n "$((b_line - 1))" "$INDEX" > "$TMP"   # todo antes del marcador BEGIN
gen_block >> "$TMP"                            # bloque regenerado (incluye BEGIN/END)
tail -n "+$((e_line + 1))" "$INDEX" >> "$TMP"  # todo después del marcador END
mv "$TMP" "$INDEX"
echo "✅ INDEX.md actualizado ($(date '+%Y-%m-%d %H:%M'))"
