#!/usr/bin/env python3
"""Publikations-Schritt: nimmt Gate-bestandene Artikel in redaktion/live.txt auf, baut dist/ nur aus Live-Artikeln
(interne Links auf nicht-live Artikel werden entlinkt), schreibt Laufbericht. Mit --check <url>: HTTP-200-Pruefung."""
import datetime, glob, json, os, re, shutil, subprocess, sys, tempfile, urllib.request
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = f"{P}/redaktion/live.txt"
live = [l for l in open(LIVE, encoding="utf-8").read().split("\n") if l] if os.path.exists(LIVE) else []
if len(sys.argv) > 2 and sys.argv[1] == "--check":
    base, fehler = sys.argv[2].rstrip("/"), 0
    for s in [""] + live:
        try: c = urllib.request.urlopen(urllib.request.Request(f"{base}/{s}", headers={"User-Agent": "Mozilla/5.0"}), timeout=20).status
        except Exception as e: c = getattr(e, "code", type(e).__name__)
        print(c, f"{base}/{s}"); fehler += c != 200
    open(f"{P}/redaktion/publish.log", "a").write(f"{datetime.datetime.now():%Y-%m-%d %H:%M} {base} seiten={len(live)+1} fehler={fehler}\n")
    sys.exit(1 if fehler else 0)
neu, zurueck, kosten = [], [], 0.0
for g in sorted(glob.glob(f"{P}/runs/*/gate.json")):
    d = json.load(open(g, encoding="utf-8"))
    if d.get("datum") != str(datetime.date.today()) and d["slug"] in live: continue
    kosten += d.get("kosten_usd") or 0
    if d.get("bestanden") and d["slug"] not in live and os.path.exists(f"{P}/articles/{d['slug']}.html"):
        live.append(d["slug"]); neu.append(d)
        open(f"{P}/redaktion/erledigt.txt", "a").write(d["query"] + "\n")
    elif not d.get("bestanden"): zurueck.append(d)
open(LIVE, "w").write("\n".join(live) + "\n")
tmp = tempfile.mkdtemp(); os.makedirs(f"{tmp}/articles"); os.makedirs(f"{tmp}/site")
for s in live:
    t = open(f"{P}/articles/{s}.html", encoding="utf-8").read()
    t = re.sub(r'<a href="(\d\d-[^"#/]+)\.html(#[^"]*)?">(.*?)</a>', lambda m: m.group(0) if m.group(1) in live else m.group(3), t, flags=re.S)
    open(f"{tmp}/articles/{s}.html", "w", encoding="utf-8").write(t)
shutil.copy(f"{P}/build.py", tmp); subprocess.run([sys.executable, f"{tmp}/build.py"], check=True)
if os.path.exists(f"{P}/dist"): shutil.rmtree(f"{P}/dist")
shutil.copytree(f"{tmp}/site", f"{P}/dist")
os.makedirs(f"{P}/redaktion/laeufe", exist_ok=True)
z = lambda d: f"| {d['slug']} | QA {d.get('qa_score')} | Gegencheck {d.get('gegencheck_score')} | falsch {d.get('fakten_falsch')} | Legal {d.get('legal_mittel_hoch')} | tote Links {len(d.get('links_tot', []))} | {d.get('kosten_usd')} USD |"
bericht = f"# Redaktionslauf {datetime.datetime.now():%Y-%m-%d %H:%M} UTC\n\nNeu live: {len(neu)} · zurückgestellt: {len(zurueck)} · live gesamt: {len(live)} · KI-Kosten: {kosten:.3f} USD\n\n## Live\n" + "\n".join(z(d) for d in neu) + "\n\n## Zurückgestellt (nächster Lauf neu)\n" + "\n".join(z(d) for d in zurueck) + "\n"
open(f"{P}/redaktion/laeufe/{datetime.datetime.now():%Y-%m-%d-%H%M}-lauf.md", "w").write(bericht)
open(f"{P}/redaktion/status.md", "w").write(bericht)
print(bericht)
