**BLOCKED at the structural ratchet: `tests/structure.py` refuses `seam_cut_total` by +1 (709 > 708). The orchestrator needs to decide between the two routes under "Payment" below before this head can open.** Everything else this group owes is done and measured below. No budget was raised and no `--record` was run.

The plan narrative now prices money in the price feed's currency (`coordinator.currency`), like every other money surface. Before this change, `_narrative_view` resolved the currency itself with `resolve_currency(hass)`, which returns the instance's label currency. A EUR feed on a SEK instance therefore published EUR sensors next to a narrative written in SEK. The local precedence is deleted, and the view reads the one value that `currency.py`'s `declared_currency` decides and the coordinator adopts on each cycle. The `narrative.render` docstring justified that local precedence ("A narrative line is recorded nowhere, so it can simply follow the instance"), and it is rewritten to state the new contract (fixer.md step 9).

Fixes #2243 (D14-s3-01; D14-s2-01 merged into it). Fixes #2222 (D5-s3-01): the price-units comment in `_audit_price_units` named a nonexistent ``money_currency``, and it now names what the sensors actually carry, `unit_of_measurement` and the `currency` attribute.

### Payment (the open decision)

The fix's shape is the architect note's "read the currency from one owner; delete the local precedence". That shape costs one cross-seam attribute reference: `_narrative_view` belongs to the `views` seam (`tests/seam_map.json`), and `currency` is stored only by `core` units (`__init__`, `_update_current_state`). The per-seam table at the head prints `views` cut 107. Inside the owning seam there is no reference left to remove: `_narrative_view` also reads `_optimization_result`, `hass` and `_opt_config`, and the view needs all three. The routes considered:

1. **Pay in `_raise_cop_issue` (seam `learning`).** This method reads `self.currency` twice in one body, once for the log line and once for the issue placeholder. Binding it to one local lowers `learning`'s cut by 1 and nets the ratchet to 708. This is outside the owning seam the architect note names, so it needs the orchestrator's after-edge. That method also has a stale comment, "In the instance currency: the prices are", which is the same class of claim as D5-s3-01 (its prices are the feed's). Fixing it in the same hunk would make the payment a genuine correction, not just a change to the metric. **Recommended**, if the after-edge is granted.
2. **Raise `seam_cut_total` by 1.** No payment inside the seam improves the code, but route 1 exists, so a raise is not the only option. It needs the owner, or a mandate scoped `budget-raise` (0013), which this seat did not read because the brief says to spare the API.
3. Rejected: passing the currency from `_insight_view` or from the `_async_update_data` publish line into `_narrative_view`. This moves the same `self.currency` reference into another units' body (the cut does not change) and touches lines outside the seam.
4. Rejected: re-deriving the code in the view from the feed state (a new `currency.py` helper over `hass.states`). That is a second precedence, which is the defect class itself, and it would lose the "an unavailable feed keeps the code already adopted" rule that `_update_current_state` applies.

Architecture score: dS +0.0000 NULL.

## Head

`701448f9062f12c8361351822c6c0fc55139c772` (branch cut from origin/main `8a94ffd03c05c9bc799db8ad11d820dbaa133844`, merge base the same, measured 2026-10-22).

## Mutation proof

The fix's production line was mutated back to `narrative.render(items, chosen, resolve_currency(hass))` in a worktree of the head, and `PYTHONPATH=tests/hastub python3 tests/features.py` was run. Result: `1 of 4302 FEATURE CHECKS FAILED`:
`FAIL D14-s3-01: the narrative prices a EUR feed on a SEK instance in EUR, and a SEK feed in SEK  [{'EUR/kWh': ['SEK'], 'SEK/kWh': ['SEK']}]`. Restored. The same check fails, alone, on the merge base `8a94ffd03` carrying only the new test (failing test first). It passes at the head.

## Null control

- The finder's harness `clean` arm (EUR feed on a EUR instance) reads 0 mismatched seams at the base and at the head. Its `reintroduce` arm (`declared_currency -> None`) reads 14 of 14 at the base and at the head, as the forward-carry required.
- In the new test, a SEK feed on the same SEK instance renders `['SEK']` at the base, the mutant and the head. Only the EUR-feed arm moves.
- D5-s3-01: `comment_symbols.py` at the base lists `MISSING coordinator.py:2078 \`money_currency\``, and the head's list differs from the base's by exactly that line (`diff` of the two non-RESULT outputs).

## Figures

The finder's harness is `$EXPORT/dev/audit/rounds/round10/D14/s3/p8_replay_currency.py` from d23205d13, sha1 `1acaac172452ff43387e83cbff0f02cfcd8a5a2d`, run as `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round10/D14/s3/p8_replay_currency.py` from each tree. The rule is in the harness header: a seam is a distinct (entity, field-path) whose delivered value names an ISO code, and it is mismatched when that code is not the feed's.
- base `8a94ffd03`: `base_money_seams=14`, `base_mismatched_seams=1` (`sensor.heat_pump_optimizer_plan_narrative attr.lines[]: ['SEK']`), `clean_mismatched_seams=0`, `narrative_fixed_mismatched_seams=0`, `reintroduce_mismatched_seams=14`
- head `701448f90`: `base_money_seams=14`, `base_mismatched_seams=0`, `clean_mismatched_seams=0`, `narrative_fixed_mismatched_seams=0`, `reintroduce_mismatched_seams=14`

Class enumeration (step 8): `grep -rn "resolve_currency(" custom_components/` returns 10 call sites at the base and 9 at the head. Their dispositions:
- `coordinator.py` `_narrative_view`: closed in this diff.
- `coordinator.py` `__init__` (the `_feed_currency(...) or resolve_currency(hass)` fallback): this is the owner's own precedence and is kept.
- `coordinator.py` `_audit_price_units` (×2): deliberately the instance label, because it names the feed/instance disagreement.
- `config_flow.py` (×6, the options dialog's money labels and `fee_bound`): instance-labelled by design and already guarded by the `price_currency` repair issue that `_audit_price_units` raises.

The harness drives every money surface the six platforms publish (14 seams), and after the fix all 14 name the feed's code.

`comment_symbols.py` (`dev/audit/rounds/round10/D5/s3/comment_symbols.py`, sha1 `19dfe7849733dce1237b685804071d9814129263`, identical at d23205d13 and the base), run as `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D5/s3/comment_symbols.py`: `comment_symbols_untriaged_missing` reads 7 at the base and 6 at the head.

The gate is `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=8a94ffd03… ./tests/run.sh` with `PREPR_SKIP_CLOSURES=1`. Its mode line is `MODE: SCOPED -- 21 script(s) run, 12 scoped out`. Every script it names is ok except `tests/structure.py`, which fails with `FAIL seam_cut_total 709 > 708 (+1)`. That is the block above. `tests/harness_headers.py` also failed inside the gate, with `gate_lock: flock-wrap refused, r10-currency-fixer holds no lease`: the seat had set `HPO_GATE_LOCK_LABEL` without taking a lease, so this is the environment and not the tree. Run directly, it prints `ALL 109 HARNESS HEADER CHECKS PASSED`. `tests/stress.py` was scoped out.

`python3 tools/audit/archscore/score.py --diff 8a94ffd03 HEAD` prints `Architecture score: dS +0.0000 NULL`.

## Red checks

`tests/structure.py`, locally, before any push: `seam_cut_total` +1. The cheaper detector is the one that caught it, a 17-second local run before the push, so no countermeasure is owed. The open decision is under "Payment".

## Forward-carry

- R10-FEEDS carry (callers of `_get_current_price` / `_current_spot_price` must handle `None`): this diff touches no such call site. `_narrative_view` reads `result.prices`, not either getter. Nothing to carry.
- The stale "In the instance currency" comment in `_raise_cop_issue` belongs to the D5/I5 class. If route 1 is not taken, it needs a brief. Carry: R10-CURRENCY's orchestrator decision (this body), so it is not filed as an issue.

## Friction

- fixer.md-step17: contradiction: the architect note's mandated shape (read the one owner from the `views` seam) costs `seam_cut_total` +1 at zero headroom, and the note forbids the out-of-seam hunk that would pay for it. Carry: orchestrator.md section 5 (an architect note should price its shape against `seam_cut_total` before dispatch).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01USXaa36pNNaVCQNZ8eH5mB
