# Durchgespielt: "Viele Systeme pro Paket" an afet-tensions (2026-09-15)

Testfeld für die Methodik aus `DESIGN.md`/Chat: Enumeration von Systemen,
Individuationskriterium anwenden, Kopplungsmatrix aufstellen. Alle Aussagen
unten direkt aus dem gelesenen Quellcode von `afet-tensions`
(`system.py`, `beta_hierarchy.py`, `crep_redshift.py`,
`hubble_tension.py`, `s8_tension.py`, `ligo_prediction.py`,
`euclid_prediction.py`, `desi_prediction.py`), nicht spekuliert.

## 1. Enumeration: was sieht nach einem "System" aus?

Auf den ersten Blick sieben Klassen: `BetaHierarchyModel`,
`CREPRedshiftEvolution`, `HubbleTensionModel`, `S8TensionModel`,
`LIGOPrediction`, `EuclidPrediction`, `DESIPrediction`.

## 2. Individuationskriterium angewendet -- nur 2 davon sind echte Systeme

- **System A -- β-Hierarchie (`BetaHierarchyModel`):** hat einen echten
  Kontrollparameter (β) und eine eigene Antwortfunktion
  `h0_effective(β) = H0_ref·exp(β·σ_Φ·Γ_domain)`. Individuiert.
- **System B -- Γ(z)-Evolution (`CREPRedshiftEvolution`):** hat eine
  echte eigene Dynamik -- eine Differentialgleichung
  `dΓ/dz = κ·Γ·(1−Γ)` (logistisch, zwei Fixpunkte Γ=0, Γ=1),
  über Rotverschiebung z integriert. Individuiert.
- **`HubbleTensionModel`, `S8TensionModel`, `LIGOPrediction`,
  `EuclidPrediction`, `DESIPrediction`:** GEPRÜFT UND VERWORFEN als eigene
  Systeme. Jede dieser fünf Klassen hat KEINE eigene Dynamik -- sie
  rufen ausschließlich Methoden von A und/oder B auf und formatieren das
  Ergebnis (z.T. mit einer festen Toleranz/einem festen Jahr für die
  Falsifikationskriterien). `LIGOPrediction` ist sogar nur eine
  Konstante (`OMEGA_RIG_HZ`), keine Dynamik überhaupt. Kein Excess-S
  messbar, weil kein Zustand über Zeit/Kontrollparameter existiert, der
  gemessen werden könnte.

**Praktische Faustregel daraus:** die Zahl der Klassen im Code sagt nichts
über die Zahl der echten Systeme aus. `afet-tensions` hat 7 Klassen, aber
nur 2 individuierte Systeme -- der Rest sind Projektionen/Ansichten.

## 3. Kopplung zwischen A und B -- real, aber NICHT reziprok

Gefunden in `desi_prediction.py`, `h0_bao()`:
```python
beta_eff = beta_model.beta_from_h0(beta_model.h0_local()) * crep.gamma_at_z(z) / crep.gamma_at_z(0.0)
```
Das ist eine echte, im Code bereits existierende Kopplung: **System B
(Γ(z)) moduliert System A (β_eff) multiplikativ über das Verhältnis
Γ(z)/Γ(0).** In Onsager-Sprache: ein Kopplungskoeffizient
`L_{B→A} ≠ 0`.

**Richtung geprüft:** die umgekehrte Kopplung existiert NICHT --
`crep_redshift.py`s ODE (`dΓ/dz = κΓ(1−Γ)`) hat keinerlei Abhängigkeit
von β irgendwo im Code. Also `L_{A→B} = 0`.

**Das ist ein reales, konkretes Beispiel für nicht-reziproke Kopplung**
-- bestätigt die in `coupling_layer_afet.md` aufgestellte Regel direkt an
echtem Code: Onsager-Reziprozität ist der Normalfall/Standardannahme,
keine Notwendigkeit. Hier liegt einer der interessanten Abweichungsfälle
vor, nicht ein Fehler.

## 4. Kopplungsform: weder exp noch tanh -- eine dritte, einfachere Form

Die schon dokumentierten Formen (exp für H0, tanh für S8, siehe
`coupling_layer_afet.md` Abschnitt 2) sind die INTERNEN Antwortfunktionen
von System A bzw. B selbst -- keine Cross-System-Kopplungen. Die
tatsächliche Kopplung zwischen A und B (`β_eff = β_local · Γ(z)/Γ(0)`)
ist **linear/multiplikativ** -- de facto Onsagers ursprüngliche,
einfachste Form (`J = L·X` mit konstantem L), nicht exp oder tanh.
**Klarstellung für die Methodik:** exp/tanh sind Kandidaten für die
Antwortfunktion EINES Systems auf seinen eigenen Kontrollparameter;
lineare Skalierung ist die Standardform für die Kopplung ZWISCHEN zwei
bereits individuierten Systemen, wenn nichts Genaueres bekannt ist.

## 5. Konsequenz für die Γ_domain-Reparatur (DESIGN.md, weiterhin nicht umgesetzt)

Diese Analyse zeigt eine zusätzliche Kalibrierungsschwäche neben dem
bekannten Γ_domain-Zirkelbezug: `beta_eff` in `desi_prediction.py`
verwendet `beta_from_h0(h0_local())`, was **numerisch geprüft (2026-09-15)
exakt wieder `BETA_LOCAL` (1.8) zurückgibt** (1.7999999999999987, reines
Fließkomma-Rauschen) -- ein Rundtrip durch dieselbe Formel, ein zweiter,
kleinerer Fall desselben Zirkelbezug-Musters. Hier nur vermerkt, nicht
repariert (gleiche Begründung wie beim Haupt-Γ_domain-Fund:
`afet-tensions` bleibt unangetastet außer bei explizitem Auftrag).

## Zusammenfassung: die Faustregel für "viele Systeme pro Paket"

1. Nicht jede Klasse ist ein System -- Individuationskriterium
   (Excess-S>0, echte eigene Dynamik) tatsächlich anwenden, nicht raten.
2. Kopplungen zwischen echten Systemen im Code suchen (oft schon
   implizit vorhanden, wie hier), dann erst als L_ij explizit machen.
3. Reziprozität nicht annehmen -- Richtung explizit prüfen.
4. exp/tanh sind Formen für die Selbstantwort eines Systems, nicht
   automatisch für die Kopplung zwischen zweien -- linear ist der
   nüchterne Standardfall ohne weitere Information.
