Part of #2271. Part of #201.

Download diagnostics now fills the `hpo-debug/1` bundle's replay half, which was `None`, with an `hpo-replay/1` document built when the file is downloaded. This is the owner's R10-DIAG-REPLAY (tvofi, 2026-10-14).

- **One copy of the rules.** The allowlist, the sanitiser, `violations`, the leak check (`seal`) and the Tibber price-sensor choice (`tibber_price_candidates`, `choose_price_entity`) move out of `tools/replay/export.py` into `custom_components/heatpump_optimizer/replay_doc.py`. That module imports only the standard library, and the export loads it by path. So the export still runs under the interpreter in the Home Assistant container. `tools/replay/export.py` keeps only its SQLite reader, the `.storage` reader, `check_file` and the command line. Over the committed synthetic day it writes the same bytes as before.
- **Read through the recorder.** `debugger.py` reads state history with `recorder.history.get_significant_states`, run through `get_instance(hass).async_add_executor_job`, never raw SQLite. `manifest.json` gains `recorder` in `after_dependencies`.
- **The window and the cap.** The window is the collection's own, at most `REPLAY_SPAN` (7 days), ending at the download. If a document would push the download past `INLINE_CAP_BYTES`, the bundle takes the newest shorter window in `REPLAY_SPANS` that fits. The measure is the download bytes with the manifest note included. If no window fits, the replay half is `None` and the manifest says why. Every refusal (no recorder, no Tibber price sensor, a leak, a recorder error) is a `manifest.replay` reason, never an exception.
- **Person and calendar entities stay out.** Diagnostics redacts their ids in values only (`_without_private_ids`), so they would survive as `states` keys. `PRIVATE_ENTITY_ID` moves to `const.py`, shared by both modules.
- **Forward-carry from #2209.** Each cycle row now carries `version`, the `integration_version` that wrote it. `store.DOMAINS["debug"]` declares it as text.
- **A pre-existing export defect, found by the new equality check.** The export read the entry allowlist off `const.py` with a line pattern. That pattern missed the two `CONF_*` values wrapped onto a second line, so every export dropped `heat_pump_capacity_limited_entity` and `internal_gains_learning_enabled` from the entry. `replay_doc.conf_keys` now reads a loaded `const` namespace. The integration passes its own namespace; the export loads the installed `const.py` by path and passes that.

The tests are in `tests/debug_collect.py`, the gate's driver for the debugger. Each one runs on a generated download built by the real `diagnostics.async_get_config_entry_diagnostics`:
- `tests/replay.py`'s check mode (`export.check_file`).
- A planted-credential null control.
- Every one of the nightly lane's `LEAK_PROBES`, planted where `tests/replay.py` plants them.
- `nightly_ha`'s A10 rule over the whole download.

## Head

`f32ad0272f8471bfd19f8e6e4b264592fb9edf8b`. Figures were measured at `98417060ab59f69b3611d022970286059f668859`, 2026-10-18T15:59:56Z, with `origin/main` at `55dc8d9c2c59c2ab614cb7c5d4b0ae9807401b50`, the merge base. The head is the previous PR head `33dfae1e672fe87d467cf8feb772b138ae7a3471` (the bot's `ci: pin killed mutants`) plus six commits:

- `3bdf8cb0a8c0b2a301a49491712456bc5c06105e` merges `origin/main` at `55dc8d9c`. Two files conflicted, both on the module-count history. Main's `plan_step.py` and this branch's `replay_doc.py` had each taken the package to 79 modules (97 files). Both are now counted: 80 modules, 98 files. The round-4 D6 harness header (`dev/audit/rounds/round4/D6/claims.py`) and `tests/deployment_shape.py`'s selection-cost note keep both histories. `docs/architecture.md` says 80. The D6 harness was re-run and its output regenerated: `arch_modules_on_disk=80`, `arch_map_listed=80`, `arch_map_missing=0`, `ha_module_level_importers=28`.
- `1a1a6a9c` and `55d80cbe` answer the two reds below: rule-level checks of `replay_doc` in `tests/debug_collect.py`, and one redundant guard deleted from `replay_doc.sanitise`.
- `20ff52b5` and `98417060` bring the mutation ledger up to date. They drop the pin of the deleted guard's site, and pin the 44 sites `tests/debug_collect.py` now kills.
- `beff6fac` changes one line of `docs/architecture.md`: 51 modules free of `homeassistant`, where it said 50. Each side of the merge said 50 of 79. The merged 80 hold 28 module-level importers plus `inputs`, which imports it only inside a function. `doc_claims` caught this locally at `98417060` (`documented=50 measured=51`). At `beff6fac`, `doc_claims` passes 169 of 169 and the D6 harness reads `claims_true=123 claims_false=0`, with its committed output unchanged.
- `f32ad027` renames one test variable in `tests/debug_collect.py`, `_kept` to `_shape_cut`, because it shadowed `debugger._kept` (`prepr.sh`'s `no-copies` refused it). At this commit `tests/debug_collect.py` still passes 122 of 122.

The previous PR head's delivery row is not in this tree. Writing it is the orchestrator's job.

Two more changes since the last body:

- **The gate now checks `replay_doc`'s rules directly.** Until now only the nightly lane (`tests/replay.py`) drove the edges the download never reaches. `tests/debug_collect.py` now drives them too: `numeric`, `json_decimal_places`, `clean_value`, every attribute shape, the entry shape, every finding `violations` names, `mapped_entities`, both of `seal`'s refusals and its six-character floor, and `choose_price_entity` with two homes. It also checks three debugger edges: a calendar id inside a list, `last_reported` equal to `last_updated`, and a download exactly on the inline cap.
- **One judge for a state's text.** `sanitise` used to null a state string that fails `text_ok`, then pass the whole payload through `clean_value`, which nulls the same string and records it the same way. The first test was a second copy of the rule. Its mutant survived because no input can tell the two apart. The copy is deleted, and the closing `clean_value` now judges every string. Nothing else changed: the export's synthetic day is byte-identical, and the sanitiser and leak-probe checks still pass 56 of 56 (Figures).

## Mutation proof

The eight mutants were re-run at `98417060` by a scratch runner. Each one edits a copy of the worktree, runs `PYTHONPATH=tests/hastub python3 tests/debug_collect.py`, and counts the failing checks. The unmutated run passes 122 of 122. All eight exit 1:

| Mutant | Production edit | Checks that go red at `98417060` |
|---|---|---|
| M1 | `async_bundle`: `if entry is not None:` becomes `if False:` | "Download diagnostics fills the bundle's replay half...", then a `TypeError` on the missing half stops the run |
| M2 | `_public`: the private-id test removed, so it returns the node | 25: the three download checks, all 21 leak-probe checks, and "a person or calendar id leaves a list as well as a value" |
| M3 | `fit_replay`: the cap test becomes `if True:` | "...gives way to the newest shorter window that fits..." and "when no window fits the inline cap..." |
| M4 | `cycle_row`: the `"version"` line deleted | "a cycle row carries the release that wrote it..." |
| M5 | `replay_doc.seal`: `return clean` becomes `return raw` | 24: the two download checks, all 21 leak-probe checks, and "replay_doc.seal refuses a document where a dropped credential survives..." |
| M6 | `store.DOMAINS`: the `rows/#/version` line deleted | "a cycle row carries the release that wrote it..." and "a ring carrying its self-test results is inside the debug store's domain" |
| M7 | `_since`: returns every state, no window trim | "...gives way to the newest shorter window that fits..." |
| M8 | `replay_document`: the Tibber choice skipped (`if False:`) | "with the Tibber source the replay half takes the price series..." and "...no price sensor the replay half is refused..." |

The new checks were proved by the repository's own mutation instrument, not by hand. `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/debug_collect.py --jobs 3` drove the 45 sites CI's `mutation` job had left unpinned:

- First run, on `1a1a6a9c`: 34 killed and pinned, 11 survived.
- Second run, after `55d80cbe`: 10 killed and pinned, 0 left unpinned. The eleventh survivor was the deleted guard.

The baseline (`rc=0 failed=0`) and the comment-only null control both survived every driver in both runs.

The conf-keys mutant was not re-run. It was measured at `aaa61a95`: with `conf_keys` restored to the line pattern, the equality check went red with `216 against 214`. Since then, `git diff --name-only 3fb386d50 55dc8d9c2` names neither `const.py` nor any file of this branch's subject.

## Null control

- **The new checks see what they claim to.** Each check that pins a survivor is the input that tells the two arms apart, and the second `--pin-killed` run shows each mutant red under it. One example: a dropped credential of exactly six characters is refused (`_leaked_six`), and one of five is written (`_short`). That pair goes red under `len(s) > 6`, which is the `CMP_BOUND` mutant at `seal`'s `len(s) >= 6`.
- **Coverage, measured at both ends.** Under `tests/debug_collect.py` alone, with `coverage` from `tests/requirements-coverage.txt`, `replay_doc.py` is 83 % at `3bdf8cb0`, the merge head before these checks. At `98417060` it is 100 %, 276 of 276 statements. The whole-suite figure CI measured at `33dfae1e` was 88.41 %.
- **Deleting the duplicate guard changed no output.** The export's synthetic day still matches its fixture byte for byte. `replay.sanitiser_checks` reads `56 0` at both the merge base and the head. All 21 leak probes still pass through the download.
- **The leak-probe checks can still fail.** With `seal` perturbed to return the raw document (M5 above), all 21 leak-probe checks fail.

## Figures

All figures are at `98417060` unless a merge-base value is given. The merge base is `55dc8d9c`, read from a `git archive` copy.

- `PYTHONPATH=tests/hastub python3 tests/debug_collect.py`: `ALL 122 DEBUG COLLECT CHECKS PASSED` and `RESULT leak_probes_through_download=21 written=21 refused=0 unit=count`. The RESULT line counts every key of `tests/replay.py`'s `LEAK_PROBES` driven through the download, and how many replay halves were written.
- With `T=$(mktemp)`, `PYTHONPATH=tests/hastub python3 tools/replay/synthesize.py --out "$T" && cmp "$T" tests/replay/synthetic-dhw-only.json && echo IDENTICAL` prints `IDENTICAL`.
- `python3 tools/replay/export.py --check tests/replay/synthetic-dhw-only.json`: `0 violation(s)`.
- `python3 -c "import sys; sys.path.insert(0, 'tools/replay'); import export; print(len(export.entry_keys(*export.default_const_paths())))"`: 214 at the merge base, 216 at the head. The rule: the number of distinct `CONF_*` string values the export admits as entry keys.
- `PYTHONPATH=tests/hastub python3 -c "import sys; sys.path.insert(0, 'tests'); import replay; r = replay.sanitiser_checks(sorted(replay.FIXTURES.glob('*.json'))); print(len(r), sum(not x[1] for x in r))"`: `56 0` at both the merge base and the head.
- `git ls-files custom_components/heatpump_optimizer | wc -l`: 98 files. The rule: the package's tracked files, Python and non-Python alike. It reads 97 at the merge base and 97 at the old PR head `33dfae1e`.
- `git diff --name-only --diff-filter=A 20ff52b5e 98417060a | wc -l`: 44 ledger rows added, 41 for `replay_doc.py` and 3 for `debugger.py`.
- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` at `beff6fac`: `ALL 169 checks PASSED`, including `architecture.md`'s `modules_free_of_homeassistant`, which reads 51 measured (at `98417060`: `documented=50 measured=51`).
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py`: `RESULT arch_modules_on_disk=80`, `arch_map_listed=80`, `arch_map_missing=0`, `ha_module_level_importers=28`.
- `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/debug_collect.py --jobs 3`, second run: `PIN KILLED: 10 pinned, 0 left unpinned`. Before that run, its inventory line read `4313 unpinned site(s) of 6249 candidate sites, 4303 at the ratchet base 55dc8d9c...; the ledger agrees with the deterministic inventory`. The 10 it pinned bring the count back to the base's 4303.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/typing_ruler.py` (with `HPO_TYPING_PYTHON` set to the seat's typing venv): `ALL 12 typing-ruler source checks PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/ha_contract.py`: `ALL 96 contracts PASSED`.
- `python3 tools/audit/archscore/score.py --diff 55dc8d9c2c59c2ab614cb7c5d4b0ae9807401b50`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/closure.py select --diff 55dc8d9c2c59c2ab614cb7c5d4b0ae9807401b50 --workdir "$D"`: `MODE: SCOPED -- 31 script(s) run, 2 scoped out.`

## Architecture score

n/a: no gate metric rises (`dS +0.0000 NULL` above).

There is no raise, and no payment was owed this round. The deleted guard is a simplification, not a ratchet payment. An earlier round's payment still stands: `violations` was split into `_entry_violations` and `_state_violations`, which kept `functions_cc_over_15` flat.

## Red checks

These are the reds on the previous PR head `33dfae1e`, read from the check-runs API and the failing jobs' logs:

- **`coverage-ratchet`**: `replay_doc.py: 88.41 %` against the 95 % per-module floor. A real gap. The module's edges were driven only by the nightly lane, which is not in the coverage tree. Answered by `1a1a6a9c` and `55d80cbe`: 100 % under `tests/debug_collect.py` alone (Null control). The cheaper detector was a local `coverage` run of the debugger's own driver before the push. No standing check exists for it, and this seat builds none: CI's per-module floor is that check, and it fired on the first push that carried the module.
- **`mutation`**: `MUTATION TABLE REFUSED -- 4353 unpinned site(s) against 4308 at the ratchet base 3fb386d5..., 45 of them added by this diff`. The bot's first `--pin-killed` pass (`33dfae1e`) pinned what the old checks killed. The 45 left were sites no check could see. Answered by the checks above, the deleted duplicate guard, and the 44 new pins. The second `--pin-killed` run leaves 0 unpinned. The cheaper detector is the same command run locally before the push, which `ci-autofix.md` names for a red autofix.
- **`validate-hacs`**: `aiogithubapi.exceptions.GitHubRatelimitException: API rate limit exceeded for installation` in HACS's own preflight, before it validated anything. This is the runner's shared installation quota, not this branch; the next run re-executes it. No cheaper detector exists for a third party's rate limit.

`entities.py`'s "graders-head-copy's delivery_status step..." was red at the old merge base too, and is left to CI to re-measure at the new one.

Re-run green locally at `98417060` (`GOLDEN_MODE=drift`, `GOLDEN_REF` set to the merge base): `debug_collect`, `deployment_shape`, `doc_claims` (at `beff6fac`), `finite_boundary`, `block_duty`, `config_flow_steps`, `guard_pins`, `manual_plan`, `plan_view`, `solar_alignment`, `wood_advisor`, `structure`, `layout`, `harness_headers`, `typing_ruler`, `golden` (drift: `NO STALE FIXTURE: 56 committed fixture(s) still match`), `env_drift --claims-only` (`claims hygiene: 55dc8d9c... ok`), `closure.py selftest` and `md_tables.mjs`. **Left to CI**: `entities`, `features`, `stress`, `env_drift`, `optimality`, `boost_drift_replay`, `backtest`, `edge`, `validate`, `arch_score_head`, `card.mjs` and `card_drift.mjs`.

## Forward-carry

The `version` stamp invalidates an assumption D15's method step 1 rests on: "`integration_version` is the download's, not each row's". It also retires the input line "While the download's `replay` is null (until R10-DIAG-REPLAY)". Both belong to `dev/governance/dimensions/D15.md`. That file is code-owned policy, and the round's live destination for brief edits is the `R10-BRIEFS-FOLD` group's brief in `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster`, which this seat cannot write. Text to carry:

> D15 M1: a row carrying `version` is that release's; the restart-gap rule applies only to rows without one. Control: `tests/debug_collect.py`'s "a cycle row carries the release that wrote it" goes red with the stamp removed from `debugger.cycle_row`. D15 inputs: the download's `debug.replay` is filled when the recorder is set up and the window fits the inline cap; otherwise `debug.manifest.replay` names why, and the export from the same box and window stands in. Re-measure at the D15 baseline.

## Unpinned sites

None: `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/debug_collect.py` leaves 0 of this diff's sites unpinned (Figures); of the 45 CI listed, 44 now carry a `killed_by` row in `tests/mutation_ledger/killed_by/` and the 45th left the tree with the deleted guard.

## Friction

- `fixer.md`: `cost`: a change to `const.py` or `store.py` scopes 32 of 33 scripts, so the scoped gate is close to a full run for any debug-bundle field.

