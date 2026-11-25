# RCA: a value declared or written off its own step grid

Seat: round-11 root-cause, class `N-step-grid` (production). Instances R9 1, R11 6, 7 in all, which meets the per-round, cross-round trigger. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

A number selector declares `min`, `step` and a default (or an example, or a widened `max`)
as independent literals, and nothing ties them. When `(value - min) % step != 0`, Home Assistant's
frontend flags a legal value as invalid and a spinner click lands off-grid. Round 9 (D4-s2-05)
found 8 config-flow defaults off the grid. Round 11 found the same declaration fault in 6 of 47
`services.yaml` selectors (`set_thermal_parameters`) and in `config_flow._widen_to_fit`, which widens
a range without re-snapping it, and four card `<input type=number>` fields. D16-s1-01 is the
write-side twin: `coordinator._command_frequency` sends FrequencyMap's decile midpoints (23.5,
37.5, 51.5, 86.5 Hz) to a number entity whose step is 1 Hz, in 50 of 50 heating rows.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`; round 9 has no JUDGE.json, so its instance is quoted from the finder record):

- `R9 D4-s2-05` (finder record, low): 8 defaults + 4 derived count; perturbation: 0 and 0.
- `R11 D14-s1-01` (verified, low): worktree: seams_total=40 (options widen 28 + services 12); --perturb-svc -> services 0, total 28; perturbation: seams_services 12 -> 0; seams_widen 28 -> 0; seams_options 0 -> 2 under --perturb-min (up).
- `R11 D16-s1-01` (weakened, low): worktree: clause_grid=50 rig x state rows; null 0; --perturb freq_grid -> 0; perturbation: --perturb freq_grid: FrequencyMap.recommend's answer rounded to the entity's 1 Hz step (the one-line production edit: quantise the target on the entity step before set_value).

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s1/step_grid.py` took 3.0 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-step-grid.json`) lists 12 seams, and 8 more sites it dispositioned as guarded or not applicable. The ledger carries 4 of the seams as instances beyond the finding. Its enumerator is cited as `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep/sweep_step_grid.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (c) followed and did not produce the intended result

Round 9's D4 seat found the class on the config flow, and its fix was scoped to
`config_flow._number` and the `RANGE_*` constants. The other declaration surfaces were not in that
fix's unit: `services.yaml`, the widen helper and the card's own inputs. The fix protocol does not
ask a fixer to sweep sibling surfaces of a single finding. Round 10's D14 carried a detector for
the class, `dev/audit/rounds/round10/D14/s1/stepgrid_seams.py`. It scans only the NumberSelector
fields of `config_flow._OPTION_FIELDS` and recorded `off_grid=0`
(`dev/audit/rounds/round10/D14/s1/REPORT.md:27`). The services file, the widen helper and the card
were not its surface. The process was followed both times, and its unit was one surface of a
three-surface class. The write side was outside every brief until D16 first ran
in this round (`dev/governance/dimensions/D16.md`, first added 2026-11-15), which is (a) for that
one instance.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 7 instances over the 148 releases they accumulated in, 0.047 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.047 x 15660 s | 741 s/release |
| form | a static `tests/` arm over every box-mode selector in `config_flow.py` and `services.yaml` (min, max, default and example on `min + k*step`), plus one quantise-to-entity-step helper on the write path |
| catch share q | 0.8: the arm sees the config-flow and services.yaml surfaces, the widen helper among them; the 4 card inputs need a browser and stay an audit probe, and the write side is closed by the helper, not the arm |
| expected benefit, q x cost | 593 s/release |
| arm time | 3.0 s (`dev/audit/rounds/round11/D14/s1/step_grid.py`, the finder harness, re-timed by this seat) |
| standing cost, arm x 16.3 PRs | 49 s/release |
| verdict | passes by 12.1x |

### Countermeasure (a class barrier, proposed; not built by this seat)

The arm reuses `D14/s1/step_grid.py`'s rule and refuses an off-grid declaration. It must show red
on this baseline (12 services seams, 28 widen seams) and green after the fix. The write side gets
no detector of its own: one helper quantises every number write onto the entity's step inside its
range, and the frequency write routes through it. The fix PR owns both.
