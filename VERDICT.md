Fix review: merge 000eae090f657edf008eaba961398705329c4197

bus-nonce: fb2d5b239ae07aa8fe95e19ec2a3c3d7

## Scope

Delta review, round after the `merge` at 46b2ba5a10195d91c80c93240f9c75b4cd1eed80. Measured head: 000eae090f657edf008eaba961398705329c4197, still the PR head at verdict time. Merge base with origin/main: 66974d47312caa46e9817b9aeae7186e9764e560 (origin/main itself). `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the role contract read is current.

## Findings

- `tests / nightly-status` concluded failure on this head (check run 123384622757) and the body's `## Red checks` says `none`, so `review_packet.py render` refuses `red-unanswered`. The red is main's scheduled `nightly-ha (stable)` run 40806276912 at ee48937; this diff touches no nightly workflow and no integration code. By fix-review.md step 11 a red `nightly-status` is not this pull request's, and the lane says it is not a required context on `main-protect`. Carry: dismissed: not this PR's red under fix-review.md step 11; the owed nightly-ha answer belongs to main's nightly lane, not this PR.

## Evidence

- PR hunks since the last verdict: for every path the PR touched at 46b2ba5a (review_packet.py, body_push.sh, prepr.sh, r10_seat_selftests_mutants.py, fix-review.md, fixer.md, delivery/2939.md), the three-dot +/- lines at the head are byte-identical to those at 46b2ba5a (sha1 compared per file). The "new code handoff" d2e92490 is a merge of origin/main into handoff/r10-orch-review-packet with no non-merge commit outside main. Its tip is an ancestor of the head, so `handoff-not-applied` does not apply to this PR.
- INSTRUMENTS.md resolution: at the head, INSTRUMENTS.md matches origin/main (main's index, with no PR diff). The branch's two INSTRUMENTS.md hunks from 46b2ba5a (the body_push.sh clause on `review_packet.py handoff` refusals (P256), and the review_packet.py refusal clause on `handoff-not-applied` / `handoff` / `brief-carries`) appear verbatim in instruments/body_push.sh.md and instruments/review_packet.py.md. Every other line of main's instruments/*.md is untouched (the three-dot diff touches only those two files), so both sides' clauses are present.
- Merge with main: `git merge-tree --write-tree origin/main 000eae090f657edf008eaba961398705329c4197` gives rc=0, tree 6a6c189f455e5eba434c0dcdbeee3066e9f18e81, with no conflict (ev/merge-tree.txt).
- Mutation, run by this review (my own targeted mutants against `review_packet.py --self-test`, ev/mutants.txt). The unmutated self-test reports 42 checks, 0 failed. M1, `handoff_not_applied` always passes: killed, 2 FAIL. M2, `brief-carries` refusals dropped: killed, 2 FAIL. M3, `fix/<t>-pr` spelling dropped: killed, 1 FAIL. CI's `tests / mutation` lane concluded success and is cited, not re-run.
- CI at the head, check-runs API, 55 runs, all concluded (ev/checks.txt). Every run is success, skipped or neutral except `tests / nightly-status`. That check is not a required check and does not block. `pr-contract / pr-contract` succeeded twice, the later run finishing 10:51Z, after the last red at 10:09Z.
- Review packet rendered here (ev/review-packet.md, ev/review-packet.out): rc 1 on the single signal `red-unanswered` for `tests / nightly-status`, handled in Findings. Its only advisory is `hot-file` with HPO_BUS_TRAIN_STATE unset, which is not a refusal.
- The body's `## Head` names 000eae090f657edf008eaba961398705329c4197, the measured head. VERSION, the manifest and the notes heading are not in the diff. Claim files are not in the diff.
- I did not re-derive the figures quoted in the body this round. Its code hunks are unchanged since the verdict at 46b2ba5a, which re-derived them.
