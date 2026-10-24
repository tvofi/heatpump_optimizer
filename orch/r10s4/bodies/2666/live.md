R10-RCA-INERT-CLOSURE-RECORDING: the root-cause seat beside #2662 (R10-CI-LAYOUT-P2, part b). It never touched #2662 or its refs. The analysis is `dev/audit/rca/R10-RCA-INERT-CLOSURE-RECORDING.md`, indexed under class I2 in `dev/audit/config/bugclasses.json`.

## Root cause

**Instances, reproduced.** Only one of the three reported instances is this class.

- **Instance 1** is `a0f525900`, `tests / closures` INERT READS UNDER-APPROXIMATED (job 120297997672, 21 min 37 s). The diff adds new reads of files under INERT prefixes and makes no INERT edit. `entities.py` imports u5 through `_u5_load`, which is a dynamic path. `harness_headers.py` reads 13 new harnesses in 9 new directories. This is the known residual of the INERT-PREDICT barrier. `ci_predict.py` at that head: quiet.
- **Instance 2** is #2656, `closures-autofix` `skip-merge-failed` (job 120356230438). This is the #357 INERT-and-read refusal working as built: `entities.py`'s reads are in-process, so they sit in `files`. The repair is a classification, and `ci-autofix.md` keeps classification out of automation. Not a defect.
- **Instance 3** is `d5b053e`, `tests / closures` UNDER-SCOPED on `tests/harness_headers.py` (job 120398407061, 32 min 06 s). The autofix then gave `skip-classifier-disagrees` (job 120411385621). This is the defect.

**Cause (instance 3).** `strace_files` splits a Python child's reads by the INERT list of the tree that recorded the trace.

1. Recorded at `d0ff8268b`, the tree that made artifact 12493224545, `harness_headers.py` files `r10_ci_layout_u5/run_part.py` and `unitcheck.py` under `inert_reads` only.
2. `9f7f443cc` then excepted both files from INERT.
3. `4a83592e3` merged that artifact. `merge` and `check` take a recording's split as data, so the two files stayed out of `harness_headers.py`'s closure.
4. `check` over that same recording printed `committed closures cover every file this run touched` (rc 0) at `4a83592e3` and again at `d5b053e`. The check was vacuous.
5. A recording at `d5b053e` reproduces CI's UNDER-SCOPED exactly: the same two files, rc 1.

`_fold` states the rule this breaks: "Filtering happens here rather than in the tracer so that it applies identically to every record, including ones taken before the filter existed." The coordinator's account holds. What it misses is that `merge` wrote the stale split into the table as well.

**Process state: (c).** The route `ci-autofix.md` gives the inert dimension was followed: merge CI's Linux (`strace`) recordings, then `check`. It said clean and was wrong. Three other reads were ruled out:

- **Not (b).** The refusal named `entities.py`'s pair, not `harness_headers.py`. Off Linux a `--single` sees no child read at all.
- **Not (d).** An INERT edit is the recorder's ordinary input.
- **No local path existed.** `closure.py affected` answers `full` at all three heads, so `prepr.sh` step 6b prints "a full derive here is forbidden". Step 6d was quiet at each head.

Class I2 is barriered. Its unit, the recording, carries a decision that a later INERT edit voids. The countermeasure moves that decision to load time.

**Class search.**

- Every recording consumer trusts the split: `merge` (full and partial), `check`, and `apply_under_scoped_recordings` through `check`.
- 82 non-merge commits on `origin/main` change `INERT` or `INERT_EXCEPT`. 28 of them changed `INERT_EXCEPT` since `dfb57a515` introduced the split.
- 8 live `inert_reads` entries name a file that is no longer INERT. All 8 are also in their script's closure, so none is under-scoped today. Instance 3 is the first measured escape.
- `unit_of` is the only other classification made at record time, and it has no edits in that history.

**Cost test.**

- Defect: 32 min 06 s of red FULL `closures` per escape, plus a second FULL run after the repair. Measured rate: 1 escape in 28 `INERT_EXCEPT` edits, about 69 s per edit.
- Countermeasure: `_load_recording` costs 7.1 ms per recording, about 0.24 s for a 34-recording check. `left_inert` costs 8.1 ms per predictor run.
- The countermeasure passes the test. An instance of a barriered class owes the barrier in any case.

**Countermeasure (the barrier, built).**

- `tests/closure.py` `_load_recording`: `merge` and `check` re-read each recording's `inert_reads` under the loading tree's INERT list.
- `tools/pr/ci_predict.py` `left_inert`: a diff that edits `tests/closure.py` gets a static UNDER-SCOPED prediction when a committed `inert_reads` file has left INERT and its script's closure omits it. This runs in prepr step 6d and in `body_push.sh`, and costs seconds. Step 6b records nothing for a FULL diff.
- Owner: the closures instrument. This lands as its own pull request, not inside #2662.
- No policy change is proposed. The rule was followed, so a firmer rule would not have helped.
- For #2662, which this seat does not touch: its repair is two lines in `tests/closures.json`, putting u5's `run_part.py` and `unitcheck.py` in `tests/harness_headers.py`'s closure. That is what `merge --partial` of a `harness_headers.py` recording writes at `d5b053e`.

| at `d5b053e` | before | after |
|---|---|---|
| `check` over the stale `d0ff8268b` recording | rc 0, clean | rc 1, UNDER-SCOPED on the 2 files |
| `merge --partial` of that recording | closure unchanged | `+2` lines in `harness_headers.py`'s closure |
| `ci_predict.py` | quiet, rc 0 | 2 UNDER-SCOPED predictions, rc 1 |

## Head

`0dda6260a8261233bb435442e52c219f3117a747` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2666.md`. The authored code head is `e9d169b79b16355cdfa64d50d11daab2d7475c54`.

`e9d169b79`, which is `origin/main` `4c31eb16e` plus this diff. Instance trees: `a0f525900`, `d0ff8268b`, `4a83592e3` and `d5b053e`.

## Mutation proof

Setting `moved = []` in `_load_recording` fails 3 of 117 `closure.py selftest` pins:

- the stale recording reads as UNDER-SCOPED;
- check passes once the closure lists the file;
- merge writes the file into the closure.

Without `left_inert`, `ci_predict.py` at `d5b053e` is quiet with rc 0. With it, rc is 1. In `prepr.sh --self-test`, the `pleft` plant gives a PREDICT UNDER-SCOPED line.

## Null control

- On `origin/main`, `check` over a fresh `harness_headers.py` recording returns rc 0 with and without the change.
- `ci_predict.py` on this diff is quiet. The diff edits `tests/closure.py`, so the new arm is armed.
- At `d5b053e` with the table that `merge` writes, the shipped `closure.py`'s `check` over a fresh recording returns rc 0, and `ci_predict.py` is quiet.
- The `pleftrec` plant makes the same INERT edit with the closure listing the file, and stays quiet.

## Figures

- 32 min 06 s, 21 min 37 s and 12 s are the jobs API's `started_at`/`completed_at` for jobs 120398407061, 120297997672 and 120411385621.
- 4 min 08 s and 3 min 58 s: `./tests/derive_closures.sh --single tests/harness_headers.py --record-only --out-dir D` at `d5b053e` and at `d0ff8268b`.
- 82, 28 and 8 are the class-search counts described above. 82 and 28 come from parsing the `INERT`/`INERT_EXCEPT` tuples of `tests/closure.py` per commit. 8 is `closures.json`'s `inert_reads` filtered by `closure.is_inert`.
- 7.1 ms, 8.1 ms and 0.14 ms: `time.perf_counter` over 200 calls each of `closure._load_recording`, `ci_predict.left_inert` and `json.loads`.
- 117 pins: `python3 tests/closure.py selftest`.
- 6.3 s: `python3 tools/pr/ci_predict.py --base <merge-base>` at `d5b053e`.

## Red checks

none

## Forward-carry

none. #2662's own repair is reported to the coordinator, not carried from here; see the `For #2662` line under `## Root cause`.

## Friction

none

