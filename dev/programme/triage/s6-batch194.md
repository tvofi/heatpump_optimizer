# Proposal triage, session s14, batch 194 (P616, P617, P618)

The bar and the denominators are batch 141's. The three rulings share one destination, the
group R10-RELAY-NOBODY-STALL (triage s6-batch189.md#P611). At this ruling that group is queued and
not yet on the roster. It has no dispatch, fix or handoff ref (`git ls-remote origin
'refs/heads/*relay-nobody*'` is empty), so no live fixer misses these carries.

Sources:
- origin/main `ee64358be7`. Every line number below is at that commit.
- `handoff/audit-r10-roster` at `9e1a9d5395`.
- The root-cause seat's scratch bare repository of `dispatch/*`, `handoff/*`, `handoff-body/*` and
  `handoff-wip/*` refs, fetched about 11:50Z. From it: 1,240 dispatch commits since 2026-11-04,
  over 202 fixer topics, and the 18 BLOCKED.md files on `handoff-wip/*`.
- The relay's `tick-loop.log` (22,603 lines, read 2026-11-11 about 12:20Z).

## P616: PREPR-SKIP-CLOSURES-IN-PROMPT

Verdict: ACCEPT narrowed, as part of the R10-RELAY-NOBODY-STALL carry STOP-TO-BLOCKED (P617). The
owner's standing ruling (PREPR_SKIP_CLOSURES=1 allowed) goes into `cloud_dispatch.py`'s rendered
fixer text, once, for every fire. The other arm, prepr.sh skipping closures by itself when the
interpreter lacks homeassistant, is rejected.

Source: queue line 294, 2026-11-11T12:01:56Z, orchestrator s14. The main-red hotfix sat 2h25m
(fix committed 09:39Z, first handoff attempt 12:04Z) because a cloud fixer stopped twice on prepr's
closures step.

Instances:
- **The ruling is already supplied by hand, per brief.** 197 of the 1,240 dispatch commits since
  2026-11-04 carry `PREPR_SKIP_CLOSURES` in their PROMPT.md, over 49 of the 202 topics (24%). The
  phrasing varies: "PREPR_SKIP_CLOSURES=1 allowed if only the homeassistant ...", "Hotfix-scoped
  prepr: `PREPR_SKIP_CLOSURES=1`". The rendered template names it nowhere: `git grep
  PREPR_SKIP_CLOSURES ee64358be7 -- tools/audit/seat/cloud_dispatch.py` is empty. The hotfix that
  stalled was a topic whose brief lacked it.
- **How often the cloud closures step stops a seat.** Of the 18 BLOCKED.md files on `handoff-wip/*`
  now, 1 names a closures refusal (r10-dependabot-3414-compat: "closures: tests/entities.py exit 1,
  CalledProcessError from tests/throwaway_git.py git init (exit 128), identical on origin/main"),
  and none names homeassistant. `ModuleNotFound` appears in the prompts of 2 topics (4 dispatch
  commits). The RCA's sample puts ENV stops at 3 of 33 real stalls (about 9 a week), the
  combi-census hotfix among them.
- **Why not the interpreter probe.** The cloud closures failure has at least two shapes. One is
  the throwaway_git `git init` exit 128 above. The other is the `tests/entities.py` shape that
  `dev/audit/rca/R10-RCA-CLOUD-ENTITIES-ENV.md` shape B records as a misdiagnosis, a run missing
  `PYTHONPATH=tests/hastub`, not a missing package. A skip keyed on "the interpreter lacks
  homeassistant" would miss the first shape and paper over the second. The rendered ruling covers
  both, and the seat says so in Friction.
- **The 20% bar.** The class it removes is a stop with no record that costs 125-196 min median
  (the RCA's `c2-20.txt`) against a healthy 10 min from last code to body. A hand step on 24% of
  topics goes away. This instance cost 2h25m on a main red. The marginal cost is one sentence in a
  file the P617 carry already edits.

Cost: one rendered sentence in `cloud_dispatch.py`, inside the STOP-TO-BLOCKED carry, and its
render-test assertion. No new file or check.

Binding: the ruling exists and is applied by hand to 24% of topics. Rendering it removes the miss
at near-zero marginal cost. The prepr arm is rejected because its predicate keys on the wrong cause.

## P617: R10-RCA-FIXER-NOBODY-STALL countermeasures C1 and C2

Verdict: ACCEPT. Carries STOP-TO-BLOCKED (C1, with P616's sentence) and REFUSAL-RECORD (C2) go on
R10-RELAY-NOBODY-STALL. The group's brief is rewritten to hold them, P611's arm 1 (the fold-arm
indent regex) is dropped as superseded by C2, and the group goes from S to M. The RCA lands with the
group as `dev/audit/rca/R10-RCA-FIXER-NOBODY-STALL.md`, scrubbed of host paths. These are
root-cause countermeasures, so they keep their route under `defect-root-cause.md`. The bar below is
checked anyway.

Source: queue line 295, 2026-11-11T12:06:50Z, the root-cause seat's result for
R10-RCA-FIXER-NOBODY-STALL.

Instances:
- **C1, checked at main.** `cloud_dispatch.py:363` renders "Never work around a hook or a refusal;
  report it in your result instead". `:236` renders "on REFUSE stop: report its line as your result
  and start no work". The fixer text routes only a question and a CARRY-LANDED exit to BLOCKED.md.
  A cloud seat's only return is a pushed ref, so a seat that obeys a refusal leaves no record.
- **C2, re-measured here.** `tick-loop.log` holds owed carry-fold lines for 65 distinct topics
  against FOLDED lines for 6 topics. Of the owed lines, 4,200 read "names no refusal line" and
  3,164 read "no kept body". The RCA, cut earlier, counted 56 topics and 6 folded, so the
  re-measure only grew. `carry_fold_arm` (`cloud_relay.sh:805`) parses the seat's free-form
  BLOCKED.md, and P611's indent regex fixes one of three shapes (indented, no kept body, prose).
  Moving the record into `keep_refused` (`body_push.sh:92`), which already writes the kept-body
  commit, removes the parse.
- **The bar.** The RCA's sample puts about 96 real stalls a week (116 x 33/40). C2 covers about 23
  of them and C1 at least 9, at most 35. So C1 and C2 together cover 32 to 58 a week, 33-60% of the
  class, each worth at least 60 min of critical-path latency (silent 125-196 min median against a
  healthy 10). That clears 20% of the class's stall time with the floor share alone. Standing cost:
  C1 is rendered text plus one push per stop; C2 adds nothing per run, since body_push already
  writes the commit.
- **Null control.** A healthy fire's 10-min last-code-to-body median is the baseline. The saving
  counts only the time past it. The RCA's own control (wakes against dispatch commits, 27% against
  27% within 60 s) rules out "the seats are woken by dispatches" as the stall mechanism.
- **The RCA's SILENT class may be one smaller.** The addendum (queue line 296) reads that
  r10-prepr-residue's 00:26Z fire pushed a BLOCKED.md at 00:29:22Z. That ref has since been rebuilt
  (`handoff-wip/r10-prepr-residue` at `19730f9f20` holds no BLOCKED.md in its history): the
  deleted-record loss the RCA's section 9 names. C1's share is stated as a range, so this moves
  nothing.

Cost:
- One group re-sized S to M: `cloud_relay.sh`, `cloud_dispatch.py` and `body_push.sh` (the
  `keep_refused` seam alone), the render and fold self-tests, and the RCA document.
- `cloud_dispatch.py` and `cloud_relay.sh` are in R10-REVIEW-DISPATCH-RESIDUE (in progress), and
  `body_push.sh` in R10-BODY-CONTRACT and R10-PREPR-RESIDUE (in progress). The group is set after
  R10-REVIEW-DISPATCH-RESIDUE. The body_push overlap is a distinct seam.

Binding: a measured share of 33-60% of a 96-a-week stall class, at a standing cost of rendered
text and a file in an existing commit.

## P618: TURN-END-ON-BACKGROUND (candidate C4) and FRUGAL_ALLOW_INLINE

Verdict: DEFER the prompt line ("never end a turn on a background job; a wait is a Monitor
until-loop") until three more silent sessions are read. REJECT setting FRUGAL_ALLOW_INLINE=1 for
cloud seats: it reverses an owner directive, which only the owner can change.

Source: queue line 296, 2026-11-11T12:07:14Z, the orchestrator's read of one cloud session
log (the r10-prepr-residue fire of 00:26Z).

Instances:
- **Evidence so far is one session, and that session was not silent.** It ended its turn at
  00:28:31Z waiting on a frugal scout, resumed 43 s later on the scout's hand-back, and pushed a
  BLOCKED.md with a Question at 00:29:22Z. A turn end that the hand-back undoes costs 43 s, not a
  stall. Whether a turn end ever becomes a silent stop is what the RCA's 9 SILENT rows would show,
  and none of them has been read.
- **The frugal setting is the owner's.** `cloud_dispatch.py:137-141` renders the owner's
  frugal-routing directive (tvofi 2026-11-06, triage s6-batch127.md#P398) verbatim to every role,
  ending "never set FRUGAL_ALLOW_INLINE". A cloud environment variable that sets it reverses that
  directive.
- **What the prompt already says.** `WAIT_LINE` (`:134`): "Never wait in one tool call longer than
  240 s; poll again instead." `:315`: push each verified step "before any wait on a background
  run, so an idle container loses nothing". The second presumes turn ends happen and guards the
  work, not the record.

Cost of acting now: a rendered line whose benefit is unmeasured. Unmeasured is DEFER.

Disposition:
- Re-open trigger: the orchestrator reads the last 20 turns of three SILENT stops from the RCA's
  section 8 table (r10-i18n-de 11-07, r10-machinery-ratchets-p2 11-04, r10-fly-cipredict-restoring
  11-06, r10-process-slim-p2 11-11; three of the four). If two or more of the three ended a turn
  on a background job and never resumed, the line goes as a carry on R10-RELAY-NOBODY-STALL's
  STOP-TO-BLOCKED arm, in the same render text, with its own render assertion.
- FRUGAL_ALLOW_INLINE goes to the owner only, by the orchestrator, if those reads show the guard
  as the cause of a silent stop.
