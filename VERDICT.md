Fix review: merge 541be6106c06457cfc4df04d1f65f26898af7208

bus-nonce: f2140a873ea6f68e0fb87ae7f2088351

## Summary

Round 1 review of PR #2833 (R10-PLAN-ISSUES-CHART). Measured at head `541be6106c06457cfc4df04d1f65f26898af7208`, merge base `c9cbe6b458a7053f914649eb02d5296d6cd8c0f4`, from detached worktrees at both. Role files: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current. The roster's group entry (handoff/audit-r10-roster `2b7fe35c67ca`) has `carry: []` and `architect_note: null`. Every control its brief names has a mutant that kills it.

## Findings

- The chart's note says the open set is "as GitHub had them at the plan's start". `issues_section` actually reads the set from the snapshot taken at render time (a `gh` fetch in `main`, or `--github-snapshot`), not from the plan's `generated.start`. In the documented use, a render right after a replan, the two moments are minutes apart; a later re-render of an old plan would show the wrong timestamp. Wording only: the data and projection are correct. Carry: dismissed: wording in a low-severity instrument note, and the documented workflow (render after a replan) makes the two moments coincide
- `tests/entities.py` (venv-ci, `PYTHONPATH=tests/hastub`) fails 2 of 2445 checks, and the set is identical at the merge base and at the head. The two checks are `gate-sweep.yml: on CI's completion, no concurrency, main's program on the trigger's run id alone, ...(U0c)` and `graders-head-copy's delivery_status step is red only when this copy's exit differs from the base copy's, or this copy alone prints OVERDUE`. Neither file is reached by this diff. Carry: dismissed: pre-existing at merge base c9cbe6b45, not caused by this PR (coordinator's extra point; see Evidence)
- `tools/plan/replan.py` at this tree (file untouched by the diff) raises `KeyError: 'XS'` on the current handoff/audit-r10-roster roster, because `sizes_hours` has no XS. I built the null-control plan from a copy of the roster with XS rewritten to S. Carry: dismissed: outside this PR's seam (replan.py is not in the diff); reported to the orchestrator in this verdict only

## Evidence

- Mutation proof (`ev/issues_chart_mutants.txt`), driver run by me at the head. RESULT mutant=M0 rc=0 fails=0 verdict=null. All 8 mutants were killed with FAIL lines: earlier-finish, closed-counted, unplanned-dropped, unplanned-also-closes, other-uncounted, offline-not-omitted, gh-missing-crashes, not-first. RESULT survived=0. These cover the brief's required controls: two-group later finish (earlier-finish), closed not counted (closed-counted), no-finish flat (unplanned-dropped).
- The existing plan-page mutant driver gives survived=0 with M0 null at both the merge base and the head (`ev/plan_page_mutants_base.txt`, `ev/plan_page_mutants_head.txt`). Moving `fail_name` changed no output.
- Unmutated self-test at the head: `plan_page self-test: 49 checks, 0 failed`. The body names no number, so there is nothing to re-derive.
- Null controls, my own probe (`ev/null_control_probe.py`, `ev/null_controls.txt`), on the real r10 roster (72 issues on open groups) and a replan of it. These are my instrument, not the finder's. No finder harness exists for an owner-requested instrument; the brief's controls are the design trace and all are tested.
  - Empty issue set and all-closed issue set: a polyline is drawn with 1 distinct y (flat at 0), no error.
  - Every carrier unplanned (`finish: None`): flat, 1 distinct y.
  - All open: 73 distinct y levels; project_issues gives close_at=72, unplanned=0, other=[201].
  - Offline snapshot: no polyline, "Omitted" note.
- Data source: `open_now` is taken from `snap["issues"]` with state OPEN, and `snap` comes from `--github-snapshot` or `_fetch_or_offline(fetch_github)`, as the body says. Projection: max of the planned finishes of open carrying groups, and any unplanned carrier makes the issue flat. This matches the body, including the divergence it states (one planned and one unplanned carrier gives flat).
- Coordinator extra point, tests/entities.py comparison by check NAME. Top-level failing set at the merge base = {gate-sweep.yml ...(U0c), graders-head-copy's delivery_status step ...}; at the head it is the same set (`ev/entities_*_toplevel_fails.txt`). Both runs print `2 of 2445 ENTITY CHECKS FAILED`. The other `FAIL a*:`/`hb:` lines are deliberate negative-control sub-results, preceded by their `ok ... passes/fails when` lines. Two of those differ textually between runs only in set-ordering and timing (a8:register_once extra list order, hb:positive_control measured ms). The fixer reported 4. I could not see their 4 names, and this environment shows 2, so I compared my two runs' sets rather than the fixer's count. No check fails only at the head: the extra point is satisfied.
- The new file `dev/audit/harnesses/r10_plan_issues_chart_mutants.py` is classified in `tests/closures.json`. entities.py's force-FULL classification check does not fail at the head.
- `python3 tests/structure.py` at the head: STRUCTURE RATCHET PASSED. The diff moves no budget.
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden/: untouched three-dot (`ev/version_untouched.txt`). The diff touches no claim file and no fixture, so env_drift has nothing to compare.
- Merge: `git merge-tree --write-tree origin/main 541be6106` exits 0 against origin/main `f3ffb1c635327365841ad430ce8fad7488a02d61` (`ev/merge_tree.txt`).
- Head: the body names 541be6106 (plus authored code head 18cd6fdc2 and merge 4a2d5c985). `git ls-remote` at verdict time shows refs/pull/2833/head = 541be6106c06457cfc4df04d1f65f26898af7208, so the head did not move (`ev/head_recheck.txt`).
- CI on this head (`ev/ci_checkruns.txt`, check-runs API, 26 runs): no run has concluded failure. prelude, refresh and cancel-superseded succeeded; record, delivery-status-publish, kernel-points and arm were skipped. The gate lanes (mutation, closure-scope, briefs, instrument-self-tests, codeql, hassfest, arch-score, budget-raise-gate) were still queued or in progress at review time, so the body's "Red checks: none" holds for what has concluded. Rule 11 has no red check to answer. This verdict reads CI as it stood at review time.
- Class: the group's issue list is empty and the brief states one seam (the section and its data function), so no enumeration rule applies. The body keeps to that seam, adding only the `gh`-missing fallback and the `open_iss` "—" when offline that the brief's offline requirement needs.
- Architecture: one renderer reads the roster through `roster_lib`, with no second script and no import of the out-of-tree reference. The CSS classes are the section's own, which the body explains avoids blinding `stamp-on-axis`.
