_Requested by **tvofi**_

Root-cause countermeasure RC1 of audit round 9 (`tools/audit/briefs/root-cause.md`, executing `.claude/rules/defect-root-cause.md`), for the check that would have gone red only on `main` at #1633 (R1a).

**Cause.** Five jobs that also grade `main` (`policy-docs`, `env-matrix`, `wave-script`, `briefs`, `coverage-ratchet`) restore their check source from the pull request's base first (`git checkout "$PINNED" --` with `PINNED = base.sha || github.sha`). A pull request is graded with the base's copy of every pinned path; the push to `main` is graded with the head's. The verdicts differ exactly when the diff touches a pinned path, and the pull request's own run cannot see it. At R1a head `a897272a` a leads fixture in `.claude/workflows/check-wave-script.mjs` (a pinned path) quoted `custom_components/heatpump_optimizer/boost.py`; `codeowners_gap.py` reads a path quoted in a file holding `new Function(` as executed, so `--check` on the head refuses 2 files, while `policy-docs` read the base's copy of that file and was green. The pinned file was the grader's **data**, not the grader.

**Process state: (c), followed and did not produce the intended result.** Two processes existed and were followed. (1) `graders-head-copy` (tests.yml, decision 0013 amended 2026-09-24) runs the head's copy of a pinned grader on the pull request, but it is keyed on the grader file changing and covers only `coverage_ratchet.py` and `delivery_status.py`; a pinned file another grader reads as data is outside its key. (2) `tools/audit/prepr.sh` runs the head's copy of `policy_lint`, `rules_sync`, `fragments_sync`, the hooks and the wave script, but never ran `codeowners_gap.py`, which arrived in `policy-docs` at `b6e3029` into a job that already pinned `.claude/workflows/*.mjs` (pinned since `51b0742`). So not (d): the pin predates the checker. The unmodified `prepr.sh` passes the defective head (Null control).

**Not the #1589 mechanism.** The brief called R1a "the same class as #1589"; git history says otherwise. #1589's last head commit (`abc431e`, 00:14:55 +0200) was green on its own tree (`uncovered_files=0`); #1592 merged at 00:19:30 and added quoted `tests/delivery_status.py`/`nightly_status.py` to `policy_lint.mjs`; #1589 merged at 00:59:37 without re-grading, and its CODEOWNERS de-owning met #1592's quotes. The base's checker on the merged tree also refuses, so a re-run of the PR's CI after #1592 would have been red. That is a stale-base semantic conflict, not base-pinned grading, and this change does not address it (the team memory's merge-into-main re-check does). Shared with R1a: the checker and the symptom, green PR then red `main`.

**Class reach.** Every program a both-event pinned job runs, and its local path before this change:

| grader | job | local path before |
|---|---|---|
| `policy_lint.mjs` (corpus, `--hooks`) | policy-docs | prepr 3, 3d |
| `rules_sync.mjs --check` | policy-docs | prepr 3b |
| `fragments_sync.mjs` | policy-docs | prepr 3c |
| `codeowners_gap.py --check` | policy-docs | **none** → 3e |
| `check-wave-script.mjs` | wave-script | prepr 4, on its own inputs only → also on any pinned path |
| `brief_lint.mjs` | briefs | **none** → 3f |
| `policy_lint_envmatrix.mjs` | env-matrix | none; exempt: 50 s, and whether its outcomes hold depends on the host (8 of 16 here, 15 of 16 on the review container) |
| `coverage_ratchet.py` | coverage-ratchet | none; exempt: needs a gate run's coverage payload; `graders-head-copy` covers it |
| `budget_raise_gate.py --rerun-stale` | budget-raise-gate-rerun | none; exempt: reads the API, not the tree |

**Change.** `prepr.sh` step 3e runs `codeowners_gap.py --check` always. When the three-dot diff touches a pinned path (`pinned_touched`, git's pathspec globs), 3f runs `brief_lint.mjs` and step 4 runs the wave script, whatever else changed: a pinned path can be any grader's data, and `check-wave-script.mjs` reads `tools/audit/prepare_baseline.sh` and imports `policy_lint.mjs`. 3g (`pinned_verdict`) reads the pinned jobs and their pathspecs out of `.github/workflows/*.yml` and refuses a grader that `prepr.sh` neither runs (an interpreter line after `rc=0`, not a comment) nor names in `PINNED_ELSEWHERE` with a reason. The reader fails closed: it refuses a job that names `PINNED` in a shape it does not know, a script named on a pinned job's run line with no interpreter on that logical line (backslash continuations joined), and a reading that finds no grader at all. A grader added to a pinned job later reaches the seat that adds it, with no edit here. Four `--self-test` cases drive the functions the steps call. The guard matches with here-strings, not `| grep -q`: under the script's `pipefail` a grep that exits on its first match can SIGPIPE the writer, and a first draft falsely named a grader unrun on 27 of 200 runs (Figures).

**Cost test** (wall-clock per release cycle). Standing cost: 3e 0.6 s on every run; 3f 4.1 s on a branch touching a pinned path (18 of the last 76 main merges); 3g a few milliseconds. Releases v6.6.11→v6.6.12 and v6.6.12→v6.7.0 carried 49 and 17 main merges; at an assumed 3 runs per pull request that is about 31–88 s of 3e plus 12–35 s of 3f per release. Defect cost: the one escape of a pinned `codeowners_gap` verdict held `main` red for 5 h 24 min (00:59 to 06:23, 7 merges landed on red, and #1604 repaired it); caught at review, as R1a was, it cost a blocked verdict and a fixer round (`a897272a` 04:42 to `c6ca4132` 04:55, plus the review). P(recurrence): 1 instance of the pinned-data shape in 76 main merges since the checker landed, so 0.2–0.6 per release. Even at the review-caught cost (≥ 30 min) the right side is ≥ 6–18 min against ≤ 2 min: it passes.

**Approval.** `prepr.sh` is not under a CODEOWNERS pattern (it is pinned) and is not in `CLAUDE.md`'s policy set, but the RC1 brief asks for tvofi's approval for any change to `prepr.sh`; the Mac seat holds tvofi's mandate until 2026-09-26T09:35Z. It adds seat-facing refusals, so treat it as needing that approval.

## Head

`8b6eb090`

## Mutation proof

Review round 1 (`blocked 8c7c1339`), each at `8b6eb090`:
- The reviewer's probe, D13 dropped from `ISOLATED_DIMS` in `tools/audit/prepare_baseline.sh`: `node .claude/workflows/check-wave-script.mjs` rc 1 (`105 passed, 1 failed`); this `prepr.sh` rc 1, `REFUSE wave-script 105 passed, 1 failed`. At `de347318` it printed `skip wave-script` and rc 0.
- Eight one-job perturbations of `governance.yml` with step 3e's run deleted (`$PINNED` unquoted, `${PINNED}`, the `PINNED:` line dropped, `PINNED: ${{ env.PIN_SHA }}`, `python3 -I -X utf8`, `python`, `uv run python`, a backslash continuation): `pinned_verdict` rc 1 on each (`--self-test`). The last four with 3e present: rc 0 on each, so the reader reads them rather than refusing them.
- Step 3e's call commented out, or moved above `rc=0`: `pinned_unrun` names `codeowners_gap.py` (`--self-test`).
- An empty workflow set: `pinned_verdict` rc 1, `no pinned grader found` (`--self-test`).
- `pinned_touched` on the real pins: a pinned `.mjs` and a file under `tools/audit/record-predicate/` touch a pin; `README.md` and `docs/HANDOVER.md` touch none (`--self-test`). An emptied pin list fails the first case.

Round 0:

- Step 3e's call deleted from a copy of this `prepr.sh`, run at `81f2c18c`: `REFUSE pinned graders  no local path for: tools/audit/round6/D11/fix/codeowners_gap.py`, rc 1.
- The reader's `|| github.sha` pattern broken (`github\.shaX`): `REFUSE pinned graders  none found in .github/workflows -- the pin reader no longer matches the workflows`.
- `--self-test`: `a pinned grader with its local run deleted is named` (fixture copy without 3e's call).
- The countermeasure on the defect: this `prepr.sh` at `a897272a` exits 1, `REFUSE codeowners_gap  RESULT uncovered_files=2 count REFUSED: 2 file(s) ...`.

## Null control

At `8b6eb090`, with this `prepr.sh` committed onto each tree (so the diff touches a pinned path and 3f and step 4 run): `a897272a` rc 1 (`REFUSE codeowners_gap uncovered_files=2`, `ok wave-script 116 passed, 0 failed`); `c6ca4132` rc 0; `81f2c18c` rc 0 (`ok codeowners_gap`, `ok brief_lint`, `ok pinned graders`, `ok wave-script 106 passed, 0 failed`).

Round 0, at `de347318`:

- The unmodified `prepr.sh` at `a897272a` (the defect): rc 0, no REFUSE line. No local path saw it.
- This `prepr.sh` at `c6ca4132` (fixed): rc 0, `ok codeowners_gap RESULT uncovered_files=0`, `ok brief_lint`, `ok pinned graders`.
- This `prepr.sh` at `81f2c18c` (base): rc 0, `ok codeowners_gap`, `skip brief_lint  no pinned path changed`, `ok pinned graders`.
- `--self-test`: `a pin that never grades main is not counted (null control)` and `every pinned grader has a local path or a reason (null control)` pass.

## Figures

- `python3 -I tools/audit/round6/D11/fix/codeowners_gap.py --check`: `81f2c18c` rc 0 `uncovered_files=0` (0.63 s); `a897272a` rc 1 `uncovered_files=2`, UNCOVERED `boost.py`, `datetime.py` (0.60 s); `c6ca4132` rc 0 `uncovered_files=0` (0.57 s). At `a897272a` with the pinned paths restored from `81f2c18c` as `policy-docs` does: rc 0, `uncovered_files=0`.
- `codeowners_gap.py --check` at every first-parent `main` commit from `b6e3029^` to `81f2c18c` (75 commits): red on 8, `b891be9` (#1589) through `f5d4743`, green again at `fab6959` (#1604). The same check at `b891be9^2`: `uncovered_files=0`; the `23e8881` checker on the `b891be9` tree: `uncovered_files=2`.
- `brief_lint.mjs`, `policy_lint.mjs`, `fragments_sync.mjs` and `check-wave-script.mjs` at the 76 first-parent commits from `b6e3029^` to `cb78e997` (with tags fetched): rc 0 on every one, so `codeowners_gap` is the only pinned grader with a measured `main` escape.
- `node .claude/workflows/brief_lint.mjs`: rc 0, 4.1 s. `node .claude/workflows/policy_lint_envmatrix.mjs "$PWD" /tmp/envm HEAD`: rc 1, `8 declared outcome(s) held, 8 did not`, 50.6 s on this container; the fix reviewer measured 15 of 16 held on theirs, so the exemption states host dependence rather than a count.
- `bash tools/audit/prepr.sh` wall time: 32.2 s unmodified at `c6ca4132`; this copy 37.3 s there (3f ran), 33.6 s at `81f2c18c` (3f skipped).
- `bash tools/audit/prepr.sh --self-test` at `8b6eb090`: 113 passed, 1 failed (99 and 1 at `de347318`). The failure is `and the step's own output names the flag, so the step runs the figure check`, which fails identically at `81f2c18c` on this container (95 passed, 1 failed).
- The guard alone, 200 runs under `set -uo pipefail` (`pinned_unrun tools/audit/prepr.sh .github/workflows/*.yml`, empty output expected): the `| grep -q` draft named a grader on 27 of 200; `de347318` on 0 of 200.
- `python3 tests/closure.py select --diff origin/main`: `MODE: SCOPED -- 0 script(s) run, 26 scoped out`.

## Red checks

none

## Forward-carry

none

## Friction

- decision-0013: cost: `prepr.sh` is itself pinned, so `pr-contract` runs the base's `--self-test` and the cases added here first run in CI after the merge.
- decision-0013: unenforced: a pinned path can be a grader's input as well as a grader, and `graders-head-copy` keys only on the grader changing.
