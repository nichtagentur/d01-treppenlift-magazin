#!/usr/bin/env python3
"""Bildredaktion: Hero-Illustration fuer einen Artikel. Aufruf: python3 pipeline/image.py <slug>
Prompt-Persona -> Bildmodell (OpenRouter) -> Bild-QA (Vision) -> max 3 Versuche, sonst kein Bild."""
import base64, json, os, re, sys, time, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm
from llm import chat, COST, MODEL, _post
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_MODEL = os.environ.get("IMAGE_MODEL") or "google/gemini-3.1-flash-lite-image"
VISION_MODEL = os.environ.get("VISION_MODEL") or "google/gemini-3.8-flash"
FALLBACK = """Stil: ruhige, flache Editorial-Illustration, warme gedeckte Farben, weiche Formen, 16:9, viel Weissraum.
Verboten: Treppenlifte, Plattformlifte, Hublifte, Schienen, Maschinen, Technik, jeder Text, Buchstaben, Zahlen, Logos, Fotorealismus, erkennbare Personengesichter.
Erlaubte Motive: Holz, Werkzeug des Tischlers (Hobel, Zollstock, Stemmeisen), Holzmaserung, leere Treppe als Architektur ohne Technik, Grundriss-Skizzen, Hausfassade, Pflanzen.
QA-Pruefliste: kein Lift/keine Schiene/keine Maschine, kein Text, kein Logo, keine Verzerrungen, passt zum Thema, nur Illustration."""
NEG = "no stairs, no steps, no staircase, no railing, no handrail, no stairlift, no lift, no rail, no diagonal pole along a wall, no machine, no text, no logo"

def briefing():
    f = os.path.join(P, "briefing", "bildsprache.md")
    return open(f, encoding="utf-8").read() if os.path.exists(f) else FALLBACK

def keys():
    return [k for k in (os.environ.get("OPENROUTER_API_KEY"), os.environ.get("OPENROUTER_BACKUP_API_KEY")) if k]

def post(body):
    ks = keys()
    for i in range(3):
        try:
            r = _post(body, ks[0]); break
        except urllib.error.HTTPError as e:
            if e.code in (401, 402) and len(ks) > 1: ks.pop(0); continue
            if i == 2: raise
        except Exception:
            if i == 2: raise
        time.sleep(5 * (i + 1))
    COST["usd"] += (r.get("usage") or {}).get("cost") or 0; COST["calls"] += 1
    return r

def gen_image(prompt):
    r = post({"model": IMAGE_MODEL, "messages": [{"role": "user", "content": prompt}], "modalities": ["image", "text"],
              "image_config": {"aspect_ratio": "16:9"}, "usage": {"include": True}})
    m = r["choices"][0]["message"]
    for im in m.get("images") or []:
        u = (im.get("image_url") or {}).get("url") or ""
        mm = re.match(r"data:image/(\w+);base64,(.*)", u, re.S)
        if mm: return ("jpg" if mm.group(1) == "jpeg" else mm.group(1)), base64.b64decode(mm.group(2)), u
    raise RuntimeError("Antwort ohne Bild")

def qa(data_url, bildprompt):
    t = f"""Du bist Bild-QA der Bildredaktion eines Treppenlift-Fachmagazins. Pruefe das Bild streng gegen diese Pruefliste/Regeln:
{briefing()}
Zusaetzlich zwingend: KEIN Treppenlift, Lift, Schiene, keine Maschine/Technik; KEIN Text, keine Buchstaben/Zahlen; KEIN Logo; keine auffaelligen Verzerrungen; passt zum Auftrag: {bildprompt}
Antworte NUR als JSON: {{"ok": true/false, "gruende": ["konkrete Maengel, leer wenn ok"]}}"""
    r = post({"model": VISION_MODEL, "response_format": {"type": "json_object"}, "usage": {"include": True},
              "messages": [{"role": "user", "content": [{"type": "text", "text": t}, {"type": "image_url", "image_url": {"url": data_url}}]}]})
    return llm.parse_json(r["choices"][0]["message"]["content"] or "{}")

def illustrate(slug, html):
    h1 = re.sub(r"<[^>]+>", "", (re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S) or [0, slug])[1]).strip()
    box = re.search(r'<div class="box">(.*?)</div>', html, re.S)
    kurz = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", box.group(1)))[:600] if box else ""
    log, grund, res = [], [], None
    for versuch in (1, 2, 3):
        p = chat(f"""Du bist Bildredakteur. Schreibe fuer den Artikel einen Bildprompt (Englisch, 2-4 Saetze, nur erlaubte Motive, Stil-Baustein der Bildsprache, 16:9, Hero-Illustration) und einen deutschen alt-Text (max 120 Zeichen, beschreibt die Illustration sachlich).
Der Prompt MUSS enden mit: "{NEG}. Illustration only."
{('Vorheriger Versuch wurde von der Bild-QA abgelehnt, vermeide: ' + '; '.join(grund)) if grund else ''}
Antwort nur JSON: {{"prompt": "...", "alt": "..."}}
--- BILDSPRACHE ---\n{briefing()}\n--- ARTIKEL ---\nH1: {h1}\nKurz gesagt: {kurz}""", as_json=True)
        bp, alt = p["prompt"].strip(), re.sub(r'["<>]', "", p["alt"]).strip()
        if NEG not in bp: bp += f" {NEG}."
        try:
            ext, data, url = gen_image(bp)
            q = qa(url, bp)
        except Exception as e:
            log.append({"versuch": versuch, "fehler": str(e)[:200]}); print("Bildfehler:", e); continue
        log.append({"versuch": versuch, "prompt": bp, "alt": alt, "qa": q}); print(f"Versuch {versuch}: QA {q}")
        if q.get("ok") is True:
            os.makedirs(f"{P}/articles/img", exist_ok=True)
            fn = f"{slug}.{ext}"; open(f"{P}/articles/img/{fn}", "wb").write(data)
            fig = f'<figure class="hero"><img src="img/{fn}" alt="{alt}" width="1200" loading="eager"><figcaption>Illustration (KI-generiert), zeigt kein konkretes Produkt.</figcaption></figure>'
            html = re.sub(r"<figure class=\"hero\">.*?</figure>\n?", "", html, flags=re.S)
            html, n = re.subn(r'(<p class="meta">.*?</p>)', lambda m: m.group(1) + "\n" + fig, html, count=1, flags=re.S)
            if not n: html = fig + "\n" + html
            res = fn; break
        grund = q.get("gruende") or ["QA nicht bestanden"]
    os.makedirs(f"{P}/runs/{slug}", exist_ok=True)
    json.dump({"slug": slug, "bild": res, "versuche": log, "bildmodell": IMAGE_MODEL, "vision_modell": VISION_MODEL,
               "kosten_usd": round(COST["usd"], 4)}, open(f"{P}/runs/{slug}/11-bild.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return html, res

if __name__ == "__main__":
    s = sys.argv[1]; f = f"{P}/articles/{s}.html"
    h = open(f, encoding="utf-8").read()
    h, r = illustrate(s, h)
    if r: open(f, "w", encoding="utf-8").write(h)
    print("Bild:", r or "keines", "Kosten USD", round(COST["usd"], 4))
