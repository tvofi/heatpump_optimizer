Fix review: blocked a81d7f15293fc2101f42e48ade37ef7022c35517 mutation-vacuous: G5-cli-hotfix-inverted G5b-cli-hotfix-inverted-prepr P8-classifier-asks-priority G3-except-fails-open P7-HOTFIX_SCOPED-dropped P9-export-dropped

bus-nonce: c1dc4bad693bf2ac23244843f575ca13

## Block

Round 1 of this PR's review (a re-fire of the first session, which stopped with no verdict). Measured head: a81d7f15293fc2101f42e48ade37ef7022c35517, which is still the PR head (`pull_request_read get`).

The PR's own seven mutants are killed. The seam that carries the PR's whole behaviour is not covered by any test, though. That seam is prepr's `hotfix_class` calling `gate_priority.py --hotfix`, and the CLI printing `is_hotfix`. The prepr self-test stubs `hotfix_class`, and the gate_priority self-test calls `is_hotfix()` directly, never `main(["--hotfix", ...])`. Survivors at the head, from the reviewer's driver (`ev/driver.py`, `ev/mutants-results.txt`, one log per mutant in `ev/mutants/`):

- G5-cli-hotfix-inverted (`gate_priority.py` main prints `int(not is_hotfix(...))`), against the gate_priority self-test: SURVIVED. G5b is the same mutant against `prepr.sh --self-test`: SURVIVED. Failure scenario: every non-hotfix branch gets `PREPR_SKIP_CODE=hotfix PREPR_SKIP_CLOSURES=1`, so its code and closure steps are skipped, and every hotfix branch runs the full prepr. Every test still passes.
- P8-classifier-asks-priority (`hotfix_class` calls `gate_priority.py --branch` without `--hotfix`): SURVIVED. Failure scenario: `priority_for_branch` prints 1 for an outside or critical-path group and 2 for a hotfix. A critical-path branch would therefore be scoped and a hotfix branch would not, and every test still passes.
- G3-except-fails-open (`_rank`'s `except` returns `RANK_HOTFIX`): SURVIVED. `is_hotfix`'s docstring promises "Every failure is False", and the body says "a failed read gives a full prepr". The fail-closed self-test arm goes through `fetch=True` with no remote, which returns before the `try` body raises, so the exception path is never exercised. The same gap already existed in `derived_priority` at the base, but this PR newly relies on it as the safety property of a skip.
- P7-HOTFIX_SCOPED-dropped (`HOTFIX_SCOPED=1` deleted): SURVIVED. With it gone, a hotfix-scoped run prints "reused from the receipt at hotfix", a false receipt claim in the code-steps line. Nothing tests the main-flow message choice.
- P9-export-dropped (`export PREPR_SKIP_CODE PREPR_SKIP_CLOSURES` deleted): SURVIVED. Either the export is unneeded (then delete it), or a child depends on it (then pin it).

A fix that pins all of these: add one end-to-end arm per direction against a fixture roster, covering `hotfix_class` → `gate_priority.py --hotfix --ref <fixture> --no-fetch` for the hotfix branch (expects 1) and for an outside, a critical and an unmapped branch (expects 0). Add a gate_priority self-test arm that calls `main(["--hotfix", ...])` and checks stdout, and one that makes `show_roster` raise (for example a malformed roster file at the ref) and asserts `is_hotfix` is False. The null control (a comment-only edit) survived, as it should.

## Evidence

- RESULT prepr self-test head: `bash tools/pr/prepr.sh --self-test` printed 548 passed, 0 failed, exit 0 (`ev/selftest-head.log`). At the base 7eadd75f it printed 542 passed, 0 failed (`ev/selftest-base.log`). The difference is the 6 new arms, which matches the body's base figure of 544 passed + 4 failed with the arms present.
- RESULT gate_priority self-test head: 17 checks, 0 failed (`ev/gate_priority-head.log`), as the body states.
- RESULT structure: `python3 tests/structure.py` at the head printed STRUCTURE RATCHET PASSED, exit 0 (`ev/structure-head.log`). The diff touches no budget file.
- RESULT merge: `git merge-tree --write-tree origin/main a81d7f15` exited 0, with no conflict (`ev/merge-tree.txt`).
- RESULT CI: `merge_train.py classify a81d7f15 --pr 3547` printed `GREEN a81d7f15293fc2101f42e48ade37ef7022c35517 pending: none red: none`, rc 0 (`ev/classify.txt`). No red, so no `## Red checks` answer is owed.
- RESULT mutants: G1, G2, G4 (gate_priority) and P1–P6 (prepr) were killed. G3, G5, G5b, P7, P8 and P9 survived, and the NULL control survived. The body's M1–M7 correspond to P1, P2, P3, P4, G1, P5 and P6, and all were killed again here.
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched (the three-dot diff is empty for those paths). No claim file is touched, and no fixture can move, because the diff is instruments-only.
- Live CLI at the head: `gate_priority.py --hotfix --branch fix/r10-prepr-residue-p2` prints 0. The roster has exactly one `"class": "hotfix"` group (R10-NIGHTLY-SLOW-ROLLING), per a scout grep of `dev/programme/rosters/`.
- Finder's harness: the packet reads "none named". This is an owner-instruction carry (Carry 21) with no audit harness, and the class is one seam (the hotfix default in prepr), so there is no enumeration rule to run.
- Not re-derived: the body's "28 s" wall clock for a scoped run at the merge base, and the carry's "about 40 minutes" figure (the body itself marks that one as not re-measured).
- tests/entities.py was not run: it needs `homeassistant`, which this cloud venv lacks. CI's green `tests / closure-scope` and `tests / fast (3.14)` stand for it at this head.
- The reviewer built the mutation driver (`ev/driver.py`); it is not the finder's.
