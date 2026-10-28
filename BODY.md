Triage batch 47 rules the one proposal with no ruling: V149 (a self-test's argv path is a closure read only CI's recording sees), as P235, DEFER to #2883's red-check root-cause route (R10-FLOW-BOARD). The triage contract keeps a root-cause countermeasure on its own route, and one verified red round in a month of closures commits does not yet clear the bar. No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`, and no roster op is owed (no ACCEPT).

## Head

`c75799e8697599b5739a377a8ecb26269b882bf9`; the file is the whole diff against `edd7e0e14e08279d0ddc53ec4fcc983570edf12a`.

## Mutation proof

`tools/audit/seat/roster_edit.py`'s triage gate is this file's only consumer. Driven with a carry text citing `triage: dev/programme/triage/s6-batch47.md#P235`:

- committed file: `triage_refusal` returns `dev/programme/triage/s6-batch47.md#P235 is not an ACCEPT ruling (DEFER)`; `ruling_verdict` returns `DEFER`.
- mutant (`Verdict: DEFER` rewritten to `Verdict: ACCEPT` in a copy): `triage_refusal` returns `None`, so the carry would land. The DEFER is what refuses it.

## Null control

At the merge base the file does not exist, and the same call returns `the triage ruling dev/programme/triage/s6-batch47.md is not on the roster branch or origin/main`.

## Figures

- 311 commits touching `tests/closures.json` since 2026-10-01, none with `argv` or `command line` in its subject: `git log origin/main --since=2026-10-01 --no-merges --format=%s -- tests/closures.json | wc -l`, then the same piped to `grep -ci 'argv\|command line'` (prints 0).
- the one verified instance, `28b0fa0f3` on #2883: `git log refs/pull/2883/head --no-merges --format='%h %s' -- tests/closures.json`.
- the argv arm at `tests/closure.py:1221-1225` and the caveat at `tools/pr/ci_predict.py:795`: `grep -n 'for argv in spawned' tests/closure.py` and `grep -n 'a data-file read is not seen' tools/pr/ci_predict.py`.
- 3.9 s per changed self-test and 913 s per single derive: the filer's measurement, quoted from `proposals.md` V149, not re-run here.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

- P235 DEFER (V149): the cheaper detector for a CI-only closures red from a self-test's argv paths is owed by `defect-root-cause.md`'s second trigger on #2883, answered in its body and by its root-cause seat. Carry: R10-FLOW-BOARD

## Friction

- handoff-instrument: contradiction: the seat's dispatch names `tools/audit/seat/handoff_push.sh` for the handoff, which opens or updates the pull request through `app_push.sh` and `gh pr edit` (lines 125, 179-216), while the same dispatch leaves every pull-request write to the orchestrator; this seat pushed the handoff and body refs only Carry: dismissed: the orchestrator runs handoff_push.sh on the pushed refs
