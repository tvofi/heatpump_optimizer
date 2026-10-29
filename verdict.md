Fix review: blocked d26a00aa259136d652ffe19066145a4e1acc97e9 mutation-vacuous: step_supply boost, sysid and non-plan-mode guards, supply_tick entry_released guard and release's release_supply survive deletion

bus-nonce: d8583904af17eafd76803076ae5d2bfa

## Block

Round 1 of review. The new step tick is a second actuator of the supply switch, firing between cycles. Its guards exist so that it does not override a command the plan did not give. Deleting any one of them leaves every check green. This head's checks pin the tick only in auto mode, with no boost, no experiment and a fresh plan.

Each mutant ran in a fresh detached worktree of d26a00aa2 (driver: `ev/mutant_driver.py`, one `str.replace` asserted to match exactly once). The unmutated null passes everything (`ALL 4581 FEATURE CHECKS PASSED`, `ev/full_NULL.txt`). Each mutant below also leaves `tests/features.py` fully green: its single red was `recorded_at = 'unknown'`, from a non-git copy in the first drive, and the null in a real worktree is clean. Each also leaves green `block_duty.py`, `boost_drift_replay.py`, `guard_pins.py`, `manual_plan.py`, `debug_collect.py`, `deployment_shape.py` and `finite_boundary.py` (`ev/closure_*.txt`, `ev/full_X*.txt`):

- X1 `pump_arbiter.py:1192` (step_supply: a live boost is on), with the branch body deleted. Path: the user presses boost on a step the plan keeps off, and at the next boundary whose plan command is off the tick writes OFF under a live boost.
- X2 `pump_arbiter.py:1190` (step_supply: a `system_identification` action returns None), deleted. Path: a step-response experiment's switch command is overwritten by the plan's at the first boundary where they differ.
- X3 `pump_arbiter.py:1188` (non-plan mode or stale plan returns None), narrowed to `inp.plan is None`. Path: comfort/boost/off modes, or a plan `_apply_action` refuses to actuate as stale, get the plan's switch written by the tick.
- X4 `pump_arbiter.py:1246` (`supply_tick`: `if inp.entry_released: return`), deleted. Path: a write after unload (#237 class).
- X5 `pump_arbiter.py:1279` (`release`: `release_supply(held)`), deleted. Path: the tick's interval listener outlives unload.

`grep -n 'supply_tick|step_supply|note_supply|release_supply|SupplyWiring|supply_write' tests/` finds no test reaching them, apart from one barrier reason string in `tests/entities.py`. The body's `## Unpinned sites` lists 1188/1190/1192/1246 GUARD_OFF (and others) as "pinned by `mutation-autofix`". That lane pins only killed mutants, and these survive, so the claim does not hold. They will surface as survivors, which `ci-autofix.md` forbids triaging automatically.

What would clear it: checks in the "supply switch at step boundaries" section, each a red under its mutant above:
- a live boost across a boundary whose plan step is off writes no OFF;
- a `system_identification` action is not overwritten at a boundary;
- a fixed mode, and a stale plan, write nothing between cycles;
- a released entry writes nothing;
- unload drops the tick.

Then re-run M1–M6 and these mutants.

## Findings

- No committed finder harness for carry 5 seam 2. The roster's carry (main `dev/programme/rosters/wave-r10-groups.json`, group R10-SAV-ACTUATION) states the control in words: phase 0 vs 14 min with identical duty verdicts, plus one mutant per seam, and names no instrument. `dev/audit/harnesses/r10_sav_actuation_phase.py` is the fixer's own, and the body calls it "the owner's instrument for this carry" rather than disclosing it as the fixer's build (fix-review step 9). I ran it unchanged, sha1 d8871c1b96466f7d0d16df9ecc15454512d6adc5, at both ends: `AGREE: yes` at d26a00aa2, `AGREE: no` at 88c6ad5bb (`ev/harness_both_ends.txt`). It implements the roster's words faithfully; the body's wording should say it is the fixer's build when the branch is next touched. Carry: dismissed: the control is the roster's own text, the instrument lands in the tree and reproduces at both ends
- The ledger residue the body forward-carries is real and is the larger part of the remaining misbooking. At the head the harness books every idle step that follows an ON step `space-instead`, at both phases: steps 1, 4, 7, 9 and 14 of `s-ss--s-s---ss-s`, so 5 of 16 verdicts are wrong. The base books 10 of 16 wrong at phase 0. The fix improves this but does not close it; the residue is phase-independent, so carry 5's control holds. Carry: #2492
- `coordinator.py` `_write_supply`'s `elif switch_entity:` GUARD_OFF survivor only logs. I agree it is equivalent in behaviour, but the body leaves the `survivor_triage` disposition to the reviewer, and it needs a recorded verdict rather than an implicit one. Carry: R10-SAV-ACTUATION

## Evidence

- Head reviewed: d26a00aa259136d652ffe19066145a4e1acc97e9 (`ev/HEAD.txt`). Still the PR head at 23:19 UTC (`git ls-remote`). Merge base e5ddba1fa equals origin/main; the code head is 3e9763e8a on 88c6ad5bb.
- Roles diff `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/`: empty, so the contract is current.
- Review packet rendered: no refusals, no advisories; carry_audit 2 items, both routed; figure_lint 8 resolved, 2 not verified (the two `git grep` figures, which I re-ran: `ev/greps.txt` matches the body's census).
- Mutation proof M1–M6 re-run on the standalone copy of the section (`ev/section_standalone.py`, lines 73104–73227 of `tests/features.py` with its preamble; `ev/mutants_section.txt`). Every one is red on exactly the checks the body names: M1, M2 and M6 fail 2 of 4 (phase agreement and boundary writes); M3 fails 2 (boundary writes and cut-off hold); M4 fails 1 (phase agreement); M5 fails 1 (`['written/silent/0']`). Unmutated: 4 of 4 pass. Per the roster, the coordinator, tick and ledger-read seams each turn control (a) red (M1, M2/M6, M4). The early_cutoff seam is unchanged in code apart from a docstring; its guard is M3 on the change-only rule.
- More mutants on the section only (`ev/mutants_extra_section.txt`): X6 (tick body not awaited) is red. X7 (cut-off `allow_on` bypassed in `_write_supply`), X8 (blocked-mode OFF skip forced) and X9 (step past `power_schedule`) are green on the section. X7 and X8 are code moved from `_apply_action`, whose earlier pins features.py killed, and were not re-driven on the full suite here. Only X1–X5 under `## Block` were run against the full closure scripts.
- Null control and the both-ends harness: as under Findings. Base phase-0 writes land only at cycles; head writes land at boundaries.
- Possible tick refusal of ON under `early_cutoff.MIN_OFF` with a stale record: checked and not reachable. An OFF step lasts 15 min and `MIN_OFF` is 10 min, so the tick's next ON boundary always falls after the hold.
- `git merge-tree --write-tree origin/main HEAD`: exit 0, tree fe5b6f600e19 (`ev/merge_tree.txt`).
- VERSION, manifest, RELEASE_NOTES.md and both claim files untouched three-dot (`ev/version_untouched.txt`). `env_drift.py --all`: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56` (`ev/env_drift.txt`).
- Structure: `STRUCTURE RATCHET PASSED`. The budget diff only lowers `class_excess_loc` 17814→17801 and `max_class_loc` 8155→8153, earned by `supply_write` leaving the coordinator class and the inline `get_current_action` rule becoming `plan_step_runs` (`ev/structure.txt`). Archscore `--diff 88c6ad5bb HEAD`: `dS +0.0000 NULL` (`ev/archscore.txt`). I did not re-derive the body's quoted first-cut `coord_footprint 2409->2430`.
- CI on d26a00aa2 at 23:19 UTC from the check-runs API: fast (3.14), closures, coverage, coverage-ratchet, typing, briefs, policy-docs, instrument-self-tests, env-matrix, arch-score, arch-instrument, replay, browser, lane-proofs, wave-script, delivery-status, closure-scope, hassfest, validate-hacs and budget-raise-gate are green. `mutation` is red, answered in the body as red by construction on the unpinned sites. `nightly-status` is red; it is main-graded and the diff touches neither `nightly.yml` nor `tests/nightly_status.py`. `mutation-pins (1)` and `(4)` were still in progress (2, 3, 5 green). codeql python was cancelled; it is not a required check and does not block. No `pr-contract` run is listed on this head.
- Body figures I could not re-derive: the local mutation drive's "30 mutants, 4 killed, 25 not started, 1 survived" at 3bc559015 (not re-run; heavy), and the 484 s features.py timing.
- Interpreter: /opt/hpo/venv-ci/bin/python (CPython 3.14.7; numpy 2.4.6, scipy 1.17.1, voluptuous 0.16.0, matching `tests/requirements-ci.txt`).
