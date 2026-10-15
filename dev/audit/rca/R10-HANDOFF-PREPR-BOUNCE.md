# R10-HANDOFF-PREPR-BOUNCE: three round-10 handoffs refused by `open_pr.sh`'s prepr step

Root-cause seat, `root-cause.md`, 2026-10-15. Measured at `origin/main` `78324e4a1`
(the refusals themselves ran at `b22db919d` and `3d650d26c`). Nothing was fixed or
written to GitHub. Every duration below is a file-timestamp difference or a `time`
line from this seat's own run; the one estimate is marked as one.

## 1. What happened, reproduced

| topic | refusal at `open_pr.sh` | mechanism | reproduced here |
|---|---|---|---|
| FAHRENHEIT | `ci predict`: `UNCLASSIFIED` and `UNDER-SCOPED` for a new `issues.py`, `INERT READS` for a new harness | static `tools/pr/ci_predict.py` arms | yes: `ci_predict.py --base origin/main` in the topic's own worktree prints the same 3 `PREDICT` lines |
| TARIFF | `ci predict`: `INERT READS` x2 for two new harnesses | same | the 2 lines are in `p1.log`; its worktree is at the merge base now, the same arm is reproduced on a probe below |
| DEEPLINK | `pr-body`: 2 errors | **not a closures red**: `## Forward-carry` names `dev/programme/rosters/wave-r10-groups.json`, "not in the tree"; `## Friction` line does not parse | yes: `policy_lint.mjs --pr-body` on its body prints exactly those two `ERROR` lines (the refusal line itself only prints "2 error(s)") |

So three refusals are **two mechanisms**, not one. The closures mechanism is 2 of 3
and is the recurring one. DEEPLINK is the same *stage* (the first complete prepr
verdict on the final tree is produced inside `open_pr.sh`) with a different cause,
section 5.

A fourth is queued: `open-i1.log` is still running as this is written, and
`ci_predict.py` in `~/.local/state/hpo/pr/r10-i1/wt` already prints 3 `INERT READS`
lines for its three new harnesses. That is a prediction, not a refusal.

Facts the closures mechanism rests on:

- `tests/harness_headers.py` reads every file under `dev/audit/harnesses/`, and
  `tests/closures.json` lists them one by one under `inert_reads` (the predictor
  counts 26 siblings; `inert_siblings()` in `ci_predict.py` fires at three or more).
  `fixer.md` step 18 *obliges* a fixer to land a harness there. A fixer who obeys
  step 18 and writes one new harness is therefore certain to meet this arm.
- `closure.py` records the inert dimension only under `strace`. `strace not found`
  on this Darwin arm64 seat; `ci-autofix.md` says the same ("the inert dimension,
  which is Linux-recorded (`strace`-only)").
- `FIXER-BRIEF.md`'s amended remedy for a predicted closures red is
  `tests/derive_closures.sh --single <script>`, "sound on Darwin for Python lanes".

### Demonstration that the amended remedy does not clear INERT READS

Probe worktree off `origin/main`, one commit adding
`dev/audit/harnesses/zz_rca_probe.py` (a copy of a listed harness):

| step | command | result |
|---|---|---|
| control, no probe | `ci_predict.py --base origin/main` | `CI PREDICT: no closures or fast red predicted` (5.4 s) |
| with probe | same | `PREDICT closures INERT READS tests/harness_headers.py: dev/audit/harnesses/zz_rca_probe.py (a new file beside 26 it lists)` (6.6 s) |
| the brief's remedy | `tests/derive_closures.sh --single tests/harness_headers.py` | rc 0, **500 s**; `git diff` on `tests/closures.json` is one line: `"seconds": 99.7` -> `498.8`; the probe path is **absent** from the diff |
| after the remedy | `ci_predict.py` again | still `INERT READS ... zz_rca_probe.py`, still 1 predicted red |
| the one-line hand edit | insert `"dev/audit/harnesses/zz_rca_probe.py",` in sorted position in `inert_reads["tests/harness_headers.py"]` | `CI PREDICT: no closures or fast red predicted` (8.7 s under load) |

The remedy the brief now prescribes costs 8.3 minutes, repairs nothing for this arm,
and quintuples a recorded `seconds` figure with a laptop timing. The hand edit
is the repair, and it already has precedent in the tree, written down only in commit
messages: `387128bb` (#2025), `fbc9400a9`, `d7bfeb0dd` ("the inert dimension is
recorded by Linux strace only, so the path is added by hand to the sorted list") and,
today, `handoff/r10-tick-roster` (`closures: harness_headers reads the new
r10_tick_which_roster harness (inert read)`). That one handoff, of the four that add a harness,
carried the line and did not bounce.

The UNDER-SCOPED arm (FAHRENHEIT's new module read by 19 scripts) is different: the
bot does repair it after a PR exists (23 `ci: re-record closures` commits since
2026-09-25, 4 of them since R9-CI-1 merged), so there waiting is right for the
*closure* and wrong only because `prepr` refuses before any PR exists. A pre-PR
repair means 19 `--single` recordings (the script's own header prices the full run
at "~25 minutes"; one script took 500 s here), unmeasured in total.

## 2. The cause, named

**Cause.** Two documents give contradictory instructions for the same refusal, and
the refusal text sends the reader to the wrong one. `prepr.sh` step 6d refuses a
predicted closures red "before the handoff" and says "who repairs which is
`ci-autofix.md`'s". `ci-autofix.md` says to wait for a bot that cannot run before a
PR exists, and (for INERT READS) cannot repair a diff whose reading script CI does not
re-record. The contradiction was found on 2026-10-08, carried, and the carry never
ran. Fixers obeyed the document the refusal pointed to.

The carry's history, because it is the stretch of the process that failed:

1. 2026-10-08, `c94842ed9`: `ci_predict` downgraded INERT READS to a warning, its
   message recording "#2025's fixer hand-edited tests/closures.json (387128bb) to pass
   prepr 6d; #2054 and #2056 met the same refusal with new harness files". Three
   instances, already.
2. Same day, `0f64774f6`: reverted, because "a scoped CI run does not re-record the
   reading script, so a warning there still lets the red reach main" (review-2061
   VERDICT3). Correct, and it makes `ci-autofix.md`'s "CI autofixes ... INERT READS"
   untrue for that diff class.
3. `dd415b926` carried the item to "R9-RO-9b" (`tests/closures`-side: "warn only when CI
   re-records the reading script"), as `dev/programme/carries/carry-1922.json`, whose
   own `_comment` says "Carry to R9-RO-9 (#1922)".
4. Destination check at `78324e4a1`: `wave-r9-groups.json` has no group `R9-RO-9b`; its
   `R9-RO-9` is `"class": "reorganisation"` (a path-layout group, owner-gated on
   workflows). `grep -c rederive tools/pr/ci_predict.py` is **0**: the carried
   behaviour was never written. `ci-autofix.md` was edited again on 2026-10-11
   (`307881fcd`, R9-CI-1, "six wording-only trims") with the contradiction in view.

Note what the carry would have changed: not this round's bounces. A new file under
`dev/audit/harnesses/` is in no closure, so `rederive` would not contain
`harness_headers.py` and the arm would still refuse. The carry's own design is also
insufficient; the missing piece is the hand-edit instruction, which exists nowhere
outside four commit messages.

## 3. Process state

**(c) The process was followed and did not produce the intended result.**

Evidence, quoted:

- The process: `ci-autofix.md`, "If `closures` is `UNDER-SCOPED` ... **wait**" and
  "do not Darwin `--single` an under-scope CI already recorded". The brief's old
  line, and its surviving line today: "CI autofix re-records (ci-autofix.md: read the
  summary line, wait for the bot commit)". Two fixers planned exactly that.
- It was obeyed, and wrong: their `## Unpinned sites` sections quote "Every site
  `prepr.sh` step 6d lists" (FAHRENHEIT, 22 sites) and cite the same step (TARIFF,
  28 sites), so step 6d ran in their trees, the `PREDICT closures` lines printed
  above its step line, and the handoff was still reported ready.
  `tests/closures.json` is absent from both handoff diffs (`git diff
  <merge-base>...handoff/r10-fahrenheit -- tests/closures.json` and the tariff one
  are empty), so the refusal was not repaired and not meant to be.
- Not (b): a firmer "prepr must pass" is what the brief said and what the fixers
  appear to have read as already satisfied by "autofix will repair". Adding "NOT left
  to the autofix bot" to the brief (done at 16:47) tells them harder and offers a
  remedy that, for INERT READS, does nothing (section 1). TARIFF's body was pushed at
  17:15, after the amendment, and refused on INERT READS only.
- Not (a): the detector exists and detected. This is the system working as designed
  on the detection side. Nothing is missing there.
- Not (d): no precondition moved after the documents were written. `ci_predict.py`
  was added 2026-10-07 (`00007b44c`); `ci-autofix.md` was edited three days later with
  it in the tree. The documents disagreed from the start of the predictor, and the
  disagreement was known on 2026-10-08.

The finding-propagation step (the 2026-10-08 carry) is also state (c), one level up:
it was followed (a carry file was written, committed and merged) and did not produce
the result, because its destination was a group that was never in the roster. That
sub-finding is `finding-propagation.md`'s to rule on; this analysis only records that
the carry file's `R9-RO-9b` is not a roster id.

DEEPLINK is (c) as well, for the carry half: the brief told the fixer to forward-carry
into the roster via `roster_edit.py`, the roster is on a branch and not on `main`, and
`prepr` requires the carry destination to exist in the tree it runs in, so the
instruction and the check cannot both be satisfied before the roster PR merges. The
Friction half is (b): the template's grammar is `<rule_id>: <kind>: <evidence>` and the
line wrote a step label.

## 4. How far the class reaches

Search, with the rule written down:

**Instance count, rule:** a handoff ref (`refs/heads/handoff/r10-*`, 15 distinct
topics, the `hpo-orphans` copies excluded) whose three-dot diff adds a file under
`dev/audit/harnesses/*.py` and does not touch `tests/closures.json`, or adds a
`custom_components/**.py` module. Command:

    git diff --diff-filter=A --name-only $(git merge-base origin/main $r)...$r

| set | n of 15 | members |
|---|---|---|
| new harness, no `closures.json` line (INERT READS predicted) | 3 | fahrenheit, tariff, i1 |
| new harness, with the hand-edited line | 1 | tick-roster |
| new production module (UNCLASSIFIED / UNDER-SCOPED predicted) | 1 | fahrenheit |

So at least 3 of 15 handoffs (20 %) carry a certain refusal, and 3 of the 4 `open_pr`
runs that have finished or run far enough to predict are in it. Null control: the
same loop over the 11 other topics returns `newHarness=0 newProdModule=0`.
Round 9 recorded three earlier instances in one commit message (#2025, #2054, #2056).
That is six in two rounds, so the recurring-error clause is met on its own terms,
and this document is the root-cause seat that clause calls for.

What else the same cause reaches: any other prepr step whose repair a Darwin seat
cannot perform before a PR exists. Checked: `PREDICT mutation ... ADDED UNPINNED`
(warn only, the body disposes, correct as designed); `claims hygiene`,
`no-copies`, `layout guard` (all repairable in-tree, all ran green here). The
`PREPR_SKIP_CLOSURES` message "closures-autofix is the only check left" printed by
`open_pr.sh` is false for the same reason: step 6d still refuses the same arms.

## 5. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

Wall-clock, per occurrence, over a release cycle. The cycle is the round-10 fix wave:
`wave-r10-groups.json` on `handoff/audit-r10-roster` has 52 groups; 15 have a handoff
ref so far.

**cost(defect), one bounce.**

- The refused prepr run, measured as `p1.log` birth to last write (the app_push
  stage that runs prepr): DEEPLINK 6 min 48 s, FAHRENHEIT 12 min 04 s, TARIFF
  9 min 52 s; mean 9.6 min. The one passing run (gate-yield) took 11 min 38 s, so the
  refusal is not cheaper than success: the run does its work, then refuses.
- The fixer round trip (wake, repair, push): **not measured; estimate 10 min**, basis:
  a one-line edit plus a re-push, plus latency the orchestrator's tick adds. Treat as
  an input, not a finding.
- The re-run of prepr after repair is not counted: it is the run that would have been
  needed once anyway.

cost(defect) = 9.6 + 10 = **about 20 min**, in the orchestrator's serial lane for the
first term.

**P(recurrence).** Measured class frequency this round: 3 of 15 handoffs (20 %), as
section 4. Lower bound, since 10 of the 52 groups have not handed off.

Expected loss over the remaining wave: 0.20 x 52 groups x 20 min = **about 3.5 h per
wave**, if the rate holds.

### Candidate countermeasures

| id | change | standing cost per handoff | passes? |
|---|---|---|---|
| M0 | do nothing | 0 | loses: 3.5 h per wave, and the class recurred across two rounds |
| M1 | `body_push.sh` runs a full `prepr.sh` | 9.6 min (the same run `open_pr.sh` repeats) | **fails**: 9.6 x 52 = 8.3 h > 3.5 h saved |
| M2 | `body_push.sh` (the handoff moment) runs `ci_predict.py --base origin/main` only, refuses on rc 1 | 5.4 to 8.7 s measured, 48 s once on a loaded machine | passes: 52 x 8.7 s = 7.5 min against 3.5 h |
| M3 | `ci_predict.py`'s `REFUSE`/`PREDICT` line prints the repair per arm instead of "who repairs which is ci-autofix.md's" | 0 s | passes |
| M4 | `ci-autofix.md` and `fixer.md` carry the pre-PR repair per arm (policy: owner approves) | 0 s | passes |
| M5 | `closures.json` lists the harness scan by directory, so a new harness needs no line | unmeasured; touches `closure.py`'s check and merge | not costed; owner's call |

M2 and M3 together close the class for the next fixer who reads the output; M4 makes
the documents agree. M1 is recorded as refused on the cost test.

## 6. Recommendation

Address **state (c)**; do not write a firmer instruction.

1. **M3, no policy**: change the text at the end of the predictor's refusal in
   `ci_predict.py` (it reads "repair before the handoff; who repairs which is
   ci-autofix.md's") to name the repair per arm:
   - `INERT READS`: add the printed path, sorted, to `inert_reads["<reader>"]` in
     `tests/closures.json` (Linux `strace` records it; no Darwin recording can);
   - `UNDER-SCOPED` / `UNCLASSIFIED`: `tests/derive_closures.sh --single <script>` for
     each named script, with the cost it will take, and that a new module read by
     many scripts is better asked of the orchestrator than recorded locally.
2. **M2, no policy**: a handoff gate that runs the static predictor only. The
   handoff is two pushes (code ref, then `body_push.sh`); the gate belongs in
   `body_push.sh`, which already runs in the fixer's worktree. It must refuse when
   `ci_predict.py` returns 1 *and* print the M3 text, so that a fixer cannot hand off
   a head that `open_pr.sh` will refuse for a reason a static read names.
3. **M4, owner approval** (policy; request states state (c)):
   - `ci-autofix.md`: replace "**wait**" with the real sequence. Before a PR exists,
     there is no bot, so a closures red that `prepr` predicts is repaired by the
     fixer; after a PR exists, the bot repairs UNDER-SCOPED and, **only where CI
     re-records the reading script**, INERT READS (`0f64774f6`). Delete or qualify
     the table row `UNDER-SCOPED`, INERT READS | `closures-autofix` for the
     second half.
   - `fixer.md` step 5: say that `prepr.sh` is run to no `REFUSE` before the handoff,
     name step 6d, and say which of its refusals are repaired by hand and which by
     `--single`.
   - `fixer.md` step 18 (or its neighbour): a new harness under `dev/audit/harnesses/`
     adds its line to `inert_reads`.
4. The brief's remaining line ("CI autofix re-records ... wait for the bot commit")
   should be struck; it contradicts the line below it. Not policy, the orchestrator's
   file.
5. **Carry**: R9-RO-9b is not a roster id. If `rederive`-keyed warn-only behaviour is
   still wanted, it needs a real roster group; it would not have prevented today's
   bounces (section 2) and should not be built on the strength of this record alone.

**Demonstration owed by `root-cause.md` step 5**, for the check-shaped M2: this seat
did not build M2. The detector it would call is shown failing on the defect and
passing once repaired (section 1: control green at 5.4 s, probe red at 6.6 s, hand
edit green at 8.7 s, and FAHRENHEIT's worktree red with 3 lines). The gate wrapped
around it is the builder's to demonstrate, with a null control that a healthy
handoff (gate-yield's head) does not trip it and a skip (`ci_predict.py` absent)
does not go green silently, as `predict_line` returns rc 3 for exactly that case.

## 7. Policy contradictions in the tree, quoted

1. `ci-autofix.md`, first paragraph: "If `closures` is `UNDER-SCOPED` ... **wait** --
   a `DIRTY` head queues no run, so no bot commit comes." against the predictor
   comment in `prepr.sh` above `predict_line`: "R9-RO-11's pre-study measured
   reddening this round's fix heads after the handoff while the autofix jobs repaired
   none of them; those refuse."
2. `ci-autofix.md`: "the bot merges INERT READS from CI recordings too (#1886,
   R9-CI-1)" against `0f64774f6`: "a scoped CI run does not re-record the reading
   script, so a warning there still lets the red reach main."
3. `ci_predict.py`, the refusal line: "repair before the handoff; who repairs which is
   ci-autofix.md's" against `ci-autofix.md`, which has no clause that says who repairs
   anything before a handoff. `grep -n 'predict\|prepr' dev/governance/rules/ci-autofix.md`
   returns nothing.
4. `open_pr.sh` sets `PREPR_SKIP_CLOSURES=1`, whose message reads "closures-autofix is
   the only check left", while step 6d of the same run refuses the same two arms.
5. `fixer.md` step 5, "leaving the rest to CI" and "Running locally does not discharge
   CI. What `scope.run` names is green locally and the body passes
   `tools/pr/prepr.sh`" say nothing of the closures refusal; step 18 (harnesses
   "land in the same pull request" under `dev/audit/harnesses/`) makes the INERT
   READS refusal certain without saying so.
6. `FIXER-BRIEF.md` (not policy), amended: "Never a full derive_closures.sh off Linux;
   CI autofix re-records (ci-autofix.md: read the summary line, wait for the bot
   commit)" and, in the next bullet, "A predicted closures red is NOT left to the
   autofix bot (no PR, no bot run): re-record ... with `tests/derive_closures.sh
   --single <script>` (sound on Darwin for Python lanes ...)". The second is wrong for
   INERT READS (section 1) and the first contradicts it.
7. `CLAUDE.md` rule table: `ci-autofix.md` is described as "wait for the bot commit,
   do not duplicate". The index carries the same instruction a fixer reads first.

## 8. Not covered

- What the three fixers ran before handing off is inferred from their bodies (step 6d
  keys quoted) and from the task statement, not from a session transcript.
- DEEPLINK was not checked for whether its fixer ran prepr at all.
- The `--single` cost for 19 scripts (FAHRENHEIT's UNDER-SCOPED arm) was not run; one
  script took 500 s.
- Whether the hand-edited `inert_reads` line passes CI's `closures` check on a Linux
  recording was not re-run; the precedent commits merged to `main`.
