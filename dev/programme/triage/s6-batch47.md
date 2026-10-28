# Proposal triage, session s8, batch 47 (P235)

One entry: V149, written by the orchestrator s8 on 2026-10-28 from fixer s8's root-cause
note on #2883, quoted from `proposals.md` as it stands. Every other id in `proposals.md` up to
V148 has a ruling on `origin/main` (batches 35-44) or in batches 45 (#2900, P227-P231) and 46
(#2902, P232-P234). Facts read at origin/main `edd7e0e14`; roster at `origin/main`'s
`dev/programme/rosters/wave-r10-groups.json`.

## P235: a self-test's argv path is a closure read that only CI's recording sees

Verdict: DEFER -- owned by the red-check root-cause route on #2883 (**R10-FLOW-BOARD**,
`resume.stage` `in-progress`): `defect-root-cause.md`'s second trigger, answered in that pull
request's body and by its own root-cause seat. The triage contract keeps such a countermeasure
on its route: "A defect countermeasure policy already requires (a root-cause countermeasure, a
carry for a red check, a finding's fix) is not a proposal and keeps its route"
(`proposal-triage.md`). What would change the answer: that seat's cost test recording that no
countermeasure is worth building, *and* a further instance on another pull request; the class
would then be a measured process proposal with no owner, and comes back here.

Source: `proposals.md` V149 (fixer s8 (#2883) SEAT-OWED root-cause, routed by orchestrator s8,
2026-10-28).

Instances: one verified; the filing counts two, both on #2883.
- `git log refs/pull/2883/head --no-merges -- tests/closures.json`: `28b0fa0f3` "closures:
  entities.py reads the two roster paths roster_lib.blob_at's self-test puts on argv (#2883
  review 3)" -- a CI-only `tests / closures` red, repaired in review round 3.
- The filing's other instance (#2883's earlier `INERT READS UNDER-APPROXIMATED: tests/entities.py:
  tools/audit/merge_throughput.py`) was repaired in `d218ef378`, which edits `tests/closure.py`
  (`git log refs/pull/2883/head -S'merge_throughput.py' -- tests/closure.py tests/closures.json`);
  nothing in that commit shows it was the argv arm, so it is not counted here.
- Programme-wide: of `git log origin/main --since=2026-10-01 --no-merges -- tests/closures.json`
  (311 commits), none names an argv or command-line read in its subject (`grep -i 'argv\|command
  line'`); the closures repairs of the month are INERT READS, which `ci_predict --apply-inert`
  already writes before the push.
- The mechanism is as filed: `tests/closure.py:1221-1225` (`for argv in spawned:`) adds every
  existing repo path on a child's command line to the script's reads, and
  `tools/pr/ci_predict.py:795` prints its green line with the caveat "(a data-file read is not
  seen)".

Cost: a new recording arm in `ci_predict.py` or `prepr.sh` (a hot file; R10-FLOW-JIDOKA lists it)
that runs each changed file's self-test under the closure recorder and diffs its reads against
`tests/closures.json`, with its self-test and a mutant; the filer measures 3.9 s per changed
self-test at run time. An existing, costlier route already covers the case on demand:
`PREPR_RECORD_CLOSURES=1` records the scoped closures on a non-Linux seat (`prepr.sh:672-675`),
and Python lanes record soundly on Darwin through `sys.addaudithook` (`ci-autofix.md`); it was
made opt-in by `2b84db687` because it costs 10-25 minutes per handoff.

Binding: route, then frequency. The filing is a root-cause note on a red check, so the cause,
the process state and the cheaper detector's cost test belong to a root-cause seat beside
#2883's fix (`root-cause.md`), which can name a countermeasure or record that none pays; a triage
ACCEPT here would decide that seat's answer before it is measured. On the numbers alone the trade
is not yet clear either: one verified red round in a month of 311 closures commits, against a new
arm in a hot instrument.
