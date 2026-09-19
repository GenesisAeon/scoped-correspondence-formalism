Auftrag: Teil 2, Milestone 29 ("Landau-Entwicklung der bestehenden
kubischen Normalform als Selbst-Falsifizierungs-Instrument") —
natürliche Erweiterung von `dynamics`, aus einer unabhängigen Claude-
Agenten-Recherche (Runde 2 zu `prompts/33_...md`).

## Quellen

- L. Onsager, "Crystal Statistics. I. A Two-Dimensional Model with an
  Order-Disorder Transition", Physical Review 65(3-4), 117–149 (1944),
  DOI 10.1103/PhysRev.65.117.
- C. N. Yang, "The Spontaneous Magnetization of a Two-Dimensional
  Ising Model", Physical Review 85(5), 808–816 (1952), DOI
  10.1103/PhysRev.85.808 (korrekte Quelle für den Exponenten β=1/8 —
  NICHT Onsager selbst, der liefert nur T_c und die freie Energie).
- J. Guckenheimer & P. Holmes, "Nonlinear Oscillations, Dynamical
  Systems, and Bifurcations of Vector Fields", Springer New York
  (1983), DOI 10.1007/978-1-4612-1140-2 (Normalform-Referenz für die
  Pitchfork-Bifurkation / mean-field-Exponent).

Alle drei DOIs per Crossref-API verifiziert.

**Explizit NICHT zitieren:** Landaus Original von 1937 (Zh. Eksp. Teor.
Fiz. 7, 19) — keine verifizierbare DOI gefunden. Die mean-field-Seite
wird stattdessen über die bereits im Repo vorhandene kubische
Normalform selbst UND die verifizierte Guckenheimer/Holmes-Referenz
begründet.

## Kontext

`dynamics.core.CubicNormalForm`/`cusp_field`/`fixed_points`
implementieren bereits EXAKT `τẋ = -x³+ax+b` mit Potential
`U(x)=x⁴/4-ax²/2-bx`. Das IST — algebraisch, nicht analog — das
Landau-Funktional eines skalaren Ordnungsparameters ohne
Gradiententerm, mit `a` als reduzierter Temperatur. Für `b=0, a>0` sind
die stabilen Fixpunkte `x*=±√a` (bereits in `fixed_points`
implementiert) — das ist ein mean-field-Exponent β=1/2 (`x* ∝
(T_c-T)^(1/2)`).

**Der Sinn dieser Erweiterung ist NICHT, eine neue Formel
hinzuzufügen, sondern ein PERMANENTES, ausführbares Gegenbeispiel gegen
Universalitätsansprüche einzubauen:** das exakt lösbare 2D-Ising-Modell
(Onsager 1944 für T_c, Yang 1952 für den Exponenten) hat β=1/8 — ein
anderer Wert für dieselbe Art Übergang in einem anderen Modell. Das
demonstriert numerisch, dass `beta_crit` (der in FORMALISM.md §2
reservierte, bisher nie belegte Symbolplatz) modellabhängig ist, keine
Universalkonstante.

## Umfang dieses Auftrags

### 1. `dynamics.landau.mean_field_order_parameter(a)`

Für `a>0`: gibt `x*=√a` zurück (ruft intern `fixed_points(a, b=0)`
auf und wählt die positive Wurzel — KEINE eigene Fixpunktformel
duplizieren).

### 2. `dynamics.landau.MEAN_FIELD_BETA = 0.5` und
### `dynamics.landau.ISING_2D_BETA = 0.125`

Als dokumentierte Konstanten, LETZTERE mit explizitem Zitat (Yang
1952) — NICHT aus der kubischen Normalform berechnet, sondern als
externer Referenzwert.

### 3. `dynamics.landau.onsager_critical_ratio()`

Gibt `kT_c/J = 2/ln(1+√2) = 2.269185314213022` zurück, mit einem
DOCSTRING-PFLICHTHINWEIS: dieser Wert liegt zahlenmäßig nahe am
bereits in früheren Revisionen verworfenen "geteilten σ≈2,2"
(β≡Stabilität/V≡Panarchy-Fehler) — das ist REINER ZUFALL, `2/ln(1+√2)`
ist ein dimensionsloses Gitterverhältnis für das 2D-Ising-Quadratgitter
und hat KEINERLEI Beziehung zu irgendeinem anderen Baustein oder Wert
in diesem Repo. Dieser Hinweis MUSS wörtlich im Docstring stehen, nicht
nur im Kommentar.

### 4. `dynamics.landau.compare_scaling_exponents(a1, a2)`

Berechnet `x*(a1)`, `x*(a2)` über `mean_field_order_parameter`, das
tatsächliche Verhältnis `x*(a2)/x*(a1)`, das ERWARTETE Verhältnis nach
mean-field (`(a2/a1)^0.5`), und das HYPOTHETISCHE Verhältnis, wenn das
Modell stattdessen dem 2D-Ising-Exponenten folgen würde
(`(a2/a1)^0.125`) — als reine Vergleichszahl, NICHT als Behauptung,
dass die kubische Normalform irgendetwas mit 2D-Ising zu tun hat.

### 5. Durchgerechnetes Beispiel

`a1=0.25, a2=0.0625` (Verhältnis 4): `x*(a1)=0.5`, `x*(a2)=0.25`,
tatsächliches Verhältnis `x*(a2)/x*(a1)=... ` — bei mean-field muss
exakt `2.0 = 4^0.5` herauskommen. Der hypothetische 2D-Ising-Wert wäre
`4^0.125=1.189207115...` — deutlich verschieden. Beide Zahlen im
JSON-Report nebeneinander, mit einem Feld, das explizit sagt: "diese
beiden Werte unterscheiden sich um Faktor ~1,68 — Beleg, dass
beta_crit modellspezifisch ist, keine Universalkonstante (FORMALISM.md
§12)".

### 6. Explizit NICHT Teil dieses Auftrags

- KEIN Gradiententerm/räumliche Kopplung (`c·Δφ`) — nur der bereits
  vorhandene 0-dimensionale Fall.
- KEINE Renormierungsgruppen-Rechnung, KEINE Ableitung von β=1/8 aus
  irgendeiner RG-Formel — nur Zitat des bekannten Werts.
- KEINE Änderung an `dynamics/core.py` — nur Aufruf von `fixed_points`.
- KEINE Verbindung zu `thermo`, `closure` oder sonst einem Baustein
  behaupten.

## Verifikation

`verify_landau_exponent_comparison.py`: (1) Beispiel oben exakt
reproduziert (Zahlen aus dem Skriptlauf), (2) `onsager_critical_ratio`
UND das Docstring-Zitat aus Punkt 3 als Textfeld im JSON-Report selbst
sichtbar (nicht nur im Quellcode), (3) Kontrollfall `a1=a2` → Verhältnis
exakt 1,0 in allen drei Varianten.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_landau_exponent_comparison.py` mit reproduzierbarem JSON-
   Report unter `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Onsager (1944)/Yang (1952)/Guckenheimer &
   Holmes (1983) UND auf `dynamics.core.fixed_points`/`CubicNormalForm`.
5. Der σ≈2,2-Warnhinweis aus Punkt 3 MUSS wörtlich im Code-Docstring
   erscheinen — Abnahmekriterium, nicht optional.
6. KEINE Mutation von FORMALISM.md oder einem der anderen sieben
   Kerndokumente.
7. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m29-landau-exponent-comparison` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 25 (`observation`), 26 (`coupling`), 27
(`membership`) und 28 (`viability`) bearbeitet werden. Bitte NICHT
`src/scoped_correspondence/__init__.py` anfassen. Claude reviewed und
merged erst nach Johanns OK.
