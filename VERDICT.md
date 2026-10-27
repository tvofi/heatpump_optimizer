Fix review: blocked 14427f3acc22e8e7e0040deca9d398175bf212e6 head-moved: measured 14427f3acc22e8e7e0040deca9d398175bf212e6, head is 25a6f0e840e413a7cb905f01e293ef4721716f8a
bus-nonce: c955c2856810de42d09b2f34ca237813

# PR #2853, round 5: the merge resolution at 14427f3acc

RESULT head: measured=14427f3acc live=25a6f0e84 (`gh pr view 2853 --json headRefOid`, read at 21:53 and re-read before posting)
RESULT recarry: automatic; `git merge-tree --write-tree 14427f3acc ea36188c` = b813c8fdec = `25a6f0e84^{tree}`
RESULT recarry-delta: paths=165, intersecting the branch's own diff in 1 path (`dev/audit/rounds/round4/D6/claims.py`)
RESULT branch-own-diff-at-live-head: paths=7 (`git diff --name-status ea36188c 25a6f0e84`)
RESULT hand-resolution-vs-automatic-merge: paths=1 (`tools/pr/ci_predict.py`, `git diff --name-only 3ff4ce0f e0388ad8`)
RESULT ci-predict --only wiring / --only mutation: rc=0 / rc=0; --only bogus: rc=2
RESULT ci-predict self-test at 14427f3acc: failed=5; `wiring_self_test` cases=3, all pass
RESULT ci-predict self-test at b69828eb4a: failed=5, FAIL labels identical to 14427f3acc
RESULT ci-predict self-test at a0e7664ea: failed=5, FAIL labels identical to 14427f3acc
RESULT prepr --self-test at 14427f3acc: stopped at ok=254 fail=0; not completed

## Why this is blocked

The head moved while this review was running. Every measurement below was taken at
`14427f3acc`; none was re-taken at `25a6f0e84`, and the PR body's `## Head` has
already been re-taken to the new SHA.

- The live head is `25a6f0e84`; the dispatched head and the packet name `14427f3acc`. A `merge` verdict at `14427f3acc` would be a verdict on a head that is no longer the PR. Carry: R10-FLOW-JIDOKA
- `25a6f0e84`'s parents are `14427f3acc` and `ea36188c` (main), and `git merge-tree --write-tree 14427f3acc ea36188c` prints tree `b813c8fdec`, byte-identical to `25a6f0e84^{tree}`: the recarry is git's automatic result, so it hides no hand resolution. That makes the delta attributable; it does not make it measured. Carry: R10-FLOW-JIDOKA
- A merge verdict at `14427f3acc` cannot be carried to `25a6f0e84`: `git diff --name-only 14427f3acc 25a6f0e84` names 165 paths and includes `dev/audit/rounds/round4/D6/claims.py`, which is one of the branch's own seven files, so `app_approve.sh --carry`'s "the delta misses the branch's own diff" test fails and section 11 makes the new head a delta for a reviewer to take. Carry: R10-FLOW-JIDOKA
- The intersecting file is not a dropped change: at `25a6f0e84`, `claims.py` carries both the branch's `--print-link-targets` / `_doc_paths` / `_doc_links` and main's `RESULT arch_modules_on_disk=83` / `arch_map_listed=83`; main's side of the recarry is two count lines over the branch's re-plumbed doc-link reader. Carry: R10-FLOW-JIDOKA
- At `14427f3acc`, both `gate` check runs concluded `cancelled`, not green (absent is not green), and `prelude` and `codeql / Analyze (python)` were also cancelled; all other completed checks concluded success, including `governance / instrument-self-tests`. At `25a6f0e84` the required checks are still queued or in progress. Carry: R10-FLOW-JIDOKA

## The resolution I measured at 14427f3acc

**The union is correct.** The merge conflict was named by
`git merge-tree --write-tree b69828eb4a a0e7664ea` in one path only,
`tools/pr/ci_predict.py` (stage blobs: base `351ec2d6`, old head `deb7e58b5`,
main `f83bf6fca`). The head's file differs from git's automatic merge of the
same parents in that one path and in no other
(`git diff --name-only 3ff4ce0f e0388ad8` = `tools/pr/ci_predict.py`), so the
seat touched only what it claimed. Its content is the union, not either side:
`ARMS` holds ten entries including `"wiring"` (ci_predict.py:540-541),
`--only` accepts all ten, and main's `wiring_preds` / `wiring_self_test` and
`("wiring", ...)` dispatch entry are present beside the branch's `ARMS` and
`--only` re-architecture. Relative to its merge parents that is 32+/14- for the
branch's re-architecture and 74+/6- for main's wiring additions, both present.

**Nothing else was dropped.** Both parents are ancestors of `14427f3acc`
(`git merge-base --is-ancestor`, both yes). The branch's other six files are
byte-identical between `b69828eb4a` and `14427f3acc` (empty diff), and all seven
are unchanged by the recarry except `claims.py`, where main's two count lines
sit on top of the branch's reader. In the recarry, the 164 other paths are
main's side taken whole (the tree equals the automatic merge).

**The branch's own diff still matches round 4** modulo main's `wiring` change:
the seven paths at the live head are
`dev/audit/harnesses/r10_seat_selftests_mutants.py`,
`dev/audit/rounds/round4/D6/claims.py`,
`dev/programme/delivery/2853.md`, `tests/harness_headers.py`,
`tools/audit/seat/body_push.sh`, `tools/pr/ci_predict.py`, `tools/pr/prepr.sh`;
six are byte-identical to the round-4 head, and the seventh's difference is
exactly main's wiring additions.

**The merge was runnable at `14427f3acc`:** `--only wiring` rc 0,
`--only mutation` rc 0, `--only bogus` rc 2 (argparse refuses the choice), and
`ci_predict --self-test` reports 5 failed. Those five are the wave-script
`AGREEMENT` cases whose fixtures diverge between `budget_raise_gate.py` and
`policy_lint.mjs`; the old head `b69828eb4a` and main `a0e7664ea` report the
same five labels (the FAIL label sets diff empty at all three refs), so the
branch introduced none of them. The `wiring_self_test` cases (3) pass.
`prepr.sh --self-test` was stopped at 254 ok / 0 fail when the head moved, so
the body's "417 passed, 0 failed" is not verified here.

## Friction

- The body's `## Head` paragraph says the `ci_predict.py` conflict was "resolved to main's version". Measured, it is a union: main's version has no `ARMS` or `--only`, and the head has both plus wiring. The sentence was true of neither parent. Carry: R10-FLOW-JIDOKA
- The body says "the five new wiring cases pass". `wiring_self_test` holds 3 cases (ci_predict.py:816-821), and all three pass; the fourth wiring-shaped line in the log, "a self-testing tool the diff adds with no workflow run line", is `plant_self_test`'s case, not the wiring arm's. The count is 3, not 5. Carry: R10-FLOW-JIDOKA
- The union makes four arm-count comments state the wrong number: `tools/pr/ci_predict.py:538` "the other eight", `tools/pr/prepr.sh:583` "not nine", `1591` "the other eight" and `2873-2874` "One arm, not nine ... other eight". With `ARMS` at ten, the other arms number nine and the whole set ten. Carry: R10-FLOW-JIDOKA
- At the live head, step 6g's claims register must re-run: main moved `arch_modules_on_disk` and `arch_map_listed` to 83 over the branch's re-plumbed doc-link reader, and the body's claimed figures were taken against the old base. Carry: R10-FLOW-JIDOKA
- The body's `## Head` sentence "The reviewed code is unchanged" is true of the seven branch files but not of the head's tree, which changed by 165 main paths (closures, structure budgets, golden fixtures and the claims files among them); the re-review must re-establish the ratchet and claim figures at `25a6f0e84`, not only re-read the seven files. Carry: R10-FLOW-JIDOKA

## Carry

Carry: R10-FLOW-JIDOKA (live roster group, `dev/programme/rosters/wave-r10-groups.json`, stage `in-progress`, PR 2853)
