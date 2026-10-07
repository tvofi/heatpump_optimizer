Fix review: blocked ace05371ed47a6a9d378883c9fefbad08315c343 other: typing ruler 0 to 5 in coordinator.py; mutation measured none of 47 new sites; advisor screenshot still shows Open schedule

bus-nonce: 5871e48d6939cc3ebf5d4ec1ec793c35

Round 1. No earlier `Fix review:` comment on #2010. A repair is owed, not a re-cut.

Head measured: ace05371ed47a6a9d378883c9fefbad08315c343. The body's `## Head` names that SHA. `git ls-remote origin refs/heads/fix/r9-ux-actions` returned the same SHA at posting. Worktree: /Users/timmalmstrom/hpo-seats/r9-ux-5-review, detached. `git diff $(git merge-base origin/main HEAD)...origin/main -- tools/audit/briefs/` was empty.

`git merge-tree --write-tree origin/main ace05371ed47a6a9d378883c9fefbad08315c343` exited 0 and wrote no `MERGE-CLAIM` line.

VERSION, the manifest version and the notes heading are absent from `git diff --name-only 6001b09a557259f37319b400d219cf83e02c563f...HEAD`. `claims-for:` in both claim files is 6.7.16, equal to `VERSION`. The pr-contract job printed `no version edit`.

## What blocks

The typing job 112558412302 (run 37548451646) printed `FAIL errors did not grow [recorded 0, measured 5 (+5)]`, `by_code[arg-type]` 0 to 1, `by_code[no-any-return]` 0 to 3, `by_code[typeddict-item]` 0 to 1, all in `coordinator.py`. A single-file `mypy --strict` with the pinned 2.3.1 interpreter named the five: `coordinator.py:1795`, `:1799` and `:1802` `no-any-return` (`_fold_away` returns `state.as_dict()` while `state` is `Any`), and `:8027` `typeddict-item` plus `arg-type` (spreading that dict into the payload, and passing the payload where `dict[str, Any]` is annotated). `## Red checks` does not name `typing`.

The mutation job 112558411932 printed `MUTATION TABLE REFUSED -- 4741 unpinned site(s) against 4695 at the ratchet base 6001b09a557259f37319b400d219cf83e02c563f, 47 of them added by this diff`, then `MUTATION TABLE REFUSED -- nothing was measured: 0 mutant(s) timed out, 47 not started for --budget-minutes`. `mutation-autofix` job 112560320989 printed `skip-no-measurement -- THE REPAIR DID NOT HAPPEN.` `## Red checks` does not name `mutation`.

`docs/img/card/advisor-light.png` is not in the diff. The image shows the hot-water row's button as Open schedule. `docs/dashboard-card.md` now says that row has an Apply button. The card change replaces `open_schedule` with `apply_dhw`, labelled `advisor.act_apply`. The group brief's documentation rule requires the changed card pages' screenshots in the same PR. `card_drift` reports `advisor_page` identical, so that catalogue state does not render the button this figure shows.

`pr-contract` jobs 112558118698 and 112558576251 failed on one error: `check env-matrix is red and ## Red checks does not name it`. At that moment the red list the job built was `delivery-status,env-matrix,nightly-status` (`typing` completed after, at 23:49:41Z). `env-matrix` is also red on origin/main at 6001b09a (governance run 37531301054). The body's only red-check paragraph names the local R9-F2.1 P3 solve, which is not a check name on this head.

`delivery-status` printed `DELIVERY STATUS UNCHECKED — 42 rowed, 2 pending, 0 overdue` for #2003 and #2001 on main. `nightly-status` printed `NIGHTLY FAILED: record-autofix failed last night` for scheduled run 37440269774. The diff adds `docs/delivery/2010.md` and does not touch those jobs' other inputs. Those two reds are not this pull request's.

`fast (3.14)`, `closures`, `coverage` and CodeQL `Analyze (python)` were still `in_progress` when the checks were read. Not cited as green or red.

## Mutation proof the body names

In `idle_reason`, `return REASON_IDLE_FUSE` was replaced with `return REASON_IDLE`. The features check's inputs (idle step, cap 0, price 0.2, room at the floor) then returned `idle`.

RESULT mutant fuse-check got=idle want=idle_fuse bare_idle=True

Restored. The same call returned `idle_fuse`.

RESULT restored fuse-check got=idle_fuse want=idle_fuse

`REASON_IDLE_FUSE` is absent at the merge base 6001b09a557259f37319b400d219cf83e02c563f. The proof is not vacuous. It is one return. The CI table did not measure the other 46.

## Null controls re-run

RESULT null at-floor step1=idle want=idle pass=True

RESULT null no-signal=idle want=idle pass=True

The body's other nulls (no setback; comfort event with no forecast; a hot-water row already at the recommendation) are the checks in `tests/features.py` and `tests/card.mjs` under those sentences. `tests/features.py` was not re-run here; `fast (3.14)` had not finished.

## Claims and the ratchet

`PYTHONPATH=tests/hastub python3 tests/env_drift.py --all origin/main` exited 0. `NO UNCLAIMED DRIFT: 56 scenario(s)`. `NO STALE FIXTURE`. 31 CLAIMED scenarios, and every leaf under them is `space_reasons` or `dhw_reasons` (0 other leaves). Six of those scenarios move only to `idle_coasting`, including `away_setback`. `node tests/card_drift.mjs origin/main`, after `tests/plan_view.py` wrote `/private/tmp/plandata-7eea360d005e.json`, exited 0: `2 state(s) moved and claimed, 38 identical` (`tooltip_hover`, `shared_steps_hover`).

`python3 tests/structure.py` exited 0. `STRUCTURE RATCHET PASSED`. `seam_cut_total` 766 <= 766. No `*_budgets.json` is in the diff. `tests/arch_score_head.py` was not re-run; the mutation log lists it `LAZY AND NEVER RUN`.

## Class

#1795 is the lane issue. The group brief is a feature, and it says there is no class. No enumeration rule is named because there is no defect class to open. The design's behaviours are what was checked. Forward-carry in the body is `none`; nothing measured here changes a later group's method beyond that brief.
