Fix review: blocked 34360097287696f1baa1b22fb2a481d3858b6ca6 harness: hb:untouched_exit fails in real Home Assistant on both images (0 ticks), so this PR turns nightly-ha red where main's last scheduled run was green

bus-nonce: fff8b70390f72a069a27efc8e34bde49

Round 1. Reviewed from a detached worktree at 34360097287696f1baa1b22fb2a481d3858b6ca6, which is the live head when this was posted. The merge base is 165510077. The brief's contract diff is empty, so the brief is current.

## RESULT lines

- RESULT nightly-ha (stable), dispatch run 37079055904, job 111075321221: `FAILED: 2 of 62 checks: ['hb:untouched_exit', 'run:exit_status']`
- RESULT nightly-ha (2025.2.0), job 111075321451: `FAILED: 2 of 62 checks: ['hb:untouched_exit', 'run:exit_status']`
- RESULT hb:untouched_exit: stable `max gap 1.2 ms over 0 tick(s)`, 2025.2.0 `max gap 7.3 ms over 0 tick(s)`. Both have reloaded=False, as wanted.
- RESULT hb:positive_control: `a 600 ms spin read as 600.2 ms; dump names the spin: True` on both images. The first dump came at `stall >= 252 ms`.
- RESULT hb:changed_save: stable 11.1 ms over 2363 ticks; 2025.2.0 201.4 ms over 4331 ticks. 0 dumps.
- RESULT hb:menu_saves: stable 12.2 ms over 2866 ticks; 2025.2.0 14.9 ms over 4347 ticks. 0 dumps.
- RESULT py-spy on the Alpine image: `py-spy rc=0` on both images. It named `Thread 1 (active+gil) _hb_spin (nightly_ha.py:1713)`.
- RESULT main's control: scheduled Tests run 36984959667 at 492d8401 (2026-10-02) had nightly-ha (stable) success and nightly-ha (2025.2.0) success.
- RESULT the reviewer's mutants (my driver, `rmut.py` in evidence; entities.py under the R9-F11.4 venv). The head baseline was `ALL 2094 ENTITY CHECKS PASSED`.
  - R1, the `_beat` gap line deleted: rc=1, 1 of 2094 failed. Killed.
  - R7, `stop()` never sets the watcher's event: rc=1, 2 of 2094 failed. Killed.
  - R8, `stop()` never cancels the tick: rc=0, `ALL 2094 ENTITY CHECKS PASSED`. **Survived.**
  - R3, SYS_PTRACE dropped from `_run_outside`'s third `_docker` call, and R4, `_stage` never calling `stage_py_spy`: the run hung (0% CPU for 29 min, on a near-full disk) and I killed it. By inspection, no entities.py check reads those call sites. The only `_run_outside` source check is the A3(e) one, and the cap check calls `docker_command` with `caps` passed by hand. Nightly would stay green too, because `hb:positive_control` needs only the Python stack. **Both survive by inspection, not by a run.**
- RESULT PR-head CI (`waitci.sh`): `DONE total=38`. NOTGREEN: nightly-ha (2025.2.0), nightly-ha (stable), nightly-status, pr-contract.
- RESULT `git merge-tree --write-tree origin/main <head>`: rc=0, no conflict. VERSION, the manifest, RELEASE_NOTES and tests/golden are untouched.
- RESULT the py-spy hashes against PyPI's JSON for 0.4.2: `aeb03234…a52f` is `manylinux_2_5_x86_64` and `142887e9…2cce` is `manylinux_2_17_aarch64`. Both match exactly.

## Why blocked

1. **The new check fails in the place it exists to run.** `hb:untouched_exit` needs `ticks > 0`. The untouched scenario finishes in 1.2 to 7.3 ms without the 1 ms `call_later` ever firing. `_async_hb_settle` returns at once because the coordinator that was not reloaded already has `_optimization_result`. So the window closes before one tick, and the container exits 1 on both images. Merged, it turns main's green nightly-ha red every night. The measurement itself is not blind: `stop()` folds in `now - _last`, so the 7.3 ms is real. The guard is wrong for a window this short, and the window is wrong for the question. An untouched exit's deferred work, such as a scheduled refresh or a listener after the abort, lands after the measurement has stopped. Repair is the fixer's call. One shape: hold every scenario's window open for a fixed minimum, for example several seconds after the last action, before settling. A tick count over a window that never opened then can no longer pass or fail by accident.
2. **The red checks are unanswered** (fix-review step 11). The live body's `## Red checks` still reads "none: no check has run on this branch yet". pr-contract refuses on that: three ERRORs for `mutation-nightly`, `nightly-ha (2025.2.0)` and `nightly-ha (stable)`. The nightly-ha reds are this PR's own (point 1). `nightly-status` is red with `NIGHTLY FAILED: mutation-ledger-push, mutation-nightly failed in the last verification dispatch` (run 37050037132). That is main's, but this diff touches `tests.yml`, which holds the reporter's job, so the exemption is void and the body owes it an answer. The body itself flagged that it would.
3. **pr-contract also prints `REFUSE 'Fixes #1758' closes #1758; not in the intended list`.** The brief (rev 3.1) says this PR closes #1758, so the body is right. The intended list given to prepr/pr-contract is what has to change, and that is the orchestrator's to set.

## The seven points asked

1. **Positive control.** The probe sees the stall: 600.2 ms for a 600 ms spin. Both the frame-attribute stack and py-spy name `_hb_spin`. That HA's blocking detector misses it is **not measured** by this run. The log scan keys on reports that blame the package (`BLOCKING_AT_OURS`), and a report blaming `/opt/hpo/nightly_ha.py` would not be counted. The claim rests on mechanism: a pure-Python spin calls none of the functions the detector wraps. The body's "HA's blocking detector cannot see this stall" is sound reasoning, but it is stated as if it were a measurement.
2. **The 1 s freeze threshold** is defensible against these figures. The worst real gap was 201.4 ms (2025.2.0 changed_save), so 1 s leaves about 5x headroom, and the 250 ms dump trigger sits just above it. One caution: a py-spy dump ptrace-stops the whole process, loop thread included. A natural stall that triggers a dump therefore measures stall plus py-spy's pause. The positive control cannot show this pause, because the spin's deadline is wall-clock and absorbs it. A 250-999 ms stall could be pushed over 1 s by the instrument itself. Record that on any future gap figure near the bound, or use `py-spy dump --nonblocking`.
3. **The watcher cannot hold the loop.** It is a daemon thread, it polls every 20 ms, and `stop()` sets the event and joins with a 30 s timeout (R7 killed). It does take the GIL for the frame walk, and py-spy pauses the process (point 2). **It can leak a tick chain.** Without `cancel()` in `stop()`, a 1 ms `call_later` chain would survive each scenario on HA's loop, and no check sees that (R8 survives). The code does cancel today. The survivor means nothing pins it.
4. **The hash pins are correct** (RESULT above). SYS_PTRACE is added only to the third container: the job log shows `--cap-add SYS_PTRACE` on the `--heartbeat-only` run alone, not on the A3-A13 or A3(e) runs. The pin is unit-level only, though: R3 and R4 survive (see RESULT). Nothing fails if the cap or the py-spy staging is dropped from the real wiring, because `hb:positive_control` passes on the Python stack alone. Now that py-spy is shown to run on Alpine (rc=0 on both images), requiring `py-spy rc=0` in the positive control's dump when one was staged would close both.
5. **Job-level `if:`.** The diff adds none: 0 added `if:` lines in `tests.yml`. Its only change is one `-r` in an existing step.
6. **Uninstrumented seams.** These are not a forward-carry. A9's reload is unload plus `async_setup_entry` plus the first solve. `hb:changed_save` and `hb:menu_saves` trigger exactly that under the heartbeat, and `_async_hb_settle` holds the window to the reloaded coordinator's first plan. So reload, unload and setup are measured in kind on the reported freeze path. What stays unmeasured is the cold boot's first solve, because `_inside_hb` runs `_await_plan` before `hb.start()`, and A8's second-entry add and unload. Neither is the options-flow freeze, and neither changes how a later stage must work. No roster group consumes A15: R9-RO-2 lists F10.7 in `after` only for the reorganisation. When the orchestrator writes the barrier decision's brief, it should carry one line: "A15 covers options-triggered reloads, not the cold boot or a second entry". That is a note for that future brief, not a carry this PR owes.
7. **CI at the head** is as RESULT above. nightly-status's red is main's but needs an answer in the body (point 2 of Why blocked).

## Also checked

- **Step 1, mutation proof.** I deleted the gap line in `_beat` (R1) and the named check failed. The fixer's 12 mutants were not re-run, because I used my own set.
- **Step 7.** The live body names `34360097287696f1baa1b22fb2a481d3858b6ca6`, the head I measured. The merge c65d0058a resolves only `tests/closures.json`, through LEDGER-MERGE as a set.
- **Step 9.** There is no finder harness. The issue's finding is that no instrument exists, so the dispatched nightly is the measurement. The fixer disclosed the enumerator grep as their own stand-in, and my mutant driver is mine.
- **Not re-derived:** the body's "35" lines from the enumerator grep at 55ea06fc.
