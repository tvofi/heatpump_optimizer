Fix review: merge bd36aebf837e963ac8e804334ad53c1a691ebf1e

bus-nonce: 87c0d6bc1b097d7af22b2eac3aca8ac4

## Evidence
- Head measured: bd36aebf837e963ac8e804334ad53c1a691ebf1e (PR head at read time; one authored commit plus the delivery-row commit). Round 1 of this review.
- RESULT ruling: triage_refusal passes the P296 carry text on the committed file (None); ruling_verdict reads P296 as ACCEPT.
- RESULT mutation: with `Verdict: ACCEPT` changed to `Verdict: REJECT`, triage_refusal returns "dev/programme/triage/s6-batch65.md#P296 is not an ACCEPT ruling (REJECT)". Reproduced.
- RESULT null control: with the file absent, triage_refusal returns "the triage ruling ... is not on the roster branch or origin/main". Reproduced.
- RESULT mechanism: carry_audit.audit at the head unions an item's own markers with its `(item <id>)` references, and sets status bad if any token fails Dests.check, so a valid re-route cannot cure a bad token. Matches the ruling's account; the one-token-per-row rule is as stated.
- RESULT lint: a plausible carry appended to a copy of origin/handoff/audit-r10-roster's wave-r10-groups.json (group R10-FLY-CARRY-DISPOSITION, which exists there, size S, file tools/audit/carry_audit.py) gives brief_lint "TOTAL: 0 error(s)". The exact carry text is not in this diff (it is a held roster op), so I linted my own wording, not the orchestrator's. policy_lint: 0 errors across 50 policy files.
- The live replay figures for #2925 and #2962 (one bad row each, 0 after patching) were not re-derived: they need the live PR bodies and comments, which this seat does not read. They are the body's figures, not verified here. The mechanism and the destinations named as bad/valid are consistent with the tool's code.
- carry_audit at the head: 0 finding items, 0 unrouted, 0 bad destinations. This PR's body: Forward-carry none, Red checks none (no gate went red).
- Merge: git merge-tree --write-tree origin/main HEAD exits 0 (no conflict).
- Scope: diff is two markdown files (triage ruling, delivery row); VERSION, manifest and release notes untouched; no claim, budget, closure or golden file moves.
- CI at read: all completed checks are success or skipped; tests/coverage, tests/closures, tests/fast, tests/browser, governance/env-matrix and governance/instrument-self-tests were still in progress at read time, none red. No pr-contract run was listed yet. This verdict carries the head's state as read, not their conclusion.
- Body describes this head: yes (names bd36aeb and the authored head 42eb592).
