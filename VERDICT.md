Fix review: merge 34466736f2f4e9b7d2e7e448652904c6e9d65d4f

bus-nonce: 192be102521f1fed6528614d5bace35b

## Scope

Round 1 (first review; no prior verdict). Policy pull request: `dev/governance/roles/fix-review.md`, `dev/governance/roles/fixer.md`, plus the RCA record and the delivery row. No line under `custom_components/`, `tools/` or `tests/` moves. Role files current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty. Merging still needs the owner's approving review at the head (or the declared mandate approval the body names); this verdict does not stand in for it.

## Evidence

- RESULT detector v7.1.11 rc=0 (`states=9 failed=0`), v7.1.12 rc=1 (`states=36 failed=4`), head rc=0 (`states=36 failed=0`); harness sha1 c6f2734378b2a6328b79b3c2f6e68611a6285e53, matching the body (ev/detector.txt, ev/harness-sha1.txt).
- RESULT record byte-identical to 2e20aa5d4e (ev/record-identity.txt).
- RESULT step 16 and the fixer.md step 3 sentence are verbatim from the record's section 5 drafts, compared with whitespace and blockquote markers normalised (ev/verbatim.txt).
- RESULT VERSION, manifest.json and RELEASE_NOTES.md untouched three-dot from the merge base (ev/version.txt).
- RESULT budgets at the head: fixer.md 313/315 lines, 5197/5216 tokens; fix-review.md 138/140 lines, 2775/2775 tokens; corpus ~69731 (base ~69740), cap 69333 + band 500. No budget file changes (ev/policy-checks.txt).
- RESULT policy_lint 0 errors across 52 files; check-wave-script 223 passed 0 failed; review_packet self-test 133 checks 0 failed; rules_sync ok.
- Mutation M1 (step 16 added to the base text with no deletions): policy_lint rc=1, fix-review.md at 144/140 lines and 2909/2775 tokens. The payment is required, and the deletions earn it, not the instrument (ev/mutants.txt).
- Mutation M2 (delete the `root-cause-detectable` routing sentence): check-wave-script rc=1. Mutation M3 (delete "never widen it"): review_packet self-test rc=1. Both "tried and reverted" claims hold.
- Each deletion was checked against the rule it defers to at the head. defect-root-cause.md Enforcement states the fixer's answer obligation, "not the body's account", the owed-reds set and the `instrument-self-tests` INTRODUCED block. finding-propagation.md Enforcement states the roster-SHA carry read. `ci-autofix.md` does not say that UNDER-SCOPED/INHERITED CLAIMS are answered by naming them, so the move into fixer.md step 5 keeps that clause. No tracked file cites the removed fixer.md section (git grep "Before you hand off" finds only the surviving "carry what you found forward" heading).
- Null control figures: `NO-PRODUCTION-DIFF` at 98847b99d7; `def _arm_space` count 1 at 1aeaf273a4 (ev/figures.txt).
- Mutation proof n/a is correct: the diff writes no production, tool or test line.
- Merge with main: `git merge-tree --write-tree origin/main <head>` rc=0 (ev/merge-tree.txt).
- Scope line re-derived: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` against merge base 2104e34d86.
- Steps 2, 4 and 6: no finder's harness applies to a policy diff and no golden moves. Its class is the record's section 3 enumerator, which closed on main through the hotfix 8fc6be183d and its tests/features.py pins. It is not this PR's.
- PR head read live equals 34466736f2f4e9b7d2e7e448652904c6e9d65d4f, the head the body names.
- CI: `merge_train.py classify 34466736f2f4e9b7d2e7e448652904c6e9d65d4f --pr 3638` -> `GREEN 34466736f2f4e9b7d2e7e448652904c6e9d65d4f pending: none red: none` (ev/classify.txt). The earlier `gate` failures in the digest were the provisional deferral red while `tests / coverage` ran.

## Findings

- Note: wording: step 2 loses "printing your own `RESULT` lines". The closing paragraph's "your RESULT lines" keeps the requirement but drops the "own, not copied" emphasis. The owner may want it back at review; it is not a block, because step 2 still requires the finder's harness at both ends. Carry: dismissed: the obligation survives in the closing paragraph and the owner reviews policy wording at merge

## Red checks

none at the head (classify GREEN).
