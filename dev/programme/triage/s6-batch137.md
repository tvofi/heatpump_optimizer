# Proposal triage, session s13, batch 137 (P437 to P458)

The bar is `dev/governance/roles/proposal-triage.md` at origin/main `6457496aba`, which now carries
R10-FLY-TRIAGE-BAR (#3310, merged 2026-11-09T00:07Z). A new proposal is accepted on a measured gain
of more than 20 %. A planned machinery group or lane stays on at least 10 %. A repair of machinery
outside `custom_components/` with severity `low` or `normal` meets both bars. Severity `medium` and
above, a root-cause countermeasure, closeout and an owner directive skip them. An unset severity is
classified here first, never assumed major.

Sources read:
- origin/main `6457496aba` (every file and line cited below is at this commit).
- The roster branch `origin/handoff/audit-r10-roster` at `9a4a04d55`.
- The session's local logs, named per entry: `s7/triage-queue-s7.txt` (the queue, lines 106 to 141),
  `s13/rca-noreturn/RCA.md` and its `ev/`, `<state>/merge_train/train.log`, `s13/dispatch-seat/`.
- No API call was needed: every figure below is from git or a local log.

Queue lines 123 to 130 (BODY-CONTRACT-CARRY-HYGIENE, SELF-CARRY-BARRIER, CARRY-WRITE-DEDUPE,
CARRY-INDEX-BASE) were ruled by the orchestrator's triage pass in `s7/triage-ruling-body-contract-hygiene.md`
and are not re-ruled here. Lines 131 and 133 are events, not proposals.

## P437: REVIEWER-NO-RETURN-WAIT, a reviewer in WAIT ends with no verdict ref

Verdict: ACCEPT, as the root-cause countermeasure (C1 and C2 of the RCA). It skips the bar. C3 is
REJECTED with the RCA's reason.

Source: queue line 141 (2026-11-09T01:40:05Z); RCA `s13/rca-noreturn/RCA.md`.

Instances:
- Four reviewers (#3339, #3350, #3297, #3325) ended `SUCCEEDED` with no `probe/rev-<pr>-<nonce8>`
  (`git ls-remote origin 'refs/heads/probe/rev-*'`, 1043 refs, none of the four; RCA section 1).
- Rate: 13 of 160 reviewer dispatches (8.1 %) on 11-07 and 11-08, 13 of 272 (4.8 %, an upper bound)
  since 11-05 (`ev/disp.txt`, RCA section 5). About 80 dispatches a day, so about 6 instances a day.
- Checked against code at `6457496aba`:
  - `tools/audit/seat/cloud_dispatch.py` `_prompt`: "on REFUSE stop: report its line as your result"
    (line 207); "3 is WAIT, so run it again", with no bound (line 231); "Never work around a hook or
    a refusal; report it in your result instead" (lines 306-307). No stop path writes the probe ref.
  - `tools/audit/seat/cloud_relay.sh` lines 692-693: "Reviewer and designer seats are out of scope:
    a reviewer's missing verdict is reviewer-fire's, in the ledger." The RCA shows the ledger's
    `reviewer-fire` closes at the fire (`cloud_dispatch.py:535-554`), so nothing detects a
    no-return.
- Process state: (c) for the prompt (followed, no terminal edge) and (a) for detection.

Cost:
- C2: one edit to `_prompt` plus self-test checks in `cloud_dispatch.py`'s own self-test. No new file.
- C1: about 30 lines and fail and pass arms in `cloud_relay.sh --self-test`. No new file.
- Neither file is on the policy caps (`node tools/policy/policy_lint.mjs --budgets` lists no
  `tools/audit/seat/*.py` or `*.sh`).
- Benefit: about 6 detections a day that today cost an orchestrator turn each, a wasted opus run of
  8 to 34 min and about 1 h of merge latency, unbounded when no one notices.

Binding:
- **C2, carry on R10-FLY-DISPATCH-RULINGS** (carries-open, owns `cloud_dispatch.py`; its seam is
  what a dispatched prompt instructs). Every reviewer stop path ends with a verdict on its probe ref:
  - A setup or hook refusal pushes `Fix review: blocked <head> seat-refused: <line>`.
  - A `review_packet` `required-red` does not stop the seat while `merge_train.py classify` reads
    WAIT; classify decides.
  - WAIT is bounded (the fixer states the bound from the returners' 37 to 66 min, RCA section 3),
    then the seat pushes `Fix review: blocked <head> ci-wait: <classify line>`. The seat never ends
    its turn while a background poll runs.
  - After the push the seat reads its ref back with `git ls-remote`.
  - Failing test first: the rendered reviewer prompt names a terminal push for each of WAIT,
    REFUSE and required-red. Null control: the fixer prompt is unchanged. A mutant deleting the WAIT
    bound fails.
- **C1, carry on R10-RELAY-SWEEP** (carries-open, owns `cloud_relay.sh`). `noreturn_arm` covers
  `dispatch/reviewer-*`: it owes `seat-no-return` when the dispatch tip is older than a reviewer
  threshold (the RCA proposes 5400 s) with no `probe/rev-<pr>-<nonce8>` and an unmoved head. The
  false comment at lines 692-693 is corrected. Self-test: fires on the four (`returned=0` in
  `ev/disp.txt`), silent on #3352, #3353, #3304 and #3359 (`returned=1`), and on a moved head.
- **C3 REJECTED:** dispatching only on a terminal classify delays every review behind hour-long CI.

## P438: UNBLOCKED-UNDISPATCHED, an opened gate with no dispatch reports nothing

Verdict: ACCEPT, as a repair of the tick's UNBLOCKED level, classified medium (critical-path
impact). It skips the bar.

Source: queue line 140 (2026-11-08T21:02:51Z).

Instances:
- `tools/audit/seat/orchestrator_tick.py` `plan()` (lines 1502-1524) flags `UNBLOCKED, not started`
  only for `UNBLOCKABLE_STAGES = (None, "", "not-started")` (line 214). A `carries-open` group with
  its gate open and no seat prints `in progress`. Of the 69 groups not done or absorbed at the roster tip, 32
  are `carries-open`; none of them can flag.
- Named instances: R10-OUTSIDE-INTAKE part 2 (undispatched 7.7 h after #3262 merged at
  2026-11-08T12:16Z, `git log origin/main` shows `4a9d2d5425`), R10-SAV-METER-FLOOR (critical path),
  R10-TRAIN-STALE-VERDICT-GUARD and R10-TRAIN-REJOIN-NO-RECARRY.

Cost: one predicate in `plan()` and one `ls-remote` of `dispatch/*` and `handoff*/<topic>` per pass,
which the tick already lists for other levels. No new file.

Binding: carry on R10-TICK-LEVELS (carries-open, owns `orchestrator_tick.py`).
- (a) A group in `carries-open` or `not-started` whose `after` groups are all done or carries-open
  and that has no dispatch, handoff or PR ref prints `UNDISPATCHED: <gid> <age>`, CP-marked as
  `designs_owed` marks.
- (b) A carry naming `start after #N` whose #N merged and whose topic has no dispatch ref prints the
  same line.
- Failing test first: the R10-OUTSIDE-INTAKE shape. Null control: a group with a live dispatch ref
  prints nothing. A mutant dropping the stage widening fails (a).

## P439: CLOUD-DISPATCH-DESIGN-REF-CASE, the design gate reads only the upper-case ref

Verdict: ACCEPT, as a low repair. It meets the bar.

Source: queue line 139 (2026-11-08T19:33:53Z).

Instances:
- `cloud_dispatch.py` line 474 reads `refs/heads/design-verdict/{group_id}` exactly, while the same
  file's reviewer prompt (lines 294-295) tells the design reviewer to push
  `design-verdict/{topic}`, and the topic is lower-case. So the instrument writes one spelling and
  gates on the other.
- `orchestrator_tick.py` `design_builds` and `designs_owed` already lower-case both sides
  (`ref[len(prefix):].lower()`), so the tick saw R10-COMBI-TANK's approval while dispatch did not.
- One instance: R10-COMBI-TANK needed `--design-exempt` (approve `a605014b` at
  `design-verdict/r10-combi-tank`).

Cost: a case-insensitive lookup, as the tick does, and one fixture. No new file.

Binding: carry on R10-FLY-DISPATCH-RULINGS (owns `cloud_dispatch.py`). Failing test first: an
approval at the lower-case ref passes the gate. Null controls: a `revise` at either spelling refuses;
no ref refuses. A mutant restoring the exact match fails the first arm.

## P440: CARRY-AUDIT-NONBLOCK-FP, a deferral word and a quoted Carry phrase refuse a verdict

Verdict: ACCEPT, as a repair, classified medium (it stranded a critical-path verdict about 6 h). It
skips the bar.

Source: queue line 138 (2026-11-08T19:24:52Z).

Instances:
- `tools/audit/carry_audit.py` lines 32-34 and 136: NONBLOCK matches `deferred\b` in prose, outside
  a section holding the block. The two refused relayed verdicts: #3327 (probe `ab457a6f`) and #3330
  (`7dd42751`), both at 19:08Z.
- The quoted `Carry:` half is already carry 47 of R10-BODY-CONTRACT ("indented Carry continuation
  and quoted Carry phrase, pinned by the seven refused verdicts", from the tick-blind RCA).

Cost: a section-kind scope on one regex and two fixtures. No new file.

Binding: carry on R10-BODY-CONTRACT, for its final part 5 beside carry 47 (the same parser seam;
the part is not yet dispatched, so this is not residue under the owner's 2026-11-08 closure ruling).
Fixtures from both probes: each is admitted. Null control: a real `[non-blocking]` item in a Block
section still owes its destination. Mutant: dropping the section scope refuses #3327 again.

## P441: OUTSIDE-CHAIN-STALL, an outside request's upstream chain idles unreported

Verdict: ACCEPT, already carried; no new op.

Source: queue line 137 (2026-11-08T19:04:45Z).

Instances: R10-COMBI-TANK (outside #3225) PR B sat about 33 h behind three predecessors. The
proposed line is carry 19 of R10-TICK-LEVELS at the roster tip: "From handoff/r10-rca-tick-blind,
body item 42c659b5: OUTSIDE-CHAIN-IDLE walks after-edges for outside-sourced groups."

Cost: nil beyond that carry.

Binding: R10-TICK-LEVELS carry 19 stands. The orchestrator adds no op.

## P442: DISPATCH-PAST-THREE-QUOTING, a session wrapper splits a reason with spaces

Verdict: REJECT.

Source: queue line 136 (2026-11-08T18:40Z).

Instances:
- `tools/audit/seat/bus.sh` line 8 and lines 504-510 take `--past-three <reason>` as one argument;
  the tracked tool is not at fault.
- The wrapper is session-local: `s13/dispatch-seat/delta-retry.sh` (11 lines) passes `"$2"` into a
  second session script, `s12/seat-dispatch/d2-sonnet-delta.sh`, which re-splits it. One instance
  (#3291's fourth round), worked around with a hyphenated token at no measured latency.

Cost: moving it into `tools/` means a new file, a self-test and a closure classification
(`tests/entities.py`), for one instance with a free workaround.

Binding: the cost of a new tracked instrument against one zero-latency instance. Fixing the quoting
inside the session script is the dispatch seat's local edit and needs no ruling.

## P443: CODEQL-PY-CAP, the python CodeQL job cancelled at its 45-minute cap

Verdict: ACCEPT, already in flight; no new op.

Source: queue line 135 (2026-11-08T18:00Z).

Instances: three cancels on 11-08 (#3291 run 42461842836, #3315 job 128801304405, main `cb551274`
job 128798570690). R10-HOTFIX-CODEQL-HEADROOM (in-progress, PR 3266) was re-scoped by the
orchestrator under the mandate on 11-08 to exactly this: raise the python job's `timeout-minutes` in
`.github/workflows/codeql.yml` from the measured distribution (p50 41.4 min, p90 44.4 min, 3 of 21
main runs at the cap, quoted from its brief at the roster tip).

Cost: nil beyond that group.

Binding: R10-HOTFIX-CODEQL-HEADROOM is the countermeasure. The root-cause seat the line asks for is
the orchestrator's dispatch under `root-cause.md`, not a triage op; the group's recut measurement
(runner-speed variance, no file growth) is its cause evidence.

## P444: TRAIN-UNDRAFT-GAP, the train skipped UNDRAFT for #3318

Verdict: ACCEPT, as a repair, classified medium (a critical-path entry skipped after 8 refusals). It
skips the bar.

Source: queue line 134 (2026-11-08T15:10Z).

Instances:
- `tools/audit/seat/merge_train.py` `undraft()` (lines 1275-1282) returns at once unless
  `item.get("draft")`, which `add` sets only for a head that is a draft at admission. A head drafted
  after its admission (a recarry or an update that re-drafts it) is never undrafted, and the merge
  then fails "Pull Request is still a draft". That is the narrowing P218 asked for, and it is the
  likely gap: #3294 was a draft at add, #3318 and #3315 were not.
- Instances: #3318 (`SKIP #3318 04f46900` in `<state>/merge_train/train.log`), #3315 (readied by hand).

Cost: one re-read of `isDraft` at the recarry and update paths that rewrite the entry, and one arm.

Binding: carry on R10-TRAIN-MERGE-LOOP-2 (carries-open, owns `merge_train.py`; it holds the P218
undraft carry). The fixer first confirms the admission path of #3318 from the train log. Then a head
the train itself or its update path left drafted is recorded `draft: true`, and an author's draft
after admission is still left alone (P218's guard). Failing test first: the #3318 shape. Null
control: a head drafted by its author after admission is not undrafted. A mutant dropping the new
record fails the first arm.

## P445: CI-ATTEMPT-ALARM, a CI run past attempt 20 goes unseen

Verdict: ACCEPT the alarm, as the root-cause countermeasure B of R10-RCA-SWEEP-SETTLE-LOOP. DEFER the
`fixer.md` rule.

Source: queue line 132 (2026-11-08T12:28:01Z).

Instances (from the RCA, quoted by the queue line): 1089 bot re-attempts on 11-08 before #3287;
0 flags in the 21.2 h before #3287 and 32 after; detection about 16 h today, about 1 h with the row.
`tools/audit/seat/beat_jobs.py` reads no run attempt at origin/main (`grep -n attempt` finds only
roster-queue attempt lines, 371 and 378).

Cost: one API call of 2.84 s per 1800 s pass (the RCA's figure), a row and its self-test arm in
`beat_jobs.py`; no new file.

Binding:
- **The alarm, carry on R10-TICK-LEVELS** (the group that owns the levels the orchestrator acts on;
  no live group owns `beat_jobs.py`). A `ci.yml` run at attempt 20 or more owes a line naming the run
  and its PR. Self-test: the #3287 window fires; a run at attempt 1 is silent (null control).
- **The `fixer.md` line, DEFER to R10-RCA-SWEEP-SETTLE-LOOP** (in-progress). It is policy, from one
  instance, and `node tools/policy/policy_lint.mjs --budgets` shows `dev/governance/roles/fixer.md`
  (listed under its retired brief name) at 314 of 315 lines and 5216 of 5216 tokens: a one-line rule needs a budget raise or a payment. It
  rides that RCA's own pull request to the owner or the mandate, or that RCA records a refusal; a
  second instance of a "cannot loop" claim failing would change this ruling.

## P446: RELAY-HANDOFF-STARVATION, returned handoffs wait 20 to 60 min for the relay

Verdict: ACCEPT, routed; no triage op.

Source: queue line 122 (2026-11-08T10:15Z).

Instances: #3299 `2eb13559`, #3308 `ac28d7e8`, #3310 `eda3592e`, with `tick-loop.log` showing
`relay=running` on every pass from 09:58Z. The line asks for a root-cause seat, and
R10-RCA-RELAY-HANDOFF-STARVATION is on the roster (in-progress).

Cost: nil beyond that group.

Binding: the RCA owns the cause, the process state, the cost test and the countermeasure or refusal.
P457 below defers to it.

## P447: TRAIN-PAUSE-DURING-STAMP, the train merges under a running stamp

Verdict: ACCEPT, as an owner directive (tvofi 2026-11-08: "The train should pause while a stamp is
running the next time"). It skips the bar.

Source: queue line 121 (s13 2026-11-08).

Instances: train 30368 merged #3309 at 08:12Z while the web stamp gated `73365699`, moving main to
`f9a96320` under it. `merge_train.py` has only the reverse hold, `HOLD_REF = "refs/heads/train-hold"`
(line 817), which makes the record beat wait on the train. No stamp-side hold exists:
`git grep -n -i 'stamp.hold' origin/main -- tools` is empty.

Cost: a hold ref taken and released by `tools/release/stamp.py` and `.claude/workflows/web-stamp.js`,
honoured by `merge_train.py` `batch` and `add` before any merge, with a dead-holder takeover, and one
self-test arm. No new file.

Binding: carry on R10-TRAIN-MERGE-LOOP-2 (owns `merge_train.py` and `train.sh`; the hold is
honoured there, and the stamp side is the hold's other end). Failing test first: a merge attempt
while the stamp hold stands logs `STAMP-HOLD` and does not merge. Null control: no hold, the merge
runs as today. A dead holder's hold is taken over. A mutant dropping the check fails the first arm.

## P448: DESIGN-RECUT-UNREVIEWED, a re-cut design waited four days for a reviewer

Verdict: ACCEPT, as a low repair of the tick's design levels. It meets the bar.

Source: queue line 120 (s13 2026-11-08).

Instances: design/R10-ADVISOR-WHATIF was re-cut to `b50afa68` at 11-04 07:34Z after "Design review:
revise bf62c545"; no design reviewer was minted for four days. `orchestrator_tick.py` has two design
levels: `designs_owed` (no `design/<g>` ref at all, lines 1529-1556) and `design_builds` (an approve
at the tip, line 1581). Neither prints a design tip newer than its last non-approve verdict.

Cost: one more branch in the existing `design_builds` read, which already lists both ref families.

Binding: carry on R10-TICK-LEVELS. A `design/<g>` tip with no verdict, or whose verdict names an older
sha, prints `DESIGN-REVIEW OWED: <g> <tip> <age>`. Failing test first: the ADVISOR-WHATIF shape. Null
control: an approve at the tip prints DESIGN-BUILD as today, not the new line.

## P449: GH-BUCKET-UNATTRIBUTED, the REST quota spent with no attributed caller

Verdict: ACCEPT, as a low repair of the gh shim. It meets the bar.

Source: queue line 119 (s13 2026-11-08).

Instances: the core bucket hit 0 of 5000 at about 07:40Z and refused the v7.1.6 stamp's gate read,
while `gh_calls.py --top --since <1h>` printed 0 calls. The daemons resolve `/opt/homebrew/bin/gh`
and no `gh-calls.log` exists (the line's 08:04Z read). At origin/main the shim's comment guard admits
only the `gh_comment.py` path baked at install (`tools/audit/seat/gh_calls.py` line 161), so a global
install would refuse a `#201` post from another checkout.

Cost: the guard admits a `tools/pr/gh_comment.py` under any registered seat root, by real path; the
install reaches every daemon's PATH. No new file.

Binding: carry on R10-FLY-GH-READ-RETRY (carries-open; the live group on the gh call layer; R10-FLY-
GH-CALL-LOG, which built the shim, is done). Failing test first: a post from a second registered
tree's `gh_comment.py` reaches the real gh. Null controls: the existing spoof arms (lines 474-483)
still refuse. The owner's 2026-11-08 order that seats must not hammer the API is the benefit: today
no instrument can name the caller.

## P450: LEDGER-CLOSE-WRONG-SHA, a close at a non-open sha is a silent no-op

Verdict: ACCEPT, as a low repair. It meets the bar.

Source: queue line 118 (s13 2026-11-08).

Instances: a train-stop opened at #3232 `bba5b4d4` (2026-11-06T22:44Z) was closed at `28e43754`, so
the open event stood until 11-08 and refused `merge_train.py sweep --stamp` with `SWEEP HELD for
#3232` (`<state>/events.tsv`, the open and close lines). One instance; it held a stamp.

Cost: a refusal in `tools/audit/seat/ledger.py`'s `close` (rc 1 naming the open sha) and a fold arm
that closes a train-stop whose PR merged. No new file.

Binding: carry on R10-TICK-LEVELS (owns `tools/audit/seat/ledger.py`). Failing test first: a close at
a sha matching no open event refuses and names the open one. Null control: a close at the open sha
closes as today.

## P451: PREFLIGHT-POLICY-ORDER, pre-flight parks every policy head under a mandate

Verdict: ACCEPT, as a major defect (the line's rating; the train never posts the citing approval).
It skips the bar.

Source: queue line 117 (s13 2026-11-08).

Instances: train 30368 `train.log` line 15241, `PARK #3262` with the mandate on the launch line.
`merge_train.py` runs `policy_approve` then `policy_gate` at the merge (lines 2511-2512, 3062-3063),
while `--pre-flight` reads `queue_pre_flight.PreFlight` (line 2806) before either. Workaround in use:
`--no-pre-flight` for the policy entry.

Cost: the pre-flight treats a live mandate with no owner approval yet as cured, as it treats a bot
tip (`bot_cured=True`, line 2806), or runs `policy_approve` first; one mutant-pinned arm.

Binding: carry on R10-RAISE-GATE-SHIM (carries-open, owns `merge_train.py` and
`budget_raise_gate.py`; its seam is the mandate-cured approval the same pre-flight reads for a budget
raise, line 2052). Failing test first: a policy head under a live mandate passes pre-flight. Null
control: with no mandate it still parks. Mutant: restoring the order fails the first arm.

## P452: POSTMERGE-ROSTER-RC3, postmerge's roster step hides the refusal

Verdict: ACCEPT the residue, as a low repair. It meets the bar.

Source: queue line 115 (2026-11-08T06:35Z); five instances, #3268, #3269, #3275, #3274, #3295.

Instances: half is already built. `39a735d8f8` (2026-11-08T07:18Z, "queue and postmerge print the
lint refusal's ERROR lines (P435)") added `refusal_detail` to `tools/audit/seat/postmerge.py` (lines
53-60), which leads with lint ERROR lines. The issue-ownership HELD guard (#3295, `roster_sync.py`
line 671) is not a lint ERROR, so it still ends in "rc 3 ... nothing pushed" with the cause unnamed.

Cost: `roster_sync.py` returns HELD as its own rc and `refusal_detail` includes a HELD line; two arms.

Binding: carry on R10-ROSTER-READ-SWEEP (carries-open, owns `roster_sync.py`). Failing test first:
the #3295 HELD shape prints the HELD line and its own rc. Null control: a lint refusal prints as
`39a735d8f8` made it.

## P453: GC-LIVE-TRAIN-CHECKOUT, worktree_gc collects a checkout a live run uses

Verdict: ACCEPT, as a major defect and an audit class (five instances). It skips the bar.

Source: queue lines 109, 114 and 116 (2026-11-08T04:00Z, 05:12Z, 07:02Z).

Instances:
- The dispatch tools-wt, relay-tools (twice) and merge-s13-3290 (twice: train 15780 at 03:55Z and
  train 95155 at 06:59Z).
- `tools/audit/worktree_gc.sh` keeps a worktree only when a process's cwd is inside it (line 33,
  `cwd-inside`, extended to every arm by `7fc93c4bdd`, 11-08 07:21Z). A run that reaches a checkout
  by `git -C`, `--checkout` or a script path is not seen.
- The fifth instance's premise is false: `--keep-dir` is not a keep list. It is the destination
  evidence directories are moved into (lines 80-82: "moved into --keep-dir (default $HPO_STATE_DIR/ev...)").
  Passing a tools checkout there protects nothing. That is a misuse, not a failed arm.

Cost: a live-user test in each removal arm (a worktree named in a live process's argv or in its open
files, by `lsof +D`, or by a live `train.pid` or lock file) and fixture arms. No new file.

Binding: carry on R10-CLOSEOUT-INSTRUMENTS (carries-open, owns `worktree_gc.sh`).
- Failing test first: a detached clean worktree at origin/main, used by a live process through
  `git -C` with its cwd elsewhere, survives every arm. Null control: the same worktree with no live
  user is collected.
- A flag that does protect a path, if one is wanted, gets its own name; `--keep-dir`'s usage line
  says it is the evidence destination.
- The audit-class root-cause seat is the orchestrator's dispatch (`root-cause.md`), not a triage op.

## P454: PREPR-SLOT-LIVELOCK, a nested self-test prepr waits on a slot its caller holds

Verdict: ACCEPT, as a major defect (it stalled the critical path 11+ min). It skips the bar.

Source: queue line 112 (2026-11-08T04:45Z); the second instance after 2026-10-27.

Instances: at 04:44Z four outer preprs held the four heavy slots, each waiting on a nested run. The
proposed fix already exists in name: `tests/gate_lock.py` defines `SLOT_LABEL_ENV = "HPO_SLOT_LABEL"`
(line 112), and `tools/pr/prepr.sh` exports it so a nested heavy step joins its caller's slot (lines
4170-4176, pinned by self-test lines 3578-3579). The livelock means step 3h's nested run did not
inherit it on 11-08; where it is lost is not established here (the self-test's own arms at lines
3629-3644 set and unset the label on purpose, so they are not themselves the cause).

Cost: find where the step-3h nested run loses the label (a cleared environment or a planted HOME)
and keep it; one arm. No new file and no new environment marker.

Binding: carry on R10-PREPR-CAP (carries-open, owns `prepr.sh` and `gate_lock.py`). Failing test
first: an outer prepr holding a slot runs its `--self-test` nested prepr with every slot taken and
completes. Null control: a bare nested run with no label still takes a slot. The proposed new
`HPO_GATE_SLOT_HELD` marker is REJECTED: it would duplicate `HPO_SLOT_LABEL`.

## P455: RED-UNOWNED-OVERFIRES, a deferral red raises RED-UNOWNED

Verdict: ACCEPT, as a low repair. It meets the bar.

Source: queue line 111 (2026-11-08T04:25Z).

Instances: four false fires in 30 min (#3274 `178dc0fe`, #3299 `f00e035b` at 03:56Z; #3296 `9697c17c`,
#3264 `730ef3ef` at 04:23Z), each on a head `merge_train.py classify` read as WAIT.
`orchestrator_tick.py` line 960 returns `red-unowned` from `self._red`, the gate check-run
conclusion, not classify. About 2 min of orchestrator re-classification per false fire.

Cost: the predicate reads `classify` (RED, rc 1, only), as P436's barrier requires of every gate
reader; one arm.

Binding: carry on R10-TICK-LEVELS. This is one instance of P436's barrier (every reader of the
`gate` conclusion goes through classify), so the fixer cites that carry on
R10-HOTFIX-TRAIN-DEFER-WAIT and reuses its predicate. Failing test first: a deferral red with a busy
run prints no RED-UNOWNED. Null control: a real red still prints it.

## P456: OWED-UNACTIONED-CAP-LINE, an informational cap line blinds the owed check

Verdict: ACCEPT, as a major defect (the line's 05:08Z re-rating: about 4 h of three BLOCKED-UNFIXED
levels and 8 h of opener refusals unseen). It skips the bar.

Source: queue lines 110 and 113 (2026-11-08T04:15Z, 05:08Z).

Instances: `orchestrator_tick.py` lines 2344-2346 print "OWED handoffs capped at N of M; the rest
print next pass" inside the OWED family. `tools/audit/seat/owed_unactioned.py` line 111 raises
`Unreadable` on an owed line naming no topic or PR, and line 167 then prints UNREADABLE for the whole
check, masking every readable key.

Cost: two changes, one arm each: the cap notice prints outside the OWED prefix, and an UNREADABLE
line still lists every key it could read.

Binding: carry on R10-TICK-LEVELS (owns both files). Failing test first: a board with the cap line
and one real unactioned key prints that key. Null control: a board with only the cap line prints no
key and is not UNREADABLE.

## P457: RELAY-SERIAL-UPDATES, the relay applies one update at a time

Verdict: DEFER to R10-RCA-RELAY-HANDOFF-STARVATION.

Source: queue line 108 (2026-11-08T03:27Z).

Instances: #3300's update about 26 min and #3301's at least 17 min, with five handed-off PRs queued
behind them; reviewer dispatch delayed up to about 2 h. The line itself owes the measure (per-update
wall time over the last 20 relay updates, queue wait per PR, heavy-slot contention), and it was not
taken.

Cost: N relay-tools trees and a lock change in `cloud_relay.sh`, unmeasured.

Binding: the same mechanism (the serial handoff arm) is P446's RCA. What would change it: that RCA's
cost test choosing a parallel arm, with the measure above.

## P458: CARRY-CONTEXT-ONLY, a context-only diff change forces a fresh review

Verdict: REJECT.

Source: queue line 106 (2026-11-08T02:55Z).

Instances: `<state>/merge_train/train.log` holds 281 `recarry: main merged` lines and 11 "the
branch's own diff differs" refusals over 5 PRs (#3014, #3022, #3147, #3296, #3315; `grep 'own diff
differs' train.log | grep -o '#[0-9]*' | sort -u`). Even if every one was context-only, that is at
most 5 of 281 recarries (1.8 %).

Cost: relaxing `tools/audit/seat/review_carry.py` (Lever L6, "the PR's patch is the one reviewed")
to ignore context lines, with the risk the line names: a context change that alters the meaning of
an unchanged hunk.

Binding: an upper bound of 1.8 % of recarries, about one 30-60 min delta round each, is far below the
20 % bar, against a weakened review-integrity lever.
