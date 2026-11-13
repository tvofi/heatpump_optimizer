Fix review: blocked 16c628e4ad0232a74f7f8732cdb59fe5b711d24e ci-red: required context gate is RED per merge_train classify (rc 1); the red run is a premature "still being judged" gate at 00:29Z, a later gate run at 01:16Z is success

bus-nonce: 6e7334c591ffa33ad58bd05fadf2c400

Round: later-round delta review (earlier verdict: merge at 3bdc73b33650). Measured head 16c628e4ad0232a74f7f8732cdb59fe5b711d24e.

## Block

`merge_train.py classify 16c628e4ad0232a74f7f8732cdb59fe5b711d24e --pr 3377` exits 1: `RED ... pending: none red: gate`. Reading the head's check runs: the red `gate` is job 131596427572 (run 43332154335, 00:28:56Z-00:29:35Z), whose log ends "FAIL run(s) [43332153169] at this head are still being judged; their gate decides". The `gate` job 131615044102 of run 43332153169 completed success at 01:16:23Z, after pr-contract / pr-contract (success, 01:10Z), tests / coverage-ratchet, lane-proofs, graders-head-copy, mutation, closures, fast, browser, typing (all success). So the red is a timing artifact, not a defect of this head; I cannot clear it from here (no re-run, no comments). Re-run the failed gate (or push-neutral re-trigger by the orchestrator) and classify again; nothing in the delta below needs a change. If the train reads that rerun GREEN, this verdict converts to merge with no further review.

## Evidence

- Delta read: `git diff 3bdc73b33650 16c628e4ad0232a74f7f8732cdb59fe5b711d24e` is mostly main's content brought in by the merge (794 files); the PR's own resolution was read as three pieces.
- Merge of main (cb41886655): dev/programme/triage/s6-batch130.md and s6-batch131.md equal origin/main's (`git diff origin/main 16c628e4ad0232a74f7f8732cdb59fe5b711d24e -- ...` = 0 lines, ev/batch130-131-vs-main-difflines.txt), so main's later rulings (P362 duplicate, P402 already landed) stand; batch130 is unchanged against the earlier reviewed head, batch131 differs from it by main's text only.
- d1f929f3da: only s6-batch219.md (5 edits, /Users/timmalmstrom/hpo-orch/... -> ~/hpo-orch/...) and s6-batch234.md (line 24, retired docs/decisions/ -> dev/governance/decisions/, which exists in the tree). No ruling text changed (ev/delta-d1f929f3.diff). `grep timmalmstrom dev/programme/triage` is empty.
- 3781e7741d: appends one carry to R10-DUTY-SWITCH-PLANNER-PRICE in dev/programme/rosters/wave-r10-groups.json, ending `Carry: R10-DUTY-SWITCH-PLANNER-PRICE (items c3ad1545)`; no ruling text elsewhere changed (ev/delta-3781e774.diff). The roster JSON loads (json.load ok).
- brief_lint on the roster: 2 errors (R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE supply_hold.py not in the tree/tag; R10-RELAY-NOBODY-STALL cloud_relay.sh:808 carry_fold_arm found at 812). The same 2 errors print at the previously reviewed head 3bdc73b33650, so neither is in this delta (ev/brief_lint-roster-head.txt). CI's `tests / briefs` and `governance / wave-script` are success at this head.
- Merge with main: `git merge-tree --write-tree origin/main 16c628e4ad0232a74f7f8732cdb59fe5b711d24e` exit 0, no conflict.
- tests/entities.py could not be run in this seat: the checkout lacks the homeassistant module (ModuleNotFoundError at tests/harness.py:29), so the first run in the brief's form failed before checking anything. I did not re-derive it; CI's closures, fast, closure-scope, arch-instrument, env-matrix and policy-docs checks at this head are success and stand in for it.
- Production code (custom_components/) is not in the delta; no mutation or both-ends measurement applies to a record PR.
- RESULT cloud-setup --check: OK. RESULT classify: RED gate (rc 1), see Block.
