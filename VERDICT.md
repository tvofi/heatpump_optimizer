Fix review: merge 819bfadab2c05648074972cdba8031b1b970ac72

bus-nonce: 62ce760755d0b54fc41dc1dac785a7fc

Round 1 (first review of this head). Roster-data PR: batch s8, merge of main into handoff/audit-r10-roster.

## Evidence
- Head measured: 819bfadab2c05648074972cdba8031b1b970ac72 (PR head at read time, ev/HEAD.txt). origin/main is 039eee1dc, the PR's base, so the three-dot and two-dot diffs agree: two files, dev/programme/rosters/wave-r10-groups.json and dev/programme/delivery/2988.md (ev/diffstat.txt).
- Mergeability: git merge-tree --write-tree origin/main HEAD exit 0, no conflict (ev/merge-tree.txt).
- RESULT brief_lint.mjs on the roster: TOTAL: 0 error(s) across 1 file(s), at this head (ev/figures.txt). RESULT tests/structure.py: STRUCTURE RATCHET PASSED.
- Re-derived the body's counts: 236 groups at head, 215 on main, 236 on the branch c7026896d; no main group missing from the head.
- Union claims re-derived field by field against both parents: R10-BUFFER-STORE keeps main's fixes [2500] and the branch's resume; R10-FLY-SUITE-ENV-FLAKES keeps main's brief and a carry list containing every entry from both sides (0 missing from either); R10-NIGHTLY-HB-RESPAWN carry list likewise holds every entry from both sides. The branch's stage/commit fields are identical on both parents, so nothing was dropped. No other group differs from both parents.
- VERSION, manifest version and RELEASE_NOTES heading untouched (diff touches only the two files above). No claim file touched, so env_drift has nothing to compare. No production or instrument code changed, so the mutation proof and null control are n/a as the body states; no figure moved on any ratchet.
- Role-file drift against main (dev/governance/roles/): empty.
- Commit message of the head carries no Claude trailer or session link.
- Body forward-carry is "none"; the diff holds no finding that changes a later stage.
- CI at this head, read from the commit check-runs API: no run red. At read time 5 checks were still in progress (tests / closures, tests / fast (3.14), governance / env-matrix, governance / instrument-self-tests, prelude) and no pr-contract run had started, so the red-check clause (role step 11) could not be applied to a concluded set. Everything concluded so far is success or skipped. The merge train must read the final CI summary before it merges; this verdict is not a CI result.
- review_packet.py render refused with host-path and wrote no packet: its home-directory test matches HOME=/root as a substring of "root-cause.md" in two added roster lines (6806, 10370), both prose in existing groups' briefs. This is the cloud-seat false positive the roster already records (the ref_privacy.py groups quoted in those lines); the lines are not host paths. The live checks above were re-read in place of the packet.

## Findings
- The review packet cannot be rendered on a cloud seat for any head whose added lines mention root-cause.md (review_packet.py host-path refusal on HOME=/root). The PR does not touch it and the roster already carries it. Carry: dismissed: already recorded in the roster's own R10 ref_privacy groups quoted at the refused lines; not this PR's
