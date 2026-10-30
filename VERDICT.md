Fix review: merge dabd6f1e596a26abc5bb85515add6480c708003a

bus-nonce: 7654c1f25df5b81d130fabc4fd0a4285

## Summary

Round 1 review of PR #3002 (R10-FLOW-DESIGN-STAGES part 3, item G only), measured from a detached worktree at dabd6f1e596a26abc5bb85515add6480c708003a (base ca0a6cfbc2e5538e6e2220793831443719ff6e98). The diff touches `tools/audit/seat/orchestrator_tick.py` (`designs_owed`, the new `_dispatch_age` and its self-test block) and the PR's own delivery row. Nothing goes beyond item G. Each control the brief names holds, and each arm's mutant fails.

## Findings

- Follow-up: a mutant survives in the age arm: changing `min(ages)` to `max(ages)` in `_dispatch_age` leaves the self-test at 223 checks, 0 failed. The fixture gives R10-L1 a single predecessor, so the "newest predecessor dispatch" rule for a group with several predecessors is not pinned. A two-predecessor fixture with different dispatch ages would pin it. The shipped code computes the correct (newest) age, so this is test strength only. Carry: R10-FLOW-DESIGN-STAGES
- Minor: the `_dispatch_age` docstring says it returns `n/a` for a group with no predecessor, but the code returns `(no predecessor)`. A no-predecessor group's line also reads "last predecessor dispatched (no predecessor)". Both are minor wording defects. No behaviour or test impact. Carry: R10-FLOW-DESIGN-STAGES
- Follow-up: `_dispatch_age` derives the topic with `rl.branch_of(p).split("/", 1)[-1]`, while the dispatcher names the ref with `cloud_dispatch._topic_of` (`branch_of(...).removeprefix("handoff/")`). The two agree on every topic the dispatcher accepts, because it refuses slashed topics. Even so, the rule now lives in two places and could drift. A shared helper (e.g. `_topic_of` moved to roster_lib) would close it. Carry: R10-FLOW-DESIGN-STAGES

## Evidence

- RESULT self-test at head: `orchestrator_tick self-test: 223 checks, 0 failed`. This matches the body's figure (ev/selftest-head.txt).
- RESULT test-first: I put the base production lines for `designs_owed` (the old `self.line`) back under the head's tests. Three new checks fail: the age, the CP mark, and age-unknown (ev/mutants.txt M7). The commit history cannot show the order (code and test landed in one commit, eba0dcc76), but the tests do fail against the pre-fix code.
- RESULT mutants (ev/mutants.txt):
  - M1 (CP always on) fails "null control: a non-critical group prints no CP mark".
  - M2 (CP always off) fails "a critical-path group carries the CP mark".
  - M3 (age replaced by `(age unknown)`) fails "prints the age since its predecessor dispatched".
  - M6 (`critical = set()`) fails the CP check.
  - M1–M3 reproduce the body's three mutants exactly.
- RESULT M5: removing the `if code: raise` guard leaves 0 failed. This is an equivalent mutant: a failed `git log` returns non-ISO output, and `fromisoformat` raises `ValueError` anyway. It is not a gap.
- The brief's controls hold. A group with no design ref prints its age ("dispatched 7h ago"). With the design ref present, nothing prints. A non-CP group (R10-L5) prints no CP mark.
- The re-shaped pre-existing DESIGN OWED check (`x.split()[2]` changed to a substring match) keeps its meaning: it still requires exactly one owed line, and that line names R10-L1.
- The dispatch-ref name `origin/dispatch/fixer-<topic>` matches `cloud_dispatch.py`'s `dispatch/<role>-<topic>` publish, with topic = branch less `handoff/`. Re-dispatches fast-forward the same ref, so the committer date of the ref's tip is the newest dispatch.
- Merge with origin/main cf4f6b7a660f5b61e0f2b933bd18647fe3ba90c7: `git merge-tree --write-tree` exits rc=0 with tree 58a0798eb02647d05c3e6ac3ff3a6b1ec8f3b312 and no conflicts (ev/merge-tree.txt).
- Structure ratchet at head: STRUCTURE RATCHET PASSED (ev/structure.txt). No budget file, closures.json, INERT, golden or claim file changes.
- VERSION, the manifest version and RELEASE_NOTES.md are untouched. `dev/governance/roles/` is unchanged between the merge base and origin/main, so the contract I read is current.
- No finder's harness is named. This is tooling item G of a residual brief, and the self-test is the instrument. I built no harness of my own.
- Head check: the PR body names authored head eba0dcc764ef877d809e1a3f9ff70f1c305f8b81 plus one row-only commit (dabd6f1e5, `dev/programme/delivery/3002.md`). That matches `git log`. PR head = dabd6f1e596a26abc5bb85515add6480c708003a when I measured and when I wrote this.
- Figures: the body's two figures (self-test 223/0, prepr.sh rc=0) are listed as resolved by figure_lint. I re-derived the self-test figure. I cited prepr.sh and did not re-run it, since it is a heavy gate.
- Forward-carry: the body says none. No finding of this PR changes a later stage's brief beyond the carries above.
- CI at dabd6f1e (check-runs API, read twice, the last read at about 16:45Z, every run listed individually): no run is red. Completed with success: tests/fast (3.14), typing, browser, arch-instrument, mutation, closure-scope, briefs, nightly-status, arch-score, budget-raise-gate, delivery-status, env-matrix, policy-docs, wave-script, hassfest, validate-hacs, codeql actions and js-ts, prelude, refresh. CodeQL rollup: neutral. The skipped jobs are conditional lanes: replay, nightly-ha, mutation-pins, mutation-autofix, claims-autofix, record, delivery-status-publish, kernel-points, arm.
- CI not concluded when I wrote this verdict: tests/closures, tests/coverage, governance/instrument-self-tests, codeql/Analyze (python), and the second workflow run's prelude (run 41091328895) were still in_progress. They are not verified green here, and the merge train must re-read them before merging. The body's `## Red checks: none` is accurate so far.
- Mutation lane: the green `tests / mutation` check was cited, not re-run. The extra mutants above are my own targeted ones.
