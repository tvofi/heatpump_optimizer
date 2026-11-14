Fix review: blocked aeb5f761cb62840ec481d9cb4df97bebadcbafbb carry-missing: not carried to R11-INTAKE-R10-RESIDUE; carry-201 entry 22's second half (window_work_minutes timing-inferred need edges) is still absent from the roster branch tip 05188a4777

bus-nonce: 4a84318df55e6c08ecc0ebc34c17bc07

## Block

Round 3 is a delta round over da2d0fd3ad716359ae2af261e530398ded16b584, at head aeb5f761cb62840ec481d9cb4df97bebadcbafbb. The delta is d8ac2c0dc3, which changes tests/entities.py at 4+/1-, and the merge aeb5f761 of it, whose parents are da2d0fd3 and d8ac2c0dc3 (ev/delta.diff, ev/delta_commits.txt).

0. **The round-2 block item 1 is still unresolved: carry-201 entry 22's second half is not in the tree.** The roster branch origin/handoff/audit-r10-roster now has tip 05188a477764 ("roster_edit append-carry R11-INTAKE-R10-RESIDUE"). That commit added two other carries: the exported_at wall-clock entry and the 11e9ad5a reference-basis digest. It did not add this one. The roster's `R11-INTAKE-R10-RESIDUE` holds 171 carry items. None of them contains `window_work_minutes`, and the roster file has 0 matches for `window_work_minutes|timing-inferred|QUEUE_EPS` (ev/carry_targets.txt, ev/roster_e22b.txt). The PR body still says "FOR THE ORCHESTRATOR TO FOLD ... then name the resulting SHA here", and it names no SHA. carry-201.json was the only file in the tree that held that text, and this PR deletes it. finding-propagation.md says "The producing PR does not merge until the carry is in the tree", so the block stands (fix-review.md step 10). The repair is outside the fixer's power: the orchestrator or relay appends the body's quoted text to R11-INTAKE-R10-RESIDUE's `carry` list on origin/handoff/audit-r10-roster, and the body then names that SHA. The code at this head needs nothing further. A round-4 review is the delta of that body change and one roster read.

Resolved since round 2:
- Round-2 block item 0, the cited-program arm (tests/entities.py:34601ff), is resolved. The `_sp_cog in _SP_CITED` clause is replaced by `_sp_cited([("x.md", f"run `{_sp_cog}`")]) == {_sp_cog: ["x.md"]}`, which plants the citation as the dora_keys and units legs already do. `len(_sp_cog_held) > 0 and not _sp_faults(_sp_cog)` is unchanged and still runs against codeowners_gap.py's real source, so the leg keeps its purpose. At the head, `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/entities.py` prints the arm `ok` and `ALL 2725 ENTITY CHECKS PASSED`, rc 0 (ev/entities_head_arm.txt, ev/entities_head_tail.txt).
- The control is not weakened. Mutant C makes `_sp_faults` count literals a program only holds as opened (`_sp_literals(..., opened=False)`; ev/mutant_C.diff). Under it the arm FAILs and names codeowners_gap's 4 held stale literals as opens-faults: `1 of 2725 ENTITY CHECKS FAILED`, rc 1 (ev/entities_mC_arm.txt). Only the held-path leg catches that mutant.

## Findings

- Follow-up: the body's `## Red checks` re-answer for `tests / fast (3.14)` names the cheaper detector (the fixer's own full entities.py run, read to its count line) and process state (b). That settles round 2's root-cause follow-up, subject only to pr-contract's run at this head. Carry: dismissed: settled in this PR at this head

## Evidence

- RESULT head-measured: aeb5f761cb62840ec481d9cb4df97bebadcbafbb. The body's head line names the same SHA (ev/HEAD.txt).
- RESULT scope: delta. The delta touches tests/entities.py only. No line under custom_components/ is in it, so the review does not widen (fix-review.md step 12).
- RESULT entities-head: arm ok; ALL 2725 ENTITY CHECKS PASSED; rc=0.
- RESULT mutant-C: arm FAIL; 1 of 2725 FAILED; rc=1. The mutant is killed.
- RESULT carry-targets: R11-INTAKE-R10-RESIDUE is at resume.stage not-started, and R10-OUTSIDE-CONTRIBUTOR-CYCLE is at in-progress, so both are live. R10-CLOSEOUT-PREP is at done, so no `Carry:` in the body targets it. carry_audit at the head reports 33 routed, 0 unrouted, 0 bad destinations (review packet).
- RESULT merge-tree: `git merge-tree --write-tree origin/main aeb5f761` exits 0 against origin/main 23cc7b8e1d (ev/merge_tree.txt).
- RESULT version: VERSION, RELEASE_NOTES.md and custom_components/ are untouched three-dot from the merge base (ev/version_check.txt).
- RESULT policy-drift: `git diff merge-base...origin/main -- dev/governance/roles/` is empty.
- RESULT CI: `merge_train.py classify aeb5f761... --pr 3553` printed `WAIT aeb5f761cb62840ec481d9cb4df97bebadcbafbb pending: gate red: none` on both polls (ev/classify_log.txt). This verdict blocks on content, so it does not wait for CI to settle. `gate` and `tests / nightly-status` read failure in the digest while other lanes were still running. I made no red-check finding, because the head's workflows have not concluded (step 11).
- RESULT figure-not-re-derived: I did not re-run the body's "measured NOT answered" spot figures (min3_running_folded=3/15, selfmod_independent_4kw=0.789), as in rounds 1 and 2.
