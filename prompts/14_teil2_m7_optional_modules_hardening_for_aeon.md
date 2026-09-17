Auftrag: Teil 2, Milestone 7 ("Optional Modules Hardening") — F08/F09 als
typisierte Module kapseln, TWO_BIT_COPY-Regressionstest ergänzen,
Scope Guards im Code statt nur in der Doku.

## Kontext

F08 (`sheaf_contextuality.md`) und F09 (`pid_redundancy_bottleneck.md`)
existieren bisher NUR als eigenständige Review-Skripte
(`verification/verify_sheaf_contextuality.py`, 6/6;
`verification/verify_pid_rb.py`, 7/7) — anders als `dynamics`,
`closure`, `viability` etc. wurden sie nie in `src/scoped_correspondence/`
produktisiert. Dieser Auftrag holt das nach, ohne die Mathematik neu zu
erfinden — reines Kapseln + zwei konkrete, bereits identifizierte Lücken
schließen (F12, F13).

## Umfang dieses Auftrags

### 1. `contextuality` (F08 kapseln + Scope Guard für F13)

Quelle: `verification/verify_sheaf_contextuality.py`
(`EmpiricalModel`, `contextual_fraction`, `has_global_section`,
`bell_222_scenario`, `classical_factorizable_model`, `pr_box_model`,
`chsh_table_i_model`). Portiere diese Typen/Funktionen 1:1 (gleiche
Zahlen wie im bestehenden Skript) nach `src/scoped_correspondence/
contextuality/core.py`.

**Scope Guard für F13 (bisher nur Prosa in `sheaf_contextuality.md` §6):**
`contextual_fraction(...)` und `has_global_section(...)` bekommen einen
PFLICHT-Parameter `assumes_independent_contexts: bool` (kein stiller
Default). Wenn `False` oder nicht übergeben: `ScopeViolationError` mit
genau dem Risiko aus F13 im Text — "wenn alle Sichten y_α=π_α(z,c,t)
Funktionen desselben angenommenen z sind, existiert die gemeinsame
Verteilung immer trivial; ein positiver CF-Wert wäre dann ein
Modellierungsfehler, keine echte Kontextualität." Der Aufrufer muss
aktiv bestätigen, dass die Kontextverteilungen unabhängig spezifizierte
Primitive sind — das ist keine automatische Prüfung (nicht prüfbar),
sondern eine erzwungene bewusste Entscheidung, analog zu
`ScopeViolationError` bei `observation.retention` für kontinuierliche
Variablen.

### 2. `information_decomposition` (F09 kapseln + TWO_BIT_COPY für F12)

Quelle: `verification/verify_pid_rb.py`
(`pid_atoms_williams_beer`, `i_min_two_sources`, `ei_q_channel`,
`blackwell_redundancy_binary_y`, `rb0_blackwell`). Portiere 1:1 nach
`src/scoped_correspondence/information_decomposition/core.py`.

**TWO_BIT_COPY-Regressionstest (F12):** `rb0_blackwell` ist bisher
explizit auf binäres Y beschränkt (`require(j.shape[2] == 2, ...)`).
Für den TWO_BIT_COPY-Fall (zwei unabhängige faire Bits A,B, Ziel
Y=(A,B), vierwertig) braucht es eine allgemeinere Blackwell-Redundanz
für endliches, nicht-binäres Y — löse das über ein LP (`scipy.optimize.
linprog`, bereits erlaubte Abhängigkeit laut
`requirements_sheaf_pid.txt`), nicht über eine neue Heuristik.
Erwartetes, literaturbekanntes Ergebnis (Harder/Salge/Polani 2013;
Kolchinsky 2405.07665): Williams-Beer `I_min` liefert `Red=1` Bit
(irreführend), Blackwell/Kolchinsky-RB(0) liefert korrekt `0`. **Beide
Werte nebeneinander berichten, nicht nur einen** — gleiches Prinzip wie
`EI_q` "daneben statt gleichgesetzt" bei den bestehenden sechs Fällen.

### 3. Legacy-Skripte bleiben unverändert

`verify_sheaf_contextuality.py` und `verify_pid_rb.py` selbst werden
NICHT geändert — sie bleiben als historische Review-Artefakte stehen
(Präzedenzfall: `legacy/adapters.py` verändert auch nie die bestehenden
Module, nur additive Brücken). Die neuen `verify_contextuality_core.py`
/ `verify_information_decomposition_core.py` prüfen die neuen Module
GEGEN die bestehenden `verify_sheaf_contextuality_results.json` (6
Szenarien) bzw. `verify_pid_rb_results.json` (7 Prüfungen) — Zahlen
müssen exakt übereinstimmen, plus die neue achte TWO_BIT_COPY-Prüfung.

### 4. Explizit NICHT Teil dieses Auftrags

- **Keine Mutation von `sheaf_contextuality.md` oder
  `pid_redundancy_bottleneck.md`** (beide gehören zu den acht
  Kerndokumenten) — auch kein Verweis-Satz auf das neue Modul. Falls
  gewünscht, ist das ein separater, von Johann freizugebender
  Folgeauftrag.
- Keine Verallgemeinerung über zwei Quellen hinaus (kein N-Quellen-PID).
- Keine neue Literaturrecherche — nur die bereits zitierten Quellen
  (Williams-Beer 2010, Kolchinsky 2024, Harder/Salge/Polani 2013,
  Abramsky-Brandenburger 2011, Abramsky-Barbosa-Mansfield 2017).
- Änderungen an `correspondence/`, `observation/`, `dynamics/`,
  `coupling/`, `closure/`, `viability/`, `membership/`,
  `identifiability/`, `validation/` — nicht anfassen.

## Verifikation

`verify_contextuality_core.py` gegen `verify_sheaf_contextuality_results.json`
(s01-s06, exakte Übereinstimmung) plus Test, dass `ScopeViolationError`
bei `assumes_independent_contexts=False`/fehlend tatsächlich auslöst.

`verify_information_decomposition_core.py` gegen
`verify_pid_rb_results.json` (p01-p07, exakte Übereinstimmung) plus die
neue TWO_BIT_COPY-Prüfung (`Red_williams_beer=1`, `RB0_blackwell=0`,
beide im Bericht).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. Zwei `verify_*.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF — Legacy-Werte
   exakt reproduziert, TWO_BIT_COPY-Werte neu und nachvollziehbar.
4. Explizites Mapping auf `sheaf_contextuality.md` / F13 bzw.
   `pid_redundancy_bottleneck.md` / F12 — jede neue Funktion referenziert
   ihre Herkunftsstelle.
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente (explizit inklusive `sheaf_contextuality.md`
   und `pid_redundancy_bottleneck.md`, siehe Abschnitt 4 oben).
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m7-optional-modules-hardening` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Claude
reviewed (Diff, Skripte selbst nachrechnen, TWO_BIT_COPY-LP von Hand
gegenprüfen, ScopeViolationError-Guard stichprobenartig testen) und
merged erst nach Johanns OK.
