# R10-RCA-GATE-BUSY-DEFER-4: the producer of a deferral was fixed three times, its reader never

Root-cause seat (`dev/governance/roles/root-cause.md`), run beside the repair fixer of
#3290 (R10-HOTFIX-TRAIN-DEFER-WAIT, head `a38bd141`, unmerged), which owns the classifier
wait. This seat changed nothing in `tools/audit/seat/merge_train.py`, `proof_watch.py` or
`tools/ci/`. Measured at origin/main `dee8b413f` (which carries #3287's merge `5c1fa41fb`)
on 2026-11-07 between 21:00Z and 21:45Z. Third instance of one class: a required `gate`
that concludes `failure` as a deferral, not a verdict (#3246, #3278's RCA, this).

## Result

- **Cause.** `gate.py` publishes an edit run's deferral as a failed `gate` check run at
  once ("run(s) [ids] at this head are still being judged; their gate decides"). The code
  run it defers to publishes no `gate` until every unit finishes, and `gate-sweep.yml`
  re-runs the deferred gate only after that run completes. For that whole time the head
  carries a completed, failed `gate`. `merge_train.py` `classify` reads a check run's
  conclusion alone, and `run_state` counts only `success` as a green `gate`, so it reads
  the deferral as RED and the train SKIPs (`ci: red at the head: gate`).
- **Why #3287 did not cure it.** #3287 fixed the producer: the deferring gate no longer
  holds a runner and `sweep.settle` re-judges it. It also made the red visible at once and
  longer to a reader: before it, a deferring gate waited, up to 720 s, a gate in progress
  the train read as pending. The reader #3278's RCA and #3287's harnesses never modelled
  is the train's classifier, shared by `bus.sh` dispatch (`merge_train.py classify`).
- **Which side moved** (`git log`, not the error text). The reader's rule,
  "only `success` is a green gate; the worst suite stands", dates from `9262e6f43`
  (2026-10-22, ci-layout P2b U9a). The producer moved three times: `fa921fd59`
  (2026-11-05 20:29Z, C3: an edit run beside an unfinished code run fails at once),
  `cc100c275` (#3276, 2026-11-07 04:47Z, the wait restored, bounded), `52f9fc5b3` (#3287,
  12:47Z, at once again, no bound). `git log --since=2026-11-04 -S'def classify(' -- tools/audit/seat/merge_train.py`
  returns 0 commits. The producer's meaning of a failed `gate` changed; the
  reader was not told.
- **Process state: (c).** Section 2.
- **Cost test: the harness passes** (standing cost 0). Section 4. A structural change to
  the readers outside `classify` is proposed, not built.
- **Built.** `dev/audit/harnesses/r10_rca_gate_busy_defer_4.py` and its fixture
  `r10_rca_gate_busy_defer_4.json`: the recorded listings of the three evidence heads,
  cut at the instant their edit gate concluded, through a chosen `merge_train.py`.

## 1. The cause, reproduced

### The evidence, read through the API

#3293 head `fefaa492`. Both runs were created 21:04:55Z. Edit run 42414123334: `gate` job
21:07:26Z to 21:07:57Z, `failure`; its log (read through `merge_train.py job-log`) says
`programs restored from dee8b413...` and ends
`FAIL run(s) [42414123291] at this head are still being judged; their gate decides`, so the
gate ran the tree that carries #3287. Code run 42414123291 was `in_progress` with its
`governance / instrument-self-tests` job unfinished at 21:07:17Z and still at 21:20Z.
#3267 `cc6ee11f` (edit gate failed 21:00:29Z, code run 42413349469 in progress) and #3268
`64fe84b2` (edit gate failed 21:00:17Z, code run 42413389218 in progress) have the same
shape. The listings are `r10_rca_gate_busy_defer_4.json`, recorded by its `record` arm.
I could not read the train's own log (it is not in the tree); the SKIP lines are the
orchestrator's, and the harness reconstructs the read from the listings.

### The listings through the train's reader

    python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_4.py replay            # this tree
    D=$(mktemp -d); git archive <ref> tools custom_components/heatpump_optimizer/manifest.json | tar -x -C $D
    python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_4.py replay --tree $D

| program | three evidence heads | settle gap (synthetic) | null controls | rc |
|---|---|---|---|---|
| origin/main `dee8b413` | RED, RED, RED (`red=['gate']`) | RED | as wanted | 1, `defects=3` |
| #3290 head `a38bd141` | WAIT, WAIT, WAIT (`pending=['gate']`) | RED | as wanted | 0, `defects=0` |
| `a38bd141` with `deferred = {GATE} if busy else set()` mutated to `set()` | RED x3 | RED | as wanted | 1, `defects=3` |

All three skips would have been prevented by #3290: at each, the code run was unfinished,
which is what its `busy` read names. **The one it would not prevent is the settle gap**:
the code run has concluded green and `gate-sweep.yml` has not yet re-run the edit gate.
`classify_at` is one read and takes no settle (its own docstring); `wait_ci` waits
`SWEEP_SETTLE_POLLS = 1` poll. The harness scene is built from the #3293 fixture by adding
a green code-run `gate` and marking the code run completed. It is synthetic, named so,
and counted apart (`settle_gap=1`); the evidence pairs hold no real instance, because
all three code runs were still in progress. Its reads are RED at main and at #3290 alike.
Whether the sweep leaves the edit gate red for longer than one poll is #3290's open
question; this record measured the gap from the census below only (median 0.9 min from
the decider's green to the re-run's green, three samples).

Null controls, all in the same run: a code run that ended `failure` reads RED at every
program (a deferral wait must not hide a real red); a head with every gate green reads
GREEN; a red non-gate required context beside a running code run reads RED. The
mutated row above is the scoring control: a copy of #3290 with its wait removed goes
back to `defects=3`, so the arm moves.

## 2. Process state: (c)

The process that existed: #3287's finder harnesses (`r10_gate_busy_defer_3.py replay`,
`r10_gate_defer_race.py`, both at both ends), its mutation proof (G1, S1-S7) and its
adversarial review. They ran, and they passed (`origin/verdict/3287`). Their unit is
`gate.judge()` and `sweep.Sweep` over recorded listings: the producer of a conclusion. No
check had a consumer of the conclusion in its unit.

The signature was in the evidence and was attributed to the defect being fixed. The
review ran `merge_train.py classify` at the PR head, which "first read RED at 16:55Z on
edit gate 128458265063" with the deferral text, and "per the brief I waited rather than
blocked". The verdict lists it as evidence, and the PR's merge made the red appear on
every head with a running code run. #3278's RCA recorded the same shape for the stale pin
("the signature of the gap was read and recorded, and it was attributed to the defect
itself").

**Why the class's barrier did not reach the instance** (`root-cause.md` section 2). The
two earlier instances are `_rca` entries with `class: null`, so no audit-class barrier is
on record for this class; what stands in as one is #3278's replay harness
(`r10_rca_gate_busy_defer_2.py`), and its unit is `gate.judge()` over recorded listings
through a chosen program copy. It asks "which program copy decides this listing, and
how". It does not ask "who reads what the decision publishes". The countermeasure
changes the unit: the replay here judges the same recorded listings through a consumer.

Ruled out: **not (d)**, as a changed precondition nobody noticed? Partly true of
`fa921fd59`, which changed what a failed `gate` means on 2026-11-05, and `A5`'s comment in
`merge_train.py` already names "R-9's defer red" as a hazard to readers; but the train's
SKIPs on this class predate #3287 (#3290's header counts 32 of 56 `ci red=['gate']` SKIPs
over 2026-11-05 to 2026-11-07, which I quote and did not re-measure), so the process
was not changed under a working check; it never had one. **Not (b)**: `fixer.md` step 8
already says a fix that changes one reader of a governance concept registers the concept
with every reader the enumeration returns, and `fix-review.md` reads every red check.
**Not (a)**: the cheaper detector, the reviewer's own `classify`, ran and printed RED.

## 3. Reach of the class

Question: which readers of a required context's conclusion can read a deferral red as
final RED. A static read of origin/main (a subagent's; I re-read `merge_pr.sh`'s `RED:` exit,
`policy_refusal`'s `POLICY_RED` and `gate_digest`'s red list myself): the deferral text appears in no
reader; `gate.py`'s `busy` is consumed by `gate.py` and its self-test alone, until #3290.

| reader | reads | reads a deferral as RED | behind #3290? |
|---|---|---|---|
| `merge_train.py classify`, `classify_at`, `Train.wait_ci` | check runs, worst `gate` suite | yes (the proof wait, the main wait, the `--overlap` log) | yes, `classify`; `wait_ci` partly |
| `merge_train.py platform_gate` (`classify --pr` cross-check) | `statusCheckRollup` | yes | no |
| `merge_train.py policy_refusal` | `statusCheckRollup`, `POLICY_RED` includes FAILURE | yes: parks the entry, `wait=False` | no |
| `bus.sh` dispatch, `cloud_dispatch.py` reviewer prompt | the `classify` exit code | yes: refuses a reviewer, tells it RC 1 is RED | through `classify` |
| `review_packet.py` `gate_digest` | check runs | yes: writes the red into the packet | no |
| `merge_pr.sh` | check runs, then `mergeStateStatus` | yes: exits 1 `RED: gate` | no |
| `ci-watch.sh` | check runs | yes: alerts `RED: gate` | no |
| `orchestrator_tick.py` `one_pr` | check runs | partly: a heuristic (`GATE_WAIT_MAX_S`, now stale, #3287's review) | no |
| `tools/ci/ruleset_cutover.py` `preconditions_gate` | newest `gate` per suite | yes: a precondition refusal, manual | no |
| `postmerge.py`, `orchestrator_tick.py` main tip | `classify --main` | no: main push runs are not edit runs | n/a |
| `body_patch.sh`, `pr-contract.yml`, `prepr.sh` | check runs less `gate` | no: `gate` is filtered out | n/a |
| `autofix_statuses.sh`, `approve_held_runs.sh`, `ci_critpath.py`, `failure_logs.sh`, `codeql-triage-poll.sh` | analytics or other names | no | n/a |

Eight rows read the deferral as final (`orchestrator_tick.py` partly), six of them outside the
`classify` family: `platform_gate`, `policy_refusal`, `gate_digest`, `merge_pr.sh`, `ci-watch.sh`
and `ruleset_cutover.py`. The harness drives `classify` only; the others are named, not
driven (Forward-carry).

## 4. Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

**The defect, measured.** Census rule: every `gate` job of a `ci.yml` run created in the
window whose log's verdict is the deferral text (`r10_gate_busy_defer_3.py census`, the
#3287 harness, run unchanged):

    python3 dev/audit/harnesses/r10_gate_busy_defer_3.py census \
      --since 2026-11-07T19:14:31Z --until 2026-11-07T21:30:00Z
    RESULT census deferral_fails=14 heads=14 per_head_max=1 held_runner_s=1844 held_ge_600=2
      resolved=3 by_bot=3 by_human=0 median_min=0.9

(19:14:31Z is #3287's merge, `5c1fa41fb`, 20:14:31+01:00; the run took 88 s.) 14 heads
carried a deferral red in 2 h 16 min; 3 resolved by the sweep (no human re-run: the
producer's repair works), after 32.3, 35.0 and 12.6 minutes counted from the edit gate's
start to the re-run's green. The other 11 had no green re-run at 21:30Z; the three evidence
heads are among them, and their code runs were still unfinished. Every one of those heads
is a head the train reads RED for the whole interval. I did not count the train's SKIPs
since the merge (its log is not in the tree): the three named by the orchestrator are
the SKIPs I read the runs of. #3290 quotes 32 of 56 `ci red=['gate']` SKIPs over 2026-11-05
to 2026-11-07. Null control: a census that read every gate would also count the
non-deferral reds; it printed `deferral_fails=14` against the log text, and the replay's
real-red scene is the control that the text and the verdict differ.

**P(recurrence).** Every edit run beside a code run that outlives it (`C3`): 14 of 14 heads
here. Three producer changes in 3 days; every future change to `gate.py` re-opens it.

**The harness's standing cost.** 0: it runs no gate and no CI lane; `replay` takes 0.055 s
wall (`time` around it). Against 11 heads reading RED for tens of minutes. The test
passes.

**What was refused.** Changing the readers outside `classify` in this pull request: they
are not this seat's files and #3290's design (the classifier waits on `busy`) fixes the
`classify` family; the rest is a design choice for that fixer and the orchestrator, not a
mechanical edit. A new CI lane that drives every reader on every `gate.py` change was
refused for cost: a reader census runs only when `gate.py` merges (4 merges to
`gate.py`, `prelude.py` and `sweep.py` since 2026-11-05).

## 5. Countermeasure

### 5.1 Built

`r10_rca_gate_busy_defer_4.py replay` (red on the defect, green on the fix, with the null
controls of section 1). It is classified in `tests/closures.json`. Standing cost: none.

### 5.2 Proposed, not built

1. **One deferral predicate for every reader**, `gate_deferred(check_run)` exported
   next to `gate.py`'s `deferral()`, so the text has one author and readers take the
   predicate (the check run's output title carries the text; #3290's self-test builds
   its fixtures that way). Readers: the table in section 3. Addresses (c): the unit
   becomes "every reader of the published conclusion".
2. **Register "a failed required gate is a verdict" in `agreement.mjs`**, with the
   readers section 3 lists, so `fixer.md` step 8 has an enumeration to run when a
   producer changes the conclusion's meaning. Owner's decision (policy-adjacent).
3. **The settle gap**: a wait keyed on the sweep's own re-run (the edit run listed
   `in_progress` again) and not a poll count. #3290's.

### 5.3 Side finding: `train.sh add --front`

`merge_train.py add <pr> <verdict> --front` exists; `train.sh add` forwards it to the
child's flag list after `--`, where it is refused as an unknown argument. The pass-through
next to `--priority` (and a pin of it in `train.sh --self-test`'s `add` argv case) belongs
to R10-HOTFIX-TRAIN-DEFER-WAIT (#3290), which owns `train.sh`; this record does not change
the file. `add <pr> --front` (re-fronting an entry already spooled, no verdict) is a
further gap: `train.sh add` needs `<verdict>`, and a verdictless form is a restructure.

## Forward-carry

- To the #3290 fixer and the orchestrator: the settle gap (section 1) and the six
  readers outside `classify`'s family in section 3. `merge_pr.sh` and `policy_refusal` act on the
  red (exit, park); `review_packet.py` and `ci-watch.sh` report it.
- To the #3290 fixer: replay this record's harness at the new head; the three evidence
  scenes must read WAIT, and the mutated-wait control must read `defects=3`.
- To the orchestrator: `orchestrator_tick.py` still describes the superseded 720 s wait
  (#3287's review carried it).
- Carry: R10-HOTFIX-TRAIN-DEFER-WAIT: `train.sh add <pr> <verdict> --front` is refused by
  `merge_train.py` as an unknown argument after `--`; add the pass-through next to
  `--priority` with an argv pin in `train.sh --self-test`, and consider a verdictless
  `add <pr> --front`.
