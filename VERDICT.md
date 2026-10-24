Fix review: merge 46dc1dda86b4e9d79f72f9a1d48bc0cc8c674f3e

bus-nonce: f7aab34fd8f09d7d55191186adf6388b

## Scope

Delta re-review of #2745 at live head 46dc1dda86b4e9d79f72f9a1d48bc0cc8c674f3e. The predecessor's merge verdict at c70c3e464a4edee48a81dd65c8c612f6e4139c3b (review/2745 f9a90bbd) covers the code, the roster edit 1debc245a and every other part of the body. This verdict judges only the one commit since then: 46dc1dda8 "ci: pin killed mutants", authored by github-actions[bot] (the ci-autofix mutation-autofix job). Round: delta re-review after the head moved by one autofix commit; the code review rounds are the predecessor's.

## Evidence

- RESULT delta-shape: `git rev-list --left-right --count c70c3e46...46dc1dda` = `0 1` (ahead 1, behind 0). `git diff c70c3e46..46dc1dda` adds 14 new files, 84 lines, all under `tests/mutation_ledger/killed_by/` (ledger.py 5, optimizer.py 8, pump_arbiter.py 1). It modifies or deletes no existing pin. Files moved outside `tests/mutation_ledger/`: 0. Nothing in `custom_components/` or under `tests/` other than the ledger moved (ev/delta-scope.txt, ev/delta-stat.txt).
- RESULT pins-match-body: the 14 anchors are the 14 sites (16 operator mutants) listed under the body's "Unpinned sites". At the head, `mutation_table.inventory()` yields exactly 16 sites for these 14 anchors (ev/sites.json). Every pinned `old` text matches its head line byte for byte (the driver asserts it before mutating).
- RESULT pins-real, 16 of 16 killed at the head, re-driven by me rather than taken from the bot. I applied each site's own `new` text from `mutation_table.inventory()` to a detached worktree at 46dc1dda and ran the pin's `killed_by` driver through `mutation_table.run_script` (the lane's own invocation, `PYTHONPATH=tests/hastub`), restoring the file afterwards. All worktrees were clean after the run (ev/redrive-results.txt, ev/drive.py):
  - ledger.py:64 CONST (`MIN_CALIBRATION_KWH = 2.0`): `mutation_table.py --anchor ... --scripts tests/features.py` at the head printed `PIN RE-VERIFICATION: 1 reproduced, 0 not reproduced`. Baseline tests/features.py rc=0 failed=0; null control NULL_COMMENT survived (ev/anchor-CONST-7dc7eda1.txt).
  - ledger.py:246 GUARD_OFF rc=1 failed=7; :355 CMP_BOUND rc=1 failed=2; :355 GUARD_OFF rc=1 failed=3; :357 RETURN_DEL rc=1 failed=7.
  - optimizer.py:345 CMP_BOUND rc=1 failed=2; :345 GUARD_OFF rc=1 failed=2; :347 RETURN_DEL rc=1 failed=6; :4600 GUARD_OFF rc=1 failed=7; :5193 GUARD_OFF rc=1 failed=3; :5399 CLAMP_DROP site 1 rc=1 failed=7; :5399 CLAMP_DROP site 2 rc=1 failed=2; :5400 CLAMP_DROP site 1 rc=1 failed=5; :5400 CLAMP_DROP site 2 rc=1 failed=6; :5400 RETURN_DEL (driver tests/plan_view.py) rc=1 failed=1, against an unmutated tests/plan_view.py baseline at the head of rc=0 failed=0.
  - pump_arbiter.py:1018 GUARD_OFF rc=1 failed=2.
  - Each failed count equals the count in the pin's `reason` line. For the two-site CLAMP_DROP anchors, where the reason quotes one site, the quoted site's count matches and the second site is also killed, as the reason says ("Each of the 2 sites under this anchor was killed"). The features.py baseline at the head is green (rc=0 failed=0, from the --anchor run), so every kill is a red against a green baseline.
- RESULT ratchet: at the head `mutation_table.py` reports "3988 unpinned site(s) of 6308 candidate sites, 3990 at the ratchet base 73b69fe0a; the ledger agrees with the deterministic inventory". The diff adds no unpinned site.
- RESULT pin-ref: the pins say "recorded against 806aa2ce89". That is a main commit (Merge #2734), an ancestor of origin/main and a descendant of the PR's merge base 73b69fe0a: the lane's ratchet base at run time, not a head. The kills were re-taken at 46dc1dda above, so the pins hold at the head independently of that ref.
- RESULT merge: `git merge-tree --write-tree origin/main 46dc1dda` exit 0, tree 8ddc0336d, no conflict and no claim-driver output (origin/main 4a00a3f05) (ev/merge-tree.txt).
- RESULT metric (step 14): the ledger movement is earned by the change. Each pin is a measured kill of a site this PR's code added, re-measured above, not an instrument artefact. No budget, closure, claim or golden file moved in the delta.
- CI on 46dc1dda (check-runs API, read about 18:25Z; two workflow runs, 40117085776 and 40117086150):
  - `tests / fast (3.14)` is failure in both runs, on `tests/stress.py` 1 of 113: winter/1z/space/pin-off makes 84263 production calls against the baseline's 78480, 1.074x over the 1.05x allowance (thermal_model.py +4072, optimizer.py +1654). These figures are identical to the body's "Red checks" entry, which answers the check (carry 1's comfort-matched thermostat run, added work by design, passes on tvofi's approving review per stress.py's rule). The predecessor judged it at c70c3e46, and the delta (ledger JSON only) cannot reach stress.py. `tests/entities.py` did not fail in this run.
  - `tests / mutation` is in_progress in both runs at the time of reading. It is the lane the delta's pins feed. My re-drive above reproduces every pin, so the lane is expected to read the 14 sites as pinned. Its conclusion was not available to me.
  - Every other completed check is success or skipped, including typing, browser, coverage, closures, closure-scope, arch-score, budget-raise-gate, hassfest, validate-hacs, codeql and governance/*.
- VERSION, the manifest version and RELEASE_NOTES.md are untouched by the delta (no file outside tests/mutation_ledger moved).
- Head recheck: origin/fix/r10-sav-comfort = 46dc1dda86b4e9d79f72f9a1d48bc0cc8c674f3e at verdict time, which is the head I measured. The body's "## Head" section names c70c3e46. The one commit since then is the ci-autofix commit judged here, which carries to it.
- Role currency: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Findings

none
