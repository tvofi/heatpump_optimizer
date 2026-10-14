Fix review: merge 17fd924a6fe8e14d1871c6b9d255f153127ac39d

bus-nonce: 20f1647cc559d5265d81df9fd608276f

Round 3, carry from round 2's merge on 4b58d3d6ebeb64a7d1d780474eefeed671491840 (verdict-2207-r2). The resolution delta 4b58d3d6ebeb64a7d1d780474eefeed671491840..17fd924a6fe8e14d1871c6b9d255f153127ac39d is exactly one file, dev/programme/delivery/2207.md (+1 line; git diff --stat rc=0), which is the orchestrator's delivery row. No code, policy, budget or claim file moved, so every round-2 RESULT line carries:
RESULT round-1 items: D11 universe drops docs/decisions/** and adds dev/governance/** (50 files); check_scopes rc=0, D11 universe=2150, zero-match universe globs: none; --self-test rc=0
RESULT leads prompt now interpolates CURRENT; D14.md M1 -> dev/audit/config/bugclasses.json; D13.md M4 -> dev/audit/rounds/round4/D11/dora_keys.py (both tracked). Each one-word cut keeps the meaning ("its seams" -> "seams"; "have been added" -> "were added")
RESULT git grep of the old tools/audit/{rotation,scopes,finding.schema,bugclasses}.json and tools/audit/round paths in the drivers, roles, dimensions, README and config: only history comments, README archive commands and ref@sha record citations
RESULT checker rc=0 176/0; mutants as #2206 r2: 10 killed, EVERY_DIM_ROUNDS survivor triaged
RESULT survivor found by the reviewer, not in the body: the leads prompt reverted to "tools/audit/ copied in" gives rc=0 176/0. Reviewer's triage: this is prompt prose that now derives from the pinned CURRENT, so a revert means hand-writing a literal back. Accepted, and recorded here.
RESULT policy_lint rc=0; --budgets rc=0 (D13.md 79/79, D14.md 32/32, verifier.md 39/39, COMMON.md 108/108, CLAUDE.md 199/221); rules_sync rc=0; brief_lint rc=0; layout rc=0 GUARD 0; tmp_paths rc=0; structure rc=0; agreement rc=0; copy-self-test rc=0; entities.py (py3.13) rc=0 2303/2303
RESULT merge-tree origin/main 4b58d3d rc=0
Author 'Tvofi2' on merge commits c693cde13 and 4b58d3d6e: the email is 70032254+tvofi@users.noreply.github.com, which is what app_approve.sh keys on. The PR author is the App, so no gate reads the name. It is cosmetic and not blocking. Use --author next time (GIT_AUTHOR_NAME in the environment overrides -c user.name).
Owner approval still owed before merge: verifier.md, CLAUDE.md, dev/audit/README.md, D13.md, D14.md (policy), and the code-owned audit-find.js and audit-verify.js. #2206 merges first.
Evidence: evidence/delta-2207.txt (this delta) and the round-2 logs (ev2) under evidence/.
