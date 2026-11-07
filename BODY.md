Fold the 2026-11-06 out-of-tree sweep changes into the tracked sweep scripts the owner ruling names, instead of beside them. Repair round for the `architecture-unsound` block on `verdict/3267`.

Owner ruling (tvofi 2026-11-06), verbatim: "There should already be tracked sweep templates/scripts for these, update them if needed".

The tracked counterparts at the merge base are `tools/audit/seat/beat_jobs.py` (the beat's job rows, run by `beatd.py` from `beatd.jobs.json`), `sweep_template.md` and `sweep_render.py`. The previous body said only `sweep_render.py` and `sweep_template.md` existed. That was false, and this body withdraws it. This head updates those scripts:

- `beat_jobs.py` gains two rows: `gantt`, which runs `sweep_gantt.py` against the plan `plan-beat` writes, and `verdict-audit`, which runs `verdict_audit.py`. Both rows are also added to `beatd.jobs.json`, every 1800 s, in class `orch-checkout` because both fetch in the orchestrator checkout. Their `GANTT-SLIP`/`GANTT-BASELINE` and `UNHELD` lines go to `S/digest/`, the digest the orchestrator's wake already reads. A failed run is `UNREADABLE`, never its partial output.
- `plan-beat` gains the `PLAN MOVED` compare. After a successful `state_docs.py --push --mirror`, a mirrored `PLAN.html` whose sha256 differs from the last pass's prints `plan-beat: PLAN MOVED <mirror>/PLAN.html re-rendered; republish owed`, once per change.
- `roster-drain` takes the differences of the deleted second drain. It now passes `--mark` and reads done or refused from the exact line `roster_queue.py` rewrites (`#done <op>` / `#refused <op>`). An op that was neither reported nor marked is `roster: UNRUN` and stays pending: before, it was marked done as `FAILED ... no report line`. A refusal by a worktree that is on no origin ref (an earlier refusal's leftover, from `roster_edit.py`) stays pending under one `roster: CASCADE` line, which names the worktree to remove.
- Deleted: `sweep_runner.sh`, `sweep_runner_selftest.py`, `roster_drain.py`, their instrument pages, `INSTRUMENTS.md` lines and `tests/closures.json` entries, and their `governance.yml` lines. That includes the double run of the runner self-test. The step now runs only the `sweep_gantt.py` and `verdict_audit.py` self-tests.
- `sweep_template.md`: (4b+) is gone, and so is the `roster_drain.py` sentence in (1b). (4b) stays the one owner of the replan and state-docs push, and now also says what `PLAN MOVED` and `GANTT-SLIP` owe. (4c) names the `verdict-audit` row's `UNHELD` lines. `sweep_gantt.py` and `verdict_audit.py` now name the beat row as their caller. A false `--fired-ledger` flag claim in `sweep_gantt.py`'s docstring and instrument page is corrected: the flag is `--fired`.

Alternatives that lost: keeping `sweep_runner.sh` as a manual path beside the beat would leave two owners of `state_docs.py --push` on one state ref, with nothing to serialise them (the verdict's finding). Keeping `roster_drain.py`'s queue-rewriting `reconcile` would be a second drain with a second marking scheme. The beat row's append-only queue and occurrence keys stay, and `roster_queue.py`'s own `--mark` becomes the one source of the exact-line mark. `roster_drain.py`'s `ROSTER-SKIPPED` for a line holding ` #` is not ported: `roster_queue.py`'s LINE GRAMMAR defines ` #` as a comment, so that skip would contradict the parser's own owner.

## Head

fc5a4f8d1b08124107354ea2a5c2d71f930261bc, the `handoff/r10-sweep-template-sync` tip this body ships with: `fix/r10-sweep-template-sync` at `61f1ec71`, with `origin/main` merged at `294a880d`, then the three repair commits. All figures below were measured on that tree. `origin/main` had not moved since that merge when prepr ran (`git rev-list --count HEAD..origin/main` printed 0), so no second prepr run was needed.

## Mutation proof

The in-tree mutant harness is `beat_jobs_selftest.py` `MUTANTS`, run by `python3 -I tools/audit/seat/beat_jobs.py --self-test`. Each mutant plants one edit in a temp copy and names the case that must fail. Ten mutants are new in this diff, all killed:
- `roster_unrun_marked` (drop the UNRUN branch) and `roster_mark_dropped` (drop `--mark`) are killed by `roster-drain: an op neither reported nor marked is UNRUN and stays pending`.
- `roster_cascade_marked` is killed by `roster-drain: a refusal by a worktree on no origin ref is CASCADE, stays pending, then runs`.
- `plan_moved_dropped` and `plan_moved_every_pass` are killed by `plan-beat: a changed PLAN.html is PLAN MOVED once; an unchanged one is no line`.
- `gantt_filter_dropped` and `gantt_rows_unmapped` are killed by the two `gantt:` cases. `gantt_rc_ignored` is killed by `gantt: a failed sweep_gantt is UNREADABLE, never its partial lines`.
- `verdict_filter_dropped` and `verdict_rc_ignored` are killed by the two `verdict-audit:` cases.
- `plan_rc1_silent` and `roster_noop_marked` had their sites re-anchored to the edited lines. Both are still killed.

Failing test first: the new cases ran against `origin/main`'s `beat_jobs.py`. The base has no `gantt` or `verdict_audit`, so those two were stubbed as no-ops so that the other cases could evaluate. Nine cases fail at the base and pass at this head: the four `gantt`/`verdict-audit` behaviour cases, `PLAN MOVED`, `UNRUN`, `CASCADE`, and the released-hold case, which now pins the `--mark`ed line.

## Null control

Each new behaviour case first asserts that its line is absent from an empty digest. Four null cases pass at both base and head:
- `roster-drain null: a lint refusal marked #refused is no CASCADE and no UNRUN, and is not retried`
- `plan-beat null: no mirrored page is no PLAN MOVED and no byte`
- `gantt null: no slip writes no digest`
- `verdict-audit null: nothing unheld writes no byte`

Of these, the `PLAN MOVED` case also proves that an unchanged page prints nothing on its second pass.

## Figures

- `python3 -I tools/audit/seat/beat_jobs.py --self-test` prints `beat_jobs self-test: <n> checks, 0 failed`. The count is cases plus `MUTANTS`. The instrument is named rather than its number.
- `python3 -I tools/audit/seat/sweep_gantt.py --self-test` and `python3 -I tools/audit/seat/verdict_audit.py --self-test` both print 0 failed.
- `python3 -I tools/audit/seat/beatd.py --self-test` prints 0 failed against the extended `beatd.jobs.json`.
- `python3 -I tools/audit/seat/sweep_render.py --self-test` prints 0 failed on the edited template.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` prints 0 unwired and 0 index gaps, with the three deleted self-testing files gone from both counts.
- `python3 tests/entities.py` prints `ALL ... ENTITY CHECKS PASSED`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` with every metric equal to its budget. The deleted files are under `tools/`, which the ratchet does not measure, so there was no re-record and no raise.
- The scope run, `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`, prints `MODE: SCOPED -- 2 script(s) run`, which are `tests/entities.py` and `tests/harness_headers.py`. Both pass locally.
- The verdict's harness, re-run: the runner steps that duplicate a beat row are 6 of 9 at `61f1ec71`. Here the runner does not exist (`git ls-files tools/audit/seat/sweep_runner.sh` prints nothing), and its three non-duplicate steps are beat rows: `gantt`, `verdict-audit` and the `PLAN MOVED` part of `plan-beat`. The class rule: `git grep -n "sweep_runner\|roster_drain.py" -- tools .github tests` returns no seam. The remaining mentions are in `dev/programme/triage/` records, which recount history and stay as written.
- The CodeQL alert 51 mode check: no helper added in this diff sets a file mode. The new rows write only through the base's `atomic()` and `mkdir`, with default modes, so there is nothing for a mode assertion to read. The alert's site, `sweep_runner_selftest.py`, is deleted.

## Red checks

The check runs of the PR's current head `61f1ec71` were read once: 68 runs (`total_count` 68), all on one page. None concluded `failure`, `cancelled` or `timed_out`.
- `gate`: the red the verdict saw at 02:57Z (run 42331132062) was the edit-run deferral, R10-HOTFIX-GATE-BUSY-DEFER, merged as #3246. Code run 42331131423 decided it, and its `gate` concluded `success`. The later `gate` runs of 42331132062 and 42333359612 also concluded `success`.
- `CodeQL` and code-scanning alert 51 (py/overly-permissive-file): `codeql / Analyze (python)` concluded `success` and `CodeQL` concluded `success` at `61f1ec71`, so the 0o700 repair closed it. This head deletes the file that carried the site. There is no cheaper detector: no local CodeQL run is a standing instrument, and building one costs a CodeQL database build per seat, which the PR's `Analyze (python)` leg already pays.
- `governance / instrument-self-tests` concluded `success` within its 30-minute timeout, so R10-HOTFIX-SELFTEST-TIMEOUT did not fire.

This head's own runs start once the orchestrator moves the PR to it. Any red there is the next round's to answer.

## Forward-carry

none

## Friction

none
