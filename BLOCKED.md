# BLOCKED: r11-outside-honest-starts-runs-p3 (outside pull request 3529 by Bankaifan)

Question: tvofi, at which default start price (currency per compressor start, the options field's 0 to 10 range) should a clamped install with no configured start price plan? Step 2 builds only at the value you pick (owner ruling Q2, 2026-11-15). The smallest measured value that brings both failing rows back to their pre-parent start count is 0.1.

Step 1 (measure before building) is done. Nothing is built: the only change on this ref is a new `defaults` mode in `dev/audit/harnesses/r11_honest_starts_runs.py`, at commit 139583edbdb7c11c6ec15f2fd00b618cea8c795d (harness sha1 953ac33d796b05e7c4435aa35c6728fb9908d3e8). origin/main tip b425502da8d15c43f9494412e686a3d852b74358, 2026-11-16T23:00Z.

## What was measured, and the rule
Command: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_honest_starts_runs.py defaults`.
- **Head**: b425502da8 (origin/main, which contains 38c254f3fb).
- **Pre-parent**: ef6363d5f2 (= 2c84a85c8c^1, main just before pull request 3602 merged), running the same harness file.
- **The rule a candidate is applied by**: the default replaces a configured cycling cost of 0 on a clamped install (`clamp_planned_levels` on), and changes nothing else.
- **Columns**: starts = off-to-on edges of the combined draw (0.1 kW run rule). energy is in kWh. pcost is the optimizer's `predicted_cost`; the objective is not comparable across prices because it includes the start price. room = lowest room temperature, in °C.

Reproduction first, with `grid` mode on the clamped, unpriced row (p_min 1.1, loss 0.4):
- Pre-parent: 2 edges, objective 7.8698.
- Head: 5 edges, objective 7.6826.
- This matches the parent's figure.

## Failing case: clamped install at configured price 0, head
| default | grid row: starts / energy / pcost / room | cycling_cost fixture | everything_on fixture |
|---|---|---|---|
| 0 (today) | 5 / 2.93 / 1.4128 / 20.19 | 7 / 42.04 / 32.0354 / 16.87 | 5 / 69.57 / 63.2857 / 17.91 |
| 0.05 | 3 / 2.75 / 1.3468 / 20.22 | 7 / 42.04 / 32.0354 / 16.87 | 4 / 69.94 / 63.4567 / 17.97 |
| 0.1 | 2 / 2.75 / 1.3980 / 20.22 | 7 / 42.04 / 32.0354 / 16.87 | 4 / 69.94 / 63.4567 / 17.97 |
| 0.25 | 2 / 2.75 / 1.3980 / 20.22 | 7 / 42.04 / 32.0354 / 16.87 | 4 / 69.94 / 63.4567 / 17.97 |
| 0.5 | 1 / 2.28 / 1.2824 / 19.96 | 5 / 42.29 / 32.5779 / 17.03 | 4 / 69.94 / 63.4567 / 17.97 |
| 1.0 | 1 / 2.28 / 1.2824 / 19.96 | 4 / 42.29 / 33.3579 / 17.09 | 4 / 69.94 / 63.4567 / 17.97 |
| 1.5 | 1 / 2.28 / 1.2824 / 19.96 | 4 / 42.29 / 33.3579 / 17.09 | 4 / 69.94 / 63.4567 / 17.97 |
| 2.5 | 1 / 2.28 / 1.2824 / 19.96 | 3 / 42.29 / 35.6129 / 17.22 | 3 / 69.45 / 64.5234 / 17.94 |
| 5.0 | 1 / 2.28 / 1.2824 / 19.96 | 2 / 42.29 / 39.3429 / 17.42 | 2 / 67.32 / 65.8530 / 17.80 |
| 10.0 | 1 / 2.28 / 1.2824 / 19.96 | 2 / 42.29 / 39.3429 / 17.42 | 1 / 62.49 / 66.9418 / 17.53 |

The same rows on the pre-parent tree, at default 0:
- grid: 2 / 2.32 / 1.1560 / 20.13
- cycling_cost: 7 / 42.04 / 32.0354 / 16.87
- everything_on: 4 / 75.05 / 69.3233 / 18.47

The full pre-parent ladder is in the harness output of the same command run at ef6363d5f2.

Reading of the table:
- **Two rows regressed.** At default 0, the parent's change raised the clamped, unpriced start count on grid (2 to 5) and on everything_on (4 to 5). It did not move cycling_cost (7 to 7).
- **What 0.1 does.** It is the smallest ladder value that restores both regressed rows to their pre-parent count: grid 2, everything_on 4.
  - At that value grid's `predicted_cost` is 1.3980, below the 1.4128 at 0.
  - everything_on's is 63.4567, above the 63.2857 at 0.
- **What 0.05 does.** It restores everything_on (4) but leaves grid at 3.
- **What 0.5 and above do.** On grid they plan 1 start, with the lowest room falling to 19.96 (20.22 at 0.1).
- **cycling_cost** first moves at 0.5 (7 to 5 starts).

## Null controls (head; each pair solved with no default and with default 10.0)
| install | starts / energy / pcost / room | array-equal |
|---|---|---|
| grid, priced clamped (0.25) | 2 / 2.75 / 1.3980 / 20.22 | True |
| grid, unpriced unclamped | 3 / 2.80 / 1.4106 / 20.14 | True |
| cycling_cost, priced clamped (1.5) | 4 / 42.29 / 33.3579 / 17.09 | True |
| cycling_cost, unpriced unclamped | 7 / 41.47 / 31.0590 / 16.90 | True |
| everything_on, priced clamped (0.5) | 4 / 69.94 / 63.4567 / 17.97 | True |
| everything_on, unpriced unclamped | 4 / 68.29 / 61.7167 / 17.82 | True |

The harness prints `null pairs that differ 0` and would exit 1 on any difference.

What these nulls show:
- Under the measured rule they hold by construction: the effective price is identical in each pair. So they show that the rule reaches no priced install and no unclamped install, and that the solve is deterministic.
- They do not test a different rule. A max(configured, default) rule would move priced installs set below the default. Two examples, read off the ladder because a clamped install at configured d solves exactly as configured 0 at default d:
  - grid priced at 0.25 would go from 2 starts to 1 under any default of 0.5 or more.
  - everything_on priced at 0.5 would go from 4 to 3 under a default of 2.5.

## Owed in step 2 (stated now so the pick can weigh it)
Where the default lives decides which installs it reaches:
- **The options field default** (`DEFAULT_CYCLING_COST` in `const.py`, used by the `config_flow.py` field and `entry_config.py`):
  - It reaches only entries whose options lack the key.
  - An entry whose options already hold 0 cannot be told from one that chose 0, so a migration would be owed to reach existing installs. That migration would overwrite a deliberate 0.
  - The default would also reach unclamped installs.
- **A substitution at solve time** (the measured rule, where both the configured cost and the clamp flag are known):
  - Candidate homes: the optimizer config's `from_config` beside `levels_clamped(cfg)`, or the coordinator's `_effective_cycling_cost`.
  - It reaches every clamped install at 0, existing ones included, with no migration.
  - A user who wants a true zero on a clamped install could no longer have one, because the field's minimum is 0. That makes it a user-visible change, which goes first in the release notes.

Carry: R11-OUTSIDE-HONEST-STARTS-RUNS-P3 (pending owner ruling on the value, Q2 step 2)
