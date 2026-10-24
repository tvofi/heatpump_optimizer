Fix review: blocked a126c8b3fa820bbac01f53f8e66c99a278af7c1e mutation-vacuous: _propagated_slab shared=False and space_served=True survive tests/features.py (also carry-missing, see Block)

bus-nonce: 8b423cb52f5dedffd3472bb47aa5ca36

This is review round 2 for #2712; the first `Fix review:` on the PR blocked 5fb0a083b. The brief calls this fixer round r4. I measured head a126c8b3fa820bbac01f53f8e66c99a278af7c1e, and it was still the PR head when this was written (`ev/HEAD.txt`). I read fix-review.md from origin/main; `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty. I worked from detached worktrees at the head and ran every mutant on a fresh worktree.

## Block

- **mutation-vacuous (step 1): both survivors that round 1 of review blocked on still survive.** The body claims a resistive element on the meter falls back to the plan's trajectory. Nothing at the coordinator pins that claim, and nothing pins the space-not-served case either:
  - M3: `shared=coord._immersion_active or signals.electric_heat.resistive_heat` -> `shared=False` leaves `ALL 4367 FEATURE CHECKS PASSED`, rc=0 (`ev/M3_shared_false.*`).
  - M4: `space_served=signals.space_heat or not signals.mode_observed` -> `space_served=True` leaves `ALL 4367 FEATURE CHECKS PASSED`, rc=0 (`ev/M4_spaceserved_true.*`).

  With M3 in place, an immersion element's draw is booked into the slab as heat-pump space heat, which is this finding's own bias class. With M4 in place, a DHW-only interval heats the slab. This round's body does not mention either mutant. They are not among the six ratchet sites, because the ratchet's inventory does not mutate call arguments. Owed: a coordinator-level value check for an immersion or resistive interval and one for a mode not serving rooms, each killing its mutant. Owed by this PR (fixer re-cut).
- **carry-missing (step 10): three `Carry:` markers name stages that hold no carry from this PR.** Evidence: `ev/carries.txt`, read on `handoff/audit-r10-roster` at 4937d60fe and on origin/main.
  - `## Forward-carry` line 3 (the DP optimality lead) names `R10-COP-PARTLOAD`, which holds 0 carries from this PR.
  - Line 4 (the open-loop `dhw_temp_trajectory` tank seed) names `R10-HEAT-METER`, which holds 0.
  - Both texts sit under `R10-BUFFER-STORE` instead, written for body a7a683d1. That is the same mismatch round 1 of review blocked on, and it is unrepaired.
  - The `## Friction` item `R10-PREPR-UNPINNED-RED` names `R10-ORCH-MACHINERY`. That group's stage is `absorbed`; its note says the concerns moved to R10-ORCH-* groups. It holds no carry for this item, and no live group holds it either.
  - The body names no roster-branch SHA (`finding-propagation.md` Enforcement).

  Repair: point the line 3 and line 4 markers at R10-BUFFER-STORE, or append them to the named groups. Carry the friction item to a live group, for example R10-FLOW-JIDOKA, which owns prepr's mutation-red line (P67). Then name the roster SHA in the body.

## Findings

- `tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check` prints `5 routed, 0 unrouted, 0 bad destination(s)` for this body. That passes `Carry: R10-ORCH-MACHINERY`, a group at stage `absorbed`, which `finding-propagation.md` says is refused ("a destination gone or done"). It also never checks that the named group holds the text. Carry: R10-FLY-CARRY-DISPOSITION
- The `killed_by` reasons this round recorded say each mutant "took tests/features.py from rc=0 failed=0 to rc=1 failed=2", and the body repeats it. At this head every one of the five sites gives `1 of 4367 FEATURE CHECKS FAILED`; only M1 gives 3. The kill is real either way, but the recorded `failed=2` figure does not re-derive here. Carry: R10-DEMAND-OVERBOOK
- `fixer.md` "Past three rounds, re-cut rather than repair": the brief names this r4. The body still describes itself as a "repair round" and keeps earlier-round history: mutation proof at df2737ed4, figures at f3ca049bf/65d37a7cb, red checks at 398daa3e5. A re-cut body was owed at the fourth round. Carry: R10-DEMAND-OVERBOOK
- The UX-HEALTH carry on the roster quotes `nometer_half scale 1.828, plan/deliv 1.936`, but the current body and round 1's re-measure give 1.858 and 1.908. The carry names the harness to re-measure with, so the stage can re-derive the numbers, but the copies disagree. Carry: R10-UX-HEALTH

## Evidence

- RESULT mutation (step 1), at head a126c8b3f, `PYTHONPATH=tests/hastub python3 tests/features.py`; full lines in `ev/mutants_summary.txt`, failing check names in `ev/*.fails.txt`:
  - unmutated: `ALL 4367 FEATURE CHECKS PASSED` rc=0. The body's 4367 reproduces.
  - M1 (`if False and kw is not None ...`): rc=1, 3 failed, the three `#2499` slab checks the body names.
  - `draw_range.py running_kw CMP_BOUND` (`>` -> `>=`): rc=1. Failed: `#2499: a draw at the running floor is standby, not heat`.
  - `running_kw CLAMP_DROP` (the floor kept at `RUNNING_FLOOR_KW`): rc=1. Failed: `a learned idle draw above the fixed floor raises it to IDLE_MARGIN times the idle draw`.
  - `_propagated_slab CMP_BOUND` lower bound (`0.0 <= dt_h`): rc=1. Failed: `a zero or negative gap replays nothing; the slab follows the plan`.
  - `_propagated_slab CMP_BOUND` upper bound (`dt_h < MAX`): rc=1. Failed: `a gap of exactly the sample window still advances the slab ...`.
  - M5, cap removed: rc=1, the same check fails.
  - `_track_dhw GUARD_OFF` (`if False:`) and `_track_dhw RETURN_DEL` (`pass`): rc=1 each. Failed: `a tank reading reaches the DHW learner, and its freeze reason the coordinator; no reading reaches neither`.
  - Null control, a comment-only line above `_propagated_slab`: rc=0, all 4367 passed.

  So each of the five named sites is killed by the named check, and the null survives.
- Coordinator's conflict ruling, checked against the commits:
  - Which side named which script is the reverse of the brief. Bot head a717ded9 names `tests/entities.py`, recorded against 2636ce9e. Handoff 65d37a7cb names `tests/features.py`, recorded against 4a00a3f0.
  - Merge cb9ef4223 kept the handoff's version, `tests/features.py`, and the head carries it.
  - Recomputing that merge with `git merge-tree` differs from cb9ef4223 only in that conflicted file. cb9ef4223 differs from 65d37a7cb only by `dev/programme/delivery/2712.md`, which came from the bot side.
  - 31b8dbecd and a126c8b3f reproduce exactly from their parents. No other file was changed by hand (`ev/merge.txt`).
- `tests/entities.py` against the CMP_BOUND mutant: rc=1, `3 of 2425 ENTITY CHECKS FAILED` against 2 on the unmutated head. That is not a kill of the behaviour. The extra failure is the mutation-table self-test `--anchor re-drives one site ... (R9-F10.13)`, which refuses because "the ledger disagrees with the deterministic inventory" once the pinned source line changes (`ev/CMPB_running_entities.fails.txt`). The bot's entities.py pin was therefore an instrument artifact, and keeping the handoff's `tests/features.py` pin, a real value kill, was right.
- `tests/entities.py` unmutated at the head: `2 of 2425` fail, `gate-sweep.yml: on CI's completion ...` and `graders-head-copy's delivery_status step ...`. These are the two the body attributes to the seat environment. CI's `tests / graders-head-copy` is green on this head.
- Head (step 7): the body's `## Head` says a126c8b3f merges code head cb9ef4223 and then origin/main c176ee55d, and the commit graph matches. The identity rules the body quotes print nothing, and 65d37a7cb..a126c8b3f changes no production, `tests/features.py` or golden file (`ev/rules.txt`). The figures carried from 4a00a3f05/f3ca049bf/65d37a7cb therefore describe this tree. I did not re-run the harness this round. Round 1 of review re-ran it at both ends: directions reproduced and nulls held, with exact values verified as directions only. Production is unchanged since then.
- Versions and claims (steps 4, 5): `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched against merge base c176ee55d.
- Structure and architecture: `tests/structure.py` prints `STRUCTURE RATCHET PASSED`. Every metric `structure_budgets.json` moves goes down: class_excess_loc -2, duplication_copies -1, max_class_loc -24, seam_cut_total -2. `score.py --diff c176ee55d HEAD` prints `dS +0.3249 WORSENS (inadmissible: coord_footprint 2463->2465)`; the body quotes dS +0.3249 and explains the +2 under `## Architecture score`. `arch-score` is green on this head (`ev/structure_arch.txt`).
- Class (step 6): the rule `grep -n "_open_loop_plan_value("` returns the definition, the slab call at coordinator.py:1012 (closed here) and the tank seed at coordinator.py:6369 (dispositioned in the body). That matches the body.
- Merge (step 13): `git merge-tree --write-tree origin/main a126c8b3f` exits 0 at main c6ef25a65. Its stderr is `LEDGER-MERGE: resolved tests/closures.json`, with no claim-file conflict.
- CI on this head (step 11; `ev/ci_checkruns.txt`): no check has concluded red. `tests / mutation` and `tests / arch-instrument` were still in progress and `pr-contract` had not reported when this was written. The earlier heads' reds on `tests / mutation` and `pr-contract` (398daa3e5, 5fb0a083b, a717ded9) are named and answered under the body's `## Red checks`. The red-check trigger cannot be judged final for this head until its workflows conclude.
- Harness (step 9): `dev/audit/harnesses/r10_demand_overbook.py` is the fixer's own instrument, landed by this PR, and no finder harness was committed. Round 1 of review recorded the same; the body states it.
