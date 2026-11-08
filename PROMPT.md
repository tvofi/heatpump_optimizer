CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-hotfix-cop-unmeasured, at head 9cf0b6108527943795f1b4dda6e6069ebff0e7f7. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 9cf0b6108527943795f1b4dda6e6069ebff0e7f7 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-hotfix-cop-unmeasured before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-hotfix-cop-unmeasured, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-hotfix-cop-unmeasured, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-hotfix-cop-unmeasured <body.md>`, which pushes refs/heads/handoff-body/r10-hotfix-cop-unmeasured; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-hotfix-cop-unmeasured`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-hotfix-cop-unmeasured and refs/heads/handoff-wip/r10-hotfix-cop-unmeasured-body. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
OWNER RULING 2026-11-07 (supersedes the footer's merge-main step): hand off at your first clean prepr.sh head. Do NOT merge a moved origin/main or re-run prepr because main moved. Merge main only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. The merge train recarries and re-proves your head on the current main.


OWNER RULING 2026-11-07 (mutants): before handoff, set MUTANT_CMD to your group's self-test, or to a features_block.py call for the lines you changed. Let prepr.sh's diff-mutant step run `tools/audit/seat/mutant_run.py --diff` over your added lines (use --max-mutants to bound it). For every SURVIVED site, add a test that kills it, or give it a `## Unpinned sites` disposition. Report the mutant run's wall time and its survivor count in `## Figures`. CI's mutation-autofix still writes the pins.

OWNER RULING 2026-11-07: a red on a check outside the required set (the merge train's required contexts; tests / nightly-status, record, record-autofix and delivery-status never count) never blocks. Do not return blocked for an unnamed non-required red. Name it in the body only if convenient.


INTERIM TOOLCHAIN: this environment's cached venvs are behind the locks (numpy, scipy, homeassistant, measured 2026-11-04). Before any measurement run: `bash tools/audit/seat/cloud-setup.sh` and then `bash tools/audit/seat/cloud-setup.sh --check`. Medium effort.

Return only by refs; no Claude footers; no host paths. Opus, medium effort.

CLOUD FIXER (opus), REPAIR round for PR #3297 (R10-HOTFIX-COP-UNMEASURED, hotfix, branch fix/r10-hotfix-cop-unmeasured, topic r10-hotfix-cop-unmeasured). The PR head is 9cf0b6108527943795f1b4dda6e6069ebff0e7f7 (handoff/r10-hotfix-cop-unmeasured 4ed3f5445; body ref handoff-body/r10-hotfix-cop-unmeasured e8bc1dad); base your work on the PR head, never re-cut. A fix review BLOCKED this head (verdict 2026-11-07T23:36:47Z, mutation-vacuous), quoted in full below.
THE CURE (orchestrator ruling): in tests/features.py's R10-HOTFIX-COP-UNMEASURED section add a `measured_cop` record to `_cu_old_payload`; assert `_cu_old._measured_cop.cop is None`; and assert the since-fix payload round-trips its `measured_cop`. Failing test first. Then re-kill the reviewer's mutant G (replace coordinator.py's `MeasuredCop.from_dict(stored.get("measured_cop") if _COP_BASELINE_KEY in stored else None)` with the ungated `MeasuredCop.from_dict(stored.get("measured_cop"))`: the new assertion must go red) and show the null control (unmutated head green). Re-run prepr.sh to a clean head (MUTANT_CMD per the mutants ruling), `tools/audit/seat/handoff_push.sh`, then re-take the whole body from .github/PULL_REQUEST_TEMPLATE.md starting from the kept body (`## Head` at the new head, every figure re-taken, `## Red checks` naming every concluded red by literal check-run name), `tools/pr/prepr.sh --body-check`, `carry_audit.py check`, and `bash tools/audit/seat/body_push.sh r10-hotfix-cop-unmeasured <body>`.
ROSTER PINS: this group's brief on the roster carries coordinator.py line pins (they broke the roster gate tonight). If your fix shifts coordinator.py lines, re-pin the brief's anchors in the body's roster ops: write the ops (append-carry or the group's re-pin op as the instruments print them) in a file BLOCKED-carry.txt on handoff-wip/r10-hotfix-cop-unmeasured-carry (parentless commit) and say so in your status line; the dispatcher queues them. If body_push.sh refuses, STOP and quote the exact refusal line in BLOCKED.md on handoff-wip/r10-hotfix-cop-unmeasured.

THE BLOCKED VERDICT:
Fix review: blocked 9cf0b6108527943795f1b4dda6e6069ebff0e7f7 mutation-vacuous: coordinator.py:4575 measured_cop provenance gate survives every check

bus-nonce: 48cc398fd1089ad881e7f6546ed55939

## Block

Round 1. Head measured: 9cf0b6108527943795f1b4dda6e6069ebff0e7f7, still the head of `fix/r10-hotfix-cop-unmeasured` when this verdict was written.

The body's item 5 says "A pre-fix store's last COP is not shown as measured either". The production line that does this is `coordinator.py:4575`, `MeasuredCop.from_dict(stored.get("measured_cop") if _COP_BASELINE_KEY in stored else None)`. I replaced it with the ungated `MeasuredCop.from_dict(stored.get("measured_cop"))` (mutant G). The result:

- `tests/features.py` rc=0, ALL 4912 FEATURE CHECKS PASSED.
- `tests/entities.py` rc=1 with 3 of 2645 ENTITY CHECKS FAILED, the same three environment failures the unmutated head prints (coverage-job reuse, release ZIP, Pages workflow).

Nothing kills the mutant. The migration check ("a COP baseline stored before measured provenance loads empty ...") loads a pre-fix payload that holds `cop_baseline` and `cop_health_cusum` but no `measured_cop`, so this gate is never exercised.

The gate carries weight on the owner's own install. Without it, the pre-fix `measured_cop` (a model value: 2.55 on the null-control fixture) loads back after the upgrade, with its old `at`. Two surfaces then read it:

- Diagnostics `cop_learner.measured_cop` (`accuracy.diagnostics_view`) reports it as measured.
- The card's Health COP row appends "Measured {age} ago." from `measured_cop_at`, right under the new "COP cannot be measured on this install" text.

This is the "do not report a model value as measured" requirement of brief items (2) and (5) and carry (a). The ObservedCOPSensor masks it only because it is unavailable while `waiting_for` names a reason.

Cure, small, and inside this group:
- Add a `measured_cop` record to `_cu_old_payload` in the R10-HOTFIX-COP-UNMEASURED section.
- Assert `_cu_old._measured_cop.cop is None`, and that the since-fix payload round-trips its `measured_cop`.
- Re-run the mutation proof on 4575.

Every other part of the review passes; see Evidence.

## Findings

- When a heat counter is configured, `probe_install` forces `heat_estimated` and `power_estimated` to False, and nothing ever inspects the electric counter (`CONF_ENERGY_ENTITY`) or the heat counter (`CONF_HEAT_ENERGY_ENTITY`) for an estimate: there is no source option for either, and `auto`'s id rule never reads their ids. A Riemann-sum counter integrated from the Tuya "Estimated Power Draw" or "Estimated Heating Output" therefore still records a measured COP through the span route (`heat_energy.close_span` -> `_fold_cop_evidence`), and that COP is the vendor's own fitted COP. This is carry (d)'s "an estimated input on EITHER side", reached through the counter pair. The body discloses that a heat counter "is read as metered" but gives no reason. The owner's install has both counters unset, so this does not reach the owner today. It is not the cause of the block. Carry: R10-COP-GATE-E
- `codeql / Analyze (python)` in run 42406301156 was cancelled at 20:19:32Z, about 45 minutes after it started at 19:34:32Z, in mid-evaluation ("The operation was canceled"). The same analysis passed in run 42406296114 (job 128552885531). It is a runner-time stall, not this diff, and it is one of the two reasons `gate` stays red. Carry: R10-HOTFIX-CODEQL-HEADROOM
- The finding has no committed finder's harness. The packet reads "Finder's harness: none named", so the brief's null control is the harness, and the fixer implemented it as the first two checks of the tests/features.py R10-HOTFIX-COP-UNMEASURED section. I transplanted that section onto the merge base myself and it reproduces the defect there (Evidence). Carry: dismissed: brief null control now committed as features.py checks

## Evidence

- Merge base aaaec2128e5d2efc2e0ad8ffe4918eec6cbb7f98. `git diff aaaec212...origin/main -- dev/governance/roles/` touches fix-review.md only, and the current main copy is the one I read and followed.
- Merge: `git merge-tree --write-tree origin/main 9cf0b610` exits 0 against origin/main 7c9c4c154 (tree 7fc7b5240). No conflict (ev/merge_tree.txt).
- RESULT head tests/features.py rc=0 ALL 4912 FEATURE CHECKS PASSED (7m14s). This is the null for every mutant below.
- RESULT null-control base: I transplanted the head's section (head lines 69695-71882) into base tests/features.py, before "early cut-off".
  - No heat slot, a DHW interval with ask == reading: the base records `{(2, True): [2.5533587538536424, 1]}` and measured COP 2.55, equal to compute_cop_dhw(8, 48). The head records `{}` and None, and the scale still takes 1 sample.
  - Tuya fixture: observed [3.1, 2.4, 4.05] equals the fitted COP fed in; the base records band `{(2, False): [3.1833..., 3]}`; the head records nothing.
  - The base then raises AttributeError on `cop_measured`.
  - This matches the body's `## Null control` (ev/null_control_base.txt).
- Mutation proof, each mutant on a fresh worktree at the head, whole tests/features.py (ev/mutants.txt, ev/mutant_detail.txt, ev/mutants_def.py):
  - A `if measured:` -> `if True:`: rc=1, 3 failed (the null control, the Tuya check and the metered-records check), as body M1.
  - B cop_sample `return None if ... else False` -> `return False`: rc=1, 1 failed (no-heat-reading refusal), as M3.
  - C `_estimated` id rule -> `return False`: rc=1, 3 failed, as M4.
  - D `not (heat_estimated or power_estimated)` -> `not heat_estimated` (power side ignored): rc=1, 1 failed (probe_install either-side check).
  - E -> `not power_estimated` (heat side ignored): rc=1, 2 failed.
  - F loader also reads the pre-fix `cop_baseline`: rc=1, 1 failed (migration), as M5.
  - G measured_cop load ungated: rc=0, SURVIVES; it also survives tests/entities.py. This is the block.
  - H `machine_score`'s `if not measurable` deleted: rc=1, 1 failed, as M6.
  - I `heat_sees_dhw or not dhw` deleted: rc=1, 1 failed, as M7.
  - J CUSUM loader also reads the pre-fix `cop_health_cusum`: rc=1, 1 failed.
  - K `COP_ESTIMATED if estimated else COP_HEAT_METERED` -> `COP_HEAT_METERED`: rc=1, 2 failed.
  - L power_estimated no longer outranked by a heat counter: rc=1, 1 failed.
- Class rule, re-run at the head: `git grep -n -e "_measured_cop.record(" -e "_observe_cop_health(" -- custom_components` returns exactly coordinator.py:5400-5401, inside `if measured:`. The direct `_cop_baseline[...]` writes are the loader (4590) and `_observe_cop_health` (9496). `_fold_cop_evidence`'s callers are the per-cycle fold (5352) and the span close (1163). The rule is sound for the writers.
- Architecture score: `python3 tools/audit/archscore/score.py --diff aaaec212 HEAD` prints `Architecture score: dS -0.0023 WORSENS (inadmissible: coord_footprint 2491->2495)`, matching the body (ev/archscore.txt). I did not decompose the +4 statement by statement.
- My judgement on the +4: it is justified. The decision is pure and lives on `InstallCapability.cop_measured` / `cop_sample` in thermal_model.py, and the coordinator only branches on its answer at the three points it already owned. I hunted for a payment inside the seam and found none that is sound:
  - Pushing the guard into `_observe_cop_health` stays inside the class and couples the health watch to the install.
  - Folding the refusal earlier would recompute `heat_kw` and the reference curve.
  - Having `machine_score` read config adds an edge `fixer.md` step 17 refuses.
  - The only larger lever I saw, moving `machine_score` out of coordinator.py, is an unrelated move and out of seam for a hotfix.
- No `*_budgets.json` is in the three-dot diff, and VERSION, the manifest and RELEASE_NOTES.md are untouched (VERSION 7.1.5 on both sides). `dev/programme/delivery/3297.md` is in the diff. The only new tracked files are that row and mutation-ledger pins, and `tests / closures` and `tests / closure-scope` are green.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, rc=0.
- `python3 tests/env_drift.py --all aaaec212`: NO UNCLAIMED DRIFT over 56 scenarios, NO STALE FIXTURE over 56 fixtures. The six claims (coord_* x5, config_flow) carry `claims-for: 7.1.5` = VERSION.
- `node tests/card_drift.mjs aaaec212` (after tests/plan_view.py): 1 state moved and claimed (score_open), 44 identical, matching the body. The tool prints "CLAIMED score_open -- no reason given" because the reason sits in comment lines above the name rather than inline. This is cosmetic, and rc=0. Carry: dismissed: evidence, not a finding
- `tests/entities.py` at the head: 3 of 2645 ENTITY CHECKS FAILED, the three environment checks the body names (ev/entities_head.txt).
- `## Head` names 9cf0b6108, the head I measured.
- Owner's ruling: it is quoted verbatim in the body, and no learner is gated. Mutant B's null arm and the Tuya check (3 scale samples) pin the retained scale training.
- CI, read job by job over all 95 check runs at the head:
  - `merge_train.py classify` exits 1 on every run from 22:50Z to 23:27Z+: `RED ... pending: none red: gate` (ev/classify.txt).
  - Both of gate's latest runs (job 128552885487 at 22:49Z, job 128551986658 at 22:44Z) print `FAIL codeql / Analyze (python): cancelled (run 42406301156)` and `pr-contract / pr-contract: failure (run 42406301156)`.
  - The pr-contract failure is the 20:19Z run, which predates the body repair. The later pr-contract run (job 128552885967, 22:40:55Z) is success, and the arch-score rerun is success. gate still reads run 42406301156.
  - Re-running that run's pr-contract and codeql/python jobs would clear it with no code change.
  - The body's `## Red checks` names gate, pr-contract, arch-score and the codeql cancellation, so step 11 is answered.
  - The block above stands on its own, independent of CI.

bus: verdict/3297 at a5a62c10db3effab150326a5dd3f3b7c0ecbd96f, confirmed from cloud-opus (review/3297 at 9345dd49798ad5d574cd8c4f5111b12de6b7a13e); evidence: ~/.zcode/bus/verdicts/3297/a5a62c10db3effab150326a5dd3f3b7c0ecbd96f/evidence


Before any commit run: export GIT_AUTHOR_NAME=hpo-fixer GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=hpo-fixer GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com, and also git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com. The cloud environment exports GIT_AUTHOR_*/GIT_COMMITTER_* as 'seat', and those environment variables beat git config, so the config alone does not hold. Never commit as 'seat'; check with git log -1 --format='%an %ae %cn %ce' after the first commit.


Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.


TIME: you have hours, not minutes. A gate, prepr or recording may run an hour: wait with Monitor windows of up to 60 min and re-arm them. Never end the session waiting on a choice: take the option that keeps coverage and the architecture sound, say so in the body, and go on. Push handoff-wip at each milestone, so your liveness can be read. If truly blocked, push BLOCKED.md on handoff-wip naming the question.
