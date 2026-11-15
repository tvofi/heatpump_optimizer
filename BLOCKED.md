Question: the brief requires the audit-plan.js refusal in this PR (#3633), but no head carrying it can pass governance / wave-script (a required check) while main's check-wave-script.mjs lacks this PR's --open-cards stubs. Which route do you rule? (a) land the grader stubs first in a PR that merges ahead of this one (e.g. move them into part 1, #3620), after which this head goes green unchanged; (b) hand off this head red on wave-script as a WIP until the stubs reach main; (c) restore the split and record part 3 in the roster, as fix review 3633 offered.

Evidence (worktree at ec058220b5, base 416280f5c2):
- python3 tools/pr/ci_predict.py --base origin/main --only graders: "PREDICT governance / wave-script GRADER check-wave-script.mjs REFUSED by the base's copy ... BOOTSTRAP: no change in this pull request reaches the base's copy; move the registration to unpinned data the grader reads, or split p1 grader / p2 artifact", rc 1.
- main's check-wave-script.mjs (pinned in CI, governance.yml "Restore the check source from the base commit") against this head's audit-plan.js: 209 passed, 7 failed (read stub carries no open_rc). Same grader against 416280f5's audit-plan.js: 223 passed, 0 failed.
- No unpinned data route: main's P3 block reads only audit-plan.js and its own stubs; treating an absent listing as empty would be a guess the refusal exists to forbid.

Built and verified at ec058220b5 (ready for handoff once routed):
- 1c2d3af97b: the evaluator/reviewer arm also tries 1 and ["x"]; check_scopes.py --repo . --self-test rc 0 (66/66); reviewer's mutant C7 norm(str(ev.get(k) or "")) -> rc 1, 65/66, that arm alone false.
- ec058220b5: refusal restored (reverses 25dabf079a). Head grader: 230 passed, 0 failed. Failing first, same grader vs 416280f5's audit-plan.js: 224 passed, 6 failed (the six refusal arms). Mutant deleting the `if (lost.length) throw` line: 228 passed, 2 failed (unaccounted, drop-with-no-reason). Null control: the kept/folded arm passes at the head.
