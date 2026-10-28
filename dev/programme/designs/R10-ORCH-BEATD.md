# R10-ORCH-BEATD design note (designer seat)

This is the group's architect note, extended (`dev/governance/roles/designer.md`). It lives on `design/R10-ORCH-BEATD` only and is never merged. Size L, lane IN, issue #2505 (concern B of the re-cut). It is the "one revision pass" the brief asks for: it re-measures the approved design at `archive/handoff/orch-machinery` `09174d94e` (`dev/audit/design/orch-machinery/DESIGN.md` §6.2, §6.5, §6.6, §8 Phase 1; round-3 review `review/orch-machinery-design` `0bd5d12f0`) against current main. It is not a new design.

**Read at.** Code: `origin/main` `aaf8af512c1fb9aeabdf58dbb5131928f432d4d1`. Roster: `origin/handoff/audit-r10-roster` `b367104780224d4b618a5866d0b501b5eae183c4`, with all 35 carries. No predecessor has a live head: R10-ORCH-DISPATCH-REG `bfc4a1e29`, R10-POLICY-FIXER-MD `662a3809c`, R10-ORCH-REVIEW-PACKET `eb2063218`, and R10-FLOW-ROSTER-FREEZE arm (a) `07cbe6fe1` (the roster still says `carries-open`) are each an ancestor of main (`git merge-base --is-ancestor`). Triage `dev/programme/triage/s6-batch45.md` P230 (V144) was read at `8c155fd43`, which is not on main.

## 1. Premises, re-measured

| design premise (09174d94e) | at `aaf8af512` |
|---|---|
| no supervisor; daemons launched by hand (S5, M30) | holds. `beatd.py` and `beatd.jobs.json` do not exist. `tools/audit/seat/daemonize.py` keeps no bookkeeping. `dev/README.md` draws `beatd` as if it existed. |
| relay is one job (B7) | moved. `cloud_relay.sh pass` runs four arms in one process (handoff, probe, confirm, stuck). `tools/audit/seat/tick_loop.sh` starts it detached through a flock holder (`<out>.relay.lock`). `held <pr>` and the review freeze (arm (a)) are already inside the handoff arm. |
| tick runs the heartbeat? | new since the design. `tools/audit/seat/tick_loop.sh` calls `timeout 60 heartbeat.sh --once`, and with `--sweep` it runs `merge_train.py sweep` (the AUTOTRAIN pitch). |
| ledger has no `postmerge-owed` (K17 (2)) | landed. `tools/audit/seat/ledger.py` `KINDS` has it, and `HPO_LEDGER_AGING` is read there. |
| seats are judged from a `workers.json` (§6.2) | half moved. `tools/audit/seat/orchestrator_tick.py` WORKERS still reads a workers JSON. R10-ORCH-DISPATCH-REG chose `$HPO_BUS_STATE/dispatched` (six fields) instead and built no JSON. |
| `state_docs.py beat` loops forever, so the job uses `--once` (N3) | holds. It takes no lock. A roster `git fetch` in the shared orchestrator checkout raced another fetch and killed the loop on 2026-10-25 (carry 28). |
| watchers keep a 60 s API floor (carry 14) | **false**. `tools/audit/seat/ci-watch.sh` sleeps a fixed 300 s, and `proof_watch.py --poll` defaults to 300 with no floor. |
| `pulse.py --seat-alive` | absent. Only `--seat-queue` exists. |
| `orchestrator_tick._seat_procs` excludes `--self-test` (carry 24) | it does not (lines 469-485). |

The approved design's job table, journal grammar, `beatd status` and the double-start rule still stand. Nothing the design relies on has been removed.

## 2. Owning seam

**`tools/audit/seat/beatd.py` (would be new) owns the schedule, supervision, per-job locks, timeouts, the journal and the digest. `tools/audit/seat/beatd.jobs.json` (would be new, data) owns the job table.** These modules only call the beat or are called by it, and none of them gains a loop:
- `tools/audit/seat/tick_loop.sh` becomes the tick job's one-shot command.
- `tools/audit/seat/cloud_relay.sh`, `tools/audit/seat/heartbeat.sh`, `tools/audit/seat/state_docs.py`, `tools/audit/seat/wt_sync.sh`, `tools/audit/seat/roster_queue.py`, `tools/audit/seat/merge_train.py`, `tools/audit/seat/ci-watch.sh` and `tools/audit/seat/proof_watch.py` are jobs and keep their contracts.
- `tools/audit/seat/sweep_template.md` reads `beatd status` and the digest.
- `tools/audit/seat/pulse.py` stays the off-host complement.

`tests/seam_map.json` maps only coordinator methods. `tests/layout.json`'s `tools` group (`tools/audit/seat/**`) classifies both new files. Wire the self-test by `selftest_wiring.py --check` (99/99 today).

**Design finding, scope (decision: orchestrator).** Ten carries are not concern B. Each has its own owning module and its own control, and none needs the beat to exist. Item 16 (`pulse.py --seat-alive`) and item 22 (`tools/audit/seat/pulse.py` DUPLICATE) belong to `tools/audit/seat/pulse.py`. Item 19 is `seat_gen.py`. Items 20 and 26 are sweep-text fixes. Item 21 adds Reads lines to the standing contracts. Item 24 and item 18's self-test-age alarm belong to `tools/audit/seat/orchestrator_tick.py` `_seat_procs`. Item 13 (context rotation) and item 35 (a record) complete the ten. The note designs them as arm (d) so that nothing is lost. The orchestrator may instead re-route them to their files' owners with `tools/audit/seat/roster_edit.py`. Either way, they are not a precondition for arms (a)-(c).

## 3. Shape

**Job table** (`beatd.jobs.json`, `{"version":1,"jobs":[…]}`). Each job has these keys: `name`, `argv` (repo-relative), `interval_s`, `timeout_s`, `heartbeat_s|null`, `env_pass` (list), `lock` (`job` or a named shared class), `kind` (`periodic|queue|watch`), `phase` (`a|b|c`). An unknown key, a missing key, an `interval_s` below 60 for `kind:"watch"`, or an unreadable file makes beatd refuse to start: rc 2, `beatd: REFUSE <reason>`, zero jobs run (B11). The self-test asserts that the code's built-in job names equal the table's names. That makes the table the data `R10-ARCH-DOCS` draws from (item 3).

| job | argv | interval/timeout | from |
|---|---|---|---|
| `tick` | `tick_loop.sh --once --no-relay --no-heartbeat --out $S/tick.txt` (`env_pass: HPO_LEDGER_AGING`) | 300/900 | §6.2, items 9, 11 |
| `relay-probe` | `cloud_relay.sh pass --arms probe,confirm,stuck` | 120/120 (first cut, N9-R) | §6.2 |
| `handoff` | `cloud_relay.sh pass --arms handoff` | 120/3600 | §6.2, items 1 (0), 4 |
| `heartbeat` | `heartbeat.sh --once --message "BEAT <status line>"` | 300/60 | items 1 (1), 5 |
| `state-docs` | `state_docs.py beat --once --apply --push --tip-file $S/beatd/state-docs.tip` (lock `orch-checkout`) | 300/300 | N3, item 28 |
| `wt-sync` | `wt_sync.sh --scratch …` (lock `orch-checkout`) | 900/600 | item 28 |
| `pitch` | `merge_train.py sweep` | 3600/900 | item 1 (1) |
| `roster-queue` | `roster_queue.py run … --queue $S/roster.queue --report $S/beatd/roster.report` | queue/600 | item 23 |
| `dispatch` | `bus.sh dispatch` per `REVIEW OWED:` line of the board | queue/300 | items 29, 33 |
| `ci-watch`, `proof-watch` | on demand: `beatd.py watch <job> -- <args>` | watch/budget | item 14 |

**Run.** `beatd.py run --state $S` takes `flock(LOCK_EX|LOCK_NB)` on `$S/beatd/beatd.lock`. A second instance prints `beatd: ALREADY RUNNING pid=<p>` and exits 75, which answers the double start. Each job runs on its own scheduler thread, so no job's run delays another job's schedule (item 1 (0)). A job runs in its own process group (`setsid`) under `$S/beatd/<job>.lock`. If that lock is held, the pass records `outcome=locked`. At the timeout the beat sends SIGTERM to the group, then SIGKILL after 10 s, and records `outcome=timeout`. A shared-class lock (`orch-checkout`) is waited on for at most 60 s, then `outcome=busy`. Only jobs that fetch in the shared checkout wait, so the fetch race of item 28 becomes serialised rather than fatal. At start the beat writes `START <utc> beatd pid= code=<HEAD sha>`. Each status call compares that SHA with `git ls-remote origin refs/heads/main` and prints `STALE-CODE behind=<n>` when they differ (item 8). The operating-system supervisor restarts `beatd.py run`. `beatd.py unit launchd|systemd` prints the unit text and installs nothing (item 1 (0)).

**Journal** (`$S/beatd/journal.log`, design §6.2 grammar). The beat writes `PASS <utc> <job> start= dur= outcome=ok|failed|timeout|locked|busy|unreadable rc= lines=`, plus `RUNNING <utc> <job> pid= elapsed=` every `heartbeat_s`. A job's last output line also goes to `$S/beatd/<job>.last`. For a hosted one-shot such as `tools/audit/seat/body_patch.sh` (items 6, 7), success is exit 0 together with a last line that matches `^body_patch: OK`.

**Status.** `beatd.py status [--json]` prints `beatd: RUNNING pid= code= behind=` or `beatd: DOWN`, then one line per job: `<job> ok|late|failed|timeout|never last=<utc> age=<s>`. A job is `late` when its age exceeds `interval + timeout`. The status also prints these alarms:
- `ALERT lock-owner-dead <lock> pid=`, item 18.
- `ALERT pulse-silent`: the jobs are healthy but `heartbeat.sh --watch` reads the pushed ref as STALE. That is item 2's control: healthy on the host while silent off it must alert.

rc is 0 when healthy, 1 on any alarm, late job or DOWN, and 2 when unreadable.

**Digest** (`$S/beatd/digest.txt`, rewritten after every pass). It has four sections, each prefixed by its source job:
- TICK: every `-> ` and `OWED` line of `tick.txt`, with their counts (item 26).
- ROSTER: `roster: <op> <group> pushed <sha>|refused <reason>` (item 23).
- DISPATCH: one line per registry append.
- BEAT: the status lines.

The orchestrator reads the digest and the ledger, and nothing else (item 12). **The double start** (B8): in the same pull request, `tools/audit/seat/sweep_template.md` step 5 reads `beatd status`, and `tools/audit/seat/tick_loop.sh` without `--once` refuses with rc 75 while `beatd.lock` is held.

**Flow, before and after.** Before, the sweep (an agent) restarts `tools/audit/seat/tick_loop.sh` under `tools/audit/seat/daemonize.py`. The loop starts the relay holder and calls `tools/audit/seat/heartbeat.sh`, and every loop is restarted by hand, sometimes twice. After, launchd or systemd starts `beatd.py run`, which runs the jobs concurrently and writes the journal and the digest. The sweep only reads `beatd status` and the digest, and queues lines to `roster.queue` and `dispatch.queue`.

**Invariants.**
- No job is an agent loop.
- Each job has one live instance.
- A job is never killed before its timeout.
- An unreadable table or journal is never a clean board.
- The beat writes no ledger event of its own: the handoff job keeps `tools/audit/seat/cloud_relay.sh`'s ledger calls (item 9), and dispatch writes only through `bus.sh dispatch` (item 33).
- There is no third is-main-red classifier (item 1 (5)).

## 4. Alternatives

1. **Keep `tools/audit/seat/tick_loop.sh` as the beat and add jobs to it.** It lost because the loop is serial: a 9-min handoff update holds the tick, and a 36-min one holds it for 36 min. The `relay.lock` holder only half-detaches the relay. The loop also has no per-job timeout and no supervisor.
2. **One process per job, each under `tools/audit/seat/daemonize.py` plus its own supervisor unit.** It lost on state ownership: about ten unit files, no single journal or status, and the shared-checkout race would need a cross-unit lock that no single owner holds.
3. **A per-job clone instead of the `orch-checkout` lock.** It lost because it multiplies the stale-code hazard of item 8 per clone.

## 5. Sibling sites

`git grep -n -E 'while :|while true|while True|--loop|--watch' -- 'tools/audit/seat/*.sh' 'tools/audit/seat/*.py'` lists the looping instruments.
- In scope: `tools/audit/seat/tick_loop.sh`, `tools/audit/seat/cloud_relay.sh`, `tools/audit/seat/heartbeat.sh`, `tools/audit/seat/state_docs.py`, `tools/audit/seat/ci-watch.sh`, `tools/audit/seat/proof_watch.py`, `tools/audit/seat/merge_train.py`.
- Out of scope, as one-shot or seat-run tools: `tools/audit/seat/bus.sh`, `tools/audit/seat/ci_critpath.py`, `tools/audit/seat/ci_probe.py`, `tools/audit/seat/gh_read.py`, `tools/audit/seat/pr_args.sh`, `tools/audit/seat/sweep_driver.py`, `tools/audit/seat/train.sh`, `tools/audit/seat/verify_eight.py`.

`git grep -c 'daemonize\.py' -- tools/audit/seat/sweep_template.md tools/audit/seat/INSTRUMENTS.md dev/governance/roles` returns 2, 3 and 1 (in `dev/governance/roles/standing-merge.md`). Each hand launch is rewritten to a beat job or a queue line.

The P230 loop list (`tools/audit/seat/tick_loop.sh`, `tools/audit/seat/state_docs.py`, `tools/audit/seat/wt_sync.sh`, the roster loop, and the relay that was missing from it) is exactly the job table. `tools/audit/seat/handover_prompt.py` renders it from `beatd.jobs.json`; it gets no second list.

## 6. Arms and evidence (each arm one PR, `dev/governance/roles/fixer.md` steps 2-8)

The finder's harness is the approved design's demonstrations, E4/E7 and S5, plus the 2026-10-25 recurrence evidence of item 28. No committed harness exists for the S5 double start: the evidence is the judge-style re-run that the fixer builds as `dev/audit/harnesses/r10_beatd_double_start.py` (would be new). The archscore target is **dS = 0**: `tools/audit/archscore/vector.py` reads only `custom_components/heatpump_optimizer`, which no arm touches. Run `score.py --diff origin/main HEAD` before and after, and it must not read worse.

- **(a) The beat** (`tools/audit/seat/beatd.py`, `tools/audit/seat/beatd.jobs.json`, `tools/audit/seat/INSTRUMENTS.md`).
  - Failing tests:
    1. A malformed table runs zero jobs and the old code reports nothing. Fixed: rc 2. Null control: a valid table runs.
    2. Two `run` instances leave both alive today. Fixed: the second exits 75. Null control: one instance runs.
    3. A job sleeping past its timeout is killed and recorded `timeout`. Null control: a job that finishes in time reads `ok`.
    4. A slow job does not delay a fast job's pass.
    5. Two `orch-checkout` jobs never overlap.
    6. `status` reports `late`, `DOWN`, `lock-owner-dead`, `pulse-silent` and `STALE-CODE`, each against a fixture. Null control: a healthy fixture prints no alarm.
  - Mutants: drop the instance flock; drop the killpg; compare `age > interval` without the timeout; let table parsing default to zero jobs. Each must fail its case.
- **(b) Jobs and the double start** (`tools/audit/seat/tick_loop.sh` `--no-relay`/`--no-heartbeat` and the refusal of loop mode under the beat lock; `cloud_relay.sh pass --arms`; `tools/audit/seat/sweep_template.md` step 5; `tools/audit/seat/handover_prompt.py` job list).
  - Controls:
    - `--arms handoff` runs only the handoff arm, and the hold-file rc 0/1/2 cases of item 4 still hold. A malformed hold file refuses the pass (mutant: treat rc 2 as 1).
    - Loop mode refuses while the beat lock is held. Null control: it runs when the lock is free.
    - The rendered sweep step 5 names `beatd status` and no `tools/audit/seat/tick_loop.sh` launch (mutant restores it).
    - `env_pass` carries `HPO_LEDGER_AGING` (mutant drops it).
  - Measurement: the item 25 record-merge count runs as a script over `git log --merges` for one UTC day after `28800999b`, against 2026-10-24's 19, with a flat-day null control. It goes in this PR's body.
- **(c) Seat retirement** (`roster-queue`, `dispatch`, `ci-watch`/`proof-watch`, and the digest; policy: `dev/governance/roles/standing-tick.md`, `dev/governance/roles/standing-roster.md`, `dev/governance/roles/standing-dispatch.md`, `dev/governance/roles/orchestrator.md` §5, and `tools/audit/seat/sweep_template.md` steps 2, 3, 4 and 6 queueing to the beat, item 15).
  - Controls:
    - A seeded owed item appears both in the digest and in the retiring seat's report on the same cycle (item 11).
    - The roster job lands a no-op-safe op on a scratch branch and refuses a seeded lint failure, which it never retries (item 23).
    - One dispatch pass over a handoff with no live dispatch adds one registry line and one `close reviewer-fire`, and a second pass adds neither (item 33).
    - A watch job wakes its waiter once, and its `interval<60` refuses.
    - The rendered sweep names no train launch for the orchestrator (item 15, one mutant).
  - Each seat stays until its job has run beside it for one full cycle (owner, verbatim: "make sure the retirement of the standing seats dont cause you to run things inline"). The policy files sit at zero headroom: pay by cutting text. The owner's approving review is required.
- **(d) Adjacent carries** (§2 finding): `tools/audit/seat/pulse.py` `--seat-alive` and DUPLICATE (items 16, 22), `tools/audit/seat/seat_gen.py` (would be new; 19), the `_seat_procs` `--self-test` exclusion and self-test age (24, 18), WORKERS reading `dispatched` (32), the sweep `-C` pin and board text (20, 26), the Reads and Wait paragraphs (21, 17), and context rotation (13). Each item keeps the control and mutant that its carry already states.

No golden fixture moves, and both claim files stay byte-identical.

## 7. Hot files, order, risks

- **Hot files:** `tools/audit/seat/cloud_relay.sh`, `tools/audit/seat/tick_loop.sh`, `tools/audit/seat/sweep_template.md`, `dev/governance/roles/orchestrator.md`. Serial position: after the four predecessors (all merged) and before R10-ORCH-PLANPAGE, whose page renders from the ledger and the digest.
- **Order:** (a) → (b) → (c). (d) is independent.
- **Risks:**
  - A 3600 s handoff bound with one update per pass drains slowly. The drain is measured in (b).
  - The supervisor unit is host config the owner applies. Until it is applied, the beat runs under `tools/audit/seat/daemonize.py` and `status` prints `supervisor=none`.
- **Owner decision pending:** item 28 asks (A) an hourly cloud probe or (B) a CI cron. The default under silence is (A), the existing ANDON pair (`tools/audit/seat/heartbeat.sh` plus `tools/audit/seat/pulse.py`). This note builds no third detector: that is item 27's cost test result. decision: owner.

## Notes for the fixer

Carry items are numbered 1-35 in roster order at `b36710478`.
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
- Carry: R10-ORCH-BEATD (item 14)
- Carry: R10-ORCH-BEATD (item 15)
- Carry: R10-ORCH-BEATD (item 18)
- Carry: R10-ORCH-BEATD (item 23)
- Carry: R10-ORCH-BEATD (item 25)
- Carry: R10-ORCH-BEATD (item 26)
- Carry: R10-ORCH-BEATD (item 27)
- Carry: R10-ORCH-BEATD (item 28)
- Carry: R10-ORCH-BEATD (item 29)
- Carry: R10-ORCH-BEATD (item 31)
- Carry: R10-ORCH-BEATD (item 32)
- Carry: R10-ORCH-BEATD (item 33)
- Carry: R10-ORCH-BEATD (item 13)
- Carry: R10-ORCH-BEATD (item 16)
- Carry: R10-ORCH-BEATD (item 17)
- Carry: R10-ORCH-BEATD (item 19)
- Carry: R10-ORCH-BEATD (item 20)
- Carry: R10-ORCH-BEATD (item 21)
- Carry: R10-ORCH-BEATD (item 22)
- Carry: R10-ORCH-BEATD (item 24)
- Carry: dismissed: duplicate of item nine, already landed text (item 10)
- Carry: dismissed: behind the owner ruling in carry-201.json, not built until it is made (item 30)
- Carry: dismissed: duplicate of item thirty, same ruling gate (item 34)
- Carry: dismissed: a seat-ledger record with no build, the DEFER unaffected (item 35)

Item 1 (7) needs no build: inventory row M43 is part of the design's history, not a file in the tree. Parts (2) and (4b) have landed (`tools/audit/seat/ledger.py` `postmerge-owed`; R10-ORCH-LEDGER). Part (3)'s freeze has landed in the handoff arm (`07cbe6fe1`), and the handoff job inherits it. Part (6) belongs to R10-ORCH-PLANPAGE.
