Fix review: blocked 5748642ff342ec68a49b085b2ef167f2d05a97ee carry-missing: R10-CI-LAYOUT's brief does not carry the follower-debounce finding

bus-nonce: c3950d9dd6ed2723fbad47052f25f07a

PR #2480, group R10-FOLLOWER-DEBOUNCE, head 5748642ff342ec68a49b085b2ef167f2d05a97ee, round 1.
Reviewed from a detached worktree at the head; head was still that SHA when this was written.
Merge base with origin/main (now 2c7ec6c0f) is 0c298f6b5; `git merge-tree --write-tree` exits 0, no conflict.

RESULT head=5748642ff342ec68a49b085b2ef167f2d05a97ee
RESULT follower_debounce=9 cases, 0 failed at the head; on origin/main's file it prints `REFUSED: first step ... is None`
RESULT mutations M1 (deferral unreachable), M2 (oldest red), M3 (trigger not excluded) each fail exactly the one named case
RESULT entities at head=ALL 2359 ENTITY CHECKS PASSED; mutation M4 (red-only job `if:`) yields 1 defect starting `if:`
RESULT harness_headers=ALL 109 HARNESS HEADER CHECKS PASSED
RESULT structure=STRUCTURE RATCHET PASSED
RESULT closure select=MODE: SCOPED -- 2 script(s) run (tests/entities.py, tests/harness_headers.py)
RESULT required checks=17 in ruleset 23698884; `PR contract re-run` is not among them, so the set is unchanged
RESULT follower runs created before 2026-10-19T15:08Z: 69 skipped, 2 failure, 29 success (31 ran the program)
RESULT carry_audit on the body: 3 finding items, 1 routed, 2 unrouted, exits 1

## Block: the forward-carry is not in R10-CI-LAYOUT's brief

The body's `## Forward-carry` says R10-CI-LAYOUT replaces this follower, must keep
the debounce semantics or drop it, must measure the per-head red count, and
inherits the API-lag gap. It cites `Carry: R10-CI-LAYOUT (roster d1707a459)`.
`d1707a459` is the roster commit that appended R10-FOLLOWER-DEBOUNCE; it does not
contain the destination carry. Opening the destination, at HEAD's roster, at
`d1707a459`, and at the live `origin/handoff/audit-r10-roster` tip `204eb8a99`, the
R10-CI-LAYOUT group's `brief` and `carry` mention neither `follower`,
`pr-contract-rerun`, `debounce`, `API-lag` nor `per-head red`. The finding changes
what R10-CI-LAYOUT must do (keep the semantics, and measure before keeping the
design), so `finding-propagation.md` requires it in that stage's own brief before
this PR merges. Evidence: `roster-check.txt`.

`Carry: R10-CI-LAYOUT (the destination brief still owes this finding; land it with roster_edit before re-review)`

## Deferred: the pr-contract red (step 11 gate not met)

At this head `pr-contract` is red twice (check runs 118515648145 at 07:48:39Z and
118515784799 at 07:49:01Z), each on `CARRY-AUDIT: 3 finding item(s): 1 routed,
2 unrouted`. The body's `## Red checks` names only `nightly-status`. The cheaper
detector is `python3 -I tools/audit/carry_audit.py check --body <file>`, which runs
in about a second and exits 1 on the same two items. Per `fix-review.md` step 11 this
class is posted only once the head's workflows have all concluded; when this verdict
was written `closures` was still `in_progress`, so it is recorded here and is not
this block's class. Routing the two `## Forward-carry` bullets clears it.
Evidence: `carry_audit.txt`, `check-runs-5748642.txt`.
`Carry: dismissed: fixed by routing the body's two Forward-carry bullets`

## Findings (non-blocking)

- The body's `## Figures` says `python3 tests/entities.py` at the head printed
  `ALL 2351 ENTITY CHECKS PASSED`. At the head it prints 2359: main's merge
  `f6abe94` added 8 `R.check` calls (the file's `R.check(` count went 1787 -> 1795,
  and the 8 added calls are in that merge). 2351 is true at the authored code head
  `f210e78`, not at the head. Re-take the figure at the head. Evidence:
  `entities_head.txt`. `Carry: dismissed: re-taken in this PR's body`
- The group brief asks for the call count per head "measured before and after".
  "Before" is measured (the 69/31 tally re-derives); "after" is a model, not a
  measurement, which cannot be run pre-merge because `workflow_run` executes the
  default branch's copy of this file. The body discloses this. Evidence:
  `follower_debounce_head.txt` (model lines). `Carry: R10-CI-LAYOUT (measure the per-head red count before keeping the design)`
- The changed-head null control is structural only: the concurrency group is pinned
  by exact string equality to `...workflow_run.head_sha` in tests/entities.py, and a
  group keyed on `workflow_run.id` is refused, but no case drives two different head
  SHAs through the step. The step itself keys only on `$HEAD_SHA`, so this is a
  gated-behaviour gap, not a known defect. `Carry: dismissed: covered by the group key pin`

## Notes on the control

- The design keys on the PR head SHA, not the run id: verified empirically that the
  watched runs and the pr-contract runs at this head all carry
  `head_sha=5748642ff342ec68a49b085b2ef167f2d05a97ee`, so `?head_sha=$HEAD_SHA` and
  the concurrency group agree. `Carry: dismissed: no action`
- The program is handed the newest red rather than the triggering run; the
  `contract_rerun.py` stale rule is unchanged and its timestamp comparison is
  against the newest red's finish, which is the latest a contract must post-date.
  `Carry: dismissed: no action`
- `follower_debounce.py` is the fixer's own instrument, disclosed as such in the
  body; no finder harness existed for a tvofi-ordered change. It is on the
  `inert_reads` list, so its 9 cases are not run by any closure; tests/entities.py's
  shape pin is the only CI guard on the jq semantics. `Carry: dismissed: recorded as a D3 seam`
- The API-lag residual the body names (a list read showing a sibling unfinished
  after its completion event) is real and cannot be measured with this build; the
  body carries it to R10-CI-LAYOUT. That carry is part of the block above.
  `Carry: R10-CI-LAYOUT (API-lag residual)`
