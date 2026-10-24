Part of #2271. Part of #201.

Download diagnostics now fills the `hpo-debug/1` bundle's replay half, which was `None`, with an `hpo-replay/1` document built when the file is downloaded. This is the owner's R10-DIAG-REPLAY (tvofi, 2026-10-14).

- **One copy of the rules.** The allowlist, the sanitiser, `violations`, the leak check (`seal`) and the Tibber price-sensor choice (`tibber_price_candidates`, `choose_price_entity`) move out of `tools/replay/export.py` into `custom_components/heatpump_optimizer/replay_doc.py`. That module imports only the standard library, and the export loads it by path. So the export still runs under the interpreter in the Home Assistant container. `tools/replay/export.py` keeps only its SQLite reader, the `.storage` reader, `check_file` and the command line. Over the committed synthetic day it writes the same bytes as before.
- **Read through the recorder.** `debugger.py` reads state history with `recorder.history.get_significant_states`, run through `get_instance(hass).async_add_executor_job`, never raw SQLite. `manifest.json` gains `recorder` in `after_dependencies`.
- **The window and the cap.** The window is the collection's own, at most `REPLAY_SPAN` (7 days), ending at the download. If a document would push the download past `INLINE_CAP_BYTES`, the bundle takes the newest shorter window in `REPLAY_SPANS` that fits. The measure is the download bytes with the manifest note included. If no window fits, the replay half is `None` and the manifest says why. Every refusal (no recorder, no Tibber price sensor, a leak, a recorder error) is a `manifest.replay` reason, never an exception.
- **Person and calendar entities stay out.** Diagnostics redacts their ids in values only (`_without_private_ids`), so they would survive as `states` keys. `PRIVATE_ENTITY_ID` moves to `const.py`, shared by both modules.
- **Forward-carry from #2209.** Each cycle row now carries `version`, the `integration_version` that wrote it. `store.DOMAINS["debug"]` declares it as text.
- **A pre-existing export defect, found by the new equality check.** The export read the entry allowlist off `const.py` with a line pattern. That pattern missed the two `CONF_*` values wrapped onto a second line, so every export dropped `heat_pump_capacity_limited_entity` and `internal_gains_learning_enabled` from the entry. `replay_doc.conf_keys` now reads a loaded `const` namespace. The integration passes its own namespace; the export loads the installed `const.py` by path and passes that.
- **The gate checks `replay_doc`'s rules directly.** `tests/debug_collect.py` drives the edges the download never reaches: `numeric`, `json_decimal_places`, `clean_value`, every attribute shape, the entry shape, every finding `violations` names, `mapped_entities`, both of `seal`'s refusals and its six-character floor, and `choose_price_entity` with two homes. `sanitise`'s first `text_ok` test, a second copy of the rule the closing `clean_value` applies, is deleted; the synthetic day stays byte-identical (Figures).
- **A leak check's detail counts and never echoes a value (round 2, CodeQL).** CodeQL's `py/clear-text-logging-sensitive-data` fired at `tests/harness.py`'s FAIL print. It was reached from `str(_secret_drop)`: the detail of the check that values under credential keys are recorded printed those values. Three `replay_doc` leak checks in `tests/debug_collect.py` now build their detail with `_unrecorded`, as `seal`'s own refusal does: the positions of the expected values that were not recorded, and a count of the rest. `seal`'s check names the type of a non-refusal instead of printing the document. The conditions are unchanged, so the same mutants fail the same checks.

The tests are in `tests/debug_collect.py`, the gate's driver for the debugger. Each one runs on a generated download built by the real `diagnostics.async_get_config_entry_diagnostics`:
- `tests/replay.py`'s check mode (`export.check_file`).
- A planted-credential null control.
- Every one of the nightly lane's `LEAK_PROBES`, planted where `tests/replay.py` plants them.
- `nightly_ha`'s A10 rule over the whole download.

## Head

`705a9b851d314f860f3fa29e0e092231d5c878ad` is the code head. It merges origin/main `06c6f3cf2589cd37fa9fe56cc5ebeef709dc8d3b` into the previous head with no conflict and no resolution, and it already contains that main, so this round adds no commit: `git merge origin/main` here prints `Already up to date.`

The authored code head is `ff914f548f3eda308b02d3834913319c1155f766`, the round-1 head `acf14d8f2267718203d9dc1b313bc8c3e9f0bc8d` plus two commits:
- `22b9b6cf7afe8b2ffe4392c40dbfb217326aab60` merges `origin/main` at `07a09406a1cc97076a6f28581f87f313b322a6b6` with no conflict. The branch's own delta did not change: `git diff 106af95a acf14d8f | git patch-id --stable` and `git diff 07a09406 22b9b6cf | git patch-id --stable` both print `126ea63748c6e299b17e5059de57649cfa385d06`.
- `ff914f548` is the CodeQL fix above. It touches `tests/debug_collect.py` only.

What differs between the authored head and this one: `git diff --stat ff914f548 705a9b851 -- custom_components tests tools/replay` prints `tests/closures.json | 1 +` and nothing else, one line from main. `git diff --stat ff914f548 HEAD -- custom_components tests/debug_collect.py tests/hastub tools/replay tests/replay.py tests/harness.py tests/nightly_ha.py | wc -l` prints `0`. So every production file, the debugger's driver and its stub are byte-identical to the head the review measured.

Figures below were re-taken at this head on 2026-10-19 between 02:50Z and 03:05Z, with `origin/main` at `06c6f3cf2`.

## Mutation proof

A scratch runner applies each mutant to a `git archive` copy of the head, runs `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` there, and counts the FAIL lines. It leaves out the `a16:` lines, which are expected failures inside the cap probes. It also counts FAIL lines that carry one of the planted credential literals (`s3cret-value`, `bob123456`, `abc123456`, `secretvalue123`). The table was measured at the authored head `ff914f548`. This head's production and test files are byte-identical to it (Head), so the table describes this tree, and M0 and M5 were re-run here: M0 prints `ALL 122 DEBUG COLLECT CHECKS PASSED`, and M5 (`replay_doc.py` line 511, `return clean` to `return raw`, restored with `git checkout`) prints `24 of 122 DEBUG COLLECT CHECKS FAILED`, rc=1. Every mutant of the table exits 1:

| Mutant | Production edit | Checks that go red at the head |
|---|---|---|
| M1 | `async_bundle`: `if entry is not None:` becomes `if False:` | "Download diagnostics fills the bundle's replay half...", then a `TypeError` on the missing half stops the run |
| M2 | `_public`: the private-id test removed, so it returns the node | 25 of 122 |
| M3 | `fit_replay`: the cap test becomes `if True:` | 2 |
| M4 | `cycle_row`: the `"version"` line deleted | 1: "a cycle row carries the release that wrote it..." |
| M5 | `replay_doc.seal`: `return clean` becomes `return raw` | 24 |
| M6 | `store.DOMAINS`: the `rows/#/version` line deleted | 2 |
| M7 | `_since`: returns every state, no window trim | 1 |
| M8 | `replay_document`: the Tibber choice skipped (`if False:`) | 2 |
| MA | `clean_value`: values under a credential key collected as non-secret (`False`) | 2: the two `clean_value` leak checks |
| MB | `_collect_strings`: a null or a bool no longer skipped | 1: "everything under a credential-named key is recorded..." |
| MC | `clean_value`: a credential-named key no longer dropped | 2: the two `clean_value` leak checks |
| MD | `seal`: the leak refusal off (`if False:`) | 1: "replay_doc.seal refuses a document where a dropped credential survives..." |

M1 to M8 give the same counts as round 1. MA to MD pin the three checks whose detail changed.

The new checks were proved by the repository's own mutation instrument in round 1 (`tests/mutation_table.py --pin-killed`, 44 pins). This round adds no production line, and CI's `mutation` job re-runs the table at this head.

## Null control

- **The detail no longer echoes a planted credential, and nothing else moved.** The same MA to MD were run on `22b9b6cf`, the merge before the fix. There the failure counts are the same (2, 1, 2, 1), and FAIL lines carry a planted credential under every one (1, 1, 2, 1). At the head they carry none (0, 0, 0, 0). M0 passes 122 of 122 at both.
- **CodeQL, run locally at both ends.** CodeQL CLI 2.27.2 (the `codeql-bundle-v2.27.2` release), query `codeql/python-queries` `Security/CWE-312/CleartextLogging.ql`, `database create --language=python` then `database analyze --format=csv`, over a source root holding `custom_components`, `tests/hastub` and the four test modules on the alert's path (`harness.py`, `debug_collect.py`, `nightly_ha.py`, `replay.py`). With `tests/debug_collect.py` from `22b9b6cf` (before the fix): 1 alert, `py/clear-text-logging-sensitive-data` at `tests/harness.py` line 50, its source `tests/debug_collect.py:1138`, `_secret_drop: list = []`. That confirms the source round 1 could only infer. With the head's file: 0 alerts. A first run over all of `tests` did not finish analysis inside 30 minutes and was stopped; it is not a figure.
- **The leak-probe checks can still fail.** With `seal` perturbed to return the raw document (M5), 24 checks fail, all 21 leak-probe checks among them.

## Figures

All figures are at the head (`705a9b851`) unless a merge-base value is given. A value labelled `07a09406` is read from a `git archive` copy of that older main, which is what the pre-fix measurements used.

- `PYTHONPATH=tests/hastub python3 tests/debug_collect.py`: `ALL 122 DEBUG COLLECT CHECKS PASSED` and `RESULT leak_probes_through_download=21 written=21 refused=0 unit=count`. The RESULT line counts every key of `tests/replay.py`'s `LEAK_PROBES` driven through the download, and how many replay halves were written.
- With `T=$(mktemp)`, `PYTHONPATH=tests/hastub python3 tools/replay/synthesize.py --out "$T" && cmp "$T" tests/replay/synthetic-dhw-only.json && echo IDENTICAL` prints `IDENTICAL`.
- `python3 tools/replay/export.py --check tests/replay/synthetic-dhw-only.json`: `0 violation(s)`.
- `python3 -c "import sys; sys.path.insert(0, 'tools/replay'); import export; print(len(export.entry_keys(*export.default_const_paths())))"`: 214 at the merge base, 216 at the head. The rule: the number of distinct `CONF_*` string values the export admits as entry keys.
- `PYTHONPATH=tests/hastub python3 -c "import sys; sys.path.insert(0, 'tests'); import replay; r = replay.sanitiser_checks(sorted(replay.FIXTURES.glob('*.json'))); print(len(r), sum(not x[1] for x in r))"`: `56 0` at both the merge base and the head.
- `git ls-files custom_components/heatpump_optimizer | wc -l`: 98 files at the head, 97 at the merge base. The rule: the package's tracked files, Python and non-Python alike.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py`: `RESULT arch_modules_on_disk=80`, `arch_map_listed=80`, `arch_map_missing=0`, `ha_module_level_importers=28`, `claims_true=123`, `claims_false=0`.
- The class census (step 8). The rule: every name inside the detail argument (the third positional, or `detail=`) of a `.check(` call in `tests/*.py` that matches CodeQL's sensitive-name heuristics (password, secret, trusted, account or user id or name, certificate), enumerated by an AST walk. It returns one seam at both ends: `tests/debug_collect.py`'s `_secret_drop`. At the merge before the fix it is `str(_secret_drop)`, the alert's source. At the head it is the second argument of `_unrecorded`, which returns positions of the expected list and a count, never an element of `_secret_drop`: closed in this diff. The census matches names, so it cannot see a credential-valued variable with a neutral name. The MA to MD runs above are the value-level check: they count planted credentials in FAIL lines directly, and they found the two neutral-named seams this diff also closes (`_dropped`'s detail and `seal`'s `_leaked`).
- Re-run green locally at the head (`PYTHONPATH=tests/hastub`, `GOLDEN_MODE=drift`, `GOLDEN_REF` the merge base), each with its last line: `python3 tests/structure.py` (`STRUCTURE RATCHET PASSED`), `python3 tests/harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`), `python3 tests/layout.py` (`layout self-test: ok`), `python3 tests/env_drift.py --claims-only 06c6f3cf2589cd37fa9fe56cc5ebeef709dc8d3b` (`claims hygiene: 06c6f3cf2589cd37fa9fe56cc5ebeef709dc8d3b ok`), `python3 tests/closure.py selftest` (`ALL 115 closure shrink pins PASSED`), `python3 tests/ha_contract.py` (`ALL 96 contracts PASSED`, then `ALL 4 convention checks PASSED`), `python3 tests/doc_claims.py` (`ALL 169 checks PASSED`), `python3 tests/deployment_shape.py` (`ALL DEPLOYMENT SHAPE CHECKS PASSED`), `python3 tests/guard_pins.py` (`ALL 50 GUARD PIN CHECKS PASSED`), `python3 tests/typing_ruler.py` (`ALL 12 typing-ruler source checks PASSED`), `python3 tests/golden.py` (`NO STALE FIXTURE: 56 committed fixture(s) still match`), `env -u BASH_ENV python3 tests/entities.py` (`ALL 2349 ENTITY CHECKS PASSED`) and `python3 -I tools/audit/seat/tmp_paths.py --check` (`0 refused`). **Left to CI** of the 31 the scope names: `features`, `stress`, `env_drift`, `optimality`, `boost_drift_replay`, `backtest`, `edge`, `validate`, `arch_score_head`, `finite_boundary`, `block_duty`, `config_flow_steps`, `manual_plan`, `plan_view`, `solar_alignment`, `wood_advisor`, `frontend`, `open_meteo`, `md_tables.mjs`, `card.mjs` and `card_drift.mjs`: this round changes none of their inputs (its own scope is `debug_collect` alone).
- `python3 tools/audit/archscore/score.py --diff 06c6f3cf2589cd37fa9fe56cc5ebeef709dc8d3b`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 31 script(s) run, 2 scoped out.` Over this round's commit alone (`--diff 22b9b6cf`): `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, the one being `tests/debug_collect.py`.

## Architecture score

n/a: no gate metric rises (`dS +0.0000 NULL` above).

There is no raise, and no payment was owed this round. The round-1 split of `violations` into `_entry_violations` and `_state_violations` still keeps `functions_cc_over_15` flat.

The fix took the shape `seal` already has. The alternatives, and why each lost: renaming `_secret_drop` dodges the name heuristic and leaves the values in the log; dismissing the alert as used-in-tests leaves the same flow for the next check that copies the pattern; a constant detail cuts the flow but loses which value went missing. `_unrecorded` keeps that, by position.

## Red checks

`pr-contract` was the only check red at the PR head `705a9b851d314f860f3fa29e0e092231d5c878ad` (check run 117852619806, read from the check-runs API). Its log reads: `[pr-body] check `wave-script` is red and `## Red checks` does not name it`. That is the red-history record over the 25 commits between origin/main and this head, which lists the failure conclusions `CodeQL, coverage-ratchet, delivery-status, mutation, validate-hacs, wave-script`. At the head itself, `wave-script` (check run 117852504529) and `delivery-status` (117852504479) are `success`. The cause of the `pr-contract` red is this body, which did not name `wave-script`; the main merge had already cleared the check. Each red of the history is answered here.

- **`wave-script`**, red on earlier heads of this branch. Inherited from main, not this diff. The agreement lane's `merge-subject-pr` read `divergent=2` on main's merges `Merge pull request #2401 (R10-ARCHSCORE-COVERAGE p5)` and `Merge pull request #2379 (R10-SENSOR-PAYLOAD)`: `stamp.py` and `delivery_status.py` read the PR number, and `policy_lint.mjs`'s `resolvePrFromCommit` read null. Cause: main's merge-subject shape outran one reader. Cleared by main's #2423 (one merge-subject grammar across readers) and #2424 (the guard), both in this head. The detector is the agreement lane, which went red on main's first push carrying the shape; no cheaper one exists. This diff touches none of those readers (`git diff --name-only origin/main...HEAD | grep -E 'tools/(policy|audit)|stamp|delivery_status'` prints nothing). At this head `wave-script` is green in CI (check run 117852504529).
- **`delivery-status`** (not a required context), red on earlier heads. Cause: main's row backlog (`DELIVERY STATUS OVERDUE`, three rows 14 to 17 commits behind) while main was red. This diff adds no delivery file. Cleared by main's later record merges; `delivery-status` is green at this head (check run 117852504479). No detector is missing: the check is the detector, and its cost is its own run.
- **`CodeQL`** (at `acf14d8f`, check run 117752117325, and at `f657fbce`, check run 117731875384): `1 new alert including 1 high severity security vulnerability`, `py/clear-text-logging-sensitive-data` at `tests/harness.py` line 50, the FAIL print. Its source was `_secret_drop`, reaching the sink through `str(_secret_drop)` in the detail of the check that values under credential keys are recorded (CodeQL locally, Null control). Fixed in `ff914f548`: no check detail in this diff prints a recorded credential, and CodeQL run locally finds 0 alerts at that head against 1 before it. Not dismissed and not suppressed. The cheaper detector is the CodeQL CLI's Python `CleartextLogging.ql` run before the push, as in the Null control. Its standing cost is the bundle install plus a database build over `custom_components` and `tests`: 32 seconds per side on the path-limited source root, after a one-time download of the bundle (about 500 MB). No seat runs it by default, and this seat builds no check for it.
- **`coverage-ratchet`** (at `33dfae1e`, job 117699624632): `FAIL every module >= 95.0 %  (1 below)`, `replay_doc.py: 88.41 %`, `COVERAGE RATCHET BREACHED`. A real gap. The module's edges were driven only by the nightly lane, which is not in the coverage tree. Answered by `1a1a6a9c` and `55d80cbe`: 100 % under `tests/debug_collect.py` alone (Null control). Green at `f657fbce`. The cheaper detector was a local `coverage` run of the debugger's own driver before the push. No standing check exists for it, and this seat builds none: CI's per-module floor is that check, and it fired on the first push that carried the module.
- **`mutation`** (at `33dfae1e`, job 117696161229): `MUTATION TABLE REFUSED -- 4353 unpinned site(s) against 4308 at the ratchet base 3fb386d5..., 45 of them added by this diff`. The bot's first `--pin-killed` pass (`33dfae1e`) pinned what the old checks killed. The 45 left were sites no check could see. Answered by the checks above, the deleted duplicate guard, and the 44 new pins. The second `--pin-killed` run leaves 0 unpinned, and `mutation` is green at `f657fbce`. The cheaper detector is the same command run locally before the push, which `ci-autofix.md` names for a red autofix.
- **`validate-hacs`** (at `33dfae1e`, job 117696134753): `aiogithubapi.exceptions.GitHubRatelimitException: API rate limit exceeded for installation`, raised in HACS's own `preflight` before it validated anything. The cause is a GitHub API rate limit on the runner's shared installation quota, not this branch. Green at `f657fbce`. No cheaper detector exists for a third party's rate limit.

## Forward-carry

The `version` stamp invalidates an assumption D15's method step 1 rests on: "`integration_version` is the download's, not each row's". It also retires the input line "While the download's `replay` is null (until R10-DIAG-REPLAY)". Both belong to `dev/governance/dimensions/D15.md`.

Landed in the `R10-BRIEFS-FOLD` group's `carry` list in `dev/programme/rosters/wave-r10-groups.json`, on `handoff/audit-r10-roster` at `2020978559ef37e9e22ae0926a5f685622da65f5`, written by `python3 tools/audit/seat/roster_edit.py append-carry R10-BRIEFS-FOLD @<file> --branch handoff/audit-r10-roster`. Read back from origin: the group's last `carry` entry equals the text below byte for byte. `node tools/policy/brief_lint.mjs` on that roster, from an `origin/main` checkout at `07a09406`, exits 0 with `TOTAL: 0 error(s) across 1 file(s)`; the tool's own lint gate printed the same. The carried text:

> From R10-DIAG-REPLAY (#2399, handoff/r10-diag-replay): dev/governance/dimensions/D15.md must change in two places, and that file is not yet in this group's files. (1) D15 M1: a row carrying `version` is that release's; the restart-gap rule ("`integration_version` is the download's, not each row's") applies only to rows without one. Control: `tests/debug_collect.py`'s "a cycle row carries the release that wrote it" goes red with the stamp removed from `debugger.cycle_row`. (2) D15 inputs: retire "While the download's `replay` is null (until R10-DIAG-REPLAY)". The download's `debug.replay` is filled when the recorder is set up and the window fits the inline cap; otherwise `debug.manifest.replay` names why, and the export from the same box and window stands in. Re-measure at the D15 baseline.

## Unpinned sites

None. This round adds no production line. Round 1's `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/debug_collect.py` left 0 of this diff's sites unpinned, and CI's `mutation` passed at `acf14d8f`.

## Friction

- `fixer.md`: `cost`: a change to `const.py` or `store.py` scopes 32 of 33 scripts, so the scoped gate is close to a full run for any debug-bundle field.

