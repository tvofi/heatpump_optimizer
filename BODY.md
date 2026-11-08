R10-RCA-SWEEP-SETTLE-LOOP is the root-cause seat for the sweep settle loop. It ran beside the R10-SWEEP-SETTLE-LOOP fixer and did not edit `tools/ci/`. Part of #201. The analysis is `dev/audit/rca/R10-RCA-SWEEP-SETTLE-LOOP.md`, indexed in `dev/audit/config/bugclasses.json` as `_rca.R10-RCA-SWEEP-SETTLE-LOOP`. Trigger: release (#3287, `52f9fc5b34`, shipped in v7.1.6).

- **Cause.** `tools/ci/sweep.py` `undecided()` arm 1 treats any non-gate job of another run whose `completed_at` is later than this gate's start as a source that finished late. When GitHub re-runs a `gate` job, it re-stamps every skipped job of that run seconds before the new gate starts. Every job that ran keeps its stamps. This was measured on #3319's runs 42469369199 and 42469369682, attempts 1 to 6. As a result, two red gates at one head re-run each other until the cap (attempt 44).
- **Process state (c).** #3287 pinned "the branch cannot loop" with one-pass nulls. Those nulls ran over hand-written units that have no `conclusion` field and that a re-run never moves. Its recorded replay ran one open-loop sweep, even though its own fixture's attempt-10 rows already showed the re-stamp. The review accepted the nulls, and the live head it watched re-ran green, which ends the loop at the first step.
- **Countermeasure A (state c), adopted and carried to the fix.** The convergence claim is pinned closed-loop over a recorded attempt-to-attempt transition. The harness added here is offered as the finder's harness at both ends.
- **Countermeasure B, proposed to triage, not built.** A beat row that flags any ci.yml run at attempt 20 or above.

## Head

`ae2bceee537b241afc74e2685daec6d3cc9e6896`, branch `fix/r10-rca-sweep-settle-loop`, two commits on origin/main `4fe7d5934b`, which is the merge base. The three-dot diff adds:
- the RCA document;
- the harness `dev/audit/harnesses/r10_rca_sweep_settle_loop.py` and its recorded fixture `.json`;
- the `_rca` entry;
- the harness's `tests/closures.json` INERT READS entry, written by `ci_predict.py --apply-inert`.

It has no production line, and no delivery row because no PR exists yet.

## Mutation proof

This handoff adds no production line. The detector it adds is the harness's `replay` arm. It was run against real program copies made with `git archive <sha> tools/ci`:
- **Red on the defect.** At `origin/main` `4fe7d5934b` and at `52f9fc5b34` it prints `RESULT replay reruns=86 max_attempt=44 sim_minutes=72 alarm=yes`.
- **Green once fixed.** On a candidate copy where arm 1 ignores `conclusion == "skipped"` it prints `reruns=1 max_attempt=2 alarm=no`. This candidate is a control for the harness, not the fix. It also passes the current `sweep.py --self-test` (52 checks, 0 failed), so today's self-test cannot tell a fixed arm 1 from a broken one.

## Null control

- `--no-restamp` (the hand-written fixtures' world) at `origin/main` prints `reruns=1 max_attempt=2 alarm=no`. The arm's power comes from the recorded transition. A world without it hides the defect.
- `52f9fc5b34^` (before `settle` existed) prints `reruns=0` on the same real-red head, which is correct: a genuine red is not re-run.
- The census predicate at alarm 20 flags 0 runs in the 21.2 h before the merge and 32 runs in the 16.6 h after it. At alarm 10 it flags 4 runs before the merge (the predecessor design's 10-17-attempt runs), which is why the proposed threshold is 20.

## Figures

- Replay: `python3 -I dev/audit/harnesses/r10_rca_sweep_settle_loop.py replay [--ci <export>/tools/ci] [--no-restamp]`, with results as above. Runtime is 0.12-0.25 s (`time -p`).
- Census: `python3 -I dev/audit/harnesses/r10_rca_sweep_settle_loop.py census <tsv> --since ... --until ... --alarm N`. The TSV is `gh api --paginate repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs?per_page=100&created=>=2026-11-06T22:00:00Z`, read at 2026-11-08T11:52:46Z.
  - Pre-merge: `runs=465 reattempts=428 at_cap=0 max_attempt=17`.
  - Post-merge: `runs=324 reattempts=1618 at_cap=17 max_attempt=45`.
- `gate-sweep.yml`: 1000 runs (the API cap) were created between 07:53:04Z and 11:50:13Z, totalling 904 run-minutes, median 23 s each.
- Detector probe: one `gh api ...ci.yml/runs?created>=...` call takes 2.84 s.
- The brief's 1089 re-attempts and 810 runner-minutes are the orchestrator's figures over its own window. They were not re-taken here.
- Local checks:
  - `python3 tools/audit/fold_ledger.py check` prints `0 violation(s)`, 138 rca entries.
  - `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
  - `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`.
  - `ci_predict.py --base origin/main` predicts no red.
  - `tests/entities.py` could not run on this host (it has no `homeassistant`); `tests/harness_headers.py` was not run to completion here, and this harness carries no EXPECTED RESULT lines, so it executes nothing of it.

## Red checks

None. No PR exists and no CI has run on this head.

## Forward-carry

- Carry 1, to the R10-SWEEP-SETTLE-LOOP fixer through the orchestrator. This must reach the fix before it merges (`finding-propagation.md`). It covers:
  - countermeasure A, a closed-loop convergence check over a recorded attempt-n/n+1 pair;
  - the harness, offered for both ends;
  - the fact that the current self-test passes a fixed arm 1;
  - the design question in RCA section 3: whether a re-run should require an input change since the previous attempt.

  Carry: #201
- Carry 2, to proposal triage: countermeasure B, the `attempt-watch` beat row at attempt >= 20, polled every 1800 s, using RCA section 4's numbers. Carry: #201
- Carry 3, to the tick's owner: `orchestrator_tick.py:1441` counts any check run completed after dispatch as worker CI activity, so a sweep re-run reads as the worker's. Whether check runs are re-stamped was not measured. Carry: #201

## Friction

none
