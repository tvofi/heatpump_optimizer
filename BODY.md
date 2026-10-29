R10-RECORD-API-O1: the three carries the root cause of the 04:53Z installation rate-limit burst left open (R10-RCA-RATELIMIT-RECUR, #2852, `dev/audit/rca/ratelimit-recur.md` sections 4 and 5).

- **Carry 1, decision O-1 (M3), built.** Governance's `record` job now runs `--stats`, the friction filer and `--sunset` only when the window step's `report` output is `true`: on the weekly schedule, on a dispatch, and on the stamp's own push (the commit that changes `VERSION`). The stamp reports the release it closes, so its window is the `v*` tag before the stamp, not the empty window its own tag opens. An ordinary push to main reads `--record` alone. The cadence change is #959 option B's. The owner's call on it is carried by mandate 6329234399 (scope `all`, the mandate that recorded O-1 in `ratelimit-recur.md` section 4). Code-owned workflow: the owner reviews.
  `record_burst_replay.py` now counts the bucket's demand as record + enumerate + rest. The enumerate is counted through `enumerate_api_calls.count` at each push's own tip: the production `record_row.enumerate_merges` under the logging stub, read from a no-checkout worktree, not a formula. The rest rate and the limit are required arguments read from the hour's M0 lines, so the harness has no figure of its own. A new `O-1` shape replays the push arm at `W` per run. `enumerate_api_calls.py` gains `count(since, cwd)`; its CLI output is unchanged. `record_api_calls.sh` now reads which modes wait on `report` from the job text: `TOTAL` counts a push and `REPORT` the schedule, dispatch and stamp arm.
- **Carry 2, built.** Nightly `record-autofix` gets a second M0 pair around "Enumerate the window's merges": `RATE_LIMIT enumerate before:` and `RATE_LIMIT enumerate after:`. The after reading carries `always()`, so it prints even when the enumeration fails closed. Code-owned workflow: the owner reviews.
- **Carry 3, already closed on main.** `65ad0e0a3` (R10-FLY-REFPRIV-HOME-SEGMENT, #2949) added the path-segment boundary to `_home_re`. This branch does not touch `tools/audit/seat/ref_privacy.py`, and its control is re-measured below on this seat, whose home is `/root`.

The roster entry lists seven carries, and the last four restate the first three:
- **Carry 4** is carry 1's text without its `From #2852` prefix (decision O-1, M3). It is answered by carry 1's build above.
- **Carry 5** is carry 2's text plus its `Carry:` destination (the second M0 pair). It is answered by carry 2's build above.
- **Carry 6** is carry 3's text plus its destination (the `ref_privacy.py` home match without a path-segment boundary). It is closed on main by `65ad0e0a3`, as for carry 3.
- **Carry 7** is the same defect, from #2925's review: a bare `$HOME` substring match that refuses `roles/root-cause.md` on a seat whose `HOME` is `/root`. It is closed by the same `65ad0e0a3` (R10-FLY-REFPRIV-HOME-SEGMENT, #2949). Its control, a failing case on `/root` against `roles/root-cause.md` and a null control that a real path under root's home still refuses, is the carry-3 measurement under `## Null control`: `[]` at `88c6ad5bb`, `['home-directory']` at `d074b94b0`, and `cd /root/.cache/x` refused at both.

Disclosed, not carried:
- The stamp arm's cost. A stamp push runs `--record`, `--stats` and `--sunset` over the closing release window, about `W + 3P` once a release. `record_burst_replay.py`'s docstring says its `O-1` shape does not model a stamp inside the burst.
- Carry 2's control can only be read after landing, from a Nightly log. On a quiet push, `RATE_LIMIT enumerate after:` minus `before:` should equal `enumerate_api_calls.py <last v* tag>` at that push, within the interval's concurrent rest. A delta of 0 on a non-empty window means the pair brackets the wrong step. The roster's carry 2 already states this control for the landing seat.
- This seat's frugal-routing hook refuses every inline shell or read call after the fifth in a turn. Discovery went through delegated readers, and the hook was not disabled (the brief forbids working around a hook).

Alternatives considered (fixer.md step 17):
- An App installation token for `--stats` and `--sunset`. It moves the reads to another bucket rather than removing 3P reads a push; `install-ratelimit.md` M3 names it as the identity-changing alternative. Not taken, because the cadence move needs no new identity.
- Keeping the stamp off the report arm, with schedule and dispatch only. Not taken: `ratelimit-recur.md` section 4 names the stamp, and a release's last histogram would otherwise wait up to a week.
- For the replay's enumerate, a `2M`/`M` formula. Not taken: it re-implements the walker and would not move with M4's kind of change.

## Head

Code head: `0c99dc0e11222274234e363928f6138dd335b7ec` (`handoff/r10-record-api-o1`). It is one commit on PR head `464daee15bcdf326788a57c17023cca1aea64611`, which merged `origin/main` `279578074a17cb2c7f527f5e28da0de4e2006db0` into `3122bc41dab91b4abb74b1db9ccdda1f8be184c1`. The commit carries the `tests/closure.py` and `tests/closures.json` repair under `## Red checks`, measured 2026-10-29 at about 19:00Z (`date -u`). At that head `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. `python3 tools/pr/ci_predict.py --base origin/main --record-self-tests` prints `CI PREDICT: no closures, fast, wave-script or instrument red predicted against 279578074a17`. `python3 tests/closure.py select --diff origin/main` prints `MODE: FULL`.

The figures, mutation proof and null control below were taken at code head `3122bc41d` against base and `origin/main` `88c6ad5bbec69bfe157e04597a74d0c9c3e4775c`, measured 2026-10-29 at about 15:20Z (`date -u`). They are stamped with that tip. The window is `v7.0.5..origin/main`, with 64 first-parent commits and 59 merges at that tip. This commit changes no production or harness line those figures read.

## Mutation proof

Four checks were added to `tests/entities.py`, each importing or executing the production artifact: the workflow text, the window step's own shell run in a throwaway repository, and the harness run as a subprocess. At the base, before the fix, the full `tests/entities.py` run printed `4 of 2474 ENTITY CHECKS FAILED`, and they were exactly these four:
- `Nightly's enumerate step is bracketed by its own M0 pair, the after reading under always()`
- `the record job's push arm reads --record alone: --stats, --sunset and the filer wait on the window step's report`
- `the window step reports on the schedule, a dispatch and the stamp, never an ordinary push`
- `record_burst_replay counts demand as record + enumerate + rest, never the record job alone`

Each mutant below was applied to the fixed head, the four checks run, and the file restored. Every mutant changes a predicate, not a tail:
- M-a, the Nightly after-reading step deleted: fails `Nightly's enumerate step is bracketed by its own M0 pair, the after reading under always()`.
- M-b, the histogram's `&& steps.window.outputs.report == 'true'` dropped: fails `the record job's push arm reads --record alone: ...`.
- M-c, the window step's `schedule|workflow_dispatch) REPORT=true ;;` arm deleted: fails `the window step reports on the schedule, a dispatch and the stamp, never an ordinary push`.
- M-d, the stamp's window taken from `HEAD` instead of `HEAD^`: fails `the window step reports on the schedule, a dispatch and the stamp, never an ordinary push`.
- M-e, the replay's `enum = sum(enumerate_cost(...))` replaced by `enum = 0`: fails `record_burst_replay counts demand as record + enumerate + rest, never the record job alone`.
- M-f, the O-1 shape's cost `w` replaced by `w + 3 * p`: fails `record_burst_replay counts demand as record + enumerate + rest, never the record job alone`.

## Null control

- The unmodified tree, at base `88c6ad5bb`: `bash dev/audit/harnesses/record_api_calls.sh v7.0.5` prints `TOTAL 241` per push (`--record` 64, `--stats` 177, `--sunset` 0). At the head the same command prints `TOTAL 64` and `REPORT 177`.
- Empty window, at both base and head: `bash dev/audit/harnesses/record_api_calls.sh origin/main` prints `TOTAL 0` with rc 0, and `python3 dev/audit/harnesses/enumerate_api_calls.py HEAD` prints `ENUMERATE 0 call(s) for 0 merge(s)`.
- The window step, executed against a planted repository (the third check above). An ordinary push gives `report=false`. Push on the stamp, schedule and dispatch each give `report=true`. That ordinary push is the null arm of the stamp arm.
- The replay without the M0 inputs refuses: `record_burst_replay.py v7.0.4 <start> <end>` exits with `the following arguments are required: --rest-per-min, --limit`.
- Carry 3, on this seat (home `/root`, uid 0), `leaks()` from each tree's `ref_privacy.py` under `Identity.of_host()`:
  - At `d074b94b0` (`65ad0e0a3^`), the `ratelimit-recur.md:7` citation line gives `['home-directory']`, the carried defect.
  - At `88c6ad5bb`, the same line gives `[]`.
  - At both, `cd /root/.cache/x` stays `['home-directory']`, so a real path under root's home is still refused.
  - `python3 -I tools/audit/seat/ref_privacy.py --self-test` prints `97 checks, 0 failed` at the base.

## Figures

- The record push arm's calls per push: `bash dev/audit/harnesses/record_api_calls.sh v7.0.5`, at head 64 against base 241, over the window `v7.0.5..origin/main` at `88c6ad5bb`. The rule is the job's own invocations under a logging `curl` stub. The figure moves with every merge and resets at a stamp.
- The enumerate's calls per push: `python3 dev/audit/harnesses/enumerate_api_calls.py v7.0.5` gives 59 calls for 59 merges, the same at base and head. That is one read a merge, M4.
- The replay over the dry hour of `ratelimit-recur.md` section 1.2 (`python3 dev/audit/harnesses/record_burst_replay.py v7.0.4 2026-10-26T04:07:04Z 2026-10-26T05:07:04Z --rest-per-min 18.9 --limit 5000`, with rest and limit read from that record's M0 ledger), at this head over 5 pushes:
  - M1+M2: record 3692 + enumerate 919 + rest 1134 = 5745 of 5000 (114 %).
  - O-1: record 935 + enumerate 919 + rest 1134 = 2988 of 5000 (59 %).
  - Comparing these with the RCA's hand ledger (record 3,691; about 5,740 with M4; about 2,990 with O-1 and M4) cross-checks the harness, not this fix. The base harness, run with the same window and hour, printed the record job alone, `M1+M2   5 run(s), 3692 call(s)`. That was its whole figure for the hour, short by the enumerate's 919 and the rest's 1134.
- The current bucket-hour, from M0: in the `governance / record` log of run 40894146135 (job 123518774781, push `88c6ad5bb`), `RATE_LIMIT before:` reads `used` 297 at 14:43:02Z and `RATE_LIMIT after:` reads 524 at 14:44:53Z, against a `limit` of 5000. That delta of 227 holds this job's `--record`, a `--stats` that stopped at an HTTP 503 on `pulls/2926`, and any concurrent rest. Its filer step went red on that 503. Under O-1 an ordinary push no longer runs the filer.
- The scoped gate: `python3 tests/closure.py select --diff 88c6ad5bb` prints `MODE: FULL`, because `.github/workflows/nightly.yml` changes the gate itself.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

Read at PR head `464daee15` (CI run 40911779633 and pr-contract run 40911780571, read 2026-10-29 at about 17:08Z).

- **`tests / closures`** (job 123581919896): `INERT READS UNDER-APPROXIMATED ... tests/entities.py: dev/audit/harnesses/enumerate_api_calls.py, tests/entities.py: dev/audit/harnesses/record_burst_replay.py`. This pull request caused it: its new `record_burst_replay counts demand ...` check in `tests/entities.py` runs the replay as a subprocess by path, and the replay imports `enumerate_api_calls`. Both files were INERT. Fixed in `0c99dc0e1`: `record_burst_replay.py` joins `INERT_EXCEPT` in `tests/closure.py` (the U5 harnesses' route), and `tests/closures.json` is re-recorded by `./tests/derive_closures.sh --single tests/entities.py` on Linux. The replay is now in entities.py's closure, and `enumerate_api_calls.py`, which only the replay's child reads, is in its `inert_reads`.
  Cheaper detector: one exists, and it was blind to this read. `prepr.sh` step 6d (`tools/pr/ci_predict.py --record-self-tests`) runs in seconds. Re-run at the old head `3122bc41d` against `88c6ad5bb`, it printed `CI PREDICT: no closures, fast, wave-script or instrument red predicted ... (a data-file read is not seen unless a changed file's own self-test makes it)`. Its import arm resolves imports statically, and a harness that a gate script starts with `subprocess` from a `Path("...")` literal is not an import. The detector that does see the read is the local recording itself, `./tests/derive_closures.sh --single tests/entities.py`: about 24 minutes on this seat (18:31:39Z to 18:53:52Z, exit 0), and `--single tests/harness_headers.py` about 4 minutes more, which `ci_predict.py` then named because the replay leaving INERT moves it from that script's `inert_reads` to its closure, against CI's `closures` job plus its autofix and a body round. No countermeasure is built here. A `ci_predict` arm reading the `.py` path literals that a changed gate script passes to `subprocess` is the candidate, and costing it is a root-cause seat's job (`defect-root-cause.md`), not this fix's.
- **`tests / closures-autofix`** (job 123595508827): `AUTOFIX: skip-merge-failed`, because merging CI's recording produced the INERT-and-recorded pair that `closure.py` refuses for `record_burst_replay.py`. Same cause and same fix as `closures`. The bot cannot move a file out of INERT, so this red needed the `INERT_EXCEPT` edit, not a wait. Cheaper detector: as above.
- **`gate`** (job 123601603476): `FAIL tests / closures: failure (run 40911779633)`. It is downstream of `closures` and clears with it. It has no cause of its own.
- **`pr-contract / pr-contract`** (job 123601209706): the body did not name the three reds above or `nightly-status`. This body names them all. Cheaper detector: `prepr.sh` step 7 reads the same contract offline, but only against the reds that exist when it runs. These reds appeared after the handoff, so this body is the answer.
- **`tests / nightly-status`** (job 123581609597): `NIGHTLY FAILED: slow failed in the last verification dispatch`, run 40835853528 (`workflow_dispatch` on `main` at `486e65c`, 2026-10-29T07:30Z), failing step `Closed-loop simulation`: `3 of 33 ROLLING CHECKS FAILED` (`the learner takes samples [0 samples over three days]`, `the learned correction moves towards the real error`, `learning reduces the comfort breach it exists to fix`). **Not this pull request's**, measured four ways:
  1. This diff cannot reach the job that failed. Both `nightly.yml` hunks (`@@ -572,0 +573,14 @@` and `@@ -588,0 +603,9 @@`) fall inside `record-autofix` (lines 541 onward). `slow` spans lines 396 to 469 and is untouched. `governance.yml` is not a Nightly job at all. The checker reads only the concluded runs of `nightly.yml` (`DEFAULT_WORKFLOW`; `grep -c governance tests/nightly_status.py` gives 0). The checker itself runs the base's pinned copy (`git checkout "$PINNED" -- tests/nightly_status.py`), and `tests/nightly_status.py` is not in this diff.
  2. The cause is on `main`, from #2919 (`fix/r10-learner-default`, merged as `994b3dff5`). `PYTHONPATH=tests/hastub python tests/rolling.py` (Python 3.11, numpy 2.4.6, scipy 1.17.1, thread counts 1) prints `ALL 33 ROLLING CHECKS PASSED`, rc 0, at `994b3dff5^1`. At `origin/main` `279578074` it prints `3 of 33 ROLLING CHECKS FAILED`, rc 1, with the same three checks. The scheduled run 40806276912 at `ee4893758`, which predates #2919 (`git merge-base --is-ancestor 994b3dff5 ee4893758` is false), concluded `slow: success`. Owner: the #2919 lane (the learner default in `coordinator.py`, `curve_learning.py` and `thermal_model.py`). Its fix belongs on `main`, outside this pull request.
  3. After landing, the new steps cannot redden `record-autofix`, so they cannot add a nightly-status red. Both are `gh api rate_limit ... || true`. Run under `bash -e`, the step's script returns rc 0 with `gh` absent from `PATH` (`gh: command not found`), and rc 0 with `GH_TOKEN=bogus`. The pin that keeps this true is in this diff. Dropping `|| true` from both steps fails exactly `Nightly's enumerate step is bracketed by its own M0 pair, the after reading under always()` (`1 of 2474 ENTITY CHECKS FAILED`, against `ALL 2474 ENTITY CHECKS PASSED` unmutated, `tests/entities.py` under Python 3.13 at `3122bc41d`).
  4. The red predates this head: the check reported the 07:30Z dispatch, nine hours before CI ran at this head.
  Cheaper detector: for this pull request's own risk, the entities pin in point 3 is that detector. It is local and already in the diff. For the `slow` red, the cheaper detector is `tests/rolling.py` on a pull request whose diff reaches the learner. That is #2919's root-cause question, owed by that lane and not this one.

## Forward-carry

none

## Friction

none
