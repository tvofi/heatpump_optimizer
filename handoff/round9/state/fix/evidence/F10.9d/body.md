_Requested by **tvofi**_

Before: `merge_fastpath.py` refused any file no closure records whenever a `run_always` script exists, because `tests/closure.py` drops INERT reads from every record. A `docs/delivery` row, which every merge adds, therefore refused the fast path as "unrecorded", the same as a doc `harness_headers.py` really opens.

After: the recorder files the INERT files a recording opened under `inert_reads` in `tests/closures.json` (INERT stays out of every closure; that classification is untouched), `check` refuses a table that misses one, and `decide()` refuses `unrecorded` only for a non-INERT file, a file listed there for a `run_always` script, or a sibling in a directory it lists a file from. A table without `inert_reads` keeps the old answer. Main's push stays FULL. Closes #1812's F10.9d item (part of #1812).

## Head

3e109874b50265fe038caf52919ce682bd95deac (branch handoff/r9-f10-closure-runalways; code commit dfb57a51, merged with origin/main 3bd6f12207a1a48c94ff6f302e533207f6c5fba0 at 2026-10-02T00:40Z).

## Mutation proof

- Predicate mutant (`inert_read_dirs` returns None, i.e. the old predicate): `python3 tools/audit/merge_fastpath.py --self-test` goes red on exactly the two new eligibility checks ("a docs/delivery row main adds ... is eligible once the table records the INERT reads" and "... the pull request's own delivery row beside a code change main made"); with the fix 33 checks, 0 failed.
- Recorder mutant (`is_inert(r) == inert` replaced by `not is_inert(r)` in `strace_files`): `tests/entities.py` ends `1 of 2035 ENTITY CHECKS FAILED`, the one new check ("the recorder files a traced Python child's INERT reads apart from the closure"); evidence/F10.9d/mut_entities.log.
- Table mutant (`docs/backlog.md` removed from `inert_reads` for harness_headers.py): `closure.py check` prints `INERT READS UNDER-APPROXIMATED` and exits 1; unmutated, it prints "committed closures cover every file this run touched".
- Survivors: `mutation_table.py --scope changed` not run locally (stress-bound and pinning is mutation-autofix's, ci-autofix.md); left to CI.

## Null control

The new pair is red-first above. Null controls kept: `docs/backlog.md` (opened by harness_headers.py) and `DISCLAIMER.md` still refuse as `unrecorded`; a new `docs/new.md` beside the docs it opens refuses; `custom_components/x/new.py` (not INERT) refuses; a head table without `inert_reads` keeps the old refusal. Baseline predicate on the same 120 pairs: `INJECT=0` below.

## Figures

- Opened INERT files, recorded: `python3 tests/closure.py record tests/harness_headers.py --out-dir D` then `python3 tests/closure.py merge --in-dir D --partial` gives `inert_reads["tests/harness_headers.py"] = DISCLAIMER.md, LICENSE, docs/audit-2026-08.md, docs/audit-2026-09.md, docs/backlog.md` (matches the five R9 F10.3 measured in `strace_files`'s docstring). layout.py and env_drift.py recorded none (`python3 tests/closure.py record tests/layout.py`, `./tests/derive_closures.sh --single tests/env_drift.py`). `tests/closure.py selftest` is not a recorded script (it has no closure entry), so what it opens is unmeasured, as before.
- ELIGIBLE re-measure, rule: pair k is head = M^2, main = M^1 for each of main's last 120 first-parent merges M, counted when `main_files` is non-empty and `decide()` returns nothing; `N=120 INJECT=0|1 python3 evidence/F10.9d/measure30.py` (INJECT=1 overlays this branch's `inert_reads` on both tables since history has none; INJECT=0 is the baseline predicate). At origin/main 3bd6f122: ELIGIBLE 0 of 120 in both (m120_0.txt, m120_1.txt). Null control: 70 of the 120 pairs have main unmoved and would also print rc 0, hence the moved>0 rule.
- Why zero: of the 50 moved pairs, `unrecorded` falls from 50 (INJECT=0) to 30 (INJECT=1) and no `docs/delivery` file remains among its causes (`python3 evidence/F10.9d/unrec.py`: tests/closures.json 17, CLAUDE.md 7, docs/plan-2026-09-open-issues.md 6, tests/closure.py 4, docs/audit-2026-09.md 1, tests/derive_closures.sh 1). Every moved pair also carries `full` (43), `claim` (29), `grader` (27), `workflow` (17) or `overlap` (7), and none had `unrecorded` as its sole reason, so the count does not move. This is a finding, carried below, not a claim that the fast path now fires.
- Gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` printed `MODE: FULL -- every test script runs ... tests/closure.py changes the gate itself`; at 66eccae3 every script passed except tests/stress.py (see Red checks). origin/main then moved once more (#1834) and was merged; at 3e109874 re-run: `python3 tools/audit/merge_fastpath.py --self-test` 33 checks 0 failed, `python3 tests/structure.py` STRUCTURE RATCHET PASSED, `python3 tests/closure.py selftest` ALL 28 closure shrink pins PASSED, `python3.12 tests/entities.py` ALL 2054 ENTITY CHECKS PASSED (python3.11 cannot even parse tests/entities.py on main: a 3.12-only f-string at line 3850). The full gate was not re-run after the second merge; CI grades the head.
- Instrument, seams: the class's seams are the writers of `inert_reads` (`_exec_record`, `_union_strace`, `_fold_inert_reads` in full and `--partial` merge) and its readers (`check`, `inert_read_dirs`); all five are covered by the checks above. No coordinator method added, so `tests/seam_map.json` is unchanged.

## Red checks

`tests/stress.py` fails one of 95 checks in this sandbox, "production calls were captured on this tree and the baseline": `AttributeError: module 'sys' has no attribute 'monitoring'`, because the sandbox runs Python 3.11 and `sys.monitoring` is 3.12+ (`GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) python3 tests/stress.py`, evidence/F10.9d/stress_head.log). The diff touches no solver code. Left to CI's 3.12+ runner. No other check went red on a commit in the branch.

## Forward-carry

/mnt/project-files/audit-r9/fix/carry-F10.9d.md (the fast path still has 0 ELIGIBLE pairs in the last 120 merges; `full`, `claim`, `grader`, `workflow` dominate), for the orchestrator to place in the next merge_fastpath owner's brief.

## Friction

none
