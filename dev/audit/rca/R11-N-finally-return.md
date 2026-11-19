# RCA: a return inside finally discards the exception in flight

Seat: round-11 root-cause, class `N-finally-return` (instrument). Instances R9 1, R11 2, 3 in all, which meets the cross-round trigger. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

A `return`, `break` or `continue` whose scope leaves a `finally` block replaces whatever
was propagating, so an exception or a `CancelledError` raised in the `try` body vanishes and the
caller sees a normal return. Python accepts the shape; 3.14 only warns (PEP 765), and the warning
is emitted at compile time, which a cached `.pyc` or an unwarned interpreter never shows. Round 9
fixed the `tests/nightly_ha.py:_async_check_a4` seat (D7-s3-51) by moving the return out of the
finally. That fix was written for the site. Round 11's AST walk over the 1069 `.py` files found one
more live jump, `dev/archive/handoff/r9-f2-solver-4/mutation_proof.py:224`, which returns 2 from its
restore `finally` and so drops a `KeyboardInterrupt` or a runner failure raised by `sh()`.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`; round 9 has no JUDGE.json, so its instance is quoted from the finder record):

- `R9 D7-s3-51` (finder record, low): swallowed=2 of 2; syntax_warnings=1 arms returning normally / SyntaxWarnings; perturbation: swallowed=0, syntax_warnings=0.
- `R11 D14-s1-02` (weakened, low): worktree: seams_baseline=1 (coordinator.py:1943), runtime_swallowed_reintroduced=1, control 0; perturbation: RESULT seams 1 -> 2; runtime_swallowed 0 -> 1.

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 -W ignore dev/audit/rounds/round11/D14/s1/finally_escape.py` took 15 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-finally-return.json`) lists 1 seams. The ledger carries 1 of the seams as instances beyond the finding. Its enumerator is cited as `python3 dev/audit/rounds/round11/D14/finally_return_enum.py .`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (c) followed and did not produce the intended result

Round 9's fix protocol ran: failing test, fix, mutation proof. Its unit was the finding's
site, and with one instance no class trigger was met, so `defect-root-cause.md` asked for no
class search. Both were followed as written. The class reached a third instance because nothing
between rounds looks for the shape. The shape needs no runtime to find: the R11 finder's walk is
static and about 1 s. The process produced a correct site fix and left the class unguarded.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 3 instances over the 148 releases they accumulated in, 0.020 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.020 x 15660 s | 317 s/release |
| form | a static arm in the lint lane: compile every tracked `.py` outside `dev/archive/` with `-W error::SyntaxWarning` (PEP 765's own warning), or the finder's AST walk where the interpreter is older than 3.14 |
| catch share q | 1.0: the shape is syntactic; the compiler's own check sees every instance |
| expected benefit, q x cost | 317 s/release |
| arm time | 1.0 s (the finder's figure for the AST walk alone, about 1 s over 1069 files; the whole harness, with its runtime arms, took 15 s here, which would still pass at 245 s/release) |
| standing cost, arm x 16.3 PRs | 16 s/release |
| verdict | passes by 19.5x |

### Countermeasure (a class barrier, proposed; not built by this seat)

The arm refuses a jump that leaves a `finally`. It must show red on a planted copy of
`mutation_proof.py:224` and green on the tree with `dev/archive/` excluded; the archive is not
executed, so the one live seam there is a fix for the archive's owner, not a gate input. The
class's fix PR owns the arm and its demonstration.
