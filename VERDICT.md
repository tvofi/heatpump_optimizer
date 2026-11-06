Fix review: blocked 622be7c53b760156e2453dacbd1724325212b9e4 class-open: sensor.py MonthlySavingsSensor publishes the wood house's saving with no wood statement, not in the diff and not dispositioned

bus-nonce: f97ee9561627fa5a9ed0861c76eedc90

## Block

Round: first fix-review round for #3244 (R10-HOTFIX-SAV-ESTIMATE part 2, topic r10-sav-wood-heat). I measured head `622be7c53b760156e2453dacbd1724325212b9e4` from detached worktrees.

The class is the owner's Carry A ruling (tvofi 2026-11-04): wherever wood is configured, the saving the integration states says that it includes wood's heat and excludes firewood's cost. The body lists the surfaces in its "what was already built" table: the ledger, the card's savings table, the card receipt and the notifier's `saving_includes_wood`. It names no rule that produced that list.

I enumerated the consumers of `savings_months[].savings_sek` and of the `savings.*`, `receipt.*`, `headline.*` and `health.learn_*` strings myself. That rule is my own, not the body's. It returns one seam that is neither in the diff nor dispositioned:

- `custom_components/heatpump_optimizer/sensor.py:486-527` `MonthlySavingsSensor` (`sensor.plan_monthly_savings`).
  - Its state is the first estimated row's `savings_sek`, which is the same metered saving as the card receipt's figure.
  - On a wood house its state and attributes carry nothing about wood: no `saving_includes_wood`, no flag. `sensor.py` reads `wood_fuel` only at 1412, 1493, 1589 and 2980-3002, all on other entities.
  - A dashboard tile or automation that reads this entity states the wood-inflated saving with no disclaimer.
  - The receipt event got a machine-readable flag (`notifier.py:103`) for that kind of consumer; this entity did not.
  - Excerpt: `ev/sensor_monthly_savings.txt`.

The other surfaces I checked are outside the class, and the body need not disposition them:
- `replayHtml` (card JS 9999) states measured cost against promised cost, not a saving against the reference.
- `headlineHtml` `_plan_predicted_savings` (card JS 9066) is the plan's projection against unoptimized heating, not the metered reference.
- The `health.learn_savings` row (card JS 9637-9642) shows status only, with no figure.

Either fix closes it: add the wood statement to the entity (an attribute such as the notifier's `saving_includes_wood`, pinned with a mutant), or disposition the entity in the body with the owner's ruling as the reason. The rest of the review below found no defect.

## Evidence

- HEAD.txt holds 622be7c53b760156e2453dacbd1724325212b9e4. The PR head was re-read before writing and is unchanged.
- `## Head` names this head and the authored code head `df4172cae30c402c674297922a1acccca4192ac1`. The record commit adds only `dev/programme/delivery/3244.md`, and that row is in the three-dot diff.
- Merge with main: `git merge-tree --write-tree origin/main 622be7c5` exits 0 with tree `1707ab0b8f3e`. origin/main is `dc0a170b6`, which is also the PR's merge base. See `ev/merge-tree.txt`.
- Role contract: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- What was already built, re-derived by grep at the fork base `0a7c84fa2` (`/home/user/wt-fork`). Every built row holds:
  - `ledger.py`: `REFERENCE_BASIS` (75), `savings_months(..., wood_configured)` (432), `calibration = max(1.0, calibration)` (465) and `"savings_sek": None if old_basis else saved` (486). No tank-keyed dash path.
  - `notifier.py:103`: `saving_includes_wood`.
  - `coordinator.py:7940`: passes `wood_configured=wood_furnace_on(...)`.
  - Card `savings.wood_note` en (331) and sv (1188), drawn in the table (14964) and pinned in `card_browser.mjs:2088`.
  - The receipt's `receipt.saved` line (9948) has no disclaimer at the fork base, so the receipt line is the one new part, as the body claims.
- Full checks at the head, all rc 0 (`ev/full_summary.txt`, logs in `ev/full_*.log`):
  - `structure.py`: STRUCTURE RATCHET PASSED.
  - `entities.py`: 2632 checks passed.
  - `features.py`: 4877 checks passed.
  - `plan_view.py`, then `card.mjs`: ALL CARD CHECKS PASSED.
  - `card_browser.mjs`: ALL BROWSER CHECKS PASSED. Chromium ran on this host.
  - `env_drift.py --claims-only`: claims hygiene ok.
  - `card_drift.mjs`: identical in all 45 states.
- Mutation results. Each mutant ran in its own worktree, with a null control first. Script: `ev/mut.py`; results: `ev/mut_*.txt`.
  - NULL (no edit): `features.py`, `card.mjs` and `card_browser.mjs` all rc 0.
  - Body M1 (`ledger.py` drops the floor): killed, `features.py` rc 1.
  - Body M2 (`ledger.py` removes the old-basis dash): killed, `features.py` rc 1.
  - Body M3 (`notifier.py` sets `saving_includes_wood` to False): killed, `features.py` rc 1.
  - Body M4 (`coordinator.py` passes `wood_configured=False`): killed at the head, `features.py` rc 1. At the fork base `0a7c84fa2` it survives with rc 0, which confirms the new pin is earned.
  - Body M5 (`woodNote = false`): survives `card.mjs` and is killed by `card_browser.mjs` (rc 1), as the body states.
  - Own R1 (receipt note dropped): `card.mjs` rc 1, `card_browser.mjs` rc 0, so killed.
  - Own R2 (receipt note always shown): `card.mjs` rc 1, so killed by the null leg.
  - Own R3 (call site passes `wood=false`): `card.mjs` rc 1, FAIL "the receipt's saving on a wood house says it includes wood's heat...", so killed.
  - Own R4 (condition loosened to `!!fuel`): `card.mjs` rc 0, `card_browser.mjs` rc 1, so killed by the shared condition's browser check.
  - Own R5 (wrong string key in the receipt note): `card.mjs` rc 1, so killed.
  - Own R6 (sv string replaced by the en one): `card.mjs` rc 1, so killed.
  - Body M6 (no fix at the base fails the new test) is covered by R1 and R3: removing the fix's line or its input fails the new `card.mjs` check.
- Finder's harness (`dev/audit/harnesses/r10_rca_sav_estimate.py census`, the same file at `handoff/r10-rca-sav-estimate` d8eeae8f): run at the fork base and at the head. Both print the same `RESULT census` lines and rc 0 (`ev/finder_census_{fork,head}.log`):
  - single 1.00, unvalved 0.92, valve-at-curve 1.00, valve-charged 1.00, wood-warm 1.00, wood-hot 1.00, all ok.
  - The census is flat by design at both ends, because part 1 (#3220) settled it.
- The body's Carry B figures, re-run at the head (`wood_plant_head.log`, `wood-plant` arm, rc 0). Every quoted figure reproduces:
  - `RESULT wood_plant_error_m1.2: mean -1.95 % min -4.50 max +0.00 sd 1.47 over 9 fires`.
  - m 0.8 and m 1.0 read 0.00.
  - No fire: plan 133.79 = drawn 133.79 kWh. m 0.8 error +25.00 %, pct 44.9 against 31.1. Flat 7.59 % at m 1.0 and m 1.2.
  - Perturbation +0.00 % at all three m.
  - The meter's shortfall per fire, (1 - drawn/plan) at m 1.0, is 0.03 / 0.66 / 0.72 / 0.77 / 1.89 / 2.08 / 3.23 / 3.70 / 4.54 %, which matches "0.03 to 4.5 %".
  - Not re-derived: the `--quick` one-step probe figures (48.57/48.57, 48.23/50.20).
- Golden fixtures and versions: `git diff --quiet origin/main 622be7c5 --` over both claim files, `VERSION`, `manifest.json` and `RELEASE_NOTES.md` exits 0. Nothing is claimed and no fixture moves (`card_drift` is identical).
- Forward-carry: one item, dismissed with a `Carry:` line, about the floor's cost on a model that reads the meter high. It is owner-ruling territory and is stated in `docs/how-it-works.md`. The packet's `carry_audit` reads 2 routed and 0 unrouted.
- CI on this head, read live (`ev/classify.log`). `merge_train.py classify` returns rc 1, `RED ... red: gate`.
  - The `CI code` run 42191159493 concluded and its `gate` job 127821770398 passed (09:40:55Z). Its jobs ended 29 success, 10 skipped and 1 cancelled, with no failures.
  - The required `gate` context is red because of the two `CI edit` runs, 42191160922 and 42192068191.
  - Both runs' gate jobs re-ran at 09:41:3x (127822327907 and 127822332689). Each printed `FAIL run(s) [<the other edit run>] at this head are still being judged; their gate decides` and exited 1.
  - So the two gates deferred to each other, and neither judged any code. This is CI tooling (`tools/ci/gate.py`), not this PR's diff.
  - The body's `## Red checks` reads "none", and the packet refuses it as `red-unanswered: gate`.
  - `pr-contract` was skipped at this head. Under fix-review step 11 a root-cause verdict waits on a `pr-contract` run after the last red, so I do not block on it. The orchestrator should re-run one edit run's gate once the other has concluded.

## Friction

- The session's frugal-routing hook refused a sixth inline read per prompt, so two locate steps went to scout agents. Carry: dismissed: a session plugin outside this repository's policy
