# R10-ORCH-BEATD design note (designer seat)

This is the group's architect note, extended (`dev/governance/roles/designer.md`). It lives on `design/R10-ORCH-BEATD` only and is never merged. Size L, lane IN, issue #2505 (concern B of the re-cut). It re-measures the approved design at `archive/handoff/orch-machinery` `09174d94e` (`dev/audit/design/orch-machinery/DESIGN.md` §6.2, §6.5, §6.6, §8 Phase 1; round-3 review `review/orch-machinery-design` `0bd5d12f0`) against current main. **Round 2 of 3**: it answers the six points of `design-verdict/R10-ORCH-BEATD` `d93e1b1f2` (§8 maps each), and designs arm (d) concretely under the orchestrator's ruling that the ten adjacent carries stay in this group and round.

**Read at.** Code: `origin/main` `6349205b61660f41f94015c352f6612d236e105d`; `git diff aaf8af512 6349205b6 -- tools/audit/seat/` is empty, so every line number of round 1 and of the verdict still holds. Roster: `origin/handoff/audit-r10-roster` `aed3322bb` (the reviewer's read; it differs from round 1's `b36710478` only in other groups' fields). No predecessor has a live head (round 1's `merge-base --is-ancestor` reads stand).

## 1. Premises, re-measured

| design premise (09174d94e) | at `6349205b6` |
|---|---|
| no supervisor; daemons launched by hand (S5, M30) | holds. `beatd.py` and `beatd.jobs.json` do not exist; `tools/audit/seat/daemonize.py` keeps no bookkeeping. |
| relay is one job (B7) | moved. `cloud_relay.sh pass` runs four arms serially in one process (line 510). `tools/audit/seat/tick_loop.sh` starts it detached under a flock holder and waits at most `HPO_TICK_RELAY_WAIT` (30 s), so **tick and relay fetches already overlap today**. |
| tick runs the heartbeat? | new: `tick_loop.sh` calls `timeout 60 heartbeat.sh --once`; with `--sweep` it runs `merge_train.py sweep`. |
| ledger has `postmerge-owed` (K17 (2)) | landed (`tools/audit/seat/ledger.py`). |
| seats judged from a `workers.json` | half moved: `orchestrator_tick.py` WORKERS still reads a workers JSON; R10-ORCH-DISPATCH-REG chose `$HPO_BUS_STATE/dispatched`. |
| state beat loops forever, so the job uses `--once` | holds; it takes no lock, and its fetch died on `cannot lock ref` in the shared checkout (carry 28). |
| the item-28 failure is git's ref lock | **reproduced** with git 2.38.1 in a scratch repo: a held `refs/remotes/origin/main.lock` makes `git fetch` print item 28's exact `error: cannot lock ref 'refs/remotes/origin/main'`; with `core.filesRefLockTimeout=5000` and the lock freed at 1 s, the same fetch exits 0 and moves the ref. |
| watchers keep a 60 s floor (carry 14) | **false**: `ci-watch.sh` sleeps 300 s fixed; `proof_watch.py --poll` has no floor. |
| `pulse.py --seat-alive`; `_seat_procs` excludes `--self-test` | both absent (`pulse.py` has only `--seat-queue`; `orchestrator_tick.py:470-485`). |

## 2. Owning seam

**`tools/audit/seat/beatd.py` (would be new) owns the schedule, supervision, per-job and class locks, timeouts, the journal, the status and the digest; `tools/audit/seat/beatd.jobs.json` (would be new, data) owns the job table.** Each job's script keeps the state it already owns, and none gains a loop: `cloud_relay.sh` owns `<log>.level` (and its lock, §3), `roster_queue.py` owns the roster queue cursor, `bus.sh` owns the dispatch registry, `orchestrator_tick.py` owns the board, `pulse.py` stays the off-host complement. `tools/audit/seat/sweep_template.md` reads `beatd status` and the digest. `tests/layout.json`'s `tools` group classifies both new files; wire the self-test by `selftest_wiring.py --check`.

Scope: the ten adjacent carries stay in this group and round (orchestrator ruling, round 2); arm (d) designs them, §6.

## 3. Shape

**Job table** (`beatd.jobs.json`, `{"version":1,"jobs":[…]}`). Keys: `name`, `argv` (repo-relative), `cwd` (`orch` = the beat's own checkout, or a path), `interval_s`, `timeout_s`, `heartbeat_s|null`, `env_pass`, `class` (`null` or `orch-checkout`), `kind` (`periodic|watch`), `phase` (`b|c`). An unknown or missing key, `interval_s < 60` on `kind:"watch"`, or an unreadable file: rc 2, `beatd: REFUSE <reason>`, zero jobs run (B11). `kind:"queue"` is gone: both queue jobs poll on an interval, so `late` has one meaning (§3 Status).

Measured per job (fetch sites by `grep -n 'fetch'` at `6349205b6`; "shared" = the orchestrator checkout or a worktree of it, which share one ref store):

| job | argv | cwd | fetches in shared ref store | interval/timeout | class |
|---|---|---|---|---|---|
| `tick` | `tick_loop.sh --once --no-relay --no-heartbeat --out $S/tick.txt` (`env_pass: HPO_LEDGER_AGING`) | orch (`--checkout` default `ROOT`, orchestrator_tick.py:4016) | yes: 418, 643, 707, 1194, 1559, 2058 | 300/900 | `orch-checkout` |
| `relay-probe` | `cloud_relay.sh pass --arms probe,confirm,stuck` | orch (git in cwd) | yes: 190, 204, 313, 380 | 120/120 | `orch-checkout` |
| `handoff` | `cloud_relay.sh pass --arms handoff` | orch | yes: 413, 427, and `update_pr.sh` 47, 50 (it `cd`s to the common checkout, line 42) | 120/3600 | none: ref-lock retry |
| `heartbeat` | `heartbeat.sh --once --message "BEAT <status line>"` | `git -C $HERE` | no: `--once` is commit-tree plus push (33-35); fetch is `--watch` only (41) | 300/60 | none |
| `state-docs` | `state_docs.py beat --once --apply --push --tip-file $S/beatd/state-docs.tip` | orch (`--checkout`) | yes: `roster_fetch_spec` (227-244, 338-352) | 300/300 | `orch-checkout` |
| `wt-sync` | `wt_sync.sh --scratch $S` | common dir (`R`, line 13) | yes: 26 | 900/600 | `orch-checkout` |
| `pitch` | `merge_train.py sweep` | orch | yes, and the detached `train.sh` it starts outlives the job | 3600/900 | none: ref-lock retry |
| `roster-queue` | `roster_queue.py run --cursor $S/beatd/roster.cursor --queue $S/roster.queue --report $S/beatd/roster.report --edit-checkout orch …` | orch for the edit checkout; its own `--lint-clone` | yes: 110 (edit checkout); 123 is its own clone | 120/600 | `orch-checkout` |
| `dispatch` | `bus.sh dispatch` for each `REVIEW OWED:` (pr, head) the registry does not hold | orch | yes: 443 | 300/300 | `orch-checkout` |
| `ci-watch`, `proof-watch` | `beatd.py watch <job> -- <args>` | caller's | no (API polls) | watch/budget | none |

**Two layers close item 28 (verdict point 2).** (i) **The ref store.** Its owner is git, and the shared store is written by fetchers no beat lock can reach: `update_pr.sh` (by the relay or by hand), a train, the orchestrator, and every fixer worktree. So `beatd.py` exports to every job `GIT_CONFIG_COUNT=2`, `core.filesRefLockTimeout=30000`, `core.packedRefsTimeout=30000`, inherited by `update_pr.sh` and the train; `beatd.py unit` prints the same two `git config` lines for the owner to apply to the shared checkout, beside the supervisor unit. (ii) **The class.** Every job that fetches in the shared store and is bounded by ≤ 900 s takes `orch-checkout` (`$S/beatd/orch-checkout.lock`) for its whole run, waits for it at most 60 s, then records `outcome=busy`. `handoff` and `pitch` are left out, by measurement: holding the class for a 3600 s handoff run would make the tick `busy` for that hour, which item 1 (0) forbids, and the class could not cover their children anyway. They rely on (i). Nothing reads `FETCH_HEAD` in the shared store (`git grep FETCH_HEAD`: only `cloud_dispatch.py` 406-431 in its own `work` clone, and self-tests), so concurrent fetches clobbering it costs nothing.

**`<log>.level` (verdict point 1).** `relay-probe` and `handoff` stay two jobs, so a long handoff never delays the probe. The race moves to its owner. `<log>.level` has **two** read-modify-write sites: `level_set` (line 169) and `dispose` (line 262), which the orchestrator runs by hand while the relay may be mid-pass. Both become calls of one helper, `level_rmw <awk-filter> [lines-file]`, which takes an exclusive flock on `<log>.level.lock` inside `cloud_relay.sh` around its read, `awk`, write and `mv`. The lock is taken through a `python3 -I -c` fcntl holder of the kind the file already uses (`STUCK_PY`, line 477), since macOS has no `flock(1)`. The lock is held for milliseconds, so the pair keeps "no job delays another". `HPO_RELAY_LEVEL_PAUSE` (self-test only) sleeps between read and write so the race is deterministic.

**First-seen memory for the handoff alarm (point 4).** A `handoff-update` line is re-stamped every pass (`level_line` takes `date -u`), so its age is always fresh and measures nothing. The handoff arm therefore writes one more kind, `OWED <utc> handoff-ahead refs/heads/handoff/<topic> <hs> #<pr> since=<utc>`, for every PR whose handoff tip is not an ancestor of its head (cloud_relay.sh:415), except a held one, which already has its own `handoff-held` line. `since=` is copied from the existing `handoff-ahead` line of the same ref and sha in `<log>.level`, and is the pass's time otherwise. That case also covers `update_pr.sh` returning 75 forever, which today writes no line.

**Run.** `beatd.py run --state $S` takes `flock(LOCK_EX|LOCK_NB)` on `$S/beatd/beatd.lock`; a second instance prints `beatd: ALREADY RUNNING pid=<p>` and exits 75. `beatd.py held --state $S` is the one reader of that lock for other scripts: rc 0 and `held pid=<p>` when it is held, rc 1 when free. Each job runs on its own scheduler thread, in its own process group, under `$S/beatd/<job>.lock` (`outcome=locked` when held). At the timeout: SIGTERM to the group, SIGKILL 10 s later, `outcome=timeout`. Start writes `START <utc> beatd pid= code=<HEAD sha>`; `status` prints `STALE-CODE behind=<n>` against `git ls-remote origin refs/heads/main` (item 8). `beatd.py unit launchd|systemd` prints unit text and installs nothing.

**Journal** (`$S/beatd/journal.log`): `PASS <utc> <job> start= dur= outcome=ok|failed|timeout|locked|busy|unreadable rc= lines=`, plus `RUNNING <utc> <job> pid= elapsed=` every `heartbeat_s`; a job's last line goes to `$S/beatd/<job>.last`. A hosted one-shot such as `body_patch.sh` (items 6, 7) succeeds on exit 0 with a last line matching `^body_patch: OK`.

**Status.** `beatd.py status [--json]`: `beatd: RUNNING pid= code= behind=` or `beatd: DOWN`, then `<job> ok|late|failed|timeout|busy|never last=<utc> age=<s>`. A periodic job is `late` when `age > interval_s + timeout_s`; a watch job with no live instance is `idle`, never `late`. An empty queue pass is `outcome=ok lines=0`, so it reads `ok`. Alarms:
- `ALERT lock-owner-dead <lock> pid=` (item 18 b).
- `ALERT pulse-silent` (item 2).
- `ALERT handoff-ahead #<pr> age=<s>`: a `handoff-ahead` line in `<log>.level` with `now − since > 1200` (item 18 a). The age is taken from `since=`, never from the line's pass time.

rc is 0 when healthy, 1 on any alarm, late job or DOWN, and 2 when unreadable.

**Digest** (`$S/beatd/digest.txt`, rewritten after every pass): TICK (every `-> ` and `OWED` line of `tick.txt`, with counts; item 26), ROSTER (`roster: <op> <group> pushed <sha>|refused <reason>|interrupted <n> <state>`), DISPATCH (one line per registry append), BEAT (the status lines). The orchestrator reads the digest and the ledger, and nothing else (item 12).

**Queue cursors (point 6).** The applier owns its cursor, never the beat.
- **Roster.** `roster_queue.py run --cursor FILE` (new; `run FIRST LAST` stays for hand use) applies lines `cursor+1 … EOF` of the append-only queue. Before each op it writes `FILE.inflight` = `<n> <sha256 of the line>` (write `.part`, then rename). After the op's report line it writes `FILE` = `<n>` and removes `.inflight`. On start, an `.inflight` left by a killed pass is resolved before anything else, and never blindly re-run:
  - For `append-carry @file`, `readback` against the roster ref decides. If it landed: `interrupted <n> landed`, and the cursor advances. If not: the line is applied once.
  - For `set-stage` and `set-pr`, the roster JSON at the ref is read for the target value, with the same two outcomes.
  - Any other op: `interrupted <n> unresolved`, the cursor stays, and the queue stops until the orchestrator queues `resolve <n> landed|retry`. That stop is an OWED line in the digest.
  
  So a killed line is neither re-applied nor skipped. The orchestrator only appends to the queue.
- **Dispatch.** No cursor: `$HPO_BUS_STATE/dispatched` (bus.sh:479) is the consumed-set. The job dispatches each `REVIEW OWED:` (pr, head) the registry does not hold. A kill before the registry append leaves nothing, and the next pass redoes it. A kill after the append but before the ledger close leaves `reviewer-fire` open, so the tick shows it OWED. The job never closes it itself, because item 33 forbids a second writer.

**Double start (point 3).** Every loop mode in scope refuses with rc 75 and `<tool>: REFUSE beatd running pid=<p>` when `beatd.py held` returns 0: `tick_loop.sh` without `--once`, `cloud_relay.sh pass --loop`, and `state_docs.py beat` without `--once`. The beat's own argv are one-shot, so they are never refused. When `beatd.py` is absent, a loop runs as today.

**Invariants.** No job is an agent loop. Each job has one live instance. A job is never killed before its timeout. An unreadable table, journal or level is never a clean board. The beat writes no ledger event of its own. There is no third is-main-red classifier (item 1 (5)). Every write to `<log>.level` is serialised by its owner's lock.

## 4. Alternatives

1. **Extend `tick_loop.sh`.** Lost: the loop is serial, has no per-job timeout and no supervisor; a 36-min handoff holds the tick.
2. **One unit per job under `daemonize.py`.** Lost: about ten units, no single journal, and no single owner of a cross-job lock.
3. **One shared `relay` class for relay-probe and handoff** (verdict point 1, first option). Lost: the probe would wait behind a 3600 s handoff, which is the coupling item 1 (0) removes. The `level_set` lock costs milliseconds.
4. **`orch-checkout` on every fetching job, handoff and pitch included.** Lost: the tick goes `busy` for a whole handoff run, and the class still misses `update_pr.sh`, the train, hand fetches and the worktrees.
5. **A per-job clone.** Lost: `update_pr.sh` `cd`s to the common checkout whatever the job's cwd (line 42), so isolation would not hold, and every clone multiplies item 8's stale-code hazard.

## 5. Sibling sites

`git grep -n -E 'while :|while true|while True|--loop|--watch' -- 'tools/audit/seat/*.sh' 'tools/audit/seat/*.py'`.
- In scope: `tick_loop.sh`, `cloud_relay.sh` (`pass --loop`), `heartbeat.sh`, `state_docs.py` (`beat`), `ci-watch.sh`, `proof_watch.py`, `merge_train.py`.
- Out, as one-shot or seat-run tools: `bus.sh`, `ci_critpath.py`, `ci_probe.py`, `gh_read.py`, `pr_args.sh`, `sweep_driver.py`, `train.sh`, `verify_eight.py`.

The level race class is `git grep -n 'mv -f "\$lv' -- 'tools/audit/seat/*.sh'`: two sites, `cloud_relay.sh:169` (`level_set`) and `:262` (`dispose`), both behind `level_rmw`. The tick only reads the level, and `mv` is atomic, so a reader never sees half a file. The fetch class is the table above. `git grep -c 'daemonize\.py'` over `sweep_template.md`, `INSTRUMENTS.md` and `dev/governance/roles` returns 2, 3 and 1; each hand launch becomes a beat job or a queue line. `handover_prompt.py` renders the P230 loop list from `beatd.jobs.json`.

## 6. Arms and evidence (each arm one PR; `fixer.md` steps 2-8)

Harness: the approved design's E4/E7 and S5, and item 28's recurrence evidence. There is no committed harness for the S5 double start, so the fixer builds `dev/audit/harnesses/r10_beatd_double_start.py` (would be new). archscore target: dS = 0 (`vector.py:98` reads only `custom_components/heatpump_optimizer`). Run `score.py --diff origin/main HEAD` before and after. No golden fixture moves, and both claim files stay byte-identical.

- **(a) The engine** (`beatd.py`, `INSTRUMENTS.md`; **no production table**, point 5). Fixture tables live in the self-test's temp directory. `run` with no `beatd.jobs.json` refuses rc 2, so no beat can run before (b). Failing tests, each with its null control and mutant:
  1. A malformed table runs zero jobs. Null: a valid table runs. Mutant: parsing defaults to zero jobs.
  2. A second `run` exits 75. Null: one instance runs. Mutant: drop the instance flock.
  3. An over-time job is killed and recorded `timeout`. Null: an in-time job reads `ok`. Mutant: drop the killpg.
  4. A slow job does not delay a fast one.
  5. **Two fixture jobs of class `orch-checkout` never overlap.** Each appends `start`/`end` with a timestamp to one file, and the test asserts no interleave. Null: two class-less jobs do overlap. Mutant: one job's class is dropped from the fixture, and the test must fail.
  6. **Ref-lock retry.** In a scratch repo, a job fetching while a ref lock is held for 1 s exits 0. Null: the same fetch without the beat's env prints `cannot lock ref` (the §1 premise). Mutant: drop `GIT_CONFIG_COUNT`.
  7. `status` reports `late`, `DOWN`, `busy`, `lock-owner-dead`, `pulse-silent` and `STALE-CODE`, each against a fixture. A watch job with no instance reads `idle`. Null: a healthy fixture prints no alarm. Mutant: `age > interval` without the timeout.
  8. **`handoff-ahead`**: a level fixture with `since=` 21 min ago and a pass time 1 min ago prints `ALERT handoff-ahead`. Null: `since=` 19 min ago prints none. Mutants: compare `≥ 1260`, or read the pass time instead of `since=`; the 21-min fixture kills both.
  9. `held` returns rc 0 while a fixture holds `beatd.lock`, and 1 when it is free.
- **(b) The table, the jobs and the double start** (`beatd.jobs.json` lands here with every row; `tick_loop.sh --no-relay --no-heartbeat` and loop-mode refusal; `cloud_relay.sh pass --arms`, `level_set`'s lock, `handoff-ahead` with `since=`, and `pass --loop` refusal; `state_docs.py beat` loop refusal; `sweep_template.md` step 5 with item 26's board text; `handover_prompt.py`). The self-test asserts that the code's job names equal the table's, and that every row's `argv[0]` is a tracked file whose new flags its own self-test accepts. Controls:
  1. **`level_set` race (point 1).** Two concurrent `level_set` calls of kinds `probe-ref` and `handoff-update`, the first paused by `HPO_RELAY_LEVEL_PAUSE=1` between read and write. Today one kind is lost: the test fails at `6349205b6`. Fixed: both kinds are present. A second case runs `dispose` of one `probe-ref` line concurrently with a paused `level_set handoff-update`; both effects must survive. Null: two serial calls keep both. Mutant: drop the lock; or route `dispose` around `level_rmw`.
  2. **Loop refusal (point 3).** One case per script: `tick_loop.sh` (no `--once`), `cloud_relay.sh pass --loop` and `state_docs.py beat` (no `--once`) each exit 75 with `REFUSE beatd running` while a fixture holds `beatd.lock`. Null: with the lock free, each runs one iteration, using `--interval` 1 and a stub that exits. Mutant per script: delete the check. The `--once` and `pass --arms` forms run under the lock (null for the beat's own argv).
  3. **`since=` carried.** Two handoff passes over the same ahead tip keep the first pass's `since=`. A moved tip resets it. A held PR writes no `handoff-ahead`. Mutant: stamp `since=` from the pass time.
  4. `--arms handoff` runs only that arm, and the item 4 hold-file rc 0/1/2 cases hold (mutant: treat rc 2 as 1). `env_pass` carries `HPO_LEDGER_AGING` (mutant drops it). The rendered step 5 names `beatd status`, the board path and both counts, and no `tick_loop.sh` launch or `tick-owed` (mutant restores "newest actionable lines").
  5. Measurement in the body: item 25's record-merge count, as a script over `git log --merges` for one UTC day after `28800999b`, against 2026-10-24's 19, with a flat-day null.
- **(c) Seat retirement and the policy text** (`roster_queue.py --cursor`; the `dispatch`, `ci-watch` and `proof-watch` jobs; the digest; `standing-tick.md`, `standing-roster.md`, `standing-dispatch.md`, `orchestrator.md` §5, and `sweep_template.md` steps 2, 3, 4 and 6 queueing to the beat). Controls:
  1. **Cursor (point 6).** A run killed after op n's push but before its cursor write: the next pass reports `interrupted <n> landed`, applies n+1, and never applies n again. A run killed before op n's push: the next pass applies n once. An op whose landed state cannot be read stops the queue with `unresolved` and does not advance. Null: an empty queue reads `ok`. Mutants: write the cursor before the op; or skip `.inflight` resolution.
  2. A seeded owed item appears in the digest and in the retiring seat's report in the same cycle (item 11).
  3. The roster job lands a no-op-safe op on a scratch branch and refuses a seeded lint failure, which it never retries (item 23).
  4. One dispatch pass over a handoff with no live dispatch adds one registry line and one `close reviewer-fire`; a second pass adds neither (item 33).
  5. A watch job wakes its waiter once; `interval<60` refuses.
  6. The rendered sweep names no train launch for the orchestrator (item 15).
  7. The rendered step 2 carries `-C {{orch_checkout}}` on every `git ` command (item 20; null: the old text fails; mutant drops `-C`).

  **Policy text folded into this PR's one owner review:** each surviving `standing-*.md` gets its Reads line (item 21) and its Wait paragraph (item 17), and `orchestrator.md` gets the context-rotation paragraph (item 13), each control as its carry states. Each seat stays until its job has run beside it for one cycle (owner, verbatim: "make sure the retirement of the standing seats dont cause you to run things inline"). These files sit at zero headroom: pay each line by cutting text.
- **(d) Adjacent carries** (orchestrator ruling: in this group, in round 10). Each part is one PR, independent of (a)-(c) except where noted.
  - **(d1) `pulse.py --seat-alive` and DUPLICATE** (items 16, 22; `pulse.py`, `sweep_template.md` step 1b, after (c) for the step text). `--seat-alive SEAT=FILE[:MIN]` reads `<seat>.alive` mtimes and one entry per seat id: `ok`, `STOPPED` past MIN or the seat's STANDING cadence, `UNREADABLE` when absent, `DUPLICATE seat <role>: <id> <id>` when two ids of one role are fresh. Failing tests: a stale alive reads `STOPPED` (today the flag is refused, rc 2); two fresh ids read `DUPLICATE`. Nulls: a fresh alive reads ok; one fresh id plus one stale id reads no DUPLICATE; the old `--seat-queue` arm still reads its format. Mutants: drop the mtime comparison; delete the count.
  - **(d2) The tick's seat liveness** (items 24, 18 c, 32; `orchestrator_tick.py`).
    1. `_seat_procs` skips a command containing `--self-test`. Failing test: a stubbed `merge_train.py --self-test` beside one real train prints the race flag today. Null: two real trains still flag. Mutant: put it back.
    2. `ALERT self-test-old <pid> age=`: the proc stub gains elapsed seconds (`ps -o pid=,etime=,command=`), and a `--self-test` process older than 3600 s flags. Fixtures at 3660 s and 3540 s (the null). Mutant on the bound.
    3. WORKERS reads `$HPO_BUS_STATE/dispatched` (six fields, older four-field lines readable). A reviewer line at the PR's current head is live; one at a moved head reads `DONE?`. Null: an empty registry prints no seat. Mutant: key on field 3 instead of fields 1-2.
  - **(d3) `seat_gen.py`** (item 19; would be new). First, measure the tracked writers per standing seat at main, and wire only those. `bump <seat>` and `check <seat> <gen>`; `check` with a lower generation exits 1 with `SUPERSEDED`. Failing test: a writer given a superseded generation writes nothing. Null: the current generation exits 0 and writes. Mutant on the comparison.

## 7. Hot files, order, risks

- **Hot files:** `cloud_relay.sh`, `tick_loop.sh`, `sweep_template.md`, `orchestrator.md`, `orchestrator_tick.py` (d2), `pulse.py` (d1).
- **Order:** (a) → (b) → (c) → (d1). (d2) and (d3) are independent; (d2) goes serial with any other open `orchestrator_tick.py` head. Before R10-ORCH-PLANPAGE.
- **Risks:**
  - A 3600 s handoff with one update per pass drains slowly; measured in (b).
  - The supervisor unit and the two `git config` lines are host config the owner applies. Until then the beat runs under `daemonize.py`, and `status` prints `supervisor=none`.
  - `core.filesRefLockTimeout` turns a lost race into a wait of up to 30 s; a fetch still refused after that prints its error as today.
- **Owner decision pending:** item 28's (A) hourly cloud probe or (B) CI cron; default under silence (A), the existing ANDON pair; no third detector (item 27's cost test). decision: owner.

## 8. Round-2 answers to `d93e1b1f2`

1. **level_set race:** a flock inside `cloud_relay.sh` (`level_rmw`), not a shared class (§3; alternative 3). It covers the second writer the verdict did not list, `dispose` at line 262. Failing test (b)1.
2. **Fetchers:** per-job table with checkout and measured fetch sites (§3). Two layers: `orch-checkout` on the six bounded fetchers, and ref-lock retry for all of them, including `handoff`, `pitch` and their children. Why not a clone: alternative 5. Tests (a)5, whose mutant drops a job's class, and (a)6.
3. **Loop modes:** `cloud_relay.sh pass --loop` and `state_docs.py beat` without `--once` refuse rc 75 through `beatd.py held`. Null and per-script mutant in (b)2.
4. **Handoff ahead > 20 min:** a `handoff-ahead` kind with a carried `since=`, and `ALERT handoff-ahead`. The 21-min fixture, the 19-min null and two mutants are (a)8; `since=` carrying is (b)3.
5. **Arm order:** (a) ships no production table; every row lands in (b) with its flags; (b)'s self-test checks every `argv[0]`.
6. **Cursor:** the roster cursor is `roster_queue.py`'s (`--cursor`, `.inflight`, resolution rules); the dispatch registry is its own consumed-set. Kill semantics and `late` are in §3, and tests in (c)1. `kind:"queue"` is removed.

## Notes for the fixer

Carry items are numbered 1-35 in roster order at `aed3322bb`.
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
- Carry: R10-ORCH-BEATD (item 16)
- Carry: R10-ORCH-BEATD (item 17)
- Carry: R10-ORCH-BEATD (item 18)
- Carry: R10-ORCH-BEATD (item 19)
- Carry: R10-ORCH-BEATD (item 20)
- Carry: R10-ORCH-BEATD (item 21)
- Carry: R10-ORCH-BEATD (item 22)
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
- Carry: dismissed: behind the owner ruling in carry-201.json, not built until it is made (item 30)
- Carry: dismissed: duplicate of item thirty, same ruling gate (item 34)
- Carry: dismissed: a seat-ledger record with no build, the DEFER unaffected (item 35)
- Item 14 puts the 60 s floor inside `ci-watch.sh` and `proof_watch.py` as well as in the table validation, so a watcher started outside the beat keeps it; add one mutant per script. Carry: R10-ORCH-BEATD (item dr1-watch-floor-in-script)
- The `heartbeat` job calls `beatd.py status` itself, inside its own 60 s timeout, so a hung status call is bounded by the job and never by a beat thread. Carry: R10-ORCH-BEATD (item dr1-heartbeat-status-call)

Item 1 (7) needs no build: inventory row M43 is part of the design's history, not a file in the tree. Parts (2) and (4b) have landed (`ledger.py` `postmerge-owed`; R10-ORCH-LEDGER). Part (3)'s freeze has landed in the handoff arm (`07cbe6fe1`). Part (6) belongs to R10-ORCH-PLANPAGE.
