Fix review: merge 1714570520834ec4edd5e6a21bb5e477b7a3d382

bus-nonce: 9705d9191efdaea4192f643743d85671

Round 1 (sonnet). Measured at head 1714570520834ec4edd5e6a21bb5e477b7a3d382 (the body's authored head 0f9759f4 plus the delivery-row commit); merge base 28d46c49.

## Evidence
- RESULT cause/state/cost/countermeasure all present in dev/audit/rca/r10-rca-flush-dispatch.md. Cause: job taken as the dispatch unit, API runs a workflow. State (c), argued against (a) (no gate absent), (b) (cost gate obeyed with the wrong unit), (d) (record-autofix moved into nightly.yml 3 days before P88). Cost test carries numbers; countermeasure A refused under the bound with a measured blind spot, B proposed as owner policy.
- RESULT harness re-run: runs 7 ids -> runs=7 runner_min=3557 record_autofix_min=6 cancelled=7 lost_ledger_min=916 (ev/runs7.txt). since 2026-10-26T02:31:17Z and since 2026-10-21T00:00:00Z both -> runs=26 runner_min=15909 record_autofix_min=33 cancelled=7 lost_ledger_min=916 (ev/since*.txt). Every row of the doc's 7-run table matches.
- RESULT null control: runs 42320317707 42372556020 -> schedule 903 min, ledger-push=success, lost=0; push run total=0 (ev/null.txt).
- RESULT mutant: forcing landed=True in a copy of the harness turns lost_ledger_min for the two lossy runs from 915 to 0 (ev/mutant.txt), so the lost figure moves with the instrument. (Per-run 788+127=915; the 916 total is of unrounded minutes.)
- RESULT claims in nightly.yml / stamp.py: FLUSH_MAX_DISPATCHES = 3 (stamp.py:2336); mutation-nightly, mutation-ledger, slow, nightly-ha gated on github.event_name != 'push' (nightly.yml lines 52, 158, 421, 513); record-autofix is a job of the same file. triage P404 is present on origin/handoff/audit-r10-roster.
- RESULT registration: fold_ledger.py check -> 0 violation(s); fold_ledger.py sync is a no-op (audit-find.js already carries the schema); check-wave-script.mjs 224 passed 0 failed; structure.py STRUCTURE RATCHET PASSED (no budget file in the diff); the harness is added to tests/closures.json INERT READS; delivery row dev/programme/delivery/3285.md is in the diff (ev/cheap.txt).
- RESULT untouched: three-dot diff of VERSION, RELEASE_NOTES.md, tools/release/stamp.py, .github/workflows/nightly.yml and dev/governance/roles is empty; no claim file or golden touched. git merge-tree --write-tree origin/main HEAD rc=0 (ev/mt.err). Commit messages carry no footer or trailer.
- RESULT CI: merge_train.py classify -> GREEN (ev/classify.txt). Across all 68 check runs (two pages, ev/checks_all_pages.txt) the only non-success non-skipped are tests / nightly-status (failure; grades main, and the diff reaches none of its inputs, so not this PR's) and governance / instrument-self-tests (cancelled at 14:20Z, while the gate re-ran; a cancel is not a red conclusion, and the diff touches no instrument that lane tests). An earlier gate run ended red only with "run(s) still being judged" after its wait expired; it re-ran green at 14:21Z. The body's "## Red checks: none" holds.
- Not re-derived: the body's tests/entities.py "ALL 2643 ENTITY CHECKS PASSED" (no Home Assistant in this seat; CI's tests / closures ran green on this head); the stamp-log attribution of 5 of the 7 dispatches (the doc labels it the triage's); the 3 to 6 h fleet-queue estimate and the 35 to 70 min per-flush queueing (the doc labels both as the triage's estimates).
- Class open (step 6): the doc's section 4 enumerates 7 code callers, 1 affected; the one affected is the instance fixed by R10-FLY-STAMP-FLUSH-COST. No other seat is in the diff or undispositioned.

## Findings
- Residual: the proposal-triage.md cost line pricing a dispatch by the jobs it runs is the only (c) countermeasure and is not landed; it is policy awaiting the owner. Carry: dismissed: policy change awaits the owner decision
- Follow-up: the instance fix (nightly.yml inputs.lanes, lanes=beat payload arm, entities pin) is not in this PR by design and is the live defect until R10-FLY-STAMP-FLUSH-COST merges. Carry: dismissed: already in that group brief by triage P404
