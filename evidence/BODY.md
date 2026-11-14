Hotfix for the tick loop's self-test, which read and could move the checkout it was run from. `tools/audit/seat/tick_loop.sh --self-test` ran its first rows (the TICK-GH rows) before pointing `HPO_TICK_CODE_DIR` at scratch, so those rows ran the freshness check on the caller's checkout: on a branch checkout behind origin/main on the watched paths one row printed an extra `TICK-STALE` line and failed, and on a detached checkout behind origin/main the restart arm checked out origin/main in the caller's checkout. `ci_predict.py` then predicted `governance / instrument-self-tests` red on an unrelated group's handoff whenever origin/main moved during its `prepr.sh` run (R10-PROCESS-SLIM part 2, PR #3451; evidence in `BLOCKED.md` at handoff-wip/r10-process-slim-p2, 1b45b89b9abfb4313cf661cf4c6712b5a51a86fa).

The fix is in the self-test alone; the loop's production lines are unchanged. Three things in the caller's environment reached a row, and each is closed where it entered; a fourth defect, found while proving these, made any row fail at random under load:

- **The checkout the script lives in.** `HPO_TICK_CODE_DIR` is exported at scratch before the first row (the earlier seat's commit 1fba05ec35). Every row but the freshness rows, which name their own clone, runs from a directory that is no checkout.
- **A repository named by the environment.** `GIT_DIR` outranks `git -C`, so with `GIT_DIR` and `GIT_WORK_TREE` exported (a git hook's environment) the rows before `throwaway_git_env` still ran the freshness check on the named checkout, whatever `HPO_TICK_CODE_DIR` said, and detached it. `throwaway_git_env` now runs before the first row.
- **The caller's `gh`.** The row "a seat bin dir with no gh shim" took whichever `gh` the caller's PATH held and expects it not to be the shim. The script puts `$HPO_STATE_DIR/bin` first on PATH before the self-test starts, and on a live seat that directory holds the shim, so the row failed on every seat host and the self-test could not be green there at all. The row now leads its PATH with a plain `gh` of its own.
- **A row's verdict under pipefail.** The script sets `pipefail`, and a row is `printf '%s\n' "$out" | grep -q ...`. A `grep -q` that leaves at its match can kill the `printf` feeding it (141), and the row then reads a match as none. This is `prepr.sh`'s own `PIPE_GREP_Q_FILES` class (R9-RCA-prepr-tmp), which `tick_loop.sh` was never drained of. Captured on this host under load: the row "null control: a refused push is printed with its reason and the pass still completes" printed FAIL while its output held both lines it greps for (`HEARTBEAT NOT PUSHED: ` and `tick=0`). It matters here because the self-test now runs itself four more times, so a stray FAIL is that much likelier per run. The self-test's subshell turns `pipefail` off; the loop keeps it.

Four rows pin it by running the whole self-test from throwaway clones: a branch clone behind origin/main, a detached clone behind, a detached clone behind named by `GIT_DIR`/`GIT_WORK_TREE`, and a branch clone at origin/main (the null control, which asserts its own behind=0 premise). Each asserts the nested tally is `0 failed` and that the clone's HEAD did not move; each runs under a state dir whose bin holds the shim, as a live seat does; a failing nested row is named on a `nested FAIL` line above its row.

Alternatives, and why each lost. A guard in `fresh_check` that refuses to move a checkout outside a self-test root would put test awareness into the production restart path. Skipping the freshness check when run from a branch would hide the read and leave the detached shape. Restricting the nested runs to the rows above the freshness rows would presume which rows can reach the caller, which is the mistake being fixed. `dev/audit/harnesses/r10_tick_selftest_checkout.sh` lands the reproducer (fixer step 18): it runs a rev's self-test from throwaway clones and from a scratch copy with each guard taken back out, never in the caller's checkout. The in-tree mutant harness `r10_seat_selftests_mutants.py` is not used for these mutants: it mutates the committed file in place and runs the step from the checkout, and these mutants are the ones that move a checkout.

Cost: the self-test now runs itself four more times. On this host, under a load average near 40, the whole self-test took 103 and 96 s; CI's step took 7 s and 13 s in the two most recent scheduled `governance` runs on main (job step "Show the tick loop refusing its own fixtures"), so about five times that is expected there.

Off Linux, scoped closure recordings are left to CI (`gate-scoping.md`): no `tests/derive_closures.sh` was run on this macOS host. The one closures edit is the inert-read entry for the new harness, written by `python3 tools/pr/ci_predict.py --apply-inert`.

## Head

81ea9ea2908ea83a012e3e42d694df56bb097c8c, merge base 8c10361eb1fea539dc5acb8f7442eac2810faa47. origin/main was at 43e95474559ca8e2188830f8775c1ddf52df964a at 2026-11-12T18:00:15Z, ahead of the merge base; `git merge-tree --write-tree origin/main HEAD` reports no conflict and `tests/closures.json` merges textually (`git merge-file` rc 0), so per `fixer.md` step 6 it is not merged in. None of the four files the self-test reads (`tick_loop.sh`, `heartbeat.sh`, `ref_privacy.py`, `tests/throwaway_git.sh`) differs between the merge base and that tip.

## Mutation proof

Each guard taken back out of the head's `tick_loop.sh`, the whole self-test run from a scratch copy: `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh 81ea9ea290 whole nocheckout gitenv plaingh` printed

    rev 81ea9ea2908ea83a012e3e42d694df56bb097c8c
    whole: tick_loop self-test: 34 checks, 0 failed rc=0
    nocheckout: tick_loop self-test: 34 checks, 3 failed rc=1
          nested FAIL: a seat bin dir with no gh shim: one TICK-GH flag line naming the gh found, beside the banner
        FAIL the self-test run from a branch checkout behind origin/main passes and does not move its HEAD
        FAIL the self-test run from a detached checkout behind origin/main passes and does not move its HEAD
        FAIL the self-test run with GIT_DIR naming a detached checkout behind origin/main passes and does not move its HEAD
    gitenv: tick_loop self-test: 34 checks, 1 failed rc=1
          nested FAIL: --once: one pass, cloud_relay.sh pass --confirm first, then the tick with its args; one banner
          nested FAIL: each pass calls the heartbeat once, with the pass line (no --out path)
        FAIL the self-test run with GIT_DIR naming a detached checkout behind origin/main passes and does not move its HEAD
    plaingh: tick_loop self-test: 34 checks, 4 failed rc=1
          nested FAIL: a seat bin dir with no gh shim: one TICK-GH flag line naming the gh found, beside the banner
        FAIL the self-test run from a branch checkout behind origin/main passes and does not move its HEAD
          nested FAIL: a seat bin dir with no gh shim: one TICK-GH flag line naming the gh found, beside the banner
        FAIL the self-test run from a detached checkout behind origin/main passes and does not move its HEAD
          nested FAIL: a seat bin dir with no gh shim: one TICK-GH flag line naming the gh found, beside the banner
        FAIL the self-test run with GIT_DIR naming a detached checkout behind origin/main passes and does not move its HEAD
          nested FAIL: a seat bin dir with no gh shim: one TICK-GH flag line naming the gh found, beside the banner
        FAIL null control: a branch checkout at origin/main (behind 0) passes and stays put

- `nocheckout` puts the `HPO_TICK_CODE_DIR` export back below the TICK-GH rows (the merge base's order): the three behind-origin/main rows fail, the null control passes.
- `gitenv` puts `throwaway_git_env` back below the heartbeat rows (the merge base's order): the `GIT_DIR` row alone fails.
- `plaingh` takes the no-shim row's own `gh` off its PATH: all four nested rows fail, each naming the no-shim row, because each nested run has the shim in its state dir's bin.
- `whole` is the unmutated control.
- A `nested FAIL` line precedes the row it belongs to. Under `nocheckout` the two detached rows have none: their nested run passes every row and the row fails on the moved HEAD alone.

## Null control

The unmodified tree, `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh 8c10361eb1` (the merge base's self-test run from each throwaway clone), printed

    rev 8c10361eb1fea539dc5acb8f7442eac2810faa47
    branch behind=1: tick_loop self-test: 30 checks, 1 failed HEAD-UNMOVED
        FAIL a seat bin dir with no gh shim: one TICK-GH flag line naming the gh found, beside the banner
    detached behind=1: tick_loop self-test: 30 checks, 0 failed HEAD-MOVED
    gitdir behind=1: tick_loop self-test: 30 checks, 2 failed HEAD-MOVED
        FAIL --once: one pass, cloud_relay.sh pass --confirm first, then the tick with its args; one banner
        FAIL each pass calls the heartbeat once, with the pass line (no --out path)
    shim behind=0: tick_loop self-test: 30 checks, 1 failed HEAD-UNMOVED
        FAIL a seat bin dir with no gh shim: one TICK-GH flag line naming the gh found, beside the banner
    level behind=0: tick_loop self-test: 30 checks, 0 failed HEAD-UNMOVED

- `branch` and `detached` are the finder's two shapes: a failing row from a branch, a moved HEAD from a detached head. `gitdir` and `shim` are the two this pull request adds.
- `level` is the null control: at behind 0, with a plain `gh`, the merge base passes and stays put, so each red above is its shape and not the harness.

The head, `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh 81ea9ea290`, printed

    rev 81ea9ea2908ea83a012e3e42d694df56bb097c8c
    branch behind=1: tick_loop self-test: 30 checks, 0 failed HEAD-UNMOVED
    detached behind=1: tick_loop self-test: 30 checks, 0 failed HEAD-UNMOVED
    gitdir behind=1: tick_loop self-test: 30 checks, 0 failed HEAD-UNMOVED
    shim behind=0: tick_loop self-test: 30 checks, 0 failed HEAD-UNMOVED
    level behind=0: tick_loop self-test: 30 checks, 0 failed HEAD-UNMOVED

The merge base's whole self-test from a scratch copy that is no checkout: `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh 8c10361eb1 whole nocheckout` printed `whole: tick_loop self-test: 30 checks, 0 failed rc=0` and `nocheckout: NOT RUN, the mutation did not apply (no '# mut:selftest-*' marker at this rev?)`. A mutant arm at the merge base is not run, because the markers it moves are this diff's.

## Figures

- Mutants at the head: `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh 81ea9ea290 whole nocheckout gitenv plaingh`, output under `## Mutation proof`.
- Shapes at the merge base and at the head: `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh 8c10361eb1` and `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh 81ea9ea290`, outputs under `## Null control`. This is the finder's control (its `BLOCKED.md`: the self-test run from a branch checkout behind main, and from a detached one) re-run at both ends in throwaway clones; the finder ran it in live checkouts, which is the defect.
- The stray FAIL, before the `pipefail` line. The rule: one run is one `--self-test` execution, and a stray FAIL is a failing row whose shape was not under test. At the previous head b80f611aa1 (the same `tick_loop.sh` less that line), `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh b80f611aa1 whole` was run four times at a load average near 40 while other `prepr.sh` runs were going: three runs printed `34 checks, 1 failed`, each naming a different nested row ("a refused push is printed", "a failing heartbeat is printed", "a seat bin dir with no gh shim"), and one printed `0 failed`. At this head the same arm was run twice, both `0 failed`. Two runs do not measure a rate; the capture above is the evidence for the cause, and the line removes the mechanism for every row at once. No mutant arm removes the line, because the failure it prevents is a race and a mutant run would pass most of the time.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`, naming `tests/doc_claims.py` (the instrument page is a doc) and `tests/entities.py` (the `tests/closures.json` entry). `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` printed `ALL 343 checks PASSED`. `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `1 of 2708 ENTITY CHECKS FAILED` at the head, twice, and the same line at the merge base, run in a detached scratch worktree at the same time as the head's second run; the one failing check is the same in all three and is answered under `## Red checks`. `tests/harness_headers.py`, a `run_always` script holding the exclusive gate lease, was not run here and is left to CI; the new harness prints no `RESULT` line for it to compare.
- Structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- CI prediction: `python3 tools/pr/ci_predict.py --base origin/main` printed `CI PREDICT: no closures, fast, governance or instrument red predicted against 8c10361eb1fe (a data-file read is not seen)`.
- prepr: `bash tools/pr/prepr.sh` at this head, with no body, printed `PRE-PR: 81ea9ea2908ea83a012e3e42d694df56bb097c8c 0000000000000000000000000 rc=0` with every step `ok` or `skip`. The skips: `self-test` (no change to `prepr.sh` or a program it names), `closures` ("the diff cannot be scoped, so CI re-records every closure; a full derive here is forbidden"), `diff mutants` (`MUTANT_CMD` unset: the diff adds no `.py` line, so `mutant_run.py` has nothing to draw), `no-copies`, `claims register`, and `body` and `receipt` for want of a body. The body's own step is `bash tools/pr/prepr.sh --body-check` on this file, run after it was written; no receipt was written, so the opener's own `prepr.sh` run is not saved by one.
- Class sweep (fixer step 8). The class is an instrument whose production arm moves a checkout onto a remote ref, reachable from that instrument's own self-test with the caller's checkout as the target. The rule: `git grep -nE 'checkout +(-q +)?--detach +(-q +)?"?origin/|"checkout", *("-q", *)?"--detach", *("-q", *)?f?"origin/' -- tools tests .claude`. Every seam it returns, against its disposition:
  - `tools/audit/seat/tick_loop.sh` `fresh_check`, target the checkout the script lives in unless `HPO_TICK_CODE_DIR` names another: closed in this diff, in the self-test (the three routes above).
  - `tools/audit/seat/cloud_relay.sh` `tools_level`, target `<state>/relay-tools`, a worktree the function adds itself: a tree of its own by construction, never the caller's checkout. Read, not driven here.
  - `tools/audit/seat/roster_queue.py`, target `--lint-clone`, a directory its caller names: not the checkout it runs from. Read, not driven here.
  - `tools/audit/seat/roster_edit.py`, inside its self-test, target the self-test's own driver clone. Read, not driven here.
  - `tools/release/stamp.py` `adopt_main`, target the working directory, which the stamp's own rule 1 requires to be a checkout of origin/main; its self-test passes a stub in its place. Read, not driven here.
  - The rule reads one spelling of one move (a detach onto a remote ref). A `reset --hard` or `checkout -B` onto a remote ref is a different spelling it does not return; no instrument was found that enumerates every such move across the seat tools, and this pull request adds none.
- Within the self-test, the routes from the caller's environment to a row. The rule: every variable the script reads before its first row. `grep -n 'HPO_[A-Z_]*\|\$HERE\|\$PATH\|\$HOME' tools/audit/seat/tick_loop.sh` over the lines of `tick_pass` and `fresh_check` returns `HPO_TICK_CODE_DIR` and `$HERE` (closed: exported at scratch), `HPO_STATE_DIR` and `PATH` (closed: scratch state dir, and the no-shim row's own `gh`), `HPO_TICK_RELAY`, `HPO_TICK_CMD`, `HPO_TICK_HEARTBEAT`, `HPO_TICK_SWEEP_CMD` (already stubbed in every row), `HPO_TICK_STALE_BOUND`, `HPO_TICK_RELAY_WAIT`, `HPO_TICK_SWEEP_EVERY`, `HPO_SWEEP_MANDATE` and `HPO_TICK_RESTARTED` (read from the caller's environment and not reset by the self-test: a caller that exports one changes a row's outcome, not a checkout; not closed here). Git's own environment is closed by `throwaway_git_env`.

## Red checks

- `governance / instrument-self-tests`, step "Show the tick loop refusing its own fixtures", predicted red by `ci_predict.py` on PR #3451's handoff (rc 1 at that head, 0 at its base), three times. Cause: the self-test rows named above read the caller's checkout, so the step's result depended on how far the seat's checkout was behind origin/main. Process state: a self-test with no row run from a checkout that differs from CI's (CI checks out detached at the head, behind 0). Cheaper detector: the four nested rows this pull request adds, which run in the self-test itself on every run; standing cost, four more self-test runs per run, timed above. The harness is the reproducer for a seat.
- `tests/entities.py`, local only, not a CI check: `1 of 2708 ENTITY CHECKS FAILED`, the check "a measured script's late-writing descendant is waited for, not recorded as nodata" (the coverage stage's wait bound). It is equally red at the merge base 8c10361eb1 on this host, run side by side with the head, and nothing in this diff is read by the coverage stage. Not root-caused here: it is another seam, on a host at a load average near 40. No cheaper detector applies, since it is not this diff's.

## Forward-carry

none

## Friction

tick_loop.sh.md: cost: one row of the self-test is a wall-clock bound ("a relay slower than the interval does not delay the board", under 3 s) and fails when the host is saturated: with three self-test loops run in parallel at a load average near 40 it failed in 5 of 30 runs, and in 0 of 10 run one at a time at the same load. It predates this diff and is not a pipefail miss; the nested rows run it four more times per run. Carry: dismissed: load artefact, numbers above
