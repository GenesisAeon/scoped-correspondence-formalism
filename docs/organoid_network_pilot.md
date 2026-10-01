# Organoid-Netzwerk-Pilot (ON-Serie)

Teil von [`ORGANOID_NETWORK_ROADMAP.md`](../ORGANOID_NETWORK_ROADMAP.md);
Quellen: [`organoid_network_source_audit.md`](organoid_network_source_audit.md).
Synthetischer, methodischer Pilot, motiviert durch Chow et al. (2026). Er
rekonstruiert **keine** biologischen Mechanismen und setzt keine
Drei-Modul-Schwelle voraus.

## Vier Ebenen

| Ebene | Modul (`src/scoped_correspondence/validation/modular_networks/`) | Frage |
|---|---|---|
| System | `adaptive_model.py` | Zustandsdynamik, Budget, Hebb-Anpassung mit fester Kantenmaske |
| Beobachtung | `observation_controls.py`, `channels.py` | Was sieht der Messoperator (voll, Summe, Rauschen, endlicher Kanal)? |
| Auslesen | `decoders.py` | Welcher Decoder, welches Training, welche Splits, welche Einheit? |
| Schluss | `information.py`, `evaluation.py` | Information, PID, Gerichtetheit (nicht kausal), Evidenzdatensätze |

## Benutzung

```bash
python scripts/run_organoid_network_pilot.py --scenario exact
python scripts/run_organoid_network_pilot.py --scenario confounds
python scripts/run_organoid_network_pilot.py --scenario adaptive --config configs/organoid_minimal.json --output out/adaptive.json
python scripts/run_organoid_network_pilot.py --scenario real --data DIR   # blockiert (Exit 2), ON6b
```

`configs/organoid_minimal.json` ist die vorab deklarierte Konfiguration
des Benchmarks: N = 12, γ = 0,8, ℓ = 0,5, 12 Modellschritte, Fenster 6–12,
σ = 0,15, Eingangsamplitude 0,6, 40 Anpassungsversuche, 50 Versuche je
Reiz, 80/20-Split, 6 Läufe, sieben Bedingungen. Eine abweichende
Konfiguration wird beim Lauf abgewiesen.

## Lesart der Ergebnisse

- Gleiche Accuracy heißt nicht gleiche Information (BSC vs. Z-Kanal).
- Ein Scoreabfall des eingefrorenen Decoders ist kein Informationsverlust
  (Codeinvertierung, Sensor-Umordnung).
- Gerichtete Information ist keine Interventionswirkung (gemeinsamer
  Treiber).
- Die Einheit ist das Präparat bzw. der Simulationslauf, nie der Versuch.
- Δ-Unterschiede zwischen Bedingungen hängen am Ausgangsniveau — Auswahl
  am Ausgangspunkt gehört in jeden Kontrollarm.

## Ergebnisvokabular

`evidence_kind` × `empirical_status` nur in den erlaubten Kombinationen
(`exhaustive_finite`/`synthetic_only`, `analytic_argument`/`not_tested`,
`numerical_sample`/`synthetic_only`,
`empirical_evaluation`/`evaluated_on_declared_data` nur mit Datensatz-Hash).
Kein Gesamtscore, kein „Emergenz bestätigt“.
