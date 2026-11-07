Fix review: blocked a8c36900eed9a789e2bab2eee70ffc883f1a608f class-open: the classify CLI exits 1 RED in the gate-sweep settle gap, live at this head 18:16:12Z

bus-nonce: 5a2baec6a7dcf5c6acf30fe8b4a9196d

## Block

Round 2 of the fix review (first round blocked at 43a9d584, class-open). The round-2 remedy is wired correctly: the `classify` CLI (`classify_cmd` -> `Train.classify_at`) and proof_watch `required_state` (`Train.classify_at`) now both use the shared `_gate_busy` predicate, and wait-ci takes the settle. While the code run runs, the deferral is a WAIT on every reader. That was reproduced live (see Evidence).

What is still open is one domain of the same predicate on the one-read readers: the **settle gap**. After the code run completes (its `gate` green, every unit done, so `busy` is empty), the edit suite's deferral red is still the worst-suite `gate` until gate-sweep.yml re-runs it. `classify_at` deliberately takes no settle there. Its docstring and the instrument doc say "the caller's next read sees the sweep", and the self-test pins RED ("defer-wait CLI: one read takes no settle -- a red beside a green suite with nothing busy is RED"). That disposition is false for the CLI's callers, because none of them re-reads on RED:
- `bus.sh` (:587) refuses a dispatch on rc 1. A review dispatch is refused for a head that is going green.
- `postmerge.py` (:49) reports the last line.
- The reviewer seats' CI wait (cloud_dispatch prompt :208/:1036) stops at exit 1 and judges the head RED.

**Live at this head**, with the head's own code (worktree at a8c36900eed9a789e2bab2eee70ffc883f1a608f):
- The code run 42397572783's `gate` went green at 18:16:00Z (check run 128486567216).
- `merge_train.py classify a8c36900eed9a789e2bab2eee70ffc883f1a608f --pr 3290` at 18:16:12Z printed `RED ... pending: none red: gate` and exited 1.
- gate-sweep's re-run of the edit gate started at 18:16:18Z (128486820605).
- The next read printed `GREEN ... red: none`, rc 0.

So this very reviewer's waiter ended on a false RED. The window was 18 s against a 60–70 s poll, so roughly a quarter of polling callers land in it.

The remedy is the fixer's design call. Some options:
- (a) In `classify_at`, read a red GATE beside a green GATE suite whose completion is recent (bounded, e.g. within SWEEP_SETTLE_POLLS * HEARTBEAT_SECONDS of the read) as WAIT, and RED after that, so a sweep that never comes still ends RED.
- (b) Read gate-sweep.yml's runs at the head the same way `_gate_busy` reads ci.yml's.
- (c) Give each CLI caller a re-read on RED. This one is weaker: it makes three copies.

Whichever is chosen, add a self-test case from this scene and flip the pinned "one read takes no settle" case.

## Findings

- Follow-up: the body's `## Figures` and `## Mutation proof` were not re-taken at this head. They quote `478 checks` and M1–M3 at 478, but the self-test at a8c36900eed9a789e2bab2eee70ffc883f1a608f prints `merge_train self-test: 485 checks, 0 failed`. They carry no mutant for the round-2 lines (`classify_at`, `classify_cmd`, proof_watch `required_state`). The class-enumeration list also omits the `classify` CLI and proof_watch readers this head closes. All of this is owed at the repair head. Carry: R10-HOTFIX-TRAIN-DEFER-WAIT
- Residual: a surviving mutant, M9. Routing `classify`'s log to stderr (`**({"log": ...stderr} if a.cmd == "classify" else {})` -> `**({})`) leaves both self-tests green, so the line is untested. It is equivalent under every current caller: the only log line on that path (`runs listing is unreadable`) precedes the verdict line. `bus.sh` reads `tail -n 1` of 2>&1, `postmerge.py` reads the last stdout line, and `review_packet.py` uses an `re.M` anchored search. Carry: dismissed: equivalent mutant under all three stdout readers (bus.sh, postmerge.py, review_packet.py)

## Evidence

- Head reviewed: a8c36900eed9a789e2bab2eee70ffc883f1a608f (ev/HEAD.txt), merge base 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76. Roles dir unchanged between merge base and origin/main (0-line diff).
- Self-tests at the head: `merge_train self-test: 485 checks, 0 failed`, `proof_watch self-test: 44 checks, 0 failed` (ev/mt-selftest.txt, ev/pw-selftest.txt).
- My targeted mutants on the round-2 lines (ev/mutants.txt), each applied, run and restored:
  - M4 (`classify_at` busy -> []): merge_train 2 failed (the CLI #3248 and CLI unreadable cases), proof_watch 2 failed (g3).
  - M6 (CLI back to the base `classify(latest_runs(runs), req)`): merge_train 2 failed.
  - M7 (proof_watch `required_state` back to the base reading): proof_watch 2 failed (g3 aborts with REQUIRED RED).
  - M8 (wait-ci all-runs settle dropped): merge_train 2 failed.
  - M1 re-run: merge_train 4 failed, matching the body.
  - M9 survives (see Findings).
  - Null control: a docstring perturbation gives 485/0 and 44/0.
  - M5 equivalent-mutant dismissal: stands per the brief, not re-judged.
- Class enumeration (ev/class-grep.txt, `git grep -n "classify("` plus classify_at/classify_cmd):
  - CLI `classify` (:8101 -> `classify_cmd` :519 -> `classify_at`) and proof_watch.py:234: both on the shared predicate.
  - `wait_ci` :1644/:1659: on the predicate.
  - `approval_owed` :544, `main_green` overlap :3148 (main has no edit run), orchestrator_tick.py :1151/:1648 (tick report lines): unchanged, consistent with the body's disposition.
- Live repro of the round-2 class at 18:01:41Z (ev/live-repro.txt), while code run 42397572783 was in_progress and edit run 42397572454's gate log said `FAIL run(s) [42397572783] at this head are still being judged; their gate decides`:
  - origin/main's code: `RED ... red: gate`, rc 1.
  - The head's code: `WAIT ... pending: gate`, rc 3.
  - My first waiter mistakenly ran origin/main's code and ended RED at 17:58:45Z (ev/classify-base-code.log), which is the base defect.
- The waiter on the head's code (ev/classify-run1.log): WAIT from 18:01:47Z to 18:15Z, then false RED at 18:16:12Z, then GREEN rc 0 at about 18:17Z (ev/classify.log). Gate rows: ev/gate-rows-1816.tsv, ev/check-runs-final.tsv, ev/ci-runs-final.tsv.
- CI at the head, judged job by job over all check-run pages (55 rows): every required context is green at the final read. The only concluded red is `tests / nightly-status` (failure at 17:49:36Z), which is not this PR's: the diff does not reach what it reads. `## Red checks: none` is consistent with that. The deferral red was superseded by gate-sweep's re-run, now green.
- Merge with origin/main aaaec212: `git merge-tree --write-tree` rc 0, tree 32e9db28 (ev/merge-tree.txt).
- #3287 interaction: #3287 has merged on main as cc100c275 (gate.py busy/judging). This PR touches neither gate.py nor gate-sweep.yml. On the merged tree the self-tests print `merge_train self-test: 492 checks, 0 failed` and `proof_watch self-test: 44 checks, 0 failed` (ev/merged-selftest.txt), including the table that pins `gate_busy` equal to gate.py's own `busy`. No copy of the deferral grammar was added: gate.py's `busy` is imported from its tree path.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: rc 0 (ev/entities.txt). `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (ev/structure.txt).
- The diff has 5 files: the delivery row dev/programme/delivery/3290.md is present, and no budget file, VERSION, manifest or RELEASE_NOTES.md is touched. `## Head` names a8c36900eed9a789e2bab2eee70ffc883f1a608f.
- Figures I could not re-derive: the s12 study's 56/32/10 SKIPs, 27 re-merges and about 3,500 runner-minutes. Its harness is not in the tree, and the body says so.
- The scheduled brief said never to send a push notification, so none was sent.
