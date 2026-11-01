plan: the closure stamp is the round's major, vN.0.0 (R10-FLY-CLOSURE-MAJOR)

Fly-in split from the R10-FLOW-TOOLKIT-MODEL carry "Round closure is v10.0.0".
`tools/plan/replan.py` modelled the programme-closing stamp as a minor bump
(`bump(version, patch, minor=True)`, kind `minor`), so `plan.json` and the plan
page printed v7.2.0 where decision 0016 (tvofi, 2026-10-29, restated 2026-10-31)
owes round 10's major, v10.0.0 -- the version `tools/release/stamp.py
--round-close 10` assigns. Landing this discharges that carry item; its roster
disposition is the roster seat's op.

Carry 1: closed in this diff -- the round-close stamp is vN.0.0, N the roster's round, as
`stamp.py --round-close N` assigns it; `check_plan` validates it and `plan_page` renders it.

The fix gives the version rule one owner. `replan.closure_version` calls
`stamp.next_version(version, None, N, N)`, the function `--round-close N` runs,
so the plan states exactly what the stamp will assign and refuses where the
stamp would (a round not above the current major). N is
`roster_lib.roster_round` of the roster's path, the reader `stamp.py`'s
`roster_round_at` uses; `main` derives it at the edge and `build_plan` takes it
as the required keyword `round_n`, so the model stays pure and no caller can
omit it. A roster naming no round refuses (exit 2), never defaults -- the same
stance `next_version` takes on an unreadable roster. The plan records
`generated.round`; the closure stamp's kind is `round-close` (`ROUND_CLOSE`);
`check_plan` refuses a closure stamp that is not the single last stamp, a
version that disagrees with `closure_version(generated.version,
generated.round)`, a plan recording no round, and any stamp kind other than
`patch` and `round-close`. Interim stamps stay patch bumps (`bump` lost only its
minor arm). `plan_page.py` renders the row unchanged in shape; its caption and
cadence note now name the round-close major, and its self-test pins the
rendered `v9.0.0` / `round-close` row.

Alternatives: hard-coding the major from the roster round inside replan (a
second copy of decision 0016's rule, which `stamp.py` already owns and refuses
on), and reading the round from `VERSION` (wrong source -- the major is the round
being closed, not the current one). Both lost to delegating to `next_version`.

## Head

`8d176a6f714c84ffb6f5e29e8d0b6c4a73a3c1aa`, measured against merge base
`8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f` (origin/main at 2026-11-01T04:25Z
is `61b0076f`, merge-tree clean). The round-1 review head was `815039200`
(the delivery row plus a merge of main over `6b38d24`); this head adds one
commit to `tools/plan/replan.py`'s self-test only. The plan files
(`tools/plan`, `plan_page.py`, `state_docs.py`, `stamp.py`, `roster_lib.py`)
are byte-identical at the two bases, so the before/after replan figures below,
taken against `2b6bef745`, describe this base too.

## Mutation proof

Each mutant is a copy of `tools/plan/replan.py` with one production line
replaced, run with `--self-test` (`REPLAN_MUTATION_CHILD=1`); every one also
sits in the self-test's own mutation table, which reports each `rc=1`.

Round 1 review (blocked at `815039200`, mutation-vacuous): the three survivors
it named, each now killed by a row planting exactly that input:
- P3 `round-close-last`: ` or plan["stamps"][-1] is not closes[0]:` -> `:`:
  rc=1; FAIL --check refuses a round-close stamp that is not the last stamp
  (planted: a correct round-close stamp followed by another stamp).
- P4 `round-close-stray-kind`: `("patch", ROUND_CLOSE)` -> `("patch", "minor",
  ROUND_CLOSE)`: rc=1; FAIL --check refuses a minor stamp beside a correct round
  close (planted: an extra `minor` stamp before a correct closure; the row also
  requires no `round close` refusal, so only the stray-kind arm can answer it).
- P5 `round-n-required`: `*, round_n: int)` -> `*, round_n: int = 10)`: rc=1;
  FAIL build_plan without round_n refuses (a call omitting `round_n` must raise
  TypeError naming it).

Null control for these rows: the same three mutants applied to
`815039200:tools/plan/replan.py` each print `self-test: 0 failed`, rc=0 -- the
reviewer's result, reproduced; at this head each is rc=1.

Unchanged from round 1, still killed:
- `round-close-version` (`"version": closing` -> `bump(version, patch)`): FAIL
  the clean plan passes --check; FAIL the closure stamp is the round-close major
  of the plan's round; FAIL the closure major follows the round, not a constant;
  and three --check passes rows.
- `round-close-check` (`elif closes[0]["version"] != want:` -> `elif False:`):
  FAIL --check refuses a round-close closure stamp v1.1.0 / v3.0.0 in round 2.
- `round-from-roster` (`round_n = roster_lib.roster_round(src)` -> `99`): FAIL a
  roster naming no round refuses, never defaults (exit 2).

Failing test first (round 1): at the baseline production code with the new arms
added, the self-test printed FAIL the closure stamp is the round-close major of
the plan's round (`kind 'minor'`, `v1.1.0`) and FAIL a roster naming no round
refuses, never defaults (exit 2).

## Null control

The unmutated copy's self-test exits 0 (the table's own null control, printed
`null control: unmutated copy rc=0`). A real replan at the merge base and at
the head, both pinned to roster commit
`e71a089ea915a04960643dac50519aefdf3befa3` and `--start 2026-10-31T12:00:00Z`,
differ only in the closure stamp: with `stamps[-1]`, `summary.closure_stamp`,
`generated.round` deleted and the closure version normalised in `groups[].stamp`
and `waves[].stamp`, `diff` of the two `jq -S` renderings exits 0 (had any
group, wave, batch, patch stamp, CI price or closure time moved, it would print
the line). Both interim patch stamps are byte-identical (v7.1.1, v7.1.2).

Before (merge base): `v7.1.1 patch 5 | v7.1.2 patch 5 | v7.2.0 minor 4`.
After (head): `v7.1.1 patch 5 | v7.1.2 patch 5 | v10.0.0 round-close 4`;
`summary.closure_stamp` `v10.0.0`, `generated.round` 10, `--check` prints
PLAN OK. The plan page rendered from each plan (offline empty snapshot) shows
the row `v7.2.0 ... minor` before and `v10.0.0 ... round-close` after.

## Figures

- self-test: `python3 -I tools/plan/replan.py --self-test` -> `self-test: 0 failed`, every row of the mutation table `rc=1`.
- plan page: `python3 -I tools/audit/seat/plan_page.py --self-test` -> 0 failed.
- state docs: `PYTHONPATH=tests/hastub python3 -I tools/audit/seat/state_docs.py --self-test` -> all checks passed.
- real replan: `python3 -I tools/plan/replan.py --roster-ref e71a089ea915a04960643dac50519aefdf3befa3 --start 2026-10-31T12:00:00Z --out plan.json` -> stamps as in `## Null control`.
- seam enumeration (rule: every tools/ or tests/ line modelling a closure as minor): `git grep -n -i -e 'minor=True' -e '"minor"' -e 'minor stamp' -e 'the minor at' -e 'closure_stamp' -- tools tests`, excluding `tools/release/stamp.py`. Base: 14 lines; head: 7. Dispositions at head: `tests/finite_boundary.py` (a store key, unrelated), `tools/audit/carry_audit.py` x2 (a word list, unrelated), `tools/audit/seat/r10_stamp_round_mutants.py` (stamp.py's legitimate interim minor bump), `replan.py` `closure_stamp` (now the round-close version), and two self-test lines (the planted refusal and its assertion). Closed in this diff: `bump(minor=True)`, kind `minor`, the `check_plan` minor arm, and the three plan-page texts.
- structure: `python3 tests/structure.py` -> STRUCTURE RATCHET PASSED.
- scope: `python3 tests/closure.py select --diff 8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f` -> `MODE: SCOPED -- 1 script(s) run` (`tests/entities.py`).
- CI predict: `python3 tools/pr/ci_predict.py` -> no closures, fast, governance or instrument red predicted.
- scoped script: `PYTHONPATH=tests/hastub python3 tests/entities.py` stops locally in `_hb_stdlib_reads` with `PermissionError: Cannot get task port` (macOS; the function's docstring names the capability this host lacks; `tests/entities.py` is unchanged by this diff). The one entities check that reads this diff, `tools/audit/seat/state_docs.py --self-test passes`, sits after that point; its command was run directly (above) and passes. CI runs entities on Linux.
- prepr: `bash tools/pr/prepr.sh body.md` -> `PRE-PR: 8d176a6f714c... rc=0`, `MODE: SCOPED`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff 8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f` -> `Architecture score: dS +0.0000 NULL`.

## Unpinned sites

n/a: no `custom_components/` site; the `tools/` sites are pinned by the in-tree mutant table in `replan.py`'s self-test (rows `round-close-version`, `round-close-check`, `round-from-roster`).

## Red checks

none

## Forward-carry

none

## Friction

none
