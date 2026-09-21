"""Dynamics core (ex-UTAC): sigmoid response, recovery rate, cubic normal form.

FORMALISM.md §2 rows: beta_response, S_rec, lambda_L (S_rec used here).
FORMALISM.md §4–§5; system_layer_utac.md.

Milestone 14 (Contraction Analysis) is exported here as a **submodule-local**
addition; package-root ``scoped_correspondence.__init__`` is intentionally
left untouched to avoid fighting parallel M15/M16 branches.

Milestone 29 (Landau Exponent Comparison / Self-Falsification) is likewise
exported submodule-locally; ``dynamics/core.py`` is CALLED only (not edited).

Milestone 33 (Fenichel / GSPT) is exported submodule-locally; independent of
M14 contraction and M29 Landau; ``dynamics/core.py`` untouched.

Milestone 34 (Floquet Multipliers) is exported submodule-locally; given 2×2
monodromy only — no ODE integrator; **not** M14 contraction;
``dynamics/core.py`` and package-root ``__init__`` untouched.

Milestone 35 (Panarchy / Adaptive-Cycle as Cusp extension) is likewise
exported submodule-locally; ``dynamics/core.py`` is CALLED only
(``fixed_points`` + ``CubicNormalForm.discriminant``); does NOT revive
V≡Panarchy≡Onsager-L.

Milestone 36 (Early-Warning Signals / Critical Slowing Down) is likewise
exported submodule-locally; ``dynamics/core.py`` is CALLED only (not edited).

Milestone 42 (Rate-Dependent Tracking / Rate-Induced Tipping,
NONSTATIONARY_ROADMAP.md package 3) is likewise exported submodule-locally;
independent of M14/M29/M33/M35/M36; ``dynamics/core.py``, ``gspt.py``, and
``panarchy_cusp.py`` are untouched -- this module answers a genuinely
different question (real non-autonomous trajectory tracking) than those
modules' quasi-static/frozen-parameter tools.

Milestone 46 (ETAS self-exciting point process, NONSTATIONARY_ROADMAP.md
package 5c) is likewise exported submodule-locally; independent of every
other dynamics submodule -- it is a discrete-event point-process
likelihood, not an ODE/SDE, and shares no code with ``rate_dependent.py``
or ``energy_balance.py`` beyond following the same fit-and-report pattern.
"""

from scoped_correspondence.dynamics.core import (
    CubicNormalForm,
    cusp_field,
    fixed_points,
    recovery_rate_at_equilibrium,
    recovery_rate_from_relaxation,
    sigmoid_response,
)
from scoped_correspondence.dynamics.contraction import (
    METRIC_EUCLIDEAN_1D,
    SOURCE as CONTRACTION_SOURCE,
    ContractionCertificate,
    contraction_rate_cusp,
    make_contraction_certificate,
    verify_contraction_bound,
)
from scoped_correspondence.dynamics.landau import (
    ISING_2D_BETA,
    MEAN_FIELD_BETA,
    ONSAGER_SIGMA_WARNING,
    SOURCE as LANDAU_SOURCE,
    ScalingExponentComparison,
    compare_scaling_exponents,
    mean_field_order_parameter,
    onsager_critical_ratio,
)
from scoped_correspondence.dynamics.gspt import (
    INDEPENDENCE_WARNING as GSPT_INDEPENDENCE_WARNING,
    SOURCE as GSPT_SOURCE,
    FoldPoint,
    critical_manifold_S,
    critical_manifold_S_prime,
    critical_manifold_fold_points,
    is_normally_hyperbolic,
    slow_manifold_distance_bound,
)
from scoped_correspondence.dynamics.floquet import (
    SOURCE as FLOQUET_SOURCE,
    SOURCE_OPTIONAL as FLOQUET_SOURCE_OPTIONAL,
    STABILITY_NEUTRAL,
    STABILITY_STABLE,
    STABILITY_UNSTABLE,
    classify_orbital_stability,
    classify_orbital_stability_matrix,
    floquet_multipliers,
    has_nontrivial_jordan_block,
    monodromy_from_trace_det,
)
from scoped_correspondence.dynamics.panarchy_cusp import (
    PANARCHY_V_ONSAGER_WARNING,
    SOURCE as PANARCHY_SOURCE,
    HysteresisSample,
    HysteresisSweepResult,
    control_path_no_fold_crossing,
    fold_thresholds,
    hysteresis_sweep,
)
from scoped_correspondence.dynamics.early_warning import (
    COUNTEREXAMPLE_WARNING as EARLY_WARNING_COUNTEREXAMPLE_WARNING,
    SOURCE as EARLY_WARNING_SOURCE,
    EarlyWarningReport,
    early_warning_at_cusp_branch,
    estimate_lambda_from_ar1,
    ou_autocorrelation,
    ou_variance,
)
from scoped_correspondence.dynamics.rate_dependent import (
    SOURCE as RATE_DEPENDENT_SOURCE,
    STABLE as RATE_DEPENDENT_STABLE,
    UNSTABLE as RATE_DEPENDENT_UNSTABLE,
    ChiDiagnosticResult,
    FrozenEquilibrium,
    TrackingResult,
    chi_diagnostic_for_cubic_example,
    classify_tracking,
    frozen_equilibria_shifted_pitchfork,
    integrate_trajectory,
    local_chi_diagnostic,
    rate_induced_tipping_cubic_example,
)
from scoped_correspondence.dynamics.energy_balance import (
    CO2_FORCING_COEFFICIENT,
    SOURCE as ENERGY_BALANCE_SOURCE,
    DATA_PROVENANCE_NOTE as ENERGY_BALANCE_DATA_PROVENANCE_NOTE,
    EnergyBalanceFitResult,
    EnergyBalanceParams,
    co2_radiative_forcing,
    fit_energy_balance_model,
    load_annual_co2,
)
from scoped_correspondence.dynamics.etas import (
    SOURCE as ETAS_SOURCE,
    DATA_PROVENANCE_NOTE as ETAS_DATA_PROVENANCE_NOTE,
    SCOPE_WARNING as ETAS_SCOPE_WARNING,
    ETASFitResult,
    ETASParams,
    compensator_g as etas_compensator_g,
    etas_branching_ratio,
    etas_neg_log_likelihood,
    fit_etas_model,
    load_catalog as etas_load_catalog,
    null_poisson_log_likelihood,
)

__all__ = [
    "CubicNormalForm",
    "cusp_field",
    "fixed_points",
    "recovery_rate_at_equilibrium",
    "recovery_rate_from_relaxation",
    "sigmoid_response",
    # M14 contraction analysis (submodule-local; package root __init__ untouched)
    "METRIC_EUCLIDEAN_1D",
    "CONTRACTION_SOURCE",
    "ContractionCertificate",
    "contraction_rate_cusp",
    "make_contraction_certificate",
    "verify_contraction_bound",
    # M29 Landau exponent comparison / self-falsification
    "MEAN_FIELD_BETA",
    "ISING_2D_BETA",
    "ONSAGER_SIGMA_WARNING",
    "LANDAU_SOURCE",
    "ScalingExponentComparison",
    "mean_field_order_parameter",
    "onsager_critical_ratio",
    "compare_scaling_exponents",
    # M33 Fenichel / GSPT (submodule-local; independent of M14/M29)
    "GSPT_SOURCE",
    "GSPT_INDEPENDENCE_WARNING",
    "FoldPoint",
    "critical_manifold_S",
    "critical_manifold_S_prime",
    "critical_manifold_fold_points",
    "is_normally_hyperbolic",
    "slow_manifold_distance_bound",
    # M34 Floquet multipliers (given 2×2 monodromy; not M14)
    "FLOQUET_SOURCE",
    "FLOQUET_SOURCE_OPTIONAL",
    "STABILITY_STABLE",
    "STABILITY_UNSTABLE",
    "STABILITY_NEUTRAL",
    "floquet_multipliers",
    "classify_orbital_stability",
    "classify_orbital_stability_matrix",
    "has_nontrivial_jordan_block",
    "monodromy_from_trace_det",
    # M35 Panarchy / Adaptive-Cycle as Cusp extension
    "PANARCHY_V_ONSAGER_WARNING",
    "PANARCHY_SOURCE",
    "HysteresisSample",
    "HysteresisSweepResult",
    "fold_thresholds",
    "hysteresis_sweep",
    "control_path_no_fold_crossing",
    # M36 early-warning signals / critical slowing down
    "EARLY_WARNING_COUNTEREXAMPLE_WARNING",
    "EARLY_WARNING_SOURCE",
    "EarlyWarningReport",
    "early_warning_at_cusp_branch",
    "estimate_lambda_from_ar1",
    "ou_autocorrelation",
    "ou_variance",
    # M42 rate-dependent tracking / rate-induced tipping (NONSTATIONARY_ROADMAP.md package 3)
    "RATE_DEPENDENT_SOURCE",
    "RATE_DEPENDENT_STABLE",
    "RATE_DEPENDENT_UNSTABLE",
    "FrozenEquilibrium",
    "TrackingResult",
    "classify_tracking",
    "frozen_equilibria_shifted_pitchfork",
    "integrate_trajectory",
    "rate_induced_tipping_cubic_example",
    "ChiDiagnosticResult",
    "chi_diagnostic_for_cubic_example",
    "local_chi_diagnostic",
    # M45 two-layer energy balance model (NONSTATIONARY_ROADMAP.md package 5b)
    "CO2_FORCING_COEFFICIENT",
    "ENERGY_BALANCE_SOURCE",
    "ENERGY_BALANCE_DATA_PROVENANCE_NOTE",
    "EnergyBalanceFitResult",
    "EnergyBalanceParams",
    "co2_radiative_forcing",
    "fit_energy_balance_model",
    "load_annual_co2",
    # M46 ETAS self-exciting point process (NONSTATIONARY_ROADMAP.md package 5c)
    "ETAS_SOURCE",
    "ETAS_DATA_PROVENANCE_NOTE",
    "ETAS_SCOPE_WARNING",
    "ETASFitResult",
    "ETASParams",
    "etas_compensator_g",
    "etas_branching_ratio",
    "etas_neg_log_likelihood",
    "fit_etas_model",
    "etas_load_catalog",
    "null_poisson_log_likelihood",
]
