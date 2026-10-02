_Requested by **tvofi**_

Part of #201.

`closures-autofix` runs the **base's** `tests/closure.py` (D11-s1-03, decision 0013's pinned grader), while `closures` runs the pull request's. When a PR moves a file out of INERT and commits a closure that reads it, the base copy's `check()` stops at the INERT-pair refusal before the under-approximation comparison. It prints no UNDER-SCOPED, so the autofix returned the quiet `skip-not-under-scoped` and went green beside a red `closures` that had printed one. No bot commit followed, and none could: the base `merge()` refuses the same pair. #1846 hit this twice and #1851 once.

This PR makes the autofix notice when its pinned classifier disagrees with the grader:

1. The `closures` job's "Fail if tests/closures.json under-approximates" step now runs under `set -o pipefail` and tees `python -u tests/closure.py check ... 2>&1` to `$RUNNER_TEMP/closures/check.txt` on both arms. The existing `always()` upload carries it, and `.txt` sits outside every `*.json` glob that `check`/`merge` read.
2. `apply_under_scoped_recordings` returns a new **red** status, `skip-classifier-disagrees`, when its own check printed no UNDER-SCOPED and `check.txt` has a line starting `UNDER-SCOPED: `. The status is not in `AUTOFIX_QUIET` and has its own `_AUTOFIX_STATUS_REMEDY` entry pointing to `derive_closures.sh --single`. The file is read only as data and can only redden the job; nothing it says can make the job push.
3. `.claude/rules/ci-autofix.md` names the status in the red list and in "What green means", and says the classifier is base-pinned. `.cursor/rules/ci-autofix.mdc` was regenerated with `rules_sync.mjs`. The file's token cap had zero headroom, so the cost was paid inside the file and the cap was not raised.

**Bootstrap: this PR cannot exercise its own new status in CI.** `closures-autofix` runs `origin/main`'s pinned `closure.py`, which lacks the new branch until this merges, so the new red can first fire on a PR opened after the merge. The `check.txt` tee runs at this PR's head, because `closures` runs the PR's own `tests.yml`. Everything below was demonstrated locally against the real CI logs.

## Head

`4fe5c0374d44433598ce98848ed650a82a53e237`. That is the merge of `origin/main` 948671af1 into the fix at 05540e8f4. The test-first commit is 07b4701ee. All measurements were taken at 4fe5c0374, except the red run at 07b4701ee and the mutants at 05540e8f4.

## Root cause

From the root-cause seat's analysis on `handoff/r9-rca-closures-autofix-skip` (6d4a51b3e, `rca/RCA-closures-autofix-skip.md`; scan tables `rca/jobs.tsv`, `rca/p2.tsv`).

- **Cause.** `closures` and `closures-autofix` classify the same recordings with different programs. The autofix's "Restore the programs this job runs from the base commit" step checks out `tests/closure.py` at `pull_request.base.sha`. #1846 moved `DISCLAIMER.md` and `docs/index.html` from INERT to `INERT_EXCEPT` and committed closures that list them. The base copy still has them INERT, so `inert_closure_violations(committed)` fails first, `check()` returns 1 without printing UNDER-SCOPED, and the status is `skip-not-under-scoped`.
- **Process state: (d).** The process was sound, and then its precondition changed. The autofix (#498) was correct while it ran the same `closure.py` as `closures`, and its quiet "not my case" status assumed the two agree. 42460ce2f (F11.2, D11-s1-03) pinned the classifier to the base for a sound security reason, but nothing re-examined what the quiet status means once the two can disagree. #1569 fixed the same symptom from a different tree/program divergence. Following `defect-root-cause.md` for (d), the countermeasure makes the process notice the change; it does not add a firmer instruction.
- **Cost test.** The RCA counted every `tests.yml` `pull_request` run created 2026-09-26..2026-10-02: 423 runs, 0 list failures, 22 runs where `closures` failed and the autofix ran, and 15 of those printed UNDER-SCOPED. **3 of the 15** ended `skip-not-under-scoped`, spread across 2 PRs (#1846 at 9bc802e6 and e42b1cdd, #1851 at 3a28a3ea), and the RCA reproduced all 3. The defect costs an estimated ≥ 30 min of seat time per PR (one reviewer diagnosis cycle; not measured). The recurring cost of the countermeasure is one `tee` in `closures` plus one line scan in `closures-autofix` of the check step's output (10 lines in run 37019499517), which only runs on a failed `closures` (22 of 423 runs). That is well under 1 s per run, so the countermeasure was built.
- **Countermeasure and its demonstration.** Items 1–3 above. The detector goes red on the defect and stays green on the by-design path. See `## Mutation proof`, `## Null control` and `## Figures`.

## Mutation proof

Each mutant was applied to the committed fix at 05540e8f4, run with `PYTHONPATH=tests/hastub:<numpy/scipy target> python3 tests/entities.py`, and then restored with `git checkout`.

- **M1, guard deleted** (`disagree = False and any(...)` in `apply_under_scoped_recordings`): `1 of 2063 ENTITY CHECKS FAILED`, namely `FAIL a pinned classifier that disagrees with the closures job's UNDER-SCOPED reddens (#1846)  [{'defect': ('skip-not-under-scoped', True), ...}]`.
- **M2, pipefail dropped** (`set -o pipefail` → `true`): `1 of 2063 ENTITY CHECKS FAILED`, namely `FAIL the closures job tees its check to check.txt beside the recordings`. This sed hit every `tests.yml` line that is exactly ten spaces plus `set -o pipefail` (3 lines, this step's among them). Only this check went red.
- **M3, new status classified quiet** (added to `AUTOFIX_QUIET["closures-autofix"]`): `1 of 2063 ENTITY CHECKS FAILED`, namely `FAIL a pinned classifier ... reddens (#1846)  [{'defect': ('skip-classifier-disagrees', True), ...}]`.

**Red first:** at 07b4701ee (test only; `closure.py` and `tests.yml` as on main) the result was `3 of 2063 ENTITY CHECKS FAILED`. The failures were the #1846 case (`skip-not-under-scoped` for the defect), the tee wiring check, and the apply-function status roster. The null-control check passed there too. At 05540e8f4 and at 4fe5c0374: `ALL 2063 ENTITY CHECKS PASSED`.

`python3 tests/mutation_table.py --scope changed --base 2e7422e59` reports `no production code line added or modified against the base` and `MUTATION TABLE PASSED (empty scope)`. The diff touches no file under `custom_components/`, so no ledger sites are involved.

## Null control

- **a46a91c's by-design failure.** In #1846's earlier run (Tests 37007613365, `closures` job 110839553394), `closures` printed `INERT READS UNDER-APPROXIMATED ... tests/doc_claims.py: DISCLAIMER.md` and no UNDER-SCOPED. Given that real check output as `check.txt` beside the same INERT-pair recordings, the head returns `skip-not-under-scoped` and the job exit is 0. That run owes no bot repair, and the result stays quiet.
- **No `check.txt`** (an artifact from before this change, or the fast arm): the result is `skip-not-under-scoped`.
- **The unmodified tree** (`tests/closure.py` at 2e7422e59) returns `skip-not-under-scoped` with job exit 0 for all three inputs, the defect included. That is the defect.
- The predicate keys only on `skip-not-under-scoped`. `skip-clean` (the 89572df0 moved-head case in the RCA scan) and `skip-not-allowed` (the loop guard) are untouched. All existing autofix checks in `tests/entities.py` (#523, #1569, R9-F10.9) still pass.

## Figures

- The 3 / 15 / 22 / 423 run counts are stated without a command here. They rest on the RCA seat's GitHub API scan, which lives only on the ref handoff/r9-rca-closures-autofix-skip at 6d4a51b3e (its rca/ directory holds the scan scripts and tables, none of them in this tree), and they were not re-taken.
- `2063 entity checks: 3 red at 07b4701ee, 0 red at 05540e8f4 and 4fe5c0374`. Command: `PYTHONPATH=tests/hastub:$PYLIB python3 tests/entities.py`, where `$PYLIB` is a `pip install --target` of CI's pins `numpy==2.4.6 scipy==1.17.1` (from `tests/requirements-ci.txt`) on Python 3.14, macOS.
- Real-log demonstration, against `$EXPORT/demo2.py` sha1 3a715f6698f7 (scratch, not in the tree). It runs `apply_under_scoped_recordings` over `{harness_headers.py: [it, DISCLAIMER.md]}` with recordings reading `DISCLAIMER.md`, which is INERT at main, and `check.txt` set to the timestamp-stripped check-step output of `closures` job 110886379255 (run 37019499517, e42b1cdd, 10 lines, sha1 e40d679b245a) or job 110839553394 (a46a91c, 5 lines, sha1 775720c7983c). Head: `e42b1cd defect: status=skip-classifier-disagrees job_rc=1`, `a46a91c null: status=skip-not-under-scoped job_rc=0`, `no check.txt: status=skip-not-under-scoped job_rc=0`. Base 2e7422e59: all three `skip-not-under-scoped job_rc=0`.
- `MODE: FULL -- every test script runs` from `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` (reason: `.github/workflows/tests.yml changes the gate itself`). The full gate is CI's; it was not reproduced locally.
- `STRUCTURE RATCHET PASSED`, from `python3 tests/structure.py`.
- `ci-autofix.md` measures 1428 tokens against a cap of 1428, and 92 lines against a cap of 96, from `node .claude/workflows/policy_lint.mjs --budgets`. `TOTAL: 0 error(s)`, from `node .claude/workflows/policy_lint.mjs`.
- `RULES-SYNC ok`, from `node .claude/workflows/rules_sync.mjs --check`.

Not run locally: the full gate (MODE: FULL, left to CI), `tests/stress.py`, `features.py` and the solver goldens (numeric, CI only), and closure recordings (`PREPR_SKIP_CLOSURES=1`; off Linux).

## Red checks

none so far on this branch. The new `closures-autofix` status cannot fire on this PR itself, because that job runs main's pinned `closure.py` (see the bootstrap note above). If `closures` goes red here, `closures-autofix` reports main's verdict.

## Forward-carry

none. The RCA's class note is recorded here for the orchestrator to decide on, and nothing is built for it: `claims-autofix` (pins `env_drift.py`, quiet `skip-not-inherited`) and `mutation-autofix` (pins `mutation_table.py`, quiet `skip-not-unpinned`) also re-classify the grader's failure with the base program and have a quiet "not my case" status, so they may share this pattern. No instance was searched for there, and this PR does not change them.

## Friction

none

## Approval

Owed: tvofi's approving review at the head, or an approval under a labelled mandate. Required because the PR edits `.claude/rules/ci-autofix.md` (policy) and its generated `.cursor/rules/ci-autofix.mdc`. The change names one new red autofix status and states that the classifier is base-pinned. It addresses process state (d).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
