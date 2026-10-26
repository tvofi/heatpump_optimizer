The root-cause record for R10-HOTFIX-BATCH-ERREXIT, round 2: the answer to fix review `blocked 908237a8c` (`verdict/2849`). It ran beside the hotfix and not inside it: no workflow is edited. The diff is docs plus one read-only instrument: `dev/audit/rca/R10-RCA-HOTFIX-BATCH-ERREXIT.md`, its `_rca` row in `dev/audit/config/bugclasses.json`, the harness `dev/audit/harnesses/r10_errexit_capture.py`, and that harness's INERT entry in `tests/closures.json`.

**Cause, reproduced (round 1, unchanged).** `nightly.yml`'s record-autofix read `batch=$?` after a bare `record_row.py --batch-due`. Under GitHub's default `bash -e`, the designed exit 4 ended the step first (jobs 121376331566 and 121376503388, exit code 4). **State (c):** the barrier `_RAF_BARE_GREEN` ran and passed with a one-call unit, `_raf_batch_gated` pins the dead line's text, and the executed-step harness runs `bash -c` with no `-e`. The hotfix #2848 is now on main as `e0ffb1213`, so countermeasure A's precondition holds.

**Round 2 answers the review.**
- Finding 2, the `$?` read in an `if`/`while` test: fixed in the reference logic (`TEST_HEAD`), failing selftest first, mutation-proved, controls re-taken (below; record section 5 A).
- Finding 3, B's scope: the record now enumerates every `bash -c` over workflow text under `tests/` and `tools/`, 14 sites, each with a disposition (record section 5 B). Running the five sites that lack `-e` under `bash -e -c` found a **4th instance of the class on main**: gate-sweep.yml's `out=$(python3 -I tools/ci/gate.py --sweep ...)` ends the step on any program exit of 1, so a rate limit never prints its `RATE-LIMITED` annotation. `_gs_step_verdict` shows it green only because it runs `bash -c`.
- Finding 4: dismissed by the reviewer, restated under Friction.
- Block 1, carry-missing: not cleared by this seat. R10-HOTFIX-BATCH-ERREXIT is now `done` on the roster branch, so `carry_audit.py` refuses it as a destination (`BAD-DEST ... is done`), and no live group owns the countermeasure. Minting one is the orchestrator's. Forward-carry below holds the exact carry text for it.

## Head

e1a684789f697772a3c533b4263d33ae3ea0c447

Three commits on `origin/main` `f6784210c` (the round-1 head `908237a8c` plus this round's one commit). `origin/main` was at `ed1c9045e` at 2026-10-26T07:15Z, and `git merge-tree --write-tree origin/main HEAD` exits 0, so main was not merged in (`fixer.md` step 6).

## Mutation proof

- Failing test first: the five test-form cases were added to `--selftest` before the fix. `python3 -I dev/audit/harnesses/r10_errexit_capture.py --selftest` printed `selftest: 16 checks, 5 failed ['if test -ne', 'if test quoted', 'if test builtin', 'while test', 'same-line if']`, exit 1. With `TEST_HEAD` it printed `selftest: 16 checks, 0 failed`, exit 0.
- Mutant: deleting the line `stmt = TEST_HEAD.sub("", stmt)` printed the same `16 checks, 5 failed` with the same five names. Restored, `0 failed`.
- On a tree: `ed1c9045e`'s `.github/` with the hotfixed gate rewritten as the bare call then `if [ $? = 4 ]; then batch=4; fi` printed `HIT ... step='Write the rows and push the record branch'` and `hits=1`, exit 1. The round-1 copy of the harness (`908237a8c`) printed `hits=0`, exit 0, on the same tree.
- Mutant of `ed1c9045e`: the guard's `if guard --require-green; then rc=0; else rc=$?; fi` back to `guard --require-green; rc=$?` printed `hits=1`.

## Null control

- `--root` over `ed1c9045e`'s `.github/` (the hotfix landed) printed `RESULT blocks=260`, `RESULT reads=5`, `RESULT hits=0`, exit 0: every `$?` site still read, none a hit.
- An empty `.github/` printed `REFUSED: no errexit run block or no $? read scanned`, `blocks=0 reads=0`, exit 2.
- This head, and `d181d014a`: `hits=1` (the I3 defect), exit 1. Backtest `bc2ad6964^` (I2 live): `hits=1` on tests.yml's `guard --require-green; rc=$?`. Backtest `718c94c84^` (I1 live): `hits=0`, I1's pipeline shape is outside the unit, as record section 6 says.
- B's enumeration control: the `ast` walk and the two `git grep` patterns named in record section 5 B returned the same 14 sites.
- B executed: `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` printed `ALL 2449 ENTITY CHECKS PASSED` on this tree before the commit (the commit after it changes only the record), and `1 of 2449 ENTITY CHECKS FAILED` on a scratch copy of `908237a8c` whose five sites without `-e` were switched to `bash -e -c`. The one is gate-sweep.yml's U0c check, with `defects=` naming the 3 `_GS_CASES` whose program exits 1. The same step run directly with a stub `python3`: `RATE-LIMITED reset_epoch=99`, rc 1 gives step rc 1 and `::error title=RATE-LIMITED` under plain `bash`, step rc 1 and no annotation under `bash -e`; `SWEEP-DONE run=2 reruns=0`, rc 1 gives step rc 0 under `bash` and rc 1 under `bash -e`.
- The scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out` and named `tests/entities.py` (its run is the line above). `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`; `python3 tests/harness_headers.py` printed `ALL 112 HARNESS HEADER CHECKS PASSED`.

## Figures

- Harness results and selftest: `python3 -I dev/audit/harnesses/r10_errexit_capture.py [--root DIR] [--selftest]`, each `--root` a `git archive <sha> .github` copy; taken 2026-10-26T07:15Z.
- B's sites: an `ast` walk over every tracked `.py` under `tests/` and `tools/` for a list literal `["bash"|"sh", ..., "-c", ...]`, crossed with `git grep -n -E '"(ba)?sh",\s*("-[a-z]+",\s*)*"-c"' -- tests tools` and `git grep -n '\["bash", "--noprofile"' -- tests tools`.
- Entity check counts: `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`, on this tree and on the `-e` copy. Under the seat profile's `BASH_ENV` both trees printed `2 of 2449 ENTITY CHECKS FAILED` (gate-sweep U0c and graders-head-copy's delivery_status, the known BASH_ENV friction), so the comparison was re-taken without it.
- `tests/arch_score.py`'s `base_runs_the_gate`, called alone (the whole script's calibration outran the seat's time limit) with `BASH_ENV` unset: both checks it holds printed `ok` on this tree and on the `-e` copy.
- Every other figure is round 1's, unchanged, with its command in the record.

## Red checks

The new head has no check runs yet (`commits/e1a684789/check-runs` answers 422, no such commit on GitHub before the push). The round-1 head `908237a8c`, this head's parent, carries four reds, all GitHub installation rate limits read from their job logs, none reached by this diff:

- `prelude` 121398617873 (04:52:40Z) and `gate` 121404488173 (04:52:59Z) and `gate` 121408083256 (05:06:52Z): `RATE-LIMITED reset_epoch=1792991224`, exit code 3, from `tools/ci/prelude.py`'s and `tools/ci/gate.py`'s own rate-limit arm. The cheaper detector exists and fired: the arm names the limit instead of crashing. The recurrence of this red is R10-RCA-RATELIMIT-RECUR's (in progress), not this record's.
- `pr-contract / pr-contract` 121407967543 (05:06:28Z): `gh: API rate limit exceeded for installation ... (HTTP 403)`, exit 1. The same limit; same owner.

## Forward-carry

- **Countermeasure A, B and the class (record section 5), plus the gate-sweep instance, for a group the orchestrator mints.** The exact carry text: "From #2849 (R10-RCA-HOTFIX-BATCH-ERREXIT). (1) Land countermeasure A: a tree-wide check over every errexit `run:` block (default shell, `bash`, `sh`) that refuses a `$?` read whose producer is a bare simple command, including a read in an `if`/`while`/`until` test, replacing `_RAF_BARE_GREEN`; reference logic and selftest are `dev/audit/harnesses/r10_errexit_capture.py` at e1a684789. Precondition: the hotfix line is on main (#2848, e0ffb1213), met. Control: at main the harness prints `blocks=260 reads=5 hits=0`, exit 0; on `d181d014a` `hits=1`, exit 1; on an empty `.github/` `REFUSED`, exit 2; re-measure with `python3 -I dev/audit/harnesses/r10_errexit_capture.py --root <tree>`. Its own mutation proof is owed by the landing fixer. Gap: A does not see a producer read through `out=$(...)`. (2) Fix gate-sweep.yml's sweep step: `out=$(python3 -I tools/ci/gate.py --sweep ...)` under the default `bash -e` ends the step on any program exit of 1 before `case` reads the outcome, so `RATE-LIMITED` prints no annotation and `SWEEP-DONE`, rc 1 is red. Fix the step (`|| true` or a condition form) and switch `tests/entities.py` `_gs_step_verdict` to `bash -e -c`; failing test first: that switch alone fails the U0c check on 3 cases. (3) Countermeasure B: switch `_train_hold_status`, `_pt_trigger`, `_cov_trust`, `_cov_marker` (`tests/entities.py`) and `tests/arch_score.py` `base_runs_the_gate` to `bash -e -c`; under `BASH_ENV` unset, all of them except `_gs_step_verdict` stayed green with `-e` on `tests/entities.py` (`tests/arch_score.py`'s `base_runs_the_gate` too). (4) Class proposal: a workflow step's meaningful nonzero exit ended by errexit before the step reads it, I1 to I4 as `non_round_instances`, the judge's or orchestrator's to mint." Carry: R10-HOTFIX-BATCH-ERREXIT (the verdict's destination; `carry_audit.py` refuses it as `done`, and the live destination is the orchestrator's to mint)
- Finding 4 of the round-1 review, `ref_privacy.py --check` refusing on the reviewing host's identity. Carry: dismissed: instrument behaviour on a root-account host, not a host path in this diff; the added-line grep is clean

## Friction

- brief: stale: the round-2 brief routes the carry to R10-HOTFIX-BATCH-ERREXIT's roster carry, but that group is `done`, so `carry_audit.py` refuses it as a destination and no live group owns the countermeasure. Carry: dismissed: the orchestrator mints the destination, recorded under Forward-carry
