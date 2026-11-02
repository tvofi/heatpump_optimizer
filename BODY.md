Closes #2272.

## Re-cut

Round 8, one finding (verdict/3078, "Fix review: blocked ee29ed568e2701badacfb4febff27a7834ff1d04 requirement-unmet"): the alert 47 repair made the open line constant (`reading the recorder`), so a successful run no longer told the operator which recorder was read. Nothing else changed: no refactor, no feature, no figure retaken beyond this line (none moved).

The repair: `open_recorder` in `tools/replay/export.py` prints the open line itself, a per-branch constant kind string: `reading the recorder: MySQL/MariaDB database` for a MySQL/MariaDB URL, `reading the recorder: SQLite database` for a SQLite URL and for the default file, and `reading the recorder: SQLite database <path>` on the `--db` branch only, where `<path>` is the operator's own `--db` argument (the parameter, read before any URL branch can reassign it). No URL or recorder-derived value reaches the line. The `reading the recorder` print in `build_export` is removed.

Carried, not fixed here: the two round-4 survivors (AWAY_COVERED, the unsupported-scheme refusal) are routed by the orchestrator to R10-REPLAY-COST-BUDGET as roster carries, and so is the `cpu_ratio` re-centring forward-carry.

## Head

Code head: `5163c7e6afea6e2c9bcc7f662bcdc5c63f37582d`, the handoff ref `handoff/r10-replay-real-day` (one commit on the PR head `ee29ed568e2701badacfb4febff27a7834ff1d04`, which contains the previous handoff tip `0cdcc3daa7ed2130a65f1914e712c703ddf28dae`). `git merge-tree --write-tree origin/main HEAD` exited 0 (clean), so origin/main was not merged; main is at `0166aefd7047b98e275bc0ab4e604fac3a7c75c6` at `date -u` 2026-11-02, and the PR's merge base is `25c46e76e2d7fe504a457a145cadbce33c773662`.

## Mutation proof

`PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_replay_real_day_mutants.py` (FAST tier) at this head: `null: red []` and `RESULT killed=37 mutants=37 null_red=0`. REPLAY-tier rows were not re-run: the delta reaches nothing `run_fixture` reads.

- The r7 verdict's mutant, the open line made fully constant again (`print("reading the recorder", ...)` in the MySQL branch): KILLED, red `recorder:open_line_names_kind_and_db_path` and `recorder:db_url_credentials_never_printed`.
- The existing alert 47 row (a recorder value interpolated into the SQLite URL branch's open line, re-pointed to the new line): KILLED, red `recorder:sqlite_db_url_named_by_kind_not_path`, `recorder:sqlite_db_url_refusal_names_kind_not_path`.
- `--db` path dropped from the open line: KILLED, red `recorder:open_line_names_kind_and_db_path`.
- URL host interpolated into the URL branch's open line: KILLED, red `recorder:open_line_url_branch_carries_no_url_value`.
- All mutants are applied to a copy and the harness removes the copy; the working tree is the unmutated one.

## Null control

- Unmutated head: harness `null: red []`.
- The planted values are non-empty and distinguishable: the URL fixture's user `hpo_reader`, password `Invented-Pa55word-91` and host `core-mariadb`, and the `--db` file `label-canary-recorder.db`. `recorder:open_line_url_branch_carries_no_url_value` also asserts the user and password are longer than 3 characters, so an emptied fixture fails it. With the host mutant applied the same check reads red.
- `recorder:open_line_names_kind_and_db_path` compares the open line to the exact expected string on each branch, so the old constant line fails it.

## Unpinned sites

None added under `custom_components/` this round. The one changed production file is `tools/replay/export.py`, which the mutation-autofix lane does not mutate; its new lines are pinned by the in-tree harness rows above.

## Figures

- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Scoped gate, `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED`; every named script rc=0 with `GOLDEN_MODE=drift` except `tests/replay.py` and `tests/golden.py`.
- `tests/replay.py`: one red, `synthetic-dhw-only.json: cycle_cost [loop_cpu_ratio 0.1506 over its budget 0.143]`. Control: the unchanged PR head `ee29ed568` in a separate worktree on the same box reads two reds of the same kind (`owner-2026-10-30-away.json` 0.2588 over 0.249 and `synthetic-dhw-only.json` 0.1628 over 0.143), so it is this container's CPU class against the recorded budget, not this delta. It is R10-REPLAY-COST-BUDGET's re-centring carry.
- `tests/golden.py`: 5 unclaimed drifts (`coord_*`, `system_identification` leaves present on one side only) measured against `origin/main` 0166aefd7, which has newer commits (R10-CEILING-PROBE) than this branch's merge base; the branch's custom_components diff against its merge base is `replay_doc.py` only, so these are main's own newer commits seen two-dot, not this branch's. Not merged, per the no-merge-unless-conflict ruling.
- Alert 47 detector: the repository ships no local CodeQL run for py/clear-text-logging-sensitive-data (`tools/pr/local_alerts.py` only reads the PR's uploaded alerts); the detector I ran is the dataflow check `recorder:open_line_url_branch_carries_no_url_value` plus the exact-line check, null green and each mutant red. The PR's CodeQL run is the authority and has not run on this head.

## Red checks

Check-run set at `ee29ed568e2701badacfb4febff27a7834ff1d04`, all 55 runs read (one page): no run concluded red; `CodeQL` `success` (alert 47 is closed there), `codeql / Analyze (python)` `success`, `tests / replay` `success`, `tests / mutation` `success`, `pr-contract / pr-contract` `success`, `gate` `success`; the others are `success` or `skipped`. The earlier reds on this branch (answered in previous bodies) are green at that head.

- `code-scanning alert 47 (py/clear-text-logging-sensitive-data)`: closed at ee29ed568 (CodeQL `success`). This head adds a print in `open_recorder` whose arguments are constants and, on the `--db` branch, the operator's own argument; no URL or recorder value reaches it. CodeQL has not concluded at this head.
- `code-scanning alert 48 (py/clear-text-storage-sensitive-data)`: `tests/replay.py` `_mariadb_install`, a false positive (an invented credential at an invented host inside a `TemporaryDirectory`); no detector can be cheaper than the finding; dismissal is owed to the owner, tvofi.
- `CodeQL`: red at earlier commits of this branch for alerts 47 and 48 (above); `success` at ee29ed568.
- `tests / fast (3.14)`: red once, at df35202a, where `tests/entities.py` FAILED (run 41269647846; its log keeps only the `FAILED` line); `success` at ee29ed568 and unchanged by this delta. Cheaper detector: `tests/entities.py` itself, which `prepr.sh` runs before the push; standing cost: already in the scoped gate (about 5 minutes); no new check proposed.
- `tests / mutation`: red at df35202a, 4cccd845 and 4c994241 for `ADDED UNPINNED` mutants in `custom_components/heatpump_optimizer/replay_doc.py`, pinned by later commits; `success` at ee29ed568. Cheaper detector: `prepr.sh` step 6d, which lists the sites a diff adds before the push; standing cost: seconds per handoff, already standing. This round adds no such site.
- Local-only reds on this box: `tests/replay.py` loop_cpu_ratio and `tests/golden.py` drift, both explained under Figures; CI's `tests / replay` and `gate` were green at the previous head.

## Carries

The group's eight roster carries, by index; dispositions unchanged from the earlier rounds' accepted record, none re-taken this round.

- Carry 1 (the real day), Carry 2 (classify the fixture), Carry 3 (#2810), Carry 4 (the R10-DIAG-REDACT precondition on the exported document), Carry 5 (the day choice), Carry 7 (the owner's export result) and Carry 8 (D15-s1-04, a boolean under a credential-named key): done.
- Carry 6 (STRANDED CARRY 57, cost-budget spread): half done; the open half, re-centring on the second CI class, is R10-REPLAY-COST-BUDGET's (see `## Forward-carry`).

## Forward-carry

- R10-REPLAY-COST-BUDGET: the `cpu_ratio`/`loop_cpu_ratio` re-centring and the two round-4 survivors (AWAY_COVERED, the unsupported-scheme refusal), routed by the orchestrator in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-REPLAY-COST-BUDGET

## Friction

none
