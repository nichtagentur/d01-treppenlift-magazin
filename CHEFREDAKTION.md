# Chefredaktions-Playbook: KI-Redaktion steuern

Stand: 2026-10-15. Grundlage: `redaktion/chefredaktion-entwurf.md`, `redaktion/contentplan.md`, `redaktion/refresh-liste.md`, `PLAYBOOK.md`.

## Der Redaktionskreislauf

Die Redaktion ist eine Schleife, die ohne Ende läuft: Planen, Produzieren, Prüfen, Freigeben, Publizieren, Messen, Aktualisieren, zurück zu Planen. Der Takt kommt per Cron auf diesem Desktop und startet `tools/redaktion-lauf.sh <takt>`.

| Phase | Prozess (Abschnitt 3) | Wer | Takt |
|---|---|---|---|
| Planen | A | Content-Planer, Chefredakteur-KI | monatlich, wöchentlich |
| Produzieren | C Schritte 1-6 | Produktions-Personas | wöchentlich (max. 1 Entwurf) |
| Prüfen | C Schritte 7-8b | Reviews, Zweitmodell | wöchentlich |
| Freigeben | C Schritt 10, D | Chefredakteur-KI (automatische Gates) | wöchentlich, Status in `status.md` |
| Publizieren | D | Chefredakteur-KI über `tools/publish.sh` | am Ende jedes Wochenlaufs |
| Messen | B Trigger, Search Console, Linkcheck | Performance-/Aktualitäts-Analyst | wöchentlich, monatlich |
| Aktualisieren | B, E | Aktualitäts-Analyst, Fachredakteure | monatlich, quartalsweise |

| Takt | Cron | Inhalt | Ausgabe |
|---|---|---|---|
| `woechentlich` | Montag 07:00 | Redaktionskonferenz (Vorlage Abschnitt 9); höchstens 1 neuer Artikel-Entwurf bis Schritt 9; Publizieren automatisch nach Gates (D), sobald `redaktion/LIVE` gesetzt ist | `redaktion/status.md`, `redaktion/entscheidungen.md` |
| `monatlich` | 1. des Monats 06:00 | Content-Planer und Aktualitäts-Analyst aktualisieren Plan und Refresh-Liste | `redaktion/contentplan.md`, `redaktion/refresh-liste.md` |
| `quartalsweise` | 1.1., 1.4., 1.7., 1.10. 05:00 | Komplett-Audit aller Artikel: linkcheck, QA-Stichprobe, Playbook-Lehren | `redaktion/refresh-liste.md`, Vorschläge in `redaktion/lehren-offen.md` |

Cron-Zeilen (Vorlage, `R` = Projektordner):
```
0 7 * * 1      R/tools/redaktion-lauf.sh woechentlich
0 6 1 * *      R/tools/redaktion-lauf.sh monatlich
0 5 1 1,4,7,10 *  R/tools/redaktion-lauf.sh quartalsweise
```
Jeder Lauf schreibt `redaktion/laeufe/<datum>-<takt>.md` (Was geprüft, entschieden, geändert, offen, Kosten) und hängt Lehren an `redaktion/lehren-offen.md` an. Die Lehre geht nach Prüfung durch die Chefredakteur-KI ins `PLAYBOOK.md` (Eintrag in `entscheidungen.md`). Der Kreislauf schließt sich, weil jeder Lauf mit seinen Ergebnissen den Eingang des nächsten bildet (Plan, Status, Refresh-Liste, Lehren).

## 0. Zweck und Dateikarte

Dieses Playbook ergänzt `PLAYBOOK.md` (Artikelproduktion) um die Steuerung: Es legt fest, wer was wann entscheidet. Die Chefredakteur-KI plant, priorisiert und bereitet das Publizieren vor. Jede Veröffentlichung, auch mit YMYL-Aussage (Recht, Förderung, Sicherheit, Preis), läuft automatisch durch die Gates aus Prozess D. Es gibt keinen Menschen im Prozess.

| Datei | Inhalt |
|---|---|
| `PLAYBOOK.md` | Wie ein Artikel entsteht (10 Schritte, Personas, Artikelformat, Orchestrierung) |
| `CHEFREDAKTION.md` | Wer was wann entscheidet (diese Datei) |
| `redaktion/contentplan.md` | Themenlücken, Plan 8 Wochen, Monatsroutine Planung |
| `redaktion/refresh-liste.md` | Artikel, Verfallsdaten, Risiko, Prüftermine, Trigger-Katalog, Refresh-Routine |
| `redaktion/status.md` | Wochenstand: Ampel, Artikel, Schritt, Blocker, zurückgestellt (anlegen, falls fehlt) |
| `redaktion/entscheidungen.md` | Entscheidungen mit Begründung und Changelog (anlegen, falls fehlt) |
| `redaktion/refresh-log.md` | Protokoll je Refresh-Lauf, nur anhängen (anlegen, falls fehlt) |
| `redaktion/laeufe/<datum>-<takt>.md` | Protokoll je Cron-Lauf; `redaktion/lehren-offen.md` sammelt Lehren |
| `tools/redaktion-lauf.sh` | Startet einen Takt (siehe Kreislauf) |

Dateien nie mit `rm` entfernen, sondern `gio trash`. Keine erfundenen Personen, Zitate, Tests oder Zahlen.

## 1. Chefredakteur-KI: Mandat, Grenzen, automatische Gates

**Die KI entscheidet allein**

| Bereich | Beispiele |
|---|---|
| Reihenfolge | Themenreihenfolge, Neu gegen Refresh, WIP-Limit |
| Pipeline | Start und Reihenfolge der Agenten, Zusammenführen der Reviews (Schritt 8) |
| Inhalt | Nicht belegbare Aussagen entschärfen oder streichen; Konflikte nach Primärquelle lösen |
| Kleinkorrekturen | Tippfehler, defekter Link, Formatierung, mit Changelog-Eintrag |
| Publizieren | Deployment nach bestandenen Gates (Prozess D) über `tools/publish.sh` |
| Korrektur und Depublizieren | Korrekturlauf, Korrekturhinweis, Depublizieren bei falschem YMYL-Fakt (Prozess E, F) |
| Zurückstellen | Artikel ohne bestandenes Gate nach 2 Schleifen |
| Änderungen an `PLAYBOOK.md` und `briefing/*` | Chefredakteur-KI, mit Eintrag und Begründung in `entscheidungen.md` |

**Automatische Grenzen (Stopp ohne Mensch)**

| Auslöser | Reaktion der Chefredakteur-KI |
|---|---|
| 2 Schleifen ohne bestandenes Gate | Artikel "zurückgestellt", nächster Wochenlauf neuer Versuch mit frischem Dossier |
| Möglicherweise falscher Rechts-, Förder- oder Sicherheitsfakt veröffentlicht | Sofort depublizieren (Prozess F), Korrekturlauf |
| Reviews widersprechen sich | Entscheidung nach Regeln in Abschnitt 5, Begründung in `entscheidungen.md` |
| Rechtliche Grauzone oder Widerspruch auf Lehner-Produktseite | Konservativ formulieren oder streichen; Eintrag in Liste "An Lehner melden" (reine Information) |
| Leserhinweis mit Personenbezug, Schadensbehauptung, Abmahnung, Herstellerbeschwerde | Betroffenen Artikel sofort depublizieren, Eintrag in `entscheidungen.md` |
| Mehr als 2 DataForSEO-Calls je Artikel, neue bezahlte Dienste | Nicht ausführen |
| Kosten über 150 % des Rahmens | Lauf stoppt, Eintrag in `status.md` |

## 2. Personas

Alle Subagents laufen auf dem Standardmodell. Pfade für Artikel relativ zu `runs/<NN>-<slug>/`.

| Persona | Auftrag | Input | Output | Rhythmus |
|---|---|---|---|---|
| Chefredakteur-KI | Steuern, priorisieren, Reviews zusammenführen, Gates prüfen, Status schreiben | `status.md`, Logs, alle Analysen | `redaktion/status.md`, `redaktion/entscheidungen.md` | Wöchentlich, bei Eskalation |
| Content-Planer | Themenlücken, Priorität, Kannibalisierungs-Vorprüfung | `research/TOP10.md`, `articles/`, letzter `contentplan.md`, Autocomplete live | `redaktion/contentplan.md`, `redaktion/rohdaten-autocomplete-<datum>.json` | Monatlich (1. Werktag), Okt/Mai 8 Wochen voraus |
| Aktualitäts-Analyst | Verfallsdaten, Trigger, Linkstatus, Primärquellen je Artikel | `articles/`, `log.md`, `tools/linkcheck.sh`, Primärquellen | `redaktion/refresh-liste.md`, `redaktion/refresh-log.md` | Monatlich, anlassbezogen, Quartal voll |
| Performance-Analyst | Klicks, Impressionen, Position, Queries, Kannibalisierung 06 gegen 11 | Search-Console-Daten der Property | Abschnitt "Performance" in `redaktion/status.md` | Wöchentlich (inaktiv ohne Zugang, siehe Abschnitt 8) |
| Produktions-Personas | Keyword-Researcher, SEO-Stratege, Rechercheur, Produkt-Prüfer, Fachredakteure, FAQ-Redakteur, QA, Fakten, Legal, Marke | siehe `PLAYBOOK.md` Schritte 1-8 | `01` bis `07` je Artikel | Je Artikel |
| Zweitmodell-Gegenprüfer | Unabhängiger Gegencheck vor dem Einbau | Artikel plus Dossier | `09-gegencheck.md` | Je Artikel (Schritt 8b) |

## 3. Prozesse

**A Themenplanung (monatlich)**
1. Content-Planer liest `research/TOP10.md`, letzten `contentplan.md`, alle H1, PLAYBOOK Schritt 1.
2. Autocomplete der Kernseeds plus Vormonats-Seeds (0,3-0,4 s Pause), kein DataForSEO ohne Bedarf (höchstens 2 Calls je Artikel).
3. Neue Queries = nicht im Vormonatsdatensatz und in keiner H1; nichts erfinden, leere Seeds als Befund notieren.
4. Kannibalisierung je Query prüfen: erweitern, abgegrenzter Winkel mit Gegenlinks oder verwerfen.
5. Priorität 1-3 nach Regeln im `contentplan.md`; Prio-1-Artikel 4-6 Wochen vor Januar bzw. August legen.
6. Chefredakteur-KI übernimmt den Plan in `status.md` und bestätigt ihn selbst.
Ausgabe: `redaktion/contentplan.md`, Rohdatendatei mit Datum.

**B Refresh**

| Trigger | Reaktion |
|---|---|
| Maschinenverordnung (EU) 2023/1230 ab 20.01.2027 | Futur auf Präsens, Primärquelle belegen; 14 Tage vor und nach dem Stichtag prüfen |
| KfW 455-B (Antragsstopp seit 31.07.2026), Kredit 159 | kfw.de prüfen, Beträge angleichen |
| Pflegekassen-Betrag (§ 40 Abs. 4 SGB XI, 4.180 EUR) oder BMG-Leistungsübersicht neu | Alle Fundstellen per `grep` ersetzen, Rechenbeispiele neu rechnen |
| Norm-Statuswechsel (EN 81-40/-41, DIN 18065, DIN EN 60529) | Gültigkeitsdaten anpassen |
| Lehner-Produktseiten geändert | Fakten-Sheet aktualisieren, Widersprüche melden |
| Steuer, BetrSichV, Landesrecht | Gesetzestext und Urteile prüfen |
| Quelle tot oder älter als 12 Monate | Quelle ersetzen oder alt kennzeichnen |
| Search Console: -20 % Klicks/Impressionen oder Positionsverlust | Query-Analyse, Inhalt gegen Top-Treffer prüfen |
| Leserhinweis zu Fehler | Korrekturlauf und Korrekturlog (Prozess E) |

Vollständiger Katalog mit betroffenen Artikeln: `redaktion/refresh-liste.md` Abschnitt 2.
Routine (Abschnitt 3 der Refresh-Liste):
1. Datum setzen, letzten Lauf in `redaktion/refresh-log.md` lesen.
2. Verfallsdaten per `grep` aus `articles/*.html` ziehen.
3. Linkcheck je Artikel (`tools/linkcheck.sh`): PRUEFEN im Browser gegenprüfen, TOT ersetzen.
4. Primärquellen direkt abrufen, nichts raten.
5. Search Console auswerten (28 Tage gegen Vorperiode).
6. Änderung nur mit Beleg, "Stand" und Abrufdatum setzen, Zahlen nachrechnen.
7. Bei wichtiger Änderung Gegencheck (`tools/gegencheck.py`), dann `python3 build.py` und Linkcheck.
8. QA-Bericht `qa/qa-<nr>-<datum>.md` und Tabelle fortschreiben.
Budget: halber Rahmen, nur betroffene Schritte. Ausgabe: `redaktion/refresh-log.md`, `redaktion/refresh-liste.md`, Liste "An Lehner melden" (reine Information).

**C Neuer Artikel**
1. Chefredakteur-KI prüft WIP-Limit und Warteschlange, gibt Thema aus `contentplan.md` frei.
2. `runs/<NN>-<slug>/` anlegen, dann PLAYBOOK Schritte 1-10 in Reihenfolge.
3. Schritte 1-2 Keyword und Brief, 3-4 Dossier und Produkte, 5-6 Entwurf und FAQ, 7 fünf Reviews parallel, 8 Schleife (max. 2), 8b Gegencheck, 9 Einbau, 10 automatische Freigabe und Publizieren.
Ausgabe: `01` bis `09` im Run-Ordner, `log.md`, Eintrag in `status.md`.

**D Publizieren (automatische Gates, alle erforderlich)**
1. Dossier vollständig, keine Punkte "nicht belegbar".
2. QA >= 85, nach der Schleife neu gemessen; höchstens 2 Schleifen.
3. Gegencheck (`tools/gegencheck.py`) Score >= 85, jeder Befund von der Chefredaktion entschieden (übernommen oder verworfen mit Begründung).
4. Linkcheck ohne TOT, Faktencheck ohne "falsch", Legal ohne mittleren oder hohen Punkt, gegenseitige Verlinkung (Muster 06 und 11).
5. Autorenzeile "Redaktion Treppenlift-Magazin, Lehner Lifttechnik (KI-gestützt erstellt und geprüft)" und Abschnitt "So entsteht dieser Artikel"; kein erfundener Personenname.
Bestanden: `tools/publish.sh` (build.py, dist/, Deploy Cloudflare Workers `d01-treppenlift-magazin`, HTTP 200 für Startseite und alle Artikel), läuft am Ende jedes Wochenlaufs, aktiv sobald `redaktion/LIVE` existiert. Nicht bestanden: Status "zurückgestellt" in `redaktion/status.md`, nächster Wochenlauf neuer Versuch mit frischem Dossier, nie halbfertig publizieren.
Ausgabe: Artikel in `dist/` und live, Entscheidung in `log.md` und `entscheidungen.md`.

**E Korrektur/Fehler (automatisch)**
1. Triage des Hinweises oder Befunds im nächsten Lauf (berechtigt, unklar, nicht berechtigt).
2. Bei falschem YMYL-Fakt sofort depublizieren (Prozess F), sonst Korrekturlauf.
3. Fakt gegen Primärquelle prüfen, betroffene Reviews wiederholen.
4. Korrekturhinweis im Artikel mit Datum bei Recht, Förderung, Sicherheit, Preis, plus Changelog im Artikel und in `log.md`.
5. Lehre als Eintrag in `redaktion/lehren-offen.md`; die Chefredakteur-KI übernimmt sie ins `PLAYBOOK.md`.
6. Zweiter Fehler gleichen Typs: Lehre wird Gate (Prüfpunkt in QA-Liste oder Skript).
7. Neu bauen und über `tools/publish.sh` deployen.
Ausgabe: `log.md` (Changelog), `redaktion/entscheidungen.md`, `redaktion/lehren-offen.md`.

**F Depublizieren (automatisch)**
1. Auslöser: falscher oder nicht belegbarer YMYL-Fakt ohne schnelle Korrektur, Rechtsforderung, Abmahnung.
2. Chefredakteur-KI verschiebt den Artikel nach `articles-zurueckgestellt/` (nie `rm`), baut neu (`build.py`) und deployt (`tools/publish.sh`).
3. Legal-Review und Faktencheck laufen neu; der Artikel kommt nach Korrektur und bestandenen Gates (Prozess D) zurück.
4. Links auf den Artikel prüfen und ersetzen, Neubau.
Ausgabe: `redaktion/entscheidungen.md`, `log.md`, `redaktion/status.md`.

## 4. RACI

R = führt aus, A = entscheidet, C = gefragt, I = informiert. Es gibt keine Spalte für Menschen: Alle Entscheidungen trifft die Chefredakteur-KI über automatische Gates.

| Prozess | Chefredakteur-KI | Planer / Analysten | Produktions-Personas | Zweitmodell |
|---|---|---|---|---|
| A Themenplanung | A | R | I | - |
| B Refresh | A | R (Auslöser, Befund) | R | R |
| C Neuer Artikel | A | I | R | R (8b) |
| D Publizieren | A, R (Gates, Einbau, Deploy, Linkcheck) | I | C | C (Gegencheck) |
| E Korrektur | A, R (Triage, Korrekturlauf) | C | R | C |
| F Depublizieren | A, R (Umsetzung, Deploy) | I | C (Legal) | - |

## 5. Entscheidungsregeln

| Regel | Festlegung |
|---|---|
| Priorisierung (höchste zuerst) | 1 Sicherheits-/Rechtsfehler veröffentlicht; 2 Refresh mit gesetzlicher Frist oder Förderänderung, nach Fälligkeit; 3 Refresh mit überschrittenem Review-Termin oder Linkfehlern; 4 Refresh bei Positionsverlust; 5 Neue Themen mit nachgewiesener Nachfrage ohne Kannibalisierung |
| Refresh vor Neu | Refresh mit hohem YMYL-Risiko geht vor jedem neuen Artikel |
| Gleichstand | Höheres YMYL-Risiko zuerst, dann geringere Kosten |
| WIP-Limit | Höchstens 3 Artikel gleichzeitig in Schritt 1-9, davon höchstens 1 YMYL-Refresh gleichzeitig; höchstens 5 Artikel mit Status "zurückgestellt"; sind es mehr, startet nichts Neues außer deren neuem Versuch (Priorität 1 ausgenommen) |
| Gates | Die automatischen Gates aus Prozess D |
| Budget je Artikel | 8-10 Agent-Läufe, 1 Zweitmodell-Aufruf, höchstens 2 DataForSEO-Calls, 15-25 Minuten; ab 150 % Stopp; EUR-Betrag steht im Lauf-Protokoll |
| Budget Refresh | Halber Rahmen |
| Konflikt Reviews | 1 Primärquelle gewinnt; 2 wörtliche Herstellerangabe; 3 im Zweifel vorsichtigere Formulierung; 4 Fehler im Dossier: erst Dossier korrigieren; 5 ohne Quelle entschärfen oder streichen; 6 Begründung in `log.md` und `entscheidungen.md` |

## 6. Rhythmus-Kalender

Die Takte stehen im Abschnitt "Der Redaktionskreislauf". Zusätzlich gelten feste Stichtage:

| Stichtag | Anlass | Betroffene Artikel |
|---|---|---|
| bis 05.01.2027 | Prüfung vor Maschinenverordnung (EU) 2023/1230 | 01, 03, 04, 05, 10, 11 |
| 20.01.2027 | MVO gilt; 14 Tage vorher und nachher prüfen | wie oben |
| 04.01.2027 (Jahreswechsel) | Förderbeträge, BMG-Leistungsübersicht, Titel "2026" auf "2027" | 02, 06, 07, 08 und alle Fundstellen 4.180 EUR |
| April 2027 | Preise, Förderung, Baurecht neu prüfen (Zusage in Artikeln 07 und 11) | 03, 07, 11 |
| Monatlich | KfW 455-B und 159 | 08, 02, 04, 05, 11 |
| Okt und Mai | Plan 8 Wochen voraus vor den Saisonspitzen | `contentplan.md` |

## 7. Aktueller Stand 2026-10-15

Publiziert wird automatisch, sobald ein Artikel die Gates aus Prozess D besteht und `redaktion/LIVE` gesetzt ist. Das fehlende namentliche Autorenprofil ist kein Blocker (siehe Abschnitt 8).

**Top-Prioritäten Refresh (Risiko hoch), Quelle `redaktion/refresh-liste.md`**

| Reihenfolge | Artikel | Score | Termin | Kern |
|---|---|---|---|---|
| 1 | 10 Montage, Vorschriften, Wartung | 78 | 05.01.2027 | Niedrigster Score; MVO-Datum gegen EUR-Lex belegen, BetrSichV-Fristen klären, ÖKO-TEST 2014 ersetzen |
| 2 | 08 Zuschuss 2026 | 86 | monatlich, 04.01.2027 | KfW 455-B/159 laufend, 4.180 EUR, Steuergrenzen, Titel 2027 |
| 3 | 02 Kosten 2026 | 85 | 04.01.2027 | 4.180 EUR und Rechenbeispiel nachrechnen, Preisquellen direkt abrufen |
| 4 | 06 Treppenlift außen | 90 | 04.01.2027 | 4.180 EUR "heute" datieren, Lehner-Widerspruch Stratos NG/A, IP-Klasse |
| 5 | 07 mieten | 85 | 04.01.2027, spätestens April 2027 | Pflegekasse bei Miete klären, Break-even nachrechnen |
| 6 | 03 gebraucht | 86 | 05.01.2027 | MVO bei Gebrauchtliften, Preistabelle, BetrSichV |
| 7 | 11 Außentreppe-Montage | 76 im Review | 05.01.2027, spätestens April 2027 | Liste "An Lehner melden" (11 Punkte), MVO, IP-Klasse |

**Nächste 4 Wochen, Quelle `redaktion/contentplan.md` Abschnitt 2**

| Woche | Query | Typ |
|---|---|---|
| 1 (ab 19.10.) | treppenlift mehrfamilienhaus | neu |
| 2 | treppenlift einbauen vermieter | neu |
| 3 | treppenlift demontieren | neu, Links auf 03, 10 |
| 4 | treppenlift wartungsvertrag | neu mit Abgrenzung zu 10, sonst Ergänzung |


## 8. Bewusst akzeptierte Risiken

| Risiko | Festlegung |
|---|---|
| Kein namentlicher Autor (QRG-Stop-Kriterium "named author") | Bewusst akzeptiert; transparente Autorenzeile und Abschnitt "So entsteht dieser Artikel" |
| Impressum-Pflichtangaben nach MStV und DDG | Liegen bei Lehner |
| Haftung für Inhalte | Liegt bei Lehner als Betreiber des Magazins |

## 9. Orchestrierung für die steuernde KI

| Regel | Festlegung |
|---|---|
| Start | Unabhängige Personas in einer Nachricht parallel starten (z. B. die 5 Reviews, Aktualitäts- und Performance-Analyst) |
| Reihenfolge | Abhängige Schritte nacheinander (Dossier vor Entwurf, FAQ vor Reviews, Gegencheck nach Schleife) |
| Modell | Standardmodell, nie ein anderes Modell an Subagents übergeben |
| Zweitmodell | Nur als Gegencheck über `tools/gegencheck.py` (OpenRouter, eigener Key aus der Umgebung, nie ausgeben) |
| Briefing | Jede Persona liest zuerst `briefing/qrg-briefing.md` und `briefing/tone-of-voice.md` |
| Ergebnisse | Jede Persona schreibt ihre Datei; die steuernde KI liest die Dateien, nicht die Chat-Zusammenfassung |

**Prompt-Vorlage "Redaktionskonferenz"**

```
Rolle: Chefredakteur-KI Treppenlift-Magazin. Takt: <woechentlich|monatlich|quartalsweise>. Datum: <heute>. R=/home/student/Projects/d01-treppenlift-magazin
Lies: R/CHEFREDAKTION.md, R/PLAYBOOK.md (Überschriften), R/redaktion/status.md,
R/redaktion/refresh-liste.md, R/redaktion/contentplan.md, R/redaktion/entscheidungen.md, alle log.md.
1. Starte parallel (Standardmodell): Aktualitäts-Analyst (Trigger, Linkcheck, Fristen bis 05.01.2027),
   Performance-Analyst (nur falls Search-Console-Zugang vorhanden, sonst vermerken).
2. Prüfe WIP-Limit (max. 3) und Artikel mit Status "zurückgestellt" (neuer Versuch mit frischem Dossier).
3. Priorisiere nach Abschnitt 5 (Refresh mit hohem YMYL-Risiko vor Neu), wähle die Aufgaben der Woche.
4. Offene Lehren (redaktion/lehren-offen.md) selbst bewerten und übernehmen.
5. Publizieren: Artikel mit bestandenen Gates über tools/publish.sh deployen (nur wenn redaktion/LIVE existiert).
Schreibe: R/redaktion/status.md (Ampel, Tabelle Artikel | Schritt | Verantwortlich | Blocker | Nächste Aktion | Datum) und hänge Entscheidungen an R/redaktion/entscheidungen.md an.
Schreibe zusätzlich R/redaktion/laeufe/<datum>-<takt>.md und hänge Lehren an R/redaktion/lehren-offen.md an.
Regeln: nichts erfinden, keine Personennamen, nie rm (gio trash), Veröffentlichung nur nach bestandenen Gates (Prozess D), höchstens 1 neuer Entwurf bis Schritt 9.
```

## Betrieb: GitHub Actions + OpenRouter

- Der Prozess läuft unabhängig vom Desktop: Repo github.com/nichtagentur/d01-treppenlift-magazin, Workflow `.github/workflows/redaktion.yml` (wöchentlich Montag 05:00 UTC, dazu manuell per "Run workflow" mit Themen und Anzahl).
- Job `plan`: `pipeline/plan.py` wählt Themen aus `redaktion/contentplan.md` (Prio 1), die nicht in `redaktion/erledigt.txt` stehen.
- Job `artikel` (Matrix, parallel je Thema): `pipeline/run_article.py` führt die Schritte 1-10 aus, mit DeepSeek `deepseek/deepseek-v4.1-flash` über OpenRouter, Web-Plugin für das Dossier und Gegencheck mit `google/gemini-4-argon`.
- Job `publish`: `pipeline/publish.py` baut nur Gate-bestandene Artikel aus `redaktion/live.txt`, entlinkt interne Links auf nicht-live Artikel, veröffentlicht auf Cloudflare Workers `d01-treppenlift-magazin`, prüft HTTP 200, committet zurück ins Repo und schreibt den Bericht nach `redaktion/laeufe/`.
- Gate (Schritt 10) im Code: QA ≥85, Fakten 0 falsch, Legal 0 mittel/hoch, 0 tote Links, Gegencheck ≥85; sonst landet der Artikel in `articles-zurueckgestellt/`.
- Secrets (GitHub Repo-Secrets): `OPENROUTER_API_KEY`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`.
- Lokale Cron-Jobs und `tools/redaktion-lauf.sh` sind abgelöst und nur noch manuell nutzbar.
- Die 11 Altartikel sind nicht live, bis sie per Refresh durch dasselbe Gate gehen.
