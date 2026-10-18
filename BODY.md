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

`36b786eb38682a22b3f5d6e1d3738692ee1d240b`, on merge base `c09d61dc9c9779e721eb73b1ea402913a52242fb`. Measured 2026-10-18 10:10 UTC; `origin/main` was then at `f00e1d85`, whose 9 changed files since the merge base include none this branch changes.

## Mutation proof

Each mutant was run from a scratch worktree at the head with `PYTHONPATH=tests/hastub python3 tests/debug_collect.py`, then restored. All 8 exit 1:

| Mutant | Production edit | Checks that go red |
|---|---|---|
| M1 | `async_bundle`: `if entry is not None:` becomes `if False:` | "Download diagnostics fills the bundle's replay half with an hpo-replay/1 document that the export's check mode passes" |
| M2 | `_public`: the private-id test removed, so it returns the node | 24 checks, among them "...carries no person or calendar id anywhere", "...the export's check mode passes" and all 21 leak-probe checks |
| M3 | `fit_replay`: returns the first document without the cap test | "a replay half that would take the download past the inline cap gives way to the newest shorter window that fits..." and "when no window fits the inline cap the replay half is empty..." |
| M4 | `cycle_row`: the `"version"` line deleted | "a cycle row carries the release that wrote it, and the debug store admits it (#2209)" |
| M5 | `replay_doc.seal`: returns the unsanitised document | "Download diagnostics fills the bundle's replay half..." (the manifest reads "refusing to write: 3 dropped credential value(s) survive elsewhere in the payload": the leak check refuses it) |
| M6 | `store.DOMAINS`: the `rows/#/version` line deleted | "a cycle row carries the release that wrote it..." and "a ring carrying its self-test results is inside the debug store's domain" |
| M7 | `_since`: returns every state, no window trim | "a replay half that would take the download past the inline cap gives way to the newest shorter window that fits..." |
| M8 | `replay_document`: the Tibber choice skipped | "with the Tibber source the replay half takes the price series from the Tibber price sensor..." and "...no price sensor the replay half is refused as the export refuses..." |

The conf-keys fix has its own mutant. With `conf_keys` restored to the line pattern, the equality check went red: `216 against 214: ['heat_pump_capacity_limited_entity', 'internal_gains_learning_enabled']`.

## Null control

- **Merge base, with this branch's `tests/debug_collect.py` and stubs copied in.** The suite is red: "a cycle row carries the release that wrote it..." fails, then `TypeError: DebugCollector.async_bundle() takes from 2 to 3 positional arguments but 4 were given`. The replay half cannot be asked for at the base.
- **The leak-probe checks can fail.** With `replay_doc.seal` perturbed to return the raw document unchecked, 23 of 108 checks fail, all 21 leak-probe checks among them: each probe's planted text is found in the replay half.
- **The export does follow `replay_doc`.** With `MAX_COORDINATE_DECIMALS` perturbed to 3 in `replay_doc.py` alone, the export's synthetic day no longer matches the committed fixture byte for byte (`cmp -s` false). At the head, unperturbed, it matches.

## Figures

- `PYTHONPATH=tests/hastub python3 tests/debug_collect.py`: `ALL 108 DEBUG COLLECT CHECKS PASSED` at `36b786eb`. Its `RESULT leak_probes_through_download=21 written=21 refused=0 unit=count` line counts every key of `tests/replay.py`'s `LEAK_PROBES` driven through the download, and how many replay halves were written.
- `PYTHONPATH=tests/hastub python3 tools/replay/synthesize.py --out "$T" && cmp "$T" tests/replay/synthetic-dhw-only.json && echo IDENTICAL` (with `T=$(mktemp)`): prints `IDENTICAL` at the head. The fixture was written at the base.
- `python3 tools/replay/export.py --check tests/replay/synthetic-dhw-only.json`: `0 violation(s)`.
- `python3 -c "import sys; sys.path.insert(0, 'tools/replay'); import export; print(len(export.entry_keys(*export.default_const_paths())))"`: 214 at the merge base, 216 at the head. The rule is the number of distinct `CONF_*` string values the export admits as entry keys.
- `PYTHONPATH=tests/hastub python3 -c "import sys; sys.path.insert(0, 'tests'); import replay; r = replay.sanitiser_checks(sorted(replay.FIXTURES.glob('*.json'))); print(len(r), sum(not x[1] for x in r))"`: `56 0` at both the merge base and the head. These are the nightly lane's sanitiser, leak-probe and Tibber checks through the moved rules.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/typing_ruler.py` (with `HPO_TYPING_PYTHON` set): `ALL 12 typing-ruler source checks PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/ha_contract.py`: `ALL 96 contracts PASSED`, the two new recorder stub contracts included.
- `python3 tools/audit/archscore/score.py --diff c09d61dc9c9779e721eb73b1ea402913a52242fb`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/closure.py select --diff c09d61dc9c9779e721eb73b1ea402913a52242fb --workdir "$D"`: `MODE: SCOPED -- 31 script(s) run, 2 scoped out.`

## Architecture score

n/a: no gate metric rises (`dS +0.0000 NULL` above).

A ratchet payment was made rather than a raise. `violations` entered measured code at cyclomatic complexity 21 and moved `functions_cc_over_15` from 31 to 32. It is split into `_entry_violations` and `_state_violations`, and the ratchet passes with no budget touched. The first cut also added a second dead top-level symbol: the text-parsing `conf_keys`, which only `tools/` read. That was paid by making the one rule serve both writers, not by recording a raise.

## Red checks

none. Four scripts went red locally on the first cut and are fixed in this branch:
- `deployment_shape`: reading `const.py` by path from the package. The read is gone; the integration uses its own `const` namespace.
- `doc_claims`: `docs/architecture.md`'s module counts are updated to 78 and 49.
- `finite_boundary`: its seeded row's stand-in lacked `integration_version`, and now seeds it.
- `typing_ruler`: 22 strict errors in the moved code, all annotated, with no ignore.

The cheaper detector for each was the script itself, run before the push. Closures were recorded on Linux for the 12 scripts that read the new files (`derive_closures.sh --scripts-from`). The rest of the selected scripts that read them, `features.py`, `entities.py`, `harness_headers.py` and others, are left to `closures-autofix`'s UNDER-SCOPED repair (`ci-autofix.md`).

## Forward-carry

The `version` stamp invalidates an assumption D15's method step 1 rests on: "`integration_version` is the download's, not each row's". It also retires the input line "While the download's `replay` is null (until R10-DIAG-REPLAY)". Both belong to `dev/governance/dimensions/D15.md`. That file is code-owned policy, and the round's live destination for brief edits is the `R10-BRIEFS-FOLD` group's brief in `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster`, which this seat cannot write. Text to carry:

> D15 M1: a row carrying `version` is that release's; the restart-gap rule applies only to rows without one. Control: `tests/debug_collect.py`'s "a cycle row carries the release that wrote it" goes red with the stamp removed from `debugger.cycle_row`. D15 inputs: the download's `debug.replay` is filled when the recorder is set up and the window fits the inline cap; otherwise `debug.manifest.replay` names why, and the export from the same box and window stands in. Re-measure at the D15 baseline.

## Unpinned sites

Each site is driven by `tests/debug_collect.py` (the debugger's gate driver, which builds the replay half through every `replay_doc` rule) and by `tests/replay.py`'s sanitiser checks; CI's `mutation` job pins the ones it kills (`ci-autofix.md`).

- custom_components/heatpump_optimizer/debugger.py:367 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:369 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:369 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:374 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:376 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:378 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:380 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:408 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:409 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:409 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:416 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:416 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:430 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:441 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:448 CLAMP_DROP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:452 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:452 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:454 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:616 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:619 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/debugger.py:623 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:40 CONST: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:109 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:137 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:137 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:139 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:152 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:158 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:161 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:163 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:165 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:173 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:175 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:180 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:182 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:184 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:188 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:191 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:191 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:200 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:203 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:215 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:216 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:218 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:218 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:220 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:221 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:231 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:233 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:233 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:235 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:239 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:239 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:241 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:245 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:250 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:252 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:260 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:262 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:266 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:270 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:271 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:271 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:273 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:277 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:288 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:298 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:299 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:299 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:301 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:302 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:303 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:304 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:305 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:306 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:316 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:319 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:322 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:345 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:347 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:347 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:353 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:361 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:363 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:365 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:367 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:370 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:376 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:379 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:379 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:381 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:383 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:383 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:383 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:386 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:389 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:389 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:401 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:412 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:412 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:414 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:416 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:422 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:425 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:425 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:426 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:428 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:432 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:434 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:436 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:445 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:445 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:447 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:450 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:453 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:467 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:471 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:504 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:504 CMP_BOUND: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:505 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:511 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/replay_doc.py:513 RETURN_DEL: pinned by mutation-autofix

## Friction

- `fixer.md`: `cost`: a change to `const.py` or `store.py` scopes 32 of 33 scripts, so the scoped gate is close to a full run for any debug-bundle field.
