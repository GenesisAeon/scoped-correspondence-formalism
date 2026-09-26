# SCF — Annahmen, Gegenmodelle und Entscheidungen unter begrenzter Beobachtung — Roadmap (2026-09-26)

Antwort auf `prompts/Answers/nicht_stationäre_Treiber/SCF_ASSUMPTION_EVIDENCE_IMPLEMENTATION_PLAN.md`
(26. September 2026, geprüfter Ausgangsstand `84848a4`, tatsächlicher
Start-Commit dieser Roadmap: `398b919`, nach dem Followup-Review-Fix).

Johanns Auftrag (2026-09-26): "mach gern alles als Roadmap fertig und
dann arbeite es gern Schritt für Schritt ab" — dieselbe Disziplin wie bei
G0–G7 und den B/C-Serien: additive Module, Hand-Nachrechnung vor Code,
unabhängige Reproduktion jedes Kontrollfalls, `verify_*.py` mit gezielten
Verletzungen, volle Suiten-Regression nach jedem Paket.

## Pakete

| Paket | Inhalt | Abhängigkeit | Status |
|---|---|---|---|
| H0 | Bestandsaufnahme und Quellenvertrag | keine | ✅ erledigt |
| H1 | Endliche Aussagen und nichtleere Evidenz | H0 | offen |
| H2 | Tragende Annahmen und Inkonsistenzkerne | H1 | offen |
| H3 | Beobachtungsabhängige Identifikation | H1 | offen |
| H4 | Endliche Entscheidungen unter deklarierter Ungewissheit | H1 | offen |
| H5 | Integrierter Pufferpilot (K5, kontinuierlich) | H1, H4 | offen |
| H6a | Adapter an bestehende SCF-Berichte (Pflicht) | H1–H3 | offen |
| H6b | Optional: synthetischer Galaxienfall | H6a | offen |
| H6c | Zurückgestellt: echte SPARC-Berichte | H6a | 🚫 zurückgestellt |
| H7 | Dokumentation, CLI, CI, Abschluss | H1–H6a | offen |

Reihenfolge (Plan Abschnitt 14.1): H0 → H1 → H2 → H3 → H4 → H5 → H6a → H7.
K7 (Randomisierung) bleibt optionale Vertiefung, kein Pflichtteil.

## H0 — Bestandsaufnahme und Quellenvertrag (erledigt)

### Ausgangslage bestätigt

- Aktueller HEAD bei Beginn: `398b919` (Followup-Review-Fix, danach
  dieses Paket). Volle Regression zu diesem Zeitpunkt: 99/99
  `verify_*.py` grün (siehe `GALAXY_DYNAMICS_ROADMAP.md`).
- **Galaxien-Abhängigkeiten aus Plan §3.1 sind tatsächlich behoben, nicht
  nur behauptet:** F1 (lokales statt globales Minimum in der
  Profil-Likelihood) und F2 (Modellgüten auf unterschiedlichen
  Teilmengen gültiger Punkte) wurden im Followup-Review-Fix (`398b919`)
  unabhängig reproduziert und korrigiert — siehe
  `GALAXY_DYNAMICS_ROADMAP.md` Abschnitt "Followup-Review-Fix". Damit
  blockieren sie H6b nicht mehr (H6b nutzt ohnehin nur die
  Zwei-Radien-Anpassung aus `verify_galaxy_observation_maps.py`, die von
  F1/F2 nicht betroffen war). Yoons fehlender Volltext (G6) ist für
  dieses Paket ohne Bedeutung.

### Vorhandene APIs bestätigt (Code direkt geprüft, nicht nur Plantext übernommen)

| Baustein | Datei | Bestätigt |
|---|---|---|
| `partition_indicator` | `correspondence/controlled_markov.py:54` | ✅ existiert |
| `check_controlled_correspondence` | `correspondence/controlled_markov.py:149` | ✅ existiert, ein Bericht PRO Mikroaktion |
| `is_union_of_classes` | `correspondence/controlled_markov.py:305` | ✅ existiert, nimmt Partitionsmatrix `C`, nicht Labels direkt |
| `Scope`, `CorrespondenceReport`, `verify_conjugacy` | `correspondence/contract.py` | ✅ existiert (siehe G2-Nutzung) |
| `identifiability/core.py` | — | ✅ existiert, Produkt-Invarianzen/Rangkontrollen |
| `BufferSpec`, `sustained_safety_over_horizon` | `viability/coupled_buffer_cbf_qp.py:89,135` | ✅ existiert |
| `bellman_value` | `validation/sequential_information_pilot.py:82` | ✅ existiert |
| `DatasetManifest`, `ValidationReport` | `validation/core.py:92,191` | ✅ existiert |
| `MetaRuleUpdate` | `metarules/core.py:51` | ✅ existiert |
| Burkert/NFW Zwei-Radien-Anpassung | `verification/verify_galaxy_observation_maps.py` (`check_observation_equivalence_cross_family_degeneracy`) | ✅ existiert (aus G3) |

Kein einziger im Plan referenzierter Baustein war falsch benannt oder
fehlend — die Quellenlage des Plans ist zuverlässig.

### K1–K8 unabhängig nachgerechnet (vor jeder Implementierung, ohne die mitgelieferte Referenz zu nutzen)

Eigenständiges Python-Skript (bool/int/rational, kein SCF-Import, kein
Optimierer) — exakte Übereinstimmung mit allen im Plan genannten Werten:

| Fall | Nachgerechnet | Ergebnis |
|---|---|---|
| K1 | Minimale Supports von {A1,A2,A3,A4} für C=r | `{A1,A4}` und `{A1,A2,A3}` — genau 2, beide bestätigt |
| K1 | Minimale Inkonsistenzkerne mit A5=¬r | `{A1,A4,A5}` und `{A1,A2,A3,A5}` — bestätigt |
| K2 | A={¬p}: `\|S_A\|=4`, `p⇒q` überall wahr, `p` nirgends wahr | bestätigt; A={p,¬p}: `S_A=∅` bestätigt |
| K3 | `x²≤1` auf W={-1,0,1} vs. W'={-1,0,1,2} | gilt auf W, Gegenmodell `x=2` auf W' — bestätigt |
| K4 | F(2)={(0,2),(1,1),(2,0)}, nur (1,1) erfüllt "beide≥1" | bestätigt; `q=(x1-x2)²` Wertemenge `{0,4}` bestätigt |
| K5 | `min{x_i(0), x_i(0)+u_i-1}≥0`, B=1 unmöglich/B=2 möglich für gemeinsamen Eingriff | von Hand hergeleitet (affine Trajektorie, Minimum an den Intervallenden): (0,2)→u=(1,0), (1,1)→u=(0,0), (2,0)→u=(0,1); gemeinsamer Eingriff bräuchte `u1≥1 UND u2≥1`, also `u1+u2≥2` — bestätigt |
| K6 | Minimax wählt B (Worst-Case 6 vs. 10), Minimax-Regret wählt A (Regret 4 vs. 6) | bestätigt; Erwartungswert-Kreuzung bei `p=0,6` bestätigt |
| K7 | Beste deterministische Entscheidung: Regret 1; randomisiert `α=1/2`: Regret 1/2 | bestätigt (optionale Vertiefung) |
| K8 | `PC=CQ` exakt bei `P=I4`, Partition `{{0,1},{2,3}}`; `E={1}` keine Vereinigung von Makroklassen | bestätigt |

Alle 10 Prüfpunkte bestätigt. Das schafft Vertrauen in die Formeln, bevor
sie in H1–H5 als Code implementiert werden — es ist noch keine
Implementierung.

### Quellen (`docs/epistemic_sources.md`)

Siehe eigene Datei. Kurzfassung: S1/S2 (Gödel/Scott-Formalisierung,
AFP/IJCAI, nur als Beispiel für explizite Semantik referenziert, keine
eigene Isabelle-Anbindung), S3 (Alloy-Doku zur Scope-Grenze endlicher
Gegenmodellsuche), S4/S5 (Vacuity Detection, nur der explizite
Antezedens-Check wird implementiert, keine volle CTL*-Analyse), S6
(minimale vs. kleinste Mengen), S7/S8 (Manski: Identifikation und
Entscheidung bei Unterbestimmtheit), S9 (robuste Optimierung), S10
(CEGAR, nur als spätere Perspektive).

### Umfangsgrenze (Plan §6.3, hier übernommen)

Kein Freitext-Parser, kein `eval`. Exakter Kern nutzt bool/int/`Fraction`
(Python `fractions.Fraction`, keine neue Abhängigkeit). Explizite Budgets
(Standard: 4096 Kandidaten, 4096 untersuchte Annahmenteilmengen, insgesamt
1.000.000 Prädikatauswertungen). Ein Budgetabbruch bestätigt weder
Minimalität noch universelle Gültigkeit.