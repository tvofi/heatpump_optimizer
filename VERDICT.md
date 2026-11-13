Fix review: blocked 552638f8dc3a1c7f270448163d44df992c62dac2 mutation-vacuous: prune CLI writes nothing; prune CLI accepts unknown drops; probe kept by listed directory

bus-nonce: 4f9a4fbb57099d2aa1830863101492cd

Round: first review (round 1), head 552638f8dc3a1c7f270448163d44df992c62dac2, measured at that head in a detached worktree.

## Block

Three non-equivalent mutants of lines this diff adds survive `python3 -I tools/ci/selftest_scope.py --self-test` (136 checks, 0 failed), and the PR's named `tools/ci/selftest_scope_mutants.sh` doesn't carry them (ev/own_mutants.txt, driver ev/run.sh):

- `main` prune branch, `write_table(root / TABLE, entries, root)` deleted: `prune` exits 0 and writes nothing. SURVIVED.
- `main` prune branch, `if unknown:` replaced by `if False:`: `prune` silently writes the table even though a drop named nothing in the entry. SURVIVED.
- `shrink_drops` probe rule, `or any(a in dirs for a in _ancestors(x))` deleted: the docstring's "or lists its directory" exemption is untested. SURVIVED. This mutant fails closed (more refusals), but nothing pins the claim.

The self-test exercises `prune_entries` but never the `prune` CLI. The body's forward-carry to R10-NUDGE-RETIRE (on handoff/audit-r10-roster 83f016606c) tells that group to remove reads with exactly `python3 -I tools/ci/selftest_scope.py prune --step ID --drop files:PATH`. That is the one sanctioned way a read leaves the table, and its CLI path is the unpinned part. To clear the block: add a self-test check that drives `main(["prune", ...])` on a fixture table (it writes the table, refuses an unknown drop with rc 1, and leaves the file unchanged), plus a fixture for a probe kept by a listed ancestor directory. Then add scope_mutant lines for the three mutants above.

Fix in the same round as well: `table_base` returns None when a named base (SELFTEST_BASE or origin/GITHUB_BASE_REF) can't be resolved, and `shrink_gaps(root, None)` then returns [], so `static` passes with the guard unevaluated (fail open). In CI today, governance.yml's instrument-self-tests job checks out with fetch-depth 0, so origin/main resolves there. A shallow or base-less run would skip the guard silently, though. An unresolvable named base should be a problem line, not a pass.

## Evidence

- ev/HEAD.txt: 552638f8dc3a1c7f270448163d44df992c62dac2. PR body `## Head` names this head and the code head 82f3cf9759 (step 7 ok).
- RESULT selftest_scope --self-test at head: 136 checks, 0 failed. `static` with SELFTEST_BASE=origin/main: 114 gated step(s), 0 problem(s). This matches the body.
- RESULT tools/ci/selftest_scope_mutants.sh at head: 20 mutants, "SELFTEST-SCOPE MUTANTS: every mutant refused", including the PR's 4 new mutants (ev/selftest_scope_mutants_tail.txt).
- RESULT own mutants at head: 17 run. 14 killed, 3 survived (above). A 4th survivor, removing `if TABLE not in {p for _, p in rows}: return []`, is equivalent: an untouched table compares equal to itself. Its only effect is the cost of one `git show`. Not a finding.
- RESULT null control, re-derived with my own driver (ev/null.py; ev/nullcontrol.txt), using the head's `shrink_gaps` over the 16 first-parent merges touching the table in ba6fd7e8b^..3b9749dac5 (count 16, matching the body). It refuses #3409 (3), #3419 (5) and #3506 (8), and passes the other 13, #3535 and #3507 among them. With the deletion exemption mutated out, #3507 is refused (2) and the other three are unchanged. Every figure the body gives reproduces.
- fold_ledger check: 0 violation(s). tests/structure.py: STRUCTURE RATCHET PASSED (ev/cheap_checks.txt).
- tests/entities.py (env -u BASH_ENV) did not run in this seat: ModuleNotFoundError homeassistant. Unverified here.
- VERSION, manifest and RELEASE_NOTES.md are untouched in the three-dot diff (step 5 ok). No claim file is touched, and the diff contains no golden fixture.
- `git merge-tree --write-tree origin/main 552638f8dc3a1c7f270448163d44df992c62dac2`: rc 0, merges cleanly (ev/mergetree.txt).
- Forward-carry (step 10): present on handoff/audit-r10-roster 83f016606c, group R10-NUDGE-RETIRE, with its precondition "Re-measure each affected step's entry at its own merge base". The packet's carry_audit reports 1 routed, 0 unrouted.
- CI at the head: classify printed WAIT ("pending: gate red: none") at every poll until this verdict (ev/classify.log). The gate wasn't red at any poll, and no red check was owed an answer. The block above doesn't depend on CI.
- Finder's harness: none named in the packet. The fix's own self-test and mutants are the fixer's instruments. The null-control driver here is mine, built for this review and disclosed as such (ev/null.py).
- Step 14: the table diff in tools/ci/selftest_closures.json re-collapses listed files into D/** entries (covered under the guard's `covers` rule). It adds HEAD, objects=true and git diff to the selftest-scope step, which matches the new git reads in `static`. No budget moved.
