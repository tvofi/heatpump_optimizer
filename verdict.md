Fix review: merge 5ec2425619161036210ed6a20428ea2f96466e95

bus-nonce: 85fcc1371ae14cd748dc298f9ce7ff4f

Round 1 of topic r10-hotfix-restore-base-skew (part 1 of 2), reviewed from a detached worktree at the handoff tip 5ec2425619161036210ed6a20428ea2f96466e95. The verdict attaches to that SHA only.

## Findings

- The PR-only callee reader in prepr.sh (`PIN_AWK`'s `expr = "pr"` regex) admits four leading sources, but the self-test drives only `inputs.restore_source` through it. The reviewer's mutant PM7 deletes `|steps\.source\.outputs\.sha` from the "pr" regex alone, and it survives: `bash tools/pr/prepr.sh --self-test` gives rc=0 and `527 passed, 0 failed` (ev/mutants.txt). By the same construction, the `needs.(prelude|gate)` alternatives in that regex are also unexercised (not run separately). The survivor fails closed: dropping an alternative makes a pin unclassified and refused, never admitted. So the cost is a false refusal on part 2's first CI run, not a hole. Carry: dismissed: fails closed, and part 2's own workflows, graded by this reader, exercise whichever callee form they use

## Evidence

- No review packet. The brief says no pull request exists yet, but PR #3463 does exist (fix/r10-hotfix-restore-base-skew, head dd0dcd3b6b). `review_carry.py 5ec2425619 dd0dcd3b6` prints `CARRY`: the delta is a merge of origin/main plus `dev/programme/delivery/3463.md`. That head's CI had not concluded when read (ev/pr3463-checks.txt). `gate` was red with "run(s) [43017202337] at this head are still being judged; their gate decides" (a judge that ran before its run finished, not a defect verdict). `tests / coverage` was in_progress. `governance / instrument-self-tests` was red, but it is outside `merge_train.py owed-reds` (ev/owed-reds.txt). pr-contract was skipped. A red CI never carries (fix-review.md step 12), so this merge does not attach to dd0dcd3b6 until that head's owed checks conclude green. The handoff tip has no CI of its own. The body's `## Red checks: none` is therefore accurate for 5ec2425619, and no owed red was concluded on any head to answer.
- Step 7, head: the body's `## Head` names 5ec2425619, the tip I measured. The body's "No commit on main since the cut" is stale: origin/main is now ee64358be. But `git merge-tree --write-tree origin/main 5ec2425619` exits 0 (tree 8b42bf42ff), with no conflict (ev/merge-tree.txt). Neither changed file differs between a7628041dc and origin/main.
- Step 1, mutation proof re-run with the reviewer's own driver (ev/mut.sh, ev/mutants.txt), not the fixer's:
  - codeowners_gap.py `--self-test`, 58 probes, 19 nulls:
    - Killed: M1 admission off (4 wrong), M2 any input leads (1 wrong), M3 gate dropped (1 wrong), M4 step dropped (1 wrong), M5 separator not required (4 wrong).
    - Survived as equivalent mutants: NULL `bool(source)` -> `source is not None` (0 wrong), and the reviewer's own M6 `.match` -> `.search` (0 wrong). PINNED_SOURCE is `^`-anchored without `re.M`, so search equals match.
  - prepr.sh `--self-test`: baseline rc=0 with 527 passed.
    - Killed: PM1 source group dropped from "both" (rc=2, 523 passed, 4 failed: restore-input, restore-prelude, restore-gate, restore-step; the body quotes this as one line). PM2 dropped from "pr" (rc=2, 1 failed). The reviewer's PM6, any `[a-z_.]+` leader in "both" (rc=2, the foreign-source null fails). PM5 step dropped from "both" (rc=2, 1 failed).
    - Survived: PM7 (see Findings).
    - Also run: PM7x, a mis-built mutant that left an empty alternative, `restore_source|)`. It is recorded as built and killed (1 failed).
  - Every prepr.sh run used `HPO_GATE_PRIORITY=0`, like the fixer's (see Forward-carry).
- Steps 2-3, harness and null control. The finder's harness for this part is the two graders' own `--check` and pin read. There is no separate committed finder harness here; `dev/audit/harnesses/r10_restore_base_skew.py` belongs to part 2, by the body's account.
  - Null control re-taken: main's (= base a7628041dc) copy of codeowners_gap.py, run from the head's tree over the same workflows, prints the same five RESULT lines as the head's copy: `enforcement_surface_files=206`, `covered_by_an_owner=68`, `pinned_by_base_restore=138`, `of_which_no_pr_job_runs=119`, `uncovered_files=0`. The diff is empty (ev/cg-base-check.txt, ev/cg-head.txt).
  - The base copy's self-test prints `55 probe(s), 15 null(s), 0 wrong`; the head's prints `58 probe(s), 19 null(s), 0 wrong`. Both match the body.
  - Not re-derived: the body's 81-line byte-identical prepr.sh `pin_read` comparison, base copy against head copy. PM1 at the head reproduces the base reader's refusal of each new form, which covers the test-first claim.
- Step 6, attack and class. A PR could redefine the admitted indirections: `steps.source`, the prelude and gate outputs, and the caller-supplied `inputs.restore_source`. But they live in `.github/workflows/`, which CODEOWNERS line 97 assigns to `@tvofi`. That is the same trust basis as the already admitted `inputs.base`. The body's probes and the reviewer's PM6 show that a foreign leader (`inputs.head ||`, `github.sha ||`) is refused, and so is a source with no base fallback. The class is a one-rule, two-reader seam, and both readers are in the diff.
- Step 8, figures at 5ec2425619, re-taken (ev/figures.txt, ev/entities.txt):
  - `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
  - `ALL 2707 ENTITY CHECKS PASSED`, with `HPO_GATE_PRIORITY=0`
  - `ALL 112 HARNESS HEADER CHECKS PASSED`
  - `STRUCTURE RATCHET PASSED`
  - `RESULT uncovered_files=0 count`
  - prepr.sh self-test: 527 ok lines
- Steps 4-5: `VERSION`, the manifest and RELEASE_NOTES.md are untouched, and `tests/golden` is unchanged, so no claim is owed.
- Step 10, forward-carry: the body's `HPO_GATE_PRIORITY` finding is in the tree. It is in R10-PROCESS-SLIM's `carry` list in `dev/programme/rosters/wave-r10-groups.json` at `handoff/audit-r10-roster` 329c996e8e, with its control (`HPO_GATE_PRIORITY=2` gives 2 of 2707 failed, `=0` passes). The two part-2 roster carries (e41acc16, 530feedf) are dispositioned to part 2, whose census is not in this diff (`git diff a7628041dc...5ec2425619 -- tests/` is empty).
- Steps 14-15: the diff moves no budget, closure, INERT entry, golden or score. It touches no `custom_components/` code. The added `_pinned_ok` helper and the regex group extend the existing readers in place.
