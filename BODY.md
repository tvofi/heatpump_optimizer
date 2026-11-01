R10-MUTANT-RUN-DRIVER (size S, issue #3122; owner tvofi approved card 4 on 2026-11-01): the tracked mutant driver every seat-local `mut.py` was re-implementing, plus the `--diff` arm that mutates a diff's added lines. Fixer seat, topic r10-mutant-run-driver.

## Head

Pull-request head `1a6a7e6a8bf1cbe04f37989aaedbab66165df624` (the code head plus a merge of origin/main and the delivery row; no code differs from the authored head). Code head `7af8c887a2439357432ce6fb14efc27429773f16`, a merge of origin/main `56630e7e6d229d960cf1b4db304d488ee20873e6` into the branch; origin/main had moved since the last full `tools/pr/prepr.sh` run and the run was repeated after the merge (see Figures).

## Mutation proof

Instrument: `python3 -I tools/audit/seat/mutant_run.py --self-test` (40 checks). Each production line below was broken in a scratch copy, the self-test run, and the line restored:

- drop GUARD_OFF, RETURN_DEL, CMP_BOUND, CALL_DEL or CONST_SWAP (the `yield` replaced by `pass`, one at a time): `diff: the added lines yield all five operators` and `diff: a self-test that does not pin them leaves survivors` go red, 2 failed each.
- skip the restore (`target.write_bytes(orig)` to `pass`): `spec: the file is restored between mutants` red.
- NULL reported as KILLED instead of SURVIVED: 3 spec checks red. `old` count check `n != 1` loosened to `n < 1`: `an old text occurring twice is refused` red.
- `start_new_session=True` to False, `_child.append(p)` deleted, or the handler's kill loop emptied: `SIGTERM mid-mutant ... the running command was killed with the driver` red in both modes.
- the timeout `_killpg(p)` deleted: `a mutant that hangs past --timeout is KILLED ... rather than waited out` red; the `--in-place` guard on a non-HEAD diff end set to `if False`: `--in-place with a diff end that is not HEAD` red.

Failing test first: before the arm existed the fixture check was red by absence (`mutant_run.py` not in the tree); the fixture adds `norm` (a guarded return, a bound, a call, a constant) and the self-test pins every operator's line with `check_norm.py` (no survivor) and none with `check_loose.py` (survivors for all five operators).

## Null control

- NULL mutant: `spec: the NULL mutant reports SURVIVED and a pinned mutant KILLED`; a command failing on the unedited tree prints `KILLED NULL`, rc 3, and no mutant runs.
- Empty diff (`HEAD...HEAD`): prints nothing, rc 0. `--report-only` over survivors: rc 0.
- A mutant whose `old` occurs twice is refused, rc 2, nothing run. Malformed spec, repeated name, NULL name, absent file, old==new, a dirty target (copy and `--in-place`): each rc 2.
- SIGTERM mid-mutant, both modes: rc 143, `git status --porcelain` empty for the target, byte-identical, no temp copy left under TMPDIR, and the running command's pid gone.
- Comment/import/def lines and lines inside multi-line strings yield no mutant; `"a < b"  # c > d` yields none; a log call yields no CALL_DEL.

## Carries answered

- Carry 1 (from R10-FLY-MUTANT-RESTORE): built here. `tools/audit/seat/mutant_run.py --spec mutants.json --cmd '<argv>' [--copy-tree|--in-place]`: automatic NULL, one `KILLED|SURVIVED name` per mutant, rc 2 on a dirty target or an `old` not occurring once, git-archive copy by default (`--copy-tree` names it), SIGTERM/SIGINT restore. The group's helper is already on main (#3060, `dev/audit/harnesses/mutant_guard.py`); `--in-place` reuses it rather than duplicating it. `features_block.py` gained `--through MARKER` and `--prelude 'import line'`, with 4 self-test checks plus 3 driving `_main`.
- Carry 2 (card 4): built here. `--diff <base>...HEAD` with the five operators, `--path`, `--max-mutants`, `--list`, `--report-only`; `tools/pr/prepr.sh` runs it report-only as step `diff mutants` when `MUTANT_CMD` is set (skips otherwise; cap `MUTANT_MAX`, default 40). Not built: replacing the seven seat-local block runners beyond `--through`/`--prelude`; the other seat-local drivers are not migrated (their seats own them).

## Figures

- `python3 -I tools/audit/seat/mutant_run.py --self-test`: 40 checks, 0 failed. `python3 -I tools/audit/seat/features_block.py --self-test`: 9 checks, 0 failed.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: 107 self-testing, 107 wired, 0 unwired (the new governance.yml step wires mutant_run). `python3 tests/structure.py`: PASSED. Scoped gate: MODE: SCOPED, tests/entities.py and tests/harness_headers.py both pass.
- Heavy pass on this fix's own added lines: `python3 -I tools/audit/seat/mutant_run.py --diff origin/main...HEAD --path tools/audit/seat/mutant_run.py --cmd 'python3 -I tools/audit/seat/mutant_run.py --self-test' --report-only`, at head 980c898f9 (the code differs from this head only by two added self-test checks): 81 survivors. A first pass found 93, and each real gap in it got a check (SIGTERM kills the child, timeout, spec and main refusals, string masking, in-place diff, cap).

## Survivor answers

The heavy pass is the instrument above; the driver's own mutation ledger does not apply (survivor_triage covers custom_components only, and the `mutation` lane mutates nothing under tools/).

- Self-test scaffolding, lines of `_self_test` and `_gone` (about 60 of 81): CALL_DEL on a `check(...)` call, CONST_SWAP on a poll count/sleep/timeout, `flag.unlink`, `shutil.rmtree` flag, `checks += 2`, `sys.path.insert` index, `return 2 if fails else 0`, and `GUARD_OFF` in the wait loops. Disposition: a self-test cannot observe its own deleted check; CI's grep requires a non-zero check count and 0 failed, and removing a check is a review matter. Not pinned.
- Equivalent: the `compile` skip and `text == src` skip in `diff_mutants` (a skipped invalid mutant would be killed, not survive: same output, slower); `if not files` and `if not mutants` early returns (the later path returns 0 too); `ln = 1` for `cur, ln = None, 0` (the hunk header sets it before use); `range(...)+2` and `>=` bounds in `string_lines` and the `n >= len(lines)` guard (one extra line, never an added line); `description=__doc__.split("\n")[1]`, a help string; `flush=False` on prints (same bytes).
- Defensive, not reachable from a fixture: the `git archive`/`tar` failure branch (`arc.wait() or tar.returncode` and its cleanup), `capture_output=False` on tar, `rmtree(..., ignore_errors=False)`, `_killpg` swallowing ProcessLookupError, a mask of `group(1)` length. Left unpinned; triage would be the same.
- Operator-table survivors on the arithmetic of the mutation itself (`+ 2` for the constant swap, `float * 2` for `1.0`): the swapped value only has to differ; the fixture checks that a constant mutant exists, not its value.
- features_block.py: 15 survivors in the diff arm at this fix's first head, all in `_self_test` scaffolding (`check` calls, `rmtree`, return codes), `_expect_error`'s `return False`, the `sys.exit(_main(...))` entry line, and `rindex("\n", 1, ...)` in `through` (equivalent: the header always precedes the marker). The parsing arms (`--prelude`, `--through`, usage rc 2) were survivors before `_main` took its path and the self-test drove it; those are now killed.

## Red checks

The check-run set was re-read in full (check-runs API, all pages, 55 runs) at head `1a6a7e6a8bf1cbe04f37989aaedbab66165df624`. Concluded red, by name: `governance / delivery-status`, and `pr-contract / pr-contract` (two runs) with the aggregate `gate` (two runs), which are red only because they refuse this body for leaving `governance / delivery-status` unnamed. Every other concluded check is success or skipped.

`governance / delivery-status`: the red is the OVERDUE row for #3096 ("triage: s9 batch 102", 12 commits since), not this pull request's row (#3151 is not in the log's list). The check grades main at its pinned SHA (`PINNED: 7f849a24911e9d52336bd79ea9ce63c67416a6ae`) and its log says it is not a required context and a red blocks no merge. This diff does not cause it: the only change to `.github/workflows/governance.yml` is one added step in the `instrument-self-tests` job (it runs `mutant_run.py --self-test`), and the `delivery-status` job and the tool it runs are untouched (`git diff $(git merge-base origin/main HEAD)...HEAD -- .github/workflows/governance.yml` shows one 7-line hunk at the self-test steps); the row set it reads does not change with this branch, and it would be red identically on main. Cheaper detector: none; the check already is the detector, runs in about 20 s, and its red clears when the #3096 batch is dispositioned. State (d), a precondition that changed underneath a sound process: the batch drain fell behind. Nothing to build here; recorded, no countermeasure.

`pr-contract / pr-contract` and `gate`: red only on `[pr-body] check governance / delivery-status is red and ## Red checks does not name it`; this section repairs that. Nothing else in the code is red.

## Forward-carry

none.

## Friction

none.
