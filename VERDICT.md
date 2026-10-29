Fix review: merge b091232ebfc12714f85772d2d763fccaa5b604aa

bus-nonce: ed7e0f85f347e88c12959fadbd71c280

## Round

Round 1 of this fix review for PR #2963 (R10-ADVISOR-WHATIF), measured at head b091232ebfc12714f85772d2d763fccaa5b604aa from detached worktrees of the head and of the merge base ce5940c0d1d8f611a818d53e7fffcafb48b356c1. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the role contract is current.

## Findings

- `plan_slots.py:69` and `plan_slots.py:76` CMP_BOUND (the two `> 1e-9` guards, `>` to `>=`) survive and nothing triages them. The body says "at most one of the two had a pin before the move". In fact neither did: the base pin `_plan_slots.close CMP_BOUND 7b589d80` is the `i < len(other_heating)` line, now `plan_slots.close CMP_BOUND b750624a`. The lines were moved verbatim, so these are the base's survivors carried over, not new ones. Only a total of exactly 1e-9 kWh separates the two mutants. Carry: dismissed: they were survivors before the move, only an exact float tolerance separates them, and the body names them under Unpinned sites
- In the body's `## Red checks` section, a stale template line follows the nightly-status answer: "none. No PR exists yet ... CI has not run." It contradicts the line above it. Carry: dismissed: body wording only; the nightly-status line answers the one red check and pr-contract passed
- `optimizer.py` re-imports `channel_heating_steps` only as a re-export now. Two callers still reach the moved names through it: `tests/guard_pins.py:708` imports both names from `optimizer`, and `dev/audit/harnesses/r10_band_census.py:83` reads `opt.CHANNEL_ACTIVE_KW`. Carry: dismissed: the re-export keeps every caller resolving, as the body states, and retiring the shim is not this size-S group's work
- Item (1), the Plan page's what-if panel figure that moves with the start state, is left undone by design and needs the owner's decision or a designer seat. #2257 is open and its body names the what-if delta. Carry: #2257

## Evidence

- Head: the PR head is still b091232ebfc12714f85772d2d763fccaa5b604aa when re-read at 19:36Z. It is one delivery-row commit on top of the automatic merge 337758bfb. That merge's tree equals `git merge-tree --write-tree ce5940c0d badd0b114` (ede09a3b…), so it contains no hand resolution. `git diff 337758bfb b091232eb` touches only `dev/programme/delivery/2963.md`.
- Merge with main: `git merge-tree --write-tree origin/main b091232eb` returns rc=0, with origin/main at ce5940c0d (ev/merge_tree.txt).
- Move fidelity: the base `_plan_slots`, dedented and renamed, is byte-identical to `plan_slots.plan_slots`. `CHANNEL_ACTIVE_KW` and `channel_heating_steps` are byte-identical between base `optimizer.py` and head `thermal_model.py` (ev/moved_body_diff.txt).
- Mutation proof (step 1), run by me at the head:
  - m1, the ruling's mutant (`slot["shared_kwh"] = round(shared, 3)` replaced by `pass`): `2 of 4574 FEATURE CHECKS FAILED`. The two failures are the checks the body names.
  - The same m1 mutant drops `shared_kwh` from the `plan_view.py` payload's first space and DHW slots (ev/head_pv.txt against ev/m1_pv.txt). `plan_view.py` itself still exits 0, so this is a capture comparison, not a failing check, which matches the body's wording.
  - m2 (GUARD_OFF on `if start_idx is None:`, ledger `9d986aaa`): features.py rc=1.
  - m3 (`kw > CHANNEL_ACTIVE_KW` changed to `>=` in `thermal_model.py`, ledger CMP_BOUND d964e804): guard_pins.py `1 of 61 GUARD PIN CHECKS FAILED`, against `ALL 61 GUARD PIN CHECKS PASSED` at the head.
  - Unmutated head: `ALL 4574 FEATURE CHECKS PASSED`.
- Ledger accounting: 11 base pins on the old scopes (6 coordinator `_plan_slots*`, 5 optimizer `channel_heating_steps`/CONST) were deleted or renamed. The head has 19 pins: 14 under `plan_slots.py/` and 5 under `thermal_model.py/`. That matches the body's eleven and nineteen. I did not re-drive every pin. I re-drove three (m1, m2, m3), and CI `tests / mutation` concluded success on this head.
- Finder's harness (step 2): I ran `r10_advisor_residue.py whatif` at the base ce5940c0d and at the head. The two outputs are byte-identical (`cmp` exit 0) and both end rc=0.
  - `RESULT whatif rows 24 plan_moves_by_start 24 held_moves_by_start 0`
  - `RESULT whatif caps rows 12 spread_by_start mean plan 45.7 settled 10.1; figures reading a saving (< -1) plan 18/36 settled 2/36`
  - The null row reads `00:00 target_plus_1 ... spread 144.7 | held ... spread 0.00`.
  - The varying-row settled values read +24.6/+24.7/+24.7 and -25.5/-21.7/-25.0.
  - Every figure the body quotes from this harness re-derives. The fixer measured against base 88c6ad5bb, and I measured against ce5940c0d: the output is the same at both.
- Null control (step 3): `tests/plan_view.py` payloads at the base and at the head compare as sorted JSON `whole identical True`. The behaviour-identical claim holds. I did not re-run the archscore whitespace null (`dS +0.0000 NULL`).
- Figures I re-derived at the head:
  - `Architecture score: dS +0.0169 IMPROVES`, `coord_footprint 2409 -> 2381`
  - `STRUCTURE RATCHET PASSED`. The budget diff only lowers values: class_excess_loc 17814->17732, max_class_loc 8155->8073, seam_cut_total 423->422.
  - `MODE: SCOPED -- 29 script(s) run, 4 scoped out.`
  - `CI PREDICT: no closures, fast, wave-script or instrument red predicted against ce5940c0d1d8`
- A figure I could not re-derive: my local `tests/entities.py` run hit my 230 s timeout under parallel load, so I could not re-derive `ALL 2470 ENTITY CHECKS PASSED` myself. I cite the CI `tests / fast (3.14)` lane instead, which concluded success on this head.
- Claims and version (steps 4 and 5): the diff leaves `VERSION`, `manifest.json`, `RELEASE_NOTES.md` and both claim files untouched. CI `governance / env-matrix` is green, and I did not re-run `env_drift.py --all`.
- Metric earned (step 14): the structure and archscore movements come from `_plan_slots` leaving the class. Moving the body back restores the 82 lines, and the fixer's whitespace null reads flat. The `layer_violations` hold at 13 is earned by relocating `channel_heating_steps`, a verbatim move into a rank-0 module beside `planned_draws_run`. Neither movement is shaped like gaming.
- Class (step 6): the body names its enumeration rule, archscore's coord_footprint charge list, and dispositions the other static members as not this brief's. The layer seam it opened enumerates 13 to 13.
- Architecture (step 15): the new pure module imports only `payload.PlanSlot` and `thermal_model`, with no Home Assistant or solver reach. The four call sites are unchanged apart from the name.
- CI on b091232eb (step 11), from the check-runs API at 19:36Z:
  - Concluded success: fast (3.14), closures, coverage, mutation, arch-instrument, arch-score, instrument-self-tests, env-matrix, typing, replay, browser, closure-scope, briefs, policy-docs, wave-script, budget-raise-gate, delivery-status, hassfest, validate-hacs, all CodeQL analyses, lane-proofs, graders-head-copy and coverage-ratchet.
  - `pr-contract` (id 123686230262) started after the last red concluded and finished success.
  - Two `prelude` runs were still in_progress.
  - The only red is `tests / nightly-status`. It is not a required check and does not block. Its log grades main's Nightly `slow` lane (run 40835853528), and this diff touches none of the workflow, plan or HANDOVER files it reads, so it is not this PR's.
- I did not read the mutation lane's log body. Its green conclusion stands beside my three targeted kills.
