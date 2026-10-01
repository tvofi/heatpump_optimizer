R9-F10.9c, the follow-up from #1822's review that roster `ae194b6e` gives this group. **Merge after #1822**: this branch is cut from its code head `af2ac763`, and it changes the coverage cache #1822 adds.

Before: a pull request's `coverage` job restores per-script coverage by exact key. A restore searches the pull request's own cache scope before `main`'s, so an earlier head of the same pull request whose `tests.yml` saved under that key would be read as the data `main`'s push run measured. The key also did not name the runner's OS.

After: the push run's staging step writes `coverage-base/.measured-by` as `<event> <ref> <commit>`. A new `covtrust` step after the restore keeps the entry only when that marker reads `push refs/heads/main <key's base>`. Otherwise it deletes the entry and every script is measured, as on a miss. The reuse branch of `Measure the tree` reads `steps.covtrust.outputs.trusted` instead of `cache-hit`, and the key gains `${{ runner.os }}`. The marker file is not a `.coverage.<name>` or `<name>.nodata`, so `closure.py coverage-split` and `coverage_tree.sh` never read it.

**No barrier lost.** A discarded entry measures every script, which is #1822's miss path. A head that forges the marker as well is not caught here; the push to `main` still measures every script unscoped, the backstop #1822's own barrier argument rests on.

_Requested by **tvofi**_

## Head

`c010925be70e8bf02533b752410d5697cb0d65c1` (code: the merge of `origin/main` at `d536fb4d`, #1823, into the verdicted head `7a113ee6f5cde689dd8ae919747022366c674d3c`), on #1822's code head `af2ac76378deb834773e8c01ad32a16bb3fe5497`. The delta from the verdict at `e67bc382` is that merge: `tests/entities.py` conflicted with #1823's checks and keeps both, the coverage-cache check after #1823's concurrency checks.

## Mutation proof

`tests/entities.py`, check `the coverage job reuses only an entry main's push run saved, keyed on the runner's OS`. It executes the staging and `covtrust` steps' own `run:` over four restores:
- `covtrust` accepting any marker → `FAIL ... wrong: {"a pull request's save": (True, True), "main's marker at another commit": (True, True)}`, `1 of 2030`.
- staging writing no marker → `FAIL ... wrong: {"the push run's own marker": (False, False)}`.
- `Measure the tree` reading `cache-hit` again → `FAIL`, `1 of 2030`.
- `runner.os` dropped from the key → `FAIL`, `1 of 2030`.

## Null control

On this head the same check passes over all four restores: the push run's own marker is trusted and kept, while a pull request's save, a missing marker and main's marker at another commit are each discarded. `ALL 2030 ENTITY CHECKS PASSED`; `tests/structure.py` passes.

## Figures

none

## Red checks

Two checks were red on earlier commits of this branch, and neither is on its current code.

`fast (3.14)` was red once, on `c1ee65df` (the merge of `main` at `411368b6` into this branch): "1 TEST SCRIPT(S) FAILED" in run 36904819953. The next commit, `3e74c871`, differs from it only by `docs/delivery/1824.md`, and the same suite passed there (run 36905055277). It also passed on `e67bc382` and `29c3eef7`. The failing script's own lines are outside what this seat can read: the log API returns only the tail, and the full-log download host is refused by the seat's proxy. So the failure does not reproduce on the identical code. No cheaper detector exists for a failure that passes on the next run of the same code.

`delivery-status` was red on `e67bc382` because `main` then had overdue rows for #1802 to #1810. That check is not required and grades `main`'s record, not this diff. #1828 wrote those rows, and the check is green on `29c3eef7`. The cheaper detector already exists: `stamp.py` refuses to run with a missing row.

CI has not run on this head. Unrun here: the full gate (`MODE: FULL`, `tests.yml` changes), typing and real-HA `ha_contract` (no Python 3.14.2 in the cloud seat), and a real cache round trip, which needs a push to `main` first.

## Forward-carry

none

## Friction

none
