Fix review: merge fd0d130a7e040c64da4fcd93c1ca2aa2a2fc9f56

bus-nonce: 1b8bb8785e0ccfb4ed783e7aa389c480

## Round

Third-round delta review of #3221 (R10-HANDOFF-PATH part 1), from the previously reviewed head 20d5aab00a01cb3bf3738e1e78a13273089bc523 to fd0d130a7e040c64da4fcd93c1ca2aa2a2fc9f56. The review ran in a detached worktree at that head. Main's `dev/governance/roles/` has not changed since the merge base, so the contract is current.

## Evidence

- RESULT the two round-2 blocks are cleared. `bash tools/audit/seat/pr_args.sh --self-test` gives `174 checks, 0 failed`, rc=0 (ev/selftest-pr_args.log). The (e) mutant, `[ "$n" = 0 ] ||` replaced by `true ||` at tools/pr/app_push.sh:313, gives `227 checks, 1 failed`: `FAIL real git (e): two tree-neutral commits past the clean merge run the full prepr`. Its null-control row `real git: the clean merge without them reuses` still reads `ok` under the mutant (ev/mutant-e.log). Unmutated, the suite gives `227 checks, 0 failed` (ev/selftest-app_push.log). The mutant is killed.
- RESULT self-tests of every seat script the diff edits, at this head:
  - open_pr.sh and update_pr.sh: `174 checks, 0 failed`, rc=0
  - app_push.sh: `227 checks, 0 failed`
  - prepr.sh: `509 passed, 0 failed`
  - body_push.sh has no `--self-test`, and it exits with a usage error, as the body says. Its trailer rows run inside prepr's self-test.
  - Every figure matches the body.
- RESULT my own extra mutants:
  - (b), the tree check in reuse_verdict, replaced by `true`: 1 failed, the `(f)` row (ev/mutant-b.log).
  - prepr.sh's main-flow `merged_steps "${1:-}" "$UNPINNED_SITES"` call deleted: `508 passed, 1 failed`, the `(a) ... runs tests/structure.py and ci predict on HEAD merged with main` row (ev/mutant-mergedsteps.log).
  - Both mutants are killed.
- RESULT planted receipts, written by me and run against the production `reuse_verdict` extracted from this head (ev/plant.sh, ev/plant.out). Every plant was refused fail-closed (rc=1, full prepr):
  - P1: the trailer names another head that is not in HEAD.
  - P1b: the trailer names main's tip, which is in HEAD.
  - P2: a code commit after the receipt, then main merged.
  - P2b: the receipted code was amended.
  - P3: the same change rebased onto a new base.
  - P3b: HEAD merged with a fork of main.
  - P4: a forged tree.
  - P5: a short sha.
  - P6: an evil merge that edits the code in its resolution.
  - The null control, a genuine receipt at the clean merge, reuses (rc=0) both before and after the plants.
- RESULT a receipt never skips the merged-tree checks. `merged_steps` is called unconditionally after step 6d. Under `PREPR_SKIP_CODE` it runs `tests/structure.py` and ci predict on HEAD merged with main, which is pinned by the `(a)` row and the mutant above. `pr-contract`, `policy_lint --pr-body` and `carry_audit` still run through `row_only_checks`; the `ureused`/`ufail` rows pin this.
- RESULT no gate weakening for a pull request without a receipt:
  - With no `--reuse`, or when the verdict fails, prepr runs with no `PREPR_SKIP_CODE`. The `unorcpt` row pins this.
  - Every skipped group is `if [ -n "$REUSE" ] ... else <original steps> fi`.
  - The only full-run change is an added check, `tests/structure.py` on the merged tree, which is stricter.
  - CI's required checks are not touched by the diff.
- RESULT the merge resolution kept both sides. `git diff 79f765e6...HEAD -- tools/pr/prepr.sh` removes only the recorder-cache line (moved earlier) and splits one `rm` line. Main's 8f6f0ea2f, 18481fd52 and 1584530f3 (git log 91a75ed8..c0b082bc) are in the merge base and are unreverted. Their five lazy `take_slot` calls sit at lines 4183, 4246, 4315, 4395 and 4438, inside the code-keyed groups or behind `elif [ -n "${REUSE:-}" ]`, so a reuse run takes no slot.
- RESULT merge with main: `git merge-tree --write-tree origin/main HEAD` exits 0 against origin/main cd0dd16910898553bb85a95bf718840b131b1a82 (ev/merge-tree.txt).
- RESULT CI: `merge_train.py classify fd0d130a... --pr 3221` printed `GREEN fd0d130a7e040c64da4fcd93c1ca2aa2a2fc9f56 pending: none red: none`, rc=0 (ev/classify.log).
  - All check runs, across all pages, are in ev/checkruns.txt (68 rows). The only concluded reds are `governance / delivery-status` (127154477191) and `tests / nightly-status` (127154477012).
  - delivery-status is OVERDUE on other pull requests' merged rows (#3181, #3191, #3201, ...), not on #3221's open row (ev/delivery-status.txt). Neither red belongs to this pull request (defect-root-cause.md), and the body answers both.
  - `pr-contract` ran three times after those reds concluded (127167424591, 127168457422, 127169743851), and all three passed. `gate` passed. `instrument-self-tests` (127154477241) passed.
- RESULT the body's `## Head` names fd0d130a7e040c64da4fcd93c1ca2aa2a2fc9f56, which is the head I measured. It was still origin's `fix/r10-handoff-path-p1` before I returned this verdict.
- VERSION, the manifest and RELEASE_NOTES.md are untouched, and so are both claim files (packet figure_lint; the three-dot diff touches none of them). No golden file is touched, so env_drift is not applicable.
- The PR carries no budget move, no `closures.json` change and no INERT change.
- No finder's harness is named. This is an owner-directive tooling change with no audit finding. The review used my own plants, which are disclosed here as mine (ev/plant.sh).
- Not re-derived by me:
  - the 27 s kept-step wall time (the body says it was not re-taken);
  - round 2's mutants P1, PH, P3, P6, M2b, M5 and M6, which the body cites from acd20e42.
- The unsigned-receipt property remains: anyone who can write `handoff-body/<topic>` can name a receipt. P386 dismissed it, and the merged-tree checks still run.

## Findings

- Follow-up: the body's `## Red checks` gives the delivery-status OVERDUE rows read at the earlier head 20d5aab0 (#3174, #3091, #3089, #3192). At this head the run lists #3181, #3191, #3201 and others. The disposition, "not this diff's red", is the same, and pr-contract passed, so this is only a stale figure. Carry: dismissed: the disposition is unchanged and the figure belongs to a non-required check outside this diff
