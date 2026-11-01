R10-CLOSEOUT-CLEANUP, instrument half (Part of #201; issues #2505, #2727, #2728). Lands the closeout instrument and folds in the two fly-ins: `prune_refs.py` (batched push arm, keep guards, `--topic`) and `worktree_gc.sh` (unpushed keep, `on-remote` class). The `--apply` run is the orchestrator's final act and was not run here; merging this sets the group carries-open.

Carry dispositions (the group's six carries):
- Carry 1 (probe refs): residue-no-pr in `prune_refs.py`'s plan, deleted by the final run; no new rule.
- Carry 2 (roster-gated `--apply`): `closeout.py` refuses naming each open group; arms and mutant `closeout-1` below.
- Carry 3 (folded R10-FLY-PRUNE-REFS): the push arm (0 gh calls, tags before deletes, null control 2N), the `claude/*`, open-group `design/` and age keeps; its inner carries (dispatch/`brief/` residue, stranded handoff refs) fall to the same plan as archive-delete residue.
- Carry 4 (folded R10-FLY-WORKTREE-GC): `unpushed` keep on both the classify and apply paths, and the `on-remote` class with its cwd, fetch and lsof controls.
- Carry 5 (`--topic`): archive-then-delete, refused on a `+` cherry line or an open PR; mutants `prune_refs-5` and `prune_refs-6`.
- Carry 6 (build the tooling now, run last): the instrument lands here; the `--apply` run is not made.

Design notes: `--topic`'s `git cherry` refusal covers `handoff/` code refs only, since body and dispatch refs are orphan commits that always carry a `+`; local branches holding commits no remote or tag has are never deleted.

## Head

Measured at head 7be77bd48296b992c8439c7d8e01a21da2c30ac7 (origin/main 6421fe135d9f5a9e65433a4433f000d2419486bf merged in; `tools/pr/prepr.sh` rerun after the merge).

## Mutation proof

Eleven mutants, each planted in a production predicate, run by `dev/audit/harnesses/r10_seat_selftests_mutants.py closeout-1 closeout-2 prune_refs-1 prune_refs-2 prune_refs-3 prune_refs-4 prune_refs-5 prune_refs-6 worktree_gc-1 worktree_gc-2 worktree_gc-3`: all KILLED, `RESULT survivors=0`. They drop the roster refusal, the step gate, the `claude/*` keep, the open-group `design/` keep, the age guard, the missing-tag refusal, the cherry `+` refusal, the dispatch topic match, the unpushed keep, the cwd test and the fetch gate.

## Null control

Every arm has one in its self-test: `--apply` with every other group done proceeds past the roster; the old gh-api arm on a 4-ref plan makes 8 writes (2N) against 0 for the push arm; a `claude/*` tip is kept while the same tip on a `fix/` ref is deleted; a done group's `design/` ref is still deleted; a topic fully on main is archived then deleted; main and the open-PR head survive; a clean seat worktree at a pushed head is removed beside the kept unpushed one; a clean detached worktree at a head no remote holds stays `unmerged-head`, and one at the origin/main tip stays kept.

## Figures

- `python3 -I tools/audit/seat/prune_refs.py --self-test` -> SELF-TEST PASS (67 checks).
- `python3 -I tools/audit/seat/closeout.py --self-test` -> 23 checks, 0 failed.
- `bash tools/audit/worktree_gc.sh --self-test` -> 91 checks, 0 failed.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` -> 105 self-testing, 105 wired, 0 index gaps.
- Dry plan on the live refs: `python3 tools/audit/seat/prune_refs.py --prs-file <[]> --roster-file dev/programme/rosters/wave-r10-groups.json --verdicts-drained`; in this checkout most tips have no local objects, so their ages are unreadable and the refs are kept (`keep-young-tip`); the closeout run fetches heads first.

## Red checks

none. `prepr.sh` first predicted two reds on this branch, both repaired before handoff: REF PRIVACY (closeout.py registered in PUSHERS as fixture pushes; its live writes are prune_refs.py's, which is guarded) and tests / closures INERT READS (`ci_predict.py --apply-inert`).

## Forward-carry

- The orchestrator's final `--apply` run (`python3 tools/audit/seat/closeout.py --roster-file dev/programme/rosters/wave-r10-groups.json --successor <N> --apply`): step 4 refuses until every open issue but the successor is dispositioned, and archiving merged cloud sessions is the orchestrator's. Carry: R10-CLOSEOUT-CLEANUP
- The probe refs for #2654 #2656 #2657 (`fix/r10-ci-layout-p2-probe-*`, `wip-sync/ext-upd-fix-r10-ci-layout-p2-probe-*`) are residue-no-pr and fall to that run's plan; no separate rule. Carry: R10-CLOSEOUT-CLEANUP

## Friction

none
