Fix review: blocked e3c97ba6a694f98e490769b08b2a02be92ea6c50 carry-missing: carries 1 and 2 (export time and frozen-collection labelling, #2814; plan_age_minutes recomputed at download, P119) are neither satisfied nor shown not to apply

bus-nonce: b2689cdcb5d6363b16ca5b6088cf2215

Round 1 (first review of the fixer's handoff). Head measured: e3c97ba6a694f98e490769b08b2a02be92ea6c50, the PR head when read.

## Block

The brief binds three roster carries (roster 23b0a4cb). The diff and the PR body address carry 0 only.

- Carry 1 (#2814: the export does not label the frozen 7-day debug collection, has no end time or age, and has no export time). The diff touches only diagnostics.py, replay_doc.py, tests/debug_collect.py, the ledger and the delivery row. It adds no export timestamp and no label for the collection window. The body never names #2814. Not satisfied, and nothing shows it does not apply.
- Carry 2 (P119, lead L7: plan_age_minutes may be the age at publish). At the head, custom_components/heatpump_optimizer/diagnostics.py `_plan_summary` (around line 155-163) copies `data.get("plan_age_minutes")` from the published payload. That value is computed by coordinator.py `_plan_age_minutes` (line 7508) against `dt_util.now()` when the payload is built (coordinator.py:7942). Nothing recomputes it from `last_optimization` and the export clock. So the carry's VERIFY step resolves to "publish-time age", and the carry's remedy applies. Its fixed-clock test (14 min reads 14; null: 1 min reads 1) and its mutant that keeps the published value are absent. Not satisfied.

The cause is the one the brief names: the fixer's prompt omitted the roster carries (proposal V61). The fix is to add both carries to this PR, with their controls, or to get a recorded disposition from the orchestrator that moves them to another group.

## Findings

- Carry 1 (#2814) is unaddressed. Diagnostics needs an export time and a label for the frozen 7-day collection's end and age. Carry: R10-DIAG-REDACT
- Carry 2 (P119) is unaddressed. plan_age_minutes needs to be recomputed at download time, with the fixed-clock control, the null control and the keep-published mutant. Carry: R10-DIAG-REDACT

## Evidence

- Carry 0 (redaction incomplete): satisfied for the diagnostics download. The value pass in diagnostics.py (`_private_values`, `_without_values`, applied at the return of `async_get_config_entry_diagnostics`) redacts each value the keyed passes remove. tests/debug_collect.py plants a credential in every section and holds a section census, plus two null controls (clean bundle byte-identical; untouched fields identical). The triage's two original values are not in the tree. The body sends the exported-day check to R10-REPLAY-REAL-DAY as a forward carry, and that roster edit is owed by the orchestrator. I did not open that roster to confirm it.
- RESULT debug_collect at head: ALL 128 DEBUG COLLECT CHECKS PASSED.
- RESULT mutant (the value pass replaced by identity at the return): 1 of 128 failed, `Download diagnostics carries none of the values its redaction removes ...`, with the carrying paths listed (ev/mutant-value-pass-identity.txt). Killed. The other 8 mutants in the body were not re-run by this seat.
- The body's figure of 14 carrying paths at the merge base was not re-derived by this seat.
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0, with no conflict (ev/merge-tree.txt).
- VERSION, the manifest version and the RELEASE_NOTES heading are untouched by the diff.
- CI at the head (check-runs API, at read time): tests / mutation and governance / delivery-status are failure. The body answers both under Red checks: mutation as predicted unpinned sites for mutation-autofix, and delivery-status as main's overdue rows. delivery-status is not a required check and does not block. Several lanes were still in progress (fast, closures, coverage, mutation-pins, instrument-self-tests, codeql python), so the step-11 answer was not judged final.
- The finder harness: the finding's harness is the triage record (dev/programme/triage/s6-batch24.md) plus the owner bundle, and the bundle is not in the tree. The planted fixture is the fixer's own instrument, and the body discloses it as such.
