Fix reviewer for PR #2651, roster batch 21, roster ops only, head 2bb638af88f6373fe208dd2e57676dfac723bec8. There is no group; review against the PR body and say so. Follow dev/governance/roles/fix-review.md exactly, from a detached worktree at the head. A red nightly-status grades main and is not this PR unless its diff reaches what that check reads. Your ev/ MUST contain a file holding the full 40-hex head sha (ev/HEAD.txt), or the relay refuses the verdict.

Verify:
(1) The three-dot diff of dev/programme/rosters/wave-r10-groups.json against origin/main changes exactly these, and nothing else:
  - R10-CI-LAYOUT-P2: the "refuses rather than mixing" carry is dropped and the corrected drop-edge carry added (f65126e9d);
  - R10-CURRENCY: the O19 carry (c539935a3); its fix-shape clause is marked as roster-seat wording;
  - R10-LEARNER-ETA (59c2ebc02), R10-UX-HEALTH (524d335a0) and R10-ARCH-DOCS (1f27f9daf): one #2647 carry each, matching #2647's live body Forward-carry text verbatim, less the trailing Carry marker;
  - R10-FLY-NO-FOOTERS: done at 7deeef1b6b, pr 2636;
  - R10-FLY-NO-FOOTERS-EMITTERS: added at 85ac3ec14, stage in-progress, resume.branch fix/r10-trailer-emitters, plus its one carry.
(2) 7deeef1b6b is an ancestor of origin/main.
(3) No group is removed and exactly one is added: the group count goes from 167 to 168.
(4) brief_lint TOTAL 0 and ref_privacy --check 0 refused.
(5) Read CI with one bulk check-runs read.

Model for this review: claude-sonnet-5-5.
bus-nonce: 4c449d579ce051cacc85535029ceb8b0
