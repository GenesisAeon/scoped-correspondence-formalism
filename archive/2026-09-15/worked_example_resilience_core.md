# Durchgespielt: resilience-core (P40) -- Phase 1, Beispiel 1/3 (2026-09-15)

Alle Aussagen unten direkt aus gelesenem und **ausgeführtem** Code
(`system.py`, `coupling.py`, `eigenrate.py`, `frame_principle.py`,
`rho_calculator.py`, `constants.py`, `benchmarks/*.py`, `tests/test_rho.py`).

## 1. Enumeration und Individuation -- eine neue Kategorie gefunden

Anders als bei `afet-tensions` (echte Systeme vs. reine Projektionen)
zeigt `resilience-core` eine DRITTE Kategorie: **ein Werkzeug/Engine, das
System-Schicht-Größen für extern zugeführte Trajektorien berechnet, ohne
selbst ein individuiertes System zu sein.**

`ResilienceCore` bekommt Γ(t) von AUSSEN (`run_cycle(gamma=...)`,
kommentiert: "typically from the paired domain package's
`get_crep_state()`") -- es erzeugt Γ nicht selbst, hat also keine eigene
Trajektorie/Dynamik, die unser Individuationskriterium (Excess-S>0 aus
eigener Komposition) prüfen könnte. Es ist kein "System" im Sinne von
Abschnitt 1 (`system_layer_utac.md`), sondern eine wiederverwendbare
BERECHNUNGSKOMPONENTE für die System-Schicht -- näher an `utac-core`
(reine Mathematik-Engine) als an einem individuierten Knoten.

**Praktische Konsequenz für die Methodik:** die Individuations-Enumeration
braucht drei, nicht zwei Kategorien: (a) echtes individuiertes System,
(b) reine Projektion/View (wie bei `afet-tensions`), (c) wiederverwendbare
Berechnungs-Engine ohne eigene Trajektorie (wie hier).

## 2. Mapping auf S/K/R/V und Kipp-/Resilienz-Größen

| resilience-core | Unsere Größe | Status |
|---|---|---|
| `eigenrate.λ* = r·tanh²(σΓ)` | Kandidat für S (Stabilität) | **NICHT unabhängig hergeleitet** -- eine angenommene Formel, keine aus echten Trajektoriendaten geschätzte Lyapunov-Rate (dasselbe Bedenken wie bei Γ_domain: plausible Form, aber nicht gemessen). |
| `criticality_margin = 1-Γ/Γ_max` | Kandidat für Precariousness | Strukturell passend (Distanz zu einer Obergrenze), ebenfalls Ansatz statt Messung. |
| `coupling.py`s `C_ij` / `coupling_factor` | **L_ij (Onsager) / Panarchy** | **Bereits real und korrekt implementiert** -- eigene Registry mit Vorzeichen-Semantik (positiv=destabilisierend, negativ=stabilisierend), passt exakt zu unserer Coupling-Schicht. Bestes Onsager-Beispiel im bisher untersuchten Ökosystem. |
| `coupling_load = total_load/C_critical` | strukturell ~ ρ (Auslastung) | Bestätigt unabhängig die Form meines P_info-Brücken-Vorschlags aus `system_layer_utac.md` Abschnitt 3.7 -- eine Auslastungsquote relativ zu einer kritischen Kapazität, real im Code, nicht nur Theorie. |

## 3. Ein VIERTER, unabhängiger "Frame Principle"-Fund

`frame_principle.py` implementiert noch eine eigene, vierte Variante
(neben Ursprungs-CREP, kanonischer Bridge-CREP, und
`v9_dimensional_emergence.md`s Frame-Stability-CREP(d)):
`frame_limit_gamma() = Γ_max·(1-σ_Φ)`, mit demselben σ_Φ=1/16 wie in
`utac-core`, aber einer VÖLLIG anderen Rolle (hier: eine Schwellen-Γ, ab
der Ρ gegen Null geht). Vermerkt für `METRIC_REGISTRY.md`, nicht dort
selbst eingetragen (folgt in Phase 2 / nächster Registry-Pflege).

## 4. Realer, verifizierter Fund: zwei der drei Kalibrierungs-Skripte lügen sich selbst an

Ausgeführt (2026-09-15), nicht nur gelesen:

| Domäne | Behauptet | Tatsächlich (Default-Parameter) | Offen gelegt? |
|---|---|---|---|
| AMOC | Ρ≈0.65 | 0.183 | **JA** -- Skript sagt selbst "Status: OPEN — pending amoc-utac (P18) timeseries", kein `rho_in_range`-Check überhaupt versucht. |
| Arctic | Ρ≈0.05±0.02 | **0.0 exakt** | **NEIN** -- `rho_in_range: false`, keine Warnung im Skript. |
| Sandpile | Ρ≈0.75±0.10 | 0.222 | **NEIN** -- `rho_in_range: false`, keine Warnung im Skript. |

**Ursache beim Arctic-Fall geklärt:** `GAMMA_MAX = 0.920` in
`constants.py` ist wortwörtlich der Arctic-Benchmark-Γ-Wert selbst
(`"Maximum observed Γ in the CREP Atlas (ERA5 Arctic...)"`)  -- die
Kritikalitätsmarge `1-Γ/Γ_max` wird für genau diese Domäne bei genau
diesem Γ-Wert IMMER exakt Null, per Konstruktion. Strukturell verwandt
mit dem Γ_domain-Zirkelbezug in `afet-tensions`: eine Konstante, die aus
dem Zielwert selbst gewonnen wurde.

**Kein Test deckt das ab:** `grep` über `tests/` findet keinen Aufruf von
`run_arctic_calibration()` oder `run_sandpile_calibration()` -- beide
Skripte haben nur ein `if __name__ == "__main__":`, werden also nie
automatisch ausgeführt. `tests/test_rho.py` selbst ist dagegen ehrlich
(Kommentar Zeile 3-10: erklärt explizit, dass die Ziel-Ρ-Werte
domänenspezifisches r brauchen, testet nur relative Ordnung, nicht die
absoluten Zielwerte) -- der Widerspruch liegt zwischen dem ehrlichen
Kern-Testsuite-Kommentar und den beiden unehrlichen (weil unkommentierten
und ungeprüften) Kalibrierungsskripten.

## 5. Zusammenfassung gegen die Go/No-Go-Kriterien (ROADMAP.md)

- Individuationskriterium anwendbar? Teilweise -- ergab eine wichtige
  dritte Kategorie ("Engine ohne eigene Trajektorie"), keine
  Ad-hoc-Erweiterung der Grundtheorie nötig.
- Neue fundamentale Kollision? Nein, nur ein weiterer (vierter)
  Namenskonflikt bei "Frame Principle"/σ_Φ -- bestätigt ein bekanntes
  Muster, kein neues Grundproblem.
- Reale Kopplungsmatrix gefunden? **Ja, bereits implementiert**
  (`coupling.py`), bestes Beispiel bisher.
- Latitude/Precariousness sinnvoll berechenbar? Precariousness-Kandidat
  ja (`criticality_margin`), Latitude/Bistabilität nicht untersucht (kein
  Anzeichen von Multistabilität in diesem Paket).

Sources: alle Aussagen aus direkt gelesenem und ausgeführtem Code in
`D:\mandala\resilience-core`, 2026-09-15.
