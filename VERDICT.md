Fix review: blocked a258212553e123d735c7eff139a8e347a1a52ea3 ci-red: required gate concluded failure at this head, three edit-run gates deferring to one another

bus-nonce: 76f26679dddd96f7ff72917aa9f3d039

## Block

Round 3 of the fix review of #3244 (R10-HOTFIX-SAV-ESTIMATE part 2, topic r10-sav-wood-heat), at head a258212553e123d735c7eff139a8e347a1a52ea3.

`python3 tools/audit/seat/merge_train.py classify a258212553e123d735c7eff139a8e347a1a52ea3 --pr 3244` prints `RED a258212553e123d735c7eff139a8e347a1a52ea3 pending: none red: gate` (rc 1), and printed the same on every run of this session (`ev/classify_2.txt`, `ev/classify_3.txt`, `ev/classify_final.txt`). A red CI never carries, so this head cannot take `merge`.

The red is not the diff's. The code run 42286556863 passed its `gate` (job 128172572226, success 21:45:53Z) after its CodeQL python rerun went green. Then all three edit runs' gates were re-run inside 2 s of one another: 42286558101 (job 128173052224), 42286624031 (job 128173059639) and 42293328283 (job 128173073456). Each listed the other two as busy and failed at once with `FAIL run(s) [...] at this head are still being judged; their gate decides`, because `deferring()` sets bound 0 (`ev/ci_gate_reds.txt`). That is the liveness defect `R10-HOTFIX-GATE-BUSY-DEFER` already owns (tools/ci/gate.py `busy()`). Nothing re-judges the head without a new trigger: `gate-sweep.yml` runs only on `workflow_run`.

Unblock: re-run one edit run's `gate` alone (not all three at once), or push a new body event, then re-classify. Every code finding below supports `merge` on a GREEN re-judge of this same head, so a re-dispatch can confirm CI and carry this review (`review_carry.py`).

Step 11 (red-check answer) is not judged. The head's last `pr-contract` run started at 21:44:07Z, before the 21:46Z reds, so the rule's precondition does not hold. The body's `## Red checks` was written at 21:05Z and does not name these three reds.

## Findings

- Follow-up: three edit-run `gate` jobs re-run together at one head each defer to the other two and all fail; no gate judges the head (#3244 at a258212553e1, 2026-11-06 21:46Z, the third case after #3239's pair). Carry: R10-HOTFIX-GATE-BUSY-DEFER
- Follow-up: the card mutant `const wood = !!(fuel && fuel.show_whatif)` → `!!fuel` (a note on a house where wood is present but not configured) survives `tests/card.mjs` and dies only in `tests/card_browser.mjs` (`a house with no wood configured carries none`). The scoped gate selects no `card_browser`; only CI's `tests / browser` lane runs it, so a local scoped run cannot see that mutant. This is the body's M5 pattern on the other leg. It is covered in CI, so this is not a block. Carry: R10-HOTFIX-SAV-ESTIMATE | dismissed: covered by the tests browser lane

## Evidence

- Head: `ev/HEAD.txt` holds a258212553e123d735c7eff139a8e347a1a52ea3; the body's `## Head` names it. Merge base 9cbd7dd0d7a66163b5b593dfe55f1d8b220785de. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the role contract is current.
- Merge: `git merge-tree --write-tree origin/main a258212553e1` exits 0 against origin/main 28482eceeb6b (`ev/merge_tree.txt`), and again against 80016a71f567 at the end (`ev/merge_tree_2.txt`). There is no conflict and no claim-driver line.
- Review packet rendered here: `ev/review-packet.md`, refusal `required-red: gate` (the block above). carry_audit at the head: 5 body items, 5 routed.
- Round-2 block re-measured (class-open: MonthlySavingsSensor). It is repaired: `sensor.py` `extra_state_attributes` publishes `saving_includes_wood` from `wood_fuel.saving_includes_wood`, the one definition the notifier also reads.
- Class, by my own rule (`ev/class_enum.txt`): A, the value keys (`savings_sek|saving_sek|savings_pct|saving_pct|savings_months|monthly_receipt|plan_monthly_savings|saving_includes_wood|wood_note`), over custom_components, blueprints, README and docs, excluding design and decisions; B, every card `savings.*|receipt.*|headline.*|health.learn*` string key; C, the prose "plain thermostat|less than … would have|saved … against". Every consumer returned is in the body's table:
  - Seams that state the metered saving, all of which now carry the wood statement: ledger (producer); coordinator `_grid_view`; notifier `_monthly_receipt`; MonthlySavingsSensor; card `receiptHtml` and `_savingsPageHtml`; the blueprint's "Monthly receipt" message; README; docs/automations.md; docs/dashboard-card.md; docs/how-it-works.md.
  - Out of class, with no stated saving: card `HEALTH_WAITING` `["savings", "_plan_monthly_savings"]` (a status), `headline.savings*` (the projection), payload types, the optimizer comment, the icon and entity-name strings, and the legacy suffix alias.
  - No seam is undispositioned.
- Finder's harness, `r10_rca_sav_estimate.py census` (the copy at handoff/r10-rca-sav-estimate d8eeae8f8e51, sha1 04b644563c84d26378cad42a603dc050e7e5fd88, the same as the body's): at the base 9cbd7dd0d7a6 and at the head, the same six lines: `RESULT census single 1.00 ok`, `unvalved 0.92 ok`, `valve-at-curve 1.00 ok`, `valve-charged 1.00 ok`, `wood-warm 1.00 ok`, `wood-hot 1.00 ok`, rc 0 at both (`ev/census_base.log`, `ev/census_head.log`). It is flat by design, as the body says.
- Carry B, re-derived at the head (`ev/wood_plant_head.log`, rc 0):
  - `RESULT wood_plant_error_m0.8: mean +0.00 % min +0.00 max +0.00 sd 0.00 over 9 fires`
  - `RESULT wood_plant_error_m1.0: mean +0.00 % … over 9 fires`
  - `RESULT wood_plant_error_m1.2: mean -1.95 % min -4.50 max +0.00 sd 1.47 over 9 fires`
  - No fire: plan 133.79 = drawn 133.79 kWh, error +25.00 % / +0.00 / +0.00 at m 0.8 / 1.0 / 1.2, flat 7.59 % at m 1.0 and 1.2.
  - Perturbation (the pump blind to the fire): +0.00 % at every m.
  - Every figure equals the body's.
- Full suites at the head, run in full (`ev/head_rc.txt`):
  - `features.py` rc 0 and `entities.py` rc 0 (`ev/head_features.log`, `ev/head_entities.log`).
  - `structure.py` rc 0, STRUCTURE RATCHET PASSED; no budget moved.
  - `plan_view.py && card.mjs` rc 0 and `card_browser.mjs` rc 0. My first card and browser runs omitted `PYTHONPATH=tests/hastub` for plan_view; that was my setup error, and the rc=1 lines in head_rc.txt are those runs. The rerun lines are the measurement.
- Golden claims: `env_drift.py --all 9cbd7dd0d7a6` at the head rc 0, `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE` (`ev/head_env_drift.log`). Each of the five claimed coord_* moved exactly one leaf, `sensors.monthly_savings.extra_state_attributes.saving_includes_wood` (present on one side only), so every claim moved and every move is claimed. `claims-for: 7.1.4` equals VERSION 7.1.4, and claimed_drift.txt differs from the base only by the five claim lines. `card_claimed_drift.txt` is unchanged.
- Protected files: `git diff --quiet <mb> HEAD -- VERSION manifest.json RELEASE_NOTES.md card_claimed_drift.txt` rc 0.
- My own mutants, each in its own detached worktree at the head, one exact replacement (runner `ev/mut.py`, logs under `ev/mutants/`). Null control: entities rc 0, card rc 0.
  - R1, blueprint guard → `data.saving_sek is not none`: killed by entities, on the blueprint wood check.
  - R2, guard → `data.saving_includes_wood` alone: killed by entities, on the same check.
  - R3, guard negated: killed by entities.
  - R4, blueprint text → "Firewood is free.": killed by entities.
  - R5, sensor attribute → `False`: killed by entities `((False, True), (False, False), (False, False))`.
  - R6, notifier → `True`: killed by features, 1 of 4877 (the receipt-event check).
  - R7, definition → `bool(data.get("wood_fuel"))`: killed by entities `((True, True), (True, True), (False, False))` and by features.
  - R8, card receipt `${wood` → `${!wood`: killed by card.mjs (`the receipt's saving on a wood house says it includes wood's heat … (en, sv); none without wood`); browser rc 0.
  - R9, card `!!(fuel && fuel.show_whatif)` → `!!fuel`: survives card.mjs, killed by card_browser (see Findings).
  - R10, `receiptHtml` without `wood`: killed by card.mjs.
  - The entities `a3:*` FAIL lines are its own negative self-tests and print in the null run too.
  - The body's M11 and M12 are my R1 and R2 shape (both die). Its M8 is my R5 and dies. The sv string `savings.wood_note` reads "Sparandet inkluderar värme från ved. Vedens kostnad räknas inte." (card.js:1188); card.mjs's en and sv check dies under R8 and R10.
- Figures not re-derived by me: the body's 65-line and 6-line counts for its own rule R (I ran my own rule instead), and the jinja2 render, which needs venv-ha (I did not run it; the source pin plus R1 to R4 cover the guard and text).
- Delivery row `dev/programme/delivery/3244.md` is in the three-dot diff. Both Forward-carry items carry a `Carry:` line (carry_audit 5 routed, 0 unrouted).
- CI at this head: every other context concluded success or skipped (`ev/review-packet.md` digest; get_check_runs, 81 runs).
