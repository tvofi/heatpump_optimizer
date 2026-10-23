# R10-ORCH-MACHINERY design note (designer seat, round 10): a stop at step 2

This is the group's architect note. It lives on `design/R10-ORCH-MACHINERY` only and is never merged. Size L, lane IN, issue #2505. The inputs were the roster entry and all 45 carries at `origin/handoff/audit-r10-roster` `5ba47bffcc4eb4682efe5fe430284b99672d1537`, the approved design at `handoff/orch-machinery` `09174d94e24faa0a02cda531164ec55ac2c49577` (`dev/audit/design/orch-machinery/DESIGN.md`), the five `after` groups' briefs, and `dev/governance/dimensions/D7.md`.

**Result: a design finding, and the seat stops here** (`dev/governance/roles/designer.md` step 2). As rostered, the group is not one change with one owner. It bundles three new instruments, each owning its own concern, a roster-schema change owned by a fourth module, and at least ten independent single-module defects. No shape is written below, by design: the step says to report and stop, not to split the concern myself. The re-cut in §4 is evidence for the orchestrator's decision. It is not a design.

## 1. Read at

- Code: `origin/main` `fef4a1351db3e8e328d714e84299284c6876eecb`. No predecessor has a live handoff head. All five `after` groups are `done`, and each `resume.commit` is an ancestor of main (`git merge-base --is-ancestor`): R10-ROSTER-OPS `929275e8a`, R10-CI-LAYOUT `5a755f53e`, R10-TICK-OWED-LEVEL `295c874e8`, R10-FLOW-MAIN-GATE `49018a8be`, R10-CI-LAYOUT-P1 `fae523a14`.
- Build gate (`resume.note`): satisfied. `tools/audit/seat/state_docs.py` imports `roster_sync` and runs it under `beat --apply`.

## 2. Applicability: this seat was not owed

Carry 20 (an owner ruling, 2026-10-21) reads: "Design step ... not needed; this group already has an approved design, pre-study or prototype, which serves as its design note." `designer.md`'s *Applies to* line agrees: the contract covers only L and XL groups "with no approved design, pre-study or prototype on record". `resume.next_step` already names the fixer dispatch at the approved design and its round-3 review (`review/orch-machinery-design` `0bd5d12f0`). The orchestrator should decide whether this dispatch was intended. That decision does not change the finding in §3. Whoever builds hits the same seams.

## 3. The finding: one group, several owners

`dev/governance/roles/fixer.md` step 17 puts one owner on each concern. The approved design names three modules, one for each instrument: the obligations ledger (design §6.3), the supervised beat `beatd` (§6.2), and `tools/audit/seat/plan_page.py` (only the last exists on main). It orders them as separate landings (its §8, Phases 1 and 3). The carries since then add owners the design never covered. The paths below are cited by each carry's own text. To list them, run `jq -r '.groups[]|select(.group=="R10-ORCH-MACHINERY")|.carry[]' wave-r10-groups.json | grep -oE '[A-Za-z0-9_./-]+\.(py|sh|json|mjs)' | sort -u`.

| concern | owning module (main) | carries |
|---|---|---|
| A. obligations ledger (OWED level, dispositions, event kinds) | the new ledger module (design §6.3); today the level is `tools/audit/seat/cloud_relay.sh`'s `<log>.level` | brief (1), 12, 13(2)(4b), 22, 35, 36, plus the RCA ledger extension in the brief |
| B. supervised beat and job table | the new `beatd` (design §6.2); `tools/audit/seat/daemonize.py` and `tools/audit/seat/tick_loop.sh` today | brief (2), 13(0)(1)(3), 14, 18, 30, 41, 42, 43 |
| C. plan page | `tools/audit/seat/plan_page.py`, driven by `tools/audit/seat/state_docs.py` | brief (3), 13(6), 15, 39, 40 |
| D. roster schema: `owner_gate` structure, absorbed-edge closure, brief pin, stage set | `tools/audit/seat/roster_lib.py` (`DONE_STAGES`), `tools/audit/seat/roster_sync.py`, `tools/audit/seat/roster_edit.py` | 23, 24, 25, 32, 37 |
| E. dispatch and worker registry | `tools/audit/seat/bus.sh` (`dispatch`) | 13(4), 17, 44 |
| F. the PR contract reads the roster | `tools/audit/carry_audit.py`, `pr-contract` | 1, 38 |
| G. independent defects, one module each | `tools/audit/worktree_gc.sh` (0); `tools/audit/seat/daemonize.py` (8); `tools/audit/seat/update_pr.sh` (9); `tools/pr/ci_predict.py` (11); `tools/audit/seat/cloud-setup.sh` (16, 26); `tools/audit/seat/orchestrator_tick.py` `bus()` (27); the env-matrix CI arm (34); the yield-probe guardrail (10, 33) | 0, 8, 9, 10, 11, 16, 26, 27, 33, 34 |
| no build | records, decisions and residuals | 2, 3, 4, 5, 6, 7, 19, 20, 21, 28, 29, 31 |

A, B and C are separate concerns, and the brief itself orders them as three landings. D changes `DONE_STAGES`, and `tools/audit/seat/pr_cap.py`, `tools/audit/seat/prune_refs.py`, `tools/audit/seat/handover_prompt.py` and the tick all read it (carry 24). It is also policy: rows vii and viii of the design's §8 table need the owner's approval before merge. Design §6.4 gave these predicates to R10-ROSTER-OPS, a group now `done`, so their owner moved without a seam decision. F is a policy tool's behaviour. Each item in G is a single-file fix with its own control, and none of them needs A, B or C.

**The premises moved too.** The design was read at `a2b25bbc5`, 1503 commits before `fef4a1351`. Since then, `cloud_relay.sh`, `orchestrator_tick.py`, `tick_loop.sh`, `state_docs.py`, `roster_lib.py`, `roster_sync.py` and `plan_page.py` gained 2,791 lines and lost 130 (`git diff --stat a2b25bbc5 origin/main -- <those>`). The design's S1 cause ("the tick never opens `cloud-disposed`", a 3.9 MB board) is now partly answered by R10-TICK-OWED-LEVEL: the relay rewrites a level file each pass and reads `cloud-disposed` (`cloud_relay.sh`, `level_set`). Item (3)'s shared-model premise is withdrawn by carries 15 and 39. A build against §6.3's and §6.7's measurements would rediscover facts that have since changed.

## 4. Re-cut for the orchestrator to decide (evidence, not a design)

The cut that gives one owner per group is A, B, C, D and E as separate groups, in the order A → E → B → C, with D independent. B's handoff job writes A's dispositions. E's dispatch writes A's `reviewer-fire` close (carry 17). C reads A's fold. Concern F goes to the policy group that owns `pr-contract`, and the owner approves it (`owner_gate`). Each item in G becomes its own XS or S group, or moves to the group that already owns its file. A and B are each at least size L (design §6.8: about 300 and 400 lines), so each needs its own design under decision 0014, unless the owner rules again, as in carry 20, that the approved design covers it. In that case §3's moved premises must first be re-measured into a revision of the design.

Alternative considered: keep one group and land A, B and C as three pull requests under one owner seat. It lost because D and F change other modules' contracts (`DONE_STAGES` readers, `pr-contract`). One fixer would then hold write authority over five owners' files at once, which is the monolith the design's own §7 item 3 rejects, and the 45 carries could not be matched one-to-one to the pull requests that answer them.

## 5. Notes for the fixer

There is no fixer until the re-cut is decided. This note re-routes no carry. Routing is the orchestrator's roster write (`tools/audit/seat/roster_edit.py`), done after the decision. Two preconditions hold for whoever picks up A or C. First, `python3 -I tools/audit/seat/plan_page.py --self-test` printed `41 checks, 0 failed` at `fef4a1351` (carries 15 and 39). Second, `dev/audit/harnesses/r10_relay_owed_class_reach.py` is the before-and-after control the ledger must keep (carry 35).
