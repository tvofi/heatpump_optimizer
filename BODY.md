R10-CARRY-RESIDUE part 2: the carry audit, bus round counter, body_push/relay and standing-tick items the round-3 re-cut routed here.

Code: 30986c09c9f1e6a20e9ff9fd76266b2df3fc535c

## Head

30986c09c9f1e6a20e9ff9fd76266b2df3fc535c, measured at merge base daf8b349fd30cc60786eeca333a426b693aa4c5f (origin/main at 2026-11-08T21:19Z). It is the blocked head 6b5d99b5c48036517be86310c773e8e8a66cbe14 with origin/main merged into it twice (fixer.md step 6: merge, never a re-cut): 1877c8000 resolved the conflict at main 51cd5ec8a; main then moved to daf8b349f (#3346: `tests/card_browser.mjs` and its delivery row, disjoint from this diff), merged cleanly as 30986c09c, and every figure below and `prepr.sh` were re-run at 30986c09c.

## Merge resolution

The round-1 verdict blocked 6b5d99b5c on a content conflict in `tools/audit/carry_audit.py` `landed()` with #3318 (merge 17e621f08). Main added the own-group carry-status arm (`own_group`, `own_carry_status`, `# mut:ownstatus`, the `statuses` argument and the `CARRY-STATUS` print); this head replaced the landing predicate so a source lands only through a group's carries. The resolution keeps both, in that order: an own-group item naming one of its carries by index is a status line and `continue`s before any landing test; every other item takes this head's predicate (`r["id"]` in brief or carries, a source token in carries only). The `landed()` docstring now states the source rule. No other file conflicted; `cloud_dispatch.py` auto-merged. `git merge-tree --write-tree origin/main HEAD` now prints only the tree id (9e89e536f) at 30986c09c, no CONFLICT line.

## Carry dispositions

- Carry 0: covered here. `dev/governance/roles/standing-tick.md` names the unflagged `CARRY: #<pr> <sha>` line beside the ancestor-recarry test, inside the file's budget (25 lines, `policy_lint.mjs` clean). A policy edit: it waits for the owner's approving review (see Approval).
- Carry 1: fixed in `carry_audit.landed()`. A source token (`--pr`, `--topic`) lands an item only through a group's carries, never its brief; an item id still lands through either. The brief names the PRs it was cut from, which is why `--pr '#3234'` hid every missing carry.
- Carry 2: same edit as carry 0.
- Carry 3: `body_push.sh` exits 4 when CARRY-LANDED is the refusal (the earlier arms exit before it) and every refusal prints `body_push: REFUSED <KIND>`; `cloud_relay.sh` gains `carry_fold_arm` (run each pass after `handoff_arm`), see carry 14. The carry named a `handoff-wip/<topic>-carries` ref; none is needed, because the refused body is already kept on `handoff-wip/<topic>-body`.
- Carry 4: `bus.sh blocked_rounds` counts distinct blocked heads on `verdict/<pr>`.
- Carry 5: `set-resume --field pr` per done group lacking `resume.pr`; precondition: count measured at the roster seat's own base, each `pr` read from `dev/programme/delivery/<N>.md`. Roster DATA edit on the roster branch this seat may not write; it waits for the orchestrator's roster seat with its precondition kept. Nothing was written or guessed here.
- Carry 6: one `edit-brief` per live group naming the old handoff phrase; precondition: the phrase count over live briefs reads 0 afterwards. Roster DATA edit on the roster branch this seat may not write; it waits for the orchestrator's roster seat with its precondition kept. Nothing was written or guessed here.
- Carry 7: `set-stage <G> absorbed --into <host>`; precondition: `carry_audit.py roster` then reports REROUTED. Roster DATA edit on the roster branch this seat may not write; it waits for the orchestrator's roster seat with its precondition kept. Nothing was written or guessed here.
- Carry 9: duplicate of carry 5. Roster DATA edit on the roster branch this seat may not write; it waits for the orchestrator's roster seat with its precondition kept. Nothing was written or guessed here.
- Carry 10: duplicate of carry 6. Roster DATA edit on the roster branch this seat may not write; it waits for the orchestrator's roster seat with its precondition kept. Nothing was written or guessed here.
- Carry 11: duplicate of carry 7, and the absorbed-group lint is built only after those data edits land. Roster DATA edit on the roster branch this seat may not write; it waits for the orchestrator's roster seat with its precondition kept. Nothing was written or guessed here.
- Carry 8: plant C6 now fails with FAIL lines (see Mutation proof).
- Carry 12: same as carry 8.
- Carry 13: same edit as carry 0.
- Carry 14: `carry_fold_arm` reads each `handoff-wip/<topic>` BLOCKED.md and, only when its refusal kinds are exactly CARRY-LANDED and `handoff-wip/<topic>-body` is kept, runs `carry_fold.py` on that body and then `body_push.sh` from a worktree at `handoff/<topic>`. Any other block prints `OWED carry-fold ...` and goes on the level. The fixer prompt (`cloud_dispatch.py`) tells a fixer to push the exit-4 output as BLOCKED.md.
- Carry 15: the review packet reports it, but the group holds carries 0 to 14 on `origin/handoff/audit-r10-roster`; nothing is owed under that number.

## Mutation proof

- Carry 1, re-taken at 30986c09c: `landed()`'s source check read against `group_text(dests, tok)` (brief included) instead of `group_text(dests, tok, False)`: `python3 tools/audit/carry_audit.py --self-test` goes `402 checks, 1 failed` (FAIL "landed: the source named only in the group's brief does not land it (#3234, before)"); restored: `402 checks, 0 failed`.
- Merge resolution (main's arm kept): `if tok == own and own_carry_status(...)` (`# mut:ownstatus`) replaced by `if False:`: the same self-test goes `402 checks, 2 failed` (FAIL "landed: an own-group item naming one of its carries by index lands nothing and is a status line", FAIL "landed: the group is read from pr_group when the source names no topic"); restored: `0 failed`. So the resolution keeps #3318's pins live under this head's predicate.
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

All at 30986c09c, 2026-11-08 (UTC).

- `python3 tools/audit/carry_audit.py --self-test` : 402 checks, 0 failed (395 at 444f489ad; the 7 added are #3318's own-group checks).
- `bash tools/audit/seat/body_push.sh --self-test` : 36 checks, 0 failed.
- `bash tools/audit/seat/cloud_relay.sh --self-test` : 384 checks, 0 failed.
- `bash tools/audit/seat/bus.sh --self-test` : 161 checks, 0 failed (the one baseline failure at 73365699a no longer fails at merge base daf8b349f).
- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` : 129 checks, 0 failed.
- `python3 -I tools/audit/seat/ledger.py --self-test` : 101 checks, 1 failed (the KINDS census, see Red checks).
- `python3 tests/structure.py` : STRUCTURE RATCHET PASSED.
- Scope: `python3 tests/closure.py select --diff daf8b349f` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`; `scope.run` names `tests/doc_claims.py` and `tests/entities.py`.
- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` : `ALL 296 checks PASSED`; `PYTHONPATH=tests/hastub python3 tests/entities.py` : `ALL 2668 ENTITY CHECKS PASSED` (its `FAIL` lines are the refusal fixtures it drives; exit 0).
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` at 30986c09c: `rc=0`; `closures` skipped (PREPR_SKIP_CLOSURES; closures-autofix is left to CI), `unpinned sites` skipped ("the diff adds no unpinned mutation site"), `diff mutants` skipped (MUTANT_CMD unset; the mutation proof above was run by hand).

## Unpinned sites

At 30986c09c `prepr.sh` step 6d reports "the diff adds no unpinned mutation site". The dispositions below are the 444f489ad run's, kept for the sites that run listed:

- `carry_audit.py:1880` and `:1882` (CONST_SWAP on the fixture's group index / done-set): equivalent. Moving the brief to a group the item does not name leaves the expected `1 missing`; the real kill is the mutation proof above.
- `roster_edit.py:1523` (RETURN_DEL, CONST_SWAP on `refuses()`'s crash arm) and `:1759` (CONST_SWAP on the group index): the arm runs only when an op crashes, so only the C6 plant reaches it. Killed there, not by the normal self-test: `r10_roster_ops_mutants.py C6` above, an in-tree harness.

## Red checks

At 6b5d99b5c (the blocked head; 30986c09c has no check-runs yet, since it is not the PR head): `prepr.sh` `closures` refused: `tests/entities.py` exited 1 while the closures were recorded. It exits 1 identically on origin/main (same `3 of 2665 ENTITY CHECKS FAILED`, a clean worktree at the merge base), so it is the container, not this diff; CI re-derives. The cheaper detector exists and ran: the same script, locally. `WARN diff mutants` is answered under Unpinned sites.

Check-runs of 6b5d99b5c48036517be86310c773e8e8a66cbe14 read once, filter=all, all pages (68 runs). Five concluded red; no other run at this head concluded failure, and `CodeQL` and `tests / closures-autofix` are not among them (`CodeQL` success, `closures-autofix` skipped). The checker's red history over the 5 commits between origin/main and this head lists only `governance / instrument-self-tests`; no earlier push of this PR had a red that a later push cleared.

- `governance / instrument-self-tests` (run 42478631013, job 128725587761, 13 min, not a timeout cancellation): this diff caused it. Step "Show the obligations ledger refusing its own fixtures" ended `ledger self-test: 101 checks, 1 failed`, the failure being `every kind cloud_relay.sh writes is a ledger kind (census of level_line and ledger_open)`: `carry_fold_arm` writes `level_line carry-fold`, a kind `tools/audit/seat/ledger.py` `KINDS` does not list. The four steps after it were skipped. Reproduced at this head: `python3 -I tools/audit/seat/ledger.py --self-test` prints the same FAIL. Answer: a cheaper detector exists, that one command (seconds), but `prepr.sh` does not run it; only `governance.yml` does, so the failure reached CI. Standing cost of closing the gap: one line in the `prepr.sh` self-test list, seconds per run. The repair is one entry in `KINDS` in `ledger.py`. It is still owed at 30986c09c: `python3 -I tools/audit/seat/ledger.py --self-test` prints the same FAIL there. This repair seat's brief is to fix only what the round-1 verdict names (the carry_audit.py conflict), so it is not made here; this red will recur on `governance / instrument-self-tests` at this head. The orchestrator decides that push, and the PR must not be read as clean until it lands.
- `gate` (check-runs 128725941970 at 12:07 and 128728973151 at 12:20): class R10-HOTFIX-GATE-BUSY-DEFER. Both printed `FAIL run(s) [42478631013] at this head are still being judged; their gate decides`: the edit-run deferral, with code run 42478631013 the run that decided it (it concluded failure on `governance / instrument-self-tests` above). Cheaper detector: none exists for a deferral that fires while the deciding run is in flight; standing cost: the red clears when that run concludes, and this one cleared into the real failure.
- `gate` (check-run 128731910040 at 12:32): the same run's final decision, `FAIL pr-contract / pr-contract: failure (this run)`. It is the aggregate of the `pr-contract` red below, not a separate cause.
- `pr-contract / pr-contract` (check-run 128731777697): its `[pr-body]` check refused the earlier body because `## Red checks` did not name `governance / instrument-self-tests` (this section is the answer). Cheaper detector: `tools/pr/prepr.sh --body-check` against the live check-runs, run before the handoff; the earlier body was checked before the head had any concluded red, so it could not see it. Standing cost: one read of the head's check-runs per body, which this re-take did.

## Forward-carry

- The roster data edits above stay with the orchestrator's roster seat. Carry: dismissed: already carries 5, 6, 7, 9, 10 and 11 of this group, no new finding
- `standing-tick.md` line: policy, awaits the owner's review. Carry: dismissed: it is in this diff, nothing to carry

## Approval

Pending, not given: `dev/governance/roles/standing-tick.md` (the `CARRY:` line, 4 lines changed) is a policy edit and merges only on the owner's approving review at its head.

## Friction

none
