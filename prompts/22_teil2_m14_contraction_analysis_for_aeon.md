Auftrag: Teil 2, Milestone 14 ("Contraction Analysis") — natürliche
Erweiterung von `dynamics`, aus `ChatGPTAstra3.md` (Lohmiller & Slotine
1998, DOI 10.1016/S0005-1098(98)00019-3, von Claude gegen die Quelle
geprüft).

## Kontext

`dynamics.cusp_field(x, a, b, tau=1.0)` (M2, gemergt) implementiert
`τ·ẋ = -x³+ax+b`, also `f(x) = (-x³+ax+b)/τ`. Contraction Analysis
(Lohmiller & Slotine 1998) liefert eine globale Konvergenzbedingung für
benachbarte Trajektorien: gilt `f'(x) ≤ -λ < 0` für ALLE `x`, konvergieren
Abstände exponentiell mit Rate `λ`: `|δx(t)| ≤ e^{-λt}|δx(0)|`.

Für `cusp_field` ist `f'(x) = (-3x²+a)/τ`, ein nach oben durch `x=0`
begrenztes Maximum: `sup_x f'(x) = a/τ` (erreicht bei `x=0`, da `-3x²≤0`
für alle `x`). Damit ist die Bedingung exakt, ohne numerische Suche
lösbar:

- `a < 0`: global kontrahierend mit Rate `λ = -a/τ`.
- `a >= 0`: nicht global kontrahierend (`f'(0) = a/τ >= 0`).

Das ist ein reiner Scope-Gegenfall zur bestehenden Bistabilitätsbedingung
`4a³>27b²` (M2) — bei `a<0` gibt es ohnehin nur einen Fixpunkt und
globale Kontraktion; bei `a>0` (Bistabilitätsregion möglich) kann keine
globale Kontraktionsrate existieren. Keine neue Universalität, nur ein
zusätzliches, exaktes Zertifikat für den bereits vorhandenen Baustein.

## Umfang dieses Auftrags

### 1. `dynamics.contraction.contraction_rate_cusp(a, tau=1.0)`

Liefert `λ = -a/tau` wenn `a < 0`, sonst `None` (nicht global
kontrahierend — kein Fehler, ein gültiges negatives Ergebnis).
Docstring muss die exakte Herleitung (`sup_x f'(x) = a/tau` bei `x=0`)
nennen.

### 2. `dynamics.contraction.ContractionCertificate`

Typisiertes Ergebnis: `rate: Optional[float]`, `a`, `tau`,
`is_globally_contracting: bool`, `metric="euclidean_1d"`, `source`.

### 3. `dynamics.contraction.verify_contraction_bound(a, tau, x_samples)`

Nimmt eine Stichprobe von `x`-Werten und bestätigt NUMERISCH (finite
Differenz auf `cusp_field`, nicht die analytische Formel erneut), dass
`f'(x) <= -rate` für alle Stichproben gilt, wenn `rate` nicht `None`
ist — Gegenprobe der analytischen Formel gegen die bereits gemergte
`cusp_field`-Funktion (nur Aufruf, keine Änderung an
`dynamics/core.py`).

### 4. Durchgerechnetes Beispiel (bereits von Claude bestätigt)

- `a=-1, tau=1`: `f'(x)=-3x²-1<=-1` für alle `x` → `rate=1.0`,
  `is_globally_contracting=True`.
- `a=1, tau=1` (oder ein anderer positiver Wert): `f'(0)=1>0` →
  `rate=None`, `is_globally_contracting=False`. Explizit im Bericht
  vermerken, dass dies der Bistabilitäts-Scope-Bereich ist (`a>0`
  ermöglicht die bereits bekannte Cusp-Bistabilität), nicht einfach
  "Fehler".

### 5. Explizit NICHT Teil dieses Auftrags

- Keine Änderung an `dynamics/core.py` — nur Aufruf von `cusp_field`.
- Keine allgemeine mehrdimensionale Kontraktionsmetrik (Jacobi-Matrix,
  Riemannian Contraction Metric) — nur der bereits vorhandene
  eindimensionale Fall.
- Keine Verbindung zur Bistabilitätsbedingung `4a³>27b²` als neue
  Formel — nur als Kontext im Docstring erwähnen, nicht neu herleiten.

## Verifikation

`verify_contraction_core.py`: keine bestehende Legacy-Prüfung — beide
Fälle oben mit Zahlen aus dem Skriptlauf, plus die numerische
Gegenprobe (Abschnitt 3) für mindestens 5 verschiedene `x`-Werte.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. `verify_contraction_core.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
3. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
4. Explizites Mapping auf Lohmiller & Slotine 1998 (DOI oben) und
   `dynamics/core.py`s `cusp_field`.
5. KEINE Mutation von FORMALISM.md oder einem der sieben Layer-/
   Erweiterungsdokumente.
6. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m14-contraction-analysis` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu Milestone 15 (`coupling`) und Milestone 16 (`viability`)
bearbeitet werden — unterschiedliche Module, kein Konflikt (analog
M11–M13). Wie bei M11–M13: package-root
`src/scoped_correspondence/__init__.py` bitte NICHT anfassen, um
Merge-Konflikte mit den parallelen Branches zu vermeiden — nur das
jeweilige Untermodul-`__init__.py`. Claude reviewed jeden Branch
einzeln und merged erst nach Johanns OK.
