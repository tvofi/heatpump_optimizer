# RCA: a physical law coded with the wrong operator

Seat: round-11 root-cause, class `N-wrong-law` (production). Instances R11 1, 1 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`P2`) as one (`fold_ledger.py` `_group_counts`): `N-duplicated-rule`, `N-entry-data-placement`, `N-inverted-aggregate`, `N-mode-coupled-write`, `N-wrong-law`, 8 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

`defrost.derate_from_duty` returns `min(1, max(0.55, 1 + duty*1.5))`. The module documents
`1 - duty*DEFROST_LOSS_MULTIPLIER`. The added term is clamped back to 1.0, so every measured duty in
(0, 0.30] yields no derate, and a trusted 20 % defrost duty leaves the frost-band COP unchanged
(1.0 against a documented 0.70; 60 of 61 grid points mismatch). The clamp hides the sign error:
the output is always in range.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D2-s2-02` (verified, high): planted copy: duty_law_mismatch=60 of 61 grid points; at duty 0.2 the code gives 1.0 vs documented 0.7; perturbation: duty_law_mismatch 60 -> 0; frost_cop_ratio 1.0 -> 0.70 on winter_mild (73 frost steps) and shoulder (41).

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D2/s2/m2_cop_laws.py` took 1.6 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-wrong-law.json`) lists 0 seams. The ledger carries 0 of the seams as instances beyond the finding. Its enumerator is cited as `python3 dev/audit/rounds/round11/D14/N-wrong-law/enumerate.py custom_components/heatpump_optimizer`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (c) followed and did not produce the intended result

D2's derate step asks that every derate lie in [0, 1], bounded and continuous at the band
edges (`dev/governance/dimensions/D2.md:30-31`), and round 10's D2 s2 seat ran it. A derate stuck at
1.0 passes every one of those checks. The law is only visible when the code is
compared with its own docstring at grid points, which is what round 11's `m2_cop_laws.py` does.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 1 instances over the 148 releases they accumulated in, 0.007 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.007 x 15660 s | 106 s/release |
| form | a class barrier for wrong-operator laws |
| catch share q | 0.0: the sweep found 0 further seams; a sign error is not a syntactic shape, and only a per-law conformance test sees it |
| expected benefit, q x cost | 0 s/release |
| arm time | 1.6 s (`dev/audit/rounds/round11/D2/s2/m2_cop_laws.py`, re-timed by this seat) |
| standing cost, arm x 16.3 PRs | 26 s/release |
| verdict | fails: the form catches nothing measured |

### Decision not to build a class barrier

Decision: no class barrier. The fix subtracts the duty term and pins the documented law at
grid points in its regression test. `m2_cop_laws.py` is the right instrument for the family of
laws, and keeping it per round (D2) is cheaper than a gate while it has found one instance. Re-open
if a second law fails it.
