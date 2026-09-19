Auftrag: Teil 2, neuer eigenständiger Baustein "free_boundary"
(Stefan-Problem / bewegliche Phasengrenze) — KEIN Erweiterungs-
Milestone eines bestehenden Bausteins, sondern ein komplett neues,
eigenständiges Modul. Aus einer unabhängigen Claude-Agenten-Recherche
(Runde 2 zu `prompts/33_...md`) plus Johanns expliziter
Grundsatzentscheidung (2026-09-19).

## Warum ein NEUER Baustein statt einer `viability`-Erweiterung

`viability/core.py` behandelt sichere Mengen `K` als FEST vorgegeben
(`K=[b,∞)` bzw. Polyeder in M28). Im Stefan-Problem ist die Grenze
`s(t)` selbst eine dynamische Variable mit einer EIGENEN
Bewegungsgleichung (Flussbilanz an der Grenze), nicht eine gegebene
Randbedingung, gegen die geprüft wird. Beide unabhängigen
Rechercheagenten stuften dies unabhängig voneinander als (b) — eigener
Baustein — ein, mit derselben Begründung.

## Quellen

- V. A. Kot, "Solution of the Classical Stefan Problem: Neumann
  Condition", Journal of Engineering Physics and Thermophysics 90(4),
  889–917 (2017), DOI 10.1007/s10891-017-1638-2.
- J. Bollati, M. F. Natale, J. A. Semitiel & D. A. Tarzia,
  "Approximate solutions to the one-phase Stefan problem with
  non-linear temperature-dependent thermal conductivity", arXiv:
  1906.08601 (für die exakte Form der transzendenten Gleichung,
  wörtlich per WebFetch aus dem arXiv-HTML-Volltext bestätigt:
  `z*exp(z^2)*erf(z) = Ste/sqrt(pi), z>0`).

Beide Quellen wurden unabhängig verifiziert (Kot 2017 per Crossref-API
— Titel/Autor/Zeitschrift/Band/Heft/Seiten/Jahr exakt bestätigt;
Bollati et al. per WebFetch des arXiv-Volltexts).

## Umfang dieses Auftrags

Neues Paket `src/scoped_correspondence/free_boundary/` mit
`__init__.py` und `core.py`.

### 1. `free_boundary.stefan_number(c, T0, L)`

Berechnet die Stefan-Zahl `Ste = c*T0/L` (spezifische Wärmekapazität
`c`, Randtemperatur `T0`, latente Wärme `L`).

### 2. `free_boundary.neumann_lambda(Ste, tol=1e-12)`

Löst per Bisektion (oder gleichwertigem robusten Verfahren, KEIN
Newton ohne Bracket-Fallback) die transzendente Gleichung

    lambda * exp(lambda^2) * erf(lambda) = Ste / sqrt(pi)

für `lambda > 0`. Gibt `lambda`, die Anzahl Iterationen und das
erreichte Residuum zurück. `ScopeViolationError` bei `Ste <= 0`.

### 3. `free_boundary.melt_front_position(lam, alpha, t)`

`s(t) = 2*lambda*sqrt(alpha*t)` — die Position der Phasengrenze zur
Zeit `t` bei Diffusivität `alpha`.

### 4. `free_boundary.temperature_profile(x, t, lam, alpha, T0)`

`T(x,t) = T0*(1 - erf(x/(2*sqrt(alpha*t))) / erf(lambda))` für
`0 <= x <= s(t)`. `ScopeViolationError` für `x` außerhalb `[0, s(t)]`
(das Modell deckt nur die flüssige Phase ab, keine Zwei-Phasen-
Erweiterung).

### 5. Durchgerechnetes Beispiel (Pflicht)

Drei Stefan-Zahlen, jede per Bisektion gelöst, Residuum im Report:

| Ste | lambda (Zielwert) |
|---|---|
| 1,0 | ≈0,620063 |
| 0,5 | ≈0,464786 |
| 0,1 | ≈0,220016 |

Für JEDEN der drei Fälle MUSS das Skript selbst die Gleichung
`lambda*exp(lambda^2)*erf(lambda)` auswerten und gegen `Ste/sqrt(pi)`
prüfen (Residuum < 1e-9), NICHT nur den Zielwert hartkodiert
vergleichen. Zusätzlich für `Ste=1,0`: `alpha=1 mm^2/s`, Position bei
`t=100s` (`s≈12,40mm`) und `t=400s` (`s≈24,80mm`) — Verhältnis exakt 2
(die `sqrt(t)`-Gesetzmäßigkeit), im Report als eigenes Feld ausweisen.

### 6. Explizit NICHT Teil dieses Auftrags

- KEIN allgemeiner PDE-/Zwei-Phasen-Löser — nur die 1D-Ein-Phasen-
  Neumann-Ähnlichkeitslösung.
- KEINE Änderung an `viability/core.py`, `viability/nagumo.py` (M28)
  oder `viability/control_barrier.py` (M16).
- KEINE Behauptung, `free_boundary` sei ein Unterfall von `viability`
  — im Docstring explizit die oben genannte Begründung (Grenze als
  eigene dynamische Variable, keine feste Menge) festhalten.
- KEIN Zitat von Stefan (1891) selbst oder Rubinstein (1971) — für
  beide wurde in dieser Recherche-Runde keine verlässlich verifizierte
  DOI gefunden; nur die beiden oben genannten, tatsächlich geprüften
  Quellen verwenden.

## Verifikation

`verify_free_boundary_core.py`: (1) alle drei Stefan-Zahlen-Fälle oben
exakt reproduziert (Zahlen aus dem Skriptlauf, inkl. Residuumsprüfung
gegen die Gleichung selbst), (2) `sqrt(t)`-Verhältnis bei `Ste=1,0`
bestätigt, (3) Kontrollfall `Ste→0` (sehr kleine Stefan-Zahl, z.B.
0,01): `lambda` muss deutlich kleiner werden (physikalisch: wenig
latente Wärme relativ zur fühlbaren Wärme → langsameres Schmelzen).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. Neues Dokument `docs/free_boundary_core.md` — Format wie
   `docs/metarules_core.md` (Quellen, Formeln, durchgerechnetes
   Beispiel, Out-of-Scope-Abschnitt).
3. `verify_free_boundary_core.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
4. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
5. Explizites Mapping auf Kot (2017) und Bollati et al. (arXiv
   1906.08601).
6. KEINE Mutation von FORMALISM.md oder einem der anderen sieben
   Kerndokumente, KEINE Änderung an irgendeinem bestehenden Baustein-
   Verzeichnis.
7. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m31-free-boundary-stefan` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu den beiden anderen neuen Bausteinen (Musterbildung,
Perkolation) bearbeitet werden — komplett unabhängige, neue
Verzeichnisse. Bitte NICHT `src/scoped_correspondence/__init__.py`
oder irgendein bestehendes Baustein-Verzeichnis anfassen. Claude
reviewed und merged erst nach Johanns OK.
