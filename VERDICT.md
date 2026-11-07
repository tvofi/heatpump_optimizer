Fix review: blocked a38bd141ec8b42fc8d2bcd17090be1814ca97d83 class-open: classify_at reads the gate-sweep settle gap RED, so the classify CLI exits 1 and proof_watch aborts REQUIRED RED on a head going green

bus-nonce: 84365b92cf429ac148e09c02b7af75d5

## Block

This is the round-2 review: the repair after the round-1 block at 43a9d584. The PR holds three verdicts in all: 43a9d584 (round 1), then a8c36900 (`probe/rev-3290-5a2baec6`, published as verdict/3290 7d351ea6), then this one.

What round 2 asked for is wired correctly. Re-running `git grep -n "classify(" -- tools/audit/seat` at this head (ev/grep-classify.txt) shows:
- the `classify` CLI goes `main` -> `classify_cmd` (merge_train.py:546) -> `Train.classify_at` (:1633);
- proof_watch `required_state` (proof_watch.py:234) goes through `Train.classify_at`;
- `wait-ci` (no `only`) takes the one-poll sweep settle (:1695ff).

While the code run is still running, every reader reads the deferral as WAIT/pending.

The block is the one domain left open, and the a8c36900 verdict had already named it: the **settle gap**. Once the code run completes, its `gate` is green and every ci.yml run is completed, so gate.py's `busy` names nothing. But until gate-sweep.yml re-runs the edit gate, the edit suite's deferral red is still the worst `gate`. `Train.classify_at` takes no settle there. Its docstring says "the caller's next read sees the sweep", and the self-test pins that case as RED ("defer-wait CLI: one read takes no settle"). The code is unchanged since a8c36900: `git diff a8c36900 HEAD -- tools/audit/seat/merge_train.py` has no line touching `classify_at`, `_gate_busy` or the settle. The body never names that verdict or the gap. The disposition it gives ("a single read cannot wait; the caller's next read sees the sweep") is false for every caller of the one-read path:
- **proof_watch** `watch()`. At :354-356, a red from `required_state` raises `Abort("REQUIRED RED ...")`. The watch does not re-read; it aborts the merge. So the merge path the brief's FOCUS (1) protects ("do not SKIP a pull request that would go green") still fails in the gap. The (g3) case skips the gap entirely: its `landed` sleep jumps from the running code run straight to the swept green.
- **bus.sh** :587-591. On rc 1 the dispatch dies ("not reviewable"). A review dispatch is refused for a head that is about to go green.
- Reviewer and dispatch seats. Their wait (this brief included) stops at exit 1 and judges the head RED.
- **ci-watch.sh** `gate_deferred`. It keeps the red on RED, so the gap raises a false `RED: gate` wake. That is less harmful, but it is the same seam.

**Measured at this head** from its own recorded runs (ev/ci-runs-head.tsv, ev/gate-rows-head.tsv):
- Code run 42404526059 completed at 20:02:31Z, with gate 128512781341 success.
- gate-sweep re-ran edit runs 42404527136 and 42406706258 as attempt 2 from 20:03:33Z.
- The re-run gate check runs 128513382838 and 128513383466 started at 20:05:39Z.

Replaying the recorded check runs and ci.yml runs, cut at time T, through the head's own `classify_cmd` (ev/replay-gap.txt; my own driver ev/replay_gap.py, not the finder's) gives:

| T | head | base 364353e6 |
|---|---|---|
| 19:30Z, code run running | `WAIT ... pending: gate`, rc 3 | `red ['gate']` |
| 20:03Z, settle gap | `RED ... red: gate`, rc 1 | `red ['gate']` |
| 20:04Z, settle gap | `RED ... red: gate`, rc 1 | `red ['gate']` |
| 20:07Z, swept (null control) | `GREEN`, rc 0 | `green` |

The 20:03Z and 20:04Z rows are false REDs. At 20:04Z the attempt-2 runs are in progress but `judging()` reads them as not busy, because only their gate is left to run.

At this head the gap is about 188 s (20:02:31Z to 20:05:39Z). At a8c36900 it was 18 s. So any caller polling every 60–70 s lands in it at least twice, and proof_watch's single red read aborts.

Remedy: the fixer's design call. Two options:
- (a) Give `classify_at` the settle: a red GATE beside a green GATE suite whose completion falls within a bound of the read (for example SWEEP_SETTLE_POLLS × HEARTBEAT_SECONDS, or the sweep's own start latency) reads WAIT, and RED after the bound, so a sweep that never comes still ends RED.
- (b) Read gate-sweep.yml's runs, or the edit run's re-run attempt, at the head, the way `_gate_busy` reads ci.yml's.

Either way, the remedy needs:
- a self-test scene from this head's 20:02:31Z–20:05:39Z window through both the CLI and proof_watch;
- the pinned "one read takes no settle ... is RED" case flipped to WAIT within the bound, and a null past the bound;
- the a8c36900 verdict answered in the body.

## Findings

- Follow-up: `## Red checks` is stale at this head. It is read over 43a9d584's check runs and says "This round's own head has no CI yet". This head has two concluded reds, both `gate` deferrals: 128499580417 (edit run 42404527136 attempt 1, failed 19:19:15Z) and 128507622651 (edit run 42406706258 attempt 1, failed 19:53:38Z). Both logs say `FAIL run(s) [42404526059] at this head are still being judged; their gate decides` (ev/head-gate-red-logs.txt), and gate-sweep re-ran both green at 20:06Z. They are the same class the body already answers. `pr-contract / pr-contract` 128511434495 started 20:00:32Z, after the last red concluded, and is green, so this is not a root-cause block. The section must still name this head's check runs when the head is re-cut. Carry: R10-HOTFIX-TRAIN-DEFER-WAIT
- Residual: M9 survives. It routes the `classify` log to stderr (`**({"log": ...stderr} if a.cmd == "classify" else {})` -> `**({})`), and every self-test stays green. It is equivalent under every current stdout reader, as the a8c36900 verdict judged and I re-checked: bus.sh reads `2>&1` but keys on the `RED `/`APPROVAL-OWED ` line, and the only log line precedes the verdict line. Carry: dismissed: equivalent mutant under all current stdout readers (bus.sh, postmerge.py, review_packet.py)

- Residual: mutant R5 survives (`_gate_busy`'s `except ValueError: ci_runs = None` -> `ci_runs = []`). A malformed listing then gives the same verdict, nothing busy and the red standing, but without the "unreadable" log line. Only the log line goes untested, and the self-test covers the rc≠0 unreadable path. Carry: dismissed: outcome-equivalent, only the diagnostic log line differs
- Residual: mutant R6 survives (ci-watch `gate_deferred`'s `case " ${out##* red: } " in *" gate "*) return 1` -> `true`). It is equivalent: `classify` returns `wait` only when its red list is empty, so a `WAIT` line never names `gate` red. Carry: dismissed: equivalent mutant, classify's WAIT carries an empty red list by construction

## Evidence

- Head reviewed: a38bd141ec8b42fc8d2bcd17090be1814ca97d83 (ev/HEAD.txt).
  - Merge base: 364353e670f666be6c97a5942ffa0bea9132b5ce. origin/main is at 53273de4d449a990bc29734565f63babada9ff7f.
  - The roles directory is unchanged between the merge base and origin/main (0-line diff).
  - The body's `## Head` names this head.
- CI at this head: `merge_train.py classify a38bd141... --pr 3290` printed `GREEN ... pending: none red: none`, rc 0, on its first read at 20:34:57Z (ev/classify-log.txt).
  - All 94 check runs were read on one paginated listing (ev/check-runs-head.tsv, ev/check-runs-head.jsonl). The only concluded non-success, non-skipped rows are the two `gate` deferrals named under Findings.
  - Every required context's latest run is green. `governance / instrument-self-tests` and `tests / nightly-status` are success at this head.
- Self-tests at this head: `merge_train self-test: 492 checks, 0 failed`, `proof_watch self-test: 44 checks, 0 failed`, `ci-watch self-test: 18 checks, 0 failed` (ev/selftests-head.txt). These match the body's figures.
- On the merged tree (this head merged with origin/main 53273de4, which includes #3287 5c1fa41f, commit 20114e24 built locally), `gate.py`'s `busy` signature is unchanged, and the self-tests print (ev/selftests-merged.txt):
  - merge_train: 492 checks, 0 failed;
  - proof_watch: 44 checks, 0 failed;
  - ci-watch: 18 checks, 0 failed;
  - gate: 77 checks, 0 failed.
  - The defer-wait table pins `gate_busy == gate.py busy`.
  - This PR touches neither gate.py nor gate-sweep.yml, and no copy of the deferral grammar is added.
- `git merge-tree --write-tree origin/main HEAD`: rc 0, with no conflict (ev/merge-tree.txt).
- My targeted mutants (ev/mutants.txt). Each was applied by an exact one-occurrence replacement, run, and restored, and the tree was clean afterwards:
  - MA (`classify_at` busy -> []): merge_train 2 failed (the CLI cases), proof_watch 2 failed (g3).
  - MB (proof_watch reader reverted): proof_watch 2 failed.
  - MC (CLI reader reverted): merge_train 2 failed.
  - MD (wait-ci settle off): merge_train 2 failed.
  - ME (ci-watch predicate off): ci-watch 1 failed (W13).
  - R1 (`deferred = {GATE}` unconditionally): merge_train 33 failed, proof_watch 3 failed.
  - R2 (deferred gate kept in `red`): merge_train 2 failed, proof_watch 2 failed.
  - R3 (settle bound 1 -> 99): merge_train 1 failed.
  - R4 (jobs map dropped in `gate_busy`): merge_train 1 failed.
  - R5, R6 and R7 (= the a8c36900 verdict's M9) survive; see Findings.
  - Nulls (comment-only edits in `classify_at`, `required_state` and `gate_deferred`): 492/0, 44/0 and 18/0.
  - The body's MA to ME match where re-run.
  - The M5 equivalent-mutant dismissal stands, per the brief.
- Diff hygiene: the diff has 7 files, and the delivery row dev/programme/delivery/3290.md is present. No VERSION, manifest, RELEASE_NOTES.md or `*_budgets.json` file is touched, and `tests/structure.py` prints `STRUCTURE RATCHET PASSED` (ev/structure-entities.txt). No new tracked file except the delivery row.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `3 of 2645 ENTITY CHECKS FAILED` both at this head and at the merge base 364353e6 (ev/entities-head.full, ev/entities-base.full). The three are identical at both ends and are container-environmental:
  - the coverage-cache marker probe;
  - the release ZIP build step;
  - the Pages-workflow probe.
  This PR adds none of them, and CI's gate (which ran tests/entities.py in scope) is green at this head.
- Figures I could not re-derive: the s12 study's 56/32/10 SKIP counts, 27 re-merges and about 3,500 runner-minutes. The study's harness is not in the tree, and the body says so. The replay driver ev/replay_gap.py is my own instrument, not the finder's.
- The settle gap rests on the head's own pinned self-test case and on my replay of this head's recorded runs. I did not observe it live in this session, because my first live read at 20:34:57Z came after the sweep. The a8c36900 verdict observed it live at 18:16:12Z on identical `classify_at` code.
