# Contentplan Treppenlift-Magazin (Lehner Lifttechnik), Stand 2026-10-15

Quellen: Google Autocomplete live (`rohdaten-autocomplete-2026-10-15.json`, 16 Seeds, kein DataForSEO) plus `research/autocomplete-*.json`, `research/TOP10.md`. Alle Queries sind echte Autocomplete-Vorschläge. Keine neuen Volumenzahlen (nicht erhoben). Bestehend: Artikel 01 Leitfaden, 02 Kosten, 03 gebraucht, 04 Plattformlift, 05 Hublift, 06 außen, 07 mieten, 08 Zuschuss/Förderung, 09 Treppenart/Aufmaß, 10 Montage/Vorschriften/Wartung, 11 Außentreppe-Montage.
Hinweis: "treppenlift tischler", "treppenlift schreiner" und "treppenlift förderung 2027" liefern kein Autocomplete (Befund wie in TOP10.md), deshalb kein Kandidat.

## 1. Themenlücken

| Query | Intent | Zielgruppe | Nähe / Kannibalisierung | Prio | Begründung |
|---|---|---|---|---|---|
| treppenlift mehrfamilienhaus (rechtslage, brandschutz) | informational/Recht | Tischler B2B (Hausverwaltung-Aufträge) | nein (Rand zu 10 Vorschriften) | 1 | 5 Vorschläge in einer Seed, kein Artikel deckt MFH/Brandschutz; hoher Auftragswert |
| treppenlift einbauen vermieter / muss vermieter treppenlift dulden | informational/Recht | Endkunde, Tischler als Berater | nein (07 mieten behandelt Mieten des Lifts, nicht Mieter-Rechte) | 1 | 8 Vorschläge zu Vermieter, klare eigene Intention |
| treppenlift pflegegrad (2, 3) / zuschuss pflegegrad | informational/Förderung | Endkunde | ja, 08 (Variante: Abschnitt/Cluster-Ergänzung) | 2 | Viele Pflegegrad-Varianten, aber Intention nahe 08; nur als Ergänzung mit Link |
| treppenlift demontieren (anleitung) | how-to | Tischler B2B | teils, 10 (Montage), 03 (gebraucht) | 1 | 9 Vorschläge, Rückbau/Wiedereinbau ist Dienstleistung; 10 erwähnt es nicht als Hauptthema |
| treppenlift ankauf | transaktional | Endkunde (Verkäufer), Tischler als Ankäufer | ja, 03 (gebraucht ankauf) | 3 | Fast gleiche Intention wie 03, deshalb nur in 03 erweitern |
| treppenlift montageanleitung (pdf) | navigational/how-to | Tischler B2B | teils, 10 | 2 | Herstellerspezifisch (Lifta, Handicare); eigener Winkel "Montage-Checkliste herstellerneutral" möglich, nichts kopieren |
| treppenlift ohne montage | informational | Endkunde | teils, 10 (Selbsteinbau) | 3 | Verwandt mit "selbst einbauen" in 10; Gefahr der Doppelung |
| treppenlift einbauen dauer | informational | Endkunde/Tischler | teils, 10, 11 | 2 | Eigene Frage, FAQ-Ergänzung oder kurzer Ablauf-Artikel |
| treppenlift nachträglich einbauen | informational | Endkunde | teils, 01/10 | 2 | Eigener Winkel (Altbau, Bestandstreppe), Link auf 09 |
| treppenlift wartung pflicht / wartungsvertrag kosten | informational/Kosten | Tischler B2B (Servicegeschäft) | ja, 10 enthält Wartung | 1 | 4 Vorschläge, Servicegeschäft ist B2B-Kern; als eigener Artikel nur mit klar anderem Winkel (Vertragsmodell, Kalkulation), sonst 10 erweitern |
| plattformlift selber bauen / hublift selber bauen | informational | Endkunde (DIY) | teils, 04, 05 | 2 | Je ein Vorschlag; Gefahrenhinweis, Normen, Haftung als Profi-Winkel |
| plattformlift rollstuhl / treppenlift rollstuhl maße | informational | Endkunde, Tischler | ja, 04 (Plattformlift) | 2 | Hohe Nähe zu 04; Cluster-Ergänzung "Rollstuhl-Maße und Platzbedarf" prüfen |
| treppenlift rollstuhl krankenkasse | informational/Förderung | Endkunde | ja, 08 | 3 | Nur Ergänzung zu 08 |
| treppenlift alternative (für senioren) | informational | Endkunde | nein (01 Leitfaden streift) | 2 | In Autocomplete der Hauptseed, Vergleich Lift, Plattform, Rampe, Hublift stärkt Cluster |
| treppenlift in der nähe / wartung berlin (lokal) | lokal | Endkunde | nein | 3 | Ortsseiten sind hohes Dublettenrisiko und Thin-Content-Risiko; nicht automatisieren |

## 2. Plan nächste 8 Wochen (Saison: vor Januar-Hoch publizieren)

| Woche | Artikel-Query | Typ | Persona-Redakteur |
|---|---|---|---|
| 1 (ab 19.10.) | treppenlift mehrfamilienhaus | neu | Fachredakteur Recht und Bau |
| 2 | treppenlift einbauen vermieter | neu | Fachredakteur Recht und Bau |
| 3 | treppenlift demontieren (Rückbau, Wiedereinbau) | neu, Links auf 03, 10 | Tischler-Praktiker |
| 4 | treppenlift wartungsvertrag (Kalkulation, Pflicht) | neu mit Abgrenzung zu 10, sonst Ergänzung | Servicetechniker-Persona |
| 5 | treppenlift alternative | neu | Produktberater Lehner |
| 6 | treppenlift nachträglich einbauen | neu, Links auf 09 | Tischler-Praktiker |
| 7 | treppenlift pflegegrad | Cluster-Ergänzung zu 08 | Fachredakteur Förderung |
| 8 | treppenlift rollstuhl maße | Cluster-Ergänzung zu 04 | Produktberater Lehner |

Jeder Artikel braucht vor Veröffentlichung die menschliche Freigabe laut PLAYBOOK Schritt 10. Ergänzungen (Prio 3, z. B. ankauf, ohne montage) laufen als Erweiterung bestehender Artikel.

## 3. Wiederholbare Monatsroutine (für eine KI)

**Rhythmus:** am ersten Werktag des Monats, Laufzeit unter 30 Minuten. Zusätzlich Oktober und Mai (vor den Saisonspitzen) Planung 8 Wochen voraus.

**Schritte**
1. Lesen: `research/TOP10.md`, letzten `redaktion/contentplan.md`, alle H1 (`grep "<h1" articles/*.html`), PLAYBOOK Schritt 1.
2. Seeds: die 8 Kernseeds (tischler, montage, plattformlift, hublift, gebraucht, mieten, förderung <Jahr>, wartung) plus 6 Seeds aus dem Vormonat (neue Vorschläge) plus Fragewörter. Autocomplete via `suggestqueries.google.com/complete/search?client=firefox&hl=de&gl=de&q=<seed>`, 0,3-0,4 s Pause, Rohdaten nach `redaktion/rohdaten-autocomplete-<datum>.json`. Kein DataForSEO ohne Freigabe.
3. Neue Queries = nicht im Vormonats-Rohdatensatz und in keiner H1. Nur reale Vorschläge in die Tabelle, nichts erfinden. Leere Seeds als Befund notieren.
4. Kannibalisierung: je Query die Hauptintention mit den H1 (und bei Zweifel dem Artikel-Intro) vergleichen. Gleiche Intention bedeutet erweitern, abgegrenzter Winkel mit gegenseitigen Links, oder verwerfen. Empfehlung in die Tabelle.
5. Priorität: **1** = B2B-Bezug oder Auftragswert hoch UND keine Kannibalisierung UND mehrere Vorschläge im Autocomplete; **2** = Nachfrage klar, aber Teilüberschneidung oder reiner Endkunde mit Beratungsrolle; **3** = Kannibalisierung ja, lokal, Dublettenrisiko oder nur 1 Vorschlag.
6. Saison: Prio-1-Artikel so legen, dass sie 4-6 Wochen vor Januar bzw. August erscheinen.
7. Output: `redaktion/contentplan.md` im obigen Format (Lückentabelle 10-15 Zeilen, 8-Wochen-Plan, Änderungen zum Vormonat in drei Zeilen oben) plus Rohdatendatei. Alte Dateien nie löschen (kein rm), neue mit Datum.
8. Übergabe: die steuernde KI nennt dem Menschen die Prio-1-Themen und die Kannibalisierungsempfehlungen; Fakten-Dossier und Freigabe folgen im PLAYBOOK (Schritte 2 ff.).
