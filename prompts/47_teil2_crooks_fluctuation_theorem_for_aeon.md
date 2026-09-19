Auftrag: Teil 2, Milestone — Crooks-Fluktuationstheorem — Erweiterung
von `thermo`. Aus Runde 3 (von einem der vier unabhängigen Agenten
vorgeschlagen; von Claude live gegen Crossref verifiziert — Johanns
Entscheidung: einzeln gefundene, aber eindeutig belastbare Kandidaten
werden unabhängig vom Konvergenzgrad übernommen).

## Quelle

G. E. Crooks, "Entropy production fluctuation theorem and the
nonequilibrium work relation for free energy differences", Phys. Rev.
E 60, 2721–2726 (1999), DOI 10.1103/PhysRevE.60.2721. **Von Claude
selbst live per Crossref-API verifiziert** (Titel/Autor/Zeitschrift/
Band/Seiten/Jahr exakt bestätigt, 2026-09-19). arXiv-Fassung:
cond-mat/9901352.

## Kernformel

Für einen Prozess, der ein System zwischen zwei Zuständen über ein
zeitabhängiges Protokoll treibt, mit Arbeit `W` und freier
Energiedifferenz `ΔF`:

    P_F(+ω)/P_R(-ω) = e^ω,   ω = β(W - ΔF)

Daraus folgt die Jarzynski-Gleichung als Spezialfall:
`⟨e^(-βW)⟩ = e^(-βΔF)`.

## Umfang dieses Auftrags

Neue Datei `src/scoped_correspondence/thermo/crooks.py`.

### 1. `thermo.crooks.work_ratio(work, delta_f, beta)`

`ω = β(W-ΔF)`, gibt `ω` und `e^ω` zurück.

### 2. `thermo.crooks.verify_crooks_ratio(p_forward, p_reverse, work, delta_f, beta, tol=1e-9)`

Prüft `p_forward/p_reverse ≈ e^(β(W-ΔF))` für gegebene (synthetische
oder Toy-)Wahrscheinlichkeiten.

### 3. `thermo.crooks.jarzynski_estimate(work_samples, beta)`

`ΔF̂ = -(1/β)·ln(mean(e^(-β·W_i)))` über eine gegebene Stichprobe von
Arbeitswerten (rein synthetisch/Toy, keine reale Messkampagne).

### 4. Durchgerechnetes Beispiel (Pflicht)

`β=1, ΔF=0, W=1`: `ω=1`, `P_F(+1)/P_R(-1)=e≈2.718281828`. Zusätzlich
ein Zwei-Zustände-Toy-Ensemble (selbst konstruiert, mit synthetischen
Arbeitswerten, die eine bekannte Gauß-Verteilung mit vorgegebenem `ΔF`
approximieren) und `jarzynski_estimate` darauf anwenden — Ergebnis MUSS
gegen den bekannten `ΔF`-Eingabewert konvergieren (Toleranz
dokumentieren, Stichprobengröße groß genug für stabile Konvergenz).

### 5. Explizit NICHT Teil dieses Auftrags

- KEINE Gleichsetzung mit Onsager-`L_ij`/`LijTransport` oder mit
  `A_ij` — im Docstring festhalten (Crooks ist eine
  Pfad-Ensemble-Aussage über Arbeit/freie Energie, kein linearer
  Transportkoeffizient).
- KEINE Verwechslung mit Schnakenberg (M18, Netzwerkthermodynamik,
  stationäre Ströme) — eigenständiges, additiv daneben stehendes
  Thema.
- KEINE Änderung an `thermo/core.py` oder `thermo/schnakenberg.py`.

## Verifikation

`verify_crooks_core.py`: (1) Beispiel oben exakt reproduziert
(`e≈2.718281828`), (2) Jarzynski-Schätzer konvergiert gegen den
bekannten `ΔF` (Toy-Ensemble), (3) Kontrollfall `W=ΔF` (kein
Nettotreiben) → `ω=0`, Verhältnis exakt 1.

## Abnahmebedingungen (Astra-Standard, unverändert)

1. Textformeln (LaTeX/Markdown), keine Bildformeln.
2. Neues Dokument `docs/crooks_core.md`.
3. `verify_crooks_core.py` mit reproduzierbarem JSON-Report unter
   `verification/`.
4. Durchgerechnetes Beispiel mit Zahlen AUS DEM SKRIPTLAUF.
5. Explizites Mapping auf Crooks (1999).
6. KEINE Mutation von FORMALISM.md, `coupling_layer_afet.md` oder
   einem der anderen sechs Kerndokumente.
7. Johann-OK vor jeder Aufnahme in einen "Kern"-Status.

## Lieferformat

Eigener Branch `aeon/m37-crooks-fluctuation-theorem`. Kann PARALLEL zu
den anderen Runde-3-Milestones bearbeitet werden. Bitte NICHT
`src/scoped_correspondence/__init__.py`, `thermo/core.py` oder
`thermo/schnakenberg.py` anfassen. Claude reviewed und merged erst
nach Johanns OK.
