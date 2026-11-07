R10-HOTFIX-GATE-BUSY-DEFER, third PR (topic r10-gate-busy-defer-3). A deferring gate no longer holds a runner. `gate.judge()` publishes the deferral at once. `gate-sweep.yml` (`tools/ci/sweep.py`) re-runs that gate without a human once the deciding run completes. The existing green, newest-covering branch handles most heads. A new `settle` branch handles a head that no green gate follows: two gates that deferred to each other, or a decider that ended red or cancelled.

**What the runs say about the brief's cause.** The brief says nothing re-judges the deferring gate when the deciding run concludes. Today's runs do not support that as stated. On #3282 the sweep did fire for code run 42367457479. That run concluded at 11:48:41Z, and tvofi re-ran edit gate 42367457809 at 11:48:45Z. The sweep's read at 11:48:53Z then found that gate already re-queued and left it (`SWEEP-DONE run=42367457479 reruns=0`). The replay below shows that, without the human re-run, main's sweep re-runs the gate and it passes. The defects the runs do show are the following:
1. **The wait held a runner and ended red anyway.** Since #3276 merged (08:36:40Z), every deferral FAIL held its runner for the full ~12 min before publishing (`held_ge_600` = `deferral_fails` in the census below).
2. **The sweep's SKIP branch had no exit when nothing green follows.** This is a mutual deferral, or a decider that ended red or cancelled. These reds stayed until a human acted. Examples: #3265's pair at 04:06–04:08Z, and #3255's pair, both re-run attempts. The RCA of #3278 shows those ran pre-fix programs. `settle` covers the shape for whichever program the gate runs.

**The fix and the alternatives considered.**
- **Keep the wait and fix only the sweep.** This would leave a runner held ~12 min per deferral, which the brief forbids. It also feeds the runner queue that delayed the sweep's own re-runs by 7–26 min today, for example sweep 42353870719, created 08:04:01Z and run at 08:18:20Z.
- **Mark a deferral with a `ci.yml` step, or with an annotation the sweep reads.** `tests/entities.py` pins the gate job's last step (rev3 R3-1) and the sweep job's permissions (`checks: read` is absent). Either would change a pin.
- **Have the sweep read gate logs.** That needs a raw-body mode in `ghapi`.

`settle` instead decides from data the sweep already reads, the `filter=latest` jobs listing. A red gate is re-run when it started before another run's job (its gate aside) finished, or when a higher-id run's gate started while it judged. In the second case only the lower id is re-run, because `busy()`'s tie-break makes the lower id the one that decides. A re-run judges after every source finished, so it is never re-run again, and the branch cannot loop. The new harness `dev/audit/harnesses/r10_gate_busy_defer_3.py` (record, replay, census) lands with the fixture rows for #3282.

## Head

88e1140b7764571118943c5e92ef64bb21a054f0 (origin/main 28d46c4918285d36c409c1fb2f72eb77e04e569e merged in at 2026-11-07T13:13Z; that delta touches neither `tools/ci/` nor `.github/`).

## Mutation proof

Each mutant was applied in place, then `python3 -I tools/ci/gate.py --self-test`, `python3 tools/ci/sweep.py --self-test` and `python3 -I dev/audit/harnesses/r10_gate_defer_race.py` were run with `PYTHONDONTWRITEBYTECODE=1`, and the tree was restored (`git diff --quiet` clean after each).

- **M1, `judge()`'s deferral wait restored** (the bound `GATE_WAIT_MAX_S` for a reason ending "their gate decides"). Gate self-test: 77 checks, 14 failed. The race harness reads gate-wait > 0 in 2754, 2754-red, pair, cascade, editcode and prelude. Killed by, among others:
  - `FAIL #3282: the deferring edit gate publishes CI's deferral at once and holds no runner`
  - `FAIL #3263 (42338396358 beside code run 42338396871): the deferring edit gate publishes CI's deferral at once, no nap`
  - `FAIL a deferral FAILs at once (for gate-sweep.yml) and holds no runner: no nap`

  This is also the failing-test-first run: the head's self-test over main's `judge()`.
- **M2, `settle` removed** (the old SKIP). Sweep self-test: 33 checks, 10 failed, including `FAIL settle: two gates that deferred to each other (each started before the other's units finished) are both re-run, the triggering run's included`. The race harness reads RESIDUAL-RED 2 in `pair`.
- **M3, `undecided()`'s late-source arm removed.** 3 failed:
  - `FAIL settle: two gates that deferred to each other …`
  - `FAIL settle: a decider that ended red re-runs the gate that deferred to it, not itself`
  - `FAIL settle: a gate still running is polled, then the deferral it leaves red is re-judged`
- **M4, `undecided()`'s overlapping-gate arm removed.** 2 failed: `FAIL settle: a lagging-listing pair (sources done, gates overlapping) re-runs the lower id only, swept from run 1` (and from run 2). The race harness reads RESIDUAL-RED 2 in `pair`.
- **M5, the overlap arm without the id tie-break** (`i > run_id` → `True`). The same 2 checks fail, because both gates of the pair are re-run.
- **M6, `settle`'s unconcluded-gate SKIP removed.** 2 failed: `FAIL settle: a run whose gate is still queued owns convergence (SKIP, nothing re-run)` (and `waiting`).
- **M7, `settle`'s finishing poll removed.** 1 failed: `FAIL settle: a gate still running is polled, then the deferral it leaves red is re-judged`.

A disclosed self-correction: a first run of the mutant driver printed M5's two failures under M6. Its import of `sweep` went through `sweep_selftest`, and with bytecode disabled and every mutant's diff printed, M6 reads as above.

## Null control

- **A single run at its head still judges, with no wait and no red.** Race harness `single` reads `verdicts 1 UNDECIDED-RED 0 … gate-wait 0 s … RESIDUAL-RED 0` at both the base and the head. The gate self-test's `null: no other run at the head, no wait` passes. The sweep's `settle null: a lone red gate at its head is never re-run` passes.
- **A genuinely unfinished earlier source still defers.** `busy-defer null: a genuinely earlier run still adding sources is still deferred to` is unchanged and passes. `C3: … defers at once, no nap; re-run once the code run ends, it judges its sources` and `a deferring gate re-judged after the decider's red is that red, never a PASS` both pass: a deferral never passes early.
- **A real red is never re-run in a loop.** `settle null: the same reds judged after every source finished, apart, are final, never re-run (no loop)` passes, and so does `settle null: that lower gate re-judged red after the pair is final, and the higher is not re-run (no loop)`. `2754-red` reads `MASKED 0` and every verdict red at the head.
- **The base tree, on the same inputs.** `D=$(mktemp -d); git archive 630bf533d838 tools/ci tools/pr | tar -x -C $D; python3 -I dev/audit/harnesses/r10_gate_busy_defer_3.py replay --ci $D/tools/ci` prints `RESULT replay wait_s=720 first=FAIL swept=yes final=PASS`. That is the 720 s wait and the verdict CI logged (`FAIL run(s) [42367457479, 42367461228] …`).

## Figures

- **#3282 replay, base:** `D=$(mktemp -d); git archive 630bf533d838 tools/ci tools/pr | tar -x -C $D; python3 -I dev/audit/harnesses/r10_gate_busy_defer_3.py replay --ci $D/tools/ci` prints `RESULT replay wait_s=720 first=FAIL swept=yes final=PASS`.
- **#3282 replay, head:** `python3 -I dev/audit/harnesses/r10_gate_busy_defer_3.py replay` prints `RESULT replay wait_s=0 first=FAIL swept=yes final=PASS`. The re-run the sweep posts at the code run's recorded completion judges PASS, with no human.
- **Race harness:** `python3 -I dev/audit/harnesses/r10_gate_defer_race.py --ci $D/tools/ci` (the same `$D` export) against `python3 -I dev/audit/harnesses/r10_gate_defer_race.py`. The rule is the harness's gate-wait, the summed seconds every gate waited, and RESIDUAL-RED, the gates still red on the deferral after every sweep converged.

  | scenario | gate-wait, base | gate-wait, head | RESIDUAL-RED, base | RESIDUAL-RED, head |
  |---|---|---|---|---|
  | 2754 | 780 s | 0 s | 0 | 0 |
  | 2754-red | 780 s | 0 s | 0 | 0 |
  | pair | 120 s | 0 s | 0 | 0 |
  | cascade | 120 s | 0 s | 0 | 0 |
  | editcode | 600 s | 0 s | 0 | 0 |
  | single | 0 s | 0 s | 0 | 0 |
  | prelude | 480 s | 0 s | 0 | 0 |

  UNDECIDED-RED rises from 0 to 1–2 per scenario by design: a deferral is now a red the sweep converges. MASKED is 0 and DEADLOCK is `no` at both ends.
- **Census, before (live, today's runs):** `python3 dev/audit/harnesses/r10_gate_busy_defer_3.py census --since 2026-11-07T08:36:40Z --until 2026-11-07T12:59:11Z`. The rule: every `gate` job of a ci.yml run created in the window whose log's verdict is the deferral. "Minutes" runs from the deciding gate's first green after the deferral to the deferring run's next green gate, over those a later green resolved.

  The window opens at #3276's merge, so the programs wait. It prints `deferral_fails=13 heads=10 per_head_max=3 held_runner_s=9391 held_ge_600=13 resolved=7 by_bot=4 by_human=3 median_min=0.8`.

  The whole day, `--since 2026-11-07T00:00:00Z` with the same `--until`, prints `deferral_fails=133 heads=68 per_head_max=10 held_runner_s=15202 held_ge_600=16 resolved=84 by_bot=73 by_human=11 median_min=2.0`. Most of that day ran pre-#3276 programs, which deferred at once.

  These are live figures from a sliding window, so re-run the command rather than carry the numbers.
- **Census, after:** this needs runs pinned to a base carrying this change, so it is not measurable before merge. The re-runnable query is the same census command with `--since` at this PR's merge. The prediction, from the replay and the race harness, is `held_ge_600=0`. Deferral FAILs per head do not fall: every deferral is now published, and the 12-min wait rarely decided anything, since the whole-day census shows only 16 of 133 deferral FAILs waited at all. Minutes from the decider's green to the deferring gate's green are bounded by the sweep's latency plus runner queue time, the same path as today's bot-resolved ones.
- **Class census (fixer step 8): every place a CI program holds a runner waiting.** `grep -nE "\bsleep\(|_sleep\(" tools/ci/*.py | grep -vE "selftest|def _?sleep|self_test"` returns 9 sites, each with its disposition:
  - `gate.py:274`: **closed in this diff for deferrals.** It remains only as the re-read of the run's own lagging jobs listing (`lag_bound`), which no other gate decides.
  - `prelude.py:242` (`wait_sources`, up to `WAIT_MAX_S`): **a distinct finding.** It is a prelude, not a gate, and #3282's review run's prelude held a runner 11:16:40–11:48:01Z. See Forward-carry.
  - `codescan_wait.py:80`, `:95`, `:131`: the CodeQL wait, not a gate waiting on a decider. **Out of this class.**
  - `ghapi.py:108`, `:125`: the 5xx backoff. **Out of this class.**
  - `sweep.py:152`, `:181`: the sweep's polls, at most 600 s, in `gate-sweep.yml`. Not a gate, and **already bounded**.
- **Checks re-run at the head:**
  - `python3 -I tools/ci/gate.py --self-test`: 77 checks, 0 failed.
  - `python3 tools/ci/sweep.py --self-test`: 33 checks, 0 failed.
  - `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
  - `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2643 ENTITY CHECKS PASSED, run at ba40c56a before the main merge.
  - `python3 tests/harness_headers.py`: ALL 112 HARNESS HEADER CHECKS PASSED.
  - `node tools/policy/agreement.mjs`: `unregistered=0` after the harness stopped repeating the runs-path regexes.

  `tests/closure.py select` reads `MODE: FULL`, because `tools/ci/fixtures/gate_busy_defer_runs.json` changes the gate. That suite is CI's to run.

## Red checks

`prepr.sh`'s first run refused two things, both repaired before the handoff:
- `ci predict`: tests / closures, the new harness as an INERT read. Repaired by `tools/pr/ci_predict.py --apply-inert`.
- `agreement lane`: two runs-path regexes written in the new harness and in `sweep_selftest.py`. Repaired by parsing the path the way the gate self-test does.

The cheaper detector for both already exists and fired: `prepr.sh`, before any PR. No CI check has gone red on this branch, since no PR exists yet.

## Forward-carry

- **#3278's RCA document, on branch `fix/r10-rca-gate-busy-defer-2`, not edited here.** Its §1 sentence "In #3261, the higher gate waits one poll, then passes" becomes untrue at this head. That gate now publishes the deferral at once, and `settle` re-runs it (race harness `pair`: gate-wait 0 s, RESIDUAL-RED 0). Its §5.2 countermeasure, a fresh dispatch where a re-run would replay a stale pinned program, stays needed: `settle` re-runs through the same job-rerun API, so a re-run of a run created before this merges executes the old waiting program. Re-measure with that document's own `census` arm after this merges (a group of `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster`; the orchestrator appends it with `tools/audit/seat/roster_edit.py append-carry`, this seat writes no roster). Carry: R10-RCA-GATE-BUSY-DEFER-2
- **A prelude holds a runner while it waits on another run** (`prelude.wait_sources`, up to `WAIT_MAX_S` = 8700 s). This is the same runner-queue cost this PR removes from the gate; #3282's review run's prelude held one 11:16:40–11:48:01Z (its `prelude` job's started and completed stamps). It is legitimate only while the queue it lengthens is measured. Re-measure from the jobs API at your own merge base (a group of `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster`; the orchestrator appends it with `tools/audit/seat/roster_edit.py append-carry`, this seat writes no roster). Carry: R10-HOTFIX-GATE-BUSY-DEFER

## Friction

- frugal-inline-budget: cost: a session guard counted log tails and result reads as discovery searches and refused them mid-measurement, so each read went through a subagent. Carry: dismissed: a session plugin's guard, not this repository's policy
- brief-cause: contradiction: the brief's "nothing re-judges it" against #3282's own runs, where tvofi re-ran the gate 4 s after the code run concluded and 8 s before the sweep's read, which is why the sweep's log reads reruns=0. Carry: R10-HOTFIX-GATE-BUSY-DEFER
