Question: how may carry 15 be answered so the carry audit routes it?

Code is pushed at handoff/r10-standing-contracts-p2 907c15d37 (carries 21, 22, 23, 27 built; carry 16 dismissed, implemented at ae1971474; carry 24 not built).
body_push refused twice with `REFUSED BODY-LINT`; the audit says: UNROUTED body item [owed carry] 'Carry 15: dismissed: implemented at e199f727 (handoff/r10-standing-contracts-p2-p4, built by the other part)'. Writing `Carry: R10-STANDING-CONTRACTS-P2` on it gives BAD-DEST (the group is carries-open, 'valid targets: none live after R10-STANDING-CONTRACTS-P2').
Same BAD-DEST for a forward-carry of carry 24 to R10-FIXER-MD-SPELLING-CORPUS or to this group. Carry 24 (fixer.md citation vs the layout guard) needs a grader-first p1: tools/policy/policy_lint.mjs drops the docs/decisions/0011 citation-presence pin and fixer.md cites decision 0011 in prose; built here, prepr's ci_predict refused it as BOOTSTRAP (the base's policy_lint refuses the change), so it was reverted from this head.
Body is kept at handoff-wip/r10-standing-contracts-p2-body 1232c3a2.
prepr on 907c15d37: only the body/carry arms red (BAD-DEST above); every other step ok. Push of the wip step ref with force-with-lease was denied by the harness, so this note sits on the old wip tip.
