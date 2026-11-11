# R10-RCA-INERT-CLOSURE-RECORDING: a recording's INERT split is the recording tree's, not the checking tree's

The root-cause seat `r10-rca-inert-closure-recording`. It ran beside PR **#2662**
(R10-CI-LAYOUT-P2, part b, `fix/r10-ci-layout-p2b`) and not inside it
(`dev/governance/roles/root-cause.md`, `dev/governance/rules/defect-root-cause.md`).
Base `origin/main` `4c31eb16e`. Every recording below is a local Linux `strace`
recording (`./tests/derive_closures.sh --single tests/harness_headers.py
--record-only`, `/opt/hpo/venv-ci` interpreter); evidence is the seat's scratch.

**Class.** I2 (`bugclasses.json`, barriered): a measured closure diverges from the
real dependency graph. The barrier's unit is the recording: `strace_files` files a
Python child's read of an INERT path under `inert_reads` and keeps it out of the
closure. Its unit did not reach instance 3 because that decision is taken by the
INERT list of the tree that *recorded*, and `merge` and `check` consume it as data.

## 1. The three reported instances, reproduced

| # | where | red | reproduced cause | this class? |
|---|---|---|---|---|
| 1 | `a0f525900` (`ci-probe/all`, run 39918505090, job 120297997672, 21 min 37 s) | `tests / closures` INERT READS UNDER-APPROXIMATED: `entities.py` on u5's `run_part.py`, `unitcheck.py` and `tools/pr/codeql_scope.py`; `harness_headers.py` on 13 new harness files in 9 new directories | new reads of INERT-prefix files; no INERT edit in the diff | no: the INERT-PREDICT barrier's residual (a new directory has no siblings; `_u5_load` is a dynamic path). `ci_predict.py` at that head: quiet (measured) |
| 2 | #2656 at `d0ff8268b`, `closures-autofix` job 120356230438 | `skip-merge-failed`: merge refused the INERT-and-read pair (`entities.py` imports u5's modules in-process, so they are in `files`) | the #357 refusal working as built; its repair is a classification, which `ci-autofix.md` keeps out of automation | no |
| 3 | `d5b053e` (probe B2, #2657; contains #2662's code head `4a83592e3`), `closures` job 120398407061 (32 min 06 s), `closures-autofix` job 120411385621 | UNDER-SCOPED `tests/harness_headers.py`: `r10_ci_layout_u5/run_part.py`, `unitcheck.py`; autofix `skip-classifier-disagrees` | below | yes |

Instance 3, step by step:

- `9f7f443cc` adds `run_part.py`, `unitcheck.py` and `codeql_scope.py` to
  `INERT_EXCEPT`. `harness_headers.py` reads the two u5 files from a **child**
  process, which only `strace` sees.
- `4a83592e3` merges artifact 12493224545, recorded at `d0ff8268b`, before that
  edit. Recording `harness_headers.py` at `d0ff8268b` locally (3 min 58 s) files
  `run_part.py`, `script_runs.py` and `unitcheck.py` under `inert_reads` and none
  in `files`, which is what `4a83592e3` added to the table: the three under
  `harness_headers.py`'s `inert_reads`, nothing in its closure.
- `check` over that same recording passes at `4a83592e3` and at `d5b053e`:
  `closure: committed closures cover every file this run touched`, rc 0. The
  check is vacuous.
- Recording at `d5b053e` (4 min 08 s) files the two excepted files in `files`.
  `check` over it prints CI's UNDER-SCOPED with the same two files, rc 1.
- `closures-autofix` runs the base's `closure.py`, where they are still INERT, so
  its check is quiet: `skip-classifier-disagrees` (as `ci-autofix.md` lists).

**Cause.** `strace_files(trace, inert)` applies `is_inert` when the trace is
read, at record time (since `dfb57a515`, R9-F10.9d); `_fold` says why that is the
wrong place: "Filtering happens here rather than in the tracer so that it applies
identically to every record, including ones taken before the filter existed."
The INERT split was the one filter in the tracer.

## 2. Process state: (c)

The process followed is `ci-autofix.md`'s: on a red autofix "re-derive the script
it names and commit `tests/closures.json`", where "the inert dimension, which is
Linux-recorded (`strace`-only)", comes from CI's recordings. The seat merged
CI's Linux recordings and ran `check`; `check` said clean. It was wrong because
both commands trust a recording's split. Not (b): the refusal named `entities.py`'s
pair, not `harness_headers.py`, and off Linux a `--single` sees no child read, so
the named route could not record it there either. Not (d): an INERT edit is the
input the recorder exists for, not a changed precondition. Locally nothing ran:
all three heads edit `tests/closure.py` or a workflow, so `closure.py affected`
answers `full` (measured at `a0f525900`, `d0ff8268b`, `d5b053e`) and `prepr.sh`
step 6b prints "a full derive here is forbidden"; step 6d (`ci_predict.py`) was
quiet at each head (measured, 6.3 s at `d5b053e`).

## 3. Class search

- **Every consumer of a recording**: `merge` (full and partial), `check`, and
  `apply_under_scoped_recordings` (which calls `check`). All read
  `rec["files"]`/`rec["inert_reads"]` as recorded. `_widen`, `DRIVEN_BY_OTHERS`
  and `PRODUCERS` apply at fold time and are unaffected. `unit_of`
  (`UNIT_DIRS`, one entry) is also applied at record time; no edit to it is in
  the history searched below.
- **Classifier edits on `origin/main`**: 82 non-merge commits changed `INERT` or
  `INERT_EXCEPT` (43 and 42 changes; 28 to `INERT_EXCEPT` since `dfb57a515`
  introduced the split).
- **The live table**: 8 `inert_reads` entries on `origin/main` name a file that
  is no longer INERT (`entities.py` 7, `doc_claims.py` 1). Each is also in that
  script's closure, so none is an under-scope today: the earlier edits were
  re-recorded at their heads. Instance 3 is the first measured where the
  closure did not also hold it.

## 4. Cost test

- `cost(defect)`: one red `closures` run, 32 min 06 s on instance 3, then
  another FULL run after the repair (a `closure.py` edit forces FULL);
  `closures-autofix` 12 s, unrepaired.
- `P(recurrence)`: 1 escape in 28 `INERT_EXCEPT` edits since `dfb57a515` (the
  measured window), about 69 s of red CI per edit.
- `cost(countermeasure, recurring)`: `_load_recording` 7.1 ms a recording
  (0.14 ms for the plain load it replaces; 845 `inert_reads`), about 0.24 s for
  a 34-recording check; `left_inert` 8.1 ms a `ci_predict.py` run.
- Passes; and an instance of a barriered class owes the barrier regardless.

## 5. Countermeasure (built; the I2 barrier's unit moves from record time to load time)

1. `tests/closure.py` `_load_recording`: `merge` and `check` re-read each
   recording's `inert_reads` under the loading tree's INERT list, moving a file
   that is no longer INERT into `files`. Only that direction: an in-process INERT
   read is already in `files`, where the #357 refusal answers it. Pinned in
   `closure.py selftest` (3 pins, one a null control).
2. `tools/pr/ci_predict.py` `left_inert`: on a diff that edits
   `tests/closure.py`, a committed `inert_reads` file that is no longer INERT and
   that the script's closure omits is predicted UNDER-SCOPED. Seconds, in step 6d
   and `body_push.sh`, where 6b records nothing for a FULL diff. Pinned in
   `prepr.sh --self-test` (2 pins, one a null control).

Demonstrated at instance 3's tree (`d5b053e`):

| run | before | after |
|---|---|---|
| `check` over the stale (`d0ff8268b`) recording | rc 0, clean | rc 1, UNDER-SCOPED, the 2 files |
| `merge --partial` of that recording | closure unchanged | `+2` lines in `harness_headers.py`'s closure |
| `check` (shipped `closure.py`) over the fresh `d5b053e` recording, against that merged table | n/a | rc 0 |
| `ci_predict.py` | quiet, rc 0 | 2 PREDICT UNDER-SCOPED lines, rc 1 |
| `ci_predict.py` with the merged table (null control) | n/a | quiet, rc 0 |

Null controls on `origin/main` `4c31eb16e`: `check` over a fresh recording is
rc 0 with and without the change; `ci_predict.py` on the countermeasure's own
diff, which edits `tests/closure.py`, is quiet. Mutation: `moved = []` in
`_load_recording` fails 3 of 117 `closure.py selftest` pins.

**Owner.** The closures instrument (`tests/closure.py`, `tools/pr/ci_predict.py`);
it lands as its own pull request, never inside #2662. #2662's own repair is the
merged table above: two lines in `harness_headers.py`'s closure.
