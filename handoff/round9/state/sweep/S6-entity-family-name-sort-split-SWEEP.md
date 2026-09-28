# Class sweep — "an entity family whose names do not lead with a shared token splits under the name sort"

Not in `tools/audit/bugclasses.json` (new class this round).

Round-9 finding: **D8-s3-01** (weakened(low) — of the roster's production-defined entity
families, two split into more than one run under the English/Swedish name sort:
`accuracy` (`PredictionAccuracySensor` + `DiagnoseIntervalButton`, names "Prediction Accuracy" /
"Diagnose Last Interval" do not share a lead token) and `energy_meters` (six `_AccumulatingSensor`
members whose names lead with "Cost"/"DHW"/"Space Heating"/"Total").

## Enumerator

`tools/audit/round9/D14/sweep/entity-family-name-sort-split/enumerate.sh` reuses the finder's own
harness verbatim (`tools/audit/round9/D8/s3/m3_families.py`), which already walks every
production-defined family (`tariff`, `learning`, `accuracy`, `pv`, `card_headline`,
`energy_meters`) across all three roster sort orders (`entity_id`, English name, Swedish name) —
it IS the class enumerator, not merely the finder's own positive control.

Positive control: `RESULT families_split_unexplained_name_en=2, _name_sv=2` reproduces exactly
the docstring's own `Expected` line.
Null control: `tariff`, `learning`, `pv`, `card_headline` all read `0` unexplained splits in every
ordering — their members share a translation-key lead token.
Perturbation: `--perturb` (the Diagnose Last Interval button's names take the accuracy family's
lead token) drops `families_split_unexplained_name_en`/`_name_sv` from 2 to 1 — documented in the
harness header, not re-run here (cheap but already the judge's own perturbation for this
finding).

## Disposition

| seam (family) | disposition | note |
|---|---|---|
| `accuracy` (`PredictionAccuracySensor`, `DiagnoseIntervalButton`) | **instance** | `SPLIT_UNEXPLAINED` under both name orders. |
| `energy_meters` (6 `_AccumulatingSensor` members) | **instance** | `SPLIT_UNEXPLAINED` under both name orders **and** under `entity_id` (`families_split_unexplained_entity_id=1`, a run the sweep's wider run confirms beyond the finding's own name-sort scope — same family, same mechanism, not a second instance). |
| `tariff`, `learning`, `pv`, `card_headline` | **guarded** | `0` unexplained splits in every ordering — members already share a lead token. |

## Count

N = 1 verified/weakened finding (D8-s3-01, covering both the `accuracy` and `energy_meters`
families as one mechanism) + 0 additional sweep-confirmed instances (the `entity_id`-sort split
on `energy_meters` is the same family already counted, not a new one). **rca = false** (N=1 < 3,
not a ledger class, not barriered) — matches the class table's precomputed N=1/rca=no.

## Barrier proposal

None proposed at N=1: a lint rule requiring every production entity family's member names to
share a lead token would need design input (which token is canonical per family) — flag as a
`hygiene`-severity fix-time decision, not a sweep-time barrier.
