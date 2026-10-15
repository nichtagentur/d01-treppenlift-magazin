#!/usr/bin/env python3
"""Fuegt articles/NN-slug.html (Fragmente) zu site/index.html (alle auf einer Seite) und site/NN-slug.html zusammen."""
import glob, os, re, html
P = os.path.dirname(os.path.abspath(__file__))
CSS = """body{font-family:system-ui,sans-serif;max-width:820px;margin:0 auto;padding:16px;line-height:1.6;color:#222;background:#fff}
h1{font-size:1.8em;line-height:1.25}h2{margin-top:1.6em}article{border-top:4px solid #c00;margin-top:3em;padding-top:1em}
table{border-collapse:collapse;width:100%;font-size:.95em}td,th{border:1px solid #ccc;padding:6px;text-align:left;vertical-align:top}
.meta{color:#666;font-size:.9em}.box{background:#f4f4f4;padding:12px 16px;border-left:4px solid #c00}nav li{margin:4px 0}
.top{font-size:.85em}
figure.hero{margin:0 0 1em}figure.hero img{width:100%;height:auto;border-radius:4px}figcaption{font-size:.8em;color:#666}"""
def page(title, body):
    return f'<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>'
files = sorted(glob.glob(f"{P}/articles/[0-9][0-9]-*.html"))
toc, parts = [], []
for f in files:
    frag = open(f, encoding="utf-8").read()
    slug = os.path.basename(f)[:-5]
    m = re.search(r"<h1[^>]*>(.*?)</h1>", frag, re.S)
    t = re.sub("<[^>]+>", "", m.group(1)).strip() if m else slug
    toc.append(f'<li><a href="#{slug}">{html.escape(t)}</a> <span class="meta">(<a href="{slug}.html">Einzelseite</a>)</span></li>')
    parts.append(f'<article id="{slug}">{frag}<p class="top"><a href="#top">nach oben</a></p></article>')
    open(f"{P}/site/{slug}.html", "w", encoding="utf-8").write(page(t, f'<p class="top"><a href="index.html">Alle Artikel</a></p><article>{frag}</article>'))
intro = '<header id="top"><h1>Treppenlift-Magazin für Tischler und Schreiner</h1><p class="meta">Fachmagazin für Tischler und Schreiner, die Treppenlifte verkaufen und montieren. Betrieben von Lehner Lifttechnik, vollautomatisch von einer KI-Redaktion erstellt und geprüft.</p><nav><ol>' + "".join(toc) + "</ol></nav></header>"
open(f"{P}/site/index.html", "w", encoding="utf-8").write(page("Treppenlift-Magazin", intro + "".join(parts)))
print(len(files), "Artikel gebaut")
