# Class sweep — P11 (round 9, thread S4)

**Property:** the only oracle for an external counterpart (HA core, its state machine,
its recorder REST API, a device behind an integration) is a test double the implementer
wrote from what the code needed, so the tests agree with a wrong implementation.

**Enumerator:** `tools/audit/round9/D14/sweep/P11/enumerate.py`, reusing each finding's
own whole-package/whole-grid harness plus two custom probes (currency, Tibber reauth) for
the two findings that had none. `PYTHONPATH=tests/hastub python3
tools/audit/round9/D14/sweep/P11/enumerate.py`

## Positive control

| Finding | Command | Recorded value | This sweep |
|---|---|---|---|
| D1-s1-51 | `stub_store_codec.py` | 6 of 6 hostile tokens divergent | reproduced exactly (`divergent=6 of_6`) |
| D1-s1-52 | `stub_naive_clock.py` | 6 of 6 aware/naive cells invert | reproduced exactly (`divergent=6 of_6`) |
| D1-s2-71 | `l3_update_interval.py` | 4 of 4 cells unreadable | reproduced exactly (`unreadable_cells=4 of 4`) |
| D6-s1-81 | grep + probe (new) | README claims SEK fallback, HA core defaults EUR | reproduced: `resolve_currency` returns `EUR` under a real-HA-shaped `Config.currency="EUR"`, never falls to `SEK` |
| D10-s1-03 | grep + probe (new) | reauth verdict never raises `ConfigEntryAuthFailed` | reproduced: the `verdict == "reauth"` branch starts the Repairs flow then falls through to `_tibber_fetch_failed` → `UpdateFailed`; `ConfigEntryAuthFailed` is referenced nowhere in the package |
| D14-s4-02 | `p7_replay_clock.py --zone-clock` | 9-10 wrong sites under a zone-aware clock, 0 under the plain arm | reproduced exactly (autumn: 9, `replay_wrong_sites=10`, `zone_clock=0` baseline) |

## Every seam, dispositioned

**D1-s1-51 / D1-s1-52 / D1-s2-71**: each is a single seam (the one Store/`dt_util`/
`DataUpdateCoordinator` stub in `tests/hastub/`), already the whole package for its own
mechanism — the finder's positive control against 6 (or 4) input cells IS the widening.
**instance** × 3.

**D6-s1-81** (currency fallback): 1 seam — `custom_components/heatpump_optimizer/
currency.py:resolve_currency`. **instance**: no code path exercises the SEK fallback
under a real (or realistically-configured) `hass.config`, since HA core's `Config.currency`
is never `None`/falsy in practice (it defaults to `"EUR"`); the branch is live only
against the test double's `currency=None`.

**D10-s1-03** (Tibber reauth): 1 seam — `coordinator.py:_fetch_tibber_prices`'s
`verdict == "reauth"` branch. **instance**: confirmed by direct read — the branch calls
`_tibber_start_reauth()` (Repairs flow) then unconditionally falls into
`_tibber_fetch_failed()` → `_raise_update_failed()`, and `ConfigEntryAuthFailed` does not
appear anywhere in `custom_components/heatpump_optimizer/`.

**D14-s4-02** (replay clock): widened per the seam_rule ("every `dt_util.freeze(...)` call
site under `tests/`") — 100 call sites total:

| file | freeze() sites | disposition |
|---|---|---|
| `tests/replay.py` | 2 | **instance** — the nightly replay loop itself; confirmed moving under `--zone-clock` (0→9-10 wrong sites) |
| `tests/dst_checks.py` | 29 | not applicable — this IS the DST test suite: every freeze here already pins an explicit fold/gap instant chosen to exercise a transition, not a fixed-offset simulation clock standing in for wall time across many cycles |
| `tests/features.py` | 51 | not applicable — single-instant unit fixtures (one `freeze`/`unfreeze` pair per test scenario), not a multi-cycle replay loop |
| `tests/entities.py` | 12 | not applicable — same shape as `features.py` |
| `tests/golden.py`, `tests/rolling.py`, `tests/guard_pins.py` | 2 each | not applicable — same shape |

## Count

N = 6 (all six round-9 findings verified, all reproduced). No new distinct mechanism
found by widening (the two custom probes formalise findings the judge already verified by
grep; the freeze()-site widening confirms every other call site is a different, unrelated
use of the same stub function, not another instance of "a replay lane frozen at a
fixed offset"). **N = 6, rca = true** (already ≥ 3; matches the judge).

## Barrier proposal

- **P11 is structural, not fixable per-stub.** The class's own mechanism (a hand-written
  test double drifts from the real behaviour it stands in for) is best barriered by a
  **contract test suite** that runs the SAME assertions against both the stub and (in CI,
  behind a marker, on a schedule rather than every PR) the real `homeassistant` package —
  `tests/ha_contract.py` already exists for exactly this (D1-s2-71 cites it as one of the
  disagreeing readers); extend its coverage to the other four stubs (`storage.py`,
  `dt.py`, and the two new probes) rather than adding new one-off scripts per stub.
- Barrier cost: one nightly job running the real `homeassistant` package's own unit tests
  against the same fixtures already recorded, which is what the D1 finders' own
  perturbations already prove would catch each divergence. Estimated gate seconds: not on
  the PR-blocking path (nightly only), so 0 added to the PR gate.

## Exposure

None beyond the two custom probes, which read code/behaviour directly rather than
executing a HA runtime (no HA core install available in this container; both probes are
static-argument calls into the exact same functions the finder's evidence already names).
