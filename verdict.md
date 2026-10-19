Fix review: blocked 4d1730bd10c9f53cf83928051b7d43414fd9fe36 control-failed: fast (3.14) ended 53.13 min after its FULL run's creation, past the body's own 52.8 min bar; and mutant M7 (the reused-row ledger filter deleted) survives every check

Round 1. Measured head: 4d1730bd10c9f53cf83928051b7d43414fd9fe36 (merge base 4a3cbcf62, origin/main tip; roles/ unchanged vs origin/main).
Since the measurement the head has moved to c5b5d06c3. That is the expected `ci: re-record closures` from github-actions[bot] and it touches only tests/closures.json. Nothing below depends on that file except the closures re-run.

## RESULT lines

RESULT mutants_harness M1..M6 KILLED on aimed check; survivors=0 (ev/mutants.txt)
RESULT m0_here FAIL rc=1, 1 of 2356. The red is `graders-head-copy's delivery_status step ...`, and it fails identically at base 4a3cbcf62 in this container (1 of 2351, ev/base_entities_summary.txt). It is environmental and not this PR's; CI's graders-head-copy is green at this head.
RESULT m7_ledger_filter SURVIVED. With the `for _f in scripts.tsv provenance.tsv; awk '$2!="reused"'` loop deleted (ev/m7.diff), entities fails only that same environmental check (ev/m7_entities_summary.txt).
RESULT m7_effect under a floor FAIL. Head: scripts.tsv 20 data rows, 0 reused, `reused 0 of 20`. M7: 21 rows, 1 reused, `reused 1 of 21`, and provenance.tsv names a script reused that was in fact re-measured (ev/m7_ledger_*.txt). On a push to main that provenance.tsv is cached as the next base.
RESULT once_count_at_base 53 = 34 (lane-plan --all-scripts, 4a3cbcf62) - 1 (composed_closures.json: boost_drift_replay) + 20 (coverage_tree.sh DERIVED|fast at base). Re-derived independently; it matches the body.
RESULT full_run_control FAIL. Tests run 39333417268 (pull_request, head 4d1730bd) was created 22:13:39Z and `fast (3.14)` completed 23:06:47Z, an offset of 53.13 min against the bar of 52.8. Base push run 39310145738's offset is 57.80 min, re-derived (ev/base_run_fast.txt). The job's own duration fell 57.73 -> 51.85 min, but 77 s of queue time pushed the end past the bar. Under the body's own rule ("If this control fails, R(a) did not pay: the A3 Fallback applies, and the stub ships alone"), this PR as constituted does not pass its control.
RESULT stub_inert ci.yml: on = workflow_dispatch only; no push or pull_request trigger; `permissions: {}` at workflow and job; one job running `true`; no `uses:`; no `secrets`. Confirmed by reading the file.
RESULT merge_tree exit 0, tree df62eb70, no conflict.
RESULT version_files untouched (VERSION, manifest, RELEASE_NOTES, claim files).
RESULT mandate comment 6175172275 by tvofi at 2026-10-14T18:14:58Z. First line: "MANDATE: agents may approve as tvofi, scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z". The body quotes it verbatim.
RESULT carries b8a9cebe is an ancestor of handoff/audit-r10-roster and holds the 3 "From PR r10-ci-layout-p0" rows (CI-LAYOUT x2, STAMP x1), each stating its control.
RESULT ci_reds `closures` failed with UNDER-SCOPED (entities.py, harness_headers.py) and was followed by one `closures-autofix` success. Both are expected and named in the body. `ci-ratchet` did not run on this pull_request run. composed-proof was still in progress when read.

## Why blocked

1. **The control failed.** The brief asks that a pending control be reported as pending. This one finished, and it failed by about 20 s under the body's own definition (completed_at minus created_at). The job body itself was 5.9 min faster, so R(a) probably did pay. The bar as written, though, includes runner queue time, and this run misses it. The orchestrator or owner should decide between the body's fallback (the stub ships alone), a restated control that measures job duration (the comparator then reads 57.73 vs 51.85 min), or a re-measure on another FULL run. The reviewer should not pass it.
2. **A production line has no test (fix-review step 1).** The body claims "each script still has exactly one row in each" ledger. No entities check reads scripts.tsv or provenance.tsv, so the filter loop can be deleted and everything stays green. Owed: `_coverage_revalidation` also asserts that scripts.tsv and provenance.tsv hold one row per script and no `reused` row after a floor-FAIL re-validation. That assertion, with M7 added to the harness, kills the mutant.

All other claims I checked held at this head: R(a) placement, R(b) re-measure-only-reused, R(c) reused exclusion, the 68 -> 53 tightening re-derived at base, the budget-equality pin (M6), and the stub's inertness.

bus-nonce: 557ff3ace31438c2f1d994f9574a4e8e
