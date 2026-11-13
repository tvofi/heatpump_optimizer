R10-GATE-DEFER-BARRIER, part 2 (carries 5, 7, 8, 9, 10; carry 6; carries 0-4 are part 1, merged as #3499): the train waits on a queued gate-sweep run before it reads a red gate as final, the gate stops reading a run's own re-queued needs as an unfinished unit, `merge_pr.sh` no longer posts a second verdict for a head the bus already posted, and the code-owned approval cites a bare mandate id in a form `MANDATE_CITE` reads.

- Carry 1, Carry 2, Carry 3 and Carry 4 (the brief's stale line 'Part 1 of 2: build carries 0-4', ruled out by the orchestrator's opening section): built in part 1 and merged as #3499 (`git log origin/main --oneline --grep='r10-gate-defer-barrier'` names the merge); nothing in them is changed here.
- Carry 5 (GATE-SWEEP-QUEUE-WAIT): `Train._sweep_busy` reads one `gate-sweep.yml/runs?created=>=<newest green gate suite's completed_at>` listing; a queued or in-progress run there is a wait in `wait_ci` (both branches) and in `classify_at`, bounded by `polls` (TIMEOUT). No green gate suite, an unreadable or empty listing, or only completed runs: red after the settle poll, as before. `latest_runs`' worst-suite rule is untouched.
- Carry 6: already on main, `rollup_walk` (`tools/audit/seat/merge_train.py`); no change here.
- Carry 7 (GATE-BUSY-REQUEUED-NEEDS): under the orchestrator's approved bounded extra read. `prelude.prior_jobs` reads `actions/runs/<id>/attempts/<n-1>/jobs` once per poll for a run that is unfinished, has `run_attempt` above 1 and has an owed need missing or not completed in its `filter=latest` listing; `judging()` then reads that need from the previous attempt where it completed (option "judging() reads the pre-rerun sources", not "busy() discounting"). Wired in `gate.read_api` and `prelude.wait_sources`. A need unfinished in both attempts, absent from the previous listing, or an unreadable previous listing (logged to stderr with the path and HTTP status) keeps today's reading. `busy()` and its lower-id tie-break are unchanged.
  Interpretation, stated: the ruling's trigger is "skipped or missing". A skipped need is a completed job that `judging()` already reads as finished, so a read for it could not change a judgement and is not made; the state that makes a run busy is a re-queued need listed unfinished (run 43022147048 attempt 2: `pr-contract / pr-contract` queued), and that is the trigger together with missing. The recorded fixture the ruling names is constructed, not recorded (`tools/ci/fixtures/gate_requeued_needs_runs.json`, its `note` says so): attempt 1 every need concluded, attempt 2 `pr-contract / pr-contract` queued.
  Added API cost per poll: one GET per ci.yml run at the head that is unfinished, has attempt above 1 and a need unfinished or missing; zero otherwise. Enumerator: `gh api 'repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs?head_sha=<head>' --jq '[.workflow_runs[]|select(.status!="completed" and .status!="action_required" and .run_attempt>1)]|length'` (an upper bound: runs whose needs are all finished make none).
- Carry 8 (MERGE-PR-NO-REPOST): `merge_pr.sh` reads the newest posted verdict through the new `merge_train.py posted-verdict <pr>` (the add check's own `bus_posted`); for this head it prints `ALREADY POSTED: comment <id>` and posts nothing, otherwise posts as before; the `Evidence:` line form is unchanged.
- Carry 9: the approval body under a bare numeric `--mandate` reads "under mandate comment <id>"; a URL-form mandate keeps its label.
- Carry 10: not reproduced, dismissed (`## Forward-carry`).

## Head

868f8a726bf29471b5f0b42b2e514b83e03cd865, on origin/main e23124ff6e45bac1d48b4a775dad555a37965355 (`git ls-remote origin refs/heads/main` unchanged at 2026-11-13T21:17:17Z, so no merge); `git merge-tree --write-tree origin/main HEAD` reported no conflict.

## Mutation proof

Each mutant is a one-line `str.replace` on the committed file, run against the named self-test, restored with `git checkout`.
- Carry 7, `python3 -I tools/ci/gate.py --self-test` (baseline 97 checks, 0 failed): drop the overlay (`(prior.get(k) or ("",))[0] == "completed"` to `False`) fails "requeued needs: a run whose only unfinished job is its re-queued need, finished in attempt 1, is not busy"; drop the attempt guard (`if attempt <= 1 or all(` to `if all(`) fails "requeued needs null: a single-attempt run makes no extra read"; drop the trigger guard (always read) fails "requeued needs null: an attempt-2 run with every need finished makes no extra read". `python3 -I tools/ci/prelude.py --self-test` (81 checks, 0 failed): the overlay mutant fails "requeued needs: wait_sources does not wait on a lower run whose only unfinished job is a need finished in attempt 1". Equivalent, not killed: making the overlay accept any non-empty previous status; `judging()`'s own `completed` test after it still rejects it.
- Carry 5, `PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test` (baseline 753 checks, 0 failed): `_sweep_busy` returning None for a queued sweep fails 4 checks (the queued-then-in-progress wait, the TIMEOUT bound, "wait-ci: every run concluded, a queued sweep is waited on too", "classify_at: a queued sweep reads WAIT"); dropping `_sweep_busy` from `wait_ci`'s first branch fails the `classify_at` check only, so that branch is pinned by the first of the four through the other mutant.
- Carry 9: `under = self.mandate` fails "the code-owned approval body for a bare numeric --mandate id is read by MANDATE_CITE as that comment id and is worded `mandate comment <id>`" (753 checks, 1 failed).
- Carry 8, `bash tools/audit/seat/merge_pr.sh --self-test` (baseline 28 checks, 0 failed): replacing the posted-verdict condition by `false` fails "a verdict the bus already posted for the head is not posted again, and the merge goes on" (28 checks, 1 failed).

Diff-mutant pass: `tools/pr/prepr.sh` at this head with `MUTANT_IN_PLACE=1 MUTANT_CMD="env PYTHONPATH=tests/hastub python3 tools/audit/seat/merge_train.py --self-test"` drew 11 survivors (rc=0, the step is a WARN). Disposition: eight are constants and stubs inside `_sweep_queue_self_test`'s own fixture (`H`, the two check-run ids, the sweep run id, the call counter, and the unstubbed-command branch of `drive`'s `run`: nothing reads those values except as keys the fixture itself builds); `settle += 2` in `wait_ci` changes the settle count only after a poll that the sweep wait already bounds by `polls`, and no check observes a settle of 3 against 1 there; `merge_train.py:672` is `green_gate_end`'s `except` branch (an unreadable stamp reads None), which no check drives, so it is the one survivor that is a real untested branch of this diff; and the call at line 7846 is `_sweep_queue_self_test(check)` in `_self_test`: deleting it cannot fail the self-test that is also `MUTANT_CMD`, and the mutation proof above runs that block's checks through real production mutants.
Carry: dismissed: fixture constants and an equivalent counter on lines this diff adds; the unread-stamp branch is the same read `sweep_settling` made before this diff

## Null control

- Carry 7: a single-attempt run makes 0 extra reads and its unfinished need keeps it busy (id returned); a need unfinished in attempt 1 too stays busy after 1 read; a need absent from attempt 1 stays busy; an HTTP 404 on the previous attempt stays busy and logs `unread ... HTTP 404`; an attempt-2 run whose needs are all finished makes 0 reads. The fixture run (attempt 2, need queued, attempt 1 concluded) is judged not busy after exactly 1 read. The tie-break checks ("busy-defer ...") are unchanged and green in the same 97.
- Carry 5: a completed sweep with the red unchanged is RED after the settle poll; no sweep run is RED; no green gate suite beside the red makes no listing read; a sweep that stays queued ends TIMEOUT within `polls`.
- Carry 8: a posted verdict that is not `verdict/<pr>`'s tip posts as today.
- Carry 9: a `--mandate` given as an issuecomment URL keeps its label.
- Carry 10: `git worktree add --detach <dir> origin/main && cd <dir> && bash tools/audit/seat/tick_loop.sh --self-test` printed `tick_loop self-test: 42 checks, 0 failed` and `git rev-parse HEAD` read e23124ff6e before and after. Source: `fresh_check` is the only HEAD mover (`checkout -q --detach origin/main`) and the self-test points `HPO_TICK_CODE_DIR` at an empty directory, so it returns early.

## Figures

- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: FULL -- every test script runs, nothing is scoped out`, reason: the diff touches a gate file (`tools/ci/`). Not reproduced locally; CI runs it.
- `python3 -I tools/ci/gate.py --self-test`: 97 checks, 0 failed. `python3 -I tools/ci/prelude.py --self-test`: 81, 0 failed. `merge_train.py --self-test`: 753, 0 failed. `merge_pr.sh --self-test`: 28, 0 failed. `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `python3 tools/pr/ci_predict.py`: no closures, fast, governance or instrument red predicted.
- Finder instrument for carry 7's class (a run read busy beyond its genuine unfinished units): the two readers of `judging()`, `gate.busy` through `gate.read_api` and `prelude.wait_sources`; both are given `prior` in this diff. The train's own `merge_train.gate_busy` builds its runs from its own reads and has no previous-attempt listing, so it still reads such a run busy: the conservative direction (WAIT). Carry: dismissed: a wait, never a false green; the gate-side read is what ended the deferral red the train re-read.

## Red checks

none. No CI run exists at this head; `tools/pr/ci_predict.py` predicts none.

## Forward-carry

- Carry 10 (`tick_loop.sh --self-test` moving HEAD): not reproduced in a detached worktree at origin/main (`## Null control`). Untested: a probe behind origin/main, a run on a local branch, and whether `pr_args.sh` resets the environment; the cause is not established and no code changed. Re-measure: run the self-test in a detached worktree and on a local branch, `git rev-parse HEAD` before and after. Carry: dismissed: not reproduced at origin/main, with the untested arms named
- Carry 0 of the brief (re-measure RCA 5.2 with its `census` arm): part 1's body already carried it. Carry: dismissed: carried in part 1 (#3499)

## Friction

none
