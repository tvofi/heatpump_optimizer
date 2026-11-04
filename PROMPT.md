CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-learned-store-load, at head c3a279e3252a8b57bb00b5a677318cd4fe20387f. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name seat && git config user.email seat@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch c3a279e3252a8b57bb00b5a677318cd4fe20387f for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-learned-store-load before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-learned-store-load, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-learned-store-load, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-learned-store-load <body.md>`, which pushes refs/heads/handoff-body/r10-learned-store-load; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-learned-store-load`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-learned-store-load. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
INTERIM TOOLCHAIN: this environment's cached venvs are behind the locks (numpy, scipy, homeassistant, measured 2026-11-04). Before any measurement or golden run: `bash tools/audit/seat/cloud-setup.sh` and then `bash tools/audit/seat/cloud-setup.sh --check`; also confirm `python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'` against tests/requirements-ci.txt. If it cannot be refreshed say so in the body; CI remains the authority for goldens. Medium effort.

Fixers return only by refs, handoff/<topic> and body_push.sh; open no PR, post no comment; no Claude footers; no host paths.

Two latent learned-store lifecycle defects found by the R10-FACTORY-RESET fixer (orchestrator s9, 2026-10-31). (1) _async_load_thermal_learning saves the store before the COP and T4b learners have loaded, so a save in that window can write empty learner state over the stored one. (2) async_restore_learned_snapshot reads the snapshot ring without awaiting the snapshot store's read, and it never restores sample counts. Reproduce each through the production coordinator: a save during load, and a restore immediately after setup. Fix at the owning seam: one load barrier that every save and restore awaits. Controls: a learner's state survives a save issued mid-load, and a restore right after setup returns the newest snapshot including its sample counts. Null control: a fully loaded entry behaves as today. One mutant per gate.

After: none

Carry 0: STRANDED CARRY 55 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-PARAMS-OWNER, index 7; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: #2674 probe seat never scheduled; #2674 open and listed only by closed groups (ISSUE-STRANDED).

Fold into: R10-LEARNED-STORE-LOAD (live). Its brief owns the learned-store load/restore lifecycle seam that the seven #2674 leads probe.

Original text, verbatim:
#2674 (ls-r2: seven unprobed store-load leads) is scheduled as a probe-role seat on this group. Recipe with null control is in the issue; first probe whether each writer runs in the first refresh.

Carry: R10-LEARNED-STORE-LOAD

Coordinator lane (orchestrator s11 replan): only R10-COP-GATE-D and R10-LEARNED-STORE-LOAD edit coordinator.py now; if your change needs coordinator.py beyond your group's own seam, say so in the body rather than widening.
