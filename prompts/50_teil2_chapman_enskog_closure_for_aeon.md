Auftrag: Teil 2, Milestone — Chapman-Enskog-Entwicklung (BGK-Route)
als Closure-Defekt — Erweiterung von `closure`. Aus Runde 3 (VON ALLEN
VIER unabhängigen Rechercheagenten übereinstimmend vorgeschlagen).
Liegengebliebener Punkt aus Runde 2 (`prompts/33_...md`), jetzt konkret
ausgearbeitet.

## Quellen — WICHTIG, bitte genau so verwenden

Zwei unabhängige Prüfungen dieser Runde fanden KEINE verifizierbare
DOI für Chapman & Cowlings Monographie "The Mathematical Theory of
Non-Uniform Gases" — bitte NICHT als Primärzitat verwenden. Stattdessen:

- P. L. Bhatnagar, E. P. Gross & M. Krook, "A Model for Collision
  Processes in Gases. I.", Physical Review 94(3), 511–525 (1954), DOI
  10.1103/PhysRev.94.511. Per Crossref-API verifiziert (Titel, alle
  drei Autoren, Band, Seiten, Jahr exakt).
- L. H. Holway Jr., "New Statistical Models for Kinetic Theory:
  Methods of Construction", Physics of Fluids 9(9), 1658–1673 (1966),
  DOI 10.1063/1.1761920. Per Crossref-API verifiziert; Zweck des
  Papers explizit bestätigt: Korrektur des BGK-Modells, das die
  falsche Prandtl-Zahl liefert.

## Kernformel

Chapman-Enskog-Entwicklung `f = f⁽⁰⁾(1+εφ⁽¹⁾+O(ε²))` in der
Knudsen-Zahl `ε`. Ordnung `ε⁰`: Euler-Gleichungen (exakte Closure).
Ordnung `ε¹`: der Closure-Defekt IST der dissipative Transportterm.
Für das BGK-Modell mit Relaxationszeit `τ`:

    μ = p·τ                    (dynamische Viskosität)
    κ = (5/2)(k_B/m)·p·τ       (Wärmeleitfähigkeit)
    ⇒ Pr = c_p·μ/κ = 1         (BGK-Vorhersage)

Der reale Wert für ein einatomiges Gas ist `Pr=2/3` (Argon misst
≈0,67) — BGK ist um 50% falsch, GENAU DAS ist der Punkt: die einzige
Relaxationszeit kann Impuls- und Wärmediffusivität nicht unabhängig
festlegen (Holway 1966 entwickelte deshalb das ES-BGK-Modell).

## Umfang dieses Auftrags

Neue Datei `src/scoped_correspondence/closure/chapman_enskog.py`.

### 1. `closure.chapman_enskog.bgk_transport_coefficients(p, tau, m, k_B=1.0)`

`μ=p·τ`, `κ=(5/2)(k_B/m)·p·τ`, gibt beide zurück.

### 2. `closure.chapman_enskog.prandtl_number(mu, kappa, c_p)`

`Pr = c_p·μ/κ`.

### 3. `closure.chapman_enskog.relaxation_time_from_viscosity(mu, p)`

Inverse: `τ=μ/p` — Rückgewinnung aus einem gemessenen `μ` (Toy-Zahlen,
keine reale Messkampagne nötig, aber realistische Größenordnung als
Sanity-Check erlaubt).

### 4. Durchgerechnetes Beispiel (Pflicht)

`p=1, τ=1, m=1, k_B=1`: `μ=1`, `κ=2.5`. Mit `c_p=5/2` (einatomiges
ideales Gas, `k_B=1`): `Pr = 2.5·1/2.5 = 1.0` — exakt bestätigt.
Vergleich zum realen `Pr=2/3≈0.6667`: Abweichung `Faktor 1.5`.

Zusätzlich als Sanity-Check (nicht als Identitätsbehauptung): Luft bei
`T=300K, p=101325Pa`, gemessenes `μ=1.846e-5 Pa·s` ⇒
`τ=μ/p=1.8219e-10 s`. Mittlere thermische Geschwindigkeit
`⟨v⟩=√(8RT/(πM))` mit `M=0.02896 kg/mol`: `⟨v⟩≈468.3 m/s`, mittlere
freie Weglänge `λ≈⟨v⟩·τ≈8.53e-8 m` — Größenordnung stimmt mit
Literaturwert (~68nm bei 1atm) überein (nur Größenordnungsvergleich,
KEINE exakte Übereinstimmung behaupten).

### 5. Anschluss an `closure` (im Docstring ausführen)

Mikro: Boltzmann/BGK-Kollisionsoperator `P` auf der
Verteilungsfunktion; Projektion `C`: Momente (Dichte, Impuls, Energie);
Makro: hydrodynamischer Generator `Q` (Euler bei Ordnung `ε⁰`,
Navier-Stokes bei Ordnung `ε¹`). Die Chapman-Enskog-Konstruktion liefert
systematisch ein `Q`, dessen Closure-Defekt in der Knudsen-Ordnung
kontrolliert ist — STRUKTURELLE Analogie zu `is_exact_closure`/
`closure_error`, AUSDRÜCKLICH KEINE Identität mit M11 (Lumpability) oder
M21 (Michel-Siegle-Fehlerschranken).

### 6. Explizit NICHT Teil dieses Auftrags

- KEIN voller Boltzmann-Löser.
- KEINE Verwendung der Chapman-Cowling-Hartkugel-Viskositätsformel
  (`5/(16σ²)·√(mkT/π)`) — nicht verifizierbar in dieser Runde, bewusst
  weggelassen.
- KEINE Änderung an `closure/core.py` oder `closure/error_bounds.py`.

## Verifikation

`verify_chapman_enskog_core.py`: (1) Beispiel oben exakt reproduziert
(`Pr=1.0` exakt, Vergleich zu `2/3`), (2) Größenordnungs-Sanity-Check
für Luft, (3) Kontrollfall: `τ→0` ⇒ `μ,κ→0` (kollisionsdominiertes
Limit, keine Dissipation im Kontinuumslimit dieses Modells).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. Neues Dokument `docs/chapman_enskog_core.md`.
3. `verify_chapman_enskog_core.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
4. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
5. Explizites Mapping auf BGK (1954)/Holway (1966) UND auf
   `closure.core.is_exact_closure`/`closure_error` (strukturelle
   Analogie, keine Identität).
6. KEINE Mutation von FORMALISM.md, `emergence_and_closure.md` oder
   einem der anderen sechs Kerndokumente.
7. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m40-chapman-enskog-closure`. Kann PARALLEL zu den
anderen Runde-3-Milestones bearbeitet werden. Bitte NICHT
`src/scoped_correspondence/__init__.py`, `closure/core.py` oder
`closure/error_bounds.py` anfassen. Claude reviewed und merged erst
nach Johanns OK.
