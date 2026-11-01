Fix review: merge a22d6566ff960877891ba35586603e91e474cdd1

bus-nonce: 7dc92dee960e83249ccde5713cc3161e

Round 1. Record PR, judged at head a22d6566ff960877891ba35586603e91e474cdd1.

## Findings

none

## Evidence

- Three-dot diff is two markdown files, dev/programme/triage/s6-batch101.md and dev/programme/delivery/3095.md (the delivery row). No production code, claim file, VERSION, manifest or RELEASE_NOTES change.
- merge-tree against origin/main (e4c9e2016): rc 0, clean (ev/merge-tree.txt).
- Gate: merge_train.py classify at this head exits 0 GREEN, pending none, red none; the PR body's "## Red checks none" matches. The earlier packet digest showed instrument-self-tests and prelude in progress; both concluded green.
- Body names the head (## Head) and the authored head 3a7d7a712.
- Numbering: batch 100 (P355, P356) is on fix/triage-s9-batch100; P357 follows. Batch 101 file is not on main yet, as expected.
- Roster facts re-read: on origin/handoff/audit-r10-roster, R10-TRAIN-OVERLAP-GRADE carries-open (20 carries), R10-FLY-TRAIN-DEFAULTS done (6), R10-FLY-ABORT-OWN-MERGE done, R10-TRAIN-MERGE-LOOP not-started (4). On origin/main OVERLAP-GRADE is in-review. Matches the ruling's grounds.
- Carry (a) text is identical to batch 98's P353 carry except the added re-route clause and the citation (checked line by line); ask and controls (FAIL and full-log lines, kept push log, null control, old-grep mutant) are kept.
- Carry (b) is P354(a) "verbatim" by reference to the s7 carry file; its text is not in the diff, so I could not compare it byte for byte. Batch 99 holds the original.
- remerge_main.sh lines 19 and 39 on main still hold PL=$B.push.log with the EXIT trap and the grep -E 'RECARRY|REFUSE|PUSHED'; posted_verdict exists in merge_train.py. Both instances hold.
- figure_lint 3 resolved, 0 not verified. carry_audit: 0 finding items.
- Carries are not on the roster by design for a triage batch; not blocked on that.
