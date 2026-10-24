Continue from origin/handoff/r10-codeql-dependabot 5832d8c6 (body b207c883); do not restart from main. Merge origin/main into your worktree first. The opener's prepr refused two checks; repair both:
(1) field coverage: `pinned tools/policy/dependabot_contract.mjs` is unregistered. Register dependabot_contract.mjs in the field_coverage registry: DECLARED must name the arm for its input, or none with a reason.
(2) agreement lane: a grammar is written twice and unregistered. Write the grammar once and register it in the agreement lane rather than duplicating it.
Re-run tools/pr/prepr.sh to a pass at your head. #2678 (dependabot) waits on this PR, so keep it small. Push refs/heads/handoff/r10-codeql-dependabot and run body_push.sh for refs/heads/handoff-body/r10-codeql-dependabot.
