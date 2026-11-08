Fix review: blocked 7e9b464acd5289660b0d5a4ef10c7d609dd50c45 gate-red: required gate reads RED at this head after a 60-minute wait; two edit-run deferral gates were never re-run after their deciding run's gate went green

bus-nonce: 251ad11ac5356b22583f5eb4b672d52e

Round: first fix review of PR #3333 (R10-POLICY-ROLE-PACK part 2), measured at head 7e9b464acd5289660b0d5a4ef10c7d609dd50c45, merge base bb7dfb9bd6c68548d1a956adc411be91e02965e0.

## Block

- The required context `gate` is red at this head, and `merge_train.py classify` returns RED (rc 1) on every run from 14:13:30Z to 14:50:36Z (ev/classify-history.txt). Two gate check-runs failed: 128749241770 (run 42485999378, 13:46Z) and 128752555566 (run 42487402851, 13:59Z). Both logs read `FAIL run(s) [42485999343] at this head are still being judged; their gate decides`. That deciding code run's own gate, 128754451277, concluded **success** at 14:07:03Z, and every unit in it is green. Under A5 (`latest_runs`/`gate_suites`) each suite's latest gate counts and the worst stands. gate-sweep.yml should have re-run both deferring gates once the decider concluded, but it had not done so 44 minutes later, so the red stands. I found no defect in the authored work (see Evidence). Re-run the two gate jobs (`gate.py --refresh`, or rerun jobs 128749241770 and 128752555566). Once `classify` reads GREEN, a re-dispatch at this same head should return merge, unless the head moves. Why gate-sweep did not fire is not established here. Carry: R10-POLICY-ROLE-PACK

## Findings

- Surviving mutant, PACK_ROLE values: changing `"reviewer": "fix-review"` to `"fix_review"` leaves the self-test at 129 checks, 0 failed. The new arm checks the prompt against `PACK_ROLE` itself, which is a tautology. A role name `role_pack.py` does not know makes the seat get `role_pack: REFUSE role must be one of ...` (rc 2) and silently fall back to the full re-read, so the saving is lost without any signal. Suggested pin: assert `set(PACK_ROLE.values()) <= set(role_pack.ROLE_CONTRACT)`. Today all four values render rc 0 (ev/mutants.txt), so this is a regression guard, not a live defect. Carry: R10-POLICY-ROLE-PACK
- Surviving mutants, unpinned prompt text: the `; on REFUSE read those files as before.` fallback clause can be dropped (M6), and the FRUGAL_LINE body after its pinned prefix can change, for example `at most 5` to `at most 50` (M8); neither reddens the self-test. The roster control asked only that a dropped line be killed, which M1 shows, so this is weaker than "verbatim" but within the brief. Carry: R10-POLICY-ROLE-PACK
- Deferred: the body leaves open whether Agent-tool subagents run SessionStart (the brief's "measure that at the base"), and the cloud payload has no confirmed per-seat env field for `HPO_SEAT_ROLE`, so the brief's "cloud_dispatch.py sets the variable" became a prompt instruction. That deviation is disclosed. The measurement is still owed. Carry: R10-POLICY-ROLE-PACK

## Evidence

- Diff (three-dot from bb7dfb9bd): `tools/audit/seat/cloud_dispatch.py` (+25 −1) and `dev/programme/delivery/3333.md` (new row). The delivery row is in the diff. VERSION, the manifest, RELEASE_NOTES.md, every `*_budgets.json` and both claim files are untouched. No file under the CLAUDE.md policy set or `dev/governance/` is touched, and CODEOWNERS does not own `cloud_dispatch.py`. The body calls the change policy-adjacent, and the roster's owner_gate is "mandated approval under 6329234399".
- Role contract currency: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Self-test at head: `cloud_dispatch self-test: 129 checks, 0 failed`, which re-derives the body's figure (ev/selftest-head.txt).
- Mutation proof (ev/mutants.txt): M1, dropping FRUGAL_LINE from the join, gives 1 FAIL (the frugal arm) and re-derives the body's named mutant. M2, a duplicated line, gives 1 FAIL. M3, dropping the pack instruction, gives 1 FAIL (the pack arm). M5, dropping `--out`, gives 1 FAIL. M7, giving the probe a pack, raises KeyError (rc 1). M4, M6 and M8 survive (Findings).
- Null control: the head's two new arms grafted onto the base `cloud_dispatch.py` give `129 checks, 2 failed`, both new arms (ev/null-control-base.txt). This confirms the body's null control.
- Harness: no finder's harness is named. The group's carry 4 names its control, "one arm per role finds the line; a mutant that drops it is killed", and I ran that at both ends as above. Class: `_prompt` is the single prompt builder for all five roles, so the class is one seam.
- FRUGAL_LINE is byte-equal to the owner directive quoted in the roster carry (ev/roster-group.txt).
- `role_pack.py render` exits 0 for fix-review, fixer, designer and design-review at head.
- Structure ratchet: `STRUCTURE RATCHET PASSED` (ev/structure.txt). `tests/entities.py` cannot run in this seat (`ModuleNotFoundError: homeassistant`, ev/entities.txt), the same as the fixer's seat. CI's `tests / closure-scope` and `tests / closures` are success, and the new row is a `dev/programme/delivery/` ledger row of the kind main already carries.
- Merge: `git merge-tree --write-tree` is rc 0 against bb7dfb9bd and again against the moved main 8a4cf2618c53a6dca6b65df3eae5efc8832d1796 (ev/merge-tree.txt). Main's 10 new files do not overlap the diff.
- `## Head` names 7e9b464acd5289660b0d5a4ef10c7d609dd50c45, which is the head I measured. At 14:50Z the branch ref was still that head.
- Checks (all 68 check-runs, one page of 100, read at about 14:13Z): every check is success or skipped except the two deferral gates above. `pr-contract / pr-contract` 128754318221 is success (14:06:28Z) and started after the last red concluded. The body's `## Red checks` names `closures` (a local prepr refusal) and not `gate`. The gate red is the infrastructure deferral above, not a red the diff owes a root cause for.
- Figures the body quotes: 129 checks / 0 failed and 1 FAIL under the dropped-line mutant are both re-derived. The body's diff-mutant step (`MUTANT_CMD`, no survivor) was not re-run: CI `tests / mutation` is success, and my own targeted mutants are above.
