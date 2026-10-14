Fix review: merge c674dc3b8630df977d7c1333093f082a40365bf9

bus-nonce: 0af5a810b06ae6ccab1aae467ffff1da

Round 3, carry from round 2's merge on ba0ce1719e2e0f462a95492e7927d6148b18da96 (verdict-2206-r2). The resolution delta ba0ce1719e2e0f462a95492e7927d6148b18da96..c674dc3b8630df977d7c1333093f082a40365bf9 is exactly one file, dev/programme/delivery/2206.md (+1 line; git diff --stat rc=0), which is the orchestrator's delivery row. No code, policy, budget or claim file moved, so every round-2 RESULT line carries:
RESULT checker@ba0ce17 on main's drivers rc=0 175/0; both new pins "not declared" (round-9 drivers not held)
RESULT checker on drivers head 4b58d3d rc=0 176/0; with base prepare_baseline.sh (as CI restores tools/audit/*.sh) rc=0 176/0, CURRENT pin "not both declared"
RESULT mutants @4b58d3d: find ROUND_DIR->tools/audit rc=1; find ROUND_DIR->dev/audit/round rc=1; verify ROUND_DIR old rc=1 (2 fail); find CURRENT->['tools/audit/'] rc=1; find CURRENT drops dev/audit/config rc=1; prepare_baseline CURRENT_PATHS drops dev/audit/config rc=1; panel killed rc=1; decl removed rc=1; one lens rc=1; no retry rc=1; EVERY_DIM_ROUNDS w/o 10 rc=0 (triaged round 1)
RESULT merge-tree origin/main ba0ce17 rc=0; agreement rc=0
Pin (b) vacuous on #2207's own CI: accepted. governance.yml restores tools/audit/*.sh from PINNED, so the pair cannot be graded on the PR that introduces it. On main's push run PINNED=github.sha holds both, so a mismatch reddens main within one merge (CLAUDE.md rule 1's property). I ran it armed locally on 4b58d3d: it holds, and it fires on both sides.
Evidence: evidence/delta-2206.txt (this delta) and the round-2 logs (ev2) under evidence/.
