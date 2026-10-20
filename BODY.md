Move the last tracked residue of the round-9 hand-off tree
(`handoff/round9/fix/resume/FR-8.md`, `handoff/round9/plan-table-live.md`) to
`dev/archive/handoff/round9/`, where the other round-9 hand-off trees live, and
record the move in `tests/layout.json` as
`handoff/round9/` -> `dev/archive/handoff/round9/`. The two files move whole:
`git diff -M` shows two 100%-similar renames and no edit.

Landing the move empties `handoff/`, whose spelling is also the fixer hand-off
branch namespace of decision 0011 (`handoff/<topic>`). The layout instruments
manufacture an emptied parent as a moved path, so the move alone would sweep
every branch name the seat tools spell (322 citations in 53 files) and refuse
the pull request. `tests/layout.json` gains `ref_namespaces` so
`layout.landed()` does not manufacture a parent that names refs; the moved tree
itself, and any explicit `retired` entry under the prefix, stay swept.
`tools/audit/seat/moved_paths.py` reads the same `landed()` and passes the key
through.

Every live citation of the old path is re-pointed: the design-of-record
comments in `heatpump-optimizer-card.js`, the probe provenance in
`tests/features.py`, `roster_lib.py`'s algorithm provenance and
`handover_prompt.py`'s self-test fixture. A citation whose file only ever lived
on the archived round-9 branches is re-pointed to its tag, named without the
old tracked path. Two record files cannot be re-pointed without falsifying what
they recount: `dev/audit/config/bugclasses.json` (a `ref@sha:path` evidence
ledger) and `dev/programme/plan-2026-09-open-issues.md` (a quoted gate error).
Both join `historical`, keyed on the exact file rather than a directory, because
their text records where a path was when it was written.

## Head

5fd7fbdfb87051270d66fec0ef2ed860ce12f6a9

## Mutation proof

The fix is one clause in `tests/layout.py`'s `landed()`:
`and not any(d.startswith(ns) for ns in ref_namespaces)`. Deleting it reddens
both self-tests, each importing the production symbol:

```
$ python3 tests/layout.py --self-test
FAIL guard self-test: a ref namespace's name is not a citation of its emptied parent: {'new-reference': 1, 'unswept': 1, 'placement': 0}
layout self-test: 1 case(s) FAILED

$ python3 -I tools/audit/seat/moved_paths.py --self-test
FAIL its parent, a ref namespace, is not a moved directory
moved_paths self-test: 11 checks, 1 failed
```

Restored: `layout self-test: ok` and `11 checks, 0 failed`.

## Null control

The guard is clean at the pre-move tree, so its clean run at the head is not a
check that was already red:

```
$ python3 -I tests/layout.py --guard --base origin/main   # at origin/main, nothing staged
layout: GUARD: 0 refusal(s) against 3b1c3d56bb70
```

Undo the sweep (restore the four live files to the base while the move and map
stay staged) and the same guard refuses the move; restore the sweep and it is
clean again:

```
unswept: custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js:1540 cites handoff/round9/, which this diff moves
unswept: tests/features.py:59372 cites handoff/round9/, which this diff moves
unswept: tools/audit/seat/handover_prompt.py:182 cites handoff/round9/, which this diff moves
unswept: tools/audit/seat/roster_lib.py:9 cites handoff/round9/, which this diff moves
... 7 refusal(s) against a2b25bbc5518
```

The `ref_namespaces` clause itself is measured at both ends by the guard
self-test: a branch name under the namespace is not a citation (0 findings);
the moved tree under it is still swept (`{'new-reference': 1, 'unswept': 1}`).

## Figures

- Move is content-preserving: `git diff --cached -M --summary` prints
  `rename {handoff => dev/archive/handoff}/round9/fix/resume/FR-8.md (100%)` and
  the `plan-table-live.md` twin; `--numstat` is `0 0` for both, and each moved
  file's sha256 equals the base blob's.
- Build the counterfactual: with the move and map staged and `ref_namespaces`
  not yet declared, `python3 -I tests/layout.py --guard --base origin/main`
  prints `361 refusal(s)`: 322 for `handoff/` across 53 files (the branch names
  the rule spares) and 39 for `handoff/round9/` (the sweep this PR performs).
- Guard, head: `python3 -I tests/layout.py --guard --base origin/main` prints
  `layout: GUARD: 0 refusal(s) against a2b25bbc5518`.
- `moved_paths.py` over the lines this diff adds prints 2 hits, both the map's
  own entry (`"old": "handoff/round9/"` and its `new`); no added line in a live
  file is a `STALE?` hit.
- `git grep -l handoff/round9` names 26 files: `tests/layout.json`, the
  `dev/archive/**` copies, and the files the manifest now lists as `historical`
  (`dev/audit/rounds/**`, `dev/audit/config/bugclasses.json`,
  `dev/programme/{delivery,plan-2026-09-open-issues.md,rosters,round9}`), plus
  the `dev/audit/rca/` record directory. No live tool, test or product file
  names it.
- Scoped gate: `python3 tests/closure.py select --diff <merge base>` prints
  `MODE: SCOPED -- 10 script(s) run, 23 scoped out`. Nine are green; the one
  machine-measuring script, `tests/harness_headers.py`, is green alone under
  the gate lease (below), and `tests/structure.py` prints
  `STRUCTURE RATCHET PASSED`.
- `harness_headers.py` under `gate_lock.py take --label r10-handoff-archive`:
  `ALL 109 HARNESS HEADER CHECKS PASSED` (12:45:30-12:50:41 UTC, rc 0).
- `h7_memory_gate.py`'s boolean, paired under the same lease at the head and at
  `origin/main` a2b25bbc: `inject2x_attrib_rule_fires=True` at both, and
  `clean_attrib_rule_fires=False` at both.

## Red checks

`harness_headers` went red locally on an unleased run of the head: 12 findings
were one long simulator killed at its 900 s wall cap (`sysid_estimator_frontier.py`,
`rc=124`), and one was `h7_memory_gate.py`'s `inject2x_attrib_rule_fires` reading
`False` against a `True` header. Neither file is in this diff. The cheaper
detector is `tests/gate_lock.py`'s exclusive lease, which `gate-scoping.md`
already prescribes for the two machine-measuring scripts, at no recurring cost
beyond the wait it exists to serialise: under it `harness_headers` passes all
109 checks and the `h7` boolean reads `True` at both the head and `origin/main`,
so the earlier reds were load, not a regression.

## Forward-carry

none

## Friction

brief-citations: stale: the roster brief cites `tools/audit/moved_paths.py`; the tool is `tools/audit/seat/moved_paths.py`. Carry: dismissed: this PR's evidence names the real path, and no other citation in the tree has the stale spelling.

## Architecture score

n/a: no metric rises; `python3 tests/structure.py` passes at every budget.
