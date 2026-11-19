# Class sweep: N-wrong-law (round 11, PLAN phase D)

Class status: not present in `dev/audit/config/bugclasses.json` (new this round; nearest P2).
Finding: D2-s2-02 (defrost `derate_from_duty`, sign of the duty term), reproduced on a planted copy.

## Enumerator
`python3 dev/audit/rounds/round11/D14/N-wrong-law/enumerate.py [pkg]`: AST walk listing every
clamped affine law `min(hi, max(lo, 1 +/- a*k))` (either nesting) and comparing its operator with
the law its function's docstring states (`1 - ... x K`). Seam rule seed: the finding's
`grep DEFROST_LOSS_MULTIPLIER|derate_from_duty`, widened to the whole package.

- Package at handoff/audit-r11-register (28b864af6d): seams=1, mismatch=0.
- Positive control: planted copy (`1.0 - duty*` to `1.0 + duty*` in defrost.py) gives mismatch=1 at
  `defrost.py:205 derate_from_duty`, re-finding D2-s2-02.
- Null control: clean fixture (one documented function, no clamp) gives seams=0.
- Perturbation: the one-line re-introduction above moves mismatch 0 to 1.

## Dispositions
| seam | disposition |
|---|---|
| `defrost.py:205 derate_from_duty` (finding site) | guarded: `tests/features.py:36341` pins `derate_from_duty(0.1)` to `1 - 0.1*DEFROST_LOSS_MULTIPLIER`, monotonicity at 36346; production carries the documented minus |

Instances beyond the finding: 0. Barrier: the features.py law check; the enumerator is a
candidate lint for operator drift on future clamped laws (limit: it reads only laws written
as `1 +/- a*k` inside a min/max clamp).
