Fix review: merge 30b143922cdc5ed869fe32150ecb20cc8202727b

bus-nonce: 46ae93690a0bd9e981192349f4d76371

Round 2 (delta) of PR 3438, handoff tip `30b143922cdc5ed869fe32150ecb20cc8202727b`. No pull request head carries this tip yet, so there is no review packet and no CI to wait on; the evidence is my own re-runs. Delta against round 1's head: one analysis document and one delivery row, no production, test or workflow line, so no mutant is owed. `git merge-tree --write-tree origin/main 30b143922cdc5ed869fe32150ecb20cc8202727b` exits 0.

## Evidence

Round-1 items, each re-checked at the tip:
- class-open: section 3's rule (`grep -n 'github.event.pull_request.base.sha' .github/workflows/*.yml | grep -v 'PINNED:.*base.sha\|PINNED=.*base'`) returns 11 lines at the tip (`ev/rule-output.txt`), identical to the 11 the document pastes. All 11 are dispositioned in its table. P572's "Do not change the diff bases" at roster `dbff400de` names BASE_SHA, SINCE, PR_BASE, MACHINERY_BASE, PAYLOAD_BASE and tests.yml's BASE, so the ten (including `dependabot-automerge.yml:69`, a whole checkout, and `arch-score.yml:63`) are dispositioned correctly. `tests.yml:1180` is placed in the class with a reason I confirmed: the `mutation-pins` job's checkout has no `ref`, and `tests.yml:1214` writes `git show "$PR_BASE":tests/mutation_table.py` into it. The body's 32 = 21 PINNED + 11 reproduces (32 literal lines; 22 restore sites, one of them `ci.yml:117`, which has no literal).
- Cost-test misquote: section 4 now says P572 counts 19 of 23 exposed, quotes "Not measured: how many of them reach `carry_receivable`" (P572 lines 60 and 63), and labels 19 x 64.6 = 1227 an upper bound. The verdict rests on the measured 64.6 min. Fixed.
- Census arm's standing cost: now costed (1.98 s median, 0.222 s cached) with break-evens 3876 s / 1.98 = 1957 and 3876 / 0.222 = 17459 runs a week (arithmetic checks, as do 37181 and 331621). Fixed. The arm's 1.98 s and 0.222 s are the fixer's measurements from the hotfix WIP; I did not re-time them this round (round 1 ran the demonstration at 29 / 0 defects, and section 5 is unchanged).

Class sweep, re-derived at the tip: 22 restore sites per file (1, 6, 2, 6, 1, 6); `ci.yml:117` is the only `merge-base FETCH_HEAD HEAD` line; `_BP_UNITS` at `tests/entities.py:28736` holds the two files; `git rev-list --count d08ed31049..c620ebba96` = 53, `--merges` = 19; window 231 first-parent commits, 211 merges; 9 touch `roster_lib.py`; the null-control path `tools/none.py` = 0; the head touches neither `roster_lib.py` nor `carry_audit.py`. Resolver timing: 100 pairs took 1.94 s here (19 ms a pair), against the document's 7 ms and the round-1 reviewer's 16 ms; the conclusion (about 3060 runs x ~0.016 s = 49 s a week) holds on any of them. Not re-derived: `427c4ca874`'s parents (no longer fetchable, as the document discloses); the census arm's timing.

Carry accounting: the body's two forward-carries to R10-HOTFIX-RESTORE-BASE-SKEW are in the tree at roster `dbff400de` (`wave-r10-groups.json`, items e41acc16 and 530feedf, with the control stated as a precondition). Its two own-group findings are marked fixed in the document, which I confirmed above.

Red checks: none owed by this PR (no head exists; `nightly-status` is not in the owed set the body names).

## Findings

- Residual: section 4 states "58 touch the 22 patterns of `pr-contract`'s restore pathspec" with the command `git log --format=%H -m $W -- <pathspec>`. Run with the 22 patterns quoted, as the workflow's `git diff` passes them (git pathspec, where `*` crosses `/`), it prints 69; 58 is what an unquoted shell expansion of the same patterns prints (`ev/window.txt`). Round 1 reproduced 58 the same way. No conclusion moves: the estimate is "at least one a week" and both figures are far above it. The document should name the quoting if the figure is kept. Carry: dismissed: conclusion-neutral figure in a record document; no consumer reads the count and the cost test's verdict does not depend on it
