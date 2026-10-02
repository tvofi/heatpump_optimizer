_Requested by **tvofi**_

Round-9 F10.7, gate infrastructure (diagnostic). Fixes #1758. Part of #201.

#1758 is the owed trigger-1 RCA for the v6.6.0 options-flow freeze (RCA-BULK-3 section 4). It could not establish the cause, and named process state (c): nightly-ha's only loop instrument was HA's blocking-call detector, which sees synchronous I/O and is blind to a CPU stall. `tests/nightly_ha.py` had no heartbeat or max-gap measurement.

**What this adds: A15, a loop-stall heartbeat on the nightly-ha options round-trips.** It is nightly only and costs 0 s on pull requests.

- `LoopHeartbeat` runs a 1 ms `call_later` probe on HA's running loop and records the largest gap between ticks.
- A watching thread reads the last tick. A stall of `HB_DUMP_S` or more is dumped while it is still open:
  - first the loop thread's Python stack, built from frame attributes only (no source file reads);
  - then `py-spy dump`, when the host staged one.
- A loop with no tick for `HB_HANG_S` is reported by name from the watcher, which then emits the result marker and exits. A full freeze shows up as `hb:<scenario>` instead of a 25-minute container timeout.
- It runs on a third container boot (`--heartbeat-only`), seeded two-zone + DHW as #1758 asks. Nothing it saves reaches the A3-A13 run. The seed forces `two_zone_mode="on"` with a lower-floor thermometer and sets `dhw_enabled`. The default seed is already two-zone by the presence rule and has no hot water.
- The four checks are demanded by name in `INSIDE_CHECKS`:
  - `hb:positive_control`: a deliberate 0.6 s CPU spin on the loop. It must read as a gap of at least that length, with a dump naming `_hb_spin`. HA's blocking detector cannot see this stall.
  - `hb:untouched_exit`: an untouched save-and-close of `comfort`, then an opened page abandoned (`async_abort`). Precondition: no reload. A reload here would be #1107's defect.
  - `hb:changed_save`: `target_temperature` changed, saved and closed. Precondition: the coordinator was replaced.
  - `hb:menu_saves`: five changed saves in a row in menu mode (#100's `AFTER_SAVE_MENU`), without waiting between them, then the dialog closed. The values alternate, so every save is a change and the burst ends changed. Precondition: the coordinator was replaced.
- After its actions, each scenario keeps measuring until the reloaded coordinator has a plan (bounded by `HB_SETTLE_S`), so the reload's first solve is inside the window.
- A scenario fails at a gap of `HB_FREEZE_S` (1 s) or more. **That is a design choice** (fixer.md step 11): a one-second loop gap is a freeze a user sees, and the sysid fit's measured 43-228 ms on the loop (#1658) stays under it. The gap is printed on a green run too (the `..` lines and each check's detail), because the barrier decision waits on that number.
- **py-spy.** The HA image ships none. `tests/requirements-nightly-ha.txt` (new) hash-pins py-spy 0.4.2's two Linux wheels. The nightly-ha job's existing install step adds `-r` for it. `_stage` copies the host's `py-spy` beside the driver, on a Linux host only. The heartbeat container alone gets `--cap-add SYS_PTRACE`, because py-spy reads its parent process. Whether that binary runs inside the Alpine image is measured by the first nightly, not here. If it does not, the dump records py-spy's error and keeps the Python stack, so no stall goes undumped.
- **Limit, stated in the code.** The watcher needs the GIL. A stall inside C code that holds the GIL is measured, but dumped only once it lets go.
- **Out of scope by the brief.** The barrier decision, the freeze's cause (to be filed as its own issue once the instrument finds it), and tvofi's optional host Profiler run (D11).

Files: `tests/nightly_ha.py`, `tests/entities.py` (the A15 pins, plus one wiring check), `.github/workflows/tests.yml` (one `-r` in nightly-ha's install step), `tests/requirements-nightly-ha.txt` (new) and `tests/closures.json` (one path, below). No production file is touched. `tests.yml` is code-owned, so it needs tvofi's approving review at the head.

## Head

2daa9eac2ab15959f8b53020d7aadf10f4f8c32c: the code commits 37069b2c, 55ea06fc and 6af10f55, plus the merge of `origin/main` 03ba7f70 (2026-10-02T22:40Z). The merge base is 03ba7f70. Every figure below was taken at 2daa9eac unless it names another ref.

## Mutation proof

Failing test first. At 37069b2c's parent tree plus the new `tests/entities.py` block (constants only, no instrument), `tests/entities.py` stopped with `AttributeError: module 'nightly_ha' has no attribute 'LoopHeartbeat'`.

Mutants: `/Users/timmalmstrom/hpo-seats/R9-F10.7/body/mut.py` (out of tree, sha1 d2df88a38c87b6d9d79ad865ed5e1b214b85a6da). It applies one predicate change at a time to `tests/nightly_ha.py` in place, runs `tests/entities.py` and restores the file. At 2daa9eac every mutant exited 1 with exactly 1 of 2094 checks failed, and that check is its own:

- M1, `_beat` stops recording the gap: FAIL `the heartbeat measures a CPU stall it did not cause and dumps the frame` (spun max_gap 0.000 s).
- M2, dump trigger scaled out of reach: the same check fails (dumps=[]).
- M3, hang trigger scaled out of reach: FAIL `a stall past hang_after calls on_hang once, from the watching thread`.
- M4, freeze bound dropped; M5, reload precondition dropped; M6, zero-tick guard dropped: each fails FAIL `hb scenario passes under the freeze bound and fails at it, on a reload mismatch, on no ticks, and on a raise`.
- M7, positive control ignores the dump: FAIL `hb:positive_control passes at the spin, and fails just under it or without the spin's frame`.
- M8, no `--cap-add` emitted: FAIL `the heartbeat container may ptrace itself for py-spy; the A3-A13 one may not`.
- M9, seed without `dhw_enabled`: FAIL `the heartbeat boot is two-zone + DHW by the model's own reading; the A3-A13 seed has no DHW`.
- M10, values stop alternating: FAIL `every heartbeat save changes the value, and the burst ends changed`.
- M11, after-save choice dropped: FAIL `a heartbeat save posts the changed key in its section with the after-save choice`.
- M12, py-spy not copied: FAIL `the host's py-spy is staged executable beside the driver, and none is staged without one`.

The boundary arms are pinned at the bound itself:
- `hb:changed_save` passes at `HB_FREEZE_S - 0.001` and fails at `HB_FREEZE_S`.
- `hb:positive_control` passes at `HB_CONTROL_S` and fails at `HB_CONTROL_S - 0.001`.

`python3 tests/mutation_table.py --scope changed --base origin/main` -> `MUTATION TABLE PASSED (empty scope)`. The diff touches no production line, so `--scope changed` draws no site and there are no survivors to list.

## Null control

- **The instrument on an idle loop.** In the same run, with no spin, it ticks (ticks > 10), reports a gap under `HB_CONTROL_S`, dumps nothing naming `_hb_spin`, and makes no `on_hang` call (`and on an idle loop it ticks, reports no such gap and dumps nothing`). A heartbeat that always read high, or that dumped on every run, fails this check.
- **The base seed.** `_dhw_enabled_from_config` reads the unmodified A3-A13 seed as having no DHW. That is the arm separating the heartbeat seed from the default one (M9 shows that check can fail).
- **A flake found and fixed on the way.** In the first mutation pass, two mutants unrelated to the hang (M6 and M8) also failed the hang check, so 2 of 12 `entities.py` runs missed `on_hang`. Cause: `traceback.format_stack` read each frame's source through `linecache` (`tests/entities.py` is 1.3 MB) and held the watcher past the end of the 0.6 s spin. A standalone 20-run repeat outside `entities.py` missed 0. 6af10f55 builds the dump from frame attributes instead. After that, 6 consecutive `entities.py` runs had 0 hang failures, and the 12-mutant pass at 2daa9eac had no off-target failure. The same change keeps a dump taken during a stall in HA from doing file I/O.

## Figures

- The issue's enumerator, at both ends: `git show <ref>:tests/nightly_ha.py | grep -cE 'call_later|max_gap|[Hh]eartbeat|py-spy'`.
  - 687e15b6 (the brief's base) -> `0`.
  - 55ea06fc -> `35`.
  - Rule: any line naming the probe, its gap, the arm or the dumper. Each `git show` was checked for success before counting. A first attempt under zsh expanded `$ref:t` as a modifier and printed 0 at both ends from a failed `git show`; that zero was discarded.
- Seams, the class's enumeration rule: `git show HEAD:tests/nightly_ha.py | grep -nE "await hass\.config_entries\.(async_reload|async_add|async_setup|async_unload|options\.async_(init|configure))|await flows\.async_(init|configure)|await _boot\("`. This lists every loop-driving call site in the container half. Dispositions:
  - The A15 options round-trips (`flows.async_init` / `async_configure`): closed in this diff.
  - The A5 page walk (`_async_open_options_step` and its `async_configure` resubmits): untouched saves. Covered in kind by `hb:untouched_exit`, which drives the same save path on the same page shape. Not itself under a heartbeat.
  - A9's five `async_reload` calls: the reload is the mechanism `hb:changed_save` and `hb:menu_saves` trigger under the heartbeat. A9's own loop is not instrumented. **Open seam**, outside the brief's scope (the options round-trips); for the orchestrator to dispose.
  - A8's `async_unload` (and its second-entry add) and the three `_boot` setups (A14): not the reported freeze path. Not instrumented. **Open seams**, the same disposition. A14 is already its own "partial" row in the module docstring.
- `PYTHONPATH=tests/hastub ~/hpo-seats/R9-F11.4-venv/bin/python3 tests/entities.py` -> `ALL 2094 ENTITY CHECKS PASSED`.
- `PYTHONPATH=tests/hastub ~/hpo-seats/R9-F11.4-venv/bin/python3 tests/harness_headers.py` -> `ALL 94 HARNESS HEADER CHECKS PASSED`.
- `PYTHONPATH=tests/hastub ~/hpo-seats/R9-F11.4-venv/bin/python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`. No budget moved and none was raised.
- `PYTHONPATH=tests/hastub ~/hpo-seats/R9-F11.4-venv/bin/python3 tests/config_flow_steps.py` -> `ALL 496 checks PASSED`. It imports `nightly_ha`.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` -> `MODE: FULL -- every test script runs, nothing is scoped out.` because `.github/workflows/tests.yml changes the gate itself`. Locally I ran the scripts whose closures list a changed file (`tests/entities.py`, `tests/harness_headers.py`, `tests/config_flow_steps.py`). The rest of the FULL run is CI's.
- Closure: `tests/closures.json` gains `tests/requirements-nightly-ha.txt` under `tests/entities.py`, which reads it through the #1548 hash-pin check and the new wiring check.
  - Measured by `./tests/derive_closures.sh --single tests/entities.py --record-only --out-dir D` (Darwin; a Python lane is recorded by audit hook). The recording run's only failure was the classification check itself, the #1071 shape.
  - Only that one path was taken from it. The recording's rc, seconds and `inert_reads` rewrites were discarded.
  - `python3 tests/closure.py check --in-dir D --partial` -> `closure: committed closures cover every file this run touched`.
- `node .claude/workflows/policy_lint.mjs` -> `TOTAL: 0 error(s) across 40 policy file(s)`. `node .claude/workflows/rules_sync.mjs --check` -> `RULES-SYNC ok`. Both were taken at 55ea06fc; this diff touches no policy file.
- Not run locally:
  - The container lane itself. There is no Docker daemon on this host (`docker images` -> cannot connect to `/var/run/docker.sock`; colima has no instance), so the four `hb:` checks have never run inside Home Assistant. A `workflow_dispatch` of Tests on this branch is the first measurement.
  - CI's closures recording (`PREPR_SKIP_CLOSURES=1`), `features.py` and the solver goldens.

## Red checks

none: no check has run on this branch yet. If `nightly-status` is red on the PR, it owes an answer here, because this diff touches `tests.yml`, which that reporter reads.

## Forward-carry

none: the brief defers the barrier decision until the instrument finds the stall, and no later stage's brief depends on this diff. The open seams under Figures (A9's reloads, A8's unload, setup) belong to this stage, so they go to the orchestrator for an issue or a carry rather than to another stage's brief.

## Friction

- environment: cost: no Docker daemon on the seat host, so a lane whose whole subject is real Home Assistant can only be unit-tested here. Its first real reading needs a dispatched nightly.
- fixer_step3: unclear: "re-execute the finding's harness" has no harness to re-run for a diagnostic whose finding is "no instrument exists"; the enumerator grep stands in for it.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
