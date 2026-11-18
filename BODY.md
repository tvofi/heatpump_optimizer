Part 3 of R11-PRE-HANDOFF-BOOKKEEPING: proposal PC-1113-17 (roster carry 17), a privacy defect. `body_push.sh`'s `keep_refused` published any refused body on the orphan ref `handoff-wip/<topic>-body`, including a body the pr-body lint had refused because it carried this host's identity, so a privacy refusal still wrote the refused text to origin. Now `keep_refused` first judges the body, and any RESUME note, with `ref_privacy.py body-lines`, the predicate the comment gate and `prepr.sh --body-check`'s privacy arm already use. If it refuses, or the judge itself fails, nothing is pushed: the refusal and its exit code stay as they were, and the local body path is printed. Every refusal arm (predictor, head-stale, figure-block base, BODY-LINT, review packet, CARRY-LANDED) calls `keep_refused`, so the predicate keys on the body's content and not on which arm refused it.

This part builds Carry 17 alone. Carry 0, Carry 1, Carry 2, Carry 3, Carry 4, Carry 5, Carry 6, Carry 7, Carry 8, Carry 9, Carry 10, Carry 11, Carry 12, Carry 13, Carry 14, Carry 15, Carry 16, Carry 18, Carry 19, Carry 20: the group's other carries, which the brief records as delivered by parts 1 (#3664) and 2 (#3701), both merged; this diff touches none of them.

Alternatives: (a) parse the BODY-LINT output for the `REFUSE ref_privacy (body)` line and skip the keep for that arm only. It lost because it keys on another script's wording and covers one arm, while the same body refused first by the predictor or the review packet would still be kept. (b) the chosen fix: reuse the existing predicate, add no new classifier, put it in one place.

## Head

ae619d80a8643e62eabf91360a0b30f786ef0e8e

prepr: passed rc=0 at ae619d80a8643e62eabf91360a0b30f786ef0e8e

## Mutation proof

Changed the fix's predicate line (the `# mut:privacy` `if`) to `if false; then` in place and ran `bash tools/audit/seat/body_push.sh --self-test`: rc 1, and these checks failed:
- `... and nothing is kept on origin`
- `... and the output says so and names the local body`
- `... and prints no keep line`
- `PRIVACY: the predictor arm keeps nothing either`
- `PRIVACY: a RESUME note naming this host keeps nothing either`

After restoring the line, the self-test passed 57 of 57. The self-test also carries this mutant as its own arm (`MUTANT mut:privacy`, a sed copy), which asserts that the privacy body is kept when the predicate is false.

Test first: the new arms were added before the fix and run against the unfixed `keep_refused`. The same five checks failed and the null-control and mutant arms passed. That is the expected shape, since the unfixed tree keeps every refused body.

The fix does not classify text by shape. It delegates to `ref_privacy.body_lines`, whose spelling corpus is `ref_privacy.py --self-test`'s and is unchanged here, so this PR adds no corpus.

## Null control

- The same body, which names a fixture account's home, run under another non-public fixture host. `body-lines` does not refuse it, so this is a non-privacy BODY-LINT refusal, and it is kept on `handoff-wip/t-body`, its text intact (`null control: the same body under another host ...`, ok).
- The existing per-arm loop (pred, lint, packet, landed) on a body with no host identity still keeps each refused body (its 4 x 6 checks, ok).
- At the merge base the self-test prints 49 checks, 0 failed. The head adds 8 checks. The `fatal: --negotiate-only` line in its output is printed at both ends.

## Figures

- `bash tools/audit/seat/body_push.sh --self-test`: base 49 checks 0 failed; head 57 checks 0 failed; the in-place mutant 5 failed (list above).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED`, scope.run names `tests/doc_claims.py`. Ran it with `PYTHONPATH=tests/hastub`: all checks passed.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Fixture home: the self-test's fixture host home is `/srv/<account>`, outside the `/home/<x>`, `/Users/<x>` grammar that `ref_privacy.py --check` and `tmp_paths.py` refuse in a tracked line; `ref_privacy.body_lines` still reads it as this host's home, as the 5 failing mutant checks show.
- Class enumeration (fixer step 8). Rule: `git grep -n -i "refused body\|keep_refused\|body_keep" -- ':!tools/audit/seat/body_push.sh'` lists the tree's writers of a refused body to origin outside `body_push.sh`. It returns no writer: the hits are `cloud_relay.sh`'s carry_fold_arm, which reads a kept body and re-runs `body_push.sh` and so passes through this fix, plus roster, triage and RCA text. The one writer, `keep_refused`, is closed in this diff.
- Architecture score: the diff touches only `tools/audit/seat/body_push.sh`, a shell instrument. `gate.py` reads it at CI. It was not measured locally.

<!-- figure-block: scope-line mb=7c2f4c30cab5610cf8f5b040c326836ab544d27d head=ae619d80a8643e62eabf91360a0b30f786ef0e8e -->
~~~text
MODE: SCOPED -- 1 script(s) run, 32 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

none

## Friction

none
