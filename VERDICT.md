Fix review: blocked 1c385e45693e6d72965391146ea549d51f633afe test-vacuous: the production wiring of pins_running in run() and the mutation-pin-plan alternative survive deletion with the self-test green
bus-nonce: 5032055f2ba69cb8cde3e6b4ee7d5946

Round 1. Measured at head 1c385e45693e6d72965391146ea549d51f633afe (merge base 323fc7c48). The roles diff from the merge base to origin/main is empty. Evidence dir: /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev-2297/evidence

RESULT selftest head 33 checks 0 failed; base 323fc7c48 24 checks 0 failed (also 24 at 8747bbfc4)
RESULT mutants 17 planted, 14 killed, 3 survived (/private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev-2297/evidence/mutants.txt, runner /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev-2297/evidence/mutants.py)
RESULT survivor M11-run-unwired: the pins=lambda: pins_running(repo_slug, head) argument in run() deleted -> 33 ok
RESULT survivor M9-regex-no-pin-plan: "mutation-pin-plan" dropped from PIN_CHAIN -> 33 ok
RESULT survivor M16: TypeError dropped from pins_running's except -> 33 ok (minor)
RESULT fixer's five mutants re-run in my own form (M1 M2 M3 M5 M6): all killed
RESULT guard order: M12 (pin check moved above the other refusals) killed; M17 (chain read for every head) killed

## Blocking

1. M11. The only line that connects the fix to production is the pins= argument in run(), and no check covers it. plan_one's default is pins=lambda: [], which means "settled". So deleting the argument, or adding a caller that forgets it, restores the cancelling push and the self-test stays at 33 ok. That default fails open, while the PR's own design says an unread chain must fail closed. Fix: make pins a required keyword, or default it to None so a missing read is skip-pins-unread, and add an arm that drives run() (or one extracted per-PR step) with a stub api and asserts skip-pins-running.
2. M9. The brief and the body name mutation-pin-plan as part of the chain, but no arm pins it. The window matters. The jobs API does not list a job until its needs are met (probe: /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-round-10-audit-programme-de1185/ab673435-c91c-44f8-bd8e-6fa54b531db8/scratchpad/rev-2297/evidence/jobs-api-probe.txt shows two in_progress runs with pins shards running and no mutation-autofix row). So while mutation-pin-plan runs,  has completed and no mutation-pins job exists yet. pin-plan is then the only chain job listed, and the M9 mutant would merge and cancel the chain at that moment.
3. The body's "Unpinned sites" says every new predicate is pinned. M11 and M9 contradict that, and its "31 arms that existed before" is 24 at both bases I ran.

## Adversarial questions from the brief

- Does a skipped DIRTY PR ever get merged? Only on a later push to main or a manual workflow_dispatch. merge-main.yml triggers on push to main and workflow_dispatch only, and mutation-autofix's own push to the head does not trigger it. In a quiet period the PR stays DIRTY with no bound. The docstring says so honestly, but the body's bound (350, mutation-pins' timeout-minutes) understates the chain: mutation 160 + pin-plan 5 + pins 350 + autofix 10, plus queue time. A stuck queued job is bounded by GitHub's 24 h queue expiry. A held (action_required) run reports status=completed (probe), so it is skipped and never blocks. A queued run with no jobs (37642397144, queued since 2026-10-07, 0 jobs) yields [] and never blocks. Not blocking, but the body's bound sentence is wrong.
- Does the unread arm fail safe without starving? Yes. The read happens only for a head every other guard would merge (M17 killed). A rate limit fails mergeable_of first, as skip-error, the existing behaviour. One residual: the runs read takes page 1 only (per_page=100, total_count not checked), so a head with more than 100 runs, for example accumulated PR-contract re-runs, can hide the Tests run and read as settled. That is a fail-open edge, not reproduced.
- Are the job-name matches exact? Yes, anchored, and mutation-nightly, mutation-ledger and mutation-ledger-push are excluded (M10 killed). A rename escapes silently: renaming any of the four jobs in tests.yml turns the guard into a constant [] with every check green, because nothing ties PIN_CHAIN to tests.yml's job names. Suggested countermeasure in the same fix: an arm that loads tests.yml and asserts that the set of jobs PIN_CHAIN matches is exactly {mutation, mutation-pin-plan, mutation-pins, mutation-autofix}.
- Are the existing guards unchanged in order? Yes. The decide() arms are unchanged and the pin checks come last (M12 killed). plan_one reads pins only when status == merge (M17 killed).
- Transition gaps (residual): because unstarted dependent jobs are unlisted, there is a window of seconds between one stage completing and the next being created (mutation -> pin-plan, pin-plan -> pins, last shard -> autofix) where no chain job is listed. A push in that window still cancels the chain. Worth a sentence in the docstring.

Not re-run: the gate and the mutation table (CI's, tvofi 2026-09-30). The head's check-runs were still queued or in progress when I measured (14 of 36 not concluded); this verdict does not depend on them.
