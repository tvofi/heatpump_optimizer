# BLOCKED: r10-dispatch-at-handoff-p2

Head: code on handoff-wip (2 commits over afc1586a4): review_packet.py head-note asks
policy_lint --pr-body --head (Carry 16); packet refuses figure-lint and moved-head (Carry 3).
review_packet.py --self-test: 78 checks, 0 failed; a substring-restoring mutant fails 2 P405 arms.

Block: tools/pr/prepr.sh REFUSEs at `closures`: "failed while being recorded: tests/entities.py (exit 1)".
Run alone in this container, tests/entities.py exits 1 with 3 of 2665 checks failed, none on a file this diff touches:
  - the coverage job reuses only an entry main's push run saved
  - the release ZIP holds the integration folder at its root ("the build step fails")
  - the Pages workflow deploys on a release tag ("probe ... rc=1 enabled=[]")
bus.sh --self-test also has 1 failure ("an ordinary append with no intervening fetch ...") that reproduces at origin/main.
Question: is this container's entities.py red expected (needs network/gh/zip tooling)? A clean prepr run is the handoff condition.

Not built (owner/orchestrator ruling or scope): Carries 0 (re-key, held-verdict relay), 4, 6 vs 17 (a pending required
context holds per 6 but WAIT dispatches per 17's card 7; the two conflict and wait on a ruling), 8, 11, 12.
Delivered at main, no re-fix: Carries 2, 5, 7, 9, 10, 13, 14, 15 (evidence in the survey of afc1586a4).
