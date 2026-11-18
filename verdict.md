Fix review: merge 6a229a2817f0974cc6603eea47a951ef724884d6

bus-nonce: 745c5f9d4f4e8aad2b9b9efa7592cd41

Round 1, cloud reviewer seat. Reviewed from a detached worktree at 6a229a2817f0974cc6603eea47a951ef724884d6; merge base ae0ed64af898d8923ac35afe6e9c031ac1e6b111 (three-dot). The harnesses are the finders', exported from plan/r11 819aa2e354b4e5baaf824b8568fd72bea8168a75 (dev/audit/rounds/round11). The fixer's companion was not used. An earlier verdict/3727 was read but not relied on; every figure below was re-derived.

## Finder harnesses, base -> head

- D6/s5/claims.py --only c_mock, c_fix_review_j5, c_round4_d6, c_brief_exclude, c_unleased, c_instrument_dirs, c_worktree_apply, c_handover_docs: at the base each reads false/stale (1), reproducing its finding (mock_users=5, 19 of 19 dirs absent, --apply refused rc=2, ...). At the head each anchor matches 0 units, so the wrong sentence is gone (ev/d6s5_only_base_control.txt, ev/d6s5_only_head.txt). The harness reads absence, not truth, so each new sentence was checked by hand against the tree (below). All are true.
- c_event_hub: stale at both ends. The harness hard-codes the basename event_hub_writes.py (claims.py:382), so it cannot see the fix. The cited dev/audit/harnesses/r10_livestate_event_hub_writes.py exists.
- D6/s7/plan_claims.py: wrong_rows 35 -> 26 in this clone. The drop of 9 equals the finding's count. The 26 left at both ends are reference-pass rows (SHA and path lookups) that fail because this clone is shallow (ref_sha_ok=0 of 717), not sentences this PR touched (ev/ledger_plan_head.tsv, ev/d6s7_d11s2_runs.txt).
- D11/s2/policy_health.py --list: dup_units 16 -> 10, rulings_overlap 1 -> 0. The 10 left are the pairs the body dispositions (1 deliberate, 8 decision history, 1 provenance sentence).
- node tools/policy/policy_lint.mjs: the same 6 ERROR lines at base and head (diff empty, ev/lint_errors_*.txt), so no regression. The body reports 0; this clone's 6 are pre-existing in it. rules_sync --check: OK.

## Sentence checks at the head (each against code, not prose)

- steward SKILL.md -> claim-files.md:29 carries git merge-tree --write-tree origin/main HEAD.
- root-cause.md -> defect-root-cause.md:70 carries the inequality and its units.
- standing-roster.md -> standing-tick.md:6 carries the "run things inline" constraint.
- D4/D5-criteria -> D4.md:4 and D5.md:4 quote the owner's words verbatim.
- brief-citations.md: brief_lint.mjs:215 SYMBOL_GREP_EXCLUDE = [':!.claude'] only. True.
- gate-scoping.md: dev/audit/rounds/round4/D6/claims.{json,md} exist. True.
- writing-for-agents.md: closure HANDOVER_DIRS covers dev/programme/ and docs/; the one handover is dev/programme/HANDOVER.md. "Exactly one handover" is true.
- HANDOVER.md: worktree_gc.sh:4 usage <owner/repo> [--dry-run]. True.
- tests/README.md and plan gate lock: run.sh:330-348 asks gate_lock.py needs-lease per script. True.
- INSTRUMENTS.md: dev/audit/rounds, rca, config/{bugclasses,scopes,rotation}.json, config/finding.schema.json and harnesses all exist; dev/audit/README.md:306 indexes j5_gil.py. True.
- ABOUT.md and dev/audit/README.md: true (5 suite scripts use unittest.mock; no contract sends a reviewer to j5_gil).
- plan-2026-09: web-fix-wave.js:435 only logs and the merge chain (424-433) has no latch; verdict_sha in bus.sh:187-191; cross_seam_fraction retired (structure.py:418-422, not in budgets); rules_sync.mjs:30-31 writes both .claude/rules and .cursor/rules; README.md:14 badge target is absolute; entities.py:1140 reads docs/architecture.md counts. All true.
- D15.md step 2: debug_ingest.py:95-107 stage 2 is export.violations over the replay half, and stage 2b is the planted-credential null control. True. See the policy list.
- RULINGS.md: the two dropped entries are stated verbatim in D11.md:95-98 (dated 2026-10-24) and D6.md:11-12. The file's own rule (1) drops an entry that policy already states.

## Edits that change what a seat must do (policy: owner's approving review)

1. dev/governance/dimensions/D15.md step 2: the D15 seat's privacy gate changes. Before, it ran export.violations over the whole bundle with a planted-credential arm. Now it runs debug_ingest.py stage 2 (replay half only, planted arm in stage 2b), plus a new rule for the rest of the download: credential keys hold only **REDACTED**. That rule is backed by no instrument; the nearest checks are the diagnostics tests at tests/entities.py:26324-26352, which cover the Tibber token, the name and the location only. It also narrows the scope export.violations judges.
2. dev/programme/RULINGS.md: two owner rulings leave the register every seat reads. 2026-10-24 "mechanise first" now lives only in D11.md (a finder brief), and the 2026-11-13 d5/d6 scope quote only in D6.md. This follows the file's rule (1), but how far each ruling reaches is the owner's call.
3. dev/programme/plan-2026-09-open-issues.md: drops "every seat is told to open all three [.mdc] at seat start". The instruction was stale, since rules now load by paths: globs, but a seat duty is removed.

## Corrections (no seat obligation changes)

The pointer dedups (root-cause, standing-roster, steward SKILL, D4/D5-criteria); the paths in brief-citations, gate-scoping, writing-for-agents, HANDOVER, ABOUT, INSTRUMENTS, dev/audit/README and tests/README; and in the plan file, the verdict grammar, the cross_seam_fraction removal, the gate-lock pointer, the web-fix-wave log, the badge and the architecture.md "since fixed" notes. The .claude/rules and .cursor/rules copies are generated (rules_sync --check OK).

## Notes (not blocking)

- D6-s2-02 and D6-s2-03 (merged into D6-s5-02) are unfixed. The body discloses this under Forward-carry, with policy_lint's fixture as the reason, pending an orchestrator ruling. The group lands partial.
- D15 step 2's "elsewhere credential keys hold only **REDACTED**" can be read as a claim or as a step. A finder cannot tell which, and no instrument runs it.
- tools/audit/seat/INSTRUMENTS.md:15 has trailing whitespace (git diff --check).
- D15-s1-02's privacy_gate.py --bundle was not run: no bundle is in the tree.
