Auftrag: Teil 2, Milestone — Panarchy/Adaptive-Cycle als Cusp-
Erweiterung — Erweiterung von `dynamics`. Aus Runde 3, Spur C
(CREP/UTAC/AFET-Inspirationsliteratur ehrlich neu geprüft). Von DREI
der vier unabhängigen Agenten übereinstimmend auf dieselbe Quelle
gestützt — sehr hohe Konvergenz.

## Vorgeschichte (Pflichtkontext für den Docstring)

Dieses Projekt hieß ursprünglich "CREP-UTAC-AFET" und war u.a. von
Hollings Panarchy/Adaptive-Cycle-Theorie inspiriert. Eine frühere
Revision hat versucht, `V ≡ Panarchy ≡ Onsager-L` DIREKT
gleichzusetzen — das war falsch und wurde vollständig zurückgenommen
(siehe `GLOSSARY.md`). **Dieser Auftrag reaktiviert NICHT diese
Gleichsetzung.** Es wird ausschließlich die bereits vorhandene
Cusp-Geometrie in `dynamics` verwendet — kein neues Symbol `V`, kein
Bezug zu Onsager-`L` oder `LijTransport`.

## Quellen

- C. S. Holling, "Resilience and Stability of Ecological Systems",
  Annual Review of Ecology and Systematics 4(1), 1–23 (1973), DOI
  10.1146/annurev.es.04.110173.000245 (begrifflicher Ursprung, KEINE
  eigene Formel — nur zur Einordnung zitieren).
- **M. Zwick & J. Hughes, "Formalizing the Panarchy Adaptive Cycle
  with the Cusp Catastrophe", Proc. Computational Social Science
  Society of the Americas 2017, DOI 10.1145/3145574.3145591** — die
  eigentliche Formalisierung: bildet die vier Adaptive-Cycle-Phasen
  (Exploitation/Conservation/Release/Reorganization) auf die
  Faltungs-/Hysterese-Struktur der Cusp-Katastrophe ab. Von drei
  unabhängigen Rechercheagenten per Crossref-API bestätigt (Titel,
  beide Autoren, Konferenz, Jahr, DOI exakt). **Hinweis:** der
  Volltext war in dieser Recherche nicht abrufbar (403) — nur der
  Abstract live bestätigt. Vor der Umsetzung sollte, falls möglich,
  das vollständige PDF besorgt und die genaue Phasen-Zuordnung
  gegengeprüft werden; falls nicht möglich, im Docstring als
  "Abstract-verifiziert, Volltext nicht eingesehen" kennzeichnen.

## Kernformel

Bereits vorhanden in `dynamics.core.CubicNormalForm`/`fixed_points`/
`discriminant`: `τẋ = -x³+ax+b`, Faltmenge `4a³-27b²=0`. Zwick &
Hughes interpretieren eine langsame Kontrollbahn `(a(t),b(t))`, die
diese Faltmenge zweimal durchquert, als die Hysterese-Schleife des
Adaptive Cycle: Durchqueren der einen Falte = "Release" (Ω-Phase),
Durchqueren der anderen = "Reorganization" (α-Phase); die beiden
stabilen Äste dazwischen = "Exploitation→Conservation" (r→K).

## Umfang dieses Auftrags

Neue Datei `src/scoped_correspondence/dynamics/panarchy_cusp.py`.

### 1. `dynamics.panarchy_cusp.hysteresis_sweep(a, b_values)`

Für festes `a>0` und eine Liste von `b`-Werten (ein "Hinweg" und ein
"Rückweg", d.h. `b` steigt dann fällt): ruft `fixed_points(a,b)` und
`discriminant(a,b)` (BEIDE aus dem bestehenden `dynamics.core`, NICHT
neu implementieren) für jeden Wert auf, verfolgt den Ast, auf dem sich
der Zustand befindet (Kontinuität), und erkennt Sprünge (Zweig
verschwindet, wenn `discriminant` das Vorzeichen wechselt).

### 2. `dynamics.panarchy_cusp.fold_thresholds(a)`

`b_c = ±√(4a³/27)` — die beiden Faltwerte bei festem `a` (aus
`4a³-27b²=0` aufgelöst).

### 3. Durchgerechnetes Beispiel (Pflicht)

`a=3, b=0`: Gleichgewichte `x=0,±√3` (aus `fixed_points` bestätigen).
`fold_thresholds(3) = ±2/√3 ≈ ±1.1547`. Hysterese-Sweep: `b` von `-2`
über `0` bis `+2` und zurück — zeigen, dass der Zustand beim
Überschreiten von `b=+1.1547` von einem Ast auf den anderen springt
(Release) und beim Unterschreiten von `b=-1.1547` auf dem Rückweg
zurückspringt (Reorganization), NICHT bei `b=0` (Hysterese, kein
reversibler Pfad).

### 4. Explizit NICHT Teil dieses Auftrags

- KEIN neues Symbol `V` oder "Panarchy-Potential" — nur die
  bestehenden `CubicNormalForm`-Größen.
- KEINE Verbindung zu `LijTransport`, Onsager-`L` oder `thermo`.
- KEINE volle Adaptive-Cycle-Semantik (α-Phase als "Reorganisation" im
  vollen ökologischen Sinn) — nur die geometrische Hysterese-Struktur,
  mit explizitem Docstring-Hinweis: "Interpretationsschicht, keine
  bewiesene ökologische Aussage."
- KEINE Änderung an `dynamics/core.py` — nur Aufruf von `fixed_points`/
  `discriminant`.

## Verifikation

`verify_panarchy_cusp_core.py`: (1) Beispiel oben exakt reproduziert
(Faltwerte, Sprungpunkte aus dem Skriptlauf), (2) Kontrollfall: fester
`b` innerhalb `(-b_c,+b_c)` bei Variation von `a` — KEIN Sprung ohne
Faltendurchquerung.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. Neues Dokument `docs/panarchy_cusp_core.md`, MIT der Vorgeschichte
   oben (V≡Panarchy≡Onsager-L-Retraktion) explizit erwähnt.
3. `verify_panarchy_cusp_core.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
4. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
5. Explizites Mapping auf Holling (1973, nur Einordnung) und Zwick &
   Hughes (2017, die eigentliche Formel), MIT Vermerk, dass der
   Volltext nicht eingesehen wurde (nur Abstract verifiziert).
6. Der Vorgeschichte-Hinweis (keine Wiederbelebung von
   V≡Panarchy≡Onsager-L) MUSS wörtlich im Docstring erscheinen.
7. KEINE Mutation von FORMALISM.md oder einem der anderen sieben
   Kerndokumente.
8. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m35-panarchy-cusp`. Kann PARALLEL zu den anderen
Runde-3-Milestones bearbeitet werden — mehrere betreffen ebenfalls
`dynamics` (Fenichel/GSPT, Floquet, Scheffer Early-Warning); jede
erhält eine EIGENE neue Datei in `dynamics/`, sodass nur
`dynamics/__init__.py` und `pyproject.toml` beim Merge triviale,
erwartbare Konflikte haben können. Bitte NICHT
`src/scoped_correspondence/__init__.py` oder `dynamics/core.py`
anfassen. Claude reviewed und merged erst nach Johanns OK.
