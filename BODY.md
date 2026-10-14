This lands the grader half of the D15 dimension (#2209) before the driver half. CI grades `wave-script` with the base's copies of `tools/policy/check-wave-script.mjs` and `tools/audit/*.sh` ("Restore the check source from the base commit", `.github/workflows/governance.yml`), so #2209 cannot turn its own grader changes green. This follows the pattern #2206 set: both files pass against main's current drivers, which have no D15, and against #2209's drivers, which have it.

The diff touches two files and no others:

- **`tools/audit/prepare_baseline.sh`:** `ISOLATED_DIMS` gains D15, whose perturbations edit production.
- **`tools/policy/check-wave-script.mjs`:**
  - **Worktree-list comparison.** It now compares `ISOLATED_DIMS` with `audit-find.js`'s `ISOLATED`, but only over the dimensions the driver declares or a brief names.
    - A dimension with neither a brief nor a `DIMS` entry is tolerated as pending, for the one merge between the graders and the driver.
    - A new pin shows that a declared or briefed dimension is still compared.
  - **Negative controls.** The schema's controls move from `D15-s1` to `D16-s1`.
  - **Bundle pins.** The three D15 bundle pins arm only once `audit-find.js` declares `BUNDLE_DIMS`, the way the `ROUND_DIR` and `CURRENT` pins key on declared constants.

**Design choice, stated:** the tolerance lets `prepare_baseline.sh` create an `audit-r<round>-D15` worktree on main before D15's brief lands. No seat dispatches into it. It ends when #2209 merges, because D15 then has a brief and a `DIMS` entry and is compared.

## Head

`29c14042b8f2a948f9ba6724bb5e37c31cd3cb8b` (`handoff/r10-d15-checker`), from `origin/main` at `554e2ecfa`.

## Mutation proof

Each mutant was applied in place by `mutants.sh`, then the checker was run and the file restored. The script is in the seat scratch directory, not committed.

- **`no-pending-tolerance`** (main's drivers): `const known = s.baseline` gives 178 passed, 2 failed. Failing:
  - `FAIL every dimension brief is in the round driver's DIMS, and its worktree lists agree`
  - `FAIL ISOLATED_DIMS may lead the driver only by a dimension with no brief and no DIMS entry (pending: D15)`
- **`always-equal`** (#2209's drivers): `const known = s.isolated` gives 178 passed, 2 failed. Failing:
  - `FAIL the check fires: the two worktree lists drifting apart is refused (positive control)`
  - `FAIL ISOLATED_DIMS may lead the driver only by ...`
- **`bundle-clause-off`** (#2209's drivers): `BUNDLE_DIMS.has(dim) ?` replaced with `false ?` in `audit-find.js` gives 179 passed, 1 failed. Failing:
  - `FAIL once audit-find.js declares BUNDLE_DIMS, its finders carry the named bundle and export, ...`
- **`abs-path-off`** (#2209's drivers): the absolute-path refusal disabled gives 179 passed, 1 failed. Failing:
  - `FAIL a relative bundle path is refused before Prepare (declared)`

## Null control

On main's drivers, unmutated, `node tools/policy/check-wave-script.mjs` reports 180 passed and 0 failed. The bundle pins print `not declared`, and the pending pin prints `pending: D15`. On #2209's drivers, overlaid on this head, the same command reports 180 passed and 0 failed. There the bundle pins are armed (D15-s1, D15-s2 and D15-s3), and the pending pin prints `pending: none`.

## Figures

- `node tools/policy/check-wave-script.mjs` against main's drivers: rc=0.
- `node tools/policy/check-wave-script.mjs` with #2209's `audit-find.js`, `scopes.json`, `rotation.json`, `finding.schema.json` and `D15.md` checked out over this head: rc=0.
- `bash tools/audit/prepare_baseline.sh --wall-self-test`: rc=0, printing `RESULT finder_wall=ok`.
- `bash tools/audit/prepare_baseline.sh --strip-self-test`: rc=0, printing `RESULT strip_earlier_rounds=ok`.
- `bash tools/audit/prepare_baseline.sh --copy-self-test`: rc=0, printing `RESULT copy_current=ok`.
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` with python3.13 first on PATH: rc=0, `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, `5 TEST SCRIPT(S) PASSED` (with the run_always lines)

## Red checks

- `nightly-status`: this check grades main's nightly (#2205, which a fixer is working on), not this diff. The diff touches two grader files, and the nightly reads neither. No cheaper detector applies to this branch.

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
