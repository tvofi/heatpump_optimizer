# Prompt: the round-9 fixing orchestrator adopts the ALT endgame plan

You are the round-9 fixing orchestrator. Read `CLAUDE.md` and `tools/audit/briefs/orchestrator.md`
before acting; nothing below loosens them.

tvofi has decided to replace `handoff/round9/state/DRAFT-ENDGAME-PLAN.md` with the alternative plan on
`handoff/audit-r9-plan` at `d5262feb`:

- `handoff/round9/state/ALT-ENDGAME-PLAN.md`: the review of the draft and the per-wave, per-PR schedule.
- `handoff/round9/state/ALT-ROSTER.json`: the roster for the rest of the programme.
- `handoff/round9/state/alt/`: the evidence (a163db90), the in-tree carry drafts, and the filed issue
  bodies with their read-back.
- Issues #1736 to #1745: filed, verified, and each already carries its disposition.

Read the plan in full before step 1. Its §3 is the owner's ratchet stance: "the ratchets are not set in
stone; the end goal is optimal architecture". A raise the better shape needs is asked for before the push,
never avoided by a worse shape.

## Steps, in order

1. **Re-base the plan.** It was measured at origin/main `31394964`.
   - List every merge since then on origin/main and apply it to `ALT-ROSTER.json`'s `resume` fields. F1.4
     is #1735.
   - If a merge touched a file a carry or an EG brief cites, re-run that brief's citations with
     `node .claude/workflows/brief_lint.mjs <roster>`, after fetching the round-9 evidence refs
     (`handoff/audit-r9-evidence`, `handoff/audit-r9-sweep-*`, `handoff/r9-rca-*`). It must print
     `TOTAL: 0 error(s)`.

2. **Adopt the roster** on `handoff/audit-r9-fixplan`.
   - Replace `.claude/workflows/wave-r9-groups.json` with the re-based `ALT-ROSTER.json`. If the live file
     changed after `68919da9`, apply ALT's three deltas to it instead:
     - the truthed `resume` fields;
     - the carries appended to the briefs of R9-F1.10 (#1741), R9-F10.1b (#1740) and R9-F10.4 (#1738),
       with those numbers added to each group's `issues`;
     - lane EG, groups R9-EG-B0 to R9-EG-B7.
   - Before any regeneration, change `handoff/round9/fix/src/gen.py` so it carries every group's existing
     `resume` forward. It currently rebuilds them as `not-started`, which has wiped 17 merged groups. If
     you would rather not change it, stop regenerating.
   - Lint the result and read it back.

3. **Land one record PR** by the `hpo-author` App through `tools/audit/app_push.sh`, never `push.sh`.
   - Add `handoff/round9/state/alt/carries/carry-1686.json` and `carry-1654.json` under
     `.claude/workflows/`.
   - Append `carry-1649.entry-to-append.json` to the existing `.claude/workflows/carry-1649.json`. Copy
     the full `carry-1649.json` draft over it only if main's file is unchanged since `31394964`.
   - Disposition #1736 to #1745 in the plan of record (`delivery-status-tracking.md` step 5), and give
     the PR its own `docs/delivery/<N>.md` row.
   - This must merge before R9-F10.1b, R9-F1.10 or R9-F10.4 starts: a carry is in the tree before its
     stage begins (`finding-propagation.md`).
   - The PR touches policy-adjacent record files only. It adds no budget and no `VERSION` edit.

4. **Post one #201 comment** with `.claude/workflows/gh_comment.py post`, and read it back. It says:
   - the plan was adopted;
   - the roster SHA;
   - the new EG lane;
   - what is dispatched now.

5. **Dispatch W0 now:**
   - re-review and merge F1.4 (#1735);
   - **start F7.2**: both its after-edges are merged, and it gates F2.4;
   - dispatch **R9-EG-B0**, a `root-cause.md` seat for #1736 that runs beside the programme, not inside
     any fix.

   Then follow `ALT-ENDGAME-PLAN.md` §4, one merge at a time, respecting every `after` edge.

## Rules specific to this plan

- **Lane EG never blocks an F-lane.** No F group has an EG after-edge; keep it that way.
- **Structure-budget writers are serialised.** R9-EG-B1, R9-EG-B5 and R9-EG-B7 all write the structure
  budgets, so never two of them are in flight at once (plan principle 2).
- **B1 lands after the fix release.** Stamp v6.8.0 after R9-F10.6 and R9-F11.5 (stamp point c), then
  land R9-EG-B1. Its fixer may prepare the branch earlier.
- **R9-EG-B5 is the owner's opt-in.** Ask tvofi before dispatching it. If he declines, set its
  `resume.stage` to `done`, with the refusal in `last_step`.
- **R9-EG-B7 is a measured go/no-go.** Where a seam's cut does not fall, record the halt on #1744 with
  the numbers.
- **EG PRs are pure refactors.** They claim no golden drift, and a moved golden means the PR is not pure.
  Each names its null control in the body (the issue states it). B1 and B5 carry the principle-3 check:
  a three-dot diff plus a whole-file comparison at every merge from main.
- **Raises.** Any budget raise, including #1738 arm (c)'s re-definition of `classes_over_300` inside
  R9-F10.4, needs tvofi's confirmation before the push, and merges on his approving review
  (budget-raise-gate, 0013).
- **Mandate.** It expires 2026-09-29T18:15Z. W0 and W1 fit inside it. Everything in lane EG and every
  owner-gated item after that waits for renewal, not for your judgement.

## Stop and ask tvofi when

- `brief_lint` is non-zero after re-basing and the fix would weaken a citation instead of correcting it;
- a carry's destination stage has already started; the carry then belongs to a new issue or that PR's
  own brief, not to a merged group;
- a merge since `31394964` has changed something the plan measured (a hub write, a store version, the
  duplication detector), so that the plan's verdict no longer follows.
