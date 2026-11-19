# RCA: a failure caught and recorded below WARNING, or not at all

Seat: round-11 root-cause, class `N-swallowed-failure` (instrument). Instances R11 25, 25 in all, which meets the per-round, cross-round trigger. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

A broad `except Exception` around a persist, load, capture or diagnosis body records the
failure at DEBUG, or records nothing, and returns. A persistent failure is then invisible at the
default log level. D1-s3-05: 10 of the 10 persist handlers the lifecycle reaches stay silent at
WARNING with the save forced to fail on every pass. D1-s3-07: 7 of 12 reached broad handlers leave
no record at any level. The sweep classified the 257 handlers of `tools/audit/enumerate.py
d1-excepts`, and 47 are seams (24 the judged sites, 23 beyond). The handlers were written to keep a
cycle alive. Logging at WARNING was avoided because that floods (round 10's `N-log-flood`). A
once-per-transition helper (`log_latch.log_held`) now exists, and none of these sites uses it.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D1-s3-05` (weakened, low): planted copy: persist_silent_at_warning=10 of 10 reached handlers; perturb 10 -> 9; perturbation: 9.
- `R11 D1-s3-07` (verified, low): planted copy: silent_broad_no_record=7 of 12 reached; perturb 7 -> 6; perturbation: 6.

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s3/persist_family.py` took 44 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-swallowed-failure.json`) lists 47 seams, and 159 more sites it dispositioned as guarded or not applicable. The ledger carries 23 of the seams as instances beyond the finding. Its enumerator is cited as `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep/swallowed_sweep.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (c) followed and did not produce the intended result

D1's guards step asks of every handler of `enumerate.py d1-excepts` whether it logs once and
hides no bug (`dev/governance/dimensions/D1.md:52-53`), and round 10's D1 s3 seat ran it. Round 10 ran that step
and its countermeasure aimed at the opposite direction, the WARNING that repeats every cycle. The
fix for a flood is to log less, and a handler that logs nothing passes every flood check. The step
was followed, and its round-10 instrument only counted records that were too many, never too few.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 25 instances over the 148 releases they accumulated in, 0.169 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.169 x 15660 s | 2645 s/release |
| form | a static `tests/` arm over `tools/audit/enumerate.py d1-excepts` refusing a non-re-raising handler whose highest record is below WARNING and does not go through `log_held`, outside a reasoned list |
| catch share q | 0.9: the enumerator already lists every handler (257); the residue is a handler that logs through an indirection the AST rule does not follow |
| expected benefit, q x cost | 2381 s/release |
| arm time | 0.5 s (an estimate: the enumerator is an AST pass of the size R10 measured at 0.36 s for N-log-flood's sites) |
| standing cost, arm x 16.3 PRs | 8.1 s/release |
| verdict | passes by 292.5x |

### Countermeasure (a class barrier, proposed; not built by this seat)

This shares N-log-flood's proposed helper. A handler logs a held warning once per
transition through `log_held`, so the arm and the flood arm can both be green. It must show red on
this baseline (47 seams) and green after the fix, with the reasoned list (setup probes, optional
imports, per-event writes) carried beside it. The fix PR owns the arm and the list.
