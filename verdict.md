Fix review: blocked 345cdf5866c2f03cf3ae764c2aa4bd1b18d70184 carry-missing: pr-contract is red at this head because CARRY-AUDIT reports 3 unrouted body items (2 under Measured limitation, 1 under Forward-carry)

Round 1 for this reviewer. Measured head 345cdf5866c2f03cf3ae764c2aa4bd1b18d70184. It was still the PR head when this verdict was written. Merge base 4a3cbcf62e6f, which equals origin/main. No change under dev/governance/roles/ since the merge base.

## The blocker

- Both `pr-contract` runs at this head (jobs 118355113137 and 118355261360) fail in `tools/audit/carry_audit.py check --body` with:
  `CARRY-AUDIT: 3 finding item(s): 0 routed, 3 unrouted, 0 bad destination(s)`
  - item 2eca8613: "The mapping reads the water temperature only at the floor"
  - item 2859fcbc: "Reaching the real maximum"
  - item 9cf3c469: "## Forward-carry: none ..."
- What is actually carried: the substance of the R10-CEILING-PROBE precondition is written in the roster at origin/handoff/audit-r10-roster d8250cd44. Its brief records ceiling-commanded draws into "draw_range's ceiling-commanded evidence (R10-SETPOINT-BOOST fix B)".
- The gap: the body says "Forward-carry: none" and routes neither limitation. The mapping limitation (no gain identified between set-point and draw) and the p_max owner question are recorded nowhere the audit accepts.
- The fix is a body-only edit: route each item to its destination (the roster carry for R10-CEILING-PROBE; tvofi for the two owner questions). No code change is needed.
- The body's `## Red checks` section answers arch-score and mutation, but not pr-contract.

## Verified (RESULT lines)

- RESULT merge-tree: `git merge-tree --write-tree origin/main <head>` exits 0. No conflict, no claim-file driver call.
- RESULT version: pr-contract prints "no version edit". VERSION, the manifest and the notes heading are untouched. No golden or claim file is touched.
- RESULT A floor collisions: head `floor: cells 155 heating floor at or below the gate 0`, base `... 63`. Matches the body.
- RESULT B window:
  - head: `window plan: engaged False observed (0.9, None) idle 0.3 planned None`
  - base: `engaged True observed (0.9, 2.034) idle None planned (0.9, 2.034)`
  - probe window: `engaged True observed (2.94, 3.0)` at both trees.
  - Matches the body: 3.0 kW learned from the probe-shaped window; the base learns a false 2.03 kW.
- RESULT null (byte-identity): all 32 per-plan lines (16 installs x spread/flat, sha1, objective deltas, savings) are identical between base and head (`diff` empty). The spread line `cells 16 relaxed start objective lower 8 higher 0 identical plan 8` matches the body.
- RESULT a figure that does NOT reproduce:
  - body: `flat: cells 16 relaxed start objective lower 0 higher 0 identical plan 16`
  - measured at both trees: `flat: cells 16 relaxed start objective lower 2 higher 0 identical plan 14`
  - The two different cells are 0.6/750/False/True and 0.6/0/False/True, each with relaxed-delta -1.814.
  - Identical at base and head, so this is not caused by the fix. It is probably a solver/BLAS environment difference, but I cannot re-derive the body's number, so it is not verified.
- RESULT arch: `tools/audit/archscore/vector.py .` gives identical output at base and head (24 keys, no key differs, coord_footprint 2498 at both). CI `arch-score` is green at this head.
- RESULT M0: the 7a block plus this group's block (features_block.py, from "-- live power clamp, 7a" to "#1956") gives `ALL 68 FEATURES BLOCK PASSED`.
- RESULT reviewer mutants (my own set, ev/mut.py, applied to a git-archive copy and restored):
  - R1-R12, R14, R17 and R19 go red in the block.
  - Each body mutant M1-M14 has a counterpart here that went red.
  - R13 (valve rounds nearest) survives the block but is killed by the full suite: 6 of 4247 fail, the valve set_value/set_temperature checks.
- RESULT survivors (full features.py, 4247 checks):
  - **R16: removing `lo=min(floor_c, heat_c)` from `_flow_target` survives.** The only full-suite failure is the #363 recorded_at check, which an archive copy without .git fails anyway.
  - So the arbiter's "a heating floor rounds up" is unpinned at its production site. The body's M10 mutates the quantiser, not the arbiter's plumbing.
  - Effect: an inlet such as 25.3 C gives a floor of 30.3, written as 30 instead of 31. It stays above the gate, so A is unaffected.
  - CI's own CLAMP_DROP at pump_arbiter.py:622 (lo=floor_c) is likely an equivalent mutant, so mutation-autofix cannot pin this line by killing.
  - Recommend one check through `_flow_target` with a fractional inlet. Not blocking on its own.
- RESULT equivalent survivors (not defects):
  - R15 (gate rounds up) and R18 (DHW gate nearest) are equivalent on every whole-degree gate: the value is the gate, the entity minimum (lo rounds up) or the entity maximum (hi rounds down).
- RESULT four changed features expectations (C), each checked against the code:
  - GCHV hot-water gate "40" (whole-int formatting of 40.0): correct.
  - degF delivery cells: 21 C = 69.8 F, nearest gives 70. Correct.
  - smart_write valve: a 23.5 C cap rounds down to 23 (C), or 74.3 F down to 74. Correct.
  - degF min clamp: a 44.6 F minimum rounds up to 45 F = 7.22 C. Correct.
  - The 'flow' valve check uses `int(_expected_flow)`, i.e. floor, which matches the "down" rounding for positive values.
  - None is weakened.
  - Also changed but not named among the four: `_SP_READ` moved from 22/24/26/31 to 27/29/32/36, so each anchor keeps its own lift above the gate. The sub-gate case is pinned separately ("an 18 degC tank ..."), so coverage holds. It is still an undisclosed fixture change to an existing check.
- RESULT quantiser bounds (ev/probe_quantiser_head.txt):
  - Over nearest, up and down, writes stay within the entity min/max for °F, 0.5-step, 0.1-step and a non-whole-range °C entity.
  - A 0.5-step entity keeps 23.5, a 0.1-step entity keeps 23.4, °F writes go out as 74 and 127.
  - Exception: an entity whose range is narrower than one step (25.3-25.7, step 1) gets 25, below its minimum. No on-step in-range value exists there, so this is pathological and not blocking.
  - The repair flow (`repairs.py`) is a write_setpoint caller the body does not name. It writes a disinfection floor at nearest, so on a °F entity floors of 48/53/58/63 C go out 0.22 K low. That is inside MIXING_VALVE_WRITE_EPSILON 0.25, so the notice still clears. No defect, but it is a seam of the "one service call" class that the body leaves undispositioned.
- RESULT B starvation (ev/probe_idle_head.txt):
  - A pump that never reaches its ceiling learns no maximum (`high None`) by design, and its low end and follows_ask still learn: 72/72 samples are evidence.
  - Residual risk: if the gate is not truly off (the compressor runs at the gate on a cold inlet), the idle median absorbs compressor draw. At a gate-held draw of 1.4 kW, 24 of 72 running samples are dropped and the low end shifts from 1.35 to 1.8 kW.
  - follows_ask (read by the live COP learner) uses the same filter.
  - Not blocking: it needs the gate to command heat, which the design rules out. Worth a note to R10-CEILING-PROBE.
- RESULT CI on head (check-runs API):
  - green: arch-score x2, budget-raise-gate x2, typing, browser, env-matrix, closure-scope, hassfest, validate-hacs, instrument-self-tests, policy-docs, delivery-status, nightly-status, briefs
  - red: pr-contract x2 (the blocker above); mutation (the 59 added unpinned sites, as the body predicts: "4206 unpinned against 4147 ... 59 added")
  - still running when measured: fast, coverage, mutation-pins 1-12, CodeQL python. Not re-run by me (step 11).
- Harness provenance: `dev/audit/harnesses/r10_setpoint_boost.py` is the fixer's own. The finding is an owner report with no finder's harness, so the both-ends figures above use the fixer's instrument. The probes and mutants are this reviewer's (ev/). The owner's export was not requested or used.

bus-nonce: bdfeff3d9d24d549523dba7670d8d9b9
