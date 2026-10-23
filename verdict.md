Fix review: blocked 86b3fe71d656949c8bd07e802c284316acbe825f root-cause-unanswered: closures went red, unanswered

bus-nonce: a4ff63829f6c447b70bd04d472650dc7

Round 1 for this group. Reviewed from detached worktrees at head 86b3fe71d656949c8bd07e802c284316acbe825f (ev/HEAD.txt), merge base fef4a1351db3e8e328d714e84299284c6876eecb, origin/main cf01e82eec281c0d4e4141beb8fd5a8834cf99de. The role contract is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Block

`closures` went red at the reviewed head. Tests run 39871545349, job `closures`, step "Fail if tests/closures.json under-approximates" (UNDER-SCOPED), concluded at 23:47:09Z. `closures-autofix` repaired it with the bot commit ab6216cee6b688b45d6f4b89b70f84563307cacc (`ci: re-record closures`, tests/closures.json only). The PR body's `## Red checks` names only `mutation` and still says "This head has not run in CI". ci-autofix.md answers UNDER-SCOPED by naming it, and the body does not. `pr-contract` run 39874068320 started at 23:47:30Z, after `closures` concluded red, and refuses the body on exactly this point: "ERROR [pr-body] check `closures` is red and `## Red checks` does not name it" (ev/ci_check_runs.txt).

Disclosed on timing: step 11 says to post this block only once the head's workflows have all concluded. `mutation-pins (1)` at this head was still in_progress after more than 85 minutes (started 23:27:15Z). Every other job of the run has concluded. I did not wait longer. A finish of that job cannot answer the `closures` red. It can only add a `mutation-autofix` commit.

**The code passed every check I ran.** The remedy is a body edit only: name `closures` UNDER-SCOPED under `## Red checks` as repaired by ab6216c, and update the `## Red checks` sentence that says the head has not run in CI. Then re-verdict or `--carry`. ab6216c touches only tests/closures.json, the branch's own diff does not include that file, and the claim files are untouched, so it looks carry-eligible under orchestrator.md section 11. That call belongs to the orchestrator.

## Findings

- With `HASTUB_TZ=Europe/Stockholm` set, `tests/features.py` fails at the merge base fef4a135 as well as at this head: 5 of 4299 fail at the base, 4 of 4300 at the head. Two of the failures are the R9-F1.1 N-shared-config pair ("published mid-solve []"), and one is the naive/aware timestamp check (ev/features_base_TZ.txt, ev/mutants.txt "=== null"). It does not reproduce without that variable: the head prints `ALL 4307 FEATURE CHECKS PASSED`. No workflow under .github/workflows sets HASTUB_TZ. So this is a wall-clock or zone dependence in the suite that predates this branch, outside this group's seam. Carry: dismissed: pre-existing at base fef4a135 and not run in any CI lane's environment; reported here for the orchestrator to route
- The departure from the architect note that the body raises under `## Friction`: hunks in `_resolve_away`, the new `_expire_away_override`, and away.py, outside the note's owning seam (`_replay_interval` call site). The brief's own fix needs them. The roster already serialises them: at cccbf4fb5 and at the current roster tip, R10-LIVESTATE's `after` includes R10-LOOP-CPU and its stage is `not-started`. No new state is added. `git merge-tree` against current main is clean. I do not read this as architecture-unsound. The ruling on the after-edge that the body asks for is still owed. Carry: dismissed: the orchestrator's after-edge ruling, asked in the PR body; the existing R10-LIVESTATE after-edge serialises the touched hunks

## Evidence

- **Head.** The reviewed head is 86b3fe71d656949c8bd07e802c284316acbe825f. The branch tip is now ab6216cee6b688b45d6f4b89b70f84563307cacc, one github-actions[bot] commit on top (`ci: re-record closures`: tests/closures.json, +`process_worker.py` in one closure plus two timing fields). pr-contract reports it as an "accepted autofix commit". No authored commit moved the head (ev/git_checks.txt). The body's `## Head` names 86b3fe7, the head I measured.
- **Mutation proof** (my own mutants, each applied alone by an exact-once str.replace and then reverted; barrier = `replay.kernel_checks()`; ev/mutants.txt, ev/features_noTZ.txt):
  - RESULT null (unmutated head): `KC_FAILS 0` (5 of 5 pass); features.py without HASTUB_TZ `ALL 4307 FEATURE CHECKS PASSED`, rc 0.
  - RESULT M1 `_replay_interval`'s `return await _await_off_loop(` called inline: FAIL "P10: the space-heating learners replay the elapsed interval in the process worker, never on the loop", KC_FAILS 1.
  - RESULT M2 `_recovery_off_loop`'s `float(await _await_off_loop(` called inline: FAIL "P10: an away override's recovery estimate simulates the ramp ... (D14-s1-01)" with `'loop': 183`, KC_FAILS 1.
  - RESULT M3 guard `if self._away_state == written:` changed to `if True:`: FAIL "D14-s1-01 the away recovery estimate is handed off the loop, and a switch written during its await is not reverted by the resolve's publish", `1 of 4307 FEATURE CHECKS FAILED`. This is the LIVESTATE carry's control, and it reads red as the carry states.
  - RESULT M4 snapshot removed (`house = replace(live)` changed to `house = live`): KC_FAILS 0, no check reads it. That is expected: in the in-process harness the job runs on the same object, and the snapshot only guards against a callback writing the live state while the job is pickled. The body names the snapshot but claims no check for it, and the mutant is not one ci_predict draws.
- **Failing test first** (head tests over the base production code: worktree at the head, `git checkout fef4a135 -- custom_components/`): RESULT 2 of 5 barrier checks FAIL, the away arm (`'loop': 183`) and the learner arm. The three old arms pass (ev/failing_test_first.txt).
- **Finder's harness** `dev/audit/rounds/round10/D14/s1/p10_seams.py`: sha1 c8ba174c3fa7f6768a7576d31b6597835df45589, identical at base and head. Run with `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub`, /opt/hpo/venv-ci python 3.14.7, 6 cycles:
  - RESULT base fef4a135 `--away`: `loop_kernels_away_seam=183`, `loop_kernels_all=183`, `static_seams=36`.
  - RESULT head `--away`: `loop_kernels_away_seam=0`, `loop_kernels_all=0`, `worker_kernels=70`, `static_seams=36`.
  - RESULT null control `--away --deficit 0`: 0 / 0 at the base and 0 / 0 at the head. This is the carry's null control from the roster, and it holds.
  - RESULT head `--away --perturb` (re-introduction): `loop_kernels_away_seam=183`, `loop_kernels_all=2625`. The harness still sees the seam at the head, so the head's 0 is not vacuous.
  - The `seam` line diff between base and head is the single pair `coordinator.py:_replay_interval:simulate_step` -> `coordinator.py:_replay_step:simulate_step`, as the body states. This re-derives the body's de69745ff figures at the current merge base fef4a135 with the same numbers (ev/finder_*.txt).
- **Class census.** The body's rule is `static_seams()`. It returns 36 sites at both ends, and the moved site is the one the body names. Every site is dispositioned in the body. I checked the count and the moved pair, but not each of the 36 dispositions individually.
- **Brief check 2 (LIVESTATE carry).** cccbf4fb508cca8ce711dd06add13cc034ac0edb (`roster_edit append-carry R10-LIVESTATE`) is an ancestor of origin/handoff/audit-r10-roster. It appends a carry to R10-LIVESTATE whose seven lines are word for word the body's `## Forward-carry` bullet, including the control (the features.py check, red under `if True:`) and "Re-measure at your merge base". The PR body names the SHA (ev/roster_carry_cccbf4fb5.diff).
- **Brief check 3.** `git diff $(git merge-base origin/main HEAD)...HEAD --name-only -- dev/programme/rosters/` is empty. The diff does not edit wave-r10-groups.json.
- **Version and claim files.** VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched in the three-dot diff (no claim files moved, so env_drift has nothing to compare).
- **Merge.** `git merge-tree --write-tree origin/main 86b3fe71...` exits 0 (tree cec2ed6af7a4e70c5977acde0435af56ff2adece). No conflict.
- **Structure.** At the head `tests/structure.py` prints STRUCTURE RATCHET PASSED and `tests/arch_score_head.py` prints ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED.
  - class_excess_loc reads 18268 at the base and 18258 at the head. The coordinator's charged helper lines go 410 -> 400.
  - The budget only moves down, and the move is earned by `_replay_step` leaving the coordinator-handed helper span; it is not an instrument artefact.
  - seam_cut_total reads 708 at both ends (ev/structure_arch.txt).
  - I did not re-run score.py's dS; CI's arch-score passed at the head.
- **CI at the head** (check-runs API; ev/ci_check_runs.txt):
  - Green: fast (3.14), coverage, coverage-ratchet, typing, browser, briefs, closure-scope, Governance, Architecture score, Budget raise gate, Hassfest, Validate, CodeQL, and both push-time pr-contract runs.
  - `mutation` is red with exactly the three sites the body predicts and answers (coordinator.py:1629, 9553, 9577). My M2 and M3 runs confirm two of them are killed. The `_expire_away_override` RETURN_DEL I did not re-run.
  - `mutation-pins (1)` was still in progress.
  - `nightly-status` is red with "NIGHTLY ABSENT", a scheduled run not firing. Its own log says it is not a required context and does not block (main-protect's contexts). This diff touches no workflow or nightly lane, so that red is not this PR's.
  - `closures` is red with UNDER-SCOPED and unanswered: see `## Block`.
- **Re-runs.** CI's heavy runs (the gate and the mutation table) are cited and were not re-run, as the contract says.
- **Not re-derived:** the body's scoped-gate counts (`MODE: SCOPED -- 23 script(s) run, 10 scoped out`, `25 TEST SCRIPT(S) PASSED`), the agreement lane, the ux10 harness BLOCK-line diff, the pickled-model size of 2508 bytes, and the barrier's `worker:simulate_step` 1911 / 1733 figures.
- **Reading of the guard.** When `async_set_away` writes during the await, the resolve keeps the switch's write and drops that cycle's resolved fields. The next cycle resolves again. I read that as the stated design.
