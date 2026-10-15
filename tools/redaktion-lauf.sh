#!/usr/bin/env bash
# Wiederkehrender Redaktionslauf der Chefredakteur-KI. Aufruf: tools/redaktion-lauf.sh woechentlich|monatlich|quartalsweise
# Startet Claude Code headless mit dem Skill chefredaktion; der Wochenlauf publiziert danach automatisch (tools/publish.sh).
set -euo pipefail
T="${1:?takt fehlt}"
P="$(cd "$(dirname "$0")/.." && pwd)"
source "$HOME/.env" 2>/dev/null || true
export PATH="/home/linuxbrew/.linuxbrew/bin:$HOME/bin:/usr/local/bin:/usr/bin:/bin"
D="$(date +%F)"; OUT="$P/redaktion/laeufe/$D-$T.md"
cd "$P"
case "$T" in
  woechentlich)  AUF="Redaktionskonferenz (CHEFREDAKTION.md, Takt woechentlich): Stand pruefen, redaktion/status.md und redaktion/entscheidungen.md aktualisieren, hoechstens 1 Artikel (neu oder Refresh, nach Prioritaetsregeln) nach PLAYBOOK.md bis Schritt 9 bearbeiten. Den Artikel nur bei bestandenem Publikations-Gate (PLAYBOOK Schritt 10) nach articles/ einbauen." ;;
  monatlich)     AUF="Monatlicher Planungslauf (CHEFREDAKTION.md, Takt monatlich): Content-Planer und Aktualitaets-Analyst als parallele Subagents; redaktion/contentplan.md und redaktion/refresh-liste.md aktualisieren; Entscheidungen in redaktion/entscheidungen.md." ;;
  quartalsweise) AUF="Quartals-Audit (CHEFREDAKTION.md, Takt quartalsweise): tools/linkcheck.sh ueber alle articles/*.html, QA-Stichprobe von 3 Artikeln, Lehren in PLAYBOOK.md und CHEFREDAKTION.md einarbeiten." ;;
  *) echo "unbekannter Takt: $T"; exit 1 ;;
esac
claude -p --dangerously-skip-permissions "Du bist die Chefredakteur-KI. Nutze den Skill chefredaktion. $AUF Schreibe am Ende einen Bericht (Was getan, Entscheidungen, zurueckgestellte Artikel, Gate-Ergebnisse, Lehren) nach $OUT." >> "$P/redaktion/laeufe/cron.log" 2>&1
[ "$T" = woechentlich ] && "$P/tools/publish.sh" >> "$P/redaktion/laeufe/cron.log" 2>&1 || true
