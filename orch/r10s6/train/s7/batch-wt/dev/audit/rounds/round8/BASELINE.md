# Round 8 baseline

- baseline SHA: `cdf82daabcfe3777d98b31489f36df5555ec9d82` (origin/main at dispatch, 2026-09-23; the merge of #1489)
- export (no .git): /home/claude/audit-r8/export — never work in it directly; every seat works in its own tree under /home/claude/audit-r8/seats/<label>, made by /home/claude/audit-r8/mktree.sh
- git trees (D0, D3, D9, D11, D13 and their verifiers/judges): detached worktrees of /home/claude/heatpump_optimizer at the baseline; earlier rounds stripped as tracked deletions
- two round-4 files restored in every tree because tests/entities.py opens them unguarded: tools/audit/round4/D11/governance_cost.py (+ its import d11lib.py), tools/audit/round4/D6/claims.json
- python: /usr/bin/python3 (3.11.15) — numpy 2.4.6, scipy 1.17.1, voluptuous 0.16.0, threadpoolctl 3.6.0, aiohttp 3.14.3, PyYAML 6.0.1 (tests/requirements-ci.txt pins), jsonschema 4.26
- node: v22.22.2; Playwright module: NODE_PATH=/home/claude/audit-r8/pw/node_modules (playwright 1.56.1); Chromium: PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers (chromium-1194)
- drift cache: ~/.cache/heatpump_optimizer/drift-baseline/ (warmed for the baseline with --all)
- machine: cloud Linux container, 4 vCPU, 15 GB RAM, no swap, x86_64. NOT the audit box the README describes; every timing number is provisional and is re-taken by the judge.
- no `gh` binary: D11/D13 read GitHub through the GitHub MCP tools (load with ToolSearch "mcp__github__"), read-only.
- thread pin: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
- gate lock: python3 tests/gate_lock.py take/renew/release --label <label> — required for stress.py and any MODE: FULL run
- KNOWN PREPARATION ARTEFACTS, not findings: tests/entities.py reports 1 failing check on the unstripped baseline checkout (the PR-template acceptance arm: "the real template -> rc=1 (must be 0)"; that one is fair game). Stripping earlier rounds makes 8 further checks fail (instruments that read tools/audit/round*/), and the no-.git export fails 11 more (handover `updated-for:` reachability, git-driven lint arms). Do not report those 19 as findings; name them as harness gaps if you meet them.
