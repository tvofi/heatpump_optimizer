Fix review: merge a21a5f988f5aa70d197957361710c106438dd6c0

bus-nonce: c2a0eaa0aff9e842b1fb15097267eb70

Round 1, record PR, head a21a5f988f5aa70d197957361710c106438dd6c0 (measured at that head; CI classify GREEN at it).

## Findings

None.

## Evidence

- RESULT diff: three-dot diff against merge base ca6333333 changes exactly dev/programme/delivery/3142.md and dev/programme/triage/s6-batch104.md; no VERSION, manifest, RELEASE_NOTES or claim-file change.
- RESULT merge: git merge-tree --write-tree origin/main (407eb0cb3) exits 0, no conflicts.
- RESULT ci: merge_train.py classify prints GREEN, pending none, red none; ev/classify.txt. PR body names ## Head with the head (code head 18db0281, plus the delivery-row commit), ## Red checks none.
- RESULT grounds: orchestrator.md section 13 at origin/main carries the quoted sentence (line break only); tests/structure.py line 241 is PACKAGE_DIR under custom_components/; selftest_wiring.py, ci_budgets.json, INSTRUMENTS.md and instruments/ exist on main; tools/audit/seat/gantt_drift.py does not exist yet, as the ruling states.
- RESULT roster: on origin/handoff/audit-r10-roster, R10-PLAN-REAL-DURATIONS (M, sonnet fixer, files tools/plan/ and plan_page.py), R10-ORCH-PLANPAGE (delivery/3001.md present), R10-FLY-STANDING-CONTRACTS, R10-FRICTION-RECORDS, R10-GRADE-DRIVERS and R10-SAV-COMFORT (after R10-SAV-BASELINE) exist as described; R10-FLY-GANTT-DRIFT is absent, by design until the record merges. The roster has 304 groups now, so the body's 302 to 303 figure was at its own branch 1bc687570 and is not re-derived here.
- RESULT text: verdict ACCEPT, group, size S, sonnet fixer and opus reviewer, no after, files list and triage pointer agree across the ruling and the body. Thresholds are kept out of scope.
- Not re-derivable: the session-local stand-in (191 lines, 9 checks, 0.04 s), the acks file, the 17:54Z run, the seat ledger line and #3097's in-flight state live outside the repository. Added line 25 holds a grep pattern, not a host path; the packet reports no host-path refusal.
- Packet: refusals none, advisories none, carry_audit 0 findings, figures 2 resolved.
- Wording nit, no change needed: the PR title says s9 while the file says s10 and is named s6-batch104 as its neighbours are.
