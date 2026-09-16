# Durchgespielt: scope-resilience (P41) -- Phase 1, Beispiel 3/3 (2026-09-15)

Kein `DISCLAIMER.md` gefunden -- keine Policy-Ausnahme. Alle Aussagen aus
gelesenem UND ausgeführtem Code (`system.py`, `semantic_crep.py`,
`semantic_utac.py`, `path_monitor.py`).

## 1. Individuation -- echter Kandidat gefunden, mit Zeitachse

Anders als `aeon-jurist` hat dieses Paket eine echte, wenn auch simple,
Zeitachse: `PathDriftMonitor` akkumuliert Γ_sem über aufeinanderfolgende
`run_cycle()`-Aufrufe in einem gleitenden Fenster und berechnet
`dΓ_sem/dt`. Ein individuierbares System wäre hier **der Γ_sem-Pfad einer
Konversation über die Zeit**, nicht das Paket selbst (analog zu
`afet-tensions`: das Paket ist die Engine, das Individuum ist die
konkrete Instanz/Trajektorie). Individuationskriterium wäre grundsätzlich
anwendbar, sobald genug Γ_sem-Samples für eine echte Lyapunov-Schätzung
vorliegen (aktuell nur ein simpler Differenzenquotient, kein
Lyapunov-Exponent).

## 2. Vorbildliche Ehrlichkeitsstruktur -- besser als alle bisherigen drei Pakete

- `SemanticCREP.compute()` ist explizit als **Proxy** gekennzeichnet
  ("This is a proxy, not a measurement of real semantic drift"),
  `compute_from_content()` als die **echte**, inhaltsbasierte Alternative
  -- exakt die directly_stated/hypothesis-Trennung aus `semantic-map`.
- `get_domain_r()` wirft eine **echte `UserWarning`** zur Laufzeit, wenn
  ein unkalibrierter (`"estimate"`/`"conservative_default"`) r_sem-Wert
  verwendet wird -- aktive Offenlegung statt stiller Annahme. Kein
  anderes bisher untersuchtes Paket tut das.
- `calibrate_r()` bietet einen echten, unabhängigen Kalibrierungspfad
  (`r = Ρ_observed / (tanh²(σΓ)·(1-Γ/Γ_max))`) -- strukturell nahe am
  Γ_domain-Zirkelbezug-Muster, ABER hier explizit als Werkzeug für
  spätere echte Kalibrierung angeboten, nicht schon intern zirkulär
  verwendet (kein Aufruf von `calibrate_r()` mit dem eigenen
  Vorhersagewert als `rho_observed` gefunden).

## 3. Realer, numerisch verifizierter Fund: der behauptete Fixpunkt löst die eigene ODE nicht

`semantic_utac.py`s Docstring behauptet:
```
dH_sem/dt = r·H_sem·(1 − H_sem/K_sem)·tanh(σ·Γ_sem)
Fixpunkt: H*_sem = K_sem · tanh(σ · Γ_sem)
```
**Numerisch geprüft (2026-09-15):** für r=1, K=1, σ=2.2, Γ=0.5 ergibt
`H*_sem = 0.8005` -- eingesetzt in die eigene ODE ergibt
`dH/dt = 0.128 ≠ 0`. Der tatsächliche (einzige nichttriviale) Fixpunkt
der wie angegeben geschriebenen ODE ist `H_sem = K_sem` (dort exakt
`dH/dt = 0`), UNABHÄNGIG von Γ. Die Formel `K·tanh(σΓ)` wäre nur dann ein
echter Fixpunkt, wenn `tanh(σΓ)` stattdessen die KAPAZITÄT modulieren
würde (`dH/dt = r·H·(1 − H/(K·tanh(σΓ)))`), nicht die gesamte Rate --
plausible Korrektur, aber nicht bestätigt, nur als Hypothese vermerkt.

**Praktische Einordnung:** im tatsächlich ausgeführten Code wird die ODE
selbst NIE integriert -- `attractor()` berechnet direkt
`K·tanh(σΓ)` algebraisch, ohne je die Differentialgleichung zu lösen. Der
Fehler betrifft also die Docstring-Herleitung/Motivation, nicht das
Laufzeitverhalten des Pakets. Trotzdem real und dokumentationswürdig --
genau die Art Diskrepanz, die nur durch Nachrechnen auffällt, nicht durch
Lesen.

## 4. Precariousness/Kipp-Variable bereits im Code vorhanden

`is_hallucination_regime(h_sem, gamma_sem)`: `H_sem < H*_sem` ->
"hallucination regime", sonst "coherence regime" -- strukturell exakt
unsere Precariousness/Kipp-Variable (Distanz zu einer Schwelle, mit
zwei benannten Regimen auf beiden Seiten), unabhängig vom Fixpunkt-Fund
oben (die Regime-Logik selbst bleibt korrekt, nur die "Fixpunkt"-
Bezeichnung/Herleitung ist fraglich).

## 5. Kopplung: keine gefunden

Kein Onsager-artiges Kopplungsregister wie bei `resilience-core` --
`scope-resilience` behandelt jeweils einen einzelnen semantischen Pfad,
keine mehreren interagierenden Systeme. Kein Fund hier, kein Widerspruch
zur Methodik.

## 6. Zusammenfassung gegen die Go/No-Go-Kriterien (ROADMAP.md)

- Individuationskriterium anwendbar? Ja, konzeptionell (Γ_sem-Pfad über
  Zeit), noch ohne echte Lyapunov-Schätzung.
- Neue fundamentale Kollision? Nein.
- Reale Kopplungsmatrix? Nicht hier, aber bereits einmal bei
  `resilience-core` gefunden -- Kriterium insgesamt erfüllt.
- Latitude/Precariousness sinnvoll berechenbar? Precariousness-Analogon
  (`H_sem` vs. `H*_sem`) bereits im Code vorhanden und funktional korrekt.

Sources: `D:\mandala\scope-resilience\src\scope_resilience\*.py`, direkt
gelesen und (Abschnitt 3) numerisch ausgeführt, 2026-09-15.
