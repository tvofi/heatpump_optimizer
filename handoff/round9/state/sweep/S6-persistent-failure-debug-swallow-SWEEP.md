# Class sweep — "persistent failure swallowed at DEBUG"

Not in `tools/audit/bugclasses.json` (new class this round).

Round-9 finding: **D1-s2-04** (verified, medium — of 24 `except Exception` → `_LOGGER.debug(...)`
guards in `coordinator.py`, the 5 reachable on the live optimization cycle
(`_command_frequency`, `_async_drive_pumps`, `_async_watch_learning_drift`,
`_maybe_run_fuse_advisor`, `_maybe_refresh_price_tile`) were driven for 3 consecutive cycles each
with an injected persistent `TypeError`; every one produced 0 records at WARNING or above and 0
repair issues — `silent_sites=5 of 5`, re-run here and reproduced exactly).

## Enumerator

`tools/audit/round9/D14/sweep/persistent-failure-debug-swallow/enumerate.sh`: static family is
the grep for every `except Exception` immediately followed by `_LOGGER.debug(...)` (24 sites,
reproducing the finding's own seam rule exactly); dynamic family reuses the finder's own harness
(`tools/audit/round9/D1/s2/guards.py`), re-run here (cheap: 3 synthetic cycles per guard, no
solver grid) and reproducing `silent_sites=5 of 5`.

Positive control: the dynamic re-run reproduces `visible__async_watch_learning_drift=0`,
`visible__maybe_run_fuse_advisor=0`, `visible__maybe_refresh_price_tile=0` (and the other two
cycle-path sites) at exactly the finding's baseline counts.
Null control: `guards.py --perturb debug_to_warning` (DEBUG calls routed to WARNING) drops
`silent_sites` to 0 — documented in the harness, not re-run here.
Perturbation: the same `--perturb debug_to_warning` is both the null control and the judge's
perturbation for this finding.

## Disposition

| seam group | count | disposition | note |
|---|---|---|---|
| `_command_frequency` (:4662), `_async_drive_pumps` (:4667), `_async_watch_learning_drift` (:4682), `_maybe_run_fuse_advisor` (:5087), `_maybe_refresh_price_tile` (:5094) | 5 | **instance** | D1-s2-04 itself — reached and silent on 3/3 cycles, `silent_sites=5 of 5`. |
| `_ensure_ecl110_state_subscription` (:2444), mode-notice clearing (:4525) | 2 | **guarded** | Explicitly best-effort by comment (`# noqa: BLE001 - clearing is best-effort`) and one-shot setup subscriptions, not a per-cycle persistent-failure path the harness's cycle-driven metric applies to. |
| Learned-thermal-parameter, price-model, ledger, accuracy-history, energy-totals, manual-plan, learner-snapshot load/persist pairs (:2849,:3128,:4287,:4463,:7168,:7192,:7199,:7259,:7266,:7321,:7327,:7366,:7395,:7423,:8898,:8911) | 16 | **guarded** | Storage I/O explicitly documented "never block setup on storage" — a load/persist failure degrades to defaults/no-op by design, not a silently-broken live control the user would otherwise expect to see act. |
| `_maybe_refresh_price_tile`'s per-tile inner failure (:10120) | 1 | **guarded** | Same mechanism as the cycle-path `_maybe_refresh_price_tile` guard already counted at :5094 — a nested try inside the same already-dispositioned call, not a second independent site. |

## Count

N = 1 verified finding (D1-s2-04, covering all 5 cycle-path guards as one finding) + 0 additional
sweep-confirmed instances (the widened static scan found 19 more `except Exception` →
`_LOGGER.debug` sites, all off the live cycle path and either one-shot setup or documented
best-effort storage). **rca = false** (N=1 < 3, not a ledger class, not barriered).

## Barrier proposal

None proposed at N=1 for the whole class (most of the 24 sites are legitimately silent by
design); the fix belongs to the 5 cycle-path guards specifically — a targeted check that a guard
on the live-cycle call path logs at WARNING (or raises a repair issue) after N consecutive
failures, not a class-wide structural gate.
