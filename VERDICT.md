Fix review: blocked 7cbfa680134ea1ddb34d202ef1ab11e0efb93807 mutation-vacuous: seat-gh ls-files tracked check (M2b), codescan_wait carried_over steps-absent clause (M3b)

bus-nonce: 1ad9850b0bd30fe0956cb8d70ee83b34

Round 1 (first review). Measured head 7cbfa680134ea1ddb34d202ef1ab11e0efb93807, merge base 63bcdcaad827ad3d98f914bc2e5b6110f9bb9444.

## Block

- M2b, tools/audit/seat/shims/seat-gh (the new admit block): replacing `git -C "$troot" ls-files --error-unmatch tools/pr/gh_comment.py >/dev/null 2>&1` with `true` leaves `gh_calls.py --self-test` at 204 checks, 0 failed. The body's null control "an untracked file of the same path and name" (t4) is refused by the worktree-registration loop, because t4 is not a registered worktree. It never reaches the tracked-file predicate. No arm plants an untracked gh_comment.py inside a registered worktree, so the "tracked" half of the PR's admission rule is unpinned. Owed: an arm with an untracked (or `git rm --cached`) tools/pr/gh_comment.py in a registered worktree that must stay refused (rc 1) and that turns rc 7 under this mutant.
- M3b, tools/ci/codescan_wait.py `carried_over`: dropping ` and "steps" not in j` leaves `codescan_wait.py --self-test` at 24 checks, 0 failed. Null control 23 ("a lagging step row ... is still unsettled") builds its jobs with `jobs()`, which carries no `conclusion` key, so `carried_over` is already False through the conclusion clause and arm 23 never tests the steps clause. Under the mutant, a completed/success job whose step row is present but lagging (or `steps: []`) reads as carried over, settled and uploaded. That is exactly the case the function's docstring says "is not this". Owed: arm 23 (or a new arm) with `conclusion: "success"` plus a lagging or empty `steps` that stays unsettled and not uploaded, and that turns red under this mutant.

## Findings

- Follow-up: tests/ci_ratchet.py `gather_runs.api`: the empty-stdout-is-a-failure branch (`or not (proc.stdout or "").strip()`) survives its own deletion (M4c, 67 checks 0 failed). The behaviour predates this PR (moved verbatim into `attempt`), so it does not block. Carry: dismissed: pre-existing unpinned branch moved verbatim, not introduced by this PR; the fixer may add a one-arm pin while re-cutting M2b/M3b

## Evidence

- RESULT self-tests at head (ev/selftests-head.txt, ev/app_push-head.txt): codescan_wait 24 checks 0 failed; gh_calls 204 checks 0 failed; ci-ratchet 67 checks 0 failed; seat_venv 27 checks 0 failed; app_push 230 checks 0 failed. Every self-test figure in the body re-derived green.
- RESULT mutants (ev/mutants.txt, driver ev/mutants_driver.py): the fixer's named mutants are killed. M1 app_push push without gh_read retry: 2 failed. M2a shim worktree admit never sets ok: 2 failed. M3a carried_over False: 1 failed (arm 21). M4a single read: 2 failed. M4b retry on every failure: 1 failed (404 null control). M3c conclusion clause dropped: killed (arm 22). M2b and M3b survive (Block). M4c survives (Findings).
- Equivalent mutants, not counted: M2c (`[ "$broot" != "$gcpy" ] &&` dropped): when gcpy lacks the suffix, broot is a file path, `git -C <file>` fails and the loop admits nothing. M3d (status clause dropped from carried_over): the API never reports conclusion success on a job that is not completed, and settled() checks status first (arm 24 is pinned by that earlier check, not by carried_over).
- Merge with main: `git merge-tree --write-tree origin/main <head>` rc 0 (ev/merge-tree.txt). The head is 0 commits behind origin/main.
- VERSION, the manifest version, the RELEASE_NOTES heading, both claim files, closures.json and the budget files are untouched. The three-dot diff touches 6 files: dev/programme/delivery/3427.md, tests/ci_ratchet.py, tools/audit/seat/gh_calls.py, tools/audit/seat/shims/seat-gh, tools/ci/codescan_wait.py and tools/pr/app_push.sh.
- dev/governance/roles/ has no diff between the merge base and origin/main, so the contract is current.
- PR body head SHA = 7cbfa680134ea1ddb34d202ef1ab11e0efb93807, the head measured (step 7). The Head section's trailing bare SHA b660583bb17f721662bec4c89807c16b1614e15e is unexplained.
- Finder's harness: none committed (the packet says "none named"). The figures are the fixer's own self-test arms. The body's carry-3 instance count ("two instances") was not re-derived by the fixer, and not by this seat.
- Forward-carry: both body items are `dismissed:` with reasons, and carry_audit at the head reads 2 routed, 0 unrouted.
- CI: `merge_train.py classify 7cbfa680134ea1ddb34d202ef1ab11e0efb93807 --pr 3427` printed `GREEN 7cbfa680134ea1ddb34d202ef1ab11e0efb93807 pending: none red: none` at 02:43:01 UTC (ev/classify.log). The review packet's `gate failure` (and its red-unanswered refusal) was an earlier read; classify had `gate` pending throughout until green. No required red is owed a `## Red checks` answer.
