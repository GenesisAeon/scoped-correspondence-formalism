Auftrag: Teil 2, Milestone 10 ("Approximation Certificates") — natürliche
Erweiterung von `correspondence`, aus einer unabhängig geprüften
DeepResearch-Recherche (`prompts/Answers/ChatGPTAstra3.md`, Zitate und
Rechenbeispiele von Claude unabhängig verifiziert — 12/12 Quellen echt
und zutreffend, alle Zahlenbeispiele von Hand nachgerechnet).

## Kontext

`correspondence.Correspondence` (M1, gemergt) hat bereits
`conjugacy_residual`/`verify_conjugacy` — diese verlangen exakte
Übereinstimmung (`ErrorMetric.near`, Toleranz nahe Null). Girard &
Pappas (2007, DOI 10.1109/TAC.2007.895849, "Approximation Metrics for
Discrete and Continuous Systems") definieren **approximate simulation**
über eine Pseudometrik mit explizitem Fehlerbudget `ε`, wobei die exakte
Relation der Nullfehler-Spezialfall ist. Das passt direkt auf den
bestehenden Kern `T∘Φ_j^t≈Φ_k^{ct}∘T`, OHNE eine neue Modulhierarchie
zu brauchen — `conjugacy_residual` liefert bereits die punktweise
Abweichung, es fehlt nur die Toleranz-Interpretation als Zertifikat.

**Wichtige Abgrenzung (nicht überbehaupten):** Girard & Pappas' voller
Begriff ist **relational** — er erlaubt eine beliebige Relation
zwischen Zuständen, nicht nur eine feste Abbildung `T`. Dieser Auftrag
implementiert NUR den **Spezialfall mit fester, bereits gegebener
`StateMap T`** (das ist alles, was der bestehende `Correspondence`-Kern
hergibt). Das Zertifikat beweist NICHT die Existenz einer allgemeinen
Simulationsrelation — das muss im Docstring und im Bericht explizit
stehen, analog zum "reiner Strukturtest"-Disclaimer bei
`check_generic_structure`.

## Umfang dieses Auftrags

### 1. `correspondence.approximation.ApproximationCertificate`

```python
@dataclass(frozen=True)
class ApproximationCertificate:
    epsilon: float
    max_residual: float
    ok: bool  # max_residual <= epsilon
    relation_kind: str  # "fixed_map_bound" (NICHT "bisimulation"/"simulation")
    scope: Scope
    assumptions: tuple[str, ...]
    residuals: tuple[Residual, ...]
    source: "Girard & Pappas 2007, DOI 10.1109/TAC.2007.895849"
```

`relation_kind` MUSS `"fixed_map_bound"` oder vergleichbar explizit
einschränkend heißen — NICHT `"simulation"` oder `"bisimulation"`, da
der volle Vertrag (beliebige Relation) hier nicht geprüft wird.

### 2. `correspondence.approximation.verify_approximate_simulation(...)`

Ruft **ausschließlich** die bereits gemergten
`Correspondence.conjugacy_residual`/`verify_conjugacy` auf (KEINE
Änderung an `correspondence/contract.py`) und interpretiert das
Ergebnis gegen ein Toleranzbudget `epsilon` statt gegen Null:

```python
def verify_approximate_simulation(
    correspondence: Correspondence,
    states: Sequence[State],
    times: Sequence[float],
    epsilon: float,
) -> ApproximationCertificate: ...
```

### 3. Durchgerechnetes Beispiel (aus `ChatGPTAstra3.md`, von Claude
### bereits von Hand bestätigt — im Skript exakt reproduzieren)

\[
\dot x=-x,\qquad \dot y=-y+0.1,\qquad x(0)=y(0)=0.
\]

Exakte Lösungen: `x(t)=0`, `y(t)=0.1(1-e^{-t})`. Damit
`|x(t)-y(t)|=0.1(1-e^{-t})≤0.1` für alle `t≥0` (Grenzwert bei
`t→∞`, nie überschritten). Baue `Correspondence` mit
`source.flow`/`target.flow` aus den exakten Lösungen (nicht
numerisch integrieren — die Analytik ist bereits gegeben),
`state_map=StateMap(lambda x: x)` (Identität), und zeige:
- `epsilon=0.1`: Zertifikat `ok=True` für ein Zeitraster `t∈[0,10]`.
- `epsilon=0.05`: Zertifikat `ok=False` (da die Abweichung sich `0.1`
  nähert, für hinreichend große `t` wird `0.05` überschritten) —
  zeigt, dass eine engere Toleranz denselben Fall zu Recht ablehnt.

### 4. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `correspondence/contract.py` — nur Aufruf.
- Keine allgemeine relationale Simulationsprüfung (beliebige Relation
  statt fester `T`) — das wäre der volle Girard-Pappas-Vertrag, hier
  nur der Spezialfall mit fester Abbildung.
- Kein `RelationKind`-Enum oder sonstige Typ-Umbauten an
  `CorrespondenceReport`/`Residual`/`ErrorMetric` — das ist laut
  `ChatGPTAstra3.md` ein API-Freeze-Thema vor `1.0.0`, kein
  Zwischenschritt.
- Keine Umbenennung von `thermo`, `conjugacy_residual` oder
  `ErrorMetric` — separates, späteres Thema.

## Verifikation

`verify_approximation_core.py`: keine bestehende Legacy-Prüfung (neues
Konzept, wie schon bei `membership`/`metarules`) — die zwei Fälle oben
(`epsilon=0.1` → `ok=True`, `epsilon=0.05` → `ok=False`) mit Zahlen aus
dem Skriptlauf, plus ein Nullfehler-Fall (`source.flow==target.flow`,
identische Zustandsräume) als Kontrollprüfung
(`max_residual` exakt `0`, jedes `epsilon≥0` liefert `ok=True`).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_approximation_core.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Girard & Pappas 2007 (DOI oben) und
   FORMALISM.md §1 / `correspondence/contract.py`.
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m10-approximation-certificates` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Claude
reviewed (Diff, Skript selbst nachrechnen, beide Epsilon-Fälle von Hand
gegenprüfen) und merged erst nach Johanns OK.
