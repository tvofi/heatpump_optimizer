Fix review: blocked ee29ed568e2701badacfb4febff27a7834ff1d04 requirement-unmet: the open line no longer tells an operator which recorder was read

bus-nonce: df0a2979fe616316aa4fe16af9bda459

Round 7 (scoped re-check). This is past the third round; the brief says the re-cut is pre-authorized. Measured head: ee29ed568e2701badacfb4febff27a7834ff1d04, which is still the PR head at verdict time (ls-remote fix/r10-replay-real-day).

## Block

1. **The repair drops the recorder's identity from every successful run (brief scope item 1).** The brief requires that "the printed text must still tell an operator which recorder was read (null control: the label path)". At this head, tools/replay/export.py:459 prints the constant `reading the recorder` (ev/export_open_line.txt).
   - On a run that succeeds, nothing on stderr or in the written document now names the recorder: not its kind (SQLite or MySQL/MariaDB) and not the --db path.
   - `rec.label` is printed only by the quiet-window refusal (export.py:492). The new check `recorder:sqlite_db_url_refusal_names_kind_not_path` pins that refusal path, not the open line.
   - The body says "the label no longer prints on open" but does not disposition the lost operator information. It only re-points the checks that used to assert on it.
   - Before this repair, the old line told the operator "SQLite <path>" for --db, the default path or a configuration.yaml path, and gave the kind for a URL.
   - A sound repair appears to exist without reintroducing the CodeQL flow: print a per-branch constant kind (for example "reading the recorder: SQLite database" / "MySQL/MariaDB database", chosen in open_recorder's branches from constants and never derived from the URL), or print the operator-supplied --db path only on the --db branch. Its killed mutant would be the open line made fully constant again. I did not run CodeQL on that alternative, so whether it stays clean is the fixer's to show.

## Findings

- The successful export no longer names the recorder it read: the open line at tools/replay/export.py:459 is constant, which breaks the brief's scope-1 requirement (Block 1). Carry: R10-REPLAY-REAL-DAY
- Round-4 finding 2 is still open and the body does not claim it fixed, so it is carried, not blocking. `AWAY_COVERED = frozenset({"owner-2026-10-30-away.json"})` is never checked against the committed fixtures. With that literal misspelt (`...-awy.json`), every FAST check stays green at this head (ev/my_mutants_r7.txt, SURVIVED). Carry: R10-REPLAY-REAL-DAY
- Round-4 finding 3 is still open. The unsupported-scheme refusal in open_recorder (`raise SystemExit("the recorder URL is neither SQLite nor "`) can be mutated to `f"the recorder {url} is neither SQLite nor "` and every FAST check stays green (ev/my_mutants_r7.txt, SURVIVED). For a credentialed postgresql:// URL that would print the password to stderr; it is the same class as alert 47, and nothing pins it. Carry: R10-REPLAY-REAL-DAY
- The forward-carry the body asks of the orchestrator is still owed: restate R10-REPLAY-COST-BUDGET's roster carry as re-centring 355.7 / 3740.0 / 0.249 on the second CI class. This container's null reads `cpu_ratio 385.3 over its budget 355.7` on the owner fixture (ev/one60_head_null.summary), the same class of red the body discloses. Carry: R10-REPLAY-COST-BUDGET

## Evidence

- Head: ee29ed568e2701badacfb4febff27a7834ff1d04 (ev/HEAD.txt). Its code head is 0cdcc3daa7ed, two commits on 67cc0e0a: 134d1b92b and 0cdcc3daa. The body's `## Head` names both the PR head and the code head.
- Delta: compared with 67cc0e0a merged with base 25c46e76e, the head differs only in tools/replay/export.py (1 line), tests/replay.py and dev/audit/harnesses/r10_replay_real_day_mutants.py (ev/delta_vs_old_plus_main.txt). This is only the repair.
- Merge with origin/main 25c46e76e: `git merge-tree --write-tree` exits rc=0 (ev/merge_tree.txt).
- CI: `merge_train.py classify` printed `GREEN ee29ed568e2701badacfb4febff27a7834ff1d04 pending: none red: none` with rc=0 (ev/classify.out, ev/classify.log).
- CodeQL: check run 125000782197 at this head concluded success, titled "No new alerts in code changed by this pull request", once `codeql / Analyze (python)` (125000581047) concluded success. When the packet was rendered it was neutral ("1 configuration not found") because the Python analysis had not finished. Alert 47 is gone at this head; no dismissal was needed.
- Mutation, with the fixer's harness at this head (ev/fixer_fast.txt): `RESULT killed=34 mutants=34 null_red=0`. That includes the new row "recorder label interpolated into the open line (alert 47)", KILLED by `recorder:open_line_constant_no_label`.
- Mutation, with my own FAST-tier variants (a reviewer-built script that reuses the in-tree harness's fast() and apply(); ev/my_mutants_r7.py, ev/my_mutants_r7.txt). NULL red []. Each variant below is KILLED; the check that turned red is in brackets:
  - rec.label restored in the f-string [open_line_constant_no_label]
  - rec.label by %-format [open_line_constant_no_label]
  - rec.label as a second print argument [open_line_constant_no_label]
  - db by str.format [open_line_constant_no_label]
  - db_url by concatenation [open_line_constant_no_label, sqlite_db_url_named_by_kind_not_path, sqlite_db_url_refusal_names_kind_not_path]
  - open line deleted [db_url_credentials_never_printed, open_line_constant_no_label, sqlite_db_url_named_by_kind_not_path]
- The open line now holds no f-string and no format argument.
- Finder's harness from round 4: `tests/replay.py --one tests/replay/owner-2026-10-30-away.json --step-minutes 60`, with HASTUB_TZ=Europe/Stockholm OPENBLAS_NUM_THREADS=1 PYTHONPATH=tests/hastub, summarised by ev/summ_finder.py through ev/run_one.sh (copied from the round-4 ref and re-pointed at this container).
  - Null at the head: away 0, 3 commanded cycles (active, override, floor/target 15.0), space_kwh 8.17 to 12.94, cycle_cost red `cpu_ratio 385.3 over its budget 355.7`. The cycle_cost reading is this container's CPU class: the CI `tests / replay` run (125000687320) concluded success at this head.
  - Mutant `recorded_away = []`: KILLED, away=2 ("declares away coverage but the replay carried no commanded cycle"; "records no active command").
  - Round-3 and round-4 behaviour is not regressed (ev/one60_head_*.summary).
- Body `## Red checks`:
  - It names `CodeQL`, alert 47, alert 48, `tests / fast (3.14)`, `tests / mutation`, `tests / replay`, `pr-contract / pr-contract` and `gate` by their literal names.
  - At this head no check concluded red, so nothing further is owed.
  - The body's "0cdcc3daa has not run CI" is about the code head, not the PR head. I could not read check-runs for 0cdcc3daa from this seat, so that sentence is not verified; it is also not a claim about this head.
- Standing checks:
  - Claim files, VERSION, manifest and RELEASE_NOTES are untouched three-dot from MB 25c46e76e. The delivery row dev/programme/delivery/3078.md is in the three-dot diff (ev/standing.txt).
  - `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (ev/structure.txt).
  - Scoped gate: CI `tests / fast (3.14)` (125000687293) log reads "15 TEST SCRIPT(S) PASSED; 18 SCOPED OUT AND NOT RUN (see the NOT RUN block above -- this is not a full gate)". The log tail I fetched did not include the `MODE:` line itself, so the mode is inferred from the scoped-out count, not quoted.
- Figures in the body:
  - `killed=34 mutants=34 null_red=0` re-derived.
  - "STRUCTURE RATCHET PASSED" re-derived.
  - The body's synthetic-dhw-only loop_cpu_ratio readings (0.1534, 0.1578, 0.1471, control 0.1488) were not re-derived: they are machine-dependent, and CI replay is green.
