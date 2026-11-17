Fix review: merge be2d6def14ea4d2c4c30f1016af1ab6a1b7c3592

bus-nonce: 1c2c198886324a94c8367a1403471d2d
pending-ci: gate

## Round

Round 2: a delta review over reviewed head 4bfd3c06fa7316f88ffa19621d3df1ac0b1b69c3 (fix-review.md step 12). The delta is `git diff 4bfd3c06 be2d6def` (ev/delta.diff). It adds two lines to `tools/audit/product_reads.py`, both in `self_test()`: one new arm. This is an instrument and test delta only, so the scope does not widen.

## Previous verdict's findings

- Block `class-open` on `dev/audit/rounds/round11/product-reads/operation.tsv`: now dispositioned. The body's `## Forward-carry` names the file, its 6 retired `duty=control | running` rows, the judgement the re-cut needs, and a route: `Carry: R11-INTAKE-R10-RESIDUE`. carry_audit at the head reads `1 routed, 0 unrouted, 0 bad destination(s)` (ev/review-packet.md). Step 6 accepts a site that is dispositioned in the body, so the block clears.
- Finding M3/M6, the surviving mutants on `if tok in ("observe", "off"): return first`: resolved. The new arm `token: off holds under duty=off on the first pass, not on a restart pass` kills both. M3 gives `got (False, False), want (True, False)` and M6 gives `got (True, True), want (True, False)`, both exit 1, as the body's mutation proof (c) says (ev/mutants.tsv).

## Findings

- Residual: mutant M7 survives. It narrows the branch to `if tok in ("off",): return first`, so an `observe` token falls through to `return None` ("not recorded") instead of holding on the first pass under duty=observe. With M7, `--self-test` still prints `SELF-TEST passed (86 arms)`, exit 0 (ev/mutants.tsv), because no arm uses an `observe` token. To kill it, add the `observe` counterpart of the new arm: `token_holds("observe", {**ps, "duty": "observe"}, None)` should be True. This sits in an instrument's self-test, not production code. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- Head reviewed: be2d6def14ea4d2c4c30f1016af1ab6a1b7c3592 (ev/HEAD.txt). It equals refs/pull/3698/head and the body's `## Head`.
- Role contracts: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so fix-review.md is current.
- Merge: `git merge-tree --write-tree origin/main be2d6def` exits 0 with a clean tree, 9b31be7ec51e9c8ffa4e79c68dcf7b83af580364, against origin/main 4ecca4cc580b1065e366bf12bd5a917d40d03c0e (ev/merge-tree.txt).
- Self-test at the head: `python3 -I tools/audit/product_reads.py --self-test` prints `SELF-TEST passed (86 arms)`, exit 0 (ev/selftest-head.log). This matches the body's 86.
- Mutants (ev/mutants.tsv): M3, M6, M8 (the tuple narrowed to `("observe",)`), M9 (`return ps["plan"]`, which ignores ordinal) and M10 (the DUTY_OF guard disabled, body b) are KILLED. M7 SURVIVES (see Findings). The worktree was clean after the mutants.
- Previously verified at 4bfd3c06 and unchanged by the delta: the null control at both ends, body mutation (a), the selftest_scope static and select results, and VERSION, the manifest, RELEASE_NOTES.md and tests/golden being untouched.
- figure_lint at the head: `MODE: FULL` is unverified, because no program it knows printed it. A push to main forces FULL, so the line is consistent with a hotfix, but I did not re-derive it.
- CI: I polled `merge_train.py classify be2d6def --pr 3698` for about 30 minutes, at least 60 s between runs. Every run printed `WAIT be2d6def14ea4d2c4c30f1016af1ab6a1b7c3592 pending: gate red: none` (ev/classify-polls.txt, ev/classify-final.txt). When I stopped, `tests / fast (3.14)` was still in progress. The `gate` aggregator and `tests / nightly-status` read failure in the check-runs listing, but classify counts no red, and `tests / nightly-status` is not in the owed-reds set. The review_packet's `introduced-red: unreadable` refusal came from instrument-self-tests still running at render (ev/review-packet.md). That job is the defect's own check, so the relay should confirm it green.
- Note: figure: the body says `selftest_scope.py --self-test` prints `118 checks` on macOS and `128` on Linux. The previous round measured 128 on Linux. I did not re-derive 118, because I have no macOS run.

## Friction

none
