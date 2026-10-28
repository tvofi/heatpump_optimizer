Fix review: merge 56e61dc9edbb61c293b22254928ad8e1548b1bb6

bus-nonce: 883a73ef784660da472bb9dbdba6a8f0

Round 1. Head measured: 56e61dc9edbb61c293b22254928ad8e1548b1bb6 (the PR head at fetch time). Docs-only change: one triage file plus the PR's own delivery row.

## Findings

none

## Evidence

- RESULT mutation: on the committed file `ruling_verdict` reads P271 as ACCEPT and P272 as REJECT. A text citing `#P272` is refused as "not an ACCEPT ruling (REJECT)". Citing `#P271` passes. Flipping P272's verdict line to ACCEPT makes the gate read ACCEPT, so the file's verdict lines are what the gate keys on (ev/mutation.txt).
- RESULT null control: with the file absent the gate returns "the triage ruling dev/programme/triage/s6-batch58.md is not on the roster branch or origin/main", as the body says.
- RESULT merge: `git merge-tree --write-tree origin/main HEAD` exits 0 with no conflicts. The base is b0b2d7697, and origin/main has moved but touches neither path (ev/merge-tree.txt).
- RESULT scope: the three-dot diff touches only dev/programme/triage/s6-batch58.md and dev/programme/delivery/2934.md. VERSION, the manifest and the RELEASE_NOTES heading are untouched. No claim, budget or closure file moves.
- RESULT figures: the quoted lines re-derive at this head. `sleep 300` is at ci-watch.sh:290, `POLL_SECONDS = 300` at merge_train.py:486, and `sleep 300` at prepr.sh:2549 and :3285. `triage_refusal` is at roster_edit.py:466 and `ruling_verdict` at :455. The V184 measurement and the roster and ledger paths (`~/hpo-orch/...`, `s7/...`, roster 54bd827cf) are out-of-tree. I could not re-derive them and did not verify them.
- Packet: carry_audit 0 findings, figure_lint 0 refused, no mutation-ledger diff, no refusals. The body names no finder's harness, and none is owed for a record-only triage.
- Role contracts: dev/governance/roles/ is unchanged between the merge base and origin/main.
- Forward-carry: the body states none. P272's rejection is carried by the owner-order citation in the fly-in briefs, not by this file, and the file states why.
- CI on this head: at read time the check-runs API listed arm (skipped) and prelude, refresh and cancel-superseded (queued, two runs). No gate check had concluded, none was red, and no pr-contract run had started. I cite no CI result for this head. The merge train gates on the required checks.
- Red checks: none exist, so root-cause answers are not owed.
