Fix review: merge 8978e0437c46a10207dd682057665a214453e083

bus-nonce: 0588ef2115c4f4374d781ec52ba29609

Round 1 of this review. Measured head 8978e0437c46a10207dd682057665a214453e083; origin/main merges cleanly (merge-tree exit 0).

## Findings

- Residual: live local seats must pin the numbered identity or the guard now refuses their push; that pin lives outside the tree, as the body notes. Carry: dismissed: owner-side launch configuration the body already names for the orchestrator, no tree change owed.

## Evidence

- merge_train.py classify at head: GREEN, pending none, red none. The only red in the digest is governance / delivery-status, not a required check.
- ref_privacy.py --self-test at head: 124 checks, 0 failed (body figure matches).
- Mutant 1, email_shape returns [] early: 124 checks, 7 failed (body: 7). Mutant 2, digits requirement made optional in _NUMBERED: 124 checks, 5 failed (body: 5). Both restored with git checkout.
- plan_audit.py --self-test 27 checks 0 failed; delivery_row.sh --self-test 6 checks 0 failed; app_push.sh --self-test 227 checks 0 failed (the earlier red).
- VERSION, manifest version and RELEASE_NOTES heading untouched in the diff; no claim or golden file touched.
- Callers of the guard (body_push, bus, handoff_push, heartbeat, cloud_dispatch) pass through ref_privacy.py; none writes a placeholder identity into the tree per the body's writers grep.
- Not re-derived: the 47-lines-in-12-files census figure and the macOS-only prepr self-test failure; neither affects the verdict.
