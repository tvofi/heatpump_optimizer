Fix review: merge 79bed84a1aae96391d9d492922cf8c6e70d27446

bus-nonce: a70a35927af590d7275e382e246f2738

Round 1, a RECORD PR (two files: dev/programme/triage/s6-batch92.md, dev/programme/delivery/3046.md; no production code, so no mutation proof, harness, or claim-file movement applies). Head measured: 79bed84a1aae96391d9d492922cf8c6e70d27446; base 7539d1675.

## Findings

- Wording nit in the P331 table and prose: "merged later at the same head, `811112b78`" / "`ecca12ceb`" name the MERGE commits of #3031 and #3039 (origin/main: "Merge pull request #3031 ...", "#3039 ..."), not their heads. The heads were 7ef58ef6e (#3031, matches run 41211188623's head_sha) and 49c160536 (#3039, matches run 41196240353). The claim (merged at an unchanged head) holds; only the SHA label is wrong. Carry: dismissed: wording only; the ruling's carry text (the code change) does not depend on it.
- The delivery row names no head SHA. Ground (f) asked that it name this head; the row format carries none (siblings 3043 and 3041 read the same: PR link, state, title, group), so this is the row format, not a defect of this PR. Carry: dismissed: row format has no head field.

## Evidence

- Setup: cloud-setup --check OK. fix-review.md vs main: no role-file change. Merge: `git merge-tree --write-tree origin/main 79bed84a1aae96391d9d492922cf8c6e70d27446` exit 0, tree 57e2bc0f (no conflict, no claim-file driver lines). Three-dot diff is exactly the two files; delivery row present.
- CI: merge_train.py classify at this head, GREEN (pending none, red none) after several WAITs. Review packet: no refusals, no advisories, carry_audit 0 findings, figure_lint 2 resolved / 0 not verified.
- (a) At base 7539d1675: REVIEW_POLL_SECONDS = 5 (merge_train.py:601); polls: int = 24 (:1026); review_settle at :2095 (docstring "up to polls times"); policy_refusal :2058 with the "missing requirement is a review" return at :2091, wait False, approval = rd != CHANGES_REQUESTED. Same line numbers on origin/main. The reframe (the wait already exists, P86) holds; the two defects are the bound and the classifier.
- (b) Run 41211188623: 2026-10-31T14:40:04Z to 14:46:10Z, success (366 s). Run 41196240353: 11:17:29Z to 11:18:48Z, success (79 s). Both match the ruling. Distribution re-read 2026-10-31T16:4xZ (latest 60 runs, 59 completed): p50 88 s, p90 1885 s, p95 2388 s, max 3391 s by my index rule; the ruling's p50 91 / p90 2388 / p95 5549 / max 10626 was read at about 14:5xZ and the window has since moved, so the tail figures are not re-derivable now; the shape (median in seconds, long tail past the 120 s the bound covers) holds. The train log (13 "(24/24)" lines, SKIP lines for #3031/#3039/#3013/#3000) is out of tree; I could not re-derive those and say so.
- (c) policy_refusal returns wait False for BLOCKED/APPROVED with every required context green, so a gate check-run poll would see nothing to wait on: the rejected form is grounded.
- (d) roster_edit.ruling_verdict reads P331 ACCEPT and P332 ACCEPT; replacing the verdict lines with REJECT reads REJECT for both, and triage_refusal then refuses a carry citing either.
- (e) cloud_relay.sh confirm_arm is lines 304-339 and reads no PR state; app_comment.sh:67 dies "a verdict posts only on an open one"; handoff_arm lists open PRs at :399 into cloud-prs. Review refs: 344 refs/heads/review/* now; 56 tips with committer time 14:10-14:56Z; 53 of them on PRs not open (open now: 3046 3045 3042 3016 3006; the ruling read 3 open, the set moved). bus.sh push_verdict (:214) proposes on review/<pr>, but no log in the tree names the 14:10-14:56Z writer, so the DEFER of part (1) is grounded. The P332 carry text agrees with the ruling (reuse the pass's open list, skip non-open, unknown stays owed, two null rows, one mutant).
- Carries are not on the roster by design; not checked there.
