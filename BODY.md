Repair round for the three planner defects of the 2026-11-08 replan study (a name-prefix lane collision, b refused/deferred groups still scheduled, c the critical-path coordinator-cap exemption). Group R10-FLY-REPLAN-DEFECTS. Blocks of `Fix review: blocked b59abf37196379f3264b3aaad42e199aaf053207` answered: class-open, mutation-vacuous, red-ci, and the owner question.

(a) `roster_lane` matches `INSTRUMENT_NAME_STEMS` as the exact group or `<stem>-...`, so `R10-I1` no longer takes `R10-I18N-DE`. (b) `roster_lib.CLOSED_STAGES` gains `refused` and `deferred`; `refuted` stays open. (c) `build_plan` exempts a ready critical-path group from the coordinator cap, flags it `exempt_coordinator`, and `check_plan` leaves flagged groups out of its coordinator count.

## Head

5e55b7e4cc87350c7e15f2bca43049fabace6e8f: the PR head 3cf879467196df974967d702e2e407b9de068f14 plus this repair. `git merge-tree --write-tree origin/main HEAD` exits 0 against `origin/main` 82a2c142f (2026-11-09T05:57Z), so there is no merge; the one resolution it reports is the `tests/closures.json` ledger merge driver. Main moved after the last `tools/pr/prepr.sh` run; the figures stamped below are at merge base 20e83746fe91.

## Owner ruling carried (Carry: R10-FLY-REPLAN-DEFECTS)

The open owner question is ruled by the orchestrator under mandate 6715477401: "a group whose `after` names a DEFERRED group stays held behind it (deferred means postponed, not done); a group whose `after` names a REFUSED or REFUTED group is released (that predecessor never lands)." Implemented in `roster_lib.gates` (the one predicate: a predecessor in `RELEASING_STAGES` = finished + `refused` + `refuted` no longer gates), `roster_lib.held_behind_deferred` (transitive), `roster_lib.depth_of`, `replan.dependency_graph` and `replan.build_plan` (a held group is emitted unscheduled with `held_behind`, `done` true so every reader that skips a done group skips it), and the readers named under Figures.

## Block 1: class-open (closeout)

Cause: adding `refused` and `deferred` to `CLOSED_STAGES` dropped them from `open_groups`, which `closeout_exempt` and `closeout.roster_blockers` read, so the `resume.host` rule was dead for `refused` and a hosted `deferred` group stopped blocking. Fix: `roster_lib.unfinished_groups` (every group not in `FINISHED_STAGES` = done + `absorbed`), read by `closeout_exempt` and `roster_blockers`. Alternative rejected: reading `groups_of` at each closeout call site duplicates the rule. Closeout therefore behaves as at the merge base for every stage.

Reviewer's harness `evidence/probe_closeout.py` (sha1 123d68927f7c435b15336da810a8dd409433e8f8, verdict/3326), both ends, same fixture, `H` in-progress, `R` hosted by `H`:

| tree | refused | refuted | deferred |
|---|---|---|---|
| 3cf879467 (before) | `['H']` | `['H','R']` | `['H']` |
| this head | `['H','R']` | `['H','R']` | `['H','R']` |
| merge base 20e83746 (control) | `['H','R']` | `['H','R']` | `['H','R']` |

Self-test rows: `closeout.py` "a refused group whose host is still open blocks", the deferred twin, and "a deferred group with no host still blocks" (its null); `roster_lib.py` "a refused or deferred group stays unfinished ... closeout_exempt exempts it only when its host is not open".

## Mutation proof

Mutants applied to the production line, then the self-tests run; each line is the mutant and what it turned red (`$HOME`-local driver `mut2.py`, sha1 not in tree; the `replan.py` ones are the in-file harness).

- `closeout_exempt` reads `open_groups` (`set(unfinished_groups(roster))` -> `set(open_groups(roster))`): `roster_lib.py`, `closeout.py` red.
- `roster_blockers` reads `open_groups`: `closeout.py` red (the hosted refused/deferred rows).
- `RELEASING_STAGES` plus `deferred` (deferred releases): `roster_lib.py` red.
- `RELEASING_STAGES` without `refuted`, then without `refused`: `roster_lib.py` red, each.
- `held_behind_deferred` not transitive (`elif a in held and gates(G[a])` -> `elif False`): `roster_lib.py` red.
- `critical_path` reads every open edge again (`if a in G and gates(G[a])` -> `if a in G`): `roster_lib.py` red.
- `depth_of` reads `is_open` again: `roster_lib.py` red.
- `handover_prompt.ready_next` back to `a not in open_`: `handover_prompt.py` red, two rows ("a group after a deferred group is held", "after a refuted group is released").
- Block 2: `check-ignores-flag` (`if g.get("coordinator") and not g.get("exempt_coordinator")]` -> `if g.get("coordinator")]`), new in-file mutant: KILLED by the new row "--check passes a flagged critical-path start that overlaps a running coordinator group".
- `edge-releases-ruled` (`dependency_graph` back to `if a in open_:`) and `deferred-holds-dependent` (`held = roster_lib.held_behind_deferred(G)` -> `held = {}`), new in-file mutants: both KILLED. The first version of the second targeted `open_ = open_ - set(held)`, which survived (the held branch of the output loop masks it); retargeted to the producing line.
- Earlier mutants (`lane-stem-boundary`, `coordinator-cp-exempt`, `coordinator-cp-flag`, the updated `coordinator-cap`/`cp-first-in-tier`) still KILLED: `python3 tools/plan/replan.py --self-test` prints `self-test: 0 failed` with every mutant killed.

## Null control

- Block 2 fixture: X3 (L, coordinator) runs while CP1 (XL, coordinator, after D) starts flagged; the row asserts `X3.start < CP1.start < X3.finish` so the overlap is real, and its null is the same plan with the flag removed, which `check_plan` refuses with `coordinator cap`. The reviewer's probe `evidence/probe_check.py` gave `[]` at the head and the cap message under the mutant.
- Ruling arms, replan: `deferred` -> dependent and its own dependent `held_behind` the group, `start` null; `refused` -> dependent starts at 0 and is not held; `refuted` -> the group is still scheduled, its dependent released with `after == []`; null: a `queued` predecessor still gates (`after == ["R10-Q"]`, starts later).
- Ruling arms, `roster_lib`: `gates` / `held_behind_deferred` / `depth_of` for `refused`, `refuted`, `done`, `absorbed` (released) against `deferred` (held), and the transitive case.

## Figures

Each command is the instrument; counts are not carried.

- Seam rule for the changed predicates (`CLOSED_STAGES`, `open_groups`, `is_open`, now also `gates`, `unfinished_groups`): `grep -rnE "open_groups|is_open\(|closeout_exempt|roster_blockers|CLOSED_STAGES|DONE_STAGES" tools tests` (null control: it returns `closeout.py`, which the first body's list lacked). Dispositions:
  - `closeout.py` (`roster_blockers`, `step_issues` via `closeout_exempt`): fixed in this diff (Block 1).
  - `plan_table.py` (all five `open_groups` calls), `resume_doc.py` open counts and waves, `handover_prompt.py` `in_flight`, `prune_refs.open_group_ids`, `size_durations.py`, `ci_predict.py`, `carry_audit.py`, `merge_throughput.py`, `roster_sync.py`, `roster_edit.py`: read the open set as work still owed; a refused or deferred group dropped from it is the intended reading (deferred stays owed only through the edge rule and closeout). Self-tests of each: 0 failed.
  - After-edge readers, changed to `roster_lib.gates` so they follow the ruling: `resume_doc.py` "Ready next", `handover_prompt.ready_next`, `plan_page.py` `blk`, `orchestrator_tick.py` `blockers` line; `roster_lib.depth_of`. Pinned only for `handover_prompt.ready_next` (rows above) and `depth_of` (`roster_lib.py`).
  - `roster_lib.critical_path` and the `plan_table.py` mermaid dependency drawing now skip an edge to a refuted group (`gates`); `critical_path` is pinned by the `roster_lib.py` row "critical_path: an edge to a refuted group is released" (mutant: `if a in G and gates(G[a])` -> `if a in G` goes red), the drawing by no row. Not drawn: an edge to a deferred group (the group is not in the open set), display only.
- Block 3 closures, `python3 tools/pr/ci_predict.py --base origin/main`: `no closures, fast, governance or instrument red predicted`. Cause of the red: the new `tests/entities.py` edge runs `orchestrator_tick.py --self-test`, opening four INERT files (`orchestrator_tick.py`, `pr_cap.py`, `budget_raise_gate.py`, `app_approve.sh`). Repair, by the route `INERT_EXCEPT` documents: the four join `INERT_EXCEPT` in `tests/closure.py`, then `./tests/derive_closures.sh --single tests/entities.py` twice (the first recording fails its own "every tracked file is measured or classified" check, since the table does not yet list them; the second is the fixed point and records `rc` 0). Alternatives: classify the reads out of the tick edge (drops the edge that catches the CLOSED_STAGES regression), or `--apply-inert` (it files them under `inert_reads`, which the self-test-reads arm names UNDER-SCOPED for a script whose self-test reads them).
- `tools/pr/prepr.sh --self-test`: `514 passed, 0 failed`; its glob-sibling fixture planted `orchestrator_tick.py` and `pr_cap.py` as INERT siblings, which are no longer INERT, so it now plants `ci_critpath.py` and `plan_audit.py`.
- Self-tests at this head, all `0 failed`: `replan.py`, `roster_lib.py`, `closeout.py`, `orchestrator_tick.py`, `handover_prompt.py`, `resume_doc.py`, `plan_page.py`, `plan_table.py`, `roster_sync.py`, `roster_edit.py`. `python3 tests/entities.py` prints `ALL 2669 ENTITY CHECKS PASSED`; `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Replan before/after figures of the first body (R10-I18N-DE lane, R10-FLY-CLOUD-FRUGAL-OFF done) are unchanged by this round except that a dependent of a deferred group is now held.

## Unpinned sites

The diff's added guards are pinned by the self-test rows above; `prepr.sh` step 6d lists any it finds unpinned and each is named in the Mutation proof section as killed. The `plan_page.py` `blk`, `orchestrator_tick.py` `blockers` and `plan_table.py` drawing edge reads carry no row: Forward-carry.

## Red checks

- **tests / closures** (job 128899105839) at the old head: `INERT READS UNDER-APPROXIMATED` on `tests/entities.py` for `tools/audit/seat/pr_cap.py` and `tools/pr/app_approve.sh`, caused by this diff's tick edge (above); also `tests / closures-autofix` (job 128903614688), which refused because `orchestrator_tick.py` is INERT and read. Cheaper detector: `prepr.sh` step 6d / `ci_predict.py --only self-test-reads`, which names the three reads in about 3 minutes against CI's closures at about 15; it did not run at the old head because that head was pushed without a prepr run after the edge was added. It now runs clean here.
- **gate** at the old head failed because of `tests / closures`; it clears with it.
- Earlier-head reds (`governance / instrument-self-tests`, `pr-contract`) were answered in the first body and are unchanged.

## Forward-carry

- The `plan_page.py` `blk`, tick `blockers` and `plan_table.py` drawing edge reads follow `roster_lib.gates` with no pinning row; they are display text and chart edges with no scheduling effect. Carry: dismissed: display-only, the scheduling and ready-next readers are pinned

## Friction

none
