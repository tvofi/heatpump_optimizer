<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

R9-UX-4, lane UX (#1795, design of record `handoff/round9/state/alt/design/ux/DESIGN-UX.md` at 1a90e4cb, section UX-4, decision U1). Part of #1795 and #201; the lane issue stays open for UX-5..7. Builds on R9-EG-B3a (#1852, `payload.py`).

Before: the integration had no outbound notification of any kind (no event, no `persistent_notification`, no notify call in `custom_components/heatpump_optimizer/`), so a closed month, a house heading below its floor, a stale input or a stale plan was visible only to someone looking at a card.

After: five documented Home Assistant events, each fired once per occurrence, and a blueprint that routes them.
- `heatpump_optimizer_monthly_receipt` (month, total, saving against a plain thermostat), `_comfort_at_risk` (predicted minimum, when, the floor, whether the peak guard is holding heating back), `_input_stale` (input, age, limit), `_plan_stale` (age), `_manual_plan_released` (channel, steps, reason, expiry). Every event also carries `entry_id`.
- `blueprints/automation/notifications.yaml`: a notify target (`notify.send_message`), one switch per event, and quiet hours the comfort alert passes through. An event during quiet hours is dropped, not deferred; the blueprint says so.
- `docs/automations.md` has an "Events" section with a table of every event and every data key; README and `docs/automations.md` link the blueprint.

How. New module `notifier.py`, registered in `__init__.py` right after `entry.runtime_data = coordinator` through `coordinator.async_add_listener`; no line is added to `coordinator.py` (a test pins that the file names no notifier). It reads the typed `Payload` (`.get` on declared keys, never bare keys). An occurrence is a rising edge: each detector returns its occurrences with a key, the event fires when the key differs from the last one sent, and a detector that sees its signal gone forgets the key so the next occurrence fires again. A payload that does not carry a detector's signal at all (`None` from the detector) leaves that state alone, so a light payload neither fires nor re-arms. What was sent lives in a `QuarantiningStore` (`heatpump_optimizer_<entry>_notifier`) written after each change and read back at setup. Event data is exactly `EVENT_DATA[event]`, so an undeclared key cannot leak and a declared one is always present. A receipt already held when the store is first created is adopted silently (an upgrade must not announce last month as news).

Decisions worth a reviewer's eye:
- **The store opts out of the instant bound (`lead=None`).** The manual-plan occurrence key is the override's expiry, the owner's instant and ahead of the clock by design. With the default bound the store rewrote that key on load, and a restart announced the same override again; `tests/features.py` found it (the restart check failed on the first run). `finite_boundary.py` lists the opt-out beside `away`'s, with its reason.
- **Comfort at risk is one event per episode,** not per worsening: a deeper forecast on a later refresh does not fire again; it re-arms only after a refresh with no risk. No hysteresis band: a plan oscillating across the floor refresh to refresh fires at each crossing (disclosed in `docs/automations.md`). Not built; no evidence yet that it happens, and a band is a threshold the owner would have to be told about.
- **"Why" in the comfort sample is limited to what is published.** The design's sample names the fuse limit; no field says why a step is cold until UX-5's sub-codes, so the event carries `peak_guard_suppressing` and the blueprint says "the peak guard is holding heating back". UX-5 can extend `EVENT_DATA`.
- **Manual-plan release fires once per release episode,** not once per override: a release that lapses for one solve and returns fires again (the detector clears its key whenever a solve releases nothing, and `released_*` is re-derived each solve; probe release, none, release gives two events). More steps released within one episode do not re-fire. Keying the clear on the override ending would fix it but is not small, so it is disclosed here and in `docs/automations.md`, as the comfort oscillation is.

## Head

fe03e7a8fc3e5d2dc565444d9e6a0f7bf9c765f9 (code head on `handoff/r9-ux-events`; `origin/main` merged in at 165510077)

## Mutation proof

`mutation_table.py --scope changed --base origin/main --max 0` lists 24 added sites, all in `notifier.py`, none pinned (CI's mutation-autofix pins them). Each was driven by hand against the UX-4 block of `tests/features.py` (the one driver that reaches the module), a one-line replace per site, restored after:
- 24 of 24 killed: every GUARD_OFF (`if X:` to `if False:`) at lines 73, 76, 93, 99, 102, 114, 128, 130, 140, 146, 197, 218, 221, 225, 234, 252; every BOOLOP (`and` to `or`) at 200, 213, 215, 225, 231; RETURN_DEL at 155 (`return found` to `return None`); CONST at 35 (store version 1 to 2); CMP_BOUND at 102 (`low >= floor` to `low > floor`: the check "a plan at the floor ... fire[s] nothing"; to `<=`: nine checks).
- Three survived the first pass and each got a check: the store version (the disk version is pinned at 1), `if not cold` (a plan with no readable room temperature must not crash), and the stored-value type filter (a non-text value in the store is dropped on load).
- Also killed, by named check: dedupe off (7 checks), no re-arm on clear (4), `problem != "stale"` (3), no baseline adoption (1), no persist (1).

Failing test first: the UX-4 block was written before `notifier.py` existed and failed on `ImportError: cannot import name 'notifier'`.

Round 1 (#1865) re-run: the restart check pinning `lead=None` had a fixed expiry and went vacuous once the calendar passed it. The block now freezes the clock (`_UX4_NOW`) and derives the expiry from it. Mutant `lead=None` deleted, block run with `_UX4_NOW` at 2026-10-02T12:00Z, 2031-01-01T00:00Z and 2026-10-03T07:00Z (the instant the reviewer's freeze found it surviving): the restart check fails in all three, and the unmutated block passes all 18 in all three.

## Null control

- The unchanged refresh: three repeats of the same receipt, risk, stale input, stale plan and release each fire nothing (`[[], [], []]` in each check), and a payload carrying none of the signals neither fires nor re-arms what was sent.
- The unmutated module: `ALL 18 UX4 PASSED` through the block alone, which is what every mutant above is read against.
- The restart: a notifier rebuilt over the same store fires none of the five for the same signals; one that saw them clear fires four again (the receipt never clears).
- Control for "coordinator.py grew nothing": `git diff $(git merge-base origin/main HEAD)...HEAD --stat -- custom_components/heatpump_optimizer/coordinator.py` prints nothing.

## Figures

- `PYTHONPATH=tests/hastub ~/hpo-seats/R9-F11.4-venv/bin/python3 tests/features.py`: `1 of 3670 FEATURE CHECKS FAILED`; the one is `R9-F2.1 P3` (shipped 110.4366 against 110.1297 refined), which the seat block records as failing on this Mac at main too (BLAS), so CI is its authority. The 18 UX-4 checks pass in it.
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`; no budget moved, no raise. Its first run was `FAIL dead_top_level_symbols 2 > 1` on a module-level `EVENTS` nothing in production read; it was removed and `EVENT_DATA` made live by building each event's data from it.
- `tests/entities.py`: `ALL 2081 ENTITY CHECKS PASSED` (its `a3`/`a4`/`a5`/... FAIL lines are its own negative controls). `tests/harness_headers.py`: `ALL 94 HARNESS HEADER CHECKS PASSED` after `tools/audit/round4/D6/claims.py` was regenerated (modules 70, listed 70, importers 26, links 16). `tests/deployment_shape.py`: `ALL DEPLOYMENT SHAPE CHECKS PASSED`. `tests/finite_boundary.py`: `ALL 69 FINITE BOUNDARY CHECKS PASSED` with the notifier store wired into its loader, saver, seed and opt-out tables. `tests/manual_plan.py` and `tests/config_flow_steps.py` (both run `async_setup_entry`): pass.
- Counts that moved: `docs/architecture.md` 70 modules, 26 importing `homeassistant`, 43 HA-free (the count of 43 is the tree's: 70 less 27 touching it anywhere); `tests/deployment_shape.py` note, 88 package files.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` prints `MODE: FULL -- every test script runs, nothing is scoped out.` because the diff edits `tests/closure.py` (see the owner gate below). `GOLDEN_MODE=drift` is CI's.
- `closures.json`: `notifier.py` is in the 12 closures that contain both `frontend.py` and `__init__.py` (the lazy setup-time imports), by hand, because this Mac cannot record; CI's closures autofix confirms or corrects. The new blueprint is in `tests/entities.py` and `tests/doc_claims.py`'s closures, the two that read `blueprints/`.

## Red checks

- `closures` on the pushed head (CI run 37073640871): `UNDER-SCOPED: tests/features.py really reads 2 file(s) ... notifications.yaml, docs/automations.md`, and `closures-autofix` returned skip-classifier-disagrees because main's `closure.py` treats the blueprint as INERT. Cheaper detector: none on this Mac, since recording a closure needs Linux and CI's recording is the only instrument; the standing cost is one CI cycle. The cause is that the new UX-4 block reads the blueprint and the docs. Fixed by hand-merging that run's recording for `tests/features.py` alone (`closure.py merge --partial --allow-failures`, one artifact downloaded; the timing left as it was).
- Two local reds before the first push, each answered:
- `structure.py` `dead_top_level_symbols 2 > 1`: cheaper detector is `structure.py` itself, seconds; fixed in the same working tree.
- `entities.py` "every tracked file is either measured or deliberately classified" on `notifier.py`, plus the architecture HA-free count (I had written 44, the tree's is 43): the detector is already seconds-cheap and ran before the push.

## Forward-carry

`.claude/workflows/wave-r9-groups.json` (group R9-UX-5, on `handoff/audit-r9-fixplan`): the comfort event's "why" (the design's "the fuse limit caps heating 02:00-05:00") is carried into that brief by the coordinator, which owns the roster entry; this PR ships `peak_guard_suppressing` only.

## Owner gate

This PR needs tvofi's review as code owner, which the brief did not expect: `tests/closure.py` is code-owned and the diff adds one line to its `INERT_EXCEPT`, for `blueprints/automation/notifications.yaml`. A new blueprint is read by `tests/doc_claims.py` and `tests/entities.py`, so a recorded read of a file under the INERT `blueprints/` prefix is the pair #357 refuses, and `closures-autofix` returns skip-still-fails on it; the three existing blueprints are listed there for that reason. No budget raise, no `harness.py`, no `run.sh`. The same edit makes the scoped gate `MODE: FULL`.

## Friction

- fixer.md-5: unclear: the brief says to classify the module "through CI's closures autofix, never INERT"; a new blueprint cannot be classified that way (above), and a new module's closure memberships have to be written by hand locally for `entities.py` to pass at all.
