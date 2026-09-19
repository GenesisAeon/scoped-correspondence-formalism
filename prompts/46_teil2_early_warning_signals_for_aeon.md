Auftrag: Teil 2, Milestone — Early-Warning-Signale / kritisches
Verlangsamen — Erweiterung von `dynamics`. Aus Runde 3, Spur C. Von
ALLEN VIER unabhängigen Rechercheagenten übereinstimmend vorgeschlagen
— die höchste Konvergenz der gesamten Runde. Stärkster Kandidat dieser
Runde.

## Quellen

- M. Scheffer et al., "Early-warning signals for critical
  transitions", Nature 461, 53–59 (2009), DOI 10.1038/nature08227. Von
  allen vier Agenten per Crossref-API verifiziert (Titel, alle Autoren,
  Zeitschrift, Band, Seiten, Jahr exakt).
- **Pflicht-Gegenbeweis-Zitate** (müssen mitgeliefert werden, siehe
  unten): C. Boettiger & A. Hastings, "Quantifying limits to detection
  of early warning for critical transitions", J. R. Soc. Interface
  9(75), 2527–2539 (2012), DOI 10.1098/rsif.2012.0125; P. D. Ditlevsen
  & S. J. Johnsen, "Tipping points: Early warning and wishful
  thinking", Geophys. Res. Lett. 37(19) (2010), DOI
  10.1029/2010GL044486.

## Kernformel

Linearisierung um einen stabilen Gleichgewichtspunkt mit Eigenwert
`λ<0` plus additives Rauschen: `dX = -λ(X-x*)dt + σdW`. Stationäre
Ornstein-Uhlenbeck-Statistik: `Var(X) = σ²/(2λ)`,
`Corr(X_t,X_{t+Δt}) = exp(-λΔt)`. Bei Annäherung an eine Bifurkation
(`λ→0⁺`): `Var→∞`, Autokorrelation `→1`.

## Umfang dieses Auftrags

Neue Datei `src/scoped_correspondence/dynamics/early_warning.py`.

### 1. `dynamics.early_warning.ou_variance(sigma, lam)`

`Var = σ²/(2λ)`. `ScopeViolationError` bei `λ≤0`.

### 2. `dynamics.early_warning.ou_autocorrelation(lam, delta_t)`

`ρ = exp(-λ·Δt)`.

### 3. `dynamics.early_warning.estimate_lambda_from_ar1(rho, delta_t)`

Inverse: `λ̂ = -ln(ρ)/Δt` — Rückgewinnung von λ aus der gemessenen
Autokorrelation (Konsistenzprüfung mit Punkt 1/2).

### 4. Pflicht: Kopplung an die bestehende `dynamics`-API

Muss `dynamics.core.recovery_rate_at_equilibrium(x, a, tau, b)` als
Quelle für `λ` AUFRUFEN (nicht neu berechnen) — der ganze Sinn dieser
Erweiterung ist, dass sie eine bereits vorhandene Größe in
beobachtbare Statistiken übersetzt.

### 5. Durchgerechnetes Beispiel (Pflicht)

Kubische Normalform, `b=0, τ=1`, stabiler Ast `x*=√a`, `S_rec=2a`
(bereits vorhandene Formel). `σ²=0.02`, `Δt=1`:

| `a` | `x*=√a` | `S_rec=2a` | `Var=σ²/(2·S_rec)` | `ρ=e^(-S_rec)` |
|---|---|---|---|---|
| 0,5 | 0,7071 | 1,0 | 0,0100 | 0,367879 |
| 0,05 | 0,2236 | 0,1 | 0,1000 | 0,904837 |

Zehnfache Annäherung an die Cusp-Faltung (`a→0`) → zehnfacher
Varianzanstieg, Autokorrelation steigt von 0,368 auf 0,905. Inverse
Schätzung MUSS im Skript gegengeprüft werden:
`λ̂ = -ln(0.904837)/1 = 0.100000` — exakt der Eingabewert.

### 6. Pflicht: Gegenbeweis-Abschnitt

Der JSON-Report UND der Docstring MÜSSEN explizit auf Boettiger &
Hastings (2012) und Ditlevsen & Johnsen (2010) verweisen: steigende
Varianz/Autokorrelation ist NOTWENDIG bei `λ→0`, aber NICHT
HINREICHEND als Beweis einer nahenden Bifurkation (Fehlalarme bei
endlichen Datensätzen; reales Beispiel Dansgaard-Oeschger-Ereignisse
laut Ditlevsen & Johnsen als rauschinduziert, nicht bifurkationsbedingt
identifiziert).

### 7. Explizit NICHT Teil dieses Auftrags

- KEINE Schätzer-Pipeline für reale Zeitreihen (Fenstergrößen,
  Trendtests) — das gehört zu `identifiability`/`validation`, nicht
  hierher; diese Erweiterung bleibt Modellrechnung (Verification-Seite,
  nicht Validation).
- KEINE Gleichsetzung von `Var`/`S_rec` mit `beta_response` — im
  Docstring festhalten (bereits bestehende "Independence of
  beta_response"-Regel gilt unverändert).
- KEINE Änderung an `dynamics/core.py` — nur Aufruf von
  `recovery_rate_at_equilibrium`.

## Verifikation

`verify_early_warning_core.py`: (1) Beispiel oben exakt reproduziert,
(2) inverse Schätzung `λ̂` bestätigt Eingabe, (3) Kontrollfall `λ`
konstant (weit von der Falte entfernt) → `Var`/`ρ` bleiben stabil
zwischen zwei Parametersätzen.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. Neues Dokument `docs/early_warning_core.md`, MIT dem
   Gegenbeweis-Abschnitt.
3. `verify_early_warning_core.py` mit reproduzierbarem JSON-Report
   unter `verification/`.
4. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
5. Explizites Mapping auf Scheffer et al. (2009) UND auf
   `dynamics.core.recovery_rate_at_equilibrium`.
6. Boettiger & Hastings (2012) und Ditlevsen & Johnsen (2010) MÜSSEN
   im JSON-Report als Textfelder erscheinen — Abnahmekriterium.
7. KEINE Mutation von FORMALISM.md oder einem der anderen sieben
   Kerndokumente.
8. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m36-early-warning-signals`. Kann PARALLEL zu den
anderen Runde-3-Milestones bearbeitet werden — mehrere betreffen
ebenfalls `dynamics` (Fenichel/GSPT, Floquet, Panarchy-Cusp); jede
erhält eine EIGENE neue Datei in `dynamics/`, sodass nur
`dynamics/__init__.py` und `pyproject.toml` beim Merge triviale,
erwartbare Konflikte haben können. Bitte NICHT
`src/scoped_correspondence/__init__.py` oder `dynamics/core.py`
anfassen. Claude reviewed und merged erst nach Johanns OK.
