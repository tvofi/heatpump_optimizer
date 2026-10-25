Fix review: merge fa23170a1a2d82923087f173c5919fd275df30b7

bus-nonce: 524fd5eca439680391ab1021b6d13e6d

Round 2 (delta review of e3c97ba6..fa23170a). Head measured: fa23170a1a2d82923087f173c5919fd275df30b7, still the PR head when this verdict was written. The role contract was current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` was empty.

## Carries

- Carry 0 (D15 triage, redaction incomplete): satisfied, and the delta does not regress it. The delta does not change `_private_values`, `_without_values` or the value pass at the return of `async_get_config_entry_diagnostics` (custom_components/heatpump_optimizer/diagnostics.py:313-337). The census adds one exempt section, `.exported_at`. That section holds only the export clock's ISO text and no text the install supplies. Mutant: the value pass replaced by identity at the return. 1 of 135 failed (`Download diagnostics carries none of the values its redaction removes ...`). Killed (ev/mutant-carry0-value-pass-identity.txt).
- Carry 1 (#2814, no export time, no label for the frozen collection): satisfied.
  - Export time: diagnostics.py:304 reads the clock once, and diagnostics.py:318 sets `exported_at`. Check `the download carries its own export time ...`. Mutant M2 (line deleted) killed: census `exempt-gone=['.exported_at']`, then KeyError.
  - Window: debugger.py:300-317 `collection_window`, spread into the manifest at debugger.py:619 beside the configured `days`. The checks are `the manifest labels the finished collection ...` and `a collection with no row has no window ...`. Killed: M3 (window removed), M6 (min/max to first/last; the fixture's rows are out of order), M7 (age from the first row rather than the last) and M8 (age at `started_at` rather than the export clock).
  - `days` stays the configured 7, and the measured `span_hours` sits beside it. The body's alternative (f) gives the reason: an `hpo-debug/1` schema key keeps its meaning. I accept it.
- Carry 2 (P119): satisfied.
  - VERIFY, re-derived: coordinator.py:7508 `_plan_age_minutes` measures against `dt_util.now()` when the payload is built, so the published value is the publish-time age.
  - Remedy: diagnostics.py `_plan_summary(data, now)` recomputes the age from `last_optimization` through `drift.stored_age_seconds` at the export clock.
  - Controls, re-run by this seat against a payload stating 0.8:
    - A fixed clock 14 min after `last_optimization` reads 14.0.
    - Null control: 1 min reads 1.0.
    - -5 min reads None, and no solve reads None.
  - The carry's mutant (the published value kept, `data.get("plan_age_minutes")`): 3 of 135 failed, with the 14 and 1 checks reading [0.8]. Killed (ev/mutants.txt M1).

## Findings

- The forward-carry to R10-REPLAY-REAL-DAY is present on main's roster: `after` names R10-DIAG-REDACT, and the brief reads "the fixer commits it only after R10-DIAG-REDACT's redaction holds on the exported document". It states the precondition but not the control the body names, `export.check_file` and `seal` run on the owner's exported day. That group's fixer must run that control on the real exported document. Carry: R10-REPLAY-REAL-DAY
- The class census leaves `input_ages_minutes` (publish-time per-entity ages) and `plan_stale` (judged at publish) open, together with the run time of the stored self-test results. All three are #2814 remainders the body dispositions there, and this PR does not close #2814. Carry: #2814
- Class census instrument: the body's census rule ran as an inline script that is not in the tree, so this seat did not re-run it. I checked its output by reading `_plan_summary`'s copied tuple: at the head it no longer copies `plan_age_minutes`. Carry: dismissed: a one-time census whose output was confirmed by reading the code; an instrument in the tree is not worth building for it

## Evidence

- RESULT debug_collect at head: ALL 135 DEBUG COLLECT CHECKS PASSED (ev/debug_collect-head.txt). On the `git merge-tree --write-tree origin/main HEAD` tree it also gives ALL 135 PASSED (ev/debug_collect-merged.txt).
- RESULT mutants (this seat's own, each applied and then restored; ev/mutants.txt, ev/mutant-ge-to-gt.txt):
  - M1 keep-published: killed, 3 failed.
  - M2 no-exported_at: killed.
  - M3 no-window: killed.
  - M4 drop the ahead guard: killed, 3 failed.
  - M5 ahead reads 0: killed, 3 failed.
  - M6 min/max swap: killed.
  - M7 age from the first row: killed, 2 failed.
  - M8 window age at `started_at`: killed.
  - ge-to-gt in `stored_age_seconds`: killed, 1 failed.
  - The carry-0 value-pass identity mutant: killed, 1 failed.
  - The working tree was clean after each.
- Figures re-derived: 135 checks (body: 135); the plan age reads 14.0, 1.0 and None at +14, +1 and -5 min (body: the same); 8 of 8 round-2 mutant kinds killed (body: 8 of 8; my set overlaps theirs and adds M7 and M8). Not re-derived: the base-side figure (0.8 at e3c97ba6; my M1 mutant reproduces that behaviour), the architecture score dS +0.0000, the scoped-gate MODE line at 69a02ccd5 and the 21 unpinned sites (CI's mutation lane covers them).
- The finder harness: the owner bundle and the triage record (dev/programme/triage/s6-batch24.md#P119, #2814) are not in the tree. As in round 1, the companion is the fixer's own synthetic `_aged_download`, which the body discloses as such. This seat applied the triage's own rule (`plan_age_minutes` against the export time minus `last_optimization`) through those checks and through mutant M1.
- `tests/structure.py`: STRUCTURE RATCHET PASSED. `tests/closure.py no-copies`: clean.
- `tests/entities.py` at head: 2 of 2445 failed. They are `gate-sweep.yml: on CI's completion ...` and `graders-head-copy's delivery_status step ...`, the same two the body reproduced at the merge base with the diff absent. Both read workflow files and neither reads diagnostics.py, debugger.py or drift.py (ev/entities-head.txt). The ge-to-gt mutant was applied to drift.py for a few seconds while this run was in progress. entities.py's two failures do not read drift.py, so the count is unaffected.
- Merge: `git merge-tree --write-tree origin/main HEAD` exit 0, no conflict (ev/merge-tree.txt). The head already contains origin/main c9cbe6b45 (merge base = c9cbe6b45), and main has not touched custom_components/ or tests/debug_collect.py since then.
- VERSION, the manifest version and the RELEASE_NOTES heading are untouched by the delta.
- Step 7: the body's `## Head` names fa23170a1a2d82923087f173c5919fd275df30b7, the head measured.
- CI at the head (check-runs API, at read time):
  - `tests / mutation` is failure. The body answers it under Red checks: unpinned sites for mutation-autofix, with ci_predict.py as the cheaper detector, which ran.
  - `governance / delivery-status` is failure. It reads main's overdue rows, the body answers it, and it is not a required check and does not block.
  - Still in progress at read time: fast, closures, coverage, browser, mutation-pins (1, 2), instrument-self-tests and codeql python. So the step-11 answer for any later red is not judged here. That is for the merge train's head check.
  - Concluded green: arch-score, arch-instrument, typing, closure-scope, briefs, policy-docs, env-matrix, wave-script, nightly-status, hassfest, validate-hacs, budget-raise-gate.
