Fix review: blocked 8f073db70d18895d0962924ac8da72647a02090a mutation-vacuous: replan.build_plan open_ = open_ - set(held) and roster_lib.held_behind_deferred gates(G[a]) conjunct survive, non-equivalent

bus-nonce: 51591997d1813a7dfaa2ba1745825129

## Block

Round 2 (the previous block was at b59abf37). Head measured: 8f073db70d18895d0962924ac8da72647a02090a.

Two added production lines that the ruling depends on fail no check when I mutate them, and each mutant changes behaviour (step 1):

1. `tools/plan/replan.py` `build_plan`: `open_ = open_ - set(held)` -> `open_ = open_`. The replan self-test still prints `self-test: 0 failed`. The body says the held branch of the output loop masks this mutant. My probe (`ev/probe_held.py`, my own instrument) shows it does not: roster `R10-P` deferred, `R10-Q` (XL, after `R10-P`), `R10-U` (S), slots=1. At the head `R10-U` starts at `2026-01-05T00:00:00Z` and `check_plan` returns `[]`. Under the mutant the held `R10-Q` takes the slot in the simulation, `R10-U` starts at `2026-01-05T08:00:00Z`, and `check_plan` refuses with `stamp cadence ...` and `summary: open-group count disagrees ...`. At slots=6 it refuses too (`ev/probe-held-head.txt`, `ev/probe-held-mutant.txt`). Carry: R10-FLY-REPLAN-DEFECTS
2. `tools/audit/seat/roster_lib.py` `held_behind_deferred`: `elif a in held and gates(G[a]):` -> `elif a in held:`. `roster_lib.py` and `replan.py` self-tests stay green. Fixture: `P` deferred, `R` refuted after `P`, `D` after `R`. The head returns `{'R': 'P'}`, so `D` is released, as the ruling requires for a refuted predecessor. The mutant returns `{'R': 'P', 'D': 'P'}` and holds `D`. Carry: R10-FLY-REPLAN-DEFECTS

## Findings

- Mutant 1 above: `open_ = open_ - set(held)` needs a row that fails without it. For example, a deferred predecessor whose held dependent would otherwise take a contended slot, asserting the free group's start and `check_plan(...) == []`. The body's statement that it is masked should be corrected. Carry: R10-FLY-REPLAN-DEFECTS
- Mutant 2 above: the `gates(G[a])` conjunct in `held_behind_deferred` needs a row for a refuted (or other releasing) group held behind a deferred one, with its dependent released. Carry: R10-FLY-REPLAN-DEFECTS
- `tools/audit/seat/resume_doc.py` "Ready next" (`if not any(roster_lib.gates(G[a]) for a in deps if a in G):` reverted to `if all(a not in open_ for a in deps):`) survives `resume_doc.py --self-test`. It is a ready-next reader, the twin of `handover_prompt.ready_next`. The body's Unpinned-sites list does not name it, and the Forward-carry dismissal reads "the scheduling and ready-next readers are pinned", which is false for this one. It needs a pin or a disposition. Carry: R10-FLY-REPLAN-DEFECTS
- `orchestrator_tick.py` `blockers` and `plan_page.py` `blk` survive their mutants (`ev/mutants-a.txt`). Both are disclosed in the body and dismissed as display-only. I accept that disposition and do not block on them. Carry: dismissed: disclosed and dispositioned display-only in the PR body's Forward-carry

## Evidence

- RESULT self-tests at head, all 0 failed: roster_lib 75, closeout 38, handover_prompt 20, resume_doc 15, plan_page 67, plan_table 26, orchestrator_tick 283, replan `self-test: 0 failed` (`ev/selftests.txt`, `ev/replan-selftest.txt`).
- RESULT in-file replan mutants, all killed by the in-file harness at head: coordinator-cap, cp-first-in-tier, lane-stem-boundary, coordinator-cp-exempt, coordinator-cp-flag, check-ignores-flag, edge-releases-ruled, deferred-holds-dependent.
- RESULT my mutants (`ev/mut.py`, my own driver, `ev/mutants-a.txt`, `ev/mutants-b.txt`):
  - Killed: closed-drops-refused-deferred, closeout_exempt-open, roster_blockers-open, unfinished-reads-closed, releasing-plus-deferred, held-not-transitive, depth-is_open, critpath-all, ready_next-revert, tick-skip-deferred.
  - Survived: held-ignores-gates, resume_doc-ready-revert, tick-blockers-open, plan_page-blk-done, replan-open-minus-held.
- Block 1 (closeout class-open) answer verified: the closeout and roster_lib rows go red under the `open_groups` reverts.
- The tests/entities.py edge: tick-skip-deferred turns `orchestrator_tick.py --self-test` red (283 checks, 1 failed), which the entities check keys on (rc and ", 0 failed").
- `git merge-tree --write-tree origin/main 8f073db7`: rc 0, `LEDGER-MERGE: resolved tests/closures.json` (`ev/merge-tree.txt`).
- VERSION, manifest, RELEASE_NOTES.md, both claim files and structure_budgets.json are untouched (three-dot, empty).
- Figures not re-derived: the count from `prepr.sh --self-test` and `ALL 2669 ENTITY CHECKS PASSED` are left to CI's heavy runs, per step 11.
- CI: `gate` red at render was a deferral. Its log reads `FAIL run(s) [42580173777] at this head are still being judged; their gate decides`, which is not a defect. `merge_train.py classify 8f073db7 --pr 3326` then went from WAIT to exit 0 at 08:15:21Z: `GREEN 8f073db70d18895d0962924ac8da72647a02090a pending: none red: none` (`ev/classify.txt`, `ev/classify-log.txt`). No required check is red at this head, so step 11 owes nothing. The block does not depend on CI.
- No finder's harness is named in the packet: the defects come from the replan study. The probes and mutant driver here are my own instruments.
