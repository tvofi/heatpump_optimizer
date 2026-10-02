Fix review: merge eed5ac3fa3ed0b2d4df7680800b097217a90acc2

bus-nonce: 8db4179c5462380a9656fc650f7fbf22
Round: 2. Reviewer: R9-EG-B5 fix reviewer, from a detached worktree at the head. The head was re-read at posting: eed5ac3fa3ed0b2d4df7680800b097217a90acc2. Merge base and origin/main: aa7a81192 (#1859).

Carry from round 1 (review/1858 f6deb825b):
RESULT production three-dot diff: `diff <(git diff 5f87e25a1...291b3e0fa -- custom_components) <(git diff aa7a81192...eed5ac3fa -- custom_components)` is empty, and `git diff 291b3e0fa eed5ac3fa -- custom_components` is empty. Main touched no custom_components file between the two merge bases.
RESULT merge resolution: eed5ac3fa's tree 7d7f3898b equals `git merge-tree --write-tree` of its parents, so there is no hand resolution. `git merge-tree --write-tree origin/main HEAD` rc=0.
RESULT provenance.py origin/main(aa7a81192) HEAD rc=0: "PROVENANCE PASSED: 27 units, 0 problem(s)", residual +29/-31, control 27/27. This is the same as round 1.
RESULT ledger_check.py aa7a81192 rc=0: form/layout [], completeness [], unpinned 3909 here and 3909 at base, added unpinned 0, null control without the #1748 pairing 147, refusal None. This is unchanged after main's mutation_table.py change.
Round-1 findings 1-5 (provenance and my perturbations, no silent revert, the 3 substitutions, the ledger carry, the config Protocol accepted) carry unchanged.

Round-2 delta, against the round-1 owed list:
RESULT D6 header: 7ddec1a78 moves arch_modules_on_disk and arch_map_listed from 67 to 68, with history notes. claims.json and claims.md change only the C32/C33 result strings to 68. I could not run claims.py locally: it imports golden.py, which needs numpy. CI's fast lane passed harness_headers.py.
RESULT closures: 87371ea3a adds 29 lines to tests/closures.json. Against CI's round-1 Linux recordings (run 37036628897, 58 recordings on the same production tree), every production file a recording read is in that script's committed closure at this head. The one exception is tests/dst_checks.py, which has no closure key at main either (by design). The `closures` check at this head is a success, and closures-autofix was skipped. So CI judged the hand-merge complete.
RESULT deployment_shape: 2b6cd5cfa re-derives the #1218 note (85 -> 86 files, the pair counts +1, the backtest four 14 -> 16). fast passed deployment_shape.py and entities.py.
RESULT Red checks: the body names harness_headers (cheaper detector: run it locally, the seat-block item), the entities closure reds, the closures-autofix skip-failed-recording deadlock and the stress.py rc=1 under recording, and pr-contract. I checked the stress claim independently: #1852's closures run 37026062126 also recorded stress.py rc=1 (with entities.py and harness_headers.py). The 15.2x/14.5x and 11.6x/11.0x figures are the fixer's, and I did not re-derive them. The standing gap is cited to handoff/r9-rca-closures-autofix-skip, which exists (6d4a51b3e).
RESULT CI at eed5ac3 (check-runs API): 35 runs. Success: fast (3.14), closures, mutation, typing, pr-contract (latest run 111003746586; an earlier one was cancelled), delivery-status. The only non-green run is nightly-status, and it is not this PR's: "NIGHTLY ABSENT: nothing failed, but mutation-ledger, mutation-ledger-push did not run in that scheduled run (last night)". The diff reaches none of its inputs: no nightly script or job, plan, HANDOVER, or delivery row other than docs/delivery/1858.md. It is unrequired on main-protect.

Note, not blocking: the body's `## Head` section opens with two duplicated, self-referential paragraphs ("eed5ac3 merges the authored code head eed5ac3 ..."). The third paragraph is correct and names this head. pr-contract passed it. The orchestrator may want them cut before posting.
Not run locally (no numpy): claims.py, harness_headers.py, features.py, golden fingerprint, env_drift. These rest on CI's green fast lane at this head.
Evidence: ~/hpo-seats/1858-review/ev2 (provenance and ledger at this head, #1852's recording rc list, HEAD.txt). Round-1 evidence is on review/1858 f6deb825b.
