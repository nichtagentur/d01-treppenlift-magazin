#!/usr/bin/env python3
"""Ein Artikel nach PLAYBOOK.md, Schritte 1-10, voll automatisch ueber OpenRouter.
Aufruf: python3 pipeline/run_article.py "<query>" <NN> "<persona>"
Ergebnis: runs/<NN>-<slug>/ (alle Zwischenschritte, gate.json) und articles/<NN>-<slug>.html
oder articles-zurueckgestellt/<NN>-<slug>.html."""
import datetime, glob, html as H, json, os, re, sys, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from llm import chat, COST, MODEL
from linkcheck import check_html, UA

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEGEN = os.environ.get("GEGENCHECK_MODEL", "google/gemini-4-argon")
QUERY, NN, PERSONA = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "Fachredakteur")
HEUTE = datetime.date.today()
MONAT = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"][HEUTE.month - 1] + f" {HEUTE.year}"
rd = lambda p: open(os.path.join(P, p), encoding="utf-8").read()
QRG, TON = rd("briefing/qrg-briefing.md"), rd("briefing/tone-of-voice.md")
LOG = []

def log(s):
    print(s, flush=True); LOG.append(f"- {datetime.datetime.now():%H:%M:%S} {s}")

def fetch(u, n=4000):
    try:
        t = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=20).read().decode("utf-8", "ignore")
        t = re.sub(r"(?s)<(script|style|nav|footer)[^>]*>.*?</\1>", " ", t)
        return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", t)))[:n]
    except Exception as e:
        return f"(nicht abrufbar: {e})"

REGELN = f"""Feste Regeln des Treppenlift-Magazins:
- Betreiber: Lehner Lifttechnik (österreichischer Hersteller, Peuerbach). Lehner nie als Partner von Tischlern darstellen; eigene Produkte sachlich verlinken und als "Betreiber dieses Magazins" kennzeichnen.
- Zielgruppe: Tischler und Schreiner in Deutschland, die Treppenlifte verkaufen und montieren (B2B). Sie-Form, sachlich, kurze Sätze, kein Werbegeschrei.
- YMYL: Recht, Förderung, Sicherheit, Geld. Keine Zahl, Frist, Norm oder Quelle erfinden. Unbelegtes entschärfen ("in der Regel", "Einzelfall, bei Bauaufsicht/Hersteller klären") oder weglassen.
- Pflegekasse "kann" zahlen (§ 40 Abs. 4 SGB XI ist Kann-Leistung). "Antrag vor Auftrag" ist Empfehlung der Verbraucherzentrale, kein Gesetz.
- "Außenbereich" ist im Baurecht ein Fachbegriff (Fläche außerhalb bebauter Ortsteile); für Treppen draußen "im Freien" schreiben.
- Keine Personennamen als Autor erfinden. Stand: {MONAT}."""

FORMAT = f"""HTML-Fragment (kein <html>, kein <body>, keine Code-Zäune), genau diese Struktur:
<h1>…</h1>
<p class="meta">Stand: {MONAT} · Redaktion Treppenlift-Magazin, Lehner Lifttechnik (KI-gestützt erstellt und geprüft) · Lesezeit ca. X Min.</p>
<div class="box"><strong>Kurz gesagt:</strong> direkte Antwort in max. 3 Sätzen</div>
<nav><strong>Inhalt</strong><ol><li><a href="#id">…</a></li>…</ol></nav>
<h2 id="…">…</h2> … mindestens eine <table> und eine Checkliste (<ul>) für den Tischler …
<h2>Quellen</h2><ol><li><a href="URL">Titel</a>, abgerufen {MONAT}</li></ol>
<h2>Über diesen Artikel</h2><p>Betreiber Lehner Lifttechnik, mit KI-Unterstützung erstellt und automatisch geprüft, Stand, keine Rechts- oder Steuerberatung.</p>"""

def bestand():
    out = []
    for f in sorted(glob.glob(f"{P}/articles/[0-9][0-9]-*.html")):
        m = re.search(r"<h1[^>]*>(.*?)</h1>", open(f, encoding="utf-8").read(), re.S)
        out.append(f"{os.path.basename(f)}: {re.sub('<[^>]+>', '', m.group(1)).strip() if m else ''}")
    return "\n".join(out)

def autocomplete(q):
    u = "https://suggestqueries.google.com/complete/search?client=firefox&hl=de&gl=de&q=" + urllib.parse.quote(q)
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=15).read().decode("utf-8", "ignore"))[1]
    except Exception: return []

PRODUKTSEITEN = ["plattform-treppenlifte/delta/", "plattform-treppenlifte/omega/", "plattform-treppenlifte/stratos-ng/",
    "sitz-treppenlifte/alpha/", "sitz-treppenlifte/neo/", "vertikale-plattformlifte/sigma/", "vertikale-plattformlifte/elevex/",
    "vertikale-plattformlifte/liftboy-4/", "vertikale-plattformlifte/stepsaver/"]

def review(rolle, auftrag, art, extra=""):
    return chat(f"""Du bist {rolle} des Treppenlift-Magazins. {REGELN}
{auftrag}
Antworte NUR als JSON-Objekt wie angegeben.
{extra}
--- ARTIKEL ---
{art}""", as_json=True)

def reviews(art, dossier, produkte):
    jobs = {
        "qa": lambda: review("QA/QRG-Prüfer (Google Quality Rater Guidelines)", """Bewerte streng nach dem QRG-Briefing (20 Punkte, Stop-Kriterien; der fehlende namentliche Autor ist ein bewusst akzeptiertes Risiko und KEIN Stop-Kriterium, solange die Autorzeile "KI-gestützt" transparent ist).
JSON: {"score": 0-100, "stop": ["offenes Stop-Kriterium", ...], "fehler": [{"zitat": "...", "korrektur": "..."}]}""", art, "--- QRG-BRIEFING ---\n" + QRG),
        "fakten": lambda: review("Faktenprüfer", """Prüfe JEDE Zahl, Frist, Norm und Rechtsaussage gegen das Dossier und die Produktfakten.
JSON: {"falsch": [{"zitat": "...", "korrektur": "..."}], "unbelegt": [{"zitat": "...", "korrektur": "entschärfen oder streichen"}]}""", art, "--- DOSSIER ---\n" + dossier + "\n--- PRODUKTFAKTEN ---\n" + produkte),
        "legal": lambda: review("Legal-Reviewer (deutsches Sozial-, Steuer-, Bau-, Gerätesicherheits-, Werbe- und Haftungsrecht)", """Suche falsche Rechtsgewissheit, fehlende Einzelfall-Hinweise, Heil- oder Garantieversprechen, Irreführung über die Lehner-Beziehung, Haftungsrisiken für Tischler.
JSON: {"punkte": [{"schwere": "hoch|mittel|klein", "zitat": "...", "ersatz": "..."}]}""", art),
        "marke": lambda: review("Marken- und Produktprüfer Lehner Lifttechnik", """Prüfe Ton gegen das Tone-of-Voice-Briefing und jede Lehner-Produktangabe gegen die Produktfakten (bei Widerspruch konservativer Wert + "beim Hersteller bestätigen").
JSON: {"fehler": [{"zitat": "...", "ersatz": "..."}], "an_lehner_melden": ["..."]}""", art, "--- TONE OF VOICE ---\n" + TON + "\n--- PRODUKTFAKTEN ---\n" + produkte),
    }
    with ThreadPoolExecutor(5) as ex:
        fut = {k: ex.submit(f) for k, f in jobs.items()}
        links = ex.submit(check_html, art)
        r = {k: f.result() for k, f in fut.items()}
    r["links"] = [{"url": u, "status": s, "code": str(c)} for u, s, c in links.result()]
    return r

def ersetze(art, r):
    """Konkrete Ersatzformulierungen der Prüfer wörtlich übernehmen (zitat -> ersatz/korrektur), bevor das Modell überarbeitet."""
    n = 0
    for f in r["legal"].get("punkte", []) + r["marke"].get("fehler", []) + r["fakten"].get("falsch", []) + r["qa"].get("fehler", []):
        z, e = (f.get("zitat") or "").strip(), (f.get("ersatz") or f.get("korrektur") or "").strip()
        if len(z) > 15 and e and z in art and "<" not in e: art = art.replace(z, e, 1); n += 1
    return art, n

def gate_status(r, gegen_score=None):
    g = {"qa_score": r["qa"].get("score", 0), "qa_stop": r["qa"].get("stop", []),
         "fakten_falsch": len(r["fakten"].get("falsch", [])),
         "legal_mittel_hoch": len([p for p in r["legal"].get("punkte", []) if p.get("schwere") in ("hoch", "mittel")]),
         "links_tot": [l["url"] for l in r["links"] if l["status"] == "TOT"], "gegencheck_score": gegen_score}
    g["ok_vor_gegencheck"] = g["qa_score"] >= 85 and not g["qa_stop"] and g["fakten_falsch"] == 0 and g["legal_mittel_hoch"] == 0 and not g["links_tot"]
    return g

def main():
    # 1 Intent
    sugg = {s for q in (QUERY, QUERY + " ", "wie " + QUERY, QUERY + " kosten") for s in autocomplete(q)}
    intent = chat(f"""Du bist Keyword-Researcher. Query: "{QUERY}". Echte Google-Autocomplete-Vorschläge (DE): {sorted(sugg)}
Bestehende Artikel des Magazins:\n{bestand()}\n{REGELN}
Bestimme Suchintention, Winkel für die Zielgruppe Tischler, Kannibalisierung (welcher bestehende Artikel ist nah, wie grenzen wir ab) und 6-8 FAQ-Fragen NUR aus den echten Vorschlägen.
JSON: {{"intent": "...", "winkel": "...", "kannibalisierung": "...", "faq_fragen": ["..."], "verwandte_artikel": ["NN-datei.html"]}}""", as_json=True)
    log(f"1 Intent: {intent.get('winkel', '')[:120]}")
    # 2 Brief
    brief = chat(f"""Du bist SEO-Stratege. Erstelle den Content-Brief für "{QUERY}". Intent: {json.dumps(intent, ensure_ascii=False)}
Bestehende Artikel:\n{bestand()}\n{REGELN}
JSON: {{"h1": "...", "slug": "kurzer-slug-ohne-nummer-ascii", "kurzantwort_ziel": "...", "h2": ["..."], "faq": ["..."], "interne_links": [{{"datei": "NN-....html", "anker": "..."}}], "recherchefragen": ["konkrete Fakten, die belegt werden müssen"]}}""", as_json=True)
    slug = f"{NN}-" + re.sub(r"[^a-z0-9-]", "", brief.get("slug", "artikel").lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss"))[:60].strip("-")
    D = os.path.join(P, "runs", slug); os.makedirs(D, exist_ok=True)
    w = lambda n, t: open(os.path.join(D, n), "w", encoding="utf-8").write(t if isinstance(t, str) else json.dumps(t, ensure_ascii=False, indent=1))
    w("01-intent.json", {"query": QUERY, "autocomplete": sorted(sugg), **intent}); w("02-brief.json", brief)
    log(f"2 Brief: {brief.get('h1')} -> {slug}")
    # 3 Dossier (Web) und 4 Produktfakten parallel
    def dossier():
        return chat(f"""Du bist Rechercheur (getrennt vom Redakteur). Recherchiere im Web die Fakten für den Artikel "{brief.get('h1')}" (Deutschland, Stand {MONAT}).
Recherchefragen: {json.dumps(brief.get('recherchefragen', []), ensure_ascii=False)}
Quellen-Reihenfolge: Gesetz (gesetze-im-internet.de), Behörden/KfW/Pflegekasse/BMG, Normherausgeber, Verbraucherzentrale/Stiftung Warentest, Hersteller, erst dann Ratgeberportale (nie als einzige Quelle).
Ausgabe Markdown-Tabelle: Aussage | Quelle (volle URL, die du wirklich gefunden hast) | primär/sekundär. Danach Liste "nicht belegbar". Keine erfundenen URLs.""", web=True)
    def produkte():
        seiten = "\n\n".join(f"### https://www.lehner-lifttechnik.com/lifte/{p}\n{fetch('https://www.lehner-lifttechnik.com/lifte/' + p)}" for p in PRODUKTSEITEN)
        return chat(f"""Du bist Produkt-Prüfer. Extrahiere aus den Lehner-Produktseiten die für "{brief.get('h1')}" relevanten Fakten (Typ, innen/außen, Traglast, Maße, Normen, Besonderheiten) mit URL. Widersprüche offenlegen. Nur was im Text steht.\n{seiten}""")
    with ThreadPoolExecutor(2) as ex:
        fd, fp = ex.submit(dossier), ex.submit(produkte)
        dos, prod = fd.result(), fp.result()
    w("03-dossier.md", dos); w("04-produkte.md", prod); log("3+4 Dossier und Produktfakten")
    # 5 Entwurf
    art = chat(f"""Du bist {PERSONA} des Treppenlift-Magazins. Schreibe den Artikel NUR aus Brief, Dossier und Produktfakten. 1.200-1.800 Wörter (harte Grenze ohne FAQ).
{REGELN}\n{FORMAT}
Interne Links relativ, z. B. <a href="06-treppenlift-aussen.html">…</a>, nur auf Dateien aus der Liste: {bestand()}
Quellen: nur URLs aus dem Dossier oder den Produktfakten.
--- BRIEF ---\n{json.dumps(brief, ensure_ascii=False)}\n--- DOSSIER ---\n{dos}\n--- PRODUKTFAKTEN ---\n{prod}\n--- TONE OF VOICE ---\n{TON}""")
    w("05-draft.html", art); log(f"5 Entwurf: {len(re.sub('<[^>]+>', ' ', art).split())} Wörter")
    # 6 FAQ vor den Reviews
    faq = chat(f"""Du bist FAQ-Redakteur. Schreibe den Abschnitt <h2 id="faq">Häufige Fragen</h2> mit 6-8 Fragen aus dieser Liste: {json.dumps(brief.get('faq') or intent.get('faq_fragen'), ensure_ascii=False)}
Format je Frage: <h3>Frage?</h3><p>Antwort</p>. Erster Satz beantwortet direkt, 2-4 Sätze, nur Fakten aus Dossier/Artikel, offene Rechtsfragen als Einzelfall. Nur das HTML ausgeben.
{REGELN}\n--- DOSSIER ---\n{dos}\n--- ARTIKEL ---\n{art}""")
    art = art.replace("<h2>Quellen</h2>", faq + "\n<h2>Quellen</h2>", 1) if "<h2>Quellen</h2>" in art else art + "\n" + faq
    w("05-draft.html", art); log("6 FAQ eingefügt")
    # 7 Reviews + 8 Schleife (max 3)
    r = reviews(art, dos, prod); g = gate_status(r)
    w("06-reviews.json", r); log(f"7 Reviews: QA {g['qa_score']}, falsch {g['fakten_falsch']}, Legal mittel/hoch {g['legal_mittel_hoch']}, tote Links {len(g['links_tot'])}")
    for schleife in (1, 2, 3):
        art, n = ersetze(art, r); log(f"8 Schleife {schleife}: {n} Ersatzformulierungen wörtlich übernommen")
        art = chat(f"""Du bist Chefredaktion und Autor. Arbeite ALLE Korrekturen der Reviews in den Artikel ein (Priorität: Stop-Kriterien, falsche Fakten/Recht, Produkt, Ton/Struktur).
Unbelegtes entschärfen oder streichen, nie raten. Tote Links entfernen (Quelle streichen oder Aussage entschärfen). Struktur und Format beibehalten. Gib den kompletten korrigierten Artikel aus.
{REGELN}\n{FORMAT}\n--- REVIEWS ---\n{json.dumps(r, ensure_ascii=False)}\n--- DOSSIER ---\n{dos}\n--- ARTIKEL ---\n{art}""")
        w(f"07-final-s{schleife}.html", art)
        r = reviews(art, dos, prod); g = gate_status(r)
        w(f"06-reviews-s{schleife}.json", r)
        log(f"8 Schleife {schleife}: QA {g['qa_score']}, falsch {g['fakten_falsch']}, Legal mittel/hoch {g['legal_mittel_hoch']}, tote Links {len(g['links_tot'])}")
        if g["ok_vor_gegencheck"]: break
    # 8b Gegencheck Zweitmodell, danach Faktencheck auf dem Ergebnis
    gtxt = chat(f"""Du bist unabhängiger Gegenprüfer (Zweitmodell) für ein B2B-Fachmagazin (YMYL, Google QRG). {REGELN}
Prüfe den Artikel gegen Dossier und Produktfakten und überarbeite ihn: nur belegte Verbesserungen, keine neuen Zahlen/Namen/Quellen, Struktur und Links behalten.
Antwortformat genau so:
===BEFUNDE===
(nummerierte Liste: Zitat -> Problem -> Änderung)
===SCORE===
(nur eine Zahl 0-100 nach QRG für die überarbeitete Fassung)
===HTML===
(komplettes überarbeitetes HTML-Fragment)
--- DOSSIER ---\n{dos}\n--- PRODUKTFAKTEN ---\n{prod}\n--- ARTIKEL ---\n{art}""", model=GEGEN)
    bef, _, rest = gtxt.partition("===SCORE===")
    sc, _, ghtml = rest.partition("===HTML===")
    gscore = int((re.findall(r"\d+", sc) or ["0"])[0])
    ghtml = ghtml.strip().removeprefix("```html").removeprefix("```").removesuffix("```").strip()
    w("09-gegencheck.md", f"# Gegencheck {GEGEN}\n\nScore {gscore}\n\n" + bef.replace("===BEFUNDE===", "").strip())
    if ghtml.startswith("<h1"):
        r2 = reviews(ghtml, dos, prod); g2 = gate_status(r2, gscore)
        w("09-reviews-gegencheck.json", r2)
        if g2["ok_vor_gegencheck"]: art, r, g = ghtml, r2, g2
        else: log(f"8b Gegencheck-Fassung verworfen (QA {g2['qa_score']}, falsch {g2['fakten_falsch']}, Legal {g2['legal_mittel_hoch']})")
    g["gegencheck_score"] = gscore
    log(f"8b Gegencheck {GEGEN}: Score {gscore}")
    # 10 Gate
    g["bestanden"] = g["ok_vor_gegencheck"] and gscore >= 85
    so = f"""<h2>So entsteht dieser Artikel</h2><p>Dieser Artikel wurde vollautomatisch von einer KI-Redaktion erstellt und geprüft: Suchintention aus Google Autocomplete, Web-Recherche mit Quellen, Produktdaten live von lehner-lifttechnik.com, Entwurf und FAQ, vier parallele Prüfungen (Qualität nach Google-Richtlinien, Fakten, Recht, Marke), Link-Prüfung und ein Gegencheck durch ein zweites KI-Modell. Veröffentlicht wird nur, was alle Prüfstufen besteht (Qualität {g['qa_score']}/100, Gegencheck {gscore}/100, keine falschen Fakten, keine offenen Rechtspunkte, keine toten Links). Modelle: {MODEL}, {GEGEN}. Stand: {MONAT}. Einen namentlich genannten Autor gibt es nicht.</p>"""
    art = art.replace("<h2>Über diesen Artikel</h2>", so + "\n<h2>Über diesen Artikel</h2>", 1) if "<h2>Über diesen Artikel</h2>" in art else art + "\n" + so
    w("10-final.html", art)
    ziel = "articles" if g["bestanden"] else "articles-zurueckgestellt"
    os.makedirs(os.path.join(P, ziel), exist_ok=True)
    open(os.path.join(P, ziel, slug + ".html"), "w", encoding="utf-8").write(art)
    if g["bestanden"]:
        try:
            from image import illustrate
            art2, bild = illustrate(slug, art)
            if bild: art = art2; open(os.path.join(P, "articles", slug + ".html"), "w", encoding="utf-8").write(art); log(f"11 Bild: {bild}")
            else: log("11 Bild: keines (QA nicht bestanden), Artikel bleibt ohne Bild")
        except Exception as e:
            log(f"11 Bild-Fehler (Artikel unberuehrt): {e}")
    g.update({"query": QUERY, "slug": slug, "h1": brief.get("h1"), "kosten_usd": round(COST["usd"], 4), "llm_calls": COST["calls"], "modell": MODEL, "gegencheck_modell": GEGEN, "datum": str(HEUTE)})
    w("gate.json", g); log(f"10 Gate: {'BESTANDEN' if g['bestanden'] else 'ZURUECKGESTELLT'} -> {ziel}/{slug}.html, Kosten {g['kosten_usd']} USD")
    w("log.md", f"# Lauf {slug}\n\n" + "\n".join(LOG) + "\n")

if __name__ == "__main__":
    main()
