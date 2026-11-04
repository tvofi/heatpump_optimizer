R10-HOTFIX-GATE-STALE-JOBS, repair round 2 of #3205. `tools/ci/gate.py` published red verdicts for jobs that had already finished, because it read them from a stale Actions jobs listing.

**Cause.** The jobs listing lags the run graph. The ordering is sound: `gate` needs `prelude` and `pr-contract`, and `pr-contract` needs every unit. So by the time `gate` starts, every job it reads as unfinished (or does not see at all) has finished. The independent RCA seat measured this on handoff-wip/r10-rca-gate-stale (`dev/audit/rca/r10-gate-stale-jobs.md` at `9b0df6105`): 14 false reds over 8 days. Round 1's re-read matched only own `PENDING`, which covered 3 of the 14. The other 11 were `FAIL prelude: None` (10, from the prelude check in `gate()`) and own `ABSENT` (1).

**Fix (round 2).** Round 1's `lagging()` becomes `lag_bound(why)`. It returns the number of seconds `judge()` may keep re-reading, and 0 unless **every** reason is this run's own listing-lag reason:
- own `PENDING (this run)`: up to `GATE_WAIT_MAX_S` (720 s), as in round 1;
- **a prelude listed but unfinished**. `read_api` now passes the prelude job's `status` along with its `conclusion`, and `gate()` writes `prelude: PENDING (this run)` only when the prelude is listed with a status other than `completed`. That reason shares the 720 s bound. A prelude that is not listed at all still reads `prelude: None` and gets no wait;
- **own `ABSENT (this run)`**: up to the shorter `GATE_ABSENT_MAX_S` = 2 x `POLL_S` (120 s). Its one measured lag is 20 s. A structural absence, such as a renamed job, is absent on every run, so its wait is kept short.

What round 1 built is kept: a lagging job never reads as success, so an exhausted bound still FAILs; any other reason beside a lag reason (a real failure, a skip, a deferral mix) is published at once, with no wait. One addition: a cleared lag leaves a step-summary note, `listing lag: <first reason> re-read for <n> s`. This is the RCA's countermeasure 4, so the next incident cluster leaves a record. The 10-30 cluster left none.

**The bound.** I kept `GATE_WAIT_MAX_S` at 720. With 60 s polls the last read lands at exactly 720 s, so the measured 704 s prelude lag (41876634563, a lower bound) clears at that read: harness shape 3 passes, having waited 720 s. A longer bound does not fit the job. `ci.yml`'s `gate` has `timeout-minutes: 15`, and the self-test pins `GATE_WAIT_MAX_S + POLL_S + 120 <= 900`. Raising the timeout would change the pinned `ci.yml` graph to cover lags longer than any measured. A lag past 720 s stays a FAIL, which is safe: gate-sweep re-judges it. The RCA also advises against widening the bound on these numbers.

**ABSENT null (workset).** Own `ABSENT` is written only when a unit is in this run's own workset and its job is missing from the listing. A unit outside the workset never reaches that line: `gate()` skips the run as a source and writes `<unit>: no run at this head judged base ...`, which is not a lag reason. Self-test `null (workset): an edit run lists no code unit; that is no ABSENT and no wait` drives that case through `judge()`: an `edited` event, a body-only listing, no other run. It asserts no `ABSENT` reason and `naps == []`.

Alternatives, and why each lost:
- Treat an own unfinished or unlisted job as passed, since its needs ran it. Unsound: 3 of the 6 PENDING-only attempts hid a real failure (RCA section 3), and the 41094975103 shape (prelude really failed) would pass.
- Wait on an unlisted prelude too. The brief rules this out: an unlisted prelude is not "listed unfinished". Keeping `prelude: None` for it leaves the cross-check's meaning unchanged.
- One bound for ABSENT and PENDING. A structural ABSENT would then cost 12 min on every run (RCA countermeasure 3). The mutant `M4` below shows the self-test pins the split.
- Another endpoint (`GET /actions/jobs/<id>`, check-runs). The RCA could not measure that either is fresher, so it would be an unverified assumption.

Roster carries on this group, each answered:
- Carry 1 (e67341cc, prelude None and own ABSENT not re-read): closed in this diff. `lag_bound` covers a prelude listed unfinished and own ABSENT; finder's harness 0 of 9 mismatches at the head (Null control).
- Carry 2 (e350d851, `codescan_wait.py` own-run path): read here, not measured; carried on in `## Forward-carry`, first item.
- Carry 3 (d0916ca4, `pr-contract.yml` red list): read here, not measured; carried on in `## Forward-carry`, second item.

## Head

bc806747bfd242e61d728b6784ab36d742193bd9, which is round 1's head e102db7b7ac0eb7510d2b853ee86dd1ee49a1c4e plus one commit, on base d7582ed404a87603bd02fefda610d7ebbe4181e1 (`origin/main` at 2026-11-04T18:41:50Z). Main had not moved at the last `prepr.sh` run, so the run was not repeated.

## Mutation proof

Each mutant is a one-line Python replace in `tools/ci/gate.py`. For each, I ran `python3 -I tools/ci/gate.py --self-test` and the finder's harness, then restored the file. The restored tree reads `gate self-test: 48 checks, 0 failed` and `mismatches 0 of 9`.
- M1, own ABSENT not a lag reason (`endswith((OWN_PENDING,))`). Self-test 2 failed: `a run without tests / arch-instrument (U5b): re-read, inside the ABSENT bound, then red` and `41289450679 shape: an own job not yet listed, then listed -> one re-read, PASS`. Harness: `mismatches 1 of 9`.
- M2, prelude predicate deleted (`listed_unfinished = False`). Self-test 2 failed: `41863133083 shape: prelude listed unfinished, then success -> one re-read, PASS` and `41094975103 shape: prelude listed unfinished, then failure -> its true reason, after the re-read`. Harness: `mismatches 2 of 9`.
- M3, `read_api` drops the prelude status (`"status": None`). The same 2 self-test checks fail. Harness: `mismatches 2 of 9`.
- M4, ABSENT shares the long bound (`return GATE_WAIT_MAX_S`). Self-test 2 failed: `a run without tests / arch-instrument (U5b)...` and `an own job never listed stays red, its wait inside the shorter ABSENT bound`. Harness: `mismatches 0 of 9`, because no harness shape is a never-listed job.

Failing test first: I committed the new checks with only the constant defined. Against round 1's production code they read `gate self-test: 47 checks, 4 failed` (the U5b ABSENT check, the 41863133083 and 41094975103 prelude shapes, and the 41289450679 ABSENT shape).

`tools/` sites are outside `mutation-autofix`'s lane. The in-tree mutant harness is the self-test above plus `dev/audit/harnesses/r10_ci_gate_core.py mutants`.

## Null control

Finder's harness: the RCA seat's `dev/audit/harnesses/r10_gate_stale_jobs/harness.py` from `$EXPORT` = ref handoff-wip/r10-rca-gate-stale at `9b0df6105c67a009bce09feea9f4dffe8079a86a`, sha1 `7527a4832039d125950b8f07e1b2d931a6ef874c`. It is not landed here; that seat lands it. Run as `python3 -I harness.py <tree with tools/ci>`:

| shape | want | main d7582ed40 | r1 e102db7b7 | head bc806747b |
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

Mismatches: main 4 of 9 (rc 1), r1 3 of 9 (rc 1), head 0 of 9 (rc 0). The two fresh-listing nulls wait 0 s at all three trees, so the head neither fires on a healthy listing nor passes a real red. Self-test nulls at the head, each with `naps == []`: an unlisted prelude stays `FAIL prelude: None`; the workset case above; a real failure beside a lagging job; a skipped own unit. The cleared-lag note is absent on a fresh listing.

## Figures

- `python3 -I tools/ci/gate.py --self-test`: `gate self-test: 48 checks, 0 failed` at the head. At round 1's production code with the new checks: `47 checks, 4 failed`.
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
