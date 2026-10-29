The heartbeat lane's stall sampler moves off py-spy on interpreters that ship CPython's own remote unwinder. The scheduled Nightly 40806276912 (head ee48937) failed `hb:positive_control` on `nightly-ha (stable)` (`FAILED: 2 of 64 checks: ['hb:positive_control', 'run:exit_status']`). py-spy 0.4.2 cannot walk some CPython 3.14.9 Home Assistant processes. Past "Found interpreter" it spins in its stack walk, blocking or not, for the life of the process, so every try of the control is cut at the sample timeout. The manual re-run 40835853528 (head 486e65c) did **not** fail that way: its `nightly-ha (stable)` job 123320354418 passed. Its one red is the `slow` job 123320354392, step "Closed-loop simulation", which this diff does not touch. That run is the one `tests / nightly-status` reads now (`## Red checks`).

`sample_command()` in `tests/nightly_ha.py` now returns the stdlib `_remote_debugging.RemoteUnwinder` snippet (`_STDLIB_SAMPLE`), run in a child, wherever `importlib.util.find_spec("_remote_debugging")` finds it (3.14+, the `stable` arm). Elsewhere it returns the staged `py-spy dump --nonblocking`, so the 3.13 floor keeps py-spy, where #2479 measured 0 hangs. Nothing else in `LoopHeartbeat` changes: `HB_CONTROL_TRIES`, `HB_CONTROL_HOLD_S` and the 5 s cut (now `SAMPLE_TIMEOUT_S`) are the same. The control still requires the out-of-process section, `sampler rc=0:`, to name `_hb_spin`, so it keeps its power: N1 to N4 below each still fail it.

Round 2 repairs the committed control-power instrument `dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py`, which round 1's rename broke (commit b8005392b). Its mutant targets follow the renamed names: `self.sample_timeout`, `SAMPLE_TIMEOUT_S`, `sample_timeout=` and `"sampler rc=0:"`. The block it extracts from `tests/entities.py` now runs with every module-level stdlib `import` that precedes it in that file, read by `ast`. When entities.py runs whole, the block sees those same names, so the next stdlib name the block reads does not break the harness again. The harness gains `M11-pyspy-first`, which mutates the new `sample_command()` predicate. The head then merges the live PR branch (67be951d3), which carries 2f033a59a: the group harness's Docker-free `--inproc` arm, which the figures below use.

Alternatives considered. A container respawn (option (b) of R10-NIGHTLY-HB-RESPAWN) lost. The stdlib unwinder read every process py-spy hung on, so a respawn would restart a process that never needed restarting, and would add a second container start to the lane. A longer py-spy timeout lost because the hang does not end. Making the timeout inconclusive lost because it changes what the check asserts. For the harness, hard-coding `import subprocess` into its header lost to the `ast` read: it fixes this instance and breaks again on the block's next stdlib name.

## Head

`b23e91e0dfc5042485500b9c11f02b2872c3d752` (handoff/r10-fly-nightly-hb). It is b8005392b, the harness repair on ac7353951, merged with origin/fix/r10-fly-nightly-hb at 67be951d3. Merge base `e5ddba1fad5e6eccfeceaeaaa249bc459963405b`, which `origin/main` still was at 2026-10-29T21:10Z. `git merge-tree --write-tree origin/main HEAD` exits 0, no conflict. Every figure below was taken at this head unless it is marked as an earlier seat's.

## Mutation proof

Production mutant: delete the fix's predicate in `sample_command()` (`if importlib.util.find_spec("_remote_debugging") is not None:` and its `return`). The sampler is then py-spy wherever it is staged, which is the base's behaviour. Two instruments ran it at this head under CPython 3.14.6:

- `PYTHONPATH=tests/hastub python dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py`, entry `M11-pyspy-first`:

      M11-pyspy-first KILLED by: the stall sampler is the interpreter's own unwinder where it ships one, staged or not; else the staged py-spy, nonblocking; ...

- `python dev/audit/harnesses/r10_fly_nightly_hb.py --tree <head> --mode N4 --inproc hung --runs 2 --out <dir>`: `SUMMARY mode=N4 inproc=hung python=3.14.6 runs=2 ok=0 fail=2`. Every try reads `(True, True, False)`, with gaps 5290.5 to 5301.9 ms and `sampler=py-spy`. That is the base's failure, back.

The whole mutant harness at this head:

    M0-null all checks pass
    SUMMARY killed=15 survived=0 null=ok
    rc=0

The 15 mutants are M1 to M11, X1, X2, X3 and X5, every entry of `MUTANTS` except M0. Each line prints `KILLED by:` with a named check.

Harness mutant (the round-2 repair): remove the import injection from `block()`, i.e. `return "".join(lines[start:end])`, and run M0 alone:

    M0-null FAILS: (block did not run: rc=1 '... NameError: name 'subprocess' is not defined ...')
    SUMMARY killed=0 survived=0 null=FAIL

That is the reviewer's failure, reproduced: the injection is what makes the null pass. The unrepaired harness at ac7353951 reads `M0-null FAILS: ... NameError ...`, then `M2-timeout-30: the mutated site occurs 0 times, not once`, `rc=1`. That matches `verdict/2964`'s evidence.

## Null control

The base is `origin/main` e5ddba1fa, which carries py-spy as its sampler. It ran under the same harness and the same CPython 3.14.6:

- `--mode plain --inproc hung --runs 3`: `ok=0 fail=3`. Every try reads `(True, True, False)`, gaps 5273.9 to 5327.6 ms, `sampler=py-spy`. This is the nightly's signature (CI: 5308.8 ms = `HB_DUMP_S` + the 5 s cut + slack): the failing test first, at the base.
- `--mode plain --inproc real --runs 10`: `ok=10 fail=0`, gaps 600.3 to 600.6 ms on the runs shown. The base passes on a py-spy that answers, so what reddens it is the hung py-spy, not the harness.

At the head, the control's power under `--inproc real`, 2 runs each:

- N1 (the spin stalls nothing): `ok=0 fail=2`, readings `(False, False, False)`, gaps 1.6 to 6.5 ms.
- N2 (the watcher never dumps): `ok=0 fail=2`, `(True, False, False)`.
- N3 (the sampler reads a pid that does not exist): `ok=0 fail=2`, `(True, True, False)`.

The mutant harness's own null control is M0 at this head (all checks pass). The control for the harness repair is the harness mutant above.

## Figures

All at this head, CPython 3.14.6 (uv-installed venv, `tests/requirements-ci.txt` plus `py-spy==0.4.2`). The rule for each `r10_fly_nightly_hb.py` row is its `SUMMARY ... ok= fail=` line, with one row per run; a run is ok when `hb:positive_control` passes on some try. Command form: `python dev/audit/harnesses/r10_fly_nightly_hb.py --tree <worktree> --mode <m> --inproc <real|hung> --runs <n> --out <dir>`.

| tree | mode | inproc | runs | ok | fail |
|---|---|---|---|---|---|
| base e5ddba1fa | plain | hung | 3 | 0 | 3 |
| base e5ddba1fa | plain | real | 10 | 10 | 0 |
| head | plain | hung | 10 | 10 | 0 |
| head | plain | real | 10 | 10 | 0 |
| head | N1 | real | 2 | 0 | 2 |
| head | N2 | real | 2 | 0 | 2 |
| head | N3 | real | 2 | 0 | 2 |
| head | N4 | hung | 2 | 0 | 2 |

- The head's `plain hung` runs read `sampler=python` with gaps 600.3 to 600.4 ms on the runs shown. On the py-spy that never returns, the fix samples with the unwinder and passes on try 1. Null control: the base row on the same hung py-spy, 0 of 3. This measures the sampler in this interpreter, never real Home Assistant (the harness's docstring says the same).
- Mutant harness: `SUMMARY killed=15 survived=0 null=ok`, rc=0 (`## Mutation proof`). Null control: `M0-null FAILS` at ac7353951, and at this head with the import injection removed.
- Real-container figures, an earlier seat's and **not re-taken here**: this container's Docker daemon is not running (`docker info` rc=1). They were taken on the same `tests/nightly_ha.py`: `git diff 877f4addb HEAD -- tests/nightly_ha.py` is empty. Image homeassistant/home-assistant:stable 2026.10.4, CPython 3.14.9, digest `sha256:23f4dfbb69ce76315dbc4de7915504f1c2dcecd7ca2648113a493a385972e133`.
  - Base `--mode probe`: 60 runs, ok 59, fail 1. In the failing process all 3 py-spy calls hung, and the stdlib unwinder answered 6 of 6 times in 0.052 to 0.097 s.
  - Fix `--mode side`: 30 runs, ok 30, with py-spy beside the unwinder hung on 2.
- CI at ac7353951, same `nightly_ha.py`, read in `verdict/2964` evidence:
  - `nightly-ha (stable)` passes `hb:positive_control` on try 1, with the sampler section in the stdlib unwinder's format.
  - `nightly-ha (2025.2.0)` passes, with py-spy's format: the 3.13 floor still samples with py-spy.
- Scoped gate: `python tests/closure.py select --diff e5ddba1fad5e6eccfeceaeaaa249bc459963405b --workdir <dir>` printed `MODE: SCOPED -- 5 script(s) run, 28 scoped out`. Each ran at this head with `PYTHONPATH=tests/hastub`:
  - `tests/entities.py`: `ALL 2473 ENTITY CHECKS PASSED`.
  - `tests/config_flow_steps.py`: `ALL 534 checks PASSED`.
  - `tests/debug_collect.py`: `ALL 158 DEBUG COLLECT CHECKS PASSED`.
  - `tests/doc_claims.py`: `ALL 203 checks PASSED`.
  - `tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `run.sh`'s `run_always` lines:
  - `tests/env_drift.py --claims-only e5ddba1fa`: `claims hygiene: ... ok`.
  - `tests/closure.py selftest`: `ALL 117 closure shrink pins PASSED`.
  - `tests/layout.py`: `layout self-test: ok`.
  - `tests/harness_headers.py`: as above.
- `python tests/structure.py`: `STRUCTURE RATCHET PASSED`.

Instruments: `dev/audit/harnesses/r10_fly_nightly_hb.py` (the group's, with 2f033a59a's `--inproc` arm) and `dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py` (repaired here). Both are landed in this PR (fixer.md step 18).

Class seams (step 8). The class is every consumer of a name this diff renamed. Round 1's rule read only `tests/nightly_ha.py` and missed the mutant harness. This round's rule reads the whole tree:

    git grep -n -e 'spy_timeout' -e 'PY_SPY_TIMEOUT_S' -e 'py-spy rc=' -e '_py_spy_path' -e 'py_spy=' -e 'py-spy did not run' -- .

At ac7353951 it returns 8 lines outside `dev/audit/rca/`, 6 of them in `r10_nightly_pyspy_retry_mutants.py`. That is the null control: the rule finds the seam the reviewer named. At this head it returns no line in that harness. The lines it returns:

- `dev/audit/rca/nightly-ha-pyspy-timeout.md` (8 lines) and `dev/programme/carries/carry-201.json:105`: records that recount py-spy-era output, left as written (step 10).
- `dev/audit/harnesses/r10_fly_nightly_hb.py:71`: `echo "blocking py-spy rc=$?"`. This is that harness's own log line for its blocking-py-spy probe, which really is py-spy, so it is correct as written.
- Consumers that import `tests/nightly_ha.py`, from `git grep -l nightly_ha -- dev/audit/harnesses`: `r10_fly_nightly_hb.py` and the mutant harness (both run above), and `r10_nightly_pyspy_retry.py`. That last one uses only `nightly_ha._stage` (it has no `LoopHeartbeat` or sampler reference), so it is untouched by the rename.

Round 1's in-file dispositions still hold:

- `sample_command` (the 3.13-floor arm): pinned by the sampler-selection check and by M11 / N4.
- `stage_py_spy` / `_host_py_spy` and the staging call: needed by the floor arm and the harness's `side` mode.
- The constant comments: true as written.
- The `SYS_PTRACE` comment in the heartbeat-only launch: it names only py-spy, but the cap equally serves the stdlib unwinder. Wording only, left for the fix reviewer.

## Red checks

`tests / nightly-status`: it reads the last verification dispatch, 40835853528 (head 486e65c), whose only failing job is `slow` (job 123320354392, step "Closed-loop simulation"). Its `nightly-ha (stable)` passed. This diff does not touch the closed-loop simulation, so the check is main-graded and stays red after this merge until main's `slow` lane is green. That red is the orchestrator's on main (`defect-root-cause.md`). This PR is the fix for the earlier red, the scheduled 40806276912's `hb:positive_control`, measured above: base 0 of 3 against a hung py-spy, head 10 of 10. Cheaper detector for that hang: none exists. It depends on py-spy 0.4.2 against the CPython build inside the current HA `stable` image, on a real HA process. The stub suite never runs that process, and the nightly lane is the only detector that does. The `--inproc hung` arm now replays the failure's shape without that process.

Carry 1 (the roster's: "fix the flaky nightly; it turned tests / nightly-status red on every PR that touches what that check reads"). Answered for the flake it was registered on: `hb:positive_control`'s py-spy hang, fixed and measured above. Not answered for the check's present red, which is the `slow` lane's closed-loop simulation in 40835853528. That is a distinct failure this diff does not touch, so `nightly-status` stays red until main's `slow` lane is green.

Round 1 broke the committed mutant harness. A cheaper detector did exist there: the class-seam rule, had it read the tree rather than one file, returns the harness's six lines. This round's rule does (`## Figures`). No CI check runs that harness, so no check went red.

## Forward-carry

- The premise of R10-NIGHTLY-HB-RESPAWN changes. The hang is structural per process; the respawn is owed only if a nightly on a main carrying this fix fails `hb:positive_control` again with every try's sampler timed out or rc!=0. It landed in dev/programme/rosters/wave-r10-groups.json as the group's `carry` (commit d63e5544d). That group inherits the control-power instrument `dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py`, which runs again at this head (`SUMMARY killed=15 survived=0 null=ok`). Carry: R10-NIGHTLY-HB-RESPAWN

## Friction

- fixer.md-step6: cost: while this seat worked from its dispatched head ac7353951, another seat's commit 2f033a59a reached `handoff/r10-fly-nightly-hb` and was merged into the PR branch. The first push was refused as non-fast-forward. The seat merged the live branch (no conflict) and re-took every figure at the merged head, rather than overwriting the ref. Carry: dismissed: two seats on one topic is the dispatcher's to sequence; the merge kept both seats' commits
- fixer.md-step5: cost: the seat's container ships CPython 3.11, which cannot parse the tree, and its Docker daemon is not running. The gate and the harnesses were run in a uv-installed CPython 3.14.6 venv. Carry: dismissed: seat environment cost, not a policy defect
