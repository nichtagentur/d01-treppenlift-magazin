# Redaktions-Playbook: von einer Search Query zum geprüften Artikel

Eingabe: **eine Search Query** (z. B. "treppenlift kurvig").
Ausgabe: ein recherchierter, QA-, Rechts- und Marken-geprüfter Artikel als HTML-Fragment in `articles/`, eingebaut in `site/index.html`.
Alle Schritte machen KI-Agenten, auch Freigabe und Publizieren. **Es gibt keinen Menschen im Prozess:** Die Chefredakteur-KI entscheidet über automatische Gates (Schritt 10).

Gelernt im ersten Durchlauf (10 Artikel, 2026-10-15). Die Lehren stehen jeweils als **Warum** beim Schritt.

---

## 0. Feste Grundlagen (einmal pro Projekt, alle 3 Monate auffrischen)

| Datei | Inhalt | Agent |
|---|---|---|
| `briefing/qrg-briefing.md` | Quality Rater Guidelines (Stand 11.09.2025): YMYL, E-E-A-T, Highest Quality, Needs Met, QA-Prüfliste mit 20 Punkten und Stop-Kriterien | SEO-Stratege |
| `briefing/tone-of-voice.md` | Lehner-Tonalität, Do's und Don'ts, **Fakten-Sheet nur mit Quell-URLs**, Produkt-URLs | Brand-Editor |
| `research/TOP10.md` + `research/*.json` | Keyword-Landschaft, Autocomplete, Suchvolumen, Trends | Keyword-Researcher |

Diese Dateien werden **nicht** bei jedem Artikel neu erstellt. Jeder Agent liest sie vollständig, bevor er anfängt.
**Warum:** Ohne gemeinsame Briefings schreibt jeder Agent in anderem Ton und mit anderem Qualitätsmaßstab.

## Ordner pro Artikel

```
runs/<NN>-<slug>/
  01-intent.md       Suchintention, Volumen, SERP, Autocomplete-Fragen
  02-brief.md        Gliederung, Mehrwert, FAQ-Fragen, interne Links
  03-dossier.md      Faktentabelle: Aussage | Zahl | Quelle-URL | Datum | primär/sekundär | geprüft
  04-produkte.md     Lehner-Produktdaten nur von lehner-lifttechnik.com, mit URL
  05-draft.html      Entwurf des Redakteurs
  06-review-*.md     qa, fakten, recht, marke, links
  07-final.html      wird nach articles/<NN>-<slug>.html kopiert
  log.md             was in welchem Schritt passiert ist, Scores, offene Punkte
```

---

## Ablauf (10 Schritte)

Regeln für alle Subagents: Sie laufen auf dem Standardmodell (Sonnet). Kein Agent bekommt ein anderes Modell. Nie `rm`, nie Platzhalter, nie erfundene Personen, Zitate, Tests oder Erfahrungen.

### Schritt 1: Intent und Nachfrage (Agent "Keyword-Researcher")
- Google Autocomplete live: Query, Query + a-z, Fragewörter (`was/wie/wer/wann/kann man`). Endpoint: `https://suggestqueries.google.com/complete/search?client=firefox&hl=de&gl=de&q=...`, 0,3 s Pause.
- DataForSEO (geteiltes Guthaben, **maximal 2 Calls**): ein Call für das Suchvolumen von 10-20 Varianten, ein Call für den organischen SERP der Query (Top 10: Wer rankt? Welcher Seitentyp?).
- Ergebnis `01-intent.md`: Hauptintention in einem Satz, Nebenintentionen, echte Fragen für die FAQ, Seitentyp der Top 10.
- **Kannibalisierungs-Check:** `articles/` auf Artikel mit gleicher Intention prüfen. Ist die Intention gleich, gibt es drei Möglichkeiten: den bestehenden Artikel erweitern, einen klar abgegrenzten neuen Winkel schreiben (mit gegenseitigen Links) oder abbrechen. Die Empfehlung kommt in `01-intent.md`, die Chefredakteur-KI entscheidet und trägt die Entscheidung in `redaktion/entscheidungen.md` ein.
  **Warum:** Die Query "treppenlift im außenbereich" (Durchlauf 2) hat dieselbe Intention wie der bestehende Artikel 06 "treppenlift außen". Zwei Seiten zur gleichen Intention konkurrieren in Google gegeneinander.
- **Warum:** Reine B2B-Begriffe ("händler werden", "tischler", "aufmaß") haben keine Nachfrage. Tischler holt man über die Fragen der Endkunden ab und gibt Profi-Wissen dazu.

### Schritt 2: Content-Brief (Agent "SEO-Stratege")
- Gliederung (H2/H3), Kurzantwort für die ersten 3 Sätze, **mindestens ein eigener Mehrwert** (Tabelle, Rechenbeispiel, Checkliste, Ablaufschema), 6-8 FAQ-Fragen aus Schritt 1, Links auf die vorhandenen Magazin-Artikel.
- Ehrliche Grenzen festlegen: Wann ist dieses Produkt die falsche Lösung?
- Ergebnis `02-brief.md`.

### Schritt 3: Fakten-Dossier (Agent "Rechercheur", getrennt vom Redakteur)
- Jede Zahl, Frist und Rechtsaussage wird in eine Tabelle eingetragen: Aussage, Quelle, Datum, primär oder sekundär.
- Reihenfolge der Quellen: Gesetz (gesetze-im-internet.de), Behörde/KfW/Pflegekasse, Norm-Herausgeber (DIN Media), Verbraucherzentrale/Stiftung Warentest, Hersteller, erst dann Ratgeberportale.
- Widersprüchliche Angaben werden als Spanne mit beiden Quellen eingetragen.
- Ratgeberseiten mit KI-Text oder Affiliate-Interesse (bau.de, pflege-helfer24, Vermittlungsportale) nur als Hinweis verwenden, nie als einzige Quelle.
- Fachbegriffe mit Doppelbedeutung markieren: "Außenbereich" ist im Baurecht (BauGB, BayBO, LBO BW) die Fläche außerhalb bebauter Ortsteile, nicht "draußen an der Treppe". Im Text "an der Außentreppe" oder "im Freien" schreiben.
- Was eine Empfehlung ist, als Empfehlung eintragen (Beispiel: "Antrag vor Auftrag" empfiehlt die Verbraucherzentrale, das Gesetz verlangt es nicht).
- Fehlt eine Regel im Gesetz (BayBO und LBO BW nennen Treppenlifte nicht ausdrücklich), dann als "Einzelfall, Bauaufsicht fragen" eintragen.
- Normen mit aktueller Ausgabe eintragen (EN 81-41: Ausgabe 2025-07). EUR-Lex blockiert Bots, deshalb DGUV oder TÜV Nord als Sekundärquelle nutzen.
- Das Dossier ordnet jeden Fakt auch der richtigen Stelle zu (Beispiel: "Wege auf dem Grundstück" fördert laut BMG der KfW-Kredit, nicht die Pflegekasse). Falsche Zuordnungen im Dossier kehren in jeder Runde zurück.
- **Schnellmodus unter Zeitdruck:** Ein unvollständiges Dossier (Durchlauf 2: 16 Punkte "nicht belegbar") senkt die erste QA auf 76. Das kostet eine Korrekturschleife, und das Zweitmodell braucht das vollständige Dossier. Lieber 5 Minuten mehr in Schritt 3 investieren.
- Jede Quelle selbst öffnen. "Nur im Suchauszug gesehen" reicht nicht als Beleg.
- **Warum:** Im ersten Durchlauf haben die Redakteure selbst recherchiert. Die QA fand eine erfundene Ersparnis von 25 %, tote Quellen, eine Strom-Zahl aus einer KI-Quelle und eine Warentest-Angabe ohne den zitierten Satz.

### Schritt 4: Produktfakten (Agent "Produkt-Prüfer")
- Lehner-Produktdaten **live** von den Produktseiten holen: Tragfähigkeit, Plattformmaße, Mindesttreppenbreite, innen/außen, Normen, Temperatur.
- Widersprüche auf der Lehner-Seite selbst offenlegen (Beispiel: Stratos NG/A, 900 x 1400 mm gegenüber 800 x 1000 mm).
- Bei einem Widerspruch steht im Text der konservative Wert mit dem Zusatz "beim Hersteller bestätigen". Werte wörtlich übernehmen, ohne Deutung (Sigma: "+45 °C bis -15 °C", nicht "Betrieb").
- Der Produkt-Prüfer schreibt am Ende eine Liste "An Lehner melden" mit den Widersprüchen und Lücken auf der Website (Durchlauf 2: 11 Punkte, etwa IP-Klasse, Temperatur, Dübel und Wartungsintervall fehlen). Das ist ein Nebenprodukt für das Marketing.
- **Warum:** Zwei falsche Produktaussagen sind erst in der QA aufgefallen ("Lehner nennt keine Mindestbreite", obwohl Delta 890 mm und Omega 950 mm angeben; "Liftboy 4 nicht für außen", obwohl er innen und außen einsetzbar ist).

### Schritt 5: Entwurf (Agent "Fachredakteur", Persona passend zum Thema)
- Personas: Kalkulation, Markt/Geschäftsmodell, Technik/Normen, Recht/Förderung, Tischlermeister.
- Der Redakteur schreibt **nur** aus `02-brief.md`, `03-dossier.md` und `04-produkte.md`. Braucht er einen neuen Fakt, kommt dieser zuerst ins Dossier.
- Ton nach `tone-of-voice.md`: Sie-Form, sachlich, kurze Sätze, kein Werbegeschrei.
- Lehner nie als Partner von Tischlern darstellen, denn Tischler kommen im Partnerprofil nicht vor. Eigene Produkte sachlich verlinken und als "Betreiber dieses Magazins" kennzeichnen.
- Länge 1.200-1.800 Wörter. HTML-Fragment im Format unten.
- Die Wortgrenze steht im Prompt als harte Regel. In Durchlauf 2 kamen mit FAQ und Überarbeitung rund 3.000 Wörter heraus.
- Hinweise wie "Fachwissen, nicht aus einer Quelle zitiert" höchstens einmal in der Offenlegung erklären, nicht bei jeder Aussage (Durchlauf 2: 13-mal, Abzug in QA und Ton).

### Schritt 6: FAQ (Agent "FAQ-Redakteur", VOR den Reviews)
- 6-8 FAQ aus den echten Fragen in `01-intent.md` (Autocomplete, live nachgeholt). Sie stehen in `05-draft.html` vor `<h2>Quellen</h2>`.
- Der erste Satz beantwortet die Frage direkt, insgesamt 2-4 Sätze. Nur Fakten aus dem Dossier, neue Fakten zuerst ins Dossier.
- Offene Rechtsfragen ehrlich als offen oder Einzelfall benennen.
- **Warum:** Im ersten Durchlauf kamen die FAQs erst nach der QA und wurden nie geprüft. FAQ-Antworten sind kurz und absolut formuliert und werden oft als Snippet oder KI-Antwort zitiert. Gerade dort darf kein ungeprüfter Fakt stehen.

### Schritt 7: Reviews (5 Agents parallel über den ganzen Artikel inkl. FAQ, jeder schreibt `06-review-<typ>.md`)

| Review | Prüft | Typische Funde im ersten Durchlauf |
|---|---|---|
| **QA / QRG** | die 20 Punkte aus `qrg-briefing.md`, Score 0-100, Stop-Kriterien, Kurzantwort oben, Mehrwert, Ton | Absolutaussagen in der Kurzantwort, fehlende Inhaltsverzeichnisse |
| **Faktencheck** | 5-8 wichtigste Zahlen gegen Primärquellen | KfW-Stopp am 30. statt 31.07.2026, unplausible Spanne 25.000-150.000 EUR (gilt nur für Außenaufzüge mit Kabine) |
| **Legal Review** (Persona Sozial-, Steuer-, Bau- und Gerätesicherheitsrecht) | § 40 Abs. 4 SGB XI (Kann-Leistung, 4.180/16.720 EUR, Antrag vor Auftrag), §§ 33, 35a EStG, § 554 BGB, § 20 WEG, BetrSichV, Maschinenverordnung (EU) 2023/1230 ab 20.01.2027, EN 81-40/-41, Landesbauordnung | Pflegekasse "zahlt" statt "kann gewähren"; Zuschuss bei Miete nicht gesichert; Prüfpflicht im Privathaushalt offen |
| **Marke / Produkt** | Ton gegen `tone-of-voice.md`, Lehner-Daten gegen `04-produkte.md`, keine falschen Partneraussagen | falsche Produktaussagen (siehe Schritt 4) |
| **Link-Check** (Skript, kein Agent) | `tools/linkcheck.sh articles/<datei>` | 404 bei bau.de und pflege-helfer24, 403 bei TÜV SÜD |

Link-Check: Prüfen mit GET, nicht mit HEAD. Bayern-Seiten liefern bei HEAD 405 und bei GET 200. 403 bei Bot-Sperren (EUR-Lex, Uni-Server) nicht als tot werten, sondern im Browser gegenprüfen.

### Schritt 8: Überarbeitungsschleife (Agent "Chefredaktion")
- Die Chefredaktion führt alle Reviews zu einer priorisierten Fehlerliste zusammen: 1. Stop-Kriterien, 2. falsche Fakten und Recht, 3. Produkt, 4. Ton und Struktur.
- Der Fachredakteur korrigiert Text und FAQ, danach laufen QA und Faktencheck erneut über den ganzen Artikel.
- **Abbruch:** QA-Score mindestens 85 **und** kein offenes Stop-Kriterium außer dem namentlichen Autor (bewusst akzeptiertes Risiko, siehe Schritt 10). **Höchstens 2 Schleifen**, danach wird der Artikel automatisch zurückgestellt (Schritt 10).
- Widersprechen sich zwei Reviews (Durchlauf 2: Marke gegen Fakten bei der Sigma-Temperatur), entscheidet die Chefredaktion anhand der Primärquelle und schreibt die Entscheidung ins Log.
- Was nicht belegbar ist, wird entschärft ("in der Regel", "Einzelfall, beim Hersteller oder der Überwachungsstelle klären") oder gestrichen, nie geraten.

### Schritt 9: Einbau (Skript)
- **Vorher Schritt 8b: Gegencheck durch ein Zweitmodell.** `python3 tools/gegencheck.py runs/<NN>-<slug>` (Standard `google/gemini-4-argon` über OpenRouter, eigener Key; Kosten rund 0,14 USD pro Artikel). Das Skript schreibt `09-gegencheck.md` (Befunde und Score) und `09-gegencheck.html`.
- Die Chefredaktion prüft jeden Befund gegen die Reviews. Das Zweitmodell kann einen bereits korrigierten Fehler zurückbringen, wenn er im Dossier steht (Durchlauf 2: BMG-Wege). Solche Befunde verwerfen und das Ergebnis als `10-final-gegengecheckt.html` speichern.
- `cp runs/<NN>-<slug>/10-final-gegengecheckt.html articles/<NN>-<slug>.html && python3 build.py` (ohne 8b: `07-final.html`), danach `tools/linkcheck.sh articles/<NN>-<slug>.html` erneut.
- Bestehende Artikel zum selben Thema verlinken auf den neuen Artikel (Durchlauf 2: 06 -> 11, Kasten "Weiterlesen" vor den Quellen).
- Eintrag in `log.md`: Scores vorher/nachher, Korrekturen, Restrisiken, Review-Termin (Preise und Förderung spätestens nach 6 Monaten neu prüfen).

### Schritt 10: Automatische Freigabe (Publikations-Gate)
Die Chefredakteur-KI publiziert, wenn **alle** Bedingungen erfüllt sind:
- QA-Score mindestens 85, **nach der Schleife neu gemessen** (keine Selbsteinschätzung).
- Zweitmodell-Gegencheck (`tools/gegencheck.py`) Score mindestens 85 und **alle Befunde** von der Chefredaktion entschieden (übernommen oder verworfen mit Begründung im Log).
- Linkcheck ohne TOT.
- Faktencheck ohne Wertung "falsch".
- Legal-Review ohne mittleren oder hohen Punkt.

**Nicht bestanden:** höchstens 2 Schleifen, danach wird der Artikel automatisch zurückgestellt: Status "zurückgestellt" in `redaktion/status.md`, der nächste Wochenlauf startet einen neuen Versuch mit frischem Dossier. Nie halbfertig publizieren.

**Autorenzeile:** Nie einen Personennamen erfinden. Stattdessen transparent: "Redaktion Treppenlift-Magazin, Lehner Lifttechnik (KI-gestützt erstellt und geprüft)" plus Abschnitt "So entsteht dieser Artikel" (Prüfschritte, Quellen, Stand). Das QRG-Stop-Kriterium "named author" wird damit als bewusst akzeptiertes Risiko dokumentiert.

**Publizieren:** `tools/publish.sh` (ruft `build.py` auf, kopiert die öffentlichen Seiten nach `dist/`, deployt Cloudflare Workers `d01-treppenlift-magazin`, prüft HTTP 200 der Startseite und aller Artikel). Läuft am Ende jedes Wochenlaufs automatisch. Einmalige Inbetriebnahme: Datei `redaktion/LIVE` (Go-Live-Schalter; einmal gesetzt bleibt alles automatisch, ohne die Datei wird nur gebaut, nicht deployt).

**Fehler nach Publikation:** automatischer Korrektur-Lauf, Korrekturhinweis und Changelog im Artikel. Bei falschem YMYL-Fakt sofort depublizieren: Artikel nach `articles-zurueckgestellt/` verschieben (nie `rm`), neu bauen, deployen.

---

## Artikelformat (HTML-Fragment)

```html
<h1>…</h1>
<p class="meta">Stand: <Monat Jahr> · Redaktion Treppenlift-Magazin, Lehner Lifttechnik (KI-gestützt erstellt und geprüft) · Lesezeit ca. X Min.</p>
<div class="box"><strong>Kurz gesagt:</strong> Antwort in max. 3 Sätzen</div>
<h2>…</h2> … Tabelle / Checkliste / Rechenbeispiel …
<h2>Häufige Fragen</h2> <h3>Frage?</h3><p>Antwort</p> …
<h2>Quellen</h2><ol><li><a href="…">Titel</a>, abgerufen <Monat Jahr></li></ol>
<h2>So entsteht dieser Artikel</h2><p>Prüfschritte (QA, Faktencheck, Legal, Marke, Linkcheck, Zweitmodell), Quellen, Stand, KI-gestützt erstellt und geprüft, kein Personenname, keine Rechts-/Steuerberatung.</p>
```

## Orchestrierung (für die steuernde KI)

1. Schritte 1 bis 4 laufen nacheinander. 3 und 4 dürfen parallel laufen, sobald der Brief steht.
2. Schritt 6 (FAQ) ist fertig, bevor Schritt 7 startet. Schritt 7: alle 5 Reviews in **einer** Nachricht parallel starten.
3. Bei mehreren Queries als Pipeline arbeiten: Die QA eines Artikels startet, sobald sein Entwurf fertig ist, nicht erst wenn alle fertig sind.
4. Jeder Agent bekommt im Prompt: Persona, die Pfade der Briefings zum vollständigen Lesen, die Ein- und Ausgabedateien, die Regeln von oben und "antworte in 5 Sätzen".
5. Mitlesende können `site/index.html` im sichtbaren Chrome (ein Tab, alle Artikel) nach jedem Build neu laden; es ist keine Freigabe nötig.
6. Erwarteter Aufwand pro Artikel: etwa 8-10 Agent-Läufe plus ein Zweitmodell-Aufruf, 15-25 Minuten.
7. Bei Präsentationen früh etwas zeigen: den Entwurf mit FAQ als `site/<NN>-vorschau-entwurf.html` mit einem Vorschau-Hinweis öffnen und nach dem Einbau in den Papierkorb legen.

## Betrieb: GitHub Actions + OpenRouter

- Der Prozess läuft unabhängig vom Desktop: Repo github.com/nichtagentur/d01-treppenlift-magazin, Workflow `.github/workflows/redaktion.yml` (wöchentlich Montag 05:00 UTC, dazu manuell per "Run workflow" mit Themen und Anzahl).
- Job `plan`: `pipeline/plan.py` wählt Themen aus `redaktion/contentplan.md` (Prio 1), die nicht in `redaktion/erledigt.txt` stehen.
- Job `artikel` (Matrix, parallel je Thema): `pipeline/run_article.py` führt die Schritte 1-10 aus, mit DeepSeek `deepseek/deepseek-v4.1-flash` über OpenRouter, Web-Plugin für das Dossier und Gegencheck mit `google/gemini-4-argon`.
- Job `publish`: `pipeline/publish.py` baut nur Gate-bestandene Artikel aus `redaktion/live.txt`, entlinkt interne Links auf nicht-live Artikel, veröffentlicht auf Cloudflare Workers `d01-treppenlift-magazin`, prüft HTTP 200, committet zurück ins Repo und schreibt den Bericht nach `redaktion/laeufe/`.
- Gate (Schritt 10) im Code: QA ≥85, Fakten 0 falsch, Legal 0 mittel/hoch, 0 tote Links, Gegencheck ≥85; sonst landet der Artikel in `articles-zurueckgestellt/`.
- Secrets (GitHub Repo-Secrets): `OPENROUTER_API_KEY`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`.
- Lokale Cron-Jobs und `tools/redaktion-lauf.sh` sind abgelöst und nur noch manuell nutzbar.
- Die 11 Altartikel sind nicht live, bis sie per Refresh durch dasselbe Gate gehen.
