_Requested by **tvofi**_

Part of #201.

## The defect

Today's scheduled nightly (run 37189092011, 2026-10-04T08:29Z, main `fb11a017`) failed in `mutation-ledger`: `MUTATION TABLE REFUSED` — **the null control (a comment-only edit) was killed by `tests/stress.py`**, voiding every kill of the run. A comment-only edit changes no behaviour; a driver that notices it is judging noise.

The kill came through the per-call-cost channel: `summer/1z/dhw/fuse-cap` spent 99 ms of kernel CPU against the baseline's 47 ms = **2.13×, over the 1.80× factor, on an unchanged plan**; the budget-factor channel was also marginal (8.0× vs its 7.9× budget).

Two same-day dispatch runs on the same code **succeeded** (37190840519 and the 13:02Z ledger deployment) — the channel is runner-noise sensitive, not deterministic. The #1878 SIGXCPU fix is separately validated and green.

## The fix

Measured headroom for runner variance in the per-call kernel-CPU channel — median-of-N samples or a factor re-calibrated on the ledger's own recorded cross-runner variance (state the numbers) — keeping round-5 D9-07's intent (a genuinely slower per-call kernel must still be caught; plant one) and the count channels unchanged. The null control must survive every runner.

Root-cause section owed here per defect-root-cause.md: named cause, process state, cost (a voided nightly + a red main lane), countermeasure.

## Sources

Roster: `origin/handoff/audit-r9-fixplan` (R9-FR-9). Log: run 37189092011, job 111397325352, the `MUTATION TABLE REFUSED` line verbatim.
