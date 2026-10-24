# Fixer round 2, R10-INPUT-STALENESS, topic r10-input-staleness. Your handoff head is 7668a4d0974444c9806fe83ae0656b0b6bd1e50a (origin/handoff/r10-input-staleness); origin/main is a6620c30a or later. No PR is open yet. The PR closes #2234.

open_pr.sh refused the open at prepr's pr-body step: `check mutation is red and ## Red checks does not name it`. ci_predict.py predicts mutation red, with 10 ADDED UNPINNED sites:
- coordinator.py:8911, three sites (BOOLOP, CMP_BOUND*2, RETURN_DEL on `return value if value is not None and 0.0 < value <= 100.0 ...`);
- inputs.py:259 GUARD_OFF, 285 CMP_BOUND, 287 GUARD_OFF, 290 GUARD_OFF, 292 RETURN_DEL, 306 RETURN_DEL and 874 GUARD_OFF.
Run `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at the head to see them.

Do (dev/governance/roles/fixer.md, CLAUDE.md, in a worktree of your own from the handoff head):
1. Pin every new site with the check that kills it: `python3 tests/mutation_table.py --pin-killed` (read its --help first). For each site that SURVIVES, add a value check in tests/features.py (or entities.py) that kills it. It must go red on the mutant and green on the head; a coverage-only check pins nothing. The goal is no new unpinned site, not prose dispositions.
2. Re-run ci_predict.py until it prints no mutation red, then prepr with PREPR_SKIP_CLOSURES=1 until all ok. Run features.py and entities.py with PYTHONPATH=tests/hastub.
3. Push fast-forward to refs/heads/handoff/r10-input-staleness. Update BODY.md from origin/handoff-body/r10-input-staleness: add a `## Head` note for this round, update ## Mutation proof and ## Figures for the new pins and checks, and keep everything else verbatim. Then run `bash tools/audit/seat/body_push.sh r10-input-staleness <body.md>`.
Rules: PREPR_SKIP_CLOSURES=1; spare the GitHub API; no Claude footers, Co-Authored-By or session links anywhere.
