#!/usr/bin/env bash
# Automatisches Publizieren: build.py, oeffentliche Seiten nach dist/, Deploy auf Cloudflare Workers, HTTP-200-Pruefung.
# Laeuft nur, wenn redaktion/LIVE existiert (einmaliger Go-Live-Schalter).
set -euo pipefail
P="$(cd "$(dirname "$0")/.." && pwd)"; cd "$P"
source "$HOME/.env" 2>/dev/null || true
export PATH="/home/linuxbrew/.linuxbrew/bin:$HOME/bin:/usr/local/bin:/usr/bin:/bin"
[ -f redaktion/LIVE ] || { echo "publish: redaktion/LIVE fehlt, kein Deploy"; exit 0; }
N=$(hostname | grep -oE '[0-9]+$'); NAME="d${N}-treppenlift-magazin"
python3 build.py
mkdir -p dist && find dist -type f -name '*.html' -exec gio trash {} +
cp site/index.html dist/
for f in articles/[0-9][0-9]-*.html; do cp "site/$(basename "$f")" dist/; done
npx -y wrangler@4 deploy --name "$NAME" --assets ./dist --compatibility-date 2026-10-01
U="https://$NAME.nichtagentur.workers.dev"; FEHLER=0
for f in dist/*.html; do s=$(basename "$f" .html); [ "$s" = index ] && s=""
  c=$(curl -s -o /dev/null -w '%{http_code}' -L "$U/$s"); echo "$c $U/$s"; [ "$c" = 200 ] || FEHLER=1; done
echo "$(date -Is) deploy $U fehler=$FEHLER" >> redaktion/publish.log
exit $FEHLER
