Design review: approve 43ff5ae6c1464d640acbce4ee03ab7cd23579c26

Round 2. I reviewed the delta fe76bbf2a6..43ff5ae6c1 (design.md only) against the base the note names, 91f6e91bea926777d03fc23de1c21e5247abf290. Prior verdict: origin/design-verdict/r11-ci-3885-queue 1f5a8a65a0.

Prior revise points:
1. Resolved. design.md §3 L6(a) is dropped, so gate-sweep.yml keeps no cancelled-conclusion skip and `settle` (tools/ci/sweep.py, `def settle`) still acts on a decider cancelled at the live head. §4 W1 now says how its re-run survives: every completed CI run keeps its sweep, cancelled ones included. §4 Tests adds the cancelled-decider W1 row, and the existing settle row stays beside it as the null. The §5 ship order and hot files no longer name L6a.
2. Resolved. §4 W1 routes each deferred run through `stale_pin` and then `fresh` (sweep.py:234 and :248 at base). A stale pin gets ONE `STALE-PIN` dispatch, matching sweep.py:48-50 and the `self.dispatches` guard at :263. A current pin gets `rerun-failed-jobs`. §4 Tests adds the stale-pin row: a dispatch and no re-run. Its null row is the current pin: a re-run and no dispatch.

Decisions routed:
- decision: owner. §6 "CI-5 (settled)" says the owner has made CI-5 obsolete. At review time nothing on origin shows it: refs/heads/handoff/r11-ci-3885-ci5-drop does not exist (git ls-remote), dev/programme/RULINGS.md on origin/main has no CI-5 entry, and ci.yml:70-76 on origin/main still carries the `CI-main` group. Until the owner confirms it, this is pending owner confirmation. No lever's shape depends on it: L1 applies only to `pull_request synchronize`, and push runs keep their own groups.
- decision: orchestrator. §5 holds L1 until handoff/r11-ci-3885-ci5-drop merges. That ref does not exist yet, so the orchestrator decides whether L1 waits for it or ships first against today's ci.yml, with `CI-main` unchanged.

Notes for the fixer (carried, not revise points):
- If L1 lands before the CI-5 drop, or the drop never lands, L1 keeps the `CI-main` expression at ci.yml:76 byte-identical. The new tests/entities.py concurrency pin then also keeps a row for the main push's first attempt in `CI-main`. Carry: R11-CI-3885-QUEUE (item l1-ci-main-order)
- W1's route through `fresh` inherits its existing leave-rules: a deferral red covered by a green gate (sweep.py:267) and the `code_red` no-dispatch rule (sweep.py:64-67). The W1 rows assert which of these lines prints, so a deferred run that is left is not counted as re-run. Carry: R11-CI-3885-QUEUE (item w1-fresh-leaves)

Checked and sound: the earlier points still hold (seam, L2's finder harness ci3885_light.py, null controls, the split into small PRs). Sibling designs: design/R11-CI-CASE-SELECT names none of ci.yml concurrency, sweep.py or prelude.py. The `concurrency ... cancels in progress` pin that L1 must rewrite exists at tests/entities.py:21412 at base.
Token count: not reported by this harness.
