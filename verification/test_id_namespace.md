# Test-ID namespace / alias layer (Milestone 1)

**Principle:** no renumbering. The existing 19+16+18+6+7 = **66** checks keep their
script-local ids as provenance; this table only adds a stable public alias
(ARCHITECTURE_ROADMAP.md — *Migrationsprinzip für bestehende Tests*; Astra ChatGPTAstra2.md).

Kind: Verification (synthetic). Not empirical validation.

| # | Script | Legacy id (unchanged) | Public alias | Notes |
|---|---|---|---|---|
| 1 | `verify_formalism.py` | `c01_sigmoid_independence` | `VER-CORE-c01_sigmoid_independence` | Basis / counterexample & model checks |
| 2 | `verify_formalism.py` | `c02_coordinate_mismatch` | `VER-CORE-c02_coordinate_mismatch` | Basis / counterexample & model checks |
| 3 | `verify_formalism.py` | `c03_positive_a_insufficient` | `VER-CORE-c03_positive_a_insufficient` | Basis / counterexample & model checks |
| 4 | `verify_formalism.py` | `c04_probability_not_distance` | `VER-CORE-c04_probability_not_distance` | Basis / counterexample & model checks |
| 5 | `verify_formalism.py` | `c05_directed_matrix_not_thermodynamics` | `VER-CORE-c05_directed_matrix_not_thermodynamics` | Basis / counterexample & model checks |
| 6 | `verify_formalism.py` | `c06_information_window` | `VER-CORE-c06_information_window` | Basis / counterexample & model checks |
| 7 | `verify_formalism.py` | `c07_raw_frame_units` | `VER-CORE-c07_raw_frame_units` | Basis / counterexample & model checks |
| 8 | `verify_formalism.py` | `c08_s8_not_probability` | `VER-CORE-c08_s8_not_probability` | Basis / counterexample & model checks |
| 9 | `verify_formalism.py` | `p01_cusp_branches_and_time` | `VER-CORE-p01_cusp_branches_and_time` | Basis / counterexample & model checks |
| 10 | `verify_formalism.py` | `p02_cusp_region` | `VER-CORE-p02_cusp_region` | Basis / counterexample & model checks |
| 11 | `verify_formalism.py` | `p03_information_channel` | `VER-CORE-p03_information_channel` | Basis / counterexample & model checks |
| 12 | `verify_formalism.py` | `p04_frame_normalization_and_domain` | `VER-CORE-p04_frame_normalization_and_domain` | Basis / counterexample & model checks |
| 13 | `verify_formalism.py` | `p05_symmetric_and_antisymmetric` | `VER-CORE-p05_symmetric_and_antisymmetric` | Basis / counterexample & model checks |
| 14 | `verify_formalism.py` | `p06_heat_balance_and_relaxation` | `VER-CORE-p06_heat_balance_and_relaxation` | Basis / counterexample & model checks |
| 15 | `verify_formalism.py` | `p07_self_similarity_of_relaxation` | `VER-CORE-p07_self_similarity_of_relaxation` | Basis / counterexample & model checks |
| 16 | `verify_formalism.py` | `p08_discrete_rate_and_sampling` | `VER-CORE-p08_discrete_rate_and_sampling` | Basis / counterexample & model checks |
| 17 | `verify_formalism.py` | `p09_amoc_frozen_control` | `VER-CORE-p09_amoc_frozen_control` | Basis / counterexample & model checks |
| 18 | `verify_formalism.py` | `p10_solar_quiet_submodel` | `VER-CORE-p10_solar_quiet_submodel` | Basis / counterexample & model checks |
| 19 | `verify_formalism.py` | `p11_document_links` | `VER-CORE-p11_document_links` | Basis / counterexample & model checks |
| 20 | `verify_extensions.py` | `e01_circle_reconstruction` | `VER-REC-e01_circle_reconstruction` | Reconstruction |
| 21 | `verify_extensions.py` | `e02_sampling_alias_and_conditioning` | `VER-REC-e02_sampling_alias_and_conditioning` | Reconstruction |
| 22 | `verify_extensions.py` | `e03_projected_memory` | `VER-MEM-e03_projected_memory` | Memory / non-Markov projection |
| 23 | `verify_extensions.py` | `e04_exact_lumpability` | `VER-CLS-e04_exact_lumpability` | Closure / lumpability |
| 24 | `verify_extensions.py` | `e05_nonclosed_aggregation` | `VER-CLS-e05_nonclosed_aggregation` | Closure |
| 25 | `verify_extensions.py` | `e06_approximate_error_bound` | `VER-CLS-e06_approximate_error_bound` | Closure error bound |
| 26 | `verify_extensions.py` | `e07_effective_information_ensembles` | `VER-INF-EI-e07_effective_information_ensembles` | Effective information |
| 27 | `verify_extensions.py` | `e08_fixed_ensemble_data_processing` | `VER-INF-EI-e08_fixed_ensemble_data_processing` | EI / data processing |
| 28 | `verify_extensions.py` | `e09_svd_does_not_imply_ei` | `VER-DIAG-SVD-e09_svd_does_not_imply_ei` | Diagnostic (not emergence score) |
| 29 | `verify_extensions.py` | `e10_inverse_is_not_detailed_balance` | `VER-DYN-REV-e10_inverse_is_not_detailed_balance` | Dynamics / reversibility |
| 30 | `verify_extensions.py` | `e11_topological_conjugacy_rates` | `VER-COR-e11_topological_conjugacy_rates` | Correspondence / conjugacy |
| 31 | `verify_extensions.py` | `e12_parameter_scaling_nonidentifiability` | `VER-COR-e12_parameter_scaling_nonidentifiability` | Correspondence / scaling |
| 32 | `verify_extensions.py` | `e13_generic_heat_structure` | `VER-TH-e13_generic_heat_structure` | Thermodynamics / GENERIC |
| 33 | `verify_extensions.py` | `e14_viability_at_fixed_recovery_rate` | `VER-VIA-e14_viability_at_fixed_recovery_rate` | Viability |
| 34 | `verify_extensions.py` | `e15_predictive_states` | `VER-CLS-PRED-e15_predictive_states` | Closure / predictive states |
| 35 | `verify_extensions.py` | `e16_current_document_links` | `VER-DOC-e16_current_document_links` | Documentation CI |
| 36 | `verify_transformations.py` | `t01_context_derivatives` | `VER-COR-T01` | Context transformations / closure / viability (IDs preserved) |
| 37 | `verify_transformations.py` | `t02_state_dependent_time` | `VER-COR-T02` | Context transformations / closure / viability (IDs preserved) |
| 38 | `verify_transformations.py` | `t03_parameter_chain_rule` | `VER-COR-T03` | Context transformations / closure / viability (IDs preserved) |
| 39 | `verify_transformations.py` | `t04_composed_transformations` | `VER-COR-T04` | Context transformations / closure / viability (IDs preserved) |
| 40 | `verify_transformations.py` | `t05_scalar_boundary_and_hitting` | `VER-COR-T05` | Context transformations / closure / viability (IDs preserved) |
| 41 | `verify_transformations.py` | `t06_sum_difference_transformation` | `VER-COR-T06` | Context transformations / closure / viability (IDs preserved) |
| 42 | `verify_transformations.py` | `t07_unequal_rates_break_closure` | `VER-COR-T07` | Context transformations / closure / viability (IDs preserved) |
| 43 | `verify_transformations.py` | `t08_memory_elimination` | `VER-COR-T08` | Context transformations / closure / viability (IDs preserved) |
| 44 | `verify_transformations.py` | `t09_orthant_boundary_conditions` | `VER-COR-T09` | Context transformations / closure / viability (IDs preserved) |
| 45 | `verify_transformations.py` | `t10_shared_budget_conflict` | `VER-COR-T10` | Context transformations / closure / viability (IDs preserved) |
| 46 | `verify_transformations.py` | `t11_optimal_symmetric_horizon` | `VER-COR-T11` | Context transformations / closure / viability (IDs preserved) |
| 47 | `verify_transformations.py` | `t12_closed_sum_not_local_safety` | `VER-COR-T12` | Context transformations / closure / viability (IDs preserved) |
| 48 | `verify_transformations.py` | `t13_moving_boundaries` | `VER-COR-T13` | Context transformations / closure / viability (IDs preserved) |
| 49 | `verify_transformations.py` | `t14_finite_actuation_reservoir` | `VER-COR-T14` | Context transformations / closure / viability (IDs preserved) |
| 50 | `verify_transformations.py` | `t15_changing_partition_exact_closure` | `VER-COR-T15` | Context transformations / closure / viability (IDs preserved) |
| 51 | `verify_transformations.py` | `t16_nonstationary_total_variation_bound` | `VER-COR-T16` | Context transformations / closure / viability (IDs preserved) |
| 52 | `verify_transformations.py` | `t17_residual_to_trajectory_bound` | `VER-COR-T17` | Context transformations / closure / viability (IDs preserved) |
| 53 | `verify_transformations.py` | `t18_recursive_flux_balance` | `VER-COR-T18` | Context transformations / closure / viability (IDs preserved) |
| 54 | `verify_sheaf_contextuality.py` | `s01_margin_compatibility_222` | `VER-CTX-s01_margin_compatibility_222` | F08 Contextuality |
| 55 | `verify_sheaf_contextuality.py` | `s02_classical_global_section` | `VER-CTX-s02_classical_global_section` | F08 Contextuality |
| 56 | `verify_sheaf_contextuality.py` | `s03_pr_box_cf_one` | `VER-CTX-s03_pr_box_cf_one` | F08 Contextuality |
| 57 | `verify_sheaf_contextuality.py` | `s04_chsh_table_i_partial_cf` | `VER-CTX-s04_chsh_table_i_partial_cf` | F08 Contextuality |
| 58 | `verify_sheaf_contextuality.py` | `s05_vb1_deterministic_contradiction` | `VER-CTX-s05_vb1_deterministic_contradiction` | F08 Contextuality |
| 59 | `verify_sheaf_contextuality.py` | `s06_arxiv_links_documented` | `VER-CTX-s06_arxiv_links_documented` | F08 Contextuality |
| 60 | `verify_pid_rb.py` | `p01_unique_gate` | `VER-PID-p01_unique_gate` | F09 PID / Redundancy Bottleneck |
| 61 | `verify_pid_rb.py` | `p02_xor_synergy` | `VER-PID-p02_xor_synergy` | F09 PID / Redundancy Bottleneck |
| 62 | `verify_pid_rb.py` | `p03_and_and_full_redundancy` | `VER-PID-p03_and_and_full_redundancy` | F09 PID / Redundancy Bottleneck |
| 63 | `verify_pid_rb.py` | `p04_nonnegative_atoms` | `VER-PID-p04_nonnegative_atoms` | F09 PID / Redundancy Bottleneck |
| 64 | `verify_pid_rb.py` | `p05_rb0_blackwell` | `VER-PID-p05_rb0_blackwell` | F09 PID / Redundancy Bottleneck |
| 65 | `verify_pid_rb.py` | `p06_ei_q_beside_pid_smoke` | `VER-PID-p06_ei_q_beside_pid_smoke` | F09 PID / Redundancy Bottleneck |
| 66 | `verify_pid_rb.py` | `p07_arxiv_links` | `VER-PID-p07_arxiv_links` | F09 PID / Redundancy Bottleneck |

## Namespace summary

| Namespace | Count | Source |
|---|---:|---|
| `VER-CORE-*` | 19 | `verify_formalism.py` |
| `VER-REC-*` | 2 | extensions e01–e02 |
| `VER-MEM-*` | 1 | extensions e03 |
| `VER-CLS-*` / `VER-CLS-PRED-*` | 4 | extensions e04–e06, e15 |
| `VER-INF-EI-*` | 2 | extensions e07–e08 |
| `VER-DIAG-SVD-*` | 1 | extensions e09 |
| `VER-DYN-REV-*` | 1 | extensions e10 |
| `VER-COR-*` (incl. e11–e12) | 2 | extensions conjugacy/scaling |
| `VER-COR-T01` … `VER-COR-T18` | 18 | `verify_transformations.py` |
| `VER-TH-*` | 1 | extensions e13 |
| `VER-VIA-*` | 1 | extensions e14 |
| `VER-DOC-*` | 1 | extensions e16 |
| `VER-CTX-*` | 6 | F08 sheaf |
| `VER-PID-*` | 7 | F09 PID/RB |
| **Total** | **66** | |

Note: legacy `p01`… in formalism vs PID collide only at the bare name; aliases
`VER-CORE-p01_*` vs `VER-PID-p01_*` keep them distinct.

New Milestone-1 equivalence checks (not part of the historical 66) use ids
`MIG-COR-*` in `verify_correspondence_core.py`.
