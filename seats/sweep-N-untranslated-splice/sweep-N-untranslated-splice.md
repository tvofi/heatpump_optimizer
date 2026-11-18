# Class sweep: N-untranslated-splice (round 11, phase D)

Class mechanism: a localized message interpolates text the integration does not
translate, so sv/de users read an English fragment inside their language.
Judged finding: D4-s3-01 (weakened, low), the card's `err.message` failure lines.
Ledger status: the class is new this round (absent from `bugclasses.json`).

## Enumerator

`python3 dev/audit/rounds/round11/D14/sweep/untranslated_splice.py`. It lists:

- every value of a `translation_placeholders` / `description_placeholders` /
  `placeholders` dict literal in the package that reads an exception or an error string
  (an `except ... as` name, `str(err)`, `.args`/`.message`, or a local named
  err/error/detail/reason/cause/msg);
- every card `L()` parameter that reads `err.message` or `String(err)`.

At the register head it lists 21 seams. Controls (`untranslated_splice_controls.sh`):

| control | result |
|---|---|
| positive: the finding's seam_rule (`grep -nE "err(\.message\| && err\.message)"` on the card) | 10 sites, and the enumerator lists all 10 |
| null: a clean fixture with entity-id and numeric placeholders, plus an `L()` that has no `.message` | 0 |
| perturbation: a one-line `"error": str(err)` added to `debugger.py:724` in a copy | 21 -> 22 |

## Dispositions

**The finding's own sites (10, beyond_finding false).** Card lines 11038, 11082
and 11091 (`advisor.apply_failed`), then 11641, 11660, 13332, 13437, 13937,
14173 and 15098 (`errors.could_not_*`). These are the verifier's "10 splice
sites", and the finding's harness `m3_look.mjs --err=ha` is their probe.

**Instances beyond the finding (10).** The Python side, where the server splices
the integration's own English text into an sv/de template. This survives even a
card fixed with `hass.localize`, because the translated exception message itself
carries the English text. Each one fails
`untranslated_splice_probe.py <seam>`, which renders the sv and de templates with
the value the producing code really returns (it calls `parse_windows` and
`build_override` for the windows and manual-plan seams):

| seam | probe | rendered sv |
|---|---|---|
| services.py:439 `_refuse_quiet` | quiet_windows | `Ogiltiga tysta fönster: Invalid minute in '25:99'` |
| services.py:672 set_thermal_params | dhw_windows_set_thermal | `Ogiltiga varmvattentider "…": Invalid minute …` |
| services.py:1006 apply_schedule | dhw_windows_apply | same |
| services.py:810 simulate_plan, invalid windows | dhw_windows_simulate | same |
| services.py:818 simulate_plan_failed | simulate_failed | `Simuleringen kunde inte köras för …: <str(Refused)>` |
| services.py:1157 manual_plan_invalid_slots | manual_plan | the whole message is English: the sv/de template is the bare `{error}` |
| services.py:1285 diagnose_interval_failed | diagnose_failed | `Intervalldiagnosen kunde inte köras för …: <str(ProcessWorkerUnavailable)>` |
| store.py:798 store_version issue | store_version | `… kan inte läsas: it was saved at version 3 and this release reads 2.` |
| pump_arbiter.py:1552 pump_write_ignored issue | pump_write_ignored | `…: number.x: 45 (set by the optimizer: 52)` |
| issues.py:88 price_feed_stale issue | price_feed_stale | `Priskällan levererade inga nya priser (Error fetching Tibber prices: …)` |

**Not applicable (1).** coordinator.py:2249 `solve_worker_fallback {cause}` is an
arbitrary upstream exception with no translated counterpart. The template quotes
it as the line to attach to a report, and the finding's own null control counts
no rejection that lacks a translation.

## Count and barrier

There are 10 instances beyond the finding, and the class is not barriered.
Proposed barrier: a `tests/` AST lint built on the enumerator. It refuses an
exception-derived placeholder or `L()` parameter unless the value comes through
a translated mapping: an exception subclass that carries its own
`translation_key` and placeholders, or one card helper that reads
`err.translation_key` through `hass.localize`. Its cost is one AST pass over the
package, under 1 s of gate time.
