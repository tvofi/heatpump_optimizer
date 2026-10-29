The heartbeat lane's stall sampler moves off py-spy on interpreters that ship CPython's own remote unwinder. `tests / nightly-status` went red on main because the scheduled Nightly 40806276912 failed `hb:positive_control` on `nightly-ha (stable)` (`FAILED: 2 of 64 checks: ['hb:positive_control', 'run:exit_status']`), and the manual re-run 40835853528 failed the same way. py-spy 0.4.2 cannot walk some CPython 3.14.9 Home Assistant processes. Past "Found interpreter" it spins in its stack walk, blocking or not, for the life of the process, so every try of the control times out.

`sample_command()` in `tests/nightly_ha.py` now returns the stdlib `_remote_debugging.RemoteUnwinder` snippet (`_STDLIB_SAMPLE`), run in a child, wherever `importlib.util.find_spec("_remote_debugging")` finds it (3.14+, the `stable` arm). Elsewhere it returns the staged `py-spy dump --nonblocking`, so the 3.13 floor keeps py-spy, where #2479 measured 0 hangs. Nothing else in `LoopHeartbeat` changes: `HB_CONTROL_TRIES`, `HB_CONTROL_HOLD_S` and the 5 s cut (now `SAMPLE_TIMEOUT_S`) are the same. The control still requires the out-of-process section, `sampler rc=0:`, to name `_hb_spin`, so it keeps its power: N1 to N3 below each still fail it.

Alternatives considered. A container respawn (option (b) of R10-NIGHTLY-HB-RESPAWN) lost: the stdlib unwinder read every process py-spy hung on, so a respawn would restart a process that never needed restarting, and would add a second container start to the lane. A longer py-spy timeout lost because the hang does not end. Making the timeout inconclusive lost because it changes what the check asserts.

## Head

`877f4addbf5ae580b76bc480264ddb72e120628d` (handoff/r10-fly-nightly-hb). Merge base `486e65cbd9c8451c01624f13b773feb6d722ad9b`. `origin/main` was at `279578074a17cb2c7f527f5e28da0de4e2006db0` on 2026-10-29T17:20Z. `git merge-tree --write-tree origin/main HEAD` reports no conflict, so the head is not merged forward (fixer.md step 6).

## Mutation proof

Mutant: delete the two predicate lines of `sample_command()` (`if importlib.util.find_spec("_remote_debugging") is not None:` and its `return [sys.executable, "-c", _STDLIB_SAMPLE]`). The tree then samples with py-spy on every interpreter, i.e. the base's behaviour. `python tests/entities.py` (CPython 3.14.10, `PYTHONPATH=tests/hastub`) on the mutant:

    1 of 2472 ENTITY CHECKS FAILED
    FAIL the stall sampler is the interpreter's own unwinder where it ships one, staged or not; else the staged py-spy, nonblocking; else none

Restored head: `ALL 2472 ENTITY CHECKS PASSED`. Diffing the mutant's FAIL lines against the head's leaves exactly that one line. On CPython 3.14 (CI's interpreter) the companion check `the stdlib sample of a real spinning process reads as the spin to the control, and of the same process outside it does not` runs the lane's own `_STDLIB_SAMPLE` against a real spinning child and passes at the head.

## Null control

The base tree's sampler (py-spy), in the real heartbeat container (homeassistant/home-assistant:stable = 2026.10.4, CPython 3.14.9, digest `sha256:23f4dfbb69ce76315dbc4de7915504f1c2dcecd7ca2648113a493a385972e133`), harness `--mode probe`, 60 runs over two sessions (20 + 40):

- 59 ok, and 1 FAIL that reproduces the nightly exactly: `a 600 ms spin read as 5276.4 ms; dump names the spin: True; py-spy rc=0 names it: False; try 3 of 3`.
- In that process, all 3 py-spy calls hung (state `R`, still spinning at the 4.5 s mark). A blocking (ptrace-stopping) `py-spy dump` hung too, `rc=143` at a 20 s cut. The stdlib unwinder, run against the same process during each hang, answered 6 of 6 times in 0.052 to 0.097 s and named `_hb_spin` every time.

The fix's own null controls (harness N1 to N3 on the head) are the check's power, not its pass. Each still fails `hb:positive_control` 2 of 2:

- N1 (the spin stalls nothing): `read as 2.2 ms` / `3.6 ms`.
- N2 (the watcher never dumps): `dump names the spin: False; sampler rc=0 names it: False`.
- N3 (the sampler reads a pid that does not exist): `dump names the spin: True; sampler rc=0 names it: False`, try 3 of 3.

## Figures

- Fix, `--mode side` (the unwinder samples; py-spy 0.4.2 runs beside it on the same process with a 4.5 s cut): 30 runs, `hb:positive_control` ok 30, fail 0. On 2 of the 30 processes (runs 20 and 26), the py-spy run beside the unwinder hung, `rc=143 names=0`, while the unwinder's sample passed the control on try 1. Rule: `SUMMARY ... ok=` and `spy_hung=` as `dev/audit/harnesses/r10_fly_nightly_hb.py` prints them; a run counts as hung when a py-spy call is still running at 4.5 s. Command: `python3 dev/audit/harnesses/r10_fly_nightly_hb.py --tree <head worktree> --mode side --runs 30 --out <dir> --image <stable+threadpoolctl>`. Null control: the base row below.
- Base, `--mode probe`: 60 runs (20 + 40), ok 59, fail 1, spy_hung 1. Command: `python3 dev/audit/harnesses/r10_fly_nightly_hb.py --tree <merge-base worktree> --mode probe --runs 40 --out <dir> --image <stable+threadpoolctl>` (and `--runs 20`). One hung process in 60 base runs, against 2 in 30 fix runs where py-spy ran beside the unwinder. Both are consistent with the roughly 6.7 % per-run py-spy hang rate in `dev/audit/rca/nightly-ha-pyspy-timeout.md`. The difference is the outcome: every base hang fails the control, and no fix run failed it.
- N1, N2, N3 on the head: fail 2 of 2 each. Command: `python3 dev/audit/harnesses/r10_fly_nightly_hb.py --tree <head worktree> --mode N1 --runs 2 --out <dir> --image <stable+threadpoolctl>` (likewise `N2`, `N3`).
- Scoped gate: `python3 tests/closure.py select --diff 486e65cbd9c8451c01624f13b773feb6d722ad9b --workdir <dir>` printed `MODE: SCOPED -- 5 script(s) run, 28 scoped out` (config_flow_steps, debug_collect, doc_claims, entities, harness_headers).
  - Run on CPython 3.14.10 at the head: `tests/entities.py` ALL 2472 PASSED (base 2470), `tests/doc_claims.py` ALL 203 PASSED (base 203), `tests/config_flow_steps.py` ok, `tests/debug_collect.py` ok.
  - `tests/harness_headers.py` fails 1 of 112 at both head and base, with the identical line `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py costs at most 50% of its CPU bound [cpu=245.9s against 240s]`. That is a CPU-time bound of an unrelated harness on this host. The new `r10_fly_nightly_hb.py` header checks pass.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

Instruments: the harness is `dev/audit/harnesses/r10_fly_nightly_hb.py`, landed in this PR (fixer.md step 18). The image is the tree's `docker_command(..., ["--heartbeat-only"], ("SYS_PTRACE",))` over `nightly_ha._stage(two_zone_dhw=True)`, with py-spy 0.4.2 from `tests/requirements-nightly-ha.txt` staged.

Class seams (step 8): the rule is `grep -n 'py-spy\|py_spy\|PY_SPY' tests/nightly_ha.py`, which returns 13 lines at the head. Each one's disposition:

- `sample_command` (the 3.13-floor arm): kept deliberately, pinned by the sampler-selection check. It is the only place that builds a sampler argv, and `LoopHeartbeat.dump` is its only caller.
- `stage_py_spy` / `_host_py_spy` and the staging call: still needed. The floor arm runs the staged binary, and the harness's `side` mode reads it.
- The constant comments above `_STDLIB_SAMPLE` / `SAMPLE_TIMEOUT_S` / `HB_CONTROL_TRIES`: true as written (they describe py-spy's measured behaviour).
- The `SYS_PTRACE` comment in the heartbeat-only launch ("py-spy reads this process from a child of it"): it names only py-spy, but the cap is equally what lets the stdlib unwinder read the process (`process_vm_readv` from a child). It is left as is, because the head is not re-cut for a comment. This is a wording-only seam for the fix reviewer.

## Red checks

`tests / nightly-status` (red on main from scheduled Nightly 40806276912, re-run 40835853528): this PR is the fix, measured above (base 1 of 60 runs fail the control as the nightly did, fix 0 of 30, with py-spy hanging beside it on 2 of those 30). Cheaper detector: none exists. The hang depends on py-spy 0.4.2 against the CPython build inside the current HA `stable` image on a real HA process. The stub suite never runs that interpreter or process, and the nightly lane is the only detector that does.

## Forward-carry

- The premise of R10-NIGHTLY-HB-RESPAWN changes. The hang is structural per process; the respawn is owed only if a nightly on a main carrying this fix fails `hb:positive_control` again with every try's sampler timed out or rc!=0. Landed in dev/programme/rosters/wave-r10-groups.json, the group's `carry` (commit d63e5544d). Carry: R10-NIGHTLY-HB-RESPAWN

## Friction

- fixer.md-step5: cost: the seat's container ships CPython 3.11, which cannot parse the tree, and has no venv or `node`/`jq` toolchain. The gate was run in a `python:3.14` container with `tests/requirements-ci.txt` plus the host's node, jq and gh. Docker Hub answered 429 to the HA image pull, so it came via `mirror.gcr.io`. Carry: dismissed: seat environment cost, not a policy defect
