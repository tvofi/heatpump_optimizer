Fix review: merge 808137a949c2c1ce64acc340cfd72ccfebc7a6b8

bus-nonce: e36fe01aeff76af88d3516d1dc44fc52

## Round

Re-review of the moved head 808137a949c2c1ce64acc340cfd72ccfebc7a6b8 (merge of 8aec46775 and main 8a4c438e7 after #2578). Previous verdict: merge at caac2c8d. The roles dir is current (empty three-dot diff). Judged: the second absorb's resolution delta, plus every measurement re-taken at this head.

## Findings

- R10-ORCH-MACHINERY still has to receive this PR's ROSTER-APPEND text (the handoff job reads the hold file only through `cloud_relay.sh held <pr>`; rc 2 refuses the whole pass). The group is live on origin/main (stage not-started). The orchestrator lands it with roster_edit.py; #2600 (open, "Roster: carries from the #2580 and #2598 verdicts") is the vehicle. Carry: R10-ORCH-MACHINERY
- R10-FLOW-ROSTER-FREEZE still has to receive this PR's ROSTER-APPEND text (plain PR-number lines only, remove only your own line, read back through `cloud_relay.sh held`). The group is live on origin/main (stage not-started). Carry: R10-FLOW-ROSTER-FREEZE

## Evidence

- RESULT head: measured from a detached worktree at 808137a949c2c1ce64acc340cfd72ccfebc7a6b8; the PR API head.sha is the same. ev/HEAD.txt.
- RESULT scope: the PR's own diff against the merge base 8a4c438e7 (main at the absorb) is 4 files, +134/-4, same as the caac2c8d review (cloud_relay.sh, INSTRUMENTS.md, the mutants harness, delivery/2580.md). Nothing beyond the absorb resolution and the body came in.
- RESULT mutants-file resolution: parsed MUTANTS with ast. 42 ids at 8a4c438e7, 52 at 8aec46775, 53 at the head. Union minus head: none. Head minus union: none. Every tuple from both sides is byte-equal in the head. S38, body_patch-1, cloud_relay-1..11, tick_loop-1..2 and heartbeat-1..4 are all present. INSTRUMENTS.md is +9/-0 against origin/main (git diff --numstat). ev/harness-head.txt.
- RESULT finder's harness (no names, every mutant) at the head: 60 ': KILLED', M0: 0 seat step(s) red, RESULT survivors=0, rc 0, 0 NOT RUN. cloud_relay-2..11 fail 36/49/2/3/18/2/1/1/27/1 of 189. body_patch-1 fails 3 of 62. heartbeat-1..4 and tick_loop-2 each fail 1. cloud_relay-1 and tick_loop-1 are killed by a script error rather than a failed check, as in the previous round. This matches the body's 60.
- RESULT null control: each harness row runs the unmutated step first (no NOT RUN). `cloud_relay.sh --self-test` at the head prints 189 checks, 0 failed, with the in-head null controls passing. The body's baseline figure (42 KILLED, survivors=1) was taken at the older main 93e6a63d2 and is not re-derivable at today's base; I did not re-measure it.
- RESULT figures re-derived at the head: cloud_relay self-test 189 checks, 0 failed; selftest_wiring 77 self-testing, 77 wired, 0 unwired (the body says 77/77). ev/selftest-head.txt, ev/wiring-head.txt.
- RESULT reviewer's own mutants, planted alone in a second worktree (cloud_relay.sh, restored; git status empty): the HELD continue dropped gives 3 failed, held matching a substring (grep -qF) gives 1 failed, an inverted held result gives 7 failed. Unmutated is 189/0. All killed. ev/reviewer-mutants.txt.
- RESULT merge-tree: `git merge-tree --write-tree origin/main 808137a949c2c1ce64acc340cfd72ccfebc7a6b8` exits 0, clean, at origin/main 0b162da1. ev/merge-tree.txt.
- RESULT carry audit: `carry_audit.py check` over the PR body prints 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s), rc 0. Both destinations are live on main's roster. ev/carry-audit.txt.
- RESULT untouched: VERSION, manifest, RELEASE_NOTES and tests/golden three-dot stat is 0 lines. CODEOWNERS matches nothing for cloud_relay, tools/audit/seat or r10_seat (0).
- RESULT CI (check-runs API at this head, read at 09:2xZ): 27 success, 7 skipped, 2 failure, 1 neutral (CodeQL), 2 still in progress (closures, Analyze (python)). The two failures are nightly-status (log: "NIGHTLY ABSENT: no scheduled run of the workflow was found at all", main's schedule, not this diff's) and delivery-status (log: "DELIVERY STATUS OVERDUE", the overdue row is #2588, which this diff does not touch). Both are named in their logs as not required contexts and block no merge. Neither log shows an API-rate-limit message. closures had not concluded when I read it; I did not wait for it or re-run it.
- RESULT contract line: the body's `## Red checks` answers nightly-status. delivery-status is not this PR's (its diff adds one row, 2580.md, and removes none).
- RESULT forward-carry: the body gives fenced ROSTER-APPEND text for both groups. Destination content is still pending the roster append, and the body says so.
