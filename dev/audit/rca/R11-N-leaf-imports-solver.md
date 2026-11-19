# RCA: a leaf module reaches the solver through one misplaced symbol

Seat: round-11 root-cause, class `N-leaf-imports-solver` (production). Instances R10 2, R11 7, 9 in all, which meets the per-round, cross-round trigger. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

A small module imports one name from a module that sits above it: `utc_elapsed_seconds`
through `accuracy.py`'s re-export, though `drift.py` owns it, or `HISTORY_LENGTH` from `accuracy.py`
rather than `const.py`. That one edge pulls `accuracy`, then `optimizer`, then scipy into the leaf's
import closure, about 400 ms in a fresh interpreter. Round 10 found two such edges (store and
legionella; the P1 and P4 moves took them out). Round 11 counts 13 layer violations, 7 of them on
an import that has a pure owner. The sweep adds 6 more leaves (`disinfection`, `price_model`,
`quiet_windows`, `setpoint_check` via `inputs`; `snapshots` via `store`; `sysid` via `accuracy`).
The repair is always a move, never a rewrite. Nothing says which modules are leaves, so an import
that is convenient at the time is never refused.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R10 ARCH3-s6-P4` (verified, low): legionella runtime closure 31 -> 22 modules, solver+scipy IN -> out, import 399 -> 182 ms (load1 5.5, thread_factor 1.000); private_reach 21 -> 17 over P1..P4; perturbation: --revert arm 0.0000 / NULL.
- `R10 D7-s4-8x-layering` (verified, low): static closure store 28 (optimizer IN) -> 21 out, snapshots 29 -> 22, setpoint_check 22 -> 13, quiet_windows 21 -> 11, silent_mode 20 -> 8; runtime store 29 -> 22, optimizer 1 -> 0 on all five; perturbation: P1 applied: store 29 -> 22, optimizer 1 -> 0.
- `R11 D7-s1-06` (verified, low): planted copy: layer_violations=13 at the issues cut (11 single-carrier); verifier 13 -> 6 with the seven imports moved; perturbation: 7.

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m7_prototypes.py --score --only note,avail,step,day,reader,layer,fdjac,entry,notice,curr --combined` took 23 s and exited 1. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.
 The harness did not complete on this tree, so its time is not a standing cost; the judge's reproduction above stands as the evidence.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-leaf-imports-solver.json`) lists 13 seams. The ledger carries 6 of the seams as instances beyond the finding. Its enumerator is cited as `python3 dev/audit/rounds/round11/D14/leaf_imports_solver.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (c) followed and did not produce the intended result

Round 10's fixes moved the two symbols judged that round, and the class's record kept no
barrier. `tests/closures.json` measures the import closures faithfully, but it measures them to
scope the gate, and a bigger closure is not an error to it. `tools/audit/archscore/` counts layer
violations, but only when a seat runs it. Both instruments were run and both saw the edges. Neither
refuses one. The fix moved the instances, and new edges of the same shape came in through other
re-exports.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 9 instances over the 148 releases they accumulated in, 0.061 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.061 x 15660 s | 952 s/release |
| form | a `tests/` arm holding a declared leaf list's static import closures free of `optimizer` and scipy |
| catch share q | 0.9: every judged and swept seam is an import edge on a module the list would name; a leaf missing from the list is the residue |
| expected benefit, q x cost | 857 s/release |
| arm time | 0.5 s (an estimate: a static closure walk reads the same AST `tests/closure.py` already reads; R10's measured static arms ran 0.1-0.54 s) |
| standing cost, arm x 16.3 PRs | 8.1 s/release |
| verdict | passes by 105.3x |

### Countermeasure (a class barrier, proposed; not built by this seat)

The arm reads a short declared list (the R10 and R11 leaves: store, notifier, debugger,
legionella, snapshots, setpoint_check, quiet_windows, silent_mode, disinfection, price_model, sysid,
comfort_learning, external_heat, power_guard, tariff) and refuses `optimizer` or `scipy` in any of
their closures. It must go red on this baseline, where 7 of 13 violations ride such edges, and
green after the moves. The fix PR owns the list and the arm. A list entry is a design statement,
so the list sits beside the arm with one line of reason per module.
