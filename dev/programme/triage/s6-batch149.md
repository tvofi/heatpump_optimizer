# Proposal triage, session s14, batch 149 (P559 to P560)

This batch rules `s7/triage-queue-s7.txt` line 243, which arrived after batch 148. The line makes two
proposals, so it gets two rulings. The bar and the denominators are batch 141's.

Sources: origin/main `d08ed31049`; the round roster branch at `2f484ff60e`; the bodies seat's
`body_push.sh` logs for r10-tick-residue and r10-worktree-gc-live.

## P559: S14-BRIEF-CARRIES-MOVING-TARGET (brief-carries)

Verdict: ACCEPT. It repairs an observed wrong behaviour: the handoff refuses a finished body for
carries the fixer was never given, and it checks the wrong indexes.

Source: queue line 243 (2026-11-11T01:26:35Z, the bodies seat, r10-tick-residue), first half.

Instances:
- **The moving target.** `review_packet.py` `handoff()` (lines 646-671) counts the group's `carry`
  entries at the live `--roster-ref`. The dispatched brief is fixed at fire time.
  - R10-TICK-RESIDUE's carry count over the roster history: 21 at `2cd3f772f4` (00:16Z, stage
    `in-progress`), then 22, 23, 24, 25, 26 and 27 at `2f484ff60e` (01:22Z). Queue line 4272 (P555)
    makes it 28. Command: `git rev-list` over the roster file, then the `carry` length of
    R10-TICK-RESIDUE at each commit.
  - The dispatch ref `dispatch/fixer-r10-tick-residue` (`ea7df0fc2e`) PROMPT.md holds `Carry 0`
    to `Carry 20`, so the fixer was given 21.
  - The bodies seat's `r10-tick-residue.log4` refused carries 21 to 26 (`26 carries, 6 refused`).
    Its `log5`, two minutes later, refused carry 27 alone (`27 carries, 1 refused`): the roster had
    grown between the two runs. `log6` passed only after the body named every new index. That is
    two `body_push` runs spent on carries outside the brief.
  - A false premise would have looked like a PROMPT already holding 27 carries, or an unchanged
    count since the dispatch. Neither is the case.
- **The index mismatch** (found while measuring; not in the source).
  - `cloud_dispatch.py` line 480 renders `Carry {i}` from `enumerate`, which is 0-based.
  - `review_packet.unnamed_carries` (line 508) checks `range(1, n + 1)`, which is 1-based. So carry 0
    is never checked, and a carry n that does not exist is demanded.
  - `r10-worktree-gc-live.log`: `1 carries, 1 refused`, `carry 1 is not named`. Its brief
    (`dispatch/fixer-r10-worktree-gc-live` `033d532a4a`) holds only `Carry 0`. The refusal is
    wholly the phantom.
  - The final tick body answers `Carry 27: not built in this pull request`. On a 0-based roster of
    27 carries, no carry 27 exists.
  - s13's `carry-dup-study.md` recorded #3317 and #3318 answering phantom carries for the same
    reason.
  - A false premise would have looked like the dispatch rendering `Carry 1:` for a group's first
    carry. It renders `Carry 0:`.

Cost: `review_packet.py handoff` refuses only the carries the fixer's brief named.
- **What it counts.** It reads the `Carry N:` lines of the group's dispatch ref
  (`dispatch/fixer-<topic>`, PROMPT.md) when the clone has one; otherwise a roster sha the
  dispatch records; otherwise the live roster, as today. A local fixer with no dispatch ref is
  unchanged. A repair round's re-dispatch rewrites the ref, so its brief count follows.
- **The index fix.** `unnamed_carries` counts 0-based, as the dispatch renders.
- **Self-test:**
  - a body naming `Carry 0` to `Carry 20` passes while the roster holds 27 carries and the dispatch
    PROMPT holds 21;
  - a body missing `Carry 0` is refused;
  - the null control: with no dispatch ref, a body missing a live carry is still refused;
  - a mutant back to `range(1, n + 1)` fails, and a mutant reading the live roster fails.
- Neither `review_packet.py` (1185 lines) nor `cloud_dispatch.py` has a row in
  `tests/structure_budgets.json`. Command: `git show origin/main:tests/structure_budgets.json |
  grep -n 'review_packet\|cloud_dispatch'`, which printed nothing.

Binding: one carry to R10-REVIEW-DISPATCH-RESIDUE, which holds `review_packet.py` and
`cloud_dispatch.py`. It is `not-started` with no dispatch ref, so there is no PART 2 prefix. Carry
file: `b149-P559.txt`.

## P560: S14-BRIEF-CARRIES-MOVING-TARGET (carry_audit status lines)

Verdict: REJECT. Its premise is false: the grammar it asks for already exists. A second grammar
costs complexity for no gain.

Source: queue line 243, second half. It proposes that `carry_audit` read a `Carry N: not built
here` status line as an answer, not as an owed finding.

Instances:
- **The refusal is real.** `r10-tick-residue.log2` and `log3` refused the body: `UNROUTED body
  item ... [owed carry]: 'Carry 0: not built in this pull request; ...'`. `OWED_CARRY`
  (`carry_audit.py` line 163) matches "carry N ... not built".
- **The answer already exists.** `carry_audit.py` lines 613-616 (from #3318) define the form `Carry
  3: built. Carry: <own group>`. It is a status line on the group's own carry: it lands nothing and
  prints `CARRY-STATUS`.
  - The final tick run used exactly that form. `log6` line 4 reads `CARRY-STATUS R10-TICK-RESIDUE
    body item 1679cb24: a status line on its own carry, lands nothing`.
- **The policy premise is wrong.** The source says finding-propagation.md calls such a marker "never
  a carry". That rule's "not a carry" (lines 97-98) is about a destination `git grep` cannot find.
  An own-group status line names a live group, and `carry_audit` reads it as a status by design.
- A true premise would have looked like no own-group status arm in `landed()`, or a `log6` still
  refused. Neither is the case.

Binding: the cost is a second status grammar in `carry_audit.py` and in `OWED_CARRY`, two forms
every body writer and reviewer must know, against two refusals that cost one seat learning the
existing form. What would reopen it: a measured case where the own-group form is refused or
mis-landed. No carry.
