#!/usr/bin/env python3
"""Chefredakteur-KI, Planungsschritt: waehlt Themen und vergibt Nummern. Ausgabe fuer GITHUB_OUTPUT: topics=<json>.
Aufruf: python3 pipeline/plan.py "<query1;query2>" <anzahl>"""
import glob, json, os, re, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
wunsch = [q.strip() for q in (sys.argv[1] if len(sys.argv) > 1 else "").split(";") if q.strip()]
n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] else 4
cp = open(f"{P}/redaktion/contentplan.md", encoding="utf-8").read()
erledigt = set(open(f"{P}/redaktion/erledigt.txt", encoding="utf-8").read().split("\n")) if os.path.exists(f"{P}/redaktion/erledigt.txt") else set()
personas = {}
for zeile in cp.splitlines():
    c = [x.strip() for x in zeile.strip("|").split("|")]
    if len(c) == 4 and c[0][:1].isdigit(): personas[c[1].split("(")[0].strip().lower()] = c[3]
if not wunsch:
    for zeile in cp.splitlines():
        c = [x.strip() for x in zeile.strip("|").split("|")]
        if len(c) >= 6 and c[4] == "1":
            q = re.split(r"\s*[/(]", c[0])[0].strip()
            if q not in erledigt: wunsch.append(q)
nums = [int(os.path.basename(f)[:2]) for f in glob.glob(f"{P}/articles*/[0-9][0-9]-*.html")]
nn = max(nums + [11]) + 1
out = []
for q in wunsch[:n]:
    persona = next((v for k, v in personas.items() if k and (k in q.lower() or q.lower() in k)), "Fachredakteur für Treppenlift-Montage")
    out.append({"query": q, "nn": f"{nn:02d}", "persona": persona}); nn += 1
print("topics=" + json.dumps(out, ensure_ascii=False))
