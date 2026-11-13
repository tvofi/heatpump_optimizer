R10-USER-DOCS-VERIFY, the late user-docs delta (carry 17). Pull request 3513 merged at 83e4e83d77 from base f44e761c19 (`git merge-base 83e4e83d77^1 83e4e83d77^2`); its own step commits are all on main (`git merge-base --is-ancestor 3246aa389f origin/main`), so what main lacks is only what the product merges after that base changed. Enumerated by `for c in $(git rev-list --first-parent f44e761c19..origin/main); do git diff --name-only $c^1 $c -- custom_components blueprints docs README.md; done`: #3524, #3530, #3534, #3441, #3505, #3536, #3512, #3526, #3511 (#3461 is before the base).

Disposition per merge, each read against code, never a comment:

- #3512 (R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE): the supply switch's 10-minute minimum run and pause (`supply_hold.MIN_RUN`, `MIN_PAUSE`, `hold_supply`, retried by `pump_arbiter.supply_tick`; `_passes` exempts modes other than auto and economy, boosts and system identification; `_ends_soon`/`tank_reason` the cold-tank and disinfection exception) was in no user page. Documented on the on/off switch row of docs/configuration.md.
- #3526 (R10-DUTY-SWITCH-PLANNER-PRICE): the solve now prices a learned duty switch (`optimizer._priced_stops`, `_switch_cost_fn`, `_stop_availability`, the placement candidate; `duty_switch.Direction._latch` with `N_ON`, `P_ON`, `SPAN_DAYS_ON`, `HALF_LIFE_DAYS`, `STOP_WINDOW_S`). The README's Compressor Starts row and how-it-works.md's cycling-cost section said nothing of it. Documented in docs/configuration.md (Pump duty control), docs/how-it-works.md and the README sensor row, with the `duty_switch_*` attributes `duty_switch.starts_attributes` publishes.
- #3524 (R10-DUTY-SWITCH-RESTART-LEARNING part B): `k` left the published attributes and `n` became whole episodes; no user page named either before this diff, so nothing went stale; the new row names `p` and `n`.
- #3530 (R10-MODE-BEFORE-SUPPLY-ON): `pump_arbiter.write_supply`/`_lead_mode` writes the step's mode before a switch-on under Control. Documented as a Pump duty control bullet.
- #3534, #3441, #3536: each edited its own user pages in the same merge (docs/ecl110.md; docs/dashboard-card.md and README.md; docs/configuration.md and README.md); re-read, no stale claim found.
- #3505, #3511: no user-visible change (`BOOST_SPACE_SETTLE_TAIL_HOURS` keeps the former 12 h; optimizer internals).

dev/audit/rounds/round4/D6/claims.json and claims.md are that harness's own output re-run at the head (`tests/harness_headers.py` refuses committed output that its run changes): C108 counts one more relative link, the new how-it-works.md link to `configuration.md#pump-duty-control`, with broken=[].

The brief's other carries, each already on main by pull request 3513 (its step commits are ancestors of origin/main by `git merge-base --is-ancestor 3246aa389f origin/main`), re-run here only where this diff reaches them:

- Carry 0: dismissed in the brief, superseded by Carry 1.
- Carry 1, Carry 2, Carry 3: marked implemented in the brief; at this head `python3 tests/doc_claims.py` passes both arms (Figures).
- Carry 4 (away mode and the mold floor), Carry 6 (the operating-mode row), Carry 7 (coffee.svg), Carry 9 (the Health section), Carry 14 and Carry 16 (the stratified combi probe): marked implemented in the brief; this diff touches none of those sentences.
- Carry 5, Carry 11, Carry 12, Carry 13, Carry 15: `python3 tests/doc_claims.py --markers --user` reads `0 user-doc marker(s), 0 due` at this head (Figures).
- Carry 8: dismissed in the brief (the owner's check on v7.1.12). Carry 10: dismissed in the brief, a duplicate of Carry 11.

Pages re-read: README.md, docs/setup.md, docs/configuration.md, docs/how-it-works.md, docs/automations.md, docs/dashboard-card.md, docs/ecl110.md.

## Head

6295f868a4314316f5e12c72fa2d16ead4895d35, cut from origin/main e23124ff6e45bac1d48b4a775dad555a37965355 (2026-11-13 UTC).

## Mutation proof

n/a: docs only; no production line changed. `tests/doc_claims.py` pins none of the added sentences (no claim table row reads them), stated rather than implied.

## Null control

`git grep -c -E "less than 10 minutes after it came on|A switch that stops the compressor is priced|The mode goes first when the pump is switched on|duty_switch_\*" <ref> -- README.md docs/configuration.md docs/how-it-works.md` prints nothing at origin/main and one or more lines per page at the head.

## Figures

- `python3 tests/doc_claims.py` at the head: ALL checks PASSED (coverage and stateless arms).
- `python3 tests/doc_claims.py --markers --user`: `0 user-doc marker(s), 0 due`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`.
<!-- figure-block: scope-line mb=e23124ff6e45bac1d48b4a775dad555a37965355 head=6295f868a4314316f5e12c72fa2d16ead4895d35 -->
~~~text
MODE: SCOPED -- 6 script(s) run, 27 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

none

## Friction

none
