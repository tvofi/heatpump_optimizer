Re-cuts D5 finder seat `s7` in `dev/audit/config/scopes.json`, the repair for `governance / instrument-self-tests` red on #3869 and #3883. The ledger rule in that file says a seat that grows past `ledger.max_units` "is re-cut here, never sampled".

**Cause.** `s7` held `tests/f*` (three files). At `origin/main` fd93aa3e it holds 4487 of the 4500-unit cap. #3869 and #3883 each add `tests/features.py` comments: 4520 and 4508 units at their heads. `check_scopes.py` then refuses the live scopes (`FAIL D5 ... over ledger.max_units 4500: s7 holds 4520 units`), and two steps go red:
- the owner-only canary's arm `SCOPES null: the planned shape ... passes check_scopes`;
- `check_scopes.py --self-test --repo .`'s live-scopes arms: `null control: the live D5 and D6 pass the cap and the line`, `the default verdict passes the live scopes`, `the default invocation exits 0 on the live scopes`.

The #3902 shard merge is not the cause. `tests/ci/` was not involved, and main 46d0a521 already held #3902 and passed both steps (Null control). The two pull requests need this branch's merge into their heads once it lands. Their own diffs need no change.

Neither `tools/pr/prepr.sh` nor `tools/pr/ci_predict.py` runs `check_scopes.py --repo .`, so the root-cause seat's question for those reds starts there: the live check runs in seconds and names the seat. A comment that crosses a D5 cap first shows up in `instrument-self-tests`.

**Change.** `s7` keeps `tests/fe*` (`tests/features.py` alone, 4303 units at main). `s8` takes `tests/{fi,fr}*` (`tests/finite_boundary.py` 160 units and `tests/frontend.py` 24), going from 3813 to 3997. Every cell stays owned exactly once, which `check_scopes.py` enforces.

## Head

7df39f349ae1b81dce5d8166ef7417119bda474d, cut from `origin/main` fd93aa3e9b161e92ead26e04ba8311b3fc0fc7e5. Measured 2026-11-26 UTC.

## Mutation proof

The fix is one data edit, so the mutant is reverting it. Starting from this head merged into a PR head, `git checkout fd93aa3e -- dev/audit/config/scopes.json` restores `tests/f*` and `tests/{a,b,c,d,g}*`. Then `python3 -I tools/audit/check_scopes.py --repo .` prints:
- on 3dd6cc89db (#3869 merged): rc 1, `over ledger.max_units 4500: s7 holds 4520 units`; restored, rc 0 with `s7:1f/0loc/4336u`;
- on c97cacfaf7 (#3883 merged): rc 1, `over ledger.max_units 4500: s7 holds 4508 units`; restored, rc 0 with `s7:1f/0loc/4324u`.

## Null control

`python3 -I tools/audit/check_scopes.py --repo .` at each tree, with the D5 `s7` field of its `ok`/`FAIL D5` line:
- main 46d0a521 (the brief's base): rc 0, `s7:3f/0loc/4487u`; main fd93aa3e: rc 0, `s7:3f/0loc/4487u`.
- #3869 head f211d7aa: rc 1, `s7:3f/0loc/4520u`, `over ledger.max_units 4500: s7 holds 4520 units`.
- #3883 head 642753ad: rc 1, `s7:3f/0loc/4508u`, `over ledger.max_units 4500: s7 holds 4508 units`.

`python3 -I dev/audit/harnesses/owner_only_channel.py` at main 46d0a521: rc 0, `RESULT arms=48 failed=0`, `OWNER-ONLY CHANNEL HELD`. In CI at #3869's head (job 140137272250) the same harness printed `RESULT arms=48 failed=1` and `FAIL SCOPES null`, and `check_scopes.py --self-test --repo .` printed `SELF-TEST FAILED` with the three live-scopes arms above `False`.

## Figures

- `python3 -I tools/audit/check_scopes.py --repo .` at this head: rc 0, `ok D5 mode=cells seats=10 universe=945 [... s7:1f/0loc/4303u, s8:49f/0loc/3997u, s9:69f/0loc/3903u ...]`.
- The same command on this head merged into #3869's head (3dd6cc89db): rc 0. Merged into #3883's head (c97cacfaf7): rc 0. With both PRs and this head merged: rc 0, `s7:1f/0loc/4357u`.
- Per-file D5 units, `python3 -I tools/audit/text_ledger.py --dim D5 units <file> | wc -l` at main fd93aa3e: `tests/features.py` 4303, `tests/finite_boundary.py` 160, `tests/frontend.py` 24.
- `python3 -I dev/audit/harnesses/owner_only_channel.py` and `python3 -I tools/audit/check_scopes.py --self-test --repo .`, the two red steps' commands: at this head rc 0 / rc 0 (`OWNER-ONLY CHANNEL HELD`, `SELF-TEST passed (every perturbed scope refused)`); at 3dd6cc89db and c97cacfaf7 the same; at f211d7aa and 642753ad rc 1 / rc 1 (`OWNER-ONLY CHANNEL BROKEN: SCOPES null ...`, `SELF-TEST FAILED`).

## Red checks

none

## Unpinned sites

none: the diff adds no `.py` line. `tools/pr/prepr.sh` with `MUTANT_CMD="python3 -I tools/audit/check_scopes.py --self-test --repo ."`: `diff mutants [0s] no survivor among the diff's first 40 mutant(s) under: python3 -I tools/audit/check_scopes.py --self-test --repo .`

## Forward-carry

none

## Friction

none
