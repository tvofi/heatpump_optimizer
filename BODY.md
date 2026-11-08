R10-BODY-CONTRACT part 4: the still-open carries that touch none of part 3's files. Three of the six were already built at the merge base and are answered with their measured controls; two are built here.

## Head

`c77a4c03765f8f9d1825d3ad7b3a836f643fcaf9`

## Mutation proof

Carry 43: replacing the own-group test in `landed()` (the line marked `# mut:ownstatus`) with `if False:` turns two arms red in `python3 -I tools/audit/carry_audit.py --self-test`: "an own-group item naming one of its carries by index lands nothing and is a status line" and "the group is read from pr_group when the source names no topic".
Carry 0: dropping the `--roster-ref` argument (`# mut:rosterref`) leaves the new real-roster mutant arm in `bash tools/audit/seat/body_patch.sh --self-test` accepting the body the ref refuses.
Carries 5 and 6 (built at base): `self.live(g)` dropped in `Dests.check` turns 5 self-test arms red ("a done group is a bad destination", "a closed group (R10-GONE) is refused naming it and listing the live after-edged consumers" and three more); `if pm and GROUP_TOK.match(` made `if False and ...` turns "`Carry: <done group> | dismissed: <reason>` routes" red.

## Null control

Carry 43: the same item naming another live group lands one append-carry; an own-group item with no carry index lands one; an index the group has no carry at lands; the same item from another group's pull request lands (four arms in `carry_audit.py --self-test`). Carry 0: the same body with the round roster branch holding the group is accepted (arm "the same body, the branch holding the group").

## Figures

- diff mutants: `python3 -I tools/audit/seat/mutant_run.py --diff <merge-base>...HEAD --cmd <carry_audit self-test wrapper> --max-mutants 40 --report-only`: 4 survivors, wall time about 45 s, all disposed under `## Unpinned sites`.
- carry_audit self-test: `PYTHONPATH=tests/hastub python3 -I tools/audit/carry_audit.py --self-test` prints its own check and failure counts (the instrument, not a carried number).
- body_patch self-test: `bash tools/audit/seat/body_patch.sh --self-test`.
- structure ratchet: `python3 tests/structure.py` prints STRUCTURE RATCHET PASSED at this head.
- scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed MODE: SCOPED naming carry_audit.py and body_patch.sh, run: tests/entities.py.

## Unpinned sites

- tools/audit/carry_audit.py:594 RETURN_DEL: equivalent mutant (`return None` at a function's end becomes a fall-through returning None)
- tools/audit/carry_audit.py:983 CONST_SWAP: value check, the 100-character display truncation of a CARRY-STATUS line
- tools/audit/carry_audit.py:1921 CONST_SWAP: a test fixture's carry-file issue number, read by no arm
- tools/audit/carry_audit.py:1947 CALL_DEL: a deleted self-test `check(...)` call (test line, no production behaviour)

## Red checks

closures: `prepr.sh` step 6b refuses on tests/entities.py exiting 1 while being recorded in this container: 3 checks fail (the coverage-job, release-ZIP and Pages-workflow workflow-text checks), none touching a file this diff changes; a plain run of the same script at the base checkout fails two of them here (coverage-job and release-ZIP) and a plain run on this branch printed no failure line, so the set is environmental and varies by run. Left to CI's closures context; the cheaper detector is that very step.

## Forward-carry

- Carry 0: built. `body_patch.sh` already passed `--roster-ref` at the base (commit 5c9b6d2f6); what was owed is the control, now a real-carry_audit arm: a worktree roster and main both hold R10-NEW, the round roster branch lacks it, the body's Carry names it, and the contract refuses; with the branch holding it, it passes. Carry: R10-BODY-CONTRACT
- Carry 5: already built at the base: `Dests.check` refuses a done, absorbed or closing group and `consumers()` lists the live groups after-edged on the PR's group; arms and mutants re-run above. Carry: R10-BODY-CONTRACT
- Carry 6: already built at the base: `seg_dests` returns `dismissed(<G>):<reason>` and the pointer is valid for any group of the roster; arms and mutant re-run above. Carry: R10-BODY-CONTRACT
- Carry 8: already built at the base: (i) the carry control lint and `LEGACY_CONTROL_CAP` (a17d51d41 and #3260; `node tools/policy/brief_lint.mjs` prints CONTROL ok), (ii) the one sentence in fix-review.md and judge.md (fde0de40f). No role contract is edited here, so no owner approval is owed. #2438 is already closed. Carry: R10-BODY-CONTRACT
- Carry 9: not in this part: `body_push.sh` is part 3's file; it follows part 3. Carry: R10-BODY-CONTRACT
- Carry 43: built. `landed(body, dests, source, statuses)` reads an item whose destination is the source's own group (the pr_group, else the group the topic resolves to) and which names one of that group's carries by 0-based index as that carry's status; it lands nothing and the `landed` command prints it as `CARRY-STATUS`. An index the group has no carry at still lands. Carry: R10-BODY-CONTRACT

## Carry answers

The numbers are the roster's 0-based carry indexes (the brief's own spelling); the carries this part answers are under `## Forward-carry`.

Carry 1: superseded by the card 7 ruling in carry 42 (part 3).
Carry 2: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 3: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 4: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 7: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 10: dismissed on the roster entry (status line or answered by #3260); nothing owed here.
Carry 11: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 12: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 13: dismissed on the roster entry (status line or answered by #3260); nothing owed here.
Carry 14: dismissed on the roster entry (status line or answered by #3260); nothing owed here.
Carry 15: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 16: dismissed on the roster entry (status line or answered by #3260); nothing owed here.
Carry 17: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 18: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 19: dismissed on the roster entry (status line or answered by #3260); nothing owed here.
Carry 20: dismissed on the roster entry (status line or answered by #3260); nothing owed here.
Carry 21: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 22: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 23: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 24: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 25: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 26: dismissed on the roster entry (status line or answered by #3260); nothing owed here.
Carry 27: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 28: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 29: dismissed on the roster entry (status line or answered by #3260); nothing owed here.
Carry 30: dismissed on the roster entry (status line or answered by #3260); nothing owed here.
Carry 31: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 32: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 33: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 34: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 35: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 36: dismissed on the roster entry (status line or answered by #3260); nothing owed here.
Carry 37: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 38: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 39: dismissed on the roster entry (status line or answered by #3260); nothing owed here.
Carry 40: implemented at c9c8833650e3a24eddb28cf9b172b69ae5113dba (merge of #3260); nothing owed here.
Carry 41: dismissed on the roster entry (status line or answered by #3260); nothing owed here.
Carry 42: part 3's (topic r10-body-contract-p3): card 7 registry blocks, not touched here.
Carry 44: not a roster carry: the roster holds 44 entries, indexed 0 to 43; named only because the handoff's brief-carries count is 1-based.

## Friction

none
