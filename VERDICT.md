Fix review: merge 780adaf04bef23261616489810258ce6416a17c8

bus-nonce: e74f3507528c09b418474871ae135132

## Summary
Round 1. Docs-only PR: one triage ruling (P266, V180, ACCEPT narrowed) plus its own delivery row. Head 780adaf04bef23261616489810258ce6416a17c8; authored code head 385c6cde5 differs only by dev/programme/delivery/2929.md (verified three-dot).

## Findings
none

## Evidence
- RESULT mutation: ruling_verdict(P266) = ACCEPT at head; mutant (Verdict -> DEFER in a copy) = DEFER and triage_refusal returns "...#P266 is not an ACCEPT ruling (DEFER)". Null (file absent) returns "the triage ruling ... is not on the roster branch or origin/main". Matches body.
- RESULT figures: cancel_superseded.py is 219 lines, candidates at line 48, ci.yml:154 is the "Cancel this branch's runs at superseded heads" step, CODEOWNERS:75 names it @tvofi, open_pr.sh pushes at lines 70 and 84. R10-CI-CONCURRENCY has 0 hits under dev/audit/rounds/round10 at roster be898eaef. The two Actions run listings (live API timestamps) I did not re-query; figure_lint resolved 2 of 2 figures.
- RESULT merge: git merge-tree --write-tree origin/main head exits 0 (tree e750d4fb7), no conflict.
- RESULT version: VERSION, manifest and RELEASE_NOTES untouched; no claim files, closures or budgets in the diff, so there are no moved numbers to earn.
- RESULT carry: carry_audit reports 1 item, 1 routed; the roster fly-in carry is "dismissed: registered by the held append-group op after merge", which fits as the group cannot be registered until this file is on main.
- No code change, so no class enumeration or finder's harness applies; the body names none.
- CI at read time: 6 of 7 check runs queued (prelude, refresh, cancel-superseded, two workflows), arm skipped; none red, none concluded. This is not a required-check judgement: the heavy gate was not cited. The queue is the runner-limit the ruling describes. Merge train should wait for green.
- Head re-read: still 780adaf04bef23261616489810258ce6416a17c8 at posting.
