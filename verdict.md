Fix review: merge 8baf5eac34e3e9fa3c447f47ec898a6e588efab3

bus-nonce: 2a93fe40315154492407d38c81024eb7

Round 2. Round 1 (hpo-approver comment 6256537345) blocked 63d4d2b2a. Measured head: 8baf5eac34e3e9fa3c447f47ec898a6e588efab3, still the branch tip when this was written. origin/main is 89e33859a, which is also the merge base. Contract current: `git diff merge-base...origin/main -- dev/governance/roles/` is empty.

## Round 1 blockers, each re-checked

1. **ci-red instrument-self-tests: fixed.** The self-test repository is now built through `throwaway_git_init` via `python3 -I`. `python3 -I tests/throwaway_git.py --check` at head prints `0 raw git init or clone site(s) refused, 0 stale allow entries at HEAD` (`ev/throwaway_git-head.txt`). CI agrees: instrument-self-tests job 117824524152 is success, and its log prints the same line.
2. **Red unanswered: fixed.** `## Red checks` names instrument-self-tests with a cause, a cheaper detector, a process state and a countermeasure. pr-contract job 117824983420 started at 23:50:01, after the last red run concluded (delivery-status, 23:47:54), and it is success.
3. **Fallback arm unpinned: fixed.** There is a new probe, `with no origin/main ref the walk falls back to HEAD and refuses a hand subject there`. The round-1 mutant, `catch { return SUBJECT_CUTOFF }`, now prints `FAIL ...` and `SELF-TEST 26 of 27`. So does a variant of it, `SUBJECT_CUTOFF.slice(0)`.
4. **815 vs 816: dropped.** The body no longer quotes the count. It states the rule instead: distinct first-parent subjects plus the fixed shapes, so the count grows by one per first-parent commit. Locally the head gives 817, which is 816 at 63d4d2b2 plus one commit. That fits the rule. CI's run shows 815, but CI walks the base's readers over the test merge, so it is a different tree.

## Adversarial checks

- (a) **A branch with main merged in passes the agreement lane.**
  - 07a09406 + a commit + `git merge origin/main` (git's default subject): base gives refused=1, head gives refused=0.
  - The body's own null control, #2422's ee93af58 with 89e33859 merged in, reproduces. The base refuses 2 (b772b1ad3, 0670b9cea). The head prints `1 first-parent commit(s) past 07a09406a` and `refused=0`.
  - The GitHub test merge of this head into its base: refused=0.
  - Details in `ev/scenarios.txt` and `ev/nullcontrol-ee93-*.txt`.
- (b) **A custom-subject merge on main is still refused.** Main' is 89e33859 plus `Merge pull request #9 (custom)` (92059fff2). Each of these refuses exactly that commit:
  - the test merge of the PR head into main';
  - the push run, with HEAD = origin/main = main';
  - the PR head recarried with main'.
- (c) **The fallback refuses.** With no origin/main ref:
  - HEAD = main' refuses 92059fff2;
  - HEAD = a recarried branch refuses the branch's own sync merge;
  - HEAD = this PR head refuses 8baf5eac3, its own `Merge commit ...` subject.
- (d) **Nothing weakened.**
  - The merge-call arm (`subjectWriters`) is untouched.
  - The only change is the walk's end point, from HEAD to `merge-base(HEAD, origin/main)`. The commits after that point are main's, and main's push run judges them, where the end is HEAD itself.
  - A branch's own merges can never be on main's first-parent line: GitHub's merge commit takes the first-parent slot, and squash/rebase drop them.
  - Mutant M4, turning the refusal into a note, gives 6 FAIL and `21 of 27`.
- **Mutation proof (`ev/mutants.txt`).** Both of the body's mutants reproduce as stated: the fallback mutant gives 26 of 27 with the named FAIL, and `${cutoff}..HEAD` gives 25 of 27 with both named FAILs.
- **Figures at head.**
  - `SELF-TEST 27 of 27`, and 23 of 23 at the base (`ev/selftest-head.txt`).
  - ref_privacy, 0 refused; tmp_paths, 0 refused; `FIELD COVERAGE SELF-TEST ok` (`ev/figures-head.txt`).
  - Lane at head: `refused=0` (`ev/lane-head.txt`).
- **Merge with main.** `git merge-tree --write-tree origin/main 8baf5eac` exits 0 with tree 8760800c, no conflict.
- **Untouched files.** VERSION, the manifest version and the RELEASE_NOTES heading are unchanged. The diff is `tools/policy/agreement.mjs` plus this PR's own delivery row.
- **Body.** The head SHA in the body is the head I measured. Forward-carry is `none`, and none is needed.

## CI on this head (check-runs API)

- **Green:** instrument-self-tests, wave-script (agreement lane `refused=0`, run on the pinned base's readers), pr-contract (both runs), policy-docs, env-matrix, typing, briefs, mutation, closure-scope, arch-score, budget-raise-gate, hassfest, validate-hacs, CodeQL Analyze (actions, js).
- **Red:** delivery-status, from main's overdue rows (#2413, #2412, #2407). It is exempt, and #2420 fixes it; the body answers it anyway.
- **Still in progress when read:** browser, coverage, fast (3.14), CodeQL Analyze (python). The diff touches no Python and no UI, so those lanes cannot reach it; the orchestrator should confirm they finish green before merging.

## Non-blocking observations

- **M3 survives.** If `mainLineEnd` returns `refs/remotes/origin/main` instead of the merge base, the self-test still prints 27 of 27. The difference is real but is not a weakening. That mutant judges more of main's line, so a PR with an older origin/main merged in would turn red for main's own newer defect. The merge-base choice avoids that, but nothing pins it. A recarried-branch probe where origin/main has moved past the merged commit, carrying a hand subject, would pin it.
- **Stacked branches.** If a branch is cut from another PR branch A that carries its own sync merges, and A is merged before this branch recarries, then the merge base is A's tip. That tip is off main's first-parent line, so the walk would refuse A's git-subject merges: a false refusal, never a pass. Branches here are merge-gated and cut from main, so I did not treat this as blocking.
- **CI does not run this head's self-test.** wave-script runs the agreement lane and `--self-test` from the PINNED base (`SELF-TEST 23 of 23` in job 117824524154). The 27 probes therefore run only locally until this merges. That is the lane's design, not this PR's defect.

## Instruments

I built no harness of my own. I ran the repo's `agreement.mjs`/`agreement_py.py` and `throwaway_git.py`, applied my mutants by `sed`, and built scenario repositories in a `--shared` scratch clone.
