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

`4ff6152ea166d6e11db880ae9fa70727efcaa547` merges the authored code head `88e04a5ca106a261de1a2ab8d2e08a0c6d0bae32` and then merges origin/main `af79f2114` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`88e04a5ca106a261de1a2ab8d2e08a0c6d0bae32` is the code head (round 3), on `03f7be4d362947f301e02c419e9ceb3b82fc7db4`. It changes one place: the `--resolve` self-test in `tools/merge/ledger_merge.py` now builds its throwaway repository with `throwaway_git_init` from `tests/throwaway_git.py` (#2054, R9-GITTMP), not with a raw `g("init", "-q", "-b", "main")`. It gets that function the way the same self-test's other repository already did. The helper's environment carries the identity that the deleted `env` dict used to set.

`03f7be4d362947f301e02c419e9ceb3b82fc7db4` merges main `af79f2114` into `47d48472`. That was an automatic merge by the merge train, with no resolution.

`47d48472d4e348c5076831984691e3a122944e5e` merges the code head `85d8301e9a1182018492a804f0fd633439b42906` (round 2) and origin/main `4647321d8`.

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

- Round 3: `tests/throwaway_git.py --check` is the failing test for this change. At `03f7be4d` it printed `REFUSE tools/merge/ledger_merge.py:569: g("init", "-q", "-b", "main")` and `1 raw git init or clone site(s) refused` with rc=1. At `88e04a5c` it printed `0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD` with rc=0. The `03f7be4d` run is the null control: the same command against the unconverted line refuses it.

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
- Round 3, at `88e04a5c` on venv-ci (`PATH=$HOME/.local/state/hpo/venv-ci/bin:$PATH`): I ran every step of `governance.yml`'s `instrument-self-tests` job by its own command, and each gave rc=0. That includes `throwaway_git.py --self-test` (`44 checks, 0 failed`) and `--check`, and `merge_train.py --self-test` together with its `0 failed` grep. Also rc=0:
  - `tools/merge/ledger_merge.py --self-test`: `all passed`, 50 `ok` lines, among them "closures: --resolve finishes a merge an older driver left conflicted".
  - `tests/structure.py`.
  - `PYTHONPATH=tests/hastub:custom_components:tests tests/entities.py`.
  - `closure.py select` still prints `MODE: FULL`, because `tests/closure.py` is a gate file.

## Red checks

These were measured at `03f7be4d` from its check-runs. CI at the head this update pushes will be re-read by the orchestrator. `coverage` was still in progress and is not waited on.

- **`instrument-self-tests`** (job 113428743954), step "Refuse a throwaway git repository built without the shared helper". The cause is that #2054 (R9-GITTMP) landed `tests/throwaway_git.py --check` on `main`, and that check refuses a raw `git init` in a tracked script. The merge train's main merge brought it onto this branch's round-1 `--resolve` self-test, which built its repository with `g("init", "-q", "-b", "main")` at `tools/merge/ledger_merge.py:569`. Neither side was wrong alone; the merge made the red. It is fixed in `88e04a5c`. **Cheaper detector**: run the job's own self-tests locally on the merged tree after any main merge. Its standing cost is about a minute of local time per merge; `python3 -I tests/throwaway_git.py --check` alone takes seconds. The merge train's merge was automatic, with no seat re-running instruments on the merged tree. This update re-ran the whole job locally at the code head (see Figures).
- **`pr-contract`** (job 113429992729): `[pr-body]` refused because `instrument-self-tests` was red and `## Red checks` did not name it. The body at `03f7be4d` predated that red. This body names it above. Cheaper detector: none is owed beyond the one this check already is, since it runs on every body push.
- **`delivery-status`** (job 113300036748, at the ancestor head `af9936d8`; it was green at `03f7be4d`): it was OVERDUE because rows for merges already on `main` were unread (`record: delivery rows for #1998`, `#1992`, `#1991`, `#1989`). This diff adds only its own row, `docs/delivery/2057.md`, and that row was not among the overdue ones. Clearing them was the orchestrator's, on `main`. No cheaper detector is owed, because the check already runs on every pull request at a standing cost of seconds.
- **`nightly-status`** (job 113428743210): this is `main`'s state, not this diff's. The check reports `main`'s last scheduled nightly, whose failed lanes this diff does not touch. The nightly reports its own state, so no cheaper detector is owed.

## Forward-carry

none. The transition is handled by `--resolve` and by #2059's bot, which is this seat's own PR.

## Friction

none

