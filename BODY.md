Triage P247 (V161): the `*_mutants` harnesses mutate a tracked file in place and restore it in `finally`, which a kill (a tool timeout is SIGTERM) skips, so the next run measures a mutant or refuses on a dirty tree. One shared helper, `dev/audit/harnesses/mutant_guard.py`, closes it: `arm(paths, scratch=, root=)` at the top of a harness's `main` (or `guarded(...)` around a block) (1) refuses rc 2, naming the file, when any path differs from `git show HEAD:<path>` before the first mutant; (2) installs SIGTERM/SIGINT handlers that restore from HEAD's blob and exit 128+signal; (3) at exit restores, compares each file's sha256 with HEAD's blob and exits 1 naming the file on a mismatch. Mutants stay in the working tree (no `git archive` copy; fixer.md step 2, #363).

Adopted in the twelve harnesses that rewrite a tracked file in place or write a sibling `_mutant_*.py`: arch_docs_first, carry_parser, flow_dispatch, merge_subject, plan_issues_chart, plan_page, policy_lint_family, sav_baseline, seat_selftests, shape_grammar (tracked file), train_upgrade, train_overlap_grade_p2 (scratch copy removed on kill). The flow_dispatch/plan_issues_chart/plan_page/shape_grammar `git diff --quiet` start checks are replaced by the stronger guard (it also catches staged edits).

Alternative considered: a `finally` per harness plus `atexit`: rejected, SIGTERM runs neither without a handler, and twelve copies drift.

Not adopted, dispositions: ci_layout_p0, gh_read_retry, heat_meter, nightly_pyspy_retry, cloud_setup, review_strength mutate a worktree/`git archive`/temp copy, never a tracked file in place, so a kill leaves the tree clean. Five shell harnesses (r10_flow_autotrain, r10_pusher_reap_launch, r10_tick_train, r10_train_raise_hold, r9_ro12_batch) restore by `git checkout --` per mutant and share the kill gap; they are not covered here (no shell twin of the guard exists), a follow-up for the finder of that class, not filed as an issue.

## Head

37f800f9a29343b76960d1a0675da182db605ba6 on origin/main a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0 (the code head 9a1a9835face80adc635d2ba31da0a34a146bb41 merged with main; the merge changed no file the diff touches beyond what main carried, and the last `tools/pr/prepr.sh` run at the code head exited 0).

## Mutation proof

`python3 dev/audit/harnesses/mutant_guard.py --self-test` (6 checks, pass unmutated). Start check dropped (`if dirty:` to `if False:`): FAIL "a planted leftover mutant refuses rc 2 naming the file" and FAIL "the refusal leaves the planted file as found". Handlers not installed (`signal.signal(...)` to `signal.getsignal(...)`): FAIL "SIGTERM mid-mutant leaves the file at HEAD's digest, rc 143" and FAIL "SIGINT mid-mutant ... rc 130". Both restored after.

On a real harness (`r10_flow_dispatch_mutants.py` on `tools/audit/seat/cloud_dispatch.py`): SIGTERM sent once the file differed from HEAD gave rc 143 with the file's sha256 equal to `git show HEAD:` (`e3e69c1545f6b4d2...` both). A planted `# leftover` line gave `mutant_guard: refusing, differs from HEAD ... tools/audit/seat/cloud_dispatch.py`, rc 2. With the start check dropped, the same planted run printed `RESULT mutant=M0 failed=0 verdict=null-ok`, i.e. it measured the planted file.

## Null control

A clean tree runs as before: `python3 dev/audit/harnesses/r10_flow_dispatch_mutants.py M0` printed `RESULT mutant=M0 failed=0 verdict=null-ok`, rc 0. The self-test's first check (clean tree ends at HEAD's digest, rc 0) is the same control.

## Figures

- `python3 dev/audit/harnesses/mutant_guard.py --self-test`: 6 ok, `MUTANT GUARD SELF-TEST PASSED`.
- `python3 tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/entities.py`: `ALL 2493 ENTITY CHECKS PASSED`.
- `bash tools/pr/prepr.sh`: rc 0 at the head above (gate mode SCOPED).
- Class enumeration (rule: harness files writing a tracked path in place; `grep -nE "write_text|write_bytes|git checkout" dev/audit/harnesses/*mutants*`): twelve adopted, six temp-tree, five shell dispositioned above.

## Red checks

none. Two predicted reds were repaired before the handoff: `ci predict` closures (a new harness file: `--apply-inert`, `tests/closures.json` lists `mutant_guard.py` as an inert read of `tests/harness_headers.py`) and `throwaway git` (self-test now builds its repo with `tests/throwaway_git.py`).

## Forward-carry

none, except the five shell harnesses above (r10_flow_autotrain, r10_pusher_reap_launch, r10_tick_train, r10_train_raise_hold, r9_ro12_batch), which restore by `git checkout --` per mutant and keep the kill gap; no live roster group owns them (read at origin/handoff/audit-r10-roster 61d29e166: R10-FLOW-AUTOTRAIN is done, R10-MUTANT-SKIP is done) and triage P247 narrowed the group to the Python guard, so the Not-adopted paragraph above is their recorded disposition. Carry: dismissed: triage P247 (dev/programme/triage/s6-batch49.md) narrowed R10-FLY-MUTANT-RESTORE to the Python guard and dispositioned the five shell harnesses as not covered, no shell twin of the guard exists, and this diff records that; a finder who reproduces a kill-left mutant on one files it under defect-root-cause.md

## Friction

none
