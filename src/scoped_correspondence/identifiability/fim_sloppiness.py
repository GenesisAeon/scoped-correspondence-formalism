"""Fisher-information sloppiness (Milestone 23).

Implements the local Fisher Information Matrix (FIM) geometry of
Transtrum, Machta & Sethna 2011 (DOI 10.1103/PhysRevE.83.036701) and the
sloppy / stiff eigendirection language of Raju, Machta & Sethna / Raju et al.
2018 (Phys. Rev. E 98, 052112):

    g = J^T J / sigma^2

where ``J`` is the model Jacobian ``df/dtheta`` (observations x parameters) and
``sigma > 0`` is the observation-noise scale. The eigenspectrum of ``g``
separates **stiff** directions (large eigenvalues: well-constrained) from
**sloppy** directions (small eigenvalues: poorly constrained). Anisotropy
``lambda_max / lambda_min`` quantifies the spread.

This module is intentionally restricted to **algebraic** Jacobian -> FIM
demos. It does **not**:
  - equate FIM / anisotropy to ``identifiability_jacobian_rank`` (SVD rank
    of ``J``) as the same formula -- rank tests local structural deficiency;
    FIM eigenvalues quantify metric anisotropy under noise;
  - implement general ODE forward models or automatic differentiation;
  - mutate ``identifiability/core.py``, ``profile_likelihood.py``,
    package-root ``scoped_correspondence/__init__.py``, ``FORMALISM.md``,
    or the layer docs.

Hand-derivable demo (module docstring contract)
-----------------------------------------------
Model
    f(theta1, theta2, t) = theta1 * exp(-theta2 * t)

at two observation times ``t in {t1, t2}``. Jacobian rows:

    df/dtheta1 = exp(-theta2 t)
    df/dtheta2 = -theta1 t exp(-theta2 t)

so

    J = [[ e^{-theta2 t1},  -theta1 t1 e^{-theta2 t1} ],
         [ e^{-theta2 t2},  -theta1 t2 e^{-theta2 t2} ]]

and ``g = JT J / sigma^2``.

Concrete run (theta1=1, theta2=1, t={1,2}, sigma=1) -- see verification JSON:
  lambda_max ~ 0.35527 (stiff), lambda_min ~ 0.006977 (sloppy),
  anisotropy lambda_max/lambda_min ~ 50.92.
Isotropic control: ``g = I`` -> anisotropy = 1.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence, Union

from scoped_correspondence.errors import ScopeViolationError

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "fim_sloppiness requires numpy; install the package dependencies"
    ) from exc

ArrayLike = Union[Sequence[Sequence[float]], "np.ndarray"]

SOURCE = (
    "Transtrum, Machta & Sethna 2011, Geometry of nonlinear least squares "
    "with applications to sloppy models and optimization, Phys. Rev. E 83, "
    "036701; DOI 10.1103/PhysRevE.83.036701. "
    "Raju, Marks, Kreutz, et al. / Raju et al. 2018, Information geometry "
    "and the renormalization group, Phys. Rev. E 98, 052112 "
    "(sloppy / stiff eigendirection language)."
)

PRL_DOI = "10.1103/PhysRevE.83.036701"
RAJU_DOI = "10.1103/PhysRevE.98.052112"

# Numerical floor for lambda_min when reporting anisotropy (PSD FIM).
_ANISO_FLOOR = 1e-30


def _as_2d(jacobian: ArrayLike, name: str = "jacobian") -> "np.ndarray":
    arr = np.asarray(jacobian, dtype=float)
    if arr.ndim != 2:
        raise ScopeViolationError(f"{name} must be 2-D; got shape {arr.shape}")
    if arr.size == 0 or arr.shape[0] < 1 or arr.shape[1] < 1:
        raise ScopeViolationError(f"{name} must be non-empty; got shape {arr.shape}")
    if not np.all(np.isfinite(arr)):
        raise ScopeViolationError(f"{name} entries must be finite")
    return arr


def fisher_information_matrix(
    jacobian: ArrayLike,
    sigma: float,
) -> "np.ndarray":
    """Return the Gaussian-noise Fisher information matrix ``g = J.T @ J / sigma^2``.

    Parameters
    ----------
    jacobian :
        Observation Jacobian ``J`` with shape ``(n_obs, n_params)``.
        Row ``i`` is ``df_i / dtheta``.
    sigma :
        Positive observation-noise standard deviation (homogeneous).

    Returns
    -------
    g : ndarray, shape ``(n_params, n_params)``
        Symmetric PSD Fisher information matrix.

    Notes
    -----
    Distinct from ``identifiability_jacobian_rank``: that API reports the
    numerical rank / SVD of ``J`` (local structural test). This API forms
    the metric ``g = JTJ/sigma^2`` and is used for stiff/sloppy anisotropy.

    Example (hand-derivable)
    ------------------------
    ``f(theta1,theta2,t)=theta1 exp(-theta2 t)`` at ``tin{1,2}``, ``theta=(1,1)``, ``sigma=1``::

        J = [[e^{-1}, -e^{-1}], [e^{-2}, -2 e^{-2}]]
        g = J.T @ J
        -> lambda_max~0.35527 (stiff), lambda_min~0.006977 (sloppy),
          anisotropy~50.92
    """
    J = _as_2d(jacobian, "jacobian")
    s = float(sigma)
    if not math.isfinite(s) or s <= 0.0:
        raise ScopeViolationError(f"sigma must be finite and > 0; got {sigma!r}")
    g = (J.T @ J) / (s * s)
    # Numerical symmetrization (floating-point).
    g = 0.5 * (g + g.T)
    return g


def eigenspectrum_report(g: ArrayLike) -> Dict[str, Any]:
    """Eigenspectrum of a Fisher information matrix (descending eigenvalues).

    Parameters
    ----------
    g :
        Square symmetric FIM (or any real symmetric PSD matrix).

    Returns
    -------
    dict with keys
        ``eigenvalues`` : list[float], descending
        ``eigenvectors`` : list[list[float]], columns as row-vectors matching
            ``eigenvalues`` order (each length ``n_params``)
        ``lambda_max``, ``lambda_min`` : float
        ``anisotropy`` : ``lambda_max / lambda_min`` (1.0 for isotropic / identity)
        ``stiff_direction`` : eigenvector for ``lambda_max``
        ``sloppy_direction`` : eigenvector for ``lambda_min``
        ``source`` : citation string

    Raises
    ------
    ScopeViolationError
        If ``g`` is not square, non-finite, or has non-positive ``lambda_min``
        (anisotropy undefined for singular / indefinite matrices under this
        scoped API).
    """
    G = _as_2d(g, "g")
    if G.shape[0] != G.shape[1]:
        raise ScopeViolationError(
            f"g must be square (n_paramsxn_params); got shape {G.shape}"
        )
    # Enforce symmetry for eigh
    Gs = 0.5 * (G + G.T)
    evals, evecs = np.linalg.eigh(Gs)
    # Descending
    order = np.argsort(evals)[::-1]
    evals = evals[order]
    evecs = evecs[:, order]

    if not np.all(np.isfinite(evals)):
        raise ScopeViolationError("eigenspectrum produced non-finite eigenvalues")

    lam_max = float(evals[0])
    lam_min = float(evals[-1])
    if lam_min <= 0.0 or lam_min < _ANISO_FLOOR:
        raise ScopeViolationError(
            f"lambda_min must be > 0 for anisotropy; got lambda_min={lam_min!r} "
            f"(singular / indefinite FIM out of scope for this helper)"
        )
    if lam_max < lam_min:
        # Should not occur after sort; guard anyway.
        raise ScopeViolationError("internal: lambda_max < lambda_min after sort")

    anisotropy = float(lam_max / lam_min)
    stiff = [float(x) for x in evecs[:, 0]]
    sloppy = [float(x) for x in evecs[:, -1]]
    evecs_list: List[List[float]] = [
        [float(x) for x in evecs[:, k]] for k in range(evecs.shape[1])
    ]

    return {
        "eigenvalues": [float(x) for x in evals],
        "eigenvectors": evecs_list,
        "lambda_max": lam_max,
        "lambda_min": lam_min,
        "anisotropy": anisotropy,
        "stiff_direction": stiff,
        "sloppy_direction": sloppy,
        "source": SOURCE,
        "doi_transtrum": PRL_DOI,
        "doi_raju": RAJU_DOI,
    }


def exponential_decay_jacobian(
    theta: Sequence[float],
    times: Sequence[float],
) -> "np.ndarray":
    """Analytic Jacobian of ``f=theta1 exp(-theta2 t)`` at the given times.

    Hand-derivable:
        df/dtheta1 = exp(-theta2 t),  df/dtheta2 = -theta1 t exp(-theta2 t).

    Scoped demo helper only -- not a general ODE sensitivity engine.
    """
    th = [float(x) for x in theta]
    if len(th) != 2:
        raise ScopeViolationError(
            f"exponential_decay_jacobian expects theta=(theta1,theta2); got len={len(th)}"
        )
    for v in th:
        if not math.isfinite(v):
            raise ScopeViolationError(f"theta components must be finite; got {v!r}")
    ts = [float(t) for t in times]
    if len(ts) < 1:
        raise ScopeViolationError("times must be non-empty")
    for t in ts:
        if not math.isfinite(t):
            raise ScopeViolationError(f"times must be finite; got {t!r}")

    th1, th2 = th[0], th[1]
    rows = []
    for t in ts:
        e = math.exp(-th2 * t)
        rows.append([e, -th1 * t * e])
    return np.asarray(rows, dtype=float)


__all__ = [
    "SOURCE",
    "PRL_DOI",
    "RAJU_DOI",
    "fisher_information_matrix",
    "eigenspectrum_report",
    "exponential_decay_jacobian",
]
