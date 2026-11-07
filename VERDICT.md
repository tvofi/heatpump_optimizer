Fix review: merge 5cf07f77a1b7090a1d813e9747765c6807b98055

bus-nonce: 0e48788535ab45f4187cb523aecf2bce

Round 2 adversarial fix review of #3263 (R10-HOTFIX-NIGHTLY-STATUS), from a detached worktree at 5cf07f77a1b7090a1d813e9747765c6807b98055, three-dot against merge base f2a015142714383722bf49d7ab20d8398ec9674c (= origin/main). The finder's harness is round 1's `evidence/ns_check.py` and its mutants (verdict/3263), re-run here at this head; the fixer's harness `dev/audit/harnesses/r10_nightly_status_mutants.py` is run beside it. Every round-1 finding is closed by my own re-run.

## Findings

- Reviewer mutant X6 SURVIVES: in `main`, `except Unreadable:` broadened to `except Exception:` (`ev/reviewer-extra-mutants.txt`). Claim: the in-flight fetch's handler is pinned to `Unreadable`. Harness: the PR's sliced checks via `ev/xmut.py`. Metric: slice rc. Perturbation: X6 gives rc 0, while X1 to X5 each give rc 1, so the harness moves. The survivor fails safe: a swallowed non-`Unreadable` error leaves `fly_jobs` None, so the failure stays FAILED (red), never green. M13 (handler narrowed to another type) is killed. Nothing owed. Carry: dismissed: fails safe toward red, no grading path turns green under it

## Evidence

- RESULT: round-1 M2, M4, M6, M8 and M10 are each KILLED by the PR's named checks at this head (`ev/fixer-harness.txt`): `RESULT killed=15/16`, unmutated rc=0. M2, M4, M6 and M8 are killed by "a failed lane is superseded only by a NEWER in-flight run ...". M10 is killed by "main fetches the in-flight run's jobs ...".
- RESULT: the finder's harness `ev/finder_ns_check.py` at this head prints PR-CHECK PASS and PROBES PASS (`ev/finder-check-head.txt`). Applied to this head's code, mutants M2, M4, M6 and M8 each flip their round-1 probe (B3; B2 and B5; B1; B1). So the probes still detect them, and the PR's check now carries those arms.
- RESULT: the mutation proof was re-run on every changed grading line (M1 to M16). The only survivor, M12 (drop the `concluded is not None` guard), is equivalent. When `concluded` is None, `collect` returns `jobs = []` (nightly_status.py L689), so `failing_jobs` is falsy. `verdict` also returns RUNNING or never_ran at L423 or L430, before it reads `in_flight_jobs` at L491.
- RESULT: reviewer extra mutants X1 (only the first bad job), X2 (`run_failed` kept), X3 (`>` to `<`), X4 (any conclusion counts as green) and X5 (fetch without the failing guard) are each KILLED. X6 is under Findings.
- RESULT: null controls. The old check (b0ef8f54) against this code kills only 4 of 16 (`ev/null-oldcheck.txt`). This check against the pre-fix grader at the base gives unmutated rc=1 (`ev/null-base.txt`). A genuinely failed lane stays FAILED in 9 arms of `verdict`, plus the newer-failed and unreadable arms of `main` (exit 1).
- RESULT: the window figure in the code comment is corrected and re-derives. From the API, 42235215315 `updated_at` is 18:06:31Z (failure) and 42242870295 `updated_at` is 19:17:32Z (success), 71 min 1 s apart (`ev/runs-api.txt`).
- RESULT: the round-1 red-checks finding is closed. Check run 128206881487 is `gate` attempt 1 of edit run 42309259823 at b0ef8f54. The body names that run's `gate` red (attempt 5, job 128239026202), quotes the same deferral text and answers it: cheaper detector, none from this seat; the gate's ordering is the gate workflow's.
- RESULT: red checks at this head, all 55 check runs on one page: two concluded reds.
  - `gate` 128266263058 (edit run 42327440324): "FAIL run(s) [42327439751] at this head are still being judged; their gate decides". This is the edit-run deferral. The code run's `gate` 128274624678 concluded success at 02:38:51Z.
  - `governance / instrument-self-tests` 128266024727: cancelled at its 30-minute timeout (02:05:51Z to 02:35:54Z). That is the owner's standing line (R10-PROCESS-SLIM, #3245), and the body pre-answers it (Carry R10-HOTFIX-SELFTEST-TIMEOUT).
  - `pr-contract / pr-contract` 128274216702 started at 02:36:50Z, after the last red concluded, and passed. Under fix-review.md step 11 that run is the evidence that the body answered its reds.
- RESULT: CI. `merge_train.py classify` read RED while only the edit-run deferral was red (`ev/classify-loop.txt`), then WAIT, then `02:42:29Z rc=0 GREEN 5cf07f77a1b7090a1d813e9747765c6807b98055 pending: none red: none` (`ev/classify-final.txt`).
- RESULT: merge. `git merge-tree --write-tree origin/main 5cf07f77a1b7090a1d813e9747765c6807b98055` gives rc 0, and the tree is 6871f15e, the head's own tree (`ev/merge-tree.txt`). The head's tree equals 795e8aae's tree (6871f15e), so `git diff 6871f15e 5cf07f77a1b7090a1d813e9747765c6807b98055` is empty: the merge added nothing beyond the receipted code and main.
- RESULT: diff scope (three-dot, `ev/three-dot.diff`): 5 files, +249/-1. They are `tests/nightly_status.py`, `tests/entities.py`, the new harness, `tests/closures.json` (the harness classified INERT) and `dev/programme/delivery/3263.md` (the delivery row). VERSION, the manifest, RELEASE_NOTES.md, `tests/golden`, `*_budgets.json` and `.github` are untouched (`ev/untouched.txt`, 0 bytes). `nightly.yml` is untouched, so the nightly's strength on production code is not weakened.
- RESULT: the body's figures re-derive at this head:
  - `PYTHONPATH=tests/hastub python3 tests/entities.py`: "ALL 2642 ENTITY CHECKS PASSED", rc=0.
  - `tests/harness_headers.py`: rc=0.
  - `tests/structure.py`: STRUCTURE RATCHET PASSED.
  - `tests/closure.py select`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
  - The harness gives killed 15/16 at this check and 4/16 at the old check, and unmutated rc=1 at the pre-fix grader.
- RESULT: `## Head` names 5cf07f77a1b7090a1d813e9747765c6807b98055 and the receipted code head 795e8aae. The commit messages carry no Co-Authored-By, claude.ai or session trailer (grep count 0).
- RESULT: packet rendered (`ev/review-packet.md`). Its one refusal at render, `required-red` (gate), was the edit-run deferral above and later cleared to GREEN. carry_audit printed 0 items, and figure_lint resolved 10 of 10.
- RESULT: setup. `cloud-setup.sh --check` printed OK.

## Friction

- The brief asks for a handoff-wip push at each milestone, and also to push nothing but the probe ref. I pushed only the probe ref. Carry: dismissed: brief conflict resolved toward the narrower instruction
