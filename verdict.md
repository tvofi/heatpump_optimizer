Fix review: merge 43095bdec3bba091bfe1a5a38abf172987e7ceb8

bus-nonce: 2d3fbd912b67a8d177e5e1169b8429b0

## Scope

Round 1, handoff review of R10-OUTSIDE-DISINFECTION-SETPOINT part 2, delta ef579d9ba689..43095bdec3bb (seven commits), body BODY.md at handoff-body/r10-outside-disinfection-setpoint 5b94f57b64f9 (copy: ev/BODY-5b94f57b.md). The body's `## Head` names 43095bdec3bba091bfe1a5a38abf172987e7ceb8, the head measured (ev/HEAD.txt). `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` printed nothing: the contract read is current.

## Evidence

- No pull request exists yet: no review packet, no CI runs and no check runs to read, so no red is owed an answer and `## Red checks: none` is the only state there is; `merge_train.py owed-reds` prints `tests / mutation`, `tests / typing`, `validate / validate-hacs`, none of which has run on this head. The train re-proves on the live checks once the PR opens.
- Mutation proof (fix-review step 1): `python3 tools/audit/seat/r10_disinfection_setpoint_mutants.py` at 43095bde, rc=0: NULL SURVIVED; M1-M10, M12-M20 KILLED (ev/mutants.txt). M11's retirement as equivalent checked on the code: `dhw_cycle_temp` is `max(dhw_setpoint, disinfection)`, so on a cycle at or below the everyday set-point `dhw_hard_max_temp` equals `dhw_max_temp` and the two returns are the same `_bounded` call.
- Failing first: `tests/block_duty.py` at c9258994 printed `4 of 69 BLOCK DUTY CHECKS FAILED`, the four checks the body names (ev/failing-first-c9258994.txt). At 43095bde: `ALL 70 BLOCK DUTY CHECKS PASSED`, `ALL 61 GUARD PIN CHECKS PASSED` (ev/head-suites.txt).
- Reviewer's own mutants (ev/reviewer-mutants.txt): R1 Fix capped at `dhw_max_temp` instead of the hard maximum, killed (3 of 70 block_duty); R3 `_bounded` comparing the ceiling with the raw minimum, killed (1 of 70); R4 the repair floor rounded `nearest` not `up`, survives block_duty and guard_pins but is killed by `tests/features.py` ("#2805: a fractional disinfection floor is written up ...", 1 of 5287, ev/R4-features.txt), which is in the scoped closure; R2 `hi=min(dhw_max_temp, dhw_hard_max_temp)` is equivalent by construction (`dhw_hard_max_temp >= dhw_max_temp`), a null, not a survivor.
- Harness (step 2/3): `dev/audit/harnesses/r10_disinfection_setpoint.py` sha1 6ced0aeb71d5fc00734eaf4098e65e5e665891e8 (the PR's, built by the fixer for this group, disclosed as such in the body; part 1's committed harness extended) copied over a worktree of ef579d9b and run there and at 43095bde, `--grid` and default (ev/grid-base.txt, ev/grid-head.txt, ev/default-base.txt, ev/default-head.txt). RESULT lines re-derived with the body's own greps:
  - RESULT over_limit=1: idle 104 -> 0, disabled 104 -> 0, held 341 -> 341; base by step 0 / 26 / 26 / 26 / 26 at 0.1 / 0.5 / 1 / 2 / 5. Matches.
  - RESULT fix_over=1: held 272 -> 0, idle 272 -> 0, disabled 0 -> 0; held base by step 12 / 56 / 59 / 64 / 81. Matches.
  - RESULT below_floor=1: 0 in every arm at both ends. over=1 (cycle above hard maximum) held 0 at both. Matches.
  - RESULT null control: 80 `null_*` lines IDENTICAL; held arm with fix fields cut IDENTICAL (780 lines); idle and disabled write fields moved on exactly 104 lines each, all `over_limit=1` at the base; idle over_limit=0 base rows 676, 455 on-step (my awk over `everyday/step`). Matches.
  - RESULT default mode: only the 20 `offstep` `repair_none` lines move (61 -> 60, or -> `-` on cycle rows); `repair_own` `-` throughout. Matches.
- Class rule (step 6): the body's two `git grep`s return pump_arbiter.py:1197, 1198, 1228 (and the slot tables at 402, 425 and the reader at 1246-1247, which write nothing) and setpoint_check.py:134 (ev/class-rule.txt); each is dispositioned in the body. The repair's ceiling uses `dhw_hard_max_temp`, which only sits under the floor where the disinfection temperature exceeds 70 or is off-step: `dhw_cycle_temp` is None exactly when `dhw_disinfection_temp` is, so no install with a floor gets the everyday ceiling instead.
- Step 4/5: no golden, no claim file, `VERSION`, manifest or `RELEASE_NOTES.md` touched (ev/untouched.txt), so `env_drift.py --all` has nothing to compare.
- Step 13: `git merge-tree --write-tree origin/main 43095bde` rc=0 at origin/main 289c9b996832 (ev/merge-tree.txt); no conflict.
- Step 14: `python3 tests/structure.py` STRUCTURE RATCHET PASSED (ev/structure.txt); `tools/audit/archscore/score.py --diff ef579d9b` `Architecture score: dS +0.0000 NULL` (ev/archscore.txt). No budget, closure or ledger figure moves except four new mutation-pin files, each a site the diff writes and a reviewer-confirmed kill (M19/M20/CMP_BOUND pins via block_duty).
- Not re-run: the scoped gate (`24 TEST SCRIPT(S) PASSED` at ec29e0dd) and `tests/mutation_table.py --pin-killed`; cited from the body, CI re-proves both once the PR opens. `tests/features.py` was run only under R4, not clean at head.
- Head unchanged at review end: the body's head is 43095bde, the one measured.

## Findings

- Out of scope: `_bounded`'s new rule (a caller's ceiling under the entity's minimum on its step is dropped) also reaches the two space-set-point callers that pass `hi=` (pump_arbiter.py:890 flow-level write with `hi=heat_c`, :976 feedback write), which the body's class dispositions do not list: where the heat ceiling is below the space entity's own minimum, the base wrote under the entity's range and the head writes that minimum, the value `_bounded`'s contract (inside the entity's range) already promised; tests/features.py's L2 check pins the same rule. Carry: dismissed: the head keeps a write the base sent outside the entity's accepted range inside it, consistent with the contract the body states

## Friction

none
