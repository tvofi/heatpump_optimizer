# BLOCKED: R10-PARTLOAD-RESIDUE body re-take (repair round 2)

Code head 306a0b76e8bdd3e82e7370e3f1ad7bc08be832c1 stays on `handoff/r10-partload-residue`; this seat changed no code.

**Cure (b) does not settle carry 2: the figures are not immaterial.** Re-run here, matching the prior seat to every printed digit:

- `r10_partload_residue.py refill` at 306a0b76e, at the plan's own energy-weighted draw `P_r = sum(P^2)/sum(P)`, d = 0.112: terminal error up to 3.714491 and deferred up to 0.792466 per horizon (flat); 2.117798 and 0.486127 (spread). The day's hot-water cost is 7.0145 (flat), so the terminal error is 53 % of it and 79 % of its own cell's `predicted_cost` (4.7018, cell (0.6, 750, False, True)). `null rows not zero 0`, `failures 0`, rc 0.
- `r10_partload_pricing.py` at merge base 4b5d771bd: lp_err 0.267290 against 7.0145 (3.81 %); terminal-at-max 4.368455, deferred-at-max 2.139841; `null rows not zero 0`, rc 0.

So cure (a) stands, as the prior seat took it: carry the decision to R10-SAV-COMFORT. The refreshed body (fixes `## Head` and adds the cancelled `gate` 128453123588 to `## Red checks`) passes `prepr.sh --body-check --pr-branch fix/r10-partload-residue` (rc 0; pr-body 0 errors, carry 2 routed, figures 6 resolved) and is kept at `handoff-wip/r10-partload-residue-body` cfc6f219c8285d7c570d0a6980b57e5448ddc14c. `body_push.sh` refused it:

    CARRY-MISSING R10-SAV-COMFORT body item 213e8a10: not in its brief or carries

Still missing at `handoff/audit-r10-roster` badbae55a and on origin/main.

**The question for the dispatch seat:** land this append-carry on `handoff/audit-r10-roster` (a fixer may not write the roster), as printed by `carry_audit.py land-ops`:

    append-carry R10-SAV-COMFORT 'From r10-partload-residue, body item 213e8a10: Carry 2's segmenting and refill-rate decision, its zero-derate control and the figures in `## Carry for the roster` ... Carry: R10-SAV-COMFORT (items 213e8a10)'

then re-run `bash tools/audit/seat/body_push.sh r10-partload-residue <BODY.md at cfc6f219>` unchanged. origin/main has moved to 53273de4d; `git merge-tree --write-tree origin/main 306a0b76e` reports no conflict, so no merge was made (owner ruling 2026-11-07).
