R10-ARCH-DOCS, arm B of triage P261: `docs/architecture.md` and `dev/README.md` verified against the tree, every wiring marker resolved, the machinery figure redrawn and pinned. Closes #2395. Part of #201.

## Re-cut

Round 4, after `Fix review: blocked a4eac74f1b795b565cf2843b91c5c079796368b2 doc-claim-false`. A minimal re-cut: origin/main merged into the round-3 head, the three block items closed by drawing a true arrow or deleting the false line, the arrow enumerator widened and a write enumerator added. No sentence was added to either page beyond the arrows' rows and two names in existing bullets.

1. **The figure's undrawn runs and writes.** Drawn, each with its row citing the line in the script:
   - `opr -->|"runs"| busx`: `tools/audit/seat/open_pr.sh` `bash "$SEAT/bus.sh" rekey "$T" "$N"`.
   - `opr -->|"writes"| ledger`: `tools/audit/seat/open_pr.sh` `"$SEAT/ledger.py" attempt "refs/heads/handoff/$T"`. `ledger.py` joins the helpers the "drawn as the writer" bullet names for `open_pr.sh`.
   - `train -->|"writes"| pr`, which N20 returned: `merge_train.py`'s `undraft` runs `gh pr ready` on a draft before the merge.
   - `postmerge.py`'s `merge_train.py classify` run is added to the page's "a run that only reads" bullet beside the relay's and `bus.sh`'s.
2. **`Note over T,M: record-owed opens on merge`.** Deleted, with its `record-owed closes` partner: `ledger.py`'s `record_owed` keys on an approved record pull request open thirty minutes, which no step of the diagram makes.
3. **The row "orchestrator runs fixer, reviewer and design seats".** Now cites the instrument guide the person follows, `tools/audit/seat/instruments/cloud_dispatch.py.md` `or fire the standing trigger`, in place of `cloud_dispatch.py`'s help text, which the page says fires nothing. The help text is left as it is: it describes what the person does after `--publish`.

Alternatives not taken: deleting the page's completeness sentence ("the arrows are the runs and writes of a normal pass") instead of drawing the three arrows. The arrows are true and each is pinned by its row, so drawing them keeps the sentence true at the cost of three rows; deleting it would leave the left-out list with no rule to be the exceptions of.

## Head

62a7d7a57f894aa6f4d90f296a381a4906bd0551: the merge of origin/main cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf into a4eac74f1b795b565cf2843b91c5c079796368b2, then one commit. `tests/closures.json` was resolved by the `LEDGER-MERGE` driver (`inert_reads.tests/harness_headers.py` merged as a set) and re-proved by `tools/pr/ci_predict.py --base origin/main --apply-inert`, which applied nothing.

## Mutation proof

This round changes no line of `tests/doc_claims.py`; the four new rows are pinned by its existing machinery check. `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_arch_docs_mutants.py` at the head: `RESULT baseline_fails=0`, `RESULT mutants=18`, `RESULT killed=18`, `RESULT live_calls=2`, `RESULT live_calls_shown=2`.

Failing test first, for the enumerators (each run on this head's tree):

- N18 at a4eac74f's pattern returns none of `open_pr.sh -> bus.sh` (154), `postmerge.py -> roster_sync.py` (47), `-> state_docs.py` (48), `-> merge_train.py` (49); the widened pattern (a path under a variable, `$SEAT/` or `{seat}/`) returns all four and no other new line (`diff` of the two N18 blocks: exactly those four `>` lines).
- N20 over a4eac74f's `dev/README.md` prints five `UNDRAWN` pairs, among them `open_pr.sh -> obligations ledger: lines 55 56` and `merge_train.py -> pull request: lines 1357 1359 1361 1409 1410 3350`; over this head's page those two are `DRAWN`.

## Null control

- The mutant harness's baseline: `RESULT baseline_fails=0`.
- N20's own control is the run above: the same enumerator over the round-3 page returns the two pairs this round draws; over this page it does not.
- A row's quote is checked against its file: the existing fixture `red fixture: a cited line the code no longer holds is a finding` is among the killed mutants.

## Figures

Measured at the head, origin/main cbd23f1c8bf6 at 2026-11-11T09:17:17Z.

- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: `ALL 342 checks PASSED`. `--markers`: `0 of 0 marker(s) due`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`. `tests/entities.py`: `ALL 2707 ENTITY CHECKS PASSED`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL -- every test script runs, nothing is scoped out.` (reason `tests/closure.py changes the gate itself, so every closure is suspect`); the rest is CI's.
- `python3 tools/pr/ci_predict.py --base origin/main --apply-inert`: `CI PREDICT: no closures, fast, governance or instrument red predicted against cbd23f1c8bf6 (a data-file read is not seen)`.
- `python3 dev/audit/harnesses/r10_arch_docs_enumerate.py`, N19: `arrows 45 rows 45` (42 before, plus the three drawn here); the gate check requires the two sets equal, not the counts.
- Seams (`fixer.md` step 8). The class is a drawn script's run or write the figure neither draws nor dispositions.
  - Runs. Enumerator: N18, every executable reference from one of the fifteen drawn script files to another or to `replan.py`, `open_driver.py`, `carry_fold.py`. Its four new lines, by disposition: `open_pr.sh -> bus.sh` 154, drawn this round; `postmerge.py -> roster_sync.py` 47 and `-> state_docs.py` 48, drawn already (`post -->|"runs"| rsync`, `post -->|"runs"| docs`); `postmerge.py -> merge_train.py` 49, `classify`, a run that only reads, now named on the page. Every other N18 line is the round-3 set, unchanged by the widening, with the round-3 dispositions: drawn, a read-only run the page names, text a script prints, inside a self-test, `plan_page.py`'s variable named `open_pr`, or `state_docs.py`'s roster-sync step no caller enters. Its limit: a script is matched by its file name, so a run through a variable holding the whole path is not seen.
  - Writes. Enumerator: N20, for each drawn script file and each drawn store, the lines matching that store's write pattern (a push to its ref, an append to its file, a ledger `open`/`close`/`attempt`, a `gh pr` write or the pull-request helpers, `--merge`), outside self-test functions and docstrings; `DRAWN` when the figure has that `writes` arrow. Every `UNDRAWN` line at this head, by disposition:
    - `cloud_dispatch.py -> bus refs` 308: text of the brief the script renders for a reviewer seat, which pushes the probe ref itself (`seats -->|"writes"| bus`).
    - `merge_train.py -> obligations ledger` 4210: a log line telling the reader to run `ledger.py close train-stop`; the train writes nothing there.
    - `orchestrator_tick.py -> pull request` 2424: text of a board line naming `open_pr.sh` and `update_pr.sh`.
  - Writes N20 does not see, read in the code: `bus.sh` 706 and `cloud_dispatch.py` 605 call `ledger.py` across lines, so the one-line pattern misses the verb. The first is drawn (`busx -->|"writes"| ledger`); the second is the refusal-path reopen of `reviewer-fire` the page names as left out.
  - The record comment `postmerge.py` posts through `record_beat.record` goes to the record issue, a store the figure does not draw, so it is outside the class.

## Red checks

none

## Forward-carry

- `dev/programme/rosters/wave-r10-groups.json`, R10-ARCH-DOCS-DELTA's brief: `tests/doc_claims.py` now refuses a bare marker whose groups are all done, so the re-read after the last product merge states the tree and adds no marker for a landed group. The "One owner per concern" bullets in `docs/architecture.md` were written at d08ed31049; re-check each against its module at the delta's merge base. Control: `python3 tests/doc_claims.py --markers --roster <the roster branch's file>` exits 0 with `0 of 0 marker(s) due`. Carry: R10-ARCH-DOCS-DELTA
- `dev/programme/rosters/wave-r10-groups.json`, R10-ARCH-DOCS-DELTA's brief: `dev/README.md` states that the ruleset requires only `gate` on `nudge.md` section 4's authority, not from a live read. A seat with the ruleset read confirms it against ruleset 23698884, or corrects the sentence. Carry: R10-ARCH-DOCS-DELTA
- `dev/programme/rosters/wave-r10-groups.json`, R10-USER-DOCS-VERIFY's brief: `check_marker_census`'s anchor no longer requires a marker to exist, so removing the last user-doc marker leaves `tests/doc_claims.py` green. Control: `python3 tests/doc_claims.py --markers --user` ends `0 user-doc marker(s), 0 due`. Carry: R10-USER-DOCS-VERIFY

## Friction

none
