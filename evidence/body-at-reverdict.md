_Requested by **tvofi**_

Part of #201.

`closures-autofix` runs the **base's** `tests/closure.py` (D11-s1-03, decision 0013's pinned grader), while `closures` runs the pull request's. When a PR moves a file out of INERT and commits a closure that reads it, the base copy's `check()` stops at the INERT-pair refusal before the under-approximation comparison. It prints no UNDER-SCOPED, so the autofix returned the quiet `skip-not-under-scoped` and went green beside a red `closures` that had printed one. No bot commit followed, and none could: the base `merge()` refuses the same pair. #1846 hit this twice and #1851 once.

This PR makes the autofix notice when its pinned classifier disagrees with the grader:

1. The `closures` job's "Fail if tests/closures.json under-approximates" step now runs under `set -o pipefail` and tees `python -u tests/closure.py check ... 2>&1` to `$RUNNER_TEMP/closures/check.txt` on both arms. The existing `always()` upload carries it, and `.txt` sits outside every `*.json` glob that `check`/`merge` read.
2. `apply_under_scoped_recordings` returns a new **red** status, `skip-classifier-disagrees`, when its own check printed no UNDER-SCOPED and `check.txt` has a line starting `UNDER-SCOPED: `. The status is not in `AUTOFIX_QUIET` and has its own `_AUTOFIX_STATUS_REMEDY` entry pointing to `derive_closures.sh --single`. The file is read only as data and can only redden the job; nothing it says can make the job push.
3. `.claude/rules/ci-autofix.md` names the status in the red list and in "What green means", and says the classifier is base-pinned. `.cursor/rules/ci-autofix.mdc` was regenerated with `rules_sync.mjs`. The file's token cap had zero headroom, so the cost was paid inside the file and the cap was not raised.

**Bootstrap: this PR cannot exercise its own new status in CI.** `closures-autofix` runs `origin/main`'s pinned `closure.py`, which lacks the new branch until this merges, so the new red can first fire on a PR opened after the merge. The `check.txt` tee runs at this PR's head, because `closures` runs the PR's own `tests.yml`. Everything below was demonstrated locally against the real CI logs.

## Head

`f70cd730c60e1c6b9d505a26d27f0f2e0d14e31f` merges origin/main `aa7a81192`, with no hand resolution, into this PR's previous head.

`f70cd730c60e1c6b9d505a26d27f0f2e0d14e31f` merges the authored code head `640ef43fa4c224cc5b85c8ebfe54f32843ff6e57` and then merges origin/main `aa7a81192`, with no hand resolution, into this PR's previous head.

`640ef43fa4c224cc5b85c8ebfe54f32843ff6e57`. Merge base with `origin/main`: 5f87e25a1.

The head contains, in order:
- the test-first commit 07b4701ee;
- the fix 05540e8f4;
- the orchestrator's main merge 5b660cd92 and the delivery row 40b41179e;
- round 2's test repair 640ef43fa.

Every figure below was re-taken at 640ef43fa, except the RED arm and the mutants. Those ran at 640ef43fa with the named file swapped, and each was restored with `git checkout HEAD --`.

## Root cause

From the root-cause seat's analysis on `handoff/r9-rca-closures-autofix-skip` (6d4a51b3e, `rca/RCA-closures-autofix-skip.md`; scan tables `rca/jobs.tsv`, `rca/p2.tsv`).

- **Cause.** `closures` and `closures-autofix` classify the same recordings with different programs. The autofix's "Restore the programs this job runs from the base commit" step checks out `tests/closure.py` at `pull_request.base.sha`. #1846 moved `DISCLAIMER.md` and `docs/index.html` from INERT to `INERT_EXCEPT` and committed closures that list them. The base copy still has them INERT, so `inert_closure_violations(committed)` fails first, `check()` returns 1 without printing UNDER-SCOPED, and the status is `skip-not-under-scoped`.
- **Process state: (d).** The process was sound, and then its precondition changed. The autofix (#498) was correct while it ran the same `closure.py` as `closures`, and its quiet "not my case" status assumed the two agree. 42460ce2f (F11.2, D11-s1-03) pinned the classifier to the base for a sound security reason, but nothing re-examined what the quiet status means once the two can disagree. #1569 fixed the same symptom from a different tree/program divergence. Following `defect-root-cause.md` for (d), the countermeasure makes the process notice the change; it does not add a firmer instruction.
- **Cost test.** The RCA counted every `tests.yml` `pull_request` run created 2026-09-26..2026-10-02: 423 runs, 0 list failures, 22 runs where `closures` failed and the autofix ran, and 15 of those printed UNDER-SCOPED. **3 of the 15** ended `skip-not-under-scoped`, spread across 2 PRs (#1846 at 9bc802e6 and e42b1cdd, #1851 at 3a28a3ea), and the RCA reproduced all 3. The defect costs an estimated ≥ 30 min of seat time per PR (one reviewer diagnosis cycle; not measured). The recurring cost of the countermeasure is one `tee` in `closures` plus one line scan in `closures-autofix` of the check step's output (10 lines in run 37019499517), which only runs on a failed `closures` (22 of 423 runs). That is well under 1 s per run, so the countermeasure was built.
- **Countermeasure and its demonstration.** Items 1–3 above. The detector goes red on the defect and stays green on the by-design path. See `## Mutation proof`, `## Null control` and `## Figures`.

## Mutation proof

Each arm was run at 640ef43fa with `PYTHONPATH=tests/hastub ~/hpo-seats/R9-F11.4-venv/bin/python3 tests/entities.py` (Python 3.14 with numpy and scipy). The edited file was restored with `git checkout HEAD --` after each arm, and the tree was clean after every restore.

- **RED, the fix withdrawn** (`tests/closure.py` and `tests.yml` at 5f87e25a1): `3 of 2065 ENTITY CHECKS FAILED`. The three are the #1846 case (`skip-not-under-scoped` for the defect), the apply-function status roster, and the tee wiring check.
- **M1, guard deleted** (`disagree = False and any(...)`): `1 of 2065`, namely `FAIL a pinned classifier that disagrees with the closures job's UNDER-SCOPED reddens (#1846)`.
- **M3, new status classified quiet** (added to `AUTOFIX_QUIET["closures-autofix"]`): `1 of 2065`, the same check.
- **M8, loose match** (`"UNDER" in l` for `l.startswith("UNDER-SCOPED: ")`): `1 of 2065`, namely `FAIL and stays quiet when the closures job printed no UNDER-SCOPED, or no check.txt exists (a46a91c null control)`. The real a46a91c line `INERT READS UNDER-APPROXIMATED` kills it.
- **P1, this step's `set -o pipefail` deleted:** `1 of 2065`, namely `FAIL the closures job tees its check to check.txt beside the recordings`.
- **P2, commented out:** `1 of 2065`, the same check.
- **P3, moved after `fi`:** `1 of 2065`, the same check.

P2 and P3 survived round 1. They are now killed because the wiring check requires an uncommented `set -o pipefail` line before the step's `if [ "$SCOPE_CASE"`. Each mutant edits only this step's lines, matched by the exact block.

`tests/mutation_table.py --scope changed --base 5f87e25a1` prints `no production file in scope; nothing to mutate` and `MUTATION TABLE PASSED (empty scope)`. The diff touches nothing under `custom_components/`.

## Null control

- **a46a91c's by-design failure.** In #1846's earlier run (Tests 37007613365, `closures` job 110839553394), `closures` printed `INERT READS UNDER-APPROXIMATED ... tests/doc_claims.py: DISCLAIMER.md` and no UNDER-SCOPED. Given that real check output as `check.txt` beside the same INERT-pair recordings, the head returns `skip-not-under-scoped`, job exit 0. The result is quiet.
- **No `check.txt`** (an artifact from before this change, or the fast arm): `skip-not-under-scoped`.
- **The fix withdrawn** (`tests/closure.py` at 5f87e25a1) gives `skip-not-under-scoped`, job exit 0, for all three inputs, the defect included. That is the defect.
- **The fixture no longer reads main's live INERT list.** `_af_case` takes the INERT set it needs (`inert={"DISCLAIMER.md"}` for these cases), so the base's classification is reproduced whatever main's `INERT_EXCEPT` holds. Round 1 failed because #1846 moved `DISCLAIMER.md` to `INERT_EXCEPT` on main.
- The predicate keys only on `skip-not-under-scoped`. `skip-clean` and `skip-not-allowed` are untouched. All earlier autofix checks in `tests/entities.py` (#523, #1569, R9-F10.9) still pass.

## Figures

- The 3 / 15 / 22 / 423 run counts are stated without a command here. They rest on the RCA seat's GitHub API scan, which lives only on the ref handoff/r9-rca-closures-autofix-skip at 6d4a51b3e (its rca/ directory holds the scan scripts and tables, none of them in this tree), and they were not re-taken. The round-1 fix reviewer independently re-derived 22 and 15 from those tables and replayed all five real CI runs.
- `ALL 2065 ENTITY CHECKS PASSED` at 640ef43fa, and the arm counts in `## Mutation proof`. Command: `PYTHONPATH=tests/hastub ~/hpo-seats/R9-F11.4-venv/bin/python3 tests/entities.py`.
- Real-log demonstration, against `$EXPORT/demo2.py` sha1 148756cbf202 (scratch, not in the tree). The script holds `DISCLAIMER.md` INERT, as the base did. It runs `apply_under_scoped_recordings` over `{harness_headers.py: [it, DISCLAIMER.md]}` with recordings reading `DISCLAIMER.md`, and with `check.txt` set to the timestamp-stripped check-step output of `closures` job 110886379255 (run 37019499517, e42b1cdd, sha1 e40d679b245a) or job 110839553394 (a46a91c, sha1 775720c7983c).
  - Head 640ef43fa: `e42b1cd defect: status=skip-classifier-disagrees job_rc=1`, `a46a91c null: status=skip-not-under-scoped job_rc=0`, `no check.txt: status=skip-not-under-scoped job_rc=0`.
  - `tests/closure.py` at 5f87e25a1: all three `skip-not-under-scoped job_rc=0`.
- `MODE: FULL -- every test script runs` from `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` (because `tests.yml` changed). The full gate is CI's.
- `STRUCTURE RATCHET PASSED`, from `python3 tests/structure.py`.
- `ci-autofix.md` measures 1428 tokens against a cap of 1428, and 92 lines against a cap of 96, from `node .claude/workflows/policy_lint.mjs --budgets`. `TOTAL: 0 error(s)`, from `node .claude/workflows/policy_lint.mjs`.
- `RULES-SYNC ok`, from `node .claude/workflows/rules_sync.mjs --check`.

Not run locally: the full gate, `tests/stress.py`, `features.py` and the solver goldens (numeric, CI only), and closure recordings (`PREPR_SKIP_CLOSURES=1`; off Linux).

## Red checks

- **fast (3.14)** went red at 40b41179e (job 110935386372, `2 of 2065 ENTITY CHECKS FAILED`). The two failures were this PR's own new checks.
  - **Cause:** they relied on main's live INERT list. The main merge 5b660cd92 brought in #1846, which moved `DISCLAIMER.md` to `INERT_EXCEPT`, so the INERT-pair fixture became a real UNDER-SCOPED that the base merged (`changed`). 640ef43fa makes the case pin its own INERT set.
  - **Cheaper detector:** it already exists. Running `tests/entities.py` locally after the main merge (seconds to minutes, under the 3.14 numpy/scipy venv) shows the same 2 failures before the push. That run was skipped at 40b41179e, because the merge was made after the seat's last local run. Its standing cost is one local `entities.py` run per main merge on a branch that touches `tests/closure.py` or `tests/entities.py`. No new countermeasure is built: the obligation to re-run steps 2–8 after a merge is already in `fixer.md` step 6.
- **pr-contract** went red at 40b41179e (job 110945652795). The cause was that the body did not answer `fast (3.14)`; this section now does.
- The new `closures-autofix` status cannot fire on this PR itself, because that job runs main's pinned `closure.py` (see the bootstrap note above).

- `nightly-status` is red: NIGHTLY ABSENT for `mutation-ledger` and `mutation-ledger-push`. That is main's red, not this diff's. Last night's scheduled run predates #1848, which added both jobs, and every open PR head carries the same red. This diff touches `tests.yml`, so the check is not exempt here. Cheaper detector: none; it measures a nightly that has not happened. The orchestrator owns the proof on main: a dispatched `tests.yml` run on main at aa7a8119, then the next scheduled run.

## Forward-carry

none. The RCA's class note is recorded here for the orchestrator to decide on, and nothing is built for it: `claims-autofix` (pins `env_drift.py`, quiet `skip-not-inherited`) and `mutation-autofix` (pins `mutation_table.py`, quiet `skip-not-unpinned`) also re-classify the grader's failure with the base program and have a quiet "not my case" status, so they may share this pattern. No instance was searched for there, and this PR does not change them.

## Friction

none

## Approval

Owed: tvofi's approving review at the head, or an approval under a labelled mandate. Required because the PR edits `.claude/rules/ci-autofix.md` (policy) and its generated `.cursor/rules/ci-autofix.mdc`. The change names one new red autofix status and states that the classifier is base-pinned. It addresses process state (d).

🤖 Generated with [Claude Code](https://claude.com/claude-code)


