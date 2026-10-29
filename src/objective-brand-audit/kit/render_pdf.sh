#!/usr/bin/env bash
# Print <audit>/outputs/<output_name>.html to an A4 PDF with headless Chrome (local file only, never the live site).
# Usage: bash render_pdf.sh <audit-dir>
# Chrome: $CHROME if set, else Google Chrome on macOS, else google-chrome / chromium on the PATH.
set -euo pipefail
AUDIT="$(cd "${1:?usage: bash render_pdf.sh <audit-dir>}" && pwd)"
NAME="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["output_name"])' "$AUDIT/audit.json")"
IN="$AUDIT/outputs/$NAME.html"
OUT="$AUDIT/outputs/$NAME.pdf"
[[ -f "$IN" ]] || { echo "render_pdf: missing $IN (run build_report.py first)"; exit 1; }
CHROME="${CHROME:-}"
if [[ -z "$CHROME" ]]; then
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" google-chrome google-chrome-stable chromium; do
    if [[ -x "$c" ]] || command -v "$c" >/dev/null 2>&1; then CHROME="$c"; break; fi
  done
fi
[[ -n "$CHROME" ]] || { echo "render_pdf: no Chrome found; set CHROME to its path"; exit 1; }
PROFILE="$(mktemp -d)"
rm -f "$OUT"
"$CHROME" --headless=new --disable-gpu --no-first-run \
  --user-data-dir="$PROFILE" --no-pdf-header-footer --virtual-time-budget=8000 \
  --print-to-pdf="$OUT" "file://$IN" >/dev/null 2>&1 &
PID=$!
for _ in $(seq 1 60); do
  sleep 1
  if [[ -s "$OUT" ]] && ! lsof "$OUT" >/dev/null 2>&1; then break; fi
done
kill "$PID" 2>/dev/null || true
sleep 1; rm -rf "$PROFILE" 2>/dev/null || true
[[ -s "$OUT" ]] || { echo "render_pdf: no PDF written"; exit 1; }
ls -la "$OUT"
pdfinfo "$OUT" 2>/dev/null | grep -E "^Pages" || true
