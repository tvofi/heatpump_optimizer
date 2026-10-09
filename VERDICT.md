Fix review: blocked 849fe5b9e6327720306b30ce25161fb747ecab27 harness: vacuous-pin notifier.floor_return_silence input selector -- replacing `p.get("input") == CONF_FLOOR_RETURN_TEMP_ENTITY` with `True` fails no check, and that mutant raises the floor-return repair naming `sensor.indoor` when only the indoor sensor is dead
bus-nonce: a01f6f831c0a50f4c730689e09f398ec

Round 1. Reviewer seat review-2071. Verdict at the live head `849fe5b9e`. I measured at `86c6daf48`, a detached worktree; the delta to the live head is the bot pin commit only (see the last section). Merge base `bd59a4af1`. The contract `fix-review.md` is current: `git diff merge-base...origin/main -- dev/governance/roles/` is empty.

## What holds

The fix is correct in production. One property, the floor-return slot discriminating from every other input, has no check that pins it. A second, the value comparison in `config_overridden_by_options`, is also unpinned.

RESULT lines are from my own probes (`evidence/probe.py`, `evidence/probe_other_input.py`). They are reviewer-built: the finding came from a live install with no committed harness (step 9). All data is synthetic.

```
base bd59a4af1  RESULT diag config.min_kw=3.0 config.max_kw=14.0   (setup 3.0/14.0, options 1.2/6.0)  -- bug reproduces
head 86c6daf48  RESULT diag config.min_kw=1.2 config.max_kw=6.0    -- the export is the live merge
head            RESULT diag config_setup.min_kw=3.0 overridden=[heat_pump_max_power, heat_pump_min_power, name, solar_location, tibber_token]
head            RESULT diag config.location={'latitude': 61.9, 'longitude': 15.2}   (options coordinate, other cell, coarsened)
head            RESULT diag leaks=[]   (options token, setup token, options name, full and 2-dp coordinates from both)
head            RESULT diag token_fields=[**REDACTED**, **REDACTED**] name=**REDACTED**
head            RESULT floor stale_7h:             problems=[(floor_return_temp_entity, stale)]       issues_at[0,59,60,600 min]=[0,0,1,1]
head            RESULT floor fresh_5min:           problems=[]  floor_return_temp=31.5                 issues=[0,0,0,0]  (null)
head            RESULT floor fresh_5h_under_limit: problems=[]  floor_return_temp=31.5                 issues=[0,0,0,0]  (null)
head            RESULT floor implausible_85C:      problems=[(floor_return_temp_entity, implausible)] issues=[0,0,1,1]
head            RESULT floor unknown:              problems=[(floor_return_temp_entity, unavailable)] issues=[0,0,1,1]
head            RESULT other-input-dead: problems=[(indoor_temp_entity, unavailable)] floor_return_temp=31.5 floor_return_silent_raised=0
head + R7       RESULT other-input-dead: ... floor_return_silent_raised=1 named=['sensor.indoor']
```

- **Live config.** `config` is `{**entry.data, **entry.options}`, the same merge the coordinator reads. `config_setup` keeps the setup data. Both pass through `_coarsen` and `async_redact_data`, which run over the whole payload. I found no new leak. The option key space is the data key space, and the only secret key (`tibber_token`) and `name` are redacted at any depth. `config_overridden_by_options` emits key names only.
- **Silent sensor.** The repair keys on `input_problems`. `InputHealth.details()` lists exactly the configured readings that are not `ok`, which is the same predicate as the coordinator's open-loop branch (`if not floor_return.ok`). So stale (past `QUIET_STORE_MAX_AGE_MINUTES`=360, then +60), implausible, unavailable and missing all raise it. A fresh reading, and a numeric reading under the age limit, do not. The watch only reads the payload, so it cannot mask a reading.
- **Design (DESIGN.md with A1-A4), step 15.** No `coordinator.py` line. No new function takes `coord`: `floor_return_silence` takes values and `FloorReturnWatch` takes `hass`. Store is untouched, so every store stays at version 1. The repair goes through S6 `set_issue` (WARNING, `translation_key == issue_id`, not fixable), as section 4 prescribes for seat 4. It does not double-report with `_audit_lower_floor_sensor`, which covers a different slot. The S7 `diagnostics_view` loop in `_coordinator_snapshot` is not touched or forked: the config change is the separate `diagnostics.py:144` item section 4 names. No architecture breach.
- **Merge order.** `git merge-tree --write-tree` gives rc=0 against origin/main and pairwise against #2065 `325960ef6`, #2066 `d65c68c96` and #2070 `f74924e09`. I also chain-merged main, then #2065, then #2071, and it is clean. No sibling calls `_set_issue`. #2066 and #2070 conflict with #2065 and with each other in `diagnostics.py`, but that is theirs, not this PR's.
- Steps 4, 5 and 14: no golden, claim, budget, `closures.json`, `VERSION`, manifest or notes file is in the three-dot diff. Step 7: the body names `86c6daf48`, which is the head I measured. Step 10: the forward-carry targets (DESIGN S6, section 6 "5 vs floor return") are present.

## Mutation proof (step 1), mine, at 86c6daf48

I ran the diagnostics section of `tests/entities.py` (`evidence/entities_slice.py`: header, D10-08 helpers, D10-12; 19 checks, all pass unmutated) and the PR's features block (12 checks, all pass unmutated).

| mutant | result |
|---|---|
| R1 `"config": {**data, **options}` -> `dict(data)` | 2 of 19 fail (killed) |
| R3 delete `floor_return.handle(coordinator.data)` | 1 of 12 fail (killed) |
| R8 `config_setup` -> merged | 3 of 19 fail (killed) |
| **R7** `p.get("input") == CONF_FLOOR_RETURN_TEMP_ENTITY` -> `True` | **0 of 12 fail: SURVIVES** |
| **R2** `k for k in options if k not in data or options[k] != data[k]` -> `k for k in options` | **0 of 19 fail: SURVIVES** |

**R7 is the block.** Every payload in the block either has no problems or has only the floor-return problem, so the selector is never exercised against a competing input. The null controls ("a live sensor and an unconfigured slot never raise it") pass with any selector. Under R7, a dead indoor thermometer beside a healthy floor-return sensor raises "Floor return temperature sensor is not reporting" with `{entity_id}` = `sensor.indoor` (my probe, above). This is the null control the brief asked for, and it is missing. The site is also absent from the body's "Unpinned sites", because the mutation table does not enumerate it.

**R2 is owed in the same push.** Both `_DIAG_OPTIONS` keys differ from setup, so `sorted(options)` passes "the keys options override named". To pin it, add one options key equal to its setup value and expect it absent from `config_overridden_by_options`.

**Required.** (a) A check in the features block where another configured input (for example indoor) is unreadable and the floor-return sensor is live, at 10 times the period, with no `floor_return_silent` issue. Show it kills R7. (b) An equal-valued options key in the diagnostics fixture, with a check that it is not listed. Show it kills R2. Fixer steps 2 to 8 re-execute after the push.

## Checks (step 11), check-runs at 86c6daf48

- `mutation` failure (job 113599330237): `MUTATION TABLE REFUSED -- 4629 unpinned against 4624 ... 5 added`, at notifier.py:182, 198, 201 (twice) and 219. These are exactly the five sites the body's "Unpinned sites" lists. It is the ci-autofix pin path (`mutation-pins` / `mutation-pin-plan`), so it is answered.
- `nightly-status` failure: not this PR's, because the diff reaches nothing it reads.
- Everything else completed is green or skipped. The settle state at posting is in the evidence (`checks-*.txt`).

## Not verified

- The body's figures `ALL 2231 ENTITY CHECKS PASSED`, `dS +0.0000 NULL` and `MODE: SCOPED -- 22 script(s) run` are not re-derived. Those are heavy scripts, and CI is the authority for them.
- The fixer's M1-M8 counts I re-took only in part: M3 matches my R3.

## Bot-pin delta, 86c6daf48 -> 849fe5b9e (step 12)

The live head is now `849fe5b9e6327720306b30ce25161fb747ecab27` (`ci: pin killed mutants`, from the `mutation-pins` autofix). That delta adds six `killed_by` ledger JSON files: four for `notifier.py` and two for `setpoint_check.set_issue`. It changes no production or test line (`git diff 86c6daf48 849fe5b9e -- custom_components tests/*.py` is empty), so every RESULT line and both survivors carry over unchanged. Neither R7 nor R2 is among the pinned sites. The `notifier.py:182 CONST` site the body lists has no pin file in the delta. At settle, `86c6daf48` showed a later `pr-contract` failure (113628688678), consistent with the body naming a head that is no longer the head.
