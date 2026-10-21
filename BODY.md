Group: R10-FLOW-ANDON (registration pending: roster PR-B). Spec: pack file `dev/programme/flow-study/roster/groups/R10-FLOW-ANDON.json` at pin ff1beba2a24cab268cca5426cc390dbf21185cc0 (Lean study K8). Countermeasure for R10-RCA-ORCH-CONTINUITY (cited, not redone): two orchestrator stops went unnoticed for 6 h and 16 h because no loop wrote a liveness signal readable off the host.

Each `tick_loop.sh` pass now calls `heartbeat.sh --once`, which force-pushes `heartbeat/orchestrator` (parentless empty-tree commit, message `TICK-PASS <utc> relay=<..> tick=<rc>`, no host path) with the seat's credential, `-f --no-verify`, message through `ref_privacy.py guard`. A failed push prints `HEARTBEAT NOT PUSHED: <reason>` and the loop goes on. `heartbeat.sh --watch [--max-age 1200]` is the owner-side watcher's command (exit 1 and `HEARTBEAT STALE` past 20 min or when the ref is absent). Per the Seam carry it is a standalone job script with `--once`, not entrenched in `tick_loop.sh`. Alternative rejected: writing the push inline in `tick_loop.sh` (the design retires that file).

Round 2: `heartbeat.sh` is registered `guarded` in `ref_privacy.py`'s `PUSHERS` (it already called `ref_privacy.py guard --ref`; the registry did not name it, so `instrument-self-tests`' ref_privacy step refused its push site). The guard arm of `heartbeat.sh --self-test` now runs against the reachable bare remote and asserts the ref did not move, so it fails if the guard is skipped rather than only if a push errors; mutant `heartbeat-4` deletes the guard call. Alternative rejected: registering the file as `fixture` or another unguarded disposition, which would be false, since the production `--once` path pushes a caller-supplied message.

## Head

Code head: the tip of `handoff/r10-flow-andon` (a50dee030fe8164b5da015e441b2b7ac21323b02), a single-commit fix on top of 5005f02ef, which is the merge of origin/main 4b36dc730125 into round 1's 8f5807ae4 (merge, not rebase). `git merge-tree --write-tree origin/main HEAD` is clean at origin/main 4b36dc730125.

## Mutation proof

`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py` (all mutants, at this head) -> `RESULT survivors=0`. New this round: heartbeat-4 deletes the `ref_privacy.py guard` call in `hb_push` and is KILLED (`heartbeat self-test: 7 checks, 1 failed`). Round 1's per-file mutants re-run at this head and are all KILLED: tick_loop-1 (heartbeat call deleted), tick_loop-2 (failure print silenced), heartbeat-1 (`-f` dropped), heartbeat-2 (stale limit x100), heartbeat-3 (NOT PUSHED print dropped). Ids are per file, with no new S number. The registry entry's own mutant is the null control below: the tree without it refuses.

## Null control

M0 in the same harness run runs every `instrument-self-tests` seat step unmutated and reports `M0: 0 seat step(s) red`, the ref_privacy step included. For the registry, `python3 -I tools/audit/seat/ref_privacy.py --check` from a worktree at 5005f02ef (round 1's code merged with main, no registry entry) prints `REFUSE tools/audit/seat/heartbeat.sh:35: a push site in a file PUSHERS does not name` (the CI red reproduced); at this head it prints `0 refused`. The guard arm's null control is the reachable remote: with the guard in place the ref stays at the previous pass's sha.

## Figures

- `python3 -I tools/audit/seat/ref_privacy.py --check` -> ref_privacy's own summary line, `0 refused` at this head, `1 refused` at 5005f02ef
- `python3 -I tools/audit/seat/ref_privacy.py --self-test` -> `0 failed`
- `bash tools/audit/seat/heartbeat.sh --self-test` -> `heartbeat self-test: 7 checks, 0 failed`
- `bash tools/audit/seat/tick_loop.sh --self-test` -> `tick_loop self-test: 12 checks, 0 failed`
- `python3 tools/audit/seat/selftest_wiring.py --check` -> its own summary line, 0 unwired
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py` -> `RESULT survivors=0`
- `python3 tests/throwaway_git.py --check` -> 0 refused
- `python3 tests/structure.py` -> STRUCTURE RATCHET PASSED; no budget raised
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` -> MODE: SCOPED, runs tests/entities.py and tests/harness_headers.py
- `tests/entities.py` (seat venv, PYTHONPATH=tests/hastub) -> ALL ENTITY CHECKS PASSED
- `tests/harness_headers.py` (seat venv, PYTHONPATH=tests/hastub) -> ALL HARNESS HEADER CHECKS PASSED

## Red checks

`instrument-self-tests` was red at round 1's head 8f5807ae4: the ref_privacy step refused `tools/audit/seat/heartbeat.sh:35` as a push site `PUSHERS` does not name. It is this pull request's own red, and this round fixes it. The cheaper detector already exists: `python3 -I tools/audit/seat/ref_privacy.py --check` runs in seconds with no network, and `heartbeat.sh` was a new pushing file. Its standing cost is one local command, which round 1 did not run because the fixer's step list names `scope.run` and the self-tests of the touched files, not the registry checks over `tools/audit/seat/`. The `instrument-self-tests` mutant harness's M0, which runs every step of that job, would also have caught it. This round runs both. Carry: dismissed: one-off omission, the harness M0 already covers it

`nightly-status` is red. It grades `main`, and this diff touches `.github/workflows/governance.yml`, which it reads. It cannot be this pull request's own red. The latest scheduled `tests.yml` run on main is 39563978649 (2026-10-21T07:43Z, head c77f89d, before this branch's commits existed), read with one `actions/workflows/tests.yml/runs?event=schedule&branch=main` list call. Two jobs failed there:
- `slow`: `synthetic-dhw-only.json: cycle_cost`, with `loop_cpu_ratio 0.1138` over its 0.111 budget. #2548 (R10-REPLAY-CAP, merged 17:03Z, after that run) re-records that budget.
- `mutation-nightly`: `MUTATION TABLE BREACHED`, with 39.1% of drawn mutants surviving against a 30.0% cap. All ten survivors are in `custom_components/heatpump_optimizer/` modules.

Neither job's inputs are in this diff. This diff changes only `tools/audit/seat/`, one `instrument-self-tests` step in `governance.yml`, `INSTRUMENTS.md` and one harness under `dev/audit/harnesses/`. It touches no production module, no `tests/` driver, no budget and no `tests.yml`. The `governance.yml` hunk adds one step to the `instrument-self-tests` job, which neither nightly job runs. The cheaper detector for the survivor rate is the PR-time `mutation` job scoped to a diff's own production sites. It costs nothing extra, because it already runs on every pull request, and it was green here. For the `slow` cost budget no cheaper detector exists: the measurement depends on the runner class, as #2548's body records. The check turns green on the first concluded `tests.yml` run on main after #2548 if the survivor rate is also under its cap. Carry: dismissed: main's nightly lanes, not this diff

## Forward-carry

- The owner-side watcher (a scheduled cloud task every 15 min running `heartbeat.sh --watch`, notify on exit 1) is not in the tree and needs the owner to schedule it. Carry: dismissed: owner-scheduled by design (K8 "no repo change"), stated in INSTRUMENTS.md.
- R10-ORCH-MACHINERY must register `heartbeat.sh --once` as the beat's heartbeat job and then drop the call from `tick_loop.sh`. Carry: R10-ORCH-MACHINERY

## Friction

none
