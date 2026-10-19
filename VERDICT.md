Fix review: merge 40c4e1194dfd23371403f874e9a8a1abd45da162

bus-nonce: ca38930611db40cea073c44a6e7cdd8d

## Round

Round 1. PR #2445 has no earlier `Fix review:` comment or review, so this is the first fix review of R10-SETPOINT-POWER.

Measured head: `40c4e1194dfd23371403f874e9a8a1abd45da162`, recorded in `ev/HEAD`. It is still the branch tip at verdict time (`git ls-remote`), and it is the head the PR body names (step 7). Merge base: `e59f0291a`. `fix-review.md` on origin/main has no diff from the merge base under `dev/governance/roles/`, so the contract I followed is current.

## RESULT lines

- RESULT merge-tree: `git merge-tree --write-tree origin/main(64b0ae690) 40c4e1194` exits 0 with tree 55d32b5ff and no conflict. No claim file is touched, so no driver ran (`ev/merge-tree.txt`).
- RESULT version: VERSION, the manifest version and the RELEASE_NOTES heading are all untouched. The diff touches no `tests/golden`, claim file or `*_budgets.json`. CI pr-contract printed "no version edit".
- RESULT ci fast (3.14) on Linux x86_64, job 118118404820: **success**. `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT`. That includes features, entities, `env_drift.py --all e59f0291a` (step 4: CI's run, green), optimality, stress (113, whole-solve CPU median 0.993x), structure and card_drift (40/40 identical). The 5 scoped out are arch_score.py, frontend, ha_contract, md_tables and open_meteo; none has a changed file in its closure.
- RESULT ci mutation, job 118117357434: **success**, and its log shows real evaluation, not an inconclusive pass. `0 survivor(s) of 5 evaluated`, `PIN RE-VERIFICATION: 5 reproduced, 0 not reproduced`, `MUTATION TABLE PASSED`.
- RESULT local features at head (x86_64, Python 3.14): `ALL 4230 FEATURE CHECKS PASSED` (`ev/features_head.txt`).
- RESULT local structure: `STRUCTURE RATCHET PASSED`.
- RESULT census harness at head (x86_64): `spread: cells 32 objective lower 23 higher 0 identical plan 9`, `flat: cells 32 objective lower 16 higher 0 identical plan 16`, `failures 0`. At the base, `0/0/32` on both arms (`ev/census_head.txt`, `ev/census_base.txt`).
- RESULT spread fixture (x86_64): above-p_min kWh in the 24 cheapest steps 14.79, control 18.73. Objective 18.037 against 25.299. This reproduces the body's x86_64 figures exactly (`ev/mini_head_values.txt`).
- RESULT hot-water cells: objective deltas (0.6,-4) 0.0, (0.6,+2) 0.0, (1.0,-4) -0.991, (1.0,+2) -0.524. Two cells are lower and none is higher.
- RESULT flat fixtures: space path 39.103 against 39.103 (identical); hot-water path 31.161 against 32.492 (lower).
- RESULT mutants: 9/9 claimed red, 6/8 extra red, 4/4 ledger red (table under step 1).
- RESULT CPU (x86_64, minimum of 3 `process_time` runs, 16 clamped cells): the relaxed start adds +0.27 to +3.10 s per solve, a ratio of 1.06 to 2.40. Exactly one relaxed pass per `optimize()`, including cells with two multi-starts (the hot-water warm pass adds none) (`ev/cpu_x86.txt`).

## Step 1: mutation proof, re-run

Instruments: `ev/reviewer_tools/mutants.py` and `mini.sh`, the reviewer's own and out of tree. `mini.sh` runs the R10-SETPOINT-POWER block of `tests/features.py` verbatim from the tree under test. Each mutant was applied to a detached worktree at the head and restored with `git checkout`; the tree was clean afterwards. M0 (unmutated) passes 10/10.

| Mutant | Edit | Result |
|---|---|---|
| M1 | `_flow_inlet_c` returns `state.floor_return_temperature` | red 3 |
| M2 | `FLOW_MIN_LIFT_K = 0.0` | red 3 |
| M3–M6 | each `FLOW_INLET_KEYS` rung dropped | red 1, 3, 1, 1 |
| M7 | space-path `_relaxed_starts` call deleted | red 1 (the spread check) |
| M8 | hot-water `move_starts=` deleted | red 1 (the hot-water check) |
| M9 | `_scores_rounded` ignores `_levels_relaxed` | red 3 |
| X1 | tank and floor-return rungs swapped | red 1 |
| X2 | relaxed result replaces `cands[first]` instead of appending | red 1 |
| X3 | `first >= len(cands)` guard dropped | crash (IndexError) |
| X4 | `_levels_relaxed` never reset | red 2 (incl. the flat null control) |
| X7 | stale readings accepted (`value is not None` instead of `ok`) | red 1 |
| X8 | relaxed pass also on an unclamped install | red 1 |
| X5 | hot-water path passes `first = 0` instead of `len(extra_starts)` | **survives** |
| X6 | hot-water warm pass also gets a relaxed start | **survives** |
| L CMP_BOUND, CONST 10.0, floor RETURN_DEL, relaxed RETURN_DEL | the ledger's own mutants | crash, red 1, red 4, red 3 |

On the two survivors, which block nothing:
- **X5** is equivalent on every fixture, because none passes `extra_starts`. No fixture checks that the index of the first structural start is right on either path; that holds on the space path as well.
- **X6** changes cost only, not the shipped plan. The pass-past-the-last guard is pinned at unit level (CMP_BOUND, GUARD_OFF). My CPU probe also confirms behaviourally that warm passes add no relaxed pass.

## Steps 2, 3, 9: the harness, and the null control

**No finder's harness is committed.** The group comes from the owner's live diagnostics. The replica figures (`relaxexp.py`, `compare.py`, `cputime.py`, `econ.py`, `lumped_dp.py`) run on the owner's private export from out-of-tree `$SCRATCH` and `$STUDY` paths, and this seat cannot run them. **I do not verify them** (step 8):
- the replica objectives 138.419→126.004, 322.738→286.120, 227.271→200.568 and 359.288→359.280;
- the -1.50, -8.76 and -4.89 SEK figures;
- the arm64 CPU figures.

The fixer disclosed the census harness `dev/audit/harnesses/r10_setpoint_power.py` as their own, and it landed (step 9 satisfied). I measured with it at both ends. No item in the judge's design or the architect note goes untested except the plan-identity control, ruled on below.

**Census figures depend on the architecture.** The body's `spread 24/0/8, flat 20/0/12` is the fixer's arm64 reading; the body does not name the machine. On this x86_64 runner it reads 23/0/9 and 16/0/16. The invariant the fix claims holds on both architectures: higher = 0 on both price vectors, and every moved plan scores lower (flat: 16 non-identical, 16 lower). The literal "20 of 32" is not reproducible on x86_64. The R10-STAMP carry quotes it, so the stamp should record it as an arm64 figure (finding-propagation note below).

### Ruling (1): the flat-price null control weakened from plan identity to "never worse, and every flat-price move lowers the objective"

**The data supports it. Not blocked.**
- **The mechanism makes it hold by construction.** `_multi_start_minimize` refines every candidate and ships the cross-candidate minimum; I read `optimizer.py:934-1060` at the head. `_relaxed_starts` only appends, and the two-zone continuation still moves `cands[first]` in place, so the candidate set is a strict superset. The solve has no wall-clock deadline that the extra candidate could exhaust: no deadline or timeout in `optimizer.py`, and the solve runs out of process via `optimize_in_process`.
- **Census on x86_64:** flat 16 of 32 cells move, all 16 lower, 0 higher. Spread: 23 lower, 0 higher.
- **The fixer's arm64 census** reports 20 of 32, all lower. I cannot re-derive the arm64 count here, but its sign agrees.
- **Plan identity is unattainable for this fix.** The flat band traps flat-price solves too: flat cells that were stuck at a worse objective move to a lower one. Restoring identity would mean refusing the improvement at flat prices only. The remaining job of the brief's control, keeping gain claims honest, is kept: every replica gain in the body is quoted net of the flat-price column. The features check asserts "never worse" on both paths, and X4 shows it is not vacuous.
- **Carry present:** R10-STAMP at roster `7b87e23ed` carries the ruling, its control and the release-notes obligation (`ev/roster_carry_7b87e23ed.txt`).

### Ruling (2): Raspberry Pi CPU, estimated only

**Acceptable to merge with the post-release Pi measurement already carried. A `maxiter` cap is not owed now.**
- **The relaxed pass is already capped.** It runs under the multi-start's own `maxiter`, 300 on both paths (`_relaxed_starts(..., maxiter)`, passed `maxiter` from `move_starts(candidates, maxiter)`). So it is not an unbounded new cost: at most one extra L-BFGS-B run plus one extra refined candidate.
- **One pass per solve.** My x86_64 probe found exactly one relaxed pass per `optimize()` in all 16 clamped cells, including cells with two multi-starts. The delta was +0.27 to +3.10 s, a ratio of 1.06 to 2.40, against the fixer's arm64 +2.0 to +2.7 s.
- **Pi extrapolation.** Assumption, not measured: the fixer's 4-6x single-core factor. That gives about +1 to +19 s extra, and about 62 s for the slowest whole clamped solve in my set (10.27 s × 6).
- **What a slow solve affects.** The solve runs in a separate process (`coordinator.py:1692`, `_await_process(..., optimize_in_process, ...)`), so a long solve does not starve the HA event loop. The default cycle is `DEFAULT_OPTIMIZATION_INTERVAL = 30` minutes. Even the pessimistic extrapolation is under 4% of the interval.
- **Who pays.** Only clamped (cannot-duty-cycle) installs; an unclamped install pays nothing (X8 pins that). `tests/stress.py` on CI shows whole-solve CPU at a median of 0.993x across its 54 unclamped scenarios.
- **The carry stands.** R10-STAMP owes a measured `process_time` on the owner's Pi and a cap if a clamped solve exceeds the update-interval budget.

## Steps 4, 5, 13, 14

- **Step 4, claims.** No fixture is claimed or moved. CI ran `env_drift.py --all e59f0291a`, green, and `card_drift` is identical in all 40 states. No goldens use `clamp_planned_levels`; I grepped `tests/`.
- **Step 13, merge.** `merge-tree` is clean against origin/main `64b0ae690`, which is 3 commits past the head's merge base.
- **Step 14, moved numbers.**
  - Seven `killed_by` records. CI re-verified 5. I re-killed CMP_BOUND, CONST (10.0) and the two RETURN_DELs locally. Each is earned by a features check, not by the instrument.
  - `tests/closures.json` gains one line, the new harness in the inert list. Every new tracked file needs that classification (`tests/entities.py` is green on CI).
  - The architecture score is not raised (`dS +0.0000` per the body). `structure.py` passes at the recorded value: `class_excess_loc` was paid by module-level functions and a cut comment, not by a re-record.

## Step 6: the class

The body names no enumeration rule. The brief states two defects, and the architect note names each one's owning seams. I enumerated callers in the head tree:
- `flow_setpoint_for_level` has one caller (`pump_arbiter._flow_target`), and it changed.
- `_multi_start_minimize` has two call sites (`optimizer.py:3951`, `:4546`), and both carry the relaxed start.
- `_realize_draw` has two scoring call sites (`:4328`, `:4390`), and both switched to `_scores_rounded`.
- The `_published_levels` sites ship levels; they do not score, so they are correctly unchanged.

No seam is open.

The brief's precedence list included the pump's outgoing flow. The diff deliberately excludes it, because it is the set-point's own controlled variable. The body dispositions that, and a features check pins it ("the pump's outgoing temperature alone is not a rung"). Both config slots already exist, so the brief's "become optional config inputs" item needed no new key.

## Step 11: checks at this head

Every red at `40c4e1194` failed on GitHub API access. None measured this diff:
- `arch-score` (both runs) and `pr-contract` (both runs): `gh: API rate limit exceeded` / body file never fetched.
- `validate-hacs`: `GitHubRatelimitException`.
- `env-matrix`: 15/16 held; the one FAIL is "required-contexts: the GitHub API is unreachable ... UNCHECKED".
- `nightly-status`: main's, as the body already answers.

Because no `pr-contract` run at this head has read the body, I cannot judge the red-check trigger, and I do not post `root-cause-unanswered`. Before merge, the orchestrator owes re-runs of `pr-contract`, `arch-score`, `env-matrix` and `validate-hacs`. If any of them is red on a real measurement, this verdict does not cover it.

`closures` was still in progress when I wrote this. `fast (3.14)` and `mutation` are green, and every other completed check is green or skipped.

The body's `## Red checks` answers the earlier round's reds (`mutation`, `mutation-autofix`, `fast (3.14)`, `pr-contract`, `nightly-status`), each with this diff's fix or the reason it is not this diff's.

## Step 10: forward-carry

Both carries are on `handoff/audit-r10-roster` at `7b87e23ed` under R10-STAMP, and each states its control or obligation as a precondition. The fixer-md friction carry is under R10-POLICY-FIXER-MD.

Finding to propagate to R10-STAMP: the census counts are per architecture. The carry's "20 of 32" is arm64; x86_64 reads 16 of 32, with 0 higher on both. The release-notes line should state the invariant (0 higher, every move lower), not the arm64 count. This is recorded here for the orchestrator to carry; this seat does not write to the roster.

## Step 15: architecture

The added lines follow the architect note:
- the mapping is anchored at the measured inlet plus a lift, sliding to the ceiling;
- the flat band is removed from the start set, not by smoothing the shipped score;
- `coordinator.py` is unchanged;
- the new precedence is the one resolver in the arbiter, through `InputReader`.

No breach.
