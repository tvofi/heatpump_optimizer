The plan narrative now prices money in the price feed's currency (`coordinator.currency`), like every other money surface. Before this change, `_narrative_view` resolved the currency itself with `resolve_currency(hass)`, which returns the instance's label currency. A EUR feed on a SEK instance therefore published EUR sensors next to a narrative written in SEK. The local precedence is deleted, and the view reads the one value that `currency.py`'s `declared_currency` decides and the coordinator adopts on each cycle. The `narrative.render` docstring justified that local precedence ("A narrative line is recorded nowhere, so it can simply follow the instance"), and it is rewritten to state the new contract (fixer.md step 9).

The price-units comment in `_audit_price_units` named a nonexistent ``money_currency``. It now names what the sensors actually carry: `unit_of_measurement` and the `currency` attribute. The comment in `_raise_cop_issue` said the notice is priced "in the instance currency"; it is priced in the feed's, and the comment now says so.

Fixes #2243
Fixes #2222

#2243 is D14-s3-01, with D14-s2-01 merged into it. #2222 is D5-s3-01.

### Round 3: the seam cut is paid by a real move (orchestrator decision, mandate 6329234399, session s4)

The narrative's read of `self.currency` from the `views` seam costs `seam_cut_total` +1, because `currency` is stored only by `core` units. Round 2 paid it with a local alias in `_raise_cop_issue`, and review blocked that as metric-gamed: an alias cuts an occurrence count and no coupling. The orchestrator withdrew that route. This round:

- **The alias is gone.** `_raise_cop_issue` reads `self.currency` twice, as at the base. The corrected comment and the narrative fix stay.
- **The payment is a move.** `_scores_view` (`views`) reached into two private attributes of the `learning` seam, `_cop_baseline` and `_cop_health_cusum`, to recompute a watched-bucket count that `_learning_view` (`learning`) also computes, with a different guard (`_learning_view` checks `np.isfinite`, `_scores_view` did not). A new `learning` method, `_cop_watch()`, returns both the watched-bucket count and the Cusum's share of the alarm. `_learning_view` and `_scores_view` both call it, and `tests/seam_map.json` places it in `learning` (fixer.md step 12). The views seam now asks the COP watch for its grade through one call instead of reading the watch's state. The count has one definition, and the coordinator class is 10 lines shorter.
- **No budget is raised.** Step (3) of the brief, the conditional `seam_cut_total` raise, does not apply. `seam_cut_total` measures 707 against a budget of 708, and `class_excess_loc` and `max_class_loc` drop 11 each. `tests/structure.py` exits 2 on an unrecorded gain, so the three gains are recorded downward with `tests/structure.py --record`, in their own commit with the reason in its message. No row moves up.
- **Against #2647.** At origin/main `a7cf60cfd`, #2647 (R10-SCORES, which raises `seam_cut_total` 708 -> 714) has not landed, and main's budget reads 708. If #2647 lands first, the `seam_cut_total` line in `tests/structure_budgets.json` conflicts. The resolution is main's value less this diff's net -1 (713 if main reads 714), re-measured with `tests/structure.py` at the merged tree, not 707 carried over.

Payments tried, each measured with `tests/structure.py` and `tools/audit/archscore/score.py`:

| payment | seam_cut_total | dS | disposition |
|---|---|---|---|
| route-1 alias `currency = self.currency` (round 2) | 709 -> 708 | +0.0000 NULL | withdrawn; review showed a planted alias moves the metric the same way |
| threading `currency` from `_build_data_dict` into `_insight_view`/`_narrative_view` as a parameter | not built | not built | rejected unbuilt: a re-binding of the same read inside one seam, which the brief rules out as a payment |
| `_cop_watch()` in `learning`, shared by `_learning_view` and `_scores_view` | 709 -> 707 | +0.0000 NULL (`--diff 0ebc7cf1e HEAD`) | taken |

The move pays 2: the `views` reads of `_cop_baseline` and `_cop_health_cusum` each counted on both sides of the seam, and the one `views -> learning` call that replaces them counts 2.

Carries settled in this diff, so none is forwarded:

- R10-FEEDS carry (callers of `_get_current_price` / `_current_spot_price` must handle `None`): this diff touches no such call site. Nothing to carry.

## Head

**Round 5 fixer, R10-CURRENCY: STOPPED at the raise. The code is on `handoff-wip/r10-currency-r5` at `5115ddc15`, not on `handoff/`.** The PR head is still `0b9431baec2ff7b57dceadf6ed5ef56da1d25a25`. Measured against origin/main `a6620c30adcdf0d9529ee66977694bfa2a06d5c3` on 2026-10-23 at 11:19 UTC. The orchestrator rules on the raise below under mandate 6329234399 before any of it reaches the PR.

`9195247d4b9997512af420d27016f72ae15e91d2` merges origin/main `a6620c30a` into `0b9431ba`. It uses the same resolution as the conflict fixer's local `baf3d2dd`, redone from scratch:
- **`_learning_view`'s `cop_health.watched_buckets`.** Taken from main: `_watched_cop_buckets(self._cop_baseline)`.
- **`_scores_view`.** Taken from main: `compose_scores(envelope_score(...), machine_score(...), ...)`, with the `advice` parameter.
- **`_cop_watch`.** It has no caller left, and main's `_watched_cop_buckets` and `machine_score` compute what it did. It is deleted, with its `tests/seam_map.json` entry and its four `tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._cop_watch.*.json` pins.
- **`tests/features.py`.** #2620's two machine-grade checks now pass `_rs_advice(coord)` to `_scores_view`.
- **Outside the conflict.** #2620's narrative line and its two comments merge as they are.

`5115ddc15` re-records `tests/structure_budgets.json` at the merged tree: `class_excess_loc` 18243 and `max_class_loc` 8479, each one under main's caps, and `seam_cut_total` **715 against main's 714**. That raise is the open question. The reason is in the commit message.

Re-proof at `9195247d4`, each run with `/opt/hpo/venv-ci/bin/python3` (3.14):
- `PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=1 python3 tests/features.py` printed `ALL 4334 FEATURE CHECKS PASSED` (rc=0).
- `tests/entities.py`, run the same way, printed `ALL 2406 ENTITY CHECKS PASSED` (rc=0).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 21 script(s) run, 12 scoped out.`
- At `5115ddc15`, `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`, against its own raised record.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` printed `CI PREDICT: no closures or fast red predicted against a6620c30adcd`.

Red-on-revert: each mutant is a `git archive` copy of `9195247d4` run through `tests/features.py`, and all four exit 1. Each also fails the archive runner's `#363 recorded_at` check, which comes from the runner and is left out below (fixer.md step 2).
- **#2620's side in both conflict regions, with `_cop_watch` restored** (`git merge-file -p --ours` of the 0b9431ba, merge-base and main copies of `coordinator.py`). It printed `FAIL R9-P3: every floor on a thermal parameter lives in one function with one constant ...`: #2620's re-inlined `max(house_heat_loss_scale, 0.1)` is a second floor. This is a different failing check from `baf3d2dd`'s report (`KeyError: 'reasons'`). The mutant is still red.
- **`_watched_cop_buckets` `>=` changed to `>`.** It printed `FAIL the machine grade starts at exactly COP_BASELINE_MIN_SAMPLES samples  [{19: None, 20: None}]` and main's `a COP bucket at exactly the minimum sample count is watched ...`.
- **The clip removed from `machine_score`.** It printed `FAIL a machine past the alarm threshold still grades 0, not below  [-100.0]` and its `(#2258)` twin.
- **The narrative reverted to `resolve_currency(hass)`.** It printed `FAIL D14-s3-01: the narrative prices a EUR feed on a SEK instance in EUR, and a SEK feed in SEK  [{'EUR/kWh': ['SEK'], 'SEK/kWh': ['SEK']}]`.

`0b9431baec2ff7b57dceadf6ed5ef56da1d25a25` is the orchestrator's recarry of main into the previous head (the roster PR #2655 that adds R10-STRUCTURE-ALIAS, which this body's carry names, merged). It is not a clean merge of the live head and main (the body file is not the live pull-request body), so prepr checked this head.

`b2e2b5d579b192a34d0a394e72a75e796fa3c7fe` merges main `bfd61aa` into the previous head: an automatic merge by the orchestrator, no resolution (the roster PR #2655 that adds R10-STRUCTURE-ALIAS, which this body's carry names, merged). The reviewed code is unchanged.

`72fbab2a719ce14870aa3284a35d043ea1b9588d` merges the authored code head `007ec1999b7752073cb8d550210898783582d4c8` and then merges origin/main `c26499e01` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`007ec1999b7752073cb8d550210898783582d4c8`. It is round 2's head `08ba3d9d7` with origin/main `f38f91852ea0251a9043378f76f907794874b2be` merged in, then four commits: the alias removal `0ebc7cf1e`, the `_cop_watch` move `c34bb23e9`, the budget record `34bde2120`, and a value check on the grade's clamp `e60558413`. origin/main `a7cf60cfd` was then merged in as `4731c08a4`. Round 3c added `f80d6125a` (a value check on the watch's sample bound, plus the `--pin-killed` ledger files for three sites) and `d5abe9de7` (the fourth site's ledger file). Last, origin/main `c26499e01f9d` was merged in as `007ec1999`. The two main merges bring only `tools/policy/field_coverage.mjs`, mutation-ledger files, delivery rows and `dev/programme/rosters/wave-r10-groups.json`, and no figure below reads any of them. The harness, comment_symbols and archscore figures were measured at `e60558413` (merge base `f38f91852`), 2026-10-23 04:40 UTC. `tests/features.py`, the pin runs, `ci_predict.py` and `tests/structure.py` were measured at `f80d6125a` to `007ec1999`, 2026-10-23 05:40 UTC.

## Raise justification

`seam_cut_total` needs to go from 714 to 715 against origin/main `a6620c30a`. The extra cut is #2620's own `self.currency` read in `_narrative_view` (`views`): `currency` is stored only by `core` units. The `views` row reads 110 against main's 109. #2620 paid for the read in round 3 with the `_cop_watch` consolidation. #2647 has since made that consolidation on main by another route, so the payment is gone. Every other row is at or under main's cap.

Payments tried: each one was measured on top of the merge commit `9195247d4` with `python3 tests/structure.py` and `python3 tools/audit/archscore/score.py --diff 9195247d4` (the tree). Neither was kept.
- **(b) Thread the cycle's one read from `_build_data_dict` (`views`) into `_insight_view(currency)` and `_narrative_view(currency)`**, as main does for `advice`. `seam_cut_total` 715 -> 714, `class_excess_loc` 18244 and `max_class_loc` 8480, all at main's caps. Not taken. The read and the reader stay in the same seam, and the `views -> core.currency` coupling is unchanged. Only the occurrence count falls, which is the re-binding round 3 ruled out unbuilt for this exact route and the alias class that R10-STRUCTURE-ALIAS carries. It would also break the finder's harness `dev/audit/rounds/round10/D14/s2/p8_money_units.py`, which calls `_narrative_view()` with no argument.
  Architecture score: dS +0.0000 NULL
- **(b') Hand the currency to `_build_data_dict(currency)` from its three `core` callers** (`_async_update_data` x2, `_async_first_refresh_light`). `seam_cut_total` 715 -> 713, `class_excess_loc` 18243, `max_class_loc` 8479. Not taken. It turns one read into three, each at a call site that must pass the same value, and it moves the read into `core`, the seam the metric does not price. fixer.md step 17 names that "code moved to an unmeasured path". It also widens a signature that 25 test call sites use.
  Architecture score: dS +0.0000 NULL
- **(a) Take the currency from data the views seam already holds.** Not built, because no such data exists. The views seam's only currency is `self.currency`, which `_build_data_dict` also publishes as `data["currency"]`, after `_insight_view` runs. The price sensors read `coordinator.currency` from outside the class. `OptimizationResult` carries no currency.
- **(c) A real move of a views-seam reach into core elsewhere in the class.** Surveyed by listing every cross-seam attribute reference of each `views` unit with `tests/structure.py`'s own `seam_metrics` walk, run as a scratch script. No reach is backed by a duplicated computation the way `_cop_watch` was. Main's `machine_score` already calls `_watched_cop_buckets`. The remaining cuts come in three kinds. Some are repeated reads inside one unit (`_current_action` x2 in `_build_data_dict`, `_external_heat` x3 in `_external_heat_view`), where an alias is O19. Some are reads of learning state handed to pure module functions (`_scores_view` -> `machine_score(self._cop_baseline, ...)`), where a wrapper method would be the getter ruled out in round 3 (item 931a23da). Some would only be a relabel in `tests/seam_map.json` (`async_publish_ecl110_command`), which changes no code. None was built.

The raise needed: `tests/structure_budgets.json` `seam_cut_total` 714 -> 715 (with `class_excess_loc` 18244 -> 18243 and `max_class_loc` 8480 -> 8479 recorded down), as committed in `5115ddc15` on `handoff-wip/r10-currency-r5`.

## Mutation proof

Each mutant was run from a `git archive` copy of the head, with `PYTHONPATH=tests/hastub python3 tests/features.py`. In every copy, `and the path that proceeds still stamps a resolvable recorded_at (#363)` also fails. That failure comes from the archive runner, not from the mutant (fixer.md step 2), so the lists below leave it out.

- **`_cop_watch` predicate.** `int(entry[1]) >= COP_BASELINE_MIN_SAMPLES` was mutated to `<`. It printed `3 of 4308 FEATURE CHECKS FAILED`: `FAIL a healthy watched machine grades 100` and `FAIL a machine at the alarm threshold grades 0`, plus the runner's #363 line.
- **`_cop_watch` share.** The return was mutated to `return watched, 0.0`. It printed `2 of 4308 FEATURE CHECKS FAILED`: `FAIL a machine at the alarm threshold grades 0`, plus the runner's #363 line.
- **`_cop_watch` clamp.** At `e60558413`, `np.clip(..., 0.0, 1.0)` was dropped from the share. `PYTHONPATH=tests/hastub python3 tests/features.py` printed `2 of 4309 FEATURE CHECKS FAILED`: `FAIL a machine past the alarm threshold still grades 0, not below  [-100.0]`, plus the runner's #363 line. At the head, `ALL 4309 FEATURE CHECKS PASSED`.
- **`--pin-killed`.** `PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py` drove the diff's four new sites. `coordinator.py:9130 BOOLOP`, `:9132 CLAMP_DROP` and `:9132 RETURN_DEL` were killed by `tests/features.py` and pinned. `:9130 CMP_BOUND` (`>=` to `>`) survived, because the existing checks seed a bucket one sample above the bound. A new check, `the machine grade starts at exactly COP_BASELINE_MIN_SAMPLES samples`, drives a bucket one short of the bound and one at it. A second run then printed `pinned   custom_components/heatpump_optimizer/coordinator.py:9130 CMP_BOUND -- killed by tests/features.py` and `PIN KILLED: 1 pinned, 0 left unpinned`. Each run's null control (`coordinator.py:509 NULL_COMMENT`) survived `tests/features.py`, and its baseline was `rc=0 failed=0`. `tests/features.py` was the only driver, because the default driver set made the run inconclusive: `tests/entities.py`'s baseline is red on this host (below).
- **Narrative (round 1, carried).** The production line was mutated back to `narrative.render(items, chosen, resolve_currency(hass))`, which gave `FAIL D14-s3-01: the narrative prices a EUR feed on a SEK instance in EUR, and a SEK feed in SEK  [{'EUR/kWh': ['SEK'], 'SEK/kWh': ['SEK']}]`. Round 2's reviewer reproduced this at `08ba3d9d7` (1 of 4303 failed). This round does not touch `_narrative_view`, `narrative.py` or that check.
- **COP notice.** `_raise_cop_issue`'s placeholder read mutated to `resolve_currency(self.hass)` fails `R10-CURRENCY: the COP notice prices a EUR feed on a SEK instance in EUR, and a SEK feed in SEK`. Round 2's reviewer reproduced this at `08ba3d9d7`. The check can still fail on that mutant now that the alias is gone: the check reads the placeholder `_raise_cop_issue` publishes, whatever the spelling of the read.
- **Failing test first.** For D14-s3-01, the check fails on its own at the base. The R10-CURRENCY check cannot fail on any shipped tree, because `_raise_cop_issue` already read `self.currency` at the base. It pins the corrected claim against the mutant above. `_cop_watch` is a behaviour-preserving move on every reachable state: a stored count is an `int` that `_learned_pair` validated, so the added `np.isfinite` guard in `_scores_view` never fires. Its pins are the existing machine-grade checks above.
- One gap: the predicate mutant changes `_learning_view`'s `watched_buckets`, and no check names that key. It is pinned only through `_scores_view`, which calls the same method. The base had the same gap.

## Null control

- The finder's harness `clean` arm (a EUR feed on a EUR instance) reads 0 mismatched seams at the base and at the head. Its `reintroduce` arm (`declared_currency -> None`) reads 14 of 14 at the base and at the head, as the brief requires.
- In both currency checks, a SEK feed on the same SEK instance gives `['SEK']` at the base, under each mutant and at the head. Only the EUR-feed arm moves.
- `_cop_watch`: the `no COP evidence means no machine grade, not a failing one` check passes under both mutants and at the head. Only the graded arms move.
- D5-s3-01: `comment_symbols.py` at base `f38f91852` lists `MISSING  custom_components/heatpump_optimizer/coordinator.py:2078 \`money_currency\``. The head's MISSING list differs from the base's by exactly that line.

## Figures

- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/s3/p8_replay_currency.py` (sha1 `1acaac172452ff43387e83cbff0f02cfcd8a5a2d`), run from each tree:
  - base `f38f91852`: `base_money_seams=14`, `base_mismatched_seams=1`, `clean_mismatched_seams=0`, `narrative_fixed_mismatched_seams=0`, `reintroduce_mismatched_seams=14`
  - head `e60558413`: `base_money_seams=14`, `base_mismatched_seams=0`, `clean_mismatched_seams=0`, `narrative_fixed_mismatched_seams=0`, `reintroduce_mismatched_seams=14`
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D5/s3/comment_symbols.py` (sha1 `19dfe7849733dce1237b685804071d9814129263`): `comment_symbols_untriaged_missing` reads 7 at base `f38f91852` and 6 at the head.
- `python3 -I tools/audit/carry_audit.py check --body BODY.md` on this body: `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`.
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`, `ok   seam_cut_total 707 <= 707`. Before the move, at `0ebc7cf1e`, the same command printed `FAIL seam_cut_total 709 > 708 (+1)`.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD` prints `Architecture score: dS +0.0000 NULL`. `--diff 0ebc7cf1e HEAD` (the move and the record alone) prints the same.
- Gate scope: `python3 tests/closure.py select --diff f38f91852 --workdir <dir>` printed `MODE: SCOPED -- 22 script(s) run, 11 scoped out.` `tests/stress.py` is scoped out. Run locally at `e60558413`: `tests/features.py` (`ALL 4309 FEATURE CHECKS PASSED`; at `f80d6125a`, with the bound check, the pin run's baseline was `rc=0 failed=0`), `tests/structure.py` (passed) and `tests/typing_ruler.py` (passed). `tests/entities.py` and the other scoped scripts were not finished locally on a machine at load ~66 and are left to CI, which runs the scoped set.
- Class enumeration (step 8): `grep -rn "resolve_currency(" custom_components/` gives the same dispositions as rounds 1 and 2. `_narrative_view` is closed. The `__init__` fallback, `_audit_price_units` ×2 and `config_flow.py` ×6 use the instance label by design. `_raise_cop_issue` never called it, and the R10-CURRENCY check now pins it against doing so.

## Red checks

- `pr-contract` was red on `08ba3d9d7` (jobs 120045400798 and 120032771136). `carry_audit.py` refused the `## Friction` item because `Carry: orchestrator.md section 5` is not a destination. The cheaper detector is `python3 tools/audit/carry_audit.py check --body <body>`, which runs locally in seconds before the push. Round 2 did not run it. This body was run through it before the push, and it reports 0 unrouted and 0 bad (below). The detector exists and costs seconds, so no countermeasure is owed beyond running it before each push.
- `tests/structure.py` (`seam_cut_total` +1) was red locally in rounds 1 and 3, before any push. The cheaper detector is the one that caught it, so nothing is owed.
- `mutation`, predicted red by `ci_predict.py` on `4731c08a4` (`ADDED UNPINNED coordinator.py:9132 CLAMP_DROP` and `RETURN_DEL`), refused this body's update at prepr. The cheaper detector is `ci_predict.py`, the seconds-long static read that `body_push.sh` runs and that named the sites. Round 3b answered it with prose dispositions instead of pins. The fix here is the root one: `mutation_table.py --pin-killed` pinned every new site with the check that kills it, adding a check for the one that survived. `ci_predict.py --base origin/main` at `007ec1999` now prints `CI PREDICT: no closures or fast red predicted against c26499e01f9d`, and lists no unpinned site.
- `tests/entities.py` reads `4 of 2406 ENTITY CHECKS FAILED` locally at `4731c08a4`. All four are `hb:positive_control` checks of `tests/nightly_ha.py`'s py-spy heartbeat (for example `the control rests between tries ... [two tries took 0.80s against a 1.0s rest]`). This host's py-spy sampling and load cause them. The diff touches neither `tests/nightly_ha.py` nor the heartbeat, and CI's `fast` lane runs `tests/entities.py` on Linux.

## Unpinned sites

none

## Forward-carry

- `tests/structure.py`, `seam_metrics`: the structure instrument counts cross-seam attribute-reference occurrences, not distinct attributes. Aliasing a `self.<attr>` read into a local therefore lowers `seam_cut_total` with no structural change: round 2's reviewer planted `prices = self._prices` and measured -2. Every seam-cut payment is exposed to this. The group that owns `tests/structure.py`, R10-STRUCTURE-BLIND, is at stage `done` on both origin/main and origin/handoff/audit-r10-roster, so no live group owns it. It is therefore carried on a new group, R10-STRUCTURE-ALIAS, together with round 3's rule-14 finding (a bare getter returning a tuple of state reads also pays, item 931a23da). Landed on `handoff/audit-r10-roster` at `9169bb83487c5c6fe35596e1952347c07fdedbca`. This PR does not fix it. Carry: R10-STRUCTURE-ALIAS (item 931a23da)

## Friction

- fixer.md-step17: contradiction: the architect note's mandated shape (read the one owner from the `views` seam) cost `seam_cut_total` +1 at zero headroom, and it took three dispatch rounds to find a real payment. Carry: dismissed: ruled by the orchestrator under mandate 6329234399 in round 3; no later stage owes a change



