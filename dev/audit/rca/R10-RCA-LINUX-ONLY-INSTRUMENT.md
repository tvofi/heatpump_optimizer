# R10-RCA-LINUX-ONLY-INSTRUMENT: a /proc read in an instrument turned the macOS self-test red

Root-cause seat, `root-cause.md`. The figures are the ones measured by the orchestrator
on 2026-11-12; none is re-derived here, and estimates are marked as such.

## Defect

#3475 (`fix/r10-mutant-run-forkcap`, merge `d655c4a86e`) made
`tools/audit/seat/mutant_run.py` walk `/proc` (`os.listdir("/proc")`, reading each
`stat` and `environ`) to find and stop the processes of a timed-out mutant. macOS has no
`/proc`. On the orchestrator's macOS host `tools/pr/prepr.sh --self-test` then read
"537 passed, 5 failed" at main `19baca76`. Every pull-request update or open whose push
runs full prepr was refused. First seen about 2026-11-12 12:00Z; the hotfix group
`R10-HOTFIX-MUTANT-RUN-DARWIN` fired 12:10Z and had not merged at 15:45Z. A cloud fixer
reached a no-/proc self-test of 542 passed, 0 failed at `fdfd99d5` and was held by a
closures-recording refusal on `tests/entities.py` and 16 diff-mutant survivors.

Side effect: `open_pr.sh` closed #3508 after its row push failed on the self-test
(an opener's row push runs full prepr when the body commit carries no `Prepr:` receipt),
and #3505 probably the same way. Reopening #3508 is owed after the hotfix merges.

## Cause

The instrument was written and gated on Linux only. CI runs the instrument self-tests on
Linux runners, so #3475's own gate was green; the orchestrator's host is the only place
the push path runs prepr on Darwin, and nothing exercises that path before a merge.

## Process state

(a): the process did not exist. `grep -n macos -r .github/workflows` returns no line:
no CI job or check runs an instrument self-test, or anything, on macOS. No local lane
does either. The reviewer's and fixer's checks ran where the diff was gated (Linux), and
followed correctly; the gap is that no step stood for the host that consumes the
instrument. (c) was rejected because it needs a process that ran and missed; none ran on
Darwin at all.

## Countermeasure

PROPOSED, pending the triage ruling, not built: a standing local macOS self-test lane on
the orchestrator host, run at each main tip, running `prepr.sh --self-test` and the
instrument self-tests and posting a red to the orchestrator's board line. Owner note
2026-11-12: macOS checks run as local seats, never a paid runner. As a check it owes the
demonstration in `defect-root-cause.md`: red at `19baca76` (537 passed, 5 failed), green
once the Darwin hotfix lands (542/0 was measured at `fdfd99d5`), both runs in its report.

A second, narrower proposal from the same incident: `open_pr.sh` must not close a pull
request on a host-environment refusal of its row push.

## Cost test

    cost(countermeasure, recurring) < cost(defect) x P(recurrence)

cost(defect), measured: pull requests blocked or closed by the refusal, #3490, #3491,
#3498, #3508, and the `ci-priority-pause` group; about 3.75 h from first sighting
(12:00Z) to 15:45Z with the hotfix unmerged, and still running at that time. Estimate: a
further several hours of orchestrator and dispatch-seat time spent attributing the
refusals before the cause was read (not measured).
P(recurrence): not measured as a class. Basis for an estimate: instruments under
`tools/audit/seat/` are Linux-written and the host is macOS, so any new `/proc`,
`flock`, GNU-option or `procfs` use repeats it; this is the first instance found in
round 10.
cost(countermeasure, recurring): one `prepr.sh --self-test` per main tip on the host
(the self-test's own wall-clock is not measured here), no runner cost. The test is not
settled by these figures: the cost of the lane's run time is unmeasured, which is the
open question.

## Open questions, unmeasured

- Wall-clock of the macOS self-test per run, to price the lane.
- Whether #3505 was closed by the same path (the log was not read).
- Time to merge of `R10-HOTFIX-MUTANT-RUN-DARWIN`, so the defect's end is open.
- Class frequency of Linux-only instrument code merged this round.

## Classification

No entry in `dev/audit/config/bugclasses.json` was read for this note; no `rca` field is
cited or edited. The file sits under `dev/audit/`, a prefix of `tests/closure.py`'s
`INERT` list, so it needs no closure classification of its own.
