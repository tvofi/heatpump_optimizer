Fix review: merge c3e8d3de1edac76d4bbb2ab412b63b2919ab58a6

Round 2. Measured c3e8d3de1edac76d4bbb2ab412b63b2919ab58a6, which is the pull-request head. The previous verdict blocked 26002ff5b84d59966ce3921ae3199a513599b920.

bus-nonce: 64a24160a59fbe04037e4fe0a2cfc0c7

## What changed since that block

`git diff 26002ff5 HEAD -- custom_components/heatpump_optimizer/pump_arbiter.py tests/features.py` changes only `_silent_rows`: the return annotation is `TypeGuard[str]`, plus the import and two docstring lines. `tests/features.py` and `_silent_target` are unchanged. The head also adds 13 `killed_by` files and 4 `survivor_triage` files, re-keys the two existing `desired` `RETURN_DEL` pins, and merges origin/main `1fa713f73740e99a5762019f574ccd6afa45dca2`. The body's head line is this SHA.

## Typing

The body's mypy command, with `/Users/timmalmstrom/.venv-typing-r9f23/bin/python`, exits 0 and prints no error. CI `typing` (job 112581271222) succeeded. `_silent_rows` is False for `None`, `''`, `'   '`, and `3`, and True for `06:00-08:00`, so a true result is a `str`.

## Mutation

`python3 tests/mutation_table.py --scope changed --base 6001b09a557259f37319b400d219cf83e02c563f --max 0 --scripts tests/features.py` exits 0: 4695 unpinned of 5651, 4695 at 6001b09a, `MUTATION TABLE PASSED (empty pool)`. Removing the 17 new disposition files and re-running that command refuses at 4712, 17 added by this diff. Restoring them returns 4695 and exit 0. Each new pin's `old` text is a line in `pump_arbiter.py`. The `--pin-killed` drive was not re-run.

The four `equivalent` records match that count. `step_actions` returns None for `None`, `''`, `'   '`, and `3`, which is the False the `_silent_rows` guard returns. The four bool pairs agree under `is not` and `abs(a - b) > 0.3`. `_read_setpoint` returns None when the state is in `unknown`/`unavailable`/`none`/`""`, which is the fallthrough after the deleted `return None`. A non-switch slot id is None, and `_write` returns when the slot state is None.

The round-1 mutant, `return None` before the entity check in `_silent_target`, failed the seven named checks. That function and `tests/features.py` are unchanged, so that run still describes this head. CI `fast (3.14)` on this head succeeded.

## Red checks

The body names typing, mutation, mutation-autofix, env-matrix, and pr-contract. On this head `typing`, `env-matrix`, `pr-contract`, and `fast (3.14)` succeeded. `env-matrix` is green; the three-dot diff does not edit `tools/policy/policy_lint_envmatrix.mjs`. `nightly-status` is last night's `record-autofix`. `delivery-status` printed `UNCHECKED`, 0 overdue, pending `#1917`, `#2003`, and `#2001`. `mutation` and `closures` were still in progress at posting. The inventory those jobs refuse on is the 4695 result above.

## The rest

Roster class is `feature`; the brief says there is no class. The issue's bullets are that one feature's scope, traced in the round-1 review to the checks. Forward-carry in the body is none, and this delta does not change what SW-3 or SW-4 must do. `python3 tests/structure.py` passed. `git merge-tree --write-tree origin/main HEAD` exited 0 with empty stderr. `env_drift.py --all origin/main` printed `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE`, exit 0. `VERSION`, the manifest version, and the notes heading are untouched. Card files are not in the three-dot diff.
