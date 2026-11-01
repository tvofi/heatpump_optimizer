Fix review: blocked 6502ddfcfd985f97998bbc369fc8807ae81cd9ca rule-lost: the owner's 2026-09-09 model-routing ruling was deleted and no other file states it

bus-nonce: 5de73c4931f1dbf5d17cae8c3477bcf5

Round 1. Measured head 6502ddfcfd985f97998bbc369fc8807ae81cd9ca (authored code head c2ebaeb5, rewritten against main a7dd7f50).

## Block
- Old HANDOVER.md (origin/main, line 62) held "Model routing is Claude seats, per roster group (fixerModel, reviewerModel, the model object)": Opus for orchestration, architectural fixes, review, survey, judge and production fixes; Sonnet for tests, tooling, docs, records and read-only reporting; Fable only for a very large multi-layer refactor where Opus is judged too risky; a model trailer on a merge or stamp is the session's model, not a routing event. The rewrite drops it. grep for Fable / fixerModel / "model routing" in dev/governance, CLAUDE.md and tools/audit/seat/*.md finds no home. The code only has the RANK table (audit-fix.js, audit-wave.js) and cloud_dispatch.py's model parse, which enforce no assignment rule. The new file keeps only "medium effort; mechanical turn takes sonnet or haiku" and "record PRs reviewed by sonnet". Restore the bullet (shortened is fine) or put it in a contract the owner approves.

## Findings
- Removed rule with no home: the "A new option key derives into config_flow._ABSENT_FALLBACKS (#1107)" bullet is gone. tests/config_flow_steps.py references _ABSENT_FALLBACKS in comments and a check at lines 4076 and 5219. I did not confirm the check refuses an underived key, so I could not confirm a detector replaced the prose. Carry: dismissed: I did not mutate it; the fixer should state which check carries it when restoring the routing bullet.
- Standing-merge.md still names merge_pr.sh for budget and policy heads (the file's own Owed item, surfaced and not edited here, as the body says). Carry: O1

## Evidence
- Merge: git merge-tree --write-tree origin/main HEAD exits 0 (clean) against current origin/main 61b0076f.
- CI: merge_train.py classify 6502ddfcfd985f97998bbc369fc8807ae81cd9ca -> GREEN, pending: none, red: none. The review packet gate digest is green and lists no refusals or advisories.
- node tools/policy/policy_lint.mjs: 0 errors across 50 policy files, rc 0. python3 tests/structure.py: PASSED. tests/layout.py --guard: 0 refusals. PYTHONPATH=tests/hastub python3 tests/entities.py: rc 0, handover arms ok.
- updated-for a7dd7f50 is an ancestor of origin/main.
- Policy status: dev/programme/HANDOVER.md matches no POLICY_GLOBS entry (policy_lint.mjs lists docs/HANDOVER.md only as a deliberate exclusion; the lint output names no handover; CLAUDE.md line 67 says "everything named here but dev/programme/HANDOVER.md is policy"; CODEOWNERS line 14 omits it). The body's "not policy, no ## Approval" holds. Not decided here: the owner-approval question stays as stated.
- Pointers: every path, tool and script cited in the new file resolves at the head (existence loop over about 50 paths printed no MISSING). INSTRUMENTS.md exists. pr_cap.py dispatch-gate exists and documents HPO_WIP_CAP. stamp.py has --round-close. record_row.py has --automerge-check. The archive/probe/design-ci-rev4 and review5 tags exist. I did not open decision 0016's text; the docs/decisions listing returned nothing under that path, so the decision number is not re-derived.
- Volatile state: the critical path is declared "Read at 2026-10-31 ... re-derive it". roster_lib.critical_path on origin/handoff/audit-r10-roster (5cfbe719) returns the same four groups in the same order, so no drift. The file inlines no open-PR list, cap value or mandate id.
- Kill stem: the file has one hit for "revo", at line 167 in prose describing the rule, beside no mandate id. The 10-digit ids at lines 276 (5720829142) and 303 (5702401684) are #201 comment ids carried over from the old file, one the vacuous-detector refusal and one the POLICY_GLOBS ruling; neither is a mandate comment, and neither is within 100 lines of the stem. The PR body has no stem and no 10-digit id.
- Delivery row: three-dot diff holds only HANDOVER.md and delivery/3074.md; no claim file or golden is touched, so claim files are byte-identical; VERSION and the notes are untouched.
- Other removed bullets (ledger bypass, claim files, stale-checkout, 1067 figures, red-check f605da4, rules/branches, CI umbrella, stamp key, _helper) are kept in rewritten form or sit in decisions/CLAUDE.md. The f605da4 note (CLAUDE.md "only the red-check trigger is enforced") and the #510 note are dropped as history; I judge both measured history with no binding force.
- Not run: mutation proof (n/a, record-only diff).
