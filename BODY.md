Adds `cancel_superseded.py sweep --repo R [--dry-run]` (triage P266, V180): cancels a PR branch's superseded runs from outside the run, so the queued-newer-run case (#2927, #2928) no longer holds runners. Reuses `candidates()`; one predicate, one owner. Round 2 answers the round-1 block: every unpinned sweep mutant is pinned, both listings are paged, every ACTIVE status is listed, and the API cost is stated. Not carried: adoption by R10-ORCH-BEATD as a job.

## Head

acf3d846eb9dc6c69db86f12c24943e2031f0e77 (base cf4f6b7a6)

## Mutation proof

Each mutant edits one predicate in tools/pr/cancel_superseded.py; `python3 tools/pr/cancel_superseded.py --self-test` (43 checks, 0 failed restored) then fails the named arm:

- EVENTS widened with "push": 2 FAIL (round 1).
- unreadable-PR-list guard removed: 2 FAIL (unreadable pulls / runs answer says unreadable, not a zero count).
- unreadable-runs guard removed: 1 FAIL (unreadable runs answer).
- unreadable-commit guard removed: 1 FAIL (unreadable commit answer).
- `bot_heads.add` replaced by `pass`: 2 FAIL (end to end, the stub answers github-actions[bot] as login and as git author name; the default stub answers hpo-author).
- live-head id bound replaced by `sys.maxsize`: 1 FAIL (an older-head run with a higher id than the live run is kept).
- ACTIVE status filter dropped in sweep_plan: 1 FAIL (a finished run is not kept, a ghost or skipped).
- run-side fork (`head_repository`) filter dropped: 1 FAIL.
- main/event skip dropped: 1 FAIL. Pinned, not deleted: `candidates()` also drops those events, but the `skipped` and `ghosts` counts are the sweep's report and only this skip keeps main and non-PR-event runs out of the ghost count.
- statuses cut back to three: 1 FAIL (pending and requested runs are POSTed end to end).
- pagination removed: 2 FAIL (next page is read; a still-full last page prints truncated).

## Null control

Only live-head runs cancels nothing (`sweep null`); a bot-authored live head cancels nothing; an unreadable answer cancels nothing and exits 0; each mutant above is the control for its arm: restored tree 43 checks, 0 failed.

## API cost bound

Per sweep: 1 PR listing + 5 run listings (one per ACTIVE status; one page each below 100 items, at most 10 pages per listing, a still-full last page prints `CANCEL-SWEEP: truncated: <listing> still full after 10 pages; counts are a lower bound`) + one commit read per open PR with something to cancel + one POST per cancel. Stated in the module docstring and tools/audit/seat/instruments/cancel_superseded.py.md.

## Unpinned sites

The diff adds only tools/pr/cancel_superseded.py code, outside the lane `mutation-autofix` mutates (custom_components/ only); every mutant above is pinned by an in-tree self-test arm.

## Figures

- `python3 tools/pr/cancel_superseded.py --self-test` -> 43 checks, 0 failed at the head above.
- `python3 tests/structure.py` -> see prepr result.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` -> mode line read in prepr.

## Red checks

`governance / instrument-self-tests` was red at the previous head a3b3a42cab (job 124198564586, 17:01-17:25Z). Cause not established: the job log is only readable through the last 2000 lines (the blob download is refused by the proxy, 403), and in those lines every self-test reports 0 failed and the alert_list mutants are all refused; the failing step lies above the readable tail. Not shown to be this program: its self-test (governance.yml:360) is the 30-check run that passed for the reviewer, and now 43 checks, 0 failed here. Cheaper detector: none identified, since the failing step is unread; the orchestrator's CI read at the new head decides whether the red persists.

## Forward-carry

Carry 1 (roster carry, P267/P268: the CI-priority tier module, its config file and the merge train's pause/resume), appended at 9e7ba7aae: this PR stays the sweep only, per the orchestrator's s8 disposition under mandate 6329234399. Part 2 of this group (R10-FLY-CANCEL-SWEEP PART 2, a follow-up PR after this one merges) builds it; R10-FLOW-WIP, R10-FLOW-TOOLKIT-MODEL and R10-ORCH-LEDGER stay after-edged on the group (roster: dev/programme/rosters/wave-r10-groups.json). Carry: R10-FLY-CANCEL-SWEEP

## Friction

none
