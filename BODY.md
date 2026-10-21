rca: R10-RCA-ORCH-CONTINUITY -- the programme stops silently with its host; `pulse.py` reads liveness from origin

Root-cause seat for group R10-RCA-ORCH-CONTINUITY, class `N-silent-stop`. The record is `dev/audit/rca/R10-RCA-ORCH-CONTINUITY.md`, and this body is a short form of it. Every number below comes from GitHub alone: refs, merge history, REST and #201. The orchestrator host's files (`SEATS.md`, the tick log) are cited from #201, never measured.

- **Instances, re-verified (4 in round 10):**
  - 2026-10-16 session kill (takeover note 6216882536).
  - 2026-10-17 "nothing was running" (6240942713). The brief did not list this one; the class search found it.
  - 2026-10-20 crash (6285467757).
  - 2026-10-21 host reboot (6310926491). The reboot itself cost about 15 min. The `review/2527` blocked verdict sat 7.7 h, and the merges went unrecorded. Both happened while the host was still up and no session turn ran after 23:44Z.
- **Corrections to the brief:**
  - 2026-10-18 is not an instance. The session was alive (23 tvofi comments on #201, 05:17Z–23:20Z). The missed handoffs were `bus.sh orphans` failing open, which belongs to `N-orphaned-handoff` (R10-RCA-HANDOFF-SLIP).
  - The nine stranded handoffs all predate the last opening, so they are the orphan record's standing backlog, not I4's.
- **Cause:** every consumer is a process or a turn on one host, and nothing on origin records it. `daemonize.py` keeps no bookkeeping. The only watchdog, sweep step 5, runs inside the session it watches. A stop is silence, and silence reads as "nothing owed".
- **Process state: (a).** No process watched the session or the host from outside it.
- **Class search:** six consumers.
  - Covered here: opener, verdict router/train, state beat.
  - Not covered: the per-merge #201 record, the tick loop and `wt_sync`. For each, the record says why and who owns it.
  - The replay also found the state beat silent in four 2026-10-19 windows that no comment mentions.
- **Cost test:**
  - Defect: 4.8 h per occurrence × 0.63/day = 3.0 h/day.
  - Countermeasure: 8.2 s per run. That is 3.3 min/day hourly off-host, or 20–39 min/day per sweep on-host.
- **Countermeasure:** `tools/audit/seat/pulse.py`. It judges each consumer by its owed input on origin, so its verdict is the same off the host:
  - a handoff with no pull request that arrived after the newest opening (`bus.sh orphans`, invoked);
  - a verdict still at its open pull request's head;
  - the oldest main move the state ref has not followed.

  It fails closed: an input it cannot read is `UNREADABLE`, never ok. Its self-test is wired into `instrument-self-tests`, sweep step 5 runs it, and `INSTRUMENTS.md` lists it. `dev/audit/harnesses/pulse_replay.py` replays it over round 10.
- **Owner's call (the barrier):** the class owes a barrier. The barrier is an off-host scheduled run that alarms, and this seat cannot land it. The options:
  - (A, recommended) an hourly scheduled cloud probe.
  - (B) an hourly CI cron, which puts `pulse.py` and `bus.sh` on the required-check enforcement surface.

  Until one of them runs, the register records `detector`.

No policy file, lint class or rules entry is added (decision 0012). `governance.yml` is code-owned; this PR adds one self-test step to it.

## Head

33f6c201f4f0814f4570c7441f43b175528a8154 (base `origin/main` `0cc148b2f80fe224ffe2c504b29fd4f0908183df`; figures taken 2026-10-21 09:00Z-09:40Z).

## Mutation proof

Each predicate in `tools/audit/seat/pulse.py` was deleted in a copy, then `--self-test` was run on the copy. All 20 base checks, plus the unread-state check added after M4, pass unmutated.

| mutant | what it does | result |
|---|---|---|
| M0 | inert comment edit (null mutant) | 20 checks, 0 failed |
| M1 | backlog test `if now - h * 3600 > last:` → `if True:` | 4 failed (backlog counted / 4 h starved / opening after arrival / summary) |
| M2 | consumed-verdict head test → presence only | 1 failed ("a verdict whose pull request merged or whose head moved is consumed") |
| M3 | `oldest_unfollowed` → `max(main_times)` | 1 failed ("the state-beat age is the oldest main move the state ref has not followed") |
| M4 | state arm `mt is None or st is None` dropped | the self-test raises `TypeError`, exit 1 |
| M5 | unread last opening `if last is None:` → `if False:` | 1 failed ("an unread last opening is UNREADABLE, never ok") |
| M6 | skew guard `None if t > now` dropped | 1 failed ("a stamp ahead of the clock is never aged and is named skew") |
| M7 | exit 2 for unreadable dropped | 1 failed ("--snapshot exits 1 on a stop, 2 on unreadable, 0 on a healthy board") |

Wiring: before the `governance.yml` step, `selftest_wiring.py --check` printed `UNWIRED tools/audit/seat/pulse.py`. After it, the check prints `38 self-testing, 38 wired, 0 unwired`.

## Null control

- **Self-test:** the healthy fixture reads ok on all three arms, exit 0, as does the I4 fixture after the takeover consumed it. The defect fixtures read STOPPED, exit 1.
- **Replay:** `pulse_replay.py` with `--opener-h 1000 --state-min 100000` reads 0 windows on both arms. At the default bounds it reads 25 opener samples (2026-10-16 08:45Z–14:45Z) and 37 state-beat samples in 5 windows.
- **State-beat bound:** 198 of 215 main moves since 2026-10-15 18:08Z were followed within 30 min (p90 19.2 min). The smallest of the other 17 is 49.2 min, so the 45 min bound fires on none of the healthy latencies.
- **Live:** at 09:18Z, the dumped live snapshot re-judged with `--verdict-h 100 --opener-h 1000` reads 0 stopped, exit 0.

## Figures

- `python3 -I tools/audit/seat/pulse.py --self-test`: 21 checks, 0 failed.
- `python3 -I tools/audit/seat/pulse.py --repo tvofi/heatpump_optimizer --dump <file>` at 09:18Z:
  - opener ok, 6 older than the last opening;
  - verdict STOPPED: #2526 merge `baa75f58`, 3.6 h. The session is holding #2526 for a main merge (6312035865), which is a deliberate hold, so this is the stated limit.
  - state-beat ok;
  - exit 1.
- Run time, the same command three times: 7.7–8.2 s; `bash tools/audit/seat/bus.sh orphans --min-age-h 0`: 4.8–6.4 s.
- `python3 dev/audit/harnesses/pulse_replay.py --since 2026-10-15T00:00Z --until 2026-10-21T08:00Z`: 609 samples every 15 min.
  - opener: 25 samples in 1 window, 2026-10-16 08:45Z–14:45Z.
  - state-beat: 37 samples in 5 windows (2026-10-17 11:15Z–15:15Z; 2026-10-19 11:15Z–11:45Z, 13:15Z, 15:00Z–16:45Z, 19:00Z–20:45Z).
  - The first cut of the opener rule fired on any aged orphan. It read STOPPED in 123 of 153 hourly samples.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `38 self-testing, 38 wired, 0 unwired`.
- `python3 tools/audit/fold_ledger.py check`: 43 classes, 738 instances, 114 rca entries, 0 violations. `N-silent-stop` per_round R10=4, trigger per_round true.
- `git log --first-parent --format='%ct %h' origin/main` against `git log --format=%ct origin/handoff/audit-r10-plan`: the state-follow latencies used under Null control.
- `gh api repos/tvofi/heatpump_optimizer/issues/201/comments`: takeover notes 6216882536, 6240942713, 6285467757, 6310926491 and 6312035865, and the 2026-10-18 count of 23 tvofi comments.
- `gh api repos/tvofi/heatpump_optimizer/pulls?state=all`: last pull request opened from a handoff before I4 was #2531 (`fix/r10-ci-ratchet-red`, 2026-10-20 23:44Z).
- `git for-each-ref refs/remotes/origin/review`: `review/2527` `blocked` at `de28f656`, committed 2026-10-21 00:00Z.
- Cost test, computed in the record's section 4 from the figures above:
  - idle hours per instance 3.0, 4.0, 1.0 and 7.7 (mean 3.9);
  - survey 0.5 h and 1.2 h;
  - 4 instances in 6.33 days;
  - 8.2 s × 24 per day = 3.3 min/day.
- Scoped gate, `python3 tests/closure.py select --diff 0cc148b2f`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (entities.py, harness_headers.py). Run with `/opt/hpo/venv-ci/bin/python` and `PYTHONPATH=tests/hastub`: `tests/entities.py` ALL 2363 ENTITY CHECKS PASSED, `tests/harness_headers.py` ALL 109 HARNESS HEADER CHECKS PASSED, and the `run_always` lines `tests/env_drift.py --claims-only` ok, `tests/closure.py selftest` ALL 124 closure shrink pins PASSED, `tests/layout.py` ok.
- `tests/closures.json`: `dev/audit/harnesses/pulse_replay.py` added to harness_headers' inert reads by `tools/pr/ci_predict.py --apply-inert` (the predictor's one predicted closures red); gate re-run at the head: closure selftest, harness_headers, entities and structure all pass.
- `node tools/policy/agreement.mjs` (prepr's agreement lane): `finding-class-id` read `N-silent-stop` DIVERGENT until the id was added to `dev/audit/config/finding.schema.json`'s `class_guess` enum and `.claude/workflows/audit-find.js` regenerated by `python3 tools/audit/fold_ledger.py sync`; `AGREEMENT ok` at the head.
- `bash tools/pr/prepr.sh <body>`: no refusal, `PRE-PR: 33f6c201f4f0814f4570c7441f43b175528a8154 000000000000000000000000`.
- `tests/structure.py`: STRUCTURE RATCHET PASSED. `node tools/policy/policy_lint.mjs`: 0 errors across 41 policy files. `python3 -I tools/audit/seat/tmp_paths.py --check`: 0 refused.

## Red checks

none.

## Forward-carry

- **The barrier itself.** The class owes an off-host scheduled run of `pulse.py` that alarms the owner: (A) an hourly scheduled cloud probe through `cloud_dispatch.py --role probe`, recommended, or (B) an hourly CI cron. This is the owner's decision, and the class stays `detector` until one runs. Carry: #201
- **Liveness as owed input, not process.** A consumer's liveness is its owed input on origin, which is what `pulse.py` reads, not a process on the host. `beatd status` (the machinery design, §6.2) sees only the host it runs on. The design should name `pulse.py` as its off-host complement rather than a second liveness contract. Carry: R10-ORCH-MACHINERY
- **The standing orphan backlog.** It saturates any age-only alarm: the first-cut opener rule read STOPPED in 123 of 153 hourly samples. The `handoff-no-pr` age thresholds (24 h DISPATCH, 48 h owner flag) will fire permanently unless the backlog is disposed or the alarm is keyed to arrivals after the last opening, as `pulse.py` does. Carry: R10-RCA-HANDOFF-SLIP

## Friction

- fixer.md-5: unclear: the brief says the venv python is on PATH, but `python3` resolves to 3.11 (`/usr/local/bin/python3`). `tests/entities.py` fails to parse under it (an f-string SyntaxError), so the scoped gate needs `/opt/hpo/venv-ci/bin/python` named explicitly. Carry: dismissed: environment, outside this group's files
