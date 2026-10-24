Part of #2273.

The owner's answer on a per-PR timed replay (tvofi, 2026-10-15): "Hard no, only when relevant." This runs `tests/replay.py` on a pull request only when its diff reaches what the lane times, and leaves nightly as the full run.

- `tests/closure.py` gains `replay_reach` / `replay_decision` and the `replay-reach --files-from` subcommand, which prints `replay=true|false` for `$GITHUB_OUTPUT` and its reason to stderr. The reach is the lane's `COST_FILES` (read from `tests/replay.py` as an AST literal, never imported or copied, so the lane stays their one owner), `custom_components/heatpump_optimizer/optimizer.py`, `tests/replay.py` and `tests/replay/*.json`. If the lane source names no readable `COST_FILES`, the decision is to run the lane.
- `.github/workflows/tests.yml`: `closure-scope` emits `replay` from that rule over the same three-dot `changed.txt` its other decisions read, and `replay=false` on the dispatch arm. The new `replay` job is not required. It runs only on `pull_request` with `replay == 'true'` and installs the same pinned requirements as `slow`. Its single step is `python3 tests/replay.py`. It sets `HPO_JOB_GRADES: nothing`: its verdict is about the PR's own code and it grades no other file (`codeowners_gap.py`'s rule, as for `nightly-ha`'s PR arm).
- `tests/entities.py` pins the reach against the imported `replay.COST_FILES`, the null-control paths beside it, the fail-closed arm and the wiring. The job's `if:` is evaluated over five events × three output values.
- Text the change made false is corrected: the `tests/replay.py` docstring, the `NOT_A_TEST` comment in `tests/closure.py`, the `nightly.yml` step comment ("nightly rather than per pull request until..."), and the `tests.yml` header. `tests/README.md` is left byte-identical: its line "`replay.py` runs in the nightly `slow` job instead" means instead of `run.sh`, which still holds.

Alternatives considered. (1) Make `replay.py` a selectable gate script with a measured closure in `tests/closures.json` (the roster's `files` list names it). It lost because the coordinator-cycle closure covers nearly the whole integration, so the lane would run on almost every code PR. That is wider than the owner's reach, and it makes the lane a required gate script. (2) A hand-written pathspec in `tests.yml`, like `nightly_ha`'s. It lost because it is a second copy of `COST_FILES` that can drift from the lane. (3) Put the rule in `tests/replay.py` and import it in `closure-scope`. That would run the PR's copy of an un-owned file in a reachable, grading job, which `codeowners_gap.py --check` refuses. `closure.py` is code-owned and `closure-scope` already runs it. A blanket per-PR lane is refused permanently and is not offered.

**Owner review and rollback.** The PR is code-owned: `.github/workflows/tests.yml`, `.github/workflows/nightly.yml` (comment only) and `tests/closure.py`. **Rollback:** revert the branch's commits over `50af6174f`. The new job only ever runs on a pull request and is unrequired, so a revert changes no required context.

## Head

`799830bb54ecf6556f988e674150306968f471b9`, over merge base `50af6174f53c0f9bec3f705c3a4bb99615f71acc`.

## Mutation proof

Each mutant was a worktree of the fix head with one production line changed, run with `PYTHONPATH=tests/hastub python3 tests/entities.py`. The two failures inherited at the base (see Red checks) are left out:

- M1, reach predicate: `replay_reach` returns only fixture matches. Red: `replay reach: every cost file, the optimizer, the lane and a fixture run the timed lane; nothing beside them does` (missed `coordinator.py`, `sensor.py`, `process_worker.py`, ...), and `replay reach: a lane source naming no COST_FILES runs the lane, never skips it`.
- M2, wiring: the `python tests/closure.py replay-reach ... >> "$GITHUB_OUTPUT"` line deleted from `closure-scope`. Red: `the timed replay runs on a pull request whose diff reaches it, and on nothing else in tests.yml (nightly runs it in full)`.
- M3, fail-closed arm: `replay_decision` returns `False` when it cannot read `COST_FILES`. Red: `replay reach: a lane source naming no COST_FILES runs the lane, never skips it`.
- Failing test first: the checks ran at the base before the fix existed. `tests/entities.py` stopped at `AttributeError: module 'closure' has no attribute 'replay_reach'` (rc=1).

## Null control

- A blanket per-PR lane fires on every pull request. Over main's last 100 first-parent merges up to `50af6174f`, the rule fires on 7 (#2675, #2620, #2632, #2647, #2612, #2563, #2572). Each of these touched a cost file or the optimizer.
- Paths beside the reach that must not fire it (`const.py`, a `coordinator.py` one directory down, `tools/replay/export.py`, `tests.yml`, `README.md`, `tests/entities.py`, a non-JSON file under `tests/replay/`) read `[]`. This is the entities check above.
- `HPO_JOB_GRADES: nothing` is load-bearing. With it removed from the `replay` job in a scratch worktree, `codeowners_gap.py --check` reads `uncovered_files=3` (including `tests/replay.py`), rc=1. At the head it reads `uncovered_files=0`.

## Figures

- Reach over recent merges: `for c in $(git rev-list --first-parent --merges -n 100 50af6174f); do python3 tests/closure.py changed --base $c^1 --head $c > chg.txt; python3 tests/closure.py replay-reach --files-from chg.txt; done` printed `replay=true` on 7 of 100.
- The decision at this branch's own diff: `python3 tests/closure.py replay-reach --files-from <three-dot name list>` printed `replay=true` (the diff touches `tests/replay.py`), so this PR's `replay` job exercises itself.
- Local lane cost at the base: `PYTHONPATH=tests/hastub python3 tests/replay.py` printed `ALL 93 replay checks PASSED`, `replay lane wall time 67.6 s` on a 4-core box. The job's `timeout-minutes: 30` is sized from this plus the pip install.
- Entities at the head: `PYTHONPATH=tests/hastub python3 tests/entities.py`, 2427 of 2429 checks pass; the 2 that fail are the inherited ones under Red checks, and the four new replay checks are `ok`.
- `python3 tests/closure.py selftest`: `ALL 117 closure shrink pins PASSED`.
- `python3 dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`: `uncovered_files=0`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, no metric moved.
- `python3 tools/audit/archscore/score.py --diff 50af6174f53c0f9bec3f705c3a4bb99615f71acc`: `Architecture score: dS +0.0000 NULL`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `no closures or fast red predicted`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>` reads `MODE: FULL` (`.github/workflows/nightly.yml` changes the gate itself). CI runs the full suite. Locally I ran `entities.py`, `doc_claims.py` (203 checks), and the `run_always` lines `env_drift.py --claims-only`, `closure.py selftest`, `layout.py` and `harness_headers.py` (112 checks); all passed.

## Red checks

This branch turns no check red that is red because of the branch. Two `tests/entities.py` checks fail on this box at the base `50af6174f` as well as at the head. They are inherited, and this diff touches neither job:

- `gate-sweep.yml: on CI's completion, no concurrency, main's program on the trigger's run id alone, ...` (U0c)
- `graders-head-copy's delivery_status step is red only when this copy's exit differs from the base copy's, ...`

Main's push-side `tests / ci-ratchet` red (the 0-byte artifacts listing) is not this branch's either; its hotfix is in flight.

## Forward-carry

none

## Friction

- `roster: stale: R10-REPLAY-SCOPED's files list names tests/closures.json; the reach is a rule in tests/closure.py, and closures.json is untouched (alternative 1 above says why).` Carry: dismissed: plan artifact, named so the reviewer does not look for it.
- `roster: unclear: R10-REPLAY-SCOPED lists R10-REPLAY-LANE under after, whose roster stage is still in-progress (no handoff/r10-replay-lane code ref on origin; only its body ref), yet the pool dispatched this group; nothing here depends on its diff, and a later tests/replay.py edit there merges by the tree's usual merge, not a re-cut.` Carry: dismissed: the orchestrator's dispatch call, named here.
