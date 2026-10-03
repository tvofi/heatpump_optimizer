R9-F10.12: the mutation lanes outgrow their timeouts. Part of #201.

_Requested by **tvofi**_

`mutation-nightly` and `mutation-ledger` both run `tests/mutation_table.py --scope full --max 40 --jobs 3` under a 330-minute job timeout. The cost of one mutant is set by its drivers, mainly `tests/features.py`, and that cost keeps growing. Re-measured from the job logs of the last 12 scheduled runs (2026-09-22 to 2026-10-03):

- The nightly peaked at 286 job-minutes on 2026-10-02, 87% of the timeout. That night's mutant phase alone took 243 minutes.
- The last five nightly jobs averaged 186 minutes.
- The `tests/features.py` baseline rose from 213 s to 701 s on the nightly, and reached 833 s in the 2026-10-03 ledger run.

This PR has two arms.

**(A) A wall-clock budget: `--budget-minutes M`.**
- `drive_pool` starts a mutant only if it will still end inside the deadline. The estimate is every one of its drivers at measured cost, which is what it costs if it survives, plus the EXCLUSIVE runs still owed by started mutants that no driver has killed yet.
- That reservation is released when a mutant is killed.
- The first mutant that does not fit closes the pool. It and every mutant after it become `SKIP-BUDGET` and are printed as `NOT RUN`. What did run is therefore a prefix of the shuffled pool, not a sample biased toward cheap drivers.
- The cut falls on an anchor boundary (round 1). A mutant is admitted together with every queued site of its anchor, or not at all, because a disposition covers the whole anchor and a split anchor can never be pinned. `drain_survivors` also leaves out any anchor that holds a `SKIP-BUDGET` site.
- The survivor cap is computed over the evaluated mutants. `PASSED` names the run as partial whenever a timeout or the budget left mutants unscored: `(partial: N evaluated, T timed out, K not started for the budget)`.
- A run that evaluated nothing because its mutants timed out or went unstarted is **refused**, and the reason counts each cause: `MUTATION TABLE REFUSED -- nothing was measured: T mutant(s) timed out, K not started for --budget-minutes`.
- Under `--drain`, a site that was never started is neither pinned nor listed in `survivors.txt`, and neither is its anchor's twin. Both are left for a later night.
- Cost estimates are updated with the most expensive run seen. A lazy or deferred driver is estimated at three times its cost until it settles (the run, its baseline and its null control).
- `--record` refuses a budget, because a cap is recorded from a whole pool.
- Callers: `mutation-nightly` and `mutation-ledger` pass 270 of their 330 minutes. The PR pin step passes 35 of its 60 minutes, but only when the base program has the flag (`grep -q -- '--budget-minutes'`). Until this merges, that base is main's old copy, so the pin step stays as it is today.

**(B) A driver timeout is not a kill. This was a defect.**
- Before this change, `run_script` returned `TIMEOUT_RC` and `failing_count` counted the timeout as one failing check. A mutant that only *slowed* a driver past the fixed 1200 s was therefore judged killed, and `--drain` pushed it to main as a `killed_by` pin.
- Now a timed-out run carries `timed_out` and names no failing check. `LazyBaselines.killed` returns `None` for it.
- In `drive_pool`, `None` is inconclusive. A mutant whose driver timed out becomes `SKIP-TIMED-OUT in <driver>`, unless a driver already running on it kills it. That is never `killed`, never `LIVES`, and never pinned. It stays in the drain's `survivors.txt` for a human.
- A mutant's sweep ends at its first timed-out driver (round 1), including its EXCLUSIVE runs, so a hang costs one timeout rather than one per driver. This is sound because the verdict is already inconclusive. The price is that a kill by a driver that never ran is not looked for.
- Each driver's timeout is now `driver_timeout(--timeout, own seconds) = max(floor, ceil(3 x its measured seconds))`. The recorded seconds are used until its baseline here measures it, and the same rule applies to baseline, null and mutant runs.
- A null control whose driver timed out still refuses the run (`timed out under <driver>`).

**A deliberate deviation from the roster brief.** The brief says "one that never returns still is [a kill]". The orchestrator's later direction for this seat says to make a timeout INCONCLUSIVE, never a kill, and this PR follows that direction. From outside, a hang and a slow driver look the same, so a hang is `SKIP-TIMED-OUT`: it is not scored, it is named in the table, and it is left for a human verdict.

**How this composes with #1878.**
- #1878 at `5d6edffec707f9f16485cff9f3773e2c47874dcf` adds `tests/harness_headers.py` to `EXCLUSIVE` (`EXCLUSIVE = ("tests/harness_headers.py", "tests/stress.py")`) and adds a `LEASED` set.
- `git merge-tree --write-tree` of this head with 5d6edffe returns rc 0 (tree 5f13fdf0). On that merged tree, `tests/entities.py` gives `ALL 2118 ENTITY CHECKS PASSED`. The reviewer independently measured 2115 against round 0's head.
- The budget accounts for the move without further change. harness_headers' runs move into the serial EXCLUSIVE phase, and its cost joins every undecided mutant's reservation.
- Replaying the 2026-10-02 night with that `EXCLUSIVE`:
  - unbudgeted: the pool takes 306-309 model-minutes;
  - under that night's 226-minute pool deadline: 204-208 model-minutes, with 25-31 of 40 evaluated, against 26-33 without the move.
- On 2026-10-03, the move costs 8-9 model-minutes and nothing is cut: 39/39 evaluated.
- The move also makes the baseline serial for one more driver (201-273 s on CI). The budget absorbs that, because the deadline runs from process start.

**Measured effect on nightly wall time.** The instrument is a replay of each logged night through the head's real `drive_pool`. Each driver run costs that driver's logged baseline seconds, and the kills are the logged ones. The model's null control is its own unbudgeted run against what CI actually took. It is pessimistic on every night checked:

| night | actual mutant phase | model, unbudgeted |
|---|---|---|
| 10-02 | 243 min | 268-275 min |
| 10-03 | 116 min | 140-146 min |
| 10-01 | 110 min | 150 min |
| 09-30 | 139 min | 166 min |

With `--budget-minutes 270`, the pool deadline is 270 minus the startup and baseline phase.

| night, cost multiple | model pool, budget | evaluated | model pool, unbudgeted |
|---|---|---|---|
| 10-02, 1x | 186-203 min | 26-33 of 40 | 268-275 min |
| 10-03, 1x | 140-146 min | 39 of 39 | same, nothing cut |
| 10-02, 1.5x | 173-186 min | 16-19 of 40 | 398-409 min |
| 10-02, 2x | 130-154 min | 10-12 of 40 | 528-539 min |

- At 1.5x and 2x the unbudgeted runs would hit the 330-minute job timeout.
- So the 10-02 night's job would have ended at about 247 minutes or less, against the 286 it took, on a night without hangs.
- **The real worst case** (corrected in round 1). Admission budgets each driver at its measured seconds, but a run may last up to `max(1200 s, 3 x measured)`. So each mutant that hangs while it is running past the deadline adds up to one such timeout over its estimate.
  - In the shared phase those overruns run in parallel, one per worker.
  - In the serial EXCLUSIVE phase they add up, one per hanging mutant.
  - The 60 minutes left above 270 cover a single hang at today's largest timeouts: features.py at 3 x 833 s, about 42 min, or stress.py at max(1200, 3 x 478) s, about 24 min.
  - Several hangs in the EXCLUSIVE phase, or one at a driver more than about 1.4x slower than today, can still reach the job timeout. Before round 1, a hang ran every remaining driver to its limit (the review's `probe/hang_cost.txt`: 323 min if every coordinator.py driver hangs).
- The CI-measured figure needs a run on this head. `gh workflow run tests.yml --ref handoff/r9-f10-12 -f recheck=false` runs `mutation-nightly` on any ref. `mutation-ledger` is main-only.

**Stopgap, if this cannot merge within three nights of dispatch.** Lower `--max` on `mutation-nightly` alone; it records nothing. This only defers the crossing, because the driver keeps growing.

## Head

1dc760ffe69c22f0530ef75aec71fbaa29142377

This is #1880's head fe446d246ac1c7b556a9f6b79eb8eaf6b5b2fc6c (round 0, beecd43, plus the delivery row) with round 1 merged onto it. Its merge base with `origin/main` is 20f597c6. Main has since moved to 243990abf3f598656756074f46c01430f323de40 (#1863); `git merge-tree --write-tree HEAD origin/main` returns rc 0, and that merge is the orchestrator's. Measured 2026-10-03T17:03:10Z. Round 1's failing-first commit is 4f4ff36ee85b4fda71eea3bbbdafa19610a7f431.

## Mutation proof

**Round 0, failing first.** At 401d804f9, the checks without the fix: `PYTHONPATH=tests/hastub python3 tests/entities.py` gives rc=1, `5 of 2109 ENTITY CHECKS FAILED`:
- `every driver's failing-check form reads as its count` (a timeout used to count as 1)
- `a mutant whose driver only overran its timeout is not killed, not LIVES, and never pinned (R9-F10.12)`, with `verdicts=['killed by slow.py']`
- `a driver's timeout scales from its own measured seconds over the fixed floor, and main() times every baseline, null and mutant run with it`
- `a budget too small for its pool starts mutants only while they fit, names the rest SKIP-BUDGET, and reserves the EXCLUSIVE runs it owes`
- `a run the budget let evaluate no mutant is refused; one that evaluated some, or skipped none for the budget, is not`

**Round 1, failing first.** At 4f4ff36e, with the round-1 checks but not the fix, `tests/entities.py` gives rc=1, `3 of 2117 ENTITY CHECKS FAILED`:
- `a budget cut falls on an anchor boundary, so no anchor is split and no killed twin is listed for a human verdict` (verdicts `['killed by tests/a.py', 'killed by tests/a.py', 'SKIP-BUDGET']`: the review's P1 split)
- `a mutant whose driver timed out runs no further driver` (ran all 3)
- `a run whose mutants all timed out or went unstarted is refused by cause, and a partial PASSED counts the timed-out ones` (refusals `[(None, []), ...]`)

**Round 1, breaking the fix at the head.** Each mutant gave rc=1 and `1 of 2117 ENTITY CHECKS FAILED`:

| mutant | what it breaks | check that failed |
|---|---|---|
| N1 | an anchor's twins are not admitted together | the anchor-boundary check |
| N2 | the sweep does not stop at a timeout | `a mutant whose driver timed out runs no further driver` |
| N3 | EXCLUSIVE runs are not skipped after a timeout | the same check |
| N4 | the refusal ignores timeouts | the refusal-by-cause check |
| N5 | `drain_survivors` does not exclude a cut anchor | the anchor-boundary check |
| N6 | `partial_note` ignores timeouts | the refusal-by-cause check |

N6 first survived, because the check's only partial case also had a budget cut. A timed-out-only case was added (5e7d9ed8), and then N6 was killed.

The review's `probe/probe.py` at this head:
- P1: `['killed by tests/a.py', 'SKIP-BUDGET', 'SKIP-BUDGET']`, pinned `['x.py:A']`, `survivors.txt= []`.
- P2: 1 driver run, clock 30 against an estimate of 30.
- P5: `nothing was measured: 3 mutant(s) timed out, 1 not started for --budget-minutes`.
- P6, P7 and P8 are unchanged: no timeout is a kill or a pin.

**Round 0, breaking the fix at beecd43.** Each mutant below breaks one predicate of the fix in a detached worktree of that head. Each gave rc=1 and `1 of 2110 ENTITY CHECKS FAILED`, naming:

| mutant | what it breaks | check that failed |
|---|---|---|
| M1 | `if run.timed_out: return None` deleted | `a mutant whose driver only overran its timeout ...` (verdicts=['LIVES']) |
| M2 | `driver_timeout` returns the floor | `a driver's timeout scales ...` (scaled=(1, 1200, 1200), fits=124) |
| M3 | the admission predicate becomes `if False:` | `a budget too small for its pool ...` (small: all LIVES) |
| M4 | the reservation is not released on a kill | the same budget check |
| M5 | `budget_refusal` returns None | `a run the budget let evaluate no mutant is refused ...` (out=(None, None, None)) |
| M6 | the null control's timeout guard becomes `if False:` | `and a null control whose driver timed out still refuses the run` (verdict='LIVES') |
| M7 | `failing_count` counts a timeout again | `a mutant whose driver only overran its timeout ...` (killed() True) |
| M8 | the EXCLUSIVE reservation is never added | the budget check |

**Demonstration, arm B, through main()'s own pieces.** The run uses `run_script` at the timeout main() passes, `LazyBaselines`, `drive_pool` and `pin_results`. The planted drivers are one that sleeps 3 s, against a 2 s floor and a 1.5 s baseline, and one that never returns.
- At base 1ccd0b1d, both are `killed by` and both are **pinned** (`x.py:a`).
- At the head, the slow one finishes inside its 5 s scaled timeout and is `LIVES`. The hang is `SKIP-TIMED-OUT in hang.py`. Neither is pinned.

**Demonstration, arm A, with the real `main()`.** The run is `--scope full --max 20 --jobs 1 --scripts tests/guard_pins.py,tests/plan_view.py,tests/solar_alignment.py,tests/wood_advisor.py`.
- With `--budget-minutes 0.83`: 10 evaluated, 10 `NOT RUN`, and `10 survivor(s) of 10 evaluated` exits as the cap over those 10. These drivers kill nothing here, hence `BREACHED`.
- The same run as `--drain`: 10 `NOT RUN`, and `survivors.txt` holds 10 lines, not 20.
- With `--budget-minutes 0.2`: `MUTATION TABLE REFUSED -- --budget-minutes admitted none of 8 mutant(s)`, rc=1, on a `--max 8 --jobs 2` pool.

## Null control

- With no deadline, the same pool runs whole: `unbounded` gives 4 of 4 LIVES, and the real `main()` without `--budget-minutes` evaluates 20 of 20.
- A typical night under the budget loses nothing: the 10-03 replay evaluates 39/39 under a 238-minute pool deadline.
- A timed-out NULL run still refuses the run, as it did before this change. That check is green at both base and head.
- With no change to production code, `mutation_table.py --scope changed --base origin/main` reports `no production code line added or modified`. There are no sites to pin.

## Figures

- nightly and ledger job, baseline-phase and mutant-phase minutes, features.py baseline seconds (12 scheduled runs listed by `gh api 'repos/tvofi/heatpump_optimizer/actions/workflows/tests.yml/runs?event=schedule&per_page=25'`; logs via `gh api --allow-escape-sequences repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs`, 0 failures in the counted retry): `measure_logs.py` (sha1 15a4667466d260515d9b9c1ab5a6091cef936947), rule in its docstring
- #1874 pin step timed out at 60 minutes with features.py's settled baseline at 569 s: `gh api --allow-escape-sequences repos/tvofi/heatpump_optimizer/actions/jobs/111201929552/logs`
- replay model and budget effect: `sim.py LOG <pool deadline min|none> <cost multiple> 3` (sha1 45a27b24ecf22b1d796f00cb7b059684a325d6e7); `SIM_EXCL=tests/stress.py,tests/harness_headers.py` for the EXCLUSIVE composition
- arm B demonstration: `demo_b.py <tests dir>` (sha1 f42945159be3b9ce0a3d86689a5dfd2b8b912b04), run in a detached worktree at 1ccd0b1d and at the head
- mutation proof: `mutants.py <name> tests/mutation_table.py` (sha1 0d27660815f7dfd08d49c27cc8c594cde0f786a0), then `PYTHONPATH=tests/hastub python3 tests/entities.py`
- scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: FULL` (reason: `.github/workflows/tests.yml changes the gate itself`). `tests/closures.json` puts `tests/mutation_table.py` and `tests/entities.py` in the closures of `tests/entities.py` and `tests/harness_headers.py`, and both pass locally at this head: `ALL 2117 ENTITY CHECKS PASSED`, `ALL 95 HARNESS HEADER CHECKS PASSED`. The rest is CI's.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, no budget moved
- round-1 probe: the reviewer's `probe.py` (sha1 66f1afff81ac24427bf33f62c8be8048311f932b), given the head's `tests` directory (P1-P8)
- #1878 composition: `git merge-tree --write-tree HEAD 5d6edffec707f9f16485cff9f3773e2c47874dcf`, then `tests/entities.py` in a worktree of that merge
- round-1 mutation proof: `mutants2.py <name> tests/mutation_table.py`, then `PYTHONPATH=tests/hastub python3 tests/entities.py`

## Red checks

none

## Forward-carry

- The R9-F10.13 group brief in the round-9 roster on `handoff/audit-r9-fixplan` at 33c2ac12 now carries both findings, written by the orchestrator:
  - `SKIP-BUDGET` is not a re-verification, and `SKIP-TIMED-OUT` is not a confirmation.
  - Arm A keeps `verdict[j] = "SKIP-BUDGET"`.
- Read back: the brief string contains `SKIP-BUDGET` and `SKIP-TIMED-OUT`. Their control is in this PR's `tests/entities.py`: the `small`, `exclusive` and anchor-boundary drive_pool checks. The roster file is off-tree and owned by the orchestrator.
- Still to note there, as the reviewer recommended: mutation-nightly passes no `--seed`, so its draw is the constant 20260911. On an unchanged tree a heavy night cuts the same tail. The sample was already fixed before this PR, so this is not a defect here. A date seed would change the sample that `max_survivor_fraction[full]` was recorded on, so it is a separate decision. The 33c2ac12 brief does not contain `seed`.

## Friction

- fixer.md-step-3: contradiction: the roster brief says a hang "still is" a kill, and the orchestrator's direction says a timeout is "INCONCLUSIVE, never a kill"; this PR followed the orchestrator
- SEAT-COMMON-worktree: cost: `git -C <repo> worktree add <relative path>` resolves against the main checkout; eight mutant worktrees landed under /Users/timmalmstrom/heatpump_optimizer/mut and were removed at once

🤖 Generated with [Claude Code](https://claude.com/claude-code)
