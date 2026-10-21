Group: R10-FLOW-ANDON (registration pending: roster PR-B). Spec: pack file `dev/programme/flow-study/roster/groups/R10-FLOW-ANDON.json` at pin ff1beba2a24cab268cca5426cc390dbf21185cc0 (Lean study K8). Countermeasure for R10-RCA-ORCH-CONTINUITY (cited, not redone): two orchestrator stops went unnoticed for 6 h and 16 h because no loop wrote a liveness signal readable off the host.

Each `tick_loop.sh` pass now calls `heartbeat.sh --once`, which force-pushes `heartbeat/orchestrator` (parentless empty-tree commit, message `TICK-PASS <utc> relay=<..> tick=<rc>`, no host path) with the seat's credential, `-f --no-verify`, message through `ref_privacy.py guard`. A failed push prints `HEARTBEAT NOT PUSHED: <reason>` and the loop goes on. `heartbeat.sh --watch [--max-age 1200]` is the owner-side watcher's command (exit 1 and `HEARTBEAT STALE` past 20 min or when the ref is absent). Per the Seam carry it is a standalone job script with `--once`, not entrenched in `tick_loop.sh`. Alternative rejected: writing the push inline in `tick_loop.sh` (the design retires that file).

## Head

8f5807ae45b079dc5978e925b3f56fb2008af3fc (code head; merge of origin/main f2fb1b0e950ecd047b7f08b3adef93776a622540 is a no-op, `git merge-tree --write-tree origin/main HEAD` clean).

## Mutation proof

`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py tick_loop-1 tick_loop-2 heartbeat-1 heartbeat-2 heartbeat-3 S26 S31 S34 W2` -> RESULT survivors=0. tick_loop-1 deletes the heartbeat call (KILLED), tick_loop-2 silences the failure print (KILLED, 1 failed), heartbeat-1 drops the `-f` (KILLED), heartbeat-2 widens the stale limit x100 (KILLED), heartbeat-3 drops the NOT PUSHED print (KILLED). Ids are per-file (standing rule a), no new S number. Existing S26/S31/S34/W2 still killed.

## Null control

Unmutated, every seat step passes first (the harness refuses NOT RUN otherwise). Watcher null controls in `heartbeat.sh --self-test`: a fresh ref does not alert, a 30-min-old ref alerts, an absent ref alerts, a refused push prints its reason. The base `tick_loop.sh --self-test` had 8 checks; now 12 (4 added: call once with the pass line, failing heartbeat printed, real pass moves the ref on a bare remote, refused push printed).

## Figures

- `bash tools/audit/seat/tick_loop.sh --self-test` -> "tick_loop self-test: 12 checks, 0 failed"
- `bash tools/audit/seat/heartbeat.sh --self-test` -> "heartbeat self-test: 7 checks, 0 failed"
- `python3 tools/audit/seat/selftest_wiring.py --check` -> 39 self-testing, 39 wired, 0 unwired (new governance.yml step added)
- `python3 tests/throwaway_git.py --check` -> 0 raw git init or clone sites refused (self-tests build repos through tests/throwaway_git.sh)
- `python3 tests/structure.py` -> STRUCTURE RATCHET PASSED; no budget raised
- `python3.13 tests/entities.py` -> ALL 2381 ENTITY CHECKS PASSED; `tests/harness_headers.py` -> ALL 109 HARNESS HEADER CHECKS PASSED
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` -> MODE: SCOPED, runs tests/entities.py and tests/harness_headers.py.

## Red checks

`nightly-status` is red, and it grades `main`, not this diff: it reads the last concluded scheduled run of `tests.yml` (run 39563978649, 2026-10-21 07:43Z, head c77f89dc, failure; the two before it, 39387919507 and 39218718759, also failure; 39106988523 on 2026-10-18 succeeded). This diff touches `.github/workflows/governance.yml`, which the exemption lists as read by the check, so the red is measured rather than assumed. Two jobs of that run failed: `slow`, step "Replay recorded days through the real coordinator" (`tests/replay.py`), and `mutation-nightly`, step "Drive the table over the whole package" (`tests/mutation_table.py --scope full`). Neither reads a file of this diff: the diff is `governance.yml` (a new step in a different workflow), `tools/audit/seat/heartbeat.sh`, `tick_loop.sh`, `INSTRUMENTS.md` and `dev/audit/harnesses/r10_seat_selftests_mutants.py`, none in `custom_components/`, `tests/replay.py` or the mutation table's scope. The run's head c77f89dc is an ancestor of `main` and of this code head, so the red existed before the first commit of this branch and cannot be caused by it. `slow` is the `loop_cpu_ratio` defect that #2548 (merged) answers; the `mutation-nightly` red is the orchestrator's on `main` (fix the lane and dispatch Tests on the default branch). The cheaper detector for this pull request's own risk is the new `Show the heartbeat andon refusing its own fixtures` step plus `selftest_wiring.py --check` (39 wired, 0 unwired), seconds each. No cheaper detector for the nightly red exists on this diff, because it does not touch what the red is about. Standing cost of the answer: none.

Carry: dismissed main-lane nightly red, orchestrator owns it.

`instrument-self-tests` is red at this code head and the cause is this pull request's own: step "Refuse a push that names the host, and an unregistered pusher" runs `python3 -I tools/audit/seat/ref_privacy.py --check`, which refuses `tools/audit/seat/heartbeat.sh:35` (the `git push -f` of the heartbeat ref) as "a push site in a file PUSHERS does not name". Reproduced locally at 8f5807ae4 (`--self-test` 66 checks, 0 failed; `--check` 1 refused). The push is already guarded (`ref_privacy.py guard` runs at line 31 before it), so the missing piece is only the registration: a `"tools/audit/seat/heartbeat.sh": (GUARDED, ...)` entry in `PUSHERS` in `tools/audit/seat/ref_privacy.py`. This is a code change; this return is body-only and changed none, so the red stays open until a code round lands that entry. The cheaper detector exists and fired: `ref_privacy.py --check` takes seconds and the fixer's own pass should have run it (it is in the gate for any diff adding a push site); standing cost of making it routine is nil, it is an existing job step. The `pr-contract` reds on the head are the body refusals this section answers.

Carry: R10-FLOW-ANDON register heartbeat.sh in ref_privacy PUSHERS in the next code round.

## Forward-carry

- The owner-side watcher (a scheduled cloud task every 15 min running `heartbeat.sh --watch`, notify on exit 1) is not in the tree and needs the owner to schedule it. Carry: dismissed: owner-scheduled by design (K8 "no repo change"), stated in INSTRUMENTS.md.
- R10-ORCH-MACHINERY must register `heartbeat.sh --once` as the beat's heartbeat job and then drop the call from `tick_loop.sh`. Carry: R10-ORCH-MACHINERY

## Friction

none
