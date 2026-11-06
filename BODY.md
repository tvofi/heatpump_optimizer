Partial delivery of R10-DISPATCH-AT-HANDOFF: carries 2, 5 (part 2), 9, 13, 14 and 15 in `bus.sh` and `review_packet.py`. Carries 0, 1, 3, 4, 5 (part 1), 6, 7, 8, 10, 11 and 12 are not built here; each is listed under Forward-carry with its reason.

## Head

afdba1609385cf6e3bda5e708828c31e516cfba2

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

Built: P344 autofix hold (carry 2), second reviewer at a merge-verdict head (carry 5 part 2), P348 blocked-verdict carry (carry 9, already in the tree before this branch: `verdict_at`), P368 (carry 13), P354 (carry 14), P374 (carry 15). The three-round refusal of carry 7 and the concluded-red refusal of carry 6 were already in `three_rounds` and the `classify` call; this branch adds no new text for them. Carry: dismissed: built in this diff or already in the tree

Not built, for want of time in this seat; each stays in the roster entry of R10-DISPATCH-AT-HANDOFF, which must not be closed on this merge:
- Carries 0 and 1 (dispatch at the handoff ref) wait on the owner's policy text for `fix-review.md` and `standing-dispatch.md`. Carry: R10-DISPATCH-AT-HANDOFF
- Carry 3 (refuse on a carry_audit, figure_lint or moved-head red in the packet). `review_packet.py` already refuses on carry_audit and head-note; figure_lint is only rendered, not a signal. Owner ruling of 2026-10-24 stands: dispatch never waits for CI. Carry: R10-DISPATCH-AT-HANDOFF
- Carry 4 (brief lines in `cloud_dispatch.py`), carry 5 part 1 (`review_carry.py` patch-id), carry 6 (hold on a pending required context or an unanswered red; it amends the 2026-10-24 ruling, so the owner approves the policy text at the merge), carry 8 (model routing), carries 10 and 11 (dependabot rows and body patch), carry 12 (pending-ci drafts). Carry: R10-DISPATCH-AT-HANDOFF

## Friction

none
