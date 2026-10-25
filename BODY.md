R10-PLAN-ISSUES-CHART: ports the out-of-tree issues chart into `tools/audit/seat/plan_page.py` as the page's first section, "Projected open issues". Open GitHub issues carried by not-done roster groups are projected to close at the planned finish of the last group carrying them; issues closed on GitHub are dropped; an issue with any carrier lacking a planned finish stays flat; other open issues (e.g. #201) are counted in a note. The open set comes from the snapshot's issue states (`--github-snapshot`), so the self-test needs no network; with no `gh` and no snapshot the page is still written and the chart is omitted with a note. The CLI is unchanged. Seam: only the section, its data function `project_issues` and the `gh`-missing fallback; the rest of the page is R10-ORCH-PLANPAGE's.

Alternative rejected: a separate script patching plan.html (the reference) is a second renderer and a second reader of the roster; folding it in shares `roster_lib`, the CSS variables and the SVG classes. A divergence from the reference: an issue on one planned and one unplanned group is flat (the reference counted it twice).

## Head

97caf81235b9f93b6f66bec01e3bbc7ac1e95b73

## Mutation proof

`python3 dev/audit/harnesses/r10_plan_issues_chart_mutants.py` at the head above: M0 null rc=0 fails=0; every mutant killed with a FAIL line: earlier-finish (min for max), closed-counted, unplanned-dropped, unplanned-also-closes, other-uncounted, offline-not-omitted, gh-missing-crashes, not-first. `python3 dev/audit/harnesses/r10_plan_page_mutants.py`: survived=0 (an earlier draft of the section reused the `stampline` class and let `stamp-on-axis` survive; own classes now).

## Null control

Unmutated self-test: `python3 -I tools/audit/seat/plan_page.py --self-test` reports 0 failed; M0 of both harnesses is rc=0 fails=0. The base tree's `r10_plan_page_mutants.py stamp-on-axis` is killed, as it is again at the head.

## Figures

- `python3 -I tools/audit/seat/plan_page.py --self-test` prints the check count and 0 failed.
- `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED.

## Red checks

none

## Forward-carry

none

## Friction

none
