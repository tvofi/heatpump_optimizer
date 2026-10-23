Fix review: merge 0dda6260a8261233bb435442e52c219f3117a747
bus-nonce: aa8a60022517f4473bf4d0d78a0288bd

Review round 1 of #2666 (R10-FLY-INERT-LOAD-TIME, class I2 barrier), at head `0dda6260a8261233bb435442e52c219f3117a747` (code head `e9d169b79`), merge base `4c31eb16e`. Contract currency: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` empty. Evidence files are under `evidence/`.

## Detector shown to detect (defect-root-cause.md), both arms re-run by this seat

The finder's harness is CI's own: Linux recording artifact 12493224545 (`closure-recordings`, recorded at `d0ff8268b`), file `harness_headers.py.json`, which files `r10_ci_layout_u5/{run_part,script_runs,unitcheck}.py` under `inert_reads` only. It was read, not re-derived; no Linux recording was re-made on this Mac.

- RESULT check-before: in a standalone clone at `d5b053e`, with `d5b053e`'s own `tests/closure.py`, running `python3 tests/closure.py check --in-dir <that recording> --partial` gives rc=0 and prints "committed closures cover every file this run touched". That is the vacuous pass. (evidence/d5b-check-before.txt)
- RESULT check-after: the same tree with only this PR's `tests/closure.py` diff applied (`git apply --3way`, clean) gives rc=1, UNDER-SCOPED on `tests/harness_headers.py` for `run_part.py` and `unitcheck.py`. That is exactly CI job 120398407061's pair. (evidence/d5b-check-after.txt)
- RESULT predict-before: at `d5b053e`, running `python3 tools/pr/ci_predict.py --base a6620c30a` (the merge base with main) gives rc=0 with no closures prediction. (evidence/d5b-predict-before.txt)
- RESULT predict-after: the same command with this PR's `ci_predict.py` and `closure.py` diffs applied gives rc=1 with 2 `PREDICT tests / closures UNDER-SCOPED tests/harness_headers.py: … leaves INERT` lines (run_part.py, unitcheck.py). `script_runs.py` is still INERT there and is correctly not named. (evidence/d5b-predict-after.txt)
- RESULT prepr plant: CI instrument-self-tests (job 120440697962, success) prints `ok 6d predicts UNDER-SCOPED … (r10-rca-inert-closure-recording)` and `ok and is quiet once the closure lists it … (null control)`. Cited, not re-run. (evidence/ci-selftest-lines.txt)

## Mutation proof (step 1), re-run in a throwaway clone at the head

`python3 tests/closure.py selftest` at the head prints ALL 117 closure shrink pins PASSED, rc 0. Each mutant was killed:

| mutant | result |
|---|---|
| `moved = []` | 3 of 117 FAILED (the body's three) |
| drop the `rec["files"]` union | 2 of 117 FAILED |
| drop the `rec["inert_reads"]` filter | 2 of 117 FAILED |
| `merge` reverted to raw `json.loads` | 1 of 117 FAILED |
| `check` reverted to raw `json.loads` | 2 of 117 FAILED |

`left_inert`'s removal is the predict-before/after pair above.

## Class (step 6)

The body's rule is every consumer of a recording's split, plus every classification made at record time. My own enumeration was `glob("*.json")` and `json.loads` over recording directories in `tests/closure.py`, plus `inert_reads` readers repo-wide. It returns:

- `merge` and `check`: both routed through `_load_recording`, so in the diff.
- `apply_under_scoped_recordings`: it raw-loads only for its absent-path filter, then calls `check` and `merge`, so it is routed.
- `_loadable_recordings` / `proof_consume` (C2): not in the body's list, but it is refused unless the tree is byte-identical, so the INERT list is the recorder's own and there is no seam.
- Committed-table readers (`inert_read_owners`, `select`, `lane_skip.py`): these read the table, not a recording. A stale table entry for a file that left INERT still selects its script by the exact match, or forces FULL through `unmapped`. That fails toward selection, so there is no silent seam.
- `is_inert` is pure path shape, and all of its inputs (INERT, INERT_EXCEPT, HANDOVER_DIRS, the `_is_header_corpus`, `_is_archscore` and `_CITATION_POLICY` shapes) live in `tests/closure.py`. So `left_inert`'s arming condition ("diff edits tests/closure.py") covers every way a path can leave INERT.
- The reverse direction (a child read filed in `files` that is now INERT) is dispositioned in `_load_recording`'s docstring as the #357 refusal, which fails loud.

No class-open seam.

## Re-derived figures (step 8)

- 8 live `inert_reads` entries are not INERT at the head, and 0 of them are missing from their script's closure: matches.
- 28 commits change `INERT_EXCEPT` since `dfb57a515`: matches.
- 82 commits change INERT or INERT_EXCEPT: my own parser over `git log --no-merges 4c31eb16e -- tests/closure.py` gives 83, and the one extra is `a207e7e6e`, which creates the file. Excluding the creation, it is 82, which matches. That definition is mine. (evidence/class-counts.txt)
- Timing re-taken on this Mac with 200 calls of `time.perf_counter`: `_load_recording` is 12.89 ms on the 845-entry `harness_headers.py` recording (the body says 7.1 ms over its own recording and host), and `left_inert` is 9.41 ms (body: 8.1 ms). Same order, and the cost test's conclusion is unchanged. (evidence/timing.txt)
- I did not re-take the job durations (32 min 06 s and the others), which come from the jobs API.

## Other steps

- Step 4: there are no claim, golden, `closures.json` or budget files in the diff. `python3 tests/env_drift.py --claims-only 4c31eb16e` prints "claims hygiene … ok". The diff contains no production code, so no fixture can move. The full `--all` capture was not run.
- Step 5: VERSION, the manifest and the notes heading are untouched. CI's `prepr.sh --version-edit` prints "no version edit".
- Step 7: the body names head `0dda6260a`, which is the measured head.
- Step 9: there is no committed finder harness. The instance is CI job 120398407061 and its artifact, which I measured directly. I built no instrument beyond a count parser and a timing loop, both disclosed above.
- Step 10: the body's Forward-carry is `none`. No later stage is constrained, since the barrier changes `merge`/`check` behaviour without changing any rule a seat follows.
- Step 11: the head's 44 check-runs, read through the commit `check-runs` API, show `pr-contract` failure twice (13:28Z and 13:30Z). Both are `carry_audit.py` UNROUTED on an earlier body's Forward-carry line, and the run started 13:34:35Z succeeded. `pr-contract` is excluded from the body's must-answer set (`select(.name != "pr-contract")`), and that run prints `record red-history 2 commit(s) … every failure conclusion across them: none`. No gate check went red; "Red checks: none" stands.
- Step 13: `git merge-tree --write-tree origin/main 0dda6260a` gives rc 0 at `fd7e289d0`.
- Step 14: the diff moves no budget, closure table or score. The `bugclasses.json` rca entry is the record this RCA owes.
- Step 15: `_load_recording` is a single loader both consumers share, and `left_inert` follows `inert_siblings`' arm pattern. No architecture breach.

## Non-blocking

- This diff adds one new false refusal, measured. `_load_recording` moves a no-longer-INERT `inert_reads` path into `files` without the record-time `_is_real_file` filter, and `apply_under_scoped_recordings`' #1569 absent-path drop filters only `files` before `check` re-splits. Planted case: a recording whose `inert_reads` names an absent, non-INERT path. With the head `closure.py`, `check` gives rc 1, NOT A FILE. With the base `closure.py`, the same recording gives rc 0 (null control). (evidence/absent-head.txt, absent-base.txt)
  - It is reachable only in the autofix job, and only when main adds a file and makes it INERT before the branch merges main, with a child-process read of it.
  - It fails loud (`skip-manual-repair-owed`, naming the path), and merging main repairs it.
  - The fix is one line: move only `_is_real_file` paths. Carry: dismissed: fail-loud refusal under a rare precondition, repaired by merging main; escalated to the orchestrator for a follow-up decision
- #2662's current head `04fd214a1` lists none of the u5 files in `tests/harness_headers.py`'s closure, and has no `closures` run on it yet. That is the body's "For #2662" repair, not this PR's. Carry: dismissed: another pull request's own repair, reported to the orchestrator
