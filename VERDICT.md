Fix review: blocked a390f5895eb14fd6bc624ca6d3c9f28aa00410a2 root-cause-unanswered: typing went red at the head (mypy errors 0 -> 9 in coordinator.py, binary_sensor.py, entry_config.py; green on main e0f0b6fb), unanswered; mutation and closures also red and unnamed

bus-nonce: efb07491398890f55b4d338c7e98c139

Reviewer seat r9c-rev-2025, round 1. Detached worktree /Users/timmalmstrom/hpo-seats/r9c-rev-2025 at the head; merge base e0f0b6fb (= origin/main at review time; `git merge-tree --write-tree origin/main HEAD` exit 0). `tools/audit/briefs/` was unchanged between the merge base and main. Live head re-read at posting: a390f589, unchanged.

## Blocking: three reds at the head that `## Red checks` does not answer

The body's `## Red checks` names only the local features R9-F2.1 P3. Its account of the CI run 37640455476 is "none are cited here". That run is the dispatch at the code head 5947316c, not this head. The PR's own run is 37647008756 (pull_request, a390f589). Its check-runs, read through the commit's check-runs API, are in `checkruns_head_at_post.tsv`:

1. **typing: failure** (job 112880876862). The ruler reports `FAIL errors did not grow [recorded 0, measured 9 (+9)]`, made up of arg-type +3 and no-any-return +6. By module: coordinator.py 7, binary_sensor.py 1, entry_config.py 1. Main's typing at e0f0b6fb is success, so this red belongs to the PR. The body's local "`tests/typing_ruler.py`: ALL 11" ran without `--mypy`, so it measured nothing here. This is a real ratchet failure in the fix, not only an unanswered trigger.
2. **mutation: failure** (job 112880877079). `MUTATION TABLE REFUSED`: 4734 unpinned sites against 4693 at the base, 55 of them added by this diff. Then: "nothing was measured: 0 mutant(s) timed out, 55 not started for --budget-minutes". mutation-autofix reported `skip-no-measurement -- THE REPAIR DID NOT HAPPEN`. The diff also deletes 9 `killed_by` ledger pins. For the 2 `apply_config_keys` pins the code is gone. The other 7 are not re-earned at this head.
3. **closures: failure** (job 112881062368). `UNDER-SCOPED: ... really reads custom_components/heatpump_optimizer/entry_config.py` for backtest, block_duty, boost_drift_replay, card, card_drift, config_flow_steps, doc_claims, edge, entities, features, finite_boundary, harness_headers, manual_plan, optimality, plan_view and more. closures-autofix (job 112897209809) reported `skip-failed-recording -- THE REPAIR DID NOT HAPPEN`, because a recorded script exited non-zero. So no bot commit is coming. The fixer hand-added entry_config.py to only 5 of the 20 closures that contain coordinator.py. Reproduced locally: `closure.py select --files custom_components/heatpump_optimizer/entry_config.py` SKIPs entities.py, features.py, typing_ruler.py and structure.py (`select_entry_config_only.txt`). As committed, a later change to entry_config.py alone would run none of them.

Not this PR's: `delivery-status` is red because #2003 and #2001 are OVERDUE on main, and the diff only adds the row for 2025. `nightly-status` is red, and the diff does not reach what it reads.

Still in progress at posting: `fast (3.14)` (the lane carrying features, golden and stress) and `coverage`. No heavy result is cited as green, because none exists yet at this head.

## Point by point

1. **Raw reads in migrated modules: verified, none.** I built my own scan (`scan_attrs.py`, the reviewer's instrument, not the finder's). It looks at attribute reads on `_config`/`effective_config`/`entry_config` that are not EntryConfig fields, and at `.get()`/subscript reads on those holders, in the 12 `_EC_MIGRATED` modules. RESULT head: ATTR-NOT-A-FIELD 0, HOLDER-MAPPING-READS 0, UNDEFINED {}. Null control: the same scan over main's package (with entry_config.py copied in) gives HOLDER-MAPPING-READS 115. Writes into the frozen object: none in the package at head. The only `_config.update` is the harness fallback in `solve_inputs_parity.py` for a base tree. The remaining `{**entry.data, **entry.options}` reads in coordinator.py are construction (2445), `target_temperature` (3150, the same live-entry read main makes), and the two options writes. Residual mapping readers (quiet_windows, thermal_model and the others) are disclosed in `_EC_RESIDUAL`. Note that `quiet_windows.silent_cap_kw` still reads `silent_mode_power_fraction` raw, while `silent_mode.compose` takes the parsed field. For a stored "nan" the two disagree, so this is a disclosed residual, not a stray.
2. **Three new fields: present and parsed.** `heat_pump_capacity_limited_entity` (entity slot), and `quiet_silent_windows` / `quiet_off_windows` (`_spec`, "" when blank or None). They are pinned by entities.py's new check (mutants M4 and M5 killed).
3. **model_restart_advice (#1936): works.** It reads `ctx._config.optimization_interval`. I ran `tools/audit/harnesses/scale_writer_seams.py` at the head and at main. Every value RESULT line is identical (only seam line numbers move), including `accept_admitted_offer=1.96`, `accept_admitted_applied=true` and `accept_matches_offer=true`, with the drift alarm raised so the refit line executes. The undefined-name scan prints {} at the head.
4. **apply_config_keys removal: a USER-VISIBLE BEHAVIOUR CHANGE. The owner (tvofi) must accept it; it is not equivalent.** I drove it with my own driver (`quiet_reload_driver.py`): a quiet-only `async_update_thermal_params({"quiet_off_windows": "09:00-09:30", "silent_mode_power_fraction": 0.8})`, then `async_update_options`, then a coordinator rebuilt from the entry.
   - main: `live_spec='09:00-09:30' live_off_steps=2 live_fraction=0.8 reloaded=0`
   - head: `live_spec='' live_off_steps=0 live_fraction=None reloaded=1`, then `rebuilt_spec='09:00-09:30' rebuilt_off_steps=2 rebuilt_fraction=0.8`
   - null (empty call): reloaded=0 and no spec, at both ends.

   The end state is the same, because the keys take effect after the reload. The transition is not. On main, the card's quiet-window editor saves through `set_thermal_parameters` (`quietServiceFields` always sends both specs plus the fraction) and in steady state applied live with no reload. Under this head every such save reloads the whole integration. Entities blink, the plan is republished from handover, and a cold solve runs. DHW-window saves already reload on main, so this makes quiet windows behave like them. The body discloses the change. The decision belongs to the orchestrator under the owner's mandate.

   SW-1's re-pinned check (features.py) proves three things: the options write, `effective_config != merged` (the listener's reload condition), and the parse of the merged mapping. It does not drive the listener or rebuild a coordinator. My driver covers that gap and confirms that the keys reach `compose` after the reload.
5. **Structure budgets: confirmed lower, no raise.** max_class_loc 9104 -> 8880 and seam_cut_total 766 -> 765 in `structure_budgets.json`. `structure.py` at the head: `STRUCTURE RATCHET PASSED`, duplication_copies 38 <= 38, max_class_loc 8880 <= 8880. The reduction is earned: about 300 coordinator lines of `.get`/coercion moved into entry_config.py, and the reason is in commit 8c04fcd7. I did not re-derive the body's "39 before" for duplication_copies.
6. **Counts: confirmed.** There are 72 `.py` files at the head and 71 at main. Package files are 90 at the head and 89 at main, which matches deployment_shape's 90. "26 of 72 import homeassistant / 45 free" is consistent, since entry_config imports no HA.

## Mutation proof (the reviewer's own, run against entities.py; M1 and M7 also against config_flow_steps.py)

The mutants are applied in place to entry_config.py by `mutate.py` and restored with `git checkout`. The tree was clean afterwards.

- M0 null (a comment): entities PASS.
- M1 `_number` accepts non-finite (finite check removed): **SURVIVED** entities.py (ALL 2209) and config_flow_steps.py (ALL 496).
- M2 `_number` returns the unparsable stored value: KILLED (TypeError).
- M3 `_refused_number` never returns None: KILLED (1 failed).
- M4 `_spec` unguarded, so None becomes "None": KILLED (1 failed).
- M5 `_entity` unguarded: KILLED (16 failed).
- M6 `from_mapping` stores raw: KILLED (3 failed).
- M7 `_nonzero_number` lets 0 through (dhw_tank_volume): **SURVIVED** entities.py and config_flow_steps.py.
- M8 `_whole` without its except: KILLED (TypeError).

Refused text and None specs are pinned. A refused NaN or inf (M1) and a zero tank volume (M7) are not pinned by the cheap scripts. features.py might kill them, but CI's mutation lane measured nothing at this head, so that is unverified.

## Other

- Step 7: the body names the head a390f589, and it is the head I measured. The body's figures were taken at 5947316c with merge base 38c03d94. The body says so, but every local figure predates the merge of e0f0b6fb.
- VERSION, the manifest version and the RELEASE_NOTES heading: untouched (not in the diff stat).
- Forward-carry: "none" with residuals named in `_EC_RESIDUAL`. Nothing contradicts that.

## What the fixer owes (fixer.md; the original fixer seat)

1. Fix the 9 mypy errors.
2. Fix the closures under-scope, which the autofix will not repair while a recording fails.
3. Get the mutation lane to measure, or disposition the 55 new sites.
4. Pin M1 and M7, or show the kill.
5. Answer every red in `## Red checks`.

The quiet-window reload change needs the owner's acceptance whatever the fixer does.

Evidence: /Users/timmalmstrom/hpo-seats/r9c-rev-2025-ev (HEAD.txt, checkruns_head_at_post.tsv, joblog_*.txt, scan_head.txt, quiet_reload.txt, scale_seams_{head,base}.txt, mutation_entities.txt, mutation_cfs.txt, entities_*.txt, structure_head.txt, select_entry_config_only.txt, and the reviewer-built scan_attrs.py, quiet_reload_driver.py and mutate.py).
