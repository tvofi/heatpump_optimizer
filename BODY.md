R10-REVIEW-DISPATCH-RESIDUE part 3 of 6 (topic r10-review-dispatch-residue-p3): Carries 2, 3, 8, 9 and 13, by their 0-based roster indexes.

- **Carry 13** (triage P551, S14-BRIEF-OVER-FIVE), built first. Without `--part`, `dispatch_group` refuses a fixer for a group holding more than `PART_CARRIES` (5) pending carries (`roster_lib.pending_carries`, legacy read through `roster_lib.read_legacy`), and the one-line refusal prints the split from `part_split`: index-ordered fives, with a remainder of `PART_FOLD` (2) or fewer folded into the last part. Non-contiguous pending indices print as runs (`0-1+3-6+9`). `--part k` adds one generated line after the brief's generated lines (`Part k of N: build carries a-b; the others are later parts dispatched at this part's handoff; answer none of them`). For k over 1 the topic is `<topic>-p<k>`, and `dispatch_group` refuses it when that topic equals another roster group's topic (its `resume.branch` less `handoff/`) or its normalized id: one line naming the group, nothing published. Both halves and the self-exclusion are pinned (`part-coll-topic-off`, `part-coll-id-off`, `part-coll-self-off` below). The comparison is un-normalized on the topic side: a branch spelled with upper case or `_` escapes it (round-2 review follow-up, routed there to R10-REVIEW-DISPATCH-RESIDUE). The other derived names (Carries 2, 3, 8, 9: prompt text only) derive no topic or ref. These refuse: a part past N, `--part` on a group of five or fewer, `--part` for any role but the fixer, and `--part` without `--group`. Parts are not defaulted (P551's narrowing), and `tools/plan/durations.json` is not read.
- **Carry 8** (P437 C2). The reviewer's `_prompt` text gains three things. Every stop path pushes a verdict to its probe ref: a setup or hook refusal pushes `Fix review: blocked <head> seat-refused: <the refusing line>`. The seat never ends its turn while a background poll runs, and it reads the ref back with `git ls-remote` and pushes again on a miss. On the PR path, a review_packet `required-red` does not stop the seat while classify prints WAIT, because classify decides. WAIT keeps its existing bound of about 30 minutes of polling, which sits inside the returners' 37 to 66 min whole-seat range. Past it, a complete review returns `pending-ci:` as before (R10-DISPATCH-AT-HANDOFF's pending-ci route, 5cdc0bb350), and an incomplete one pushes `Fix review: blocked <head> ci-wait: <the last classify line>`. The at-handoff reviewer has no CI wait, so it gets no `ci-wait` path.
- **Carry 9** (tvofi 2026-11-09). `FRUGAL_LINE` drops "at most 5 inline search operations per prompt". On a guard refusal the seat now dispatches a haiku or sonnet Agent subagent, and the line forbids setting FRUGAL_ALLOW_INLINE and editing .claude/settings.json. The self-test pins the whole line verbatim. Neither `instruments/cloud_dispatch.py.md` nor `r10_flow_dispatch_mutants.py` quoted the old line, and `git grep -n "at most 5 inline"` at the merge base returned only cloud_dispatch.py:140. Role-contract pointer: judged not needed, so no finding goes to part 5. Every dispatched seat's prompt carries the line once (pinned in the self-test for every role), and the guard's own refusal text names the delegation. A pointer in fixer.md or fix-review.md would be a second copy of the rule, which `finding-propagation.md` says goes stale unevenly.
- **Carry 2** and **Carry 3** were already built on main by R10-DISPATCH-AT-HANDOFF, under its own indexes 4 and 8 (`roster_lib.consumers_of` / `brief_lines`, `prepr.sh` step 7e's `carry targets` info lines; `resolve_model`, `LIGHT_REVIEW_MODEL`, `--carry-only`, `--record-pr`). This part adds no production line for them. It proves their pins with the mutants each carry names, re-created as harness entries and quoted below.

The mutant harness `dev/audit/harnesses/r10_flow_dispatch_mutants.py` was stale at the merge base: it aborted at its third mutant (`abort: brief-drop's pattern occurs 0 times`). Four patterns no longer matched (brief-drop, cli-nonce-dropped, cli-model-fixed, cli-overlay-dropped); they are re-aimed at the current text. A mutant may now name `roster_lib.py` as a fourth element.

Not built in this part: Carry 1, Carry 4, Carry 5, Carry 6, Carry 7, Carry 10, Carry 11, Carry 12, Carry 14, Carry 15, Carry 16, Carry 17, Carry 18, Carry 19, Carry 20, Carry 21, Carry 22, Carry 23, Carry 24, Carry 25, Carry 26. Each belongs to another part of this group's split (triage P551, by file); part 3 answers none of them. Carry 0 is not listed here because the review packet does not hold it open.
- Carry 27 and Carry 28: left for a later part; each stays on the roster.

Round 3 (this repair): the round-2 rewrite of the part-topic line had left the harness's `part-topic-dropped` pattern at no occurrence, so the drive aborted. It is re-aimed at the current line. The self-test gains R10-ALIAS (another id whose branch is `handoff/r10-clash-p3`) and R10-SELF-P2 (a part topic equal to its own id, which publishes), so the predicate's topic and self halves die alone. Three diff-mode production survivors the review listed are now killed: the fold's `len(parts) > 1` guard (`part_split` over one and two indices, through `split_any` so the mutant fails a named check rather than the run), the runs printer's first gap (`part_split([0, 2, 3]) == "0+2-3"`), and `--part` without `--group` (the CLI arm). The two production survivors left are answered under `## Unpinned sites`.

Round 4 (this repair, the block `mutation-vacuous: fixer-guard-off readback-nonce legacy-refusal-swallow`): three pins in the self-test, each also a harness entry. `fixer-guard-off`: a non-fixer seat (probe) of the 21-carry group dispatches unrefused, beside the fixer's refusal as the null. `readback-nonce`: the flag-path reviewer uses a 16-character nonce, and the prompt must name `probe/rev-7-<first eight>` twice (push and read-back) and never the longer form. `legacy-refusal-swallow`: a cut-over sha the clone cannot read, on the `--part` path, must refuse with the cut-over text rather than crash.

## Head

9b6fdcd4fc6953d4387b7b2b31aad138bcf92a45, on merge base cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf; origin/main at ee64358be7eeccaec5178a923cb3b83a18a924a0 (2026-11-11), against which `git merge-tree --write-tree origin/main HEAD` is clean, so no merge.

## Mutation proof

`python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py`, run end to end in the worktree at the head: each mutant applied alone, `cloud_dispatch.py --self-test` run, the file restored. This part's mutants, as that run printed them:

- `RESULT mutant=fixer-guard-off failed=1 verdict=killed` -- `FAIL a seat that is not the fixer's dispatches a group of 21 pending carries unrefused (null: the fixer refuses)`
- `RESULT mutant=readback-nonce failed=1 verdict=killed` -- `FAIL the verdict ref and its read-back both carry the nonce's first eight characters, not the whole nonce`
- `RESULT mutant=legacy-refusal-swallow failed=1 verdict=killed` -- `FAIL a --part dispatch whose cut-over roster the clone cannot read refuses naming the cut-over, not crashing`
- `RESULT mutant=brief-drop failed=11 verdict=killed` -- `FAIL a group with no carry, consumer or enumeration renders its brief and `After:` alone (the null control)`
- `RESULT mutant=part-collision-off failed=1 verdict=killed` -- `FAIL a part whose topic is another group's id (R10-CLASH-P2) or branch (R10-ALIAS) refuses naming it; part 1, a free part and a part that is its own group's id (R10-SELF-P2) publish`
- `RESULT mutant=cli-nonce-dropped failed=3 verdict=killed` -- `FAIL --group forwards --nonce to dispatch_group`
- `RESULT mutant=cli-model-fixed failed=3 verdict=killed` -- `FAIL --group forwards --model to dispatch_group`
- `RESULT mutant=cli-overlay-dropped failed=3 verdict=killed` -- `FAIL --group forwards --overlay to dispatch_group`
- `RESULT mutant=wait-line-dropped failed=1 verdict=killed` -- `FAIL every role's prompt caps one tool call's wait under the 5-minute prompt-cache TTL (R10-FLY-CACHE-PROMPTS)`
- `RESULT mutant=part-count failed=5 verdict=killed` -- `FAIL a fixer for a group with 21 pending carries (a marked 22nd not counted) refuses, printing the split`
- `RESULT mutant=part-refusal-off failed=1 verdict=killed` -- `FAIL a fixer for a group with 21 pending carries (a marked 22nd not counted) refuses, printing the split`
- `RESULT mutant=part-prefilter failed=1 verdict=killed` -- `FAIL a fixer for a group with 21 pending carries (a marked 22nd not counted) refuses, printing the split`
- `RESULT mutant=part-fold-off failed=5 verdict=killed` -- `FAIL a fixer for a group with 21 pending carries (a marked 22nd not counted) refuses, printing the split`
- `RESULT mutant=part-fold-one failed=1 verdict=killed` -- `FAIL the split folds a remainder of one or two into the last part, and only that`
- `RESULT mutant=part-pending-raw failed=3 verdict=killed` -- `FAIL a fixer for a group with 21 pending carries (a marked 22nd not counted) refuses, printing the split`
- `RESULT mutant=part-topic-dropped failed=3 verdict=killed` -- `FAIL --part 2 renders the topic <topic>-p2 and one generated line naming carries 5-9`
- `RESULT mutant=part-coll-topic-off failed=1 verdict=killed` -- `FAIL a part whose topic is another group's id (R10-CLASH-P2) or branch (R10-ALIAS) refuses naming it; part 1, a free part and a part that is its own group's id (R10-SELF-P2) publish`
- `RESULT mutant=part-coll-id-off failed=1 verdict=killed` -- `FAIL a part whose topic is another group's id (R10-CLASH-P2) or branch (R10-ALIAS) refuses naming it; part 1, a free part and a part that is its own group's id (R10-SELF-P2) publish`
- `RESULT mutant=part-coll-self-off failed=1 verdict=killed` -- `FAIL a part whose topic is another group's id (R10-CLASH-P2) or branch (R10-ALIAS) refuses naming it; part 1, a free part and a part that is its own group's id (R10-SELF-P2) publish`
- `RESULT mutant=part-split-one failed=1 verdict=killed` -- `FAIL the split folds a remainder of one or two into the last part, and only that`
- `RESULT mutant=part-runs-skip failed=1 verdict=killed` -- `FAIL the split folds a remainder of one or two into the last part, and only that`
- `RESULT mutant=part-cli-nogroup-open failed=1 verdict=killed` -- `FAIL the CLI forwards --part to the group path, and refuses it without --group`
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

Failing test first: at b64fbe44, `part-coll-topic-off` (the topic side replaced with `""`) applied to the unchanged file left `cloud_dispatch.py --self-test` with no failure; at the head the drive line above reads `verdict=killed`.

## Null control

`RESULT mutant=M0 failed=0 verdict=null-ok`: the unmutated file passes. The collision arm's own null: part 1 of R10-CLASH, `--part 2` of R10-SPLIT and `--part 2` of R10-SELF-P2 publish (`part-coll-self-off` fails it by refusing the last). Per carry, pre-existing arms: Carry 13 `five pending carries (a moved sixth not counted) dispatch unrefused, the brief byte-identical (null control)`; Carry 8 `no other role is told any reviewer stop push (null control: the fixer prompt carries none)`; Carry 9 `and no prompt grants an inline allowance the guard does not`; Carry 2 `a group with no carry, consumer or enumeration renders its brief and \`After:\` alone (the null control)`; Carry 3 `a roster ruling opus for the reviewer still resolves opus for a first-round review (null control)`.

## Unpinned sites

- `cloud_dispatch.py` prefilter `len(group.get("carry") or []) > PART_CARRIES` as `>=` (diff-mode CMP_BOUND): equivalent on output. A group of exactly five raw carries has at most five pending, so `part_line` returns "" either way; only the legacy-roster read is added, whose failure is the roster's own `RosterNotFound`. Disposition: equivalent mutant, answered here.
- `carry_only: bool = True` in the re-flowed `dispatch_group` signature (diff-mode CONST_SWAP): a pre-existing default, in scope only because the line was re-flowed; this part changes no behaviour of it. Disposition: pre-existing, outside this part.

## Figures

- `python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py` at the head: `RESULT mutants=66 survived=0`, rc=0; `RESULT mutant=M0 failed=0 verdict=null-ok`; 5 `verdict=CRASHED` (parent-drop, topic-to-id, head-ignored, roster-repo-ignored, pointer-off: pre-existing mutants, none of this part's); each of this part's is `verdict=killed` with the FAIL line under Mutation proof.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

- `node tools/policy/agreement.mjs --py-json` at the head prints `refused=2` (merge-subject-pr on b64fbe44a and 73acdd0b6, local merges of earlier rounds already in main's history through #3450); at origin/main e59e21fe it prints `refused=0`. This repair adds no merge commit.

## Red checks

none

## Forward-carry

none

## Friction

- review-packet-brief-carries: contradiction: `review_packet.py handoff` refused this part's body for group carries the part's brief says to answer none of (`REFUSE brief-carries: carry 1 is not named in the body`). A `--part` brief (Carry 13) states the same instruction, so every part body must restate the other parts' carries until the packet reads the part's own range. Carry: dismissed: the group is carries-open with no live owner of review_packet.py's range reading, and this part's brief forbids building another part's carry; the restated list in this body satisfies the packet, and the contradiction stays visible to the next part's seat here
