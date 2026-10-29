Fix review: merge 505e8aa6b3206d9ed1afbac649325bef530d3c1a

bus-nonce: 8a4f0da027e61d6ef278b3d3f926020b

## Round

Second fix review of #2953. The first blocked on the unanswered governance / policy-docs red. Measured head: 505e8aa6b3206d9ed1afbac649325bef530d3c1a, which is still the PR head at the time of writing. origin/main is ce5940c0d, and the merge base equals it.

## Findings

- A surviving mutant on a line the record claims. In `toolchain()` the record and body both say the EXPORTED branch "re-checks under that file". Deleting that re-check (`&& bash -c '. "$1" && bash "$2" --check' ...`) leaves the self-test at 16 passed, 0 failed (ev/mutants.txt, R2-no-recheck). The re-check carries weight. On a partly built prefix (venv-ci/ exists but bin/python3 does not, which is the A' venv-build case of #2947) the head prints REFUSE, and the mutant prints a false EXPORTED (ev/mutants.txt, "partial venv-ci" probe). It needs one more `ans` case: a stub venv-ci with no bin/python3 and a CLAUDE_ENV_FILE should read REFUSE. In that case the REFUSE wording ("no CLAUDE_ENV_FILE took them") also misstates the cause. Carry: R10-FLY-SUITE-ENV-FLAKES
- The record and body name a cheaper detector for the policy-docs red: emulate the base restore before predicting policy-docs, in prepr.sh/ci_predict.py. It is not built here. I checked that the body carries it, and the group exists in dev/programme/rosters/wave-r10-groups.json. Carry: R10-PREPR-CAP
- The owner step outside the tree: set the variables that `cloud-setup.sh --variables` prints, and re-paste the current setup script. It is reproduced live in this seat: `cloud-setup.sh --check` REFUSE, python3 3.11.17 (ev/checks.txt and the session output). This seat's own session-start hook is main's copy and printed no toolchain line, so the first live CLAUDE_ENV_FILE run is still the next seat dispatched after merge. Carry: dismissed: owner action outside the tree, already recorded in the RCA record section 5 and the PR body, which the orchestrator relays

## Evidence

- Null control for the red, with CI's policy-docs base restore reproduced. I used the exact pathspec list from governance.yml "Restore the check source from the base commit" and `git checkout $PINNED`, then `node tools/policy/policy_lint.mjs --hooks` (ev/restore_hooks.sh):
  - At 505e8aa6b3206d9ed1afbac649325bef530d3c1a, PINNED ce5940c0d: restored `tools/audit/seat/cloud-setup.sh`. Output: `SessionStart 16 passed, 0 failed`, `HOOKS ok: 3 wired hook(s)` (ev/hooks_head.txt).
  - At the old head 381cab4c6, PINNED its merge base: `SELF-TEST FAILED SessionStart 12 passed, 2 failed`, `HOOKS REFUSED` (ev/hooks_oldhead.txt).
  - The body's account of the red reproduces as stated.
- Mutation proof, re-run (ev/mutants.txt). Unmutated: 16 passed, 0 failed.
  - M1 (append replaced by `true`): 3 FAIL.
  - M2 (`--check` forced true): 4 FAIL.
  - M3 (`%q` to `%s`): 1 FAIL, the space-in-PATH case. My first M3 attempt did not apply, as noted in the file.
  - M4 (`--env-lines` arm emptied): 1 FAIL.
  - My own mutants: R1 (`export` dropped) gave 1 FAIL and R3 (n/a guard removed) gave 1 FAIL. R2 survived; see Findings.
- RCA record `dev/audit/rca/R10-RCA-FIXER-MD-KEY.md`:
  - Cause: section 1. Only group A, step 5 (python3 is not the seat venv), recurs.
  - Process state: section 2, state (d), with reasons it is not (b).
  - Cost test: section 4, about 8-10 ms per session start against 5-15 min per affected seat. The second figure is an estimate the record labels as untimed.
  - Countermeasure: built (the toolchain line). Refusals are recorded with numbers (keying by step; a policy edit to fixer.md).
  - All four parts the brief asks for are present.
- Figures re-derived at this head or current main:
  - `node tools/policy/policy_lint.mjs --stats --since v7.0.5` at 505e8aa6b3206d9ed1afbac649325bef530d3c1a reads `3 / 4 tools/audit/briefs/fixer.md <- at or over threshold`, which matches the body's 3 PRs / 4 entries (ev/stats_v705.txt).
  - Merged-PR counts: 286 at 279578074 and 285 at 88c6ad5bb, both matching the body (ev/figures.txt). The count is 289 at current main.
  - I did not re-take the v7.0.4 count (8 PRs / 11 entries). The body records it as measured at 88c6ad5bb, so it is not verified by this seat.
  - I did not re-time the standing cost of 34-37 ms against 27-39 ms. It is not verified by this seat.
- Class rule `git grep -n "on PATH from the environment"`: at 505e8aa6b3206d9ed1afbac649325bef530d3c1a no prompt or code site remains. The three hits are quotations inside dev/audit/rca/R10-FRICTION-GATE-SCOPING.md and this PR's record. The body's "returns none at the head" means no live site, and that holds. At 279578074 the one site was cloud_dispatch.py:137, as the body says.
- `git grep -- --env-lines` matches the body: session-start.sh, cloud_dispatch.py, the record. Nothing calls `cloud-setup.sh --env-lines`.
- Local checks at 505e8aa6b3206d9ed1afbac649325bef530d3c1a (ev/checks.txt):
  - `git merge-tree --write-tree origin/main HEAD`: exit 0, no conflict.
  - VERSION, the manifest and RELEASE_NOTES.md are untouched. Both claim files, the budgets, closures.json and closure.py are untouched.
  - `closure.py select`: MODE: SCOPED -- 0 script(s) run, 33 scoped out.
  - STRUCTURE RATCHET PASSED.
  - ALL 2471 ENTITY CHECKS PASSED, so the new files are classified.
  - cloud_dispatch self-test: 87 checks, 0 failed. cloud-setup self-test: 13 checks, 0 failed.
- CI at 505e8aa6b3206d9ed1afbac649325bef530d3c1a, from the check-runs API (ev/checkruns.txt). Every run has concluded.
  - The one red is tests / nightly-status. Its log grades main's nightly `slow` job, run 40835853528, and states it is not a required context and does not block. The diff reaches no workflow or nightly lane, and the body answers it.
  - governance / policy-docs is green here. It was the earlier red, and the body answers it under ## Red checks with the cheaper detector and its cost.
  - pr-contract / pr-contract was green on both runs, started 19:48:43Z and 19:50:47Z, after the nightly-status red concluded at 19:12:43Z. gate is green.
  - Every other check is success, skipped or neutral (CodeQL).
- Step 9: no finder's harness is committed for this group, and the review packet says "Finder's harness: none named". This is a root-cause seat whose instrument is the policy_lint --stats census, and I ran it myself. The hook self-test is the fixer's.
- The head SHA in the PR body is 505e8aa6b3206d9ed1afbac649325bef530d3c1a, matching the head I measured.
- The diff touches policy paths (.claude/hooks/, tools/audit/seat/). So merging also needs tvofi's code-owner approval, which the orchestrator gives under the mandate. I did not post, approve or merge anything.
