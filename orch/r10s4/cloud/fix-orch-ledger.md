# Fixer brief: R10-ORCH-LEDGER

You are a cloud fixer seat for group R10-ORCH-LEDGER in tvofi/heatpump_optimizer, round 10.

Follow, in this order of authority: CLAUDE.md from main, dev/governance/roles/fixer.md, every carry on the group, and the group's brief in the roster. Read the roster from origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json (group R10-ORCH-LEDGER: brief, files, carry, resume). Re-derive every figure at your merge base.

Requirements (fixer.md):
- Failing test first. Mutation proof. The finder's harness run at both ends. A null control for every quantified claim.
- Set PREPR_SKIP_CLOSURES=1; CI owns closures.
- Spare the GitHub API: bulk-list once, prefer git over the API, stop on a 403.
- No Claude footers: no Generated-with, Co-Authored-By, Claude-Session or session URLs in commits or bodies.
- Push each verified step fast-forward to refs/heads/handoff/r10-orch-ledger before any long run. Never force-push.
- The return is the PR body, delivered via tools/audit/seat/body_push.sh.
- tools/audit/seat/cloud_relay.sh is shared with R10-UPDATE-PR-SIGNALS (in progress); keep your cloud_relay.sh hunks minimal and rebase onto main before pushing.
- The roster resume.branch is null for this group; the handoff topic is r10-orch-ledger.
