Auftrag: Teil 2, Milestone 21 ("Formal Reduction Error Bounds") —
natürliche Erweiterung von `closure`, aus `ChatGPTAstra3.md` (Michel &
Siegle, DOI 10.1016/j.peva.2024.102464 / arXiv 2403.07618 — dieselbe
Quelle, die bereits für die kontinuierliche Generator-Lumpability-
Bedingung in M11 verwendet wurde, hier aber eine ANDERE, stärkere
Aussage: allgemeine Fehlerschranken für approximative Aggregation).

## Kontext

`closure.propagated_error_bound(delta_cl, k)` (M3, gemergt) liefert den
ELEMENTAREN Horizontbund `min(1, k·δ_cl)` — eine einfache, aber lockere
Schranke. Michel & Siegle (2024/2025) entwickeln STÄRKERE, formale
Fehlergrenzen für die Zustandsreduktion diskreter und kontinuierlicher
Markov-Ketten (Aggregation/Lumpability als Spezialfall): im diskreten
Fall Grenzen für den schrittweisen Fehlerzuwachs, im kontinuierlichen
Fall für die Fehlerwachstumsrate.

**Wichtig:** die exakte Formel/das exakte Theorem MUSS aus der
Primärquelle (arXiv:2403.07618) entnommen werden — nicht erfinden. Gib
im Docstring die konkrete Theorem-/Gleichungsnummer aus dem Paper an.

## Umfang dieses Auftrags

### 1. `closure.error_bounds.ReductionErrorBound`

Typisiert: `horizon` (int oder float), `bound` (float), `norm` (str,
z.B. `"TV"`), `theorem` (Referenz auf die genaue Stelle im Paper),
`assumptions`.

### 2. `closure.error_bounds.transient_reduction_bound(...)` /
### `closure.error_bounds.stationary_reduction_bound(...)`

Implementiert die tatsächliche(n) Formel(n) aus der Quelle für
transiente bzw. stationäre Fehlerentwicklung. Signatur nach Bedarf der
Formel wählen — an die tatsächliche Herleitung anpassen, nicht an
diesen Prompt.

### 3. Pflicht-Kompatibilitätsprüfung

Für mindestens einen Fall MUSS gezeigt werden: die neue Schranke ist
`<=` der bereits gemergten `propagated_error_bound(delta_cl, k)` bei
identischen Eingaben (sie ist "stärker", nicht nur "anders") — ODER,
falls die Bedingungen unterschiedlich sind (z.B. andere Norm/andere
Annahmen), dies EXPLIZIT im Bericht begründen statt stillschweigend zu
vergleichen.

### 4. Durchgerechnetes Beispiel

Mindestens ein kleines Beispiel aus der Quelle (oder ein selbst
konstruiertes, das die Formel exakt reproduziert) mit Zahlen aus dem
Skriptlauf — kein erfundener Referenzwert.

### 5. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `closure/core.py` — nur Aufruf von
  `propagated_error_bound`/`is_exact_closure`/`closure_error` zur
  Kompatibilitätsprüfung.
- Keine Vermischung mit der bereits gemergten CTMC-Generator-
  Lumpability (M11, `closure/generator_lumpability.py`) — eigenes,
  separates Modul, auch wenn dieselbe Primärquelle zitiert wird.
- Keine allgemeine Markov-Ketten-Bibliothek — nur die konkrete(n)
  Fehlerschranken-Formel(n).

## Verifikation

`verify_error_bounds_core.py`: (1) Formel korrekt aus der Quelle
reproduziert (Zahlen aus dem Skriptlauf), (2) Vergleich gegen
`propagated_error_bound` wie oben, (3) mindestens ein Grenzfall
(`k=0` oder `delta_cl=0` — Schranke muss `0` bzw. sinnvoll degenerieren).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_error_bounds_core.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Michel & Siegle (DOI/arXiv oben, konkrete
   Theorem-Stelle) und `closure/core.py`s `propagated_error_bound`.
5. KEINE Mutation von FORMALISM.md, `emergence_and_closure.md` oder
   einem der anderen sechs Kerndokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m21-formal-reduction-error-bounds` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 22 (`observation`), 23 (`identifiability`) und
24 (`contextuality`) bearbeitet werden. Bitte NICHT
`src/scoped_correspondence/__init__.py` anfassen. Claude reviewed und
merged erst nach Johanns OK.
