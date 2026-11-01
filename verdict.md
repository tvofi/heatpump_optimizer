Fix review: blocked 4cccd845f408692faa3353f1dbe3d4636a58d6fb root-cause-unrecorded: CodeQL and tests / replay are red at the head and ## Red checks names neither; the new fixture also fails the replay lane's no_default invariant (14 offenders), which the body never discloses

bus-nonce: 9c03b1c000af12c013697f90e8887c28

## Round

Round 1 (the brief's ROUND NOTE: live head 4cccd845f, code head d6a8661e8). Contract: dev/governance/roles/fix-review.md at origin/main. The role directory has no drift between the merge base and origin/main. Measured from detached worktrees at 4cccd845f (head), df35202ab (the previous head) and 8327c6e6e (the tree before both away hotfixes, with the head's tests/ and tools/replay/ laid over it).

## Block

1. **Red checks with no answer (fix-review.md step 11).** The head's whole check-run set (paginated, ev/check_runs.txt) has these concluded non-green runs: `tests / mutation` failure, `CodeQL` failure, `tests / replay` cancelled, and `pr-contract / pr-contract` and `gate` both failure. `pr-contract` run 124757339232 started at 05:07:51Z, after the last red concluded (`tests / replay` at 04:41Z), and it refuses the body with 3 errors. All three are the same gap: `CodeQL`, `code-scanning alert 47 (py/clear-text-logging-sensitive-data)` and `code-scanning alert 48 (py/clear-text-storage-sensitive-data)` are red and `## Red checks` does not name them. The alerts sit at tools/replay/export.py:454 (stderr print of the recorder label) and tests/replay.py:966 (a test writing the invented test URL to a temporary secrets.yaml). Both look like false positives on reading: the label is `redacted()` and the credentials are invented. But the body owes that answer. CodeQL is itself the cheapest detector of its own alerts, so the class is root-cause-unrecorded. `gate` fails on the same refusal ("unreadable title" in run 41273345201).
2. **`tests / replay` cancelled, and the lane is red on the new fixture beyond what the body says.** The job hit its `timeout-minutes: 30` (.github/workflows/tests.yml:1319) during the fixture's memory-doubled arm. Before it was cancelled, its log showed `FAIL owner-2026-10-30-away.json: no_default [14 offender(s): sensor.heat_pump_optimizer_valve_target_recommendation=21.0 ...]` and `FAIL ...: cycle_cost` (no recorded budget). It also showed `FAIL ...: cycle_cost sees a doubled cycle cpu`, because no budget exists for the doubled cycle to exceed. I reproduced the same 14 `no_default` offenders locally at the head and at 8327c6e6e (ev/one_wt.summary, ev/one_wt_pre.summary). The body names only `cycle_cost: no recorded budget`. It never mentions the `no_default` red or the job timeout. As committed, the "nightly regression guard" is a lane that is red every night on an invariant unrelated to away, and it cannot finish inside its job budget. That hides any real regression it was added to catch. A `no_default` offender is either a product finding (a ThermalState default published as available on the owner's install) or an invariant false positive on a real day. Either way the body must disposition it.
3. **Carry missing (fix-review.md step 10; brief duties D and E).** The body says carries 4, 6, 8 and 9 (the live-bundle reads) are "re-homed by the orchestrator". On origin/handoff/audit-r10-roster at 5cfbe719ec113fb7221f9542aa6ad138c9378986, no group outside R10-REPLAY-REAL-DAY carries them. I searched every other group's carries for unhealthy_input / 180 min / L6 / L9 / --bundle / scale drift and found hits only in done groups (R10-HEAT-METER, R10-SCORES, R10-PARAMS-OWNER, the sources) and one unrelated L6 lever. The COST_BUDGETS record for owner-2026-10-30-away.json is likewise carried only inside this group, and the body cites no roster SHA for it. On merge this group goes done and all five items are stranded in a done group.

## Findings

- The fixture's `no_default` invariant fails with 14 offenders (sensor.heat_pump_optimizer_valve_target_recommendation=21.0) at the head and at 8327c6e6e, in CI and locally. Undisclosed (Block 2). Carry: R10-REPLAY-REAL-DAY
- `tests / replay` is cancelled at its 30-minute job limit. Adding a fixture costing about 15 minutes per run, replayed four times, does not fit the lane's budget. The body's own "the nightly lane replays each fixture four times" is the cause, and nothing in the diff raises the limit or trims the arms. Carry: R10-REPLAY-REAL-DAY
- CodeQL alerts 47 (tools/replay/export.py:454) and 48 (tests/replay.py:966) are unanswered in ## Red checks (Block 1). Carry: R10-REPLAY-REAL-DAY
- Carries 4, 6, 8, 9 and the COST_BUDGETS record have no destination on the roster ref (Block 3). The orchestrator owes a live, not-done destination group before merge. Carry: R10-REPLAY-REAL-DAY
- Surviving mutant in the away check: in run_fixture (tests/replay.py, `commanded = returns if active else None`), replacing the assignment with `commanded = None` leaves the fixture's `away` check green. The run shows 0 commanded cycles and 0 offenders (ev/mut_commanded_none.summary). The synthetic controls cannot see it, because they never run the fixture. Nothing asserts that the recorded day yields at least one commanded cycle, so a broken controls replay or a renamed `controls.away` key turns the guard vacuous. The cheap pin is a check that the owner fixture's run has 12 commanded cycles (or more than 0). Carry: R10-REPLAY-REAL-DAY
- The mutation proof for every `tools/` site (export.py, cut_day.py) and phase 2 rest on out-of-tree harnesses (`mutants.py` sha1 29e550f8..., `mut2.py` sha1 c0b26da6...). fixer.md step 18 says a harness that a body figure needs reproduced lands in the same pull request. As things stand, no reviewer can re-run those figures. Carry: R10-REPLAY-REAL-DAY
- The warm-up claim (96 cycles from local midnight against the cold span: away views agree, plan energy 11.37 against 7.0 kWh, and 8.49-18.45 against 7.0-13.09 kWh) and the export-side masking figures (0 of 108 raw ids, 48 near-coordinate numbers in $EXPORT, 416/416 and 2496/2496 reads) need the owner's untracked export. I could not re-derive them, and the warm-up claim has no null control. Carry: dismissed: needs the owner's export, which no seat may hold; disclosed as not verified under Evidence
- The live head moved during the review to 4c994241d (`ci: pin killed mutants`, github-actions[bot], 34 ledger pins, no code). The body lists 41 unpinned sites and the bot pinned 34, so up to 7 sites may be survivors or unevaluated. Read the mutation-autofix log at 4c994241d before the next round. Carry: R10-REPLAY-REAL-DAY

## Evidence

- Privacy (duty A), reported by location only:
  - Every added line of the three-dot diff was grepped for the ADDRESS rule, street-word suffixes, standalone 5-digit postal shapes, UUID-shaped Tibber home ids, DB URLs, IP or host shapes, credential key=value pairs and long tokens (ev/privacy_grep.txt, file:line only).
  - Every ADDRESS or street-word hit is either the invented probe street (tests/debug_collect.py:1029-1044, tests/replay.py:680-682 and 1105-1190, the replay_doc.py:96 comment) or a generic phrase (`days 7`, `schema 41`, `owner-2026` and similar).
  - The DB URL hits are the invented test URL (tests/replay.py:873-874) with the Home Assistant MariaDB add-on's default host and database name, plus export.py:293. No UUID, IP or host shape appears in any added line.
  - The fixture: 26 distinct entity ids, 25 `<domain>.<role>` all derived from entry keys and 1 `<domain>.e_<10 hex>`, none outside the grammar (ev/privacy_ids.txt). Its free-text entry values are MQTT topic paths and enum words. `entry.options.solar_location` is held at 2 decimals.
  - The PR body's quoted ids (`states[sensor.wood_tank_bottom]` and others) are role ids from entry keys.
  - A failed connect reports `type(err).__name__` only (export.py:325-327). `redacted()` keeps scheme, host, port and path, prints them to stderr only, and writes them to no document.
  - The HMAC key is the entry id on both writers: replay_doc.py:642 for the export, and debugger.py:412-415 for diagnostics, where the entry carries `entry_id`. It falls back to "" only when an entry has no id.
  - RESULT privacy: no address, raw id or credential found in the fixture or any added file.
- Duty F (debug_replay price-id fix), with the reviewer's own driver at ev/dbg_null.py, output in ev/dbg_replay_results.txt:
  - RESULT df35202ab gate_checks 4/5: `trim_replay carries sparse export attributes forward [nordpool_rows_with_raw_today=0]` fails.
  - RESULT head 5/5.
  - Null, a fixture whose price entity keeps a raw-shaped id: 5/5.
  - Price entity None: 4/5, the check goes red. Price entity key absent: KeyError, a loud failure.
  - The fix reads `replay["entry"]["data"]["price_entity"]` from the committed fixture and adds no literal id.
  - `tests / fast (3.14)` is success at the head.
- Duty B (away invariant):
  - The head replay over the 16 cycles gives 0 `away` offenders, with 12 commanded cycles all `active=True override=True recovery=False floor=15.0 target=15.0`. Planned space heating is 6.03-13.54 kWh here, against 5.51-13.19 in the body; plan energy differs across environments and the invariant does not read it.
  - The fixture's three control pairs, under my own mutants of `away_offenders` (ev/away_mutants.txt): null green; drop the override arm KILLED (control:away:override); drop the floor arm KILLED (floor); treat recovering as not recovering KILLED (all three); drop the view arm KILLED (view); recovery always true KILLED (floor).
  - The run_fixture mutant `commanded = None` SURVIVED (see Findings).
- Duty C (disclosure):
  - RESULT 8327c6e6e: 0 `away` offenders, 12 commanded cycles, the same view tuple.
  - RESULT away views identical, head against pre-hotfix: True over 16 cycles (ev/views_compare.txt).
  - So "pre-fix passes too" is confirmed. Neither the body, tests/replay.py nor the docs claim the gate catches either hotfix's defect. The docstring cites AWAY-LIVE's stated behaviour only.
- Duty D (cost):
  - `cost_offenders` returns `no recorded budget` as offenders, so `R.check(cycle_cost)` fails. "No budget" is never treated as a pass (confirmed in CI's log).
  - Local cpu_ratio was 278.7 at head, 217.8 at pre-hotfix and 248.7 in the mutant run (three concurrent runs on 4 cores), so the body's "no 2x band holds locally" stands; CI recorded `cpu_ratio=352.1 peak_kib=3832 loop_cpu_ratio=0.2629`.
  - The record carry has no destination (Block 3).
- Re-derived figures:
  - The sanitiser, mask, recorder, leak-copy and cut_day checks give 103/103 at head (ev/sanitiser.txt).
  - `export.py --check` on the fixture: 0 violations.
  - Fixture 39 610 B, 16 cycles, 26 inputs, 0 published, away on 15:42:54Z (return 2026-10-31T19:00Z), reload 15:44Z, away off 18:39:25Z.
  - No weekend or holiday comfort fields, `away_presence_entity` None (ev/fixture_figures.txt).
- Gate:
  - `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
  - VERSION, manifest.json and RELEASE_NOTES.md are untouched. Both claim files are byte-identical to origin/main.
  - The delivery row dev/programme/delivery/3078.md is in the three-dot diff.
  - `git merge-tree --write-tree origin/main 4cccd845f`: exit 0, no conflict.
  - The macOS py-spy note is the fixer's environment and was not exercised here (Linux).
  - `tests / mutation` red is named in the body as red by construction. The autofix pin commit followed, and its 34 pins against 41 sites are a Finding.
- CI: `merge_train.py classify 4cccd845f` exited 1, `RED ... red: gate`. In the full check-run set, `CodeQL` failure, `tests / replay` cancelled, `pr-contract` failure (3 errors), `gate` failure and `tests / mutation` failure are the non-green runs. Everything else is success, skipped or neutral (ev/check_runs.txt).
- Head (step 12): I measured 4cccd845f. The live head is 4c994241d, the mutation-autofix ledger commit (review_carry: FRESH-REVIEW, because it counts the bot commit as a code commit; it touches only tests/mutation_ledger/). Every number above concerns files that commit does not touch, so all of them survive.
