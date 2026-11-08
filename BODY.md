R10-CARRY-RESIDUE part 2: the carry audit, bus round counter, body_push/relay and standing-tick items the round-3 re-cut routed here.

Code: 444f489ad66a632576438177da8683eb58ef54e1

## Head

444f489ad66a632576438177da8683eb58ef54e1, measured at merge base 73365699a135fb813a43380096b6776d57f8ff4c. origin/main had not moved when `tools/pr/prepr.sh` ran (merge-tree reports no conflict), so no second run.

## Carry dispositions

- Carry 0, 2, 13: covered here. `dev/governance/roles/standing-tick.md` now names the unflagged `CARRY: #<pr> <sha>` line beside the ancestor-recarry test, inside the file's budget (25 lines, `policy_lint.mjs` clean). It is a policy edit: it waits for the owner's approving review before merging.
- Carry 1: fixed in `carry_audit.landed()`. A source token (`--pr`, `--topic`) now lands an item only through a group's carries, never its brief; an item id still lands through either. The brief names the PRs it was cut from, which is why `--pr '#3234'` hid every missing carry.
- Carry 3 and 14: `body_push.sh` exits 4 when CARRY-LANDED is the refusal (the earlier arms exit before it) and every refusal prints `body_push: REFUSED <KIND>`; `cloud_relay.sh` gains `carry_fold_arm` (run each pass after `handoff_arm`). It reads each `handoff-wip/<topic>` BLOCKED.md, and only when its refusal kinds are exactly CARRY-LANDED and `handoff-wip/<topic>-body` is kept, runs `carry_fold.py` on that body and then `body_push.sh` from a worktree at `handoff/<topic>`. Any other block prints `OWED carry-fold ...` and goes on the level. The fixer prompt (`cloud_dispatch.py`) tells a fixer to push the exit-4 output as BLOCKED.md. The carry named a `-carries` ref; none is needed since the body already is the kept state.
- Carry 4: `bus.sh blocked_rounds` counts distinct blocked heads on `verdict/<pr>`.
- Carry 8: plant C6 now fails with FAIL lines (see Mutation proof).
- Carries 5, 6, 7 and 9, 10, 11, 12 (`set-resume --field pr`, `edit-brief`, `set-stage --into`, and the later absorbed-group lint): roster DATA edits on the roster branch this seat may not write. They wait for the orchestrator's roster seat; each keeps its precondition (count measured at that seat's base; `pr` read from `dev/programme/delivery/<N>.md`; the briefs' phrase count reads 0 afterwards; `carry_audit.py roster` reports REROUTED). Nothing was guessed or written here.

## Mutation proof

- Carry 1: `landed()`'s source check read against `group_text(dests, tok)` (brief included) instead of the carries alone: `python3 -I tools/audit/carry_audit.py --self-test` goes `395 checks, 1 failed` (FAIL "the source named only in the group's brief does not land it (#3234, before)"); restored: `0 failed`.
- Carry 4: dropping `sort -u` in `blocked_rounds`: `bash tools/audit/seat/bus.sh --self-test` adds FAIL "five re-posts at one head count as one round and dispatch (#3247)" (fixture: five re-posts at one head).
- Carry 14: replacing the `# mut:foldonly` test with only the kept-body test: `bash tools/audit/seat/cloud_relay.sh --self-test` goes `384 checks, 6 failed` (the mixed-block and no-refusal-line arms); restored: `0 failed`.
- Carry 8: `python3 tools/audit/seat/r10_roster_ops_mutants.py C6` was `rc=1 fails=0` with a KeyError tail before the fix; now `rc=1 fails=3` (FAIL "triage gate fixture restored", "drop-carry with no carry refused", "drop-carry of the last entry leaves the key empty"). The fix is `refuses()` in the `roster_edit.py` self-test treating a crash as no refusal, plus `.get("carry")` in the fixture-restored check.

## Null control

- Carry 1: the same source in a group's carries lands the item (`landed(...) == []`); `#25581` still does not land `#2558`.
- Carry 4: three distinct blocked heads are three rounds and refuse without a `## Re-cut` note (dispatch of #35 fixture).
- Carry 14: `CARRY-LANDED` plus `BODY-LINT` in one BLOCKED.md folds nothing and prints its line; a BLOCKED.md with no refusal line likewise.
- Carry 8: unmutated `roster_edit.py --self-test`: `242 checks, 0 failed`.
- `body_push.sh --self-test` pins exit 4 for the landed arm and exit 1 for pred, lint and packet, and that each prints its `REFUSED` kind.

## Figures

- `python3 -I tools/audit/carry_audit.py --self-test` : 395 checks, 0 failed.
- `bash tools/audit/seat/body_push.sh --self-test` : 36 checks, 0 failed.
- `bash tools/audit/seat/cloud_relay.sh --self-test` : 384 checks, 0 failed.
- `bash tools/audit/seat/bus.sh --self-test` : 161 checks, 1 failed, the same "an ordinary append with no intervening fetch is the same commit object as before" as at the merge base (`git stash` run: 159 checks, 1 failed).
- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` : 127 checks, 0 failed.
- `tools/pr/prepr.sh` self-test: 514 passed, 0 failed (it pinned `rc=1` for the landed refusal; now `rc=4`).
- `PYTHONPATH=tests/hastub python3 tests/entities.py` : `3 of 2665 ENTITY CHECKS FAILED` at both this head and a clean worktree of 73365699a135.
- Diff-mutant step: `MUTANT_CMD` was the three Python self-tests above; `prepr.sh` ran in 26m11s wall (`time`) in total; `mutant_run.py --diff` reports 5 survivors, dispositioned below.

## Unpinned sites

- `carry_audit.py:1880` and `:1882` (CONST_SWAP on the fixture's group index / done-set): equivalent. Moving the brief to a group the item does not name leaves the expected `1 missing`; the real kill is the mutation proof above.
- `roster_edit.py:1523` (RETURN_DEL, CONST_SWAP on `refuses()`'s crash arm) and `:1759` (CONST_SWAP on the group index): the arm runs only when an op crashes, so only the C6 plant reaches it. Killed there, not by the normal self-test: `r10_roster_ops_mutants.py C6` above, an in-tree harness.

## Red checks

`prepr.sh` `closures` refused: `tests/entities.py` exited 1 while the closures were recorded. It exits 1 identically on origin/main (same `3 of 2665 ENTITY CHECKS FAILED`, a clean worktree at the merge base), so it is the container, not this diff; CI re-derives. The cheaper detector exists and ran: the same script, locally. `WARN diff mutants` is answered under Unpinned sites. No check went red on a commit in this branch beyond those.

## Forward-carry

- The roster data edits above stay with the orchestrator's roster seat. Carry: R10-CARRY-RESIDUE-2
- `standing-tick.md` line: policy, awaits the owner's review. Carry: dismissed: it is in this diff, nothing to carry

## Approval

Pending, not given: `dev/governance/roles/standing-tick.md` (the `CARRY:` line, 4 lines changed) is a policy edit and merges only on the owner's approving review at its head.

## Friction

none
