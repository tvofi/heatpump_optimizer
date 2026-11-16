Fix review: merge 17c9dd0672322c18c03a0cd6781310d6596a6327

bus-nonce: 5f11d7cf38ea14b137cce061b3b020e7
pending-ci: gate

Round 1 (first review, full scope). Reviewed at head 17c9dd0672322c18c03a0cd6781310d6596a6327, detached checkout; role contracts current (`git diff <merge-base>...origin/main -- dev/governance/roles/` empty).

Note: figure: the body's "70 lines added, 0 removed" counts git lines inconsistently: the table's diff is 70 lines added and 3 removed (three last-item lines re-spelled with a trailing comma); by entry it is 67 added, 0 removed (ev/drift-control.txt, `entries lost base->head: 0 entries added: 67`). Carry: dismissed: paperwork, the measured entry delta is re-derived here and the table is byte-identical to the CI artifact

## Findings

- Non-blocking, deferred to the class countermeasure: the body's `## Red checks` says a root-cause seat is owed for the fourth round-11 re-record (#3606, #3629, #3652, #3671) and proposes a PR-time predictor; the class is already recorded as R10-RCA-SELFTEST-SCOPE-DRIFT (dev/audit/config/bugclasses.json, dev/audit/rca/R10-RCA-FAMILY-SELFTEST-SCOPE-DRIFT.md), whose section 6 drops the pull-request guard and assigns countermeasure A (a main-side bot re-records refused steps by union from the failing push run's own artifact) to R11-PRE-SHARED-FILES, still `not-started`. These re-records are further instances of that class, and this hotfix is exactly the manual step countermeasure A automates (control: CI artifact 14239570925 at e352724335 drives base 27 refusals to 0 when committed verbatim). Carry: R11-PRE-SHARED-FILES

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main 17c9dd06` at origin/main 6f422812 exits 0, tree 1307f21a (ev/checks.txt). The PR base is origin/main.
- RESULT artifact identity: run 43884631892's `selftest-closures` artifact (id 14239570925, zip sha256 673bed46..., matching the digest the job 133359880684 log prints) holds a selftest_closures.json byte-identical to the head's tools/ci/selftest_closures.json (sha256 55243ff5... both; ev/checks.txt).
- RESULT null control, re-derived (ev/ctl.py, ev/drift-control.txt): at the base checkout 6f422812 (governance workflow and table unchanged from e352724335), `selftest_scope.drift(base table, artifact steps, workflow_steps())` returns 27 refusals, all UNDER-SCOPED, matching the body's 27; with the head table it returns 0 refusals, 0 notes, and `stale()` is empty for both. Base 120 steps, head 120 steps, 0 entries lost.
- RESULT static: `python3 -I tools/ci/selftest_scope.py static` at the head prints `120 gated step(s), 0 problem(s)` (the body's figure).
- RESULT mutation: the PR writes no production line (data re-record). Planted instead: each of the 67 entries the head adds, dropped singly from the head table, run through `drift` against the artifact: 67 killed, 0 survived (ev/drop-mutants.txt). Disclosed limit: CI publishes only the union table, not the raw strace measurement, so the artifact stands in as the measured set; a drop is then refused by construction, and the non-trivial half of the control is the base's 27 refusals reproducing CI's count.
- RESULT finder's harness: none named; the finder's instrument here is main's own drift step, re-run above off-Linux by its own `drift` function. Harness built by this reviewer: ev/ctl.py (reviewer's, not the finder's).
- RESULT VERSION, manifest version and RELEASE_NOTES heading untouched (diff names two files: tools/ci/selftest_closures.json, dev/programme/delivery/3671.md). No claim file, budget, golden fixture or `custom_components/` path touched.
- RESULT class: the enumeration is the drift step itself over all 120 gated steps; with the head table it returns no step, so no seam is open.
- RESULT body head: the body names 17c9dd0672322c18c03a0cd6781310d6596a6327, the head reviewed.
- RESULT carry_audit on the body: see ev/carry-audit.txt. figure_lint: `FIGURES: 0 resolved, 0 not verified, 0 refused` (ev/review-packet.md).
- Observation only, not measured further: the measured `gantt-and-verdict-audit` entry adds repo-root probes `config`, `objects`, `refs`, which read like a throwaway git directory's layout folded to the checkout root; over-approximation is safe for scoping, and the head table carries them as measured. Carry: dismissed: evidence, not a finding
- RESULT CI: `merge_train.py classify 17c9dd06... --pr 3671` polled 16:14 to 16:44 UTC, every run exit 3, last line `WAIT 17c9dd0672322c18c03a0cd6781310d6596a6327 pending: gate red: none` (ev/classify-log.txt, ev/classify-last.txt); the ruleset's one required context is `gate` (tools/policy/fixtures/required-contexts.json), so it is the pending one. At 16:28 the head's test jobs (tests / fast (3.14), typing, coverage, closures) were still queued; arch-score was success, no run red. Head re-read at 16:44: refs/pull/3671/head is 17c9dd0672322c18c03a0cd6781310d6596a6327.
