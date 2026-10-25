Fix review: merge ddb4398a15abe3d445a959d922c1dc9b7f685831

bus-nonce: cb63cf3951d36d160fa79909cf56ef59

## Summary

Round 2: a delta review of PR #2833 (R10-PLAN-ISSUES-CHART). I measured head `ddb4398a15abe3d445a959d922c1dc9b7f685831` from a detached worktree at that SHA. The round-1 head was `541be6106c06457cfc4df04d1f65f26898af7208`. The scope was the two items in the brief (the harness depth seam and the pr-contract Red-checks omission) plus the PR's own code change since round 1. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract I followed is current. Both items are settled at this head.

## Findings

- The body's `## Red checks` line for `governance / delivery-status` says "this diff touches nothing that check reads". That is not literally true: the three-dot diff adds `dev/programme/delivery/2833.md`, which is a row the check reads. The red is still not this PR's. On both the round-1 head and this head the job lists only other PRs' rows as overdue (#2712, #2749, #2762, #2775, #2780, #2795, #2797, #2798, #2799, #2804, #2807, #2812, #2813). The job prints that it is not a required context, and adding the #2833 row cannot make another row overdue. Severity: low, wording only. Carry: dismissed: wording in a body answer, and the conclusion it supports (the red is not this PR's) holds under `ev/delivery_status_head.txt`

## Evidence

- Item 1, the depth seam, is settled.
  - The PR's own delta since round 1 is one hunk in `dev/audit/harnesses/r10_plan_issues_chart_mutants.py`: `ROOT = Path(__file__).resolve().parents[3]` became `ROOT = repo_root(__file__)`, and `repo_root` is imported beside `fail_name` from `r10_plan_page_mutants.py`. `tools/audit/seat/plan_page.py` is byte-identical to the round-1 head. Every other path in the 541be6106..head range came in from origin/main.
  - `repo_root` walks up to the directory holding `custom_components/heatpump_optimizer/manifest.json`. From the harness's real location it resolves to the worktree root (`ev/root_resolve.txt`).
  - Driver end to end at the head (`ev/issues_chart_mutants_head.txt`): RESULT mutant=M0 rc=0 fails=0 verdict=null. All 8 mutants were killed with FAIL lines: earlier-finish (fails=1), closed-counted (2), unplanned-dropped (3), unplanned-also-closes (2), other-uncounted (2), offline-not-omitted (2), gh-missing-crashes (1), not-first (2). RESULT survived=0. This matches the body's list.
  - Root-resolution mutants, each run with M0, show the driver fails loudly rather than passing silently:
    - `parents[2]`: rc=1, FileNotFoundError on `dev/tools/audit/seat/plan_page.py` (`ev/rootmut_parents2.txt`).
    - `parents[4]`: rc=2, refused, because git runs outside the repository (`ev/rootmut_parents4.txt`).
    - `repo_root` returning `here.parent` with no walk: rc=1, FileNotFoundError (`ev/rootmut_helper.diff`, `ev/rootmut_helper.txt`).
    - The marker changed to a path that does not exist: rc=1, `RuntimeError: no repository root above ...` (`ev/rootmut_marker.txt`).
    - Each mutant was restored, and the worktree is clean afterwards.
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` at the head prints ALL 112 HARNESS HEADER CHECKS PASSED (`ev/harness_headers_head.txt`). Putting the inline `parents[3]` walk back gives 1 of 112 HARNESS HEADER CHECKS FAILED with `FAIL depth seams: dev/audit/harnesses/r10_plan_issues_chart_mutants.py:26: ROOT = Path(__file__).resolve().parents[3]` (`ev/harness_headers_inline_walk.txt`). This is the body's figure and its red arm, re-derived.
  - Plan-page driver at the head: RESULT mutant=M0 rc=0 fails=0, RESULT survived=0 (`ev/plan_page_mutants_head.txt`).
  - Self-test: `plan_page self-test: 49 checks, 0 failed`, rc=0 (`ev/selftest_head.txt`).
- Item 2, the Red-checks omission, is settled.
  - On the round-1 head 541be6106 the check-runs API shows these failures: `tests / fast (3.14)`, `governance / delivery-status`, `pr-contract / pr-contract` x2 and `gate` x2 (`ev/ci_reds_round1_head.txt`).
  - pr-contract's own derivation excludes `pr-contract` and `gate` and required `governance / delivery-status,tests / fast (3.14)`. It refused because `tests / fast (3.14)` was not named (`ev/prcontract_541be_refusal.txt`). `gate` failed only because it relays those two runs (`ev/gate_541be.txt`).
  - The current body's `## Red checks` names both checks, and each line gives a detector and cost or a finding that none exists.
  - I ran `node tools/policy/policy_lint.mjs` from the head tree with the current body, with `--red` set to both names, the head and the merge base. The result was `PR-BODY: 0 error(s)`, rc=0, with `record red-history` naming the same two checks across 10 commits (`ev/policy_lint_head.txt`).
  - Null control: the same body with the `tests / fast (3.14)` line removed fails with the original ERROR, rc=1 (`ev/policy_lint_ctrl.txt`). The section's form is what checkPrBody requires.
- Null controls, my own probe (`ev/null_control_probe.py`, `ev/null_controls.txt`). This is my instrument, not the finder's, and it calls `issues_section` and `project_issues` directly.
  - Empty issue set: flat, 1 distinct y.
  - All issues closed: flat, 1 distinct y.
  - Every carrier unplanned: flat, 1 distinct y.
  - Offline snapshot: no polyline, with the "Omitted" note.
  - Positive arm: all open and planned gives 4 levels. The issue carried by two groups closes at the later finish, and #201 is counted in `other`.
- The delivery row `dev/programme/delivery/2833.md` is in the three-dot diff (`git diff $(git merge-base origin/main HEAD)...HEAD`).
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched three-dot.
- Merge: `git merge-tree --write-tree origin/main ddb4398a` exits 0 against origin/main `c78df2b86b5ec51d631eb0ed18bbac8feecd166a`, so there is no conflict (`ev/merge_tree.txt`).
- Head: `refs/pull/2833/head` is `ddb4398a15abe3d445a959d922c1dc9b7f685831` at verdict time, the head I measured and the one the body names (`ev/head_recheck.txt`, `ev/HEAD.txt`).
- CI on this head from the check-runs API (`ev/ci_checkruns_head.txt`, 37 runs) had not concluded at review time.
  - The only failure is `governance / delivery-status`, which the body answers and which is not a required check and does not block.
  - `tests / fast (3.14)`, typing, coverage, closures, browser, arch-instrument and codeql (python) were still queued, and instrument-self-tests and prelude were in progress. No pr-contract run on this head appears yet.
  - I cite CI as it stood and re-ran no heavy lane. The local `harness_headers.py` pass above is the cheap check behind the lane that was red in round 1.
- Discrepancy in the brief: it says the round-1 verdict was blocked on two items. The only round-1 verdict on the PR is `Fix review: merge 541be6106...`. The two items correspond to the `tests / fast (3.14)` and `pr-contract` reds that concluded on 541be6106 after that verdict. I reviewed them as the brief defines them.
