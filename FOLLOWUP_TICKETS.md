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

## F25: Teil 2, Milestone 9 — Metaregeln (erledigt 2026-09-17)

Von Aeon geliefert (`prompts/17_teil2_m9_metarules_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Erste von mehreren "Ast verbreitern"-Erweiterungen (Johanns Wunsch, natürliche mathematische Anschlüsse an den Ist-Stand zu prüfen):
- `src/scoped_correspondence/metarules/core.py`: `MetaRuleUpdate` (typisierter Wrapper für `m′=H(m,z,c,u,t)`, diskret/Event, mit benannten Varianten `descriptive_only`/`enforced_rule`), `priority_joint_control_set` (wrappt `membership.joint_control_set` unverändert, greift nur bei leerem Schnitt ein und gibt die aufgegebene Anforderung explizit namentlich aus), `unobserved_metarule_breaks_closure` (konkretes A/B-Paar über die bereits gemergten `closure`-APIs: `m=z` synchron → exakte Geschlossenheit, unabhängige Münze moduliert `m` → bricht Geschlossenheit).
- 5/5 neue Prüfungen selbst nachgerechnet (eigener Skriptlauf, JSON bis auf Zeitstempel bit-identisch). Fall B von Hand aus erster Prinzip hergeleitet, unabhängig vom Skript: die beiden `z=0`-Mikrozustände sagen unterschiedliche Makro-Folgezustände voraus (`[1,0]` vs. `[0,1]`), daraus folgt exakt `closure_error=0,5` — bestätigt. Prioritätsregel-Fälle (leerer Schnitt löst Drop von Index 0 aus, nichtleerer Schnitt bleibt identisch zu `joint_control_set`) ebenfalls von Hand bestätigt.
- `membership/core.py`, `closure/core.py` und alle 8 Kerndokumente unverändert.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m9-metarules` gelöscht.

## F26: DeepResearch-Antwort ChatGPTAstra3.md geprüft (erledigt 2026-09-17)

`prompts/Answers/ChatGPTAstra3.md` (Antwort auf `prompts/16_deepresearch_natural_extensions.md`): 10 unabhängige Erweiterungsvorschläge, je an genau einen bestehenden Baustein angeschlossen (keine Cross-Layer-Identität). Von Claude verifiziert: alle durchgerechneten Zahlenbeispiele von Hand nachgerechnet (Kontraktionsraten, Dissipativitätsbeispiel `V̇=-5`, CBF-Bedingung `u+x≥0`, Split-Conformal-Quantil `q=3`, Schnakenberg-Entropieproduktion `ln2`) — alle korrekt. Alle 12 neuen Zitate per Fork unabhängig gegen DOI/arXiv geprüft (Titel/Autor/Jahr/Inhalt) — keine Fabrikation, keine Fehlzuschreibung, insbesondere Kolchinsky 2022 (Blackwell-PID) vs. Kolchinsky 2024 (Redundancy Bottleneck, bereits in F09 genutzt) als zwei echte, verschiedene Arbeiten bestätigt (genau die Art Verwechslung, die bei Rosas 2019/2020 früher schon passiert war). Vier "hoch"-priorisierte Kandidaten: Approximation Certificates (`correspondence`), Formal Reduction Error Bounds (`closure`), Control Barrier Functions (`viability`), Split Conformal Prediction (`validation`). Erster Umsetzungsauftrag: F27.

## F27: Teil 2, Milestone 10 — Approximation Certificates (erledigt 2026-09-17)

Von Aeon geliefert (`prompts/18_teil2_m10_approximation_certificates_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Erste Umsetzung aus F26:
- `src/scoped_correspondence/correspondence/approximation.py`: `ApproximationCertificate` (Girard & Pappas 2007, DOI 10.1109/TAC.2007.895849), `verify_approximate_simulation` — interpretiert die bereits gemergten `Correspondence.conjugacy_residual`/`verify_conjugacy`-Residuen gegen ein ε-Budget statt Nahe-Null-Gleichheit. `relation_kind` wird in `__post_init__` HART auf `"fixed_map_bound"` erzwungen (löst `ValueError` bei jedem anderen Wert) — stärker als im Auftrag verlangt, verhindert zuverlässig eine spätere Überbehauptung als "simulation"/"bisimulation".
- 3/3 neue Prüfungen selbst nachgerechnet (eigener Skriptlauf, JSON identisch bis auf ein `timestamp`-Feld). Durchgerechnetes Beispiel von Hand bestätigt: `x(t)=0, y(t)=0,1(1-e^{-t})` bei `t=10` ergibt exakt `0,09999546000702375` — bestätigt, inklusive dass das Skript tatsächlich exakte analytische Flüsse nutzt (keine numerische ODE-Integration).
- `correspondence/contract.py` und alle 8 Kerndokumente unverändert.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m10-approximation-certificates` gelöscht.

## F28: DeepResearch-Antwort "Mathematische Erweiterungen Scoped Correspondence.docx" geprüft (erledigt 2026-09-17)

Zweite unabhängige DeepResearch-Antwort (vermutlich Gemini, Formeln als 186 PNG-Bilder im Export statt Text). 7 Erweiterungsvorschläge, je an genau einen Baustein: observation (Directed Information, Massey 1990/Permuter-Weissman-Goldsmith 2009), dynamics (Fenichel-Theorem/GSPT, Fenichel 1979/Kuehn 2015), coupling (Dirac-Struktur-Komposition, Cervera/van der Schaft/Baños 2007), closure (CTMC-Generator-Lumpability, Buchholz 1994/Michel & Siegle), viability (Control Barrier Functions, Ames et al. 2019 — bestätigt als echtes, eigenständiges Survey-Paper, keine Verwechslung mit dem bereits bekannten Ames et al. 2017), identifiability (Fisher-Information-Sloppiness, Transtrum/Machta/Sethna 2011, Raju et al. 2018), contextuality (CSW-Grapheninvarianten, Cabello/Severini/Winter 2014). Von Claude verifiziert: 3 Formel-Bilder stichprobenartig angesehen (korrekte Standard-GSPT-Formeln), alle 11 Zitate per Fork gegen DOI/arXiv geprüft — keine Fabrikation, eine kleine Ungenauigkeit (Permuter et al. als "zeitkontinuierlich" bezeichnet, ist tatsächlich zeitdiskret mit Rückkopplung). Bewusst keine Vorschläge für correspondence, membership, validation, information_decomposition, thermo (mit Begründung).

**Wichtiger Gegenbefund:** `ChatGPTAstra4.md` (parallel von Johann eingereicht, Ergebnis einer Weiterverarbeitung von Geminis Text durch ChatGPT) ist **unbrauchbar und verworfen** — erkennbar halluziniert (Formulierungen wie "offenbar", "vermutlich", "hypothetisches Theorem"; explizites Eingeständnis fehlenden Source-Code-Zugriffs; erfundene Dateistruktur `core/formalism.py`/`algorithms/`/`proofs/`, die nicht existiert). Keine Verwendung als Grundlage für irgendeinen Auftrag.

## F29: Teil 2, Milestone 11 — Continuous-Time Generator Lumpability (erledigt 2026-09-17)

Von Aeon geliefert (`prompts/19_teil2_m11_generator_lumpability_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F28 — überträgt `PC=CQ` auf CTMC-Generatoren: `src/scoped_correspondence/closure/generator_lumpability.py` mit `is_exact_generator_lumpability`/`generator_closure_error` (`QC=CQ_macro`, Buchholz 1994/Michel & Siegle), bewusst mit ∞-Norm statt TV (Generator-Residuen sind vorzeichenbehaftete Raten mit Zeilensumme 0, keine Wahrscheinlichkeitsmasse — im Docstring begründet). Ruft `closure.partition_matrix` unverändert auf.
- 4/4 neue Prüfungen selbst nachgerechnet, JSON bis auf Zeitstempel identisch. Beide Fälle von Hand aus den rohen Matrizen hergeleitet: exakt-lumpable Fall `QC=CQ_macro` exakt (`error=0`), nicht-lumpable Variante Residuum-Zeile `[-1,1]` → `error=1,0` — beide exakt bestätigt.
- `closure/core.py` und alle 8 Kerndokumente unverändert. Berührt bewusst nicht `src/scoped_correspondence/__init__.py` (Konfliktvermeidung mit M12/M13).
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m11-generator-lumpability` gelöscht.

## F30: Teil 2, Milestone 12 — Dirac Structure Composition (erledigt 2026-09-17)

Von Aeon geliefert (`prompts/20_teil2_m12_dirac_composition_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F28 — `src/scoped_correspondence/coupling/dirac_composition.py` mit `compose_skew_symmetric`: Komposition zweier antisymmetrischer Kopplungsmatrizen über leistungserhaltende Feedback-Interkonnektion (`u1=-y2, u2=y1`) bleibt schiefsymmetrisch (Cervera/van der Schaft/Baños 2007). Ruft `coupling.check_generic_structure` unverändert auf.
- 3/3 neue Prüfungen selbst nachgerechnet. Kompositionsformel algebraisch von Hand bestätigt: `J_total^T=-J_total` gilt für BELIEBIGE konforme `g1,g2` (nicht nur Identität) — allgemeiner als im Auftrag verlangt. Schnittstellenleistung `y1·(-y2)+y2·y1=0` exakt bestätigt (`[0.0,0.0,0.0]` im Skriptlauf).
- `coupling/core.py` und alle 8 Kerndokumente unverändert. Berührt bewusst nicht `src/scoped_correspondence/__init__.py` (im eigenen Moduldoc explizit als Konfliktvermeidung mit M11/M13 begründet).
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m12-dirac-composition` gelöscht.

## F31: Teil 2, Milestone 13 — Split Conformal Prediction (erledigt 2026-09-17)

Von Aeon geliefert (`prompts/21_teil2_m13_conformal_prediction_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F26 (Astra3) — `src/scoped_correspondence/validation/conformal.py` mit `calibrate_split_conformal` (Finite-Sample-`(n+1)`/Ceiling-Quantil, explizit NICHT das naive empirische Quantil), `predict_interval`, `SplitConformalReport` (`coverage_kind` in `__post_init__` hart auf `"marginal_exchangeable"` erzwungen), plus Pflicht-Anti-Leck-Guard `VAL-CONF-LEAK-001`. Neues separates Modul, Cygnus-Pilot-Code (`validation/core.py`) unangetastet.
- 4/4 neue Prüfungen selbst nachgerechnet. Beide Beispiele von Hand bestätigt: `R=(1,1,2,3), α=0,2` → `k=⌈5·0,8⌉=4` → `q=3` → `[7,13]`; zweites Beispiel (5 Residuen, `α=0,25`) → `k=⌈6·0,75⌉=5` → `q=4` → `[6,14]`, inklusive der im Skript mitgelieferten Gegenprobe, dass das naive Quantil fälschlich `q=2` ergäbe.
- `validation/core.py` und alle 8 Kerndokumente unverändert. Berührt bewusst nicht `src/scoped_correspondence/__init__.py`.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m13-conformal-prediction` gelöscht. **Einziger echter Merge-Konflikt der drei** (trivial): alle drei Branches bumpten unabhängig `pyproject.toml`s Versionsnummer/Beschreibung ausgehend vom selben Basis-Commit — von Hand zu `0.13.0a1` mit vollständiger Beschreibung (alle drei M11-M13-Inhalte genannt) aufgelöst.

## F32: Teil 2, Milestone 14 — Contraction Analysis (erledigt 2026-09-18)

Von Aeon geliefert (`prompts/22_teil2_m14_contraction_analysis_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F26 (Astra3) — Lohmiller & Slotine 1998. `src/scoped_correspondence/dynamics/contraction.py` mit `contraction_rate_cusp` (exakte globale Kontraktionsrate für `dynamics.cusp_field`, `sup_x f'(x)=a/tau` bei `x=0`: `a<0` → Rate `-a/tau`, `a>=0` → `None`, kein Fehler, Bistabilitäts-Scope) und `verify_contraction_bound` (numerische Gegenprobe per finiter Differenz gegen `cusp_field`, nur Aufruf).
- 4/4 neue Prüfungen selbst nachgerechnet, JSON bis auf Zeitstempel identisch. Drittes, selbst hinzugefügtes Beispiel (`a=-2,tau=2→rate=1,0`) von Hand bestätigt.
- `dynamics/core.py` und alle 8 Kerndokumente unverändert. Berührt bewusst nicht `src/scoped_correspondence/__init__.py`.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m14-contraction-analysis` gelöscht.

## F33: Teil 2, Milestone 15 — Dissipativity / Supply Rates (erledigt 2026-09-18)

Von Aeon geliefert (`prompts/23_teil2_m15_dissipativity_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F26 (Astra3) — Willems 1972. `src/scoped_correspondence/coupling/dissipativity.py` mit `check_storage_inequality` (`V̇≤w+tol`), `neutral_interconnection_supply`, `DissipativityCertificate` (mit explizitem Disclaimer: allgemeiner Energiebilanzvertrag, KEINE thermodynamische Aussage ohne weiteren Nachweis).
- 4/4 neue Prüfungen selbst nachgerechnet. Zweites Beispiel von Hand bestätigt: `-(0,5²+1,5²)=-2,5` exakt.
- `coupling/core.py`, `coupling/dirac_composition.py` und alle 8 Kerndokumente unverändert. Berührt bewusst nicht `src/scoped_correspondence/__init__.py`.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m15-dissipativity` gelöscht.

## F34: Teil 2, Milestone 16 — Control Barrier Functions (erledigt 2026-09-18)

Von Aeon geliefert (`prompts/24_teil2_m16_control_barrier_functions_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F26 (Astra3) + F28 (docx) — Ames et al. 2017/2019, von beiden Recherchen unabhängig vorgeschlagen. `src/scoped_correspondence/viability/control_barrier.py` mit der skalaren Zeroing-CBF-Bedingung (`u+x>=0` für `ẋ=u, h(x)=x, α(h)=h`); `BarrierFunction` verweigert nichtlineares `α` oder abweichendes `h` aktiv statt still falsche Lie-Ableitungen zu liefern.
- 4/4 neue Prüfungen selbst nachgerechnet. Neu hinzugekommenes 2019-Survey-Zitat (DOI 10.23919/ECC.2019.8796030) zusätzlich per WebSearch verifiziert — echtes Paper, korrekte Autorenliste. Zweiter Fall (`x=0,5`) von Hand bestätigt: `u_min=-0,5`, Margen `0,3`/`-0,1`.
- `viability/core.py` und alle 8 Kerndokumente unverändert. Berührt bewusst nicht `src/scoped_correspondence/__init__.py`.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m16-control-barrier-functions` gelöscht.

## F35: Teil 2, Milestone 17 — BROJA Bivariate Unique Information (erledigt 2026-09-18)

Von Aeon geliefert (`prompts/25_teil2_m17_broja_pid_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F26 (Astra3) — Bertschinger et al. 2014, drittes PID-Maß neben Williams-Beer/Blackwell-RB. `information_decomposition/broja.py`: `broja_pid_bivariate` löst die Optimierung über die Transportpolytop-Parametrisierung von `Δ_P` per SLSQP aus ≥5 unabhängigen Startpunkten mit Konvergenz- und Redundanz-Konsistenzprüfung (`I(y;r1)-Unq1==I(y;r2)-Unq2`).
- 4/4 neue Prüfungen selbst nachgerechnet, sogar in den Rauschziffern bit-identisch (deterministisch, fester Seed). TWO_BIT_COPY-Kreuzprobe: `Unq1≈Unq2≈1,0, Red≈Syn≈0` — exakt wie theoretisch erwartet, im Gegensatz zu Williams-Beers irreführendem `Red=1`. Zwei zusätzliche, selbst hinzugefügte Testfälle (XOR→reine Synergie, redundante Kopie→volle Redundanz) matchen unabhängig bekannte Lehrbuch-PID-Werte.
- `information_decomposition/core.py` und alle 8 Kerndokumente unverändert.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m17-broja-pid` gelöscht.

## F36: Teil 2, Milestone 18 — Schnakenberg Network Thermodynamics (erledigt 2026-09-18)

Von Aeon geliefert (`prompts/26_teil2_m18_schnakenberg_thermodynamics_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F26 (Astra3) — Schnakenberg 1976. `thermo/schnakenberg.py` mit `stationary_currents`, `cycle_affinity`, `entropy_production_rate` (mit Pflicht-Nichtnegativitätsprüfung), getrennt vom bestehenden deterministischen Drei-Zyklus (M8).
- 4/4 neue Prüfungen selbst nachgerechnet. Beide Beispiele von Hand bestätigt: symmetrischer Drei-Zyklus (Raten 2/1) → `J=1/3, A=ln2, Ṡ_prod=ln2` exakt; zweiter Fall (Raten 3/1) → `J=2/3, A=ln3, Ṡ_prod=2·ln3≈2,197` exakt. Skript flaggt selbst proaktiv, dass die zufällige Nähe zu `σ≈2,2` KEIN echter Bezug ist.
- `thermo/core.py` und alle 8 Kerndokumente unverändert.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m18-schnakenberg-thermodynamics` gelöscht.

## F37: Teil 2, Milestone 19 — CSW-Grapheninvarianten (erledigt 2026-09-18)

Von Aeon geliefert (`prompts/27_teil2_m19_csw_graph_invariants_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F28 (docx) — Cabello/Severini/Winter 2014. `contextuality/csw.py`: zweite, graphentheoretische Kontextualitäts-Charakterisierung neben der bestehenden Sheaf-CF-LP. `lovasz_theta` für `C5` über die Lovász-Regenschirm-Konstruktion HERGELEITET (nicht hartkodiert).
- 4/4 neue Prüfungen selbst nachgerechnet. Regenschirm-Algebra von Hand nachvollzogen: `cos(4π/5)=-(1+√5)/4 → tan²α=√5-1 → ϑ=√5` — Skript-Residuum exakt `0,0`. `α(C5)=2, ϑ=√5≈2,236, α*=5/2` alle bestätigt; Beispiel `p=0,44→Summe=2,2` verletzt die klassische Schranke, hält Quanten-/GPT-Schranke ein. Modul testet aktiv, dass `lovasz_theta` bei Nicht-C5-Graphen verweigert und `contextuality/core.py` nie importiert wird.
- `contextuality/core.py` und alle 8 Kerndokumente unverändert.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m19-csw-graph-invariants` gelöscht.

## F38: Teil 2, Milestone 20 — Profile Likelihood (erledigt 2026-09-18)

Von Aeon geliefert (`prompts/28_teil2_m20_profile_likelihood_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F26 (Astra3) — Raue et al. 2009. `identifiability/profile_likelihood.py`: `profile_parameter` (1D-Grid + Golden-Section, verweigert ≥2 freie Parameter), `classify_identifiability` ("flat"/"identifiable"), `likelihood_interval` (meldet unbeschränkte Intervalle explizit mit Grund statt still abzuschneiden).
- 4/4 neue Prüfungen selbst nachgerechnet. Beide Fälle von Hand bestätigt: `θ1·θ2=6` → `chi2≈0` für alle getesteten `θ1` (Rauschen ~1e-17), korrekt "flat", unbeschränktes Intervall; Kontrollfall `χ²=(θ-3)²` → exakte Parabel, bei Schwelle 1 Intervall `[2,4]` — exakt `|θ-3|≤1`.
- `identifiability/core.py` und alle 8 Kerndokumente unverändert.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m20-profile-likelihood` gelöscht.

## F39: Teil 2, Milestone 21 — Formal Reduction Error Bounds (erledigt 2026-09-19)

Von Aeon geliefert (`prompts/29_teil2_m21_formal_reduction_error_bounds_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F26 (Astra3) — Michel & Siegle, dieselbe Quelle wie M11 aber andere Aussage. `closure/error_bounds.py` implementiert Theorem 4 (DTMC), Theorem 5 (CTMC), Corollary 10 (Stationaritätsabstand), mit Pflicht-Vergleich gegen `propagated_error_bound`.
- 4/4 neue Prüfungen selbst nachgerechnet. Zusätzlich die echte arXiv-Quelle (2403.07618, Abstract UND HTML-Volltext) direkt abgerufen und Theorem 4, Theorem 5 sowie das vollständige zweigliedrige Corollary 10 wortgleich gegen Aeons Zitate bestätigt (eine erste Zusammenfassung hatte Cor. 10 auf einen Term verkürzt, gezielter zweiter Abruf bestätigte die vollständige Form). Beispielmatrizen von Hand bestätigt: `‖ΠA-AP‖∞=0,25` exakt, `π=(2/3,1/3)` als tatsächlicher Stationärvektor von Π selbst nachgerechnet.
- `closure/core.py` und alle 8 Kerndokumente unverändert.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m21-formal-reduction-error-bounds` gelöscht.

## F40: Teil 2, Milestone 22 — Directed Information (erledigt 2026-09-19)

Von Aeon geliefert (`prompts/30_teil2_m22_directed_information_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F28 (docx) — Massey 1990/Permuter et al. 2009. `observation/directed_information.py`: `I(X^n→Y^n)=Σ I(X^i;Y_i|Y^{i-1})` über die Entropie-Identität, mit Laufzeit-Garantie der Massey-Ungleichung.
- 4/4 neue Prüfungen selbst nachgerechnet. Rückkopplungsbeispiel unabhängig von der Entropie-Kettenregel neu hergeleitet (nicht aus dem Code übernommen): `I(X_1;Y_1)=1-H(p)`, zweiter Summand exakt 0, ergibt `I_dir=1-H(p)`; separat `H(X²)=1+H(p)`, `H(X²|Y²)=H(p)` ergibt `I_mutual=1` — beide exakt bestätigt (0,188722 bzw. 1,0). Kontrollfall ohne Rückkopplung liefert exakte Gleichheit.
- `observation/core.py` und alle 8 Kerndokumente unverändert.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m22-directed-information` gelöscht.

## F41: Teil 2, Milestone 23 — Fisher-Information-Sloppiness (erledigt 2026-09-19)

Von Aeon geliefert (`prompts/31_teil2_m23_fisher_sloppiness_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F28 (docx) — Transtrum/Machta/Sethna 2011, Raju et al. 2018. `identifiability/fim_sloppiness.py`: FIM-Spektralzerfall (stiff/sloppy Eigenvektoren), getrennt von `identifiability_jacobian_rank`.
- 4/4 neue Prüfungen selbst nachgerechnet. Jacobi-Matrix und FIM für das Exponential-Zerfalls-Beispiel komplett von Hand hergeleitet — exakte Übereinstimmung (`λ_max=0,35527, λ_min=0,006977, Anisotropie=50,92`). Isotroper Kontrollfall liefert korrekt `Anisotropie=1,0`. Kleine Differenz (16. Nachkommastelle) zwischen eigenem Windows-Lauf und dem committeten Linux-Box-Lauf als harmloses plattformübergreifendes LAPACK-Gleitkommarauschen bestätigt.
- `identifiability/core.py`, `profile_likelihood.py` und alle 8 Kerndokumente unverändert.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m23-fisher-sloppiness` gelöscht.

## F42: Teil 2, Milestone 24 — Čech-Cohomology-Witness (erledigt 2026-09-19)

Von Aeon geliefert (`prompts/32_teil2_m24_cech_cohomology_witness_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F26 (Astra3) — Abramsky/Mansfield/Barbosa 2012. `contextuality/cohomology.py`: relative `Z_2`-Čech-Obstruktion über GF(2)-Lineare-Algebra auf den bereits gemergten Bell-Szenario-Modellen. `proves_contextuality` wird ausschließlich aus `obstruction_nonzero` gesetzt, nie durch Invertieren — sowohl per Laufzeit-Negativtest als auch per statischer Quellcode-Prüfung auf das verbotene Muster abgesichert.
- 4/4 neue Prüfungen selbst nachgerechnet. PR-Box-Kombinatorik von Hand nachvollzogen: Fixierung `a1=0,b1=0` erzwingt über die Kontexte `{a1,b2}` und `{a2,b1}` `b2=0` und `a2=0`, aber `{a2,b2}` unterstützt nur `(0,1)` oder `(1,0)` — echter Widerspruch, bestätigt einen realen Hindernis-Fall. Skript-Ergebnis (8 von 8 Sektionen bei PR-Box, 0 von 16 bei klassisch) ist stärker als der eine handnachgerechnete Fall und konsistent damit.
- `contextuality/core.py`, `csw.py` und alle 8 Kerndokumente unverändert.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m24-cech-cohomology-witness` gelöscht. **Letzter der ursprünglich 17 identifizierten Erweiterungskandidaten — alle jetzt erledigt.**

## F43: DeepResearch-Auftrag Runde 2 — vier menschliche Antworten geprüft, zwei unabhängige Claude-Agenten nachrecherchiert (erledigt 2026-09-19)

`prompts/33_deepresearch_structural_and_mathematical_extensions.md` — Fortsetzung von F26/F28. Vier Antworten in `prompts/Answers/` geprüft:
- `ChatGPTAstra5.md` — **verworfen**: unkenntnis des bereits erledigten Teil-1-Renamings und der 24 gemergten Milestones, erfundene CREP-Akronymauflösung ("Coherence-Resonance-Emergence-Poetics"), mind. ein verdächtiges Zitat. Gleiche Fehlerklasse wie das früher verworfene `ChatGPTAstra4.md` (F28).
- `Mathematische Erweiterungen Scoped Correspondence2.md` — zitiert in den eigenen Referenzen explizit den RUNDE-1-Prompt (`16_deepresearch_natural_extensions.md`), liefert dieselben 7 Runde-1-Vorschläge erneut (6/7 bereits gemergt als M11/M12/M16/M19/M22/M23); einzig neu: ein Rechenbeispiel für das seit Runde 1 offene Fenichel/GSPT-Thema (`dynamics`), das Toy-Beispiel selbst aber zu unterspezifiziert für einen Prompt.
- `Vibe.md` — erste echte Spur-A/B-Antwort im Prompt-33-Format. Spur A verworfen (Koopman-Zitat per WebSearch als falsch verifiziert: falscher Titel/Journal/DOI-Präfix; Verweis auf nicht-existierenden Baustein `causal_emergence`). Spur B teilweise brauchbar (Stefan-Problem, Allen-Cahn, Perkolation mit plausiblen Zitaten; Landau-Theorie inhaltlich korrekt aber mit fragwürdigen Kapitel-DOIs).
- `MSCopilot1.txt` — reiner Meinungsbeitrag ohne Formeln/Zitate, aber unabhängig konvergent mit Vibe.md: empfiehlt "Boundaries"/freie Randprobleme als möglichen 13. Baustein und Chapman-Enskog für `closure`.

Da keine der vier menschlichen Antworten den Spur-A/B-Auftrag vollständig und zuverlässig erfüllte, wurden zusätzlich **zwei unabhängige, frische general-purpose-Claude-Agenten** (nicht Aeon) mit demselben Auftrag plus vollem Repo-Kontext beauftragt — ohne Einsicht ineinander oder in `prompts/Answers/`, mit der Pflicht, jedes Zitat live per WebSearch/WebFetch/Crossref-API zu verifizieren, bevor es verwendet wird. Beide lieferten (52 bzw. 55 Tool-Aufrufe) vollständig zitatgeprüfte Berichte mit expliziten (a)/(b)-Klassifizierungen und mehreren unabhängig konvergierenden Funden (Arimoto-Blahut für `observation` mit identischem Zahlenbeispiel C=0,321928 bit; Stefan-Problem mit fast identischem λ≈0,6201; Perkolation; Turing-Instabilität mit Uneinigkeit in der a/b-Klassifizierung). Ergebnis konsolidiert in `EXTENSIONS_ROADMAP.md` §Runde 2. Fünf Kandidaten (M25-M29) als Prompts an Aeon gesendet, drei weitere Punkte warten auf Johanns Grundsatzentscheidung (Turing a/b, Stefan-Problem und Perkolation als möglicher 13./14. Baustein — größerer Schnitt als eine reine Erweiterung).

## F44: Teil 2, Milestone 25 — Arimoto-Blahut-Kanalkapazität (erledigt 2026-09-19)

Von Aeon geliefert (`prompts/34_teil2_m25_arimoto_blahut_capacity_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F43 (Runde-2-Agentenrecherche, von beiden unabhängigen Agenten übereinstimmend vorgeschlagen) — Arimoto 1972/Blahut 1972. `observation/arimoto_blahut.py`: alternierende Maximierung berechnet die Kanalkapazität für eine BELIEBIGE diskrete gedächtnislose Übergangsmatrix, ergänzt (nicht ersetzt) das bestehende Shannon-Hartley-`channel_capacity`.
- 3/3 neue Prüfungen selbst nachgerechnet (der abschließende Traceback im Skriptlauf ist nur ein Windows-cp1252-Encoding-Fehler beim Ausgeben eines Pfeilzeichens NACH dem JSON-Schreiben, kein echter Bug — mit `PYTHONIOENCODING=utf-8` läuft es sauber durch). Z-Kanal-Beispiel (ε=0,5) von Hand aus der Stationaritätsbedingung `dI/dq=0` hergeleitet: `q*=0,4`, `C=log2(1,25)=0,321928...` — exakt bestätigt gegen die konvergierte Ausgabe (53 Iterationen). BSC-Kontrollfall (`p=0,1`) konvergiert korrekt in 1 Iteration (uniforme Startverteilung ist bereits optimal), `C=1-H2(0,1)=0,531004...` exakt bestätigt.
- `observation/core.py` und alle acht Kerndokumente unverändert. Berührt bewusst nicht den Paket-Root-`__init__.py` (nur `observation/__init__.py`).
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m25-arimoto-blahut-capacity` wird gelöscht.

## F45: Teil 2, Milestone 26 — Lie-Poisson / Casimir-Invarianten (erledigt 2026-09-19)

Von Aeon geliefert (`prompts/35_teil2_m26_lie_poisson_casimir_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F43 — Arnold 1966/Marsden & Ratiu 1999. `coupling/casimir.py`: `casimir_residual`/`hat_map` formalisieren die Casimir-Bedingung, die `check_generic_structure` bereits implizit verlangt (`J∇S=0`), ausdrücklich NUR für den endlich-dimensionalen so(3)*-Starrkörperfall — explizit keine Fluid-PDE-Implementierung und keine Gleichsetzung von `coupling` mit Fluiddynamik.
- 5/5 neue Prüfungen selbst nachgerechnet. Starrkörper-Beispiel (`z=(1,2,3)`, `I=(1,2,3)`) komplett von Hand hergeleitet: `J@∇C=(0,0,0)`, `ż=(-1,2,-1)`, `dC/dt=dH/dt=0`, Negativfall `J@(1,0,0)=(0,3,-2)` mit `max_abs=3` — alle exakt bestätigt. Branch lag auf einem neueren Commit als die zuerst gemeldete SHA (reine ASCII-Docstring-Bereinigung ohne Logikänderung, per Diff bestätigt harmlos).
- `coupling/core.py` und alle acht Kerndokumente unverändert. Berührt bewusst nicht den Paket-Root-`__init__.py`.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m26-lie-poisson-casimir` wird gelöscht.

## F46: Teil 2, Milestone 27 — Formal Concept Analysis (erledigt 2026-09-19)

Von Aeon geliefert (`prompts/36_teil2_m27_formal_concept_analysis_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F43 — Ganter & Wille 1999. `membership/formal_concept_analysis.py`: Galois-Verbindung (`derive_up`/`derive_down`) und vollständige Konzeptverbands-Enumeration auf der bestehenden binären `MembershipMatrix` — schließt die bisherige "kein Kandidat"-Lücke für `membership`, OHNE die zurückgestellte gewichtete Semantik zu benötigen.
- 5/5 neue Prüfungen selbst nachgerechnet. Der vollständige 6-Konzept-Verband der 4×3-Beispielmatrix von Hand über Zeilen-/Spaltenschnitt nachvollzogen (Konzept `({e1,e3,e4},{s2})` unabhängig bestätigt: Spalte s2 ist genau bei e1,e3,e4 gleich 1), inklusive der abgeleiteten Implikation "s3⇒s1" und des Negativfalls (`{e1,e2}` ist kein Konzept).
- `membership/core.py` und alle acht Kerndokumente unverändert. Berührt bewusst nicht den Paket-Root-`__init__.py`.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m27-formal-concept-analysis` wird gelöscht.

## F47: Teil 2, Milestone 28 — Nagumo-Tangentialkegel für Polyeder (erledigt 2026-09-19)

Von Aeon geliefert (`prompts/37_teil2_m28_nagumo_tangent_cone_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F43 — Nagumo 1942. `viability/nagumo.py`: notwendige-und-hinreichende Tangentialkegel-Bedingung für polyedrische/Box-Mengen, deckt den nicht-glatten Fall ab, den das bestehende M16 (CBF) nicht erreicht (keine einzelne glatte Barrierefunktion an einer Ecke).
- 3/3 neue Prüfungen selbst nachgerechnet. Alle vier Ecken des `[-1,1]²`-Beispiels per `f=A_sys·z` von Hand nachgerechnet (`f(1,1)=(-0,5;-1,5)`, `f(1,-1)=(-1,5;0,5)`, `f(-1,1)=(1,5;-0,5)`, `f(-1,-1)=(0,5;1,5)`) — exakt bestätigt, alle Randbedingungen erfüllt. Negativfall (Identitätsdynamik an Ecke (1,1)) korrekt als Verletzung erkannt.
- `viability/core.py`, `control_barrier.py` und alle acht Kerndokumente unverändert. Berührt bewusst nicht den Paket-Root-`__init__.py`.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m28-nagumo-tangent-cone` wird gelöscht.

## F48: Teil 2, Milestone 29 — Landau-Exponentenvergleich / Selbst-Falsifizierung (erledigt 2026-09-19)

Von Aeon geliefert (`prompts/38_teil2_m29_landau_exponent_comparison_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F43 — Onsager 1944/Yang 1952/Guckenheimer & Holmes 1983. `dynamics/landau.py`: nutzt die bestehende `CubicNormalForm`/`fixed_points` als Landau-Ordnungsparameter-Modell und vergleicht den modellinternen mean-field-Exponenten (β=1/2) mit dem exakten 2D-Ising-Exponenten (β=1/8) — ein eingebautes, ausführbares Gegenbeispiel gegen Universalitätsansprüche, mit Pflicht-Docstring-Warnung, dass Onsagers `2/ln(1+√2)=2,269185` rein zufällig nahe am früher verworfenen σ≈2,2 liegt.
- 5/5 neue Prüfungen selbst nachgerechnet. Alle Zahlen von Hand bestätigt: `x*(0,25)=0,5`, `x*(0,0625)=0,25`, Verhältnis `4^0,5=2,0`, hypothetisches Ising-Verhältnis `4^0,125=1,189207`, Diskrepanzfaktor `1,681793`, Onsager-Verhältnis `2,269185314` — alle exakt. Landau 1937 (keine verifizierbare DOI) korrekt nicht zitiert.
- `dynamics/core.py` und alle acht Kerndokumente unverändert. Berührt bewusst nicht den Paket-Root-`__init__.py`.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m29-landau-exponent-comparison` wird gelöscht. **Johann entscheidet zugleich (2026-09-19): Turing-Instabilität, Stefan-Problem und Perkolation werden als drei eigenständige neue Bausteine geplant (nicht als Erweiterung bestehender Module) — siehe `EXTENSIONS_ROADMAP.md` §Runde 2.**

## F49: drei neue, eigenständige Bausteine beauftragt (2026-09-19, ausstehend)

Umsetzung von Johanns Entscheidung aus F48: drei komplett neue,
eigenständige Bausteine statt Erweiterungen bestehender Module.
- `prompts/39_teil2_pattern_formation_turing_for_aeon.md` — neuer
  Baustein `pattern_formation` (Turing 1952, Schnakenberg 1979 —
  ausdrücklich NICHT Schnakenberg 1976 aus M18 —, Murray 2003).
  Pflicht-Docstring-Hinweis: eine mögliche künftige
  `correspondence`-Brücke zu `dynamics` (`S_rec(k)` verallgemeinert
  `S_rec(0)`) bleibt als offener, unbewiesener Kandidat dokumentiert,
  wird aber nicht gebaut.
- `prompts/40_teil2_free_boundary_stefan_for_aeon.md` — neuer Baustein
  `free_boundary` (Stefan-Problem, Kot 2017 + Bollati et al. arXiv
  1906.08601; Rubinstein 1971 bewusst weggelassen, keine verlässliche
  DOI in dieser Runde gefunden).
- `prompts/41_teil2_percolation_kesten_for_aeon.md` — neuer Baustein
  `percolation` (Kesten 1980 + Fisher & Essam 1961, exakt lösbarer
  Bethe-Gitter-/Baum-Fall). Pflicht-Docstring-Hinweise: keine
  Verwandtschaft zur Cusp-Schwelle in `dynamics`, und jede zufällige
  Nähe zu bereits verworfenen Zahlenwerten (u.a. 1/16) muss explizit
  als Zufall vermerkt werden.

Alle drei können parallel bearbeitet werden (komplett unabhängige,
neue Package-Verzeichnisse). `EXTENSIONS_ROADMAP.md` entsprechend
aktualisiert.

## F50: neuer Baustein `pattern_formation` — Turing-Instabilität (erledigt 2026-09-19)

Von Aeon geliefert (`prompts/39_teil2_pattern_formation_turing_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F49 — Turing 1952/Schnakenberg 1979/Murray 2003. `pattern_formation/core.py`: alle vier Turing-Bedingungen für Diffusions-getriebene Instabilität, Dispersionsrelation, Schnakenberg-1979-Kinetik als durchgerechnetes Beispiel. Komplett eigenständiger, neuer Baustein — kein Unterfall von `dynamics`.
- 5/5 neue Prüfungen selbst nachgerechnet. Fixpunkt/Jacobi von Hand bestätigt (`u*=1,0, v*=0,9, f_u=0,8, f_v=1,0, g_u=-1,8, g_v=-1,0`, `trJ=-0,2, detJ=1,0`). Kritisches `D_v` selbst aus der quadratischen Gleichung `0,64*D_v²-5,6*D_v+1=0` hergeleitet (Diskriminante 28,8, Wurzeln `8,567627`/`0,182373`) — exakt bestätigt. `k_c²` über zwei unabhängige Formeln exakt übereinstimmend (`0,341641`). Alle drei Dispersions-Vorzeichen (stabil unterhalb, ≈0 an der Kritikalität, instabil oberhalb) bestätigt.
- Beide Pflicht-Docstring-Warnhinweise wörtlich vorhanden: (1) Schnakenberg 1979 (J. Theor. Biol.) ist ein ANDERER Aufsatz als Schnakenberg 1976 (Rev. Mod. Phys.) aus M18; (2) eine mögliche künftige `correspondence`-Brücke zu `dynamics` (`S_rec(k)` verallgemeinert `S_rec(0)`) ist als offener, unbewiesener Kandidat dokumentiert, nicht implementiert.
- Kein bestehender Baustein, kein Paket-Root-`__init__.py`, keine der acht Kerndokumente berührt.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m30-pattern-formation-turing` wird gelöscht.

## F51: neuer Baustein `free_boundary` — Stefan-Problem (erledigt 2026-09-19)

Von Aeon geliefert (`prompts/40_teil2_free_boundary_stefan_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F49 — Kot 2017/Bollati et al. arXiv:1906.08601. `free_boundary/core.py`: Neumann-Ähnlichkeitslösung des Ein-Phasen-Stefan-Problems, bewegliche Phasengrenze als eigene dynamische Variable — kein Unterfall von `viability` (dessen `K` immer fest vorgegeben ist).
- 5/5 neue Prüfungen selbst nachgerechnet. `sqrt(t)`-Frontgesetz von Hand bestätigt: `s(100)=12,401253mm`, `s(400)=24,802505mm`, Verhältnis exakt `2,0` (da `sqrt(400)/sqrt(100)=2`). `lambda` fällt monoton mit sinkender Stefan-Zahl über alle vier getesteten Fälle (`Ste=1/0,5/0,1/0,01`) — physikalisch sinnvoll bestätigt. Rubinstein 1971 und Stefan 1891 korrekt NICHT zitiert (keine verifizierte DOI in dieser Runde).
- Kein bestehender Baustein, kein Paket-Root-`__init__.py`, keine der acht Kerndokumente berührt.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m31-free-boundary-stefan` wird gelöscht.

## F52: neuer Baustein `percolation` — Kesten / Bethe-Gitter-Verzweigung (erledigt 2026-09-19)

Von Aeon geliefert (`prompts/41_teil2_percolation_kesten_for_aeon.md`) direkt als GitHub-Branch, per Claude-Review gemergt nach `master`. Aus F49 — Kesten 1980/Fisher & Essam 1961. `percolation/core.py`: exakt lösbarer Baum-/Bethe-Gitter-Verzweigungsprozess (`Q=(1-p+p*Q)^m`, `p_c=1/m`) — kein Unterfall von `dynamics` oder `membership` (Perkolation betrifft die a.s.-Existenz eines unendlichen Clusters in einem ZUFÄLLIGEN Teilgraphen, ein Objekt, das keines der beiden Module abbildet).
- 5/5 neue Prüfungen selbst nachgerechnet. `m=2, p=0,6`-Fall komplett von Hand hergeleitet (`9Q²-13Q+4=0`, Wurzeln `{1; 4/9}`) — exakt bestätigt. Zusätzlich selbst den Fall `m=2, p=0,8` hergeleitet (`16Q²-17Q+1=0` → `Q*=1/16` exakt) und damit unabhängig bestätigt, dass die im Code ausgelöste 1/16-Koinzidenzwarnung nicht nur vorhanden, sondern durch eine echte, unabhängig nachvollziehbare Rechnung tatsächlich ausgelöst wird — nicht nur bei größerer Verzweigung, sondern bereits im einfachsten Binärbaum-Fall.
- Beide Pflicht-Docstring-Warnhinweise wörtlich vorhanden: keine Verwandtschaft zur Cusp-Schwelle in `dynamics` (nur zufällig dasselbe Alltagswort "Schwelle"), und die 1/16-Koinzidenz explizit als Zufall vermerkt, keine Beziehung zum bereits verworfenen README-Wert.
- Kein bestehender Baustein, kein Paket-Root-`__init__.py`, keine der acht Kerndokumente berührt.
- Gemergt auf `master` nach Johanns OK; Review-Branch `aeon/m32-percolation-kesten` wird gelöscht. **Das Repository hat damit 15 Bausteine.**

## F53: DeepResearch-Auftrag Runde 3 gesendet (erledigt 2026-09-19)

`prompts/42_deepresearch_round3_legacy_concepts_and_further_extensions.md`
— diesmal an zwei unabhängige Grok-Agenten (von Aeon beauftragt, nicht
Claude-Subagenten). Drei Spuren: (A) weitere direkte Erweiterungen wie
Runde 1/2 (jetzt 15 Bausteine, 25 bereits gemergte Vorschläge — Feld
zunehmend ausgeschöpft), (B) Fortsetzung von Runde 2s eigenständigen
Themenfeldern — explizit inklusive der zwei Punkte aus Runde 2s Auftrag
(`prompts/33_...md`), die dort nur als Orientierung genannt, aber nie
zu einem Milestone wurden: GENERIC↔Navier-Stokes (Öttinger & Grmela)
für `coupling`/`thermo`, und die Chapman-Enskog-Entwicklung
(hydrodynamischer Grenzwert als Closure-Problem) für `closure`, (C) NEU
auf Johanns Anregung — ehrliche Neuprüfung der
ursprünglichen CREP/UTAC/AFET-Inspirationsliteratur (Panarchy/Holling,
Autopoiesis/Maturana-Varela, strukturelle Kopplung im Sinne
generalisierter Synchronisation, Resilienz-Frühwarnsignale/Scheffer
et al. 2009), explizit OHNE die künstliche Übersetzung, die zu den
bereits zurückgenommenen Gleichsetzungen (β≡Stabilität,
V≡Panarchy≡Onsager-L, geteiltes σ=2,2, A_ij≡L_ij) geführt hatte. Jeder
Spur-C-Vorschlag muss explizit als (a) echte Erweiterung eines
Bausteins oder (b) eigenständiger neuer Baustein klassifiziert werden;
"nichts Zitierfähiges gefunden" (v.a. für Autopoiesis erwartet) ist
ein explizit zulässiges, valides Ergebnis.

## F54: Runde-3-Auswertung — vier unabhängige Reports (2 Claude, 2 Grok), 9 Milestones gesendet (erledigt 2026-09-19)

Vier unabhängige Antworten auf F53 lagen vor: zwei eigene Claude-
Agenten (parallel zu Aeon beauftragt) und zwei von Aeon beauftragte
Grok-Agenten (`Round3_AgentA_REPORT.md`, `Round3_AgentB_REPORT.md` in
`prompts/Answers/`). Bemerkenswerte Konvergenz: 7 von 9 Kandidaten
wurden von 3 oder 4 der 4 Agenten unabhängig gefunden, teils mit
identischem Sekundärzitat (Zwick & Hughes 2017 für Panarchy, von 3/4
Agenten unabhängig gefunden — eine sehr spezifische, seltene
Übereinstimmung, die hohe Verlässlichkeit signalisiert). Zwei
Kandidaten (Floquet, Crooks-Fluktuationstheorem) wurden je nur von
einem Grok-Agenten gefunden — von Claude zusätzlich live per
Crossref-API verifiziert (beide bestätigt: Floquet 1883, DOI
10.24033/asens.220; Crooks 1999, DOI 10.1103/PhysRevE.60.2721).

Johanns Entscheidung: alle neun "eindeutigen" Kandidaten werden
unabhängig vom Konvergenzgrad übernommen. Zusätzlich zwei
Vertiefungsaufträge erledigt:
1. **Namenskollision COT/`closure`:** Chemical Organization Theory
   (der einzige belastbare Teilaspekt von Autopoiesis, alle vier
   Agenten übereinstimmend — volle Autopoiesis: nichts gefunden)
   verwendet den Begriff "closed"/"closure" für ein komplett anderes
   Konzept als der bestehende `closure`-Baustein. Auflösung: neuer
   Baustein `chemical_organization`, API vermeidet das Wort
   "closure"/"closed" vollständig (`is_reaction_closed`,
   `is_self_maintaining`, `is_organization`), mit Pflicht-
   Docstring-Zaun gegen `closure.is_exact_closure` UND gegen M27s
   Konzeptverband (`membership`) — zweite zufällige Wortkollision
   ("Verband"/"Lattice").
2. **Brücken-Vermerk:** M39 (Pecora-Carroll/generalisierte
   Synchronisation, `coupling`) und das bereits gemergte M14
   (Kontraktionsanalyse, `dynamics`) teilen ein strukturell ähnliches
   Vorzeichenkriterium — erhält denselben "offener, unbewiesener
   `correspondence`-Kandidat"-Vermerk wie zuvor Turing↔dynamics.

Neun Prompts gesendet: `prompts/43_...md` (Fenichel/GSPT, `dynamics`),
`44_...md` (Floquet, `dynamics`), `45_...md` (Panarchy-Cusp,
`dynamics`), `46_...md` (Early-Warning-Signale, `dynamics`),
`47_...md` (Crooks-Fluktuationstheorem, `thermo`), `48_...md`
(GENERIC↔Navier-Stokes, `coupling` — mit korrigierter Quellenlage:
Öttinger-Grmela 1997 allein deckt laut unabhängiger Prüfung die
NS-Verbindung NICHT ab, stattdessen Morrison 1984 + Barham/Morrison/
Zaidni 2025), `49_...md` (Pecora-Carroll-Synchronisation, `coupling`,
mit Brücken-Vermerk), `50_...md` (Chapman-Enskog/BGK-Route, `closure`
— Chapman & Cowlings Monographie bewusst nicht zitiert, keine
verifizierbare DOI), `51_...md` (neuer Baustein
`chemical_organization`, mit beiden Namenskollisions-Zäunen).
`EXTENSIONS_ROADMAP.md` §Runde 3 entsprechend aktualisiert.

## F55: Runde 3 — alle neun Milestones geliefert, geprüft und gemergt (erledigt 2026-09-19)

Acht der neun Prompts kamen als Aeon-Branches zurück (M33, M34, M35,
M37–M41); M36 (Early-Warning-Signale) fehlte, da Aeons Grok-Kontingent
für die nächsten 5 Tage aufgebraucht war — auf Johanns Bitte von Claude
selbst direkt implementiert (eigener Branch `claude/m36-early-warning-
signals`, dieselbe Disziplin: additiv, durchgerechnetes Beispiel,
Johann-OK vor Merge).

**Alle acht Aeon-Branches unabhängig geprüft** (Diff-Scope, Skript
selbst nachgerechnet, mindestens eine Zahl von Hand):
- **M33 Fenichel/GSPT**: Faltpunkte `S(±1)=∓2/3`, Normalhyperbolizität
  an 4 Testpunkten von Hand bestätigt.
- **M34 Floquet**: `tr=1,5,det=1→μ=0,75±i0,661438,|μ|=1` (neutral);
  `tr=2,5,det=1→μ={0,5;2,0}` (instabil); Grenzfall `tr=2,det=1`
  (doppeltes `μ=1`) korrekt "neutral" statt "stable" — alle von Hand
  bestätigt.
- **M35 Panarchy-Cusp**: **Aeon fand und korrigierte selbständig einen
  Rechenfehler im Milestone-Prompt** — `fold_thresholds(3)` ist `±2`
  (aus `√(4a³/27)=√4=2`), nicht `±2/√3≈1,1547` wie im Prompt stand (ein
  beim Vereinfachen fallengelassener Faktor `a^(3/2)=3√3`). Transparent
  im JSON als `note_research_slip_2_over_sqrt3` dokumentiert statt
  stillschweigend übernommen. Von Claude unabhängig nachgerechnet:
  `4·27-27·4=0` bestätigt `b=2` als echte Falte.
- **M37 Crooks**: `ω=1,e^ω=e` exakt; Jarzynski-Schätzer konvergiert auf
  `1,50014` gegen wahren Wert `1,5`.
- **M38 GENERIC↔NS**: `a·∇E=0` (Degeneriertheit strukturell), `M∇S=
  (-1,1,3,-1)` exakt, Entropieproduktion `2/300=0,006667` exakt, alle
  Residuen von `check_generic_structure` ≈0.
- **M39 Pecora-Carroll**: `φ=c/(k-1)`, `CLE=-k` — `c=4,k=3→φ=2,CLE=-3`
  (Sync); `c=4,k=-1→φ=-2,CLE=1` (kein Sync trotz existierender
  Abbildung) — beide exakt. Brücken-Vermerk zu M14 wörtlich vorhanden.
- **M40 Chapman-Enskog**: `μ=1,κ=2,5,Pr=1,0` exakt; Verhältnis zum
  realen `Pr=2/3` exakt `1,5`; Hartkugelformel korrekt nicht verwendet.
- **M41 chemical_organization**: Regex-Scan selbst mit `grep`
  nachvollzogen (nur die erlaubte Ausnahme `is_reaction_closed`, keine
  verbotenen Bezeichner). Beispiel von Hand: ohne `r4` erzwingt die
  Summe `(Sv)_a+(Sv)_b=-v3<0` einen echten Widerspruch; mit `r4` erfüllt
  Zeuge `v=(2,1,1,1)` `(Sv)_a=(Sv)_b=0` exakt.

Alle neun gemergt auf `master` nach Johanns OK. Nach dem Mergen aller
neun (mit den erwarteten trivialen `pyproject.toml`/`dynamics`-`
coupling`-`__init__.py`-Konflikten, da mehrere Milestones dieselben
Submodule betrafen) wurde ein vollständiger Import- und Verify-Lauf
über alle betroffenen Bausteine (`dynamics`, `coupling`, `thermo`,
`closure`, `chemical_organization`) durchgeführt — alle Importe und
alle neun Verify-Skripte laufen sauber auf dem gemergten Stand.
Review-Branches gelöscht (lokal + origin für die acht Aeon-Branches;
`claude/m36-early-warning-signals` bleibt als Backup auf origin
bestehen). **Das Repository hat jetzt 16 Bausteine**, `pyproject.toml`
bei `0.41.0a1`.

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
