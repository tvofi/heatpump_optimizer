# R10-RCA-GATE-BUSY-DEFER-2, carries part: the at-once deferral red is read as final, and the settle that re-judges it loops on content reds

Root-cause seat (`dev/governance/roles/root-cause.md`), the carries part of
R10-RCA-GATE-BUSY-DEFER-2 (topic r10-rca-gate-busy-defer-p5). It addends
`dev/audit/rca/r10-gate-busy-defer-2.md` (#3278, merge `cb24224b2`), which analysed the
stale-pinned re-run. This part analyses the failure modes that #3287 (merge `5c1fa41fb`) introduced
as that class's countermeasure. Measured at origin/main `73365699a`. This seat changed nothing in
`tools/ci/` or in any reader of the gate conclusion.

The instrument is `dev/audit/harnesses/r10_gate_defer_read_final.py`, over its fixture
`r10_gate_defer_read_final.json`. The fixture covers the 13 pull requests the carries name (#3262,
#3263, #3264, #3273, #3274, #3279, #3281, #3282, #3291, #3302, #3304), plus #3296 and #3300.
Those two were picked as controls and turned out to be instances. It holds every `ci.yml` run
created on them from 2026-11-07T00:00Z to 2026-11-08T07:00Z, the jobs of every re-run or
non-success run, and the log line of every failed `gate` attempt. The fixture was recorded through
the GitHub REST API by way of the GitHub MCP tools, which this seat had in place of `gh`. The
harness header states the recording recipe and every rule below.

## Result

- **Cause 1, the reader window.** #3287 changed what a red on the required `gate` check means. A
  red can now be provisional: gate.py's `deferral()` line, published at once and re-judged later
  by `gate-sweep.yml`'s `settle`. Neither the change nor its review enumerated the code and policy
  that read that conclusion. Five readers at main still take a deferral red as final: four in code
  and one in policy. Section 4 lists them. During the window, which is the deciding run's remaining duration, those readers park, refuse or
  return the pull request.
- **Cause 2, the settle loop (a finding, carried forward, not fixed here).** `sweep.py`
  `undecided()` asks whether a red gate judged before another run's sources finished. It counts
  any non-gate job that completed after the gate started. A job re-run re-stamps the run's
  skipped jobs at the moment of the re-run, so two red gates at one head each look undecided
  beside the other's re-run. `settle` then re-runs them in turn until sweep.py's `ATTEMPT_CAP`.
  This happens even when every red is a content red that never deferred.
- **Process state: (a) for cause 1, (c) for cause 2** (section 3).
- **Carry 0 (no human re-run): covered by `5c1fa41fb`.** Under the at-once program, every deferral
  red whose deciding runs succeeded went green within 1.5 min of the decider's end. No deferral
  red was left standing after a decider that succeeded. The red window itself is unchanged: the
  deciding run's remaining duration. Figures are in section 1.
- **Countermeasure for cause 1:** the barrier carried on R10-HOTFIX-TRAIN-DEFER-WAIT by triage
  batch 136, P436: every reader of the gate conclusion goes through `merge_train.py`'s
  deferral-aware `classify_at`, plus a structural self-test. It has not landed: section 4's five raw readers stand at
  `73365699a`. The class is recorded in `dev/audit/config/bugclasses.json` as barriered only
  once it lands. Until then the `_rca` entry carries it, as `proposed`.
- **Countermeasure for cause 2:** carried to R10-HOTFIX-GATE-BUSY-DEFER, the owner of
  `tools/ci/sweep.py`, with this harness's `loop` arm as the failing test (section 6).

## 1. What happened, reproduced

    python3 dev/audit/harnesses/r10_gate_defer_read_final.py census

The census prints one row per deferral red, then RESULT lines. A deferral red is a `gate`
attempt that concluded `failure` with gate.py's `deferral()` line. Each row names the program
that published the red, read from its `programs restored from <sha>` line:

- `at-once`: that sha carries `5c1fa41fb`;
- `waiting`: it does not.

For each red the census also gives four values:

- when its deciding runs' attempts ended, and how;
- when a `gate` at the same head next concluded success, in any run;
- `red_min`, the minutes between the red and that success;
- `lag_min`, the minutes between the decider's end and that success.

| figure (RESULT name) | waiting program | at-once program (#3287) |
|---|---|---|
| deferral reds (`*_reds`) | 45 | 41 |
| heads carrying one (`*_heads`) | 25 | 18 |
| red window, median min (`*_red_min_median`) | 31.0 | 32.2 |
| red window, max min (`*_red_min_max`) | 142.8 | 54.0 |
| decider-to-green lag, max min, decider succeeded (`*_lag_min_max_decider_success`) | 0.0 | 1.5 |
| decider-to-green lag, max min, any decider (`*_lag_min_max`) | 122.2 | 35.9 |
| green attempts started by a person (`*_green_by_human`) | 15 | 6 |

Across both programs:

- 86 deferral reds (`deferral_reds`) fell on 43 heads (`heads_with_deferral`) of all 13 pull
  requests (`prs_with_deferral`).
- `residual_red=18`: deferral reds no gate at their head ever followed with a success.
- Every one of the 18 had a decider that was cancelled or failed
  (`residual_red_decider_success=0`). The head was red or superseded anyway.
- **Null control.** 276 gate failures were not deferrals (`non_deferral_reds`): CodeQL
  cancellations, `tests / closures`, `pr-contract`, `tests / mutation`. None is scored as a
  deferral. A census that keyed on `conclusion == failure` alone would have counted all 362.

Reading the figures:

- **Carry 0's measure.**
  - Deferral reds per head that carries one: 86 / 43 = 2.0.
  - Under #3287 the sweep greens a head within 1.5 min of its decider's success, and in 0.0 min
    when the decider's own gate is the green.
  - The six person-started greens under the at-once program are of two kinds. Four (#3262
    c95c3b4b and d17e43cf, #3264 56dd13aa twice) are a hand re-run at lag 0.0, racing the sweep.
    Two (#3262 d17e43cf) follow a decider that was cancelled or failed, which the sweep rightly
    leaves red.
  - The waiting program's 122.2 min (#3274 97786d25) and 73.2 min (#3279 0251fffb) waits are
    deciders that were cancelled and re-run by hand. Those are what carry 0 described.
- **The window did not grow; its readers did not change.** #3287 shortened no red: the at-once
  and waiting medians (32.2 and 31.0 min) are both the deciding code run's remaining duration.
  What #3287 changed is that a deferral now always publishes a red, and publishes it at the
  start of that window. Before it, a gate waited up to `GATE_WAIT_MAX_S` and passed if the
  decider finished inside the bound. So every reader that took a red as final now meets one on
  every deferral.
- **Triage P436's instances, re-read here.** All six PRs it names carry deferral reds in the
  census. Its #3264 review case is the row `#3264 b3f2169d run 42436586762#1`: red 02:01:18Z,
  green 02:01:51Z.
  - Its 55-PR denominator is cited, not re-measured: this seat had no `gh` for the run listing
    of a whole day.
  - So 13 of 13 here is a sample selected by instance, not a rate.
- **#3278's own detector reads #3287's design as a defect.**
  - `replay --ci <export>` of `r10_rca_gate_busy_defer_2.py` exits 0 at `812bb8747` and 1 at
    `73365699a`, with all three c3 scenes `C3-AT-ONCE`. Section 3 gives the commands.
  - #3278's document lists that arm as the re-proof for any gate change.
  - #3287's head did not contain #3278: `git merge-base --is-ancestor cb24224b2 5c1fa41fb^2`
    exits 1. #3278 merged at 19:07:48Z and #3287 at 19:14:31Z.
  - The open branch `handoff-wip/r10-hotfix-gate-busy-defer-p5` retires `C3-AT-ONCE` as #3287's
    design.
- **Stale pins after #3287.**
  - `stale_pin_reds_after_fix=6`: waiting-program deferral reds published after `5c1fa41fb`
    merged.
  - `stale_pin_reruns_after_fix=2` of them were re-run attempts: #3291 d5f8f410, attempts 3 of
    two runs, 20:18Z.
  - This is #3278's §5.2 shape, measured on this sample. The other four are pull requests whose
    base predated #3287.

## 2. The causes, named

**Cause 1.** `gate.py`'s `deferral()` red became a routine, provisional verdict when #3287 deleted
the bounded wait:

    if ok or now() - t0 + POLL_S > lag_bound(why):   # a deferral's bound is 0: published at once

Its re-judging lives in `sweep.py` `settle()`. The meaning changed in the writer; every reader of
the required `gate` context stayed as it was. #3290 (merge `48af0864a`, 7 h after #3287) taught
`merge_train.py` `classify_at` (`gate_busy` and `sweep_settling`) and the instruments that call it
to read a deferral as pending. It did not reach the readers listed in section 4.

**Cause 2.** In `sweep.py` `undecided(gate, run_id, others)`, the first arm is

    any(j.get("name") != "gate" and (j.get("completed_at") or "~") > t0 for j in jobs)

A job re-run (`POST actions/jobs/<id>/rerun`, which `settle` uses) starts a new attempt. That
attempt lists the run's skipped jobs (`kernel-points`, `governance` on an edit run;
`tests / mutation-pins` on a code run) with `started_at` and `completed_at` at the re-run's
moment. The recorded jobs show it. Edit run 42419764212's attempt 16 lists `kernel-points`
skipped at 23:44:53Z, three seconds before its gate started at 23:44:56Z. Its real jobs had
finished by 22:16:56Z.

So after run A's gate is re-run, run B's red gate has "a job that finished after it started", and
the sweep fired by A's completion re-runs B. B's completion then re-runs A. The third arm (a
higher-id run's gate started while this one judged) compounds it once the re-run gates overlap.
`must_rerun`'s cap is the only stop: `ATTEMPT_CAP = 45`, so attempt 44.

`settle` never asks whether the red was a deferral. A content red ("FAIL tests / closures:
failure (this run)") is re-run just the same.

## 3. Process state

**Cause 1: (a), the process did not exist.** No step asks a change to a check's writer to
enumerate the readers of the conclusion whose meaning it changes:

- `dev/governance/roles/fixer.md` step 8 at `5c1fa41fb^1`: "A fix that changes one reader of a
  governance concept registers the concept in `agreement.mjs` with every reader the enumeration
  returns". It is worded for a change to a reader. #3287 changed the writer.
- `tools/policy/agreement.mjs` registers no gate-conclusion or deferral concept, at `5c1fa41fb`
  or at `73365699a`.
- Step 8's class enumeration was run. The rule #3287's body names is the `itertools.product`
  census in `tools/ci/sweep_selftest.py`, eight orderings of a two-run pair. So the class was
  taken to be the writer's orderings.
- The fixer brief (`dispatch/fixer-r10-gate-busy-defer-3`, commit 1338ae7f1) scoped the fix to
  the writer: "every deferring gate at that head is re-judged or re-run without a human, through
  the existing Gate sweep path".
- The round-2 review brief (`dispatch/reviewer-rev-3287`, commit 214275ffc) asked four questions,
  all about the writer. It told the reviewer itself to wait a deferral red out ("a gate red that
  is only an edit-run deferral … wait up to 60 minutes … do not block on it"). So the one reader
  the chain knew about was patched by briefing text, not code.
- The readers belonged to a parallel group, R10-HOTFIX-TRAIN-DEFER-WAIT (#3290, first commit
  `9be54d320` at 14:22Z, before #3287 opened). The roster put no `after` edge between the two
  groups, and #3287 merged first.

Why not (b) or (c): nothing was skipped, and no reader-enumeration rule ran and failed. The rule
that exists cannot fire on a writer change.

**Contributing, (d)-shaped: preconditions changed beneath #3287.** #3278's replay arm, the
re-proof its document prescribes for any gate change, landed 7 min before #3287, and #3287's
head did not contain it. At main the arm exits 1 on #3287's design. The commands:

    D=$(mktemp -d); for c in 812bb8747 73365699a; do mkdir -p $D/$c
      git archive $c tools/ci tools/pr | tar -x -C $D/$c
      python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_2.py replay --ci $D/$c/tools/ci >/dev/null; echo "$c rc=$?"; done

They print `812bb8747 rc=0` and `73365699a rc=1`. The arm is not a CI check, so nothing ran it at
the merge.

**Cause 2: (c), the process was followed and did not produce the intended result.** #3287 ran
three checks:

- the step-8 census in `sweep_selftest.py`;
- the race harness `dev/audit/harnesses/r10_gate_defer_race.py`, whose fake jobs API #3287 taught
  to stamp `completed_at` for `settle`;
- a docstring argument that "nothing loops".

All three ran over modelled job listings. None modelled GitHub re-stamping a re-run attempt's
skipped jobs, and none put a content red at two runs of one head. The real listing breaks the
docstring's argument.

## 4. How far the class reaches: the readers of the gate conclusion at `73365699a`

No in-tree instrument enumerates the readers of the `gate` conclusion. The enumeration below
came from a search for sites that compare a check run's conclusion to failure:

    git ls-files tools .github | grep -E '\.(py|sh|mjs|yml)$' | grep -vE 'selftest|self_test|_test\.py|fixtures/' |
      xargs grep -nE 'conclusion.{0,60}(failure|FAILURE|RED\b)|(failure|FAILURE).{0,40}conclusion|in (POLICY_RED|RED)\b|mt\.classify\('

It returns 56 (file, function) sites. Each was read, along with the role contracts that state a
reading rule. The ones that read the `gate` context are:

| reader | reads a deferral red as | disposition |
|---|---|---|
| `merge_train.py` `classify_cmd` / `Train.classify_at`, and the merge step's gate-red wait | pending while `gate_busy` names a run, then `SWEEP_SETTLE_POLLS` | already guarded (#3290) |
| `proof_watch.py` (`classify_at`), `ci-watch.sh` and `bus.sh` dispatch (`merge_train.py classify`), `postmerge.py`, `cloud_dispatch.py`'s reviewer wait | pending (through `classify`) | already guarded (#3290) |
| `merge_train.py` `Train.policy_refusal` (the BRANCH-POLICY park) | **final**: `POLICY_RED` includes `FAILURE`, and the car parks | open: P436's barrier |
| `orchestrator_tick.py` `one_pr` and `main` (`mt.classify` with no `busy`) | **final**, and it prints a hand-rerun instruction citing the deleted `GATE_WAIT_MAX_S` wait | open: P436's barrier |
| `review_packet.py` `gate_digest` (the `required-red` refusal) | **final** | open: P436's barrier |
| `merge_pr.sh`, the latest-check red read | **final** until mergeStateStatus answers | open: P436's barrier |
| `dev/governance/roles/nudge.md` step 15: "A conclusion of failure returns that pull request to its original fixer this turn" | **final** (a policy reader) | open: policy, the owner's |
| `prepr.sh`, `body_patch.sh`, `pr-contract.yml` | filter `.name != "gate"` | not a reader |

The remaining sites read other checks (CodeQL, stamp, ruleset, ledger and mutation lanes) or are
self-test fixtures.

## 5. Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`
(`dev/governance/rules/defect-root-cause.md`).

**Cause 1.**
- **Frequency.** 41 at-once deferral reds on 18 heads of 13 sampled pull requests in the 11.8 h
  from `5c1fa41fb`'s merge to 07:00Z. Every one is a window in which a raw reader can act.
- **Cost per occurrence.** A raw reader's action:
  - a BRANCH-POLICY park, about one train cycle each, per P436's #3264 instance;
  - a packet's `required-red` refusal (a dispatch not made);
  - an orchestrator tick advising a hand re-run (four person-started greens at lag 0.0 here);
  - a nudge-step-15 return to the fixer.
  - The hand re-run also has a cost. P436 records one that cancelled #3262's code run; that is
    cited, not re-measured here.
- **Countermeasure cost.** One predicate already in the tree (`classify_at`), reused by four code
  readers, plus one structural self-test, per P436's estimate. No new workflow and no runner. The
  standing cost is one `gate_busy` run listing per read, which `classify` already makes.
- **Passes.** A one-time route through an existing predicate, against a reader acting wrongly on
  some of 41 windows per half day.

**Cause 2.**
- **Measured on the sample.**
  - `bot_reran_content_reds=257`: content reds on runs the bot re-ran last, re-run on attempts
    2 to 44.
  - `bot_reran_content_red_gate_min=159`: gate-job minutes.
  - Spread over 6 pull requests (`bot_reran_content_red_prs`): #3274 129, #3302 59, #3296 39,
    #3304 26 (still looping at the read), #3264 3, #3262 1.
  - Each re-run also starts one gate-sweep run, whose `settle` polls up to `POLL_WAIT` 600 s on a
    runner. That is not measured here.
- **Second cost.** A run left at attempt 44 can never be re-run by the sweep again
  (`must_rerun`): #3274's three runs at 4f8ab965.
- **Countermeasure cost.** One predicate in `settle`: re-run only a gate whose latest red is a
  deferral, or have `undecided()` drop `skipped` jobs. Each is a few lines and one fixture case.
- **Passes** on these numbers alone.

## 6. Countermeasure

**Cause 1, the barrier: not built here, owned by R10-HOTFIX-TRAIN-DEFER-WAIT** (P436's carry).
- Every reader in section 4's open rows reads the `gate` context through `classify_at`.
- A structural self-test fails on any other code path that compares that context's conclusion to
  `failure`.
- The failing test is the #3264 review instance: red 02:01:18Z, sibling green 02:01:51Z (the
  census row above).
- The null control: a gate red naming no busy run is red at once.
- Section 4's search is a starting enumeration for that self-test. It is not the self-test.

The `nudge.md` step 15 reader is policy. Its change is the owner's, so it is routed to the
orchestrator rather than edited.

**Cause 1, the process gap: proposed, not built.** Extend fixer step 8's reader rule to a writer.
A fix that changes what a check's conclusion means would enumerate that conclusion's readers and
register the concept in `agreement.mjs`. The change is policy (`fixer.md`), so it waits for the
owner. Its cost is one sentence and one concept entry. It would have put the four code readers
and the nudge step in front of #3287's review.

**Cause 2: carried to R10-HOTFIX-GATE-BUSY-DEFER, the owner of `tools/ci/sweep.py`.** The
detector is this harness's `loop` arm. It replays #3274's recorded loop: one code and two edit
runs at 4f8ab965, every gate red on `tests / closures`. The replay runs through a given
`sweep.undecided()`:

    python3 -I dev/audit/harnesses/r10_gate_defer_read_final.py loop [--ci DIR]

- At `73365699a` it prints `reruns=129 predicted_listed=129`: every actual re-run is predicted
  from the listing GitHub served.
- It prints `predicted_without_skipped=38` with every `skipped` job dropped. That is the null
  control: the re-stamped skipped jobs carry 91 of the 129.
- The remaining 38 come from the third arm's overlap, which only the loop itself produces.
- `5c1fa41fb`'s copy and `handoff-wip/r10-hotfix-gate-busy-defer-p5`'s copy (`d23377e1d`) print
  the same.

The fix is the owner's choice between two options:
- `settle` re-runs only a deferral red (the check run's log line, which gate.py writes);
- `undecided()` ignores `skipped` jobs, and `settle` ignores another run's gate overlap that its
  own re-run caused.

Failing test first: the `loop` arm reads `predicted_listed=0` for these content reds. Null
control: a deferral red at one head is still re-run once its decider ends (the census's at-once
rows).

## 7. Carries

- **To R10-HOTFIX-GATE-BUSY-DEFER (sweep.py):** cause 2, sections 2, 5 and 6. Every open pull
  request whose runs sit at attempt 44 needs a fresh dispatched run, not a re-run.
- **To R10-HOTFIX-TRAIN-DEFER-WAIT (P436's barrier):** section 4's open rows, and the #3264
  failing case.
- **To the orchestrator:** the `nudge.md` step 15 reader and the fixer step 8 extension, both
  policy. Also retire the hand re-run: the sweep greens a successful decider's head within
  1.5 min, and a person's re-run raced it four times here.
- **To `dev/audit/config/bugclasses.json`, once P436's barrier lands:** the class "a provisional
  gate red read as final", status barriered, citing this document.

## 8. Not covered

- The 55-PR denominator, and so a per-PR rate: not re-measured (no `gh` here). The 13 pull
  requests are the carries' instances.
- #3304's runs kept re-running during the recording. Its last recorded attempts are 8, 9 and 13
  (`refetched_at_end` in the fixture); later ones are not recorded.
- Whether GitHub's required-check evaluation takes the latest `gate` check run at the head is
  assumed from the merges it allowed. #3282 merged at 11:50:54Z, after its code gate's green at
  11:48:41Z, with its edit gate still red.
