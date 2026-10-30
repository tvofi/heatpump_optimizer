Adds `cancel_superseded.py sweep --repo R [--dry-run]` (triage P266, V180): cancels a PR branch's superseded runs from outside the run, so the queued-newer-run case (#2927, #2928) no longer holds runners. Reuses `candidates()`; one predicate, one owner. Round 2 answers the round-1 block: every unpinned sweep mutant is pinned, both listings are paged, every ACTIVE status is listed, and the API cost is stated. Not carried: adoption by R10-ORCH-BEATD as a job.

## Head

a44b8c7afa4e175ef50b9fcf0e889b3ae0be5423 (on b63829d1c163aff58823157d7691894f46301ae5; round 4, one instrument-page line)

## Mutation proof

Each mutant edits one predicate in tools/pr/cancel_superseded.py; `python3 tools/pr/cancel_superseded.py --self-test` (44 checks, 0 failed restored) then fails the named arm:

- EVENTS widened with "push": 2 FAIL (round 1).
- unreadable-PR-list guard removed: 2 FAIL (unreadable pulls / runs answer says unreadable, not a zero count).
- unreadable-runs guard removed: 1 FAIL (unreadable runs answer).
- unreadable-commit guard removed: 1 FAIL (unreadable commit answer).
- `bot_heads.add` replaced by `pass`: 2 FAIL (end to end, the stub answers github-actions[bot] as login and as git author name; the default stub answers hpo-author).
- live-head id bound replaced by `sys.maxsize`: 1 FAIL (an older-head run with a higher id than the live run is kept).
- ACTIVE status filter dropped in sweep_plan: 1 FAIL (a finished run is not kept, a ghost or skipped).
- run-side fork (`head_repository`) filter dropped: 1 FAIL.
- event skip dropped: 1 FAIL. `b == "main"` disjunct dropped alone (round-3 fix): was 43 checks, 0 failed (survived); now 44 checks, 1 failed (`sweep: a PR-event run on main is skipped by the branch test alone...`, got skipped 0, ghosts [93, 94], want 2, []). The new arm uses workflow_dispatch and pull_request runs on main, both in EVENTS with matching repo, so only that disjunct skips them. Kept, not deleted: candidates() also drops main, but the sweep's skipped/ghosts report depends on this skip.
- statuses cut back to three: 1 FAIL (pending and requested runs are POSTed end to end).
- pagination removed: 2 FAIL (next page is read; a still-full last page prints truncated).

## Null control

Only live-head runs cancels nothing (`sweep null`); a bot-authored live head cancels nothing; an unreadable answer cancels nothing and exits 0; each mutant above is the control for its arm: restored tree 44 checks, 0 failed.

## API cost bound

Per sweep: 1 PR listing + 5 run listings (one per ACTIVE status; one page each below 100 items, at most 10 pages per listing, a still-full last page prints `CANCEL-SWEEP: truncated: <listing> still full after 10 pages; counts are a lower bound`) + one commit read per open PR with something to cancel + one POST per cancel. Stated in the module docstring and tools/audit/seat/instruments/cancel_superseded.py.md.

## Unpinned sites

The diff adds only tools/pr/cancel_superseded.py code, outside the lane `mutation-autofix` mutates (custom_components/ only); every mutant above is pinned by an in-tree self-test arm.

## Figures

- `python3 tools/pr/cancel_superseded.py --self-test` -> 44 checks, 0 failed at the head above.
- `python3 tests/structure.py` -> see prepr result.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` -> mode line read in prepr.

## Red checks

`governance / instrument-self-tests` is this diff's own red at b63829d1c163 (review/3004, ci-red). The round-3 body said it was not this program's; that was wrong. Cause: `python3 tools/audit/seat/selftest_wiring.py --check` (governance.yml:499) printed `MISMATCH tools/audit/seat/instruments/cancel_superseded.py.md: the index line's name is not the one its entry opens with`, 1 index gap. INSTRUMENTS.md indexes the page as `cancel_superseded.py sweep`, while the entry's first bullet opened with the full command (`python3 -I tools/pr/cancel_superseded.py sweep ...`), and ENTRY_RE reads that first backticked name. Fix: the bullet now opens with `cancel_superseded.py sweep` and keeps the command in parentheses; the instrument code is unchanged.

Control: with the edit, `selftest_wiring.py --check` prints `0 index gap(s)`; with the page reverted to b63829d1c163 it prints the MISMATCH line and `1 index gap(s)`; re-applied, `0 index gap(s)`.

Root-cause trigger (red check a cheaper detector could have run): the cheaper detector is `selftest_wiring.py --check` before handoff. prepr ran it: its `ci predict` step calls `wiring_preds` (tools/pr/ci_predict.py), which runs `--check` but keeps only lines starting `  UNWIRED `, so MISMATCH, UNINDEXED, DUPLICATE and MISSING lines were discarded and it printed `no ... instrument red predicted`, here and at every earlier round. Process state: the detector existed and ran, and its filter was narrower than the check. Countermeasure not built in this re-cut (three-round rule, one-line scope); it is one change, `wiring_preds` returning every gap line naming a changed file, with a planted-MISMATCH arm in ci_predict's `--self-test`. Reported to the orchestrator in the handoff message, owed as its own group.

## Round 3

Answers the round-2 block (sweep-main-skip survivor) with one self-test arm and no production change. The reviewer's non-block `commit-only-cancel-prs` finding (commit-read cost bound unpinned) is carried to Part 2 below, per the brief's exact scope; `pr-open-state` is dismissed as in the verdict.

## Round 4

Answers the round-3 ci-red block with one line of tools/audit/seat/instruments/cancel_superseded.py.md; no production code, test or budget change. The head merges origin/main (437f1ba9b521).

## Forward-carry

Carry 1 (roster carry, P267/P268: the CI-priority tier module, its config file and the merge train's pause/resume), appended at 9e7ba7aae: this PR stays the sweep only, per the orchestrator's s8 disposition under mandate 6329234399. Part 2 of this group (R10-FLY-CANCEL-SWEEP PART 2, a follow-up PR after this one merges) builds it; R10-FLOW-WIP, R10-FLOW-TOOLKIT-MODEL and R10-ORCH-LEDGER stay after-edged on the group (roster: dev/programme/rosters/wave-r10-groups.json). Carry: R10-FLY-CANCEL-SWEEP

## Friction

none

## Prepr

`tools/pr/prepr.sh` (no closures skip; the closures step is left to CI as on this seat type) at a44b8c7afa4e: MODE: SCOPED; ci predict ok; wave-script 224 passed, 0 failed; unpinned sites skip (no unpinned mutation site); `python3 tests/structure.py` passed. Carry check: roster at 9e7ba7aae holds R10-FLY-CANCEL-SWEEP.
