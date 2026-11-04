CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-arch-shapes-classifier, at head c3a279e3252a8b57bb00b5a677318cd4fe20387f. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name seat && git config user.email seat@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch c3a279e3252a8b57bb00b5a677318cd4fe20387f for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-arch-shapes-classifier before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-arch-shapes-classifier, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-arch-shapes-classifier, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-arch-shapes-classifier <body.md>`, which pushes refs/heads/handoff-body/r10-arch-shapes-classifier; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-arch-shapes-classifier`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-arch-shapes-classifier. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
INTERIM TOOLCHAIN: this environment's cached venvs are behind the locks (numpy, scipy, homeassistant, measured 2026-11-04). Before any measurement or golden run: `bash tools/audit/seat/cloud-setup.sh` and then `bash tools/audit/seat/cloud-setup.sh --check`; also confirm `python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'` against tests/requirements-ci.txt. If it cannot be refreshed say so in the body; CI remains the authority for goldens. Medium effort.

Fixers return only by refs, handoff/<topic> and body_push.sh; open no PR, post no comment; no Claude footers; no host paths.

GROUP R10-ARCH-SHAPES-CLASSIFIER (new, size S, split from R10-ARCH-SHAPES at its round 4 under the three-round rule, orchestrator ruling 2026-10-25, mandate 6329234399). Land the reason-classifier arm of finding D8-s1-01 that #2819 parked on the branch park/r10-arch-shapes-classifier: the space and DHW step reason classifiers call a sub-running share the plan calls off idle, as the plan views, pump schedule and wood advisor already do after #2819. Its golden drift is host-dependent (see R10-996-RUNNER-CLAIMS), so it lands only on that group's claim grammar: claim the drift by shape, never by a fixed fixture list. Start from the parked commit, merge origin/main, re-execute fixer.md steps 2-8, and confirm green on the CI runner. Every carry #2819's body routes here is part of this brief.

After: none

Carry 0: The `tests/golden/claimed_drift.txt` header does not name the shape line, and a branch that claims nothing leaves that file byte-identical. The first branch that claims by shape restates the header with its claim. Carry: R10-ARCH-SHAPES-CLASSIFIER

Carry 1: R10-ARCH-SHAPES-CLASSIFIER claims by `shape: space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'`; `bash dev/audit/harnesses/r10_shape_claim_controls.sh <its head> <its base>` re-runs the real-capture controls there. Carry: R10-ARCH-SHAPES-CLASSIFIER

Carry 4: The D8-s1-01 reason-classifier arm: `optimizer.classify_space_steps` / `classify_dhw_steps` read each channel's draw only on its `channel_heating_steps`. The commit carries the helpers `channel_heating_draw` / `_heating_draws`, the feature check "a step the plan runs no pump at is idle to the reason classifiers (D8-s1-01)", and the two `tests/entities.py` dispositions back to the owner-module reading. It is commit `996b54cf15ea3c7693383165ae2f080d2e04971b` on `park/r10-arch-shapes-classifier`, and claims nothing until the claim grammar lands; the band census is its evidence. Carry: R10-ARCH-SHAPES-CLASSIFIER

Carry 5: The census `dev/audit/harnesses/r10_band_census.py` and its susceptible set are the input to the claim grammar for runner-conditional drift. The set is host-dependent, so a claim must be by shape, never a fixed fixture list. R10-996-RUNNER-CLAIMS, which this item named until it merged as #2843, is done; the queued group that lands on its grammar is the destination. Carry: R10-ARCH-SHAPES-CLASSIFIER

Carry 6: From #2946 (R10-CONFIGFLOW-PAGES arm D, verdict/2946 carry-missing): four probed P2 sweep instances of #2238 that no group owned decide "the plan runs this step" with their own 0.05 kW copy, where the owner thermal_model.planned_draw_runs uses MIN_RUNNING_DRAW_KW (0.1 kW): freq_control FrequencyMap.recommend (recommends 33.0 Hz on the 0.07 kW step the owner calls off), FrequencyMap.evidence_exhausted (gate `target_kw <= 0.05` passes 0.07), coordinator _async_learn_buffer_cooling (`float(self._current_action.get('power', 0.0)) > 0.05` reads heating=True) and coordinator _observe_frequency (watch_active = `self._commanded_power() > 0.05 and reported >= hz_min and not defrost_interval(...)`). This is D8-s1-01's fact, the same move as this group's parked classifier arm (classify_space_steps, classify_dhw_steps), so each seat calls the owner instead of a copy. Precondition and control: re-measure at this stage's own merge base with PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P2/probes_p2.py, with `defrost_interval` bound in the sixth probe's eval namespace (or the predicate re-extracted; the committed probe raises NameError there since #2527), and with enumerate_p2.py's F1_run_threshold count; at #2946's tree (origin/main 66974d473) a scratch copy read probes_failed=5 of 5 before the sixth, and enumerate_p2.py F1_run_threshold=13. Null: the committed probes_p2.py --perturb no longer applies at #2946's tree (its first FIXES text, optimizer.py `threshold: float = 0.05`, matches 0 times, AssertionError), so the stage rebuilds the null as the owner-valued swap on a temp copy and shows it reads probes_failed=0 before claiming the fix's 0. Out of scope: the F5 clone classes (R10-ROUND-PLAYBOOK).

Carry 7: The four probed P2 sweep instances that no group owns (`FrequencyMap.recommend`, `FrequencyMap.evidence_exhausted`, `_async_learn_buffer_cooling.heating`, `_observe_frequency.watch_active`) decide "the plan runs this step" with a 0.05 copy, where the owner `thermal_model.planned_draw_runs` uses `MIN_RUNNING_DRAW_KW`. That is D8-s1-01's fact, and the parked classifier arm is the same move, so they are routed to that group. It landed in `dev/programme/rosters/wave-r10-groups.json`, group R10-ARCH-SHAPES-CLASSIFIER, on `handoff/audit-r10-roster` at `494831e995497efe42aa147f85f246f9839d2898` (roster tip `3b14d527a03926d092cb06631dcd3601b35786a9` contains it), with its control stated as a precondition. Carry: R10-ARCH-SHAPES-CLASSIFIER

Carry 8: Folded in from R10-HOTFIX-PREHEAT-LABEL (tvofi, 2026-10-31: "Can't the pre-heat label group go into the classifier group? I don't need it to be a hotfix"). A fixer had started it; any work in progress is on refs/heads/handoff-wip/r10-hotfix-preheat-label, if that ref exists. The brief, whole:
Live user finding (tvofi, 2026-10-30). Probe report: handoff-body/r10-live-plan-energy 7c4e639e49214592ef2ef2ddd48df522a3efd2cd, measured at main cc930cdd1.

The space-step classifier labels a heating step preheat_weather whenever the step's heat-loss factor exceeds 1.1, and it tests this before the price test. That factor includes the learned house_heat_loss_scale, so a house whose learned scale is above 1.1 is labelled "preheat for weather" under perfectly flat weather. Measured, flat weather and flat price: scale 1.05 gives 0 such steps; scale 1.2356 gives 51; the owner's live plan gave 88 of 96.

Fix: test only the forecast's weather component, meaning the factor relative to its own scale-free baseline, so a learned level never reads as weather.
Controls:
- flat weather with scale 1.24 gives zero preheat_weather steps;
- a real forecast cold spell, at scale 1.0 and at 1.24, still labels preheat_weather;
- null control: scale 1.0 with flat weather is unchanged.
One mutant: revert to the raw factor; it fails the first control.

Carry 9: Start from refs/heads/handoff-wip/r10-hotfix-preheat-label at 9bfbe38661152e98cbe5661417c363486703093f. It holds the folded preheat-label fix almost finished, on base 14ed13551 (orchestrator s9, 2026-10-31).
Root cause: in optimize, forecast_heat_loss_factors divides effective_heat_loss_coefficient(...) by the unscaled nameplate. That function multiplies in house_heat_loss_scale (thermal_model.py ~2846), so the "weather" factor equals scale x wind x rain. The same defect sits in _anticipatory_weights, the warm start.
The fix: a module helper, _weather_loss_factors, divides each step's loss by the same house's calm, dry loss. It is bit-identical to main at scale 1.0. As a side effect class_excess_loc falls from 17655 to 17648, re-recorded in its own commit.
Tests added to tests/features.py:
- flat weather at scale 1.24 gives no preheat_weather;
- a wind spell is labelled at scales 1.0 and 1.24;
- null control: scale 1.0, flat forecast;
- floor values.
Main's code fails exactly the first two. The finder's harness takes the owner's arm from 88/96 to 0. Plans at a scale above 1.1 shift by up to about 0.14 kWh through the warm start.
Still owed:
- the scoped gate and features.py at the head;
- prepr, including Unpinned sites: the 2 CLAMP_DROP floors are killed by the floor check but are not in the ledger;
- the body.
Merge it with the classifier work, so one fixer owns classify_space_steps and its golden.

(Roster carry indexes not in this brief: 2, 3: marked done/dismissed/moved, or left to a later part. Indexes above are the roster's.)
