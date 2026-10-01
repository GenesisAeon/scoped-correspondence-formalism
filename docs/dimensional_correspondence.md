# Dimensionen, Einheiten und Buckingham-Π (J2)

Paket J2 aus [`SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md`](../SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md),
Plan §8. Code: `src/scoped_correspondence/dimensions/core.py`,
`src/scoped_correspondence/dimensions/pi_groups.py`. Prüfung:
`verification/verify_dimensional_analysis.py` (math). Lizenz der
Dokumentation: CC BY 4.0.

## 1. Drei getrennte Begriffe

| Begriff | Objekt | Beispiel | Gleichheit bedeutet |
|---|---|---|---|
| Dimension | `Dimension` — rationale Exponenten über $(M,L,T,\Theta,I,N,J)$ | Meter und Kilometer: beide $L$ | gleiche physikalische Art von Größe *im Sinne der Dimensionsanalyse* |
| Einheit | `Unit` — Skala (und ggf. Offset) gegenüber der kohärenten SI-Einheit | km: Skala 1000 | gleiche Zahl bei gleicher Größe |
| Größenart | `QuantitySpec.kind` — optionale semantische Marke | Energie vs. Drehmoment, beide $ML^2T^{-2}$ | dieselbe Bedeutung |

Eine Dimensionsübereinstimmung ist eine **notwendige
Konsistenzbedingung**, kein Beleg für physikalische Austauschbarkeit.
`check_dimension` meldet `Energie + Drehmoment` deshalb als
dimensional **konsistent**, aber mit einer **semantischen Warnung** —
zwei verschiedene Fragen, zwei verschiedene Felder.

Eine bewusst abstrakte dimensionslose SCF-Größe (z. B. ein
Informationsverhältnis) bekommt `Dimension.none()` und **keine erfundene
SI-Einheit**.

## 2. Ausdrücke prüfen

Ausdrücke sind kleine, validierte Bäume (`Q`, `Const`, `Add`, `Sub`,
`Mul`, `Div`, `Pow`, `Func`) — kein Parser, kein `eval`.
`check_dimension(expr, specs)` liefert `consistent` mit der exakten
Dimension oder `inconsistent` mit jeder Verletzung samt Pfad:

- `Add`/`Sub` verlangen gleiche Dimension.
- `exp`, `log`, `sin`, `cos`, `tanh` verlangen ein dimensionsloses
  Argument und sind dimensionslos.
- `Pow` akzeptiert rationale Exponenten exakt: $\sqrt{l/g}$ hat die
  Dimension $T$; $L^{1/2}$ bleibt $L^{1/2}$. Gleitkommaexponenten werden
  abgelehnt.
- Unbekannte Größennamen und nicht unterstützte Knoten oder Funktionen
  sind **Eingabefehler**, keine Dimensionsverletzungen.

## 3. Einheiten

`convert(value, from_unit, to_unit)` rechnet exakt zwischen Einheiten
derselben Dimension; Umrechnung über Dimensionsgrenzen ist ein
Eingabefehler. **Affine Skalen** (°C, Offset $273{,}15$) werden nicht
als multiplikative Einheiten behandelt: `multiplicative_scale(°C)` wird
abgelehnt; `25 °C` sind absolut $298{,}15\,\mathrm K$, als *Differenz*
aber $25\,\mathrm K$ (`difference=True`).

`rescale_for_base_unit_change(value, dimension, factors)` drückt eine
multiplikative Größe nach einem Wechsel der Basiseinheiten aus:
Faktor $f_b$ neue Einheiten je alte Einheit, Wert
$\cdot\prod_b f_b^{e_b}$. Nur ganzzahlige Exponenten werden exakt
umgerechnet.

**J-C04 (Reservoir):** Für $M'=q-kM$ mit $M_0=3$, $q_y=5$, $k_y=2$,
$t_y=2/5$ liefert Jahr → Tag ($f_T=365$) exakt $q_d=5/365$, $k_d=2/365$,
$t_d=146$. Gleichgewicht $q/k=5/2$ und Exponentenargument $kt=4/5$ sind
**exakt** invariant; damit ist die Lösung identisch, ohne `exp`
auszuwerten. Anschluss an `dynamics/linear_reservoirs.reservoir_step`:
beide Einheitensysteme liefern dasselbe Ergebnis (relativ $10^{-14}$),
das zudem mit der geschlossenen Form übereinstimmt.

**J-C04 (Halo):** $\rho r$ hat die Dimension $ML^{-2}$; die
Umparametrisierung $\rho'=\rho/\lambda$, $r'=\lambda r$ erhält $\rho r$
($6\cdot2=12$ mit $\lambda=3$; Eingaben aus der Plan-Beilage, J0-Befund
B1), **nicht** aber z. B. $\rho r^3$. Aus einer erhaltenen Kombination
folgt keine Erhaltung jeder anderen Halo-Observable.

## 4. Buckingham-Π

`buckingham_pi_basis(specs)` bildet die Dimensionsmatrix $D$ (Zeilen
Basisdimensionen, Spalten Größen), berechnet exakt Rang und
rationalen Nullraum und gibt eine Basis aus primitiven ganzzahligen
Exponentenvektoren samt Monomen zurück. Es gibt $n-\operatorname{rang}D$
unabhängige Gruppen.

**Unterschiedliche Basen sind gleichberechtigt.** Vergleiche laufen über
`same_pi_span` (gleicher Rang beider Mengen und ihrer Vereinigung), nie
über eine bestimmte Schreibweise.

Dokumentierte Randfälle:

| Fall | Ergebnis |
|---|---|
| leere Größenliste, doppelte Namen | Eingabefehler |
| nur dimensionslose Größen | Rang 0; jede Größe ist eine eigene Gruppe |
| voller Spaltenrang (z. B. $m,x,t$) | Nullität 0, leere Basis — gültiges Ergebnis: es gibt keine dimensionslose Kombination |
| zwei Größen gleicher Dimension | eine Gruppe $x_1/x_2$ |

**J-C03 (Pendel):** $(T,l,g)$, Rang 2, Nullität 1, Spann von
$(2,-1,1)$, also $\Pi=gT^2/l$. $g/G$ hat die Dimension $ML^{-2}$ — das
legt weder einen Zahlenwert noch eine physikalische Deutung einer
Flächendichte fest.

**Anschluss an Galaxiengrößen:** $V$ ($LT^{-1}$), $r$, $G$, baryonische
Masse $M$, $a_0$ ($LT^{-2}$): Rang 3, Nullität 2; der berechnete Spann
ist genau der von $V^2r/(GM)$ und $a_0r/V^2$. Das ist eine
Dimensionsaussage über die Variablenwahl, keine Aussage über MOND,
Halos oder die Daten des Galaxienpiloten.

Der Satz liefert **keine Dynamik und keinen universellen Zahlenfaktor**.

## 5. Grenzen

Keine Einheitenbibliothek mit Präfix- oder Namensauflösung, keine
Prüfung beliebiger Python-Funktionen, keine nichtlinearen
Einheitenskalen (z. B. Dezibel) außer dem dokumentierten affinen Fall.

## 6. Quelle

S05 Buckingham (1914), *On Physically Similar Systems*, Phys. Rev. 4,
345 — DOI siehe Plan §21; in J2 wurde geprüft, dass der DOI auflöst. Die
konkreten Nullraumrechnungen sind unabhängig hergeleitet (J0) und hier
exakt geprüft.
