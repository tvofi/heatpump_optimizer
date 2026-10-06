Fix review: blocked 26002ff5b84d59966ce3921ae3199a513599b920 root-cause-unanswered: typing, mutation, mutation-autofix and env-matrix went red, unanswered in ## Red checks

Round 1. Measured 26002ff5b84d59966ce3921ae3199a513599b920, which is still the pull-request head. The authored commit a1fda86801998d0173ba9f5863ea2023829a9c2a is inside it; the delivery-row commit is too.

bus-nonce: 72f41406760a13949efbabc6f4c8ffcc

## Red checks

`## Red checks` names one features.py check and none of the four GitHub checks that are red on this head.

`typing` (job 112532951404) failed. The census is errors 1, `by_code` arg-type 1, `by_module` pump_arbiter.py 1, against a recorded 0. Local mypy 2.3.1 `--strict` places it at `pump_arbiter.py:466`: argument 1 to `_inside_silent` is `Any | None`, expected `str`. That argument is `config.get` of the silent spec. `dict[str, Any].get` without a default is `Any | None`, and `_silent_rows` does not narrow it. The same failure is on a1fda868. The body does not name `typing`.

`mutation` (job 112532951481) printed `MUTATION TABLE REFUSED` for 17 sites this diff adds (4712 unpinned against 4695 at 6001b09a557259f37319b400d219cf83e02c563f). The body's 17 matches that ADDED UNPINNED list; the table was not re-run here. The pin step in the same job measured nothing: 17 not started for `--budget-minutes`. `mutation-autofix` (job 112535205266) printed `AUTOFIX: skip-no-measurement` and `THE REPAIR DID NOT HAPPEN`. No pin commit is coming. The body says `--pin-killed` is the autofix's and does not name either check.

`env-matrix` (job 112532467495) failed because `policy_lint` cannot find `.claude/workflows/policy_lint.mjs`. That path moved on the merge base 6001b09a (`#1919`); this diff does not touch it. `pr-contract` job 112533135653 failed on that silence. The same failure is on a1fda868. `## Red checks` does not name `env-matrix`.

`nightly-status` is last night's `record-autofix` on main. `delivery-status` printed `UNCHECKED`, 0 overdue, pending `#2003` and `#2001`, and did not name `#2007`. `fast (3.14)` succeeded. A cancelled `budget-raise-gate` has a successful sibling run (job 112532472283).

The features check the body answers did fail on this machine, at the head and under the mutant, with the same two objectives (`shipped 110.4366`, `seeded 110.1297`). `optimizer.py` is not in the three-dot diff. CI `fast` did not fail.

## Mutation proof

`return None` as the first statement of `_silent_target`, before the entity check, in a separate worktree at this SHA. `PYTHONPATH=tests/hastub python3 tests/features.py`.

Head: 1 of 3788 failed, the R9-F2.1 P3 check above. The SW-2 checks printed ok, including the seven the body names.

Mutant: those seven failed, and so did `an on echo clears the miss, so the next off is rewritten once and not yet a warning`. 9 of 3788 failed. The proof is not vacuous. The review worktree was not edited.

## Other steps

Roster class is `feature`; the brief says there is no class. The issue's bullets are that feature's scope. Each SW-2 requirement in `handoff/round9/fix/SW.md` section 2.3 and the optimizer-off bullet in 2.4 is a check in `tests/features.py` or is the out-of-scope waiver (inverted switches). Weekday tokens in the `dhw_schedule` grammar (`mo`, `sa`, `weekdays`, `weekend`) and an overnight window select the silent step through `step_actions`. The not-enforced repair is the SW-1 row of that design, not this diff. No carry: nothing measured here changes what SW-3 or SW-4 must do beyond that design.

`python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No budget file in the diff. `VERSION`, the manifest version and the notes heading are untouched. `git merge-tree --write-tree origin/main HEAD` exited 0 with empty stderr. `env_drift.py --all origin/main`: `NO UNCLAIMED DRIFT`, `NO STALE FIXTURE`, exit 0. The two `killed_by` files are the same `RETURN_DEL` pins with `, silent` added to the `old` line that is now in `desired`. Card files are absent from the diff, so `card_drift.mjs` was not run.

The re-keyed pins and the unpinned 17 are the mutation ledger's movement. CI did not record kills for the 17, because the pin step did not start them.
