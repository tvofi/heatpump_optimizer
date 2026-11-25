# RCA: an actuator left on the optimizer's last write

Seat: round-11 root-cause, class `N-unreleased-hold` (production). Instances R11 5, 5 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`N-no-expiry`) as one (`fold_ledger.py` `_group_counts`): `N-stale-step-actuation`, `N-unbounded-retention`, `N-uncleared-issue`, `N-unreleased-hold`, 16 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

`off_restore` restores an entity only if that entity was registered before the optimizer
wrote it. Registration is opt-in, one call per write site. The power switch, compressor frequency,
mixing-valve target and circulation pump were never registered, so after Off, unload or removal
they keep the optimizer's value (D16-s3-02). The other exits have no owner either. The stale-plan
branch of `_apply_action` writes nothing, so a pump switched off by an idle step stays off past the
plan's end (D16-s1-04, 5 of 5 rigs). The arbiter does not write the baseline row on the change into
Off (D16-s3-01). A restore that fails is never retried (D16-s3-04). Each write site was added on its
own, and no rule says that a write must have a release.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D16-s1-04` (verified, high): worktree: baseline_switch_off=5 rigs; perturb -> 0; perturbation: --perturb stale_on: the stale branch of _apply_action also writes the supply on through _write_supply.
- `R11 D16-s3-01` (verified, high): worktree: on Off select.pump_mode stays at the optimizer's write (1); during disinfection Off leaves number.dhw_set at 60 (1); unrestored_off=5 entities; perturbation: unrestored_off__select.pump_mode=0, unrestored_off_modbus__number.dhw_set=0.
- `R11 D16-s3-02` (verified, high): worktree: 4 actuators unregistered on off, unload and remove each (supply switch, frequency, valve, circulation); perturb -> 0; perturbation: unrestored_off_unregistered=0, unrestored_unload_unregistered=0, unrestored_remove_unregistered=0.
- `R11 D16-s3-04` (verified, medium): worktree: writes_again_off_restore_failed_while_off=0; perturb (retry) -> 1; perturbation: writes_again_off_restore_failed_while_off=1 (final 45), writes_again_off_restore_neutral_failed_while_off=1 (final 0).

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D16/s1/cells.py --no-gates` took 8.8 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-unreleased-hold.json`) lists 8 seams. The ledger carries 1 of the seams as instances beyond the finding. Its enumerator is cited as `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep/enum_unreleased_hold.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (a) the process did not exist

Before D16 (first added 2026-11-15), no brief graded what each written entity holds on each
exit. D1's lifecycle steps drive setup, unload and restart for the coordinator's own state, not for
the devices it writes. The class was found by D16's first run, at high severity on 3 of 4 judged
instances.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 5 instances over the 148 releases they accumulated in, 0.034 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.034 x 15660 s | 529 s/release |
| form | one write path that arms `off_restore` before every actuator write, plus a `tests/` arm over the write-site x exit matrix (`D16/s3/m6_restore.py`) |
| catch share q | 0.9: routing every write through the arming path covers new sites by construction; the matrix arm checks the exits; the residue is an exit the matrix does not list |
| expected benefit, q x cost | 476 s/release |
| arm time | 8.8 s (`dev/audit/rounds/round11/D16/s1/cells.py --no-gates`, which drives the stale-plan exit, re-timed by this seat; `m6_restore.py` was not timed, so the matrix arm's cost is the fix PR's to measure) |
| standing cost, arm x 16.3 PRs | 143 s/release |
| verdict | passes by 3.3x |

### Countermeasure (a class barrier, proposed; not built by this seat)

The write path makes registration structural, so a new write site cannot skip it. The
matrix arm must show the 5 unrestored entities on this baseline, 0 after the fix, and 0 on the
null arm. A bounded retry of a failed restore from the arbiter's one-minute tick closes D16-s3-04.
The fix PR owns all three. This class carries three of the round's high-severity instances. Its
cost test passes by the narrowest margin of the proposed barriers, and the 4.35 h cost(defect)
understates a pump left off or on a held set-point in the field.
