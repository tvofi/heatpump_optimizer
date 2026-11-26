# r11-pre-token-ledger: part 1 stopped before its handoff (reconciliation fire 2026-11-27)

Question: part 1's carries 0-6 merged as #3906 (merge f9eff1b832 on main), and handoff/r11-pre-token-ledger still holds closed #3898's head c892a81941, which is no ancestor of main. This seat's one-commit head 09425c02b6 (cut from origin/main fd93aa3e9b; this commit's second parent) cannot fast-forward handoff/r11-pre-token-ledger, handoff-body/r11-pre-token-ledger or this ref, and the session refused a `--force-with-lease` push. Does the orchestrator reset handoff/r11-pre-token-ledger (and the body ref) to take 09425c02b6, or name another return ref, or drop it?

Previous seat's BLOCKED.md, decided: the recommended option, take the window-bound arms. #3906 landed the upper-bound arms. The lower-bound arm, the first of 035ae800d6's two, is not on main, and 09425c02b6 adds it.

Evidence, measured at the named heads (bytecode caches cleared, PYTHONDONTWRITEBYTECODE=1: a same-size, same-second edit otherwise reads a stale .pyc and passes falsely):

- At origin/main fd93aa3e9b, the `ledger_unread` mutant `a <= at(r["t"]) < b` changed to `a < at(r["t"]) < b` (that line alone) leaves `check_scopes.ledger_round_self_test()` with 11 arms and no false arm, so it survives.
- At 09425c02b6, the new arm `--round null: a seat class whose only row is at the window's first second is read` returns False under that mutant. It also returns False under the fixture swap `whole[0]` changed to `whole[1]`. At the head, all 12 arms hold.
- `python3 -I tools/audit/check_scopes.py --repo . --self-test` at 09425c02b6 printed `SELF-TEST passed (every perturbed scope refused)`. `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- Diff mutants: `MUTANT_CMD="python3 -I tools/audit/check_scopes.py --repo . --self-test"`, run through `python3 tools/audit/seat/mutant_run.py --diff "$(git merge-base origin/main HEAD)...HEAD" --cmd "$MUTANT_CMD" --max-mutants 40 --in-place --report-only`, rc 0, with one line: `SURVIVED tools/audit/check_scopes.py:1397 STMT_DEL  pass`. That is the deletion of the arm's own assignment, the self-test-arm category #3906 lists under `## Unpinned sites`. The default `--copy-tree` run refuses `BASELINE FAILS` because the self-test needs a git checkout. An earlier CONST_SWAP survivor (`whole[:1]` changed to `whole[:2]`) is killed at this head by indexing `whole[0]`.
- prepr.sh was not run: no return ref takes the head. It is owed at whichever ref is named.
