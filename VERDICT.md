Fix review: merge 99c3c1625923adaae044b8f1940344196a9b30af

bus-nonce: 2c85745a98d698f206021bdc2f059e8b
pending-ci: gate

Round 6 of this part: a delta review over the reviewed head 6a0a3a4d96c757c5d576fbce394c324452339b15 (merge verdict, round 5). Done from a detached worktree at 99c3c1625923adaae044b8f1940344196a9b30af. origin/main read 9fdba3b8547f9762438dc19b98b310a63d34dcb1 (`ev/main.txt`). The body's `## Re-cut` still covers the fourth-round re-cut. The head was re-read before return: `refs/pull/3514/head` is 99c3c1625923adaae044b8f1940344196a9b30af.

## Evidence

- Delta shape: `git log --first-parent 6a0a3a4d..99c3c162` has two merges. c9c7965697a6 merges the repair handoff e4b68c37d939, and 99c3c1625923 merges origin/main 009643687b47. `git show --remerge-diff` is empty for both of them (`ev/remerge.log`), so no hand resolution was made at either merge.
- e4b68c37d939, the handoff's own merge of main 50373173d486, has one resolved conflict, in `tools/ci/selftest_closures.json` (`ev/remerge.e4b68c.log`). In the `files` list of step `verdict-bus`, it keeps the reviewed head's `"tools/**"` and drops main's 44 explicit `tools/` paths, which that glob covers.
- Re-derived figure: main 50373173d4 holds 44 `tools/` entries in that list, and both e4b68c37d9 and the head hold 1 entry, `tools/**` (`ev/jsondelta.log`). This matches the body's `## Head`.
- No reviewed line changed beyond what the main merges bring in. I compared each file's added and removed lines in the branch's own patch against main, before and after: `git diff e23124ff 6a0a3a4d` (the old merge base) against `git diff 009643687b 99c3c162` (the new merge base). 26 of the 27 files are identical (`ev/perfile.log`). The one that differs is `tools/ci/selftest_closures.json`.
- How `tools/ci/selftest_closures.json` differs, compared as JSON sets: 19 of its 20 changed keys are identical. The 20th, `verdict-bus/files`, removes one more path at the head: `tools/policy/legacy_control_files.json`. Main added that path between the two merge bases, and the branch's `tools/**` covers it. The textual hunks that remain differ only in where main now places the `"git"` key (`ev/jsondelta.log`). So the reviewed behaviour is kept.
- `.claude/hooks/pre-bash.sh` appears in the packet's delta diff. At the head it is main 009643687b's blob (219eae779e2c), so the change is main's and not the branch's.
- No `custom_components/` line is in the branch's diff against main, and no version or golden file is touched. `git diff --name-only $(git merge-base origin/main HEAD)...HEAD -- VERSION custom_components RELEASE_NOTES.md tests/golden` prints nothing. The delta therefore does not widen the review.
- RESULT `git merge-tree --write-tree origin/main 99c3c162` against 9fdba3b8547f: rc 0, tree c27de6a8b408, no CONFLICT line, `LEDGER-MERGE: resolved tests/closures.json` (`ev/mergetree.log`).
- RESULT at the head (`ev/selftests.log`):
  - `python3 -I tools/pr/outside.py --self-test`: `outside self-test: 266 checks, 0 failed`, rc 0. This is the same tally as the reviewed head.
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `node tools/policy/policy_lint.mjs --budgets`: rc 0.
  - `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract I read is current.
- RESULT spot mutants on `tools/pr/outside.py` at the head (reviewer's instrument, `ev/spot_mutants.log`): 3 of 3 were killed and the tree was restored.
  - Line 279, the APPROVED test inverted: 2 checks fail.
  - Line 346, the SHA40 head check dropped: 1 check fails.
  - Line 343, the `main` ref refusal dropped: 1 check fails.
  - The branch's code is byte-identical to the reviewed code, so the round-5 27-mutant proof still applies.
- The previous verdict had no findings, so none needed resolving. carry_audit at the head, from the packet: `6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)`. figure_lint: `10 resolved, 6 not verified, 0 refused`.
- CI state:
  - `python3 tools/audit/seat/merge_train.py classify 99c3c1625923adaae044b8f1940344196a9b30af --pr 3514` was polled every ~75 s from 15:59 to 16:30 UTC. Every run printed `rc=3 WAIT 99c3c1625923adaae044b8f1940344196a9b30af pending: gate red: none` (`ev/classify.log`). That is why the `pending-ci: gate` line is set.
  - At render, the packet's `introduced-red` refusal was only "unreadable" while `instrument-self-tests` was in progress. classify reports no red since then.
  - `owed-reds` printed a set including `tests / mutation`, `tests / typing` and `validate / validate-hacs`. `tests / nightly-status`, red in the packet digest, is outside that set and is not this PR's.
  - The `budget-raise-gate` red is the reviewed raise, answered in `## Red checks`. Its approval follows this verdict.

## Findings

none
