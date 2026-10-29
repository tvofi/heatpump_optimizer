Fix review: merge 2e80966dcf96777ee45d59228987d2c52a4de86d

bus-nonce: 411b2424071575146a11c196258b9484

Round 1. Measured at head 2e80966dcf96777ee45d59228987d2c52a4de86d (code head 6670a91b7 plus the delivery row; merge of origin/main 279578074 included). Head still the PR head when written.

## Findings

- The four `bash -c` helpers now share `_stub_path_env`; Countermeasure B (`bash -e -c`) must keep the `env=_stub_path_env(...)` argument when it edits the argv. Carry: R10-ERREXIT-COUNTERMEASURES
- Friction entry (`policy_lint --stats` prints no PR numbers; the enumerator `friction_lines.py` lands in this PR). Carry: dismissed: the enumerator lands in this pull request

## Evidence

- RESULT mutation: mutant `env = dict(os.environ)` in `_stub_path_env`, run by me under `env -u BASH_ENV` (CI's environment): `1 of 2471 ENTITY CHECKS FAILED`, rc=1; the one non-control FAIL is "a stand-in on PATH wins in a bash -c under a BASH_ENV that re-prepends a toolchain (#2835)" with control='toolchain' read='toolchain'. The other FAIL lines in that log are planted controls (a3/a4/a5/a8/a9/hb/a6...), present in the passing run too. Not vacuous. (ev/mutant_noBE.txt)
- RESULT head: same command unmutated: `ALL 2471 ENTITY CHECKS PASSED`, rc=0 (ev/head_noBE.txt), matching the body's 2471. The mutant with the container profile as BASH_ENV (body: 3 of 2471) I did not re-run: the control arm plants its own BASH_ENV, so the CI-environment result already proves the check; that figure is not re-derived by me.
- Merge: `git merge-tree --write-tree origin/main 2e80966dcf96777ee45d59228987d2c52a4de86d` rc=0, no conflict (ev/merge_tree.txt). origin/main 279578074 is the PR base. Role-file diff since the merge base is empty. review_carry prints CARRY.
- Diff touches no VERSION, manifest, release notes, golden or claim file, closures, or budget; the code change is tests/entities.py only (+65/-11), plus the record, enumerator, two evidence txt, delivery row. No metric moves to earn.
- Class seams: the body's rule `git grep '"PATH":' tests/*.py` dispositions nine sites; the four unguarded `bash -c` sites are closed in the diff, the other five argued (bare env under --noprofile --norc, node execFile, data literal). I read the diff: no other `{**os.environ, "PATH"` site remains in a bash -c.
- carry_audit at head: 2 items, 2 routed, 0 unrouted. R10-ERREXIT-COUNTERMEASURES exists in wave-r10-groups.json on main.
- Counts not re-derived by me: the 10 PR / 11 entry count over 285 bodies and the merge-time figures (needs 285 gh body fetches; the packet's figure_lint reports 10 resolved, 7 not verified). The committed stats file and enumerator output agree with the body and with each other; the enumerator is a committed instrument.
- CI at this head (check-runs read twice, 44 runs): the only red is `tests / nightly-status`, answered in ## Red checks (grades main's Nightly; the diff touches none of what it reads). Green: fast (3.14), coverage, coverage-ratchet, mutation, typing, browser, graders-head-copy, lane-proofs, env-matrix, delivery-status, policy-docs, wave-script, arch-score, budget-raise-gate, closure-scope, briefs, arch-instrument, hassfest, hacs, codeql actions/js. Still in_progress when read: tests / closures, governance / instrument-self-tests, codeql / Analyze (python), prelude. These had not concluded, so I judge no red from them; the orchestrator should confirm they conclude green before merging.
- Root-cause record: named cause (container BASH_ENV re-prepends the toolchain over a PATH stand-in), process state (d) with a (c) component and dates, cost test with numbers, countermeasure landed and shown both ways (red under the mutant, green at head, in CI's environment), refusals recorded with triggers.
