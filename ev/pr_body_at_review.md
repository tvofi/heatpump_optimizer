fix(seat): a row-only `update_pr.sh` push takes the body contract, not the full prepr

`update_pr.sh <branch> - <body>` exists to add a pull request's own delivery row, but its push ran the full `prepr.sh` (suites, mutants, the heavy-slot lease). On 2026-10-21, on a box queued on `gate_lock.py`'s four slots, the one-line rows for #2557 and #2558 sat 30+ minutes, and `bus.sh dispatch` refuses a head without `dev/programme/delivery/<N>.md`, so reviewer dispatch waited on them.

**What changed.** `tools/pr/app_push.sh` gains `--row-only` beside `--recarry`, with `recarry_verdict`'s shape: `row_only_verdict` reads HEAD once, takes the live head, number, title and body from the open-pull-request listing app_push already reads, and skips prepr only when all four hold, each failing closed and named on one `app_push: ROW-ONLY:` line:

- (a) HEAD has exactly one parent, the live pull-request head;
- (b) `git diff --name-status <live> HEAD` is exactly one added file, `delivery_row.sh`'s `$ROW_DIR/<N>.md` for the listing's `<N>`;
- (c) that file is one open row anchored on `<N>`, read by `tests/delivery_status.py`'s `anchored` and `OPEN_STATUS` (the tree's row reader, not a copy of its grammar);
- (d) the body file is the live body under one new `## Head` note: `head_note.py`'s own `prefix(live, note)`.

On the skip, `row_only_checks` runs step 7's body contract, pr-contract's command (`policy_lint.mjs --pr-body --head --title --paths-file --existing-file`) at the judged head with the pull request's live title; a refusal there pushes nothing. Anything else runs prepr exactly as without the flag. The push is pinned to the HEAD the verdict judged, as `--recarry`'s is. `update_pr.sh` passes `--row-only` for code sha `-` only (`# mut:rowonly`) and prints app_push's `ROW-ONLY:` line; a code sha never asks.

**Why the other prepr steps are not re-run on the skip.** The brief named three: the body contract, claim files byte-identical, and the row lint. The body contract runs. The row lint is (c). Claim files, `VERSION`, the manifest, code, closures and transport cannot move under (a)+(b): any second path in the diff, a claim file included, fails (b) and takes the full prepr, which is the null control below. Running a claim-file check after (b) would re-read what (b) pinned.

**Alternatives and why each lost (fixer.md step 17).**

- The skip decided in `update_pr.sh` alone, through `PREPR_BODY_PATH_ONLY` (prepr exits after its step 0): this lost because it bends a flag built for one step's test into a bypass, and the tool that mints and pushes would take a caller's word that the push is row-only. Here the verdict sits in `app_push.sh`, which owns the prepr gate and reads the live head itself, as `--recarry` does.
- A `prepr.sh --row-only` mode: this lost because it puts a second entry into a 2977-line script and still needs app_push's live-head reading to decide.
- `--recarry` itself: its (a) requires a two-parent merge, and a row commit has one parent.

**Scope beyond the brief's file list.** The brief listed `update_pr.sh`, `pr_args.sh`, `delivery_row.sh` and `INSTRUMENTS.md`. app_push.sh runs prepr unconditionally, so no change confined to those files could skip it soundly (see the first alternative). `delivery_row.sh` is unchanged: the verdict sources it for `ROW_DIR`, the one owner of the row's path.

## Head

`93015ecada7190edc054e49a47538704b14e1f34` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2567.md`. The authored code head is `e6dba2408a5f101ee43917b9e64b245888ec664f`.

`947d36312a73a35d5ecfaf4b4581ca2dbc37c086` merges origin/main `dbea71db7` into the authored code head `e6dba2408a5f101ee43917b9e64b245888ec664f` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`e6dba2408a5f101ee43917b9e64b245888ec664f`, cut from origin/main `3688cf259` (the base given), measured 2026-10-21T13:01Z.

## Mutation proof

Each mutant is a copy of `tools/pr/app_push.sh` beside it with one predicate removed, then `bash <copy> --self-test` (167 checks):

- M1, the `row_only_verdict ... && skip=1` line deleted (the row-only arm always runs prepr): 20 failed, among them `--row-only: the live head plus one commit adding only its own open row ...: pushed (prepr-fails set)` and `the body contract ran in its place ...`.
- M2, the verdict's result ignored (`; skip=1`), so every other arm skips: 8 failed. These are all eight `... prepr ran once, the one line names why (...)` arms: omore, oother, oedit, otwo, olive, orow, obody and onone.
- M3, (b)'s diff check deleted: 6 failed: omore, oother, oedit, and `real git: the same commit with one more file runs prepr (null control)`, `real git: another pull request's row runs prepr`, `real git: a rewrite of a row the live head carries runs prepr`.
- M4, (a)'s parent check deleted: 2 failed: olive, and `real git: the row on a commit past the live head runs prepr, though the tree diff is the row alone`.
- M7, (c)'s row-lint refusal deleted: 2 failed: orow, and `real git: a row file that anchors nobody runs prepr`.
- M6, (d)'s body refusal deleted: 2 failed: obody, and `real git: a body that is not the live one under one new note runs prepr`.
- M5, the `row_only_checks` call deleted: 3 failed: `the body contract ran in its place ...`, `--row-only: a body the contract refuses refuses, though prepr was skipped`, and `and nothing was minted or pushed`.
- `update_pr.sh`'s `# mut:rowonly` line is pinned by `pr_args.sh`'s own mutant arm: `mutant mut:rowonly (its line deleted): code sha '-' runs the full prepr`.

## Null control

- A whitespace-only mutant copy (M0) passes: `app_push self-test: 167 checks, 0 failed`. So the copy-beside-it runner fails only on a removed predicate.
- Skip versus prepr on the same row commit: `real git: ensure_row's own row commit on the live head skips prepr` passes. The same commit amended with one more file (`y`) gets the verdict line `the head adds or changes more than this pull request's own row dev/programme/delivery/7.md (git diff --name-status: A dev/programme/delivery/7.md; A y)` and runs prepr. In the stubbed arm `omore`, a diff with `tools/x.py` beside the row runs prepr once and no row-only check.
- `null control: a code sha never asks for --row-only, so its push runs the full prepr` (`pr_args.sh`).
- Failing test first, at the base's code with the new arms: `app_push self-test: 167 checks, 28 failed` (`row_only_verdict: command not found` in the real-git block) and `pr_args self-test: 59 checks, 1 failed` (`update_pr: code sha '-' asks app_push.sh for --row-only ...`). At the head: `app_push self-test: 167 checks, 0 failed`, `delivery_row self-test: 5 checks, 0 failed`, `pr_args self-test: 59 checks, 0 failed`.

## Figures

- `bash tools/pr/app_push.sh --self-test`: the tally line, 0 failed at the head; per mutant as in `## Mutation proof`.
- `bash tools/audit/seat/update_pr.sh --self-test`: delivery_row's and pr_args's tally lines, 0 failed at the head.
- `python3 tests/closure.py select --diff 3688cf25977ca71b4406be942df9592577d9b42e`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`, over the four changed files.
- Ran from `tests/run.sh`'s `run_always` lines with `PYTHONPATH=tests/hastub` under Python 3.13 (seat_venv.sh's 3.14 has no uv download here; a 3.13 venv from `tests/requirements-ci.txt`): `python3 tests/env_drift.py --claims-only 3688cf25977ca71b4406be942df9592577d9b42e` gave claims hygiene ok. The others: `python3 tests/closure.py selftest`, `python3 tests/layout.py`, `python3 tests/harness_headers.py`, `python3 tests/entities.py`; each printed its PASSED/ok line.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 3688cf25977ca71b4406be942df9592577d9b42e`: `Architecture score: dS +0.0000 NULL`.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>`: exit 0, `PRE-PR: e6dba2408a5f101ee43917b9e64b245888ec664f` with every step ok or skip and no refusal.
- Not measured: the wall-clock of a live row-only push. That push needs the App key, which no seat holds; the 30+ minutes is the brief's measurement.

## Red checks

none

## Forward-carry

none. The `--row-only` arm changes how `update_pr.sh` pushes, and that is recorded in `tools/audit/seat/INSTRUMENTS.md`'s `app_push.sh` and `update_pr.sh` entries in this diff. No later stage's brief has to work differently.

## Friction

- fixer.md-step-5: cost: `tools/audit/seat/seat_venv.sh` refused in this cloud container (`No download found for request: cpython-3.14.7-linux-x86_64-gnu`), and the system `python3` (3.11) cannot parse `tests/entities.py`, so the always-run checks needed a hand-built 3.13 venv. Carry: none (environment; reported here).

