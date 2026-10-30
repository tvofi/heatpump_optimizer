CLOUD FIXER seat for PR #2989 of tvofi/heatpump_optimizer, at head 083905bdf9650faf4743dbde95f991aac5fc78bd. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 083905bdf9650faf4743dbde95f991aac5fc78bd for the base you were given.
Output: push the code to refs/heads/handoff/r10-fly-openpr-atomic, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-fly-openpr-atomic <body.md>`, which pushes refs/heads/handoff-body/r10-fly-openpr-atomic; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (repair before update), group R10-FLY-OPENPR-ATOMIC (CRITICAL PATH), PR #2989, live head a11db7fea14bc34633eb65e8111a207142eb45ab. Your round-5 handoff is handoff/r10-fly-openpr-atomic at 083905bdf9650faf4743dbde95f991aac5fc78bd, with body beea0016. Contract: dev/governance/roles/fixer.md and dev/governance/rules/defect-root-cause.md at origin/main (e77418f9).
update_pr refused it because prepr's ancestry-reds check failed: `governance / instrument-self-tests` is red at a11db7fe, and `## Red checks` does not answer it. The red is real and comes from the round-4 open_pr.sh change. The job log (check run on a11db7fe) shows:
  ledger self-test: 77 checks, 3 failed:
    FAIL open_pr.sh carries both attempt lines
    FAIL a TERMed opener records started then unopened on its handoff ref
    FAIL null control: an opener that ends records opened,PR=<n>
  r10_ledger_mutants self-test: 135 checks, 1 failed: FAIL O1_no_attempt_on_exit: anchor occurs once in tools/audit/seat/open_pr.sh
Do:
- At 083905bd, run python3 tools/audit/seat/ledger.py --self-test and the r10_ledger_mutants self-test (dev/audit/harnesses). If they still fail, fix open_pr.sh so the ledger attempt lines and the EXIT-trap close coexist: one attempt line on each path, and the O1 anchor unique. Do not weaken the ledger tests. Then run the whole instrument-self-tests set locally until it is clean.
- In ## Red checks, name governance / instrument-self-tests at a11db7fe, its cause, and its answer. The cheaper detector is these local self-tests, which take seconds; prepr's instrument predict did not run them. Re-derive every figure.
Return handoff/r10-fly-openpr-atomic as a fast-forward of 083905bd, plus handoff-body via body_push.sh. Never open or edit the PR. If a hook refuses you, stop and report.
