Fix review: merge 8800ed7c6f7006ddf75898f79ac7bc22f5e11467

bus-nonce: none-issued (this dispatch named no nonce; published to verdict/3838, not to a probe ref)
pending-ci: tests / fast (3.14), tests / mutation-pins (1-4), gate

Round 3. This is a delta review of `git diff 48d28b55eb 8800ed7c6f`, ruled delta-only. The round-2 draft verdict at 48d28b55 is at `probe/rev-3838-dc0e98e6` (25575a96). `review_carry.py 48d28b55eb 8800ed7c6f` prints FRESH-REVIEW because the branch's own commit `c03b640cd6` changes content. Main merges `9d3d6d129b` and `665c47b391` (to merge base `eaaaf24e5b`) are main's own changes.

Note: refactor-in-move: `c03b640cd6` is described as a move, but it also changes behaviour. `raised_floor` (rooms.py:327) no longer clips `margins` at zero; the caller now pads and clips it first. The unlifted call (optimizer.py:4883) passes `margins - _padded_nonneg(room_lifts)` with no clip, where the old code clipped that difference at 0. I checked the old and new arithmetic against each other (`evidence/equiv.py`):
- Inputs shaped like `floor_limits` output (`min_temp_margins` = clipped base + lift): 0 of 20000 differ.
- Inputs with no lift: 0 of 20000 differ.
- Inputs where `room_lifts` exceeds `min_temp_margins`: 20000 of 20000 differ, and the attributed lift comes out larger.
`floor_limits` is the only producer of both arguments and always returns margins + lift, so no production path reaches the differing case. No block: the code is equivalent on its reachable inputs. A future direct `SolveLimits(room_lifts=...)` caller would get the unclipped attribution. Carry: dismissed: no stage brief constrains it; the docstring now says `margins` is "already padded", which states the caller's duty.
Note: body-garbled: the round-2 note still stands. The `## What it does` lead paragraph is spliced ("...measured under `C1, the review's mutant ... ## Null control`)."). `## What it does` also still names `_raised_floor` and `_mark_room_floor`, which are now `rooms.raised_floor` and `rooms.mark_room_floor`. The `## Red checks` and `## Unpinned sites` sections do name the move. Carry: dismissed: paperwork on this PR's body.

## Prior findings

- Round 1's `mutation-vacuous` block: resolved at round 2, and the round-2 checks still pass here. P2 block unmutated: `ALL 26 FEATURES BLOCK PASSED`.
- Round 2's body-garbled note: not resolved; repeated above.
- Round 2's `features_block.py --emit-prelude` friction (it misses `import asyncio as _asyncio`): reproduced. This review added the import to `evidence/P2.py` by hand. The body already routes it to round-end triage.

## Evidence

- Head `8800ed7c6f7006ddf75898f79ac7bc22f5e11467`. It is the live PR head (re-read before publishing), and both the handoff body `abeb1a33` and the live body name it under `## Head`. The handoff-body `Code:` trailer names `c03b640cd6`, which 8800ed7c merges.
- Role contracts are current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- `git merge-tree --write-tree origin/main 8800ed7c` exits 0 against origin/main `1207ee13b0`.
- Production delta: `c03b640cd6` only. It moves `_raised_floor` and `_mark_room_floor` from optimizer.py to `rooms.raised_floor` and `rooms.mark_room_floor`, and moves the margin padding to the caller (see the Note).
- Mutation proof at the new location (`evidence/run.sh`, `evidence/mutants.txt`). Unmutated: P2 `ALL 26`, 3B `ALL 8`, `tests/manual_plan.py` `ALL 132`, rc 0.
  - M1, `rooms.raised_floor` CLAMP_DROP (pin `raised_floor.CLAMP_DROP.7ed78c9c`): 3B `1 of 8 FEATURES BLOCK FAILED`, failing "the solve's room lifts are the held floor less the floor without the lift". The pin names `tests/features.py`, and features.py kills it.
  - M2, `rooms.mark_room_floor` GUARD_OFF (pin `mark_room_floor.GUARD_OFF.82f4b644`): `tests/manual_plan.py` rc 1 and 3B rc 1 (`TypeError`). The pin names `tests/manual_plan.py`, and manual_plan.py kills it.
  - The tree was restored (`git status` is clean).
- Structure ratchet, no raise: `python3 tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED`. Against merge base `eaaaf24e5b`, `tests/structure_budgets.json` moves two rows, both down: `class_excess_loc` 17317 -> 17301 and `module_excess_loc` 21779 -> 21770. `recorded_at` also changes. No row rises.
- Is the `module_excess_loc` drop earned? The mechanism is moving two room-lift helpers out of optimizer.py (6768 lines) into rooms.py (377 lines, under the limit). Without the move, `tests / fast` at `9d3d6d129b` measured 21822 (+43 over budget). The move is cohesive: the helpers serve the room lift that `rooms.floor_limits` computes. `archscore --diff 48d28b55eb` reads `dS +0.0280 IMPROVES`, and `--diff eaaaf24e5b` (the merge base) reads `dS +0.0000 NULL`. I do not read this as gaming.
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden` are untouched against the merge base.
- No harness change in the delta. The finder's harness `dev/audit/harnesses/room_lift_solve.py` was not re-run, because the production change is equivalent on its inputs (`evidence/equiv.txt`).

## Checks at 8800ed7c (run 45054354128 and others)

- Success: arch-score, budget-raise-gate, closures, coverage, browser, typing, codeql, policy-docs, wave-script, env-matrix.
- Pending: `tests / fast (3.14)` and `mutation-pins (1-4)`.
- `tests / mutation`: red with `ADDED UNPINNED` sites, including the moved `rooms.py:343-355` sites. The body answers these under `## Unpinned sites` and `## Red checks`; the pins are left to `mutation-pins` and `mutation-autofix`.
- `gate`: red with "run(s) [45054354128] at this head are still being judged" (timing).
- Note: root-cause-unanswered: `tests / replay` (cancelled at 30 min) and `governance / instrument-self-tests` (cancelled) at this head. The body answers both causes only at earlier heads.
