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

No policy file, lint class or rules entry is added. This is not because a rule forbids one: decision 0012's process moratorium, which an earlier draft of this body cited, was revoked by the owner (#201 comment 6322712314), and the record never rested on it. Its barrier options A and B rest on account configuration and on 0013's pinning. The revocation opens no barrier form the record ruled out, because a policy file or lint class runs only when a seat pushes, and a stopped host pushes nothing; only a scheduled run off the host can see this class. `governance.yml` is code-owned; this PR adds one self-test step to it.

Where the forward-carries land (round 2): the two `#201` lines land in this PR, as the last two entries of `dev/programme/carries/carry-201.json`, each with its control and re-measure (no live roster group owns either: the barrier is the owner's decision, and no group's files include `failure_logs.sh`). The two roster lines are landed on `origin/handoff/audit-r10-roster` by the orchestrator, not by this PR. Both are on the roster at `origin/handoff/audit-r10-roster` `545184b96` (re-fetched 21:41Z): R10-ORCH-MACHINERY's carry naming `pulse.py` as `beatd status`'s off-host complement came in `23859c81f` (and `7213e761e` appends the same line again), and R10-RCA-HANDOFF-SLIP's backlog carry came in `3c8111a4e`, its first. Each cites #2557 and states its control.

## Head

`2f171454d90475b4eb6e22d52df78a3b8cd68879` (round 2) is one commit, `2f171454d`, on the reviewed head `7e312ed2e482faf04be7eb27f38d92aef2b6fae5`. That head already merges origin/main `1ebc737e7e187a1d45c62069ae8ab69c465db928`, and `git merge origin/main` at `2f171454d` reports it already up to date (origin/main re-fetched at 2026-10-21T21:33Z). The round-2 commit changes two files: `dev/programme/carries/carry-201.json` (two carries and the `stage` text) and `tools/audit/seat/pulse.py` (one self-test fixture, no production line). The three-dot diff from the merge base is now 12 files. Figures re-taken at `2f171454d` are marked so; every other figure was taken at the head it names and is untouched by the round-2 commit.

Earlier heads: `ad6bdbcd836286887c7e42c5a63676d97019d8db` merged origin/main `5006687576713535518634a154f7de1824432219` into `01d7ac8c75533bf9e4eff9cbc73d5205a65d6f1f`, which merged origin/main `03b49e152` into the authored code head `33f6c201f4f0814f4570c7441f43b175528a8154` (base `origin/main` `0cc148b2f80fe224ffe2c504b29fd4f0908183df`; figures taken 2026-10-21 09:00Z-09:40Z unless marked as re-taken).

## Mutation proof

Each predicate in `tools/audit/seat/pulse.py` was deleted in a copy, then `--self-test` was run on the copy. All 20 base checks, plus the unread-state check added after M4, pass unmutated. Round 2 adds a 22nd check, the opener's rc clause (M8).

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
| M8 | `judge_opener`'s `or o.get("rc") not in (0, 1)` dropped (round 2, at `2f171454d`) | 1 failed ("bus.sh rc 2 or more is UNREADABLE even beside a summary line"); M0 at the same head: 22 checks, 0 failed |

M8 was the reviewer's surviving mutant R11. In practice `bus.sh` dies to stderr before its summary line, so the summary-line check already covered an rc of 2 or more. The new fixture (rc 3 beside a summary line) pins the clause anyway, so the guard no longer rests on `bus.sh`'s die path.

Wiring: before the `governance.yml` step, `selftest_wiring.py --check` printed `UNWIRED tools/audit/seat/pulse.py`. After it, the check prints `38 self-testing, 38 wired, 0 unwired` at the code head, and `39 self-testing, 39 wired, 0 unwired` re-taken at `ad6bdbcd` (main added one instrument since).

## Null control

- **Self-test:** the healthy fixture reads ok on all three arms, exit 0, as does the I4 fixture after the takeover consumed it. The defect fixtures read STOPPED, exit 1.
- **Replay:** `pulse_replay.py` with `--opener-h 1000 --state-min 100000` reads 0 windows on both arms. At the default bounds it reads 25 opener samples (2026-10-16 08:45Z–14:45Z) and 37 state-beat samples in 5 windows.
- **State-beat bound:** 198 of 215 main moves since 2026-10-15 18:08Z were followed within 30 min. The smallest of the other 17 is 49.2 min, so the 45 min bound fires on none of the healthy latencies.
- **Live:** at 09:18Z, the dumped live snapshot re-judged with `--verdict-h 100 --opener-h 1000` reads 0 stopped, exit 0.

## Figures

- Re-taken at `2f171454d`: `python3 -I tools/audit/seat/pulse.py --self-test`: 22 checks, 0 failed.
- Round 2, scoped gate at `2f171454d`: `PREPR_SKIP_CLOSURES=1 python3 tests/closure.py select --diff 1ebc737e7e187a1d45c62069ae8ab69c465db928`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (12 changed files). With `/opt/hpo/venv-ci/bin/python` and `PYTHONPATH=tests/hastub`: `tests/entities.py` ALL 2382 ENTITY CHECKS PASSED; `tests/harness_headers.py` ALL 109 HARNESS HEADER CHECKS PASSED; `tests/env_drift.py --claims-only` claims hygiene ok; `tests/closure.py selftest` ALL 124 closure shrink pins PASSED; `tests/layout.py` ok; `tests/structure.py` STRUCTURE RATCHET PASSED. `node tools/policy/policy_lint.mjs`: 0 error(s) across 41 policy file(s). `python3 -I tools/audit/seat/selftest_wiring.py --check`: 39 self-testing, 39 wired, 0 unwired. `python3 tools/audit/fold_ledger.py check`: 0 violation(s). `python3 -I tools/audit/seat/tmp_paths.py --check`: 0 refused. `agreement_py.py` then `agreement.mjs --py-json`: AGREEMENT ok. `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: no closures or fast red predicted. `node tools/policy/policy_lint.mjs --pr-body <this body> --red nightly-status,pr-contract`: 0 error(s).
- Round 2, at `2f171454d`: `node tools/policy/brief_lint.mjs`, section `dev/programme/carries/carry-201.json`: 0 error(s), 0 warning(s), with 19 carries (17 at the merge base). This is the lint the `briefs` job runs over carry files.
- Round 2, from this cloud seat at `7e312ed2e` (the `failure_logs.sh` carry's control): `bash tools/audit/seat/failure_logs.sh 2557` exits 2 in 0.5 s with empty output; `gh pr view 2557 --json headRefOid` prints `HTTP 403: GitHub GraphQL is not available from Claude Code sessions`; the null control, `gh api repos/tvofi/heatpump_optimizer/pulls/2557 --jq .head.sha`, prints `7e312ed2e482faf04be7eb27f38d92aef2b6fae5`, exit 0.
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
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `38 self-testing, 38 wired, 0 unwired` at the code head; re-taken at `ad6bdbcd`: `39 self-testing, 39 wired, 0 unwired`.
- Re-taken at `ad6bdbcd`: `python3 -I tools/audit/seat/pulse.py --self-test`: 21 checks, 0 failed; `python3 tools/audit/fold_ledger.py check`: 43 classes, 738 instances, 114 rca entries, 0 violations; `python3 -I tools/audit/seat/tmp_paths.py --check`: 0 refused.
- Merge check at `ad6bdbcd` (HANDOVER trap 19): `tests/closures.json`, `dev/audit/config/finding.schema.json` and `dev/audit/config/bugclasses.json` parse as JSON; `node --check .claude/workflows/audit-find.js` passes; `python3 tools/audit/fold_ledger.py sync` leaves the tree clean.
- Round 2, over this final body at `2f171454d`: `python3 -I tools/audit/carry_audit.py check --body <this body>` prints `CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)`, exit 0, and the same with `--roster-ref origin/handoff/audit-r10-roster` (at `545184b96`). Five items: the three Forward-carry lines and the two Friction lines. Round 1's figure (`4 routed`) was stale against its own re-taken body; the reviewer read 5. Null control: the draft of this body that kept a `Destinations:` paragraph inside `## Forward-carry` read `6 finding item(s): 5 routed, 1 unrouted`, exit 1, so the audit does read this section.
- Round 1: at `01d7ac8c`, `2 routed, 0 unrouted, 2 bad destination(s)`, exit 1; at `ad6bdbcd`, 0 bad destinations, exit 0 (the `pr-contract` answer below).
- Scoped gate re-taken at `ad6bdbcd`, `PREPR_SKIP_CLOSURES=1 /opt/hpo/venv-ci/bin/python tests/closure.py select --diff 5006687576713535518634a154f7de1824432219`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. With `PYTHONPATH=tests/hastub`: `tests/entities.py` ALL 2382 ENTITY CHECKS PASSED, `tests/harness_headers.py` ALL 109 HARNESS HEADER CHECKS PASSED, `tests/env_drift.py --claims-only` ok, `tests/closure.py selftest` ALL 124 closure shrink pins PASSED, `tests/layout.py` ok, `tests/structure.py` STRUCTURE RATCHET PASSED. `node tools/policy/policy_lint.mjs`: 0 errors across 41 policy files. `python3 -I tools/policy/agreement_py.py --out F` then `node tools/policy/agreement.mjs --py-json F`: `AGREEMENT ok`.
- `node tools/policy/policy_lint.mjs --pr-body <body> --red nightly-status,pr-contract` with the branch's changed paths: this body 0 errors. The body it replaces gets 2 errors, `nightly-status` and `pr-contract` unnamed.
- `git show <ref>:dev/programme/rosters/wave-r10-groups.json`, groups `R10-ORCH-MACHINERY` and `R10-RCA-HANDOFF-SLIP`: 0 of 2 at `01d7ac8c`, 2 of 2 at origin/main; `git log --first-parent -S` puts both in `5226fd2d1` (#2559).
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

Read from the check-runs API at `7e312ed2e482faf04be7eb27f38d92aef2b6fae5`, the newest head CI has run, latest run per name, at 21:31Z: 45 runs, two red (`nightly-status`, `pr-contract`), `coverage` still in progress, the rest success, skipped or neutral. `2f171454d` has not been run by CI: this seat pushes only `handoff/` refs.

- **`pr-contract`** at `7e312ed2e` (job 119494591921, run 39678522008, 21:24Z). Not a refusal of this body: the job died at step 6, `Read the body off the API, not the event payload`, before any contract check read anything. `gh api repos/.../pulls/2557 --jq '.body'` printed `invalid character 'S' looking for beginning of value`, so the API answered with a non-JSON page. `/tmp/pr-body.md` was never written, and steps 10, 11 and 13 then failed on the missing file (`FIGURES: /tmp/pr-body.md is unreadable`, `jq: ... Could not open /tmp/pr-body.md`, `FileNotFoundError`). From this seat, the same REST read of #2557 succeeds (## Figures). This is the 'died before any test body ran' case; the one re-run is the orchestrator's, and the PR body the orchestrator writes from this handoff re-triggers the job anyway. **Cheaper detector:** none. The job already fails closed on an unreadable body; the only faster signal is the API answer itself.
- **`pr-contract`** at `01d7ac8c` (round 1, job 119212655116, 12:09Z), kept as answered there: This PR's own red. The failing line: `BAD-DEST body item c64b5cbc: R10-ORCH-MACHINERY: R10-ORCH-MACHINERY is not a group of the roster`, and the same for `97b3bd6b` / `R10-RCA-HANDOFF-SLIP`. `carry_audit.py` reads the roster from the head's own tree. Both groups reached main's roster in #2559 (`5226fd2d1`), after this head's last main merge (`03b49e152`). So the carries were right, and the head was stale. Fixed at `ad6bdbcd` by merging origin/main. It reproduces at `01d7ac8c` (exit 1) and passes at `ad6bdbcd` (exit 0); see ## Figures. **Cheaper detector:** prepr's carry-audit arm already runs this check before a push. It reads the roster from the tree it is run in, though, so a run from a checkout of current main passes a head that CI then refuses. Running carry_audit at the head's own tree would have caught this, at a cost of seconds. No new check is built: the cure is one main merge, and the refusal already names each group it cannot find.
- **`nightly-status`** (job 119486581159 at `7e312ed2e`, 21:10Z; first seen as job 119196372889 at `01d7ac8c`, 11:30Z). Main's red, not this PR's. The failing line is `NIGHTLY FAILED: slow failed 1 night ago.`, scheduled run 39387919507 on main `0c298f6`: `FAIL synthetic-dhw-only.json: cycle_cost  [1 offender(s): loop_cpu_ratio 0.1114 over its budget 0.111]` (job 118512165515). The 2026-10-21 schedule, run 39563978649 (the run job 119486581159 names, for both `slow` and `mutation-nightly`) on main `c77f89dc`, failed the same check at `0.1138`. It also failed `mutation-nightly` with `10 survivor(s) of 23 evaluated = 39.1% ... cap 30.0%`, all ten survivors under `custom_components/heatpump_optimizer/`. This diff touches `.github/workflows/governance.yml`, which is on the reporter's input list. The edit adds one step, `python3 -I tools/audit/seat/pulse.py --self-test`, to the `instrument-self-tests` job. `tests/nightly_status.py` (pinned to main `03b49e152` in the job) reads the Tests workflow's scheduled runs, which come from `tests.yml`. This diff touches neither that file, `tests/replay.py`, nor anything under `custom_components/`. **The fix exists:** #2548 (`290712ec0`, merged 17:03Z) re-records `loop_cpu_ratio` at 0.143, and this head carries it through the merge. No `workflow_dispatch` of `tests.yml` on main has concluded since then; the newest is 39256093598, from 2026-10-19. So the check goes green on the next concluded schedule or dispatch on main, not on anything this PR can push. The mutation-nightly cap breach has no fix PR in the open list. It is in production code this PR does not touch, and it belongs to the mutation lane's owner. **Cheaper detector:** none is cheaper. The slow lane is the detector, and it is a runner-timing budget, which only a run on the runner class measures.

## Forward-carry

- **The barrier itself.** The class owes an off-host scheduled run of `pulse.py` that alarms the owner: (A) an hourly scheduled cloud probe through `cloud_dispatch.py --role probe`, recommended, or (B) an hourly CI cron. This is the owner's decision, and the class stays `detector` until one runs. The control is a precondition: the replay reads 25 opener and 37 state-beat STOPPED samples over round 10 that no on-host run reported, and 0 windows under the null bounds (`--opener-h 1000 --state-min 100000`). Destination: `dev/programme/carries/carry-201.json`, this PR. Carry: #201
- **Liveness as owed input, not process.** A consumer's liveness is its owed input on origin, which is what `pulse.py` reads, not a process on the host. `beatd status` (the machinery design, §6.2) sees only the host it runs on. The design should name `pulse.py` as its off-host complement rather than a second liveness contract. The control is a precondition: at the 2026-10-21 reboot, the host was up, and `review/2527` sat blocked at its head for 7.7 h with no session turn after 23:44Z. So a check keyed on the host or its processes had nothing to see. `pulse.py`'s self-test fixture of that shape ("the 10-21 shape: the blocked #2527 verdict 7.7 h at its head is STOPPED") reads the verdict arm STOPPED, and the healthy fixture reads ok on all three arms. Re-measure with `python3 -I tools/audit/seat/pulse.py --self-test`. Carry: R10-ORCH-MACHINERY
- **The standing orphan backlog.** It saturates any age-only alarm: the first-cut opener rule read STOPPED in 123 of 153 hourly samples. The `handoff-no-pr` age thresholds (24 h DISPATCH, 48 h owner flag) will fire permanently unless the backlog is disposed or the alarm is keyed to arrivals after the last opening, as `pulse.py` does. The control is a precondition: the first cut (any aged orphan) gave 123/153 STOPPED, and the arrival-keyed rule over the same replay gives 1 opener window (25 samples, 2026-10-16 08:45Z-14:45Z). Re-measure with `dev/audit/harnesses/pulse_replay.py` at your head, then count the orphans `bash tools/audit/seat/bus.sh orphans --min-age-h 24` lists that are older than the newest pull-request opening; if that count is above zero, an age-only threshold is already firing on backlog. Carry: R10-RCA-HANDOFF-SLIP

## Friction

- fixer.md-5: unclear: the brief says the venv python is on PATH, but `python3` resolves to 3.11 (`/usr/local/bin/python3`). `tests/entities.py` fails to parse under it (an f-string SyntaxError), so the scoped gate needs `/opt/hpo/venv-ci/bin/python` named explicitly. Re-observed in round 2 at `2f171454d`. Carry: dismissed: environment, outside this group's files
- failure-logs: stale: `bash tools/audit/seat/failure_logs.sh 2557` reads the head with `gh pr view`, which is GraphQL, and a cloud seat's `gh` refuses that (HTTP 403). The script exits 2 and prints nothing (re-measured in round 2, ## Figures). The REST job-log route also redirects to a blob host that the cloud proxy refuses (403). So the failing lines above were read through the GitHub MCP job-log tool. Destination: `dev/programme/carries/carry-201.json`, this PR. Carry: #201
