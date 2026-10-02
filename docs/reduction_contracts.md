# Vorhandene Reduktionsschranken als Verträge (J11)

Paket J11 aus [`SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md`](../SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md),
Plan §17. Code: `src/scoped_correspondence/closure/contract_adapter.py`.
Prüfung: `verification/verify_reduction_contracts.py` (math). Lizenz der
Dokumentation: CC BY 4.0.

## 1. Zweck und Abgrenzung

J11 verbindet Reduktion, Fehlergrenze, Beobachtungsgröße und zulässige
Entscheidung durchgehend. Es **baut keinen zweiten Solver**: Die
Schranken von Michel & Siegle (2024, S16) aus `closure/error_bounds.py`
werden unverändert aufgerufen. Neu sind nur die Vertragsform, die
exakten Voraussetzungsprüfungen und der Anschluss an die J4-Komposition.

Für Zeilenverteilungen und Lifting $A$ (reduziert → voll):

$$\lVert p_0P^k-\pi_0\Pi^kA\rVert_1\le\lVert\pi_0A-p_0\rVert_1+k\,\lVert\Pi A-AP\rVert_\infty$$

(Theorem 4.3; im kontinuierlichen Fall Theorem 5.3 mit Generatoren und
$t$). Die Matrix-$\infty$-Norm ist die **maximale absolute Zeilensumme**.

## 2. Zwei verschiedene Zahlen

| Wert | Herkunft | Status |
|---|---|---|
| `float_bound` | bestehendes `transient_reduction_bound` (NumPy) | `floating_point_estimate` — eine Gleitkommaberechnung einer theoretischen Schranke ist ohne Rundungsanalyse **keine** validierte Einschließung |
| `exact_bound` | dieselbe geschlossene Formel, exakt in `Fraction` ausgewertet, nachdem die Voraussetzungen exakt geprüft wurden | `proved`, `exact_rational` |

Die exakte Auswertung betrifft nur die Schrankenformel (zwei Normen), nicht
das Reduktionsverfahren. Beide Werte stehen getrennt im Bericht; eine
Abweichung zwischen ihnen würde als Warnung gemeldet. Bei Gleitkomma-
eingaben gibt es nur den Schätzwert und das Urteil `undecided`.

Bei exakten diskreten Eingaben wird zusätzlich der **tatsächliche Fehler**
am Horizont exakt berechnet und gegen die Schranke geprüft (eine
Überschreitung wäre ein interner Fehler: Voraussetzungen oder
Orientierung falsch).

## 3. Geprüfte Voraussetzungen

- **Orientierung:** Zeilenvektorkonvention. $P$ und $\Pi$ müssen
  zeilenstochastisch (DTMC) bzw. Generatoren mit Zeilensumme 0 (CTMC)
  sein. Summieren nur die **Spalten** zum Ziel, meldet der Adapter einen
  möglichen Orientierungsfehler (transponiert) — er transponiert nicht
  still.
- **Formen:** $P$: voll×voll, $\Pi$: red×red, $A$: red×voll, passend zu
  den deklarierten Zustandsnamen.
- **Item-3-Voraussetzung:** $\pi_0$ ist ein Wahrscheinlichkeitsvektor.
- **Lifting:** Theorem 4.3 braucht kein stochastisches $A$. Die
  Aussage $\mathrm{TV}=\tfrac12\lVert\cdot\rVert_1$ gilt aber nur für
  Differenzen von Wahrscheinlichkeitsvektoren; eine TV-Schranke wird
  daher nur mit zeilenstochastischem $A$ und Wahrscheinlichkeitsvektor
  $p_0$ ausgegeben, sonst abgelehnt. (Die bestehende Funktion rechnet TV
  ohne diese Prüfung als halbe L1-Schranke — im Adapter abgefangen, an
  der bestehenden Funktion nichts geändert.)
- **Anfangsfehler** $\lVert\pi_0A-p_0\rVert_1$ geht exakt ein.
- **Zeitskala:** DTMC nur mit Uhr `steps` und ganzzahligem Horizont,
  CTMC nur mit kontinuierlicher Uhr. Bei jeder Verletzung wird die
  bestehende Float-Funktion gar nicht erst aufgerufen (ihre eigenen
  Rückfallformen würden sonst eine Zahl für einen Vertrag mit verletzten
  Voraussetzungen liefern).

## 4. Anschluss an Beobachtung und Entscheidung (über J4)

`reduction_link` macht aus einem **exakt bewiesenen** Ergebnis einen
J4-`CorrespondenceLink` „reduzierte Verteilung → volle Verteilung“
($\pi\mapsto\pi A$) mit der Reduktionsschranke als Flussfehler.
`observation_link` beschreibt eine lineare Beobachtung $y=f\cdot p$ mit
dem exakten Hölder-Zertifikat $|f\cdot e|\le\max_i|f_i|\,\lVert e\rVert_1$
(bei TV doppelt). `compose_correspondences` liefert daraus die Schranke
für die Beobachtungsgröße und prüft dabei Zustandsnamen und Uhren:
inkompatible Zwischenzustände oder Zeitskalen ergeben `incompatible`.

Ohne einen solchen deklarierten Beobachtungsoperator mit Normschranke
entsteht **keine** automatische Garantie für eine nachgelagerte
Sicherheitsentscheidung.

## 5. Kontrollen

- **J-C22** (identischer Zustandsraum, Lifting $I$):
  $\lVert Q-P\rVert_\infty=1/5$, $p_0P^2=(33/50,17/50)$,
  $p_0Q^2=(11/20,9/20)$; L1-Fehler $11/50\le2/5$, TV $11/100\le1/5$;
  bestehende Float-Funktion stimmt überein. Dieser Fall prüft Norm und
  Propagation ohne echte Dimensionsreduktion.
- **Echter Reduktionsfall** (`paper_example_matrices`, 3 → 2 Zustände):
  $\lVert\Pi A-AP\rVert_\infty=1/4$, Schranke $k/4=1$ bei $k=4$, exakter
  Fehler darunter; vollständiger Vertrag mit allen Voraussetzungen.
  Zusammengesetzt mit der Beobachtung $f=(0,1,2)$ ergibt sich die
  Schranke $2$ für $|f\cdot e_4|$, die der exakte Beobachtungsfehler
  einhält.
- CTMC-Fall mit Generatoren: $t\lVert\Theta-Q\rVert_\infty=\tfrac12\cdot2=1$.

## 6. Quelle

S16 Michel & Siegle (2024), *Formal Error Bounds for the State Space
Reduction of Markov Chains* — Links siehe Plan §21 und
`closure/error_bounds.py` (`SOURCE`).
