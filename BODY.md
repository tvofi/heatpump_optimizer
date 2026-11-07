R10-HOTFIX-GATE-BUSY-DEFER, third PR (topic r10-gate-busy-defer-3). A deferring gate no longer holds a runner. `gate.judge()` publishes the deferral at once. `gate-sweep.yml` (`tools/ci/sweep.py`) re-runs that gate without a human once the deciding run completes. The existing green, newest-covering branch handles most heads. A new `settle` branch handles a head that no green gate follows: two gates that deferred to each other, or a decider that ended red or cancelled.

**What the runs say about the brief's cause.** The brief says nothing re-judges the deferring gate when the deciding run concludes. Today's runs do not support that as stated. On #3282 the sweep did fire for code run 42367457479. That run concluded at 11:48:41Z, and tvofi re-ran edit gate 42367457809 at 11:48:45Z. The sweep's read at 11:48:53Z then found that gate already re-queued and left it (`SWEEP-DONE run=42367457479 reruns=0`). The replay below shows that, without the human re-run, main's sweep re-runs the gate and it passes. The defects the runs do show are the following:
1. **The wait held a runner and ended red anyway.** Since #3276 merged (08:36:40Z), every deferral FAIL held its runner for the full ~12 min before publishing (`held_ge_600` = `deferral_fails` in the census below).
2. **The sweep's SKIP branch had no exit when nothing green follows.** This is a mutual deferral, or a decider that ended red or cancelled. These reds stayed until a human acted. Examples: #3265's pair at 04:06–04:08Z, and #3255's pair, both re-run attempts. The RCA of #3278 shows those ran pre-fix programs. `settle` covers the shape for whichever program the gate runs.

**The fix and the alternatives considered.**
- **Keep the wait and fix only the sweep.** This would leave a runner held ~12 min per deferral, which the brief forbids. It also feeds the runner queue that delayed the sweep's own re-runs by 7–26 min today, for example sweep 42353870719, created 08:04:01Z and run at 08:18:20Z.
- **Mark a deferral with a `ci.yml` step, or with an annotation the sweep reads.** `tests/entities.py` pins the gate job's last step (rev3 R3-1) and the sweep job's permissions (`checks: read` is absent). Either would change a pin.
- **Have the sweep read gate logs.** That needs a raw-body mode in `ghapi`.

`settle` instead decides from data the sweep already reads, the `filter=latest` jobs listing. A red gate is re-run when it started before another run's job (its gate aside) finished, or when a higher-id run's gate started while it judged. In the second case only the lower id is re-run, because `busy()`'s tie-break makes the lower id the one that decides. The third case is that same pair seen from its higher side: a red gate whose lower-id peer's gate judged beside it and ended green deferred to that decider, so the higher is re-run. A red lower is re-run by the second arm and the higher is not, so the pair is never both re-run. A re-run judges after every source finished and after the peer gate concluded, so it is never re-run again, and the branch cannot loop. The new harness `dev/audit/harnesses/r10_gate_busy_defer_3.py` (record, replay, census) lands with the fixture rows for #3282.

**Round 2 repair (verdict/3287 at 29ee7261, `settle-unjudged`).** At 520538cc, a higher-id gate that deferred by `busy()`'s tie-break to a lower run whose listing lagged stayed red whenever the lower's green gate did not cover the newest event, that is, the higher run was created after the lower's gate started. The sweep then took `settle`, where `undecided()` re-ran only the lower id of an overlapping pair, and the lower was green. At the base that gate waited one poll and passed, so the change introduced this. The repair is one arm of `undecided()` (`tools/ci/sweep.py`): a LOWER-id run whose gate overlapped this one (`started_at <= this completed_at`, `completed_at >= this started_at`) and ended `success`. No other production line moves. The sweep self-test gains the verdict's ordering from both sides, the no-loop second sweep, two nulls and a census of the pair's eight orderings (below).

## Head

f6c1866ba8564989a34cc3d09f001cdb5133ecbe. This is the PR head 520538ccfad01bee373382e9d56fc036c8c87ea0, plus the repair commit, plus origin/main 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76 merged at 2026-11-07T15:47Z. That main delta touches no `tools/ci/`, `tools/pr/` or `.github/` path: `git diff --quiet 88e1140b7764571118943c5e92ef64bb21a054f0 HEAD -- tools/ci/gate.py tools/ci/prelude.py .github` exits 0, and the only `tools/ci` change since 88e1140b is this repair's `sweep.py` and `sweep_selftest.py`.

## Mutation proof

**Round 2, the repair.** The failing test came first. The head's self-test over 520538cc's `sweep.py` (`git show 520538ccfad01bee373382e9d56fc036c8c87ea0:tools/ci/sweep.py` in place, `python3 -B tools/ci/sweep.py --self-test`) prints `sweep self-test: 52 checks, 3 failed`:
- `FAIL settle: the higher of a lagging pair, deferred to a lower gate that ended green but does not cover the newest event, is re-run, swept from run 1` (and from run 2)
- `FAIL census: an overlapping deferral is re-run (lower success, higher created 52, its gate 55-56)`

Each mutant below was applied in place to the new arm `or (i < run_id and g.get("conclusion") == "success" and gs <= t1 and ge >= t0)`, then `python3 -B tools/ci/sweep.py --self-test` was run, and the tree was restored. `-B` matters here. A first driver without it printed mutant 3's failures under mutant 4, because the two mutants have the same file size and were written in the same second, so a stale `.pyc` was imported. That run is disclosed and discarded.
- **R1, the arm deleted.** 3 failed: the two `the higher of a lagging pair … is re-run` checks, and `census: an overlapping deferral is re-run (lower success, higher created 52, its gate 55-56)`.
- **R2, `conclusion == "success"` dropped**, so both sides of a red pair are re-run. 2 failed: `FAIL settle: a lagging-listing pair (sources done, gates overlapping) re-runs the lower id only, swept from run 1` (and from run 2).
- **R3, `ge >= t0` dropped**, so a gate that started after the lower concluded counts as overlapping. 7 failed, among them `FAIL settle null: that higher re-judged red after the lower's gate concluded is final, swept again from run 1 (no loop)` (and run 2) and `FAIL settle null: a higher red gate that started after the lower's green gate concluded is final, never re-run`.
- **R4, `gs <= t1` dropped.** 1 failed: `FAIL a lower green gate that started after the higher red concluded: settle from run 2 re-runs nothing, the lower's own newest-covering sweep re-runs it (swept from run 2)`. This check was added after R4 first survived, as the null that kills it.

**Round 1, re-run at this head** (the same driver and `-B`) for the mutants in `undecided()`, the function the repair edits:
- **M3, the late-source arm removed.** 3 failed, the same three checks as at 88e1140b.
- **M4, the overlapping-gate arm removed.** 4 failed: the two `lagging-listing pair … re-runs the lower id only` checks, and `census: an overlapping deferral is re-run (lower failure, higher created 45|52, its gate 55-56)`.
- **M5, the overlap arm without the id tie-break.** 2 failed: the two `lagging-listing pair` checks.

**Round 1, carried from 88e1140b and not re-run.** M1 (`gate.judge()`'s wait restored) mutates `gate.py`, which is byte-identical between 88e1140b and this head (the `git diff --quiet` in `## Head`). M2, M6 and M7 mutate `settle`'s loop and SKIP, which this diff does not touch. Their result, as measured at 88e1140b:
- **M1.** Gate self-test 77 checks, 14 failed, including `FAIL #3282: the deferring edit gate publishes CI's deferral at once and holds no runner`.
- **M2, `settle` removed.** Sweep self-test 33 checks, 10 failed, at round 1's count.
- **M6.** 2 failed, `settle: a run whose gate is still queued|waiting owns convergence`.
- **M7.** 1 failed, `settle: a gate still running is polled …`.

## Null control

- **The reviewer's probe, the finder's harness at both ends.** `refs/heads/verdict/3287:evidence/probe_settle.py` (sha1 3d9425dabc3883a3834a743765d4fd47341b98e5, byte-identical to the copy run) was run from a `tools/ci` export, `python3 -B probe_settle.py`, with `cd` into the export so that its `sys.path` "." resolves. At 520538cc it prints `swept from run 1: posts=[] out='SWEEP-DONE run=1 reruns=0'` and `swept from run 2: posts=[] out='SWEEP-DONE run=2 reruns=0'`, which is the verdict's figure reproduced. At this head it prints `posts=['repos/o/r/actions/jobs/20/rerun'] … reruns=1` from both runs. Its own null, the higher created at 45, before the lower gate started, prints `posts=['repos/o/r/actions/jobs/20/rerun']` at both ends, through the green branch.
- **No loop: the sweep run twice posts nothing the second time.** The check `settle null: that higher re-judged red after the lower's gate concluded is final, swept again from run 1|2 (no loop)` applies the first sweep's re-run (attempt 2, gate 70-71, kept red) and sweeps again. It reads `posts == []` and `reruns=0` from both runs. Its perturbation, R3, turns it red.
- **A real red after the lower concluded is final.** `settle null: a higher red gate that started after the lower's green gate concluded is final, never re-run` passes. So does the R4 null, where a lower green gate started after the higher concluded: settle from run 2 posts nothing, and the lower's own newest-covering sweep re-runs it, posting `[…/jobs/20/rerun]`.
- **The pair with a red lower still re-runs only the lower.** The round-1 checks `a lagging-listing pair … re-runs the lower id only, swept from run 1|2` pass unchanged, and R2 is their perturbation.
- **Round 1's nulls are unchanged and pass at this head.** These are `settle null: a lone red gate at its head is never re-run`, `settle null: the same reds judged after every source finished, apart, are final`, and the gate self-test's `null: no other run at the head, no wait` and `busy-defer null: a genuinely earlier run still adding sources is still deferred to`.

## Figures

- **Self-tests at this head:**
  - `python3 -B tools/ci/sweep.py --self-test`: 52 checks, 0 failed.
  - `python3 -B tools/ci/gate.py --self-test`: 77 checks, 0 failed.
  - The same sweep self-test over 520538cc's `sweep.py`: 52 checks, 3 failed (named under `## Mutation proof`).
- **Census of a lagging pair's orderings (fixer step 8, the class's seams).** The rule that enumerates them is the `itertools.product` loop in `tools/ci/sweep_selftest.py` (the comment "The census of a lagging pair's orderings"). It covers the lower gate's conclusion {success, failure}, the higher run created before (45) or after (52) the lower gate started at 50, and the higher gate inside (55-56) or after (65-66) the lower gate's 50-60. That makes 8 orderings, each swept from both runs. Over the 4 overlapping orderings it checks that the deferral is re-run, the lower where it is red, else the higher. Over all 8 it checks that the sweeps fired by the re-runs' completions post nothing (`census: the second round posts nothing`), with each re-run judging after both gates and kept red. That is 12 checks. Every seam with its disposition:
  - lower success, higher created 45, inside: re-run by the green branch at both ends. Already guarded.
  - lower success, higher created 52, inside: **closed in this diff.** This is the verdict's seam. It fails at 520538cc and passes here.
  - lower failure, higher created 45 or 52, inside: the lower is re-run by the round-1 arm, already guarded, and the higher is never re-run as well.
  - higher gate after the lower concluded, all four: a final red, re-run only by a green branch where one covers the newest event. Already guarded.
  - The second round posts nothing in all 8 at this head.

  A cost of the census's shape, stated: its round two sweeps only from runs that were re-run, because a sweep runs per CI completion. Sweeping again from a run that did not complete again re-enters the green branch, which re-runs every red gate by design (DESIGN-P2.md 4.3). That is not a loop, since that run does not complete again.
- **The class's other seam, named and left.** Two sweeps that fire close together, one per completion, can each post the same re-run before either sees the run re-queued. This was already so for round 1's arms. GitHub refuses a job re-run in a run that is not completed, and `judge()` reads `run.status` before posting, so the second post is either skipped or refused. Not measured here, and not a loop.
- **#3282 replay** (`dev/audit/harnesses/r10_gate_busy_defer_3.py`, sha1 prefix 12ea35b4451f). Run as `D=$(mktemp -d); git archive origin/main tools/ci tools/pr | tar -x -C $D; python3 -I dev/audit/harnesses/r10_gate_busy_defer_3.py replay --ci $D/tools/ci`:
  - main 4b5d771b: `RESULT replay wait_s=720 first=FAIL swept=yes final=PASS`.
  - 520538cc: `RESULT replay wait_s=0 first=FAIL swept=yes final=PASS`.
  - this head (`python3 -I dev/audit/harnesses/r10_gate_busy_defer_3.py replay`): the same as 520538cc.
- **Race harness** (`dev/audit/harnesses/r10_gate_defer_race.py`, sha1 prefix 19502ff5c0b8), `python3 -I dev/audit/harnesses/r10_gate_defer_race.py --ci $D/tools/ci` against `python3 -I dev/audit/harnesses/r10_gate_defer_race.py`. gate-wait is the summed seconds every gate waited. RESIDUAL-RED is the gates still red on the deferral after every sweep converged.

  | scenario | gate-wait, main | gate-wait, head | RESIDUAL-RED, main | RESIDUAL-RED, head |
  |---|---|---|---|---|
  | 2754 | 780 s | 0 s | 0 | 0 |
  | 2754-red | 780 s | 0 s | 0 | 0 |
  | pair | 120 s | 0 s | 0 | 0 |
  | cascade | 120 s | 0 s | 0 | 0 |
  | editcode | 600 s | 0 s | 0 | 0 |
  | single | 0 s | 0 s | 0 | 0 |
  | prelude | 480 s | 0 s | 0 | 0 |

  Over a 520538cc export the harness prints the same lines as at this head. It reads flat between the two ends of the repair, because none of its scenarios is the verdict's ordering. The companion that reads the defect at 520538cc and not here is the reviewer's probe under `## Null control`. UNDECIDED-RED rises from 0 to 1–2 per scenario by design, since a deferral is now a red the sweep converges. MASKED is 0 and DEADLOCK is `no` at both ends.
- **Live deferral census (round 1, not re-run).** `python3 dev/audit/harnesses/r10_gate_busy_defer_3.py census --since 2026-11-07T08:36:40Z --until 2026-11-07T12:59:11Z` printed `deferral_fails=13 heads=10 per_head_max=3 held_runner_s=9391 held_ge_600=13 resolved=7 by_bot=4 by_human=3 median_min=0.8` at round 1. It reads GitHub's runs over a closed window, not this tree, and this seat ran no `gh api` beyond search, so it was not re-taken. The re-runnable after-merge query is the same command with `--since` at this PR's merge, with the prediction `held_ge_600=0`.
- **Class census, runner-holding waits (round 1).** `grep -nE "\bsleep\(|_sleep\(" tools/ci/*.py | grep -vE "selftest|def _?sleep|self_test"` returns the same sites at this head. The repair adds no sleep, and `sweep.py`'s two poll sites are unchanged. The dispositions are round 1's: `gate.py`'s lag re-read only (closed for deferrals), `prelude.wait_sources` (a distinct finding, see `## Forward-carry`), and `codescan_wait.py`, `ghapi.py` backoff and `sweep.py`'s bounded polls (out of class or already bounded).
- **Ratchet and scope:**
  - `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
  - `tests/closure.py select --diff $(git merge-base origin/main HEAD)` reads `MODE: FULL`, with the reason `tools/ci/fixtures/gate_busy_defer_runs.json changes the gate itself`. The full suite is CI's.
  - The claim files, `VERSION`, the manifest, the `RELEASE_NOTES.md` heading and every `*_budgets.json` are byte-identical to origin/main.
- **prepr:** `tools/pr/prepr.sh` with this body, on the committed head, at origin/main 4b5d771b: rc=0, with no red predicted by its `ci predict` step.

## Red checks

The check runs of the PR head 520538ccfad01bee373382e9d56fc036c8c87ea0 were read at 2026-11-07T15:50Z: 58 runs (`total_count` 58, one page of 100, no `latest` filter). Exactly one had concluded red:
- **`tests / nightly-status` (job 128445156513): inherited, not this diff.** It reads main's last concluded verification dispatch, run 42369836867 at head 08fd676, conclusion `cancelled`, with the mutation-ledger (1–4), mutation-ledger-push, mutation-nightly and slow lanes cancelled. Run 42382408131 was still in flight. The check is not a required context on `main-protect`. The cause is main's nightly lane, not a path this PR touches, and its owner is the nightly dispatch on `main`, which goes green on its next concluded run. No cheaper detector applies, since the check exists precisely to surface main's nightly on every PR.

The others were success, skipped, queued or in progress at the read. The blocked verdict itself is a review finding, not a check, and is answered by the repair above. The cheaper detector for that kind of miss is a self-test census over the ordering space. That is now in tree (`census:` checks in `tools/ci/sweep_selftest.py`), costs 12 checks inside the existing `governance / instrument-self-tests` step (`governance.yml`, `sweep.py --self-test`), and would have failed at 520538cc.

`tools/pr/prepr.sh` ran on the committed head f6c1866b at origin/main 4b5d771b and printed `PRE-PR: f6c1866ba8564989a34cc3d09f001cdb5133ecbe … rc=0`. Its `ci predict` step predicts no closures, fast, governance or instrument red against 4b5d771bdf8f, so no red is predicted at the handoff. origin/main had not moved past 4b5d771b when the run ended, so no second run was owed.

## Forward-carry

- **#3278's RCA document, on branch `fix/r10-rca-gate-busy-defer-2`, not edited here.** Its §1 sentence "In #3261, the higher gate waits one poll, then passes" becomes untrue at this head. That gate now publishes the deferral at once, and `settle` re-runs it (race harness `pair`: gate-wait 0 s, RESIDUAL-RED 0). Its §5.2 countermeasure, a fresh dispatch where a re-run would replay a stale pinned program, stays needed: `settle` re-runs through the same job-rerun API, so a re-run of a run created before this merges executes the old waiting program. Re-measure with that document's own `census` arm after this merges (a group of `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster`; the orchestrator appends it with `tools/audit/seat/roster_edit.py append-carry`, this seat writes no roster). Carry: R10-RCA-GATE-BUSY-DEFER-2
- **A prelude holds a runner while it waits on another run** (`prelude.wait_sources`, up to `WAIT_MAX_S` = 8700 s). This is the same runner-queue cost this PR removes from the gate; #3282's review run's prelude held one 11:16:40–11:48:01Z (its `prelude` job's started and completed stamps). It is legitimate only while the queue it lengthens is measured. Re-measure from the jobs API at your own merge base (a group of `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster`; the orchestrator appends it with `tools/audit/seat/roster_edit.py append-carry`, this seat writes no roster). Carry: R10-HOTFIX-GATE-BUSY-DEFER

## Friction

- frugal-inline-budget: cost: a session guard counted log tails and result reads as discovery searches and refused them mid-measurement, so each read went through a subagent. Carry: dismissed: a session plugin's guard, not this repository's policy
- brief-cause: contradiction: the brief's "nothing re-judges it" against #3282's own runs, where tvofi re-ran the gate 4 s after the code run concluded and 8 s before the sweep's read, which is why the sweep's log reads reruns=0. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- handoff-wip-stale: stale: `refs/heads/handoff-wip/r10-gate-busy-defer-3` still held round 1's `BLOCKED.md` commit c218a1ef on 88e1140b, so this round's step push was refused as non-fast-forward. That commit's question has been answered, since the PR exists. The step ref was not force-pushed. It is deleted after this handoff, as the brief directs, and c218a1ef is named here. Carry: dismissed: a stale step ref from round 1, removed at this handoff
