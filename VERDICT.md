Fix review: blocked 6f3609a4a17c7367263dadaa07889bc8aafbb8fa class-open: tools/audit/seat/handover_prompt.py:78 still names tools/audit/briefs/ (moved to dev/governance/roles/)

Round 1. Seat r9c-rev-2012, detached worktree at 6f3609a4a17c7367263dadaa07889bc8aafbb8fa (merge base = origin/main be0cb821; merge-tree vs origin/main exit 0). Live head re-read before posting: 6f3609a4a17c7367263dadaa07889bc8aafbb8fa.

## The block

The dispatch asks that no stale path survive in the five files the PR re-points. One does, in a file the diff edits:
- tools/audit/seat/handover_prompt.py:78, rendered into every generated next-session prompt: "the seat brief your work names under `tools/audit/briefs/` (the fixer's is `fixer.md`)". `git ls-files 'tools/audit/briefs/*'` = 0; the contracts are under dev/governance/roles/ (fixer.md present). A seat following the generated prompt reads a directory that does not exist -- the same class (#1990 class D: an instrument kept a path a move emptied).
- The RCA's class search (R9-RCA-1990.md section 2) lists handover_prompt.py's push script and row path only, and its enumeration rule (`grep -no 'tools/...\.(sh|py|mjs)'`) cannot return a directory or a .md path, so this seam is neither in the diff nor dispositioned.
- Same pass, cheap: tools/audit/seat/handoff_push.sh:7 comment "this stays while docs/HANDOVER.md names it" -- now dev/programme/HANDOVER.md (comment only; fix or disposition).
Fix: re-point line 78 to dev/governance/roles/ (and the comment), and either widen the body's enumeration rule to non-script repo paths or state that it covers scripts only. Scan used: every tools|tests|docs|dev|.claude|custom_components path literal in the five files, test -e (evidence/allpaths.txt); the remaining misses are /dev/null-style, old-first fallbacks, or self-test stub data.

## RESULT lines (everything else checks out)

RESULT merge_train --self-test head: 49 checks, 0 failed (mt_head.txt)
RESULT merge_train arm A, TOOLS old paths only + ROW_DIR=docs/delivery: 3 failed (app_approve, preflight, docs/delivery/) (armA.txt)
RESULT merge_train arm B, bare "tools/audit/worktree_gc.sh" argv: 1 failed, names the path (armB.txt)
RESULT merge_train arm C, origin/main's own file on this tree: 43 checks, 0 failed -- the gap reproduced (armC.txt)
RESULT bus --self-test head: 45 checks, 0 failed; origin/main's bus.sh: 45/0 (blind); head with default reverted to tools/audit/app_comment.sh: 1 failed (poster pin); head with tools/pr/app_comment.sh absent: 1 failed
RESULT handover_prompt --self-test head: 12 checks, 0 failed
RESULT paths at head: tools/audit/app_approve.sh, tools/audit/preflight.sh, tools/audit/app_comment.sh, docs/delivery MISSING; tools/pr/{app_approve,preflight,app_comment}.sh and dev/programme/delivery present (paths_head.txt)
RESULT carry rule (the carry's own grep) over tools/audit/seat/*: 40 hits on missing script paths, every one an old-first test -f / TOOLS fallback with the new path present (carry_rule_scan.txt)
RESULT brief_lint carry-1921.json + carry-1922.json: 0 error(s), 0 warning(s) (tools/policy/brief_lint.mjs; .claude/workflows/brief_lint.mjs no longer exists)
RESULT count re-derived, policy_lint --stats --since v6.7.16 now: head-moved 11 / 20, 18 re-verified after a merge (9 PRs); window now 58 merges / 51 with verdict (was 57/50: one merge since) (stats.txt)
RESULT cost test: 3 class-D entries x 129 min mean (388/3) / 57 merges = 6.8 min per merge -- arithmetic re-derived from the RCA's table; the per-entry lags themselves I did not re-time.
RESULT check-runs at head: 21 success, 12 skipped, 1 neutral, 1 in_progress (CodeQL), budget-raise-gate cancelled; red: delivery-status (main's pending/unread backlog, not this diff) and nightly-status -- neither reachable by this diff.

bus-nonce: 15a5edd57db36810818dc3d87e4b35e5
