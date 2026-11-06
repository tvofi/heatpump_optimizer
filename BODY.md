Partial delivery of R10-DISPATCH-AT-HANDOFF, carries numbered 1 to 16 as `review_packet.py handoff` counts them: Carry 3, Carry 6 (second-reviewer part), Carry 10, Carry 14, Carry 15 and Carry 16 in `bus.sh` and `review_packet.py`. The rest are not built here; Forward-carry lists each.

Not built here, for want of time in this seat (each stays in the roster entry of R10-DISPATCH-AT-HANDOFF):
- Carry 1 and Carry 2 (dispatch at the handoff ref) wait on the owner's policy text for `fix-review.md` and `standing-dispatch.md`.
- Carry 4 (refuse on a carry_audit, figure_lint or moved-head red in the packet): `review_packet.py` already refuses on carry_audit and head-note; figure_lint is only rendered. The owner's 2026-10-24 ruling stands: dispatch never waits for CI.
- Carry 5 (brief lines in `cloud_dispatch.py`), the `review_carry.py` patch-id half of Carry 6, Carry 7 (hold on a pending required context or an unanswered red; it amends the 2026-10-24 ruling, so the owner approves the policy text at the merge), Carry 9 (model routing).
- Carry 11 (dependabot delivery row), Carry 12 (dependabot body patch), Carry 13 (pending-ci drafts).

## Head

2d83d4e36a00ccab8aae41cd30e9d729789d2434

## Mutation proof

Each site carries a `# mut:` marker and an entry in `dev/audit/harnesses/r10_seat_selftests_mutants.py` (bus-10 to bus-13, review_packet-own). Measured by hand-planting each mutant and running `bash tools/audit/seat/bus.sh --self-test` or `python3 tools/audit/seat/review_packet.py --self-test`:
- `mut:sametree` (P374) removed: FAIL "a repeated push-verdict of one verdict appends nothing and prints the existing tip (P374)" and the new-nonce null control behind it.
- `mut:confirmlock` (P354) removed: FAIL "a confirm under a live holder's lock waits and moves nothing (P354)".
- `mut:mergehead` replaced by `true`: FAIL "a second reviewer at a head holding a merge verdict is refused, recording nothing".
- `mut:autofixhold` replaced by `if false`: FAIL the rc 3 hold arm and the `--force` arm.
- `mut:ownpr` (literal 0 restored): FAIL hot-file own-pr arm (a) and arm (b).

## Null control

- A verdict with a new nonce (new tree) still appends on `review/<pr>`.
- A dead holder's confirm lock is taken over and released.
- A head with no verdict dispatches; so does one with no autofix job in flight.
- A different open pull request holding an unboarded merge verdict on the same hot file still refuses; two ancestors are excluded neither and both are named.

## Figures

- `bash tools/audit/seat/bus.sh --self-test`: instrument for the check counts and failures at this head.
- `python3 tools/audit/seat/review_packet.py --self-test`: instrument for the review_packet checks.

## Red checks

none

## Forward-carry

Built: Carry 3 (P344 autofix hold), the second-reviewer-at-a-merge-verdict-head half of Carry 6, Carry 10 (blocked-verdict carry; already in the tree before this branch, `verdict_at`), Carry 14 (P368), Carry 15 (P354), Carry 16 (P374). The three-round refusal of Carry 8 and the concluded-red refusal of Carry 7 were already in `three_rounds` and the `classify` call; this branch adds no new text for them. Carry: dismissed: built in this diff or already in the tree

No new finding is carried: the unbuilt carries stay verbatim in the roster entry, which must not be closed on this merge.

## Friction

none
