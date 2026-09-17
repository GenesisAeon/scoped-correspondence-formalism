# Folgetickets — Revision 3, 16. September 2026

## F15: Umbenennung CREP/UTAC/AFET → Scoped Correspondence Formalism (Teil 1, erledigt 2026-09-16)

Johanns Entscheidung nach Rücksprache: das Drei-Buchstaben-Akronym-Vokabular hat wiederholt zu falschen Cross-Layer-Identitäten verleitet (β=S, V=Panarchy=L, geteiltes σ=2,2). Neuer Name und neues Vokabular sollen diese Versuchung strukturell reduzieren, ohne die bereits veröffentlichten ~60 Ökosystempakete rückwirkend umzubenennen (zu teuer/riskant für ein reines Vokabular-Problem).

Basiert auf einem eigenständigen, unabhängig konvergierenden Vorschlag von Astra ([prompts/Answers/ChatGPTAstra2.md](prompts/Answers/ChatGPTAstra2.md)), der mit realen Vorbildern begründet (Mathlib-Naturalität, Sheaf-Theorie lokal/global, Williams-Beer/Kolchinsky-Trennung, equation-free restrict/lift, Sandia Verification-vs-Validation, PEP8, SemVer).

**Umgesetzt (Teil 1):**
- GitHub-Repo umbenannt: `GenesisAeon/crep-utac-afet-formalism` → `GenesisAeon/scoped-correspondence-formalism` (privat, bleibt privat).
- Lokales Verzeichnis umbenannt (Kopie+Verifikation+Löschen, da `mv`/`Rename-Item` durch einen transienten Windows-Lock blockiert waren — Dateizahl und Diff vor dem Löschen der alten Kopie bestätigt: 296/296 identisch).
- Dual-License ergänzt (fehlte bisher komplett): GPLv3-or-later für Code (`verification/*.py`), CC BY 4.0 für Dokumentation — Konvention aus `implosive-origin-utac` übernommen.
- [GLOSSARY.md](GLOSSARY.md): vollständige Begriffszuordnung (CREP→Observation, UTAC→Dynamics, AFET→Coupling, Selbstähnlichkeit→Correspondence, F08→Contextuality, F09→Information Decomposition, `verify_*`→Verification, künftige Realdatenprüfung→Validation) und Begründung, was NICHT umbenannt wird.
- [ARCHITECTURE_ROADMAP.md](ARCHITECTURE_ROADMAP.md): grobe Sicherung von Astras vollständigem Softwarebibliotheks-Vorschlag (Teil 2, 10 Module, 16-20 Wochen, 2-4 Entwickler:innen) — **nicht beauftragt**, nur damit nichts verloren geht.
- `README.md` Titel/Badges aktualisiert, auf Glossar verwiesen.

**Bewusst NICHT umgesetzt in dieser Runde:** vollständige Migration der Formalismus-Inhalte selbst (`FORMALISM.md` §-Inhalte, Layer-Dokumente, Dateinamen wie `sheaf_contextuality.md`) auf die neuen Begriffe — das ist Teil der "Core Extraction"-Phase in `ARCHITECTURE_ROADMAP.md`, eine eigene, noch nicht getroffene Entscheidung (Umfang, Ausführung selbst/Delegation/Team).

## F16: Teil 2, Milestone 1 — Correspondence-Kern (erledigt 2026-09-16)

Von Aeon geliefert (`prompts/07_teil2_correspondence_core_for_aeon.md`), per Claude-Review gemergt nach `master`:
- `verification/test_id_namespace.md`: Alias-Tabelle für alle 66 bestehenden Prüfungen (Provenienz erhalten, keine Neunummerierung).
- `src/scoped_correspondence/correspondence/contract.py`: typisierter `Correspondence`-Kern (`ModelRef`, `StateMap`, `TimeMap`, `Scope`, `ErrorMetric`, `Residual`, `CorrespondenceReport`), implementiert FORMALISM.md §1 (Konjugations-/Semikonjugationsschema) und `context_transformations.md` T1–T4.
- Verifiziert gegen 5 Legacy-Fälle (e11, T01–T04), Zahlen exakt reproduziert. Ein erster Prüflauf zeigte 0/5 wegen eines isolierten Testordners ohne die bestehenden Vergleichsdateien — kein echter Bug, aus dem echten Repo heraus 5/5 bestätigt.
- T01 von Hand gegen das Original-Beispiel in `context_transformations.md` §3 nachgerechnet (y′=−2/(1+t)² bei t=0 → −2): exakt bestätigt.
- Alle 8 Kerndokumente (FORMALISM.md + sieben Layer-/Erweiterungsdokumente) vor und nach dem Merge byte-identisch — unberührt wie zugesagt.
- Gemergt auf `master` nach Johanns Freigabe; Review-Branch `aeon/m1-correspondence-core` gelöscht.

## F17: Teil 2, Milestone 2 — Observation, Dynamics, Coupling (erledigt 2026-09-16)

Von Aeon geliefert (`prompts/08_teil2_observation_dynamics_coupling_for_aeon.md`), diesmal direkt als GitHub-Branch (kein ZIP mehr nötig), per Claude-Review gemergt nach `master`:
- `src/scoped_correspondence/observation/core.py`: `channel_capacity` (Shannon-Hartley), `retention` (mit `ScopeViolationError` bei kontinuierlichen Variablen), `realized_rate` (mit Einheiten-Guard gegen absolute-vs-Raten-Verwechslung).
- `src/scoped_correspondence/dynamics/core.py`: `sigmoid_response`, `recovery_rate_from_relaxation` (explizit unabhängig von `beta_response`, Docstring zitiert Befund A), `CubicNormalForm` mit Fixpunkten/Diskriminante/`S_rec`.
- `src/scoped_correspondence/coupling/core.py`: `PairwiseCoupling`, `AijInfluence`/`LijTransport` als komplett getrennte Dataclasses ohne gemeinsame Basis, `check_generic_structure` als reiner Strukturtest mit explizitem "das behauptet nicht GENERIC"-Disclaimer.
- `src/scoped_correspondence/legacy/adapters.py`: dünne Namensbrücke (`shannon_hartley_K`, `utac_sigmoid`, `onsager_L` usw.) — dokumentiert selbst ehrlich, dass sie "keine Wissenschaft neu definiert".
- 13/13 neue Prüfungen selbst nachgerechnet, exakt gegen Legacy-Werte (u.a. `p02_cusp_region`s Wurzel 1,3247179572447458 bei a=1,b=1 von Hand bestätigt — identisch zu einem früheren eigenen Nachrechnen).
- Alle 8 Kerndokumente inkl. `correspondence/` unverändert; alle 66 bestehenden Prüfungen weiter grün.
- Gemergt auf `master` nach Johanns Freigabe; Review-Branch `aeon/m2-observation-dynamics-coupling` gelöscht.

## F18: Teil 2, Milestone 3 — Closure, Viability (erledigt 2026-09-16)

Von Aeon geliefert (`prompts/09_teil2_closure_viability_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`:
- `src/scoped_correspondence/closure/core.py`: `is_exact_closure` (PC=CQ), `closure_error`/`propagated_error_bound` (die TV-Fehlerschranke), `reconstruct_from_projection` (Kreisrekonstruktion), `partition_matrix`/`candidate_macro_kernel` (Lumpability-Fälle) — mit einem ehrlichen Kommentar, der bewusst auf Renormierung verzichtet, um bit-identische Legacy-Werte für e06 zu erhalten.
- `src/scoped_correspondence/viability/core.py`: `has_safe_transfer` (implementiert direkt den Satz aus `context_transformations.md` §8), `shared_budget_conflict` (der gekoppelte-Budget-Gegenfall r10), `coupled_buffer_field`, `unequal_rates_sum_derivatives` (t07).
- Legacy-Adapter rein additiv erweitert (`exact_closure_PC_CQ`, `safe_transfer_scalar` usw.) — bestehende M1/M2-Funktionen unverändert.
- 11/11 neue Prüfungen selbst nachgerechnet. Zwei Zahlen von Hand gegengerechnet: `shared_budget_conflict`s Standardfall (a=[0,5;0,5], required=1, standalone_margin=0,25) direkt aus der Formel `a_i=max(0,W_i-r_i(e_i-b_i))` hergeleitet — exakt bestätigt.
- Alle 8 Kerndokumente sowie `correspondence/`, `observation/`, `dynamics/`, `coupling/` unverändert; alle 66 bestehenden Prüfungen weiter grün.
- Bewusst nicht Teil dieser Lieferung: `membership` (überlappende Systemzugehörigkeit) und ein allgemeiner Viability-Kernel-Solver — beide eigene, spätere Aufträge.
- Gemergt auf `master` nach Johanns Freigabe; Review-Branch `aeon/m3-closure-viability` gelöscht.

## F19: Teil 2, Milestone 4 — Membership & Shared Resources (erledigt 2026-09-16)

Von Aeon geliefert (`prompts/10_teil2_membership_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`:
- `src/scoped_correspondence/membership/core.py`: `MembershipMatrix` (binäres `M_eα`, mehrere Einsen pro Zeile erlaubt, gewichtete Einträge lösen `ScopeViolationError` aus), `double_count_stocks` (naive vs. korrekte Bestandssumme bei überlappender Zugehörigkeit), `joint_control_set` (T5: `U_joint = U_physical ∩ ⋂_α U_α` für Intervalle/Boxen, leerer Schnitt → `conflict: bool` statt Exception — bewusste Design-Entscheidung, dokumentiert), `t10_via_membership` (Kreuzprobe, ruft `viability.shared_budget_conflict` unverändert auf statt es neu zu implementieren), `view` (reiner Aufrufmechanismus für `y_α=π_α(z,c,t)`, keine neue Physik).
- Anders als M1–M3: keine bestehende Legacy-Prüfung für `M_eα`/T5 — die vier Prüfungen sind frische, von Hand nachrechenbare Beispiele, plus die geforderte Kreuzprobe gegen `t10_shared_budget_conflict`.
- 4/4 neue Prüfungen selbst nachgerechnet (eigener Skriptlauf, JSON bis auf Zeitstempel bit-identisch mit Aeons Bericht). Zwei Zahlen von Hand gegengerechnet: Doppelzählung (`M.T@x=[30,40]`, Summe 70 vs. `sum(x)=60`, Differenz 10) und leerer T5-Schnitt (`lo=max(0,0,0.5)=0.5 > hi=min(1,0.3,1)=0.3`) — beide exakt bestätigt.
- `MembershipMatrix` bewusst getrennt von `closure.partition_matrix` (keine gemeinsame Basis/Cast) — gleiche Disziplin wie `AijInfluence`/`LijTransport`.
- Alle 8 Kerndokumente sowie `correspondence/`, `observation/`, `dynamics/`, `coupling/`, `closure/`, `viability/`, `legacy/adapters.py` unverändert.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m4-membership` gelöscht.

## F20: Teil 2, Milestone 5 — Identifiability & Baseline Metrics (erledigt 2026-09-17)

Von Aeon geliefert (`prompts/11_teil2_identifiability_baselines_for_aeon.md`, nach einem ersten unvollständigen Lauf ohne `core.py`/Push selbst nachgezogen) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`:
- `src/scoped_correspondence/identifiability/core.py`: `delay_amplification`/`delay_conditioning_report`/`indistinguishable_delay_vectors` (e02, Konditionierungsfaktor `1/|sin α|`), `parameter_scaling_invariance`/`identifiability_jacobian_rank` (e12, `tanh(σΓ)`-Invarianz + Jacobian-Rang 1), `svd_emergence_vs_ei` (e09, `delta_svd=0.75` bei `EI=0`), `fixed_ensemble_data_processing` (e08, 150 DPI-Vergleiche bei Seed 1977), `effective_information_baseline` (e07, EI unter benannten Baselines), plus Bonus `predictive_states` (e15).
- Stärker als M1-M4: `verify_identifiability_core.py` lädt die echte, unangetastete `verification/extension_results.json` zur Laufzeit und prüft direkt dagegen, statt nur hartkodierte Erwartungswerte zu verwenden — von Claude verifiziert, dass die Datei unverändert ist und alle sechs referenzierten Prüfungen dort tatsächlich als „passed“ stehen.
- 6/6 neue Prüfungen selbst nachgerechnet (eigener Skriptlauf, JSON bis auf Zeitstempel bit-identisch mit Aeons Bericht). Zwei Zahlen von Hand gegengerechnet: `delta_svd=1*(1/1-1/4)=0,75` und die Jacobian-Kollinearität (`col1/a == col2/σ`) — beide exakt bestätigt.
- Alle 8 Kerndokumente, `ROADMAP.md` sowie `correspondence/`, `observation/`, `dynamics/`, `coupling/`, `closure/`, `viability/`, `membership/`, `legacy/adapters.py` unverändert.
- Bewusst nicht Teil dieser Lieferung: Dataset Manifest, Train/Holdout-Split, realer Datenpilot — bleibt Johanns Domänenentscheidung (`ROADMAP.md` §3), eigener späterer Auftrag.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m5-identifiability-baselines` gelöscht.

## F21: Domänen-Survey für den realen Validierungspilot (erledigt 2026-09-17)

Von Aeon geliefert (`prompts/Answers/M6_domain_pilot_candidates_2026-09-17.md`): Faktentabelle für 5 Kandidaten (afet-tensions, amoc-utac, cygnus-jet-utac, neural-avalanche-utac, solar-flare-utac), kein Ranking, kein Fit-Kriterium. Von Claude stichprobenartig gegen die lokalen Paket-Dateien geprüft: `data/hubble_tension_data.yaml` (5 H₀-Werte) und `data/cygnus_x1_radio_epochs.yaml` (18 Epochen, 4 Richtungswechsel) exakt bestätigt, alle referenzierten Dateien existieren lokal wie angegeben. Johann hat **cygnus-jet-utac** (Makrovariable `jet_pa_deg`) gewählt — vollständige 18-Punkte-Zeitreihe bereits im Repo, echter Zeit-Split möglich, kein externer Download nötig. Folgeauftrag: F22.

## F22: Teil 2, Milestone 6 — erster echter Datenpilot cygnus-jet-utac (erledigt 2026-09-17)

Von Aeon geliefert (`prompts/13_teil2_m6_cygnus_pilot_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. **Erster Auftrag auf echten Messdaten, nicht auf Legacy-Formel oder synthetischen Beispielen:**
- `src/scoped_correspondence/validation/core.py`: `DatasetManifest` sperrt den zeitlichen 9-Kalibrierung/9-Holdout-Split VOR jedem Fit; `split_epochs` wirft `ScopeViolationError` bei jedem anderen Split (Anti-Data-Snooping — von Claude verifiziert, dass es tatsächlich auslöst); `fit_relaxation_pa` bekommt nur Kalibrierungsdaten (verify-Skript inspiziert sogar den Quelltext der Funktion, um sicherzustellen, dass „holdout" darin nicht vorkommt); kein σ/Γ_jet-Reuse aus `cygnus-jet-utac`.
- Ergebnis: `model_rmse_holdout=3,0710` vs. `baseline_rmse_holdout=3,7045` (Persistenz), `model_beats_baseline=True`. Fit ist schwach identifiziert (`r=0,00015`, `pa_eq≈8416`) — faktisch eine lineare Drift, keine sinnvolle Relaxations-Gleichgewichtslage — ehrlich berichtet statt verschwiegen.
- 6/6 neue Prüfungen selbst nachgerechnet. Beide RMSE-Zahlen von Hand aus den Roh-Epochenwerten nachgerechnet (unabhängig vom gelieferten Code) — exakt bestätigt. Datendatei-Inhalt bit-identisch mit dem lokalen `cygnus-jet-utac`-Paket bestätigt (Git-Blob-Hash unterscheidet sich nur durch CRLF/LF; Laufzeit-SHA-256 im Skript stimmt mit der lokalen Datei überein).
- Alle 8 Kerndokumente sowie alle bestehenden Module unverändert; `worked_example_cygnus_jet_utac.md` (kein Kerndokument) erhielt einen additiven Hinweis auf den Anti-Zirkularitäts-Ausschluss.
- **Einordnung:** ein plausibles, bescheidenes erstes Ergebnis (linearer Trend schlägt Persistenz um ~17% RMSE) — keine Bestätigung der Relaxationsformel als solcher, siehe Identifizierbarkeits-Caveat oben.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m6-cygnus-pilot` gelöscht.

## F23: Teil 2, Milestone 7 — Optional Modules Hardening (erledigt 2026-09-17)

Von Aeon geliefert (`prompts/14_teil2_m7_optional_modules_hardening_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`:
- `src/scoped_correspondence/contextuality/core.py`: 1:1-Port von F08 (`EmpiricalModel`, `contextual_fraction`, `has_global_section`, Szenario-Builder). **F13-Scope-Guard umgesetzt:** `contextual_fraction`/`has_global_section` verlangen den Pflichtparameter `assumes_independent_contexts=True` — `False` oder Fehlen löst `ScopeViolationError` mit dem F13-Risikotext aus. Von Claude direkt getestet: löst bei fehlendem/`False`-Argument tatsächlich aus, funktioniert nur bei explizitem `True`.
- `src/scoped_correspondence/information_decomposition/core.py`: 1:1-Port von F09 (`pid_atoms_williams_beer`, `i_min_two_sources`, `ei_q_channel`, `blackwell_redundancy_binary_y`). **F12 TWO_BIT_COPY umgesetzt:** neue `blackwell_redundancy_finite_y` verallgemeinert die bisher binär-Y-beschränkte Blackwell-Redundanz per `scipy.optimize.linprog` (Vertex-/Mixture-Methode) auf vierwertiges Y. `two_bit_copy_report()` berichtet `Red_williams_beer=1,0` (irreführend) neben `RB0_blackwell=0,0` (korrekt), wie schon bei `EI_q` "daneben statt gleichgesetzt".
- 7/7 + 8/8 neue Prüfungen selbst nachgerechnet (eigener Skriptlauf, JSON bis auf Zeitstempel bit-identisch mit Aeons Bericht). Beide Skripte prüfen nachweislich gegen die echten, unveränderten `verify_sheaf_contextuality_results.json`/`verify_pid_rb_results.json` (nicht nur gegen hartkodierte Zahlen).
- TWO_BIT_COPY-Zahlen unabhängig von Hand hergeleitet: da Y=(A,B) beide Bits exakt bestimmt, gilt `I(Y=y;A)=I(Y=y;B)=1` Bit für jedes y → `Red=1, Unq1=Unq2=0, Syn=1, I_joint=2` — exakt bestätigt. `RB(0)=0` als literaturbekanntes korrektes Blackwell-Ergebnis bestätigt (A- und B-Partitionen von Y sind unabhängig, keine nichttriviale gemeinsame Degradierung möglich).
- Legacy-Skripte (`verify_sheaf_contextuality.py`, `verify_pid_rb.py`) und alle 8 Kerndokumente (inkl. `sheaf_contextuality.md`, `pid_redundancy_bottleneck.md`) unverändert; `scipy` neu als echte Paketabhängigkeit aufgenommen.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m7-optional-modules-hardening` gelöscht.

## F24: Teil 2, Milestone 8 — Thermo & Memory (erledigt 2026-09-17)

Von Aeon geliefert (`prompts/15_teil2_m8_thermo_memory_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`:
- `src/scoped_correspondence/thermo/core.py`: `heat_generic_example` (F13-Port, ruft `coupling.check_generic_structure` unverändert auf statt es neu zu implementieren), `stochastic_inverse_not_detailed_balance` (e10-Port, Drei-Zyklus-Gegenbeispiel), `project_generic_structure` (neu — Kongruenztransformation `J'=Π J Πᵀ`, `M'=Π M Πᵀ`, verlangt explizite `grad_E_prime`/`grad_S_prime` ohne stillen `Π@grad`-Default, mit Pflicht-Disclaimer, dass algebraischer Strukturerhalt kein gültiges reduziertes GENERIC-System belegt).
- 6/6 neue Prüfungen selbst nachgerechnet (eigener Skriptlauf, JSON bis auf Zeitstempel bit-identisch mit Aeons Bericht). Skript prüft nachweislich gegen die echte, unveränderte `extension_results.json`. Drei Zahlen von Hand gegengerechnet: Entropieproduktion beim ersten Parametersatz (`0,1*10²/(250*260)=0,000153846...`), Summen-Projektion `M'=0` (folgt aus dem bereits verifizierten `M@[1,1]=0`), Einzel-Projektion `M'=G*ta*tb=6500` — alle exakt bestätigt.
- `coupling/core.py`, `closure/core.py`, alle 8 Kerndokumente (inkl. `coupling_layer_afet.md`) sowie alle anderen Module unverändert.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m8-thermo-memory` gelöscht.

## F25: Teil 2, Milestone 9 — Metaregeln (Prompt gesendet 2026-09-17, noch offen)

Prompt an Aeon: [prompts/17_teil2_m9_metarules_for_aeon.md](prompts/17_teil2_m9_metarules_for_aeon.md). Erste von mehreren geplanten "Ast verbreitern"-Erweiterungen (Johanns Wunsch, natürliche mathematische Anschlüsse an den Ist-Stand zu prüfen; parallel läuft ein DeepResearch-Auftrag für weitere Kandidaten, siehe `prompts/16_deepresearch_natural_extensions.md`). Implementiert die bisher fehlende Metaregel-Dimension `m` aus `context_transformations.md` §6 (`m′=H(m,z,c,u,t)`, T5 mit `m`-Argument, Prioritätsregel gibt explizit eine Anforderung auf, unbeobachtetes `m` bricht Geschlossenheit). Ruft `membership.joint_control_set` und `closure.is_exact_closure`/`closure_error` unverändert auf, keine Änderung an M3/M4. Keine bestehende Legacy-Prüfung — frische Beispiele wie bei F19 (Membership). Noch nicht geliefert.

## F26: DeepResearch-Antwort ChatGPTAstra3.md geprüft (erledigt 2026-09-17)

`prompts/Answers/ChatGPTAstra3.md` (Antwort auf `prompts/16_deepresearch_natural_extensions.md`): 10 unabhängige Erweiterungsvorschläge, je an genau einen bestehenden Baustein angeschlossen (keine Cross-Layer-Identität). Von Claude verifiziert: alle durchgerechneten Zahlenbeispiele von Hand nachgerechnet (Kontraktionsraten, Dissipativitätsbeispiel `V̇=-5`, CBF-Bedingung `u+x≥0`, Split-Conformal-Quantil `q=3`, Schnakenberg-Entropieproduktion `ln2`) — alle korrekt. Alle 12 neuen Zitate per Fork unabhängig gegen DOI/arXiv geprüft (Titel/Autor/Jahr/Inhalt) — keine Fabrikation, keine Fehlzuschreibung, insbesondere Kolchinsky 2022 (Blackwell-PID) vs. Kolchinsky 2024 (Redundancy Bottleneck, bereits in F09 genutzt) als zwei echte, verschiedene Arbeiten bestätigt (genau die Art Verwechslung, die bei Rosas 2019/2020 früher schon passiert war). Vier "hoch"-priorisierte Kandidaten: Approximation Certificates (`correspondence`), Formal Reduction Error Bounds (`closure`), Control Barrier Functions (`viability`), Split Conformal Prediction (`validation`). Erster Umsetzungsauftrag: F27.

## F27: Teil 2, Milestone 10 — Approximation Certificates (Prompt gesendet 2026-09-17, noch offen)

Prompt an Aeon: [prompts/18_teil2_m10_approximation_certificates_for_aeon.md](prompts/18_teil2_m10_approximation_certificates_for_aeon.md). Erste Umsetzung aus F26 — `ApproximationCertificate` für `correspondence`, Girard & Pappas 2007 (DOI 10.1109/TAC.2007.895849). Ausdrücklich nur der Spezialfall mit fester `StateMap T` (nicht die volle relationale Simulationsdefinition) — `relation_kind` muss das explizit ausweisen. Ruft `Correspondence.conjugacy_residual`/`verify_conjugacy` unverändert auf. Durchgerechnetes Beispiel (`ẋ=-x, ẏ=-y+0.1`, `|x(t)-y(t)|≤0.1`) bereits von Claude von Hand bestätigt. Noch nicht geliefert.

## Neue Forschungsaufgaben aus Revision 3

Die Literaturanschlüsse und synthetischen Gegenprüfungen sind in den Dokumenten ausgearbeitet. Die folgende empirische bzw. paketbezogene Umsetzung bleibt offen.

| ID | Gegenstand | Abnahmekriterium | Status |
|---|---|---|---|
| R3-01 | Eine Domäne für Makro-Geschlossenheit auswählen | Zustände, Eingänge, Sampling, Partition und vorab festgelegte Fehlertoleranz mit Horizont dokumentiert | offen |
| R3-02 | Zustand versus Gedächtnis vergleichen | Markov-, Delay- und Gedächtnismodelle bei kontrollierter Komplexität auf unabhängigen Bedingungen verglichen | offen |
| R3-03 | Interventionsmodell für EI begründen | q_Z, q_M, Anhebung Λ und tatsächliche Eingriffsmöglichkeiten bzw. Identifikationsannahmen angegeben | offen |
| R3-04 | NIS+/PID nur gezielt evaluieren | Zielmetrik festgelegt; passende Baseline und Datenaufteilung; keine Gleichsetzung verschiedener Emergenzwerte | offen |
| R3-05 | Thermodynamische Modellreduktion prüfen | Energie-/Entropiebilanz und Geschlossenheitsfehler vor/nach Projektion separat berichtet | offen |
| R3-06 | Pufferfähigkeit operationalisieren | zulässiger Bereich, Störungsbudget, Maßnahmen, Ressourcen und Zeithorizont domänenspezifisch festgelegt | offen |
| R3-07 | Gemeinsame Skalenrelation untersuchen | Abbildung und Normierung vorab festgelegt; Parameteridentifizierbarkeit, Gegenmodelle und Skalierungskorrekturen berücksichtigt | offen |

Aktueller Methodenstand: [Literaturanschlüsse](LITERATURE_CONNECTIONS.md), [Emergenz und Geschlossenheit](emergence_and_closure.md). Keine universelle Frame-Schwelle und kein allgemeines Individuationskriterium gelten durch die Literaturauswahl als bestätigt.

## Neue offene Punkte aus der Formalismus-Konsolidierung

Diese Tickets betreffen gezielte Folgearbeiten. Die mathematischen Korrekturen in den Dokumenten sind umgesetzt; die hier genannten Produktionscodeänderungen sind nicht Bestandteil dieses abgeschlossenen Dokumentationsschritts.

| ID | Gegenstand | Nächster prüfbarer Schritt | Status |
|---|---|---|---|
| F02 | Bedeutungen im Ökosystem | Kommentare, Datenfelder und Rechnungen auf die getrennten Größen prüfen; S/K/R/V nicht still auf C/R/E/P abbilden | offen |
| F03 | Neural `effective_r()` | Zeitabstände explizit behandeln; Schätzung bei verschiedenen Δt prüfen; fehlende Identifizierbarkeit nicht als Messung eines Defaults ausgeben | offen |
| F04 | Solar geomagnetischer Pfad | Peak-Ereignis versus verfügbare Erholung dokumentieren; eine fortlaufende Zustandskopplung nur mit eigener Modellentscheidung ergänzen | offen |
| F05 | Resilience Kopplungsregister | Einfluss-/Lastscore als solchen typisieren; Onsager-Bezeichnung erst mit Fluss/Kraft-Bilanz | offen |
| F06 | Γ-Pfade und gemeinsame Defaults | Herkunft, Verbraucher und Kalibrier-/Testtrennung pro Pfad erfassen; keine erzwungene neue Verdrahtung | offen |
| F07 | Selbstähnlichkeit | Transformation, Zeitskala, Fehlermaß und unabhängigen Modellvergleich vorab festlegen | offen |
| F08 | Sheaf-Modul für kontextuelle Überlappungen | `verify_sheaf_contextuality.py` nach Aeons Spec (PR-Box CF=1, klassisches Modell CF=0, CHSH-Tabelle 0<CF<1, VB1-Widerspruchsfall) — separates optionales Modul neben VB1, nicht dessen Ersetzung. Erstes Toy-Beispiel bewusst unphysikalisch (PR-Box), um die CF-Infrastruktur gegen bekannte Werte zu härten, bevor sie auf echte GenesisAeon-Fälle angewendet wird. | **erledigt** 2026-09-16 — von Aeon geliefert (`prompts/Answers/CREP-UTAC-AFET_F08_F09_Sheaf_PID_2026-09-16.zip`), Checksummen und 6/6-Skriptlauf von Claude unabhängig nachgerechnet, AND-Gate-Analogon und CHSH-CF=0,25 von Hand gegengeprüft, jetzt aus `FORMALISM.md` §13 verlinkt |
| F09 | PID/Redundancy-Bottleneck-Modul für `EI_q` | `verify_pid_rb.py` nach Aeons Spec: Williams-Beer (I_min-Atome) + Kolchinsky-RB als Default (Referenzimpl. github.com/artemyk/pid-as-ib), nicht Rosas-O-Information. Kanonisches erstes (Quellen,Ziel)-Paar: Mikro→Makro, anknüpfend an `worked_example_causal_emergence.md`. `EI_q` bleibt bestehen, PID wird zusätzliche Zerlegung, keine Gleichsetzung. | **erledigt** 2026-09-16 — von Aeon geliefert, Checksummen und 7/7-Skriptlauf von Claude unabhängig nachgerechnet, AND-Gate-Red=0,311278=h(1/4)-1/2 von Hand bestätigt (Lehrbuchwert), jetzt aus `FORMALISM.md` §10 verlinkt |
| F10 | Liu–Slotine–Barabási-Netzwerksteuerbarkeit | Bewusst zurückgestellt (Skalen-Mismatch: aktuelle Viabilitätsbeispiele sind 2-3-dimensional, Netzwerk-Controllability zielt auf große Netzwerke). Formeln korrekt zitiert und geprüft (Kalman-Rang, `N_D=max(N-|M*|,1)`), als dokumentierter Anhang für einen späteren echten Netzwerk-Anwendungsfall behalten, nicht gestrichen. Zweites Review (16.9.) verschärft die Begründung mit zwei selbst nachgerechneten Gegenfällen: voller Kalman-Rang garantiert keine kontrolliert-invariante Sicherheit unter beschränktem Stellwert (Gegenbeispiel `ẋ=x+u, |u|≤0,25` bei x=1); gleiche Topologie kann sehr unterschiedliche Stellkosten haben (quadratisches Stellmaß skaliert mit `1/(b²T)`). | zurückgestellt (Anhang) |
| F11 | Gemini-Originaldokument: zwei Formel-Fehlübertragungen | Nicht F08/F09 selbst betreffend, sondern die archivierte Gemini-Quelldatei (`prompts/Answers/Gemini_Extensions_2026-09-16.md`): (a) Geminis RB-Bedingung `I(A;Q)=I(B;Q)=I(A,B;Q)` ist NICHT Kolchinskys tatsächliche Formel (`RB(R)=max I(Q;Y\|S) s.t. I(Q;S\|Y)≤R` mit Blackwell-Ordnung) — Geminis Version zwingt den Kanal bei unabhängigen Quellen zur Konstanz und würde für das AND-Gatter fälschlich 0 statt der echten Blackwell-Redundanz 0,311278 liefern; (b) Geminis Cospan-Notation `A→L(x)←B` passt nicht zu Baez–Coursers tatsächlicher Typisierung `L(a)→x←L(b)`. Beide Funde rein historisch/dokumentierend — F08/F09 selbst nutzen die korrekten Formeln (verifiziert). | dokumentiert, keine Codeänderung nötig |
| F12 | F09: TWO_BIT_COPY-Testfall fehlt | Für unabhängige faire Bits A,B mit Ziel Y=(A,B) liefert Williams-Beer `I_min` fälschlich `Red=1` Bit (bekannte Maßabhängigkeit, Harder/Salge/Polani 2013), während Blackwell/Kolchinsky-RB korrekt 0 liefert. Kein Implementierungsfehler, aber `verify_pid_rb.py`s sieben Prüfungen decken diesen bekannten Grenzfall noch nicht ab. Empfehlung: TWO_BIT_COPY neben UNIQUE/XOR/AND/FULL_COPY ergänzen, `I_min`- und RB-Wert nebeneinander berichten. Caveat bereits in `pid_redundancy_bottleneck.md` §6 dokumentiert. | offen, an Aeon zu routen |
| F13 | F08: Global-Zustands-Annahme einschränken | Wenn alle Sichten y_α=π_α(z,c,t) Funktionen desselben angenommenen z sind, existiert die gemeinsame Verteilung immer trivial als Bildmaß — ein positiver CF-Wert wäre dann ein Modellierungsfehler, keine echte Kontextualität. CF ist nur sinnvoll, wenn die Kontextverteilungen e_C unabhängig spezifizierte Primitive sind, nicht Projektionen eines gemeinsamen z. Caveat bereits in `sheaf_contextuality.md` §6 und `FORMALISM.md` §13 dokumentiert. | dokumentiert, Anwendungsregel für künftige Fälle |
| F14 | Sichere Eingriffsübertragung (VB3–VB5-Vertiefung) | Hinreichende Bedingung für die Übertragung sicherer Makro-Eingriffe auf Mikrozustände (Ausführbarkeit, Nachfolgerverträglichkeit, sichere Darstellung), mit Beweis und drei selbst nachgerechneten Gegenfällen (r09 gemittelte Geschlossenheit, r10 gekoppeltes Budget, r11 offene Wärmebilanz). Als Sektion 8 in `context_transformations.md` aufgenommen. Vollständige Herleitung und alle elf Prüfungen in `reviews/formalism-review-f08-f09/`. | **erledigt** 2026-09-16 — Kernaussage plus zwei Gegenfälle (r09, r10) von Claude von Hand nachgerechnet (PC=CQ exakt, Budget-Infeasibilität 0,8>0,6 exakt), in `context_transformations.md` §8 eingearbeitet |

Structured Cospans (Baez–Courser) bleiben zurückgestellt — `context_transformations.md` deckt Komposition/Zerlegung bereits informell ab, kein akuter Verify-Gap; siehe auch F11(b). Quelle für F08–F14: [reviews/2026-09-16_gemini_extensions_review_aeon.md](reviews/2026-09-16_gemini_extensions_review_aeon.md) und [reviews/formalism-review-f08-f09/](reviews/formalism-review-f08-f09/) (zweites unabhängiges Review, 11/11 eigene Prüfungen, Primärquellen-Rekonstruktion). Aufnahmebedingung für neue Module in den Formalismus-Kern (Astra-Standard, unverändert): Textformeln, `verify_*.py` mit reproduzierbarem JSON-Report, durchgerechnetes Beispiel mit Zahlen aus dem Skriptlauf, explizites Mapping auf bestehende Begriffe, geprüfte Zitate, Johann-OK vor jeder Mutation von `FORMALISM.md`.

Aktuelle Definitionen: [FORMALISM.md](FORMALISM.md). Prüfplan: [ROADMAP.md](ROADMAP.md). Die Gegenbeispiele und korrigierten Modellbeziehungen stehen in [VERIFICATION.md](VERIFICATION.md).

## Erhaltene Paket-Folgetickets vom 15. September

Der folgende Bestand bleibt vollständig erhalten. Seine Prüf- und Releaseangaben sind die damaligen Arbeitsnachweise; diese Dokumentrevision behauptet keine erneute Ausführung. Spätere Präzisierungen einzelner Worked Examples (etwa AMOC 1.3.3 oder Cygnus 1.0.2) stehen in den jeweiligen aktuellen Beispieldateien und der Roadmap.

# Phase-2-Folgetickets (nicht Teil des jeweiligen Haupttickets)

Sammelt Funde, die waehrend eines Phase-2-Reviews auftauchen, aber nichts
mit dem eigentlichen Ticket zu tun haben -- damit sie nicht verloren
gehen, ohne das laufende Ticket aufzublaehen.

## Offen

- **`phaethon-chimera` Prediction #47 (Perihel-Durchgaenge vor Flyby)**:
  urspruenglich als "4.0 folgt arithmetisch nicht aus einer einfachen
  Perioden-Divisionsschaetzung" geflaggt. Mit echten Bahnelementen von
  JPL SBDB (tp=JD 2461285.616438 TDB, period=523.6665665 d, Loesung
  2026-06-25) nachgerechnet: reale Periheldurchgaenge liegen auf
  2026-09-02, 2028-02-07, 2029-07-15, 2030-12-21 -- nicht gleichmaessig
  ueber Kalenderjahre verteilt, wie eine Perioden-Division annimmt.
  `4.0` IST mit echten Daten konsistent, WENN der JFY2030-Flyby
  (Apr 2030-Mar 2031) am oder nach dem 2030-12-21 stattfindet; `3.0`
  waere korrekt, falls davor. JAXAs oeffentlicher Zeitplan nennt bisher
  nur "JFY2030" ohne Monat -- bleibt offen, aber jetzt praezise auf
  "3 oder 4, abhaengig vom noch nicht veroeffentlichten Flyby-Monat"
  eingegrenzt (vorher: "unklar um ~2"). Dokumentiert in
  `destiny_predictions.py` (Prediction #47).

## Erledigt

- **`aeon-trikaya`: Git-Remote fehlte** -- rein lokales Repo (2 Commits,
  `master`-Branch), nie zu GitHub gepusht. Johann bestaetigt: kein
  Absicht wie bei `vesta-sim`, sollte veroeffentlicht werden. Vor dem
  Push: `master`->`main` umbenannt (Oekosystem-Konvention), Test-Artefakte
  (`aeon_proto_*.yaml`, `test_log.yaml`, die die eigene Testsuite per
  Default im Arbeitsverzeichnis erzeugt) zu `.gitignore` ergaenzt, 76/76
  Tests lokal verifiziert. Repo erstellt und gepusht:
  https://github.com/GenesisAeon/aeon-trikaya (public, `main`). Noch
  OHNE die Standard-GenesisAeon-Release-Infrastruktur, die andere Pakete
  laengst haben (`.zenodo.json`, CI/Release-Workflows, CONTRIBUTING.md,
  Issue-Templates) -- war nicht Teil dieser Anfrage, waere ein
  natuerlicher naechster Schritt.

- **`phi-scaling-validator`: zwei redundante Release-Workflows** --
  `publish.yml` (klassisches `PYPITOKEN`-Secret, funktionierte) und
  `release.yml` (Trusted Publishing via `environment: pypi`, dessen
  Publisher nie bei pypi.org registriert war und daher bei jedem
  Tag-Push fehlschlug: `invalid-publisher`). Zusammengefuehrt in ein
  einzelnes `release.yml`, das den bereits funktionierenden
  Token-Upload nutzt; `publish.yml` entfernt, ungenutzte
  `id-token: write`-Permission entfernt. YAML-Syntax lokal validiert,
  CI nach dem Push gruen. Volle Bestaetigung erst beim naechsten
  Tag-Release moeglich (Release-Workflow triggert nur auf Tags, nicht
  auf normale Pushes).

## Erledigt (vorherige Runde)

- **`phaethon-chimera`: vollstaendiger Audit der restlichen 44 DESTINY+-
  Vorhersagen (#2, #5-47)** -- stichprobenartige Gegenpruefung aller
  Vorhersagen mit echten externen Quellenangaben (ZTF, STEREO, Hanus et
  al. 2016, JAXA-Missionsplan, Geminiden-Literatur) sowie der
  paketinternen Physik-Funktionen. Drei echte, unabhaengig verifizierte
  Fehler gefunden und korrigiert:
  - **#26 (mittlerer Radius)**: war 2,78 km, zugeschrieben "Hanus et al.
    2016 Okkultationsdaten" -- der echte Hanus et al. 2016 (A&A 592, A34)
    Befund ist ein Durchmesser von 5,1±0,2 km aus Thermophysik-Modellierung
    von Infrarotdaten, weder der Wert noch die Methode stimmten. Korrigiert
    auf 2,55 km (=5,1/2), Quellenangabe korrigiert.
  - **#40 (Auswurfgeschwindigkeit)**: war fest auf 1,2 m/s codiert, aber
    `GeminidModel.ejection_velocity_ms()` (die eigene Fluchtgeschwindigkeits-
    Formel des Pakets, v_esc=√(2GM/r)) wurde nie tatsaechlich aufgerufen, um
    diesen Wert zu erzeugen -- mit den eigenen Parametern (ρ=1700 kg/m³)
    ergibt sich ≈2,49 m/s. Vorhersage und die (gleichermassen falsche)
    Docstring-Behauptung der Funktion korrigiert.
  - **#46 (DESTINY+ Flyby-Jahr)**: war 2029, ein aelterer Missionsplan.
    JAXAs aktueller oeffentlicher Zeitplan (Traegerraketenwechsel auf H3)
    zielt auf JFY2030 fuer den Phaethon-Flyby. `DESTINY_FLYBY_YEAR`
    korrigiert und in README.md, `.zenodo.json`, `__init__.py`, `system.py`
    propagiert.
  - Zusaetzlich `data/ztf_photometry_summary.yaml` markiert (nicht
    geloescht): wird von keinem Code tatsaechlich geladen, und die
    `genesisaeon_utac_fit`-Sektion entspricht exakt bereits bestehenden
    Oekosystem-Defaults (σ=2,2, Γ=0,165) statt einer glaubwuerdigen
    eigenstaendigen Anpassung an die spaerlichen echten Daten daneben.
  - Vorhersagen #5-25, #27-35, #38-45 sind reine UTAC/Chimera/SOC-
    Modellausgaben ohne externe Literatur zum Gegenpruefen vor dem Flyby --
    unveraendert gelassen. #36 (Geminid-ZHR) und #37 (Stream-Alter) gegen
    echte publizierte Schaetzungen geprueft und konsistent befunden, auch
    wenn die "UTAC-Modell"-Zuschreibung nicht unabhaengig verifizierbar ist.
  - #47 (Perihel-Durchgaenge) hat eine verbleibende, dokumentierte
    Inkonsistenz -- s. "Offen" oben. Released als `1.0.3`, live bestaetigt
    auf PyPI.

- **`beta-clustering-utac` (P32): "σ≈2.2 emerges from the β
  distribution (UTAC v1.0 finding)" numerisch nachgerechnet -- Behauptung
  ist FALSCH.** `sigma_from_beta_distribution()` (die eigene Formel des
  Pakets) liefert auf den eigenen Daten (Standard-Synthetik-Generator UND
  literaturzitierende `data/utac_v1_78_systems.yaml`) σ≈1.28, nicht 2.2 --
  eine ~42%-Abweichung. `BETA_SCALE=2.2` ist derselbe geteilte
  Oekosystem-Default wie in `amoc-utac`/`afet-tensions`, keine
  eigenstaendige Herleitung fuer diese Domaene. Zusaetzlich entdeckt:
  dieselbe "measured-but-unused"-Diskonnektion wie bei `amoc-utac`
  -- `system.py`s `_build_crep_state()` nutzt immer den hartcodierten
  Default, nie den von `_run_cycle()` berechneten und separat
  ausgegebenen σ≈1.28-Wert. Nur die Falschbehauptung korrigiert
  (Kommentare/README/`.zenodo.json`), `BETA_SCALE`-Zahlenwert
  unveraendert gelassen -- keine unabhaengigen Daten, um einen
  "richtigen" Wert zu rechtfertigen. Released als `1.1.1`, live
  bestaetigt auf PyPI.

- **Diamond-setup 2.3.0 `bridge_adapted`-Feld bricht `==`-Exact-Match-
  Tests oekosystemweit** -- entdeckt waehrend der `beta-clustering-utac`-
  Pruefung (lokale `diamond-setup` war veraltet auf 2.2.0 gepinnt, echte
  PyPI-Version 2.3.0 fuegt additiv `bridge_adapted: bool` zu `CREPState`
  hinzu). Lokal via `pip install --upgrade diamond-setup` behoben, dann
  gezielt per Grep nach allen `test_get_crep_state_keys`-artigen Tests im
  Oekosystem gesucht. Betroffen: `beta-clustering-utac` (behoben in
  1.1.1, s.o.), `implosive-origin-utac` (behoben, `1.1.0`->`1.1.1`),
  `phi-scaling-validator` (behoben, `1.1.0`->`1.1.1`). NICHT betroffen:
  `solar-flare-utac` (nutzt eigene lokale `CREPState`-Klasse, nicht
  `diamond_setup.protocol`). Alle drei Fixes: exakter Set-Vergleich durch
  Teilmengen-Check (`{"C","R","E","P","Gamma"} <= set(state.keys())`)
  ersetzt. **Offene Frage, noch nicht geprueft:** ob die bereits vorher
  in dieser Runde released Pakete (`amazon-utac`, `hikari-ledger`,
  `amoc-utac`, `cygnus-jet-utac`, `solar-flare-utac`,
  `neural-avalanche-utac`, `phaethon-chimera`) denselben
  `diamond_setup.protocol.CREPState`-Exact-Match-Testmuster haben und
  durch die lokale 2.2.0-Veraltung faelschlich als "gruen" durchgelaufen
  sind -- noch nicht zurueckgeprueft.

- **`phi-scaling-validator`: falsche DOI in `test_to_zenodo_record`** --
  erwartete `afet-tensions`' DOI (`10.5281/zenodo.17472834`) statt der
  eigenen (`10.5281/zenodo.20513358`); derselbe Copy-Paste-Fehler wie
  zuvor bei `sa-sv-duality`. Korrigiert in `1.1.1`.

- **`solar-flare-utac`: PyPI Trusted Publishing** -- hatte seit dem
  allerersten v1.0.0-Release (2026-06-25) nie funktioniert. Johann hat
  den Trusted-Publisher-Eintrag bei pypi.org ergaenzt (2026-09-15);
  `gh run rerun --failed` danach erfolgreich. Live bestaetigt: `1.0.1`.

- **`cygnus-jet-utac`, `hikari-ledger`: PyPI Trusted Publishing hatte NIE
  funktioniert** -- `invalid-publisher` seit dem jeweils allerersten
  Release. Johann hat fuer beide einen Trusted-Publisher-Eintrag bei
  pypi.org ergaenzt (2026-09-15); `gh run rerun --failed` danach fuer
  beide erfolgreich. Live bestaetigt: beide zeigen `1.0.1`.

- **`resilience-core`: `CI`-Workflow (ruff+mypy Lint) war seit mindestens
  2026-08-01 bei jedem Push auf `main` rot (5/5 Runs `failure`), ohne
  Releases zu blockieren.** Zwei Ursachen: eine zu lange Docstring-Zeile
  in `src/resilience_core/__init__.py` (umgebrochen), unsortierte Imports
  in `tests/test_diamond.py` (ruffs eigenen Sortiervorschlag angewendet:
  `pytest`+`diamond_setup` als Drittanbieter-Gruppe, `resilience_core` als
  eigene Erstanbieter-Gruppe danach). `ruff check`+`mypy` lokal sauber,
  v1.0.3 released (2026-09-15), CI zum ersten Mal seit Wochen gruen.

- **`sandpile-utac`, `seismic-utac`: `CI`-Workflow (`Tests (Python 3.10)`)
  war seit 2026-07-17 bei jedem Push rot**, weil `diamond-setup>=2.2.0`
  seit 2026-06-25 `Requires-Python >=3.11` verlangt, aber beide Pakete
  noch `requires-python = ">=3.10"` deklarierten (alle anderen 10 Ticket-
  4/5-Pakete standen bereits korrekt bei `>=3.11`). Behoben: `requires-
  python` auf `>=3.11` gesetzt, 3.10-Zeile aus beiden CI-Matrizen entfernt.
  Dabei aufgedeckt: der `Lint`-Job (`ruff` gefolgt von `mypy` im selben
  Schritt) war durch den vorher fehlschlagenden `ruff`-Schritt seit
  Langem nie bis zu `mypy` gekommen -- nach dem Ruff-Fix liefen erstmals
  wieder 13 (`sandpile-utac`) bzw. 15 (`seismic-utac`) vorbestehende
  `mypy --strict`-Fehler auf (fehlende Generic-Typparameter auf
  `np.ndarray`, jetzt `np.ndarray[Any, Any]` -- selbes Muster wie in
  `afet-tensions`; ausserdem ein `matplotlib.cm.viridis`-Typisierungsfehler
  in `sandpile-utac`, behoben via `plt.get_cmap("viridis")`).
  `seismic-utac`s mypy-Konfiguration hatte zusaetzlich einen ungueltigen
  Fehlercode (`"untyped-decorator"`, mypy-Warnung, keine echte Suppression)
  -- entfernt, da nicht mehr benoetigt (verifiziert: `afet-tensions` hat
  eine echte Typer-CLI und besteht `mypy --strict` ohne jede Decorator-
  Sonderregel). `ruff check`+`mypy` in beiden Paketen lokal sauber,
  v1.0.2 released (2026-09-15), `CI` bei beiden zum ersten Mal seit
  2026-06-25 wieder komplett gruen (Lint + Tests).

- **Stale editable installs auf `.claude/worktrees/<paket>-vendor-fix/`
  statt Hauptcheckout, in 8 von 12 Ticket-5-Paketen entdeckt (2026-09-15).**
  `phaethon-chimera`, `sa-sv-duality`, `sandpile-utac`, `seismic-utac`,
  `cellular-genesis`, `eml-utac-bridge`, `vrig-cosmological`, `worldview`
  waren via `pip install -e` auf alte, unabhaengige
  `.claude/worktrees/<paket>-vendor-fix/`-Verzeichnisse verlinkt statt auf
  den Hauptordner -- vorbestehender Umgebungsfehler. Alle 8 per
  `pip install -e .` aus dem jeweiligen Hauptordner neu installiert und
  per `import <paket>; print(<paket>.__file__)` verifiziert. Die alten
  `-vendor-fix`-Worktree-Verzeichnisse selbst wurden NICHT angefasst.

- **`sa-sv-duality::test_system_zenodo_record`** -- hartkodierte
  `afet-tensions`' DOI statt der eigenen. Beim v1.0.1-Bump (2026-09-15)
  korrigiert auf `10.5281/zenodo.20842509` (passend zu `__zenodo__` in
  `__init__.py`).

- **`worldview::test_cli.py::TestVersionFlag::test_version_short_flag`**
  -- Rich-ANSI-Splitting-Bugmuster bei der `-V`-Flag-Pruefung. Beim
  v1.0.1-Bump (2026-09-15) per ANSI-Escape-Strip vor dem Assert behoben.

- **resilience-core: PyPI Trusted Publishing** -- Johann hat den fehlenden
  Trusted-Publisher-Eintrag direkt bei PyPI ergaenzt (2026-09-15). Re-Run
  von GitHub-Actions-Run `34951902193` (`gh run rerun --failed`) danach
  erfolgreich: PyPI zeigt `1.0.1`/`1.0.2` live (JSON-API bestaetigt),
  GitHub-Release veroeffentlicht. Offen bleibt nur die unabhaengige
  Verifikation, ob Zenodo tatsaechlich eine neue Version archiviert hat
  (der "Publish to Zenodo"-Workflow-Schritt selbst ist weiterhin nur ein
  Platzhalter-Echo, siehe `release.yml`).

- **`cellular-genesis`, `eml-utac-bridge`, `phaethon-chimera`: PyPI
  Trusted Publishing hat NIE funktioniert** -- `gh run list` zeigte, dass
  der `Release`-Workflow bei allen drei Paketen seit ihrem initialen
  v1.0.0-Release (Juni 2026) durchgehend an `invalid-publisher` scheiterte
  (deren live stehende 1.0.0-Versionen wurden damals also ausserhalb
  dieser Pipeline hochgeladen, vermutlich manuell per API-Token). Johann
  hat fuer alle drei Projekte einen Trusted-Publisher-Eintrag bei pypi.org
  ergaenzt (2026-09-15); `gh run rerun --failed` danach fuer alle drei
  erfolgreich. Live bestaetigt (PyPI JSON-API, nach kurzer CDN-Verzoegerung
  fuer cellular-genesis/eml-utac-bridge): alle drei zeigen `1.0.1`.

- **`worldview::tests/test_cli.py` faelschlich als diamond-setup-
  Kontamination geloescht (Ticket 5, 2026-09-15).** GrokBots Suche
  `find src -iname cli.py` fand `worldview`s eigenes CLI-Modul nicht, weil
  es unter `src/worldview/cli/main.py` liegt (nicht `cli.py` direkt) --
  daher faelschlich als "keine eigene CLI" eingestuft und die Datei
  geloescht, OHNE ihren Inhalt zu pruefen (Verstoss gegen die im Prompt
  selbst verlangte Methodik). Tatsaechlich war es eine vollstaendige,
  funktionierende Testsuite fuer `worldview.cli.main.app`
  (`--version`/`-V`/`info` etc.), erkennbar auch daran, dass die
  Coverage nach Loeschung von 99% auf 71% (`src/worldview/cli/main.py`:
  0%) fiel -- das vermeintlich "vorbestehende" `fail_under=99`-Problem aus
  GrokBots Bericht war also real, aber selbstverschuldet, nicht
  vorbestehend. Per `git checkout HEAD -- tests/test_cli.py`
  wiederhergestellt, Coverage wieder bei 99.59%. `test_preset.py`/
  `test_validator.py` fuer `worldview` dagegen unabhaengig geprueft und
  zu 100% echte diamond-setup-Kontamination bestaetigt -- deren Loeschung
  bleibt bestehen.

- **`phaethon-chimera::test_run_with_n_orbits` (neu von Ticket 5
  geschrieben) schlug nach Fix der Stale-Install-Umgebung real fehl --
  Rich-ANSI-Splitting-Bugmuster (`assert "5 orbits" in result.output`
  scheitert, weil rich die "5" separat hervorhebt).** In Claude-Review
  direkt behoben (ANSI-Escape-Codes vor dem Assert per Regex entfernt,
  gleiches Muster wie beim diamond-setup-CLI-Bug oben). 56/56 Tests
  gruen danach, deckt sich mit GrokBots urspruenglicher Zahl -- aber aus
  den richtigen Gruenden (GrokBots Testlauf lief vermutlich in einer
  korrekten Umgebung und hatte diesen Bug nie gesehen, waehrend Claudes
  erster Review-Lauf durch die Stale-Install falschen Code testete, der
  zufaellig ebenfalls fehlschlug -- zwei unabhaengige Probleme, die sich
  ueberlagert haben).
