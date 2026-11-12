# Proposal triage, session s13, batch 138 (P459 to P463)

The bar is `dev/governance/roles/proposal-triage.md` at origin/main `3fdaa9da9a`, as batch 137 read
it. A new proposal is accepted on a measured gain of more than 20 %. A planned machinery group or
lane stays on at least 10 %. A repair of machinery outside `custom_components/` with severity `low`
or `normal` meets both bars. Severity `medium` and above, a root-cause countermeasure, closeout and
an owner directive skip them. An unset severity is classified here first, never assumed major.

Sources read:
- origin/main `3fdaa9da9a` (every file and line cited below is at this commit).
- The roster branch `origin/handoff/audit-r10-roster` at `ccc3286441`, and its history.
- The session's local logs, named per entry: `s7/triage-queue-s7.txt` (lines 143 to 147, every line
  after batch 137's RULED line 142), `cloud-relay.daemon.log`, `s11/ci_priority.log`, the opener's
  `s9/seat-opener/driver3.py` and its logs, and `state-mirror/plan.html` (04:57Z).
- The handoff and design refs of R10-HOTFIX-CODEQL-HEADROOM, and the body of closed #3365.
- API reads, each named beside its figure: one job listing over 20 main `ci.yml` runs, PR listings,
  and a #201 comment search.

## P459: CARRY-STATUS-DISAGREE, body_push passes a status line that dispatch refuses

Verdict: ACCEPT, as a low repair. It meets the bar. The proposal's cure is already built: both
readers call the one predicate. The defect is the source each passes it.

Source: queue line 143 (2026-11-09T02:31:48Z).

Instances:
- `tools/audit/seat/body_push.sh` lines 181-182 run `carry_audit.py landed --body ... --topic
  "$TOPIC"`. `tools/audit/seat/bus.sh` `carry_landed` (lines 232-233) runs the same `landed` with
  `--pr "#$1"` and no topic.
- `tools/audit/carry_audit.py` `own_group` (lines 586-594) resolves the own group only from
  `pr_group` or a non-`#` token. With `--pr "#3345"` alone it returns None, so `own_carry_status`
  (line 626) never runs. The `Carry 26 (...)` status line `becd0c23` then reads `CARRY-MISSING`
  (`cloud-relay.daemon.log`: `CARRY-MISSING R10-TICK-LEVELS body item becd0c23: not in its brief or
  carries`, then `bus: REFUSE: dispatch: #3345's body routes a carry its group does not hold`).
- Recurrence: `cloud-relay.daemon.log` holds CARRY-MISSING dispatch refusals for 11 PRs (`grep -o
  "dispatch: #[0-9]*'s body routes a carry"`). Their distinct missing lines are 9. Only `becd0c23`
  names its own group by index. #3293's `Carry 1: stays carried` line routes to
  R10-FLY-STAMP-FLUSH-COST, not its own R10-HANDOFF-PATH, so it was a real miss. One instance in 11.
- Cost of the instance: the reviewer for #3345 waited. The orchestrator worked around it by landing
  the status line as a roster carry (`s7/carries/s13-3345-becd0c23.txt`, `#done` in
  `s7/roster-queue-s7.txt`), which adds a duplicate carry to R10-TICK-LEVELS.

Cost: `carry_landed` already reads `repos/<repo>/pulls/<n>`. It keeps `.head.ref` as well, strips
`fix/` and `-pr`, and passes `--topic`. That is about 3 lines and one arm of `bus.sh`'s self-test.
No new file and no new API call.

Binding: carry on R10-DISPATCH-AT-HANDOFF (carries-open, owns `bus.sh`; its seam is the dispatch
gate's carry refusal).
- Failing test first: a body whose own-group `Carry <i>:` status line `body_push` passes is
  refused by `carry_landed` today, and is admitted after the fix.
- Null control: an own-group line with no index, or an index past the group's carries, still lands
  or refuses as `body_push` says.
- Mutant: dropping `--topic` refuses the status line again.

Carry: R10-DISPATCH-AT-HANDOFF

## P460: CI-PRIORITY-PAUSES-AWAITING-REVIEW, the pause cancels a head that owes a reviewer

Verdict: REJECT as tracked work. The line's destination, R10-CI-PRIORITY-PAUSE, is `refused` at the
roster tip. The tool at fault is the session-local stop-gap `s11/ci_priority.py`, which no tracked
group owns.

Source: queue line 144 (2026-11-09T02:46:14Z).

Instances:
- `s11/ci_priority.log` (`grep -c "PAUSE run [0-9]* <branch> "`): #3326 (`fix/r10-fly-replan-defects`)
  was paused once, at 23:33Z on 11-08. #3347 (`fix/r10-sav-comfort-p4`) was paused twice, at 20:53Z
  and 23:20Z. #3345 (`fix/r10-tick-levels-p2`) was paused twice, at 20:45Z and 02:44Z.
- The stop-gap's rate (`s11/ci_priority.log`, by day): 49 PAUSE on 11-07, 37 on 11-08 and 8 on
  11-09 to 03:44Z. Each PAUSE is a cancel and a re-run.
- The group's measured ceiling: P428 (batch 136, `handoff/triage-s13-batch136`) dropped
  R10-CI-PRIORITY-PAUSE. The queue time a pause could return is 2.7 % of main CI wall time. The
  roster note reads "keep test failed (owner bar 2026-11-08, >=10%)".

Cost: a skip arm in the stop-gap needs one roster or ledger read per pass. A tracked version would
re-open a group the keep test refused.

Binding:
- The ceiling is 2.7 %, below the 10 % keep bar. Against it, the line's 3 PRs each lost a reviewer
  round, in 45 pauses on 11-08 and 11-09.
- The cheaper course is the orchestrator's call: retire the stop-gap, which serves a dropped group.
  If it keeps running, the orchestrator can add a session-local skip for heads with an open
  `dispatch/reviewer-*` or an owed reviewer-fire line. Neither is a roster op.

Carry: dismissed: destination group refused by P428 and the tool is session-local; retire or patch it locally

## P461: PLAN-PAGE-NONE-LEAK, the public plan page prints Python `None` and list reprs

Verdict: ACCEPT, as a low repair. It meets the bar, and it lands on the owner-directed public page.

Source: queue line 145 (2026-11-09T03:23:28Z).

Instances:
- `tools/audit/seat/plan_page.py` lines 340 and 342 write `r["wave"]` raw into `data-wave` and the
  `<title>` tooltip. Line 260 sets `wave` to None for a group the plan gives no wave, and line 264
  does the same for a group the plan counts done. The table already guards the same field with
  `{r["wave"] or "—"}` (line 524).
- The tooltip's `sort key {pg['sort_key']}` (line 255) prints a Python list repr. A null in
  `replan.py`'s `sort_key` (`plain(priority(n))`, line 1254) then shows as `None`, with HTML-escaped
  quotes.
- `state-mirror/plan.html` at 04:57Z (`grep -o`): 1 `data-wave="None"`, 1 `wave None` (R10-CATALOG-PR),
  and 51 `sort key [...None...]`. The queue line counted 53 at 03:19Z.
- The open #3350 (R10-OUTSIDE-INTAKE part 2) does not fix it: its head's `plan_page.py` still holds
  both raw writes, at lines 353 and 355.

Cost: render `—` (or omit the attribute) for a missing wave, and format the sort key as plain
values. That is a few lines and one `plan_page.py --self-test` fixture. No new file.

Binding: carry on R10-OUTSIDE-INTAKE, beside its carry 1. That carry is the plan-page count-sentence
fix in the same file and the same render seam, from the 2026-11-08 plan-page read, and it is not yet
built. The group owns the public plan page under the owner's 2026-11-06 ruling. No live group lists
`plan_page.py` in `files`.
- Failing test first: a self-test group with no wave and a sort key holding a null renders no
  `None`.
- Null control: a group with wave 3 still renders `wave 3` and `data-wave="3"`.
- Mutant: dropping the guard prints `None` again.

Carry: R10-OUTSIDE-INTAKE

## P462: OPENER-LOST-HANDOFF, a closed PR's surviving branch discharges a successor handoff

Verdict: ACCEPT the tracked half as a low repair to R10-TICK-LEVELS (`ledger.py`). REJECT the opener
half: it is session-local.

Source: queue line 146 (2026-11-09T03:51:14Z).

Instances, against code:
- `handoff/r10-hotfix-codeql-headroom` `2d7bc354` merges origin/main `6457496aba` into `4a3932f5`.
  Closed #3365's branch `fix/r10-hotfix-codeql-headroom-pr` `9ef6799d` merges the same `6457496aba`
  into the same `4a3932f5`, and both trees are `6a141abceb` (`git rev-parse <c>^{tree}`).
- `tools/audit/seat/ledger.py` `landed` (line 464) reads a tip as carried when the only commits
  outside main and the fix heads are merges (`merges-only`). The relay's level, `handoff_level`
  (line 490), passes every fetched `fix/*` ref as heads (line 499), including a closed PR's branch. So the successor handoff read as discharged, and
  no `handoff-no-pr` line reached the board. `bus.sh` orphans (lines 857-858) pass the same
  `$fix_heads`.
- The opener half: `s9/seat-opener/driver3.py` line 48 skips on any `fix/<t>` or `fix/<t>-pr` ref.
  Its seen-set is keyed on `(topic, sha)` (line 79), so a body re-pushed at the same code sha is
  never retried.
- Recurrence: 13 PRs were closed unmerged since 10-25 (`gh pr list --state closed`, mergedAt null).
  4 left a `fix/*` branch with no open PR. In 3 of the 4 the handoff tip is a strict ancestor of the
  closed branch (`git merge-base --is-ancestor`), so the handoff was delivered and then closed; that
  is correctly discharged. In 1 (this one) the tip is a successor, `merges-only`. One 50-minute
  critical-path stall in about 15 days.

Cost: in `ledger.py`, a closed or branch-only `fix/*` head may discharge by `ancestor` and never by
`merges-only`. The relay already holds the open-PR list (`cloud-prs`), and the level passes it, or
`landed` takes a second head list. About 10 lines and two self-test arms. No new file.

Binding: carry on R10-TICK-LEVELS (carries-open, owns `ledger.py`; the classifier the relay's level
and `bus.sh` orphans share).
- Failing test first: the codeql shape. A tip whose tree equals a non-open `fix/*` head's, outside
  it only by a merge, is owed.
- Null control: a tip that is a strict ancestor of a closed PR's branch stays discharged (the 3
  delivered-then-closed topics). A tip `merges-only` against an open PR's head stays discharged.
- Mutant: restoring every `fix/*` head to `merges-only` discharges the codeql shape again.
- The opener's skip and its seen-key are the orchestrator's session-local driver; no roster op.

Carry: R10-TICK-LEVELS

## P463: CODEQL-HEADROOM-PREMISE-FAILED, ruling for R10-HOTFIX-CODEQL-HEADROOM

Verdict: ACCEPT, re-scoped (of keep, re-scope or refuse: re-scope). The group stays, and it stays
a cap change, as its roster brief already says. The wrap handoff (`2d7bc354`, body `42108817`) is
refused and is not opened.
- The cure is the python-leg timeout in `.github/workflows/codeql.yml` by design note
  `design/r10-hotfix-codeql-headroom` `e64e8fdb` section 3: a per-leg matrix cap, python 75 and the
  other two legs 45.
- The fixer is dispatched fresh from origin/main, not from the handoff.
- The group is severity `medium` in the CP lane, so it skips the bar.

Source: queue line 147 (2026-11-09T03:52:01Z); `handoff-body/r10-hotfix-codeql-headroom` `42108817`;
#3365 (closed, its body read by `gh pr view 3365 --json body`).

The owner's ruling, as recorded:
- The only record is the roster's relay of it, at the group's creation (`c07086ac4e`, 2026-11-06,
  `append-group`). Verbatim: "Owner ruling tvofi 2026-11-06 (coordinator, via the dispatch seat):
  lower priority than #3232." The same brief goes on: "Cure the cause, not the cap: move the large
  module-level code of tests/features.py and tests/entities.py into functions called once [...] and
  do not raise the cap or exclude files from the scan."
- The owner's own words are in neither the tree nor the roster. A search of #201's comments from
  2026-11-06 to 2026-11-08 finds none that names CodeQL (`gh api .../issues/201/comments?since=...`,
  `test("(?i)codeql")`). So the record does not show whether "do not raise the cap" was the owner's
  sentence or the coordinator's brief.
- The roster tip withdraws it, verbatim: "Orchestrator ruling under mandate comment 6624093439,
  2026-11-07: re-scope. The owner ruling of 2026-11-06 (lower priority than #3232) stands for
  priority, but its cure [...] is REFUTED twice by measurement, so that cure and its instruction not
  to raise the cap are withdrawn." The 2026-11-08 ruling then scopes the group to "raise the CodeQL
  python job's timeout-minutes".
- Mandate 6624093439 is scope `all`, from 2026-11-04T06:18Z to 2026-11-14T18:14Z, so it covers the
  code-owned workflow.
- The ban on excluding files was never withdrawn. It stands, and the design's S3 (`paths-ignore`)
  stays out.
- The body's "the owner's ruling forbids both" is therefore stale for the cap and correct for the
  exclusion.

Instances:
- **The wrap's premise is refuted three times.**
  - Measurement 1: jobs 128428511054 and 128440898484 were capped against main's 26m27s (quoted from
    the roster brief).
  - Measurement 2: the recut body `3838ebda` found runner variance.
  - Measurement 3: #3365's body, run 42473930832, job 128711085671. It was cancelled at 45.1 min.
    Extraction ended at about 21 min: `features.py` took 1211 s, inside main's 817-1389 s, and
    `entities.py` 191 s against 343-688 s. So 23 min of query evaluation ran with no result, past
    the design's measured 9m09s-20m26s evaluation range on main.
  - The repair rounds that built `2d7bc354` were opener-driven re-merges of the #3266 wrap (prompts
    `864afb9e` and `a8dd6516` on `dispatch/fixer-r10-hotfix-codeql-headroom`). They were not
    dispatched against the re-scoped brief.
- **The cap binds now** (one API listing of the last 20 main `ci.yml` push runs, the `Analyze
  (python)` job per run, at 2026-11-09T05Z): 9 of 19 jobs were cancelled at exactly 45.1 min between
  11-08 15:22Z and 11-09 03:04Z. The 10 successes ran 29.6 to 44.1 min. The design's 480-job
  enumerator, from 10-25 to 11-07, reads 12 capped, with p50 rising from 30.4 to 42.2 min.
- **Null control:** the actions and javascript-typescript legs on the same runners read p99 at most
  2.3 min, with 0 capped (design section 1). The cancels are the python leg's length, not a runner
  outage.

Cost:
- Keep (the wrap): 4,700 changed lines in two hot test scripts, a permanent 20000-line guard, and no
  measured gain. `tests/features.py` is listed by six live groups (design section 1).
- Re-scope: about 10 lines in `codeql.yml` and the one `_analyze_cap` pin in `tests/entities.py`
  (about 15 lines, design section 7). No structure budget moves and no new file.
- A job split (design section 4: it triples the step list and its four pins) and a query-suite
  change (it drops analysis) both lose to the matrix cap.
- A `threads` change is unmeasured, and `features.py`'s extraction is one file on one thread, so it
  is not adopted.

Benefit: about half of main's python jobs on 11-08 completed no analysis. Each cancel reds main's
`gate` and every PR whose diff analyses python, and costs a 45-minute re-run. The board's re-run
lines on #3299, #3358 and #3360 are this.

Binding: carry on R10-HOTFIX-CODEQL-HEADROOM, and `set-files --add tests/entities.py`, because
design section 7 rewrites the `_analyze_cap` pin there. The roster dropped that file at
`a264ffe553`.
- The fixer cuts from origin/main and implements design `e64e8fdb` sections 3 and 7. It does not
  touch `tests/features.py` or the wrap, and does not exclude any file.
- The orchestrator retires handoff `2d7bc354` and its body unopened.
- The design's reopen trigger (any python job capped at 75, or a 7-day p90 over 65 min) and its S1
  recommendation (split `tests/features.py`) are the orchestrator's to put to the owner. They are
  not triage ops.

Carry: R10-HOTFIX-CODEQL-HEADROOM
