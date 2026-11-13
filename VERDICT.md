Fix review: blocked a98d895577770cd84ad8baa3114d6fbfb895a455 conflict: the head does not merge with origin/main ad95665ea3162167a93b92879c618db5c3a18c93, tools/pr/ci_predict.py conflicts in three hunks with main's 68e1704e2b (pull request 3549), and gate is red at the head beside a red pr-contract

bus-nonce: 94d09ed654c5d527e29a2cc3a190e40e

Round 4 of this part, a delta review over the reviewed head 17afc3f532cbc00e84f8c22957cb9a12d362b160, from a detached worktree at a98d895577770cd84ad8baa3114d6fbfb895a455. From the fourth round `fixer.md` owes a re-cut. The delta holds no `custom_components/` line, so the scope was not widened.

## Block

`git merge-tree --write-tree origin/main a98d895577770cd84ad8baa3114d6fbfb895a455` with origin/main at ad95665ea3162167a93b92879c618db5c3a18c93 (`git ls-remote origin refs/heads/main` read the same sha, about 14:40 UTC, 2026-11-13): rc 1, `CONFLICT (content): Merge conflict in tools/pr/ci_predict.py`, and one driver line, `LEDGER-MERGE: resolved tests/closures.json`. No `MERGE-CLAIM:` line was printed, so neither claim file is involved; the conflict is off the claim files (fix-review.md step 13). `ev/delta.log`, `ev/step2.log`.

The head's merge base with main is 3038b9deaf915a4b3defedd52307f5c57e574a50, the v7.1.15 stamp. Main has since merged pull request 3549, whose commit 68e1704e2b gives `ci_tree_run`'s clone the round-roster refs through `fetch_round_rosters(run)` (tagged `# mut:roundrefs`) and pins it with `roundref_self_test(root)`. This branch's 365d2bb236 builds the same thing for part 2's carry 5 another way: `ROSTER_REF`, `round_roster_refs(root)`, an `update-ref` loop, and `roster_ref_self_test()`. The three conflict hunks are the helper's definition, its call inside `ci_tree_run`, and the self-test call (`ev/delta.log`, section `## conflict`). Two implementations of one concept now meet; which survives is the fixer's resolution, and the body's Carry 5 paragraph, its two `ci_predict.py` mutants under `## Mutation proof` and the `ci_predict.py` lines under `## Unpinned sites` each name this branch's symbols and are owed a re-take against whatever the resolution keeps.

Beside it, `python3 tools/audit/seat/merge_train.py classify a98d895577770cd84ad8baa3114d6fbfb895a455 --pr 3514` printed `RED a98d895577770cd84ad8baa3114d6fbfb895a455 pending: none red: gate`, rc 1, not rc 4: the red is not only the raise's owed approval. `pr-contract / pr-contract` (job 131933460599, started about 14:08 UTC) concluded failure at this head. The last 170 lines of its log hold no refusal: `FIGURES: 22 resolved, 11 not verified, 0 refused`, `figure_block verify: 0 block(s), 0 refused`, the preflight's `clean    no refusal`, `no version edit`, and `CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)`. The refusing step is earlier in the log and this seat did not read it (API quota); the cause of the pr-contract red is not established here. The pull request reads `mergeable_state: dirty`.

## Previous findings

The round-3 block (self-test-red) is answered in the code and in CI, on these measurements:

- `git diff 17afc3f532cbc00e84f8c22957cb9a12d362b160 ce3542125d4655ecc5f86e5214c77c26d5525d89` is one file, `.github/workflows/governance.yml`, 12 lines added and 12 removed: the `outside-contract` step and its four comment lines moved from after `survivor-list` to directly before `tick-loop`. The sorted lines of the file at both commits are identical (`diff` of the two sorted files prints nothing, rc 0), the body's figure. At the head the step is at line 1226 and `tick-loop` at line 1234.
- RESULT the two `run:` commands in the head's order, in a detached worktree at a98d895577770cd84ad8baa3114d6fbfb895a455 with origin/main at ad95665ea3162167a93b92879c618db5c3a18c93 (`ev/step_order.head.log`): HEAD reads the head; `outside self-test: 212 checks, 0 failed`, rc 0; HEAD still the head; `tick_loop self-test: 30 checks, 0 failed`, rc 0; HEAD then reads ad95665ea3162167a93b92879c618db5c3a18c93 and `tools/pr/outside.py` is absent. So the old order would still fail here and the new one passes: the order is what separates them, in this seat's run as in the body's.
- `governance / instrument-self-tests` concluded success at the head (check run 131908825662, the packet's digest), and classify printed no `INTRODUCED` line. This seat did not read that job's log, so that the `outside-contract` step was selected and ran there is the job's conclusion, not a line I read.
- The body's `## Red checks` names `governance / instrument-self-tests` at 17afc3f532cbc00e84f8c22957cb9a12d362b160 and answers the trigger: the cheaper detector (the job's steps run in workflow order in a detached clone whose origin/main is ahead on the loop's files), its standing cost (one run of the set per handoff), and why none is built (pull request 3520 removes the cause). Answered; the answer itself is not mine to grade (step 11).

## Delta

`git log --first-parent 17afc3f532cbc00e84f8c22957cb9a12d362b160..a98d895577770cd84ad8baa3114d6fbfb895a455` is two merges. 21b69d9a97d8b4b2072546d8adb4b67865f8c11d merges the handoff ce3542125d4655ecc5f86e5214c77c26d5525d89 into the reviewed head; its tree equals the handoff's (`git rev-parse` of both `^{tree}`: 261d1db301056411d8f205b3edc51255a1ee3d7b) and `git show --remerge-diff` prints no hunk. a98d895577770cd84ad8baa3114d6fbfb895a455 merges main 3038b9deaf915a4b3defedd52307f5c57e574a50; `git show --remerge-diff` prints no hunk and the one driver line `LEDGER-MERGE: resolved tests/closures.json` (two closures merged as sets). The only branch-own commit in the range is ce3542125d4655ecc5f86e5214c77c26d5525d89. `.github/workflows/governance.yml` and `tools/pr/outside.py` are the same blobs at the handoff and at the head.

## Evidence

- `python3 tools/audit/seat/merge_train.py owed-reds` lists `gate`, `pr-contract / pr-contract` and `budget-raise-gate / budget-raise-gate` among its 22 names (`ev/step2.log`).
- `budget-raise-gate / budget-raise-gate` concluded failure at the head (check run 131935014661): the raise's owed approval, which the body's `## Red checks` answers and which follows a merge verdict. It is not the block.
- `review_packet.py render` printed three refusals: `structure` (the merge conflict above), `red-unanswered` (`pr-contract / pr-contract` not named in `## Red checks`) and `required-red` (`gate`). The packet was written.
- The body's `## Head` names a98d895577770cd84ad8baa3114d6fbfb895a455 and `git ls-remote origin refs/pull/3514/head` read that sha at about 14:40 UTC. Its sentence that the head merges main 3038b9d automatically with no resolution matches the remerge-diff above.
- carry_audit over the body at the head, from the packet and from the pr-contract log: `5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)`. figure_lint: `22 resolved, 11 not verified, 0 refused`.
- `VERSION`: the pr-contract log prints `no version edit: origin/main...a98d895577770cd84ad8baa3114d6fbfb895a455 moves none of VERSION, the manifest version or a notes heading`.
- Not re-taken this round, because the block makes them moot and the delta touches none of their files: the eight self-tests other than `outside` and `tick_loop`, the mutants, `tests/entities.py`, `tests/structure.py`, the policy budgets and the architecture score. Round 3 measured them at 17afc3f532cbc00e84f8c22957cb9a12d362b160.
- The closing self-audit ran over this verdict with an empty body file, since this seat has no file copy of the live body; the body's own audit is the pr-contract line above.

## Findings

- The round-3 finding stands at this head and on current main's ref: `tick_loop.sh --self-test` at the head's copy left a detached worktree on origin/main (`ev/step_order.head.log`), so every `governance / instrument-self-tests` step after `tick-loop` measures main's tree on a pull request whose copy of the loop predates pull request 3520. The body carries it. Carry: R10-GATE-DEFER-BARRIER

## Friction

- This seat's stop hook printed `stop-selfcheck: this turn touched the policy corpus and policy_lint refuses it`, six `[citations]` errors in `tools/audit/README.md` lines 288 to 296, on a turn that had only fetched: `git status --short` was empty at ad95665ea3162167a93b92879c618db5c3a18c93 and the clone was still shallow then. Whether the six are main's or the shallow clone's artifact was not established. Carry: R11-INTAKE-R10-RESIDUE
- The probe ref `probe/rev-3514-94d09ed6` already held 0585707298d06573bc9f67bb33962dd92c7cb58a (committed 14:01 UTC, 2026-11-13) when this seat pushed: an earlier firing of the same dispatch, first line `Fix review: merge a98d895577770cd84ad8baa3114d6fbfb895a455` with `pending-ci: gate`. It was taken before `gate` concluded red and before main reached ad95665ea3162167a93b92879c618db5c3a18c93, so it does not see the conflict. This verdict is committed with that commit as its parent rather than parentless, so the ref moves forward and the earlier verdict stays readable at the parent; nothing was force-pushed. Carry: R11-INTAKE-R10-RESIDUE
