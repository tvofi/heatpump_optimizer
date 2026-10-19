Fix review: blocked 8be64a110fa4e741889920c4eff2b6b4cb99cf3a carry-missing: not carried to R10-CI-LAYOUT or R10-BRIEFS-FOLD; three of the body's four Forward-carry and Friction lines are not in handoff/audit-r10-roster at 5472ac0d6, and the body names no roster SHA

bus-nonce: f80ab1804942e189dbff059a04dfe3bd

Round: 2. Round 1 was the `Fix review: blocked b891dfa04 mutation-survivor` comment; this head fixes that finding. This is round 2, so from the fourth round a re-cut would be owed, not yet.
Measured head: 8be64a110fa4e741889920c4eff2b6b4cb99cf3a (ev/HEAD). Its merge base with origin/main is e59f0291a, which is origin/main's tip.
Contract: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
Environment: this container exports PYTHONUNBUFFERED=1, as the dispatch said. The seat interpreter is /opt/hpo/venv-ci/bin/python3, CPython 3.14.7.

## Blocking

- Step 10, forward-carry. `finding-propagation.md` (Enforcement): "The producing PR does not merge until the carry is in the tree ... The body names the file, the stage and (a roster carry) the branch SHA: the reviewer opens that, not the claim." The body's carry lines end `Carry: R10-CI-LAYOUT` (three of them) and `Carry: R10-BRIEFS-FOLD` (Friction). None of them names a roster branch SHA. I opened `handoff/audit-r10-roster` at its tip 5472ac0d67f8 and the other six `handoff/*roster*` refs (ev/carry.txt, ev/carry_grep.txt):
  - The seven unwired self-tests outside `tools/audit/seat/`: these are covered in substance by R10-CI-LAYOUT's earlier carry, which predates this PR and says "Enumerate every `--self-test` under tools/ with a command ... disposition each". This PR's own enumeration (the seven names and its weaker grep rule) is not written there.
  - The coverage of `merge_pr.sh`'s path after its gates and of the push lines in `handoff_push.sh`, `open_pr.sh` and `update_pr.sh`: not in R10-CI-LAYOUT's brief or carries. The roster's one `merge_pr.sh ... gate` hit is a different group's mandate-gate brief.
  - The cost question of the field-coverage census copying `custom_components/heatpump_optimizer/`: absent.
  - The Friction line (`.git/info/exclude` holds a bare `seat/` line, so `git add -A` leaves a new seat instrument untracked) to R10-BRIEFS-FOLD: absent. Neither `info/exclude` nor `git add -f` appears in the roster.
  
  A carry that exists only in the PR body is the case step 10 names, "only in this PR's comments". Fix: append the carries with `roster_edit.py append-carry`, each with its control and a re-measurement instruction. Name the roster SHA in the body. No code change is needed.

## Verified at this head

- Round-1 finding, re-run with PYTHONUNBUFFERED=1 set (ev/direct_mutants.txt, ev/harness_full.txt):
  - S30 (`return 1 if unwired else 0` -> `return 0`), run directly: `FAIL --check exits 1 on an unwired file (rc=0)`, `15 checks, 1 failed`, rc=1. KILLED.
  - Two extra mutants of my own on the same line. `return 1` and `return 1 if tests else 0` are both killed by the null-control arm (`--check exits 0 when every file is wired`). The new arm cannot pass by refusing everything.
  - S04 (`"-u" not in` -> `"-u" in`), run directly under PYTHONUNBUFFERED=1: `SELF-TEST FAIL`, with 4 arms failing, including the new `the logged argv carries the prepended -u`. KILLED. Two extra mutants of mine were killed the same way: deleting the `run_argv.insert(1, "-u")` line, and narrowing the basename tuple to `("python",)`.
  - The PR's harness, all mutants, under PYTHONUNBUFFERED=1: S04, S04U and S30 KILLED. The S04/S04U last line is the CLI usage line because the step goes on to its CLI calls after the self-test fails. rc=1 either way.
  - Control at c4a6597eb (the round-1 files, PYTHONUNBUFFERED=1, ev/control_c4a6597eb.txt): S30 gives `13 checks, 0 failed` rc=0, and S04 gives `SELF-TEST PASS` rc=0. Both survive, which reproduces round 1. The kill is earned by the diff.
  - Unmutated: `selftest_wiring self-test: 15 checks, 0 failed`. `daemonize.py --self-test` prints `SELF-TEST PASS` both under PYTHONUNBUFFERED=1 and under `env -u PYTHONUNBUFFERED`.
- The body's mutation figures (ev/harness_full.txt, `PYTHONUNBUFFERED=1 python3 -I dev/audit/harnesses/r10_seat_selftests_mutants.py`, a clean worktree at the head): 36 lines `== M0 rc=0`, `== M0: 0 seat step(s) red`, `grep -c ' KILLED'` = 34, 0 SURVIVED, 0 NOT RUN, `RESULT survivors=0`, rc=0. `git status --short` was empty afterwards. These match the body.
- Field-coverage fold (ev/field_coverage.txt): at the head, `RESULT misread=0`, with all nine inputs reading RUN and README SKIPPED. At fb9b3fc1f, `RESULT misread=8`. These match the body.
- Figures (ev/figures.txt):
  - Gate scope: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
  - Wiring: `selftest_wiring: 37 self-testing, 37 wired, 0 unwired`, rc=0.
  - Ratchets and claims: `STRUCTURE RATCHET PASSED`; `policy_lint.mjs --budgets` rc=0; `ALL 109 HARNESS HEADER CHECKS PASSED`; `claims hygiene: e59f0291a... ok`. That claims figure was taken at the current merge base. The body quotes fb9b3fc1f, the code head's base.
- Step 5: `VERSION`, `manifest.json`, `RELEASE_NOTES.md` and `tests/golden` show an empty diff from the merge base (ev/step5.txt).
- Step 13: `git merge-tree --write-tree origin/main 8be64a110` exits 0 and prints tree 982bb6457, with no MERGE-CLAIM line (ev/merge_tree.txt). The head already contains origin/main e59f0291a.
- Step 7: the body's `## Head` names 8be64a110fa4e741889920c4eff2b6b4cb99cf3a, the head I measured.

## CI at this head (step 11, ev/check-runs.tsv, read at 14:33Z with filter=all)

- `instrument-self-tests` (the job this PR adds to): success, 14:24:37Z to 14:28:03Z.
- Red: `arch-score`, `validate-hacs`, `env-matrix`, `pr-contract` (2 runs) and `nightly-status`. I read the logs (ev/log_*.txt). The first five all died on `API rate limit exceeded for installation (HTTP 403)` before their checks ran:
  - `arch-score` failed reading the PR body.
  - `validate-hacs` failed in HACS's `repos.get`.
  - `env-matrix` failed with `required-contexts ... the GitHub API is unreachable`.
  - `pr-contract` 118115365678 and 118116886250 failed at "Read the body off the API". The steps after it failed on the missing `/tmp/pr-body.md`.
  
  So `pr-contract` has not checked the body at this head. `nightly-status` is main's red, and the body answers it.
- `coverage` and `Analyze (python)` were still in progress at 14:33Z.
- None of these reds is this diff's. They need a re-run once the installation's quota resets. Under step 11 I do not block on them, because no workflow has concluded with a `pr-contract` run reading the body. They are not answered in the body either, and I am not grading that.

## Not re-derived

- (moved to Verified: the offline spy over the 37 files printed `offline_spy: 37 files, 0 refused`, rc=0, and 0 per-file lines lack ` offline |` (ev/offline_spy.txt). This matches the body.)
- `tests/entities.py` at the head was still running when I wrote this, so I cite CI rather than a local run.
- The body's job-time figure and its seven-unwired census outside `tools/audit/seat/` were not re-run.
- The macOS sandbox-exec path of `offline_spy.py` cannot be measured on this Linux seat.
