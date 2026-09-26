# Epistemischer Pufferpilot (H5) — K5, kontinuierlicher Fall

Antwort auf `SCF_ASSUMPTION_EVIDENCE_IMPLEMENTATION_PLAN.md` §4.5-4.6, K5.
Verbindet die H4-Unterscheidung zustandsweise vs. uniform zulässig
(`docs/epistemic_scope.md`) mit der bereits vorhandenen, unabhängig
geprüften Zwei-Puffer-CBF-QP-Maschinerie
(`viability/coupled_buffer_cbf_qp.py`: `BufferSpec`,
`sustained_safety_over_horizon`, `solve_cbf_qp`,
`compare_intervention_strategies`) — dieses Paket implementiert KEINE
neue Sicherheits-/Optimierungslogik, sondern verdrahtet die vorhandene
für genau die im Plan angegebene kontinuierliche K5-Faser.

## Aufbau

Faser: dieselben drei Zustände wie K4 (`F(2)={(0,2),(1,1),(2,0)}`,
`x1+x2=2`). Dynamik pro Puffer: `x_dot_i = -1 + u_i`, `0<=u_i<=1`,
gemeinsames Budget `u1+u2<=B`, Horizont `t∈[0,1]`. Sicherheit:
`x_i(t)>=0`.

Da Horizont und Drain hier exakt `1` sind, fällt die im Plan angegebene
notwendige-und-hinreichende Bedingung `min{x_i(0), x_i(0)+u_i-1}>=0`
exakt mit `sustained_safety_over_horizon`s bereits vorhandener,
geschlossener Formel `min(x_i(0), x_i(0)+(u_i-drain)*horizon)>=0`
zusammen — keine neue Formel, nur ein Spezialfall der bestehenden.

## Drei Informationsmodi

| Modus | Beobachtung vor dem Eingriff | Eingriff | Worst-Case-Kosten |
|---|---|---|---:|
| A — keine Beobachtung | keine | EIN gemeinsames `u` für die ganze Faser (`minimal_uniform_intervention`) | 2 |
| B — Vorzeichen von x1−x2 | `sign(x1-x2)` | zustandsabhängig anhand des Vorzeichens (`sign_based_policy`) | 1 |
| C — voller Zustand | `x` vollständig | zustandsweise CBF-QP-optimal (`solve_cbf_qp` pro Zustand) | 1 |

Modus A reproduziert exakt den Plan-Befund: eine gemeinsame Intervention
braucht `u1>=1` (wegen `(0,2)`) UND `u2>=1` (wegen `(2,0)`), also
`u1+u2>=2` — bei Budget 1 unmöglich, bei Budget 2 möglich. Modus B zeigt,
dass eine GROBE Beobachtung (nur das Vorzeichen, nicht der volle Zustand)
bereits ausreicht, um die Worst-Case-Kosten auf 1 zu senken — dieselbe
Worst-Case-Kostenzahl wie bei vollständiger Zustandsbeobachtung (Modus
C). Das ist eine Beobachtung für DIESES Beispiel, keine allgemeine
Aussage, dass Vorzeichen-Information immer gleichwertig zu voller
Zustandsbeobachtung ist.

`minimal_uniform_intervention` berechnet die minimale gemeinsame
Intervention in geschlossener Form (pro Pufferindex das Maximum der
`cbf_lower_bound`-Anforderung über alle Faserzustände hinweg, nicht per
Suche) und wird in `verify_epistemic_buffer_pilot.py` zusätzlich
numerisch gegen `sustained_safety_over_horizon` (Tolerenz `1e-9`)
gegengeprüft — beide müssen exakt übereinstimmen.

## Grenzen

- Gilt nur für diese eine deklarierte Faser mit exakt diesen drei
  Zuständen, diesem Drain, Horizont und diesen Box-Grenzen — keine
  Verallgemeinerung auf andere Fasern oder Horizonte ohne erneute
  Herleitung.
- `solve_cbf_qp` ist auf genau 2 Puffer beschränkt (bestehende
  Einschränkung aus `viability/coupled_buffer_cbf_qp.py`).
- Die numerische Toleranz `1e-9` in `sustained_safety_over_horizon` ist
  eine numerische Vergleichsgrenze, kein exaktes Ergebnis; die
  geschlossene Herleitung oben ist exakt.
