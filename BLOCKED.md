BLOCKED: R10-HOTFIX-SELFTEST-TIMEOUT repair round 2, body push refused.

Code: handoff/r10-hotfix-selftest-timeout = 6301ec8864e229b27c9d65964ef65bb2d8b5e201 (X8 arm; harness RESULT survivors=0 over M1, M2, X8; scoped gate rc 0; structure, selftest_wiring and prepr.sh rc 0; body-check rc 0).
Body: refused, kept at handoff-wip/r10-hotfix-selftest-timeout-body 7b441f3f04a5d28b044a420f8d71e09abc2eae05.

Refusal: body_push.sh's CARRY-LANDED check: `CARRY-MISSING R10-HANDOFF-PATH body item d01fdda0`. Item 2's carry (a deterministic mut:unlock in pr_args.sh) is routed to R10-HANDOFF-PATH, and must be on the round's roster branch before the body pushes. Landing it (carry_audit.py land-ops, an append-carry applied by roster_queue.py) writes handoff/audit-r10-roster, a branch this seat may not write.

Question: will the queue runner land that carry on R10-HANDOFF-PATH (text in the kept body's Forward-carry), so the body can be re-pushed unchanged? Or should it be routed elsewhere? Re-labelling it "dismissed" to pass would misstate it, so I did not.
