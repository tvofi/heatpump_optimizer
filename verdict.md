Fix review: merge 30b069508f194240f90ddd05cb5cfee0613814e1

bus-nonce: ff2b1f4c7c38a33fa032981c5120be5d
pending-ci: tests / coverage, tests / fast (3.14), tests / browser, tests / closures, tests / mutation

## Summary

Round 2, a delta review of R10-HOTFIX-FLOW-SETPOINT-STUCK at head 30b069508f194240f90ddd05cb5cfee0613814e1, over the reviewed head 90eb45f69f511811ddd2ed9e7c6570ab8b2abdd1 (`review_carry.py` prints FRESH-REVIEW, so this is the delta). The branch's own delta (c91412dfb9..head) changes no production code: one docs sentence, one strengthened check in tests/features.py, #3404's mutant harness re-anchored, six mutation-ledger pins, and the delivery row. The custom_components/ lines in `git diff <reviewed-head> <head>` all come from the origin/main merge c91412dfb9, whose tree is exactly the automatic merge-tree result, so it carries no hand resolution. Nothing here widens the scope. The previous verdict's one finding was carried to R11-INTAKE-R10-RESIDUE and is untouched by this delta. It still stands as carried.

## Evidence

- RESULT delta scope: `git diff --stat c91412dfb9 30b069508f19` gives 10 files, none under custom_components/ (ev/delta_merge.txt). The main merge c91412dfb9 has tree b742b6a5ba, the same tree `git merge-tree --write-tree 90eb45f69f51 e23124ff6e` produces automatically.
- RESULT strengthened restart check earns its value pin: with #3404's M09 applied (`record.pop("space_setpoint", None)` -> `pass`), the head's check fails with `(1, [35])` for both unload and off, and the arbiter block prints `1 of 57 FEATURES BLOCK FAILED` (ev/m09_new.txt). The same mutant against the old count-only predicate prints `ALL 57 FEATURES BLOCK PASSED` (ev/m09_old.txt), so M09 survived before the change, as the body says. I re-derived M09 only. I did not re-run M10 or M11 against the old predicate.
- RESULT #3404's mutant harness at the head: `python3 dev/audit/harnesses/r10_arbiter_off_restore_mutants.py` exits rc 0 with 36 KILLED and only the 2 `SURVIVED NULL` lines (ev/mutants_head.txt). That is 21 on the arbiter block (M01-M20 and M35_forget_drops_own_write) and 15 on the seam block (M21-M38 less M33, M35 and M36). This matches the body's 35 KILLED plus M35 at 790d5e66ce, with M35 now killed on the arbiter block. The base-side `20 KILLED and 19 SURVIVED` at 154dbb4c61 was not re-derived.
- RESULT seam block end marker: at the head the bare `_fb_floor = _fb_sim(` first occurs at tests/features.py:87683, before the Carry 8 checks at 88292-88419. The replay marker `_fb_floor = _fb_sim(clamp=(26.4` is at 88434. The fixed block prints `ALL 53 FEATURES BLOCK PASSED` and its output includes the 3 Carry 8 checks (ev/block_seam.txt). The arbiter block prints `ALL 57 FEATURES BLOCK PASSED` (ev/block_arbiter.txt). Both of the body's figures re-derive.
- Re-anchored mutants: each re-anchored `old` occurs once at the head, or the harness would have refused before running. M03 now drops `if own:` in `_arm_space`, which is the own-write check that this branch moved there. M36 is retired because Off's guard no longer reads `held.dropped`, which the reviewed production diff shows. I accept both intents.
- RESULT detector `r10_rca_setpoint_latch.py --check`: at the head rc 0, `failed=0` of 36 (ev/det_head.txt). At origin/main 50373173d4 rc 1, `failed=4`, including `written=55.0 dropped=25.0 reading=25 armed=False` (ev/det_main.txt).
- RESULT doc_claims at the head: `ALL 348 checks PASSED` in 10 s (ev/doc_claims.txt), matching the body's red-check answer. The docs delta only removes "as before" plus a line rewrap.
- Mutation ledger: the six new pins replace anchors that the reviewed production lines changed (the old 59013da4, cbe69d47 and 605f504a pins are gone at the head). Each is a `--pin-killed` killed_by row, and their movement comes from the reviewed code change, not from the instrument. The failure counts inside the pins' reasons come from full tests/features.py runs, which are CI's heavy runs. I did not re-take them.
- Merge: `git merge-tree --write-tree origin/main 30b069508f19` against origin/main 50373173d4 exits 0. `LEDGER-MERGE: resolved tests/closures.json` was printed and no MERGE-CLAIM line appeared (ev/delta_merge.txt).
- VERSION, the manifest and the claim files are untouched by the delta. Neither a claim file nor tests/golden/ is in the branch delta.
- CI at this head: `merge_train.py classify 30b069508f19 --pr 3561` printed `WAIT 30b069508f194240f90ddd05cb5cfee0613814e1 pending: gate red: none` (rc 3) on every run from 23:45 to 00:31 UTC (ev/classify_log.txt). The workflows were re-run at 00:26. At about 00:30, `tests / coverage`, `tests / fast (3.14)`, `tests / browser`, `tests / closures` and `tests / mutation` were in progress. Completed and green: `tests / typing`, `validate / validate-hacs`, `arch-score`, `tests / briefs`, `budget-raise-gate`, `hassfest`, `tests / closure-scope` and `tests / arch-instrument`. I saw no red on a required context. Because this review is complete, the verdict carries `pending-ci:` for the relay to settle.
- Red checks: the body answers the earlier reds at a02783d44d: `tests / fast (3.14)` (doc_claims), `tests / mutation` (6 unpinned, now pinned) and `tests / mutation-autofix`. Each names its cheaper detector.
- carry_audit self-check: rc 0, `CARRY-AUDIT: 2 finding item(s): 2 routed` (ev/carry_audit.txt). I gave it a body file holding the PR body's `## Forward-carry` and `## Friction` sections verbatim, which the packet's own carry_audit counts as the body's only finding item (86f47084).

## Findings

- Follow-up: the body's `## Head` section is stale. It says "this head fast-forwards it with the repair commits only", "no main merge was needed" and "Branched from origin/main 154dbb4c61 (merge base)". In fact the head contains the origin/main merge c91412dfb9, and its merge base is e23124ff6e. The head SHA it names is correct, and every figure I relied on was re-derived here at the head. Carry: dismissed: body prose only, no code or figure effect, the head SHA is correct and the merge is re-proven at the head

## Friction

none
