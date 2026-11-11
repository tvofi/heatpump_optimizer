# Proposal triage, session s9, batch 91 (P329, P330)

The rolling batch after batch 90 (#3039). Facts were read at origin/main `0cae227c3`.

## P329: carry_audit reads a review's summary prose as an unrouted finding

Verdict: ACCEPT, narrowed, as one carry on R10-FLY-RELAY-REVIEW-FF. That group holds P308's
`## Evidence` carry (`s6-batch74.md#P308`), which edits the same classifier, `items()` in
`tools/audit/carry_audit.py`. The narrowed rule is an owner-approval carve-out read in every verdict
section. Both arms of the proposal as filed are rejected.
- **What was proposed.** One of two things:
  - (a) `carry_audit` skips a review's `## Summary` section, and non-bulleted prose, the way it
    skips the verdict line;
  - (b) the reviewer contract requires `Carry: dismissed` on summary prose.
- **What the over-fires are.** P308, once built, frees every `## Evidence` item that has no LEAD,
  no lead above it and no `Carry:` marker. Among the field items that park the train, that leaves
  three outside `## Evidence`. Each trips NONBLOCK's `does not block`:
  - #3013 `fccf8846` (`## Summary`): "`away.py` is code-owned, so `main-protect-checks` requires
    tvofi's approving review at merge. This verdict flags that and does not block on it."
  - #3005 `e963066e` (the opening paragraph under `## Round`): "coordinator.py is code-owned, so
    tvofi's approving review is still owed before the merge. This is flagged and does not block."
  - #3038 `7dba2920` (`## Summary`): "... it is not sounder (see Findings), so the score does not
    block."
- **Two of the three state a merge condition, not a note.** The code-owner rule of
  `main-protect-checks` enforces the owner's approving review at the merge. A reviewer who repeats
  that rule, and says its own verdict does not block on it, defers no work. That is the shape of
  NOT_REQUIRED's check-state carve-out, which frees a check's state and nothing else.
- **(a) is REJECTED.**
  - **Prose with no bullet is where routed findings sit.** In the 484 `verdict/<pr>` refs, 69
    flagged items sit in a `## Summary` section or in non-bulleted prose outside `## Evidence`, and
    19 of them carry a `Carry:` marker. Unheaded or opening prose holds real findings:
    - #2549 `01ce8b81`: "Residual, not blocking: the detached holder is a child of the loop's
      process group ...";
    - #2217 `aab127ea`: "Observation (no block): seat boxes read 1.99-2.03 locally ...";
    - #2386 `97a3b64e` and `e414e101`: two defects, numbered under an unheaded lead.

    Skipping that prose drops the class this arm exists to catch.
  - **A skip keyed on the `Summary` heading buys little.** In the same 484 refs, exactly two items
    are flagged under a heading `Summary`: #3013 `fccf8846` and #3038 `7dba2920`. The carve-out
    below already clears #3013. The skip would buy one item, #3038, and leave a whole section that
    a reviewer can write a deferral into unread.
- **(b) is REJECTED.** It edits `fix-review.md` (137 of 140 lines in `--budgets`) to make every
  reviewer pay for a classifier defect, and it changes what a seat must do, so the owner approves
  it. `Carry: dismissed (item <id>)` already exists for a one-off.
- **#3038's shape is DEFERRED.** "The score does not block" is a reviewer's ruling on the
  architecture score. One instance in 484 refs gives no shape to fit a carve-out to. Re-open at
  three such items once P308 and this carry have landed. Until then the workaround is unchanged:
  `Carry: dismissed (item <id>)`.

Source: the orchestrator s9's triage-queue line of 2026-10-31T12:27:57Z (slip, recurring). #3031
item `61602ac4` and #3038 item `7dba2920` each cost a park and a solo `--no-pre-flight` train run,
and the orchestrator waived both by id.

Instances: every figure below is `carry_audit.items(text, True)` at `0cae227c3`.
- **The train log.** `train/current.log` (orchestration dir) holds seven PARK lines whose first
  item is a review comment. All seven are over-fires: #3011 `804b8e49`, #3013 `fccf8846`,
  #2997 `a7dc6fe0`, #3005 `e963066e`, #3019 `dc6d3107`, #3031 `61602ac4` and #3038 `7dba2920`.
  Each comment body was read once with
  `gh api repos/tvofi/heatpump_optimizer/issues/comments/<id> --jq .body`.
  - Four of the seven fall in `## Evidence` and clear under P308: #3011, #2997, #3019 and #3031.
  - #3011's comment holds a second item, `d7cfccbd`, a code-owned note under `## Evidence`, which
    P308 also clears.
  - The remaining three are the ones listed above.
- **The last 30 merge verdicts** (`verdict/<pr>` `VERDICT.md` that opens `Fix review: merge`,
  #3007 to #3039). 11 items are flagged and 5 of them have no `Carry:` marker. 3 of those 5 are in
  `## Evidence`, where P308 clears them: #3030 `7e0f5e82`, #3019 `dc6d3107` and #3007 `41721472`.
  The other 2 are #3013 and #3038, both in `## Summary`.
- **The carve-out, prototyped** over all 484 `verdict/<pr>` refs and the seven comments, using the
  rule in the carry below. It changes exactly these items from flagged to clear:
  - verdict/2997 `a7dc6fe0`, verdict/3004 `fdeb7c52`, verdict/3005 `e963066e`, verdict/3013
    `fccf8846`;
  - and the comment copies of #2997, #3005 and #3013.

  No other item changes. #3011 `d7cfccbd` stays flagged ("I note this for the merge seat only; it
  does not block" is not the bare sentence), and P308 clears it.
- **Null rows hold.** These items name code-owned paths and stay flagged, because neither holds
  the approval sentence:
  - #2281 `e9ead054`: "It is code-owned and routed to TICK-ORCH", a residual;
  - #2867 `fe436106` (F7) and `9132bbad`: a finding about the wrong code-owned group.

Cost: S. All of it sits in `items()` in `tools/audit/carry_audit.py`: one sentence-level strip,
about 10 lines, plus four self-test rows and one mutant. `carry_audit.py` has no
`policy_lint.mjs --budgets` row; the `--budgets` output at `0cae227c3` names it 0 times. No policy
file changes. The carry rides P308's dispatch on the same branch of the same function, so it adds
no fixer or review cycle of its own.

Binding:
- **Benefit, measured.** Four code-owned notes were flagged, at #2997, #3004, #3005 and #3013,
  all in the past week. Two of them (#3005, #3013) sit outside `## Evidence`, where P308 does not
  reach, and each parked the critical-path train. Each park cost an orchestrator waiver and a
  solo `--no-pre-flight` run.
- **The class recurs.** It comes back whenever a fix touches a code-owned path, which every
  R10-COP-GATE part does (`coordinator.py`).
- **Cost.** The carve-out frees one sentence of known shape and nothing beside it. Its cost is a
  few lines in a carry already owed on that function.
- **The rejected arms.** One blinds a section that holds real findings; the other moves a
  classifier defect onto every reviewer.

The carry:
1. **The approval sentence.** A sentence (split on `.` or `;`) is freed when it states the owner's
   approving review is required at the merge: it matches
   `\bapproving review\b.*\b(?:at|before) (?:the )?merge\b`, case-insensitive. Freed means
   NONBLOCK and DEFERRED are not read in it.
2. **The bare sentence after it.** The one sentence directly after it is freed too, but only when
   that sentence says nothing except that this does not block. It matches
   `\s*(?:this (?:review|verdict) |this is |it )?(?:flag(?:s|ged)(?: that)?,? (?:and )?)?(?:does not block(?: on it)?|not a block)\s*[.;]?\s*$`,
   case-insensitive.
3. **Every verdict section reads it.** That covers `## Evidence`, `## Summary` and any other
   heading, read the way NOT_REQUIRED's clause is freed. LEAD still reads an item's first words.
   An item that opens with a lead stays a finding.
4. **Fixtures that go from flagged to clear:**
   - #3013 `fccf8846` and #3005 `e963066e`, each with its text verbatim;
   - "- x.py is code-owned, so tvofi's approving review is required at merge. This review does not
     block on it."
5. **Null rows that stay findings:**
   - "- x.py is code-owned, so tvofi's approving review is required at merge. A defect in y is left
     in place, not blocking." (the second sentence is not bare);
   - "- x.py is code-owned and a defect in it does not block." (no approval sentence);
   - #2281's "It is code-owned and routed to TICK-ORCH" shape, under a residual heading.
6. **One mutant.** Drop the strip, and the three fixture rows fail.

Rejected: (a) skipping `## Summary` or non-bulleted prose, and (b) a reviewer-contract
`Carry: dismissed`. Deferred: #3038's "the score does not block" shape, re-opened at three
instances.

## P330: the merge seat serialises default-flag pull requests into solo trains

Verdict: ACCEPT, narrowed, as one carry on R10-FLY-TRAIN-DEFAULTS. The carry is the contract
sentence, kept inside `standing-merge.md`'s current cap. The optional `add` refusal is REJECTED.
R10-FLY-TRAIN-DEFAULTS is `carries-open`, its `files` name `dev/governance/roles/standing-merge.md`,
and its part 2 is still owed.
- **The policy and the instrument already allow batching.**
  - `standing-merge.md` (lines 8-9 at `0cae227c3`) names "one live train".
  - `train.sh` documents `add` (lines 12-16): it "loads one verdicted pull request into the state
    dir's live train -- it joins the batch after the one running -- or, with no train live, starts
    one".
  - `train.sh` also refuses a second live train on the same state dir by pidfile (line 25).
- **What is missing is the obligation.** Nothing says a verdicted default-flag pull request joins
  the live train rather than waiting for it to end.
- **The s9 merge seat's sequencers waited.** `seq3.sh` and `seq4.sh` (s9 merge-seat scratch) each
  run `train.sh add` once per PR and then `waitend`, which polls for a new `TRAIN_RC=` line before
  the next add. That makes every PR a train of its own, `queue=1`. #3037, #3030 and #3039, all on
  default flags, were planned as three solo trains.
- **The orchestrator caught it before the cost landed.** At 13:24Z it added #3030 and #3039 into
  the live #3037 train (seat-ledger, "per orchestrator (batch, do not serialise)").
- **The cost avoided.** One solo train in this log runs 48 to 67 minutes:
  - #3022: `BATCH 20261031-111910`, which ends `TRAIN_RC=0 end=2026-10-31T12:26:51Z`;
  - #3038: `BATCH 20261031-122831`, which ends at 13:16:13Z.

  Each default-flag PR serialised behind another pays roughly one such wait.
- **The owner has ruled on it.** tvofi, 2026-10-31, relayed: "it should queue and batch merges
  where possible".
- **The `add` refusal (arm 2) is REJECTED. Its premise is already built, and it would not see the
  slip.**
  - `merge_train.py`'s `add` already takes one flock and allows one train per state dir. A second
    live train is already refused.
  - The sequencers never ran two trains at once. They waited for one to end and then started the
    next, and at that moment no train is live, so an add-time refusal has nothing to refuse.
  - Catching "a verdicted PR held back while a train runs" needs the seat's own queue state.
    `train.sh` does not have it.
- **Waivers stay separate.** A `--no-pre-flight` waiver runs as its own train because the flags are
  train-wide, and the train has no by-id waiver (merge seat, seat-ledger 10:45Z, #3031). Two
  waivers due at once may share one train. A by-id waiver flag would remove the solo train
  altogether. That was not proposed, and P329's carve-out lowers how often a waiver is needed. It
  is not ruled here.

Source: the orchestrator s9's triage-queue line of 2026-10-31T13:24:23Z (slip, owner-flagged).

Instances:
- `seq3.sh` and `seq4.sh`: one `waitend` per `run`, five and four PRs. The default-flag PRs in them
  are #3037, #3030 and #3039.
- `train/current.log`: the #3037 train, `BATCH 20261031-131945 ... queue=1 (#3037)`, was launched
  solo at 13:19:38Z. #3030 and #3039 joined it at 13:23:11Z and 13:23:32Z, after the orchestrator
  intervened.

Cost:
- **The edit.** One sentence in `dev/governance/roles/standing-merge.md`. Its `policy_lint.mjs
  --budgets` row at `0cae227c3` is `standing-merge.md 36 37 501 507`, so the sentence must be paid
  inside the cap. For example, replace "one live train," on line 9 with the sentence and shorten
  the parenthetical `RECOMMENDED` reference. Do not raise the cap.
- **Approval.** `standing-merge.md` is policy, so the owner approves the merge, or an agent does
  under mandate 6329234399 (scope `all`).
- **No code.** It adds nothing to `train.sh` or `merge_train.py`.

Binding:
- One sentence within an existing cap turns an owner instruction into the merge seat's contract.
  The seat is a sonnet seat that follows that contract literally.
- It saves about one solo-train wait (48-67 min) for each default-flag PR that would otherwise
  queue behind another.
- The refusal arm costs code and catches nothing that the pidfile does not already catch.

The carry: in `standing-merge.md`'s Instruments paragraph, state that a verdicted pull request on
the recommended flags joins the live train with `train.sh add` as its next batch, and never waits
for that train to end. Only a pull request whose flags differ (a `--no-pre-flight` waiver) waits
for its own train, and waivers due together share one. Keep the file within its cap: 37 lines,
507 tokens. A sequencer that runs `add` only after `TRAIN_RC` is the shape this forbids.
