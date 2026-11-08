Fix review: merge 7e9b464acd5289660b0d5a4ef10c7d609dd50c45

bus-nonce: ac25a682b4d9682ab1767a339fb54d0e

Round: first fix review of PR #3333 (R10-POLICY-ROLE-PACK part 2), measured at head 7e9b464acd5289660b0d5a4ef10c7d609dd50c45, merge base bb7dfb9bd6c68548d1a956adc411be91e02965e0. dev/governance/roles/ shows no diff between the merge base and origin/main, so the contract I applied is current.

## Evidence

- RESULT head: the remote ref fix/r10-policy-role-pack-p2 is at 7e9b464acd5289660b0d5a4ef10c7d609dd50c45 (git ls-remote), the same SHA the body's `## Head` names.
- RESULT diff: the three-dot diff touches two files, tools/audit/seat/cloud_dispatch.py (+25/-1) and dev/programme/delivery/3333.md (+1, the delivery row). It does not touch VERSION, the manifest, RELEASE_NOTES.md or any *_budgets.json. No policy file is touched: cloud_dispatch.py is not in CLAUDE.md's policy set and CODEOWNERS does not own it. The body calls it "policy-adjacent", but no owner approval is required by path.
- RESULT self-test head: `cloud_dispatch.py --self-test` reports 129 checks, 0 failed (ev/selftest-head.txt). The two new arms (P398 frugal line; pack render per role) are ok.
- RESULT mutants (each restored afterwards): M1 dropping FRUGAL_LINE from the join is killed (1 FAIL), the body's own mutant reproduced. M2 emitting FRUGAL_LINE twice is killed. M3 removing the pack setup is killed. M4 giving the probe a pack is killed. M5, M6 and M7 survive (see Findings).
- RESULT null control: a comment-only edit leaves 129/0. At the base, cloud_dispatch.py has 0 occurrences of FRUGAL_LINE, so the arms cannot pass there.
- RESULT renderer: `role_pack.py render <r> --out` exits 0 for every PACK_ROLE value: fix-review 31099 B, fixer 42898 B, designer 24461 B, design-review 24101 B. An unknown role prints `role_pack: REFUSE ...` with rc 2, so the prompt's "on REFUSE" fallback is keyed on real output.
- RESULT merge: `git merge-tree --write-tree origin/main 7e9b464acd5289660b0d5a4ef10c7d609dd50c45` gives rc 0, tree 0469adc20507, no conflict.
- RESULT CI: `merge_train.py classify 7e9b464acd5289660b0d5a4ef10c7d609dd50c45 --pr 3333` returns rc 0, `GREEN 7e9b464acd5289660b0d5a4ef10c7d609dd50c45 pending: none red: none` (ev/classify.txt). The packet digest lists no failure on any check run.
- RESULT red checks: no check concluded red at this head. The body's `## Red checks` reports a local prepr refusal (entities.py: ModuleNotFoundError homeassistant, seat environment), and CI's tests / closures is green, so no root-cause trigger is owed.
- RESULT harness: the finding has no committed finder's harness (the packet says "none named"). The group carry's own control ("one arm per role finds the line; a mutant that drops it is killed") is the de-facto harness, and I re-ran it myself (M1). I built no instrument beyond sed mutants.
- RESULT figures: the body quotes "129 checks, 0 failed" and "1 FAIL" under the M1 mutant. I re-derived both at head. The body has no other figures.
- RESULT forward-carry: the body says none. The carry this PR implements (P398) is on the roster at origin/handoff/audit-r10-roster 6fb2599d5f27.

## Findings

- Surviving mutant M5: changing PACK_ROLE's "reviewer" to "fixer" passes the self-test (129/0), because the arm checks the prompt against PACK_ROLE itself and that check is tautological. Nothing checks that the mapping is correct, or that each value is a role role_pack.py accepts. Control: assert PACK_ROLE == {"reviewer": "fix-review", ...} literally and assert each value is in role_pack's ROLES; M5 is then killed. Carry: R10-POLICY-ROLE-PACK
- Surviving mutant M6: deleting "; on REFUSE read those files as before." passes the self-test, so the fallback the prompt promises is unpinned. Control: an arm asserts the REFUSE fallback is present in every PACK_ROLE prompt. Carry: R10-POLICY-ROLE-PACK
- Surviving mutant M7: changing "at most 5 inline" to "at most 9 inline" passes the self-test. The arm compares against the constant and a prefix only, so the owner's verbatim text past the prefix is unpinned. Control: assert FRUGAL_LINE equals the literal string in the P398 triage. Carry: R10-POLICY-ROLE-PACK
- Deferral: the body leaves two things open. First, the SessionStart route (HPO_SEAT_ROLE) is unused in the cloud until a payload env field is confirmed. Second, the brief's measure-first token count and its local-subagent SessionStart measurement were not made in this PR. The group's justification figure (policy re-read tokens falling, with the pack's size beside it) is therefore still owed. Carry: R10-POLICY-ROLE-PACK

## Friction

none
