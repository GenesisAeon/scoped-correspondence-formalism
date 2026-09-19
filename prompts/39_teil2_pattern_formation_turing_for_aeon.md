Auftrag: Teil 2, neuer eigenständiger Baustein "pattern_formation"
(Diffusions-getriebene Musterbildung / Turing-Instabilität) — KEIN
Erweiterungs-Milestone eines bestehenden Bausteins, sondern ein
komplett neues, eigenständiges Modul. Aus einer unabhängigen Claude-
Agenten-Recherche (Runde 2 zu `prompts/33_...md`) plus Johanns
expliziter Grundsatzentscheidung (2026-09-19): Turing-Instabilität wird
NICHT als Erweiterung von `dynamics` gebaut, sondern als eigener
Baustein.

## Warum ein NEUER Baustein statt einer `dynamics`-Erweiterung

Zwei unabhängige Rechercheagenten haben dieses Thema vorgeschlagen,
kamen aber zu unterschiedlichen Einschätzungen: der eine sah es als
direkte `dynamics`-Erweiterung (dieselbe Jacobi-Eigenwert-Rechnung,
nur über eine Wellenzahl k parametrisiert), der andere als
eigenständigen Baustein (ein räumlicher Laplace-Operator und ein
Kontinuum von Moden haben in KEINEM der bisherigen 12 Bausteine eine
Entsprechung — `dynamics/core.py` ist durchgehend 0-dimensional).
Johann hat sich für die zweite Lesart entschieden.

**Wichtig — die mögliche Anbindung wird NICHT verworfen, nur nicht
gebaut:** im Docstring des neuen Moduls MUSS folgender Hinweis wörtlich
erscheinen: eine künftige `correspondence`-Brücke zwischen
`pattern_formation` und `dynamics` ist strukturell denkbar (Turings
`S_rec(k)` würde `dynamics.recovery_rate_at_equilibrium` — dort
implizit `S_rec(0)` — auf eine Wellenzahl `k` verallgemeinern), wird
aber HIER NICHT behauptet oder implementiert. Eine echte Konjugation
müsste über den regulären `correspondence`-Vertrag mit eigenem Beweis
und eigener Prüfung laufen, nicht als stillschweigende Abkürzung.

## Quellen

- A. M. Turing, "The chemical basis of morphogenesis", Phil. Trans. R.
  Soc. Lond. B 237(641), 37–72 (1952), DOI 10.1098/rstb.1952.0012.
- J. Schnakenberg, "Simple chemical reaction systems with limit cycle
  behaviour", J. Theor. Biol. 81(3), 389–400 (1979), DOI
  10.1016/0022-5193(79)90042-0. **ACHTUNG, zwingend im Docstring
  vermerken:** dies ist ein ANDERER Aufsatz desselben Autors als
  Schnakenberg 1976 (Rev. Mod. Phys. 48, 571, DOI
  10.1103/RevModPhys.48.571), der bereits in M18
  (`thermo/schnakenberg.py`) verwendet wird — andere Zeitschrift,
  anderes Jahr, andere Aussage (Reaktionskinetik mit Grenzzyklus vs.
  Netzwerk-Thermodynamik). Keine Vermischung der beiden Module.
- J. D. Murray, "Mathematical Biology II: Spatial Models and
  Biomedical Applications", Springer New York (2003), DOI
  10.1007/b98869 (Referenz für die Standardform der Turing-Bedingungen
  und die Turing-Analyse der Schnakenberg-1979-Kinetik).

Alle drei DOIs wurden von zwei unabhängigen Agenten per Crossref-API
verifiziert.

## Umfang dieses Auftrags

Neues Paket `src/scoped_correspondence/pattern_formation/` mit
`__init__.py` und `core.py`.

### 1. `pattern_formation.jacobian_stability(J)`

Für eine 2×2-Jacobi-Matrix `J=[[f_u,f_v],[g_u,g_v]]` an einem
homogenen stationären Zustand: prüft `tr(J)<0` UND `det(J)>0`
("ODE-stabil ohne Diffusion").

### 2. `pattern_formation.turing_conditions(J, D_u, D_v)`

Prüft ALLE VIER Bedingungen für Diffusions-getriebene Instabilität:

    (i)   tr(J) = f_u+g_v < 0
    (ii)  det(J) = f_u*g_v - f_v*g_u > 0
    (iii) D_v*f_u + D_u*g_v > 0
    (iv)  (D_v*f_u + D_u*g_v)^2 > 4*D_u*D_v*det(J)

Gibt zusätzlich die kritische Wellenzahl zurück:

    k_c^2 = (D_v*f_u + D_u*g_v) / (2*D_u*D_v)

und — als Gegenprobe im selben Aufruf — die alternative Formel bei
exakter Kritikalität `k_c^2 = sqrt(det(J)/(D_u*D_v))` (beide MÜSSEN im
Skript berechnet und auf Übereinstimmung geprüft werden).

### 3. `pattern_formation.dispersion_relation(J, D_u, D_v, k)`

Eigenwerte von `J - k^2*diag(D_u,D_v)`; gibt `Re(lambda_max(k))`
zurück (reellwertig für die hier betrachteten Fälle).

### 4. `pattern_formation.schnakenberg_1979_steady_state(a, b)`

Homogener Fixpunkt der Kinetik `f=a-u+u^2*v`, `g=b-u^2*v`:
`u*=a+b`, `v*=b/(a+b)^2`, plus die Jacobi-Einträge an diesem Punkt
(`f_u=(b-a)/(a+b)`, `f_v=(a+b)^2`, `g_u=-2b/(a+b)`, `g_v=-(a+b)^2`).

### 5. Durchgerechnetes Beispiel (Pflicht)

Schnakenberg-1979-Kinetik mit `a=0.1, b=0.9`:
- Fixpunkt: `u*=1.0, v*=0.9`.
- Jacobi: `f_u=0.8, f_v=1.0, g_u=-1.8, g_v=-1.0`.
- `tr(J)=-0.2<0`, `det(J)=1.0>0` — ODE-stabil bestätigt.
- Bei `D_u=1`: kritisches `D_v` ist die positive Wurzel von
  `0.64*D_v^2 - 5.6*D_v + 1 = 0`, also `D_v_c ≈ 8.567627` (die zweite
  Wurzel `≈0.182373` ist die kleinere, physikalisch hier nicht
  relevante Lösung — beide im Report angeben).
- `k_c^2 = (0.8*8.567627-1)/(2*8.567627) ≈ 0.341641`, UND per
  Gegenprobe `sqrt(1/8.567627) ≈ 0.341641` — beide MÜSSEN
  übereinstimmen.
- Dispersionsrelation an drei Punkten: `D_v=0.99*D_v_c` (stabil,
  `Re(lambda_max)<0`), `D_v=D_v_c` (exakt marginal, `Re(lambda_max)≈0`
  bis auf numerisches Rauschen), `D_v=1.2*D_v_c` (instabil,
  `Re(lambda_max)>0`) — alle drei Vorzeichen MÜSSEN im Skriptlauf
  bestätigt werden.

### 6. Explizit NICHT Teil dieses Auftrags

- KEIN PDE-Löser, KEINE räumliche Simulation/Musterbildung selbst —
  nur die lineare Stabilitätsanalyse (Dispersionsrelation).
- KEINE Änderung an `dynamics/core.py`, `thermo/schnakenberg.py` oder
  irgendeinem anderen bestehenden Modul.
- KEINE Behauptung, `pattern_formation` sei ein Unterfall von
  `dynamics` — der Docstring-Hinweis aus dem Abschnitt oben ist
  Pflicht, aber als OFFENER, UNBEWIESENER Kandidat, nicht als Tatsache.
- KEINE Verwechslung der beiden Schnakenberg-Quellen (siehe oben,
  Pflicht-Warnhinweis im Docstring).

## Verifikation

`verify_pattern_formation_core.py`: (1) Beispiel oben exakt
reproduziert (Zahlen aus dem Skriptlauf), (2) die beiden `k_c^2`-
Formeln stimmen überein, (3) alle drei Dispersions-Vorzeichen bestätigt,
(4) Kontrollfall: `D_v` deutlich unterhalb `D_v_c` (z.B. `D_v=1`) zeigt
`turing_conditions` als NICHT erfüllt (Bedingung iv verletzt).

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. Neues Dokument `docs/pattern_formation_core.md` — Format wie
   `docs/metarules_core.md` (Quellen, Formeln, Mapping-Tabelle wo
   sinnvoll, durchgerechnetes Beispiel, Out-of-Scope-Abschnitt, der
   Docstring-Hinweis zur offenen `correspondence`-Brücke).
3. `verify_pattern_formation_core.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
4. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
5. Explizites Mapping auf Turing (1952)/Schnakenberg (1979)/Murray
   (2003), MIT dem Pflicht-Warnhinweis zu Schnakenberg 1976 vs. 1979.
6. Der `correspondence`-Brücken-Hinweis MUSS wörtlich im Docstring
   erscheinen — Abnahmekriterium, nicht optional.
7. KEINE Mutation von FORMALISM.md oder einem der anderen sieben
   Kerndokumente, KEINE Änderung an irgendeinem bestehenden Baustein-
   Verzeichnis.
8. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m30-pattern-formation-turing` auf
`GenesisAeon/scoped-correspondence-formalism`, direkt gepusht. Kann
PARALLEL zu den beiden anderen neuen Bausteinen (freie Randbedingung,
Perkolation) bearbeitet werden — komplett unabhängige, neue
Verzeichnisse. Bitte NICHT `src/scoped_correspondence/__init__.py`
oder irgendein bestehendes Baustein-Verzeichnis anfassen. Claude
reviewed und merged erst nach Johanns OK.
