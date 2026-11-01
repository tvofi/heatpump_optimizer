Fix review: merge 810d219eea086085f2b75b6462ce3e2d7f5fbd64

bus-nonce: 3507ab29b200eec3d450caf3ab260f9e

Round 1. Record PR, reviewed from a detached worktree at the head.

## Findings

- The delivery row and the PR title say "s9 batch 107" while the file's title and prose say session s10; the same row shape on #3141 reads "s9 batch 103". Carry: dismissed: a session label in a row, no test or later stage reads it
- The ledger-sourced facts (the 20:25Z to 20:37:15Z lines on #3047, train 54386, the 19:50Z and 20:34:40Z owner rulings) are in a seat ledger this seat cannot read, so they are taken as quoted. Carry: dismissed: the ruling's verdict and destination rest on the repository facts re-derived below, which settle ACCEPT with no ledger input

## Evidence

- Head: 810d219eea086085f2b75b6462ce3e2d7f5fbd64, still the PR head (refs/pull/3152/head). Three-dot diff names exactly dev/programme/delivery/3152.md (+1) and dev/programme/triage/s6-batch107.md (+60); no production code.
- Re-derived at 7f849a249 (an ancestor of origin/main): app_comment.sh check_pr lines 68-69 hold the "head moved" refusal; bus.sh line 512 holds the review_carry CARRY refusal dated tvofi 2026-10-27. Both match the file.
- #3077 head is aa6148d4ff35c457e83310337760e075cb823a14 (open); git diff --numstat 7f849a249...aa6148d4f -- tools/pr/app_comment.sh prints 56 8. Its diff holds the three self-test arms the file names: pin-only head posts with the carry as last line, own code commit refused "head moved", carried body reads back identical. A null control (unmoved head, no carry line) is also in it.
- Roster (origin/handoff/audit-r10-roster c6ca679a2, and a7856cd5c as cited): R10-FLY-CARRY-DOC-CONTEXT exists, carry list entry 3 is the P264 text quoting check_pr lines 68-69; so the destination is a live group and the "no new carry" claim holds. #3077's body numbers the same carry 4 in its own list; the roster's index is the one the file uses.
- origin/main s6-batch53.md has "## P264" with the four instances #2612, #2775, #2745, #2912 and the carry the file quotes.
- ruling_verdict on the committed file: P365 reads ACCEPT, P364 reads None; triage_refusal on a text citing s6-batch107.md#P365 returns None; with the verdict flipped it reads REJECT (null control).
- Standing checks: merge-tree --write-tree origin/main exits 0, no conflict; VERSION, claimed_drift.txt, card_claimed_drift.txt and RELEASE_NOTES.md byte-identical to origin/main; no host path in added lines; no Claude footer or trailer in the branch commits.
- Body: ## Head names 810d219ee; ## Red checks says none, and the head's check-run set (4 runs) holds no concluded failure: arm skipped, cancel-superseded, prelude and refresh queued.
- CI: merge_train.py classify printed WAIT (pending: gate red: none, rc 3) on every poll over about 12 minutes; the runs were still queued, so no conclusion exists at this head. Judged on the absence of any red and a diff that touches only two markdown files.
- Figures: the body's 56/8 is re-derived above; the file's other counts (four instances, seven days) match batch 53.
