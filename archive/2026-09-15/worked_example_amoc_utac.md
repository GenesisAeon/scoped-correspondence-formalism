# Durchgespielt: amoc-utac (P18) — Phase-3-Kandidat, Gruppe 1 (2026-09-15)

Alle Aussagen unten direkt aus gelesenem und teils selbst numerisch
nachgerechnetem Code (`system.py`, `constants.py`, `crep_amoc.py`,
`tipping_predictor.py`, `tension_metric.py`, `ethics_gate.py`,
`fingerprint.py`, `freshwater.py`, `rapid_loader.py`, `benchmark.py`),
Version 1.3.2, Hauptcheckout `D:\mandala\amoc-utac\amoc_utac\` (nicht die
beiden stale `.claude/worktrees/`-Kopien).

## 0. Policy-Check zuerst

`amoc-utac` ist **P18**, Registry-Domain-Tag `"UTAC, CREP"` (nicht
`"Pure-science-no-bridge"`). Der ausgeschlossene climate/ecology-Bereich
aus der 2026-08-31-Entscheidung ist explizit P59, P60, P87–P97, P99–P103,
P105–P121 (`PACKAGE_REGISTRY.md` Abschnitt "Why no UTAC/CREP/AFET bridge
in the climate/ecology series"). P18 liegt eindeutig außerhalb dieses
Bereichs, und die Registry selbst führt `amoc-utac` als Beispiel für ein
Paket mit "real, relevant context" im UTAC/CREP-Rahmen (Zeile 485). **Kein
Policy-Ausschluss — reguläres Individuations-Beispiel, volle Tiefe.**

## 1. Enumeration — acht Klassen, geprüft auf eigene Dynamik

`AmocUTAC` (Diamond-Wrapper), `RapidLoader`, `AmocFingerprintIndex`,
`FreshwaterTransport`, `CREPAmocTensor`, `TippingPredictor`,
`TensionMetric`, `EthicsGate`.

## 2. Individuationskriterium — nur EIN echtes System

- **`RapidLoader`, `AmocFingerprintIndex`, `FreshwaterTransport`,
  `CREPAmocTensor`:** reine Berechnungs-Engines ohne eigene Trajektorie
  über die Zeit — sie nehmen eine Zeitreihe/einen Wert entgegen und
  liefern eine Zahl zurück (dieselbe dritte Kategorie wie bei
  `resilience-core`: "Werkzeug ohne eigene Komposition"). Kein Excess-S
  messbar.
- **`TensionMetric`, `EthicsGate`:** reine Projektionen/Views auf bereits
  existierenden Zustand (wie `HubbleTensionModel` etc. bei
  `afet-tensions`) — `TensionMetric.update()` liest nur bereits
  berechnete `gamma`/`H`/`dH_dt` und formatiert eine gewichtete Summe;
  `EthicsGate.check()` liest nur die Tension und trifft eine
  Schwellenwert-Entscheidung. Keine eigene Dynamik.
- **`AmocUTAC` selbst:** Orchestrator/Diamond-Adapter, keine eigene
  Differentialgleichung — delegiert an `TippingPredictor`.
- **`TippingPredictor` — das einzige individuierte System.** Enthält die
  tatsächliche UTAC-ODE (`_ode()`, per `solve_ivp` integriert):
  `dH/dt = r·H·(tanh(σ·Γ(t))/K − H/K)`, mit echtem Fixpunkt
  `H*(Γ) = K·tanh(σ·Γ)` und einer echten Kontrollparameter-Trajektorie
  Γ(t). Das ist exakt UTACs kanonische Logistik-Schwellenform (aus
  `system_layer_utac.md`), numerisch integriert, nicht nur behauptet.

**Verhältnis 8 Klassen → 1 individuiertes System** — konsistent mit dem
bereits an `afet-tensions` (7→2) und `resilience-core` (gemischt, aber
nur `coupling.py` "hart") gefundenen Muster: Klassenzahl sagt nichts über
Systemzahl aus.

## 3. GAMMA_AMOC: derselbe Zirkelbezug wie afet-tensions' GAMMA_DOMAIN — numerisch bestätigt

`constants.py`: `GAMMA_AMOC = atanh(0.50) / 2.2`. Selbst nachgerechnet:

```
atanh(0.50)/2.2 = 0.249684611060934   (Code rundet auf "≈0.251" an mehreren Stellen)
tanh(2.2 · 0.249684611060934) = 0.5 exakt (bis auf Fließkomma-Rauschen)
```

Das ist die **identische Konstruktion** wie bei `afet-tensions`s
GAMMA_DOMAIN (aus dem Zielwert selbst zurückgerechnet, keine unabhängige
Messung) und `resilience-core`s GAMMA_MAX (Arctic-Γ = Arctic-Benchmark-Γ
selbst). Der Docstring in `system.py` benennt das sogar offen als
"Central result: Γ_AMOC = arctanh(η=0.50) / σ=2.2 ≈ 0.251" — als
Herleitung präsentiert, obwohl es eine Rückwärts-Konstruktion aus dem
Zielwert η=0.50 ist, keine Messung.

**`benchmark.py`s `gamma_formula_check()` prüft explizit `abs(arctanh(0.5)/2.2
− 0.251) < 0.001` — das ist eine Tautologie-Prüfung**, kein empirischer
Test. Sie kann per Konstruktion nie fehlschlagen.

## 4. Neuer, bisher nicht dokumentierter Fund: zwei entkoppelte Γ-Werte im selben Lauf

Das ist über den bekannten Zirkelbezug hinaus ein eigenständiger,
konkreter Befund, numerisch verifiziert:

**Zwei völlig unabhängige Γ existieren gleichzeitig:**

1. **"Diagnostisches" Γ** (`crep_amoc.py`, `compute_gamma()`) — eine
   echte gewichtete Summe aus vier datengetriebenen Komponenten
   (C=AR1-Anstieg, R=Fov-Resonanz, E=Varianzverhältnis, P=Permutations-
   entropie), berechnet in `system.py::_run_cycle()` aus der simulierten
   Zeitreihe. Fließt in `_crep_components`/`get_crep_state()` und in
   `TensionMetric`/`EthicsGate` ein.
2. **"Prädiktives" Γ** — der Fixwert `GAMMA_AMOC=0.2497` plus ein fester
   linearer Trend (`gamma_trend=0.0015`/Jahr), gesetzt in
   `TippingPredictor.__init__()` und verwendet in `simulate_utac()`.

**Verifiziert (Codepfad in `system.py::_run_cycle()`, Zeilen 133-138):**
`self._predictor.simulate_utac(t_span=..., H0=h0, gamma_trend=0.0015)`
übergibt **kein** `gamma`-Argument — `simulate_utac()`s interne
`gamma_func(t)` verwendet ausschließlich `self.gamma_amoc` (den
Prädiktor-eigenen Fixwert aus Konstruktionszeit), NIE das gerade
berechnete diagnostische Γ. Die tatsächlich simulierte Trajektorie
(`_utac_sim["H"]`, `_utac_sim["H_star"]`, und darüber
`_detect_phase_events()`s Schwellenwert-Durchgänge) hängt also
**vollständig vom zirkulären Fixwert ab, nicht vom diagnostischen,
datengetriebenen Γ.**

Zum Vergleich existiert im selben `_run_cycle()` noch ein DRITTER,
separat berechneter `h_star`-Wert (Zeile 141:
`h_star = self.K * math.tanh(self.sigma * gamma)`, mit dem
diagnostischen `gamma`), der in `_utac_internal`/`get_utac_state()`
landet — numerisch verschieden von `_utac_sim["H_star"]`, je nachdem wie
weit das diagnostische Γ vom zirkulären 0.2497 abweicht (Sensitivität
selbst geprüft: bei Γ=0.4 statt 0.2497 ist H*/K bereits 0.71 statt 0.50
— ein Sprung von 21 Prozentpunkten, nicht vernachlässigbar).

**Konsequenz:** `get_utac_state().H_star` und die per
`_detect_phase_events()` gemeldeten Kipppunkt-Jahre stammen aus zwei
verschiedenen, nie gegeneinander geprüften Γ-Quellen. Die
Kippjahr-Vorhersage (`predict_tipping_year()`) ist ausschließlich vom
zirkulären Fixwert getrieben — das diagnostische, aus (synthetischen)
Daten berechnete Γ hat auf die eigentliche Vorhersage keinen Einfluss,
obwohl der Code so gelesen werden könnte (und die Docstrings das
suggerieren: "As Γ increases under freshwater forcing, the fixed point
... drifts").

## 5. Noch ein Schritt tiefer: auch das diagnostische Γ testet nur sich selbst

`system.py::_run_cycle()` ruft immer `self._loader.synthetic_annual()`
auf (nie den YAML-Loader für echte RAPID-Daten) — die AMOC-Zeitreihe ist
**vollständig synthetisch erzeugt**, mit einem in `rapid_loader.py`
Zeile 78-83 **hart einprogrammierten exponentiellen Kollaps ab 2050**
(`strength = (baseline−2.0) · exp(−(y−2050)/80)`). Das diagnostische Γ
(AR1-Anstieg, Varianzverhältnis, Permutationsentropie — allesamt
klassische "critical slowing down"-Signaturen) wird also gegen eine
Zeitreihe berechnet, die per Konstruktion bereits kollabiert — die
"early warning signals" schlagen an, weil das Skript sie eingebaut hat,
nicht weil eine gemessene physikalische Beobachtung sie zeigt.
`benchmark.py::check_gamma()` prüft dann, ob dieses (auf synthetischen,
selbst-erfüllenden Daten berechnete) Γ nahe am zirkulären 0.251 liegt —
eine zweite, sich überlagernde Zirkelschluss-Ebene: Zirkel-Konstante
gegen Zirkel-Daten geprüft.

**Wichtig zur Einordnung:** das ist kein Vorwurf an das Paket als
"Fälschung" — `rapid_loader.py`s Docstring nennt die Methode offen
"synthetic time-series generator", und der Code versteckt das nicht.
Aber es bedeutet: weder der zirkuläre `GAMMA_AMOC`-Fixwert noch das
"diagnostische" datengetriebene Γ sind an echten RAPID-Messwerten
verifiziert — beide sind, auf unterschiedliche Weise, in sich
geschlossene Konstruktionen.

## 6. Ehrlicher Gegenbefund: der Code kennt sein eigenes Problem teilweise schon

`tipping_predictor.py`, Zeilen 147-155, eigener Kommentar (verbatim):
> "H0 is calibrated to sit almost exactly at the tipping threshold (by
> construction, gamma_amoc -> H* ~= 0.50*K), so the single deterministic
> run is numerically unstable right at that boundary..."

Das ist eine bemerkenswert offene Selbstdiagnose der Zirkel-Konstruktion
(anders als bei `afet-tensions`/`resilience-core`, wo der Zirkelbezug
unkommentiert war) — nur eben nicht bis zu der hier gefundenen
Konsequenz (zwei entkoppelte Γ, synthetische Selbstbestätigung)
weitergedacht. Auch `constants.py` dokumentiert vorbildlich eine echte
Korrektur (Ditlevsen 2057→2065 nach Autoren-Korrektur 2025) und eine
kritische Gegenstimme (Morr et al. 2026 Preprint) statt sie zu
verschweigen — dieselbe Ehrlichkeits-Disziplin, die an anderer Stelle im
Ökosystem (AMOC-Kalibrierungsskript als Vorbild in `resilience-core`,
schon vor dieser Session dokumentiert) positiv aufgefallen ist.

## 7. Kopplung — eine BEABSICHTIGTE, aber NICHT FUNKTIONIERENDE Kopplung gefunden

Der Code-Aufbau *suggeriert* eine Kopplung `L_{Γ_diagnostisch → H}`
(diagnostisches Γ soll über `h_star` die Systemdynamik beeinflussen) —
das ist strukturell genau das AFET-Bild (Γ als "Kraft" X, H als Fluss
J). Real verifiziert: diese Kopplung ist im tatsächlich simulierten Pfad
**nicht verdrahtet** (siehe Abschnitt 4) — ein konkreter, numerisch
belegbarer Bug, kein Interpretationsspielraum. Keine andere
Inter-System-Kopplung gefunden (nur ein individuiertes System vorhanden,
Kopplung würde ohnehin ≥2 Systeme brauchen).

## 8. UTAC-Struktur: strukturell korrekt, nicht das Problem

Die Fixpunktform `H*=K·tanh(σΓ)` und die ODE-Form entsprechen exakt
`system_layer_utac.md`s kanonischem Modell — das ist nicht der Fehler.
Individuationskriterium, cusp-Erweiterung etc. sind hier nicht das
Problem; das Problem liegt ausschließlich in der Kalibrierung der
Eingangsgröße Γ, nicht in der UTAC-Mathematik selbst.

## 9. Zusammenfassung gegen die Phase-1-Kriterien

- Individuationskriterium anwendbar? Ja, ohne Ad-hoc-Erweiterung — ein
  klares System von acht Kandidatenklassen.
- Neue fundamentale Struktur-/Namenskollision? Nein.
- Reale Kopplungsmatrix? Eine *beabsichtigte* Kopplung gefunden, aber
  als Bug nicht funktionsfähig — ein interessanter Negativ-Fund für die
  Methodik selbst (Codepfade können eine Kopplung *nahelegen*, ohne sie
  tatsächlich zu implementieren; das muss immer numerisch geprüft
  werden, nicht am Docstring abgelesen).
- Latitude/Precariousness sinnvoll berechenbar? `TensionMetric`s
  `τ_H = 1−H/K` ist strukturell eine Precariousness-artige Größe, aber
  auf denselben zirkulären Γ-Pfad angewiesen wie alles andere hier.

## Verdikt: PARTIAL/COSMETIC FIT — mit einem echten, unabhängig verifizierten Doppelbug

Die UTAC-Mathematik selbst ist ein **echter struktureller Treffer**
(kanonische Fixpunktform, real per ODE integriert, kein bloßes
Vokabular). Die Eingangsgröße Γ, auf der alles andere aufbaut, ist es
nicht: (a) `GAMMA_AMOC` ist zirkulär aus dem Zielwert
zurückgerechnet (identisches Muster wie `afet-tensions`/
`resilience-core`), (b) die tatsächlich simulierte Trajektorie
verwendet ausschließlich diesen zirkulären Fixwert, nicht das an sich
vorhandene, datengetriebene diagnostische Γ (unverdrahtete, aber im Code
suggerierte Kopplung — ein eigenständiger Bug), und (c) selbst dieses
diagnostische Γ wird gegen selbst-erfüllende synthetische statt echte
RAPID-Zeitreihen berechnet. Eine echte Formalismus-Integration (Phase
3B, Schritt 2) wäre hier NICHT nur eine Frage der S/K/R/V-Benennung,
sondern würde zuerst verlangen: (1) `GAMMA_AMOC` unabhängig neu zu
fitten (wie beim `afet-tensions`-Γ_domain-Refit, Daten dafür wären
RAPID/van-Westen-Originaldaten, nicht vorhanden in diesem Repo), (2) die
Kopplung diagnostisches-Γ→Simulation tatsächlich zu verdrahten oder
bewusst zu verwerfen, (3) offen zu benennen, dass die "early warning"
-Diagnostik aktuell an synthetischen, nicht realen Zeitreihen läuft.
Das sind reale Vorbedingungen, keine kosmetische Umbenennung — daher
"partial", nicht "strong fit", trotz der strukturell sauberen
UTAC-Mathematik.

Nichts an `amoc-utac` selbst wurde für diese Analyse verändert.

## Nachtrag (2026-09-15): echter Vorzeichenfehler gefunden und behoben

Beim Umsetzen der Γ-Ehrlichkeits-Doku (Refit-Ticket) fiel beim
Nachrechnen von `predict_tipping_year()` ein weiterer, unabhängiger,
tieferer Bug auf: `TippingPredictor.h_star()` war `K·tanh(σ·Γ)` --
**steigend** in Γ. Das bedeutet: steigende Süßwasser-Forcierung Γ zog
den Fixpunkt Richtung K (volle AMOC-Stärke) statt Richtung 0
(Kollaps) -- exakt entgegengesetzt zur eigenen Klassen-Dokumentation
("the fixed point ... drifts below K") und jeder zitierten Quelle.

Numerisch verifiziert vor dem Fix: `simulate_utac()` über 120 Jahre
bewegte H von 9,0 auf 12,7 Sv (Erstarkung statt Schwächung); der
deterministische Kippjahr-Lauf überschritt die Schwelle nie und fiel
still auf den Fallback `start_year+120=2144` zurück -- das erklärte
den bizarren `utac_deterministic_year=2144` bei gleichzeitigem
`utac_central_year=2024` mit exakt identischer 5%/95%-Bandbreite
(degenerierte Monte-Carlo-Streuung, da H0 exakt auf der Schwelle
kalibriert ist).

Auf Johanns Entscheidung ("Jetzt reparieren") korrigiert zu
`K·(1−tanh(σ·Γ))`. Da `AMOC_TIPPING_ETA=0.50` selbst-symmetrisch ist
(1−0,50=0,50), bleibt `GAMMA_AMOC` unverändert gültig -- nur die
Richtung von H*(Γ) für Γ≠Γ_AMOC war falsch. Nach dem Fix zeigt
`simulate_utac()` echte Schwächung (9,0→5,8 Sv über 120 Jahre) und die
Monte-Carlo-Streuung ist nicht mehr degeneriert. Release: v1.3.3.
Die entkoppelte diagnostische-Γ-Problematik (Abschnitte 4-5 oben)
bleibt bewusst unangetastet dokumentiert, nicht "repariert" --
Verdrahten würde nur einen ungeprüften Wert gegen einen anderen
ungeprüften (synthetisch-datenbasierten) Wert tauschen, keine echte
Validierung hinzufügen.
