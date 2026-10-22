Group: R10-FLOW-ANDON (registration pending: roster PR-B). Spec: pack file `dev/programme/flow-study/roster/groups/R10-FLOW-ANDON.json` at pin ff1beba2a24cab268cca5426cc390dbf21185cc0 (Lean study K8). Countermeasure for R10-RCA-ORCH-CONTINUITY (cited, not redone): two orchestrator stops went unnoticed for 6 h and 16 h because no loop wrote a liveness signal readable off the host.

Each `tick_loop.sh` pass now calls `heartbeat.sh --once`, which force-pushes `heartbeat/orchestrator` (parentless empty-tree commit, message `TICK-PASS <utc> relay=<..> tick=<rc>`, no host path) with the seat's credential, `-f --no-verify`, message through `ref_privacy.py guard`. A failed push prints `HEARTBEAT NOT PUSHED: <reason>` and the loop goes on. `heartbeat.sh --watch [--max-age 1200]` is the owner-side watcher's command (exit 1 and `HEARTBEAT STALE` past 20 min or when the ref is absent). Per the Seam carry it is a standalone job script with `--once`, not entrenched in `tick_loop.sh`. Alternative rejected: writing the push inline in `tick_loop.sh` (the design retires that file).

Round 2: `heartbeat.sh` is registered `guarded` in `ref_privacy.py`'s `PUSHERS` (it already called `ref_privacy.py guard --ref`; the registry did not name it, so `instrument-self-tests`' ref_privacy step refused its push site). The guard arm of `heartbeat.sh --self-test` now runs against the reachable bare remote and asserts the ref did not move, so it fails if the guard is skipped rather than only if a push errors; mutant `heartbeat-4` deletes the guard call. Alternative rejected: registering the file as `fixture` or another unguarded disposition, which would be false, since the production `--once` path pushes a caller-supplied message.

## Head

`c8b85d11564a9f429fafbe3353a4b8746e45b187` merges the authored code head `841c65da4deed8c78dd73616b56aa0661b830c3a` and then merges origin/main `46e368127` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

Code head: the tip of `handoff/r10-flow-andon` (841c65da4deed8c78dd73616b56aa0661b830c3a), the merge of origin/main 5a755f53efda (#2529) into PR head 7a3fc062b4cfe43acc34dc24481dd21bc1a073ac (merge, not rebase). Figures below were taken at that head against origin/main 5a755f53efda, 2026-10-21T22:34Z. `git merge-tree --write-tree origin/main HEAD` is clean at that tip; at 7a3fc062b it exits 1 (the conflict this round resolves).

## Conflict resolution

One file, `dev/audit/harnesses/r10_seat_selftests_mutants.py`, two hunks, both resolved by keeping both sides:
- The module docstring's id sentence: main says `S01..S38 each plant one production-line`, this branch said `S01..S34 and the per-file ids (tick_loop-N, heartbeat-N) each plant...`. Kept: `S01..S38 and the per-file ids (tick_loop-N, heartbeat-N) each plant one production-line`.
- The tail of `MUTANTS`: main appended S35..S38 (#2444's forward-carry: three `handoff_push.sh` push lines and the `merge_pr.sh` merge line), this branch appended tick_loop-1, tick_loop-2, heartbeat-1..heartbeat-4. Kept main's four first, then this branch's six, each tuple byte-identical to its side.
No other file conflicted; the rest of #2529 (governance.yml, closure.py, closures.json, INSTRUMENTS.md, cloud_relay.sh, handoff_push.sh, a new harness and two delivery rows) merged automatically.

## Mutation proof

`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py` (every mutant, at 841c65da4) -> `M0: 0 seat step(s) red`, then every mutant `KILLED`, `RESULT survivors=0`, exit 0.
- This PR's six: tick_loop-1 KILLED (heartbeat call deleted), tick_loop-2 KILLED (`tick_loop self-test: 12 checks, 1 failed`), heartbeat-1..heartbeat-4 KILLED (each `heartbeat self-test: 7 checks, 1 failed`).
- Main's four from #2529: S35, S36, S37 KILLED (each `handoff_push self-test: 2 checks, 1 failed`), S38 KILLED (`merge_pr self-test: 16 checks, 2 failed`).
- S01..S34, S04U and W1..W3 also KILLED.

## Null control

For the resolution keeping both sides: a scratch probe parses the `MUTANTS` id set at three revisions (`ast` over `git show <rev>:<path>`). It prints `main=35 branch=37 head=41 union=41 missing_from_head=[] extra_in_head=[]` and exits 0 at HEAD. Run with origin/main in HEAD's place (a main-side-only resolution) it lists the six andon ids missing and exits 1. Run with 7a3fc062b in HEAD's place (a branch-side-only resolution) it lists S35..S38 missing and exits 1. For the mutants, M0 in the same harness run runs every `instrument-self-tests` seat step unmutated and every step is rc=0, so each KILLED is the mutant's. Round 2's registry null control (`ref_privacy.py --check` refuses heartbeat.sh at 5005f02ef) is not affected by this merge and was not re-taken.

## Figures

All at 841c65da4, origin/main 5a755f53efda, 2026-10-21T22:34Z:
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py` -> `RESULT survivors=0`, M0 `0 seat step(s) red`
- `bash tools/audit/seat/heartbeat.sh --self-test` -> `heartbeat self-test: 7 checks, 0 failed`
- `bash tools/audit/seat/tick_loop.sh --self-test` -> `tick_loop self-test: 12 checks, 0 failed`
- `python3 -I tools/audit/seat/ref_privacy.py --check` -> ref_privacy's own summary line, `0 refused`
- `python3 -I tools/audit/seat/ref_privacy.py --self-test` -> `0 failed`
- `python3 tools/audit/seat/selftest_wiring.py --check` -> its own summary line, 0 unwired
- `python3 tests/throwaway_git.py --check` -> 0 refused
- `python3 tests/structure.py` -> STRUCTURE RATCHET PASSED; no budget raised
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` -> MODE: SCOPED, runs tests/entities.py and tests/harness_headers.py
- `tests/entities.py` (seat venv, PYTHONPATH=tests/hastub) -> ALL ENTITY CHECKS PASSED
- `tests/harness_headers.py` (seat venv, PYTHONPATH=tests/hastub) -> ALL HARNESS HEADER CHECKS PASSED

## Red checks

At PR head 7a3fc062b the one red check is `nightly-status`. This head has not run CI yet; it inherits that check's input unchanged. `nightly-status` grades the scheduled runs on `main`, not this diff. Its failing inputs are main's nightly lanes. This diff touches no production module, no `tests/` driver, no budget and no `tests.yml`. Its `governance.yml` hunk adds one step to `instrument-self-tests`, which no nightly job runs. The cheaper detector for main's nightly reds is the PR-time `mutation` job and the scoped gate, which already run on every pull request and were green at 7a3fc062b. Carry: dismissed: main's nightly lanes, not this diff

`ci-ratchet` was skipped on this PR. Main's own red there is runner-speed variance, and R10-CI-LAYOUT owns it. It is not this diff's: this diff adds no CI job and changes no budget. Carry: R10-CI-LAYOUT

`instrument-self-tests`: read from the check-runs API per commit (`repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs`, 2026-10-22). It concluded `failure` at 8f5807ae45b079dc5978e925b3f56fb2008af3fc (round 1 head, completed 2026-10-21T17:56:21Z) on an unregistered push site (`heartbeat.sh` absent from `ref_privacy.py`'s `PUSHERS`), and round 2 fixed that cause. It concluded `success` at 7a3fc062b4cfe43acc34dc24481dd21bc1a073ac (completed 2026-10-21T21:10:47Z), and 841c65da4 has no check run yet. The harness M0 above re-runs every step of that job green at 841c65da4. Carry: dismissed: fixed in round 2, green at 7a3fc062b

## Forward-carry

- The owner-side watcher (a scheduled cloud task every 15 min running `tools/audit/seat/heartbeat.sh --watch`, notify on exit 1) is not scheduled in the tree and needs the owner to schedule it. Carry: dismissed: owner-scheduled by design (K8 "no repo change"), stated in INSTRUMENTS.md.
- R10-ORCH-MACHINERY must register `heartbeat.sh --once` as the beat's heartbeat job and then drop the call from `tick_loop.sh`. Carry: R10-ORCH-MACHINERY

## Friction

The scoped scripts need the seat venv.
