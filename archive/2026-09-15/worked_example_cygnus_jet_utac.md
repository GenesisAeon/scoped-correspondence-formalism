# Durchgespielt: cygnus-jet-utac (P17) — Phase-3-Kandidat (2026-09-15)

Alle Aussagen unten direkt aus gelesenem und **numerisch nachgerechnetem**
Quellcode von `D:\mandala\cygnus-jet-utac\cygnus_jet_utac\`
(`system.py`, `jet.py`, `orbital.py`, `stellar_wind.py`, `accretion.py`,
`mirror_jet.py`, `efficiency.py`, `constants.py`, `_genesis_stubs.py`,
`benchmark.py`), nicht spekuliert.

## 0. Ausschluss-Policy-Check

`PACKAGE_REGISTRY.md` listet P17 (`cygnus-jet-utac`) als normales,
veröffentlichtes UTAC/CREP-Paket (Zeile 67, Status "published"). **Kein**
Eintrag in der climate/ecology-Ausschluss-Serie (die beginnt strukturell
erst ab P59) — Analyse regulär zulässig.

## 1. Enumeration: neun Klassen, davon EINE echte individuierte System

`CygnusJetUTAC` (Orchestrator), `UTAC_ODE`, `CREPTensor`,
`PhaseTransitionLoop`/`JetMirrorMachine`, `UnifiedLagrangian`, `RelJet`,
`CygnusOrbit`, `StellarWindModel`, `AccretionDisk`.

## 2. Individuationskriterium angewendet

- **`UTAC_ODE` (H(t), UTAC-Zustandsvariable) — INDIVIDUIERT.** Echte
  eigene Dynamik: `dH/dt = r·H·(1−H/H*)`, `H*(t) = K·tanh(σ·Γ(t))`,
  per **4th-order Runge-Kutta** integriert (`_genesis_stubs.py:88-117`,
  auch die genesis-os-Fallback-Version, nicht nur ein Platzhalter). Der
  Fixpunkt H* ist strukturell stabil (Standard-Logistik-ODE:
  λ = −r < 0 am Fixpunkt für H*>0) — echte, messbare eigene Stabilität.
  Klarster Individuations-Fall im bisher untersuchten Ökosystem, weil
  tatsächlich numerisch integriert wird, nicht nur eine statische Formel
  ausgewertet.
- **`CygnusOrbit` — VERWORFEN.** Reine deterministische Kepler-Kinematik
  (`phase(t) = ω·(t−t0) mod 2π`), keine eigene Dynamik, kein Zustand über
  die Zeit hinaus, der integriert würde — eine Uhr, kein System.
- **`StellarWindModel` — VERWORFEN.** CAK-β-Windgesetz (Castor, Abbott &
  Klein 1975), aber eine reine Funktion von `r` (Abstand) — kein eigener
  Zustand, keine eigene Zeitentwicklung.
- **`AccretionDisk` — VERWORFEN.** Reine Umrechnungs-/Skalierungs-Engine
  (Eddington-Normierung, `to_utac_H`/`from_utac_H`) — berechnet H(t) nicht
  selbst, liefert nur Hilfsgrößen. Exakt `resilience-core`s dritte
  Kategorie ("Engine ohne eigene Trajektorie").
- **`RelJet` — GEPRÜFT UND VERWORFEN, kein Excess-S nachweisbar.** Hat
  zwar eigenen Zustand (`_position`, `_direction`), der über die Zeit
  fortgeschrieben wird — aber die Richtungsänderung ist rein
  GETRIEBEN+DIFFUSIV (`propagate()`: deterministische Wind-Deflektion
  Richtung `wind_dir` plus additives Gauß-Rauschen), **keine
  rückstellende/selbststabilisierende Kraft**. Ohne externe Windkraft
  bliebe die Richtung einfach konstant (reiner Drift+Random-Walk) — das
  ist das Gegenteil von "gemessene Stabilität übersteigt naive
  Zusammensetzung" (Individuationskriterium, `system_layer_utac.md`
  Abschnitt 1). Kein eigenes System nach unserer Definition, auch wenn es
  wie eines aussieht (eigene Klasse, eigener Zustand, eigene Update-Regel).
- **`JetMirrorMachine` — VERWORFEN.** Ereignis-Detektor/Vergleicher
  (Ringpuffer + Schwellenwert-Vergleich), keine eigene S/K/R/V-Dynamik.
- **`CREPTensor` — VERWORFEN als System, aber wichtig als Signalquelle.**
  `Γ = (C·R·E·P)^(1/4)` wird JEDEN Schritt neu aus C/R/E/P berechnet
  (`system.py:296-313`), die ihrerseits aus Orbital-Phase, Wind-Ram-Druck
  und H(t)-Abweichung stammen — kein eigener Zustand über die Zeit, reine
  Momentaufnahme/Aggregation fremder Größen.
- **`UnifiedLagrangian` — VERWORFEN.** Statische Newtonsche
  Gravitationspotential-Formel, keine Dynamik.

**Ergebnis: 1 von 9 Klassen ist ein echtes individuiertes System** —
dasselbe Muster wie `afet-tensions` (2/7) und `resilience-core`
(Engine-Kategorie bestätigt, hier zusätzlich ein neuer Unterfall:
"getriebener/diffusiver Zustand ohne Rückstellkraft" bei `RelJet`, klar
unterscheidbar von echter Individuation).

## 3. Kopplung — NICHT prüfbar, weil nur EIN individuiertes System existiert

Die Methodik verlangt ≥2 individuierte Systeme, um eine Onsager-Matrix
L_ij aufzustellen (wie bei `afet-tensions`s β↔Γ(z)-Fund). Hier gibt es
nur `UTAC_ODE`/H(t) als echtes System — alle anderen Klassen sind
Projektionen/Engines, die H(t) *speisen* (Orbital→Wind→CREP→Γ→H) oder
*konsumieren* (H→Jet-Rauschskalierung, H→Mirror-Machine), aber selbst
keine Systeme sind. Es handelt sich um eine **lineare, gerichtete
Zufuhrkette**, keine Kopplung zwischen zwei Systemen im Sinne unserer
Coupling-Schicht.

**Nebenfund — toter Parameter:** `StellarWindModel.crep_R_component(t,
jet_pos)` nimmt `jet_pos` als Argument, verwendet es aber im
Funktionskörper NIRGENDS — es wird immer `r = CYG_ORBITAL_SEPARATION`
verwendet (`stellar_wind.py:159`, Kommentar erklärt das explizit als
Designentscheidung: Wind koppelt am Jet-Ansatzpunkt, nicht am
weit entfernten Jet-Kopf). Kein Bug (Verhalten ist beabsichtigt und
dokumentiert), aber der ungenutzte Parameter suggeriert eine
Jet-Position→Wind-Rückkopplung, die es tatsächlich nicht gibt — genau
die Art von Schein-Zyklus, vor der die Coupling-Schicht-Methodik warnt
(erst Kopplungsrichtung im Code verifizieren, nicht am Funktionssignatur
raten).

## 4. Zentrale Zahlenbehauptung nachgerechnet — bestätigt, aber TAUTOLOGISCH

`efficiency.py` behauptet: "Γ_jet = arctanh(0.10)/2.2 ≈ 0.0456 — the
first CREP-domain calibration for a stellar black hole system."

**Numerisch nachgerechnet (Python):**
```
Γ_jet = arctanh(0.10)/2.2 = 0.04560697624139799
recovered η = tanh(2.2 × Γ_jet) = 0.10000000000000002
```
Stimmt exakt. **Aber:** das ist eine reine algebraische Inversion einer
Gleichung mit einer Unbekannten (Γ) und zwei bereits vorgegebenen Werten
(η=0.10 aus Prabu et al. 2026, σ=2.2 als "Default") — bei JEDEM Wert von
σ ergibt dieselbe Inversion exakt η zurück. Das ist keine unabhängige
Messung/Bestätigung, sondern eine Definitionsgleichung.

**Kritischer Fund zu σ=2.2 selbst:** `constants.py:44-46` kommentiert
`UTAC_SIGMA_DEFAULT: float = 2.2` explizit als **"GenesisAeon ERA5
baseline"** — ERA5 ist ein Klima-Reanalyse-Datensatz, verwendet in den
Klima-/Arktis-UTAC-Paketen dieses Ökosystems, NICHT in Prabu et al. 2026
oder irgendeiner Cygnus-X-1-spezifischen Quelle. **Gegengeprüft:**
`amoc-utac/amoc_utac/constants.py:13` (ein AMOC-Klimapaket) verwendet
`UTAC_SIGMA: float = 2.2` — denselben Zahlenwert, wortwörtlich derselbe
generische Ökosystem-Default, nicht domänenspezifisch aus
Schwarzloch-Physik hergeleitet. (`UTAC_R_DEFAULT=0.12` dagegen weicht von
AMOCs `UTAC_R=0.08` ab — nur σ ist nachweislich identisch kopiert, nicht
beide Konstanten pauschal.)

**Konsequenz:** Γ_jet≈0.0456 ist real und reproduzierbar berechenbar,
aber NICHT "die erste CREP-Domänen-Kalibrierung für ein
Schwarzloch-System" im Sinne einer unabhängig hergeleiteten physikalischen
Konstante — es ist eine Umkehrung der einzigen echten Messung (η=0.10)
durch einen wiederverwendeten, domänenfremden Kopplungskoeffizienten.
Ein anderer σ-Default hätte einen komplett anderen "Γ_jet" ergeben, bei
identisch perfekter Rückgewinnung von η — klassisches Muster des bereits
in `afet-tensions` (Γ_domain) und `resilience-core` (GAMMA_MAX)
dokumentierten Zirkelbezug-Antipatterns
([[circular_calibration_constant_antipattern]]).

## 5. Der "Benchmark gegen Prabu et al. 2026" — alle sechs Ziele sind Konstruktions-Artefakte, keine unabhängigen Tests

`benchmark.py:17-24` listet sechs Beobachtungsgrößen. Einzeln
nachverfolgt, woher jede tatsächlich kommt:

| Ziel | Behauptet als | Tatsächliche Quelle im Code | Unabhängig? |
|---|---|---|---|
| `accretion_efficiency` (0.10) | Simulationsergebnis | IST η, das zur Γ_jet-Definition selbst verwendet wurde (Abschnitt 4) | **NEIN — tautologisch** |
| `jet_power_W` | Simulationsergebnis | `system.py:240`: linear so skaliert, dass bei H_mean≈η exakt `CYG_JET_POWER` (der Zielwert selbst) herauskommt | **NEIN — Zielwert direkt eingebaut** |
| `jet_velocity_c` (0.50) | Simulationsergebnis | `RelJet.__init__`: `beta: float = 0.5` — ein hartkodierter Eingabeparameter, keine Vorhersage | **NEIN — Eingabe, nicht Ausgabe** |
| `jet_extent_ly` (16.0) | Simulationsergebnis | `system.py:242-244`, Kommentar: *"Report as fixed"* — `CYG_JET_EXTENT` wird direkt zurückgegeben, nicht simuliert | **NEIN — konstant zurückgegeben** |
| `orbital_period_days` (5.6) | Simulationsergebnis | direkt aus `CYG_ORBITAL_PERIOD`-Eingabeparameter, keine Ableitung | **NEIN — Eingabe-Echo** |
| `dance_events_per_year` (2.0) | Emergentes Ergebnis der stochastischen Simulation | `jet.py:181-183`, Kommentar: *"σ = σ_base·√dt, calibrated so random walk ... gives ~2 crossings ... per year (seed=42)"* — die Rauschamplitude wurde EXPLIZIT so getunt, dass genau dieser Zielwert herauskommt | **NEIN — Rauschparameter auf Zielwert zurückgerechnet** |

**Alle sechs "bestandenen" Benchmark-Ziele sind entweder direkt
eingegebene Konstanten, die unverändert zurückgegeben werden, oder freie
Parameter, die explizit auf den Zielwert hin kalibriert wurden.** Der
Benchmark prüft die interne Konsistenz der Modellkonstruktion, nicht eine
unabhängige Übereinstimmung mit Beobachtungsdaten. Das ist ein anderer,
umfassenderer Fall des in `worked_example_resilience_core.md` Abschnitt 4
gefundenen Musters ("Kalibrierungsskripte lügen sich selbst an") — hier
liegt es nicht an einem übersehenen Fehler, sondern strukturell in der
Modellkonstruktion selbst.

## 6. Was trotzdem real und gut gemacht ist

Nicht alles ist Kalibrierungs-Artefakt — die zugrunde liegende Physik ist
großteils lehrbuchkorrekt und eigenständig implementiert, unabhängig vom
CREP/UTAC-Anstrich:
- **RK4-Integration** der UTAC-ODE (nicht nur Euler, nicht nur eine
  statische Formel) — methodisch solide.
- **CAK-β-Windgesetz** (Castor, Abbott & Klein 1975) korrekt umgesetzt
  (`velocity(r) = v_inf·(1−R*/r)^β`, Massekontinuität für Dichte).
- **Spezialrelativistische Jet-Kinematik** (Lorentz-Faktor,
  Rodrigues-Rotation für 3D-Richtungsänderungen) korrekt.
- **Kepler'sche Bahnmechanik** (Massenschwerpunkt-Aufteilung, dritte
  Kepler'sches Gesetz für die große Halbachse) korrekt.
- Die UTAC-Fixpunkt-Struktur `H* = K·tanh(σ·Γ)` UND die
  Differentialgleichung `dH/dt = r·H·(1−H/H*)` entsprechen exakt der in
  `system_layer_utac.md` Abschnitt 2 referenzierten UTAC-Kernmathematik —
  keine Abweichung, keine Ad-hoc-Erweiterung nötig.

## 7. Zusammenfassung gegen die Phase-1/3-Kriterien

- Individuationskriterium anwendbar? **Ja, sauber** — ergab exakt 1 von 9
  Klassen als echtes System, plus einen neuen, sauber abgegrenzten
  Sonderfall (`RelJet`: getrieben+diffusiv, aber nicht individuiert).
- Reale Kopplungsmatrix zwischen ≥2 Systemen? **Nein** — nur ein
  individuiertes System im Paket vorhanden, Coupling-Schicht hier nicht
  testbar (kein Fehler der Methodik, sondern eine Paket-Eigenschaft).
- Zahlenbehauptungen nachgerechnet? **Ja** — Γ_jet-Formel stimmt exakt,
  ABER die Kalibrierungskette dahinter (σ=2.2 domänenfremd, alle sechs
  Benchmark-Ziele tautologisch) entwertet die wissenschaftliche
  Kernbehauptung des Pakets ("erste CREP-Domänen-Kalibrierung").
- Latitude/Precariousness sinnvoll berechenbar? Nicht untersucht — mit
  nur einem individuierten System und rein monostabiler Logistik-Dynamik
  (kein Hinweis auf Bistabilität im Code) vermutlich nicht ergiebig ohne
  die Spitzen-Katastrophen-Erweiterung künstlich hinzuzufügen.

## Verdikt: **PARTIAL/COSMETIC FIT**

Gespalten, nicht einheitlich:
- **System-Schicht (UTAC): stark, genuin.** Die H(t)-Dynamik ist eine
  echte, numerisch integrierte, individuierte System-Instanz, exakt nach
  der referenzierten UTAC-Kernmathematik, eingebettet in überwiegend
  lehrbuchkorrekte reale Astrophysik. Eine Formalismus-Integration auf
  dieser Ebene (S/K/R/V-Methoden für `UTAC_ODE` ergänzen, explizite
  Resistance/Precariousness/Rate-Größen wie bei `resilience-core`s
  `coupling.py` nachrüsten) wäre sinnvoll und risikoarm.
- **Information-Schicht (CREP) und die Kernbehauptung des Pakets:
  schwach, irreführend.** Γ_jet ist eine tautologische Umkehrung mit
  einer domänenfremden, wortwörtlich aus einem Klimapaket kopierten
  Konstante; alle sechs "Benchmark"-Ziele sind Konstruktions-Artefakte,
  keine unabhängigen Tests. Die Selbstbeschreibung als "erste
  CREP-Domänen-Kalibrierung für ein Schwarzloch-System" ist beim
  aktuellen Stand nicht haltbar.
- **Coupling-Schicht (AFET): nicht anwendbar** innerhalb dieses Pakets
  (nur ein individuiertes System vorhanden) — könnte relevant werden,
  falls `cygnus-jet-utac` künftig über eine echte `genesis-os`-Integration
  (aktuell nur Stub-Fallback, `_GENESIS_AVAILABLE=False` im Normalfall)
  mit einem zweiten individuierten System gekoppelt würde.

**Empfehlung für Phase 3B:** falls dieses Paket in die Formalismus-
Integration aufgenommen wird, NUR die System-Schicht (UTAC_ODE) betreffen
— nicht die Γ_jet-Kalibrierungsbehauptung durch die Integration
aufwerten oder implizit bestätigen. Der Zirkelbezug-Fund (Abschnitt 4-5)
gehört unabhängig davon nach `FOLLOWUP_TICKETS.md`/`METRIC_REGISTRY.md`,
wie bereits bei `afet-tensions`/`resilience-core` gehandhabt — Fund
dokumentieren, Paketcode nicht ungefragt ändern.

Sources: alle Aussagen aus direkt gelesenem und numerisch nachgerechnetem
Code in `D:\mandala\cygnus-jet-utac`, Gegenprüfung gegen
`D:\mandala\amoc-utac\amoc_utac\constants.py`, 2026-09-15.

## Nachtrag (2026-09-15): Γ-Ehrlichkeits-Fix umgesetzt, v1.0.2 released

`efficiency.py`, `benchmark.py`, `CITATION.cff`, `.zenodo.json`: die
"erste CREP-Domänen-Kalibrierung"-Behauptung entfernt/korrigiert,
alle sechs Benchmark-Ziele als Konstruktionsartefakte gekennzeichnet
(Docstring-Note mit Verweis auf diese Analyse). Γ_jet-Zahlenwert
unverändert (bleibt eine reale, reproduzierbare Umkehrung -- nur die
Einordnung als unabhängige Kalibrierung wurde korrigiert). Kein Bug in
der UTAC-Dynamik selbst (anders als bei `amoc-utac`) -- hier war reine
Dokumentations-/Framing-Ehrlichkeit nötig, keine Verhaltensänderung.
