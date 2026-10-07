Fix review: blocked 79ca6b475001749e33625ad066b7085d17bbc92a d-unbounded: batch merges onto a red main, so revert-first cannot bound D
bus-nonce: c53376a4fc90d826c63ed17d3bcacbc5

Round 1. Reviewer seat review-2044, detached worktree at 79ca6b47. The policy files were current against origin/main (`git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` printed nothing). R9-RO-12 has no finder harness. The fixer's mutation drive and self-test are the instruments. The probe below is my own, and I say so.

## Blocking 1: D's bound is not enforced (the attack the brief named)

D lands a lone entry unproved and relies on `main`'s FULL push run plus revert-first (orchestrator.md section 11). That bound holds only if each D merge lands on a `main` whose own push run is complete and green. `batch` never reads `main`'s state. `wait_ci` is called at the entry heads (L296, L410) and at the proofs (L502, L525), and never at `origin/<base>`. The old `run` was implicitly guarded: re-merging `main` into the head made a red `main` show up as a red head. `batch` takes that guard away and puts nothing in its place.

Probe: `evidence/probe_red_main.py` adds three cases to the PR's own `_batch_self_test` world. In each, `main` goes red after the heads were cut green. Output is in `evidence/probe_red_main.out`.
- RESULT lone entry, main red: rc=0, merged=[1], with no proof. TRAIN DONE. The FULL push run that follows is red because of `main`'s own break. Revert-first then reverts #1, which is the wrong merge.
- RESULT pair, main red: rc=0, merged=[1]. The proof was red only because `main` was red. The two-left rule blamed #2, sent it to serial, and D-merged #1 onto the red `main`. Here the train merged after observing a red. That is worse than plain D.
- RESULT null control, main green, same world: merged=[1, 2]. Both probe checks fail at the head: 76 checks, 2 failed.

The same gap allows back-to-back lone merges inside one push-run window, about 45 minutes by the body's own figure. A red push run would then sit on top of two unproved merges, and section 11's "the merged diff" no longer names a single merge. The policy does say who reverts: section 11 is the orchestrator's contract, and it says "Then `main` is green after it ... revert first". But the instrument that section 11 now names as the landing path does not hold that precondition.

Requested fix, cheapest shape: `batch` refuses to admit or merge anything until `origin/<base>`'s required contexts are completed and green at its tip. Use `wait_ci(tip, only=required())` with the same 5-minute poll. Give it a self-test that fails without the guard (the two probe cases above), and add a mutant to the drive.

## Blocking 2: section 11 and nudge.md now disagree on merge_fastpath

Section 11 at the head removed the `merge_fastpath.py ... ELIGIBLE` bypass entirely, so `batch` is now the only landing path it names. nudge.md section 18 still says "Only `merge_train.py batch` or an eligible `merge_fastpath.py` skips the CI wait". Either both files name the fast path or neither does. The fixer should pick one, and the body should state which. orchestrator.md sits at 4096 of 4096, so any wording added there must be paid for first.

## Verified (these survive to the next round unless the code moves)

- Mutation drive `bash dev/audit/harnesses/r9_ro12_batch_mutants.sh` re-run: M0 74/0, and every one of M1–M10 is red with the failures the body names (M5 IndexError; M6 10 failed). Output: `evidence/mutants.txt`.
- Self-tests: merge_train 74/0, merge_fastpath 35/0, app_push 60/0 (`evidence/selftests.txt`).
- Live null control (`evidence/live-trees.txt`, `checkruns-cb9b1831.tsv`): proof cb9b1831 has all 14 non-PR-only required contexts present and green, out of 34 runs. `7ad7026d^{tree}` equals `cb9b1831^{tree}` (b243c101). `ddf33d15^{tree}` equals `cb9b1831^1^{tree}` (ecab3090). The base is f637d24a. I recomputed both proof trees with plain `git merge-tree`, no driver, and got identical results.
- Live perturbation (`checkruns-d8f8d050.tsv`, `policy-docs-d8f8d050.log`): env-matrix and policy-docs are failures at d8f8d050. The log reads `about 60358 tokens exceeds the cap of 60091` and shows the D13/D12 duplicate. The base 9395f6c2 is f6a962e2 plus one commit touching only `policy_budgets.json`. The tree of `a39528cc` (1d7a815b) equals my recomputed text merge of base and #2035's head.
- The proof build uses text merge. Every `merge=` driver named in base's `.gitattributes` (claimnotes, ledgermerge) is overridden with `git merge-file`. A user-defined driver takes precedence over a built-in one in ll-merge, and M1 shows the override is load-bearing.
- Main's tree is compared with P_(i-1) before each merge attempt (guard, L376, re-fetching each time) and with P_i after (L382). A stamp or record PR landing mid-batch fails the guard. An autofix push or force-push to an entry trips `land`'s `head(pr) != h` check, and `--match-head-commit` rejects it in any case.
- Serial routing: workflow, claim, grader and every `*_budgets.json` change go through `file_class` (M4). A policy path stops the batch at admission rather than routing serial, which is consistent with `run`.
- Bisect: the two-left case drops the later entry and D-merges the first. The ≥3 case proves every all-but-one set. Attribution re-proves after each drop, and the loop terminates because `kept` shrinks each round. This is correct apart from Blocking 1, which is what turns the two-left rule into a merge-after-red when `main` is red.
- Ruleset 23698884 `main-protect-checks` has `strict_required_status_checks_policy: false`, so a head behind `main` can be merged as the batch needs. The live rehearsals ran on unprotected `batch/` bases, so this is the only evidence that the real-main path is mergeable (`evidence/ruleset-checks.json`).
- Policy caps (`node tools/policy/policy_lint.mjs --budgets`, rc 0): orchestrator.md is at 4096 of 4096 and nudge.md at 3804 of 3814. The full lint run exits 0.
- VERSION, the manifest and the notes heading are untouched. Claim files are untouched. `git merge-tree --write-tree origin/main HEAD` exits 0.

## Residual, non-blocking (for the fixer to fix or record)

- There is a gap between the guard and `gh pr merge`, so another merge can still land in between. Only the post-merge tree check catches it, after the fact. GitHub's merge has no expected-base parameter, so the body should name this as a residual risk.
- The post-merge check compares tree(`origin/<base>` tip) with P_i, not tree(land's returned merge sha). A commit landing just after ours gives a false stop, which is the safe direction.
- `merge-tree` reads `.gitattributes` from the checkout it runs in. A driver named only there, and not in base's `.gitattributes`, is not overridden. The post-merge check is the backstop.
- `batch/<tag>-<n>` branches are never deleted, so they accumulate one or more per batch.

## CI at the head (CI's check-runs, read 2026-10-08)

At 79ca6b47 there are 36 runs. fast (3.14), mutation, policy-docs, closure-scope and pr-contract (both runs) are success. budget-raise-gate is cancelled with a success twin. delivery-status and nightly-status are red. They are not this PR's red by `defect-root-cause.md` unless the diff reaches what they read, and the row file is the only thing in the diff they read. Analyze (python) and coverage were still in progress when read. The body's "Red checks: none" will need re-checking at the next head.
