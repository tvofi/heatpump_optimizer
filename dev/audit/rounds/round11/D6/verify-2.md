# D6 verifier, unit D6#2 (round 11)

Trees: every finding here is planted-tree scope (D6-s5/s6/s7), so all numbers come from the private export copy
`../audit-r11-px-D6-2` (baseline export, PYTHONPATH=tests/hastub), with --repo pointing at the local clone holding 92d38ecb.
Interpreter: python3.13 with numpy (python3.14 lacked numpy: under it `golden.py --help` fails, plan_claims.py
reports wrong_rows=10 via a spurious row 05820d6641 "a flag is missing", and claims.py crashes in c_topologies --
an environment artefact, not a finding effect). All figures are counts (contention-immune); load1 175-248, thread_factor 1.00.

| id | V1 reproduced | perturbation | V2 own metric | vote |
|---|---|---|---|---|
| D6-s5-01 | mock_users=5, fix_review_j5_refs=0, README false_or_stale=2 | mock_suite: 5->1, README 2->1 | grep of tests/*.py importing unittest.mock = 5; briefs/fix-review.md absent; j5_gil in fix-review.md = 0 | verify, low |
| D6-s5-02 | round4_d6_rewritten_at_doc_path=0, gate-scoping 1 | round4_d6: 0->2, gate-scoping 1->0 | tools/audit/round4/D6 exists=0; dev/audit/rounds/round4/D6/claims.json exists=1 | verify, low |
| D6-s5-03 | round2_symbol_found=1, brief-citations 1 | brief_exclude: brief-citations 1->0 | brief_lint.mjs SYMBOL_GREP_EXCLUDE = [':!.claude'] only (no round2 entry) | verify, low |
| D6-s5-04 | handovers_under_docs=0, writing-for-agents 1 | handover_docs: 0->1, file 1->0 | find docs -iname '*handover*' = 0; dev/programme/HANDOVER.md = 1 | verify, low |
| D6-s5-05 | leased_or_slotted_besides_stress=9 (lease harness_headers.py, slot 8) | needs_lease: tests/README 1->0 | my own enumeration over all tests/*.py|*.mjs with a scope file per name: 31 non-`none` (unrecorded names fall to slot); MACHINE_MEASURING holds harness_headers.py | verify, low |
| D6-s5-06 | instrument_record_dirs_listed=19, absent=19 | instruments_dirs: INSTRUMENTS 1->0 | ls tools/audit/seat/{round3,round9,handoff,rca}: 0 of 4 present | verify, low |
| D6-s5-07 | worktree_gc_apply_refused=1 (rc=2 REFUSE unknown option) | worktree_apply: HANDOVER 1->0 | bash tools/audit/worktree_gc.sh --apply rc=2 | verify, low |
| D6-s5-08 | event_hub_cited_name_files=0 | event_hub: 0->1 (up, as stated) | find -name event_hub_writes.py = 0; r10_livestate_event_hub_writes.py = 1 | verify, low |
| D6-s6-01 | false=2 stale=16 false_plus_stale=18 | combi_station / card_de / wood_birch: 18->17 each | 24 of 82 „quoted“ strings in de.json match no de.json value (incl. English labels such as „Lower floor (modelled)“, „Restore learned snapshot“) | verify, low |
| D6-s7-01 | false_rows=4, head_na_refused=1 | machinery-true ci_skipped_switches 21->9; fork-full false_rows 4->3; delivery-row-refused class_mismatch_delivery 1788->0, paths 3->2; null ci_null_push=0 | prelude.py scope = "auto" for non-push events (fork PR is scoped); head_note.py treats ## Head as a read heading | verify, low |
| D6-s7-02 | wrong_rows=9 (python3.13) | wave-red-guard 9->8, mdc-three 9->8; wave_red.mjs null arm merges_after_red=0 | .cursor/rules alwaysApply=10, .claude/rules=10, fixer.md gate-lock mentions=0, docs/architecture.md '65 entities'=0, entities.py reads architecture.md (19 refs) | verify, low |

V3: all are documentation/policy text read by agents, not runtime Home Assistant paths; reachability is "agent-facing
docs, no HA path"; severity low (misdirection cost only). D6-s6-01 is user-facing German UI text, reachable in real HA
options/repairs flows (translations served by HA), still low. Seat rules: each harness is a curated per-claim check
list, enumerating only the demonstrated sentences, not every seam of the phenomenon (D6-s6 ledger.py is the exception:
it walks all 2300 units of de.json). Classes: N-move-stale-path fits s5-01..04/06/08 per bugclasses.json naming;
s5-05/s5-07/s7-01/s7-02 "new" kept (behaviour drift, not a moved path); s6-01 I5 kept.
