A room-temperature listener, modelled on the peak guard, switches a space-heating pump off once inside a plan interval when the room passes its threshold. The next cycle's own switch write resumes it. Decision on #201 (comment 6067353918, mandate 6067089637). Last PR of the live-fix wave; its learner-freeze order (amendment A2) is carried to fix 5.

**Shipped rule: plan-aware.** Threshold = max(active comfort target, the plan's predicted room at the end of the current step) + 0.5 K. **Inert in every measured case; ships as a guard.** The rule comparison, closed-loop harness and DST wall-clock kill are round 3's measurements; the production lines they grade are byte-identical here.

The cut-off (`custom_components/heatpump_optimizer/early_cutoff.py`) reads configuration through #1745's `EntryConfig`, never a raw key; acts only on a `step_duty == "space"` step; exempts hot-water/both/idle, a boost, disinfection, a **defrost entity that exists and reads on** (one that merely exists but reads `off` is NOT exempt -- see ## Mutation proof), a tank below minimum, non-plan modes, a stale plan and a cold lower zone; enforces `MIN_ON`/`MIN_OFF` and once-per-cycle; writes only the power switch through `pump_arbiter.switch_supply`; freezes the learners under one reason `early_cutoff`. That substance is round 1-3's, unchanged by this diff.

**This pass (round 6) clears the reds the bot's own pin commit left behind.** At `a15508b7a` the required `mutation` check still refused on 6 added sites: `mutation-autofix` had gone green having pinned 31 `killed_by` rows, but its shard drive measured 4 of those sites surviving every driver (two `CMP_BOUND` twins at `early_cutoff.py:251`, both at `:264`) and never measured 2 more (`:275`, `:304`) because the shard's `--budget-minutes` overran -- and the `ci: pin killed mutants` loop guard means no second bot pass (`ci-autofix.md`). This diff adds the two killing checks those survivors need, triages the one genuinely equivalent twin, and leaves the four killable-but-unmeasured sites to the canonical Linux drive at this head.

## Head

`43881d405dfe9a3a14c305fe4ac4b84e5995665d` -- on the bot's `a15508b7a` (`ci: pin killed mutants`: 31 `killed_by` rows, all kept and verified complete -- the deterministic census below refuses on exactly the 4 the shards did not pin), this branch adds: the merge of `origin/main` `969c3a5c8` (docs and prestudy evidence only, no conflict; production and tests trees identical to the prior base `d3dbf2c3`), two killing checks in `tests/features.py` (round 6, ## Mutation proof), one `survivor_triage` row (the equivalent clock-skew twin), and this body. The reviewed production bytes are unchanged from `a9b1b48c4`'s. Measured 2026-10-10 against `origin/main` `969c3a5c8`.

## Mutation proof

Round-6 arms, driven by the lane's committed worktree-pool verifier (`tools/audit/seat/verify_eight.py`, one private worktree per arm, the tree's own `tests/features.py`, FAIL set diffed against the clean baseline whose only failure is the macOS BLAS float `R9-F2.1 P3`):

| arm | mutation | verdict | the check that fires |
|---|---|---|---|
| `251` low bound | `0 <= i` -> `0 < i` | **KILLED** | `_planned_room reads the first step's end (the i == 0 bound is inclusive)` -- NEW this round. The mutant empties the first step's read, and `threshold`'s `max(base, *[])` then raises on the section's very first fire, so the check is placed at the TOP of the section: its FAIL prints before the file dies, making the kill FAIL-line-visible (the crash alone is rc-only -- the same shape as the bot's `threshold RETURN_DEL` pin) |
| `251` far bound | `i < len(trajectory) - 1` -> `<=` | **KILLED** | `_planned_room holds no reading past a trajectory shorter than its timestamps` -- NEW; drives a ragged plan (trajectory shorter than timestamps, unreachable on the public path), where the mutant indexes past the trajectory's end (the check catches the `IndexError` so the file keeps running) |
| `264` skew bound | `as_utc(since) > utc` -> `>=` | **SURVIVES** | none -- **equivalent**: when the stamp equals `utc` exactly, zero elapsed is already `< MIN_ON`, so the line returns `"min_on"` either way; carries the `survivor_triage` row committed in this diff |
| `264` MIN_ON bound | `utc - as_utc(since) < MIN_ON` -> `<=` | **KILLED** | `the min_on guard is a strict < (a switch on exactly MIN_ON is not held)` -- NEW, twin of the round-5 MIN_OFF check, drives `_cycle_guard` at exactly `MIN_ON` |
| `275` | `< limit - MARGIN_K` -> `<=` | **KILLED** | `_second_zone_cold is False at the exact target-margin boundary (strict <)` -- round 5's check; CI never measured this site (shard budget) |
| `304` | `if reason is not None:` -> `if False:` | **KILLED** | the round-5 hold checks (a cold lower floor / a switch already off / MIN_ON holds) hold the cut; under the mutant the cut is written |

The `264` skew arm is the drive's own discrimination control: it is the one site no check can separate, and it reads SURVIVES while every neighbouring arm reads KILLED. The first placement of the `251` checks (bottom of the file, `e79c669aa`) read the low twin SURVIVES for exactly the crash reason above -- an instrument artifact this placement removes, and the honest reason the checks sit where they do.

The earlier rounds' arms (the defrost-off kill, the eight round-5 checks, the two triaged `RETURN_DEL` equivalents at `_plant_exempt`/`_cycle_guard` terminals) are the round-6 reviewer's `miniec.py` table, re-published in `origin/verdict/2070`: 14 arms, 12 KILLED, 2 SURVIVES-both-triaged, measured at `a9b1b48c4` whose early-cut-off production bytes are identical to this head's. The bot's own drive at `a15508b7a` pinned 31 more `killed_by` rows (all `tests/features.py` except `structure.py`/`config_flow_steps.py` pins from round 4).

## Null control

`early_cutoff.py:224` -- `# Exempt only if it exists AND reads on, not either.` -- is the pin drive's built-in null control (#1521): the CI drive at `fdbf59f63` printed `null control ... early_cutoff.py:224 NULL_COMMENT survived every driver` in all seven shards before grading any mutant, so every kill above is measured on a pool the control proved sensitive. The `264` skew arm above is this round's behavioural null control (an arm that must not move, and does not).

## Architecture score

- `coord_footprint` 2586 -> 2587: the early cut-off's freeze guard is one `if` in `_tail_free` (`coordinator.py`) -- the feature's own actuation seam, held there because the slab observer ignores only the unmetered reason and must see the cut (live-fix design note A2). The same diff deleted the coordinator's `_on_off_service` helper and routed the switch write through `pump_arbiter.switch_supply` (13 net coordinator lines removed); the one added logic statement is the feature itself, not a payable debt.

## Figures

Stamped against `origin/main` `969c3a5c8`, taken 2026-10-10T19:54Z (rule: figures below are functions of that tip; re-take after any merge of main):

- Deterministic ratchet at this head (no mutant): `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --scope changed --base origin/main` -> `MUTATION TABLE REFUSED -- 4612 unpinned site(s) against 4608 at the ratchet base 969c3a5c8..., 4 of them added by this diff` (`early_cutoff.py:251 CMP_BOUND*2`, `:275 CMP_BOUND`, `:304 GUARD_OFF`). The two `:264` sites this diff's `survivor_triage` row covers fell out of the refusal; the remaining four are killed by named `tests/features.py` checks (## Mutation proof) and their `killed_by` rows are the canonical Linux `mutation-autofix`'s to record at this head -- the loop guard on the bot's own `ci:` head is why it has not.
- Round-6 drive: `python3 tools/audit/seat/verify_eight.py HEAD "251 CMP_BOUND" "264 CMP_BOUND" "275 CMP_BOUND" "304 GUARD_OFF"` at this head -> `total 6 killed 5 survivors 1`, the one survivor the triaged `264` skew twin (the verifier prints one line per arm and a `total/killed/survivors` summary; the full log is `r6-verify2.log` in the seat evidence).
- Architecture score: `python3 -I tools/audit/archscore/score.py --diff origin/main HEAD` -> `dS -0.0006 WORSENS (inadmissible: coord_footprint 2586->2587)`, the one rise, explained under ## Architecture score (the `arch-score` gate passes a rise so explained; its `--self-test` case set pins that rule).
- Structure ratchet: `python3 tests/structure.py` -> `max_class_loc 8811 <= 8811`, `seam_cut_total 762 <= 762`, `STRUCTURE RATCHET PASSED`.
- D6 claims census on this head: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` -> `arch_modules_on_disk=76`, `arch_map_listed=76`, `arch_map_missing=0`, `ha_module_level_importers=28`, `claims_true=123` -- unchanged from round 5's figures (the main merge touched only `dev/` and `docs/`).
- Scoped gate: `python3 tests/closure.py select --diff <merge-base>` -> `MODE: SCOPED -- 23 script(s) run, 10 scoped out`.
- D12-s2 surfaces (round 3's, carried): `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round9/D12/s2/surfaces.py --perturb` -> 0 failing cells baseline, 2 under `--perturb`; the production lines it drives are byte-identical at this head.

## Unpinned sites

The deterministic census adds four unpinned sites at this head; each is killed by a named `tests/features.py` check measured this round, and its `killed_by` row is recorded by the canonical Linux `mutation-autofix` at this head (features.py is BLAS-red on this seat, `R9-F2.1 P3`, so `--pin-killed` is INCONCLUSIVE here -- round 5 measured the same wall):

- custom_components/heatpump_optimizer/early_cutoff.py:251 CMP_BOUND*2: both bounds killed (first-step and ragged-plan checks, ## Mutation proof).
- custom_components/heatpump_optimizer/early_cutoff.py:275 CMP_BOUND: killed by the round-5 exact-boundary check (## Mutation proof).
- custom_components/heatpump_optimizer/early_cutoff.py:304 GUARD_OFF: killed by the round-5 hold checks (## Mutation proof).

The `:264` sites are not in this list: the line's two bounds share one ledger anchor, one is killed by the new MIN_ON check and the other is the triaged equivalent, so the anchor's only expressible disposition is the `survivor_triage` row committed here (`_cycle_guard.CMP_BOUND.ea4781b3.json`, verdict `equivalent`, reason naming which twin survives and which the new check kills).

## Red checks

- `mutation` (red at `a15508b7a`, this pass's cause): the census refused on 6 added sites; the bot's drive had pinned 31 but measured 4 surviving (`251` one twin, `264` both) and skipped 2 for `--budget-minutes` (shards 4 and 7, `skip-budget` on the last site each; the `ci:` head's loop guard admits no second pass). Cheaper detector and standing cost: the deterministic census (`tests/mutation_table.py --scope changed`) names the unpinned sites in seconds before any mutant, and did; what it cannot name is a mutant no driver kills -- that measurement is the mutation lane's own (~100-minute sweep), which is what this diff gives new killing checks to. The `skip-budget` sites are the instrument finding under ## Friction.
- `arch-score` (red at `a15508b7a` and at the two heads before it): `coord_footprint 2586->2587`, the cut-freeze `if` in `_tail_free` -- explained under ## Architecture score; the rise is the feature's own guard, and the same diff removed 13 net coordinator lines. Cheaper detector: the gate itself runs pre-push (`tools/audit/archscore/score.py --diff origin/main HEAD`, ~30 s here) and its failure text names the section that explains a rise; this body now carries it.
- `pr-contract` (red at `a15508b7a` and earlier): the consequence of the two above -- the body did not name `arch-score` in this section. Named and answered here; no separate cause.
- `fast (3.14)` (red at earlier branch heads `b731ef6b3`, `f74924e09`; green at `a15508b7a` and at `a9b1b48c4`): the round-1/2 failures (`entities.py` unclassified `early_cutoff.py`, `harness_headers.py` stale arch headers, `layout.py` moved-path guard, a stale ledger disposition) were each fixed in their own round by the diff that introduced them; every failure was reachable pre-push by an existing selectable script the scoped gate runs in seconds to ~2 minutes. Not red at any head this body describes.
- `mutation-autofix` (red at `f74924e09` only): `skip-measure-failed` -- the missing null control round 4 added. A repair path, not a detector; owes no cheaper detector of its own. Green (`changed`, 31 rows) at `fdbf59f63`.
- `nightly-status`: grades `main`'s nightly; this diff touches nothing it reads (its exemption in `policy_lint.mjs`), so its red is the orchestrator's on `main`.

## Forward-carry

`none` -- the shard-precedence and budget-overrun findings below are instrument defects in the mutation lane's own jobs, not constraints on a stage that has not started; their home is the #201 root-cause path (`defect-root-cause.md`), already named there by the round-6 reviewer. The null-control requirement a later seat re-running `--pin-killed` needs is in the tree (`early_cutoff.py:224`).

## Friction

- `ci-autofix`: unenforced: two gaps in one head. (1) `merge_pin_shards` folds shard statuses by `min()` over `_SHARD_PRECEDENCE` (`tests/mutation_table.py:1054-1055`), so a shard that pinned 3 outranks the honest `skip-budget`/survivor reports of its siblings; (2) the `--budget-minutes` overrun leaves a site NOT RUN rather than red, and the `ci: pin killed mutants` loop guard then forbids the retry -- a PR can stay red on sites no bot pass will ever reach. Evidence: `mutation-pins (4)` and `(7)` job logs at run 38059652436 (`PIN KILLED: 3 pinned, 3 left unpinned (2 survived, 1 not started for the budget)`); destination: #201 root-cause seat.
- `gate-scoping`: cost: the update-branch merge to `origin/main` can conflict in `tests/closures.json` (Linux-`recorded` table re-sorted and re-hashed off-branch); the compliant route is the driver `--resolve` (set-union of already-recorded lists), never hand-merging recordings off Linux. This round's merge (`969c3a5c8`) carried no such conflict.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
