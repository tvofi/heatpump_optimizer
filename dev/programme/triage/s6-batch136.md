# Proposal triage, session s13, batch 136 (P425 to P436)

These rulings apply the owner's two rulings of 2026-11-08 (tvofi, about 01:40Z and 02:00Z). A new
proposal is accepted only on a measured improvement of more than 20 %. An already planned
instrument or machinery group is kept only on a measured improvement of at least 10 %. The measures
are CI time, programme completion time, right-first-time and token usage. A minor or low
instrument or machinery defect takes the bar. Major and critical defects, the countermeasures
policy requires, closeout and owner directives keep their route. An unmeasured proposal is DEFER;
an unmeasured keep test is DROP. These rulings outrank the >10 % in `proposal-triage.md` until
R10-FLY-TRIAGE-BAR merges.

Sources read:
- origin/main `48af0864a`.
- The roster branch `origin/handoff/audit-r10-roster` at `439aebb50`.
- The session's local logs, named per entry: `s12/ci-tput/` (a 47.9 h CI study, 2026-11-05T13:26Z
  to 11-07T13:26Z), `s12/filecap/evidence.txt`, `s13/lane-study/runs/` (replan base, 2026-11-08,
  wall 170.42 h) and `s7/roster-queue-s7.txt`.
- The API last: CI run lists and run attempts, cited where used.

Denominators used throughout:
- **CI time:** 29876 runner-min/day (`s12/ci-tput/waste.txt`, first line: 59594 runner-min over
  47.9 h).
- **Programme completion:** the replan base wall of 170.42 h (`s13/lane-study/runs/base1.json`
  `summary.wall_hours`; closure 2026-11-15T03:55Z). The critical path is HANDOFF-PATH, ARCH-DOCS,
  CLOSEOUT-CLEANUP and CATALOG-PR.
- **Right-first-time:** 55 PRs had a `ci.yml` run from 2026-11-07T00:02Z to 11-08T01:59Z (`gh run
  list --workflow ci.yml --created '>=2026-11-07T00:00:00Z' --limit 1000`, 540 runs, `pr=<n>` from
  the titles).

## P425: keep test, R10-CI-EDIT-RUNNER (PR 3303)

Verdict: DROP. The measured CI-time benefit is at most 2.8 %, against the 10 % bar. Programme
completion, right-first-time and tokens are unmeasured, so they count for nothing.

Source: queue line KEEP-TEST-20261108, set (A); orchestrator priority request, 2026-11-08.

Instances:
- **The PR's own figures.** These come from #3303's body, which ran
  `dev/audit/harnesses/r10_ci_slim/body_defer.py` over 2026-11-05T13:26Z to 11-07T22:00Z (56.6 h).
  - Edit job-minutes went 3524 -> 2187 and review job-minutes 889 -> 263, which is 1963 min gross.
  - The code-gate wait added 625 min, so the net saving is 1338 min.
  - The window's runner time is 29876 x 56.6 / 24 = about 70,400 min.
  - So the saving is 1.9 % net, and 2.8 % even if the added gate wait is never subtracted.
- **The regime main is in now.** Since 2026-11-07T05:00Z (C3, #3276, on main) the same command
  with `--since` reports:
  - Edit runs: 358 -> 426 job-min, 68 more.
  - Review runs: 180 -> 57, 123 fewer.
  - Net 55 min over about 10.2 h, about 12,700 runner-min: 0.4 %.
  - The body itself records that carry 0's premise no longer holds: the edit prelude median is now
    0.48 min, against the carry's 37.2.
- **An independent upper bound, before C3.** `s12/ci-tput/analysis.txt` gives prelude waits beyond
  one minute of 2030 min (edit) and 582 min (review) in 47.9 h, against 59594 total: 4.4 %.
- **Programme completion.** The group is not on the critical path (`s13/lane-study/runs/instr_table.txt`:
  the CP column is empty, and its only dependants are ARCH-DOCS and ROUND-PLAYBOOK-FINAL through
  their after-lists).
- **Right-first-time.** Not shown. The body does not claim to close the deferral class P436 rules
  on, and its code gate "defers to that re-run at once; the sweep re-judges it", which leans on the
  same sweep.

Cost: the merge (a MODE: FULL gate on code-owned `.github/workflows/ci.yml`), an `actions: write`
grant on the `gate` job, and +382/-54 lines (gate.py +145). The body records that mutants M5-M8
were not re-taken at the head.

Binding:
- The bar, at every reading of the figures.
- The severity reads `high`, but this is not a defect repair: #3105 is a tracking issue, and both
  carries are owner-approved throughput builds (plan-regain card 9 and lever 5). The owner named
  the group in the keep-test set, so no directive exemption is claimed (orchestrator, 2026-11-08).
- #3105's disposition: half 2 (the tests/run.sh summary naming) was delivered by #3181
  (`c0b082bc4`, R10-CI-RUNNER-FIXES, done). Half 1 is refused here.
  - No other live group wires #3105.
  - R10-HOTFIX-GATE-BUSY-DEFER carries 6 and 8 (one item, written twice) name the same prelude
    runner-hold. These figures fail it too, so those two carries are dismissed by this ruling's
    measure.
- Ops (applied by the orchestrator, 2026-11-08): `set-stage R10-CI-EDIT-RUNNER refused` and a
  `set-resume` note. PR 3303 was closed unmerged.

## P426: keep test, R10-FLY-KEYED-MERGE-DRIVERS

Verdict: DROP. The conflict class it removes has almost stopped, and its upper-bound benefit is
under 1 % on every measure.

Source: KEEP-TEST-20261108 (A); its brief cites P412, which states "savings estimate 8 to 20 h" and
leaves the measurement to the group.

Instances:
- **The rounds.** `s12/filecap/evidence.txt` scanned 828 merges from 2026-10-15T12:25Z to
  11-07T13:55Z.
  - It found 147 conflicting merge-forward rounds. The two files this driver keys touch 23 of them:
    the roster JSON 15 and INSTRUMENTS.md 8.
  - By date (`grep` of the round lines for those two files, `cut -c1-10 | uniq -c`), 22 of the 23
    fall on 10-16 to 10-31 and one on 11-04. None has fallen since the roster moved to its own
    branch, past that single 11-04 round.
- **The forward rate.** One round in the last seven days. The plan's remaining 170.42 h, about 7
  days, projects about one round.
- **CI time.** One round re-runs one code run, at 48 min average (`s12/ci-tput/analysis.txt`:
  "invalidated: main merged into head", 8736 runner-min over 181 runs). That is under 0.1 % of
  CI time.
- **Programme completion.** Off the critical path, with 0 dependants
  (`s13/lane-study/runs/instr_table.txt`).
- **Right-first-time.** At most 23 of 428 work PRs over 23 days, 5.4 %, and about 0 % at the
  current rate.
- P412's 8-20 h is summed PR lag, not completion time. Its own lag figures (median 1.4 h) would
  give about 1.4 h of lag over the remaining programme.

Cost: an S group of 1032 priced minutes (`base1.json`), a new merge driver and `.gitattributes`
wiring.

Binding: the bar. Op: `set-stage R10-FLY-KEYED-MERGE-DRIVERS refused`.

## P427: keep test, R10-FLY-DISPATCH-RULINGS

Verdict: KEEP, narrowed to carry 0, which is an owner directive. The `--preamble` flag is DROPPED:
its benefit is unmeasured.

Source: KEEP-TEST-20261108 (A); the group was created by P419 (batch 134).

Instances:
- **Carry 0** is the owner's ruling of 2026-11-07, quoted in the carry: "Having the fixers merge
  main and re-run prepr after each main head move seems extremely wasteful, as the train can
  handle that." The reviewer side is the same ruling. A directive keeps its route without the bar.
  - The carry measures one instance: four `prepr.sh` runs of about 12 min each on f-3262-r6, three
    of them caused by main moving.
  - The change is in the fixed role text `cloud_dispatch.py` renders, and it needs no preamble
    mechanism.
- **The preamble** (P419) counts three instances: f-nonreq-reds, p-3290-r3 and the
  CI-SELFTEST-SCOPE mint. No figure on the four measures was taken.
  - The rulings it would carry reach seats today through the session wrapper.
  - The one ruling that cost measured time, carry 0, is fixed in the rendered text itself.

Cost of the narrowed group: carry 0 alone. That is the fixer and reviewer prompt text in
`tools/audit/seat/cloud_dispatch.py`, plus `dev/governance/roles/fix-review.md` (code-owned;
policy, so it merges on the owner's approving review or under a mandate in force).

Binding:
- The owner-directive route for carry 0, and the bar for the rest.
- Op: `edit-brief R10-FLY-DISPATCH-RULINGS` to a brief that builds carry 0 only. The `--preamble`
  flag and its self-test arms go out. The text may keep the existing `triage:` citation to
  batch 134 P419 (an ACCEPT); it must not cite this entry, because a KEEP does not pass the
  roster's triage gate.

## P428: keep test, R10-CI-PRIORITY-PAUSE

Verdict: DROP. The queue time it could reclaim is 2.7 % of main CI wall time, and it is not
measured on anything else.

Source: KEEP-TEST-20261108 (A); the group holds P267 and P268 (owner-directed, 2026-10-28).

Instances:
- **Main CI.** Over the 60 `push` runs of `ci.yml` in `s12/ci-tput/jobs/`, the queue time of each
  run's longest job is 71.2 min against 2637 min of run wall time: 2.7 %. The median is 0.05 min
  and the maximum 20.7 min.
  - Rule: per run, the job with the largest created-to-completed span; queue is created_at to
    started_at. Instrument: a one-off over `s12/ci-tput/jobs/*.json` and `allruns.json`.
  - That is the most a pause could return to main's critical wait, before the re-run cost of the
    cancelled victims is netted off.
- **Account saturation** (`s12/ci-tput/EVIDENCE.txt`): 38 to 40 concurrent jobs 11.2 % of the time.
  The median job queue is 0.1 min; 855 of 11548 jobs queued more than 5 min.
- **Programme completion.** Not on the critical path (`instr_table.txt`).
- **Right-first-time and tokens.** Not affected.

Cost: an M group of 1253 priced minutes. It adds a cancel and re-run of victim PRs' CI, which
spends CI time, and a new config file plus four roster fields.

Binding:
- The bar. The owner-directed origin is not an exemption here, for the reason in P425: the owner's
  keep-test set names the unmeasured planned groups, and this is one.
- #3104 is wired to this group. Its per-group `source` field is partly covered by R10-OUTSIDE-FIRST
  (P420, in progress), which adds that field. No live group builds the pause.
- Ops: `set-stage R10-CI-PRIORITY-PAUSE refused`, and #3104 is closed as refused, citing this
  batch.

## P429: keep test, R10-POLICY-ROLE-PACK (carries 4 and 5)

Verdict: KEEP carry 4, an owner directive. DROP carry 5, which misses the bar.

Source: KEEP-TEST-20261108 (A). The group's main build is merged: PR 3256 at `41aa9050f`, with
carries 0 to 3 marked implemented. Carries 4 and 5 are open.

Instances:
- **Carry 4** is the owner's directive of 2026-11-06, P398: "have the seats use subagents as
  required". It keeps its route. `git show origin/main:tools/audit/seat/cloud_dispatch.py | grep -c
  'frugal routing guard'` gives 0, so it is not built.
- **Carry 5** is P399, a RemoteTrigger PreToolUse hook. P399 measured 7 sourceless fires among the
  342 `FIRED` lines since 2026-10-31, 2.0 % of fires, costing 342.7 seat-min in one incident.
  - On right-first-time that is 2.0 %, under 10 %.
  - The defect is minor: a re-fire recovers it, nothing merged wrong, and nothing blocked the
    train. So it takes the bar.
  - The remedy exists without a hook: fire the `PAYLOAD.json` that `cloud_dispatch.py` already
    publishes.

Cost of carry 5: a hook script and a code-owned `.claude/settings.json` matcher.

Binding:
- The bar for carry 5, the directive route for carry 4.
- Op: `drop-carry R10-POLICY-ROLE-PACK 5`. The group stays carries-open on carry 4.

## P430: keep test, R10-PLANTED-DEFECT-AUDIT (carries 3 to 5)

Verdict: DROP the three open carries. The group's build is merged: PR 3240 at `a2240924b`, an
ancestor of origin/main, with carries 0 to 2 marked implemented.

Source: KEEP-TEST-20261108 (B); severity `low`, so minor.

Instances:
- **Carries 3 to 5** are round-2 review residue on a dispatch helper that blocks nothing (the
  guardrail "sets no exit code").
  - Carry 3: an unpinned `insufficient` re-dispatch branch.
  - Carry 4: a duplicate `MUTANTS` key.
  - Carry 5: `digest.txt` keeps DISPATCH lines, growing by one line per episode, 3 in 5.4 days
    (carry 5's own figure).
- **The four measures.** None moves measurably.
  - CI time: none.
  - Completion: off the critical path.
  - Right-first-time: no PR was refused on it.
  - Tokens: three digest lines in 5.4 days.

Cost: an S part of 1188 priced minutes (`base1.json`).

Binding:
- The bar.
- Ops: `mark-carry R10-PLANTED-DEFECT-AUDIT 3`, `4` and `5`, each `dismissed` with the reason
  "keep test failed, owner bar 2026-11-08; triage batch 136 entry 430". Then `set-stage
  R10-PLANTED-DEFECT-AUDIT done --at-sha a2240924bdbcb582a5d77898268c6ab45baeca54`.
- #3126 closes as delivered by #3240, with its residue refused here.

## P431: keep test, R10-REPLAY-COST-2

Verdict: DROP. It is minor (severity `low`), and its one behavioural item affects 1.3 % of
replay draws.

Source: KEEP-TEST-20261108 (B).

Instances:
- **The behavioural carries, 0 and 6** (one item, written twice): one clean draw refused out of the
  78 synthetic-clean replay jobs that carry 1 re-derived. That is 1.3 % of replay draws, and a
  smaller share of PR heads. One job: 127310664875.
- **The rest, carries 1 to 5 and 7 to 12**, are body figures, docstrings, a stale comment and
  three surviving mutants of an earlier head. None moves a measure.
- **Programme completion.** Off the critical path, with 1771 priced minutes (`base1.json`).

Cost: an M group.

Binding:
- The bar.
- Op: `set-stage R10-REPLAY-COST-2 refused`. It has no wired issue.

## P432: R10-REPLAY-COST-BUDGET, "already set done 2407ff613": not confirmed

Verdict: not done. A record repair is owed, and this is not a keep test.

Source: KEEP-TEST-20261108 (B), "confirm".

Instances:
- **What `2407ff613` changed.** `git show 2407ff613` (roster branch, 2026-11-07T22:05:47Z) changes
  only `resume.commit`, from `62f94f3fb...` to `80016a71`. The stage stays `carries-open`, because
  the closing rule finds a pending carry: carry 3, the runner-class bands, is unmarked at
  `439aebb50`.
- **Carry 3 is built.** Carry 4 is already dismissed as "duplicate of carry 3, implemented by PR
  3234 80016a71". `80016a71f` (Merge pull request #3234) is an ancestor of origin/main.
- **Every other carry is marked.** Carries 0 to 2 read `[implemented: 62f94f3fb...]`.

Binding:
- Ops: `mark-carry R10-REPLAY-COST-BUDGET 3 implemented 80016a71f`, then `set-stage
  R10-REPLAY-COST-BUDGET done --at-sha 80016a71f`.
- This frees the 1188 priced minutes it still holds in the plan (`base1.json`).

## P433: keep test, R10-HOTFIX-SELFTEST-TIMEOUT: classified major, KEEP, and its fix is landed

Verdict: KEEP. Classified major: it timed out a gate-covered job on main and stalled the train.
It also passes the bar on CI time alone.

Source: KEEP-TEST-20261108 (C), unclassified.

Instances:
- **Classification.** The brief records two of six main runs cancelled at the 30-minute job
  timeout (42280756390 and 42307872956), each stalling the train by one main-CI wait. That is a red
  on main on a job the required `gate` covers: the owner's main-red-required case. So the defect
  is major.
- **CI time.** The class "self-test 30-min timeout (run gave no verdict)" is 6535 runner-min,
  11.0 % of all runner time (`s12/ci-tput/waste.txt`). That is at least 10 %, so the group would
  pass the keep bar even if minor.
- **The fix is merged.** #3275 merged at `17e115792` (2026-11-07T23:39Z).
  - Main's `governance / instrument-self-tests` then took 10m48s at `17e115792` (run 42426208362,
    23:39:43Z to 23:50:31Z) and 10m09s at `e36e5327d` (run 42433442429), against 28m39s to 29m45s
    before (the brief's four runs).
  - Rule: `gh api actions/runs/<id>/jobs?filter=latest`, completed_at minus started_at.
- **A separate finding.** At `e36e5327d` that job concluded `failure` in the step "Show the pre-PR
  self-check refusing its own fixtures" (same call). That is a main red, not a timeout, and
  belongs to whatever owns that step. It is reported to the orchestrator here, not ruled.

Binding:
- Ops: `mark-carry R10-HOTFIX-SELFTEST-TIMEOUT 0 implemented 17e115792` (carry 0 is an evidence
  instance that the fix covers), then `set-stage R10-HOTFIX-SELFTEST-TIMEOUT done --at-sha
  17e115792`. Also set the roster `severity` to `high` when a field op exists. The op set has none
  today, so a `set-resume` note records "classified major, triage batch 136 entry 433".

## P434: the severity mapping in the keep-test line

Verdict: ACCEPT the mapping for defect groups, with one amendment.

Source: KEEP-TEST-20261108, which reads `low` = minor, `medium` and `high` = major or critical,
and `normal` = the rca, closeout and directive kinds.

Binding:
- **The amendment.** Roster severity skips the bar only where the group repairs a defect: a wrong
  behaviour that was observed. On a throughput or feature build, `high` is a priority tag and
  exempts nothing.
  - This is why P425 (`high`), P427's preamble (`high`) and P428 (`high`) take the bar.
  - It is also why P435 and P436 keep their route: both are defects, classified on the evidence.
- **An unclassified group is classified first,** never assumed major (P433).
- There is no op. The mapping binds this seat's later keep tests.

## P435: ROSTER-GATE-LINEPIN, a pre-existing line shift blocks every roster write

Verdict: ACCEPT changed, as a defect. The class-eliminating form: the roster write gate refuses
only the lint errors the write adds, and prints the refusal's detail. Auto re-pinning and
anchor-only citations are REJECTED.

Source: queue line ROSTER-GATE-LINEPIN (main s13, 2026-11-07T23:58:01Z).

Instances:
- **The 11-07 stall, from the roster branch.** `git log 439aebb50 --since=2026-11-07T20:00Z --
  dev/programme/rosters/wave-r10-groups.json` shows:
  - The last write before the gap: `95ca69ef0` at 22:29:03Z.
  - The next: `0d142795c` at 23:54:58Z, `edit-brief R10-HOTFIX-COP-UNMEASURED`, the re-pin that
    cleared it.
  - Every roster writer was blocked for 1 h 26 min. The queue line's "00:5xZ" is the commit's
    local +01:00 time.
- **The class recurs.** P313 (batch 76) ruled the line-shift class DEFER on one confirmed
  instance (#3011) and one mention (r10-roster-lint). It named "a third line-shift block" as what
  would change the answer. This is the third, on a wider surface: every roster write, not one
  review. Three instances in round 10 make it an audit class, which owes a class-eliminating
  barrier (`defect-root-cause.md`).
- **Classification: major.** It stalls every roster-dependent dispatch and postmerge stage,
  matching P409's hotfix tier for the same impact. So it keeps its route without the bar.
- **The mechanism.** `roster_edit.py` `write_roster` (origin/main) runs `lint_gate` over the
  whole roster, against a fresh origin/main checkout. So any merge that shifts a file a not-done
  brief cites by `path:line` makes every later write fail rc=3. Most writes do not touch that
  brief. `s7/roster-queue-s7.txt` holds 17 rc=3 notes, and none prints the lint detail.

Cost: about 30 lines in `roster_edit.py`, with one extra lint run on the base, about 73 s of one
core (P313's figure) per write that already lints. Alternatively, cache the base's error set per
origin/main sha.

Binding:
- **The destination.** A carry on R10-ROSTER-WRITE-SWEEP (carries-open, PR 3253), which owns
  `roster_edit.py` and `roster_queue.py`:
  - The lint gate refuses only the errors whose (path, citation) key is absent at the write's
    base. It still prints every pre-existing error as a warning naming its group, so the owner
    re-pins it.
  - `roster_queue.py` and the postmerge wrapper print the rc=3 detail lines, not only the total.
- **The controls.**
  - Failing test first: a roster whose not-done brief cites a shifted line admits an unrelated
    `set-resume`.
  - The same write that adds a bad citation is refused.
  - Null control: a clean roster writes as today.
  - A mutant that compares against an empty base set is killed.
- **REJECTED.** Auto re-pin is a writer silently rewriting citations it did not author.
  Anchor-only citations change `brief-citations.md` and lose the precision `brief_lint.mjs`
  enforces.
- **The two old refusals.**
  - Line 2338 (append-group R10-SAV-METER-FLOOR): dismiss. The group is on the roster at
    `439aebb50`.
  - Line 810 (edit-brief R10-FLY-STANDING-CONTRACTS): dismiss as superseded. The live brief
    (4104 chars) begins with the same text and was edited after the refused 10-31 copy (3933
    chars).
- The carry text cites `triage: dev/programme/triage/s6-batch136.md#P435`.

## P436: GATE-DEFERRAL-NO-RECHECK, a deferral red read as final

Verdict: ACCEPT changed, as a defect with a root-cause addendum and a barrier owed. The premise
"nothing re-runs it" is refuted for every instance checked: the gate sweep re-runs the deferring
gate. The cost is the window before that re-run, in which consumers read the at-once deferral red
as final. Option (a), a new re-dispatch, is REJECTED: the sweep already is one. Option (b) is
accepted, narrowed and bounded.

Source: queue line GATE-DEFERRAL-NO-RECHECK (main s13, 2026-11-08T00:44:23Z), plus the
orchestrator's 02:0xZ addendum: #3264 review run 42436586762.

Instances:
- **Who re-ran the deferring run.** `gh api actions/runs/<id>/attempts/2`, `triggering_actor` and
  `run_started_at`, against each code run's `updatedAt`:
  - #3302: edit run 42430821615. Re-run by `github-actions[bot]` at 01:15:13Z, 14 s after code run
    42430821315 concluded at 01:14:59Z.
  - #3304: edit run 42427026851. Re-run by `github-actions[bot]` at 00:26:34Z, 14 s after code run
    42427026761 concluded at 00:26:20Z.
  - #3291: edit run 42429084435. Re-run by `github-actions[bot]` at 00:59:37Z.
  - #3264, the review case: run 42436586762's gate failed at 02:01:18Z, deferring to edit run
    42433523102, which concluded at 02:01:52Z. It was re-run by `tvofi` at 02:02:10Z, 18 s later,
    and attempt 2 concluded `success` at 02:02:51Z. Sweep run 42436762727 started at 02:01:54Z.
  - #3274: code run 42434593342 had not concluded at the read.
  - #3262 and the earlier #3264 heads were not re-read.
  - The bot is the gate sweep (`gate-sweep.yml`, `workflow_run` on CI completion; `tools/ci/sweep.py`).
- **Where the cost lands.** In the window between the deferral red and the re-run, two consumers
  read the red as final:
  - The bus dispatch refuses the head.
  - The train's merge step parks it [BRANCH-POLICY]: #3264, about one train cycle.
  - `merge_train.py` `wait_ci` already reads a deferral as pending while `gate_busy` names a run,
    and waits `SWEEP_SETTLE_POLLS` after (R10-HOTFIX-TRAIN-DEFER-WAIT). The BRANCH-POLICY diagnosis
    ("PARKS the entry [BRANCH-POLICY] with that reason unless a required context is still
    pending") does not apply that reading.
  - The manual stopgap made it worse. `s13/edit_rerun.sh` re-runs by hand, and a re-run during the
    code run cancelled #3262's code run, which shares the concurrency group.
- **Frequency.** The queue line names 6 PRs (#3262, #3264, #3274, #3291, #3302, #3304). The
  orchestrator counts 7 with the #3264 review case, which falls on a head already named. Out of the
  55 PRs with CI in about 26 h, that is 10.9 % to 12.7 % not right-first-time on this machinery.
- **Recurrence after a countermeasure.** Five of the six named heads contain `5c1fa41fb`, #3287
  (`git merge-base --is-ancestor 5c1fa41fb pull/<n>/head`; #3291 does not). #3287 made every
  deferral publish at once. The class R10-RCA-GATE-BUSY-DEFER-2 analysed therefore has a new
  failure mode that its own countermeasure introduced.

Cost:
- One predicate reused by the train's BRANCH-POLICY diagnosis and the bus dispatch's head
  classification. The bus already calls `merge_train.py classify`, so it is one call path.
- A replay self-test over the instances above.
- No new workflow and no new runner.

Binding:
- **Classification.** A defect, and major: it refuses dispatch and merge per PR, on 10.9 % to
  12.7 % of PRs. Being an audit class (three or more in round 10), it also owes a class-eliminating
  barrier by `defect-root-cause.md`. Either way it keeps its route without the bar.
- **The root-cause seat is owed** (CLAUDE.md, recurring errors). It is not a new group: the class
  and its RCA document belong to R10-RCA-GATE-BUSY-DEFER-2 (carries-open, PR 3278). It gets a
  carry: this failure mode, with process state, cost test and countermeasure, stated as the side
  effect of #3287's at-once deferral.
- **The barrier,** as a carry on R10-HOTFIX-TRAIN-DEFER-WAIT (in progress, PR 3290; owns the
  train's deferral read):
  - Every reader of the required `gate` check's conclusion reads it through `classify` with
    `gate_busy` and the sweep settle. That covers the BRANCH-POLICY park, the bus dispatch's WAIT
    and `proof_watch.py`.
  - A gate red whose output is `gate.py` `deferral(...)` is pending while a run it names is
    unconcluded, and for `SWEEP_SETTLE_POLLS` after.
  - A structural self-test fails if any other code path compares that check's conclusion to
    `failure`.
  - Failing test first: the #3264 review instance (red 02:01:18Z, sibling green 02:01:51Z) is
    parked today and waits under the fix.
  - Null control: a gate red naming no busy run is red at once.
  - A mutant dropping the settle is killed.
- **Orchestrator.** Retire `s13/edit_rerun.sh`: the sweep re-runs within about 15 s of the
  decider's completion, and a manual re-run cancels code runs.
- Carry texts cite `triage: dev/programme/triage/s6-batch136.md#P436`.
