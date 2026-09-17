Auftrag: Teil 2, Milestone 11 ("Continuous-Time Markov Generator
Lumpability") — natürliche Erweiterung von `closure`, aus einer
unabhängig geprüften DeepResearch-Recherche (Gemini,
`prompts/Answers/Mathematische Erweiterungen Scoped Correspondence.docx`
— Zitate von Claude unabhängig gegen DOI/arXiv geprüft, alle echt und
zutreffend).

## Kontext

`closure.is_exact_closure`/`closure_error` (M3, gemergt) prüfen die
DISKRETE Bedingung `PC=CQ` für Übergangsmatrizen. Buchholz (1994, DOI
10.1017/S0021900200107338, "Exact and Ordinary Lumpability in Finite
Markov Chains") und Michel & Siegle (bereits verifiziert, DOI
10.1016/j.peva.2024.102464 / arXiv 2403.07618 — deckt explizit auch den
zeitkontinuierlichen Fall ab) übertragen dieselbe Idee auf
zeitkontinuierliche Markov-Ketten (CTMC): für einen Generator (Raten-
matrix) `Q` mit Zeilensumme 0 gilt exakte Lumpability, wenn ein
Makro-Generator `Q_macro` existiert mit

\[
Q\,C = C\,Q_{macro}
\]

(dieselbe Kommutativitätsform wie `PC=CQ`, nur mit Generator statt
Übergangsmatrix — Ratenmatrix statt Sprungwahrscheinlichkeiten).

## Umfang dieses Auftrags

### 1. `closure.generator_lumpability.is_exact_generator_lumpability(Q, C, Q_macro, tol)`

Prüft `Q@C == C@Q_macro` exakt (analog zu `is_exact_closure`, aber für
Generatoren). Zusätzliche Validierung: `Q`-Zeilensummen `==0`
(Generator-Eigenschaft), `Q`-Außerdiagonalelemente `>=0`.

### 2. `closure.generator_lumpability.generator_closure_error(Q, C, Q_macro)`

Fehlermaß `max_i |(QC)_i - (CQ_macro)_i|_∞` (kein TV-Maß wie beim
diskreten Fall — Generatoren sind keine Wahrscheinlichkeiten, daher
Betrag statt TV; im Docstring begründen).

### 3. Durchgerechnetes Beispiel (frisch konstruiert — keine bestehende
### Legacy-Zahl für diesen Fall)

Baue ein 3-Zustand-Mikrosystem mit explizitem Generator `Q` (Zeilen-
summe 0, off-diagonal ≥0) und `partition_matrix([0,0,1])` (bereits
gemergt, nur Aufruf — Zustände 0,1 zu Makrozustand A, Zustand 2 zu
Makrozustand B). Zwei Fälle:
- **Exakt lumpable:** `Q` so konstruiert, dass Zustände 0 und 1
  identische Übergangsraten in Zustand 2 haben (und umgekehrt
  symmetrisch) → `Q@C == C@Q_macro` exakt, `generator_closure_error==0`.
- **Nicht lumpable:** eine Variante von `Q`, bei der Zustände 0 und 1
  unterschiedliche Raten in Zustand 2 haben → Fehler `>0`, konkrete
  Zahl aus dem Skriptlauf.

### 4. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `closure/core.py` — nur Aufruf von
  `partition_matrix` (M3, gemergt).
- Keine Verallgemeinerung auf approximative CTMC-Fehlerschranken (das
  wäre ein separates, größeres Thema aus Astra3s "Formal Reduction
  Error Bounds"-Vorschlag für `closure` — eigener, späterer Auftrag,
  hier nicht mit hineinnehmen).
- Keine Änderung an `coupling/`, `validation/` oder einem anderen
  Modul.

## Verifikation

`verify_generator_lumpability_core.py`: keine bestehende Legacy-
Prüfung (frisches Beispiel wie bei `membership`/`metarules`). Beide
Fälle (exakt / nicht lumpable) mit Zahlen aus dem Skriptlauf, plus
Validierung der Generator-Eigenschaften (Zeilensumme 0, off-diagonal
≥0) als eigene Prüfung.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_generator_lumpability_core.py` mit reproduzierbarem
   JSON-Report unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Buchholz 1994 / Michel & Siegle (DOI oben)
   und `closure/core.py`s `is_exact_closure`/`closure_error`.
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m11-generator-lumpability` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Dieser
Auftrag kann PARALLEL zu Milestone 12 (`coupling`) und Milestone 13
(`validation`) bearbeitet werden — unterschiedliche Module, kein
Konflikt. Claude reviewed jeden Branch einzeln und merged erst nach
Johanns OK.
