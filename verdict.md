Fix review: merge 5603c8cc84cdb09a5920ea670a6108587dbf1dbb

bus-nonce: 0d27075020de392eb61d45ae165d1f9f
pending-ci: arch-score / arch-score, budget-raise-gate / budget-raise-gate, codeql / Analyze (actions), codeql / Analyze (javascript-typescript), codeql / Analyze (python), governance / delivery-status, governance / env-matrix, governance / instrument-self-tests, governance / policy-docs, governance / wave-script, hassfest / hassfest, tests / briefs, tests / closure-scope, tests / mutation, tests / nightly-status, validate / validate-hacs

## Evidence

Round 2 of review (a delta review). Round 1 blocked head 4f61c74a526b4c1c82e32fd5c0453c93ff9c1db9 as dropped-entries. The repair under review is the range 4f61c74a..5603c8cc. The head 5603c8cc is a merge of b06e830153c7b9888cf4fccaae00f175690cb283 into 4f61c74a, and the two trees are identical (both 2466b32f71afcc5a9ad84c3d5e3faa6fc03f9c3e). The merge base with origin/main is e4ca2d940efd1e87912d80cb3ebddf8240ba0729.

- Required control (no dropped entries). Command: `python3 ev/dropped.py e4ca2d940efd1e87912d80cb3ebddf8240ba0729 5603c8cc84cdb09a5920ea670a6108587dbf1dbb`, where e4ca2d94 is the result of `git merge-base origin/main HEAD`. For each step, the script checks that every top-level key, step key and field key at the merge base is still at the head. It also checks every entry in files, probes, dirs and git. An entry is excused only if its path is no longer a file or directory in the head's tree. It counts an `index` or `objects` flag that was true at the base and is no longer true as dropped. Head result: `dropped=0 base_steps=114 head_steps=114`. No entry was excused. Output: ev/dropped.txt.
- Null control: the same command run on 4f61c74a526b4c1c82e32fd5c0453c93ff9c1db9 prints `dropped=14`. That is 9 path entries (ci-predictor and verdict-bus rosters as file, probe and dir; prepr `.gitattributes`, `tests/env_drift.py` and `tools/merge/ledger_merge.py`), 3 `?` git markers (dependency-graph-census, temp-or-machine-path, throwaway-git-helper) and 2 objects flags (dependency-graph-census, throwaway-git-helper). This matches round 1's block and the repair commit's subject exactly.
- Delta shape: `git diff 4f61c74a 5603c8cc` changes only tools/ci/selftest_closures.json, with 18 insertions and 4 deletions. All 4 deleted lines are `"objects": false` / `"git": []` lines that the delta replaces with `true` / `["?"]`. No measured entry is removed. Only 6 steps change from round 1 to the head, and each is a step listed in the block. Diff: ev/delta.diff.
- Body figure re-derived: the body says 98 entries untouched by round 1 are still byte-identical to the merge base. At the head, 98 steps are equal between the base and round 1, and all 98 are equal at the head.
- `python3 -I tools/ci/selftest_scope.py --self-test` at the head: `selftest_scope self-test: 117 checks, 0 failed`, the same figure the body quotes (ev/selftest.txt). `selftest_scope.py static`: `114 gated step(s), 0 problem(s)` (ev/static.txt).
- Mutation proof: the change is a measured data file. A deleted entry is the mutant, and the dropped-entries control above is what kills it: the round-1 table, which lacks the 14 entries, prints 14. The push-to-main drift step (a fresh strace) is the production detector. It cannot be re-run on this seat.
- Merge check: `git merge-tree --write-tree origin/main 5603c8cc84cdb09a5920ea670a6108587dbf1dbb` returns tree 97864b480175001e263edfd38ce6d2d0cfdb54f5 with rc 0, so there is no conflict (ev/merge-tree.txt).
- Packet carry audit at the head: `CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)`. The body's carries route to R10-SELFTEST-SCOPE-UNION-GUARD, which is on origin/handoff/audit-r10-roster.
- `env -u BASH_ENV python3 tests/entities.py` could not run on this seat. Under venv-ci it fails on the missing `homeassistant` import. Under venv-ha it fails on the missing `paho` import from homeassistant's mqtt component (ev/entities.txt). The cause is the seat's environment, not the tree: the delta adds no tracked file, so the classification check is unaffected. Its figure is not re-derived here.
- CI: `merge_train.py classify 5603c8cc84cdb09a5920ea670a6108587dbf1dbb --pr 3535` exited 3 twice, more than 60 s apart, both times printing `WAIT 5603c8cc84cdb09a5920ea670a6108587dbf1dbb pending: gate red: none` (ev/classify1.txt, ev/classify2.txt). The packet lists every required context as queued. Per the dispatch, I did not wait: the relay posts this verdict once CI is green at this head.

## Findings

none
