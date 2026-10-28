# R10-ORCH-BEATD design note (designer seat)

This is the group's architect note (`dev/governance/roles/designer.md`). It lives on `design/R10-ORCH-BEATD` only and is never merged. Size L, lane IN, issue #2505 (concern B of the re-cut), on the critical path. It re-measures the approved design at `archive/handoff/orch-machinery` `09174d94e` (`dev/audit/design/orch-machinery/DESIGN.md` §6.2, §6.5, §6.6, §8 Phase 1) against current main.

**Re-cut after the third `revise`** (`design-verdict/R10-ORCH-BEATD` `1d5cdad0f`, on round 3 `f0f046929`). By `design-review.md` there is no fourth note. This is the minimal shape the fixer starts from: **arm (a) is specified in full and goes first; (b) and (c) are scoped, and each carries its review points as the verdicts wrote them.** One PR per arm, serial (a) → (b) → (c), never swarmed (triage P245). Rounds 1-3 approved most of (b) and (c); that text is not re-argued here. Where this note is silent on (b) or (c), round 3's text at `f0f046929` §3 and §6 is the reference, and the points below override it.

**Read at.** Code: `origin/main` `6d86acc90`. `git diff --stat 6d86acc90 0b8f8b585 -- dev/governance tools/audit/seat .claude CLAUDE.md AGENTS.md` is empty, so every citation holds at `0b8f8b585`. Spike: `dev/programme/designs/R10-ORCH-BEATD.spike/` on this ref (never merged).

## 1. Owning seam

- **`tools/audit/seat/beatd.py`** (would be new) owns the schedule, supervision, per-job and class locks, timeouts, the journal, `status`, `held`, and each job's environment, including the resolved real git.
- **`tools/audit/seat/beatd.jobs.json`** (would be new, data) owns the job table. Arm (a) ships no production table.
- **`tools/audit/seat/beatd_shims/git`** (would be new) owns the fetch retry. It sits in a directory of its own that only `beatd.py` prepends (revise point 2).
- Each job's script keeps the state it already owns, and none gains a loop. `pulse.py` stays the off-host complement.

`tests/layout.json`'s `tools` group and `tests/closure.py` classify the new files; the self-test is wired by `selftest_wiring.py --check`.

## 2. Arm (a): the engine and the shim — one PR, first

**Scope.** `beatd.py`, `beatd_shims/git`, and their `INSTRUMENTS.md` entries. Nothing else: no job row, no edit to any job's script, no policy text. Fixture tables live in the self-test's temp directory. The archscore target is dS = 0 (`vector.py:98` reads only `custom_components/heatpump_optimizer`); run `score.py --diff origin/main HEAD` before and after. No golden fixture moves, and both claim files stay byte-identical.

**Job table** (`{"version":1,"jobs":[…]}`). Keys: `name`, `argv` (repo-relative), `cwd` (`orch` = the beat's checkout, or a path), `interval_s`, `timeout_s`, `heartbeat_s|null`, `env_pass`, `class` (`null` or `orch-checkout`), `kind` (`periodic|watch`). An unknown or missing key, `interval_s < 60` on `kind:"watch"`, or an unreadable file gives rc 2 with `beatd: REFUSE <reason>`, and zero jobs run.

**Run.** `beatd.py run --state $S` holds `$S/beatd/beatd.lock`; a second run exits 75 with `ALREADY RUNNING`. Each job runs on its own thread and process group under `$S/beatd/<job>.lock`. At its timeout it gets SIGTERM, then SIGKILL 10 s later. A class job takes `$S/beatd/<class>.lock` for its whole run, waits at most `class_wait_s` (default 60), and then records `outcome=busy`. Start records `code=<HEAD sha>`. Each job's env gets `HPO_BEATD_JOB=<name>`, `HPO_REAL_GIT`, `HPO_GIT_SHIM_LOG=$S/beatd/git-retry.log`, and `PATH` with `beatd_shims` first.

**Journal, status, held.**
- The journal records `RUNNING` lines and `PASS <utc> <job> … outcome=ok|failed|timeout|locked|busy|unreadable`.
- `status` reports `late` (`age > interval_s + timeout_s`), `idle` for a watch job with no instance, and `DOWN`, plus the alarms `ALERT lock-owner-dead` (item 18 b), `ALERT pulse-silent` (item 2) and `STALE-CODE behind=` (item 8). rc is 0, 1 or 2.
- `held` is `beatd.lock`'s one reader for other scripts: rc 0 held, 1 free. (b) and (c) build every refusal on it.

**The real git, resolved once (revise point 2).** Round 3's rule, "the first `git` on `PATH` outside its own directory", compared strings and looped on a relative entry, a trailing slash, and two shim copies (`1d5cdad0f` `evidence/shim_discovery.out`). The re-cut rule:
- `beatd.py` resolves the real git once at start, from its own `PATH` before it prepends the shim directory, canonicalises it, and refuses rc 2 if that file is a shim. It exports the result as `HPO_REAL_GIT`.
- The shim uses `HPO_REAL_GIT` when it is executable and not a shim. Otherwise it walks `PATH`. An empty entry means `.`. It skips every candidate that is a shim and takes the first survivor, canonicalised by `cd … && pwd -P`, then exports it so that children never walk again.
- "Is a shim" is a marker, line 2 `# hpo-git-shim`, read with shell builtins only (`read`), so it does not depend on `PATH` holding `head` or `grep`. A copy anywhere, under any spelling, is recognised.
- No real git: `git shim: no real git on PATH`, rc 127. The shim never `exec`s itself.

**Reach (revise point 2).** The shim lives in `tools/audit/seat/beatd_shims/`, never in `tools/audit/seat/shims/`. That keeps it out of the orchestrator's sweep, which puts `tools/audit/seat/shims` first on `PATH` (`sweep_template.md:51`, a relative entry), and out of `roster_queue.py:95-97`'s prepend. It reaches exactly the `PATH`-resolved `git` of a beat job's process tree. `git grep -nE '/usr/(local/)?bin/git' -- tools/audit/seat` finds no absolute git. `seat_venv.sh --install-shims` copies only `seat-python*` (line 250).

**Retry** (approved in round 3, unchanged). The subcommand is found by skipping `-C`, `-c`, `--git-dir`, `--work-tree` and `--namespace` with their values, and any other leading `-` option. Anything but `fetch` or `pull` is `exec`'d unchanged. A `fetch` or `pull` whose stderr holds `cannot lock ref` is re-run at most `HPO_GIT_RETRIES` (default 2) more times, 1 s and then 2 s apart. Only the last attempt's stderr is printed. Each retry appends `<utc> retry=<n> rc=<rc> <sub>` to `HPO_GIT_SHIM_LOG`. `beatd.py` keeps `GIT_CONFIG_COUNT`/`core.filesRefLockTimeout=30000` in the job env. A fetch is idempotent, and a pull whose fetch failed has merged nothing.

**Spike, run on this host** (macOS, `/bin/bash` 3.2.57, git 2.38.1; `race.out`, `discovery.out`):

| case | spike at this ref | round 3's shim (`f0f046929`) |
|---|---|---|
| race B: shim, no env / shim + env | rc 0, 2 / 1 retries | same |
| race B: no shim (± env), or `HPO_GIT_RETRIES=0` | rc 1 | same |
| `git --version`: absolute, one copy | rc 0 | rc 0 |
| relative entry | rc 0 | rc 124 (loop) |
| trailing slash | rc 0 | rc 124 |
| two shim copies | rc 0 | rc 124 |
| duplicate entry | rc 0 | rc 0 |
| `HPO_REAL_GIT` names a shim copy | rc 0 | rc 0 (ignored) |
| no real git on `PATH` | rc 127, one line | rc 124 |

`race.sh` now runs under bash 3.2: the empty env array is expanded as `${e[@]+"${e[@]}"}` (carry dr3-bash32).

**Failing tests, each with its null control and mutant.** Every fixture runs under `/bin/bash` 3.2 on macOS, with no bash-4 construct, and no `set -u` empty-array expansion (dr3-bash32).
1. A malformed table runs zero jobs. Mutant: parsing defaults to zero jobs.
2. A second `run` exits 75. Mutant: drop the instance flock.
3. An over-time job reads `timeout`, and an in-time one reads `ok`. Mutant: drop the killpg.
4. A slow job does not delay a fast one.
5. Two `orch-checkout` jobs never interleave their `start`/`end` lines. Null: two class-less jobs do overlap. Mutant: drop one job's class. A third job past `class_wait_s` records `busy`.
6. **The two-fetcher race.** The verdict's hook fixture: fetch A holds `refs/remotes/origin/main.lock` for 3 s, and B starts 1 s later as a beat job.
   - Fixed: B exits 0, `origin/main` equals upstream, and `git-retry.log` has at least one line.
   - Null: B with the beat's env but no shim on `PATH` exits 1 with `cannot lock ref`.
   - Mutants: `HPO_GIT_RETRIES=0`; beatd stops prepending `beatd_shims`; the shim drops `-C` from its option skip (the fixture runs `git -C c fetch`).
   - B through a child (`bash -c 'git -C c fetch -q origin'`) proves inheritance. `git status` through the shim leaves `git-retry.log` empty. `git fetch` from a missing remote fails once with git's own message and no retry.
   - **Discovery (revise point 2).** `discovery.sh`'s cases each return within 5 s, with `git --version` rc 0: a relative entry, a trailing slash, two shim copies in two directories, a duplicate entry, and `HPO_REAL_GIT` naming a shim copy. With no real git on `PATH`, the shim returns rc 127. Mutant: round 3's string compare, which gives rc 124 on three of the cases. A second mutant has the marker test call `head`, which loops on the no-git case.
   - `beatd.py run` refuses rc 2 when its own resolved git is a shim.
7. `status` reports `late`, `DOWN`, `busy`, `idle`, `lock-owner-dead`, `pulse-silent` and `STALE-CODE`, each against a fixture. Null: a healthy fixture prints no alarm. Mutant: `age > interval` without the timeout.
8. `held` returns rc 0 while a fixture holds `beatd.lock`, and 1 when it is free.

**Out of (a), deferred.** The heartbeat argv (dr3-heartbeat-argv), the class-wait measurement (dr3-class-wait) and the `handoff-ahead` rc 0 case (dr3-ahead-after-rc0) go to (b). The P241 dispatch case (dr3-p241-record-skip) and `pulse.py`'s seat names (revise point 3) go to (c). (a) needs none of them: it runs no production row.

## 3. Arm (b): the seven rows, the level and the double start — one PR, after (a)

**Scope** as round 3 §6 (b) at `f0f046929`: `beatd.jobs.json` with the seven rows `tick`, `relay-probe`, `handoff`, `heartbeat`, `state-docs`, `wt-sync`, `pitch`; `tick_loop.sh --no-relay --no-heartbeat` and its loop refusal; `cloud_relay.sh pass --arms`, `level_rmw` with keep and `since=`, `handoff-ahead`, and the refusals of `pass --loop` and `--watch`; `wt_sync.sh --beat` and its refusal; the `state_docs.py beat` refusal; `ledger.py` `KINDS`, `AHEAD_OWED_S` and `ahead_due`; `orchestrator_tick.py:749-754`; `sweep_template.md` step 5. Its controls (b)1-(b)7 stand as written there. The self-test asserts that every row's `argv[0]` is tracked and that its own `--help` or self-test accepts the row's flags. Each script's `INSTRUMENTS.md` entry is updated in the PR that changes its flags.

**Added by the re-cut:**
- **`state_docs.py --push` while the beat runs (revise point 1, mechanism).** A top-level `--push` exits 75 with `state_docs: REFUSE beatd running pid=<p>: the beat's state-docs job pushes` while `beatd.py held` returns 0 and `HPO_BEATD_JOB` is not `state-docs`. `beat`'s internal `main(common + ["--push"])` (265) runs inside the job and is not refused. `--mirror` without `--push` is never refused, so a seat still refreshes its local mirror. Control (b)8: with a fixture holding `beatd.lock`, a hand `--push` exits 75 and pushes nothing. Null: the lock is free, and one push lands on a bare-repo fixture. Mutants: delete the check; key it on `held` alone, which also refuses the job's own push.
- **Heartbeat argv (dr3-heartbeat-argv).** The row is `beatd.py heartbeat --state $S`. That subcommand computes the status line in-process and runs `heartbeat.sh --once --message "BEAT <line>"` inside the job's 60 s timeout. This replaces round 3's placeholder argv and the dr1 note's assumption that `heartbeat.sh` calls status itself. The every-row flag check covers it. Mutant: the row's argv carries a literal `<status line>`.
- **`handoff-ahead` after an rc 0 update (dr3-ahead-after-rc0).** After the head read, the handoff arm tests `merge-base --is-ancestor "$hs" "$nh"`. When that fails, it writes the `handoff-ahead` line even though the update returned 0. A failed update keeps its `handoff-update` line, flagged at once. The 1200 s `handoff-ahead` line written beside it is not wanted, because one alarm per cause is enough: rc ≠ 0 writes `handoff-update` only. Control in (b)4: an rc 0 update whose stub head does not contain `hs` leaves one `handoff-ahead` line. Null: a stub head that contains it leaves none. Mutant: skip the ancestor test.
- **Class wait (dr3-class-wait).** Before landing the rows, measure the tick's pass duration at main over one day of `TICK-PASS` lines. If the 90th percentile exceeds 60 s, drop `relay-probe` from `orch-checkout`, because the shim now covers its fetch race. Otherwise keep it and record the figure in the body. A longer `class_wait_s` is the fallback only if the class is still needed. The figure goes in the PR body, with its command.

## 4. Arm (c): the four rows, seat retirement and the policy text — one PR, after (b)

**Scope** as round 3 §6 (c) at `f0f046929`: `roster_queue.py --cursor`; `bus.sh dispatch-owed`, `dispatched.lock` and `ledger.py owed-pairs`; `beatd.py watch`; the 60 s floors in `ci-watch.sh` and `proof_watch.py`; the digest's ROSTER and DISPATCH sections; `pulse.py` `STANDING = {"merge": 120}` with a `RETIRED` map; `--seat-queue` of a retired seat refuses rc 2 naming its job; `standing-tick.md`, `standing-roster.md` and `standing-dispatch.md` each reduced to a retirement paragraph; their three `CLAUDE.md` rows; `orchestrator.md` §5; and the rewrites of §5 below. Its controls (c)1-(c)7 stand as written there. Each retired seat stays running until its job has run beside it for one cycle, before the merge (owner: "make sure the retirement of the standing seats dont cause you to run things inline"). The policy text goes to the owner's one approving review.

**Added by the re-cut:**
- **`pulse.py` names jobs, not retired seats (revise point 3).** `seat_of` (200-211) routes through `RETIRED`. A STOPPED opener reads `job dispatch:`, a STOPPED non-merge verdict reads `job dispatch:`, a merge verdict still reads `seat merge:`, and a STOPPED state-beat reads `job state-docs:` (`ARM_SEAT`, 92; the prefix at 219). Control (c)9: one fixture per arm (opener, verdict-merge, verdict-other, state-beat), each asserting its prefix. Mutant: leave `ARM_SEAT` as it is. The pulse self-test that compares the contracts with `STANDING ∪ RETIRED` also asserts that every `ARM_SEAT` value and every `seat_of` return is a key of one of them.
- **P241, one owed-decider (dr3-p241-record-skip).** `bus.sh dispatch-owed` takes its pairs only from the board, through `ledger.py owed-pairs`, and the board's `REVIEW OWED` lines are `review_owed`'s. Triage P241's rule, that `review_owed` skips `record/` and autofix PRs, therefore reaches dispatch with no second derivation. `bus.sh` adds no owed predicate of its own. (c)4 gains a case: once P241 has landed, a board built from an open `record/` or autofix PR yields no dispatch. Mutant: a `bus.sh`-side owed filter that ignores the board.
- **Hand-run text (revise point 1, text).** §5's rewrite set, with control (c)8 widened to it.

## 5. Hand launches and hand runs, every line disposed (revise point 1)

Round 3's filter missed `run` and `--push`. The re-cut disposes of **the whole name grep**, not a filtered subset:

```
P='tick_loop\.sh|cloud_relay\.sh|heartbeat\.sh|state_docs\.py|wt_sync\.sh|merge_train\.py|train\.sh|roster_queue\.py|ci-watch\.sh|proof_watch\.py|daemonize\.py|orchestrator_tick\.py'
git grep -n -E "$P" 6d86acc90 -- dev/governance tools/audit/seat/sweep_template.md tools/audit/seat/INSTRUMENTS.md .claude CLAUDE.md AGENTS.md
```

It prints 70 lines at `6d86acc90`, and the same 70 at `0b8f8b585`. The verdict's launch-word filter gives 19 of them, and widened with `\brun` it gives 30. Every line of the 70 falls in one of the classes below. The rewrite and the class sum are 23 + 47 = 70.

**Rewritten in (c): 23 lines.** Each one tells a seat to run, loop, detach or restart a beat job's script, or describes that run as a seat's.

| site | today | (c) text |
|---|---|---|
| `nudge.md:89`, `nudge.md:109` | run `state_docs.py` with its push flag and the mirror | "refresh the mirror with `state_docs.py --mirror ~/hpo-orch/state`; the beat's `state-docs` job pushes" |
| `standing-merge.md:13` | `state_docs.py --push` after each merge | "after each merge, report `set-stage owed …`; the beat's `state-docs` job pushes the state docs" |
| `sweep_template.md:63` | step 4: `state_docs.py --push --mirror` | `--mirror` only, plus the same clause |
| `nudge.md:113` | start a `wt_sync.sh` loop detached | "the beat's `wt-sync` job runs it; `beatd.py status` shows it" |
| `sweep_template.md:59` | `update_pr.sh` detached per handoff | step 2: the `handoff` job |
| `sweep_template.md:61` | the train sweep, detached | step 3: the `pitch` job (item 15) |
| `sweep_template.md:65` | restart the tick seat | step 5 (landed in (b)); (c) removes the restart clause |
| `standing-tick.md:11`, `standing-dispatch.md:14` | the seat's own instrument | the retirement paragraph naming the job |
| `INSTRUMENTS.md:316`, `:338`, `:355` | `cloud_relay.sh --watch` and `pass --loop`, detached | "the `relay-probe` and `handoff` jobs run `pass --arms`; both loop modes refuse while the beat runs" |
| `INSTRUMENTS.md:528` | `tick_loop.sh --sweep` every 1800 s | "the `pitch` job runs `sweep`" |
| `INSTRUMENTS.md:981`, `:982`, `:984`, `:992`, `:996` | the `tick_loop.sh` loop, run detached | "the `tick` job runs `--once --no-relay --no-heartbeat`; the loop refuses while the beat runs" |
| `INSTRUMENTS.md:1007`, `:1011` | `tick_loop.sh` calls `heartbeat.sh --once`; the beat will retire that call | "the `heartbeat` job runs `beatd.py heartbeat`"; `--watch` stays the owner's off-host task |
| `INSTRUMENTS.md:958` | the standing roster seat's queue runner | "the `roster-queue` job's runner, `run --cursor`" |
| `INSTRUMENTS.md:1058` | `state_docs.py beat` on a loop | "the `state-docs` job runs `beat --once`; the loop refuses while the beat runs" |

**Stay: 47 lines**, in four classes.
- **Describes an instrument, and tells no seat to launch a beat job's script** (36): `INSTRUMENTS.md` 84, 179, 213, 278, 296, 297, 321, 394, 428, 488, 493, 497, 527, 531, 557, 632, 643, 681, 702, 761, 773, 781, 805, 841, 845, 950, 998, 1014, 1034, 1039, 1042, 1134; `orchestrator.md` 235, 267, 277; `sweep_template.md:40`. Line 702, "Its driver is `tick_loop.sh`", stays true, because the `tick` job's argv is `tick_loop.sh`.
- **The surviving merge seat's or the orchestrator's own train** (5): `nudge.md:41`, `nudge.md:52`, `standing-merge.md:8`, `standing-merge.md:10`, and `fixer.md:7` (a fixer's one CI watcher). `merge_train.py run` and `batch` are no beat argv. A second train beside `pitch` writes nothing twice: `train.sh add` is `ALREADY` for a live train, under `QUEUE_LOCK` (`merge_train.py:721`, `:845`).
- **One-shot, not a beat job's mode** (3): `nudge.md:101` (`ci-watch.sh` one-shot, which exits), `nudge.md:105` (reads `state_docs.py`'s default ref and runs nothing), and `.claude/workflows/audit-plan.js:68` (a score run under `daemonize.py`).
- **A filed carry record, history** (3): `.claude/workflows/carry-1921.json` 16, 17, 18.

**Control (c)8, widened.** For each of the 23 sites, a fixture holds the round-3 phrase it replaces, and the rendered text must no longer contain it. Re-running the whole grep must print exactly the 47 kept lines, by file and text, plus the 23 rewritten ones. A new line that names a beat job's script fails until it is classed. Null: the old text fails. Mutants: restore `nudge.md:109`, then `standing-merge.md:13`, each failing alone. The two state-docs hand runs are closed twice: by (b)8's refusal in mechanism, and by this text.

## 6. Hot files, order, risks

- **Order:** (a) → (b) → (c), one PR each, serial. (d2), the tick's seat liveness approved in round 2 (`_seat_procs` skips `--self-test`; `ALERT self-test-old` at 3600 s with 3660/3540 s fixtures; WORKERS reads `$HPO_BUS_STATE/dispatched`), goes after (b). (d1) and (d3) stay dismissed (round 3 §6 (d)). All of this lands before R10-ORCH-PLANPAGE.
- **Hot files:** (a) touches only new files and `INSTRUMENTS.md`. (b) and (c) share `cloud_relay.sh`, `tick_loop.sh`, `orchestrator_tick.py`, `ledger.py`, `bus.sh`, `state_docs.py`, `sweep_template.md`, `orchestrator.md` and `pulse.py`.
- **Risks:**
  - A third concurrent fetcher can outlast two retries. It then fails as today, and `git-retry.log` shows it.
  - The supervisor unit is host config that the owner applies. Until then the beat runs under `daemonize.py`, and `status` prints `supervisor=none`.
  - A 3600 s handoff with one update per pass drains slowly. That is measured in (b).
- **Owner decision pending:** item 28's (A) hourly cloud probe or (B) CI cron. The default under silence is (A). decision: owner.

## 7. The third verdict's points, as carried

1. **Hand runs** → (b)8, the `state_docs.py --push` refusal, and (c)'s 23 rewrites with (c)8 widened (§5). Every one of the 70 lines is disposed.
2. **Shim discovery and reach** → (a): resolve once, skip by marker, rc 127 with no real git, and a directory of its own. (a)6 gains the four verdict cases plus three more; the mutant is the string compare. Measured on this ref (`discovery.out`).
3. **`pulse.py` seat names** → (c)9, and the self-test widened to `ARM_SEAT`.

## Notes for the fixer

Carry items are numbered 1-35 in roster order at `8b434ef62`; the round-2 and round-3 carries are keyed by their `dr2-` and `dr3-` ids. Each `dr3-` carry names the arm that owns it; arm (a) owns only dr3-shim-discovery and dr3-bash32.
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
- The heartbeat job computes its status line inside its own 60 s timeout, so a hung status call is bounded by the job; the mechanism is now `beatd.py heartbeat` (item dr3-heartbeat-argv). Carry: R10-ORCH-BEATD (item dr1-heartbeat-status-call)
- Answered in the design, kept for the fix review to check: (b)5's 1200/1201 fixtures (item dr2-ahead-boundary), (b)2 (item dr2-confirm-carry-dispose), (c)1's worktree removal (item dr2-inflight-worktree), (c)4's lock (item dr2-dispatch-double-mint), and `review_freeze` 380 moved under `handoff` (item dr2-380-citation). Carry: R10-ORCH-BEATD (item dr2-folded)
- Arm (a). The shim resolves real git once: `HPO_REAL_GIT` from `beatd.py`, else a PATH walk that skips every candidate carrying the line-2 marker, read by builtins only; rc 127 when none is found; the shim lives in `beatd_shims/`, which only `beatd.py` prepends. (a)6 gains the relative, trailing-slash, two-copy and duplicate cases, each within 5 s, plus the poisoned `HPO_REAL_GIT` and no-git cases; the mutant is round 3's string compare (spike `discovery.sh`). Carry: R10-ORCH-BEATD (item dr3-shim-discovery)
- Arm (a). Every fixture runs under macOS `/bin/bash` 3.2: no empty-array expansion under `set -u` (`${e[@]+"${e[@]}"}`), no bash-4 construct. The spike `race.sh` is fixed and re-run here. Carry: R10-ORCH-BEATD (item dr3-bash32)
- Arm (b). `state_docs.py --push` refuses rc 75 while `beatd.py held` returns 0 and `HPO_BEATD_JOB` is not `state-docs`; `--mirror` alone is never refused; control (b)8 with null and two mutants (§3). Arm (c). The 23 rewrites of §5 and the widened (c)8 over all 70 lines. Carry: R10-ORCH-BEATD (item dr3-hand-runs)
- Arm (b). The heartbeat row's argv is `beatd.py heartbeat --state $S`, which runs `heartbeat.sh --once --message "BEAT <line>"` with the line computed in-process; the every-row flag check tests it. Carry: R10-ORCH-BEATD (item dr3-heartbeat-argv)
- Arm (b). After the head read, `merge-base --is-ancestor "$hs" "$nh"` failing on an rc 0 update writes `handoff-ahead`; an rc != 0 update writes `handoff-update` only, never also a 1200 s `handoff-ahead`. Carry: R10-ORCH-BEATD (item dr3-ahead-after-rc0)
- Arm (b). Measure the tick's pass duration at main before landing the rows; past a 60 s 90th percentile, drop `relay-probe` from `orch-checkout` (the shim covers its race), else keep it and record the figure and its command in the body. Carry: R10-ORCH-BEATD (item dr3-class-wait)
- Arm (c). `seat_of` routes through `RETIRED`: opener and non-merge verdict read `job dispatch:`, state-beat reads `job state-docs:`, a merge verdict `seat merge:`; one fixture per arm; mutant leaves `ARM_SEAT`; the self-test covers `ARM_SEAT`'s values against `STANDING ∪ RETIRED`. Carry: R10-ORCH-BEATD (item dr3-pulse-seat)
- Arm (c). `bus.sh dispatch-owed` takes pairs only from the board via `ledger.py owed-pairs`, so triage P241's `review_owed` skip of `record/` and autofix PRs reaches dispatch with no second owed-decider; (c)4 gains the case that such a board yields no dispatch once P241 has landed. Carry: R10-ORCH-BEATD (item dr3-p241-record-skip)

Item 1 (7) needs no build: inventory row M43 is part of the design's history, not a file in the tree. Parts (2) and (4b) have landed (`ledger.py` `postmerge-owed`). Part (3)'s freeze landed in the handoff arm (`07cbe6fe1`). Part (6) belongs to R10-ORCH-PLANPAGE.
