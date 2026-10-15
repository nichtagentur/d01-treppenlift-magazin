#!/usr/bin/env bash
# Prüft alle Links in einer HTML-Datei per GET (nicht HEAD: manche Server liefern bei HEAD 405).
# 403 = oft Bot-Sperre, nicht automatisch tot -> im Browser gegenprüfen.
f="$1"; [ -f "$f" ] || { echo "usage: $0 datei.html"; exit 1; }
grep -oE 'href="https?://[^"]+"' "$f" | sed 's/href="//;s/"$//' | sort -u | while read -r u; do
  c=$(curl -s -o /dev/null -L --max-time 20 -A "Mozilla/5.0 (X11; Linux x86_64) Chrome/130" -w '%{http_code}' "$u")
  case "$c" in 2*) s=OK;; 403) s=PRUEFEN;; *) s=TOT;; esac
  printf '%s\t%s\t%s\n' "$s" "$c" "$u"
done
