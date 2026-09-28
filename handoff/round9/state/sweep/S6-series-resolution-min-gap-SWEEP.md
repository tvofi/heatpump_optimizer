# Class sweep — "series resolution inferred from the minimum gap"

Not in `tools/audit/bugclasses.json` (new class this round).

Round-9 finding: **D1-s5-04** (verified, low — `open_meteo.py:231` infers the irradiance series'
sample resolution as `timedelta(seconds=min(gaps))` over all positive consecutive-timestamp gaps.
A single spurious small gap — a duplicate or near-duplicate timestamp, an out-of-order sample
that survives the sort — collapses the inferred resolution far below the series' true, regular
spacing, which then misdescribes every downstream consumer of `IrradianceSeries.resolution`).

## Enumerator

`tools/audit/round9/D14/sweep/series-resolution-min-gap/enumerate.sh` greps every "resolution ="
assignment and every `min(gaps)`-shaped computation across `custom_components/heatpump_optimizer/*.py`.

## Disposition

| seam | disposition | note |
|---|---|---|
| `open_meteo.py:231` (`resolution = timedelta(seconds=min(gaps))`) | **instance** | D1-s5-04 itself — the only time-series resolution inferred from a raw minimum gap. |
| `config_flow.py:2394`, `:3798`, `prefill_offer.py:100` (`resolution = device_prefill.resolve_with_fallback(...)`) | **not applicable** | Unrelated mechanism — `resolution` here names a device-identity *conflict resolution* result (`resolve_with_fallback`), not a time-series sampling interval; the name collision is coincidental, not a second seam of this class. |

## Count

N = 1 verified finding (D1-s5-04) + 0 additional sweep-confirmed instances (no other time-series
resolution inference exists in the package). **rca = false** (N=1 < 3, not a ledger class, not
barriered).

## Barrier proposal

None proposed at N=1: the fix (a robust interval estimate — e.g. the modal or median gap, or a
gap floor tied to the feed's declared cadence) is local to `open_meteo.py`'s one function; not
worth a permanent structural gate for a single call site.
