CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-partload-pricing, at head c3a279e3252a8b57bb00b5a677318cd4fe20387f. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name seat && git config user.email seat@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch c3a279e3252a8b57bb00b5a677318cd4fe20387f for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-partload-pricing before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-partload-pricing, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-partload-pricing, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-partload-pricing <body.md>`, which pushes refs/heads/handoff-body/r10-partload-pricing; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-partload-pricing`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-partload-pricing. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
INTERIM TOOLCHAIN: this environment's cached venvs are behind the locks (numpy, scipy, homeassistant, measured 2026-11-04). Before any measurement or golden run: `bash tools/audit/seat/cloud-setup.sh` and then `bash tools/audit/seat/cloud-setup.sh --check`; also confirm `python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'` against tests/requirements-ci.txt. If it cannot be refreshed say so in the body; CI remains the authority for goldens. Medium effort.

Fixers return only by refs, handoff/<topic> and body_push.sh; open no PR, post no comment; no Claude footers; no host paths.

The residue of R10-COP-PARTLOAD (#2872, #3006): with a part-load derate the electrical cost of heat is convex, and several valuations still price it linearly or at a steady mean draw; the live buffer store's planner cost and the inline buffer fallback in the two-zone and batch steps also wait here. Measure each magnitude first, with the zero-derate and flat-price null controls the carries name, and change a cost law only where the measured error is material; a D0 reading of the hot-water planner and the terminal cost decides any segmentation. Every carry was moved verbatim by the s9 carry-routing pass (2026-11-01) from a carries-open source group; each names its own controls. Re-measure every figure a carry states at this group's own merge base; carry no count. A carry that says it waits on an owner or orchestrator ruling waits for that ruling, and the body says so.

After: none

Carry 0: The 2.5x CPU cost of the live buffer store, and the 272 s owner-box outlier: a bound or warm start on the planner must earn it (R10-BUFFER-STORE carry, `optimizer.py`). Carry: R10-COP-PARTLOAD

Carry 1: The inline 35 L buffer fallback in the two-zone and batch steps, left to the group that next prices that family in `optimizer.py`. Carry: R10-COP-PARTLOAD

Carry 2: From PR #3006 round 2 (handoff-body/r10-cop-partload-p2 cee77229): linear valuations under a convex cost. The hot-water LP's objective (price * E / cop), the terminal row_cost, _deferred_energy_cost and the wood advisor's pump-heat price all price heat linearly at a COP, with no draw rate. Under a part-load derate the electrical cost is convex in heat, so each is a secant under-estimate. FIRST measure the magnitude: the cost error, in currency per day, between the linear price and the derated per-step price on the round-2 derate scenarios, with a zero-derate null control that must read 0. Segment only if the error is material: per-step segments in the LP, a stated refill rate for the terminal and deferred figures. A later D0 pass on _plan_dhw_min_cost and _terminal_cost owns the decision.

Carry 3: From PR #3006 round 2 (handoff-body/r10-cop-partload-p2 cee77229): mean-draw pricing. The setpoint sweep and the always-hot hot-water baseline price a day's hot water as a steady mean draw. That draw sits under the modulation floor on a real install, so the part-load derate rarely reaches it, while real hot water runs in bursts near p_dhw_max. FIRST measure it: re-price both cost laws at the planned run power on the round-2 scenarios and report the change in the sweep's chosen setpoint and in the baseline cost, with a zero-derate null control that must read no change. Pricing at the run power changes both cost laws, so it is a design change, not a conversion.

Carry 6: Pi CPU of the relaxed start, re-routed by the triage seat (s9 hold audit, 2026-11-01) from a hold on R10-COP-PARTLOAD, which went done (#2872 merged as d1c7708c2) before this carry was released. R10-PARTLOAD-PRICING is the live residue of R10-COP-PARTLOAD and owns custom_components/heatpump_optimizer/optimizer.py, where _relaxed_starts (the relaxed duty-cycle pass) lives on main. No other live group holds this item: a roster search for "process_time" finds it only on done R10-STAMP.

STRANDED CARRY 59 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-STAMP, index 5; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: owed after the stamp: a measured process_time on the owner's Pi; live grep "Raspberry|process_time|Pi install" empty.

Fold into: R10-COP-PARTLOAD (live). It holds the solver CPU measurements folded from R10-STORE-RACES.

Original text, verbatim:
Source: #2445 Forward-carry. Raspberry Pi CPU of the relaxed setpoint start is estimated only (+8 to +16 s per clamped solve, from +2.0 to +2.7 s measured on arm64). Owed after the stamp: a measured process_time on the owner's Pi install at the release head and its base, and cap the relaxed pass's maxiter if a clamped solve exceeds the update-interval budget.

Carry: R10-PARTLOAD-PRICING

Carry 7: Coordinator lane (s10 plan-slip, 2026-11-01): this group is planned off the coordinator.py cap; no carry or brief seam names coordinator.py. A fix that needs a coordinator.py edit stops and reports before editing, and is then re-queued behind the coordinator cap.

(Roster carry indexes not in this brief: 4, 5: marked done/dismissed/moved, or left to a later part. Indexes above are the roster's.)
