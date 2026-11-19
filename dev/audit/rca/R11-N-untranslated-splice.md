# RCA: an English upstream string spliced into a localized message

Seat: round-11 root-cause, class `N-untranslated-splice` (instrument). Instances R11 9, 9 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`I4`) as one (`fold_ledger.py` `_group_counts`): `N-instrument-locator`, `N-unordered-tiebreak`, `N-untranslated-splice`, 11 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

Service handlers raise a translated `HomeAssistantError` and pass `str(error)` from an
upstream exception (`DHWWindowError`, `ManualPlanError`, `ProcessWorkerUnavailable`) as a
placeholder. The card prints `err.message`, the English text. Swedish and German users then read
an English fragment inside their own language, in 24 of 24 non-English error cells (D4-s3-01). The
sweep lists 7 service sites and 1 card site. The translation keys exist. The variable part is the
upstream exception's own English text, and nothing translates it.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D4-s3-01` (weakened, low): planted copy: english_error_lines=24 over 24 non-en error cells; --perturb err_localize -> 0; perturbation: --perturb=err_localize: every `(err && err.message) || err` site first reads hass.localize(`component.${err.translation_domain}.exceptions.${err.translation_key}.message`, err.translation_placeholders).

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `node dev/audit/rounds/round11/D4/s3/m3_look.mjs --vp=375,768,1280 --err=ha --states=pin_fail,save_fail` took 24 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-untranslated-splice.json`) lists 18 seams. The ledger carries 8 of the seams as instances beyond the finding. Its enumerator is cited as `python3 dev/audit/rounds/round11/D14/N-untranslated-splice/enumerate.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (a) the process did not exist

D4 checks rendered text per language, and its round-11 seat drove the error states for the
first time (`m3_look.mjs --states=pin_fail,save_fail`). D10's `exception-translations` rule grades
whether an exception has a translation key. A key with a raw-English placeholder passes it. No
step looked at what is spliced into the placeholder.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 9 instances over the 148 releases they accumulated in, 0.061 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.061 x 15660 s | 952 s/release |
| form | a static `tests/` arm refusing a `translation_placeholders` value built from `str()` of an exception, plus one card helper that renders a service rejection through `hass.localize` |
| catch share q | 0.9: the 7 service seams share the `str(error)` placeholder shape; the card seam is closed by the helper; the residue is a placeholder built by another spelling |
| expected benefit, q x cost | 857 s/release |
| arm time | 0.5 s (an estimate for one AST pass over services.py; the sweep's enumerator is not tracked) |
| standing cost, arm x 16.3 PRs | 8.1 s/release |
| verdict | passes by 105.3x |

### Countermeasure (a class barrier, proposed; not built by this seat)

The arm must show red on this baseline (7 service sites) and green after the upstream
errors carry a translation key and placeholders of their own. The card helper reads the translated
exception, with `hass.loadBackendTranslation('exceptions')` first. The fix PR owns both.
