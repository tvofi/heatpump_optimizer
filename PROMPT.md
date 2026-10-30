CLOUD PROBE seat for tvofi/heatpump_optimizer, topic r10-live-away-heating, at head cf4f6b7a660f5b61e0f2b933bd18647fe3ba90c7. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: a read-only probe. Measure what the brief below asks against the tree at cf4f6b7a660f5b61e0f2b933bd18647fe3ba90c7 (`git fetch origin cf4f6b7a660f5b61e0f2b933bd18647fe3ba90c7`); change no tracked file and send no code to any ref.
Output: write your result as a body file and run `bash tools/audit/seat/body_push.sh r10-live-away-heating <result.md>`, which pushes refs/heads/handoff-body/r10-live-away-heating; that push is the return signal. A return push carries only your own result tokens.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
INVESTIGATION PROBE seat (read-only for production code; harness only), topic r10-live-away-heating. A user finding reported live by tvofi on 2026-10-30, so it is expedite priority.

Symptom, in the owner's words: "Turning away mode on still leaves plenty of heating slots in the plan, even though indoor temperature is already 22 degrees and i also lowered the set point to 18."

Question: is this a defect, and if so, where?

Work in a detached worktree at origin/main. Read custom_components/heatpump_optimizer/away.py (the AwayState and setback target, deadline-driven recovery) and follow how away mode and the user's set point reach the optimizer's space-heating plan: the target or comfort band the solver is given, the lower comfort floor, any pre-heat or return-recovery charge, price-driven thermal-mass charging, and DHW slots that a reader could mistake for heating. Also check how fast a toggle or a set-point change reaches the plan: an immediate replan, or only at the next optimization interval.

Then build a reproduction harness through the production coordinator/optimizer path, never a re-implementation of a formula. Scenario: indoor 22.0 °C, user set point lowered to 18, away mode on, with a realistic outdoor temperature and a 24-48 h price curve. Count the space-heating slots, their power and their timing.
Null controls, both required:
1. Away off at set point 18 with indoor 22. Does it schedule the same slots?
2. A flat price curve. Does the heating disappear, which would make it price-driven pre-charge?
Also run the same scenario with indoor at 18 to separate a stale reading from a wrong target.

Classify the cause as one of:
(a) correct behaviour, with a measured reason, e.g. recovery heating before an away deadline or a defrost or minimum-runtime floor;
(b) the away target or set point is not applied to the space plan;
(c) the plan is not recomputed on the toggle or set-point change, so it is stale until the next interval;
(d) price-driven charging ignores the upper comfort bound or the away setback;
(e) the slots are DHW or legionella, not space heating, and the plan display mislabels them;
(f) something else, named.
Cite path:line for each step of the chain.

If the user's live diagnostics would settle it, say exactly which fields you need. Never read anything under ~/Downloads.

Commit the harness to dev/audit/harnesses/r10_live_away_heating.py on your own probe branch, and publish your report as BODY.md on handoff-body/r10-live-away-heating via bash tools/audit/seat/body_push.sh r10-live-away-heating <file>. The report must contain:
- the classification;
- the measured table with both null controls;
- the code chain;
- if it is a defect, a minimal fix brief in prose, plus which roster group owns the seam (search the roster at origin/handoff/audit-r10-roster for away.py and the optimizer files) or whether it needs a new hotfix group.
Change no production file.
