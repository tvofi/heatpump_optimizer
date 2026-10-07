Closes #1940

Leaves #201 open.

R9-DBG-2: the debugger's self-tests, the inline cap on the diagnostics bundle, and the nightly-ha size check. The R9-DBG-0 pre-study (`tools/audit/round9/prestudy/debugger-prestudy.md` at `eae236d66`, sections 4 and 7) is the spec. R9-DBG-1 (#1987) already landed the finalize button and its translations, so this PR wires the button to the self-tests and does not add a second button.

- **Self-tests on finalize** (`debugger.py`). However a collection ends (the seven days, the `debug_collect` stop action, or the Finalize Debug Collection button), the stop takes effect at once and `_async_finish` runs once in the background. It runs the five self-tests from the pre-study's section 4 table, in order, under `run_self_tests`. Together they get `SELF_TEST_BUDGET` (15 minutes). Each one is cut off with `asyncio.timeout` at whatever budget is left, and once the budget is gone the rest are skipped. A check that raises is recorded and does not stop the others. A check returns its result, or an awaitable of it, and only the solver smoke and the store read suspend. An earlier pass-through coroutine wrapper for the synchronous ones matched a test helper's body, and `no-copies` refused it, so `run_self_tests` now awaits only an awaitable result. The five:
  - `stores`: each store document on disk against its `DOMAINS` declaration, plus whether the `QuarantiningStore` scrub would change it (`_sanitize`).
  - `accuracy`: bias, MAE, trust and sample count re-derived through `AccuracyTracker.from_dict` from the accuracy store, next to the live tracker's, with the stored and restored sample counts. The two windows differ, and the report says so.
  - `solver`: one `async_simulate({}, limited=False)` with no override, so its `cost_delta` against the live plan should be 0. It reports the wall time next to the week's `payload_solve_time_ms` spread. `limited=False` keeps it off the user's rate limiter and the card cache.
  - `sensors`: for indoor, outdoor and DHW temperature, the number of missing readings, the value range and the longest unchanged run, plus the live input-health view (`problem_inputs`, `input_ages_minutes`, `learners_frozen`).
  - `feeds`: cycles with no prices, cycles with a stale forecast and its largest staleness, and the solve failures the week added.
  None of them actuates or opens a socket. The results are saved with the ring as JSON text: one new `debug` `DOMAINS` row, `self_tests: _TEXT`, which follows the `snapshots/#/data` precedent. They survive a reload and are carried in the bundle as `manifest.self_tests`. Results that finish after the collection was restarted are discarded.
- **Inline cap** (`debugger.capped`, called from `diagnostics.py`). Download diagnostics carries the bundle whole up to `INLINE_CAP_BYTES` (8 MiB, the pre-study's "8 MB raw"). Past that it carries `{schema, manifest, inline: false, bytes, cap_bytes, store_file: ".storage/heatpump_optimizer_<entry>_debug"}`. The size is measured as `json.dumps` text, which is longer than the compact JSON Home Assistant writes, so the downloaded file stays under the cap.
- **Nightly lane A16** (`tests/nightly_ha.py`). This is the size check the pre-study's section 8 left owed to this lane. A planted week goes through `diagnostics` and Home Assistant's own `json_bytes`, once under the real cap (`a16:debug_inline`: carried whole, and serialisable by HA) and once about 1 MB past it (`a16:debug_capped`: the summary, and a download under the cap). Both names are in `INSIDE_CHECKS`. The judge `check_a16` runs in the PR gate from `tests/debug_collect.py`, with each arm swapped as its null control. The container half runs only on schedule or `workflow_dispatch`.
- **Translations and docs**: the option description in `strings.json`, `en.json` and `sv.json` now says that ending the collection runs read-only self-tests. `docs/configuration.md` names the five self-tests and the over-cap summary.
- **Test-side repair**: DBG-1's solve-wall check patched `debugger.time.monotonic` and never put it back. `debugger.time` is the process's one `time` module, and asyncio's loop clock reads it, so every later `asyncio.sleep` hung. The real function is now restored right after that check.

Alternatives considered:
- (a) Persist the results as a nested `DOMAINS` declaration: about 40 rows for a diagnostic record no loader installs. JSON text is the existing `snapshots/#/data` shape.
- (b) Run the self-tests inside the diagnostics download: up to 15 minutes in an HTTP request. The pre-study puts them on the finalize press.
- (c) Put the cap in `diagnostics.py` alone: `capped` is pure and lives next to the bundle it measures, so `diagnostics.py` adds one call and `tests/debug_collect.py` drives both.

`_longest_flat` was first written with an `index and ...` guard, which is an equivalent mutant (at index 0 the run is 0, so both arms give 1). It now compares against a sentinel and has no equivalent site.

What this PR does not do:
- The solver smoke calls `async_simulate`, not the pre-study's `tests/stress.py:reference_solve`, which lives in `tests/` and cannot ship.
- The store test is a domain and quarantine report for every store, with a full `as_dict -> from_dict` round trip for the accuracy store only. A generic round trip would need one loader per store.

_Requested by **tvofi**_.

## Head

`6fe488c9db7c0d423c7ad8543be6502f9fc1c55f`

## Mutation proof

Applied one at a time in a detached worktree at `6fe488c9`. Each mutant was run with `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` and then restored. The probe is the seat's one-off `mutate.py`, kept in scratch, not in the tree. Lines starting `FAIL a16:` are the judge's printed null arms, so they are not counted. Every mutant below exited 1:

- M1 `capped` always inline (`if True:`): `a bundle at the cap is carried inline, and one byte over it is the summary`; `Download diagnostics carries the summary and the store file when the bundle is over the cap, and the whole bundle under it`; `the nightly A16 judge passes a whole bundle and a summary past the cap, ...`
- M2 `size <= limit` becomes `<`: `a bundle at the cap is carried inline, and one byte over it is the summary`
- M3 the `except Exception` arm of `run_self_tests` deleted: `RuntimeError: bad store` escapes, and the script crashes
- M4 `if left <= 0` becomes `if False`: `a self-test that raises is recorded and the next still runs; one past the budget is cut off, and those after it are skipped`; `a budget with exactly nothing left starts no further self-test`
- M5 the restart guard becomes `if True`: `self-test results that finish after the collection restarted are discarded`; `the first collection's self-tests, finishing after a second collection was also finalized, are discarded`
- M6 `finalize` spawns only `async_save` (DBG-1's body): `finalizing stops the collection at once and runs the five self-tests after it`, then `KeyError: 'stores'`
- M7 `quarantined` always `False`: `the store self-test names a field off its domain and a leaf the quarantine scrubs, ...`
- M8 the `"self_tests": _TEXT` row deleted from `store.py`: `a ring carrying its self-test results is inside the debug store's domain`
- M9 `diagnostics.py` without `capped`: `Download diagnostics carries the summary and the store file ...`; `the nightly A16 judge ...`
- M10 the loaded `self_tests` dropped: `the self-test results survive a reload and ride the bundle's manifest`
- M11 `check_a16` without `over.get("inline") is False`: `the nightly A16 judge fails a download over the cap that does not say it is a summary`
- M12 every forecast counted stale: `the feed self-test counts cycles with no prices, cycles with a stale forecast, ...`
- M13 every run counted flat: `the sensor self-test counts a missing reading and the longest unchanged run per input, ...`
- M14 `accuracy_report` reads the document root: `the monitor self-test re-derives bias from the stored window ...`; `the self-tests read the entry's own store documents from disk`
- M15 `manifest.self_tests` dropped: `KeyError: 'self_tests'`
- M16 the solver smoke goes under the user's limiter: `the solver self-test solves once without the user's limiter ...`
- M21 an awaitable result is never awaited: the solver result is a coroutine, and the script crashes
- M22 every result is awaited: the first synchronous check raises `TypeError`, and the script crashes
- M17 `restart` keeps the results: `starting a finished collection again clears its self-test results`
- M18 the restart guard's `and` becomes `or`: `the first collection's self-tests, finishing after a second collection was also finalized, are discarded`
- M19 `left <= 0` becomes `left < 0`: `a budget with exactly nothing left starts no further self-test` (on a frozen clock, the only way that boundary is reached)
- M20 `_longest_flat` drops `max`: `the sensor self-test counts a missing reading and the longest unchanged run per input, ...`

Ledger pinning is `mutation-autofix`'s job (`ci-autofix.md`), so nothing was pinned locally. At `7c5d1a93`, `python3 tests/mutation_table.py --scope changed --base origin/main` listed 16 `ADDED UNPINNED` sites, all in `debugger.py`. At `e0358dbb`, `_longest_flat` was rewritten, which removed its `BOOLOP` site. The diff inventory was not re-run at this head. In the list at `7c5d1a93`, every guard, comparison bound and removable return in the new code maps to a mutant above, or is a `RETURN_DEL` whose deletion crashes a check (`store_keys`, `store_report`, `sensor_sanity`, `run_self_tests`, `read_stores`, `_longest_flat`). Survivors on the touched sites: none known. `mutation`'s `--scope changed` table at this head is the authority.

## Null control

- M0, the same probe with no change applied at `6fe488c9`: `ALL 55 DEBUG COLLECT CHECKS PASSED`, rc 0.
- At the merge base `8d7903e6`, with only the new test (commit `15b0a2bf`): the script stops at `AttributeError: module 'heatpump_optimizer.debugger' has no attribute 'store_keys'`. The test fails before the fix.
- The pricing harness at `8d7903e6` (below) prints `RESULT selftests=absent`.

## Figures

All taken at `6fe488c9` unless another SHA is named, on 2026-10-07, against `origin/main` `8d7903e69cfebb3db279b7a17a0ca066f04c40e0`.

- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>` at `89782b2f`: `MODE: SCOPED -- 23 script(s) run, 10 scoped out.` The later commits add `tests/debug_collect.py` checks and `tools/audit/harnesses/r9_dbg2_selftest_price.py`, which is under the INERT `tools/audit/` prefix. A loop over this diff's files against `closure.orphan_files()` printed `changed files that are orphans: []`.
- Ran locally, one at a time, as `PYTHONPATH=tests/hastub <python> tests/<script>.py`. Some ran at earlier commits of this branch while it moved; those commits are noted. On the seat venv's Python 3.14 at `505ec49c` (the commits after it change only `run_self_tests` in `debugger.py`): `entities.py` `ALL 2202 ENTITY CHECKS PASSED` and `harness_headers.py` `ALL 109 HARNESS HEADER CHECKS PASSED`. At `6fe488c9`: `debug_collect.py` `ALL 55 DEBUG COLLECT CHECKS PASSED`, and `structure.py` `STRUCTURE RATCHET PASSED`. On system Python 3.11 at `89782b2f`..`7c5d1a93`: `config_flow_steps` `ALL 496 checks PASSED`, `deployment_shape` `ALL DEPLOYMENT SHAPE CHECKS PASSED`, `doc_claims` `ALL 160 checks PASSED`, `env_drift` `NO STALE FIXTURE: 5 committed fixture(s) still match what this tree computes`, `finite_boundary` `ALL 84 FINITE BOUNDARY CHECKS PASSED`, `guard_pins` `ALL 47 GUARD PIN CHECKS PASSED`, `manual_plan` `ALL 129 manual plan checks PASSED`, `block_duty` `ALL 46 BLOCK DUTY CHECKS PASSED`, `wood_advisor` `ALL 7 wood-advisor checks PASSED`, `plan_view` (pass line), `solar_alignment` `ALL SOLAR ALIGNMENT CHECKS PASSED`, `typing_ruler` `ALL 11 typing-ruler source checks PASSED`, and `node tests/md_tables.mjs` `RESULT doc_misrendered_lines=0`. On 3.11, `entities.py` and `harness_headers.py` fail to compile their own 3.12+ f-strings (`entities.py:3915`, and `claims.py`). That is the interpreter, not this diff, which is why they ran on 3.14. Left to CI, per the seat brief's heavy-script rule: `features.py`, `golden.py`, `boost_drift_replay.py`, `arch_score_head.py`, `card.mjs` and `card_drift.mjs`.
- The oracle, the pre-study's priced table, re-run on the shipped code: `PYTHONPATH=tests/hastub python3 tools/audit/harnesses/r9_dbg2_selftest_price.py --bundle week.json.gz`. Its sha1 at this head is `d5c54708e19c82dc240835909ab9fc7a08144be2`. `week.json.gz` is `git show origin/handoff/r9-dbg-0:tools/audit/round9/prestudy/runs/week/bundle.json.gz`, with sha1 `cb6e9e3357648afc41adcadaff218f135908cc3d`. The harness prints each self-test's wall time as a `RESULT` line, and the sum next to the 900000 ms budget. At `--repeat 1` (336 rows, 5 stores), every self-test was `ok` and `selftest_total_ms` was under one second, against the 900000 ms budget. The figure varies with the seat's load, so the harness is the instrument and no number is carried here. The solver row is the orchestration only, because the harness's stand-in coordinator does not solve. The pre-study priced the solve itself (`reference_solve`, 20.2 ms). `bundle_inline=1`. Perturbation: `--repeat 60` gives `bundle_bytes=8897796` against the cap of 8388608 and `bundle_inline=0`, and `selftest_total_ms` stays under one second. Null control: at `8d7903e6` the harness prints `RESULT selftests=absent`. This bundle is smaller than the pre-study's 1,435,346 B, because DBG-1's bundle leaves `replay` empty for the repo-side harness, and the harness seeds no payload snapshots.
- `tools/pr/prepr.sh` with the venv first on PATH: no refusal other than the `## Head` line this body now carries. `python3 -I tools/audit/seat/tmp_paths.py --check`: `tmp_paths: 0 refused, 0 stale allow entries at HEAD`.

## Red checks

Expected on the first CI run. Not yet observed at this head.
- `closures`: `UNDER-SCOPED: tests/debug_collect.py`. It now imports `tests/nightly_ha.py` and drives `diagnostics.py`, and its committed closure lists neither (read from `tests/closures.json` at this head). `closures-autofix` re-records it (`ci: re-record closures`). Cheaper detector: `./tests/derive_closures.sh --single tests/debug_collect.py`, a few seconds. The seat brief keeps closure recordings in CI, so it was not run here.
- `mutation`: `ADDED UNPINNED` sites in `debugger.py` (above). `mutation-autofix` pins the killed ones (`ci: pin killed mutants`). Cheaper detector: `python3 tests/mutation_table.py --scope changed --base origin/main`, about 5 s. It was run, and it lists them.
- `mutation-autofix` and `closures-autofix`: if either reports a `skip-*` failure status, the repair is the seat's, under `ci-autofix.md`.
- `delivery-status` and `nightly-status`: if red, they grade main's record and main's nightly lane, not this diff.

## Forward-carry

none. No finding here changes how a later stage must work. The A16 container half runs on the next scheduled nightly-ha run, or on a `workflow_dispatch`.

## Friction

fixer.md: unenforced: DBG-1's `tests/debug_collect.py` patched `time.monotonic` process-wide and never restored it. Every later `asyncio` wait in that script hung, and the first run of this branch's tests sat until the 120 s tool timeout. Nothing flags a test that leaves a stdlib function patched.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
