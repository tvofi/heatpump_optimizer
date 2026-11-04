R10-HOTFIX-GATE-STALE-JOBS, repair round 3 of #3205 (body re-taken). `tools/ci/gate.py` published red verdicts for jobs that had already finished, because it read them from a stale Actions jobs listing.

**Cause.** The jobs listing lags the run graph. The ordering is sound: `gate` needs `prelude` and `pr-contract`, and `pr-contract` needs every unit. So by the time `gate` starts, every job it reads as unfinished (or does not see at all) has finished. The independent RCA seat measured this on handoff-wip/r10-rca-gate-stale (`dev/audit/rca/r10-gate-stale-jobs.md` at `9b0df6105`): 14 false reds over 8 days. Round 1's re-read matched only own `PENDING`, which covered 3 of the 14. The other 11 were `FAIL prelude: None` (10, from the prelude check in `gate()`) and own `ABSENT` (1).

**Fix (round 2).** Round 1's `lagging()` becomes `lag_bound(why)`. It returns the number of seconds `judge()` may keep re-reading, and 0 unless **every** reason is this run's own listing-lag reason:
- own `PENDING (this run)`: up to `GATE_WAIT_MAX_S` (720 s), as in round 1;
- **a prelude listed but unfinished**. `read_api` now passes the prelude job's `status` along with its `conclusion`, and `gate()` writes `prelude: PENDING (this run)` only when the prelude is listed with a status other than `completed`. That reason shares the 720 s bound. A prelude that is not listed at all still reads `prelude: None` and gets no wait;
- **own `ABSENT (this run)`**: up to the shorter `GATE_ABSENT_MAX_S` = 2 x `POLL_S` (120 s). Its one measured lag is 20 s. A structural absence, such as a renamed job, is absent on every run, so its wait is kept short.

What round 1 built is kept: a lagging job never reads as success, so an exhausted bound still FAILs; any other reason beside a lag reason (a real failure, a skip, a deferral mix) is published at once, with no wait. One addition: a cleared lag leaves a step-summary note, `listing lag: <first reason> re-read for <n> s`. This is the RCA's countermeasure 4, so the next incident cluster leaves a record. The 10-30 cluster left none.

**The bound.** I kept `GATE_WAIT_MAX_S` at 720. With 60 s polls the last read lands at exactly 720 s, so the measured 704 s prelude lag (41876634563, a lower bound) clears at that read: harness shape 3 passes, having waited 720 s. A longer bound does not fit the job. `ci.yml`'s `gate` has `timeout-minutes: 15`, and the self-test pins `GATE_WAIT_MAX_S + POLL_S + 120 <= 900`. Raising the timeout would change the pinned `ci.yml` graph to cover lags longer than any measured. A lag past 720 s stays a FAIL, which is safe: gate-sweep re-judges it. The RCA also advises against widening the bound on these numbers.

**ABSENT null (workset).** Own `ABSENT` is written only when a unit is in this run's own workset and its job is missing from the listing. A unit outside the workset never reaches that line: `gate()` skips the run as a source and writes `<unit>: no run at this head judged base ...`, which is not a lag reason. Self-test `null (workset): an edit run lists no code unit; that is no ABSENT and no wait` drives that case through `judge()`: an `edited` event, a body-only listing, no other run. It asserts no `ABSENT` reason and `naps == []`.

**Prelude disposition (root-cause constraint 3).** A prelude listed unfinished waits: `prelude: PENDING (this run)` shares the 720 s bound, and a prelude that really failed reads `FAIL prelude: failure` after the re-read (41094975103 shape). An unlisted prelude stays `FAIL prelude: None` with no wait, since it is not a lag reason; the self-test null `prelude not listed at all is no lag, no wait` pins it.

Alternatives, and why each lost:
- Treat an own unfinished or unlisted job as passed, since its needs ran it. Unsound: 3 of the 6 PENDING-only attempts hid a real failure (RCA section 3), and the 41094975103 shape (prelude really failed) would pass.
- Wait on an unlisted prelude too. The brief rules this out: an unlisted prelude is not "listed unfinished". Keeping `prelude: None` for it leaves the cross-check's meaning unchanged.
- One bound for ABSENT and PENDING (round 1 rejected a separate shorter bound; the head now adds one, `GATE_ABSENT_MAX_S = 2 * POLL_S`, for own-ABSENT only, because the RCA measured a 20 s ABSENT lag against a structural ABSENT, such as a renamed job, that is absent on every run and would otherwise cost 12 min on every run; RCA countermeasure 3). The self-test now pins the split: the mutant `ABSENT bound = WAIT bound` is killed (Mutation proof).
- Another endpoint (`GET /actions/jobs/<id>`, check-runs). The RCA could not measure that either is fresher, so it would be an unverified assumption.

Roster carries on this group, each answered:
- Carry 1 (e67341cc, prelude None and own ABSENT not re-read): closed in this diff. `lag_bound` covers a prelude listed unfinished and own ABSENT; finder's harness 0 of 9 mismatches at the head (Null control).
- Carry 2 (e350d851, `codescan_wait.py` own-run path): read here, not measured; carried on in `## Forward-carry`, first item.
- Carry 3 (d0916ca4, `pr-contract.yml` red list): read here, not measured; carried on in `## Forward-carry`, second item.

## Head

5e1e16a64f65fa2b7760902fdf316f9c45d760d0: the authored code head bc806747bfd242e61d728b6784ab36d742193bd9, a merge of origin/main 2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e (the PR head 6e1e8023d merged d1e7dbbbb), and one commit that pins the ABSENT bound in the self-test. origin/main was 2a9cd3476 when I last ran `tools/pr/prepr.sh` on this head (rc 0, body check run with this body below); it had not moved after.

## Mutation proof

Round 2 retaken against `lag_bound()` in the head's `tools/ci/gate.py`. Each mutant is a one-line `sed` replace, `python3 -I tools/ci/gate.py --self-test` run, file restored after (restored: `gate self-test: 49 checks, 0 failed`). Killed means the named checks go red:
- `lag_bound` body `return 0` (the `if not why or not all(...)` line made `if True:`): 8 failed, among them `run 41870314676 shape: own jobs read in_progress, then completed -> one re-read, PASS`, `41863133083 shape: prelude listed unfinished, then success -> one re-read, PASS`, `41289450679 shape: an own job not yet listed, then listed -> one re-read, PASS`, `an own job never listed stays red, its wait inside the shorter ABSENT bound`. Killed.
- `all(` to `any(` in `lag_bound`: 1 failed, `null: a unit really failed beside a lagging one stays red, no wait`. Killed.
- `GATE_ABSENT_MAX_S = GATE_WAIT_MAX_S`: 1 failed, `the ABSENT bound is shorter than the pending bound, and pinned to two polls` (got (False, 720), want (True, 120)). This mutant survived 48 of 48 checks before this round, because the two checks that claim "inside the shorter ABSENT bound" assert `<= GATE_ABSENT_MAX_S`, which moves with the constant. Failing test first: the new check was added alone; the mutant read `49 checks, 1 failed`, the unmutated tree `49 checks, 0 failed`. Killed.
- `listed_unfinished = False` in `gate()`: 2 failed, `41863133083 shape...` and `41094975103 shape: prelude listed unfinished, then failure -> its true reason, after the re-read`. Killed.
- `listed_unfinished = True` (an unlisted prelude waits): 2 failed, `41094975103 shape...` and `null: prelude not listed at all is no lag, no wait (only a listed unfinished prelude waits)`. Killed.
- `bound = 0` in `judge()` (no wait of any kind): 14 failed. Killed.
- Equivalent, no action: forcing the `src is not me` conditional in `gate()` either way yields identical text, because `where` is "this run" when `src is me`; the conditionals are redundant, not a defect.

Null control for the mutation proof: the unmutated tree, same command, `gate self-test: 49 checks, 0 failed` before and after every mutant.

`tools/` sites are outside `mutation-autofix`'s lane. The in-tree mutant harness is the self-test above plus `dev/audit/harnesses/r10_ci_gate_core.py mutants`.

## Null control

Finder's harness: the RCA seat's `dev/audit/harnesses/r10_gate_stale_jobs/harness.py` from `$EXPORT` = ref handoff-wip/r10-rca-gate-stale at `9b0df6105c67a009bce09feea9f4dffe8079a86a`, sha1 `7527a4832039d125950b8f07e1b2d931a6ef874c`. It is not landed here; that seat lands it. Run as `python3 -I harness.py <tree with tools/ci>`:

| shape | want | main d7582ed40 | r1 e102db7b7 | head bc806747b (5e1e16a64 reruns identically) |
|---|---|---|---|---|
| 41870314676 proof, stale 285/181 s | PASS | FAIL PENDING | PASS, 300 s | PASS, 300 s |
| 41870522291, real red hidden | FAIL | FAIL, wrong reason | FAIL `failure`, 180 s | FAIL `failure`, 180 s |
| 41876634563 prelude stale 704 s | PASS | FAIL `prelude: None` | FAIL `prelude: None` | PASS, 720 s |
| 41863133083 prelude stale 134 s | PASS | FAIL `prelude: None` | FAIL `prelude: None` | PASS, 180 s |
| 41094975103 prelude really failed | FAIL | FAIL, wrong reason | FAIL, wrong reason | FAIL `prelude: failure`, 360 s |
| 41289450679 pr-contract absent 20 s | PASS | FAIL ABSENT | FAIL ABSENT | PASS, 60 s |
| past the bound, stale 800 s | FAIL | FAIL, 0 s | FAIL, 720 s | FAIL, 720 s |
| null: fresh listing | PASS | PASS, 0 s | PASS, 0 s | PASS, 0 s |
| null: real red, fresh listing | FAIL | FAIL, 0 s | FAIL, 0 s | FAIL, 0 s |

Mismatches: main 4 of 9 (rc 1; origin/main 2a9cd3476 re-run in round 2 also 4 of 9), r1 3 of 9 (rc 1), head 0 of 9 (rc 0; re-run at 5e1e16a64 also 0 of 9). The two fresh-listing nulls wait 0 s at all three trees, so the head neither fires on a healthy listing nor passes a real red. Self-test nulls at the head, each with `naps == []`: an unlisted prelude stays `FAIL prelude: None`; the workset case above; a real failure beside a lagging job; a skipped own unit. The cleared-lag note is absent on a fresh listing.

## Figures

- `python3 -I tools/ci/gate.py --self-test`: `gate self-test: 49 checks, 0 failed` at the head (48 at bc806747b, plus the ABSENT pin). At round 1's production code with round 2's checks: `47 checks, 4 failed`.
- `python3 -I $EXPORT/dev/audit/harnesses/r10_gate_stale_jobs/harness.py <tree>`: the table above, per tree (`git archive <sha> tools/ci`).
- `python3 dev/audit/harnesses/r10_ci_gate_core.py replay`: `GATE-REPLAY2 rc 0`, output IDENTICAL to `1371a0a6:measure/rev/gate_replay2.txt`. This is the null for every scenario the design replays.
- `python3 dev/audit/harnesses/r10_ci_gate_core.py mutants`: `RESULT mutants=16 survivors=0`.
- `python3 dev/audit/harnesses/r10_ci_gate_core.py sim`: `GATE-SIM rc 0`, output IDENTICAL to `1371a0a6:measure/rev/gate_sim.txt`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff <merge-base>`: `MODE: FULL`, reason `tools/ci/gate.py changes the gate itself`. Left to CI per `fixer.md` step 5.

## Red checks

At the PR head 6e1e8023d the only concluded red was `tests / nightly-status`, read by the fix reviewer's `merge_train.py classify` as main-inherited: it reports the nightly lane's state, is in no `REQUIRED` class, `gate` reports it as "Not gating", and this diff (`tools/ci/gate.py`, `dev/programme/delivery/3205.md`) does not reach what it reads. This head, 5e1e16a64, has not run CI yet, so no concluded check exists at it; the set is re-read when it does. The defect itself turned PR heads and train proofs red on `gate` (14 false reds, RCA section 3); the RCA seat answered the trigger: no cheaper detector exists, because the lag exists only at read time on the live service. This PR adds the noticing line in its place (RCA countermeasure 4).

## Forward-carry`, first item.
- Carry 3 (d0916ca4, `pr-contract.yml` red list): read here, not measured; carried on in `## Forward-carry`, second item.

## Head

5e1e16a64f65fa2b7760902fdf316f9c45d760d0: the authored code head bc806747bfd242e61d728b6784ab36d742193bd9, a merge of origin/main 2a9cd3476dae9f45d3091b546fdd2723bcb0ce4e (the PR head 6e1e8023d merged d1e7dbbbb), and one commit that pins the ABSENT bound in the self-test. origin/main was 2a9cd3476 when I last ran `tools/pr/prepr.sh` on this head (rc 0, body check run with this body below); it had not moved after.

## Mutation proof

Round 2 retaken against `lag_bound()` in the head's `tools/ci/gate.py`. Each mutant is a one-line `sed` replace, `python3 -I tools/ci/gate.py --self-test` run, file restored after (restored: `gate self-test: 49 checks, 0 failed`). Killed means the named checks go red:
- `lag_bound` body `return 0` (the `if not why or not all(...)` line made `if True:`): 8 failed, among them `run 41870314676 shape: own jobs read in_progress, then completed -> one re-read, PASS`, `41863133083 shape: prelude listed unfinished, then success -> one re-read, PASS`, `41289450679 shape: an own job not yet listed, then listed -> one re-read, PASS`, `an own job never listed stays red, its wait inside the shorter ABSENT bound`. Killed.
- `all(` to `any(` in `lag_bound`: 1 failed, `null: a unit really failed beside a lagging one stays red, no wait`. Killed.
- `GATE_ABSENT_MAX_S = GATE_WAIT_MAX_S`: 1 failed, `the ABSENT bound is shorter than the pending bound, and pinned to two polls` (got (False, 720), want (True, 120)). This mutant survived 48 of 48 checks before this round, because the two checks that claim "inside the shorter ABSENT bound" assert `<= GATE_ABSENT_MAX_S`, which moves with the constant. Failing test first: the new check was added alone; the mutant read `49 checks, 1 failed`, the unmutated tree `49 checks, 0 failed`. Killed.
- `listed_unfinished = False` in `gate()`: 2 failed, `41863133083 shape...` and `41094975103 shape: prelude listed unfinished, then failure -> its true reason, after the re-read`. Killed.
- `listed_unfinished = True` (an unlisted prelude waits): 2 failed, `41094975103 shape...` and `null: prelude not listed at all is no lag, no wait (only a listed unfinished prelude waits)`. Killed.
- `bound = 0` in `judge()` (no wait of any kind): 14 failed. Killed.
- Equivalent, no action: forcing the `src is not me` conditional in `gate()` either way yields identical text, because `where` is "this run" when `src is me`; the conditionals are redundant, not a defect.

Null control for the mutation proof: the unmutated tree, same command, `gate self-test: 49 checks, 0 failed` before and after every mutant.

`tools/` sites are outside `mutation-autofix`'s lane. The in-tree mutant harness is the self-test above plus `dev/audit/harnesses/r10_ci_gate_core.py mutants`.

## Null control

Finder's harness: the RCA seat's `dev/audit/harnesses/r10_gate_stale_jobs/harness.py` from `$EXPORT` = ref handoff-wip/r10-rca-gate-stale at `9b0df6105c67a009bce09feea9f4dffe8079a86a`, sha1 `7527a4832039d125950b8f07e1b2d931a6ef874c`. It is not landed here; that seat lands it. Run as `python3 -I harness.py <tree with tools/ci>`:

| shape | want | main d7582ed40 | r1 e102db7b7 | head bc806747b (5e1e16a64 reruns identically) |
|---|---|---|---|---|
| 41870314676 proof, stale 285/181 s | PASS | FAIL PENDING | PASS, 300 s | PASS, 300 s |
| 41870522291, real red hidden | FAIL | FAIL, wrong reason | FAIL `failure`, 180 s | FAIL `failure`, 180 s |
| 41876634563 prelude stale 704 s | PASS | FAIL `prelude: None` | FAIL `prelude: None` | PASS, 720 s |
| 41863133083 prelude stale 134 s | PASS | FAIL `prelude: None` | FAIL `prelude: None` | PASS, 180 s |
| 41094975103 prelude really failed | FAIL | FAIL, wrong reason | FAIL, wrong reason | FAIL `prelude: failure`, 360 s |
| 41289450679 pr-contract absent 20 s | PASS | FAIL ABSENT | FAIL ABSENT | PASS, 60 s |
| past the bound, stale 800 s | FAIL | FAIL, 0 s | FAIL, 720 s | FAIL, 720 s |
| null: fresh listing | PASS | PASS, 0 s | PASS, 0 s | PASS, 0 s |
| null: real red, fresh listing | FAIL | FAIL, 0 s | FAIL, 0 s | FAIL, 0 s |

Mismatches: main 4 of 9 (rc 1; origin/main 2a9cd3476 re-run in round 2 also 4 of 9), r1 3 of 9 (rc 1), head 0 of 9 (rc 0; re-run at 5e1e16a64 also 0 of 9). The two fresh-listing nulls wait 0 s at all three trees, so the head neither fires on a healthy listing nor passes a real red. Self-test nulls at the head, each with `naps == []`: an unlisted prelude stays `FAIL prelude: None`; the workset case above; a real failure beside a lagging job; a skipped own unit. The cleared-lag note is absent on a fresh listing.

## Figures

- `python3 -I tools/ci/gate.py --self-test`: `gate self-test: 49 checks, 0 failed` at the head (48 at bc806747b, plus the ABSENT pin). At round 1's production code with round 2's checks: `47 checks, 4 failed`.
- `python3 -I $EXPORT/dev/audit/harnesses/r10_gate_stale_jobs/harness.py <tree>`: the table above, per tree (`git archive <sha> tools/ci`).
- `python3 dev/audit/harnesses/r10_ci_gate_core.py replay`: `GATE-REPLAY2 rc 0`, output IDENTICAL to `1371a0a6:measure/rev/gate_replay2.txt`. This is the null for every scenario the design replays.
- `python3 dev/audit/harnesses/r10_ci_gate_core.py mutants`: `RESULT mutants=16 survivors=0`.
- `python3 dev/audit/harnesses/r10_ci_gate_core.py sim`: `GATE-SIM rc 0`, output IDENTICAL to `1371a0a6:measure/rev/gate_sim.txt`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff <merge-base>`: `MODE: FULL`, reason `tools/ci/gate.py changes the gate itself`. Left to CI per `fixer.md` step 5.

## Red checks

- `tests / nightly-status` (failure on run 41887769752, round 1's head). It reports the nightly lane's state, is in no `REQUIRED` class, and `gate` reports it as "Not gating". This diff does not touch it, and it does not trigger the root-cause rule.
- The defect itself turned PR heads and train proofs red on `gate` (14 false reds, RCA section 3). The trigger's question was answered by the RCA seat: no cheaper detector exists, because the lag exists only at read time on the live service. This PR adds the noticing line in its place (RCA countermeasure 4).

## Forward-carry

- `tools/ci/codescan_wait.py` `source()`, own-run path: when this run owns codeql it returns `_jobs()` at once, with no poll, and `legs_uploaded()` then keeps only legs whose upload step is listed `success`. A stale step row would read as "stood down", and that leg's analysis would be neither waited for nor read, so the check may fail open. I read this in the code; it is unmeasured (RCA section 3). The next step is to measure step rows inside the three incident windows before anything is built. The roster brief write is the orchestrator's; this seat may push only its return refs. Carry: R10-FLY-GH-READ-RETRY
- `.github/workflows/pr-contract.yml`, step "List the red checks at this head": it keeps only `status == "completed" and conclusion == "failure"` check runs, so a red that is still lagging is left off the list the body must answer, and the check may fail open. I read this in the code; it is unmeasured, and the next step is the same measurement as above. Carry: R10-FLY-GH-READ-RETRY

## Friction

none
