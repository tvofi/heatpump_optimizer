Fix review: merge 3bf9c454d969bec3e93bfed75d9ff027754a271d

Merge-delta check for #1805 (R9-F1.9). The head moved from e54fb07a to 3bf9c454 when the Mac merged main a413832a (#1803, F10.2) into it. The code head is still cf0d1103, which carries a full merge verdict (evidence: F1.9-review-cf0d1103/).

RESULT tree: `git merge-tree --write-tree e54fb07a a413832a` exits 0 with tree d44d5d19. 3bf9c454^{tree} is also d44d5d19, so the merge is exactly the clean automatic merge.
RESULT delta_vs_main: `git diff a413832a 3bf9c454` gives the same 13 files and +277/-26 lines as F1.9's own diff against its merge base. Nothing else comes in.
RESULT structure: `tests/structure.py` at 3bf9c454 prints STRUCTURE RATCHET PASSED, rc 0. coordinator_loc and max_class_loc are still 9014, so F10.2 did not touch them.
RESULT scope: `closure.py select --diff a413832a` prints MODE: SCOPED -- 18 script(s) run.
CI on 3bf9c454 at 08:27Z:
- green: typing, closure-scope, budget-raise-gate, pr-contract, policy-docs, briefs, delivery-status, nightly-status, wave-script, instrument-self-tests, hassfest, validate-hacs, CodeQL js/actions
- running: fast (3.14), mutation, closures, coverage, browser, env-matrix, CodeQL python
- red: none
The Mac merges only once all of these finish green.
