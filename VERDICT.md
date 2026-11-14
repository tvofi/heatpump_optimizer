Fix review: merge ec9645014c773759edfbf632829c7cbef272ba33

bus-nonce: bf8628d0f6e87675ed41eb8794f48f77
pending-ci: gate

## Round

First round, full review (no earlier reviewed head). Measured head: ec9645014c773759edfbf632829c7cbef272ba33, the PR head when read at 03:45Z and again before this verdict. Merge base and origin/main: 513a07dfdc0daf09a054826974dbb64bfea9de27. Role contracts are current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main ec96450` exits 0 with tree 6b4d495cbd and no conflict (ev/merge-tree.txt). The head also merges cleanly with #3563's head and with part 1's branch (fix/r10-docs-strings-residue).
- RESULT mutation (step 1): the fixer's seven mutants M1 to M7 were re-run at this head, each as one exact replacement that was then restored, and `git diff --quiet` passed afterwards. All seven are killed: M1 1 FAILED (solve_bands leaves target_temp), M2 1 FAILED (ECONOMY_ABSOLUTE_FLOOR), M3 1 FAILED (fuse_kw None at 0 A), M4 1 FAILED (production[0] anchor), M5 4 FAILED (DeviceInfo anchor plus the three fixed-device-name checks), M6 1 FAILED (spot + fee_per_kwh anchor), M7 2 FAILED (_ADVISOR_DUTY_FRACTION plus the dashboard-card replay sentence). No mutant survived (ev/mutants-M1-M6.log, ev/mutant-M7.log). M4, M5 and M6 are source-text anchors, so they would also fire on an equivalent rewrite. They fail closed and are not vacuous.
- RESULT old-text pin: with the merge base's `custom_components` and `docs` checked out over the head, `tests/doc_claims.py` prints `14 of 380 checks FAILED`, the body's figure re-derived (ev/old-text-pin.log). Restored: `ALL 380 checks PASSED`.
- RESULT null controls (step 3): the seven old-wording null controls and the de grid-title null control pass inside the arm (ev/doc_claims-structure.log).
- RESULT census: I re-derived it with my own script over `.options.step` menu_options and titles. At the base, de mismatches `grid`, `modbus_prefill`, `thermal_model` and `solar_pv`, and strings, en and sv have none. At the head, none of the four files has a mismatch. Each file compares 25 pairs, which matches the body's figure.
- RESULT class enumeration (step 6): I ran the body's `git grep` rule at this head. The remaining hits are card JS (`health.learn_savings_why`, `advisor.basis_*`, `receipt.covers`) and tests/card.mjs, which are dispositioned to #3563. I confirmed #3563's head diff rewrites all three keys in en, sv and de. The other hit is topology.py:1220, a comment the body dismisses. No undispositioned seam.
- RESULT code facts behind the sentences, read at the head:
  - Carry 5: `_floor_widening` gates on `_vent_cusum.tripped and open_window_relax_enabled`, and away.py:400 applies `max(ECONOMY_ABSOLUTE_FLOOR, min_temp - by)`.
  - Carry 6: `fuse_kw` is None at 0 A (entry_config.py:266). The fuse guard (coordinator.py:6299) and the fuse advisor (coordinator.py:8969) both return early on None. `_power_headroom` matches the description.
  - Carry 7: coordinator.py:9839.
  - Carry 8: `name="Heat Pump Optimizer"` (coordinator.py:4214), `_attr_has_entity_name = True` (entity.py:204), and CONF_NAME is used only as the title (config_flow.py:2841, 2896).
  - Carry 9: ledger.py:333.
  - Carry 10: `_ADVISOR_DUTY_FRACTION: Final = 0.5`.
- RESULT part 1's production change: away.py drops the `AwayConfig.legionella_before_return` field. `git grep legionella_before_return` finds no reader at the base outside dev/, and none at the head, so it was a dead field.
- RESULT figures at this head (ev/doc_claims-structure.log, ev/entities-envdrift.log):
  - `tests/doc_claims.py`: `ALL 380 checks PASSED`.
  - `tests/entities.py`: `ALL 2713 ENTITY CHECKS PASSED`. The body's 2711 was measured at the authored head 3047b48a before main was merged in, so the two counts do not contradict each other.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `env_drift.py --all 513a07dfdc`: `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`.
- RESULT step 5: VERSION, manifest.json, RELEASE_NOTES.md and both claim files are untouched in the three-dot diff.
- RESULT figures not re-derived: the scoped-gate line `MODE: SCOPED -- 23 script(s) run, 10 scoped out` and the env_drift-against-origin/main `DRIFT config_flow` account are CI's heavy runs and were not re-run (fix-review.md 11). The base-side carry-12 PNG `cmp` measurement was not re-derived either: this seat has no recording host.
- RESULT forward-carry (step 10): carry 12 item a0e752f6 is present in `dev/programme/rosters/wave-r10-groups.json` on handoff/audit-r10-roster, group R11-INTAKE-R10-RESIDUE. It states its re-measure (`cmp` of a `card_browser.mjs` render against the committed PNGs).
- RESULT red checks (step 11): the body says `## Red checks: none`. classify reported `gate red: none` throughout the wait. CI at this head: `merge_train.py classify` was polled every ~60 s from 03:45Z to 04:16Z and printed `WAIT ec9645014c773759edfbf632829c7cbef272ba33 pending: gate red: none` (rc 3) every time (ev/classify.log). This merge verdict is therefore returned with `pending-ci: gate`. The head was re-read at 04:16Z and is unchanged.

## Findings

- Follow-up: this PR's three-dot diff includes part 1's commit c79e44e2 (away.py, the four string files, configuration.md, how-it-works.md, carries 0 to 4). Part 1 is PR #3576, which is open and has no review yet. This verdict reviewed part 1's production change (the dead-field removal above) but did not verify the text of carries 0 to 4 against the code; that is #3576's review. Merging #3580 first would land part 1 without its own verdict, so #3580 should follow #3576's merge verdict in the train (a split part of this group). Carry: R10-DOCS-STRINGS-RESIDUE
- Residual: carry 6's corrected sentence says the headroom sensor is "unavailable without a capacity tariff". `_power_headroom` also returns `{"available": False}` when a capacity tariff exists but does not bill the current window (`sample_factor` 0). The sentence omits that case but states nothing false. Carry: dismissed: an omission of the unbilled-window case, not a false statement; the corrected sentence is true of every case it names

## Friction

none
