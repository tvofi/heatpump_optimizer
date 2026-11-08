R10-RCA-SWEEP-SETTLE-LOOP is the root-cause seat for the sweep settle loop. It ran beside the R10-SWEEP-SETTLE-LOOP fixer and did not edit `tools/ci/`. Part of #201. The analysis is `dev/audit/rca/R10-RCA-SWEEP-SETTLE-LOOP.md`, indexed in `dev/audit/config/bugclasses.json` as `_rca.R10-RCA-SWEEP-SETTLE-LOOP`. Trigger: release (#3287, `52f9fc5b34`, shipped in v7.1.6).

- **Cause.** `tools/ci/sweep.py` `undecided()` arm 1 treats any non-gate job of another run whose `completed_at` is later than this gate's start as a source that finished late. When GitHub re-runs a `gate` job, it re-stamps every skipped job of that run seconds before the new gate starts. Every job that ran keeps its stamps. This was measured on #3319's runs 42469369199 and 42469369682, attempts 1 to 6. As a result, two red gates at one head re-run each other until the cap (attempt 44).
- **Process state (c).** #3287 pinned "the branch cannot loop" with one-pass nulls. Those nulls ran over hand-written units that have no `conclusion` field and that a re-run never moves. Its recorded replay ran one open-loop sweep, even though its own fixture's attempt-10 rows already showed the re-stamp. The review accepted the nulls, and the live head it watched re-ran green, which ends the loop at the first step.
- **Countermeasure A (state c), adopted and carried to the fix.** The convergence claim is pinned closed-loop over a recorded attempt-to-attempt transition. The harness added here is offered as the finder's harness at both ends.
- **Countermeasure B, proposed to triage, not built.** A beat row that flags any ci.yml run at attempt 20 or above.

## Head

`3aa0616e7b29c421d00bb3054922275717e44625` merges origin/main `daf8b349fd30` into `1b2307959d53`: an automatic merge, no resolution. Main's delta since `51cd5ec` touches only `tests/card_browser.mjs` and `dev/programme/delivery/3346.md`, which nothing in this diff reads. The reviewed code is unchanged.

`1b2307959d535b0400dc25fc9891a190a76db8a2` merges main `51cd5ec` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`50a78a49ba19061c5d4e6e4a8f5efae62da64aab` merges the authored code head `95f3e79e7af9a4dbe2e18be5078eeaf89d23bd53`.

`95f3e79e7af9a4dbe2e18be5078eeaf89d23bd53` (the repair of blocked 8db2e568; origin/main `bb7dfb9bd6c6` merged, prepr.sh rc=0 on it), branch `fix/r10-rca-sweep-settle-loop`, two commits on origin/main `4fe7d5934b`, which is the merge base. The three-dot diff adds:
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
- Re-taken at `3aa0616e7b29` (`date -u` 2026-11-08, origin/main `daf8b349fd30`): `replay` prints `RESULT replay reruns=86 max_attempt=44 sim_minutes=72 alarm=yes`, and `replay --no-restamp` prints `RESULT replay reruns=1 max_attempt=2 sim_minutes=1 alarm=no`. `tests/closure.py select` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out` (`tests/entities.py`). `tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Local checks at the earlier head:
  - `python3 tools/audit/fold_ledger.py check` prints `0 violation(s)`, 138 rca entries.
  - `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
  - `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`.
  - `ci_predict.py --base origin/main` predicts no red.
  - `tests/entities.py` could not run on this host (it has no `homeassistant`); `tests/harness_headers.py` was not run to completion here, and this harness carries no EXPECTED RESULT lines, so it executes nothing of it.

## Red checks

Train skip at `1b2307959d53`, run 42519917698: `governance / instrument-self-tests`, `pr-contract / pr-contract` and `gate` red.

- `governance / instrument-self-tests`: the one failing check in job 128852059264's log is `FAIL   mutant mut:unlock (its line deleted): the holder is still alive when the run returns`, giving `pr_args self-test: 184 checks, 1 failed` in the `update-pr` step. That is a timing-dependent arm in `tools/audit/seat/pr_args.sh`, a file this diff does not touch (`git diff --stat $(git merge-base origin/main HEAD)...HEAD` lists six files, none under `tools/`). The arm reads the lock holder inside its 0.2 s `mut:watch` poll, so under load it can read a holder that already exited. Not this diff's: in the same job, the `pr-args` and `open-pr` steps ran the same self-test and printed `pr_args self-test: 184 checks, 0 failed`, and `governance / instrument-self-tests` is `success` at main `51cd5ec8` (run 42519600464). The deterministic arm is open #3317's carry 19/40 (R10-HANDOFF-PATH part 3). No cheaper detector is owed: the arm is itself the detector, and its flake is already being fixed there. Carry: R10-HANDOFF-PATH|#3317
- `pr-contract / pr-contract`: its only `ERROR` is `[pr-body] ... check \`governance / instrument-self-tests\` is red and \`## Red checks\` does not name it`. This section now names it. No cheaper detector: the body could not name a red that did not exist when it was written. Carry: dismissed: answered by this section
- `gate`: red because the two checks above are red; it carries no failure of its own. Carry: dismissed: follows the two above

Earlier round:

Verdict "Fix review: blocked 8db2e568 root-cause-detectable: tests / fast (3.14)", red `tests/harness_headers.py`.

- Cause, mine: `harness_headers.py` check "every inlined walk matches the canonical helper and no depth root remains" failed at 8db2e568 on `dev/audit/harnesses/r10_rca_sweep_settle_loop.py:37: ROOT = HERE.parents[2]` (run locally: `1 of 112 HARNESS HEADER CHECKS FAILED`, the only FAIL line). Fixed in a0ee437f: the harness inlines the canonical `repo_root`. After: `harness_headers.inline_scan()` rc 0 and `depth_root_seams()` is `[]`; `replay` still prints `RESULT replay reruns=86 max_attempt=44 sim_minutes=72 alarm=yes`.
- The named `a3:roster`, `a3:orjson`, `a3:finite` are `tests/nightly_ha.py` checks driven from `tests/entities.py`, not `harness_headers.py`; my diff touches neither, and the local `harness_headers.py` run lists no a3 line. I did not reproduce them and do not claim them fixed; if they are red at this head they are not caused by this diff.
- Root-cause trigger: cheaper detector exists and is standing: `prepr.sh` "ci predict" ran `harness_headers` seams only on a changed file's self-test, and a new harness under `dev/audit/harnesses/` has none, so it missed this. Standing cost of running `depth_root_seams()` in prepr for any added file in that scope: one in-process scan, well under a second (`python3 -c "import harness_headers as h; h.depth_root_seams()"`). No countermeasure built here; recorded as a refusal to widen prepr inside a repair PR, for the orchestrator to cost.
- Remaining: no CI has run on `3aa0616e7b29`.

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

