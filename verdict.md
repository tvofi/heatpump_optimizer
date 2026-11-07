Fix review: blocked 43a9d5842392426ea06806affa479461f6017645 class-open: merge_train.py:8013 classify CLI and proof_watch.py:226 read a deferral red as RED, undispositioned

bus-nonce: 43d186d67f27454563fb99abb0686157

Round: first.

## Block

- The body's class rule is `git grep -n "classify(" -- tools/audit/seat`. At this head it returns seven merge_train/orchestrator_tick/proof_watch readers of `merge_train.classify` (ev/class-grep.txt). The body dispositions `wait_ci` (closed), `approval_owed` (:529), `main_green` (:3115) and `orchestrator_tick` (:1151, :1648), and says the proof waits share `wait_ci`. Two readers it returns are in neither the diff nor the body:
  - `tools/audit/seat/merge_train.py:8013`, the `classify` CLI subcommand. Dispatch and every reviewer seat use it to wait for CI ("exits 1 RED"). It calls `classify(latest_runs(runs), req)` with no `busy`, so a deferring edit gate reads as a final RED while the code run runs. That is the defect this group exists to remove, at the seam the brief's focus (1) names ("classify").
  - `tools/audit/seat/proof_watch.py:226`, `required_state`. It calls `_train().classify(last, self.required_names())` with no `busy`. This is a separate check-runs read, not `wait_ci`, so the body's "proof waits share wait_ci" does not cover it.
- I saw this happen live on this PR's own head. At 16:22:14Z `merge_train.py classify 43a9d584... --pr 3290` exited 1 with `RED ... pending: none red: gate` (ev/classify-log.txt). Both red gates are edit-run deferrals: runs 42387524862 and 42387655386 each log `FAIL run(s) [42387525051] at this head are still being judged; their gate decides` (ev/edit-gate-logs.txt). Code run 42387525051 was still `in_progress` at that time (ev/ci-runs.txt). On the same live reads, this PR's own `gate_busy` returns `[42387525051]` and `classify(..., busy)` returns `('wait', ['gate'], [])`, but the CLI's call returns `('red', [], ['gate'])` (ev/live-seam.txt).
- Remedy: route the CLI `classify` (and `proof_watch.required_state`) through `Train._gate_busy` when GATE reads red, with a self-test case (the #3248 frame read through the CLI path). Alternatively, give each reader a reasoned disposition in the body. Either way, also disposition the `wait-ci` subcommand (:8000, `only=None`).

## Findings

- M5 survives: the mutant drops `{} if status == "action_required" else` in `gate_busy`. The self-test still reads 478 checks, 0 failed. This is an equivalent mutant: gate.py `busy` excludes `action_required` by status before it reads `jobs`, so the mapping only mirrors gate.py's read_api shape. Carry: dismissed: equivalent mutant, busy() filters that status first

## Evidence

- Head reviewed: 43a9d5842392426ea06806affa479461f6017645 (ev/HEAD.txt). Merge base: 1c1ae100b59e. Three-dot diff: dev/programme/delivery/3290.md (new, the delivery row), tools/audit/seat/merge_train.py, tools/audit/seat/instruments/merge_train.py.md. VERSION, the manifest and RELEASE_NOTES.md are untouched.
- `git merge-tree --write-tree origin/main HEAD`: clean. Merged with #3287's head 520538cc: clean (tree 8e94e233), and the merge_train self-test on that combined tree gives 478 checks, 0 failed (ev/combo-3287-selftest.txt). gate.py's `busy(ctx, runs)` signature and the jobs shape are unchanged by #3287, so there is no dependency or conflict.
- `python3 tools/audit/seat/merge_train.py --self-test` at the head: 478 checks, 0 failed. This matches the body.
- Mutation proof, re-run by me, each restored afterwards (ev/mut-*.txt):
  - M1 (`busy = []`): 4 failed. Matches the body, including the named 13:01Z case.
  - M2 (`deferred = set()`): 4 failed. Matches.
  - M3 (settle off): 2 failed. Matches.
  - M4 (my own: per-suite jobs replaced with `{}`): 1 failed, the judging table row.
  - M6 (my own: `SWEEP_SETTLE_POLLS` set to 50): 2 failed, including the bound case.
  - Null control (comment-only edit): 0 failed.
- The finder's harness: none is named or committed. The 56/32/10 SKIP figures and about 3,500 runner-minutes come from the s12 study, whose harness is not in the tree. I could not re-derive them, and the body says so too. The #3248 and 13:01Z scenes are self-test frames, not recorded-run replays.
- On the train path the fix is sound. A red with no busy run still SKIPs on its first poll. A code-run red gets no settle. The wait is bounded by `polls` (TIMEOUT). An unreadable listing leaves the red standing. No second copy of the deferral grammar is added: `busy` is imported from tools/ci/gate.py.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED; no budget moved. `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2645 ENTITY CHECKS PASSED (ev/entities.txt). `tests/closure.py select`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`.
- CI at the head, read at 16:22Z (ev/check-runs.txt): the code run 42387525051 is still in progress. `gate` is red twice, and both are edit-run deferrals. `tests / nightly-status` is red, which is not this PR's: the diff does not reach what it reads. I did not judge `## Red checks` (step 11), because the head's workflows have not all concluded.
