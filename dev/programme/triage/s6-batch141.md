# Proposal triage, session s14, batch 141 (P500 to P545)

This batch rules every line of `s7/triage-queue-s7.txt` after line 164, the last line a batch file
cites (batch 140, P493). It also rules two items from session 13's notes: a Dependabot `ignore:` and
a PyPI hash checker (P543, P544).

The bar is `dev/governance/roles/proposal-triage.md` at origin/main `45adb0c3b4`, read with the
owner's rulings of 2026-11-08:
- A new proposal is accepted on a measured gain of more than 20 % in CI time, programme completion
  time, right-first-time or token usage.
- A planned instrument group stays on 10 %.
- A lesson that needs no instrument goes to R10-ROUND-PLAYBOOK-FINAL. A rejected proposal is not
  built, and nothing is deferred out of round 10 as work.
- Batch 136's P434 reading still applies: a severity skips the bar only where the work repairs a
  wrong behaviour that was observed. An owner directive, and a class barrier at the third
  instance, skip it too.

Denominators, all from batch 136 and not re-taken:
- **CI time:** 29876 runner-min/day.
- **Completion:** the replan base wall of 170.42 h.
- **Right-first-time (RFT):** 55 PRs with a `ci.yml` run on 11-07.

Sources read:
- origin/main `45adb0c3b4`.
- The roster at `origin/handoff/audit-r10-roster` `b34b3d6284`, as `dev/programme/rosters/wave-r10-groups.json`.
- The batch files on `handoff/triage-s12-batch131` and `handoff/triage-s13-batch134` to `140`. The
  highest ruled entry is P499.
- `s7/roster-queue-s7.txt`.
- The merge train's `train.log` in its state directory.
- The s13 studies `s13/fpy-study/fpy-study.md` and `s13/stack-study/stack-study.md`.
- API reads, each named beside its figure.

No entry touches a capped file: `git grep -n <file> origin/main -- 'tests/*_budgets.json'` prints
nothing for orchestrator_tick, beat_jobs, merge_train, bus.sh, prepr.sh, plan_page, liveness,
hooks_setup, beatd or fixer.md.

Lines that need no ruling:
- **165:** the record of batch 140.
- **194:** RCA-OWED, which takes the root-cause route.
- **196:** BARRIER-OWED STALE-GATE-FAILURE. The orchestrator queued it to R10-TRAIN-RESIDUE (roster
  queue line 4182).
- **207:** folded by the owner on 2026-11-09 19:15Z. The fold is now R10-PLAN-PAGE-RESIDUE carry 1.
- **209 and 210:** SEAT-SILENT-EXIT. These are RCA countermeasures, so they keep their route.
  R10-REVIEW-DISPATCH-RESIDUE carry 7 already holds the reviewer no-return arm.
- **212:** outside #3380 is held by R10-WATER-SETPOINT-FEEDBACK, which is #3405.

## P500: OWED-UNACTIONED-KEYOF

Verdict: REJECT. It is built.

Source: queue line 166 (2026-11-09T08:07:54Z).

Instances: `owed_unactioned.py:101` keys `OWED <kind> #<n> <head12>`. It came in with commit
`c70ed6b58d`, which reached main in #3345 (`2b777aad79`, 2026-11-09T16:23Z), after the proposal.

Cost: none. Binding: nothing is left to build.

## P501: PLAN-PAGE-LEGEND-DRIFT, its addendum, and PLAN-TOOLTIP-NONE

Verdict: ACCEPT, on the owner-directive route. Only the residual items are accepted.

Source: queue lines 167, 177 and 193.

Instances:
- The owner, 2026-11-09, verbatim in R10-PLAN-PAGE-RESIDUE carry 1: "the plan page should be fixed
  with all your input, it woud fit to fold it into the next plan page group".
- **Already fixed: the legend drift (167(1)).** The legend and the tier tooltip now both render
  `replan.TIER_LEGEND` (`plan_page.py:681` and `:1094` at main).
- **Already carried: the None leak and the strip counter.** These are 167(4), 177(a), 177(b) and
  193, held by R10-PLAN-PAGE-RESIDUE carries 1(4), 3 and 4.
- **Residual, in no carry:**
  - the `data-f="partial"` filter matches no row (167(2));
  - the open-issue count reads "35 open issues" against the chart's "33 open now" (167(3));
  - a hotfix that blocks the critical path is not marked on it (167(5));
  - done rows list open groups under "Blocked by" (177(c));
  - the page has no closing `</body></html>` (177(d) and 193). `grep -n '</html>'` on main's
    plan_page.py prints nothing.

Cost: render fixes in `plan_page.py`, each with a fixture and a mutant.

Binding: one carry, R10-PLAN-PAGE-RESIDUE (`carries/b141-P501.txt`). The fixer re-reads each item at
its base and drops any that no longer reproduces.

## P502: SKIP-DEFERRAL-NOT-ENVIRONMENT, instances 3 to 7

Verdict: REJECT, as a duplicate. R10-GATE-DEFER-BARRIER holds the class barrier (P436, carry 2) and
the readers' fix (carry 3).

Source: queue line 168.

Instances: #3348, #3353, #3357, #3362 and #3370 add to the barrier's count. They add no new
mechanism.

Binding: no op.

## P503: TRIAGE-141-NOTE and the ROUTE of r10-roster-write-sweep

Verdict: REJECT. There is nothing left to rule.

Source: queue lines 169 and 189.

Instances:
- At the roster tip, R10-CARRY-RESIDUE-2 is at stage `done`. The s13 orchestrator set that.
- The four leftover #3253 carries line 189 asked to place are CARRY-RESIDUE-2 carries 5 to 8, with
  their text in 9 to 12.
- Each is a roster DATA op (`edit-brief`, `set-stage ... absorbed --into`). Those ops are the
  orchestrator's, not a build.

Binding: no op.

## P504: APP-PUSH-ADOPT-EMAIL

Verdict: REJECT.

Source: queue line 170.

Instances:
- One: #3356. That is 1 of 55, or 1.8 % RFT.
- The workaround, re-authoring the commit to the contributor's numbered noreply with identical
  trees, is owner-endorsed (tvofi 2026-11-09).

Binding: 1.8 % against >20 %.

## P505: CARRY-FOLD-AUDIT-DISAGREE

Verdict: REJECT. This is the instance P488 already ruled.

Source: queue line 171.

Instances: one, #3345 item `becd0c23`. That is the same instance as P459, and P488 reversed it at
1.8 % RFT.

Binding: 1.8 % against >20 %.

## P506: LIVENESS-HOOK-PARITY, with S14-HOOK-RESTART-PATH

Verdict: ACCEPT, on the owner-directive route.

Source: queue lines 172 to 176 and 223.

Instances:
- **The owner's direction:** tvofi 2026-11-09, "keep the local one, but propose an update to the
  live one to cover the gaps". R10-STANDING-CONTRACTS-P2 carry 16 (tvofi 2026-11-01) orders every
  useful standing loop and hook folded onto main.
- **The restart defect:** the session-local restart drops PATH. beatd and the tick then came back
  under Python 3.11, and the opener row died on a SyntaxError (opener digest
  `open_driver rc=1: SyntaxError`, 2026-11-11T00:00Z). No handoff opened from that restart onward.
- **What main has:** `tools/audit/seat/hooks/liveness.py` has no restart arm, no read-proof gate and
  no checkout-presence arm. `beatd.py` has no interpreter floor (`grep -n version_info` prints
  nothing).

Cost: one instrument PR over `hooks/liveness.py`, `hooks_setup.py` and `beatd.py`, with a planted
case and a null control per arm in `hooks_setup.py --self-test`.

Binding: one carry, R10-STANDING-CONTRACTS-P2 (`carries/b141-P506.txt`). The orchestrator adds the
three files to the group.

## P507: ROW-ONLY-HEAD-ORPHANED-CODE-RUN and DELIVERY-ROW-IN-OPENING-PUSH

Verdict: REJECT.

Source: queue lines 178 and 202.

Instances:
- The ci-docs study gives 57 to 625 runner-min/day of cancelled first runs. That is 0.19 % to
  2.09 % of 29876.
- The orphaned-gate red has one counted instance (#3371). Its cure, dispatching the code run at the
  row head, is an owner-endorsed workaround (tvofi 2026-11-09).

Binding: at most 2.09 % CI time and 1.8 % RFT, against >20 %.

## P508: PACKET-GATE-DEFERRAL-WAIT

Verdict: REJECT, as a duplicate. R10-GATE-DEFER-BARRIER carry 3 names `review_packet.py`
`gate_digest` as an open reader of the deferral red.

Source: queue line 179. Binding: no op.

## P509: RULED-GROUP-AFTER-EDGES

Verdict: REJECT. It is built.

Source: queue line 180.

Instances:
- `roster_lib.RELEASING_STAGES = FINISHED_STAGES + RULED_STAGES`, and `is_open` excludes those
  stages.
- That came in with commit `26a2e6cfc1` ("after-edges by predecessor stage"), merged in #3326
  (`30c48cfbaf`, 2026-11-09T14:37Z), after the proposal.

Binding: nothing is left to build.

## P510: DESIGN-REVIEW-OWED, the third instance (DESIGN-RECUT-UNREVIEWED and DESIGN-REVIEW-OWED-BLIND)

Verdict: ACCEPT, on the class-barrier route. This is the third instance. It supersedes the `#held`
`b137-P448.txt` line (roster queue line 3481), whose group R10-TICK-LEVELS is done.

Source: queue lines 181 and 219, with P448 and P495.

Instances (114.4 h of design wait in total):
- **R10-ADVISOR-WHATIF:** re-cut `b50afa68`, unreviewed 96 h (P448).
- **R10-GENERIC-HEAT-CURVE-PERSISTENT:** re-cut `c52e3782`, unreviewed about 16 h. This one was on
  the critical path, so it is 9.4 % of 170.42 h on its own.
- **R10-WATER-SETPOINT-FEEDBACK:** an outside request, unreviewed 2.4 h.

`orchestrator_tick.py` still has only DESIGN OWED (line 1603) and DESIGN-BUILD (line 1655).

Cost: one branch in the existing `design_builds` read, which already lists both ref families.

Binding: one carry, R10-TICK-RESIDUE (`carries/b141-P510.txt`). P515 calls the same predicate.

## P511: TRAIN-WAITS-ON-PHANTOM-RUN

Verdict: REJECT.

Source: queue line 182.

Instances: one 7320 s hold on a zero-job `pull_request_review` run. That is 2.03 h, or 1.19 % of
170.42 h.

Binding: 1.19 % against >20 %.

## P512: STATE-DOCS-PUSH-RACE, TRAIN-DOCS-PUSH-NONFF and TRAIN-DOCS-NONFF

Verdict: REJECT. It is built.

Source: queue lines 183, 188 and 215.

Instances: #3395 (R10 state-docs-push-race, `3aac11dfba`, 2026-11-10T01:01Z) puts the retry in
`state_docs.py` (line 246, and self-test arm 3 at line 1172).

Binding: nothing is left to build.

## P513: TICK-RED-UNANSWERED-OWED-SET

Verdict: REJECT, as a duplicate. R10-HOTFIX-NONREQUIRED-REDS-2 (#3384, open) brief item (3)
filters exactly this tick line through the owed-reds set.

Source: queue line 184. Binding: no op.

## P514: BOT-MERGE-HEAD-NOTE

Verdict: REJECT.

Source: queue line 185.

Instances: 4 in one day (#3329, #3299, #3358, #3345). That is 7.3 % RFT. Each cost one `body_patch`
and a re-mint.

Binding: 7.3 % against >20 %.

## P515: CP-OUTSIDE-WATCH and CP-WATCH-GROUPS-TO-TREE

Verdict: ACCEPT, on the owner-directive route.

Source: queue lines 186 and 221.

Instances:
- **The directives:** tvofi 2026-11-09 ~15:00Z, "never let the critical path or outside PRs slip,
  ever". Again ~23:10Z: "This should under no circumstances never, ever be allowed to slip since it
  is outside request".
- **The slips:**
  - #3345 blocked unseen for 1 h 45 min;
  - #3349 waited 1 h for its approval;
  - the R10-WATER-SETPOINT-FEEDBACK design waited 2.4 h for a reviewer;
  - the R10-COMBI-TANK-PR-B designer sat unfired for 48 min;
  - line 225: #3398, #3405 and #3417 had no return 11 h after their fires.
- The check runs today only as a session-local loop. `roster_lib.is_outside` (line 725) and
  `critical_path_read` (line 807) exist on main.

Cost: one beat row or tick level of about 200 lines with self-test arms. The DESIGN-REVIEW-OWED
predicate is shared with P510.

Binding: one carry, R10-TICK-RESIDUE (`carries/b141-P515.txt`).

## P516: OPENER-TRIAGE-GROUP and OPENER-STARVED-TRIAGE

Verdict: REJECT. The behaviour is by design.

Source: queue lines 187 and 214.

Instances: owner correction 2026-11-07 20:35Z, recorded in `s13/RESUME-s13.md` lines 28-29:
"triage record handoffs are NOT opened as PRs ... only merges along with stamps". The opener's skip
is that rule working.

Binding: owner ruling.

## P517: ROUTE of r10-suite-host-determinism (DST-date seams on `7631e7ed`)

Verdict: REJECT. Close it, with no next part.

Source: queue line 190.

Instances:
- `BLOCKED.md` at `7631e7ed` measures failures only in non-UTC zones on DST-transition dates. CI
  runs in UTC.
- The next transition date, 2027-03-28, falls after the round's close.
- In CI, 0 of the measured failures reproduce.

Binding: 0 % on every measure. The ref stays as evidence.

## P518: TRAIN-OWNER-APPROVAL-OWED

Verdict: REJECT. It is built: #3400 (approval owed in the packet) and #3401 (the train's mandate
policy, `policy_approval_due`), both merged 2026-11-10.

Source: queue line 191. Binding: nothing is left to build.

## P519: SEAT-IDENTITY-EMAIL-UNSET

Verdict: REJECT. The mechanism is on main.

Source: queue line 192.

Instances: one commit (`cd78999f`). `cloud-setup.sh` now exports both `GIT_AUTHOR_EMAIL` and
`GIT_COMMITTER_EMAIL` from `SEAT_EMAIL` (lines 72 and 84, with a self-test at 167).

Binding: 1 instance; nothing is left to build.

## P520: SLIP, review not owed at push (#3374)

Verdict: REJECT.

Source: queue line 195.

Instances: one 2 h 21 min wait. The tick already derives `review-owed` (`ledger.py` KINDS). That is
1.8 % RFT.

Binding: 1.8 % against >20 %.

## P521: FPY-CM1, settle-gated dispatch

Verdict: REJECT.

Source: queue line 197 (`fpy-study.md` table, line 135).

Instances:
- Reject-rate cut: −11.4 % over the round and −19.2 % over 7 d. Both are below 20 %.
- The 24 h figure, −36.9 %, falls in the window when `gate-sweep.yml` was `disabled_manually`. The
  study itself records only 2 unsettled blocks after the 07:33Z re-enable.
- The concluded-red half is built: `bus.sh:600-612` refuses dispatch on classify RED (K15(d)). The
  re-run half is `gate-sweep`.

Binding: 19.2 % at best, against >20 %. The remainder overlaps R10-GATE-DEFER-BARRIER.

## P522: FPY-CM2, replay the reviewer's mutants

Verdict: REJECT. The cut is −3.6 % over the round and −2.6 % over 7 d (study line 136). Below the
bar.

Source: queue line 198.

## P523: FPY-CM3, refusing prepr diff mutants

Verdict: REJECT. The cut is −2.7 % over the round and −2.5 % over 7 d (study line 137). Below the
bar.

Source: queue line 199.

## P524: BARRIER-OWED HARNESS-HEADERS-RED

Verdict: REJECT as a new item. It is routed already, as R10-PREPR-RESIDUE carry 12 (#3401 item
`fd81bbe9`).

Source: queue line 200.

Instances: 12 blocks across 12 PRs (`fpy-study.md` line 120). Carry 20 restates carry 12.

Binding: no new op. The orchestrator may dismiss carry 20 as a duplicate of 12.

## P525: DEFECT, `review_strength.py --by size` crash

Verdict: REJECT the tool change.

Source: queue line 201.

Instances:
- **The read:** `review_strength.py:251` reads `((grp or {}).get("model") or {}).get("fixer")`.
- **The datum:** 1 of 435 roster groups (R10-REPLAY-OPEN-LOG) holds `"model": "sonnet"`, a string.
  The other 426 hold a dict and 8 hold none.
- **Who is affected:** only audit runs. 0 % on all four measures.

Binding: below the bar. The cheaper cure is the one roster datum, an orchestrator op.

## P526: HOTFIX-PREPR-SCOPED

Verdict: ACCEPT, on the owner-directive route.

Source: queue line 203.

Instances:
- tvofi 2026-11-09, verbatim: "hotfixes should have aggressively scoped or no prepr".
- The main de.json hotfix spent about 40 min in a full prepr while 7 PRs waited.
- Today it is a session-local brief append. `git grep -i hotfix` finds nothing on main in
  `cloud_dispatch.py`, `open_pr.sh` or `app_push.sh`.

Cost: the scope is decided once, in `prepr.sh`: a `fix/r10-hotfix-*` topic defaults to
`PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1` and prints that scope. That makes no prompt or opener
edit necessary.

Binding: one carry, R10-PREPR-RESIDUE (`carries/b141-P526.txt`).

## P527: STACK-STUDY, P1 (stacked train) and P2 (dispatch at the parent's merge verdict)

Verdict: REJECT, both.

Source: queue line 204 (`stack-study.md` lines 5 and 90).

Instances:
- A replay of the round's chains moves completion by 0.00 to 0.06 h in every arm. That is at most
  0.04 % of 170.42 h.
- P1 costs about 600 to 800 lines.

Binding: 0.04 % against >20 %. The study's conditions for a hand-run stack are a playbook lesson
(P545).

## P528: PAST-THREE-MECHANICAL

Verdict: ACCEPT, on the owner-directive route.

Source: queue line 205.

Instances:
- tvofi 2026-11-09 18:35Z, verbatim: "the split shoud never apply when the gap is mechanical only".
- `bus.sh` `three_rounds()` (lines 506-520) still refuses a fourth round with no class exemption.
- No roster group holds the change.

Cost:
- **The code:** a class read in `three_rounds()` and a self-test with a mechanical arm and a
  substantive null control.
- **The policy:** a `fixer.md` "Past three rounds" sentence. That is policy, under mandate
  6715477401.

Binding: one carry, R10-REVIEW-DISPATCH-RESIDUE (`carries/b141-P528.txt`).

## P529: BLOCKED-STOP-LANDED

Verdict: REJECT.

Source: queue line 208.

Instances: 2 stale tick lines (r10-rca-ci-critpath-3 and r10-round-playbook). Each costs one
dismissal.

Binding: no measure moves by even 1 %.

## P530: TRAIN-NO-RECARRY-AFTER-RED-FIX

Verdict: ACCEPT. This repairs an observed wrong behaviour, on the third-instance barrier route, and
I classify it medium.

Source: queue line 211.

Instances:
- Train batch 20261109-194013 skipped #3329, #3351, #3304 and #3364, and #3350 was handled by hand.
  Each was skipped "red at its head" on main's red, which PR 3378 had since cured.
- `merges_as_is` (`merge_train.py:2553`) still returns True under a non-strict ruleset whatever the
  head's red. It recarries only for `grade_held`, a conflict or a bot tip.
- Each skip costs a train cycle, which is hours (P491).

Cost: one condition in `merges_as_is`, one mutant and a null control.

Binding: one carry, R10-TRAIN-RESIDUE (`carries/b141-P530.txt`).

## P531: REPLAY-REF23-STALE

Verdict: REJECT. The defect is not observed now.

Source: queue line 213.

Instances:
- `tests / replay` is `skipped` on the last 8 first-parent merges of main.
- On 8 open PR heads it is skipped or green: #3405 and #3398 green, 0 red. Read by `gh api
  .../commits/<sha>/check-runs`.
- The lane is non-required.

Binding: 0 of 8 heads.

## P532: CARRIES-OPEN-NO-TRIGGER

Verdict: REJECT. It is superseded by two things:
- the carries-open audit, which moved residue into not-started groups the tick dispatches;
- R10-CARRY-SINK-BARRIER (#3417, owner-approved 2026-11-10), which refuses a carries-open
  destination.

Source: queue line 216. Binding: no op.

## P533: TRAIN-SERIAL-GRADER

Verdict: DEFER. The benefit is unmeasured. The owning group is R10-TRAIN-RESIDUE.

Source: queue line 217.

Instances: 44 of 54 distinct serial-routed entries in `train.log` (lines 15000 to 19378) carry
`grader`. That is 81 %.

What would change it: the admission-to-merge hours of grader-only serial entries against batched
ones over the same window. A completion gain over 20 % passes it.

## P534: TRANSLATION-MERGE-DRIVER

Verdict: REJECT.

Source: queue line 218.

Instances: 3 in a day (#3350, #3299, #3297). That is 5.5 % RFT. Four production groups remain that
touch translations.

Binding: 5.5 % against >20 %.

## P535: RETRIAGE-P402

Verdict: REJECT. The re-ruling is done and stands.

Source: queue line 220.

Instances: `handoff/triage-s12-batch131` (`69ec032a2`) re-rules P402 as "REJECT, already landed",
on #3280 (`aaaec2128`, an ancestor of main).

Binding: nothing more is owed by triage.

## P536: GUARDRAIL-VOCAB

Verdict: REJECT.

Source: queue line 222.

Instances: one false-trip audit, costing about 8 cloud seats. The trip rate moves from 2/30 to 5/30
(P = 0.116, which is not significant).

Binding: under one seat a day saved over the four days left, against >20 % of tokens.

## P537: S14-EXTRAS-DEAD-CHECKOUT

Verdict: REJECT, as a duplicate. R10-TICK-RESIDUE carry 13 has `plan_beat` pass the overlay's
`plan_coordinator_cap`.

Source: queue line 224. Binding: no op.

## P538: S14-FIRE-LEDGER-UNVERIFIABLE

Verdict: REJECT, as covered.

Source: queue line 225.

Instances:
- The relay no-return arm over `dispatch/reviewer-*` is R10-REVIEW-DISPATCH-RESIDUE carry 7 (P437).
- P515's SEAT-SILENT arm catches an outside or CP seat with no return within 90 min. That would have
  caught #3398 and #3405 at 90 min, not 11 h.
- Reading the session id back after a fire is orchestrator practice (P545).

Binding: no new op.

## P539: S14-OWNER-ORDER-NOT-OWED

Verdict: REJECT the ledger kind. The lesson goes to the playbook (P545).

Source: queue line 226.

Instances: 2. One stamp ran 13 h late. One workflow re-enable ran 9.5 h late (line 162). Neither is
on a measured critical-path bar.

Binding: unmeasured against >20 %.

## P540: S14-QUEUE-REASON-FLAG

Verdict: REJECT. The lesson goes to the playbook (P545).

Source: queue line 227.

Instances: 3 `append-carry ... --reason` lines in 4182 queue lines (0.07 %). Both 11-10 and 11-11
lines were re-queued without the flag (roster queue lines 4181 and 4182).

Binding: 0.07 %.

## P541: S14-TICK-MAIN-RED-NO-LINE, narrowed to the tick's reader

Verdict: ACCEPT, narrowed. This repairs an observed wrong behaviour, and I classify it medium,
because the arm is blind on every Actions job. The INFRA-RERUN half is REJECTED: R10-GH-READ-RESIDUE
carry 3 retries the gather at its source.

Source: queue line 228.

Instances:
- **What the tick reads:** `red_brief` (`orchestrator_tick.py:1858`) reads only
  `check-runs/<id>`'s `.output`.
- **What it finds there:** at `45adb0c3b4`, 78 of 78 check-runs have null `summary` and `text`
  (`gh api .../commits/45adb0c3b4/check-runs`). So the brief prints "no error line read" for every
  red.
- **The escape-sequence refusal is real but belongs to a different reader.** `gh api
  .../actions/jobs/129708149047/logs` refused with "pass --allow-escape-sequences". The tick never
  reads logs. `merge_train.job_log` is the one reader that passes the flag, and `failure_logs.sh`
  already uses it.
- 2 instances in a day (`96346fdec3`, `45adb0c3b4`). Main stayed red for 9 h.

Cost: on empty output, `red_brief` reads `merge_train.job_log` and takes the ERR_LINE from it. A
self-test arm and a null control.

Binding: one carry, R10-TICK-RESIDUE (`carries/b141-P541.txt`).

## P542: S14-RECONCILE-HOLD-PARSE

Verdict: REJECT. The tool is session-local, and R10-STANDING-CONTRACTS-P2 retires it. Nothing is
owed beyond that.

Source: queue line 229.

## P543: Dependabot `ignore:` for homeassistant-stubs, zeroconf and cronsim

Verdict: REJECT.

Source: session 13's notes (the #3408 body, Forward-carry).

Instances:
- **#3414** (Dependabot, open, head `4182e75d`). `tests / typing` fails "THESE PACKAGES DO NOT
  MATCH THE HASHES" on homeassistant 2026.11.0: its expected hashes are 2026.10.4's (job
  129708149047).
- **The pins do not fit.** PyPI's `requires_dist` for homeassistant 2026.11.0 pins `zeroconf==0.152.0`
  and `cronsim==2.7`. #3414 proposes 0.154.0 and 2.8.
- **The ignore would not have made any of the three green.** With it, #3088, #3323 and #3414 would
  each still be red (stale hashes in all three). That is 0 of 3.
- **An ignore of zeroconf would also block** the 0.152.0 move that homeassistant itself needs.

Binding: 0 of 3 PRs green with it.

## P544: a PyPI hash checker as a `tools/` instrument

Verdict: REJECT. CI's own detector already does this.

Source: session 13's notes.

Instances:
- The typing job's `pip install --require-hashes` reported #3414's stale hash at 07:29:42Z. The PR
  was created at 07:14:40Z.
- #3147 dismissed the same per-pin detector.
- The re-apply branch compiles each lock with hashes, so its hashes are correct by construction.
- That is 0 re-apply rounds saved across #3088, #3323 and #3414.

Binding: 0 of 3. This is the third stale-hash instance. #3408's Forward-carry says that is when
`root-cause.md`'s cost test becomes owed. That is a root-cause seat's work, and the orchestrator's to
dispatch.

## P545: playbook lessons of this batch

Verdict: ACCEPT, to R10-ROUND-PLAYBOOK-FINAL, as the round's destination for a lesson that needs no
instrument.

Source: P527, P538, P539 and P540.

Instances: the four lessons:
1. Stack only under the study's named conditions, at the parent's merge verdict (P527).
2. A cloud fire is logged with its session id, read back from `list_runs` about 2 min after the
   fire, never with the one-shot trigger id alone (P538).
3. An owner order with a trigger condition goes into the orchestrator's pending list the turn it is
   given, with its condition. A session rotation carries that list (P539).
4. `append-carry` takes no `--reason`. Read back the drain's refusal for every queued op (P540).

Cost: one playbook paragraph.

Binding: one carry, R10-ROUND-PLAYBOOK-FINAL (`carries/b141-P545.txt`).
