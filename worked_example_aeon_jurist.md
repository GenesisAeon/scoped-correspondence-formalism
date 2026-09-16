# Durchgespielt: aeon-jurist (P55) -- Phase 1, Beispiel 2/3, Ersatz (2026-09-15)

Kein `DISCLAIMER.md` gefunden -- keine Policy-Ausnahme, Analyse regulär
durchgeführt. Alle Aussagen aus gelesenem Code (`system.py`,
`classifier.py`, `precedents.py`).

## Ergebnis: keine Individuation möglich -- vierte Kategorie: statischer Klassifikator ohne Zeitachse

`PersonhoodClassifier` ist ein TF-IDF-Ähnlichkeits-Retrieval + fixes
Subjekt-Lookup (`_LEVEL_BY_SUBJECT`) -- eine EINMALIGE Klassifikations-
funktion (Anfrage rein, `Finding` raus), keine Trajektorie, kein
Kontrollparameter, keine Zeitentwicklung. Unser Individuationskriterium
(Excess-S>0 aus komponierter Information) braucht eine Zeitachse, um S
überhaupt zu definieren -- die gibt es hier nicht.

**Damit vierte Enumerations-Kategorie bestätigt** (nach: echtes System /
reine Projektion / Engine-ohne-eigene-Trajektorie): **statischer
Ein-Schuss-Klassifikator, S/K/R/V nicht anwendbar, weil keine Zeitachse
existiert.** Kein Fehler der Methodik, sondern ein legitimer,
unspektakulärer Ausgang.

## Bemerkenswert: das Paket ist bereits vorbildlich ehrlich

`_build_utac_state()` setzt `H_star=0.7` mit dem Kommentar **"invented
threshold, not from the original TS code"** -- eine explizite, im Code
selbst stehende Kennzeichnung eines unbegründeten Werts, exakt die Art
von Ehrlichkeit, die unser `evidence_status`/`derivation_type`-System in
`semantic-map` erzwingen soll. Ebenso: der Modul-Docstring von
`system.py` sagt selbst, die CREP/UTAC-Zuordnung sei "a new interpretive
layer added for this package," nicht Teil des Original-Algorithmus.

Auch der Klassifikator selbst ist selbstkritisch dokumentiert: das Level
(P0/P1/P2) ist ein FESTES Lookup auf `subject`, nicht aus der
Ähnlichkeitssuche abgeleitet -- mit dem expliziten Beispiel, dass eine
"ai"-Anfrage immer P2 bekommt, obwohl der einzige KI-Präzedenzfall
(EU AI Act) explizit NICHT gewährt wurde. Das steht so im Docstring, nicht
von mir neu gefunden -- das Paket dokumentiert seine eigene Schwäche
bereits selbst.

## Konsequenz für die Methodik

Keine Kopplungsmatrix, kein Latitude/Precariousness hier -- dieses Paket
trägt nichts zu den entsprechenden Go/No-Go-Kriterien bei, zeigt aber:
(a) die Enumeration muss "keine Zeitachse -> nicht anwendbar" als
regulären, sauberen Ausgang kennen, und (b) es lohnt sich, bei jedem
Paket zu prüfen, ob es (wie hier) bereits selbst ehrlich über invented
constants/Interpretationsschichten Auskunft gibt -- solche Stellen sind
wertvolle Vorbilder für den Rest des Ökosystems, nicht nur Fundstellen.
