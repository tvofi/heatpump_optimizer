# R10-RCA-FLUSH-DISPATCH: the stamp's record flush dispatched all of `nightly.yml`

The root-cause seat for the owner-ruled hotfix (2026-11-07): the stamp dispatching a whole Nightly
run to get the one-minute `record-autofix` job. It ran beside the fix (topic
`r10-fly-stamp-flush-cost`) and not inside it (`dev/governance/roles/root-cause.md`); it edits
neither `tools/release/stamp.py` nor `.github/workflows/nightly.yml`. Times are UTC. Run data was
read from the Actions API on 2026-11-07 after 12:09Z; base is `516ad1b6b` (v7.1.5).

**Defect.** `dispatch_record_beat` (`tools/release/stamp.py`) POSTs
`actions/workflows/nightly.yml/dispatches` with `{"ref": "main"}`. `nightly.yml` has no `inputs:`
and no job reads one; `record-autofix` is its only job a `push` needs, and every other job's `if:`
admits a dispatch. A dispatch therefore runs `mutation-nightly`, four `mutation-ledger` shards,
`mutation-ledger-push`, `slow` and two `nightly-ha` lanes beside the one-minute job it was sent for.

## 1. Cause

- **Introduced whole.** `git log -S dispatch_record_beat origin/main` returns one commit,
  `6b1aa629f` (2026-10-25 21:32Z, "the stamp flushes the batched record beat ...",
  R10-FLOW-RECORD-PITCH round 2), merged as #2836 (`28800999b`, 2026-10-26). The dispatch target has
  not changed since; `3f65ea301` (2026-11-06) moved the window anchor the flush reads, not the dispatch.
- **Forced by the layout.** `record-autofix` exists only in `nightly.yml` (`git grep -n
  'record-autofix:' .github` finds the one job). No file holds a record-only job, so "dispatch the
  record beat" had no target narrower than the file, and no input to narrow the run. The cause is a
  trigger that is whole-workflow meeting a workflow whose lanes are all dispatch-admitting.
- **Known to its author.** The same commit wrote, above `FLUSH_MAX_DISPATCHES`, "each dispatch also
  runs every nightly lane" (`git log -S'also runs every nightly lane'` returns only `6b1aa629f`). The
  author priced the lanes as a reason to cap dispatches at 3, and not as a reason to avoid them.
- **Brief and code disagreed in one word.** The carry that specified the flush
  (`dev/programme/triage/s6-batch19.md:31`) says "The stamp step dispatches `record-autofix`". The
  code dispatches `nightly.yml`. The PR body says "It dispatches `nightly.yml`" and names no cost. The
  triage's cost line (`s6-batch19.md:24`) reads "No new file, no API calls, no Pi cost": it priced
  lines and calls, not runner minutes.

## 2. Process state: (a), the process did not exist

No rule, brief line or check asked what a workflow dispatch *runs*. The brief named the right job;
nothing compared that name with the target's `if:`s. Why each stage passed it:

| stage | what it did | why it passed |
|---|---|---|
| fixer self-test | `stamp.py` self-test drives `record_flush` with `dispatch=lambda: ...` | the stub replaces the only line that names the target, so it pins call order and count (`_fl.count("dispatch") == FLUSH_MAX_DISPATCHES`), never the URL or payload |
| mutation proof | mutants `stamp-3`, `stamp-4` and a spacing mutant | none touches `NIGHTLY_WORKFLOW_FILE` or the payload; the body's own "Unpinned sites" lists `dispatch_record_beat` as having "no in-tree mutant harness" |
| fix review | round 2 comment: "The flush only dispatches `nightly.yml`" | the reviewer read "only" as scoped; the question "what else runs" was nobody's step, and the review is a read of the diff against the brief, whose line said `record-autofix` |
| owner approval | review 5646765539 on the code-owned files | approval of the diff; no lane question in it |
| CI | green | nothing in CI reads dispatch call sites |

Not (b): no instruction was skipped, because none existed. Not (c): no check was wrong; the one
that bore on it (the stub) was never about the target. Not (d): `nightly.yml`'s `if:`s admitted a
dispatch before and after `6b1aa629f`. A comment held the cost; a comment is read by nobody.

## 3. Cost test

Measured 2026-11-07 (`gh api repos/<repo>/actions/workflows/nightly.yml/runs?event=workflow_dispatch&created=2026-11-07`
for the runs, `actions/runs/<id>/jobs` for each job's `completed_at - started_at`; the first run's
`started_at` is 05:52Z, the seventh's 11:50Z):

| figure | value |
|---|---|
| Nightly dispatches that day | 7 (runs 42344537787, 42346251204, 42353878060, 42357667261, 42364230438, 42367391498, 42369836867) |
| runner-minutes, all jobs | 3557 (59.3 h) |
| of which `record-autofix` | 6.2 min over the 7 runs, 0.17 % |
| cancelled job-minutes | 2201 |
| `mutation-ledger` shards cancelled | 23 of 28 (null: the first dispatch's 4 shards concluded `success`, so a shard can finish) |
| `mutation-ledger-push` | cancelled in all 7 runs, so no run's finished shards reached the ledger |

The jobs cancelled at three instants (09:38Z, 09:43Z, 12:09Z), which is the hand-cancelling; the API
does not mark it as such. All seven runs list `tvofi` as actor and triggering actor, so the API
cannot say which dispatches the stamp sent; the stamp's seven are taken from the owner ruling and the
count of dispatches is the API's. A stamp that flushes sends up to `FLUSH_MAX_DISPATCHES = 3`.

`cost(defect)`: about 508 runner-min a dispatch (3557 / 7), per flushing stamp 1 to 3 dispatches, plus
the ledger work a cancel loses (the first dispatch's shards ran 2.1 to 3.6 h; shards cancelled mid-run in runs 2 to 7).
`P(recurrence)`: every stamp whose window owes a non-record row dispatches, 7 of 7 attempts that
day, so P is 1 until the dispatch narrows. `cost(countermeasure)`: 1 s to read about 20 workflow files and
the tool files once per governance run (0.2 s measured, `check` over this tree), no runner-minutes beyond the
governance job that already runs. 0.2 s per run against 59 runner-h: the test is passed by five orders
of magnitude, so the countermeasure is built. The fix itself is the sibling fixer's.

## 4. Countermeasure, and how far the class reaches

`tools/audit/seat/dispatch_scope.py` (new, INERT with the rest of `tools/audit/`): every dispatch
call site under `tools/` and `.github/` is registered with the jobs it wants, and the target's jobs
are evaluated under a main dispatch (an unresolvable term counts as true, so a lane is never hidden).
It refuses an unregistered call site, an unwanted lane, a wanted job that does not run, a stale entry
and a declared input never sent.

**Class search.** `python3 -I tools/audit/seat/dispatch_scope.py --check` enumerates 8 call sites
(null control: its self-test plants an unregistered one and the count and refusal both appear).
They are:

| call site | target | runs more than it wants? |
|---|---|---|
| `tools/release/stamp.py` | `nightly.yml` | **yes, this defect** |
| `.github/workflows/tests.yml` (3 sites) | `ci.yml` | no: the umbrella re-dispatch is the whole umbrella by design; its jobs are gated on the prelude's workset |
| `.github/workflows/merge-main.yml` (2 hits, one an echo of the command) | `ci.yml` | no, same |
| `tools/audit/seat/ci_probe.py` (2 hits) | a parameter; `tests.yml` in its self-test | no: a probe, and `tests.yml` has no dispatch trigger |

Comment-only mentions (`nightly.yml:20`, `.claude/workflows/web-fragments.md:148`) are not call
sites. The class has one instance; it is registered as `N-dispatch-whole-workflow`, status `open`
with a detector (see below), not counted as barriered.

**Demonstration (detector on the defect, on the fix, null).**

- Red on the defect, at base: `--check` prints `REFUSE: tools/release/stamp.py: dispatching
  nightly.yml wants ['record-autofix'] but also runs ['mutation-nightly', 'mutation-ledger',
  'mutation-ledger-push', 'slow', 'nightly-ha']`, rc 1. The five names are the lanes of the 7 runs
  above (`mutation-ledger` is one matrix job, four shards).
- Green on a fix: a copy of the tree with the dispatch-admitting `if:`s in `nightly.yml` narrowed to
  `schedule` (a stand-in for the sibling fix) yields no refusal. The self-test also carries a split
  fix and an input fix (`inputs.lanes == 'all'`) green, and the input fix red when the input is
  declared and never sent, or when the registry omits it.
- Null controls: an unregistered call site, a stale entry, a wanted job that never runs on a dispatch
  and a comment-only mention each have their own arm (9 arms, 0 failed; green arms prove the red
  arms are not red for any workflow).

**Landing order.** `--check` is red on `main` until the sibling fix lands, so this change wires only
the self-test (`governance.yml`, which is green). The sibling fix, or the PR after it, adds the
one-line `--check` step to `governance.yml` and edits `WANTS`' stamp entry to the shape it chose
(`inputs` if it uses an input). Until that step exists, the detector is built and the barrier is not.

**Not claimed.** I did not check why seven stamps flushed in a day, or whether `3f65ea301`
(2026-11-06) raised the number of owed windows. Both would change P only if it were below 1.
