Fix review: merge 67e09398e9383dddea40c86efd563ad336b2088c

bus-nonce: 78c3bd288fb382eb7b12c82ac98f811b

Round 1, record PR (triage P323). Diff is two new files: dev/programme/triage/s6-batch86.md and dev/programme/delivery/3033.md. No production code, VERSION, manifest or notes touched.

## Findings
- The 3 ms and 26 ms figures name no enumerator. The text says "measured on this host" with "20 calls took 0.056 s / 0.52 s", but no command is committed. I could re-derive only the ratio: 20 python3 starts took 0.68 s here, about 34 ms each, so the 26 ms order holds. My 3 ms analogue was an in-shell case, which forks nothing. A real per-call cost needs the hook script's own start. The fixer should record the enumerator and a hook-start measurement in its body. Carry: R10-FLY-BASH-KILL-GUARD
- Neither the held op b86 append-group nor the group JSON is reachable from this seat. No roster branch I can read holds R10-FLY-BASH-KILL-GUARD, and the PR carries none. So "passes brief_lint" and "after: names only existing groups" are not verified here. The orchestrator must run brief_lint.mjs on the group JSON at op time. Carry: O1

## Evidence
- Each cited path exists at the PR base 851d1ce6b: .claude/hooks/pre-edit.sh, .claude/settings.json, tools/policy/policy_lint.mjs, tools/audit/seat/cloud_dispatch.py, tools/audit/seat/pr_args.sh, tests/entities.py, tests/structure_budgets.json.
- Code-owned: CODEOWNERS lines 110-111 list /.claude/hooks/ and /.claude/settings.json as @tvofi. The carry text (6) says so.
- Claim (2) is true: cmdHooks tests a PreToolUse matcher against EDIT_TOOLS only, so a Bash matcher reads MATCHER BLIND.
- Out-of-scope prose mentions: git grep for pkill|killall in tools/, .claude/hooks/ and .github/ returns only cloud_dispatch.py:209,1035 and pr_args.sh:199, all prose or checks of the prompt. The claim holds.
- merge-tree with origin/main exits 0. review_packet: carry_audit 0 findings, no refusals. The figure_lint "unverified" lines are git invocations, not figure failures.
- CI at render: gate pending (prelude, refresh and cancel-superseded queued), not awaited. A record PR draws no mutants, so mutation proof, null control and metric moves do not apply.
