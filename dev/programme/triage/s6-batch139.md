# Proposal triage, session s13, batch 139 (P464 to P475)

The bar is `dev/governance/roles/proposal-triage.md` at origin/main `0a8033305d`, read with the
owner's two rulings of 2026-11-08 that the brief for this batch restates:
- A new proposal is accepted only on a measured improvement of more than 20 % in CI time,
  programme completion time, right-first-time or token usage.
- A planned machinery group or lane stays on at least 10 %.
- A repair of machinery outside `custom_components/` with severity `low` or `normal` (minor) is not
  exempt as a defect countermeasure. It takes the bars, over 20 % to add.
- Severity `medium` and above, a root-cause countermeasure, closeout and an owner directive skip
  the bars. An unset severity is classified here first, never assumed major.

Each improvement is measured against the process stage the defect touches, not against the
defect's own instances, because a repair always removes 100 % of its own instances. The base is
named in each entry.

Sources read:
- origin/main `0a8033305d`. Every file and line cited below is at this commit unless a PR head is
  named.
- The roster branch `origin/handoff/audit-r10-roster` at `b1de33a83a`.
- The session's local logs, named per entry: `s7/triage-queue-s7.txt` (lines 148, 149 and 151 to
  160, every line after batch 138's RULED line 150), `s13/merge-rerun-log-s137.txt`,
  `s13/merge-STATE-HANDOFF-s137.md`, `s9/sweep-runner/reconcile.py` with its
  `reconcile-holds.txt` backups, the opener's `s9/seat-opener/driver4.py` with its `fails.txt`,
  `cloud-relay.daemon.log`, and `state-mirror/plan.html` (07:56Z).
- Git refs: every `verdict/*` ref (fetched 2026-11-09 about 08:20Z), the heads of open #3345,
  #3359 and #3366, and `handoff-body/r10-hotfix-codeql-headroom-p2` `ffaa1a54`.
- API reads, each named beside its figure: the gate-sweep workflow state, PR listings and PR
  bodies.

Seams. Three lines share one cause, the gate deferral that nothing re-runs: P465, P468 and P470.
They are ruled together through P465. Two lines are the orchestrator's session-local stand-ins and
not tracked code: P464 (the sweep runner) and P474 (the opener driver).

## P464: HOLD-MASKS-NEW-VERDICT, a reconcile hold hides a verdict that returned under it

Verdict: REJECT as tracked work. The tool is session-local, and the measured gain is below the bar.

Source: queue line 148 (2026-11-09T04:01:31Z).

Severity: low. The stand-in reported every masked key once its hold expired. Nothing was lost.

Instances:
- `s9/sweep-runner/reconcile.py` lines 72-99 hold a key by prefix until the hold line's own
  expiry. Nothing compares the hold with a later verdict. It is not in the tree (`git ls-tree -r
  origin/main` has no `reconcile.py`).
- `reconcile-holds.txt.bak-0209` and `.bak-0402` hold #3350, #3339 and #3329 until 03:30Z, and
  #3361 and #3362 until 06:00Z. The queue line's "until 03:30Z" is right for three of the five.
- The verdict refs confirm all five blocked verdicts: #3362 at 02:44Z, #3329 at 03:01Z, and the
  others as the queue line states.

Measured gain:
- The masked delay is 5 PRs at about 65 min, 325 min in all (queue line's figure).
- The base is the blocked-verdict cycle since 11-08 00:00Z. There are 58 blocked verdicts on
  `verdict/*` (`git log --since=2026-11-08T00:00Z`, `grep -c 'Fix review: blocked'`). At the 3.4 h
  median blocked cycle that R10-REVIEW-ENUMERATE's brief records, that is about 11,800 min.
- 325 of 11,800 min is 2.7 %, below the 20 % bar.

Cost: one comparison in a session-local script (a hold yields when `verdict/<pr>`'s tip is newer
than the hold line).

Binding:
- 2.7 % against the 20 % bar.
- The cheaper course is the orchestrator's: patch the stand-in locally.
- The tracked successor of the sweep runner is R10-FLY-STANDING-CONTRACTS. Its brief already lists
  "hold-file lines never expire" as a defect for its design to remove, so its designer reads this
  seam already. No roster op.

Carry: dismissed: session-local stand-in, 2.7 % of the blocked-verdict cycle

## P465: DEFERRAL-RERUN-INSTRUMENT, a tracked instrument for the hand re-run of a deferring gate

Verdict: REJECT the new instrument as a duplicate. The tree already holds it: `tools/ci/sweep.py`
`settle`, run by `.github/workflows/gate-sweep.yml`. That workflow is switched off. Turning it back
on is the owed action, and it is the orchestrator's, not a roster op.

Source: queue line 149 (2026-11-09T04:03:26Z).

Severity: medium. Every deferral red blocks a merge until someone re-runs it.

Instances:
- `gh api repos/tvofi/heatpump_optimizer/actions/workflows/gate-sweep.yml`: `state
  disabled_manually`, updated 2026-11-08T11:54Z. Its last runs are 2026-11-08 12:21-12:22Z, all
  success (`gh run list -w gate-sweep.yml`).
- The merge seat's rule says why: "Gate-sweep is disabled (until hotfix #3327 merges)"
  (`s13/merge-STATE-HANDOFF-s137.md`, the deferral-rule line).
- #3327 (R10-HOTFIX-SWEEP-SETTLE-LOOP, "stop sweep.settle re-running sibling gates on re-stamped
  skipped jobs") merged 2026-11-08T22:02:10Z (`gh pr list --search 'sweep settle'`). Its code is on
  main: `34b98bbdb6` and `6158186e11` in `git log origin/main -- tools/ci/sweep.py`.
- The workflow has stayed off since that merge. `s13/merge-rerun-log-s137.txt` holds 55 hand
  re-runs from 22:04Z on 11-08 to 07:14Z on 11-09. 46 of them are gate-deferral re-runs: the
  `deferral`, `gate job` or `gate (` lines, less the 5 CodeQL-cap lines and 4 other causes.
- The same cause reaches reviews. Of the 26 CI-class blocked verdicts since 11-08 (`verdict/*`,
  `blocked <sha> ci-` or `gate-`), 9 name a deferral that nothing re-ran: #3333, #3291 (twice),
  #3341, #3352, #3364, #3348, #3360 and #3329 at `4818b1a2`. #3359's names a gate red "never
  re-run" without saying deferral, and it is not counted. Two of the 9, #3291 and #3348, say
  "gate-sweep is disabled" in the verdict.

Cost of the proposal: a new `merge_train.py` sub-command and beat row that would re-implement
`sweep.settle`, a second owner of one rule.

Binding:
- No roster op.
- The orchestrator decides whether #3327 is enough to turn `gate-sweep.yml` back on, and records
  the decision. The settle loop's own RCA, #3329 (R10-RCA-SWEEP-SETTLE-LOOP, open), holds the
  replay harness that tests that choice.
- While the workflow stays off, the hand rule in the merge seat's handoff stands. It costs about 46
  re-runs and 9 review rounds a night.
- P468 and P470 below are this same cause, so each is deferred until the sweep runs again.

Carry: dismissed: duplicate of tools/ci/sweep.py settle; re-enable gate-sweep.yml (orchestrator)

## P466: PACKET-READS-RUN-ID-AS-SHA, the carry-landed check reads a run id as a commit

Verdict: REJECT at the bar. The defect is real and reproduced. One open body in 35 hits it.

Source: queue line 151 (2026-11-09T04:18:34Z).

Severity: low. The packet fails closed (UNAVAILABLE). Rewording the body clears it.

Instances:
- `tools/audit/seat/review_packet.py` line 260, `LANDED`, captures `\b([0-9a-f]{7,40})\b` after
  "landed". All-digit strings are allowed, against `brief_lint.mjs`'s `SHA_RE` (line 247), which
  requires one `a-f` letter. Reproduced: `LANDED.findall('Carry 5 landed: A 1760-job run (run
  42454528717)')` gives `[('5', '42454528717')]`. `is_ancestor` (line 335) then raises
  `Unavailable`.
- The pattern also reads prose. #3361's body line 11 says "origin/main ... meanwhile landed a
  second design" inside a `Carry 5` line, so the match is not a landing claim at all.
- Recurrence: of 35 open PRs, the body that matches `carry N ... landed ... <7+ digits>`
  (`gh pr list --state open --json body` with a jq `test`) is #3361 alone. Local logs hold one
  `is-ancestor <all-digit>` failure, this one.

Measured gain: 1 of 35 open PRs' dispatch path (2.9 %). Below the 20 % bar.

Cost: about 3 lines (the `a-f` look-ahead `brief_lint.mjs` uses), one fixture and one null control.

Binding: 2.9 % against 20 %. The workaround is to cite a run id off the `Carry N ... landed` line.
A third instance goes to `root-cause.md`, not to triage again.

Carry: dismissed: 1 of 35 open bodies; below the bar

## P467: RELAY-MINTS-UNPUBLISHED, the relay mints a nonce and publishes no reviewer payload

Verdict: DEFER until it is measured. The owning group is R10-RELAY-SWEEP (carries-open, owns
`cloud_relay.sh`).

Source: queue line 152 (2026-11-09T04:48:47Z).

Severity: low. A fire from the stale ref is refused by `push-verdict`, so it fails closed. The
cost is a hand step.

Instances:
- `tools/audit/seat/cloud_relay.sh` lines 635-637: the handoff arm runs `bus.sh dispatch <pr> <nh>
  cloud`, keeps `bus-nonce:` and opens `reviewer-fire <pr> <nh> nonce=...`. No
  `cloud_dispatch.py ... --publish` follows. `cloud_dispatch.py` has the `--publish` path (line 697)
  and takes `--nonce` (line 1182).
- The queue line's figures are #3339 at 04:40Z and #3350 at 04:46Z, about 5 min and one seat turn
  each.

Not measured: how many relay-moved heads there were, and what share of their apply-to-fire time
the hand publish takes. The relay's local logs carry no timestamps on their `OWED reviewer-fire`
lines (`cloud-relay.daemon.log`, `cloud-relay.log`), so this seat could not count them.

What would change it: the apply-to-fire latency of relay-moved heads over one day, read from
`dispatch/reviewer-rev-<pr>` commit times against the relay's `reviewer-fire` opens. If the hand
publish is more than 20 % of it, the proposal passes as a carry on R10-RELAY-SWEEP.

Carry: dismissed: deferred, unmeasured; owner R10-RELAY-SWEEP

## P468: BODY-PATCH-LEAVES-STALE-REDS, a body patch leaves an older run's pr-contract red

Verdict: DEFER. This is P465's cause, so it is re-measured once `gate-sweep.yml` runs again. The
owning group is R10-BODY-CONTRACT (carries-open, owns `body_patch.sh`).

Source: queue line 153 (2026-11-09T05:45:22Z).

Severity: low. Two instances, each cured by one re-run.

Instances:
- #3355 is real: `s13/merge-rerun-log-s137.txt` at 05:45:13Z and 05:49:31Z re-ran the code run's
  failed jobs and two gate jobs after the 05:36Z body patch.
- `merge_train.py` `latest_runs` (lines 400-410) keeps the worst gate suite on purpose, because
  GitHub's ruleset refuses a merge while any suite's gate is non-success (the comment at lines
  386-393). So option (b), the newest result only, would let the train pass a head GitHub then
  refuses. It is not adopted.
- Option (a), a re-run from `body_patch.sh`, is the job `sweep.settle` does for a gate whose source
  changed, under #3327's rule "re-runs a bot-started gate only past a new source"
  (`git log origin/main -- tools/ci/sweep.py`, `34b98bbdb6`). With the workflow off, nothing
  re-judges it.

What would change it: with `gate-sweep.yml` running, a body patch at a head whose code run's gate
judged the old body still leaves a red after one sweep interval. Then option (a) passes as a carry
on R10-BODY-CONTRACT.

Carry: dismissed: deferred behind P465 (gate-sweep off); owner R10-BODY-CONTRACT

## P469: OWED-UNKEYABLE-FIXER-ROUND, the keyer cannot read the tick's own fixer-round line

Verdict: REJECT as a duplicate. It is already built, at open #3345 (R10-TICK-LEVELS part 2), which
delivers R10-TICK-LEVELS carry 16.

Source: queue line 154 (2026-11-09T05:45:41Z).

Severity: low (board noise; the PR it names is legitimately held).

Instances:
- At origin/main, `tools/audit/seat/owed_unactioned.py` `key_of` (lines 79-113) raises
  `Unreadable` on `-> OWED fixer-round #3299 e225451599cf blocked at head, no repair in 9h`, and
  on the same shape for `dirty` (reproduced by loading the module).
- At #3345's head `1c29e5ab`, the same lines key `('#3299', ['e225451599cf'])` for both kinds.
  Its new arm `OWED [a-z][a-z-]* (#\d+) ([0-9a-f]{12}) ` and its self-test loop over `body-ahead`,
  `train-parked`, `recut`, `fixer-round`, `dirty` and `red-unowned` cover it. An OWED line naming
  no PR stays `Unreadable` there, the null control.
- R10-TICK-LEVELS carry 16 (from batch 133's P416) asks for exactly that: "a self-test that every
  owed kind the tick emits in its own fixtures has a key arm".

Cost: none beyond #3345's merge.

Binding: no roster op. The noise ends when #3345 merges. Its reviewer can take this line as one
more instance.

Carry: dismissed: built at open #3345 (R10-TICK-LEVELS carry 16)

## P470: SKIP-DEFERRAL-NOT-ENVIRONMENT, a gate-deferral skip is not re-admitted at its verdict

Verdict: DEFER. The owning group is R10-TRAIN-REJOIN-NO-RECARRY (in-progress, open #3359), and
the cause is P465's.

Source: queue line 155 (2026-11-09T05:54:49Z).

Severity: medium (it holds a merge-verdicted PR out of a live train for hours). That skips the bar.
It is still deferred, because the work it asks for is in flight and its cause is turned off.

Instances:
- `tools/audit/seat/merge_train.py` `already_held` (lines 1224-1250) re-admits a same-verdict
  skip only when its class is in `READMIT_SAME_VERDICT` (line 973: HOLDER, BRANCH-POLICY,
  PRE-FLIGHT).
- `s13/merge-STATE-HANDOFF-s137.md`, batch 20261108-230008: "#3337 SKIP (gate deferral)" and
  "#3330 SKIP (gate deferral)". Both read GREEN later at the same verdict.
- #3359's head `6ccb12bd` adds `Train.rejoin`: a GATE-red skip rejoins once its head classifies
  GREEN within the train's wait cap. RED never rejoins. That is the owner's card-1 ruling of
  2026-11-07, "with no merge-seat re-add".
- What #3359 leaves is a gate skip whose deferral red outlasts the cap. With `gate-sweep.yml` on,
  `settle` re-runs a deferral minutes after its decider ends. The skips in the queue line all fell
  in the hours the workflow was off (P465).

What would change it: after #3359 merges, with `gate-sweep.yml` running, a GATE-class skip that is
GREEN at its verdict and refused by `already_held` on re-add. Then add a GATE class to
`READMIT_SAME_VERDICT`, admitted only when classify at add reads GREEN. It goes as a carry on
R10-TRAIN-REJOIN-NO-RECARRY.

Carry: dismissed: deferred behind #3359 and P465; owner R10-TRAIN-REJOIN-NO-RECARRY

## P471: PREFLIGHT-PATH-MASKED, a hand pipe hid a wrong preflight path

Verdict: REJECT. One instance with no harm, in a hand pipe the orchestrator writes, not a tracked
tool.

Source: queue line 156 (2026-11-09T06:23:35Z).

Severity: low. The comment it guarded was clean: preflight was run afterwards, per the queue line.

Instances:
- `tools/pr/preflight.sh` is the tracked path (`git ls-tree -r origin/main`).
  The script the queue line's pipe named, directly under `tools/audit/`, does not exist.
  `tools/audit/seat/instruments/preflight.sh.md` names the right path already.
- `tools/pr/gh_comment.py` is the posting instrument `comment-readback.md` names. A hand
  `| tail -2 && post` bypasses its read-back.

Cost: a tracked wrapper is a new file for one slip. The cheaper cure is the orchestrator's: run
`tools/pr/preflight.sh` under `set -o pipefail` (or without a pipe), then `gh_comment.py`.

Binding: one instance and no measured cost, against a new file. A recurrence goes to
`root-cause.md`.

Carry: dismissed: one harmless hand-pipe slip; session practice

## P472: MANDATE-APPROVE-INSTRUMENT, the train posts the mandate approval on code-owned heads

Verdict: REJECT at the bar.

Source: queue line 157 (2026-11-09T06:33:33Z).

Severity: not a defect. It is a new capability (`policy_approve` posts only for policy paths, by
design, at `merge_train.py` lines 2296-2319).

Measured gain:
- The proposer's figure is 3 recarries this session (#3352, #3361, #3348) at 5-10 min each, 15-30
  min in all.
- The base is first-merge-verdict-to-merged on machinery PRs, p50 2.5 h, from R10-PROCESS-SLIM's
  card C4 measurement on the roster.
- 5-10 min of 150 min is 3 % to 7 % per affected PR, below 20 %.

Cost:
- A new approval path in the train for every CODEOWNERS head, with its carry and read-back arms.
- Who approves a code-owned path is decision 0011's (only `@tvofi` reviews code-owned paths; a
  mandate makes the orchestrator that approver). A tool that posts it widens an approval machine,
  and that is the owner's to want.

Binding: 3 % to 7 % against 20 %, plus an approval-authority change no ruling asked for.

Carry: dismissed: below the bar; approval authority is the owner's

## P473: PLAN-PAGE-NONE-LEAK extension, two more render defects on the public plan page

Verdict: ACCEPT. Items (2) and (4) ride beside P461 on R10-OUTSIDE-INTAKE as one new carry.
Items (1) and (3) are already P461 and that group's carry 1, so they get no new op.

Source: queue line 158 (2026-11-09T06:59:04Z).

Route: owner directive. R10-OUTSIDE-INTAKE builds the page the owner ruled public on 2026-11-06
("the plan html for an ongoing round should be made publically available", quoted in its brief).
A public page that states the programme wrongly fails that directive, so the bar is skipped on
that route. This entry does not rest on reading "low or normal meets both" as a pass. The owner's
2026-11-08 ruling makes a low repair take the bars.

Instances, against `state-mirror/plan.html` at 07:56Z:
- (1) `data-wave="None"` 1 and `wave None` 1. This is P461 and needs no new op.
- (2) The status strip reads `<b>0</b><span>part merged, residual open</span>`, while the page
  holds 96 occurrences of `carries-open, part merged` (`re.findall`). The strip's count and the
  table's label come from two predicates that disagree. That is a correctness defect, not wording.
- (3) "1 other open issues are on no open group ... and the 0 listed below as unplanned". This is
  R10-OUTSIDE-INTAKE carry 1 (the count sentence) and needs no new op.
- (4) 4 group descriptions render a raw markdown heading (`class="d"># Fixer brief ...`), for
  example the O10-policy-fixer-md and O10-policy-gate-scoping rows. The queue line also reports
  one stray newline carrying triage text, which this seat did not locate in the 07:56Z page.

Cost:
- (2) is one predicate shared by the strip and the table.
- (4) strips a leading markdown heading and joins lines when a description renders.
- Both go in `tools/audit/seat/plan_page.py`'s render seam, with arms in its `--self-test`. No new
  file.

Binding:
- Carry on R10-OUTSIDE-INTAKE (carries-open), and `set-files --add tools/audit/seat/plan_page.py`.
  The group's `files` do not list it, although P461's carry and open #3350 both edit it, and no
  live group lists it (roster at `b1de33a83a`: every group naming `plan_page.py` is done or
  absorbed).
- Failing test first: a self-test plan with one group at stage carries-open and a merged part
  counts 1 in the strip, the same as its row. A description whose text begins `# Fixer brief`
  renders without the `#`.
- Null control: a plan with no part-merged group still reads 0, and a description with no heading
  is unchanged.
- Mutant: counting the strip from the old predicate reads 0 again.

Carry: R10-OUTSIDE-INTAKE

## P474: OPENER-STRIPPED-TOPIC-MISREAD, the opener cannot find the group of a -p2 topic

Verdict: REJECT as tracked work. The tracked `open_driver.py` resolves this exact body. The
defect is in the session-local opener stand-in.

Source: queue line 159 (2026-11-09T07:07:19Z).

Severity: low as code. The cost was high: about 1.4 h on the critical path's unblocking hotfix.
That is an argument for running the tracked opener, not for a tracked fix.

Instances:
- `tools/audit/seat/open_driver.py` `resolve` (lines 97-117) strips one trailing `-p<N>` and
  checks that the body's first lines name the group as a whole word (`names_group`, line 92).
  Driven with the roster group and the first three lines of `handoff-body/
  r10-hotfix-codeql-headroom-p2` `ffaa1a54`, it returns `('R10-HOTFIX-CODEQL-HEADROOM',
  'R10-HOTFIX-CODEQL-HEADROOM (part 2): r10 hotfix codeql headroom p2')`.
- The line that printed `NEEDS-TITLE/GROUP (no roster group for topic)` is
  `s9/seat-opener/driver4.py` line 66. It sets `g = t.upper()` and never strips a part suffix.
  `s9/seat-opener/fails.txt` holds the three tries at `a325da38`.
- R10-HANDOFF-PATH carry 14 (the `-p<N>` suffix) was verified as built at its merge base by #3293
  (arm "sav-comfort-p2").

Cost: none tracked. The session-local fix is the orchestrator's: retire `driver4.py` for
`tools/audit/seat/open_driver.py`, or call its `resolve`.

Binding: no roster op. Batch 138's P462 also rejected an opener half as session-local. This is the
second opener stand-in defect in two batches, and the tracked opener has neither.

Carry: dismissed: session-local opener; tracked resolve() already handles it

## P475: REVIEWER-BLOCKS-ON-WAIT, cloud reviewers block a head that is still waiting on CI

Verdict: ACCEPT, medium, as the class's countermeasure. The barrier is already planned as
R10-DISPATCH-AT-HANDOFF carry 12, which is unbuilt, and the 2026-11-08 dispatch ruling made it
due.

Source: queue line 160 (2026-11-09T07:14:21Z).

Severity: medium. Each instance is a full review round, and one of them pushed #3329 past the
three-round rule. It is a third instance, so it routes as a countermeasure and skips the bar.

Instances (`verdict/*` refs):
- #3345 `4a6e3e6a` at 05:12Z: "blocked 1c29e5ab ... ci-pending: classify still WAIT (rc 3) after
  ~50 min".
- #3362 `ce35fbd4` at 05:57Z: "blocked e1c061cf ... ci-unsettled: ... still exits 3 (WAIT) after
  about 35 min; no defect found in the diff".
- #3329 `419fef3a` at 23:45Z on 11-08: "blocked 1310d182 ... ci-incomplete: ... code run
  42524776987 cancelled".
- Since 11-08 00:00Z, 26 of 58 blocked verdicts are CI-class (`blocked <sha> ci-` or `gate-`): 20
  ci-red, 2 ci-cancelled, 1 each ci-pending, ci-unsettled, ci-incomplete and gate-red. The
  deferral share of them is P465's. The WAIT and cancelled share (5) is this line's.

Why now:
- #3366 (R10-DISPATCH-AT-HANDOFF part 2, open) reads its carry 7 as "superseded by the
  orchestrator ruling of 2026-11-08 (WAIT dispatches, only RED holds)". Reviewers are now fired at
  WAIT heads.
- Carry 12 is the other half, which #3366 leaves "untouched here". It says a reviewer whose review
  is complete pushes its drafted verdict with a `pending-ci` marker, and the relay posts it when CI
  settles. That is the proposal's candidate (a). Without it, the reviewer's only exits are to wait
  unboundedly or to block.

Cost:
- As carry 12 states: the reviewer contract's pending-ci exit, a relay arm that posts on GREEN and
  reports on a moved head, and its controls.
- No new file in the group's seam (`bus.sh`, `review_packet.py`, `fix-review.md`,
  `standing-dispatch.md`).

Binding: carry on R10-DISPATCH-AT-HANDOFF (carries-open).
- Build carry 12 next, with these three instances as its failing cases.
- A WAIT head with a finished review posts `pending-ci`, never `blocked`. A cancelled code run is
  reported for a re-run, not blocked.
- Whether a CI-only block counts toward the three-round rule is `fix-review.md` text, which is
  policy. The body states it and the owner approves it at the merge.
- Null control: a head whose classify reads RED on a required context still returns `blocked`.
- Mutant: dropping the pending-ci arm makes the #3345 fixture block again.

Carry: R10-DISPATCH-AT-HANDOFF
