Fix review: blocked d7029ade34c87eb0baaad0313a90d352edb99f2f tests-red: tests/entities.py fails the #1218 selection-cost note, the merged closures derive 184 of the 561 pairs and tests/deployment_shape.py still says 182

bus-nonce: e53823c3aee1358b3b7b83bdadcf0a90

Delta round over the reviewed head `8800ed7c6f7006ddf75898f79ac7bc22f5e11467`. Five verdicts on this PR come before it, at `6ef32c22`, `48d28b55`, `8800ed7c` (archive and bus) and `9516fcc5`, so this is round 5 or later. From the fourth round, fix-review.md says a re-cut is owed. The packet's `## Review scope` line reads `full`, because `verdict/3838` names `9516fcc5`, not `8800ed7c`. Per the orchestrator's delta ruling, I reviewed `git diff 8800ed7c6f70 d7029ade34c8` and the findings of the latest verdict, `blocked 9516fcc5 architecture-unsound`. `9516fcc5` is `8800ed7c` plus the bot's pin commit.

## Block

- **tests-red (C8: a head still red takes no merge verdict).** `classify` reads `RED d7029ade34c87eb0baaad0313a90d352edb99f2f pending: none red: gate` (`ev/classify.log`). The `gate` job (139155188742) prints one line, `FAIL tests / fast (3.14): failure (this run)`. `tests / fast (3.14)` (job 139103666783) ends with `1 TEST SCRIPT(S) FAILED`.
  - I reproduced the failure at this head. `python3 tests/entities.py` exits 1 with `1 of 2762 ENTITY CHECKS FAILED` (`ev/entities_head_local.txt`, `ev/entities_rc.txt`). The one real failure is `FAIL and the lane's docstring records those measured numbers as the selection-cost note (#1218)  [... 184 of 561 pairs at >= 0.80 ...; missing markers -> ['184 of the 561']]`. The other `FAIL` lines in that file are the script's own null-control fixtures, inside checks that pass.
  - Cause: this PR's diff. I re-derived the pair count with entities.py's own predicate (`ev/pairs.py`, `ev/pairs.txt`):
    - At the merge base `b4a8bbd5` and at origin/main it is `182 of 561`.
    - The PR's `tests/closures.json` adds `comfort_floor.py` to 27 closures and `cycle_lane.py`'s closure. Once merged with main's 34 scripts, it gives `184 of 561`. This is already true at `90702254f2`, the merge of `f52e700df1`, and at every later head.
    - The PR updated the docstring's `all 122 files` but not its `182 of the 561 script pairs` (`tests/deployment_shape.py:60`).
  - Repair: set the pair count in `tests/deployment_shape.py`'s #1218 note to the derived `184 of the 561`, adding a dated clause in the paragraph's style, and re-run `tests/entities.py`. A docstring edit is a test-tree change; the production delta is sound (below).

## Findings

- Note: root-cause-unanswered: `tests / fast (3.14)` (owed set). The body's `## Red checks` answers an earlier `fast` red (the structure ratchet at `271f2f1f85`), not this one. Its `## Head` says `ci_predict.py` predicted no `fast` red at `bed836b449` and at `1a73c6a6`, but `tests/entities.py` fails at both trees. `ci_predict.py` does not run the selection-cost check after a closures merge. That check is the cheapest detector short of entities.py's full run, which takes 584 s in CI. Carry: dismissed: the fixer answers it in the body with the repair above; the route is the fixer's own `## Red checks`
- Residual: mutant K8, `comfort_floor.raised_floor` taking `floors` without the `[:n_steps]` cut, survives the 3B block, the `#224` comfort-envelope block and `tests/edge.py` (`ev/mutants_out.txt`, `ev/mutants_edge.txt`). The cut is carried byte-for-byte from the base's `f[:n_steps]` in `_build_comfort_bounds`. The production callers pass `_mold_floor_series(horizon.outdoor_temps)` (`coordinator.py:6295`, `:11301`), and no test hands a mold series longer than the horizon. Carry: dismissed: pre-existing guard moved unchanged, its survival is not this PR's behaviour

## Prior findings

- Round at `9516fcc5`, `architecture-unsound` (the helpers moved into `rooms.py`): resolved.
  - `raised_floor` and `mark_room_floor` now live in the new `custom_components/heatpump_optimizer/comfort_floor.py`. It imports only `numpy` and `payload`'s two reason codes. This is the block's own second repair ("a small new module owned by the bound build").
  - `git grep -nE "\b(raised_floor|mark_room_floor)\(" -- custom_components | grep -v "def "` returns three lines, all in `optimizer.py` (`ev/callers.txt`).
  - `rooms.py`'s own diff is now only `floor_limits` and `FloorLimits`.
  - The body raises the placement as a departure from the note.
- Same verdict, the residual (the clip at zero on the unlifted margins): resolved. The outer `_padded_nonneg` is back on `margins - lifts`. My mutant O3, which removes it, is killed by the 3B block: `FAIL ... the room lifts never exceed the margins that carry them ...`.

## Evidence

- Head `d7029ade34c87eb0baaad0313a90d352edb99f2f` (`ev/HEAD.txt`): re-read from `refs/pull/3838/head` before writing, unmoved. The body's `## Head` names it.
- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty (`ev/roles_drift.txt`).
- Merges with main: `git merge-tree --write-tree origin/main d7029ade34c8` rc 0 at origin/main `bb6377b4da` (`ev/merge_tree.txt`).
- Delta: `git log --first-parent 8800ed7c..d7029ade` holds one bot pin, three bot main merges and two hand merges. The production delta in the PR's own three-dot diff is `comfort_floor.py` (new), `optimizer.py` (the two imports, plus the bound build padding the margins before `raised_floor` and clipping the unlifted margins) and `rooms.py` (the helpers removed).
  - Production widening (step 12): none. The moved arithmetic is the only reviewed code the delta touches, and the mutants below cover it.
- Mutation proof, in a detached worktree at the head; the tree was restored after each mutant (`git status: 0 modified`). Scripts are `ev/mut.sh` and `ev/mutants.py`. Detectors are the 3B block and the `#224` comfort-envelope block through `features_block.py` with emitted preludes, plus `tests/edge.py`.
  - Unmutated: 3B `ALL 12 FEATURES BLOCK PASSED`, `#224` `ALL 8 FEATURES BLOCK PASSED`, `edge` rc 0.
  - Killed by 3B:
    - K1: margin add.
    - K2: ceiling clip.
    - K3: mold maximum.
    - K4: 0.15 to 0.5.
    - K5: `- room_lifts[i]` dropped.
    - K6: `room_temps[i + 1]` unguarded (Traceback).
    - K7: `room_temps[i]`.
    - O1: the margins unpadded.
    - O2: the unlifted build without the lift.
    - O3: the unlifted margins unclipped.
    - O4: a lift longer than the horizon not cut (Traceback).
  - Killed by `tests/edge.py`:
    - O5: `mark_room_floor` handed None.
    - O6: `_build_comfort_bounds` handed no `room_lifts`.
  - K8 survives every detector (under Findings).
  - The body's K1 to K4 are re-derived by my K6, O1, O3 and O4.
  - The body's `ALL 11 FEATURES BLOCK PASSED` is at `bed836b449`. At this head the block reads 12, because main's #3871 section now follows the 3B section and the start-only marker runs to the end of the file. It is not a figure this delta moves.
- Structure: `python3 tests/structure.py` `STRUCTURE RATCHET PASSED`, `ok module_excess_loc 21765 <= 21765`, `ok class_excess_loc 17281 <= 17281` (`ev/structure.txt`).
  - Three-dot against `b4a8bbd5`: `class_excess_loc` 17297 -> 17281, `module_excess_loc` 21774 -> 21765. No row is raised. The interim raise `afd32f78f0` is paid by `ee0e11d51d`.
  - Step 14: the -9 on `module_excess_loc` comes from moving the two helpers out of `optimizer.py` into a new module that owns their concept. That is the move the previous block named as sound, so the drop is earned.
- `archscore --diff b4a8bbd5`: `Architecture score: dS +0.0000 NULL` (`ev/archscore.txt`).
- `VERSION`, the manifest version, `RELEASE_NOTES.md`, `tests/golden` and both claim files: the three-dot diff against the merge base is empty.
  - The manifest's three-dot diff is empty. Its two-line change in `git diff 8800ed7c d7029ade` is main's, not the PR's.
- Step 16: no actuator-write refusal is added; attribution only.
- Owed reds (`ev/owed_reds.txt`):
  - `tests / fast (3.14)` and `gate` are red. The block above covers them.
  - `tests / mutation` is green at this head. The digest's `tests / nightly-status` failure is outside the owed set. `tests / replay` is cancelled and outside the set.
- Finder's harness: none named (packet `## Finder's harness: none named`). The round-1 verdict measured `dev/audit/harnesses/room_lift_solve.py` byte-identical across the feature. This delta moves arithmetic; it does not change values, and the mutants above pin that arithmetic.
- The orchestrator's local report of a full `features.py` pass (6160/6160) was not re-taken. CI's fast summary names one failed script, and `tests/entities.py` alone reproduces it. I stopped my own `features.py` run after that (by PID).
- `carry_audit.py check` rc 0: `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)` (`ev/carry_audit.txt`). The `--body` I passed holds only the body's one `Carry:` item, the same one the packet's own head-time audit counts, and not the full PR body.
