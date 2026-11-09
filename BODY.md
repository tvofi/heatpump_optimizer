Root-cause analysis `dev/audit/rca/R10-RCA-TICK-BLIND.md`: why the tick board did not prevent the 11-08 stalls (owner's question, tvofi 2026-11-08). Five cases, each with a named cause, a process state, a cost test with measured numbers, and a routed countermeasure. No production code and no policy land here: one new markdown file under `dev/audit/` (an INERT prefix in `tests/closure.py`).

- (a) Outside #3225 (R10-COMBI-TANK) sat 33.0 h after its last seat ref (20.8 h after PR 0 merged). Cause: PLAN derives `in progress` / `blocked by` from roster stage alone, and outside intake closes at `answered`. State (c). Carry: R10-TICK-LEVELS
- (b) 23 handoffs had no PR. A session-local `driver4.py` ran instead of `open_driver.py`, whose `-pN` topic resolution has existed since 2026-11-02, and its NEEDS-TITLE/REFUSE/STUCK lines went to its own files. State (b), against `orchestrator.md` section 13. Carry: R10-TICK-LEVELS
- (b) The stand-in opener is retired in favour of the tree's beat. Carry: R10-FLY-STANDING-CONTRACTS
- (c) The #3327 and #3330 verdicts were refused by carry_audit false positives (an indented `Carry:` continuation; a quoted `Carry:` phrase), finally at 13:32Z and 14:33Z, and were still owed at 20:43Z. That makes seven such refusals this round, so a barrier is owed. State (c). Carry: R10-BODY-CONTRACT
- (c) The board prints probe-refused unclassed and unranked. Carry: R10-TICK-LEVELS
- (d) Of 17 NOT REVIEWABLE lines, 8 were rerun-settleable and 6 real. Gate sweep has been `disabled_manually` since 2026-11-08T11:54Z, so deferrals are never rerun. State (d). Carry: R10-TICK-LEVELS
- (e) `record beat owed` queries `search/issues` with `type:comment`, which returns 0 for recorded shas (measured, 0 against 2 and 7), so it fires at its cap of 10 on every pass. Its retry posts duplicate #201 lines (6726155237, 6726174539, 6726198190; #3312 twice). State (c) for the query, (a) for the retry. Carry: R10-TICK-LEVELS
- Class: a board line whose state or named repair is wrong, seven instances in R10, so a repair-discharges-line self-test barrier is owed. Carry: R10-TICK-LEVELS

The orchestrator asked for a new fly-in group, R10-FLY-TICK-BLIND. `carry_audit.py check` refuses it as `BAD-DEST ... not a group of the roster`, so the carries name the existing owning seams. If the roster seat appends the group, re-point the R10-TICK-LEVELS carries there.

## Head

9dc72ad26857944fdacfdd9acff2e38daa77db32, one commit on origin/main 17e621f08c. Board evidence is from the 19:11:13Z board measured at 996ded2a6dc5. Live GitHub reads were taken 19:40-20:45Z.

## Mutation proof

n/a: no countermeasure is landed. Each check-shaped arm owes its own failing-then-passing self-test arm on the exact cases recorded in section 1, in its fixer's PR (section 4 of the document).

## Null control

For (d), #3297, whose red is a real `tests / fast` failure, stays `back to its fixer` under the proposed split. For (e), the same search without the `type:comment` qualifier returns non-zero counts for both recorded shas, so the zero comes from the qualifier and not from a missing comment.

## Figures

- 17 NOT REVIEWABLE, 20 `back to`, 244 flagged lines: `grep -c` over the 19:11Z `tick.txt`.
- The class split 5/2/1/3/6: every red gate's job-log `FAIL` line via `gh api actions/jobs/<id>/logs`, recorded in the seat's scratch `ev/notrev-classified.txt`.
- Gate sweep `disabled_manually`, updated 2026-11-08T11:54:00Z: `gh api repos/tvofi/heatpump_optimizer/actions/workflows`.
- COMBI-TANK after-edges 01:53:41Z to 19:25:55Z: the roster file's `after` read at each commit of `git log -S R10-COMBI-TANK` on `handoff/audit-r10-roster` (9b2b70355c, 62ecb13511).
- Search counts 0 against 2 and 0 against 7: `gh api --method GET search/issues -f q=<sha40> repo:tvofi/heatpump_optimizer [type:comment]`.
- carry_audit refusals reproduced, rc 1 on both verdicts: `python3 -I tools/audit/carry_audit.py --roster-ref origin/main check --body /dev/null --comments <verdict json>`.

## Red checks

none

## Forward-carry

- NOT REVIEWABLE names deferral-only and real, and the board flags a disabled Gate sweep. Carry: R10-TICK-LEVELS
- OWED handoff lines carry the opener's last result; OPENER ABSENT; triage held-by-ruling; counted, never silently capped. Carry: R10-TICK-LEVELS
- Retire the session-local stand-in opener for open_driver.py under beatd.py. Carry: R10-FLY-STANDING-CONTRACTS
- OUTSIDE-CHAIN-IDLE walks after-edges for outside-sourced groups. Carry: R10-TICK-LEVELS
- probe-refused classified by reason and ranked by critical path. Carry: R10-TICK-LEVELS
- carry_audit: indented Carry continuation and quoted Carry phrase, pinned by the seven refused verdicts. Carry: R10-BODY-CONTRACT
- unrecorded-merge query fixed; HANDOVER line stops naming state_docs. Carry: R10-TICK-LEVELS
- postmerge / record_beat posts nothing when #201 already carries the sha40. Carry: R10-TICK-LEVELS
- Repair-discharges-line self-test barrier per flagged line kind. Carry: R10-TICK-LEVELS

## Friction

none
