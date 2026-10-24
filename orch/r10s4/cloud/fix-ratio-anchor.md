# Fixer brief: R10-RATIO-ANCHOR

You are a cloud fixer seat for group R10-RATIO-ANCHOR in tvofi/heatpump_optimizer, round 10.

Follow, in this order of authority: CLAUDE.md from main, dev/governance/roles/fixer.md, every carry on the group, and the group's brief in the roster. Read the roster from origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json (group R10-RATIO-ANCHOR: brief, files, carry, resume). Re-derive every figure at your merge base.

Requirements (fixer.md):
- Failing test first. Mutation proof. The finder's harness run at both ends. A null control for every quantified claim.
- Set PREPR_SKIP_CLOSURES=1; CI owns closures.
- Spare the GitHub API: bulk-list once, prefer git over the API, stop on a 403.
- No Claude footers: no Generated-with, Co-Authored-By, Claude-Session or session URLs in commits or bodies.
- Push each verified step fast-forward to refs/heads/handoff/r10-ratio-anchor before any long run. Never force-push.
- The return is the PR body, delivered via tools/audit/seat/body_push.sh.
- coordinator.py: PRs #2620 (CURRENCY) and #2632 (LOOP-CPU) are open and also edit coordinator.py. Keep your diff in coordinator.py minimal to ease their merges; touch only your owning seam.
