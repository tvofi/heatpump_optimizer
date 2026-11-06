Fix review: blocked dea3c729d67555753cbfe41c283cf49e5de7c517 class-open: blueprints/automation/notifications.yaml monthly-receipt message states the wood house's saving with no wood statement

bus-nonce: 02624d4d66ee6726669e64b505795156

Round 2 fix review of PR #3244 (R10-HOTFIX-SAV-ESTIMATE part 2, topic r10-sav-wood-heat), measured at head dea3c729d67555753cbfe41c283cf49e5de7c517 (tree equal to the handoff code 49c4bce874edbfb3fff2cafcf5c7ffc8ce7beecb; `git diff --stat` between them is empty).

## Block

The round-1 seam is repaired: `sensor.py` `MonthlySavingsSensor` now publishes `saving_includes_wood` from the one definition `wood_fuel.saving_includes_wood`, and its mutants die (Evidence). The class is still open, though. I enumerated the consumers of `savings_months[].savings_sek` myself and followed the value through the receipt event (`notifier.py:97`, `saving_sek`). That turned up a shipped consumer that is neither in the diff nor dispositioned in the body: `blueprints/automation/notifications.yaml:105-123`, the "Monthly receipt" branch of the integration's notifications blueprint. It sends the user a notification reading "Heating and hot water cost {total}, {saving_sek} {currency} ({saving_pct} %) less than a plain thermostat would have." It does not read `saving_includes_wood`, which the event carries and `docs/automations.md:146` documents. So on a house with wood configured, the integration's own notification states a saving that includes wood's heat and leaves out firewood's cost, with no disclaimer. That breaks Carry A as the body states it: "Wherever wood is configured, the saving the integration states says that it includes wood's heat and excludes firewood's cost." The body's enumeration rule searches only `custom_components` and the card, so it cannot return this seam. The seam survives the repair: the blueprint is byte-identical to the merge base 817c2b16 (`git diff --stat 817c2b16..HEAD -- blueprints` is empty). Quoted template: `ev/blueprint_receipt_message.txt`.
The repair is small: append `{% if data.saving_includes_wood %} The saving includes heat from wood; firewood's cost is not counted.{% endif %}` to the receipt message (or the equivalent wording). Pin it with a check that renders the template, or a source pin like the card's, and add a null leg without wood. Also extend the class rule to `blueprints/`, or disposition the blueprint.

## Findings

- Follow-up: the body's class rule (`git grep ... -- custom_components`) stops at the package boundary, while the receipt event that carries the saving leaves the package through `blueprints/` and `docs/automations.md`. A rule for "where the integration states the saving" must follow the value through the event to its shipped consumers. This is the block's own seam and its fix lands in this PR. Carry: R10-HOTFIX-SAV-ESTIMATE

## Evidence

- Head and merge: PR head `dea3c729d67555753cbfe41c283cf49e5de7c517` (the PR API read it at review time). `git merge-tree --write-tree origin/main dea3c729` against origin/main 30638cf0c8a7 exits 0 with tree 0e3b5172fbe6 (no conflict; `ev/merge_tree.txt`). The merge base is 817c2b16989e.
- CI: `merge_train.py classify dea3c729... --pr 3244` gives `GREEN dea3c729d67555753cbfe41c283cf49e5de7c517 pending: none red: none`, rc=0 (`ev/classify.txt`). The packet's gate digest is green with no concluded red. The body's `## Red checks` says the head "has not run CI". That was true when the body was written and is superseded by the green runs. Carry: dismissed: evidence, not a finding
- Role-file drift: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Protected files: `git diff --quiet 817c2b16 dea3c729 -- VERSION manifest.json RELEASE_NOTES.md tests/golden/card_claimed_drift.txt` gives rc=0. `env_drift.py --claims-only` gives rc=0 ("claims hygiene: origin/main ok"). Five structure-only claim lines (`coord_*`, one boolean key added) are justified in the body, and the diffs of the five fixtures are exactly that one key each.
- Full suites at the head, PYTHONPATH=tests/hastub: `structure.py` rc=0 STRUCTURE RATCHET PASSED; `entities.py` rc=0 ALL 2638 ENTITY CHECKS PASSED; `features.py` rc=0 ALL 4877 FEATURE CHECKS PASSED; `plan_view.py && card.mjs` rc=0 ALL CARD CHECKS PASSED; `card_browser.mjs` rc=0 ALL BROWSER CHECKS PASSED (`ev/*.txt`).
- My mutants at the head, each restored afterwards (the worktree was clean after the runs):
  - `sensor.py` attribute → `False`: entities rc=1, `MonthlySavingsSensor states ... [((False, True), (False, False), (False, False))]`. Dies.
  - `sensor.py` attribute → `True` (the null leg): entities rc=1, `[((True, True), (True, False), (True, False))]`. Dies.
  - Card `receiptHtml` wood-note text emptied: card rc=1, `the receipt's saving on a wood house says it includes wood's heat ...`. Dies.
  - Card `const wood = true` (the null leg, a note on every house): card rc=1 on the same check. Dies.
  - The `a3:*`/`a4:*` FAIL lines in the mutant logs are entities.py's own negative self-tests, as the body says.
  - These re-take the body's M6 to M9. The notifier and ledger mutants M1 to M4 were not re-run, and neither was M10: those lines are from round 1 and #3220, and features.py and entities.py pass at the head.
- Finder's harness (`r10_rca_sav_estimate.py census`, sha1 04b644563c84d26378cad42a603dc050e7e5fd88, the same file at both ends), at the base 817c2b16 and at the head: six identical RESULT lines (single 1.00, unvalved 0.92, valve-at-curve 1.00, valve-charged 1.00, wood-warm 1.00, wood-hot 1.00, all ok), rc=0 at both ends. It is flat by design, as the body says (`ev/census.txt`).
- Class enumeration, my own rule: `git grep -E 'savings_sek|saving_sek|savings_months|plan_monthly_savings|MonthlySavingsSensor|savings_pct|saving_pct'` over custom_components, plus the event's consumers across the tree (`monthly_receipt` in blueprints/ and docs/), plus the card's `savings.*|receipt.*|headline.*|health.learn_*` key uses grouped by function. Consumers that state the metered saving:
  - ledger producer: built.
  - coordinator: built.
  - notifier event: built.
  - `MonthlySavingsSensor`: built this round.
  - card `receiptHtml` and `_savingsPageHtml`: built.
  - `blueprints/automation/notifications.yaml:119-123`: NOT built. This is the block.
  Out of class: `headline.savings*` reads `_plan_predicted_savings` (the plan's projection), and `health.learn_*` renders only waiting rows with no figure (`HEALTH_WAITING` at card.js:9488-9642).
- Not re-run: the body's `wood-plant` Carry B figures (mean −1.95 %, max −4.50 % at m 1.2). Under the block they are not yet verified by this review. Carry: dismissed: evidence, not a finding
- Round: 2 of the fix review.
- Self-audit: `carry_audit.py check` over this verdict ran with a stub body (the PR body's own carry items audited in the packet: 4 routed, 0 unrouted): CARRY-AUDIT 3 finding item(s), 3 routed, 0 unrouted, rc=0. Carry: dismissed: evidence, not a finding
