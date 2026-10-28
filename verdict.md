Fix review: merge 5a1a60c87abe79629f4ab647c2d1b72b62e4a788

bus-nonce: 5988b126c0a056b2c9c6fbaa02ad4ac2

Round 1. Head measured: 5a1a60c87abe79629f4ab647c2d1b72b62e4a788 (code head 86d399b50 plus the delivery-row commit). Docs-only diff: two files, dev/programme/triage/s6-batch56.md and dev/programme/delivery/2931.md. No production code, no VERSION, manifest or notes change, no claim files, no closures or budgets touched.

## Findings

None.

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main 5a1a60c87abe79629f4ab647c2d1b72b62e4a788` exit 0, no conflicts; origin/main is still b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa, the merge base.
- RESULT mutation proof (the file's only consumer is roster_edit.py's triage gate): on the committed file `ruling_verdict(src,'P267')` = ACCEPT and `triage_refusal` returns None; with the Verdict line rewritten to DEFER in a copy it returns "...#P267 is not an ACCEPT ruling (DEFER)"; with the file absent it returns "the triage ruling ... is not on the roster branch or origin/main". Body's mutation proof and null control reproduce.
- RESULT figures re-derived: merge_train.py is 5831 lines; `wait_ci` at line 1142; `unstale` at line 2452 with the `/rerun` POST at 2468; `--overlap` text at line 172 and the recarry phase comment at 488. `git ls-tree origin/main dev/audit/config/` lists bugclasses.json, finding.schema.json, rotation.json, scopes.json. Roster be898eaef (live handoff/audit-r10-roster tip): kinds instrument 105, defect 29, production 8; one hotfix-prefixed group R10-HOTFIX-BATCH-ERREXIT; R10-TRAIN-OVERLAP-GRADE, R10-FLOW-WIP and R10-ORCH-LEDGER all exist there. Archive tags 103da8f7b, 728c633ef, 16ed57ce7 match.
- RESULT archived findings: prepr.sh heavy_run is at tools/pr/prepr.sh:767; N-orphaned-handoff.md lines 48 and 55 read as quoted; cloud_dispatch.py self-test checks sit at lines 535, 544 and 585 with the quoted names. The 2577 mutants were not re-driven (the ruling says so itself).
- Forward-carry: three carries named (R10-TRAIN-OVERLAP-GRADE, R10-FLOW-WIP, R10-ORCH-LEDGER); carry_audit at the head: 3 routed, 0 unrouted, 0 bad destinations.
- Commits: two, no Claude, Co-Authored-By or session text in messages. Delivery row is in the open-row shape. ci_priority.json and ci_priority.py are absent from the tree, as the ruling describes them as to-be-built.
- Not re-derivable here: the V181 text and owner amendments quoted from proposals.md (not in the tree, lives with the orchestrator); the R10-FLY-CANCEL-SWEEP brief and the batch-55 file (P266) are not on main or in the roster, so the ruling's references to them are taken from the body. tests/entities.py could not run in this container (no homeassistant module), so the classification gate was not run by me; the file is under dev/programme/triage like its sibling rulings.
- CI at render and re-read: the head's runs (prelude, cancel-superseded, refresh) were all queued, arm skipped; no check had concluded and none was red, so no red check owes a root-cause answer. The body states Red checks: none. The merge train reads CI itself before landing.
- Red-check and under-scoped answers: none owed.
