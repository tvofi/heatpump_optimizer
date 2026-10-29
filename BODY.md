R10-ORCH-BEATD arm (a): the supervised beat's engine, `tools/audit/seat/beatd.py`, and the beat jobs' git, `tools/audit/seat/beatd_shims/git`, with their `INSTRUMENTS.md` entries and the self-test's CI step. This is the first of three serial arms of #2505 (concern B). It does not close the issue, because (b) and (c) follow.

The approved note is `dev/programme/designs/R10-ORCH-BEATD.md` on `design/R10-ORCH-BEATD` at 32e249d2ed66bd8dfd7f158efedeb93b306edac5 (`Design review: approve 32e249d2ed66bd8dfd7f158efedeb93b306edac5`, design-verdict at 4c15decb07c645eb54d543f1d4c8a12f14b7d7b9). Its §2 is built as written. For (b) and (c), the round-3 reference text is f0f0469294c95f39b399c1392c1d393bebc4985c §3 and §6.

Scope, as §2 sets it:
- no job row (`beatd.jobs.json` does not exist yet, so `run` without `--jobs` refuses with rc 2);
- no edit to any existing script;
- no policy text;
- both claim files byte-identical, and no golden fixture touched.

The only edit to an existing file outside `INSTRUMENTS.md` is `governance.yml`: one step, and the `instrument-self-tests` cap with its comment. `selftest_wiring.py --check` refuses an unwired self-test, so that step is required.

What the engine does:
- **Table.** It refuses a malformed table (rc 2, zero jobs run).
- **Single instance.** It holds `beatd.lock`; a second `run` exits 75.
- **Jobs.** Each job runs under its own lock and process group, with SIGTERM at `timeout_s` and SIGKILL 10 s later unless the group has emptied, whether or not its leader exited on the SIGTERM; the job lock drops after.
- **Class lock.** It takes the `orch-checkout` class lock, waits at most `class_wait_s` (default 60), and then records `busy`.
- **Journal.** It writes the journal.
- **`status`.** It reports `late`, `idle` and `DOWN`, plus `ALERT lock-owner-dead`, `ALERT pulse-silent` and `STALE-CODE behind=`.
- **`held`.** This is `beatd.lock`'s one reader for other scripts.
- **Real git.** It resolves the real git once and refuses rc 2 when that git is a shim or does not answer `git version` (carry dr4-real-git-validate).

The shim resolves the real git from `HPO_REAL_GIT` only when that is a regular executable file that is not a shim (carry dr4-real-git-validate: a directory falls back to the PATH walk). Otherwise it walks `PATH` and skips every copy that carries the line-2 marker, read with builtins. With no real git it exits 127. It retries a `fetch` or `pull` that fails on `cannot lock ref`.

Arm (a)'s three carries are closed here: dr3-shim-discovery, dr3-bash32 and dr4-real-git-validate. The (b) and (c) carries stay on the roster group, as the note and the verdict assign them.

Two repairs followed the first open's prepr refusal (code f1f34cd61):
- **throwaway git.** The self-test's fixture repositories are built with `tests/throwaway_git.py` (`throwaway_git_init` / `throwaway_git_clone`), so auto-maintenance is off in both the environment and each repository's config. The race's fetches still run under the beat's own env.
- **policy_lint `named-docs`.** The bare-name pass resolved the word `git` in `.claude/rules/claim-files.md` prose to the tracked extensionless file `tools/audit/seat/beatd_shims/git`, the only tracked file with that basename. The shim must be named `git` to be found on `PATH`, and it is an executable, not prose. The exclusion is the data file's: `dev/governance/config/corpus_excluded.json` gains the path, and its `_comment` the reason. `policy_lint.mjs` is byte-identical to main.

## Fix review round 1: each item answered

The verdict `Fix review: blocked ad1ba9adb7341d31288d27648da09f0ce61def19` (review/2916 at 803820f94) named one block and three findings. Commit 84e5684e5 answers all four.

- **Block: sigkill-escalation.** `Beat.supervise` sent the group SIGKILL only inside `while p.poll() is None:`, so once the leader exited on SIGTERM a TERM-ignoring descendant outlived the timeout and the job lock dropped beside it. Now, when the loop ends with the escalation still owed (`kill_at` set), `kill_group(p.pid, kill_at)` polls the group with `killpg(pgid, 0)` until the grace ends and then sends the group SIGKILL; `ProcessLookupError` means the group is empty and ends it early. `run_one` drops the job lock only after `supervise` returns. Pinned by case (3)'s arm `a TERM-ignoring grandchild is killed after its leader exits`, its null `null: a leader ignoring TERM too is killed at the grace, rc -9` (the reviewer's null), and the plants `m3_no_group_kill_after_leader`, `m3_kill_group_no_sigkill` and `m3_no_sigkill_live_leader` (the reviewer's x1).
  - Alternatives. Waiting on the group with `os.waitpid(-pgid)` reaps only our own children, and the orphaned grandchild is reparented away from beatd, so it cannot see it. Sending SIGKILL at once when the leader exits drops the 10 s grace the note gives a trapping descendant to clean up. The poll keeps both.
  - Residual: pid reuse. Once the group empties, a new process could take that number as its own group id inside one 0.1 s poll step and receive the SIGKILL. Linux does not reuse a number while it names a live group, so the window is that step alone.
- **Five unpinned behaviours** (the reviewer's mutants, each now a case arm and a `MUTANTS` entry):
  - `x4_no_heartbeat`: case (3)'s slow job now has `heartbeat_s: 1`; arm `a heartbeat job journals RUNNING past elapsed=0`, null `null: a job with no heartbeat journals RUNNING once` (the stubborn job, 12 s with no heartbeat), plant `m3_no_heartbeat`.
  - `x8_watch_as_periodic`: the next-start rule moved from `Beat.loop` into `next_start()`, called by the loop. A watch job's `interval_s` is at least 60 s, beyond a fixture's budget, so case (4) drives the rule, not a run: arm `a watch job restarts interval_s after its instance ends`, null `null: a periodic job keeps its grid, or restarts from a late start`, plant `m4_watch_as_periodic`. That a loop passes the end time is read, not run.
  - `x13_unreadable_staleness_clean`: case (7) arm `an unreadable staleness read is rc 2, never clean` (a START code no repository holds), plant `m7_unreadable_staleness_clean`; the healthy fixture is its null.
  - `x15_sigterm_handler_off`: case (2) arm `SIGTERM stops the beat and TERMs its job: rc 0, PASS rc=-15, STOP` (a beat with no `--once` or `--for`, so only the signal ends it), null `null: the job was running when the beat got SIGTERM`, plant `m2_sigterm_handler_off`.
  - `x16_held_never_dead_clear`: case (7) arm `a RUNNING line with no PASS under a free beatd.lock is a dead instance`, null `null: the same lines under a held beatd.lock read running`, plant `m7_dead_running_kept`.
- **instrument-self-tests margin.** The self-test's mutants now run four at a time (`MUTANT_WORKERS = 4`, a `ThreadPoolExecutor`; each plant has its own temp tree and state directory, and output stays in `MUTANTS` order). On this host the full self-test takes 266 s against 688 s serial for the same 25 plants. #2873's job took 16 min 32 s without beatd, so the job comes to about 21 min of its 30-minute cap, about 9 min of headroom against the 4 min measured at ad1ba9adb. The workflow comment states this. A separate job was the alternative; with the step at about 4.5 min the existing job holds it with margin, and no new job name enters the files that read this job's (`tests/entities.py`'s `_IST_JOB`, `tools/pr/ci_predict.py`).
- **Crash accounting** (evidence in the verdict, not a finding). A crashing mutant now fails with `[crash …]` in its line rather than counting as a kill. That surfaced two plants which had been killing by crash: `m2_no_instance_flock` (case (2) read the mode of a lock file the mutant never creates) and `m4_serial_jobs` (the beat never stops, and `_beat` raised `TimeoutExpired`). Both cases now read those states, and both plants kill through their named checks.
- **`m3_no_killpg` retargeted.** With the escalation fixed, a beat that TERMs only the leader still kills the group 10 s later, so the plant survived `its process group was killed`. Case (3)'s slow job now runs a grandchild that traps TERM and writes a marker; the arm `its process group took SIGTERM before any SIGKILL` reads the marker, and the plant kills it. A marker, not a duration, because a container whose pid 1 reaps no orphans keeps a killed grandchild as a zombie, which `killpg(pgid, 0)` still finds.

## Fix review round 2: the block answered

The verdict `Fix review: blocked ca2dc27d74252606afb264c514585f9ea0e405b5` (review/2916 at 1ae1d3fef, verdict/2916 at 5f9b05586) named one block, `mutation-vacuous`: the reviewer's plants y1 (`kill_group`'s `while time.time() < at:` to `while False:`) and y16 (`KILL_GRACE_S = 10.0` to `0.5`) each survived case (3), so the 10 s SIGTERM-to-SIGKILL grace was unpinned. Commit 6fd9984a7 answers it in the self-test alone; no production line changes.

- **The pin.** Case (3)'s two stubborn arms, `a TERM-ignoring grandchild is killed after its leader exits` and its null `null: a leader ignoring TERM too is killed at the grace, rc -9`, now also require the job's PASS `dur=` to lie in `[2 + KILL_GRACE_S, 2 + KILL_GRACE_S + 5]` (`timeout_s` is 2). `KILL_GRACE_S` is read from the unmutated module that runs the case, so a plant that shortens the constant in the copy under test cannot move the bound. `dur` is beatd's own, measured from the job's start to the lock drop, so a zombie grandchild (the marker arm's concern) does not reach it. The upper bound makes "at the grace" true as the null's name says; its 5 s slack covers a loaded runner.
- **The plants**, each a `MUTANTS` entry:
  - `m3_kill_group_no_grace` (the reviewer's y1): (3) `a TERM-ignoring grandchild is killed after its leader exits`;
  - `m3_grace_half_second` (the reviewer's y16): (3) `null: a leader ignoring TERM too is killed at the grace, rc -9`. It targets the live-leader path, which y1 cannot reach, so between them both paths' grace is pinned.
- **Alternatives.** Timing the grandchild's death from outside the beat reads the zombie the round-1 marker avoided. Pinning `KILL_GRACE_S == 10.0` by value alone pins the constant, not `kill_group`'s use of it (y1 survives it). The `dur` bound pins both.
- **The seven other surviving plants** (y2, y3, y6, y7, y9, y13, y14 in the verdict's `## Findings`) are deferred, not answered here. The verdict owes each "a case arm and a `MUTANTS` entry, or a stated deferral"; this repair's brief is the block alone, and each is a behaviour correct at this head (the verdict says so). Destination: the R10-ORCH-BEATD roster group's next round on this PR, if the orchestrator opens one, or arm (b), whose brief reopens the self-test.

## Head

6fd9984a7ec03ba9c6f20193c0d442947986206d

One commit on the reviewed head ca2dc27d74252606afb264c514585f9ea0e405b5 (which merged code head 84e5684e5 with origin/main 593f57c44). No merge since: `git merge-tree --write-tree origin/main HEAD` exits 0 against origin/main 6493ea362 (2026-10-29T00:05Z). Every figure below without a named SHA was taken at 6fd9984a7; figures from round 1 keep their SHA.

## Mutation proof

The self-test plants each `MUTANTS` entry in a temp copy of `beatd.py` and `beatd_shims/git`, runs that case against the copy, and requires the named check to go red. Every plant is a predicate change, and the self-test pins each anchor to occur exactly once in production text. At 6fd9984a7, all 27 plants print `ok` (`mutant <name> turns (<case>) '<check>' red`):

- `m1_parse_defaults_to_zero_jobs`: (1) `unreadable`
- `m1b_unknown_key_accepted`: (1) `unknown key`
- `m2_no_instance_flock`: (2) `second run exits 75`
- `m2_lock_world_readable` (CodeQL alert 45): (2) `lock files are owner-only under umask 022`
- `m3_no_killpg`: (3) `its process group took SIGTERM before any SIGKILL`
- `m3_no_group_kill_after_leader` (the block): (3) `a TERM-ignoring grandchild is killed after its leader exits`
- `m3_kill_group_no_sigkill` (the block): (3) the same check
- `m3_no_sigkill_live_leader` (reviewer x1): (3) `null: a leader ignoring TERM too is killed at the grace, rc -9`
- `m3_kill_group_no_grace` (round 2, reviewer y1): (3) `a TERM-ignoring grandchild is killed after its leader exits`
- `m3_grace_half_second` (round 2, reviewer y16): (3) `null: a leader ignoring TERM too is killed at the grace, rc -9`
- `m3_no_heartbeat` (reviewer x4): (3) `a heartbeat job journals RUNNING past elapsed=0`
- `m4_watch_as_periodic` (reviewer x8): (4) `a watch job restarts interval_s after its instance ends`
- `m2_sigterm_handler_off` (reviewer x15): (2) `SIGTERM stops the beat and TERMs its job: rc 0, PASS rc=-15, STOP`
- `m4_serial_jobs`: (4) `fast passes while slow runs`
- `m5_class_ignored`: (5) `class jobs never interleave`
- `m6_retries_zero`: (6) `race: B through the shim exits 0, origin/main current, a retry logged`
- `m6_no_shim_prepend`: (6b) `beat job B exits ok through the shim`
- `m6_drop_C_skip`: (6) the same race check
- `m6_string_compare` (round 3's rule, f0f046929 spike `shims/git`): (6) `discovery relative: rc 0 within 5 s`
- `m6_marker_via_head`: (6) `discovery no-real-git: rc 127, one line`
- `m6_real_git_dir_accepted` (dr4): (6) `discovery real-git-is-dir: rc 0 within 5 s`
- `m6_beatd_trusts_any_git` (dr4): (6) `beatd refuses rc 2 when its git is not git`
- `m7_late_without_timeout`: (7) `null: past interval, inside interval + timeout, is not late`
- `m7_no_pulse_alarm`: (7) `pulse-silent while beatd reads healthy`
- `m7_unreadable_staleness_clean` (reviewer x13): (7) `an unreadable staleness read is rc 2, never clean`
- `m7_dead_running_kept` (reviewer x16): (7) `a RUNNING line with no PASS under a free beatd.lock is a dead instance`
- `m8_held_always_free`: (8) `held: rc 0 while held`

Failing test first, for round 2's block: with the two `MUTANTS` entries added and case (3) not yet bounded (the working tree before 6fd9984a7's case edit), `--self-test 3` printed `FAIL mutant m3_kill_group_no_grace turns (3) 'a TERM-ignoring grandchild is killed after its leader exits' red` and `FAIL mutant m3_grace_half_second turns (3) 'null: a leader ignoring TERM too is killed at the grace, rc -9' red`, `22 checks, 2 failed`, rc 1; its other 20 lines, the case's 8 checks and the five other case-(3) plants, printed `ok`. With the bound, the same command's two lines print `ok` (in the full run below).

Failing test first, for round 1's block: the new self-test text over ad1ba9adb's production text (`beatd.py` above the self-test mark from ad1ba9adb, below it from 84e5684e5's tree; a temp copy) with `--self-test 3 2 7 --no-mutants` printed `FAIL (3) a TERM-ignoring grandchild is killed after its leader exits` while its null `null: a leader ignoring TERM too is killed at the grace, rc -9` printed `ok`. The two other failures were the anchor checks of `m3_no_group_kill_after_leader` and `m3_kill_group_no_sigkill`, whose production lines that tree lacks. The arms for x13, x15 and x16 printed `ok` there: they pin behaviour that was already correct.

The reviewer's own mutant harness (`ev/xmut.py` at review/2916), re-run at 84e5684e5 with its anchor count read over production text (the new `MUTANTS` entries repeat those anchors in the self-test, so the unmodified harness reads count 2 for x4, x15 and x16) and with x8's anchor moved to `next_start()`: `x1_no_sigkill`, `x4_no_heartbeat`, `x8_watch_as_periodic`, `x13_unreadable_staleness_clean`, `x15_sigterm_handler_off` and `x16_held_never_dead_clear` each print `KILLED`, none `CRASH`. At ad1ba9adb all six printed `SURVIVED` (the verdict's `ev/reviewer-mutants.txt`). Unmodified, the harness at 84e5684e5 still prints `KILLED` for x2, x5, x6, x7, x9, x10, x11, x12, x13 and x14, and now also for x1; x3 is still not run (its anchor occurs twice, as at ad1ba9adb).

## Null control

Round 2, the finder's harness: the reviewer's `ev/ymut.py` (verdict/2916 at 5f9b05586, sha1 e6d3da28608e6f4feb916462aff6e320f8ba945f), unchanged, `ONLY=y1_kill_group_no_grace,y16_grace_half_second /opt/hpo/venv-ci/bin/python -I ymut.py <tree>`:
- at ca2dc27d7: `BASELINE (3) 8 checks, not-true: []`, `RESULT y1_kill_group_no_grace: SURVIVED; red=[]` and `RESULT y16_grace_half_second: SURVIVED; red=[]`, the verdict's reading;
- at 6fd9984a7: `BASELINE (3) 8 checks, not-true: []`, `RESULT y1_kill_group_no_grace: KILLED; red=['(3) a TERM-ignoring grandchild is killed after its leader exits']` and `RESULT y16_grace_half_second: KILLED; red=['(3) a TERM-ignoring grandchild is killed after its leader exits', '(3) null: a leader ignoring TERM too is killed at the grace, rc -9']`.

The bound's own null is in that run: the unmutated baseline holds all 8 checks true, so the bound does not refuse the correct grace; and y1 leaves the live-leader null green, so the null arm's bound reads the live-leader path, not `kill_group`. The round-1 probe (`ev/probe-sigkill-escalation.sh`, sha1 0ef8282926e6db2f9f41b1104e2dfada6f4daf4e) at 6fd9984a7: `beatd rc=0 after 12s`, `PASS … dur=12 rc=-15 outcome=timeout`, `grandchild … state: gone`, and an empty `stubborn.lock` with mode `-rw-------`.

Round 1:


Each case carries its own null in the same run, and each printed `ok` at 6fd9984a7:
- (1) a well-formed table runs its job.
- (2):
  - a run after the first ends gets the lock;
  - the 0o644 mutant reads the mode check red under the same umask 022 (`Popen(umask=0o022)`);
  - the job was running, with no PASS, when the beat got SIGTERM.
- (3):
  - an in-time job reads `ok`;
  - a job with no heartbeat journals RUNNING once;
  - a leader ignoring TERM too is killed at the grace (`rc=-9`), so the escalation's own path still fires with the new one beside it.
- (4) the fast job alone passes as often; a periodic job keeps its grid, or restarts from a late start.
- (5) two class-less jobs overlap.
- (6):
  - B with the beat's env and no shim exits 1 with `cannot lock ref`;
  - beatd runs when the real git is first on `PATH`;
  - `git status` through the shim logs no retry.
- (7):
  - a healthy fixture prints no alarm, rc 0;
  - a live lock owner, and a pulse with nothing stopped, are no alarm;
  - past the interval but inside interval + timeout is not late;
  - a RUNNING line with no PASS under a held `beatd.lock` reads `running`.
- (8) `held` is rc 1 with no lock file, and rc 1 after release.

The finder's harness for the block is the reviewer's probe, `ev/probe-sigkill-escalation.sh` at review/2916, run unchanged but for the tree path, under `/opt/hpo/venv-ci/bin/python`:
- at ad1ba9adb: `beatd rc=0 after 4s`, `PASS … dur=2 rc=-15 outcome=timeout`, and 15 s after the timeout `grandchild … state: S`;
- at 84e5684e5: `beatd rc=0 after 12s`, `PASS … dur=12 rc=-15 outcome=timeout`, and `grandchild … state: gone`.

Step 8, the class: the seams through which a timed-out job's processes can outlive its lock are the exits from `Beat.supervise`, enumerated by `grep -n "return\|while p.poll() is None" tools/audit/seat/beatd.py` inside `supervise`:
- the `OSError` return before `Popen`: no process exists, nothing to kill;
- the end of `while p.poll() is None:` with `kill_at` set: closed in this diff (`kill_group`);
- the end of that loop with `kill_at` already `None`: the SIGKILL was sent inside the loop, with the leader alive, so the group got it;
- the end of that loop with no timeout (`outcome is None`): the job finished in time, and a descendant it left running is outside the timeout clause; the note gives no rule for it, so it is left as is.
The beat's own SIGTERM handler TERMs the groups and does not escalate. The note's §2 states only "stops scheduling" and SIGTERMs; an escalation there is a design question for (b), not this repair.

## Figures

- `HOME=<empty> GIT_CONFIG_GLOBAL=/dev/null /opt/hpo/venv-ci/bin/python -I tools/audit/seat/beatd.py --self-test` (Linux, Python 3.14.7, no committer identity, as on a CI runner): `beatd self-test: 119 checks, 0 failed`, rc 0, 278 s wall. That is 65 case checks, 27 anchor checks and 27 mutant checks; the rule is `grep -c` over the log for lines starting `ok   (`, `ok   anchor` and `ok   mutant`, and the anchor and mutant checks are one per `MUTANTS` entry. Round 1's figure at 84e5684e5 was `115 checks, 0 failed`, 266 s; the two new entries add 2 anchor and 2 mutant checks and no case check.
- Serial control: before the four-way pool, the same 25-plant table run serially under python3 3.11.17 took 688 s and printed `114 checks, 1 failed`, the one being `m3_no_killpg` before its retarget (above).
- `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh BODY.md` (run under /opt/hpo/venv-ci, on this body): `PRE-PR: 6fd9984a7ec03ba9c6f20193c0d442947986206d`, rc 0, with 29 ok, 9 skip and 0 REFUSE (`grep -c` of the `ok`, `skip` and `REFUSE` lines).
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `100 self-testing, 100 wired, 0 unwired`.
- `python3 -I tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2470 ENTITY CHECKS PASSED`. `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`. These are the scripts `scope.run` names, run under /opt/hpo/venv-ci (Python 3.14.7).
- `python3 tests/closure.py select --diff 593f57c44fa57490ed757343b9f277ef97ad5ca5`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, naming `tests/entities.py` and `tests/harness_headers.py`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `no closures, fast, wave-script or instrument red predicted against 593f57c44fa5`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 593f57c44fa57490ed757343b9f277ef97ad5ca5 HEAD`: `Architecture score: dS +0.0000 NULL`. The note's target is dS = 0; `vector.py` reads only `custom_components/heatpump_optimizer`.
- `git diff --stat 593f57c44fa57490ed757343b9f277ef97ad5ca5...HEAD -- VERSION tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt custom_components RELEASE_NOTES.md`: empty (0 lines).
- instrument-self-tests timing, from the check runs' `started_at`/`completed_at`: #2873's job 16 min 32 s (16:43:54Z to 17:00:26Z); #2916's at ad1ba9adb 26 min 01 s (20:44:19Z to 21:10:20Z, from the verdict's `ev/check-runs.txt`).
- Earlier figures, kept with their SHAs: `84 checks, 0 failed` at f008c2b75 (macOS, /bin/bash 3.2.57, git 2.38.1); `87 checks, 0 failed` at f0f8c3b60 and ad1ba9adb (Linux, Python 3.14.7). The `named-docs` null (at d72c4a982, without the exclusion, `TOTAL: 1 error(s)` with the `[named-docs] tools/audit/seat/beatd_shims/git` error) and the env-matrix and `policy_lint_mutants.mjs` figures at c991d64cd are unchanged by this commit, which touches neither the corpus nor the exclusion.

## Red checks

- **`CodeQL`** and **`code-scanning alert 45 (py/overly-permissive-file)`** at e09b123f9 (#2916). `Lock.take` created each lock file 0o644. **Fixed at f0f8c3b60:** the mode is 0o600, as `tests/gate_lock.py`'s, pinned by case (2)'s `lock files are owner-only under umask 022` and the plant `m2_lock_world_readable`.
  - **Root-cause trigger.** No cheaper detector exists for this property in this tree: `prepr.sh` runs no CodeQL query, and no lint reads `os.open` modes. `grep -rn "os.open(.*O_CREAT" tools tests` returns two other sites, neither a lock CodeQL reported. So no countermeasure is built here.
- **`governance / instrument-self-tests`** (cancelled) at e09b123f9. Two causes, both fixed at f0f8c3b60:
  - **Case (7) crash.** Its `commit-tree` ran outside `throwaway_git`'s env, so on a runner with no global git identity it exited 128.
  - **Timeout.** The job hit its 20-minute cap. The cap is 30; this round cuts the self-test to about 4.5 min (`## Fix review round 1`).
  - **Root-cause trigger.** A cheaper detector exists: run a fixture self-test with `HOME=<empty> GIT_CONFIG_GLOBAL=/dev/null`, or have `tests/throwaway_git.py --check` refuse a fixture git call made without the throwaway env. Its standing cost is one env override per self-test run, or one AST rule. Process state: (c). It is not built here, because it changes `tests/throwaway_git.py`, outside arm (a); it is owed to a root-cause seat under `defect-root-cause.md`.
- **`gate`** (both runs at e09b123f9). The gate aggregates the others' conclusions and printed `governance / policy-docs: failure`, `governance / env-matrix: failure` and `pr-contract / pr-contract: failure`, plus `unreadable title` for run 40738998081, the title-edit run. It has no failure of its own.
- **`pr-contract / pr-contract`** at e09b123f9. It printed `PR-BODY: 4 error(s)`: the body then on the PR did not name `CodeQL`, alert 45, `governance / env-matrix` or `governance / policy-docs` under `## Red checks`. This body names all four.
- **`governance / env-matrix`** and **`governance / policy-docs`** at e09b123f9 (#2916). Both are the one `[named-docs] tools/audit/seat/beatd_shims/git` error, fixed through `corpus_excluded.json`.
  - **Cause.** The exclusion was written into `tools/policy/policy_lint.mjs`, which both jobs restore from the base before grading.
  - **Root-cause trigger.** A cheaper detector exists: prepr running each `PINNED` check source from the merge base, as `governance.yml`'s restore step does; its standing cost is one `git show <base>:<path>` per pinned file per prepr run. Process state (c). Not built here: it is a change to `tools/pr/prepr.sh`, the base-copy grader class that R10-RCA-PREPR-HEAD-GRADERS (PR #2925) owns.
- No check is red at ad1ba9adb in the verdict's `ev/check-runs.txt`; the block was a measured defect, not a CI failure.
- No check is red at ca2dc27d7 in the round-2 verdict's `ev/check-runs.txt` (no failure or cancellation; five runs still in progress at its read). Round 2's block was `mutation-vacuous`, a measured gap in the self-test, not a red check, so no root-cause trigger fires for it.

## Forward-carry

- **The beat's SIGTERM handler TERMs its running groups but never escalates** (round-2 verdict, third finding): a TERM-ignoring descendant of a job running when beatd is stopped can outlive the beat, and its lock drops as beatd exits. It changes how arm (b) must work, so it belongs in arm (b)'s brief on the R10-ORCH-BEATD roster group as a precondition (`finding-propagation.md`). Destination: that brief. This repair seat may push only its return refs, so it has not written it; the orchestrator owes it (`roster_edit.py`) before this PR merges. Carry: R10-ORCH-BEATD
- **Seven plants the reviewer named survive** (y2, y3, y6, y7, y9, y13, y14; `## Fix review round 2`). Destination: the same roster group, as owed in this PR's next round or in arm (b)'s brief, which reopens the self-test. Carry: R10-ORCH-BEATD

## Friction

none
