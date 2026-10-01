# Gewichtetes Split Conformal mit begrenzter Garantie (J8)

Paket J8 aus [`SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md`](../SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md),
Plan §14. Code: `src/scoped_correspondence/validation/weighted_conformal.py`.
Prüfung: `verification/verify_weighted_conformal.py` (math). Lizenz der
Dokumentation: CC BY 4.0.

## 1. Verfahren und Garantieumfang

Vorhersager auf einer **separaten** Trainingsmenge fixiert;
Kalibrierpunkte i.i.d. aus $P$, ein unabhängiger Zielpunkt aus $Q$;
$P(Y\mid X)=Q(Y\mid X)$, $Q_X\ll P_X$; Gewichte $w=dQ_X/dP_X$ bis auf
einen positiven Faktor **bekannt** (S13). Das Quantil ist die kleinste
Bewertung, deren normierte kumulative Masse $1-\alpha$ erreicht; die
Masse des Testpunkts liegt bei $+\infty$ und fehlt nie. $q=+\infty$
bedeutet: das Vorhersageintervall ist die **ganze reelle Gerade** (JSON:
`{"kind": "whole_real_line"}`), nicht leer.

Die Abdeckungsaussage ist **marginal** über Kalibrierung und Zielpunkt,
keine konditionale Garantie für ein festes $x$. Sie wird nur unter den
genannten Annahmen geerbt (`guarantee_status`):

| Situation | Status |
|---|---|
| bekannte Dichteverhältnisse, kein Clipping | `inherited_under_stated_assumptions` |
| geschätzte Gewichte | `not_inherited_estimated_weights` |
| Clipping (Verfahrensänderung) | `not_inherited_procedure_changed` |

Zeitliche Autokorrelation und Concept Shift werden durch Kovariaten-
gewichtung nicht repariert. Training und Kalibrierung müssen disjunkt sein
(sonst Eingabefehler). Diagnosen: effektive Stichprobengröße
$(\sum w)^2/\sum w^2$, größter normierter Gewichtsanteil, Anteil
unbeschränkter Intervalle, empirische Abdeckung, mittlere endliche Breite.
Exakte `Fraction`-Eingaben liefern exakte Quantile.

## 2. Kontrollen

- **J-C15:** $(1,2,3)$, Gewichte $(1,1,1)$, Testgewicht 1, $\alpha=1/4$:
  3; Testgewicht 4: $+\infty$; Gewichte $(1,2,1)$, $\alpha=2/5$: 2.
  Gemeinsame Skalierung aller Gewichte ändert nichts (MR6).
- **J-C16** (32 Fälle, mit der **Produktions**funktion): ungewichtet
  $40951/100000$, gewichtet 1, unbeschränkt $89991/100000$ — der
  Abdeckungsgewinn wird hier mit überwiegend nutzlosen Intervallen
  erkauft; Abdeckung, Breite und Unbeschränktheit stehen daher
  nebeneinander.
- **J-C17** (Concept Shift): Quantil 0, Abdeckung 0 — die Voraussetzung
  ist verletzt, kein Widerspruch zum Satz.

## 3. Vergleich mit fester und adaptiver Kalibrierung

Vorab festgelegtes Szenario: $X\sim U[0,1]$ unter $P$, Dichte $2x$ unter
$Q$ (bekanntes $w=2x$), heteroskedastisches Rauschen $(0{,}1+x)\varepsilon$,
Vorhersager 0, $\alpha=0{,}1$, 100 Kalibrier- und 50 Testpunkte, 300
Wiederholungen (Seed 2):

| Verfahren | mittlere Abdeckung |
|---|---|
| festes Split Conformal (`conformal.py`) | 0,850 |
| gewichtetes Split Conformal (neu) | 0,910 |
| ACI (`adaptive_interval_calibration.aci_update_alpha`, sequentiell) | 0,890 |

Das ist **ein** Szenario. ACI zielt auf langfristige sequentielle
Abdeckung — eine andere Garantie. Ein Realdatentest wurde nicht
durchgeführt (er dürfte neutral oder schlechter ausfallen, Plan §14).

## 4. Korrektur und Befund am bestehenden `conformal.py`

- Die Docstring-Formulierung zu `+inf` („empty finite interval“) wurde wie
  vom Plan verlangt berichtigt: ganze reelle Gerade.
- **Befund (nicht geändert):** `ceil((n+1)*(1-alpha))` mit Float-α ergibt
  für α ∈ {0,45; 0,7; 0,85; 0,95; 0,99} bei mathematisch ganzzahligem
  Produkt einen um 1 zu großen Index, weil der Float nicht das gemeinte
  Dezimal-α ist. Wirkung nur konservativ; übliche α unbetroffen.
  Entscheidung offen, siehe [`DEEP_RESEARCH_BACKLOG.md`](../DEEP_RESEARCH_BACKLOG.md).
  Das J8-Modul akzeptiert α exakt als `Fraction`.

## 5. Quelle

S13 Tibshirani, Barber, Candès & Ramdas (2019) — Links siehe Plan §21.
Die Quantilkonvention bei Gleichstand ist oben festgelegt; ein
Volltextabgleich steht im Backlog.
