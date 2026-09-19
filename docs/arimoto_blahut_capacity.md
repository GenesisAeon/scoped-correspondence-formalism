# Arimoto–Blahut Channel Capacity (Milestone 25)

## Scope

Finite discrete memoryless channels (DMCs). Given a row-stochastic channel
matrix \(Q(y|x)\), compute the Shannon capacity

\[
C(Q)=\max_{r\in\Delta^{|X|-1}} I(r;Q)
\]

and a capacity-achieving input \(r^\*\) by the Arimoto–Blahut alternating
iteration (bits when \(\log=\log_2\)).

**Not in scope**

- Rate-distortion BA (Blahut 1972 also treats \(R(D)\); this module does not).
- Continuous Shannon–Hartley \(\,B\log_2(1+\mathrm{SNR})\,\) — that remains
  `observation.core.channel_capacity`. M25 is an **additional** DMC model,
  not a replacement.
- Edits to `observation/core.py` or package-root `__init__.py`.

## Sources

- Arimoto, S. (1972). An algorithm for computing the capacity of arbitrary
  discrete memoryless channels. *IEEE Trans. Inf. Theory* **18**(1):14–20.
  DOI [10.1109/TIT.1972.1054753](https://doi.org/10.1109/TIT.1972.1054753).
- Blahut, R. E. (1972). Computation of channel capacity and rate-distortion
  functions. *IEEE Trans. Inf. Theory* **18**(4):460–473.
  DOI [10.1109/TIT.1972.1054855](https://doi.org/10.1109/TIT.1972.1054855).

## API

```python
from scoped_correspondence.observation import (
    blahut_arimoto_capacity,
    z_channel,
    bsc_channel,
)

res = blahut_arimoto_capacity(z_channel(0.5))
# res.capacity ≈ log2(1.25) ≈ 0.321928
# res.r_star  ≈ (0.6, 0.4)
# res.iterations — BA steps to tolerance
```

`ScopeViolationError` is raised if `Q` has negatives or is not row-stochastic.

## Hand-checkable examples

| Channel | Analytic \(C\) | \(r^\*\) | Notes |
|---------|----------------|---------|-------|
| Z, \(\varepsilon=1/2\) | \(\log_2(5/4)=\log_2(1.25)\) | \((0.6,0.4)\) | Closed form from \(\beta=(1-\varepsilon)\varepsilon^{\varepsilon/(1-\varepsilon)}\) and critical point of \(h(\alpha/2)-\alpha\) |
| BSC, \(p=0.1\) | \(1-H_2(0.1)\) | uniform | From uniform start, BA is already at the fixed point |

Verification: `verification/verify_arimoto_blahut_capacity.py`.
