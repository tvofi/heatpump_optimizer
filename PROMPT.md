CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-plan-page-residue, at head 9774026d059395474cd3a8fb115320c6a7dd3248. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 9774026d059395474cd3a8fb115320c6a7dd3248 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-plan-page-residue before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-plan-page-residue, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-plan-page-residue, even with no code. Then push the code to refs/heads/handoff/r10-plan-page-residue, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-plan-page-residue <body.md>`, which pushes refs/heads/handoff-body/r10-plan-page-residue; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-plan-page-residue`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-plan-page-residue and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-plan-page-residue and refs/heads/handoff-wip/r10-plan-page-residue-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
REPAIR ROUND 2 for R10-PLAN-PAGE-RESIDUE (size M), pull request 3428, head 9774026d059395474cd3a8fb115320c6a7dd3248 (handoff/r10-plan-page-residue 1be2e399191dc8613371955ec5e8e2f0b5812ab9 is an ancestor of the PR head). Continue from the PR head; do not re-cut.

SCOPE. The group's roster carries (Carry 1 through Carry 6) are this PR's scope; keep each named as `Carry N` in the body. Any carry marked PART 2 ITEM is out of this part.

THIS IS THE SECOND BLOCK. The next review is round 3. In one pass: list EVERY survivor the verdict names, kill each with a pin or a deletion, and land the durations input driver as a tracked harness (fixer.md step 18). Run `mutant_run.py --diff` before the handoff and hand off only with zero unanswered survivors. If the fix cannot be made minimal, say so in BLOCKED.md rather than hand off a partial.

----- REVIEW VERDICT (verbatim) -----
Fix review: blocked 9774026d059395474cd3a8fb115320c6a7dd3248 mutation-vacuous: hot-render hot-gates hot-discharged hot-notdone, and the durations input driver is not landed (fixer.md 18)

bus-nonce: 874a9352450cf4d9810664f7dbb5465d

Round 2 (delta re-review of 3bfdec2a09..9774026d05). The measured head is 9774026d059395474cd3a8fb115320c6a7dd3248. It was still the branch tip when this verdict was written (ev/head-at-verdict.txt).

## Block

The delta answers all three items the round-1 block named, and both of its findings. Two defects remain in what the delta adds.

- **The hotfix mark (Carry 5 item 3) is not pinned where it is drawn.** The self-test checks the `hot` flag on the rows from `build_rows`. Its `hot_page` is built from those rows, not from the rendered HTML. No check reads `hotcp`, `▲` or the title "hotfix blocking a critical-path group" in the page. My driver (ev/my-mutants.txt, ev/my-mutants-driver.py) found four survivors at this head. Each had `plan_page.py --self-test` rc=0 with no FAIL line:
  - `hot-render`: the `▲` span's `if r["hot"]` changed to `if False`. The carry's deliverable disappears from the page and nothing fails.
  - `hot-gates`: `roster_lib.gates(G[a])` dropped from `gating_crit`. A predecessor in a releasing stage would be marked. The body says the mark uses "the same gating edges as `Blocked by`", but nothing pins that.
  - `hot-discharged`: `a not in discharged` dropped from `gating_crit`.
  - `hot-notdone`: `g not in done` dropped from `hot`. This may be equivalent if every closed stage is a releasing stage. I did not establish that.

  Fix: add a page-level check that the `hotcp` mark appears exactly on the hot rows, and none on the cold fixture. Add fixture arms for a discharged predecessor and for a releasing-stage predecessor. For `hot-notdone`, either add an arm or record it as equivalent with the reason.
- **The re-measured `tools/plan/durations.json` cannot be reproduced from the tree.** The body says `size_durations.fetch` could not run (GraphQL 403). Its `--prs-cache` input was instead built over REST by a "scratch driver, sha1 8bba87c7...", and that driver is not in the diff. `fixer.md` step 18 says that a driver a body figure needs to be reproduced lands in the same pull request. `sizes_hours` (S 21.4, M 32.4, L 35.6, XL 35.6), `round_hours` 5.69 and `review_rounds` all depend on that input (ev/durations-diff.txt). The committed `sizes_provenance` also says "Measured by tools/plan/size_durations.py; re-derive, never edit", with no mention that the input was a REST-built cache. A reader re-deriving through the GraphQL path cannot tell whether a mismatch is drift or a different input. Fix: either (a) land the REST cache builder under `tools/audit/seat/` or `tools/plan/` and classify it, and state the REST input in `sizes_provenance`, or (b) have a seat with GraphQL re-run `replan.py --measure-sizes --out-durations` at the merge base without `--prs-cache` and commit that output, which the body already offers.

## Findings

- Follow-up: `size_durations.fetch` has only a GraphQL path. Here it turned a carry's one-command step into an unlanded scratch driver. The body's Friction dismisses this because "the relay has GraphQL". That dismissal holds only if remedy (b) above is taken. Under remedy (a) the REST path becomes tooling this PR lands. Carry: dismissed: settled by whichever remedy the block's second item takes in this PR

## Evidence

- Items the round-1 verdict blocked on, now answered:
  - Carry 0 item (1), closure conditions: `replan.CLOSURE_CONDITIONS` is in `summary.closure_conditions`. `check_plan` refuses a plan without it, and the page lede states it. The in-tree mutant `closure-conditions`, harness mutant `closure-conditions-text` and my `check-cc` (`check_plan` guard deleted) are all killed by a named FAIL.
  - Carry 0 item (3), durations: the file was re-measured in this PR (`sizes_measured_at` 2026-11-11T02:57:51Z, previously 2026-11-01T07:38:26Z). Its input is the defect in the Block's second item. I could not re-derive the figures: the cache and its driver are not in the tree, and this seat has no GraphQL. Carry: dismissed: evidence, not a finding
  - Carry 5 item (3), hotfix mark: built. Its row flag is pinned (harness mutants `hotfix-mark` and `hotfix-gates-crit` killed); its rendering is not, as the Block's first item says.
- Round-1 findings, now answered:
  - The `TypeError` arm now passes `str([...])`.
  - `review-min` and `wall-hours` are in-tree mutants, both "self-test fails when ... is deleted" ok (ev/selftest-replan.txt).
  - `eta-dash` and `zero-other` are recorded as equivalent. I re-ran `zero-other`: it exits rc=0 with no FAIL. That fits the body's equivalence claim, because the general path renders the same zero sentence. I accept it. Carry: dismissed: evidence, not a finding
- Removed mutant `stamp-on-axis`: `closure_at = max(stamps[-1].at, post_end)`, and the post-closure arm pins `pc["stamps"] == p0["stamps"]`, so no stamp lies past closure. Deleting the stamp term is a sound simplification, not a lost pin.
- Roster carries: the body names Carry 0 to Carry 5 individually (Carry 5 is also read as Carry 6). It does not send any item to a next part, and claims no part-2 item: Carry 5 item 3 is part 1 under round 1's reading. Carry 1 item 1 is still dispositioned "not reproduced". I did not re-derive the roster `source` figure. Carry: dismissed: evidence, not a finding
- RESULT self-tests at head: `replan.py --self-test` rc=0 "self-test: 0 failed"; `plan_page.py --self-test` rc=0 "91 checks, 0 failed". Both match the body's Figures.
- RESULT harness `r10_plan_page_mutants.py M0 hotfix-mark hotfix-gates-crit closure-conditions-text`: M0 null, three killed, `survived=0` (ev/harness-new-mutants.txt).
- Step 5: `VERSION`, the manifest and the notes heading are untouched. No claim or golden file is touched.
- Step 13: `git merge-tree --write-tree origin/main 9774026d05` rc=0, no conflict, against origin/main dbd1ab5b07 (ev/merge-tree.txt).
- Step 14: no budget, closures.json, INERT or golden file moves.
- CI: `merge_train.py classify` printed `WAIT ... pending: gate red: none` from 04:16Z on (ev/classify-poll.txt). This verdict's block does not depend on CI.
- Finder's harness: none. This is an instrument group fed by roster carries and closes no issue. Carry: dismissed: evidence, not a finding
