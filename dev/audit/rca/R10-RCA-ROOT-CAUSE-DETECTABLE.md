# R10-RCA-ROOT-CAUSE-DETECTABLE: a red check the body did not answer, and the seat mutant self-tests no local path ran (#2875, #2865)

The root-cause record for the recurring-friction key `root-cause-detectable`
(#2875) and for the red-check trigger on #2865 (Carry 5 of this group), which
`dev/governance/roles/root-cause.md` and `dev/governance/rules/defect-root-cause.md`
owe. It lands one countermeasure, in `tools/pr/ci_predict.py`.

**Merge base and window.** Measured on 2026-11-06 at `origin/main`
`7e8939d38`. Window `v7.0.4..origin/main`, tag `v7.0.4` =
`b448d26063cdb56aef915ceb604b807a885f9d71`. Instrument:
`node tools/policy/policy_lint.mjs --stats --since v7.0.4`, 517 merged pull
requests, 450 carrying a parsable verdict. Nothing is carried from earlier
records: the figures in `R10-RCA-FRICTION-RESIDUE.md` (3 PRs, 5.2 days) are a
control, not a source.

## 1. The count, and the 12 instances

`root-cause-detectable` reads **12 PRs / 12 entries** (threshold 3), the
sibling words `root-cause-unrecorded` 5 / 6 and `root-cause-unanswered` 5 / 5.
Twelve pull requests are named by the first line of a `Fix review: blocked <sha>
root-cause-detectable:` comment (gathered by comment search over the window's
merge list, then each first line read; the count equals the histogram's):

| check that was red | PRs | the cheaper detector the reviewer named |
|---|---|---|
| `governance / instrument-self-tests` | #2664, #2870, #3049, #3200, #3221 | `ref_privacy.py --check` (#2664); `selftest_wiring.py --check` (#2870); the PR's own `gh_calls` self-test (#3049); `r10_ledger_mutants.py` T3 anchor (#3200); the line for #3221 names the job only |
| `tests / closures` family | #2869 (`closure.py` selftest, "about three seconds"), #2883 (INERT READS), #3206 (names the job only) | `python3 tests/closure.py` selftest / the scoped gate |
| `tests / fast` | #3051, #3066 (`harness_headers.py`, 0.7 s via `inline_scan`), #2873 (`card.mjs`, 118 s) | `tests/harness_headers.py`; `node tests/card.mjs` |
| `pr-contract` | #2841 | `tools/pr/preflight.sh`, seconds |

Control: a class word with no instance in the window (`version`) counts 0 by the
same search, and the search reproduces the histogram's 12 exactly.

## 2. Named cause

There are two causes under one word, and they are separable by what the
reviewer wrote.

**Cause A (nine of twelve): a CI job that no local path predicts.**
`tools/pr/ci_predict.py` is the local predictor `prepr.sh` runs for the CI
jobs a seat cannot see. Its `instrument` arm predicted two of the dozens of
checks `governance / instrument-self-tests` runs: `ref_privacy.py --check`
(`privacy_preds`) and `selftest_wiring.py --check` (`wiring_preds`). Each
instance in the instrument row is the next check of the same job that the arm
does not run. #2664 and #2870 are the two it now predicts; both were added
after the instance that exposed them (`R10-RCA-2671-WAVE-SCRIPT.md`
countermeasure B, #2870's repair). #3200 and #2865 are a third: the seat
mutant drivers.

**Cause B (the body column, all twelve): the answer is owed before the red is
knowable.** The body is written and pushed at handoff, before the pull request
exists and before CI has run; the trigger is enforced by the reviewer reading
the PR's checks afterwards. A seat that has no local detector for a red check
cannot answer it in the body, so every instance of Cause A is also an instance
of B. The instances whose detector *did* exist locally (#2841, #2869, #3051,
#3066: `preflight.sh`, `closure.py`, `harness_headers.py`) are cause B alone:
the detector ran in the scoped gate or in `prepr.sh`, was not run, or its red
was not carried into `## Red checks`. This record does not establish which of
the three for each; the reviewer lines do not say.

## 3. #2865, reproduced: why the mutant self-tests are Cause A

`#2865` (R10-ORCH-DISPATCH-REG) went red on `governance / instrument-self-tests`
(run 40368808901, job 121733907279: `FAIL T3_review_owed_silent: anchor occurs
once in tools/audit/seat/orchestrator_tick.py`) because an edit to a planted
file moved a seat mutant's anchor. At this base:

- `governance.yml` runs four drivers, `r10_roster_ops_mutants.py`,
  `r10_stamp_round_mutants.py`, `r10_ledger_mutants.py` and
  `r10_mandate_guard_mutants.py`, each with `--self-test`.
- Each driver refuses to start when a plant's anchor no longer occurs exactly
  once in its target (the `ck(... anchor occurs once ...)` line,
  `r10_ledger_mutants.py:128`). The plants live in files other than the driver,
  so an ordinary edit to `ledger.py`, `orchestrator_tick.py`, `cloud_relay.sh`,
  `stamp.py` or the roster library can break a driver the author never touched.
- `tools/pr/prepr.sh` calls none of them, and `ci_predict.py` predicted none:
  `wiring_preds` and `privacy_preds` were the whole `instrument` arm.

Timings measured here, one run each: roster_ops 1.13 s, stamp_round 0.33 s,
ledger 0.71 s, mandate_guard 0.10 s; **2.28 s for the four**.

**Why it is a reach problem and not a rule problem.** The mutants are, by
design, hand mutants of *other* files (`r10_ledger_mutants.py` docstring: "each
plant is one exact one-occurrence replacement in one of the files the ledger
change touched"). A PR that edits `orchestrator_tick.py` has no reason to open
`r10_ledger_mutants.py`. The instruments guide lists the drivers; nothing
connects a changed target to the driver that plants into it.

## 4. Process state

**(c): the process was followed and did not produce the intended result.**
`prepr.sh` step 6d runs `ci_predict.py` precisely to predict the jobs CI runs
that a seat cannot; it was run, it predicted green, and `instrument-self-tests`
went red. The arm's *unit* was two named checks of a job that has dozens
(`governance.yml` lines 767-796 alone run four mutant drivers); it was
extended once per instance, each time to the one check that had just failed.
Not (a): the predictor existed for this job. Not (b): #2865's body ran
`prepr.sh` and named the cheaper detector. Not (d): nothing changed
underneath the arm; its coverage of the job was always partial.

The reviewer's own disposition on #2865 was to route the countermeasure to the
orchestrator's root-cause routing, which never happened; this is that record.

## 5. How far the class reaches

The class is "a job with N checks, a predictor with k < N of them".
`governance / instrument-self-tests` is the measured case (5 of the 12). The
same job runs other `--self-test` lines, for example `gh_calls`, `ledger`,
`orchestrator_tick`, `plan_page`, `pr_args`, `pr_cap`, `open_driver`,
`proof_watch`, `prune_refs`: **a PR that edits one of those files fails its own
self-test**, as #3049 did. That wider arm (run the `--self-test` of every wired
instrument the diff changes) is not built here: of the 12 instances it would
have caught one beyond those now predicted (#3049), its standing cost per run
is unmeasured, and one instance does not make a class. It is recorded as the
next step if a second PR (not #3049) fails its own instrument self-test in a
window after this lands. The `closures` family (3 PRs) and `fast` (3 PRs) rows
are the other jobs and are not this record's: the detectors those reviewers
name are in the scoped gate.

## 6. Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, wall-clock,
per occurrence.

- **Defect cost.** `R10-RCA-FRICTION-RESIDUE.md` section 2 measured the median
  time from a `root-cause-detectable` block to the next verdict at **181 min**
  (3 PRs, `v7.0.4` at its base). Not re-measured: the per-PR fetch it used is
  not re-run here; the figure is labelled as that record's.
- **P(recurrence).** The mutant-driver shape has two instances in the window
  (#2865 and #3200); 2 of 517 merged pull requests. The class word as a
  whole: 12 of 450 verdict-carrying PRs, 2.7 %.
- **Standing cost.** The new arm runs a driver only when the diff touches a
  file the driver quotes as a plant target (or the driver itself): at most
  2.28 s, only for such a diff; every other diff pays a file read and a regex.
  Even charged to every one of the 517 merges the ceiling is 517 x 2.28 s =
  19.6 min, against 2 x 181 min = 362 min of defect for the two instances
  alone.

The test passes with a margin of about 18x at its worst-case ceiling, so the
countermeasure is built.

## 7. Countermeasure (landed): the `mutants` arm

`tools/pr/ci_predict.py`: `mutant_preds(root, changed)`, registered in `ARMS`
as `mutants` and called from `predict`. It reads which drivers
`governance.yml` runs, takes each driver's plant targets as the repository
paths its source quotes (plus itself), and runs `--self-test` only for a driver
with a target in the diff. A red is `("instrument", "SEAT MUTANT SELF-TEST
<driver>: <first FAIL line>")`, the job the CI red is filed under.

Addresses state **(c)**: it changes the unit of the arm (a driver whose target
moved), not the arm count.

**Demonstration, both runs.** `python3 tools/pr/ci_predict.py --self-test`
carries three new rows over a planted driver and target:

```
  ok   a planted target edited so its anchor is gone is predicted red
  ok   the same target with its anchor intact is predicted green
  ok   null control: a diff touching no planted target runs no driver (the anchor is gone, no red)
```

Against the real tree at this base, with `orchestrator_tick.py` in the
changed set: intact tree -> `[]`; with `r10_ledger_mutants.py`'s own T-plant
anchor duplicated into `orchestrator_tick.py` ->
`[('instrument', 'SEAT MUTANT SELF-TEST r10_ledger_mutants.py: FAIL T1_unkinded_printed: the mutant parses')]`;
changed set `{README.md}` -> `[]`. The file was restored byte for byte
afterwards.

**Mutation proof.** With the driver-selection line replaced by `if False:`
(always run), the null-control row fails and the self-test is red; the file
was restored (`cmp` against a copy).

**Not claimed.** The arm is not a plant at the `predict` call site (the
`ARMS` tuple and the `arms` table carry it, the self-test drives the helper).
The follow-up row in the call-site plant table is the standing shape
(`#1591`'s lesson); it is not added here, so a deleted `mutants` entry in
`arms` would leave the helper green. That gap is stated, not hidden.

## 8. Not established here

- Which of #2841, #2869, #3051, #3066 were failures to run a local detector
  and which were failures to write the result into `## Red checks`: the
  reviewer lines do not say.
- Cause B has no countermeasure recorded here beyond the arm: a body cannot
  answer a red it cannot see, and writing a guess into `## Red checks` would be
  the false-answer defect `defect-root-cause.md` enforcement exists to prevent.
- #3221 and #3206 name only the job; their cheaper detector is not stated.
