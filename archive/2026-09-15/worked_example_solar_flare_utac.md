# Durchgespielt: solar-flare-utac (P21) -- Phase 3, Formalismus-Fit-Prüfung (2026-09-15)

Alle Aussagen unten direkt aus gelesenem und **ausgeführtem** Code
(`system.py`, `active_region.py`, `reconnection.py`, `crep_solar.py`,
`superflare.py`, `goes_loader.py`, `geomagnetic.py`, `constants.py`,
`benchmark.py`, `tests/*.py`), nicht spekuliert.

## 0. Policy-Check

`PACKAGE_REGISTRY.md` (Zeile 71): `solar-flare-utac` = P21, Status
"published", KEIN Eintrag in der 2026-08-31-Ausschlussliste
(P59, P60, P87–P97, P99–P103, P105–P117). Explizit bestätigt an anderer
Stelle im Registry (klimakatalog-Abschnitt): `solar-flare-utac` wird dort
namentlich als "non-climate UTAC package" aufgeführt, das
`klimakatalog`s eigene Climate-Deny-List korrekt ausschließt. Astrophysik,
keine Klima-/Ökologie-Domäne -- **regulärer Prüfkandidat, keine Ausnahme.**

## 1. Enumeration: sechs Klassen, drei Kategorien

`MagneticActiveRegion`, `ReconnectionThreshold`, `SolarCREP`,
`GOESLoader`, `SuperflareStatistics`, `GeomagneticStorm`.

## 2. Individuationskriterium angewendet

- **System A -- `MagneticActiveRegion` (H(t)):** hat eine echte eigene
  ODE (`dH/dt = r_buildup·(1−H) − λ·H`), RK4-integriert, mit
  stochastischer Störung und einem echten Reset-Mechanismus bei
  Schwellenüberschreitung. **Individuiert.**
- **System B -- `GeomagneticStorm`:** hat eigenen persistenten Zustand
  (`_dst_current`, `_storm_history`) UND eine eigene Relaxationsdynamik
  (`dst_recovery()`: exponentieller Zerfall `dst_0·exp(−t/τ)`, echte
  Eigenwertstruktur mit `λ = 1/τ_recovery = 0.1 hr⁻¹`). **Individuiert**
  -- separates System, nicht nur eine View auf System A.
- **`ReconnectionThreshold`:** zustandslose Gating-Funktion von (H, Γ) →
  λ. Keine eigene Trajektorie, keine Excess-S messbar. Fällt in die
  dritte Kategorie aus dem `resilience-core`-Beispiel: Berechnungs-
  Engine ohne eigenes System.
- **`SolarCREP`:** berechnet Γ(t) frisch aus externen Inputs (H, dH/dt,
  Flux-Fenster, Zyklusphase) bei jedem Aufruf -- kein eigener,
  rückgekoppelter Zustand über die Zeit (nur ein `_last_state`-Cache).
  Dieselbe "Engine ohne eigene Trajektorie"-Kategorie wie
  `ResilienceCore` in `worked_example_resilience_core.md`.
- **`GOESLoader`, `SuperflareStatistics`:** reine Daten-Generatoren/
  Statistik-Werkzeuge (Potenzgesetz-Sampling, MLE-Fit, Permutations-
  entropie). Keine Systeme.

**Ergebnis:** 6 Klassen, 2 individuierte Systeme -- dieselbe Faustregel
wie bei `afet-tensions` bestätigt sich erneut.

## 3. Kopplung A→B: real, nicht-reziprok (dritter Fall dieses Musters)

In `system.py`s `run_cycle()`: bei jedem `flare_triggered`-Ereignis wird
`result["energy_released_J"]` (System A) direkt an
`self._geomagnetic.predict_dst(flare_energy_J=...)` (System B)
übergeben -- eine echte, im Code bereits existierende Kopplung
`J_{A→B} ≠ 0`. Geprüft: **kein Rückweg** -- `GeomagneticStorm`s Output
(`dst_peak_nT`, `storm_class`) fließt nirgends zurück in `self._ar` oder
`self._reconnect`; es wird nur ins Ereignis-Log geschrieben. Damit
`L_{B→A} = 0`. **Dritte unabhängige Bestätigung** (nach `afet-tensions`
Γ(z)→β_eff und dem allgemeinen Prinzip aus `coupling_layer_afet.md`),
dass Onsager-Reziprozität der Normalfall, nicht die Notwendigkeit ist.

**Kopplungsform:** `predict_dst()` berechnet
`p_dyn = (v_cme/v_ref)² · η_flare` und `dst_injection = Q·p_dyn·1e12` --
bei festem `v_cme` **linear/multiplikativ** in `η_flare`, exakt dieselbe
"lineare Standardform für Kopplung zwischen zwei bereits individuierten
Systemen" wie bei `afet-tensions` gefunden, nicht exp/tanh.

**Systeminterne Antwortfunktion von B auf sich selbst** (`dst_recovery`,
reiner exponentieller Zerfall nach einer Störung) passt zum
exp-Kriterium aus `coupling_layer_afet.md` Abschnitt 2 (unbeschränkte,
ratenartige Relaxations-Observable → exponentiell) -- vierte
unabhängige Bestätigung dieses Kriteriums.

## 4. Numerisch nachgerechnet: S (Stabilität) für System A

Analytisch (Linearisierung der ruhenden ODE um ihren tatsächlichen
Fixpunkt): `d(dH/dt)/dH = −(r_buildup+λ_quiet) = −0.065` ⇒
`S = −λ_max = 0.065 > 0` (stabile Relaxation). **Numerisch bestätigt**
(RK4-Simulation, Störung um den Fixpunkt, exponentieller Fit der
Abklingrate): `−0.064999...`, auf 6 Nachkommastellen identisch.

**Wichtiger Nebenfund dabei:** der analytische Fixpunkt der ruhenden
ODE liegt bei `H* = r_buildup/(r_buildup+λ_quiet) = 0.06/0.065 ≈ 0.923`
-- NICHT bei `H_STAR_QUIET = 0.10`, wie der Docstring in `constants.py`
("Quiescent fixed point") und `system.py` ("H* ≈ 0.1") behaupten.
`H_STAR_QUIET` ist tatsächlich nur der Reset-Wert NACH einer Eruption,
kein echter Fixpunkt der ruhenden Dynamik selbst -- die ruhende Phase
strebt in Wahrheit monoton auf 0.923 zu (weit über der Eruptions-
schwelle 0.6) und wird ausschließlich durch den Reset-Mechanismus
selbst am Erreichen dieses Fixpunkts gehindert. Physikalisch plausibel
für ein Avalanche-/SOC-System (kein stabiler Zustand unterhalb der
Schwelle ist gerade das Kennzeichen solcher Systeme), aber die
Namensgebung "quiescent fixed point" ist irreführend -- es ist ein
Reset-Wert, kein Fixpunkt.

## 5. Kalibrierungs-Ehrlichkeit: drei von fünf offiziellen Benchmarks sind Tautologien

`benchmark.py`s `SolarBenchmark.run_all()` ausgeführt (nicht nur
gelesen):

```
[FAIL] gamma_solar: target=0.014, measured=0.01364 (tol=0.005, relative)
[PASS] xclass_energy_J: target=1e+32, measured=1e+32 (tol=0.5, log)
[PASS] power_law_index: target=1.8, measured=1.8 (tol=0.1, relative)
[FAIL] reconnection_timescale_min: target=10, measured=197.1 (tol=0.3, relative)
[PASS] flare_frequency_per_cycle: target=150, measured=150 (tol=0.2, relative)
```

**Drei der fünf Checks vergleichen eine Konstante exakt mit sich
selbst:**
- `_check_gamma_solar`: misst `SolarCREP().nominal().Gamma`, was per
  Konstruktion **identisch** `GAMMA_SOLAR` zurückgibt (`nominal()`
  reicht die Konstante nur durch, verifiziert: `nominal().Gamma ==
  GAMMA_SOLAR` → `True`).
- `_check_xclass_energy`: `measured = E_MAX_J`, `target = E_MAX_J`.
- `_check_flare_frequency`: `measured = XCLASS_PER_CYCLE`,
  `target = XCLASS_PER_CYCLE`.

Alle drei sind bei Konstruktion garantiert (nahezu) exakt -- keine
unabhängige Messung, keine Information. `_check_power_law_index`
generiert einen synthetischen Katalog MIT `POWER_LAW_INDEX_ALPHA` als
Sampling-Parameter und fittet denselben Exponenten dann zurück -- ein
Selbstkonsistenz-Test des eigenen MLE-Fitters, keine Prüfung gegen
echte GOES-Daten (die Docstring-Behauptung "1975–2026 GOES X-ray
catalog" wird hier NICHT tatsächlich eingebunden, es ist reine
synthetische Selbstprüfung).

**Trotzdem schlagen zwei Checks real fehl -- und niemand merkt es:**
- `gamma_solar`: `|0.01364−0.014|/0.014 ≈ 2.6%`, aber Toleranz ist nur
  0.5% -- die eigene tautologische Prüfung scheitert an einem
  Rundungs-Mismatch zwischen dem gespeicherten Präzisionswert und dem
  gerundeten Zielwert.
- `reconnection_timescale_min`: **Faktor ~20 daneben** (197 statt 10
  Minuten). Ursache numerisch verifiziert: bei
  `Gamma = 2·GAMMA_SOLAR ≈ 0.0273` liefert
  `tanh(σ_CREP·Γ) = tanh(2.2·0.0273) = tanh(0.06) ≈ 0.06` -- der
  CREP-Gate sättigt bei so kleinem `Γ_solar` nur zu 6%, weit entfernt
  von der für die 10-Minuten-Zielzeit nötigen Sättigung nahe 1. Das ist
  kein Zufallsfehler, sondern eine strukturelle Inkonsistenz zwischen
  der Größenordnung von `GAMMA_SOLAR` (≈0.0136) und dem behaupteten
  physikalischen Ziel (10 min) bei fixem `σ_CREP=2.2`.

**Warum das nie auffällt:** `grep` bestätigt, `SolarBenchmark` wird
NIRGENDS in `tests/` importiert oder ausgeführt -- nur `cli.py`s
`benchmark`-Befehl ruft es auf. Der tatsächliche Pytest-Ersatz
(`test_gamma_solar_value` in `test_diamond_interface.py`) prüft nur
dieselbe tautologische Konstante direkt, und
`test_reconnection_time_decreases_with_gamma` prüft nur eine
QUALITATIVE Monotonie-Eigenschaft, nie den quantitativen 10-Minuten-
Zielwert. **Exakt dasselbe Muster wie bei `resilience-core`**
(Kalibrierungsskript, das sich selbst anlügt, weil es nie in die
automatisierte Testsuite eingebunden wurde) -- hier zusätzlich
verschärft durch drei tatsächlich tautologische Prüfungen.

## 6. Latitude/Panarchy

**Latitude (Becken-Breite) nicht sinnvoll anwendbar in der klassischen
Form:** `MagneticActiveRegion` ist kein bistabiles System (keine zwei
koexistierenden stabilen Äste) -- es ist ein Schwellenwert-Reset-Modell
(Relaxations-Oszillator/Avalanche-Typ): monotoner Aufbau bis zur
Schwelle, dann harter Reset. Basin-Stability-Sampling im Sinne von
`system_layer_utac.md` Abschnitt 3 würde hier keine sinnvolle
Becken-Geometrie finden, weil es kein zweites Becken gibt, in das
gekippt werden könnte -- nur einen Sägezahn. Strukturell eher mit
Ashwins R-Tipping/Rate-abhängigen Übergängen verwandt als mit
Zeeman/Thom-Bistabilität.

**Panarchy/V:** die A→B-Kopplungsstärke aus Abschnitt 3
(`Q_COEFFICIENT · (v/v_ref)²`) ist der konkrete `L_{A→B}`-Wert -- real
vorhanden, nicht nur postuliert.

**Precariousness/Rate:** direkt aus dem Code ablesbar --
Precariousness `= H_THRESHOLD − H` (Abstand zur Eruptionsschwelle,
monostabiler Grenzfall der Formel aus `system_layer_utac.md` Abschnitt
3), Rate `= dH/dt`, beide bereits im laufenden Code berechnet
(`_build_utac_dict()`).

## 7. Zusammenfassung gegen die Go/No-Go-Kriterien

- Individuationskriterium anwendbar? Ja, ohne Ad-hoc-Erweiterung --
  ergab exakt dieselben drei Kategorien wie in `resilience-core`
  (echtes System, Projektion/View, Engine ohne Trajektorie).
- Neue fundamentale Kollision? Nein.
- Reale Kopplungsmatrix gefunden? Ja (A→B, nicht-reziprok, linear) --
  dritte unabhängige Bestätigung des "Onsager-Reziprozität ist
  Normalfall, keine Notwendigkeit"-Musters.
- Latitude/Precariousness sinnvoll berechenbar? Precariousness/Rate ja
  (direkt im Code), Latitude/Basin-Stability NICHT sinnvoll (kein
  bistabiles System -- Avalanche-Typ statt Kipppunkt-Typ, ein
  strukturell neuer, bisher nicht kategorisierter Systemtyp).

## Verdikt: **STRUKTURELLER FIT BESTÄTIGT, ABER MIT ERNSTEN, VERIFIZIERTEN KALIBRIERUNGSPROBLEMEN**

Erzwungene Einordnung in die drei vorgegebenen Kategorien: am ehesten
**PARTIAL FIT** -- nicht weil die Struktur kosmetisch/vorlagenhaft wäre
(das Gegenteil ist der Fall: zwei echte individuierte Systeme, eine
echte nicht-reziproke Kopplung, eine numerisch bestätigte
Stabilitätsgröße, ein neuer legitimer Systemtyp ohne Bistabilität), sondern
weil die KONKRETEN Zahlen, die das Paket als "validiert" präsentiert,
das bei genauerem Hinsehen nicht sind: drei tautologische Benchmarks,
zwei davon zusätzlich real fehlschlagend (einer davon um Faktor 20),
niemals von der automatisierten Testsuite erfasst, plus eine
irreführende "Fixpunkt"-Bezeichnung für einen reinen Reset-Wert. Die
Formalismus-STRUKTUR trägt hier eindeutig; die Zahlen, mit denen sie
gefüllt ist, brauchen einen echten, unabhängigen Kalibrierungs-Pass wie
bei `afet-tensions`/`resilience-core`, bevor sie als "central result"
zitiert werden sollten. Nichts am Paket selbst wurde verändert.

Sources: alle Aussagen aus direkt gelesenem und ausgeführtem Code in
`D:\mandala\solar-flare-utac`, 2026-09-15.

## Nachtrag (2026-09-15): Fixes umgesetzt, v1.0.1 released

`gamma_solar`-Benchmark-Check korrigiert (Ziel war eine gerundete
0,014-Literalkonstante statt der präzisen `GAMMA_SOLAR`, daher
Rundungs-Fehlschlag -- jetzt behoben, echter Fix). `reconnection_
timescale_min`s 20×-Diskrepanz bewusst NICHT erzwungen behoben --
mangels echter unabhängiger Daten in `constants.py` explizit als OPEN
dokumentiert. `H_STAR_QUIET`-Fehlbezeichnung korrigiert (Reset-Wert,
kein Fixpunkt). `CITATION.cff`s Cross-Domain-"erklärt die
Vorhersageschwierigkeit"-Behauptung korrigiert. Kein Bug in der
UTAC-System-Schicht selbst -- die bleibt wie im Verdikt oben
strukturell solide. PyPI Trusted Publishing hat fuer dieses Paket
nie funktioniert (siehe FOLLOWUP_TICKETS.md) -- Release-Code liegt
bereit, wartet auf Johanns pypi.org-Eintrag.
