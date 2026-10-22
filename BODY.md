Part of #2495. Group R10-CI-LAYOUT-P2, sub-PR **P2a, "umbrella engine, inert"** (plan `1011d6b2f:plans/ci-layout/EXECUTION.md` §3, §3.1). It merges five unit heads and adds the glue. No workflow trigger, no check name and no ruleset changes: `contexts` stays the 17, and `tools/ci/` has no caller until P2b.

| unit | head | what |
|---|---|---|
| U0a gate core | `06c99c0e3` | `tools/ci/ghapi.py` (the one REST client), `prelude.py`, `gate.py` (predicate, `REQUIRED`, `--refresh`, `RATE-LIMITED`), the fixture's additive `gate_required`, the oracle driver `r10_ci_gate_core.py` |
| U0b sweep | `65514d997` | `tools/ci/sweep.py` and `sweep_selftest.py`; `tools/audit/seat/sweep_driver.py` and its self-test; `r10_sweep_driver_arm.py` |
| U6-lib alert lister | `c90a9b15b` | `tools/ci/alert_list.py` and `alert_list_mutants.sh` |
| U9c ruleset instrument | `75956eeed` | `tools/ci/ruleset_cutover.py` and its two saved-JSON fixtures |
| UP probe instrument | `7b73637df` | `tools/audit/seat/ci_probe.py`, its `PUSHERS` row, the `ci-probe/` prune family |

**Assembly.** Conflicts were resolved by keeping every unit's lines:
- `r10_seat_selftests_mutants.py`: each block keeps its own per-file ids, 82 ids with no duplicate. U0a's `rel()` and U9c's `seat_path()` are the same function, so one is kept.
- `tests/layout.json`: `tools/ci/**` appears once.
- `tests/closure.py`: U0b's and U9c's per-file `GATE_FILES` lines and U6-lib's two `INERT` lines are dropped, because U0a's `tools/ci/` prefix classifies those files.
- `closures.json`: a set union.

**Bind** (contract items 2-3):
- `gate.py --sweep` imports `tools/ci/sweep.py` and calls `sweep.main(argv, get, post)` with ghapi's functions. The guarded `FAIL sweep-unavailable` fallback is gone.
- `ghapi.get` takes an optional `headers` argument. This is additive: `get(path, params=None)` still works. `alert_list.bind(get, repo)` prefixes `repos/<repo>/` and forwards the SARIF `Accept` header. Its `__main__` binds `ghapi.get` and fails closed without `GITHUB_REPOSITORY`.
- Under `tools/ci/`, only `ghapi.py` names `urllib`.

**Glue.** Two new `tests/entities.py` pins:
- `gate.REQUIRED`'s sorted union equals the fixture's `gate_required`, which must be sorted and duplicate-free, and `contexts` holds 17.
- The half of the forgery rule that needs no `ci.yml` (DESIGN-P2 2.1): no workflow except `ci.yml` defines a job that can report as `gate`; no workflow or job grants `checks: write` or `write-all`; every workflow declares top-level `permissions:`.

`tmp_paths.py` gains an `ALLOW` entry for `ci_probe.py`'s self-test fixture.

## Head

`0e066014d8d31e690b2ee5ddd5fae76bb3015a04`, merge base `a9db47846647` (origin/main after #2579, 2026-10-22). The head adds the nine `governance.yml` `instrument-self-tests` steps: one each for `ghapi`, `prelude`, `gate`, `sweep`, `alert_list`, `ruleset_cutover`, `sweep_driver` and `ci_probe`, plus `alert_list_mutants.sh --self-test`. Each asserts its tally line.

## Mutation proof

- **Seat mutants**: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py`, run at the head, gave `RESULT survivors=0`: M0 `0 seat step(s) red`, 90 `KILLED`, no `SURVIVED` and no `NOT RUN` or `PATTERN FOUND` lines, and W1-W3 killed. P2a's ids are `gate-1..3`, `ghapi-1..3`, `prelude-1..2`, `sweep_driver-1..3`, `ruleset_cutover-1..3` and `ci_probe-1..4`. `gate-3` now deletes the bound dispatch; `ghapi-3` deletes the header forwarding.
- **Alert-list mutants**: `sh tools/ci/alert_list_mutants.sh --self-test` refused 9 of 9, including the glue's case "the binding drops the Accept header".
- **Gate predicate**: `r10_ci_gate_core.py mutants`, 16 of 16 killed at U0a's head. The predicate is unchanged here, because the glue touches only `main()`'s `--sweep` arm.
- **Entities pins**: each pin was run against a mutated copy of the tree, through its own block. Dropping `ci-ratchet` from `PUSH_ONLY` gave `only in gate_required: tests / ci-ratchet`. Cutting `contexts` to 16 gave `contexts holds 16`. A `gate` job in `tests.yml` gave `tests.yml: job gate can report as gate`. `checks: write` in `hassfest.yml` gave `top grants checks: write`.

## Null control

- `python3 -I tools/audit/seat/selftest_wiring.py --check` reads `87 self-testing, 87 wired, 0 unwired`, rc 0, at the head. At the merge commit before the steps it read `87, 78, 9 unwired`, rc 1.
- `r10_ci_gate_core.py replay --no-b3-fill` gives `rc 1; output DIFFERS`: exactly the two push rows go BAD. `b3 --plant` gives `parity RED`. So the IDENTICAL comparison can fail.
- Each entities pin carries in-file plants: three for the REQUIRED pin and five for the forgery pin. A reader that compares nothing fails its own check.

## Decisions

Confirmed by the orchestrator under mandate 6329234399 (2026-10-22):
1. `ghapi.get(path, params=None, headers=None)`: the `headers` argument is additive, and the contract's two-argument form stands. `alert_list.bind` forwards the SARIF `Accept` header through it.
2. `gate.py --sweep` imports `tools/ci/sweep.py` directly, and the `sweep-unavailable` fallback is removed. Mutant `gate-3` is re-targeted to delete the bound dispatch.
3. alert_list's mutants stay in `tools/ci/alert_list_mutants.sh`, wired as their own `instrument-self-tests` step, and are not duplicated into `r10_seat_selftests_mutants.py`.
4. `tools/audit/seat/tmp_paths.py` gains an `ALLOW` entry for `ci_probe.py`'s self-test fixture, the scratch path its dismissal check must refuse.
5. `tests/closure.py` drops the per-file lines under `tools/ci/` (U0b's and U9c's `GATE_FILES` lines and U6-lib's `INERT` lines), because U0a's `tools/ci/` prefix classifies them.
6. The forgery pin also requires every workflow to declare top-level `permissions:`, so no job falls back to the repository's default token.

## Figures

- Self-tests, each `python3 -I <file> --self-test` with the 3.14.7 seat venv:
  - `ghapi` 13 checks, 0 failed;
  - `prelude` 27, 0 failed;
  - `gate` 27, 0 failed;
  - `sweep` 21, 0 failed;
  - `alert_list` 25, 0 failed;
  - `ruleset_cutover` 51, 0 failed;
  - `sweep_driver` 15, 0 failed;
  - `ci_probe` 34, 0 failed;
  - `python3 tools/audit/seat/prune_refs.py --self-test`: `SELF-TEST PASS (29 checks)`.
- Oracles over the assembled `gate.py`, from `dev/audit/harnesses/r10_ci_gate_core.py`:
  - `replay`: `rc 0; output IDENTICAL to 1371a0a6:measure/rev/gate_replay2.txt`, and `replay --model` reads the same;
  - `sim`: `GATE-SIM rc 0; output IDENTICAL to 1371a0a6:measure/rev/gate_sim.txt`, which holds the 42 sequences at END-BAD 0 and the 7 planted defects refused;
  - `b3`: `parity GREEN`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `4 of 2399 ENTITY CHECKS FAILED`. The same command at `origin/main` a9db47846 reads `4 of 2397 ENTITY CHECKS FAILED`, with the same four py-spy heartbeat-control checks. The two new pins read `ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, with no budget raised.
- Other checks:
  - `python3 tests/throwaway_git.py --check`: 0 refused;
  - `python3 -I tools/audit/seat/tmp_paths.py --check`: 0 refused;
  - `ref_privacy.py --check`: 0 refused;
  - `tests/layout.py`: `GUARD: 0 refusal(s)`;
  - `tools/pr/ci_predict.py --base origin/main`: no closures or fast red predicted.
- `python3 -I tests/harness_headers.py` fails at import here, because `-I` drops `PYTHONPATH=tests/hastub`, as U9c reported. The suite's own run is in the gate line below.
- Gate: `PREPR_SKIP_CLOSURES=1 GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=a9db47846647 PYTHONPATH=tests/hastub ./tests/run.sh` printed `MODE: FULL`, because `tests/closure.py` and `tools/ci/` are gate files. Result: `4 TEST SCRIPT(S) FAILED` (`optimality.py`, `card.mjs`, `stress.py`, `entities.py`); everything else was `ok`, `harness_headers.py` included (`ALL 109 HARNESS HEADER CHECKS PASSED`). All four are environmental or main's and not caused by this diff; see `## Red checks`.
- Line counts, from `git diff --stat origin/main...HEAD`: 26 files, 3686 insertions, 4 deletions (`governance.yml` +67). Production lines by each unit's own rule (in its body): U0a 450, U0b 317, U6-lib about 140, U9c 309, UP about 310. File totals:
  - `tools/ci/`: `gate` 419, `ghapi` 225, `prelude` 281, `sweep` 167, `alert_list` 305, `ruleset_cutover` 510, each self-test included;
  - `tools/audit/seat/`: `ci_probe` 466 and `sweep_driver` 150.

## Red checks

- **nightly-status**: red on main's ancestry, not this diff's. It reports the nightly lanes' latest result on main. The diff touches no nightly lane: `git diff --name-only origin/main...HEAD | grep -E 'nightly|rolling|mutation_table|nightly_ha'` matches nothing. No cheaper detector is owed here.
- **Local `entities.py`, four py-spy heartbeat-control checks** (`hb:positive_control` retries, the rest between tries, the hung-sample arms): these are main's, not this diff's. The same four fail at `origin/main` a9db47846 on this host (4 of 2397). The diff touches no heartbeat or py-spy code. CI owns them.
- **Local `optimality.py`, `stress.py`, `card.mjs`**: none of the three scripts' measured closures in `tests/closures.json` holds a changed file. The `optimality.py` red (`1 of 84 OPTIMALITY CHECKS FAILED`, a closed claim still recorded) and the `stress.py` red (`shoulder: cheaper than holding the setpoint [4.67 vs 3.96]`) read the same at the earlier base `origin/main` 49018a8bec8d in a detached worktree (both scripts' closures are untouched by the #2579 merge's delta too). `card.mjs` died with a Node 20 `JavaScript heap out of memory` on this host. CI owns these three. No cheaper detector is owed by this diff.

## Forward-carry

- **The sweep's exit code**: `gate.py --sweep`'s exit code is `sweep.main`'s. A rate limit prints `RATE-LIMITED` (contract item 3's word) but exits 1, not the gate's 3. A non-200 run read raises out of `sweep.main` (exit 1, traceback), which fails closed. `gate-sweep.yml` must key on the stdout word, not on the exit code. Carry: P2b brief (U8+U10, U0c).
- **The two-part `get` signature**: `ghapi.get(path, params=None, headers=None)` is now the signature both CI-run modules use. Any further `tools/ci/` reader that needs a media type binds through it. Carry: P2b brief (U6, U9d).
- **The rest of the forgery rule**: "exactly one job in `ci.yml` reports `gate`" needs the real `ci.yml`. Carry: P2b brief (U0c entities pins).
- **The units' own carries**: U0a's to U0c (`run-name`, `fetch-depth: 0`, the gate step); U0b's live status values and `workflow_run` on a job-token re-run; U9c's ruleset staging at H. Carry: P2b brief.

## Friction

- `writing-for-agents: cost`: the brief prescribes `python3 -I tests/harness_headers.py`, which cannot import the stubbed `homeassistant` under `-I`. `run.sh`'s form passes. Carry: plans/ci-layout P2a common brief.
- `gate-scoping: unenforced`: UP's handoff reported `ref_privacy --check` at 0 but did not run `tmp_paths.py --check`. That check refused UP's self-test fixture on the assembled tree, and it would have reddened `governance` in CI. Carry: plans/ci-layout P2a common brief.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
