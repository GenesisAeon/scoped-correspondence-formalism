# Durchgespielt: neural-avalanche-utac (P20) -- Phase 3B, Formalismus-Fit-Prüfung (2026-09-15)

Alle Aussagen unten direkt aus gelesenem und **numerisch nachgerechnetem**
Code (`system.py`, `crep_neural.py`, `constants.py`, `homeostasis.py`,
`branching.py`, `ei_balance.py`, `avalanche.py`, `power_law.py`), sowie
Cross-Check gegen `amoc-utac/amoc_utac/constants.py`. Kein Code angefasst,
reine Analyse.

## 0. Policy-Check

`PACKAGE_REGISTRY.md` bestätigt explizit (Zeile 678-679): `neural-avalanche-utac`
ist NICHT Teil der 2026-08-31-Klima/Ökologie-Ausnahme -- die Registry listet
es eigens als eines der "non-climate UTAC packages", die von einem
Klimakatalog-Deny-List ausdrücklich ausgenommen sind. Domäne: Neurowissenschaft
(Gehirnkritikalität), kein Klima/Ökologie-Paket. Regulärer Prüffall.

**Wichtiger Vorbefund aus der Registry selbst (Zeile 1145-1150):** ein
früherer Grok-Durchgang fand bereits "the same universality language" wie
bei `amoc-utac` (dort entfernt) in `neural-avalanche-utac`s README,
CITATION.cff, UND einem Notebook namens `04_gamma_brain_universality.ipynb`
-- explizit als "future, separately-scoped pass" vermerkt, NICHT behoben.
Das ist ein unabhängiger, bereits dokumentierter Hinweis auf genau das
Problem, das dieser Bericht unten im Code selbst bestätigt.

## 1. Enumeration: was sieht nach einem System aus?

Acht Klassen: `NeuralAvalancheUTAC` (Hauptklasse, Diamond-Interface),
`NeuralCREPTensor`, `HomeostaticPlasticity`, `EIBalanceMonitor`,
`BranchingRatioEstimator`, `AvalancheDetector`, `PowerLawFitter`,
`EthicsGate`/`TensionMetric` (Hilfsklassen).

## 2. Individuationskriterium -- ein einziges echtes, individuiertes System

- **`NeuralAvalancheUTAC`:** hat einen echten Zustand `H(t)` (Branching
  Ratio σ_b) mit eigener Dynamik über `run_cycle()`. Individuiert.
- **`HomeostaticPlasticity`:** ist der TATSÄCHLICHE dynamische Motor --
  eine echte lineare Relaxations-ODE `σ(t+Δt) = σ(t) + r·(σ*-σ(t))·Δt`,
  r=0.15/h zitiert auf "Hengen lab in-vivo recordings (rat V1, 96h)".
  Genuine Eigenwertstruktur: λ = -r (immer negativ, monostabil,
  konvergiert immer gegen σ*=1). **S = -λ_max = +0.15** ist damit direkt
  aus dem echten ODE-Parameter berechenbar, NICHT aus einer zirkulären
  Konstante zurückgerechnet -- ein echter Pluspunkt (siehe Abschnitt 5).
  Kein eigenständiges "System" im Sinne der Methodik, sondern der interne
  Trajektorien-Motor von `NeuralAvalancheUTAC` -- wie `resilience-core`s
  dritte Kategorie ("Engine"), nur hier tatsächlich innerhalb desselben
  Pakets aufgerufen (nicht extern zugeführt).
- **`NeuralCREPTensor`, `BranchingRatioEstimator`, `AvalancheDetector`,
  `PowerLawFitter`:** reine Berechnungs-/Diagnose-Werkzeuge ohne eigene
  Trajektorie -- werden pro Zeitschritt neu auf die aktuellen Spike-Daten
  angewendet, tragen selbst keinen Zustand über die Zeit. Keine Systeme.
- **`EIBalanceMonitor`:** hat echte, plausible Logik (`compute_balance`,
  `gamma_modulation`, `from_branching_ratio`) -- aber **numerisch
  verifiziert: wird in `system.py`s `run_cycle()` NIRGENDS aufgerufen**
  (`grep -rn "_ei_monitor"` findet nur die Instanziierung in `__init__`,
  keinen einzigen Methodenaufruf im Simulationspfad). Totes Diagnose-Modul
  -- gelabelt, aber nicht ausgeführt. Direkter Treffer für den
  Prüfpunkt "wird CREP/UTAC-Dynamik tatsächlich berechnet oder nur
  behauptet?": hier eindeutig NUR behauptet.

**Ergebnis: EIN individuiertes System pro Paket** (wie bei den meisten
bisher geprüften Paketen), mit einem echten internen Motor
(`HomeostaticPlasticity`), aber keine zweite, gleichzeitig laufende
Komponente, mit der es INNERHALB des Pakets koppeln könnte.

## 3. Kopplungssuche -- keine reale Kopplung vorhanden, nur eine statische Zahlenübereinstimmung

Es gibt keine zwei koexistierenden Systeme innerhalb dieses Pakets, die
sich koppeln könnten (anders als bei `afet-tensions`s A↔B-Fund). Die
einzige "Kopplung", die das Paket selbst behauptet, ist die
**Cross-Package-"Universalität"** zu `amoc-utac` (P18):

> "Both AMOC ocean circulation and neural criticality converge to the
> same CREP value at the η = 50% homeostatic setpoint."

Das ist **keine Onsager-Kopplung** im Sinne der Kopplungs-Schicht -- es
fließt kein Fluss J zwischen den beiden Paketen, es gibt keinen
Kraftterm X, kein L_ij wird aus echten gemeinsamen Daten geschätzt. Es ist
ein **statischer Vergleich zweier unabhängig definierter Konstanten**
(`GAMMA_BRAIN` vs. `GAMMA_AMOC`), zur Laufzeit per
`abs(gamma_measured - GAMMA_AMOC) < 0.05` geprüft. Für die
Kopplungs-Schicht (AFET) gibt es hier folglich nichts zu individuieren --
weder reziprok noch gerichtet, weil gar keine dynamische Kopplung
vorliegt.

## 4. Numerisches Nachrechnen -- die "Universalität" ist eine Tautologie, kein Fund

**Schritt 1 -- der Γ-Rücktransport in `run_cycle()` ist eine mathematische
Identität, numerisch geprüft:**

```python
gamma = arctanh(sigma_b / K) / sigma_crep
H_target = K * tanh(sigma_crep * gamma)
```

Da `tanh(arctanh(x)) = x` für jedes x, folgt algebraisch
`H_target ≡ sigma_b`, UNABHÄNGIG vom Wert von `sigma_crep`. Numerisch
bestätigt für σ_b ∈ {0.3, 0.6, 1.0, 1.4, 1.8} bei σ=2.2 -- `H_target`
reproduziert `sigma_b` in jedem Fall exakt (bis auf Fließkomma-Rauschen
<1e-15). **Das bedeutet: der CREP-Γ-"Rücktransport", der laut Docstring
die UTAC-Dynamik antreiben soll, hat in `run_cycle()` schlicht KEINE
kausale Wirkung auf `H` -- er ist eine reine Umbenennung/Relabelung von
σ_b über eine invertierbare Funktion, kein Antriebsmechanismus.** Die
tatsächliche Rückkehr zu σ_b=1 passiert ausschließlich über den separaten
`self._homeostasis.update()`-Aufruf (Abschnitt 2), der von Γ und σ_crep
komplett unabhängig ist.

**Schritt 2 -- die "Γ_brain = Γ_AMOC = 0.251"-Übereinstimmung ist per
Konstruktion, nicht empirisch:**

Beide Pakete verwenden exakt dieselbe Formel `Γ = arctanh(η)/σ` mit
demselben, nicht domänenspezifisch hergeleiteten `σ=2.2`
("GenesisAeon default across all packages", wörtlich so kommentiert in
BEIDEN `constants.py`-Dateien):

| | Verhältnis η | Herkunft von η | σ | Γ |
|---|---|---|---|---|
| `neural-avalanche-utac` | H*/K = 1.0/2.0 = **0.50** | H*=1 real (Branching-Ratio-Kritikalität, Harris 1963/Beggs-Plenz), K=2 als plausible, aber nicht unabhängig hergeleitete "supercritical ceiling" | 2.2 | 0.2497 |
| `amoc-utac` | η = **0.50** | "50% weakening projection (Chavent et al. 2026)" | 2.2 | 0.2510 |

Beide η-Werte sind für sich genommen plausibel domänenspezifisch
motiviert (nicht erfunden, um die Übereinstimmung zu erzwingen) -- aber
die **Übereinstimmung der beiden η-Werte selbst (0.50 = 0.50) ist ein
Zufallsprodukt der jeweils gewählten Modellparameter** (hätte `K=2.5`
statt `2.0` gewählt worden -- ebenfalls physikalisch plausibel --, wäre
η=0.4 und die "Universalität" verschwunden), und das gemeinsame `σ=2.2`
ist in KEINEM der beiden Pakete unabhängig für die jeweilige Domäne
hergeleitet, sondern ein geteilter Ökosystem-Default. Damit ist die
"Cross-Domain-UTAC-Universalität" strukturell **dieselbe Antimuster-
Klasse wie Γ_domain in `afet-tensions` und GAMMA_MAX in
`resilience-core`**: eine geteilte, nicht unabhängig kalibrierte
Konstante erzeugt einen scheinbar bedeutsamen Zahlen-Zusammenfall, der
bei näherem Hinsehen aus der Formel selbst folgt, nicht aus unabhängiger
Messung zweier realer Systeme. Bestätigt exakt den bereits in der
Registry vermerkten Verdacht auf überzogene "universality language".

**Schritt 3 -- C/R/E/P ist NICHT unser neues S/K/R/V, sondern die alte
kanonische Bridge-Metrik:** `crep_neural.py`s vier Komponenten heißen
Coherence (AR(1)-Autokorrelation), Resonance (Power-Law-Exponent-Nähe),
Emergence (Fano-Faktor-Überschussvarianz), Permutation-Entropy -- exakt
die bereits an anderer Stelle dokumentierte "kanonische Bridge-CREP"
(Coherence/Resonance/Emergence/Potential), NICHT die neu hergeleiteten
Größen Stabilität/Kinetik/Reproduktionsfähigkeit/Verbindungsfähigkeit
aus `information_layer_crep.md`. Eine Übertragung auf unseren
Formalismus kann sich NICHT auf den Namen "CREP" allein stützen -- es
wäre eine komplett neue Übersetzungsarbeit nötig, keine Wiederverwendung.

**Schritt 4 -- die UTAC-ODE-Form weicht von UTACs eigener kanonischer
Form ab:** UTACs eigene Referenzgleichung ist entweder das logistische
Modell `dH/dt = r·H·(1-H/K)·tanh(σΓ)` oder die Sigmoid-Form
`P(R_ctrl) = L/(1+exp(-β(R_ctrl-Θ)))` (`system_layer_utac.md`). Die
tatsächlich implementierte Gleichung hier ist eine einfache lineare
Relaxation `dσ/dt = r·(σ*-σ)` (Abschnitt 2) -- kein logistischer
Selbstbegrenzungsterm, kein Sigmoid. Real, gut zitiert (Hengen-Labor),
aber strukturell nicht dasselbe Modell wie UTACs eigene kanonische
Gleichung -- nur mit UTAC-Vokabular überschrieben.

## 5. Was tatsächlich real und nicht-zirkulär ist (zur Fairness)

- **S = -λ_max = +r = +0.15/h** ist eine echte, aus einem realen ODE-
  Parameter (nicht aus dem Zielergebnis zurückgerechnet) berechenbare
  Stabilitätsgröße -- strukturell genau das domänen-neutrale Verfahren
  aus `information_layer_crep.md` Abschnitt 7 (Lyapunov-Exponent aus
  Trajektoriendaten/Modellparametern, kein gefitteter Zielwert).
- **Branching-Ratio-Schätzung (Harris 1963)**, **Avalanche-Detektion
  (Beggs & Plenz 2003)** und **Powerlaw-MLE-Fit (Clauset et al. 2009)**
  sind reale, etablierte, unabhängig zitierfähige Methoden -- korrekt
  implementiert (visuell geprüft, keine offensichtlichen Fehler), nicht
  erfunden.
- σ_b=1 als Kritikalitätspunkt ist ein echter, in der Literatur
  etablierter Referenzwert (nicht domänenspezifisch für dieses Paket neu
  erfunden).

## 6. Zusammenfassung gegen die Prüfkriterien

- Individuationskriterium anwendbar? Ja, ein echtes System
  (`NeuralAvalancheUTAC`, angetrieben von `HomeostaticPlasticity`s
  echter linearer Relaxations-ODE), keine Ad-hoc-Erweiterung nötig.
- S numerisch belastbar? **Ja** (S=+0.15, direkt aus realem ODE-Parameter,
  nicht zirkulär) -- ein positiver Befund.
- Reale Kopplungsmatrix zwischen ≥2 Systemen? **Nein** -- die einzige
  behauptete Kopplung (zu `amoc-utac`) ist keine dynamische Kopplung,
  sondern ein statischer, per Konstruktion tautologischer
  Konstantenvergleich (Abschnitt 4).
- CREP S/K/R/V tatsächlich berechnet? **Nein** -- das Paket berechnet die
  ANDERE (kanonische Bridge-)CREP-Bedeutung (C/R/E/P), nicht unsere
  S/K/R/V. Direkte Übernahme nicht möglich, nur Neuübersetzung.
- UTAC-Schwellenwertdynamik in kanonischer Form? **Nein** -- reale, aber
  strukturell andere (lineare statt logistische) ODE, nur mit
  UTAC-Vokabular gelabelt.
- Dead Code/nur behauptete Dynamik gefunden? **Ja** -- `EIBalanceMonitor`
  ist vollständig unbenutzt im Simulationspfad.

## Verdikt: **PARTIAL/COSMETIC FIT**

Kein `NO FIT`, weil es eine echte, individuierte, nicht-zirkuläre
Kernressource gibt (`HomeostaticPlasticity`s reale Relaxations-ODE mit
literaturzitiertem r, S=+0.15 sauber daraus ableitbar) UND real
angewendete, unabhängig etablierte Methodik (Harris/Beggs-Plenz/Clauset).

Kein `STRONG FIT`, weil (a) die eigene "CREP" die alte C/R/E/P-Bridge-
Metrik ist, nicht unser S/K/R/V, (b) die eigene "UTAC"-ODE strukturell
eine einfache lineare Relaxation ist, nicht UTACs kanonische
logistische/Sigmoid-Form, (c) die einzige behauptete Kopplung
(Cross-Domain-"Universalität" zu `amoc-utac`) numerisch nachweisbar eine
Tautologie aus geteilten, nicht unabhängig kalibrierten Konstanten ist,
keine echte Onsager-Kopplung, und (d) ein komplettes Diagnose-Modul
(`EIBalanceMonitor`) im Simulationspfad tot ist -- gelabelt, aber nicht
ausgeführt.

**Für eine echte Integration in den neuen Formalismus** müsste (1) die
"Universalität" entweder unabhängig neu hergeleitet oder als
konstruktionsbedingter Zufall offengelegt werden (deckt sich mit dem
bereits in `PACKAGE_REGISTRY.md` vermerkten "language fix"-Bedarf), (2)
eine echte Übersetzung der eigenen C/R/E/P auf S/K/R/V neu geleistet
werden (keine Wiederverwendung möglich), (3) `EIBalanceMonitor` entweder
tatsächlich verdrahtet oder als unbenutzt dokumentiert werden. Das ist
mehr Aufwand als eine reine "GrokBot-Implementierung" -- entspricht
strukturell eher einem eigenen kleinen Refit-Ticket (wie
`afet-tensions`s Γ_domain) als einer einfachen S/K/R/V-Methodenergänzung.

Sources: alle Aussagen aus direkt gelesenem und numerisch nachgerechnetem
Code in `D:\mandala\neural-avalanche-utac` und
`D:\mandala\amoc-utac\amoc_utac\constants.py`, 2026-09-15. Registry-
Querverweis: `PACKAGE_REGISTRY.md` Zeilen 678-679, 1145-1150.

## Nachtrag (2026-09-15): Sprachbereinigung umgesetzt, v1.0.1 released

Der bereits in `PACKAGE_REGISTRY.md` vermerkte "future language cleanup"
ist jetzt erledigt: `constants.py`, `system.py` (inkl.
`gamma_universality_check()`, Methodenname aus Kompatibilitätsgründen
beibehalten, nur die Behauptung korrigiert), `README.md` (inkl. dem
faktisch unfalsifizierbaren "Falsifiable Prediction"-Abschnitt),
`CITATION.cff`, `.zenodo.json` und das Notebook
`04_gamma_brain_universality.ipynb` (Ehrlichkeits-Hinweiszelle
eingefügt, Rest als korrekte Formel-Illustration belassen). Γ-Rücktransport-
Tautologie und `EIBalanceMonitor`-Totcode dokumentiert, nicht künstlich
verdrahtet. Zusätzlich: chronischer Python-3.10-CI-Fehler und 23
mypy-Altlasten behoben.
