R10-REVIEW-DISPATCH-RESIDUE part 3 of 6 (topic r10-review-dispatch-residue-p3): Carries 2, 3, 8, 9 and 13, by their 0-based roster indexes.

- **Carry 13** (triage P551, S14-BRIEF-OVER-FIVE), built first. Without `--part`, `dispatch_group` refuses a fixer for a group holding more than `PART_CARRIES` (5) pending carries (`roster_lib.pending_carries`, legacy read through `roster_lib.read_legacy`), and the one-line refusal prints the split from `part_split`: index-ordered fives, with a remainder of `PART_FOLD` (2) or fewer folded into the last part. Non-contiguous pending indices print as runs (`0-1+3-6+9`). `--part k` adds one generated line after the brief's generated lines (`Part k of N: build carries a-b; the others are later parts dispatched at this part's handoff; answer none of them`). For k over 1 the topic is `<topic>-p<k>`, which `roster_lib.group_for_branch` already maps back. These refuse: a part past N, `--part` on a group of five or fewer, `--part` for any role but the fixer, and `--part` without `--group`. A group whose carry list holds five or fewer entries never reads the legacy roster. Parts are not defaulted (P551's narrowing), and `tools/plan/durations.json` is not read.
- **Carry 8** (P437 C2). The reviewer's `_prompt` text gains three things. Every stop path pushes a verdict to its probe ref: a setup or hook refusal pushes `Fix review: blocked <head> seat-refused: <the refusing line>`. The seat never ends its turn while a background poll runs, and it reads the ref back with `git ls-remote` and pushes again on a miss. On the PR path, a review_packet `required-red` does not stop the seat while classify prints WAIT, because classify decides. WAIT keeps its existing bound of about 30 minutes of polling, which sits inside the returners' 37 to 66 min whole-seat range. Past it, a complete review returns `pending-ci:` as before (Carry 12, 5cdc0bb350), and an incomplete one pushes `Fix review: blocked <head> ci-wait: <the last classify line>`. The at-handoff reviewer has no CI wait, so it gets no `ci-wait` path.
- **Carry 9** (tvofi 2026-11-09). `FRUGAL_LINE` drops "at most 5 inline search operations per prompt". On a guard refusal the seat now dispatches a haiku or sonnet Agent subagent, and the line forbids setting FRUGAL_ALLOW_INLINE and editing .claude/settings.json. The self-test pins the whole line verbatim. Neither `instruments/cloud_dispatch.py.md` nor `r10_flow_dispatch_mutants.py` quoted the old line, and `git grep -n "at most 5 inline"` at the merge base returned only cloud_dispatch.py:140. Role-contract pointer: judged not needed, so no finding goes to part 5. Every dispatched seat's prompt carries the line once (pinned in the self-test for every role), and the guard's own refusal text names the delegation. A pointer in fixer.md or fix-review.md would be a second copy of the rule, which `finding-propagation.md` says goes stale unevenly.
- **Carry 2** and **Carry 3** were already built on main by R10-DISPATCH-AT-HANDOFF, under its own indexes 4 and 8 (`roster_lib.consumers_of` / `brief_lines`, `prepr.sh` step 7e's `carry targets` info lines; `resolve_model`, `LIGHT_REVIEW_MODEL`, `--carry-only`, `--record-pr`). This part adds no production line for them. It proves their pins with the mutants each carry names, re-created as harness entries and quoted below.

The mutant harness `dev/audit/harnesses/r10_flow_dispatch_mutants.py` was stale at the merge base: it aborted at its third mutant (`abort: brief-drop's pattern occurs 0 times`). Four patterns no longer matched (brief-drop, cli-nonce-dropped, cli-model-fixed, cli-overlay-dropped); they are re-aimed at the current text. A mutant may now name `roster_lib.py` as a fourth element.

## Head

bd34f6b06b2b4a343cc8a0e80dc750d5c7d2995d, measured on a merge base equal to origin/main a7628041dc02e298c5399003d4c0576391dd5c4e (stamped 2026-11-11T06:58Z).

## Mutation proof

Each mutant was applied alone, in a `git archive` copy of the head, by `python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py`; then `cloud_dispatch.py --self-test` was run and the file restored:

- `RESULT mutant=brief-drop failed=11 verdict=killed` -- `FAIL a group with no carry, consumer or enumeration renders its brief and `After:` alone (the null control)`
- `RESULT mutant=cli-nonce-dropped failed=3 verdict=killed` -- `FAIL --group forwards --nonce to dispatch_group`
- `RESULT mutant=cli-model-fixed failed=3 verdict=killed` -- `FAIL --group forwards --model to dispatch_group`
- `RESULT mutant=cli-overlay-dropped failed=3 verdict=killed` -- `FAIL --group forwards --overlay to dispatch_group`
- `RESULT mutant=part-count failed=4 verdict=killed` -- `FAIL a fixer for a group with 21 pending carries (a marked 22nd not counted) refuses, printing the split`
- `RESULT mutant=part-refusal-off failed=1 verdict=killed` -- `FAIL a fixer for a group with 21 pending carries (a marked 22nd not counted) refuses, printing the split`
- `RESULT mutant=part-prefilter failed=1 verdict=killed` -- `FAIL a fixer for a group with 21 pending carries (a marked 22nd not counted) refuses, printing the split`
- `RESULT mutant=part-fold-off failed=5 verdict=killed` -- `FAIL a fixer for a group with 21 pending carries (a marked 22nd not counted) refuses, printing the split`
- `RESULT mutant=part-fold-one failed=1 verdict=killed` -- `FAIL the split folds a remainder of one or two into the last part, and only that`
- `RESULT mutant=part-pending-raw failed=3 verdict=killed` -- `FAIL a fixer for a group with 21 pending carries (a marked 22nd not counted) refuses, printing the split`
- `RESULT mutant=part-topic-dropped failed=2 verdict=killed` -- `FAIL --part 2 renders the topic <topic>-p2 and one generated line naming carries 5-9`
- `RESULT mutant=part-line-dropped failed=2 verdict=killed` -- `FAIL --part 2 renders the topic <topic>-p2 and one generated line naming carries 5-9`
- `RESULT mutant=part-cli-dropped failed=2 verdict=killed` -- `FAIL --group forwards --part to dispatch_group`
- `RESULT mutant=part-role-open failed=1 verdict=killed` -- `FAIL a part past the split, a part of a group of five or fewer, and a part for another role refuse`
- `RESULT mutant=part-range-off failed=1 verdict=killed` -- `FAIL a part past the split, a part of a group of five or fewer, and a part for another role refuse`
- `RESULT mutant=part-small-open failed=1 verdict=killed` -- `FAIL a part past the split, a part of a group of five or fewer, and a part for another role refuse`
- `RESULT mutant=wait-bound-dropped failed=1 verdict=killed` -- `FAIL WAIT is bounded: past about 30 minutes an incomplete review pushes `ci-wait` with the classify line`
- `RESULT mutant=ci-wait-dropped failed=1 verdict=killed` -- `FAIL WAIT is bounded: past about 30 minutes an incomplete review pushes `ci-wait` with the classify line`
- `RESULT mutant=required-red-dropped failed=1 verdict=killed` -- `FAIL a required-red packet does not stop the reviewer while classify reads WAIT: classify decides`
- `RESULT mutant=seat-refused-dropped failed=1 verdict=killed` -- `FAIL the reviewer's setup or hook refusal pushes `seat-refused`, and it reads its ref back, at the PR and at the handoff`
- `RESULT mutant=poll-end-dropped failed=1 verdict=killed` -- `FAIL the reviewer's setup or hook refusal pushes `seat-refused`, and it reads its ref back, at the PR and at the handoff`
- `RESULT mutant=readback-dropped failed=1 verdict=killed` -- `FAIL the reviewer's setup or hook refusal pushes `seat-refused`, and it reads its ref back, at the PR and at the handoff`
- `RESULT mutant=frugal-allowance-back failed=2 verdict=killed` -- `FAIL every role's prompt carries the frugal-routing line once, verbatim (P398)`
- `RESULT mutant=model-roster-ignored failed=6 verdict=killed` -- `FAIL a fixer dispatched with no model runs on the roster's fixer model and prints the model and the field it read`
- `RESULT mutant=record-pr-opus failed=1 verdict=killed` -- `FAIL a carry-only review and a record-PR review resolve sonnet whatever the roster rules`
- `RESULT mutant=done-filter-dropped failed=1 verdict=killed` -- `FAIL a fixer's brief lists the live consumers (after-edged and file-sharing) as the only valid Carry targets, not the done one`
- `RESULT mutant=enum-line-dropped failed=1 verdict=killed` -- `FAIL and the group's class-enumeration command`

Failing test first: the new arms ran against the unchanged production code and went red: `FAIL a fixer for a group with 21 pending carries (a marked 22nd not counted) refuses, printing the split`, then `TypeError: dispatch_group() got an unexpected keyword argument 'part'`.

## Null control

`RESULT mutant=M0 failed=0 verdict=null-ok`: the unmutated file passes. Each carry also has its own null-control arm:
- Carry 13: `five pending carries (a moved sixth not counted) dispatch unrefused, the brief byte-identical (null control)`. The PROMPT.md tail equals `group_brief(five, ..., fixer=True)`, and the prompt carries no `Part` line.
- Carry 8: `no other role is told any reviewer stop push (null control: the fixer prompt carries none)`.
- Carry 9: `and no prompt grants an inline allowance the guard does not`.
- Carry 2: `a group with no carry, consumer or enumeration renders its brief and \`After:\` alone (the null control)`, pre-existing.
- Carry 3: `a roster ruling opus for the reviewer still resolves opus for a first-round review (null control)`, pre-existing.

## Figures

- `python3 tools/audit/seat/cloud_dispatch.py --self-test` at the head: `cloud_dispatch self-test: 166 checks, 0 failed`. At the merge base: `cloud_dispatch self-test: 153 checks, 0 failed`.
- `python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py` at the head: `RESULT mutants=56 survived=0`, 5 `verdict=CRASHED` (parent-drop, topic-to-id, head-ignored, roster-repo-ignored, pointer-off: pre-existing mutants, killed before the summary line), none of them this part's; each of this part's 27 is `verdict=killed` with a named FAIL line (Mutation proof). At the merge base: `abort: brief-drop's pattern occurs 0 times` (rc=2), after M0 null-ok and tree-skip killed.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No `structure_budgets.json` key moved.
- Class enumeration (fixer.md step 8) for Carry 13's class, "a fixer brief over five pending carries". The rule: every live group on the roster branch (stage outside `roster_lib.CARRY_CLOSED`) whose `roster_lib.pending_carries` exceeds `PART_CARRIES`, each printed with its `part_split`. Command: `python3 -I over_five.py`, a scratch probe that runs exactly that loop over `roster_lib.reader_ref(".", None)` = origin/handoff/audit-r10-roster at 17578fc4f95516ae290400a75fd995f2fb806202. It printed `live groups over five pending: 15`:
  R10-ARCH-DOCS 11, R10-USER-DOCS-VERIFY 12, R10-ROUND-PLAYBOOK-FINAL 16, R10-ARBITER-OFF-RESTORE 11, R10-PREPR-RESIDUE 23, R10-TRAIN-RESIDUE 19, R10-TICK-RESIDUE 29, R10-REVIEW-DISPATCH-RESIDUE 22, R10-PLAN-PAGE-RESIDUE 6, R10-STANDING-CONTRACTS-P2 24, R10-SEAT-IDENTITY-P5 6, R10-SUITE-ENV-RESIDUE 7, R10-SAV-VALUATION-RESIDUE 6, R10-COMBI-TANK-PR-B 8, R10-ARCH-DOCS-DELTA 8.
  Disposition: every one is closed in this diff. Its next fixer dispatch through `--group` refuses and prints the split. R10-REVIEW-DISPATCH-RESIDUE's own split by file (triage P551) still goes through the flag path (`--brief`), as this part did. Null control: the same loop over the five-carry fixture group prints nothing, and the self-test arm above dispatches it unrefused.
- Carry 8's 13 of 160 (8.1 %) and the 37 to 66 min returner range are P437's figures, cited and not re-measured here.

## Red checks

none

## Forward-carry

none

## Friction

none
