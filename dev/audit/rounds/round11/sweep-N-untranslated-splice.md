# Class sweep: N-untranslated-splice (round 11, D14 steps 3-4)

**Property.** A message the integration shows in sv or de is entirely in that
language whenever the integration owns the text. A seam of the class hands a
localized template a runtime string the integration never translates: an
exception's `str()`, an upstream `err.message`, or a backend `error` field.

**Class ledger.** `dev/audit/config/bugclasses.json` has no entry for this
class yet; it is new this round (finding D4-s3-01, `class_guess: new`). The
nearest done record, `#1546 untranslated UpdateFailed raises`, covers raises
that have no translation key, not translated templates with an untranslated
placeholder.

## Detector

`python3 dev/audit/rounds/round11/D14/N-untranslated-splice/enumerate.py`
scans the whole package and has three arms:

- `js-errmsg`: a card `L(...)` placeholder fed from `err.message` or `String(err)`.
- `js-errfield`: a card `L("errors.*", {err: x.error})` fed from a backend result's `error` string.
- `py-ph-exc`: a `translation_placeholders` `"error"` value taken from an exception (`str(err)`, `str(error)`, or a slice of one).

`bash dev/audit/rounds/round11/D14/N-untranslated-splice/controls.sh` runs all three controls:

| control | result |
|---|---|
| positive | TOTAL 18. The list includes all 10 card sites behind D4-s3-01 (the finding's `seam_rule` lines 11038, 11082, 11091, 11641, 11660, 13332, 13437, 13937, 14173, 15098) |
| null | TOTAL 0 on `fixture_clean/`, where the card localizes the error and the raise uses only owned placeholders |
| perturbation | TOTAL 0 -> 1 when one line of the clean fixture is changed back to `{ err: (err && err.message) \|\| err }` |

## Dispositions (18 seams: all are instances, none guarded, none not-applicable)

Each Python probe is `python3 dev/audit/rounds/round11/D14/N-untranslated-splice/probe.py <translation_key>`.
The probe renders the sv `exceptions.<key>.message` with the text the seam
actually passes. For the dhw arms that text comes from a real
`DHWWindowError` raised by `dhw_schedule.parse_windows`. The probe exits 1 on
an English fragment. All seven Python probes fail at this tree, for example:
`Ogiltiga varmvattentider "X": Invalid minute in '25:99'`.

Beyond the finding (8):

| seam | what is spliced |
|---|---|
| services.py:439 `_refuse_quiet` | `str(DHWWindowError)` into the quiet-window refusal |
| services.py:672 set_thermal_params | `str(DHWWindowError)` |
| services.py:810 simulate_plan_invalid_windows | slice of the English `whatif.Refused` text |
| services.py:818 simulate_plan_failed | `str(error)`, the solver or worker exception |
| services.py:1006 apply_schedule | `str(DHWWindowError)` |
| services.py:1157 manual_plan_invalid_slots | the whole sv message is `{error}`, so the user sees only English `ManualPlanError` text |
| services.py:1285 diagnose_interval_failed | `str(ProcessWorkerUnavailable)` |
| card.js:13428 `errors.could_not_simulate` | `first.error`, which is `str(err)` from coordinator.py:11234/11242 |

Judged sites (10, D4-s3-01): the `(err && err.message)` card failure lines
listed above. Their probe is the finding's `m3_look.mjs --err=ha` grid.

**Consequence for the finding's proposed fix.** A card helper that reads
`translation_key` through `hass.localize` does not close the class. The
translated template still carries English `{error}` text from the 7 Python
seams. The barrier therefore needs both halves:

1. Module errors (`DHWWindowError`, `ManualPlanError`, `whatif.Refused`) carry a code and placeholders that the raise translates.
2. The card localizes rejections.

## Proposed barrier

Make `enumerate.py` a `tests/` script that refuses any new seam, at a cost of
under 1 gate second (one regex pass over the package). It would start from an
allow-list of the 18 seams above, and the list could only shrink. It is not
built in this round (tooling freeze); it goes to round-end triage.
`barriered: false`.
