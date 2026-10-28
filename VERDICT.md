Fix review: merge 67942203677a3a416fc84e25161a614390c67a99

bus-nonce: dcdc56547551e7a48656f24e4ac922ea

## Scope

PR #2622, group R10-CI-LAYOUT-P2, sub-PR P2a: the inert umbrella engine under `tools/ci/` plus the seat probe and sweep driver. Measured head `67942203677a3a416fc84e25161a614390c67a99`, merge base `fd9914851f06`. I reviewed it from detached worktrees at that head. `fix-review.md` is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty. The dispatch does not state the round, and I could not determine it.

**The head moved during the review.** It is now `91f2bcd4c236095d621f238d44a6ae005e3df220`, a merge of origin/main `de69745ff` into the measured head. Its resolution delta is empty: the tree of `git merge-tree --write-tree 6794220 de69745ff`, `6bb68184`, equals `91f2bcd4c^{tree}`. Because `tests/closures.json` is in both the branch's diff and the merge, the carry predicate in orchestrator.md §11 does not hold. So I judged the resolution delta as step 12 requires. The only overlapping path, `tests/closures.json`, is the ledger driver's set union. It keeps main's two added harness entries (`r10_solver_seed_or_stop.py`, `r10_solver_winner_polish.py`) and the PR's ten. The only lines lost are three `seconds` timing scalars, where the PR's values win. The delta is sound. Every number below was measured at `6794220`, and none depends on the merged main content.

## Findings

- The forgery pin (DESIGN-P2 2.1, built as approved) refuses `checks: write`, `write-all` and any job that can report as `gate`. It does not refuse `statuses: write`. A required check pinned to `integration_id` 15368, which is `ruleset_cutover.py`'s `NEW_CHECKS`, can probably be satisfied by a commit status with context `gate` posted with a GITHUB_TOKEN that holds `statuses: write`. I have not verified this against GitHub's rule evaluation. No workflow grants `statuses: write` today (`grep -rn statuses .github/workflows` finds only a comment), so nothing is exposed at this head. P2b's forgery half should either add `statuses` to the refused grants or record why a status cannot satisfy the ruleset. Carry: R10-CI-LAYOUT-P2
- The body's `## Figures` gives `ci_probe 466` lines. At this head and at the code head `7bf6a92`, `tools/audit/seat/ci_probe.py` has 499 lines (`git show <head>:tools/audit/seat/ci_probe.py | wc -l`; numstat +499), so 466 is the count from before route B. `## Head` also has a stray second paragraph naming `99d4f4d25c55…` with the same wording as the `67942203` paragraph. The body should correct both before the merge message is cut. Carry: R10-CI-LAYOUT-P2

## Evidence

- Merge with main: `git merge-tree --write-tree origin/main 6794220` gave rc 0, with `LEDGER-MERGE: resolved tests/closures.json` and no claim-file conflict (ev/merge-tree.txt).
- VERSION, the manifest, RELEASE_NOTES, golden fixtures and `*_budgets.json` are untouched (three-dot diff is empty). CI's `prepr.sh --version-edit` printed "no version edit".
- Step 1, the mutation proof. The seat harness `r10_seat_selftests_mutants.py`, run on all 21 P2a ids (ci_probe-1..7, ruleset_cutover-1..3, gate-1..3, ghapi-1..3, prelude-1..2, sweep_driver-1..3), gave `RESULT survivors=0`, every id KILLED (ev/seat_mutants.txt). `r10_ci_gate_core.py mutants` gave `RESULT mutants=16 survivors=0`. `alert_list_mutants.sh --self-test` gave `ALERT-LIST MUTANTS: every mutant refused`. I also planted four mutants of my own (ev/own_mutants.txt, ev/own_mutant_D_entities.txt), and all were killed:
  - A, `git_commit` without the exact-name test: ci_probe self-test 4 failed.
  - B, `do_push` without the commit check: 4 failed.
  - D, the entities forgery reader ignoring job-level grants: `1 of 2399 ENTITY CHECKS FAILED`, plant missed `a job grant`.
  - C: the alert_list Accept-header drop is the glue's case in alert_list_mutants.sh.
- Step 2, the finder's harness at both ends. The group's design oracles at head:
  - `replay`: rc 0, `IDENTICAL to 1371a0a6:measure/rev/gate_replay2.txt`;
  - `replay --model`: IDENTICAL;
  - `sim`: rc 0, `IDENTICAL to 1371a0a6:measure/rev/gate_sim.txt`;
  - `b3`: `parity GREEN`.

  Both ends do not apply here: P2a is new inert code with no caller, and the baseline holds no `tools/ci/`.
- Step 3, the null controls. `replay --no-b3-fill` gave rc 1, `output DIFFERS`. `b3 --plant` gave `parity RED`, only in tests.yml `['ci-ratchet']`. `selftest_wiring.py --check` gave `87 self-testing, 87 wired, 0 unwired`, rc 0 (ev/gate_core.txt, ev/static.txt).
- Self-tests at head (`python3 -I <file> --self-test`, Python 3.11, ev/selftests.txt) all match the body's figures:

  | self-test | checks | failed |
  |---|---|---|
  | ghapi | 13 | 0 |
  | prelude | 27 | 0 |
  | gate | 27 | 0 |
  | sweep | 21 | 0 |
  | alert_list | 25 | 0 |
  | ruleset_cutover | 51 | 0 |
  | sweep_driver | 15 | 0 |
  | ci_probe | 40 | 0 |
  | prune_refs | 29 (`SELF-TEST PASS`) | 0 |
- Static checks (ev/static.txt):
  - throwaway_git: 0 refused;
  - tmp_paths: 0 refused;
  - ref_privacy: 0 refused;
  - `layout self-test: ok`;
  - `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub tests/entities.py` gave `ALL 2399 ENTITY CHECKS PASSED` (3.13 venv with requirements-ci). The body reports 4 failures, all py-spy heartbeat checks that also fail on main. They are environmental, and this environment does not reproduce them.
- The agreement lane against the BASE copy, as wave-script runs it. I extracted both `run:` blocks from governance.yml and ran them in a detached worktree at head with `PINNED=fd9914851f06`. Result: `RESULT divergent=0 unregistered=0 dead=0 refused=0`, then `AGREEMENT ok` (ev/agreement_base_copy.txt). `tools/policy/agreement.mjs` is byte-identical to main. CI's wave-script concluded success at both 6794220 and 91f2bcd4c.
- Route B (decision 8): `git_commit` accepts a SHA only when `git rev-parse --verify --quiet --end-of-options <sha>^{commit}` succeeds and prints exactly the SHA. `do_review` fetches `refs/pull/<pr>/head` before refusing. `gate.py --sweep` with no `--run` fails closed with `FAIL usage`, rc 2.
- Step 6, class. The entities pins carry in-file plants: three for REQUIRED and five for forgery. My mutant D shows the plants detect a gap in the reader. The `statuses: write` seam above is outside the approved design's rule. It is carried, not blocked, because the PR builds exactly the approved rule.
- Step 7: the body's `## Head` names 6794220, the head I measured.
- Step 8, figures I could not re-derive:
  - "82 ids with no duplicate": I count 62 unique per-file ids plus 42 S/W/M ids at this head, with no duplicates, and I cannot find which rule gives 82.
  - "101 KILLED" for the full harness at `49ccd4a6c`: not re-run. I re-ran only the 21 P2a ids.
  - The full gate figures at `0e066014d`: cited, not re-run (step 11, tvofi 2026-09-30).
  - The diff stat "26 files, 3725 insertions, 4 deletions" matches the code head `7bf6a92`. The measured head reads 27 files, +3732/-7, which adds the delivery row and the closures re-record.
- Step 11, CI at 6794220 (ev/check-runs.txt, ev/pr-contract-6794220.txt):
  - nightly-status red: main's transition red. The body answers it, and the diff reaches no nightly file.
  - pr-contract red: carry_audit gave `BAD-DEST ... R10-RCA-BODY-LINT is not a group of the roster`. That group existed on the handoff roster but not yet on main's.
  - At 91f2bcd4c, pr-contract concluded success, and wave-script, mutation, policy-docs, briefs, scope and budget-raise-gate are green.
  - closures, fast (3.14), coverage, instrument-self-tests and Analyze (python) were still in progress at 91f2bcd4c when I wrote this. They are the orchestrator's to see green before the merge.
  - At 6794220, `fast (3.14)` and `ci-ratchet` were cancelled by supersession.
- Step 10: the forward-carry destinations are R10-CI-LAYOUT-P2, R10-RCA-BODY-LINT and R10-POLICY-LINT-FAMILY. carry_audit at 91f2bcd4c reads every item routed.
- Step 14: no budget, archscore, golden or claim file moves. The `closures.json` and `INERT` movement is the closures autofix recording (`77cc8b0ab`) of files this PR adds, so the change earned it.
