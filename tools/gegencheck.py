#!/usr/bin/env python3
"""Gegencheck + Ueberarbeitung eines finalen Artikels durch ein zweites Modell (OpenRouter).
Aufruf: python3 tools/gegencheck.py runs/<NN>-<slug> [modell]
Liest 07-final.html, 03-dossier.md, 04-produkte.md; schreibt 09-gegencheck.md und 09-gegencheck.html."""
import json, os, sys, urllib.request, urllib.error
run = sys.argv[1]
model = sys.argv[2] if len(sys.argv) > 2 else "google/gemini-4-argon"
rd = lambda n: open(os.path.join(run, n), encoding="utf-8").read()
prompt = f"""Du bist unabhaengiger Gegenpruefer (zweites Modell) fuer ein B2B-Fachmagazin: Zielgruppe Tischler/Schreiner in Deutschland, die Treppenlifte verkaufen und montieren. Betreiber des Magazins ist Lehner Lifttechnik (oesterreichischer Hersteller). YMYL-Thema (Recht, Geld, Sicherheit), Google Quality Rater Guidelines.

Aufgabe:
1. Pruefe den Artikel gegen Dossier und Produktfakten: falsche oder unbelegte Aussagen, Rechtsgewissheit wo es Einzelfall ist, Widersprueche, unklare Stellen fuer Tischler, schwacher Nutzen.
2. Ueberarbeite den Artikel: nur Verbesserungen, die belegt sind. KEINE neuen Zahlen, Namen, Normen oder Quellen erfinden. Links, Struktur (H1, H2, FAQ, Quellen) und HTML-Format beibehalten. Lehner bleibt "Betreiber dieses Magazins", nie "Partner der Tischler". Kein Autorenname erfinden.

Antwortformat genau so:
===BEFUNDE===
(nummerierte Liste: Zitat -> Problem -> Aenderung; am Ende Score 0-100 nach QRG)
===HTML===
(das komplette ueberarbeitete HTML-Fragment, ohne Codeblock-Zaeune)

--- DOSSIER ---
{rd('03-dossier.md')}
--- PRODUKTFAKTEN ---
{rd('04-produkte.md')}
--- ARTIKEL (07-final.html) ---
{rd('07-final.html')}"""
def call(key):
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}]}).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=600))
try:
    r = call(os.environ["OPENROUTER_API_KEY"])
except urllib.error.HTTPError as e:
    if e.code not in (401, 402): raise
    print(f"Eigener Key: HTTP {e.code}, falle auf Backup-Key zurueck")
    r = call(os.environ["OPENROUTER_BACKUP_API_KEY"])
txt = r["choices"][0]["message"]["content"]
bef, _, htm = txt.partition("===HTML===")
open(os.path.join(run, "09-gegencheck.md"), "w", encoding="utf-8").write(f"# Gegencheck {model}\n\n" + bef.replace("===BEFUNDE===", "").strip() + "\n")
htm = htm.strip().removeprefix("```html").removeprefix("```").removesuffix("```").strip()
open(os.path.join(run, "09-gegencheck.html"), "w", encoding="utf-8").write(htm + "\n")
u = r.get("usage", {})
print(f"Modell {r.get('model')} | Tokens in {u.get('prompt_tokens')} out {u.get('completion_tokens')} | Kosten USD {u.get('cost')}")
