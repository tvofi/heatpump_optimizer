# Fixer round 2, R10-ORCH-LEDGER, topic r10-orch-ledger. Your handoff head is 6062f975e0b5a68e7adf3ef795d9ca5ec4f8ad21 (origin/handoff/r10-orch-ledger); origin/main is a6620c30a or later. No PR is open yet.

open_pr.sh refused the open at prepr's agreement lane: `AGREEMENT REFUSED: one concept, readers that disagree or a grammar written twice and unregistered`. `python3 -I tools/policy/agreement_py.py` plus `node tools/policy/agreement.mjs --py-json` at 6062f975 print `RESULT divergent=0 unregistered=3`:
  UNREGISTERED  "[0-9a-f]{40}" in .claude/workflows/policy_lint.mjs, tools/audit/seat/ledger.py
  UNREGISTERED  "\\bledger_open ([a-z-]+) " in tools/audit/harnesses/r10_ledger_class_reach.py, tools/audit/seat/ledger.py
  UNREGISTERED  "\\blevel_line ([a-z-]+) " in tools/audit/harnesses/r10_ledger_class_reach.py, tools/audit/seat/ledger.py

Do (dev/governance/roles/fixer.md, CLAUDE.md, in a worktree of your own from the handoff head):
1. Fix each one by the sound route, not by renaming a pattern to dodge discovery (that is a metric game).
   - The two `ledger_open` / `level_line` grammars: the harness should import the pattern, or a parse function, from ledger.py rather than writing it a second time. If the harness must stay independent of the code it measures (the finder's-harness rule), register the pair in the agreement lane's registry instead, as an agreement pair whose readers are checked to agree. Read tools/policy/agreement_py.py to see how existing pairs (e.g. budget-raise, attribution) are registered, and choose by judgement; say why in the body.
   - The 40-hex SHA grammar: share or register it the same way. Check whether a shared constant already exists for this grammar elsewhere in tools/ before adding one.
2. Re-run the agreement lane to `unregistered=0`, plus prepr with PREPR_SKIP_CLOSURES=1 (`bash tools/pr/prepr.sh` or the body_push path) to all ok. Re-run the ledger's own self-tests and the harness at both ends.
3. Push fast-forward to refs/heads/handoff/r10-orch-ledger. Update BODY.md from origin/handoff-body/r10-orch-ledger: add a short `## Head` note for this round and keep every other section verbatim unless a figure changed. Then run `bash tools/audit/seat/body_push.sh r10-orch-ledger <body.md>`.
Rules: PREPR_SKIP_CLOSURES=1; spare the GitHub API; no Claude footers, Co-Authored-By or session links anywhere.
