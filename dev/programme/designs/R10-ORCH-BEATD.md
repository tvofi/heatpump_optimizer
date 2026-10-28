# R10-ORCH-BEATD design note (designer seat)

This is the group's architect note, extended (`dev/governance/roles/designer.md`). It lives on `design/R10-ORCH-BEATD` only and is never merged. Size L, lane IN, issue #2505 (concern B of the re-cut). It re-measures the approved design at `archive/handoff/orch-machinery` `09174d94e` (`dev/audit/design/orch-machinery/DESIGN.md` §6.2, §6.5, §6.6, §8 Phase 1) against current main. **Round 3 of 3**: it answers the five points of `design-verdict/R10-ORCH-BEATD` `810697a5a` (§8 maps each) and folds its six carries. Where a point allowed it, scope was cut: (d1) and (d3) are dismissed as moot after (c), by measurement (§6 (d)), and the round-2 `ALERT handoff-ahead` in `beatd status` is gone, so the tick is the one classifier of that line.

**Read at.** Code: `origin/main` `6d86acc909f7fc465e5736771daf8fa45c1373a4`. `git diff --stat 6349205b6 6d86acc90 -- tools/audit/seat/` touches only `INSTRUMENTS.md`, `roster_lib.py` and `state_docs.py`; this note re-reads every line it cites from those three. Roster: `origin/handoff/audit-r10-roster` `8b434ef62`. Spike: `dev/programme/designs/R10-ORCH-BEATD.spike/` on this ref (the shim and its race, never merged).

## 1. Premises, re-measured

| design premise (09174d94e) | at `6d86acc90` |
|---|---|
| no supervisor; daemons launched by hand (S5, M30) | holds. `beatd.py` and `beatd.jobs.json` do not exist; `daemonize.py` keeps no bookkeeping. |
| relay is one job (B7) | moved. `cloud_relay.sh pass` runs four arms serially in one process; `tick_loop.sh` starts it detached and waits at most 30 s, so tick and relay fetches already overlap today. |
| the item-28 failure is git's ref lock | **reproduced, and the round-2 remedy refuted** (`810697a5a` `evidence/reflock_two_fetchers.sh`). Two real fetches of one remote-tracking ref: B exits 1 with `cannot lock ref`, with or without `core.filesRefLockTimeout`. A re-run of B exits 0. |
| watchers keep a 60 s floor (carry 14) | **false**: `ci-watch.sh` sleeps 300 s fixed; `proof_watch.py --poll` has no floor. |
| a seat per standing role (0015 §5) | after (c) one standing seat is left, merge (`pulse.py:91` `STANDING` minus tick, dispatch, roster). |

## 2. Owning seam

**`tools/audit/seat/beatd.py` (would be new) owns the schedule, supervision, per-job and class locks, timeouts, the journal, the status, the digest and each job's environment. `tools/audit/seat/beatd.jobs.json` (would be new, data) owns the job table. `tools/audit/seat/shims/git` (would be new) owns the fetch retry.** Each job's script keeps the state it already owns, and none gains a loop:
- `cloud_relay.sh` owns `<log>.level` and its lock (§3).
- `ledger.py` owns the level kinds, `handoff-ahead` included, and the 1200 s boundary.
- `orchestrator_tick.py` owns the board, and is the one reader that flags a `handoff-ahead` line.
- `roster_queue.py` owns the roster cursor.
- `bus.sh` owns the dispatch registry, its lock, and the owed-dispatch loop.
- `pulse.py` stays the off-host complement.

`tests/layout.json`'s `tools` group and `tests/closure.py` classify the three new files; wire the self-test by `selftest_wiring.py --check`.

## 3. Shape

**Job table** (`beatd.jobs.json`, `{"version":1,"jobs":[…]}`). Keys: `name`, `argv` (repo-relative), `cwd` (`orch` = the beat's own checkout, or a path), `interval_s`, `timeout_s`, `heartbeat_s|null`, `env_pass`, `class` (`null` or `orch-checkout`), `kind` (`periodic|watch`). There is no `phase` key: a row lands in the arm that lands its argv. An unknown or missing key, `interval_s < 60` on `kind:"watch"`, or an unreadable file gives rc 2, `beatd: REFUSE <reason>`, and zero jobs run (B11).

**Rows landed by (b)**, each argv existing at (b)'s head. Fetch sites were found by `grep -n 'fetch'`. "Shared" means the orchestrator checkout or one of its worktrees; they share one ref store.

| job | argv | cwd | fetches in the shared store | interval/timeout | class |
|---|---|---|---|---|---|
| `tick` | `tick_loop.sh --once --no-relay --no-heartbeat --out $S/tick.txt` (`env_pass: HPO_LEDGER_AGING`) | orch | 418, 643, 707, 1194, 1559, 2058 | 300/900 | `orch-checkout` |
| `relay-probe` | `cloud_relay.sh pass --arms probe,confirm,stuck` | orch | 190, 204, 313 | 120/120 | `orch-checkout` |
| `handoff` | `cloud_relay.sh pass --arms handoff` | orch | 413, 427, `review_freeze` 380, and `update_pr.sh` 47, 50 | 120/3600 | none |
| `heartbeat` | `heartbeat.sh --once --message "BEAT <status line>"` | `git -C $HERE` | none (`--once` is commit-tree plus push) | 300/60 | none |
| `state-docs` | `state_docs.py beat --once --apply --push --tip-file $S/beatd/state-docs.tip` | orch | `roster_fetch_spec` (240-260, 351) | 300/300 | `orch-checkout` |
| `wt-sync` | `wt_sync.sh --beat --scratch $S` | common dir (line 13) | 26 | 900/600 | `orch-checkout` |
| `pitch` | `merge_train.py sweep` | orch | yes, and the detached `train.sh` it starts (Popen with the inherited env, merge_train.py:812) outlives the job | 3600/900 | none |

**Rows appended by (c)**, with their flags (§3 Queue jobs):

| job | argv | cwd | fetches | interval/timeout | class |
|---|---|---|---|---|---|
| `roster-queue` | `roster_queue.py run --cursor $S/beatd/roster.cursor --queue $S/roster.queue --report $S/beatd/roster.report --edit-checkout <orch> --worktree $S/beatd/roster.wt --lint-clone $S/beatd/roster.lint` | orch | 110 (edit checkout); 123 is its own clone | 120/600 | `orch-checkout` |
| `dispatch` | `bus.sh dispatch-owed $S/tick.txt` | orch | 443 | 300/300 | `orch-checkout` |
| `ci-watch` | `ci-watch.sh` (`kind:"watch"`) | the request's | none (API polls) | 300/the request's budget | none |
| `proof-watch` | `proof_watch.py` (`kind:"watch"`) | the request's | none | 300/the request's budget | none |

**Item 28, the ref store (verdict point 1).** The fix has two parts.
- **The shim.** `beatd.py` prepends `tools/audit/seat/shims` to every job's `PATH`, so the job and its whole process tree reach `shims/git` first. The precedent is `roster_queue.py:95-97`, which already prepends that directory, and `bus.sh:1062-1083`'s self-test git shim. The shim finds the real git as the first `git` on `PATH` outside its own directory. It finds the subcommand by skipping `-C`, `-c`, `--git-dir`, `--work-tree` and `--namespace` with their values, and any other leading `-` option. Anything but `fetch` or `pull` is `exec`'d unchanged, so the tick's other git calls cost one `exec`. A `fetch` or `pull` whose stderr holds `cannot lock ref` is re-run at most `HPO_GIT_RETRIES` (default 2) more times, 1 s and then 2 s apart. Only the last attempt's stderr is printed. Each retry appends `<utc> retry=<n> rc=<rc> <sub>` to `HPO_GIT_SHIM_LOG`, which `beatd.py` sets to `$S/beatd/git-retry.log`, and the digest counts those lines.
- **The lock-timeout env.** `beatd.py` keeps `GIT_CONFIG_COUNT`/`core.filesRefLockTimeout=30000`, so each attempt waits out the holder instead of failing on `File exists`.
- **Why a re-run is safe.** A fetch is idempotent, and a pull whose fetch failed has merged nothing.

Measured with `R10-ORCH-BEATD.spike/race.sh` on the verdict's fixture (git 2.43.0):

| B, the second fetcher | rc | retries |
|---|---|---|
| shim + env | 0 | 1 |
| shim, no env | 0 | 2 |
| no shim, no env (today) | 1 | 0 |
| no shim, env (round 2) | 1 | 0 |
| shim with `HPO_GIT_RETRIES=0` | 1 | 0 |

**What the shim reaches.** It reaches every `git` resolved by `PATH` under a beat job:
- `orchestrator_tick.py`'s `["git", …]`;
- `cloud_relay.sh`, and `update_pr.sh`, which only prepends `venv-ci/bin` (line 27);
- `merge_train.py sweep` and its `train.sh`, which also only prepends (322, 363);
- `wt_sync.sh`, `state_docs.py` and `roster_queue.py`.

`git grep -nE '/usr/(local/)?bin/git'` over `tools/audit/seat` finds no absolute git. It does not reach the orchestrator's hand fetches or the fixers' worktrees. A beat job no longer dies on their race, and they keep today's one attempt, so a hand fetch that loses reruns as it does now. `seat_venv.sh --install-shims` copies only `seat-python*` (line 250), so no seat bin gains the git shim.

The `orch-checkout` class stays as round 2 had it (the verdict found the assignment sound). Every job of the shared store bounded by ≤ 900 s takes `$S/beatd/orch-checkout.lock` for its whole run, waits for it at most 60 s, and then records `outcome=busy`. `handoff` and `pitch` stay out of it, because a 3600 s hold would make the tick `busy` for an hour.

**`<log>.level` (approved in round 2, extended for points 2 and the confirm carry).** `level_set` (169) and `dispose` (262) become calls of one helper, `level_rmw`. It takes an exclusive flock on `<log>.level.lock` around its read, `awk`, write and `mv`, using a holder of `tick_loop.sh`'s `RELAY_HOLDER` kind (52, run at 76), since macOS has no `flock(1)`. `level_set <kind> <lines-file> [<keep-file>]` gains two carries, both computed **from the locked read**, never from an earlier one:
- **Keep.** Each `<ref> <sha>` in `<keep-file>` keeps its current line of `<kind>` if that line is still there. The confirm arm passes its "unknown, keep" pairs (cloud_relay.sh:313-315) as that file, instead of copying lines it read before the lock. A hand `dispose` between the two reads is therefore no longer undone (carry dr2-confirm-carry-dispose).
- **`since=`.** A new `handoff-ahead` line takes the `since=` of the current line with the same ref and sha, or the pass's time if there is none. A disposed or moved tip therefore restarts its clock.

`HPO_RELAY_LEVEL_PAUSE` (self-test only) sleeps between the read and the write.

**`handoff-ahead` (verdict point 2).** `ledger.py` `KINDS` gains `"handoff-ahead": "derived"` (90-95). `ledger.py` also gains `AHEAD_OWED_S = 1200` and `ahead_due(row, now) -> (due, age)`, which raises on a missing or unparseable `since=`. The line has the form `OWED <utc> handoff-ahead refs/heads/handoff/<topic> <hs> #<pr> since=<utc>`.

**When the handoff arm writes it.** It is written only for a PR still ahead **when its iteration ends**, never at the ahead test (415). There are four ends:
- the recorded-failure skip (421);
- no body (428);
- `update_pr.sh` busy, rc 75 (442);
- update failed, rc ≠ 0 (443).

A held PR keeps only its `handoff-held` line. An update with rc 0 writes nothing, so a normal handoff is never flagged. After the loop, `level_set handoff-ahead` runs beside the two existing calls.

**How the tick prints it** (orchestrator_tick.py:749-754, inside `lg.KINDS`):

| line | tick prints |
|---|---|
| `handoff-ahead`, `ahead_due` false | `ahead: <row> age=<s>`, unflagged |
| `handoff-ahead`, `ahead_due` true | `OWED: <row> age=<s>`, flagged |
| `handoff-ahead`, `ahead_due` raises | `REFUSED: …`, flagged |
| any other kind | as today |

The digest copies the flagged lines, which is item 18 (a)'s alarm. `beatd status` does not re-classify it.

**Run, journal, status, digest** (approved in round 2, unchanged except where named):
- **Run.** `beatd.py run --state $S` holds `$S/beatd/beatd.lock` (a second run exits 75 with `ALREADY RUNNING`). `beatd.py held` is that lock's one reader for other scripts. Each job runs on its own thread and process group under `$S/beatd/<job>.lock`; at its timeout it gets SIGTERM, then SIGKILL 10 s later. Start records `code=<HEAD sha>`.
- **Journal.** It records `PASS <utc> <job> … outcome=ok|failed|timeout|locked|busy|unreadable`, plus `RUNNING` lines.
- **Status.** It reports `late` (`age > interval_s + timeout_s`), `idle` for a watch job with no instance, and `DOWN`. Its alarms are `ALERT lock-owner-dead` (item 18 b), `ALERT pulse-silent` (item 2) and `STALE-CODE behind=` (item 8). rc is 0, 1 or 2.
- **Digest.** It holds TICK (every `-> ` and flagged line of `tick.txt`, with counts; item 26), ROSTER, DISPATCH, and BEAT (status plus the `git-retry.log` count).

**Queue jobs ((c); the cursor was approved in round 2).**
- **Roster.** `roster_queue.py run --cursor FILE` writes `.inflight` before each op and resolves it on start, by readback for `append-carry` and by the JSON value for `set-stage` and `set-pr`. Anything else stops as `unresolved` until the orchestrator queues `resolve <n> landed|retry`.
- **Dispatch.** `bus.sh dispatch-owed <board>` is a new subcommand, so the registry's owner owns the loop.
  - It refuses rc 2 when the board is absent or older than 1200 s; unknown is not "nothing owed".
  - It gets each (pr, head) of the board's `REVIEW OWED` lines from `python3 -I ledger.py owed-pairs <board>`. `ledger.py` is the owner of `review_owed`'s text (orchestrator_tick.py:697-702), so it is the one parser.
  - Under `$HPO_BUS_STATE/dispatched.lock` it checks each pair against the registry and calls `dispatch <pr> <head> cloud` for each one missing. The reviewer word is the relay's (cloud_relay.sh:452), so downstream reads one route.
  - `dispatch`'s append (479) takes the same lock, so the relay's handoff dispatch and this job cannot both mint for one (pr, head) (carry dr2-dispatch-double-mint).
  - The `reviewer-fire` close stays `dispatch`'s own (484), so there is no second writer (item 33).
- **Watch.** `beatd.py watch <job> --budget S --wake FILE -- <args>` runs that row's `argv[0]` with `<args>` once, under the job lock, and writes its last line to `FILE` on exit. That write is the waiter's one wake (item 14). Both scripts also keep the 60 s floor themselves (carry dr1-watch-floor-in-script).

**Double start (round-2 point 3, widened for point 4).** Every loop mode in scope refuses with rc 75 and `<tool>: REFUSE beatd running pid=<p>` while `beatd.py held` returns 0:
- `tick_loop.sh` without `--once`;
- `cloud_relay.sh pass --loop`, and **`cloud_relay.sh --watch` without `--once`** (a loop round 2 missed; INSTRUMENTS.md:316, :338);
- `state_docs.py beat` without `--once`;
- **`wt_sync.sh` without `--beat`.** `wt_sync.sh` has no loop mode, so a hand loop is a shell loop around it, and each iteration is refused.

The beat's own argv are never refused. With `beatd.py` absent, every script runs as today.

**Invariants.** No job is an agent loop. Each job has one live instance. A job is never killed before its timeout. An unreadable table, journal, level or board is never clean. The beat writes no ledger event of its own. Every write to `<log>.level` and to the dispatch registry is serialised by its owner's lock. A beat job's fetch survives a concurrent fetch of the same ref.

## 4. Alternatives

1. **Extend `tick_loop.sh`.** Lost: the loop is serial, with no per-job timeout; a 36-min handoff holds the tick.
2. **One unit per job under `daemonize.py`.** Lost: about ten units, no journal, and no owner of a cross-job lock.
3. **`core.filesRefLockTimeout` alone (round 2).** Lost by measurement (§3 table): B still exits 1, now on the old-value check.
4. **Job-private fetch refspecs** (the verdict's second option). Lost on call count: every fetch site in the two tables, plus `update_pr.sh` and `train.sh`, and every reader of `origin/main` would have to name a private ref. The hand fetches and the worktrees would still update the shared refs, and the shim needs none of those edits.
5. **`orch-checkout` on handoff and pitch.** Lost: the tick would be `busy` for an hour, and the class does not reach their children.
6. **Keep `ALERT handoff-ahead` in `beatd status`.** Lost: a second classifier of one line, beside the tick.

## 5. Sibling sites

- **Loops:** `git grep -n -E 'while :|while true|while True|--loop|--watch' -- 'tools/audit/seat/*.sh' 'tools/audit/seat/*.py'`.
  - In scope: `tick_loop.sh`, `cloud_relay.sh` (`pass --loop` and `--watch`), `heartbeat.sh`, `state_docs.py`, `ci-watch.sh`, `proof_watch.py`, `merge_train.py`. `heartbeat.sh --watch` is one check, which the owner's cloud task runs off-host (INSTRUMENTS.md:1007), so it is not refused.
  - Out, as one-shot or seat-run tools: `bus.sh`, `ci_critpath.py`, `ci_probe.py`, `gh_read.py`, `pr_args.sh`, `sweep_driver.py`, `train.sh`, `verify_eight.py`.
- **Level writers:** `git grep -n 'mv -f "\$lv'` finds two sites, both behind `level_rmw`.
- **Registry writers:** `git grep -n '/dispatched"'` in `bus.sh` finds the append at 479, behind `dispatched.lock`.
- **Hand launches (verdict point 4).** The grep is keyed on every job's script name, not on `daemonize.py`:

  ```
  P='tick_loop\.sh|cloud_relay\.sh|heartbeat\.sh|state_docs\.py|wt_sync\.sh|merge_train\.py|train\.sh|roster_queue\.py|ci-watch\.sh|proof_watch\.py|daemonize\.py|orchestrator_tick\.py'
  git grep -n -E "$P" -- dev/governance tools/audit/seat/sweep_template.md tools/audit/seat/INSTRUMENTS.md .claude CLAUDE.md AGENTS.md
  ```

  It returns 70 lines, and 11 match `detached|start|launch|background|loop|every N|restart`. Each is disposed of below.

  | site | what it launches | arm and rewrite |
  |---|---|---|
  | `nudge.md:113` | a `wt_sync.sh` loop | (b) refusal; (c) "the beat's `wt-sync` job runs it; `beatd.py status` shows it" |
  | `INSTRUMENTS.md:338` | `cloud_relay.sh --watch`, detached | (b) refusal; (c) text |
  | `INSTRUMENTS.md:355` | `pass --loop` | (b) refusal; (c) text |
  | `INSTRUMENTS.md:528` | `tick_loop.sh --sweep` every 1800 s | (c) text: the `pitch` job runs it |
  | `INSTRUMENTS.md:992` | `tick_loop.sh`, detached | (c) text |
  | `sweep_template.md:59` | `update_pr.sh`, detached per handoff | (c) step 2 |
  | `sweep_template.md:61` | the train sweep, detached | (c) step 3 (item 15) |
  | `sweep_template.md:65` | the tick seat | (b) step 5 |

  Three stay as they are:
  - `standing-merge.md:10`: the surviving merge seat's own train. It is safe beside `pitch`, because `train.sh add` is `ALREADY` for a live train (merge_train.py:845, under `QUEUE_LOCK` 721).
  - `nudge.md:101`: `ci-watch.sh` one-shot, which exits.
  - `.claude/workflows/audit-plan.js:68`: a score run, not a beat job.

  Each rewrite carries a rendered-text control, (c)8.

## 6. Arms and evidence (each arm one PR; `fixer.md` steps 2-8)

Harness: the approved design's E4/E7 and S5, item 28's recurrence evidence, and the verdict's `evidence/reflock_two_fetchers.sh`. The fixer builds `dev/audit/harnesses/r10_beatd_double_start.py` (would be new) for S5. The archscore target is dS = 0 (`vector.py:98` reads only `custom_components/heatpump_optimizer`); run `score.py --diff origin/main HEAD` before and after. No golden fixture moves, and both claim files stay byte-identical.

- **(a) The engine and the shim** (`beatd.py`, `shims/git`, `INSTRUMENTS.md`; no production table). Fixture tables live in the self-test's temp directory. Failing tests, each with its null control and mutant:
  1. A malformed table runs zero jobs (mutant: parsing defaults to zero jobs).
  2. A second `run` exits 75 (mutant: drop the instance flock).
  3. An over-time job reads `timeout` and an in-time one `ok` (mutant: drop the killpg).
  4. A slow job does not delay a fast one.
  5. Two `orch-checkout` jobs never interleave their `start`/`end` lines. Null: two class-less jobs do overlap. Mutant: drop one job's class.
  6. **The two-fetcher race, replacing round 2's (a)6.** The verdict's hook fixture: fetch A holds `refs/remotes/origin/main.lock` for 3 s, and B starts 1 s later as a beat job. Fixed: B exits 0, `origin/main` equals upstream, and `git-retry.log` has ≥ 1 line. Null: B with the beat's env but no shim on `PATH` exits 1 with `cannot lock ref`. Mutants:
     - `HPO_GIT_RETRIES=0`;
     - beatd stops prepending `shims` (B exits 1);
     - the shim drops `-C` from its option skip (the fixture runs `git -C c fetch`, so the subcommand is misread and B exits 1).

     A second case runs B through a child (`bash -c 'git -C c fetch -q origin'`), which proves inheritance. A third: `git status` through the shim leaves `git-retry.log` empty, and `git fetch` from a missing remote fails once with git's own message, with no retry.
  7. `status` reports `late`, `DOWN`, `busy`, `idle`, `lock-owner-dead`, `pulse-silent` and `STALE-CODE`, each against a fixture. Null: a healthy fixture prints no alarm. Mutant: `age > interval` without the timeout.
  8. `held` returns rc 0 while a fixture holds `beatd.lock`, and 1 when it is free.
- **(b) The seven rows, the level and the double start** (`beatd.jobs.json` with exactly §3's first table; `tick_loop.sh --no-relay --no-heartbeat` and its loop refusal; `cloud_relay.sh pass --arms`, `level_rmw` with keep and `since=`, `handoff-ahead`, and the refusals of `pass --loop` and `--watch`; `wt_sync.sh --beat` and its refusal; `state_docs.py beat` refusal; `ledger.py` `KINDS`, `AHEAD_OWED_S` and `ahead_due`; `orchestrator_tick.py:749-754`; `sweep_template.md` step 5 with item 26's text; `handover_prompt.py`). The self-test asserts that every row's `argv[0]` is tracked and its own `--help` or self-test accepts the row's flags.
  1. **Level race.** Concurrent `level_set probe-ref` and paused `level_set handoff-update` keep both kinds; a `dispose` concurrent with a paused `level_set` keeps both effects. Null: serial calls. Mutants: drop the lock; route `dispose` around it.
  2. **Confirm keep (dr2-confirm-carry-dispose).** A `confirm-owed` line in the keep-file is disposed while the confirm arm's `level_set` is paused. After the pass the line is absent; today it returns. Null: an undisposed kept line survives. Mutant: copy kept lines from a read before the lock.
  3. **Loop refusal.** One case per mode while a fixture holds `beatd.lock`: `tick_loop.sh` (no `--once`), `cloud_relay.sh pass --loop`, `cloud_relay.sh --watch` (no `--once`), `state_docs.py beat` (no `--once`) and `wt_sync.sh` (no `--beat`). Each exits 75 with `REFUSE beatd running`. Null: lock free, one iteration with a stub. Mutant per script: delete the check. The beat's own argv run under the lock.
  4. **`handoff-ahead` written after the decision.**
     - A pass whose update returns 0 leaves no `handoff-ahead` line (mutant: write at 415).
     - Update rc 75, rc 1, no body and a recorded failure each leave one line.
     - Two passes over one ahead tip keep the first `since=`; a moved tip resets it; a held PR writes none (mutant: stamp `since=` from the pass time).
     - `ledger.py`'s self-test: `KINDS["handoff-ahead"] == "derived"`, and that every kind `cloud_relay.sh` passes to `level_line` is in `KINDS`.
  5. **The tick at the boundary** (carry dr2-ahead-boundary).
     - `since=` 1200 s before the pass prints an unflagged `ahead:` line; 1201 s prints a flagged `OWED: … age=1201`. Mutants: `>=`, which flags 1200 s; and reading the pass time, which never flags.
     - A line with no `since=` prints flagged `REFUSED`.
     - Null: the line with no `handoff-ahead` kind in `KINDS` prints `REFUSED`, as today.
  6. `--arms handoff` runs only that arm, and the hold-file rc 0/1/2 cases hold (mutant: rc 2 as 1). `env_pass` carries `HPO_LEDGER_AGING`. Rendered step 5 names `beatd status`, the board and both counts, and no tick seat (mutant: restore "newest actionable lines").
  7. Measurement in the body: item 25's record-merge count over `git log --merges` for one UTC day after `28800999b`, against 2026-10-24's 19, with a flat-day null.
- **(c) The four rows, seat retirement and the policy text** (`roster_queue.py --cursor`; `bus.sh dispatch-owed`, `dispatched.lock`, `ledger.py owed-pairs`; `beatd.py watch`; the 60 s floors in `ci-watch.sh` and `proof_watch.py`; the digest's ROSTER and DISPATCH sections; `pulse.py` `STANDING = {"merge": 120}`, with a `RETIRED` map naming the job for tick, dispatch and roster, and its self-test at 475-477 comparing the contracts with `STANDING ∪ RETIRED`; `--seat-queue` of a retired seat refuses rc 2 naming its job; `standing-tick.md`, `standing-roster.md` and `standing-dispatch.md` each reduced to a retirement paragraph naming its job; their three `CLAUDE.md` rows; `orchestrator.md` §5; `nudge.md:113`; INSTRUMENTS.md 338, 355, 528 and 992; `sweep_template.md` steps 1b, 2, 3, 4 and 6). Controls:
  1. **Cursor.** A kill after op n's push: `interrupted <n> landed`, then n+1 is applied and n never again. A kill before the push: n is applied once. An unreadable landed state stops with `unresolved`. Null: an empty queue reads `ok`. Mutants: write the cursor before the op; skip `.inflight`. The stale `--worktree` of a killed run is removed before re-applying (carry dr2-inflight-worktree).
  2. A seeded owed item appears in the digest and in the retiring seat's report in the same cycle (item 11).
  3. The roster job lands a no-op-safe op on a scratch branch and refuses a seeded lint failure, which it never retries (item 23).
  4. **Dispatch.**
     - One `dispatch-owed` pass over a board with one `REVIEW OWED` (pr, head) the registry lacks adds one registry line and one `close reviewer-fire`; a second pass adds neither (item 33).
     - Concurrent `dispatch-owed` and `dispatch` for one pair mint once (mutant: drop `dispatched.lock`).
     - A board older than 1200 s, or absent, refuses rc 2 (mutant: treat it as empty).
  5. A watch request wakes its waiter once; `interval_s < 60` refuses. With the beat absent, `ci-watch.sh` and `proof_watch.py` each refuse a poll under 60 s (one mutant per script).
  6. Rendered sweep text names no train launch for the orchestrator (item 15). Step 2 carries `-C {{orch_checkout}}` on every `git ` (item 20; null: the old text fails; mutant drops `-C`).
  7. `pulse.py`: `--seat-queue tick=…` refuses rc 2 naming the `tick` job. Null: `merge=…` still reads its format. Mutant: leave tick in `STANDING`.
  8. **Hand-launch text.** None of the eight rewritten sites still tells a reader to start, loop or detach a beat job's script, by the §5 grep with its launch words over the rendered text. Null: the old text fails. Mutant: restore `nudge.md:113`.

  The policy text is folded into this PR's one owner review. `standing-merge.md` gets its Reads line (item 21) and Wait paragraph (item 17); `orchestrator.md` gets the context-rotation paragraph (item 13). Each retired seat stays running until its job has run beside it for one cycle, which is controls 2-4 compared live, before the merge (owner: "make sure the retirement of the standing seats dont cause you to run things inline"). Zero-headroom files pay each added line by cutting text.
- **(d) Adjacent carries**, measured against (c)'s retirement (verdict point 5).
  - **(d1) dismissed.** After (c) the one standing seat left is merge. Its liveness is already judged by `--seat-queue merge=` (pulse.py:48-53), and a duplicate merge seat writes nothing twice: its `train.sh add` is `ALREADY` for the live train, under the train's `QUEUE_LOCK` (merge_train.py:721, 845). Tick, roster and dispatch become beat jobs, each single-instance by its job lock and `beatd.lock` ((a)2). No `<seat>.alive` writer exists in the tree, and none is needed.
  - **(d2) the tick's seat liveness**, as approved in round 2: `_seat_procs` skips `--self-test`; `ALERT self-test-old` at 3600 s, with fixtures at 3660 and 3540 s; WORKERS reads `$HPO_BUS_STATE/dispatched`. It goes serial after (b), which also edits `orchestrator_tick.py`.
  - **(d3) dismissed, by measurement.** Item 19's three writers at `6d86acc90` are:
    - roster apply, `roster_queue.py run` → `roster_edit.py --push`: the `roster-queue` beat job after (c);
    - dispatch fire, `bus.sh` `dispatch` append at 479: the `dispatch` beat job plus the relay's call, both under `dispatched.lock` after (c);
    - merge_train queue read, `main` 5816 → `land` 1790 → `gh pr merge` 1814, spool `spool_read` 781: one live train per state dir, with `add` serialised by `QUEUE_LOCK` (721, 755).

    No writer remains seat-driven without a single-instance lock, so `seat_gen.py` would gate nothing.

## 7. Hot files, order, risks

- **Hot files:** `cloud_relay.sh`, `tick_loop.sh`, `orchestrator_tick.py` ((b), (d2)), `ledger.py` ((b), (c)), `bus.sh` ((c)), `sweep_template.md`, `orchestrator.md`, `pulse.py` ((c)).
- **Order:** (a) → (b) → (c); (d2) after (b). Before R10-ORCH-PLANPAGE.
- **Risks:**
  - A 3600 s handoff with one update per pass drains slowly; measured in (b).
  - The supervisor unit is host config the owner applies. Until then the beat runs under `daemonize.py`, and `status` prints `supervisor=none`.
  - A third concurrent fetcher can outlast two retries. It then fails as today, and `git-retry.log` shows it.
- **Owner decision pending:** item 28's (A) hourly cloud probe or (B) CI cron; default under silence is (A). decision: owner.

## 8. Round-3 answers to `810697a5a`

1. **Ref lock:** a retrying `git` shim on every beat job's `PATH`, measured against the two-real-fetcher race (§3 table, spike on this ref). (a)6 is replaced by the hook fixture, with its null and three mutants, and it reaches handoff, `update_pr.sh`, pitch and the train. Round 2's §1 row, "two layers", alternative 4's reason and risk 3 are replaced.
2. **`handoff-ahead`:** it is in `ledger.py` `KINDS` with its self-test. It is written only at an iteration's end with the PR still ahead, never on an rc 0 update. The tick prints it unflagged until 1200 s and flagged from 1201 s ((b)4, (b)5).
3. **Rows:** (b) lands seven rows whose argv exist at (b); (c) appends four with their flags. `phase` is dropped. Dispatch is `bus.sh dispatch-owed`, owned by the registry's owner.
4. **Hand launches:** the grep is keyed on every script name (§5), giving eleven sites, each disposed. `wt_sync.sh` refuses without `--beat` under `beatd.lock`, and `cloud_relay.sh --watch` joins the refusals. The `nudge.md:113` rewrite is in (c), which goes to owner approval at merge.
5. **(d):** the seats that survive (c) are merge only. (d1) is dismissed, and (d3) is measured and dismissed (§6 (d)); (d2) stands.

## Notes for the fixer

Carry items are numbered 1-35 in roster order at `8b434ef62`; the round-2 carries are keyed by their `dr2-` ids.
- Carry: R10-ORCH-BEATD (item 1)
- Carry: R10-ORCH-BEATD (item 2)
- Carry: R10-ORCH-BEATD (item 3)
- Carry: R10-ORCH-BEATD (item 4)
- Carry: R10-ORCH-BEATD (item 5)
- Carry: R10-ORCH-BEATD (item 6)
- Carry: R10-ORCH-BEATD (item 7)
- Carry: R10-ORCH-BEATD (item 8)
- Carry: R10-ORCH-BEATD (item 9)
- Carry: R10-ORCH-BEATD (item 11)
- Carry: R10-ORCH-BEATD (item 12)
- Carry: R10-ORCH-BEATD (item 13)
- Carry: R10-ORCH-BEATD (item 14)
- Carry: R10-ORCH-BEATD (item 15)
- Carry: R10-ORCH-BEATD (item 17)
- Carry: R10-ORCH-BEATD (item 18)
- Carry: R10-ORCH-BEATD (item 20)
- Carry: R10-ORCH-BEATD (item 21)
- Carry: R10-ORCH-BEATD (item 23)
- Carry: R10-ORCH-BEATD (item 24)
- Carry: R10-ORCH-BEATD (item 25)
- Carry: R10-ORCH-BEATD (item 26)
- Carry: R10-ORCH-BEATD (item 27)
- Carry: R10-ORCH-BEATD (item 28)
- Carry: R10-ORCH-BEATD (item 29)
- Carry: R10-ORCH-BEATD (item 31)
- Carry: R10-ORCH-BEATD (item 32)
- Carry: R10-ORCH-BEATD (item 33)
- Carry: dismissed: duplicate of item nine, already landed text (item 10)
- Carry: dismissed: moot after arm c, merge alone survives and seat-queue judges it (item 16)
- Carry: dismissed: measured at main, every remaining writer already single-instance after arm c (item 19)
- Carry: dismissed: moot after arm c, a doubled merge seat adds nothing twice (item 22)
- Carry: dismissed: behind the owner ruling in carry-201.json, not built until it is made (item 30)
- Carry: dismissed: duplicate of item thirty, same ruling gate (item 34)
- Carry: dismissed: a seat-ledger record with no build, the DEFER unaffected (item 35)
- The `level_rmw` holder is `tick_loop.sh`'s `RELAY_HOLDER` pattern (52, run at 76), which takes the lock and runs a child under it; `STUCK_PY` (477) is only a probe. Carry: R10-ORCH-BEATD (item dr2-holder-pattern)
- The heartbeat job calls `beatd.py status` itself, inside its own 60 s timeout, so a hung status call is bounded by the job. Carry: R10-ORCH-BEATD (item dr1-heartbeat-status-call)
- Answered in the design, kept for the fix review to check: (b)5's 1200/1201 fixtures (item dr2-ahead-boundary), (b)2 (item dr2-confirm-carry-dispose), (c)1's worktree removal (item dr2-inflight-worktree), (c)4's lock (item dr2-dispatch-double-mint), and `review_freeze` 380 moved under `handoff` (item dr2-380-citation). Carry: R10-ORCH-BEATD (item dr2-folded)

Item 1 (7) needs no build: inventory row M43 is part of the design's history, not a file in the tree. Parts (2) and (4b) have landed (`ledger.py` `postmerge-owed`). Part (3)'s freeze landed in the handoff arm (`07cbe6fe1`). Part (6) belongs to R10-ORCH-PLANPAGE.
