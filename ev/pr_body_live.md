Closes #2272.

## Re-cut

R10-REPLAY-REAL-DAY: the replay lane's first real recorded day, tvofi's 2026-10-30 away episode, cut from the owner's export, masked, sealed and replayed through the current coordinator as a nightly guard on the away path. This body replaces the earlier ones. The round-3 block (mutation-vacuous away guard) is answered below; nothing else in the code moved except what `## Head` names.

The block: `recorded_away = []` in `run_fixture` (and, equivalently, the owner fixture with `controls.away` emptied) left the away check green with 0 commanded cycles. The repair, in `tests/replay.py`:

- `away_offenders(observations, events, expect_commanded)`: for a fixture in the new `AWAY_COVERED` set (the owner fixture; coverage is declared there, a design choice) the replay must carry at least one commanded cycle. The docstring now claims only what the check delivers.
- `away_coverage_offenders(name, events)`: a covered fixture whose `controls.away` holds no active command is refused. It runs in `run_fixture` and, per committed fixture, in `sanitiser_checks` (`away_coverage:<fixture>`).
- Two new controls pair each refusal with its green case: `control:away:coverage_needs_a_command`, `control:away:coverage_needs_a_commanded_cycle`.

## Head

`67cc0e0a15100eef34848203fdb2bc5c370a830e` merges the authored code head `e46ff0a75f1264bb19cbefb444453fb9a91dbaf7` and then merges origin/main `407eb0cb3` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

Code head: e46ff0a75f1264bb19cbefb444453fb9a91dbaf7. It is the earlier handoff tip a8f48032e911703f58acea90dc15cbea5f609437 (PR head 18bdd5c88 plus the d9ca33852 merge and the away-guard repair) plus one commit, the alert-47 repair. `git merge-tree --write-tree origin/main HEAD` exited 0 at origin/main d052f80f7f81d42db5c57a55ebaef7056c7ce01a (`date -u` 2026-11-01), so nothing was merged; main had not moved since the last prepr-relevant read.

The round-3 figures were taken at 80c6fa40a; the delta to this head touches only `tools/replay/export.py`, `tests/replay.py` (one check, one import) and the harness (one row).

## Mutation proof

In-tree harness, `HASTUB_TZ=Europe/Stockholm OPENBLAS_NUM_THREADS=1 PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_replay_real_day_mutants.py --replay` at 80c6fa40a: `RESULT killed=35 mutants=35 null_red=0` (round 3's head). At this head the FAST tier alone (no `--replay`) reads `RESULT killed=33 mutants=33 null_red=0`, including the new row below; the REPLAY rows were not re-run, as the delta reaches nothing `run_fixture` reads. New rows (the first is this round's):

- `export.py` a SQLite `db_url` path carried into the recorder label (`label = SQLITE_URL_LABEL` -> `label = f"SQLite {db}"`): KILLED, red `recorder:sqlite_db_url_named_by_kind_not_path`.
- Fixture-side twin, the owner fixture with `controls.away` emptied: KILLED, red `away_coverage:owner-2026-10-30-away.json`.
- `away_coverage_offenders` not asking a command-less fixture: KILLED, red `control:away:coverage_needs_a_command`.
- `expect_commanded` check off: KILLED, red `control:away:coverage_needs_a_commanded_cycle`.
- REPLAY tier, `recorded_away = []` (round 3's survivor): KILLED, `away` 2 offenders (no active command, no commanded cycle), `cycle_cost` 1.
- REPLAY tier, `commanded = None` (round 2's): KILLED, `away` 13 (12 cycles and the coverage line).
- REPLAY tier, `no_default` exemption not handed the config: KILLED, `no_default` 14.

## Null control

- Unmutated head: FAST red `[]`; REPLAY null replay counts all 0 (`finite`, `unit`, `no_default`, `agreement`, `cycle`, `not_frozen`, `away`, `cycle_cost`).
- Finder's harness at both ends (`tests/replay.py --one tests/replay/owner-2026-10-30-away.json`, same env, `--step-minutes 60`): at the previous head 18bdd5c88 with `recorded_away = []` applied, `away` is `[]` (survives, 4 cycles); at this head the same mutant reads `away` 2 (REPLAY row above).
- Each new refusal is paired with its green case in `controls()` (`pair(...)` requires bad non-empty and good empty).

## Figures

- Alert-47 check at this head: `recorder_checks()` returns `recorder:sqlite_db_url_named_by_kind_not_path` green; the printed line is `reading the recorder SQLite database` for `--db-url sqlite:///url-named-recorder.db`, where the null (the mutant) prints the file name.
- Other: none new beyond the ones above; commands: the harness line in `## Mutation proof`; `python3 tests/structure.py` printed STRUCTURE RATCHET PASSED; `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` printed "no closures, fast, governance or instrument red predicted". The `COST_BUDGETS` recorded values are unchanged and the cost-budget restatement is below.

## Red checks

Every concluded red check on any commit of this branch, each verified against its job log (job logs downloaded and grepped, 2026-11-01).

- `CodeQL`: code-scanning alert 47 (py/clear-text-logging-sensitive-data, `tools/replay/export.py`, the `reading the recorder {rec.label}` stderr line) and alert 48 (`tests/replay.py` `_mariadb_install`).
  - Alert 47, real in part, repaired in code. The label was built from the `db_url`, which may come from `secrets.yaml`. 2042aefb7 already made the MySQL/MariaDB label a constant (`MYSQL_LABEL`). The remaining tainted route was a SQLite recorder named by a `db_url`: its label was `SQLite {db}` with `db` taken from the URL. This head names it `SQLITE_URL_LABEL` ("SQLite database") and prints a path only where the person typed it (`--db`, or the default under the config directory). Location only, never a value, as the owner ruled. Check `recorder:sqlite_db_url_named_by_kind_not_path` (green here); its mutant is killed (`## Mutation proof`). CodeQL could not be rerun from this seat; if it still reports 47, the dismissal is owed to the owner, tvofi.
  - Alert 48 is a false positive: `_mariadb_install` writes an invented credential at an invented host into a `TemporaryDirectory`, the input the never-printed checks need. Renaming it would evade the scanner. Dismissal owed to the owner, tvofi.
  - Cheaper detector: CodeQL is the cheapest detector of its own alerts; it has no local run in the seat toolchain.
- `tests / fast (3.14)`, red at df35202ab (run 41269647846, job step "Run the suite"). The log shows `FAIL debug replay: trim_replay carries sparse export attributes forward  [nordpool_rows_with_raw_today=0]` and `FAILED: python3 tests/entities.py`. Cause: `tools/replay/debug_replay.py` named the synthetic fixture's price entity by its raw id, which the masking renames to `sensor.price`; fixed by d6a8661e8, which reads the id the fixture's entry holds. Green at the PR head 18bdd5c88 (run 41312230596). Cheaper detector: the scoped gate, which runs `tests/entities.py`.
- `tests / mutation`, red at df35202ab, 4cccd845f and 4c994241d (jobs 124739667817, 124745368506, 124756673066; step "Drive the table over what this diff tested"). The logs list `ADDED UNPINNED` sites in `replay_doc.py` (7 at 4c994241d: 535, 577 twice, 579, 580, 589, 672) and `MUTATION TABLE REFUSED -- 3579 unpinned site(s) against 3572`. Cause: new guards no check drove. Repaired by `mask_seam_checks` and the pins (see `## Unpinned sites`); green at 18bdd5c88 (run 41312230596). Cheaper detector: `prepr.sh` step 6d, in seconds.
- `tests / replay`, cancelled (not failed) at 4cccd845f and 4c994241d by `timeout-minutes: 30`: the fixture's four ~12-CPU-minute replays. Fixed by `COST_ARMS_SKIPPED`; success at 18bdd5c88.
- `pr-contract / pr-contract` and `gate`, failure at 4cccd845f: the body left the reds above unanswered. This body names them.
- No other concluded red check stands on any commit of this branch. This head has not run CI.

## Carries

The group's eight roster carries (`dev/programme/rosters/wave-r10-groups.json` at origin/handoff/audit-r10-roster), by index. Dispositions are unchanged from the earlier rounds' accepted record; this pass re-took none of them.

- Carry 1 (the real day), Carry 2 (classify the fixture), Carry 3 (#2810), Carry 4 (the R10-DIAG-REDACT precondition on the exported document), Carry 5 (the day choice) and Carry 7 (the owner's export result): done.
- Carry 6 (STRANDED CARRY 57, cost-budget spread): half done, the budget is recorded; the open half, re-centring on the second CI class, is the orchestrator's restatement of R10-REPLAY-COST-BUDGET (see `## Forward-carry`).
- Carry 8 (D15-s1-04, a boolean under a credential-named key): done.

## Forward-carry

- Owed to the orchestrator: restate R10-REPLAY-COST-BUDGET's carry in `dev/programme/rosters/wave-r10-groups.json` as "re-centre the recorded 355.7 / 3740.0 / 0.249 on the second CI class's reading", with its control. Carry: R10-REPLAY-COST-BUDGET
- Carries 4, 6, 8 and 9 (live-bundle reads) are held verbatim by R10-LIVE-BUNDLE-READS in the roster. Carry: R10-LIVE-BUNDLE-READS
- The mold-guard finding is a carry of R10-USER-DOCS-VERIFY in the roster, unchanged. Carry: R10-USER-DOCS-VERIFY
- The widened `not_frozen` rule's blind spot (a published value tracking an input idling at zero that meets one non-zero value and then freezes is not judged; `control:not_frozen` still fires on the two-value case) is a disclosed design trade recorded in `tests/replay.py`'s comment, not a defect. Carry: dismissed: disclosed design trade with its control
- The warm-up claim, export-side masking figures and pump-draw comparison need the owner's untracked export and stay unverified. Carry: dismissed: no seat holds the export

## Friction

none

