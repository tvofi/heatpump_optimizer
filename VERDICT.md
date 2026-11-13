Fix review: merge f971a17a03288d763ffdd592bf19eaefc7b9cbfa

bus-nonce: 2a024896f6459ce839e007c937c2f78d

## Round

First review (round 1), full scope, of R10-ROUND-PLAYBOOK-FINAL part 2. A policy and record PR: dev/audit/README.md, dev/programme/HANDOVER.md and the delivery row dev/programme/delivery/3550.md. No `custom_components/` line. The owner's approving review is still owed at this head because dev/audit/README.md is policy. This verdict does not stand in for it.

## Findings

- The body's sentence "Carry 31's D11 and D13 paragraphs were not found in R11-INTAKE-R10-RESIDUE at the roster branch tip I read" is false at the head's roster state. It may have been true at an earlier tip. Roster commit c01f40f5c (handoff/audit-r10-roster, an ancestor of the current tip 66b81ca477) moved R10-ROUND-PLAYBOOK-FINAL carry 31 into R11-INTAKE-R10-RESIDUE as its carry index 25. That carry is "Add one paragraph each to dev/governance/dimensions/D11.md and D13.md ...". c01f40f5c's parent 31e7b09d25 holds 0 copies of it. The same batch landed this body's three routed carries as indices 41 to 43. So the body's newer note ("landed ... at c01f40f5c") is true, and the older sentence is stale beside it. Roster carry 41 now reports as missing something that roster carry 25 holds. The README's text ("Carry 31 goes with it: one paragraph each in D11.md and D13.md ...") is true. Intake should dismiss carry 41 as superseded by carry 25 and not build the paragraphs twice. Carry: R11-INTAKE-R10-RESIDUE
- HANDOVER records "R10-SEAT-SCRIPT-OUTPUT, open #3490 at 0e64c66e3b: nothing". Since then, origin/main merged #3490 at 5288db5dad, second parent b7c9734095, which is a descendant of the head this PR read. At this head's merge base 3b9749dac5 the line was true. On current main the "open" is stale, and the head that merged was never re-read. That falls to the closure re-check the body already records as pending owner confirmation, and it now covers a merged PR, not an open one. Carry: R11-INTAKE-R10-RESIDUE
- No finder's harness is committed for this group (fix-review step 9). This is a policy and record edit. The only committed instrument that reads it is brief_lint's playbook path check, and I ran it as the mutation proof below. Carry: dismissed: policy and record diff with no quantified claim beyond the lint figures re-derived under Evidence

## Evidence

- Head measured: f971a17a03288d763ffdd592bf19eaefc7b9cbfa (ev/HEAD.txt), the same as the PR head and the head in the body's `## Head` section. The body also has a bare line 6d39a63552 under `## Head`. It is an ancestor commit ("README: cite the census directory ..."), not a second head.
- Merges with origin/main: `git merge-tree --write-tree origin/main <head>` rc=0 (ev/merge_tree.txt). The head is behind main by #3490's merge, but the merge is clean.
- Mutation proof, re-run in a scratch worktree. Renaming tools/audit/carry_audit.py made brief_lint print `ERROR [(playbook)] playbook path: tools/audit/carry_audit.py: not in the tree`, TOTAL 1 error, rc=1 (ev/brief_lint_mut_filerename.txt). The body quotes `carry_auditX.py`, which matches renaming the README citation instead. Both mutants are refused. My second mutant renames the new census path in the README to protection-censusX/, and brief_lint refuses it (ev/mutant_census.txt). Restored, brief_lint gives TOTAL 0 errors and `PLAYBOOK ok` (ev/brief_lint_head_full.txt).
- Figures re-derived at the head. `node tools/policy/policy_lint.mjs --budgets` rc=0, with tools/audit/README.md at 315 lines against a cap of 321 and ~6050 tokens against 6059 (ev/policy_lint_full.txt). `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (ev/structure.txt). `node tools/policy/brief_lint.mjs`: 0 errors (ev/brief_lint.txt). The packet's figure_lint gives 3 resolved, 0 not verified, 0 refused.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2711 ENTITY CHECKS PASSED, rc=0 (ev/entities.txt). The docstring's PYTHONPATH is needed: bare venv-ci python3 fails on the homeassistant import.
- Citations at the head: dev/audit/rounds/round10/protection-census/ is a tree. dev/governance/rules/ratchet-budgets.md:110 states "a change proving over 20% improvement", so the 10%-to-20% correction matches its cited rule.
- HANDOVER re-read SHAs: all 13 merged SHAs resolve to the named groups' merge commits and are ancestors of the merge base. The open heads e3622cb3d8 (#3499), 07941da7b5 (#3451) and ece5ee3b58 (#3491) equal their live refs/pull heads. #3490 is covered under Findings.
- Forward-carry (step 10): the three body carries routed to R11-INTAKE-R10-RESIDUE are present as roster carries 41 to 43 at c01f40f5c and at the tip 66b81ca477 (ev/roster_r11_intake_carries.txt). carry_audit at the head: 7 routed, 0 unrouted, 0 bad destinations.
- VERSION, the manifest version, the RELEASE_NOTES heading and both claim files are untouched: the three-dot diff has 3 files.
- Class (step 6): one-seam record edit. No enumeration rule is named or owed, and that absence is not read as compliance.
- CI at this head: `merge_train.py classify f971a17a03288d763ffdd592bf19eaefc7b9cbfa --pr 3550` exited 0 and printed `GREEN f971a17a03288d763ffdd592bf19eaefc7b9cbfa pending: none red: none` (ev/classify_final.txt), after WAIT with no reds from 12:02 to 12:27 UTC (ev/classify.log). No red to answer.
