Fix review: blocked 6f1dd2040ce51f5dbff0ce67ffc1085637b29ea6 class-open: a high-limit sensor reading at or below the gate makes the loop write the gate or below it, and the two added vendor comments keep the combi census red after #3466

bus-nonce: aeccdd3f69b478d94d6fb214de3af9ea

Round: first (handoff tip 100ff9351df307cbdaaea4c24ae15cb78ff1c799; measured head 6f1dd2040ce51f5dbff0ce67ffc1085637b29ea6).

## Block

1. **The new upper bound has an unguarded domain, and the loop can write the off gate (I2).** `_feedback_bounds` (`pump_arbiter.py:976-983`) now appends the high-limit sensor to `highs`, but nothing keeps `hi >= lo`. Then `_feedback` sets `rec.w_c = min(max(nudged, lo), hi)`, and `_bounded(..., lo=lo, hi=hi)` passes `hi_c` below the gate floor and below the entity's own minimum. Before this diff, `hi` could only be the ceiling (30 °C or above) or a read-back cut above the previous write. This diff gives it a third source, a configurable sensor. The picker offers any `sensor`/`temperature`, and `WATER_RANGE_C` admits −20 to 100 °C, so a mis-picked outdoor or room sensor is accepted as a limit. Measured with the finder's harness `sim` at the head (`ev/probe2.py`, `ev/probe_gate.txt`), on the step-up block of the PR's own fixture with a return unit (gate 20 °C):
   - high limit 5.0 → 30 of 62 writes at or below 20.0 °C, the lowest 5.0 (below the entity minimum of 15);
   - high limit 15.0 → 30 of 62, lowest 15.0;
   - high limit 20.0 → 30 of 62, each one exactly the gate;
   - high limit 21.0 or 22.0 → none at or below 20.0;
   - null control, no sensor → none (lowest 26.0).
   The writes alternate between today's target and the limit (`26.4, 5.0, 26.7, 5.0 …`), so each run start is followed by an off command. `_feedback_bounds`' own docstring promises "nor at the gate (I2)". The crossed-pair guard covers only two set sensors, and the unusable-sensor check never tests a single limit below the loop's lower bound. This is the predicate's unguarded domain (fix-review step 6). The fix belongs in this diff: drop a limit that would put `hi` below `lo` (or below the gate clearance) as unusable, as the PR already does for a crossed pair, and add a check with its no-sensor null control. A low limit above the ceiling is safe: the ceiling wins and the highest write stays 32.0 (`ev/probe_edges.txt`).
2. **This PR adds two of the vendor-name sites that keep `tests / fast (3.14)` red after #3466.** At the head, `combi_type_branch census` FAILs listing eight sites (`ev/features_head.txt`). #3466 rewrites six of them. With #3466 merged into this head (`git merge-tree` clean, tree `3b7f5185500e0b12ddeb79ce50c76d7c353632f8`), the census still FAILs, on exactly `['config_flow.py:1704', 'const.py:836']` (`ev/features_head_plus_3466.txt`). Both are comment lines this diff adds ("a Luxtronik's inputs 10104 and 10103"). So the fast red at this head is not only main's. Name the behaviour, not the vendor, on those two lines, as #3466 does. The docstring edit at `pump_arbiter.py:1049-1052` sits next to #3466's own edit at line 1047; they merge cleanly.

## Findings

none

## Evidence

- `ev/HEAD.txt`: the head I reviewed. `git merge-tree --write-tree origin/main <head>` exits 0 at origin/main 60413046e (`ev/merge_with_3466.txt`). `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- Finder's harness `dev/audit/harnesses/r10_water_setpoint_feedback.py` (sha1 ee9f738ce477dddab30d808eef4cdaddcdbbf178, the head's file), run at the merge base 0a2139b1dd and at the head (`ev/harness_both_ends.txt`). The three part-1 rows are identical at both ends. At the base, `return limit 27.6` prints highest 28.1 with the sensor set or unset, and `return minimum 28.0` prints lowest 27.6 either way. At the head, with the sensor set, they print highest 27.6 and lowest 28.0. This matches the body.
- Mutation proof, `tests/features.py` at the head with each mutant applied (`ev/mutation_driver.txt`, `ev/driver_*.txt`, `ev/mutant_*.txt`):
  - M1 (`lows.append(low)` deleted) FAILs the minimum-28.0 check.
  - M2 (`high` dropped) FAILs the limit-27.6 check.
  - M4 (`if False:`), M5 (`>=` to `>`) and M6 (both `WATER_RANGE_C` rows deleted) each FAIL the unusable-sensor check.
  - M8 (mine: the limits forced to `None`) FAILs both sensor checks.
  - M3 was not re-run.
  - M7 was not applied: its pattern occurs twice, so my driver refused. The body discloses it as an equivalent survivor, and its reasoning matches `InputReader.read` (`inputs.py:995-1013`: `value` is withdrawn when the reading is implausible, and with no age limit nothing else sets it while not ok).
  - Each mutant run also shows the combi census FAIL, which is the head's baseline, not the mutant's.
- `tests/features.py` at the head: rc=1, `1 of 5245 FEATURE CHECKS FAILED`, the combi census only. All eight part-3 checks pass.
- Figures re-derived at the head:
  - `git grep -c -E 'space_setpoint_(low|high)_limit_entity'` matches no line at origin/main (exit 1) and seven files at the head.
  - The seam rule `_bounded(inp, "space_setpoint"` returns five sites (614, 755, 886, 949, 1158), as the body says.
  - `tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
  - `archscore --diff origin/main` printed `dS +0.0000 NULL` (`ev/cheap_checks.txt`).
- carry_audit was run with the body's `## Red checks`, `## Forward-carry` and `## Friction` sections (all `none`) as the body file; the packet's own carry_audit at the head printed 0 finding items.
- Not checked: VERSION, manifest, RELEASE_NOTES and both claim files appear in no hunk of the three-dot diff. No golden or `env_drift` drift was re-run.
- Forward-carry: the body names none. Carry 8's 10107 read is ruled to R10-OUTSIDE-DHW-START-HYSTERESIS by the orchestrator; I did not open the roster.
- CI: `merge_train.py classify` still prints `WAIT 6f1dd2040ce51f5dbff0ce67ffc1085637b29ea6 pending: gate red: none` after about 40 minutes (`ev/classify_last.txt`). No owed red concluded at this head, so `## Red checks: none` is not yet contradicted. The census red above is shown by a local run and is part of the block, not a root-cause trigger finding.
