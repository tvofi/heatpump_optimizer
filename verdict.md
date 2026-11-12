Fix review: merge ef4556bb4241560de9862a5b856153aab4ff5584

bus-nonce: be4c7874d754f378d5f64cca6aa51525

## Round

First round, at the handoff (no pull request yet). Head reviewed: ef4556bb4241560de9862a5b856153aab4ff5584, base 0b276e8c0cd4ddbcf5c5e0adfe179af00441e7f3; the body's `## Head` names the same SHA (step 7). Role contract unchanged on main since the merge base (`git diff` of dev/governance/roles/ empty).

## Evidence

- No pull request exists, so there is no review packet and no CI to read: no check run exists at this head, step 11 has nothing to answer, and the body's `## Red checks: none` is consistent with that. `merge_train.py owed-reds` prints tests / mutation, tests / typing, validate / validate-hacs.
- Merge with main: `git merge-tree --write-tree origin/main <head>` exits 0 (ev/merge-tree.txt); no conflict, no claim-file driver invoked.
- Pull-request arm, planted ratchet breach (ev/plant.py, ev/plant.out; the driver drives `gate.judge` with a faked jobs listing at the base tree and at the head tree): RESULT event=pull_request red=tests / fast (3.14) (the job running tests/structure.py) outcome FAIL at base and at head; red=tests / ci-ratchet outcome PASS at base and at head (ci-ratchet's job has `if: github.event_name == 'push' && ref == main`, so it never runs on a pull request and was never owed there; at the head it is now listed as a note instead of being silently absorbed into the owed set); red=tests / coverage-ratchet PASS at base and at head. REQUIRED["pr"], REQUIRED["pr-cc"] and REQUIRED["no-pr"] are identical at base and head (dumped in ev/plant.out). The pull-request arm lost nothing: every outcome is unchanged.
- Push arm, same driver: red=tests / ci-ratchet: base FAIL tests / ci-ratchet, head PASS with `machinery (report-only, never gating): tests / ci-ratchet=failure`; red=tests / coverage-ratchet: FAIL at both; red=tests / fast (3.14): FAIL at both; all green: PASS at both. Only ci-ratchet moved, as Q1 rules.
- Pre-existing at base and unchanged here: on a pull_request event a red `tests / coverage-ratchet` passes the gate and is not even listed as a note, because the owed set is REQUIRED's union over every event class. This PR neither introduces nor touches it.
- Mutation proof (ev/mut.out): unmutated self-test 91 checks, 0 failed (base: 87, 0 failed). M1 PUSH_ONLY with ci-ratchet put back: 3 failed (the three checks the body names). M2 coverage-ratchet dropped from PUSH_ONLY: 3 failed. M3 machinery line on every event: 2 failed. M4 machinery line never: 2 failed. M5 machinery line including owed jobs: 2 failed. No survivor.
- Harness (finder's, dev/audit/harnesses/r10_ci_gate_core.py b3): base GREEN / --plant RED (ci-ratchet dropped); head GREEN / --plant RED (coverage-ratchet dropped). Both ends confirmed.
- Body figures re-derived at the head: gate self-test 0 failed; b3 GREEN/RED; stamp.py --self-test RESULT stamp_self_test=pass; closure select MODE: FULL; structure.py STRUCTURE RATCHET PASSED; merge_train.py --self-test 656 checks, 0 failed (ev/mt.out). `prepr.sh` rc=0 was not re-run: not re-derived.
- Step 4/5: VERSION, RELEASE_NOTES.md, manifest and tests/golden untouched; the PR claims no drift and moves no fixture.
- Step 14: the fixture required-contexts.json loses exactly tests / ci-ratchet, earned by the PUSH_ONLY change (M1 re-adds it and the fixture check fails). No budget, closure or claim file moves.
- Step 6 class: one seam (gate.py's push set); stamp.py's docstring, entities.py's comment and merge_train.py's item-11 check are the other pins of the push set, all moved in the diff.

## Findings

- The b3 parity harness now reads its exemption list from the port it grades (`port.PUSH_REPORT_ONLY`): a plant moving coverage-ratchet from PUSH_ONLY into PUSH_REPORT_ONLY leaves b3 GREEN (ev/more.out), so the harness alone no longer detects a required push job being made report-only. Carry: dismissed: gate.py's own self-test kills that plant (91 checks, 3 failed, ev/more.out), so the port is still pinned; no stage needs to change.

## Friction

none
