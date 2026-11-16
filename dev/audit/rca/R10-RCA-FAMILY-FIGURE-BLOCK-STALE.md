# R10-RCA-FAMILY-FIGURE-BLOCK-STALE: a body's generated block rendered against another base or head than pr-contract's

Round-end family analysis (loop card L8) of two sibling families the round-10 orchestrator
counted apart: figure-block-base-mismatch (HANDOVER's "generated-block-stale") and the head-move
proposals PC-1113-10 and PC-1113-19. Measured at `origin/main` `a39627da59` on 2026-11-15. Lands
no code.

## 1. Instances

From the sweep log (`$HPO_STATE_DIR/s14/sweep.md`):

| line | pull request | how the block went stale |
|---|---|---|
| 1906, 1910 | #3556 (twice: `6e1ad808`, `0165e02a`) | a recarry, then the `ci: merge main` bot commit moved the head |
| 2062 | #3569 | `remerge_main.sh` pushed under the old body; gate red about an hour on a gating PR |
| (PC-1113-19) | #3561 | the same, `## Head` not naming the remerged head |
| 2084 | #3574 | the mutation-pin bot moved the head |
| 2334 | #3587 | the pin bot moved the head |
| 2389, 2391 | #3532 (twice), #3568 | `update_pr.sh`'s body-only refresh rendered against `origin/main` |
| 2597 | #3593 | the same: `MODE: FULL` in the body, `MODE: SCOPED -- 27 run` at `pr-contract` |

Ten reds over 2026-11-13 22:15Z to 2026-11-15 07:32Z. Each was `pr-contract`'s `figure_block
verify` refusal; `pr-contract` is a need of the required `gate`, so each turned the gate red.

## 2. Named cause

Two causes, one shape (a body that describes a head or base the check does not use):

- **Base.** `tools/audit/seat/update_pr.sh:105` and `tools/audit/seat/open_pr.sh:118` render
  with `--base origin/main`; `.github/workflows/pr-contract.yml:396` verifies with `--base
  "$PR_BASE"`, which is the event's `pull_request.base.sha` or the API's `.base.sha` (line 172).
  `figure_block.py` runs the instrument from the base tree overlaid on the head
  (`tools/pr/figure_block.py`, its docstring lines 13-17), so after main moves, the scope line
  renders against a different base tree and can read `MODE: FULL` where `pr-contract` reads
  `SCOPED` (intake carry 162 measured the overlay effect on `tests/closure.py`). A body-only
  refresh, which moves no head, is where the two bases diverge most.
- **Head.** A head moved by a path that does not re-render the body (`app_push.sh --recarry`
  under `remerge_main.sh`, the `merge-main` bot, the mutation-pin bot) leaves a block naming the
  old head (`figure_block.py:168`, the head and merge-base attributes are compared).

## 3. Process state

Base: (c). The refresh step existed and ran every time; it produced a block for the wrong base.
Head: (a) for the bot paths: no process re-renders a body when a bot moves the head; the
orchestrator repaired each by hand with `figure_block.py refresh --base <pulls base.sha>`.

## 4. Class reach

L9 names figure blocks as one of four artifacts that should be generated after the head moves,
not edited by the writer of the body; the others are in
`R10-RCA-FAMILY-SELFTEST-SCOPE-DRIFT.md` section 4. The relay's body-only re-apply (sweep line
1407) and its dispose of a refused body-only update (line 1626) are the same shape.

## 5. Cost test

- cost(defect): a red gate until noticed (about an hour on #3569, a gating pull request), one
  body-patch seat turn, and on #3532 a blocked verdict round (line 2394: "body only").
- P(recurrence): ten in about 33 hours, while main merged at its round-10 rate.
- cost(countermeasure, recurring): base, one `gh api pulls/<n> --jq .base.sha` read per
  refresh (under a second); head, the generator L9 builds.

The base countermeasure passes at once; the head one is the class elimination L9 already owns.

## 6. Countermeasure

1. Base, now: `update_pr.sh` and `open_pr.sh` refresh with `--base` set to the pull request's
   recorded base sha, as the by-hand cure did. Group R11-HOTFIX-FIGURE-BLOCK-BASE (triage
   `dev/programme/triage/r10-round-end.md#P774`). Admissible under the freeze: #3593, a
   `custom_components/` pull request, went gate-red on it. Demonstration owed: a self-test case
   where main has moved past the pull request's base sha renders the block `pr-contract` verifies
   (red on the base before the fix, `MODE: FULL` against `SCOPED`); null control, main not moved,
   identical output.
2. Head: R11-PRE-SHARED-FILES under L9 (P748): the block is rendered by whatever moves the head,
   or by `pr-contract` itself.
