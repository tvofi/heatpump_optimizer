R9-CI-2b, PR 1 of 2 (tvofi's decision on the pre-study, 2026-10-08: build the layout first, since it unblocks PRs). Round 2.

GitHub computes `mergeStateStatus` with no merge driver. Every open pull request that re-recorded `tests/closures.json` therefore went DIRTY after a merge to `main`, and a DIRTY pull request runs no CI. On 2026-10-08 that was 4 of the 6 open PRs (#2054, #2053, #2025, #2010), and each one was DIRTY on this file alone. The ledger driver resolved every one of those locally.

The pre-study found two causes. This PR removes both in the writer.

- **Timings.** `recorded.<script>.seconds` was rewritten on every recording, and run-to-run noise is 0.3x–3.4x. A re-timing inside 2x of the committed value now keeps it (`closure.stable_seconds`, `SECONDS_BAND = 2.0`, which tvofi accepted). The ledger driver applies the same band, where before it always took the larger value. With this PR's writer, 12 of 72 real re-timings are still rewritten. `mutation_table.recorded_seconds()` reads the timing for three things: the sweep order, the budget estimate (`budget_seconds`) and a lazy driver's timeout, `max(floor, TIMEOUT_SCALE x seconds)` with `TIMEOUT_SCALE` 3. A run up to 2x the kept value therefore still fits its timeout, and the constant's comment now says to keep the band below 3.
- **Layout.** Lists and keys were kept in append order, so two branches appending at a list's tail edited the same lines (#2010's `inert_reads`). Every writer now goes through `write_closures`, whose text is `canonical_text(payload)`: `json.dumps(indent=1, sort_keys=True)` at every depth, with string lists sorted and de-duplicated. The driver writes that same text from either side's layout. **`closure.py check` refuses any text that is not byte-identical to it** (round 2), and the refusal names `python3 tests/closure.py canonical`. `closure.py canonical` re-sorted main's table once. That step changed no entry. The branch's only content change against the merge base is one new `inert_reads` line, `tests/harness_headers.py -> dev/audit/harnesses/r9_ci2b_closures_merge.py`, which classifies this PR's harness.

**Transition, once.** After this merges, every open pull request that touched `tests/closures.json` conflicts with it on GitHub one time. I measured that for #2054, #2025, #2010 and #2024 against a simulated main+#2057, using git's default merge.
- **Why the merge refuses.** A branch's own driver copy is the one its `git merge` runs, so the pre-change driver refuses main's re-sorted table.
- **How to finish it.** After the merge, the work tree holds main's driver: run `python3 tools/merge/ledger_merge.py --resolve tests/closures.json`, then commit. On #2010's head, `--resolve` returned 0 and its output is the canonical text. PR 2 (#2059) does the same merge from main's checkout.
- **A pre-change writer cannot land non-canonical text.** `closures-autofix` runs the base's `closure.py`. A pull request whose run still has a pre-#2057 base can get that job's pre-change text pushed to its branch (`{seconds, rc}` entries, appended keys). The required `closures` check runs the PR's own `closure.py`, whose `check` now refuses that text, so such a branch cannot merge green. The repair is `closure.py canonical`, or a main merge through the driver. A push to `main` forces `full`, so a table out of layout would turn main red within one merge, not silently.

## Head

`85d8301e9a1182018492a804f0fd633439b42906` is the code head (round 2), measured 2026-10-08. The orchestrator's script merges it into the pull request head with origin/main.

## Mutation proof

The ledger is `/Users/timmalmstrom/hpo-seats/r9-ci-2b/mutation.txt`. Each mutant was applied in a separate worktree, then restored.

- M1, `stable_seconds` band test deleted: `closure.py selftest` FAILs "a timing re-recorded within 2x keeps the committed seconds" and "two branches re-timing one script merge with no driver".
- M2, `write_closures` sorts nothing: FAILs "a merge writes sorted keys and sorted lists" and "two branches re-timing one script merge with no driver".
- M3, `check`'s layout refusal deleted: FAILs "check refuses an unsorted table".
- **M8 (round 2), the byte comparison deleted**: FAILs "check refuses a recorded entry as {seconds, rc}", "check refuses top-level keys unsorted" and "check refuses indent 2" (3 of 56).
- M4, the driver's band deleted: `ledger_merge.py --self-test` FAILs "closures: two re-timings inside 2x of the base keep the base".
- M5', the driver's layout sort deleted (round-2 shape): FAILs "closures: the driver writes the layout from two tail-appended legacy sides" and "closures: --resolve finishes a merge an older driver left conflicted".
- M7, the `--resolve` write-back deleted: FAILs "closures: --resolve finishes a merge an older driver left conflicted".
- M0, unmutated: `ALL 56 closure shrink pins PASSED`, `all passed`.

Failing first:
- Round 1: `/Users/timmalmstrom/hpo-seats/r9-ci-2b/failing-first.txt`.
- Round 2: before the byte comparison, the three variant pins read FAIL `rc=0` (`/Users/timmalmstrom/hpo-seats/r9-ci-2b/failing-first-r2.txt`).

## Null control

- In `closure.py selftest`, write_closures' own text is the null control for the three refused variants: "check passes write_closures' own text (null control)".
- In the harness `dev/audit/harnesses/r9_ci2b_closures_merge.py`, the `as_written` arm is the unmodified writer's output. Merges are `git merge-file`, so no driver takes part.

## Figures

- The pre-study's own population (21 closures.json edits from the 98 PR merges among the last 120 merges at `816547ef`, 420 ordered pairs), re-measured with this PR's writer (`stable_seconds` + `canonical_text`) beside git's text merge:
  - Result: `RESULT population=816547ef pairs=420 as_written=70 pr_writer=16 seconds_rewrites=72 still_rewritten_by_band=12`.
  - The pre-study's 14 was its seconds-removed arm. This writer keeps the band, so the right figure is 16.
  - The command is in this seat's study dir, `/Users/timmalmstrom/hpo-seats/r9-ci-2b/study/` (`synth.py` population, PR-writer arm). The in-tree successor is the harness below.
- `python3 dev/audit/harnesses/r9_ci2b_closures_merge.py pairs 120` at today's main printed `RESULT pairs=506 semantic=0 conflicts_as_written=87 conflicts_layout=17`. The 17 remaining are large deletions (#2015's path moves, #1851) that meet an insertion in the same range.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: FULL`, because `tests/closure.py` is a gate file. Run locally on venv-ci 3.14 at `85d8301e`:
  - `tests/closure.py selftest` (ALL 56)
  - `tools/merge/ledger_merge.py --self-test`
  - `tests/entities.py` (ALL 2210)
  - `tests/harness_headers.py` (ALL 109)
  - `tests/layout.py`
  - `tests/env_drift.py --claims-only origin/main`
  - `tests/structure.py` (passed, no budget touched)
  
  The rest of FULL is CI's.

## Red checks

These were measured at the previous head `af9936d8`. CI at the head this update pushes will be re-read by the orchestrator.

- `nightly-status` (job 113300181884): `main`'s last scheduled run 37595831734 failed `mutation-ledger`, `mutation-nightly` and `record-autofix`. Those are lanes on `main` that this diff does not touch. The nightly reports its own state, so no cheaper detector is owed.
- `delivery-status` (job 113300036748): OVERDUE, because rows for merges already on `main` are unread (`record: delivery rows for #1998`, `#1992`, `#1991`, `#1989`). This diff adds only its own row. Clearing it is the orchestrator's, on `main`. The check already runs on every pull request, so none is owed.

## Forward-carry

none. The transition is handled by `--resolve` and by #2059's bot, which is this seat's own PR.

## Friction

none
