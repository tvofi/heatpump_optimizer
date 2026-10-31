Fix review: merge 7b42b54998f1544050329cacab65d20c0a513b09

bus-nonce: 1dae2128f423fbf5cf068b5716d663cc

Round 1, record PR (two files: dev/programme/triage/s6-batch75.md, dev/programme/delivery/3017.md); no production code.

## Findings

- The batch cites P308's seam as `carry_audit.py:206-209` and M1's as "line 222"; at current origin/main (5d4e0bcfb) the Evidence branch is lines 205-208, the body `else` arm 220-222. The cites were read at 437f1ba9b and drifted by one line when main moved; the substance (distinct seams, same file) holds. Carry: dismissed: record cite off by one line against a later main, prose only, no ruling depends on the number

## Evidence

- RESULT head: PR head still 7b42b54998f1544050329cacab65d20c0a513b09 at post time; `git merge-tree --write-tree origin/main` exits 0 (tree 9c5fc49c2), no conflict, no claim file touched.
- RESULT CI: `merge_train.py classify 7b42b54998f1544050329cacab65d20c0a513b09` exit 0, GREEN (pending none, red none); no gate check red, so step 11 owes nothing.
- RESULT roles: `git diff merge-base...origin/main -- dev/governance/roles/` empty; contract current.
- RESULT P309: probe report at origin/handoff-body/r10-rca-jidoka-yield resolves to c8f3acd99; it holds the M1 text, the 2 vs 18 min/day cost test and the shape-C section (lines 78-105). `dev/audit/` is an INERT prefix (tests/closure.py:321), as the ruling says. Group name R10-RCA-JIDOKA-YIELD is new in the roster branch (no existing group), consistent with "new S group".
- RESULT P310: probe table 21/125 after #2838 (19/73 PRs, 168 reviewed) and 50/334 before, 84 min median, 14 of 21 shape A, all present in the report (lines 21-24, 59, 101). Roster branch R10-FLY-RELAY-REVIEW-FF holds CARRY 0 (carry index 10): `carry_audit.py landed`, `land-ops`, bus.sh dispatch refusal, so "already carried" is true; `carry_audit.py` main has only check/pr/sweep/owners (lines 543-556), so "unbuilt" is true. The fold note records mandate 6329234399 and the orchestrator's approval, and the ruling states it records and does not grant it.
- RESULT P311: the six rules and the 5-distinct/at-most-2 split match report section (3); DEFER with a stated trigger (third instance of rules 2 to 4, or rule 3 recurring) is consistent with the batch's no-ACCEPT-without-measure rule.
- RESULT gates: `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body` on the batch file prints CARRY-AUDIT 0 finding items; figure_lint 2 resolved, 1 not verified (`git log`), 0 refused; review_packet refusals none, advisories none.
- Not re-derived: the 223-tip null control (155/165 rc 0, 10 flips), the 1330-commit enumeration and the 18 vs 2 min/day figures need the probe's vcore.py appendix and a full handoff-body sweep; I read them against the report and did not re-run them. The held roster ops the brief names (R10-RCA-JIDOKA-YIELD.json, b75-P310.txt) are not in this diff and the file names only the group JSON path, so I checked consistency against the roster branch (group absent, CARRY 0 present) rather than the ops themselves. A record PR has no mutation proof or both-ends harness; none was owed.
- tests/entities.py could not be run in this checkout (ModuleNotFoundError: layout); the CI closures and closure-scope checks are green at the head.
