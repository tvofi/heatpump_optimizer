# D1 round 10 -- verifier report (single verifier, lenses V1-V3)

Worktree: detached at handoff/audit-r10-register 9355f107d (the branch was already
checked out elsewhere, so `git worktree add --detach`); production tree identical to
baseline 17f1c55fad1b. Box: Mac arm64, contended (load1 10-29 across runs,
thread_factor 1.00-1.23). All numbers are counts, not timings, so contention does
not move them, except D1-s1-01's 5-round run (below). Own harnesses: `v_*.py` in this
directory, each with its command in the header.

| id | V1 base / perturbed / null | V2 (own) | reach (real HA) | class | seam rule | vote | sev |
|---|---|---|---|---|---|---|---|
| D1-s1-01 | 5 rounds: AssertionError "cycle did not complete" (20 s wait under load1~10-29); `--rounds 2`: torn_alive=2, early_cutoff keys=2; `--perturb` (5 rounds) also timed out | `v_m1_own.py`, async_on_unload coroutines AWAITED (real-HA semantics; the stub drops async_shutdown): own_torn_alive=3/3; clearing `_STATES[c].wiring` -> 0/3 | yes: every reload/options save | new | enumerates the 5 annotated WeakKeyDictionary registries; misses un-annotated ones | verify | medium |
| D1-s1-02 | torn_midsolve=2/2, null=0; perturb -> 0 | `v_m4_climate_path.py` (also issues the climate's follow-up `async_request_refresh`, reads after both settle): torn=2/2 (comfort, boost: action.mode=eco) | yes: climate `_async_set_mode` uses refresh=False; follow-up comfort refresh does not repair | N-shared-config (concurrent writer reverted), not new | none given | verify | medium |
| D1-s2-01 | warnings=5, changed=5, control 0; perturb -> 0 | `v_s2_bound_own.py`: `_bound_instants` on 5 dues at now+1..24 h: lead=0 rewrites 5/5, accuracy lead 0/5 | yes: every restart with pending dues; harm only on rollback + log noise | P2 (same embedded fact bounded by two divergent leads), not N-future-instant (this is that guard over-firing) | enumerates all 17 QuarantiningStore( sites | verify | low |
| D1-s2-02 | 4/4 published, 4/4 booked, control 2; perturb -> 0 | `v_s2_price_own.py`: `_current_spot_price` at +1..+100 h past list end returns last row 5/5; inside list correct | yes: stalled price entity/source answering ok | new | enumerates readers of the two price getters only, not other last-entry-forever lookups | verify | medium |
| D1-s2-03 | empty_forecast 4/4, control 0; perturb -> 1 | `v_s2_weather_own.py`: 4/4 WARNINGs on direct calls with empty forecast | empty-forecast arm yes; no-entity arm NOT reachable via config flow (CONF_WEATHER_ENTITY is vol.Required) | new | none given | weaken (reach of one arm) | low |
| D1-s3-01 | empty_ok_wipes=1; perturb -> 0 | `v_s3_tibber_own.py`: pull_prices on 200+empty -> verdict ok, rows 0; `_current_spot_price` then 0.0 | yes: Tibber returning empty priceInfo | P2 (entity path refuses empty, Tibber path admits), N-silent-zero is an instrument class | none given | verify | medium |
| D1-s3-02 | startless=96, misplaced=95; perturb -> 0,0 | own: 96/96 admitted with starts_at='' | weak: both queries request startsAt; needs an upstream schema violation | P1 (malformed external feed, no guard) | none given | weaken | low |

Attacks run: contention (counts only; m1 5-round failure is a wait timeout under
load, 2-round and own 3-round runs reproduce); stub divergence (m1: harness never
awaits async_shutdown -- own harness awaits it, leak stands; m4: added the real
follow-up refresh, torn stands); null controls all 0; no aggregates to leave out.
