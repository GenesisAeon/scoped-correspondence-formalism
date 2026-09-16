# Numerische Verifikation (ARCHIVIERT 2026-09-16, historisch)

**Diese Prüfung bezieht sich auf die inzwischen zurückgenommene
Formel `a=-S(Θ)` aus `system_layer_utac.md` Abschnitt 3.6 (Entwurf 1,
siehe `archive/2026-09-15/system_layer_utac.md`).** Diese Formel wurde
aus einer zentrierten kubischen Form hergeleitet, die -- wie die
ChatGPT-Astra-Review vom 15.9. zeigte -- nicht dieselbe Dynamik ist wie
die in Abschnitt 3.5 tatsächlich angegebene, uncentrierte Form
`R_ctrl³-a(R_ctrl-Θ)-b`. Diese hier bestätigten Ergebnisse sind daher
nur für die alte, inzwischen ersetzte Formulierung gültig. Die aktuelle,
korrigierte kubische Erweiterung (einheitliche Normalform `τẋ=-x³+ax+b`)
und ihre Verifikation stehen in `../../FORMALISM.md` Abschnitt 5 und
`../../verification/verify_formalism.py` (Checks `p01_cusp_branches_and_time`,
`p02_cusp_region`). Als historisches Dokument unverändert belassen.

---

`cusp_model_numerical_check.py` prüft zwei Behauptungen aus
`system_layer_utac.md` (Abschnitt 3.5/3.6) an einem synthetischen
Spitzen-Katastrophen-System (`V(x) = x⁴/4 − (a/2)x²`, x=R_ctrl−Θ, b=0) --
**kein echtes GenesisAeon-Paket, sondern eine Validierung der eigenen
Formeln an einem kontrollierten Testfall.**

## Ergebnis (2026-09-15)

1. **`a = −S(Θ)`** -- bestätigt exakt für a ∈ {−1, −0.3, 0, 0.3, 1, 2.5},
   inklusive des Umschlagpunkts a=0. λ_max wird dabei per numerischer
   Ableitung des Drifts geschätzt (nicht aus der geschlossenen Formel
   übernommen) -- eine echte unabhängige Prüfung, keine Tautologie.
2. **Latitude via Basin Stability ≈ analytische Sattelpunkt-Distanz √a**
   -- < 0,5% Abweichung für a ∈ {0.5, 1, 2, 4}, Fehler nur durch
   Sampling-Auflösung erklärbar.

## Gefundener und korrigierter Fehler

Der erste Testlauf hatte einen Vorzeichenfehler: die Störung wurde vom
Sattelpunkt WEG statt AUF ihn ZU angewendet, wodurch das System immer im
selben Becken blieb (100-300% "Fehler", tatsächlich ein Testfehler, kein
Modellfehler). Nach Korrektur der Störrichtung: siehe Ergebnis oben.
Dokumentiert statt stillschweigend korrigiert, wie im Rest des
Ökosystems üblich.

## Was das NICHT zeigt

Diese Verifikation bestätigt, dass unsere Herleitungen an einem
kontrollierten synthetischen System numerisch korrekt sind. Sie
bestätigt NICHT, ob `CREP_critical≈0.84` aus dem Frame Principle mit
`S(Θ)=0` übereinstimmt -- das bleibt eine offene, echte Messdaten
erfordernde Frage (siehe `system_layer_utac.md`, Abschnitt 3.7,
Punkt 10 in Abschnitt 5).
