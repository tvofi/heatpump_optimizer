Red repair after #2423 (merged as 89e33859). That PR's merge-subject guard in `tools/policy/agreement.mjs` walked `--first-parent` from HEAD back to 07a09406. On a pull-request branch, that walk reaches the branch's own `Merge origin/main into <branch>` commits, which `fixer.md` step 6 requires. Their subject is git's, not GitHub's, so the guard refused every recarry in prepr. On #2420 it printed `REFUSED merge-subject-pr aa8ada780 "Merge origin/main into record/autofix"`, which blocked the drain.

**Fix.** The guard now judges only main's first-parent line. Its walk ends at `git merge-base HEAD refs/remotes/origin/main` (`mainLineEnd`) instead of at HEAD. Depending on where it runs, that end is:
- HEAD itself, on main's push run;
- the base, on a pull request's test merge;
- the last main commit merged in, on a recarried branch.

A branch's own merge onto main is written by GitHub, and main's push run judges it. With no origin/main ref the walk falls back to HEAD. There a branch's own merges are refused by name rather than passed unseen. Both arms of the guard are unchanged:
- a custom-subject merge on main is still refused;
- a tracked merge call that passes a subject or body is still refused.

**Self-tests on a real repository** (a temporary `git init` under the root, removed after the run):
- a recarried branch's own `Merge origin/main into fix/x` is not judged;
- with `Merge pull request #2 (custom)` on origin/main, the guard run from a recarried branch refuses exactly that commit;
- run on main itself (HEAD = origin/main), it refuses the same commit.

**Alternatives considered:**
- Accept git's `Merge ... into ...` subjects as a third template. That fails because a hand merge on main with a git-style subject would then pass.
- Skip merges whose second parent is on main. This is equivalent, but more code than reading the merge base.

## Head

931fa7b7b0867d157067c75fd202fe5965d36a32 (merge base 89e33859a, origin/main at 2026-10-19).

## Mutation proof

- The walk's end restored to `${cutoff}..HEAD` (#2423's form): `FAIL a recarried branch's own \`Merge origin/main into <branch>\` is not judged` and `FAIL a hand subject on main is refused from a recarried branch, and only it`, `SELF-TEST 24 of 26 probes held`.

## Null control

- A sample recarry: a local copy of #2422's branch (head ee93af58) with origin/main (89e33859) merged in by `git merge --no-ff`.
  - Under origin/main's `agreement.mjs` (the #2423 guard) the lane refuses ae3582d14 and the branch's own earlier merge 0670b9cea: `RESULT ... refused=2`.
  - Under this head's `agreement.mjs`: `merge-subject guard: 1 first-parent commit(s) past 07a09406a`, `RESULT divergent=0 unregistered=0 dead=0 refused=0`. The copy and its branch were deleted afterwards.
- At this head, unrecarried: `pair merge-subject-pr: 4 readers, 815 items, 0 divergent`, `RESULT ... refused=0`.

## Figures

- `node tools/policy/agreement.mjs --self-test`: `SELF-TEST 26 of 26 probes held` (23 at the merge base).
- `python3 -I tools/policy/agreement_py.py --out <scratch>/g.json && node tools/policy/agreement.mjs --py-json <scratch>/g.json`: the lines quoted under Null control.

## Red checks

- `wave-script`. #2423's guard did not turn a check red on CI, because a pull request's run restores the base's `agreement.mjs`. It refused locally in prepr's agreement step on every recarried branch. It would also have reddened `wave-script` on every recarried PR once the guard was on the base, which it now is, since 89e33859. Cheaper detector: a real-repository self-test of the walk, added here. Its standing cost is a few `git` calls inside the `--self-test` step. #2423 had self-tested the guard on a synthetic log only, which could not see which commits the walk reaches. Process state: (c), the process was followed and did not produce the intended result. #2423's mutation and null controls ran, but over a log handed in, never over the walk.

## Forward-carry

none

## Friction

none
