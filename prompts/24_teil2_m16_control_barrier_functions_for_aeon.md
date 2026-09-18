Auftrag: Teil 2, Milestone 16 ("Control Barrier Functions") —
natürliche Erweiterung von `viability`, aus zwei unabhängig
konvergierenden DeepResearch-Antworten (`ChatGPTAstra3.md`: Ames, Xu,
Grizzle & Tabuada 2017, DOI 10.1109/TAC.2016.2638961; der
`.docx`-Bericht: Ames et al. 2019, ECC-Survey "Control Barrier
Functions: Theory and Applications" — beide von Claude gegen die
Quellen geprüft, echte, unterschiedliche Arbeiten, keine Verwechslung).

## Kontext

`viability` (M3, gemergt) behandelt bisher nur diskrete/punktweise
Fälle (`has_safe_transfer`, `shared_budget_conflict`). Control Barrier
Functions (CBF) übertragen "sichere Menge bleibt invariant" auf
zeitkontinuierliche, steuerungsaffine Systeme `ẋ=f(x)+g(x)u`. Für eine
sichere Menge `C={x: h(x)≥0}` mit differenzierbarem `h` ist die
Zeroing-CBF-Bedingung:

\[
L_f h(x) + L_g h(x)\,u + \alpha(h(x)) \ge 0,
\]

wobei `L_f h`, `L_g h` die Lie-Ableitungen entlang `f`, `g` sind und
`α` eine Klasse-K-Funktion (hier: `α(h)=h`, linear).

## Umfang dieses Auftrags

### 1. `viability.control_barrier.BarrierFunction`

Typisiert `h: Callable`, `alpha: Callable` (Klasse-K-Funktion, hier
linear `alpha(h)=h` als einziger in diesem Auftrag abgedeckter Fall).

### 2. `viability.control_barrier.cbf_condition(L_f_h, L_g_h, u, alpha_h)`

Prüft `L_f_h + L_g_h*u + alpha_h >= 0` — reiner Ungleichheitscheck mit
bereits berechneten Lie-Ableitungswerten (kein symbolisches
Differenzieren nötig für dieses Milestone).

### 3. `viability.control_barrier.admissible_controls_cbf(...)` /
### `verify_forward_invariance(...)`

Für das skalare System `ẋ=u`, `h(x)=x`, `α(h)=h`: `L_f h=0` (da
`f=0`), `L_g h=1` (da `h=x`, `dh/dx=1`, `g=1`). Bedingung: `u+x>=0`.

### 4. Durchgerechnetes Beispiel (bereits von Claude bestätigt)

Bei `x=0.2`:
- `u=-0.1`: `-0.1+0.2=0.1>=0` → zulässig (sicher).
- `u=-0.3`: `-0.3+0.2=-0.1<0` → unzulässig (verlässt die sichere Menge).

Beide Fälle im Skript exakt reproduzieren, `BarrierCertificate` mit
`safe: bool`, `margin: float` zurückgeben.

### 5. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `viability/core.py` — nur neues, separates Modul
  `viability/control_barrier.py`.
- Kein Quadratic-Programming-Löser für die minimal-invasive
  CBF-QP-Steuerung — nur der Zulässigkeitscheck einer gegebenen
  Steuerung `u`.
- Keine mehrdimensionalen Systeme, keine nichtlinearen `α` — nur der
  skalare Fall mit linearem `α(h)=h`.
- Keine Verbindung zum bestehenden `has_safe_transfer`-Satz (M3) als
  neue gemeinsame Formel — beide bleiben getrennte Zertifikate für
  unterschiedliche mathematische Fragen (diskrete Eingriffsübertragung
  vs. kontinuierliche Vorwärtsinvarianz).

## Verifikation

`verify_control_barrier_core.py`: keine bestehende Legacy-Prüfung —
beide Fälle oben mit Zahlen aus dem Skriptlauf, plus mindestens ein
weiterer `x`-Wert zur Gegenprobe.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_control_barrier_core.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Ames et al. 2017/2019 (Quellen oben) und
   `viability/core.py`.
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m16-control-barrier-functions` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 14 (`dynamics`) und Milestone 15 (`coupling`)
bearbeitet werden. Package-root `src/scoped_correspondence/__init__.py`
bitte NICHT anfassen (Konfliktvermeidung, wie bei M11–M13). Claude
reviewed jeden Branch einzeln und merged erst nach Johanns OK.
