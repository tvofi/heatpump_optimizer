merge 65814159824c4b7d8de9cc99339fa837ae290d4b delta-clean

# #1799 (F1.8) fix review: delta verdict at head 65814159

Reviewer: opus review seat. This is a delta review over round 3 (94f6909b) and round 4 (f0147b7a). The full gate and the mutation table were not re-run here; the review cites the head's CI.

## The delta since round 3
- 7d372cba: the typing fix. identity_update returns `str | UndefinedType` and is passed as `unique_id=`. The sensor unit locals are annotated. The hastub gains the `helpers.typing` sentinel, and harness.py's FakeConfigEntries skips UNDEFINED as upstream does. Verified locally on the pinned toolchain: ALL 9 typing-ruler checks PASSED.
- 6f0627c5: a Linux re-record of the 16 closures that were under-scoped by the new stub, plus harness_headers' helpers/__init__. Only tests/closures.json changed.
- 9380337e: 18 killed_by pins via `--pin-killed`, 0 left unpinned, no survivors. Each anchor is a site this PR adds: identity_update, _save, _money, _price_feed, _feed_currency, _audit_price_units, declared_currency, money_scale, fee_bound, spec_problem and the sensor unit property.
- Merges of main 0ba354c5 and d62b99a5 are clean.

## CI at 65814159 (re-read head confirmed 65814159 before posting)
- Green: mutation (job 110184994652; the table runs against 0ba354c5 with no unpinned growth), fast (3.14), closures, typing, coverage, coverage-ratchet, pr-contract (both runs), briefs, closure-scope, hassfest, validate-hacs, CodeQL and Analyze, instrument-self-tests, policy-docs, delivery-status, browser and graders-head-copy.
- The autofix jobs are skipped, since nothing was owed.
- Red: budget-raise-gate only. That is by design, and it clears on the approving review at this head.

## Red checks (step 11)
Every red check this PR has seen is named and answered in the body (pr-contract is green, so its lint agrees). The round-4 reds were closures, closures-autofix, fast (3.14), mutation and mutation-autofix. They had a single cause, the unclassified hastub typing.py, and the cheaper detector was prepr.sh's closures step plus tests/entities.py before handoff.

## Structure raise 116 -> 117 (coordinator_multiassigned_attrs)
Re-measured at 65814159: STRUCTURE RATCHET PASSED; multiassigned 117 <= 117; coordinator_methods 224 <= 224.
The raise is still the architecturally right call. `self.currency` is one attribute with two writers: its initial value in `__init__` and its per-cycle adoption in `_update_current_state`. That is the same pattern as the other 116.
There are two ways to avoid it, and both are worse:
- (a) a setter or helper method, which costs a coordinator method at zero headroom (224/224);
- (b) moving the state to sensor.py, which touches 13 read sites and splits ownership of the published currency.
The round-2 attempt to hide the second writer behind a lambda property was blocked as evading the ratchet, and it stays blocked.

## Other judgements carried forward
- The sensor.py borrow (outside the plan) is necessary and minimal. Without the base unit property, the EUR replay stays 11/11 mismatched.
- tests/harness.py is code-owned. Its change is a faithful one-line mirror of upstream's UNDEFINED handling, so the owner approval for it, given by the orchestrator under the mandate, is appropriate.
- No open findings.
