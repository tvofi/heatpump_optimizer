Fix review: merge 16c628e4ad0232a74f7f8732cdb59fe5b711d24e

bus-nonce: e2a363efe8881d2c984f66ed00437ef6

Round: resume of the review at this same head (prior verdict probe/rev-3377-6e7334c5@39ce7dfb blocked solely on ci-red). Head unchanged.

## Evidence

- CI: `merge_train.py classify 16c628e4ad0232a74f7f8732cdb59fe5b711d24e --pr 3377` exits 0: `GREEN ... pending: none red: none` (ev/classify.txt). The prior block was a premature "still being judged" gate deferral at 00:29Z; the later gate run succeeded and the required context now reads green.
- Reused from the prior verdict (CI-independent, head unchanged): merge of main (cb41886655) leaves s6-batch130/131 equal to origin/main (ev/batch130-131-vs-main-difflines.txt); d1f929f3da changes only paths in s6-batch219/234, no ruling text (ev/delta-d1f929f3.diff); 3781e7741d appends one carry to R10-DUTY-SWITCH-PLANNER-PRICE, roster JSON loads (ev/delta-3781e774.diff).
- brief_lint on the roster: 2 pre-existing errors (supply_hold.py absent; carry_fold_arm at 812 not 808), identical at the earlier reviewed head 3bdc73b33650, so not in this delta (ev/brief_lint-roster-head.txt). CI briefs and wave-script are success.
- Merge with main: `git merge-tree --write-tree origin/main 16c628e4ad0232a74f7f8732cdb59fe5b711d24e` exit 0, no conflict.
- tests/entities.py was run with env -u BASH_ENV and failed before checking anything: ModuleNotFoundError homeassistant at tests/harness.py:29 (this seat lacks the module). Not re-derived; CI's closures, fast, closure-scope and policy-docs checks at this head are success and stand in for it.
- Production code (custom_components/) is not in the delta; no mutation or both-ends measurement applies to a record PR.
- RESULT cloud-setup --check: OK. RESULT classify: GREEN (rc 0).
