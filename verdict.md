Fix review: blocked ad62bf6346a131111ea482185caa2813e9851a19 mutation-vacuous: ci_critpath --event/--branch run-list filter dropped survives the self-test

Round: 1 (first review of this head). Measured at ad62bf6346a131111ea482185caa2813e9851a19 from a detached worktree; re-read before writing: the PR head and refs/pull/2645/head are still that SHA. Merge base e30b24bbc4; origin/main 4200ea4c42. `git diff <mb>...origin/main -- dev/governance/roles/` is empty: the contract read is current.

## The blocking finding

`tools/audit/seat/ci_critpath.py` `Api.runs` builds the run-list query from `--event`/`--branch`:
`q = "".join(f"&{k}={v}" for k, v in (("event", event), ("branch", branch)) if v)`.
No client-side filter backs it: the rows returned are filtered only for cancelled/skipped. Mutant `c10-event-branch-q` (`q = ""`) leaves the self-test at `24 checks, 0 failed`: no check passes `--event` or `--branch`, and the stub `get` ignores the query string. With it, `--workflow tests.yml --last 8 --event push --branch main` silently mixes pull-request and branch runs into main's median.

The body leans on this exact filter twice:
- `## Red checks`: the cheaper detector it names for `ci-ratchet` is `ci_critpath.py --event push --branch main --last 8`, which "reads the same median before a push lands".
- `## Forward-carry` to R10-CI-LAYOUT-P2 (roster 5e70cc5ce): the next fixer is told to keep its window on one side of a job-graph change with "`--event`, `--branch`, or `--run` lists".

So a changed site that two claims rest on has no mutant and no check (brief item 3). The fix is small: one self-test check where the stub returns a different run list when `event=push&branch=main` is in the path (or asserts the path it was called with), plus a seat mutant like `c10` in `r10_seat_selftests_mutants.py`.

Two more survivors. Neither blocks, but the fixer should look at both:
- `c9-git-first` (`p.stdout if False`: always read needs from the contents API): self-test stays green. The output is the same; only the API-read count changes, and the body quotes that count ("11 API reads ... again reads 1"). Low value; a check on `reads` for a head git holds would pin it.
- `c7-cycle-guard` (cycle refusal removed): survives. GitHub refuses cyclic `needs:`, so this is a guard against input the API cannot produce. I judge it equivalent in practice.

## RESULT lines

```
RESULT head=ad62bf6346a131111ea482185caa2813e9851a19 moved=no
RESULT selftest ci_critpath=24/0 flow_metrics=16/0 review_strength=100/0 (python 3.11.17, -I)   # body: same
RESULT selftest_wiring=89 self-testing, 89 wired, 0 unwired                                         # body: same
RESULT seat_mutants M0=0 steps red (Linux; body's 3 pr_args reds were its Mac) ci_critpath-1 KILLED 3 failed, ci_critpath-2 KILLED 2, flow_metrics-1 KILLED 1, flow_metrics-2 KILLED 4, ruleset_cutover-1/2/3 KILLED 1 each, survivors=0
RESULT own_mutants=18 killed=15 survived=3 (c7-cycle-guard, c9-git-first, c10-event-branch-q)
RESULT mutants_file three-dot vs merge base: +6 lines only (this PR's block); head vs origin/main differs by exactly those 6 lines; main's ruleset_cutover-1..3 block byte-identical
RESULT merge-tree origin/main head: rc=0 tree 91e0d774e8; LEDGER-MERGE: resolved tests/closures.json (inert_reads set merge); no MERGE-CLAIM lines (no claim file touched)
RESULT structure.py=STRUCTURE RATCHET PASSED; archscore dS +0.0000 NULL; no *_budgets.json touched
RESULT parity: PARITY 24/24, NULL 9/24, NEEDS 40 files 0 differ, mutant differs on 28   # body: same
RESULT carry_audit pr 2645: 5 routed, 0 unrouted, 0 bad
RESULT entities.py (venv-ci 3.14.7): head 2404/2404 pass; origin/main 4200ea4c 2406/2406 pass; merge(origin/main, head) 2406/2406 pass
RESULT CI at head: red fast (3.14) [entities 1 of 2406], red nightly-status; closures, coverage, CodeQL python in progress
```

## Brief checklist

1. **No round constant in code.** Grepping the three instruments for r10/R10/heatpump_optimizer/tvofi finds only `flow_metrics.py:6`, a usage example (`--prefix R10-`) in the docstring. In `ci_critpath.py`, `--repo` has no default. In `flow_metrics.py`, `--prefix` and `--roster` are required. Default values the body names: `--record-prefix record/` and `--tree origin/main`. No added review_strength line names the round or repository. Holds.
2. **Self-tests and wiring** match the body. The named mutants all kill, and so do main's three. The mutants file merged cleanly, with main's block byte-identical (above).
3. **Coverage of the changed sites without a full harness re-run.** The full re-run was skipped after the merge, and that is justified: the merges add only main's lines, which I ran. But the named set plus the body's targeted list leaves `--event`/`--branch` with no mutant and no check. That is the blocking finding. Every other site I planted was killed: queue held in replay, p90 rank, needs-field reset, jobs and runs paging, matrix mapping, expression name, cf path, first verdict, merge and roster windows, patch-id, unresolved, prev-merge kind, unjudged count.
4. **structure.py** passes. **dS** +0.0000. Merges clean with origin/main. The entity failures the fixer saw on the Mac (heartbeat timing, `a8:register_once`) do not reproduce here on 3.14.7 at the head, at main or at the merge. The `FAIL` lines in those logs are the suite's indented null controls, the same set at main and at the head. pr_args: M0 here reports no red seat step. `instrument-self-tests` is green in CI at the head, and it runs the pr_args steps.
5. **Carries.** carry_audit reads 5/0/0. The three roster carries are all on `origin/handoff/audit-r10-roster`:
   - c137945d6 → R10-FLY-YIELD-GUARD. It owns the yield-probe guardrail (`yield-probe.md`), which reads review strength: the right owner.
   - 5e70cc5ce → R10-CI-LAYOUT-P2. In progress; it owns `tests.yml`/`governance.yml`/`ci.yml` and states its next W figure with this instrument: the right owner. One note on its wording: `analyse` refuses a `--drop-edge` only when both jobs ran in that run and the edge is gone. If a graph change renames or removes either job, the drop is a silent no-op, not a refusal. So "a window that straddles a job-graph change refuses" holds only for a graph change that keeps both jobs. Not blocking; the carry should say so.
   - 2ad8710e4 → R10-FLOW-JIDOKA. A stale `S36` pin in a seat mutant harness is a stop-the-line instrument-health item. Its roster files (prepr.sh, policy-rot) do not include the harness, so the fit is by role, not by file. Acceptable.
   - R10-FLOW-TOOLKIT-MODEL (the FUTURE-STATE figures) and the dismissed `--record-prefix` carry are routed per carry_audit.
6. **CI** (ev/check_runs.txt):
   - `nightly-status`: red. Its diff does not reach what it reads, so it is not this PR's (`defect-root-cause.md`). The body names it.
   - `fast (3.14)`: red, `tests/entities.py` "1 of 2406 ENTITY CHECKS FAILED". The body's `## Red checks` predates this run ("No check has run on this head yet"), so it is unanswered there. The check does not reproduce locally at the head, at main or at the merge on 3.14.7. Main's full push run at the merge base passed `fast (3.14)`. The retrieved log tail does not show which check failed. It looks like the timing-class checks (hb:*) the fixer reported; that is a judgement, not a measurement.
   - Under rule 11 I post no root-cause class on it: closures and coverage are still running, and no `pr-contract` run has started since `fast` concluded red (last pr-contract 03:20:54Z, fast red 03:29:48Z). The fixer owes the answer in `## Red checks` once the workflows conclude.

## Not re-derived

- The `review_strength.py` one-node sweep (`mutants=2612 killed=2562 survived=50`): not re-run.
- The live-API figures (655 verdicts, the 0.52/0.15 windows, the flow_metrics window counts, and "11 API reads"): this seat has no `gh` and did not fetch the bus tags.

Those figures are the fixer's, not verified here.

bus-nonce: da7eafe36d7cad6ecc675da0f5632b30
