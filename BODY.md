R11-HOTFIX-REPLAN-ROSTER-REF (hotfix, S; found_by owner, owned_by D11 — the roster seat records both on the group, which this seat may not write). `tools/plan/replan.py`'s `load_roster` named the round-10 roster branch when no `--roster-ref` was given, so the beat's plan-beat (no `--roster-ref`) built the round-11 plan from the round-10 branch's stale copy of `wave-r11-groups.json`. The default is now `roster_lib.reader_ref` (`default_roster_ref`'s answer, its note on stderr), as `owed_watch.py`, `round_metrics.py`, `bottleneck_check.py` and `cloud_dispatch.py` read it; the docstring and `--roster-ref` help say so.

Owner ruling 2026-11-22 (no round named in a default or docstring): every live default the class rule below returns is fixed here.

- `tools/plan/replan.py`: `load_roster` fallback, module docstring, `--roster-ref` help → `roster_lib.reader_ref`.
- `tools/audit/seat/roster_queue.py`: the module constant naming the round-10 roster path, the default of `readback`, `readback_text`, `roster_at` and the `unwired` command's read → `roster_rel(ref)`, i.e. `roster_lib.roster_path` at that ref (the newest `wave-r<N>-groups.json` there). A roster seat pushing to the round-11 branch had its append-carry read-back reading the round-10 file.
- `tools/audit/seat/closeout.py`: `--report-dir` default naming round 10's evidence directory → `report_dir_for(--roster-file)`, the roster file's own round; a roster file naming no round refuses, rc 2.
- `tools/audit/seat/plan_phases.py`: the usage line in the docstring → `round<N>`.

The barrier: `roster_lib.round_literal_defaults` (run by `roster_lib.py --self-test`, governance step `roster-library`) refuses a round literal (`audit-r<N>`, `wave-r<N>`, `round<N>`, any N) in a default shape anywhere in `tools/**/*.py` at a ref (the self-test reads HEAD from git's object store, as `tmp_paths.py --check` does, so no runner of the self-test records a read of an INERT tools/ file): argparse `default=`/`help=`, a parameter default, a parameter reassigned in the body, an `or`/`.get`/conditional fallback, a module-level UPPER constant, or a docstring line saying "default". Legal: a function whose name says self-test, a file under a `round<N>/` directory, and `ROUND_RECORDS` keyed on (file, constant) for four fixed records (round 10's carry cut-over commit, round 4's D6 register directory, round 4/6's D11 library search paths, `gh_comment.py`'s verbatim posted bodies). The key admits its own constant in its own file only: one self-test arm plants the same literal under another constant name in the record's file and is refused, another plants the record's own constant (`REGISTER_DIR`) under another file path and is refused.

Alternatives not taken: a plain text grep over `tools/` returns every self-test fixture and dated record (the census below), so it would need an allow-list keyed on line text, which a new default with the same literal passes; scoping by AST default shape needs no per-line list. Placing the check in `tmp_paths.py --check` (its own governance step) would give round naming a second owner; `roster_lib` owns which roster and which ref.

## Head

`1e81226fb9f9fa7dad1796e5268f8f6e8e095f6d` adds the self-test arm `a ROUND_RECORDS key admits its constant in its own file and no other` to `roster_lib.py`: `REGISTER_DIR`, a record of `tools/release/stamp.py`, planted with a round literal at `tools/x/other.py` must return one hit. This answers verdict/3880 (M7 survived). The previous head was 0b1994a331; this commit is the only code change since then.

## Mutation proof

- verdict/3880 M7 (the ROUND_RECORDS test `(rel, x) not in ROUND_RECORDS` loosened to `x not in {k for _, k in ROUND_RECORDS}`, which matches on the constant name in any file): unmutated, `roster_lib.py --self-test` prints `125 checks, 0 failed`. Under the mutant it prints `125 checks, 1 failed` with `FAIL a ROUND_RECORDS key admits its constant in its own file and no other (got: [])`.
- replan, in-tree: the self-test's mutation table gains `roster-ref-default` (the `reader_ref` line replaced by the round-10 literal, assembled at run time); `python3 -I tools/plan/replan.py --self-test` prints `mutation roster-ref-default: 'ref = roster_lib.reader_ref(repo, ref)' -> rc=1` and `ok self-test fails when roster-ref-default is deleted`. The same mutant run alone fails exactly `no --roster-ref reads round 12's roster branch` (PlanError: cannot list rosters at origin/handoff/audit-r10-roster) and `the CLI with no --roster-ref plans from round 12's branch` (rc=2); the round-10 null control passes under it, as it must.
- the barrier: that same replan mutant fails `roster_lib.py --self-test` on `no tools/ default in this checkout names a round` (got `tools/plan/replan.py:165: parameter fallback: audit-r10`, `... or fallback: audit-r10`).
- roster_queue: `rel = rel or roster_rel(ref, cwd)` in `roster_at` replaced by the round-10 path fails `a later round's roster is the one a ref carries: read, read back and shown` (69 checks, 1 failed).
- closeout: `--report-dir` default restored to the round-10 literal runs past the refusal into `json.load` of README.md, and the self-test crashes (rc 1); `report_dir_for` deleted fails `no --report-dir reports under the --roster-file's round`.
- prepr's diff mutants (40, in place) leave one survivor: `SURVIVED tools/audit/seat/closeout.py:472 STMT_DEL pass`, the deletion of `both --report-dir arms ran`, the check that refuses deleting either report-dir arm. A check's own deletion is unobservable from inside the self-test it belongs to; the two arms it guards are killed.
- Each default shape is a planted source `round_literal_hits` must refuse (one arm per shape, the conditional on both branches, a docstring opening on a blank line naming its own line).
- prepr's diff mutants (`MUTANT_CMD`: roster_lib's and closeout's self-tests) left four `roster_lib` survivors at 0bd09ea2f4 (`rel.split("/")[:-1]` to `[:-2]`, the function-level `top = False` to `True`, `get_docstring(clean=False)` to `True`, the conditional's body hit deleted); each now fails one arm (124 checks, 1 failed, per mutant).

## Null control

- ROUND_RECORDS file half: the record's constant in its own file (`tools/release/stamp.py`, `REGISTER_DIR`) still returns `[]` (arm `a ROUND_RECORDS key admits its own constant and no other`), so the new arm refuses only because the file differs.
- replan: a scratch repo whose rounds are 9 and 10 resolves to `origin/handoff/audit-r10-roster` through the same `load_roster` call (`no --roster-ref reads round 10's roster branch (null control ...)`). The CLI arm runs for the newest round only: a scratch round-10 roster meets `CARRY_CUTOVER`'s real commit, absent from a scratch repo.
- symptom: at the head, `--roster-ref origin/handoff/audit-r10-roster` given explicitly reproduces the base's group set exactly (116 groups, none of the three).
- lint: the base tree returns 5 hits (below); fixtures, a round read through a variable, a literal outside a default shape and a `round<N>/` directory each return none (four null arms).
- roster_queue: the commit before the newer roster reads its own round's file. closeout: a round-9 roster file gives round 9's directory.

## Figures

- `python3 -I tools/plan/replan.py --out P --start 2026-11-22T00:00:00Z` (no `--roster-ref`, this clone, origin/handoff/audit-r11-roster a45c0c450f, origin/handoff/audit-r10-roster 9719e7bfb0): base e3cb5c019b reads origin/handoff/audit-r10-roster, 116 groups, R11-OUTSIDE-3849 / R11-OWNER-FLOWCAP / R11-OWNER-COOLING-GUARD absent; head reads origin/handoff/audit-r11-roster, 126 groups, all three present. Null: head with that ref explicit, 116, group set identical to base's (`cmp` of the sorted id lists).
- `python3 -I -c "import sys; sys.path.insert(0,'tools/audit/seat'); import roster_lib; print(roster_lib.round_literal_defaults(REF))"` with REF e3cb5c019b464a770cc7c6fe2fbc858ed29debf7: 5 hits — `closeout.py:779 argparse default round10`, `roster_queue.py:72 module constant wave-r10`, `replan.py:10 docstring default`, `replan.py:163 parameter fallback`, `replan.py:3388 argparse help` (all audit-r10); with REF HEAD: 0.
- Class census, the ruling's rule: `git grep -nE "audit-r1[0-9]|round1[0-9]|wave-r1[0-9]" -- tools tests ':!*closures.json'` at the base. Every line outside the five above is a self-test fixture (`roster_lib`, `state_docs`, `cloud_dispatch`, `carry_audit`, `carry_fold`, `ledger`, `orchestrator_tick`, `owed_watch`, `plan_audit`, `plan_public`, `pulse`, `ref_privacy`, `roster_edit`, `handover_prompt`, `loop_ledger`, `finder_overlap`, `ci_predict`, `codeql_scope`, `gate_priority`, `stamp`, `beat_jobs_selftest`, `body_patch.sh`, `bus.sh`, `prepr.sh`, `brief_lint.mjs`, `check-wave-script.mjs`, `tests/lane_skip.py`) or a dated record: `roster_lib.CARRY_CUTOVER`; `review_strength.py`'s and the comments' citations of `dev/audit/rounds/round10/` evidence; `tests/closure.py`'s and `tests/layout.json`'s path classifications; `tests/doc_claims.py`'s `ROSTER` and `--markers` docstring, which read the round-10 roster because the marker grammar it resolves names `R10-` groups only (528 of them on that roster, 8 on round 11's) — round-10 by construction, not a live default. `tools/ci/selftest_closures.json` and `tests/closures.json` are measured tables of paths read. The AST rule (`round_literal_defaults`) extends the ruling's 1[0-9] grep to any N; its own census at the base found the same five live defaults and nothing else outside `ROUND_RECORDS` and `round<N>/` directories.
- Scope: `python3 tests/closure.py select --diff e3cb5c019b` prints `MODE: SCOPED -- 2 script(s) run`, `tests/doc_claims.py` and `tests/entities.py`, both run with `PYTHONPATH=tests/hastub` at 1ed52b9d10: rc 0 (since then: the selftest table and closeout's self-test, neither in either script's closure; prepr's `gate mode` at the head: `MODE: SCOPED`). `python3 tests/structure.py`: rc 0. Self-tests run green: `replan.py`, `roster_lib.py` (124 checks), `roster_queue.py` (69), `closeout.py` (41).
- `python3 -I tools/ci/selftest_scope.py record --step roster-library`, then `absorb --from` that file: the step now reads git objects (`cat-file`, `ls-tree`), the UNDER-SCOPED arm `ci_predict.py` predicted at 1ed52b9d10. Its `self-tests-outside-seat` note (dirs miss `tests/hastub`) is drawn by the merge base too, main's to absorb, and is left to it.
- `MUTANT_IN_PLACE=1 MUTANT_CMD="bash -c 'python3 -I tools/audit/seat/roster_lib.py --self-test && python3 -I tools/audit/seat/closeout.py --self-test'"`: in place because the roster_lib self-test reads HEAD from git; `bash -c` because mutant_run splits the command with shlex and runs no shell.
- `python3 tools/audit/archscore/score.py --diff e3cb5c019b`: `Architecture score: dS +0.0000 NULL`.

## Red checks

none

## Forward-carry

none

## Friction

none

