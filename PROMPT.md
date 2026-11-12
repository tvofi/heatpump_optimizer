CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-hotfix-main-ist-readset-2, at head 2b4515dc52821ad721225090d329c224dbddafae. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 2b4515dc52821ad721225090d329c224dbddafae for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-hotfix-main-ist-readset-2 before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-hotfix-main-ist-readset-2, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-hotfix-main-ist-readset-2, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-hotfix-main-ist-readset-2 <body.md>`, which pushes refs/heads/handoff-body/r10-hotfix-main-ist-readset-2; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-hotfix-main-ist-readset-2`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-hotfix-main-ist-readset-2 and refs/heads/handoff-wip/r10-hotfix-main-ist-readset-2-body. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
HOTFIX. Main push-only self-test read-set drift at main 6e100ef6: governance / instrument-self-tests job 131147058316, step Refuse a self-test read set the committed table misses (the push-only drift step over tools/ci/selftest_closures.json), same family as merged hotfix #3487 r10-hotfix-main-ist-prepr-scope. Drift lines, verbatim apart from quote marks:
  UNDER-SCOPED step policy-lint-mutants: probes misses ["dev/audit/config/.gitattributes", "dev/governance/config/.gitattributes", "dev/governance/config/cfr_exclusions.json"]
  UNDER-SCOPED step field-coverage: files misses ["tools/pr/figure_block.py", "tools/site/day_chart.mjs"]
  UNDER-SCOPED step verdict-bus: probes misses ["tools/pr/figure_registry.json"]
  UNDER-SCOPED step push-names-the-host: files misses ["tools/pr/figure_block.py"]
  UNDER-SCOPED step selftest-wiring: files misses ["tools/audit/seat/r10_disinfection_setpoint_mutants.py", "tools/pr/figure_block.py", "tools/site/day_chart.mjs"]
  UNDER-SCOPED step features-block: probes misses ["tools", "tools/audit", "tools/audit/seat"]
  UNDER-SCOPED step features-block: dirs misses ["tools/audit/seat"]
  UNDER-SCOPED step mutant-driver: probes misses ["the stm checker script (a bare name, no path)"]
  UNDER-SCOPED step programme-pulse: files misses ["tools/audit/seat/gh_read.py", "tools/audit/seat/merge_train.py"]
  UNDER-SCOPED step programme-pulse: probes misses ["tools/policy/policy_lint.mjs"]
  UNDER-SCOPED step programme-pulse: dirs misses ["tools/audit/seat"]
  UNDER-SCOPED step review-packet: probes misses ["tools/pr/figure_registry.json"]
  UNDER-SCOPED step tick-loop: probes misses [".gitmodules", "tools/.git", "tools/HEAD", "tools/audit/.git", "tools/audit/HEAD", "tools/audit/seat/.git", "tools/audit/seat/HEAD"]
  UNDER-SCOPED step tick-loop: it read the index, the table says not
  UNDER-SCOPED step tick-loop: it read the objects, the table says not
  UNDER-SCOPED step hooks-setup: files misses ["tools/audit/seat/r10_disinfection_setpoint_mutants.py"]
  UNDER-SCOPED step ci-predictor: probes misses ["tools/pr/figure_block.py"]
  UNDER-SCOPED step prepr: dirs misses ["dev/audit/config", "dev/governance/config"]
  UNDER-SCOPED step open-pr: files misses ["tools/audit/seat/r10_disinfection_setpoint_mutants.py", "tools/pr/figure_block.py", "tools/site/day_chart.mjs"]
  UNDER-SCOPED step pr-args: files misses ["tools/audit/seat/r10_disinfection_setpoint_mutants.py", "tools/pr/figure_block.py", "tools/site/day_chart.mjs"]
  UNDER-SCOPED step update-pr: files misses ["tools/audit/seat/r10_disinfection_setpoint_mutants.py", "tools/pr/figure_block.py", "tools/site/day_chart.mjs"]
Fix: re-record the named self-tests read sets in tools/ci/selftest_closures.json per the re-record rule stated in tools/ci/selftest_scope.py (read it at current main). Name which merge introduced each read by git log on the read path: candidates are #3479 and #3497 (figure_block.py, figure_registry.json, day_chart.mjs, r10_disinfection_setpoint_mutants.py are the paths to log); say in the body which. Failing check first: the check that refuses on the table missing a read must be red at main for these steps and green after, with a null control. PR body answers the red-check trigger: a cheaper detector is selftest_scope check run by prepr on a diff that adds a read, if it does not already; state which. Only tools/ci/selftest_closures.json changes unless the rule requires more.
Entities trap: a new tracked file must be classified in a closure or on the INERT list of tests/closure.py.
