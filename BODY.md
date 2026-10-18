Red repair after #2423 (merged as 89e33859). That PR's merge-subject guard in `tools/policy/agreement.mjs` walked `--first-parent` from HEAD back to 07a09406. On a pull-request branch, that walk reaches the branch's own `Merge origin/main into <branch>` commits, which `fixer.md` step 6 requires. Their subject is git's, not GitHub's, so the guard refused every recarry in prepr. On #2420 it printed `REFUSED merge-subject-pr aa8ada780 "Merge origin/main into record/autofix"`.

**Fix.** The guard now judges only main's first-parent line. Its walk ends at `git merge-base HEAD refs/remotes/origin/main` (`mainLineEnd`) instead of at HEAD. That end is:
- HEAD itself, on main's push run;
- the base, on a pull request's test merge;
- the last main commit merged in, on a recarried branch.

A branch's own merge onto main is written by GitHub, and main's push run judges it. With no origin/main ref the walk falls back to HEAD. There every first-parent merge is judged, so a branch's own merges are refused by name rather than passed unseen. Both arms of the guard are unchanged:
- a custom-subject merge on main is still refused;
- a tracked merge call that passes a subject or body is still refused.

**Self-tests on a real repository.** The repository is built by `tests/throwaway_git.py`'s `throwaway_git_init`, called through `python3 -I`, and every probe's git call uses the environment it returns. That puts auto-maintenance off in both the environment and the repository's config, and nothing raw is left for `throwaway_git.py --check` to refuse. Four probes:
- a recarried branch's own `Merge origin/main into fix/x` is not judged;
- with `Merge pull request #2 (custom)` on origin/main, the guard run from a recarried branch refuses exactly that commit;
- run on main itself (HEAD = origin/main), it refuses exactly that commit;
- with no origin/main ref, the fallback walks HEAD and refuses exactly that commit.

**Alternatives considered:**
- Accept git's `Merge ... into ...` subjects as a third template. That fails because a hand merge on main with a git-style subject would then pass.
- Skip merges whose second parent is on main. This is equivalent, but more code than reading the merge base.
- An `ALLOW` entry in `tests/throwaway_git.py` for a raw `git init`. That fails because a JS path to the shared mechanism exists, through `python3 -I`, so no exemption is needed.

## Head

240a8f5b454f5a16fbf7867136d65a225171c17a (merge base 89e33859a, origin/main at 2026-10-19).

## Mutation proof

- The fallback made to pass everything, `catch { return SUBJECT_CUTOFF }` (the review's mutant): `FAIL with no origin/main ref the walk falls back to HEAD and refuses a hand subject there`, `SELF-TEST 26 of 27 probes held`. Each walk probe now requires the refusal to name the hand-subject commit. A count alone was satisfied by the walk's own "cannot walk" refusal, which is how this mutant had held 26/26.
- The walk's end restored to `${cutoff}..HEAD` (#2423's form): `FAIL a recarried branch's own \`Merge origin/main into <branch>\` is not judged` and `FAIL a hand subject on main is refused from a recarried branch, and only it`, `SELF-TEST 25 of 27 probes held`.

## Null control

- A sample recarry: a local copy of #2422's branch (head ee93af58) with origin/main (89e33859) merged in by `git merge --no-ff`.
  - Under origin/main's `agreement.mjs` (the #2423 guard) the lane refuses the new merge 45d1068f8 and the branch's own earlier merge 0670b9cea: `RESULT ... refused=2`.
  - Under this head's `agreement.mjs`: `merge-subject guard: 1 first-parent commit(s) past 07a09406a`, `RESULT divergent=0 unregistered=0 dead=0 refused=0`. The copy and its branch were deleted afterwards.
- At this head, unrecarried: `pair merge-subject-pr: 4 readers, ... 0 divergent`, `RESULT ... refused=0`. The pair's item count is the distinct first-parent subjects in `v6.5.0..HEAD` plus the fixed shapes in `agreement_py.py`, so it grows by one with each commit on HEAD's first-parent line. The body states the rule, not the number.

## Figures

- `node tools/policy/agreement.mjs --self-test`: `SELF-TEST 27 of 27 probes held` (23 at the merge base).
- `python3 -I tests/throwaway_git.py --check`: `throwaway_git: 0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD` (it refused `tools/policy/agreement.mjs:441: rg(['init', '-q'])` at 931fa7b7).
- `python3 -I tools/audit/seat/ref_privacy.py --check` and `python3 -I tools/audit/seat/tmp_paths.py --check`: 0 refused. `node tools/policy/field_coverage.mjs --self-test`: `FIELD COVERAGE SELF-TEST ok`.
- `python3 -I tools/policy/agreement_py.py --out <scratch>/g.json && node tools/policy/agreement.mjs --py-json <scratch>/g.json`: the lines quoted under Null control.

## Red checks

- `instrument-self-tests` (red at 931fa7b7 and 63d4d2b2, caused by this branch). `tests/throwaway_git.py --check` refused the self-test's raw `git init`; this head routes it through `throwaway_git_init` (above). Cheaper detector: the same `--check`, under a second locally, which exists but is in no local path. `tools/pr/prepr.sh` ran clean at 931fa7b7 without it. Process state: (b), the process existed (the `instrument-self-tests` lane) and was not run locally. Countermeasure, for the orchestrator to dispatch: prepr runs `throwaway_git.py --check`, standing cost under one second per run.
- `pr-contract` (red at 63d4d2b2). It is red because `## Red checks` did not name `instrument-self-tests`; this body names it.
- `wave-script`. #2423's guard refused locally in prepr's agreement step on every recarried branch. It would have reddened `wave-script` on every recarried PR once the guard was on the base, which it is since 89e33859. Cheaper detector: the real-repository walk self-test added here. Process state: (c), #2423's controls ran over a log handed in, never over the walk.
- `delivery-status` (red at 63d4d2b2), inherited from main. Main's delivery rows for the record-autofix merges #2413, #2412 and #2407 are overdue (`DELIVERY STATUS OVERDUE`, 3 overdue), and #2420 fixes it. This diff touches nothing that job reads.

## Forward-carry

none

## Friction

none
