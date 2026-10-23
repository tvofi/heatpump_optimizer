Fix review: merge 763702294959c3324049058bc6658ca9dfce8ec5

bus-nonce: 94a077b06388748abc8e6bcc7cc1b2bd

PR #2669, R10-POLICY-LINT-FAMILY (size S). Review round 1 of this pull request (the fixer's round 2; no `review/2669` or `verdict/2669` ref existed). Measured head `763702294959c3324049058bc6658ca9dfce8ec5` (the bot's `ci: re-record closures` on the body's `## Head` `48dbc2c81`), merge base `12032c43c`; the authored code head `4963b53d0` and its measurement base `a6620c30a` as the body names them. Contract currency: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the head's `fix-review.md` is current. Owner approval for the policy paths is the orchestrator's under mandate 6329234399 at merge; this verdict is not it.

Reviewer environment: macOS, bash 3.2.57, the seat interpreter (CPython 3.14.7) as `python3`. Evidence under `evidence/`.

## The barrier is shown to detect (defect-root-cause.md), both arms re-run

- **C2/C3, every path, at both ends.** `bash dev/audit/harnesses/r10_raise_paths.sh <rev>` (`raise_paths_base.txt`, `raise_paths_head.txt`, per-path outputs in `paths-base/`, `paths-head/`):
  - base `a6620c30a`, no-section body: prepr, body_push, body_patch each `rc=0 raise_errors=0` (the defect).
  - head `7637022`, no-section body: prepr, body_push, body_patch each `rc=1 raise_errors=1`, the error `the diff raises 1 cap(s) (tests/structure_budgets.json: class_excess_loc: 18234 -> 18235 (a cap went up)) and the body has no ## Raise justification section` (the cap value is the tree's at 7637022; the body's 18244 was taken at 4963b53).
  - null control, `raise/good.md`'s section: every path `rc=0 raise_errors=0` at both ends.
  - **pr-contract arm, environment:** on bash 3.2 the harness's pr-contract arm reads `rc=1 raise_errors=0` for both bodies at both ends, because the workflow's own block expands an empty `"${RED_ARGS[@]}"` under `set -u` (`bash: line 18: RED_ARGS[@]: unbound variable`, `paths-head/pr-contract-none.txt`); the runner's bash 5 does not. Re-run with one red (`budget-raise-gate`, which both bodies answer) fed to `/tmp/pr-reds.txt`, the only change (`r10_raise_paths_bash32.sh`, my copy, diff printed in my log: the ROOT line and that one line): base `rc=0 raise_errors=0` none / `rc=0` section; head `rc=1 raise_errors=1` none / `rc=0 raise_errors=0` section (`p32-a6620c3/`, `p32-7637022/`). This reproduces the body's pr-contract figures.
- **C1, the recorded sections.** For `c6c8fee16 9b5742049 84e2aaf66 f2b98c1df 8f564875d`: each `raise/recorded/<c>.md` is a substring of `git show <c>:BODY.md` (all 5 VERBATIM), and `python3 -I tools/policy/budget_raise_gate.py --check-body` on the fixture exits 1, 1, 1, 1, 0 with the clauses `Payments tried`, `Payments tried`, `Architecture score`, `Architecture score`, accepted.
- **Mutation proof**, `python3 dev/audit/harnesses/r10_policy_lint_family_mutants.py --agreement-json evidence/agreement_py.json` (`mutants_head.txt`), against the unmutated owners each rc=0 (`clean_owners.txt`: `FIXTURE ok: 93 error(s) hold 256 pins`; `budget_raise_gate self-test: 255 checks, 0 failed`; `body_patch self-test: 62 checks, 0 failed`; `RESULT divergent=0`; `policy_lint_mutants.mjs` rc=0; `prepr.sh --self-test` `341 passed, 0 failed`, `prepr_selftest_clean.txt`):
  - M1 rc=1 (three FIXTURE VACUOUS: controls, double, residual); M2 rc=1 (residual); M3 rc=1 (raise arm on bare-payments drew 0); M4 rc=1 (5 gate rows); M5 rc=1 (`RESULT divergent=13`); M6 rc=1 (e2e no-section raise); M7 rc=1; M8 rc=1; M9 rc=1; M10 rc=1; M12 rc=1 (`policy_lint gets pr-contract's arguments ... (got '0', want '1')`); `RESTORED 12 file(s)`; worktree clean after.
  - M11 read `rc=3` with no marker line in the harness run. Re-run by hand (the same one-line deletion, file restored, `git status` clean): `340 passed, 1 failed`, rc=2, the one FAIL `body_check hands policy_lint the base, so a raise with no ## Raise justification is refused here and at body_push, not first at the train (got 1, wanted 0)` (`prepr_selftest_M11.txt`). Killed. The pin is a source-shape test of `declare -f body_check`; the behaviour it stands for is the C3 harness's prepr/body_push arms above.
  - #2408 shadowing mutant: `node tools/policy/policy_lint_mutants.mjs` at head prints `PIN record record-known-bad with a local at shadowing at(path), it threw: at is not a function`; at both `a6620c30a` and `12032c43c` `policy_lint_mutants.mjs` has 0 matches for `record-known-bad|cmdRecord`, so nothing reached `cmdRecord` there (survives by construction). `git status` after the lane: ledger unmodified.

## The finder's harness at both ends (#2410)

`node dev/audit/harnesses/r10_family_replay.mjs [<root>]`, recorded window `v7.0.0..df6ca4bc` (`replay_base.txt`: root = a full `git archive a6620c30a` export; `replay_head.txt`):
- base: `mutation-vacuous count=5`, `mutation (family) count=7`, `(8 entries in all)`.
- head: `mutation-vacuous count=5`, `mutation (family) count=7`, `(7 entries in all), less the 5 that mutation-vacuous already files on its own line`.
- PRS null control identical at both ends: mutation 2390; mutation-vacuous 2275,2305,2365,2404,2406; mutation-survivor 2444; test-vacuous 2297,2360; vacuous-test 2391; vacuous-check 2400; mutant-survives 2376. Base family = vacuous's 5 + 2390 + 2444; head = the 12 less those 5. Matches the body.

**The live window the body left unmeasured, measured here** (`node tools/policy/policy_lint.mjs --stats --since v7.0.4 --window-cache evidence/window_v704.json` with a token; base's `policy_lint.mjs` from `a6620c30a` run over the same cache, served from it; origin/main `fd7e289d0`, 53 merged PRs; `stats_head_v704.txt`, `stats_base_v704.txt`):
- base: `5 / 7 mutation (family) <- at or over threshold`, and its would-open line fires at 5, beside `mutation-vacuous` at 4 (#2580, #2605, #2645, #2647) firing its own.
- head: `2 / 5 mutation (family) (of 6; mutation-vacuous files its own)`, below the threshold, no family line. The 2 are #2528 (`vacuous-test`) and #2579 (`mutation-survivor`).
- So on #2410's live window this change takes the family line off: 4 of base's 5 occasions are the member's own filed ones. Two further words occur there, `mutation-unpinned` (#2632) and `unpinned-site` (#2629); with them the head would read 4 and fire. #2561 section 5 (`dev/audit/rca/R10-RCA-HARNESS-FRICTION.md`) dispositions this obligation as different (`mutation-untriaged`, #2379, "is the unpinned-site triage, a different obligation"), so they are correctly outside the family and not a class-open seam; the body does not say so. Carry: #2410

## Other checks

- **Step 6, class.** Gate budget-file discovery is `SUFFIX = "_budgets.json"`, the lint's trigger the same suffix; the 7 tracked budget files all match. The grammar's reader enumeration in `## Figures` matches the diff. The family arm's degraded verdict case (`!verdictArmInforms`) cannot leave a filed member unfiled with members present, because members only exist as keys when block classes read. Title seam: `bash dev/audit/harnesses/r10_title_seam.sh v7.0.0..a6620c30a` prints `RESULT titles=345 refused=0`, `CONTROL refused=1` (`title_seam.txt`).
- **C4.** `python3 tools/audit/fold_ledger.py check`: `45 classes, 746 instances ... 118 rca entries`, `0 violation(s)`; `N-train-only-predicate` status barriered, rca `R10-RCA-RAISE-GATE-GRAMMAR`, doc landed.
- **Steps 4, 5.** `git diff --name-only 12032c43c...HEAD -- VERSION custom_components tests/golden RELEASE_NOTES.md` lists 0 files; claim files untouched. `git merge-tree --write-tree origin/main HEAD` rc=0 at origin/main `fd7e289d0`. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `node tools/policy/brief_lint.mjs`: `CARRY ok`.
- **Step 7.** `## Head` names `48dbc2c`; pr-contract at this head reads `HEAD: ## Head names 48dbc2c; accepted autofix commit(s) on top of it: 7637022 (ci: re-record closures)`.
- **Step 14.** No `*_budgets.json` moves. `tests/closures.json` moves only by the bot's 7637022 (5 `inert_reads` entries for `tests/entities.py`, 3 re-timings), earned by the new grandchild read. Pins 254 -> 256 are the two new arms.
- **Step 15.** The lint calls the gate's own function rather than mirroring it; the one mirrored line (the heading test) is registered in `agreement.mjs` (`raise-justification: 2 readers, 50 items, 0 divergent`; 13 under M5).

## Red checks (step 11), read from the commit check-runs API

- `7637022`: every run concluded; reds: one `pr-contract` (job 120473213226, 14:36Z), whose log reads `ERROR ... check closures is red and ## Red checks does not name it`; the re-run after the body edit (job 120531703229, started 16:34:29Z, after every other run concluded) is success: `record red-history 13 commit(s) ... every failure conclusion across them: closures`, `PR-BODY: 0 error(s)`. pr-contract is the body contract and excluded from its own red list.
- `48dbc2c`: `closures` failure (job 120456986792), `closures-autofix` success (job 120472970719, pushed 7637022), `pr-contract` failure (the same unanswered closures).
- **`closures` answer judged, not accepted.** The body answers "none exists". Re-run at `48dbc2c`: `python3 tools/pr/ci_predict.py --base 12032c43c` prints `CI PREDICT: no closures or fast red predicted against 12032c43cc32 (a data-file read is not seen)`, rc=0 (`ci_predict_48dbc2c.txt`). The read is `tests/entities.py` -> node `policy_lint.mjs` -> `python3 -I budget_raise_gate.py --check-body`, a grandchild; `prepr/raise/` is a new directory (no listed siblings), and the inert dimension is Linux `strace`-only (`ci-autofix.md`; `R10-RCA-INERT-PREDICT.md`'s child-process class, whose accepted route is the bot repair). I find no existing detector cheaper than the gate that sees this read; the answer stands.

## Non-blocking

- `r10_raise_paths.sh`'s pr-contract arm cannot run on macOS bash 3.2 with an empty red list (above). Carry: dismissed: the arm executes the workflow's own block verbatim, which runs under the runner's bash 5; with one red it reproduces the body's figures here.
- `r10_family_replay.mjs` given a root with only `tools/policy/` exported printed the seven `PRS` lines as `-` and no `RESULT` line, rc=0, rather than refusing the root. Carry: dismissed: the empty reading is visible in its own `PRS` null-control lines, and a full-tree root reproduces the recorded figures.

RESULT raise_paths_base no_section prepr=0/0 body_push=0/0 body_patch=0/0 pr_contract(bash3.2,1 red)=0/0
RESULT raise_paths_head no_section prepr=1/1 body_push=1/1 body_patch=1/1 pr_contract(bash3.2,1 red)=1/1
RESULT raise_paths_null_control section base=all rc0 head=all rc0
RESULT c1_recorded verbatim=5/5 check_body_rc=1,1,1,1,0
RESULT mutants killed=12/12 (M11 by hand) restored=12 record_known_bad=PIN at head, unreachable at base
RESULT family_replay_recorded base=7 (8 entries, incl. mutation-vacuous's 5) head=7 (7 entries, less 5 filed)
RESULT family_live_v7.0.4..fd7e289d0 base=5 fires head=2 silent
RESULT title_seam titles=345 refused=0 control=1
RESULT closures_red answered=yes cheaper_detector=none (ci_predict rc=0 at 48dbc2c)
