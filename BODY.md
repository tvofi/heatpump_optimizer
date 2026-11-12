Hotfix for the tick loop's self-test, which read and could move the checkout it was run from. `tools/audit/seat/tick_loop.sh --self-test` ran its first rows (the TICK-GH rows) before pointing `HPO_TICK_CODE_DIR` at scratch, so those rows ran the freshness check on the caller's checkout: on a branch checkout behind origin/main on the watched paths one row printed an extra `TICK-STALE` line and failed, and on a detached checkout behind origin/main the restart arm checked out origin/main in the caller's checkout. `ci_predict.py` then predicted `governance / instrument-self-tests` red on an unrelated group's handoff whenever origin/main moved during its `prepr.sh` run (R10-PROCESS-SLIM part 2, PR #3451; evidence in `BLOCKED.md` at handoff-wip/r10-process-slim-p2, 1b45b89b9abfb4313cf661cf4c6712b5a51a86fa).

The fix is in the self-test alone; the loop's production lines are unchanged. Things in the caller's environment reached a row; the checkout and the `gh` are closed where they entered, and the environment as a whole is closed by construction (the last bullet but one); a further defect, found while proving these, made any row fail at random under load:

- **The checkout the script lives in.** `HPO_TICK_CODE_DIR` is exported at scratch before the first row (the earlier seat's commit 1fba05ec35). Every row but the freshness rows, which name their own clone, runs from a directory that is no checkout.
- **A repository named by the environment.** `GIT_DIR` outranks `git -C`, so with `GIT_DIR` and `GIT_WORK_TREE` exported (a git hook's environment) the rows before `throwaway_git_env` still ran the freshness check on the named checkout, whatever `HPO_TICK_CODE_DIR` said, and detached it. `throwaway_git_env` now runs before the first row.
- **The caller's `gh`.** The row "a seat bin dir with no gh shim" took whichever `gh` the caller's PATH held and expects it not to be the shim. The script puts `$HPO_STATE_DIR/bin` first on PATH before the self-test starts, and on a live seat that directory holds the shim, so the row failed on every seat host and the self-test could not be green there at all. The row now leads its PATH with a plain `gh` of its own.
- **A row's verdict under pipefail.** The script sets `pipefail`, and a row is `printf '%s\n' "$out" | grep -q ...`. A `grep -q` that leaves at its match can kill the `printf` feeding it (141), and the row then reads a match as none. This is `prepr.sh`'s own `PIPE_GREP_Q_FILES` class (R9-RCA-prepr-tmp), which `tick_loop.sh` was never drained of. Captured on this host under load: the row "null control: a refused push is printed with its reason and the pass still completes" printed FAIL while its output held both lines it greps for (`HEARTBEAT NOT PUSHED: ` and `tick=0`). It matters here because the self-test now runs itself four more times, so a stray FAIL is that much likelier per run. The self-test's subshell turns `pipefail` off; the loop keeps it. A row pins the line: 2 MB after its match makes the SIGPIPE certain, the form `prepr.sh`'s own self-test uses for this class.
- **The caller's environment, closed by construction.** Round 2 found the earlier drop list (every `HPO_TICK_*` and `HPO_SWEEP_MANDATE`) open: `heartbeat.sh` reads `HPO_HEARTBEAT_REMOTE`, and with a URL there the self-test force-pushed `heartbeat/orchestrator` to it; the stubs' own controls (`TICK_RC`, `RELAY_RC`, `HB_RC`, `SWEEP_RC`, `SWEEP_WORD`) reached every row that left one unset. The drop list is gone. `--self-test` now re-runs the script under `env -i` (`selftest_allowlisted`) carrying only `SELFTEST_ENV`: `PATH` and `TMPDIR` (else `/tmp`) from the caller, a scratch `HOME`, and, only when set, the nesting flag `HPO_TICK_SELFTEST_NESTED` and `offline_spy.py`'s `SPY_LOG` and `SPY_REAL_GIT` (its PATH wrappers read them; without them a spied run's `git` would exec nothing). The rows' entry point, `--self-test-allowlisted`, refuses any exported name off that list but bash's own `PWD`, `OLDPWD`, `SHLVL` and `_` (`selftest_env_check`), so a name nobody enumerated cannot reach a row, whoever calls it. Three rows pin it: the every-variable nested row now also sets `HPO_HEARTBEAT_REMOTE=nope`, the five stub controls, `RELAY_SLEEP=10` and an unlisted `HPO_TICK_UNLISTED=1`; the entry point run with `HPO_TICK_UNLISTED=1` refuses before any row, naming it; and the self-test run with `HPO_HEARTBEAT_REMOTE=https://127.0.0.1:9/hb.git` in its caller's environment passes under `offline_spy.py` with `network=0 remote_git=0` and a non-zero `git=` count, beside the spy's null control (one `git ls-remote` at that URL counted as `remote_git=1`).
- **A wall-clock row.** "a relay slower than the interval does not delay the board" bounded the pass at under 3 s, in whole seconds, over a pass that already waits one. It predates this diff, but the self-test now runs it six times a run, and on this host at a load average near 40 it failed in 4 of about 13 executions at 46d3e79cdd. The row now asserts the property itself: the pass is back with its board written while the 6 s relay has not finished, read from the relay's own log. The two mutants that pinned it (`r10_seat_selftests_mutants.py` S31, the detach line, and S34, the serial relay) both wait the relay out and both still fail it: each applied to a scratch copy of the head's script (that harness mutates the checkout in place; a one-off probe in seat scratch), the 30-row form printed `31 checks, 4 failed` for S31 and `31 checks, 7 failed` for S34, this row among them.

Five rows pin the checkout shapes by running the whole self-test from throwaway clones: a branch clone behind origin/main, a detached clone behind, a detached clone behind named by `GIT_DIR`/`GIT_WORK_TREE`, a detached clone behind named by `HPO_TICK_CODE_DIR` with every other loop variable set too, and a branch clone at origin/main (the null control, which asserts its own behind=0 premise). Each asserts the nested tally is `0 failed` and that the clone's HEAD did not move; each runs under a state dir whose bin holds the shim, as a live seat does; a failing nested row is named on a `nested FAIL` line above its row.

Alternatives, and why each lost. Extending the drop list with the six names round 2 found is the repair the verdict sketched; it lost because the class is any name a row or a child it runs for real reads, and a list closes only the names someone has found (the same list missed these six). An allowlist inside the running shell (unsetting every exported name off it) would leave the shell's non-exported state and its already-expanded top-level lines from the caller's run; a re-exec under `env -i` starts from nothing. Draining the self-test's `| grep -q` sites and listing `tick_loop.sh` in `prepr.sh`'s `PIPE_GREP_Q_FILES` is the tree's barrier for the pipefail class; it lost because `prepr.sh` is outside this group's files and the drain rewrites every row's assertion where one pinned line removes the mechanism for the self-test's subshell. A guard in `fresh_check` that refuses to move a checkout outside a self-test root would put test awareness into the production restart path. Skipping the freshness check when run from a branch would hide the read and leave the detached shape. Restricting the nested runs to the rows above the freshness rows would presume which rows can reach the caller, which is the mistake being fixed. `dev/audit/harnesses/r10_tick_selftest_checkout.sh` lands the reproducer (fixer step 18): it runs a rev's self-test from throwaway clones and from a scratch copy with each guard taken back out, never in the caller's checkout. The in-tree mutant harness `r10_seat_selftests_mutants.py` is not used for these mutants: it mutates the committed file in place and runs the step from the checkout, and these mutants are the ones that move a checkout.

Cost: the self-test now runs itself five more times, plus once more under `offline_spy.py`; at this head on this host the whole self-test took `real 1m30s` (`time bash tools/audit/seat/tick_loop.sh --self-test`). On this host, under a load average near 40, the whole self-test took 103 s and 96 s at the previous head 81ea9ea290, with four nested runs, and was not timed again with the fifth; CI's step took 7 s and 13 s in the two most recent scheduled `governance` runs on main (job step "Show the tick loop refusing its own fixtures"), so about six times that is expected there.

Off Linux, scoped closure recordings are left to CI (`gate-scoping.md`): no `tests/derive_closures.sh` was run on this macOS host. The one closures edit is the inert-read entry for the new harness, written by `python3 tools/pr/ci_predict.py --apply-inert`.

## Head

fbde1675681fb1f8f86e971b923070e8a62b382f, merge base 8c10361eb1fea539dc5acb8f7442eac2810faa47. origin/main was at 4145f2852642fd0b5ccb8b7af60d41e896a5eea3 at 2026-11-12T20:34:36Z; `git merge-tree --write-tree origin/main HEAD` exited 0 (no conflict), so per `fixer.md` step 6 it is not merged in. `git diff --stat 8c10361eb1 4145f28526 -- tools/audit/seat/tick_loop.sh tools/audit/seat/heartbeat.sh tools/audit/seat/ref_privacy.py tools/audit/seat/offline_spy.py tests/throwaway_git.sh` prints nothing: none of the five files the self-test reads differs between the merge base and that tip.

## Mutation proof

Each new guard taken back out of the head's `tick_loop.sh`, the whole self-test run from a scratch copy: `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh fbde167568 whole envi allowlist pipefail` printed

    rev fbde1675681fb1f8f86e971b923070e8a62b382f
    whole: tick_loop self-test: 39 checks, 0 failed rc=0
    envi: tick_loop self-test: 39 checks, 2 failed rc=1
          nested FAIL: --once: one pass, cloud_relay.sh pass --confirm first, then the tick with its args; one banner
          nested FAIL: null control: no cloud_relay.sh in the tree (before #2419) skips the relay and still ticks
          nested FAIL: a failing relay pass is reported and the tick still runs; the tick's status is reported
          nested FAIL: a relay slower than the interval does not delay the board; the banner says relay=running
          nested FAIL: a pass that finds the relay in flight starts none (no overlap) and still ticks
          nested FAIL: null control: the late relay is reaped with its log next pass, and a fast relay reports ok
          nested FAIL: each pass calls the heartbeat once, with the pass line (no --out path)
          nested FAIL: a failing heartbeat is printed, never silent, and the loop still exits cleanly
          nested FAIL: --sweep: one sweep after the tick, its last line after the banner, its whole output in <out>.sweep.log
          nested FAIL: --sweep: the next pass inside the interval sweeps nothing (the slow backstop)
          nested FAIL: a refused sweep is reported with its rc and the pass still completes
          nested FAIL: a real pass moves heartbeat/orchestrator on the remote
          nested FAIL: null control: a refused push is printed with its reason and the pass still completes
          nested FAIL: freshness null control: behind 0 is silent (code=<sha7> behind=0 on the banner) and does not exec
          nested FAIL: freshness: behind within the bound and no change to the loop's own files relays, restarts nothing; the heartbeat says behind=1
          nested FAIL: freshness: a held relay lock does not restart, skips the relay and still writes the board under TICK-STALE
          nested FAIL: freshness: a dirty tree prints the banner, skips the relay and is never moved
          nested FAIL: freshness: a checked-out branch is never moved (restart needs a detached head)
          nested FAIL: freshness: origin/main's tick_loop.sh failing bash -n is never checked out or exec'd
          nested FAIL: freshness: a loop-file change with a free lock and a clean detached tree checks out origin/main and execs it with the same args
        FAIL the self-test run with every loop variable, the stubs' controls, HPO_HEARTBEAT_REMOTE and an unlisted name set in the caller's environment, HPO_TICK_CODE_DIR naming a detached checkout behind origin/main, passes and does not move its HEAD
        FAIL the self-test run with HPO_HEARTBEAT_REMOTE a URL in the caller's environment passes under offline_spy.py: no network call, no remote git call, its git calls seen
    allowlist: tick_loop self-test: 39 checks, 1 failed rc=1
        FAIL the rows' entry point run with a name off the allowlist refuses before any row, naming it
    pipefail: tick_loop self-test: 39 checks, 7 failed rc=1
        FAIL a row's verdict is its reader's: a grep -q that leaves at its match, its writer killed mid-write, still reads the match
          nested FAIL: a row's verdict is its reader's: a grep -q that leaves at its match, its writer killed mid-write, still reads the match
        FAIL the self-test run from a branch checkout behind origin/main passes and does not move its HEAD
          nested FAIL: a row's verdict is its reader's: a grep -q that leaves at its match, its writer killed mid-write, still reads the match
        FAIL the self-test run from a detached checkout behind origin/main passes and does not move its HEAD
          nested FAIL: a row's verdict is its reader's: a grep -q that leaves at its match, its writer killed mid-write, still reads the match
        FAIL the self-test run with GIT_DIR naming a detached checkout behind origin/main passes and does not move its HEAD
          nested FAIL: a row's verdict is its reader's: a grep -q that leaves at its match, its writer killed mid-write, still reads the match
        FAIL the self-test run with every loop variable, the stubs' controls, HPO_HEARTBEAT_REMOTE and an unlisted name set in the caller's environment, HPO_TICK_CODE_DIR naming a detached checkout behind origin/main, passes and does not move its HEAD
        FAIL the self-test run with HPO_HEARTBEAT_REMOTE a URL in the caller's environment passes under offline_spy.py: no network call, no remote git call, its git calls seen
          nested FAIL: a row's verdict is its reader's: a grep -q that leaves at its match, its writer killed mid-write, still reads the match
        FAIL null control: a branch checkout at origin/main (behind 0) passes and stays put

- `envi` replaces the `env -i` re-exec with a direct call of the rows in the caller's environment: the two rows that set caller variables fail (the every-variable row naming twenty nested rows; the spy row), every other row passes.
- `allowlist` makes `selftest_env_check` pass every name: the refusal row alone fails.
- `pipefail` (the round-1 pin, kept) deletes `set +o pipefail`: the 2 MB row fails in the outer run and in every nested run.
- `whole` is the unmutated control.
- The round-1 arms `nocheckout`, `gitenv` and `plaingh` move lines this round does not touch; they were run at fb218fa5f7 (round 2's body) and not again. `envscrub` no longer applies at this head: the line it deleted is gone, and the arm says `NOT RUN` on a rev without its marker.

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

The merge-base runs above were taken in round 1 and not re-taken: the harness reads only the rev's committed files. The head, `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh fbde167568`, printed

    rev fbde1675681fb1f8f86e971b923070e8a62b382f
    branch behind=1: tick_loop self-test: 31 checks, 0 failed HEAD-UNMOVED
    detached behind=1: tick_loop self-test: 31 checks, 0 failed HEAD-UNMOVED
    gitdir behind=1: tick_loop self-test: 31 checks, 0 failed HEAD-UNMOVED
    shim behind=0: tick_loop self-test: 31 checks, 0 failed HEAD-UNMOVED
    level behind=0: tick_loop self-test: 31 checks, 0 failed HEAD-UNMOVED

The merge base's whole self-test from a scratch copy that is no checkout: `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh 8c10361eb1 whole nocheckout` printed `whole: tick_loop self-test: 30 checks, 0 failed rc=0` and `nocheckout: NOT RUN, the mutation did not apply (no '# mut:selftest-*' marker at this rev?)`. A mutant arm at the merge base is not run, because the markers it moves are this diff's.

## Figures

- Mutants at the head: the command and output under `## Mutation proof`.
- Shapes at the merge base and at the head: outputs under `## Null control`. This is the finder's control (its `BLOCKED.md`: the self-test run from a branch checkout behind main, and from a detached one) re-run in throwaway clones.
- Round 2's harm, re-run at both ends (a one-off probe in seat scratch, not landed: each rev's five files written to a scratch directory, its self-test run with `HPO_TICK_SELFTEST_NESTED=1`, the outer rows only, and one variable set in the caller's environment). `HPO_HEARTBEAT_REMOTE` set to the path of a scratch bare repository: at fb218fa5f7 `31 checks, 2 failed rc=1`, and `git for-each-ref` on that repository printed `refs/heads/heartbeat/orchestrator`; at fbde167568 `31 checks, 0 failed rc=0` and the repository holds no ref. Each stub control set alone, fb218fa5f7 against fbde167568: `TICK_RC=1` 14 failed against 0; `RELAY_RC=1` 3 against 0; `HB_RC=1` 3 against 0; `SWEEP_RC=2` 1 against 0; `SWEEP_WORD=X` 1 against 0; `RELAY_SLEEP=10` 0 against 0 (the reviewer's figures reproduced at fb218fa5f7). The fb218fa5f7 column is the null control for the fbde167568 column.
- The whole self-test under the instrument the brief names: `python3 -I tools/audit/seat/offline_spy.py tools/audit/seat/tick_loop.sh` printed `offline_spy: tools/audit/seat/tick_loop.sh rc=0 network=0 remote_git=0 git=795 subprocess=n/a backstop=none offline | tick_loop self-test: 39 checks, 0 failed` (run at 2d851203d0, whose only difference from the head is the refusal row's `env -i` prefix). Its null control is the spy row's own control row, which passes at the head: the spy counts a git call at the URL as remote.
- Self-test at the head: `time bash tools/audit/seat/tick_loop.sh --self-test` printed `tick_loop self-test: 39 checks, 0 failed`, `real 1m30.062s`. At 2d851203d0 the refusal row failed (`39 checks, 1 failed`): run from inside the rows, its child inherited the rows' own exports (`GIT_*`, `HPO_STATE_DIR`) and the refusal named one of those first; fbde167568 runs that child under `env -i` with the one off-list name.
- The class: every name a row, or a child the rows run for real, reads from the environment. Rule: the parameter expansions (`$NAME`, `${NAME...}`, `${!v}`, `compgen -v PREFIX`) in `tools/audit/seat/tick_loop.sh`, `tools/audit/seat/heartbeat.sh` and `tests/throwaway_git.sh`, the stubs the self-test writes, and the `os.environ`/`os.getenv` keys in `tools/audit/seat/ref_privacy.py` and `tools/audit/seat/offline_spy.py` (read by a subagent over those five files; locals and positional parameters set aside). Every name it returns, against its disposition under `env -i`:
  - On the allowlist, set explicitly by `selftest_allowlisted`: `PATH` (the caller's), `HOME` (scratch), `TMPDIR` (the caller's, else `/tmp`), `HPO_TICK_SELFTEST_NESTED`, `SPY_LOG`, `SPY_REAL_GIT` (the caller's, only when set).
  - Absent from the environment, then set by the rows that need one: `HPO_STATE_DIR`, `HPO_TICK_CODE_DIR`, `HPO_TICK_RESTARTED`, `HPO_TICK_STALE_BOUND`, `HPO_TICK_RELAY_WAIT`, `HPO_TICK_SWEEP_EVERY`, `HPO_TICK_SWEEP_CMD`, `HPO_SWEEP_MANDATE`, `HPO_TICK_RELAY`, `HPO_TICK_CMD`, `HPO_TICK_HEARTBEAT`, `TICK_RC`, `RELAY_RC`, `HB_RC`, `SWEEP_RC`, `SWEEP_WORD`, `RELAY_SLEEP`.
  - Absent and never set, so the reader's default applies: `HPO_HEARTBEAT_REMOTE` (`heartbeat.sh`: `origin`, the scratch remote), `USER` and `LOGNAME` (`ref_privacy.py`'s home and name redaction: empty).
  - Absent, and dropped again by `throwaway_git_env`: `GIT_CONFIG_KEY_*`, `GIT_CONFIG_VALUE_*`.
  - Set by bash itself: `BASH`, `PWD`, `OLDPWD`, `SHLVL`, `_`.
  - Whatever this rule misses (git's and Python's own environment reads, a name a later row starts reading) is closed by the same construction: `selftest_env_check` refuses any exported name off the list, and the `allowlist` arm is its mutant.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`, naming `tests/doc_claims.py` and `tests/entities.py`. At 2d851203d0: `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` printed `ALL 343 checks PASSED`; `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/entities.py` printed `ALL 2709 ENTITY CHECKS PASSED`. Not re-run at fbde167568, whose delta is one row's command line inside the self-test.
- Structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- CI prediction: `python3 tools/pr/ci_predict.py --base origin/main` printed `CI PREDICT: no closures, fast, governance or instrument red predicted against 8c10361eb1fe (a data-file read is not seen)`.
- Review round 2 (`Fix review: blocked fb218fa5f7 class-open`): repaired by the construction above, not by the drop list it sketched; its three repair items are answered in order: `HPO_HEARTBEAT_REMOTE` and the stub controls cannot reach a row, and the enumeration rule now covers every file a row runs for real.
- Round-1 repairs kept: the 2 MB pipefail row (its arm above) and the nested rows.
- prepr: `bash tools/pr/prepr.sh` at this head, with no body, printed `PRE-PR: fbde1675681fb1f8f86e971b923070e8a62b382f 0000000000000000000000000 rc=0` with every step `ok` or `skip`. The skips: `self-test` (no change to `prepr.sh` or a program it names), `closures` ("the diff cannot be scoped, so CI re-records every closure; a full derive here is forbidden"), `diff mutants` (`MUTANT_CMD` unset: the diff adds no `.py` line, so `mutant_run.py` has nothing to draw; the self-test's mutants are the harness arms above), `no-copies`, `claims register`, and `body` and `receipt` for want of a body. The body's own step is `bash tools/pr/prepr.sh --body-check` on this file.
- Class sweep (fixer step 8), the checkout moves: unchanged from round 2 and not re-run, since this round changes no checkout move. The rule `git grep -nE 'checkout +(-q +)?--detach +(-q +)?"?origin/|"checkout", *("-q", *)?"--detach", *("-q", *)?f?"origin/' -- tools tests .claude` returned `tick_loop.sh` `fresh_check` (closed in this diff), `cloud_relay.sh` `tools_level`, `roster_queue.py`, `roster_edit.py` and `stamp.py` `adopt_main` (each a tree of its own or its caller's naming; read, not driven).

## Red checks`. `tests/harness_headers.py`, a `run_always` script holding the exclusive gate lease, was not run here and is left to CI; the new harness prints no `RESULT` line for it to compare.
- Structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- CI prediction: `python3 tools/pr/ci_predict.py --base origin/main` printed `CI PREDICT: no closures, fast, governance or instrument red predicted against 8c10361eb1fe (a data-file read is not seen unless a changed file's own self-test makes it)`.
- Review round 1 (`Fix review: blocked 81ea9ea290 mutation-vacuous`): both items are repaired in this head, the pipefail pin and the loop-variable scrub, each with its row and its harness arm above; the wall-clock row is the reviewer's finding, taken too.
- prepr: `bash tools/pr/prepr.sh` at this head, with no body, printed `PRE-PR: fb218fa5f70d57a959f362da8074df1145656cf0 0000000000000000000000000 rc=0` with every step `ok` or `skip`. The skips: `self-test` (no change to `prepr.sh` or a program it names), `closures` ("the diff cannot be scoped, so CI re-records every closure; a full derive here is forbidden"), `diff mutants` (`MUTANT_CMD` unset: the diff adds no `.py` line, so `mutant_run.py` has nothing to draw), `no-copies`, `claims register`, and `body` and `receipt` for want of a body. The body's own step is `bash tools/pr/prepr.sh --body-check` on this file, run after it was written; no receipt was written, so the opener's own `prepr.sh` run is not saved by one.
- Class sweep (fixer step 8). The class is an instrument whose production arm moves a checkout onto a remote ref, reachable from that instrument's own self-test with the caller's checkout as the target. The rule: `git grep -nE 'checkout +(-q +)?--detach +(-q +)?"?origin/|"checkout", *("-q", *)?"--detach", *("-q", *)?f?"origin/' -- tools tests .claude`. Every seam it returns, against its disposition:
  - `tools/audit/seat/tick_loop.sh` `fresh_check`, target the checkout the script lives in unless `HPO_TICK_CODE_DIR` names another: closed in this diff, in the self-test (the three routes above).
  - `tools/audit/seat/cloud_relay.sh` `tools_level`, target `<state>/relay-tools`, a worktree the function adds itself: a tree of its own by construction, never the caller's checkout. Read, not driven here.
  - `tools/audit/seat/roster_queue.py`, target `--lint-clone`, a directory its caller names: not the checkout it runs from. Read, not driven here.
  - `tools/audit/seat/roster_edit.py`, inside its self-test, target the self-test's own driver clone. Read, not driven here.
  - `tools/release/stamp.py` `adopt_main`, target the working directory, which the stamp's own rule 1 requires to be a checkout of origin/main; its self-test passes a stub in its place. Read, not driven here.
  - The rule reads one spelling of one move (a detach onto a remote ref). A `reset --hard` or `checkout -B` onto a remote ref is a different spelling it does not return; no instrument was found that enumerates every such move across the seat tools, and this pull request adds none.
- The caller's environment, enumerated from the script. The rule: `grep -oE '\$\{?(HPO|GH|GIT|GITHUB)_[A-Z_0-9]+' tools/audit/seat/tick_loop.sh | tr -d '${' | sort -u`. Every name it returns, against its disposition:
  - `HPO_TICK_CODE_DIR`, `HPO_TICK_RESTARTED`, `HPO_TICK_STALE_BOUND`, `HPO_TICK_RELAY_WAIT`, `HPO_TICK_SWEEP_EVERY`, `HPO_TICK_SWEEP_CMD`, `HPO_TICK_RELAY`, `HPO_TICK_CMD`, `HPO_TICK_HEARTBEAT`, `HPO_SWEEP_MANDATE`: dropped before the first row (the `compgen -v HPO_TICK_` line, which also drops any `HPO_TICK_*` a later change adds), then set by the rows that need one. The every-variable row sets each of the ten.
  - `HPO_TICK_SELFTEST_NESTED`: the self-test's own flag, kept on purpose; it only skips the nested block.
  - `HPO_STATE_DIR`: read at the script's top for PATH, before the self-test starts; the self-test exports its own scratch state dir, and the no-shim row brings its own `gh`. Every nested row sets it.
  - The rule returns no `GIT_*`, `GH_*` or `GITHUB_*` name: the script reads none itself. Git's own environment is dropped by `throwaway_git_env`; `gh` is reached through PATH alone, closed as above, and no row runs a real `gh`.

## Red checks

- `governance / instrument-self-tests`, step "Show the tick loop refusing its own fixtures", predicted red by `ci_predict.py` on PR #3451's handoff (rc 1 at that head, 0 at its base), three times. Cause: the self-test rows named above read the caller's checkout, so the step's result depended on how far the seat's checkout was behind origin/main. Process state: a self-test with no row run from a checkout that differs from CI's (CI checks out detached at the head, behind 0). Cheaper detector: the five nested rows this pull request adds, which run in the self-test itself on every run; standing cost, five more self-test runs per run, timed above. The harness is the reproducer for a seat.
- No pull request exists and no CI has run at this head, so no check in `merge_train.py owed-reds` is red on it.

## Forward-carry

none

## Friction

none
