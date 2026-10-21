merge_pr.sh's owner mode reads the code-owned mandate scope from the gate it already reads the mandate through, and the owner hand-off from proof_watch.py is now pinned by a test. Closes #2497

The group's handoff 6219325c (2026-10-18) was never opened, and main has since landed most of it: tvofi's 0ed4aceb2 (merge_pr.sh owner mode takes `--mandate`, reads it live through budget_raise_gate's `_mandate` and `mandate_state`, and refuses before any post), dcd012deb (proof_watch.py hands it `--mandate` and refuses owner mode without one), and R10-SEAT-SELFTESTS-CI's step that runs `merge_pr.sh --self-test` and `proof_watch.py --self-test` in `instrument-self-tests`. This head merges main into 6219325c and keeps main's side of all five files. The handoff's duplicate governance.yml step is dropped, so this diff touches no workflow. Three pieces were still missing, and the commits after the merge add them:

- **Scope in one place.** merge_pr.sh passed the scope to `mandate_state` as the literal `("code-owned", "all")`, while the gate holds the other readers' scopes: `MANDATE_COVERS_RAISE`, and `MANDATE_COVERS_POLICY`, which merge_train.py and orchestrator_tick.py read as `g.`. This diff adds `MANDATE_COVERS_CODE_OWNED` beside them, and merge_pr.sh reads `g.MANDATE_COVERS_CODE_OWNED`.
- **Tests.** No test covered the scope: merge_pr.sh's self-test only used scope `all`. Its self-test now has a `code-owned` arm that passes and a `budget-raise` arm that refuses. The gate's self-test has three `covers_code_owned` checks.
- **Owner hand-off untested.** proof_watch.py's self-test drove app mode only. Its new (a3) arm pins that owner mode passes `--mandate <id>` to merge_pr.sh and that `--mode owner` without `--mandate` refuses at launch. The (a2) app arm is the null.
- **Docs.** INSTRUMENTS.md's proof_watch.py entry names owner mode's `--mandate`.

Brief, item by item, at this head:
- merge_pr.sh reads the mandate live through budget_raise_gate.py: `mandate_in_force` (main, 0ed4aceb2), and with this diff its scope too.
- It refuses before any GitHub write without a mandate: `gates` runs before `app_comment.sh` and `gh pr review` (main, 0ed4aceb2).
- proof_watch owner mode hands it the mandate id: `Watcher.do_merge` and the launch refusal in `main` (main, dcd012deb). This diff adds the test that pins them.
- Self-tests wired in CI: governance.yml `instrument-self-tests` (main, R10-SEAT-SELFTESTS-CI); `selftest_wiring.py --check` refuses an unwired one.

## Head

2eb1f37801733d093efe92b0b1569803c44b64a0 (merge base with origin/main 6961f06637964001a2ed544e495ea0312eeefa37, origin/main tip 6961f0663, 2026-10-21T09:49Z). The mutants M1-M4 ran at 031364171; the merge of main since then touches none of the four files, and the three self-tests and `tests/structure.py` were re-run at this head.

## Mutation proof

Each mutant was made in the worktree at the head above, run, then restored with `git checkout -- .`; the failing lines are pasted.

- M1: `MANDATE_COVERS_CODE_OWNED = ("code-owned", "all", "budget-raise")` in tools/policy/budget_raise_gate.py. Result: `FAIL mandate: scope budget-raise does not cover an owner approval of code-owned paths: got True, want False` (budget_raise_gate self-test: 242 checks, 1 failed). Also `FAIL owner mode under a budget-raise mandate refuses: the gate's MANDATE_COVERS_CODE_OWNED excludes it (rc=0: )` (merge_pr self-test: 14 checks, 1 failed).
- M2: merge_pr.sh reads `g.MANDATE_COVERS_RAISE` in place of `g.MANDATE_COVERS_CODE_OWNED`. Result: `FAIL owner mode under a code-owned mandate in force now passes (rc=1: MANDATE REFUSE: mandate 4100000001 has scope code-owned, which does not cover an owner approval of code-owned paths)` and `FAIL owner mode under a budget-raise mandate refuses ...` (merge_pr self-test: 14 checks, 2 failed).
- M3: in proof_watch.py `Watcher.do_merge`, `argv += ["--mandate", self.mandate]` becomes `pass`. Result: `FAIL (a3) owner mode passes --mandate <id> to merge_pr.sh` (proof_watch self-test: 36 checks, 1 failed). A first try deleted the line instead. That left an empty `if` body, so the mutant was an IndentationError and tested nothing; it is not counted.
- M4: in proof_watch.py `main`, the launch refusal's predicate becomes `a.mode == "never"`. It was run with a `gh` stub that exits 1, so the mutant could not reach GitHub. Result: `FAIL (a3) --mode owner without --mandate refuses at launch (got 1, want 2)` (proof_watch self-test: 36 checks, 1 failed).
- Failing test first: at a9012429d (tests, before the fix) the gate's self-test raised `NameError: name 'MANDATE_COVERS_CODE_OWNED' is not defined`.

## Null control

Unmodified head (M0): `budget_raise_gate self-test: 242 checks, 0 failed`, `merge_pr self-test: 14 checks, 0 failed`, `proof_watch self-test: 36 checks, 0 failed`. Inside the tests, the nulls are the (a2) app arm, which hands no `--mandate`, and merge_pr.sh's `app mode on a ready pull request passes the gates (null control)`.

## Figures

- `python3 tools/policy/budget_raise_gate.py --self-test` prints the tally line quoted in Null control.
- `bash tools/audit/seat/merge_pr.sh --self-test` prints the tally line quoted in Null control.
- `python3 -I tools/audit/seat/proof_watch.py --self-test` prints the tally line quoted in Null control.
- `python3 tests/structure.py` exited 0 at the head.
- `python3 tests/closure.py select --diff 6961f06637964001a2ed544e495ea0312eeefa37 --workdir <dir>` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`: every changed file is under tools/, which is INERT. The three self-tests above are the CI step's lines, run here.

## Red checks

none at handoff: no PR is open yet. `nightly-status` and `delivery-status` grade main: `nightly-status` is red on the nightly `slow` lane's `loop_cpu_ratio` budget, which the separate r10-replay-cap work fixes. This diff touches nothing either of them reads.

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
