R10-PLAN-ISSUES-CHART: ports the out-of-tree issues chart into `tools/audit/seat/plan_page.py` as the page's first section, "Projected open issues". Open GitHub issues carried by not-done roster groups are projected to close at the planned finish of the last group carrying them; issues closed on GitHub are dropped; an issue with any carrier lacking a planned finish stays flat; other open issues (e.g. #201) are counted in a note. The open set comes from the snapshot's issue states (`--github-snapshot`), so the self-test needs no network; with no `gh` and no snapshot the page is still written and the chart is omitted with a note. The CLI is unchanged. Seam: only the section, its data function `project_issues` and the `gh`-missing fallback; the rest of the page is R10-ORCH-PLANPAGE's.

Alternative rejected: a separate script patching plan.html (the reference) is a second renderer and a second reader of the roster; folding it in shares `roster_lib`, the CSS variables and the SVG classes. A divergence from the reference: an issue on one planned and one unplanned group is flat (the reference counted it twice).

## Head

`ddb4398a15abe3d445a959d922c1dc9b7f685831` merges the authored code head `e0d052785ae0691439c4ba7c42790902b52f73ff` and then merges origin/main `f3ffb1c63` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

The authored code head is `e0d052785ae0691439c4ba7c42790902b52f73ff`. It adds one commit to `18cd6fdc2980a69de94ad9e26756900d2457dbdf` after a merge of origin/main (`d4c726f9d`, no conflicts): `r10_plan_issues_chart_mutants.py` now takes its root from `repo_root` in `r10_plan_page_mutants.py`, which it already imported `fail_name` from, instead of the inlined `parents[3]` walk that `tests/harness_headers.py` refused on `tests / fast (3.14)`.

## Mutation proof

`python3 dev/audit/harnesses/r10_plan_issues_chart_mutants.py` at the head above: M0 null rc=0 fails=0; every mutant killed with a FAIL line: earlier-finish (min for max), closed-counted, unplanned-dropped, unplanned-also-closes, other-uncounted, offline-not-omitted, gh-missing-crashes, not-first. `python3 dev/audit/harnesses/r10_plan_page_mutants.py`: survived=0 (`fail_name`, the one FAIL-line grammar, now lives in `r10_plan_page_mutants.py` and the new driver imports it, so `node tools/policy/agreement.mjs --py-json` reports unregistered=0; an earlier draft of the section reused the `stampline` class and let `stamp-on-axis` survive; own classes now).

## Null control

Unmutated self-test: `python3 -I tools/audit/seat/plan_page.py --self-test` reports 0 failed; M0 of both harnesses is rc=0 fails=0. The base tree's `r10_plan_page_mutants.py stamp-on-axis` is killed, as it is again at the head.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` prints ALL 112 HARNESS HEADER CHECKS PASSED (rc=0); before the fix it printed 1 of 112 FAILED with `FAIL depth seams: dev/audit/harnesses/r10_plan_issues_chart_mutants.py:26: ROOT = Path(__file__).resolve().parents[3]`.
- `python3 dev/audit/harnesses/r10_plan_issues_chart_mutants.py` prints `RESULT survived=0`, every mutant killed, M0 rc=0 fails=0.
- `python3 -I tools/audit/seat/plan_page.py --self-test` prints the check count and 0 failed.
- `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED.

## Red checks

- `tests / fast (3.14)`: the inlined `parents[3]` depth walk in the new driver. The cheaper detector is the depth-seam check of `tests/harness_headers.py`, which prepr runs locally; its standing cost is not measured. Answered: the walk is replaced by the shared `repo_root`, and the check is green at the head above (the pre-fix run was the red arm: restoring the inline walk makes it fail again).
- `governance / delivery-status`: main's backlog of overdue delivery rows; this diff touches nothing that check reads, so no detector in this PR could have predicted it.

## Forward-carry

none

## Friction

none


