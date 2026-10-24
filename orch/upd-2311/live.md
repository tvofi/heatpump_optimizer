R10-ARCHSCORE-COVERAGE, part 2 of 5: the hub census sees readers, returned values, rebinds and event callbacks (roster items 4 and 7).

Part of #2235.
Part of #2259.

**Stacked on #2293** (part 1). This branch contains part 1's head `87d54712cfbd12d6a1b3e4cec2db350c2dbfa221` merged in, so until #2293 merges, its diff against main includes part 1's. The part-2 delta alone is `git diff 87d54712cfbd12d6a1b3e4cec2db350c2dbfa221...HEAD`. This part depends on #2293's `expected.json`, so it merges after #2293.

What changes. Two counters, each with an ablation switch (`ARCHSCORE_ABLATE`):

- **C15 (item 4, D7-s1-83)**, in `metrics/common.Engine`:
  - A call evaluates to what its callee returns (`_call_roles` / `_returns`). This covers methods of a class a role names and package functions, with parameters bound to the call's argument roles. It is memoised and recursion-guarded.
  - A hub handed to a collaborator's constructor as a zero-argument reader is that hub wherever `self.F()` is read (`readers`). The reader can be `lambda: _ctx_of(self)._thermal_params` or a reference to a coordinator method taking only `self`.
  - A coordinator collaborator's attribute rebound to a hub is the hub (`_derive_rebinds`). The rebind can be direct (`ctx._thermal_model.params = ctx._thermal_params`) or go through a local the hub is also rebound to (P1's `_publish_params`).
  - Before, `_derive_aliases` followed only constructor arguments that were paths, and `ev` read every call as nothing. ARCH2-s1's P1 prototype therefore hid three spellings: `via_live_model`, `via_guard_reader` and `via_learner_reader`.
- **C16 (item 7, ARCH2-s2 P4's instrument half)**, in `metrics/hub_solve_writes`: a coordinator method handed to code outside the package is a root (`event_roots`; `roots()` is the one list both the metric and `tests/arch_score_head.py` read). Code outside the package means a Home Assistant event, MQTT or timer subscription, which calls back with the live hubs. Before, the census rooted at the cycle and the two solves only, so the ECL110 state message's and the meter event's in-place hub writes were counted by no score metric. A callback handed to a package function is reached from wherever that function is, so it is not a root of its own.

Today's tree: `hub_solve_writes` 38 -> 41. The three new sites are the ECL110 handler's two displacement fields and the meter event's `peak_guard_active`, the same three ARCH2-s2's `event_hub_writes.py` names. `tests/arch_score_head.py` lists them in `CYCLE_HUB_WRITERS` as producers at the event that moved them, with why. Nothing else moves on today's tree: main spells every hub handle as a path, so C15 closes the spellings the next refactor would use.

Calibration:
- **C15**: planted BAD and GOOD `a3_hub_reader_control` / `_fix` (the DHW learner holds the hub as a lambda reader and writes one more field through it), and attempt `rt_19_hub_reader_lambda`.
- **C16**: planted BAD and GOOD `a3_hub_event_write_control` / `_fix` (the ECL110 handler writes the live state instead of its own slot), and attempt `rt_20_hub_write_event` (a solve's hub write moved into the meter event).
- The rebind and returned-value spellings are pinned on a synthetic package in `tests/arch_score.py` (`hub_spellings`), with two nulls: a reader returning a collaborator, and a callback handed to a package function.
- `expected.json` gains those six cases. No recorded verdict moved, no weight changed, and no weight perturbation moves a verdict.
- C16 changes every stored corpus vector's `hub_solve_writes`, so `corpus_vectors.json` was re-measured (`--only-metric hub_solve_writes,shared_inplace_writes,footprint`): +3 on 74 trees, +2 on 11, +0 on 2. `shared_inplace_writes` and `coord_footprint` re-measured byte-identical.

Alternatives considered:
- A name list of event roots, like ARCH2-s2's harness's three, lost to the structural rule, which needs no edit when a callback is added.
- Making event roots a separate score metric lost to widening `hub_solve_writes`' roots. That has C13's precedent (the cycle joined the solves for the same reason), and the census asks one question: which live hub writes the runtime reaches.
- Rooting at every coordinator method lost: setup-time writes are not the #1736 hazard, and they would make the head check's producer table meaningless.
- For C15, a list of reader spellings lost to evaluating the callee's return, which reads any spelling the role engine can already evaluate.

## Head

`f687e6175e44dd21c691e04b43ed0e5fdd51602d` merges main `25afc1c` into the previous head: an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged.

`16806d6be5f03fd3bb1f4e5e334353dfda7ac9b5` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2311.md`. The authored code head is `1348109737a306eabcccf088af7e35d4c10c8c45`.

`ab10e156042e10d777b739068aa02c4eb24e4bf8` merges origin/main `c42d7cea6` into the authored code head `1348109737a306eabcccf088af7e35d4c10c8c45` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`1348109737a306eabcccf088af7e35d4c10c8c45` (part 1 `87d54712c` and origin/main `98fe51b42` merged in; measured `2026-10-15T22:23Z`)

## Mutation proof

Each mutant was applied in place on the committed head, run, and restored with `git checkout` (script `mutate_p2.sh` in the seat's scratch). The runners were `calibrate.py --only` the six new cases plus `a3_hub_solve_writes_*`, then `tests/arch_score.py --stored` (which runs `hub_spellings`), then `tests/arch_score_head.py`. M0 (no mutation) moved no case it ran, and both scripts passed.

- M1, `ev` reads a call as nothing (the `_call_roles` return deleted). MOVED: `a3_hub_reader_control` (WORSENS -> IMPROVES), `a3_hub_reader_fix` (IMPROVES -> NULL), `rt_19` (NULL -> IMPROVES). `hub_spellings` FAIL: the zero-argument reader method, a package function's returned value, and the lambda reader handed to a constructor (3 of 72).
- M2, readers not recorded. MOVED: the same three. `hub_spellings` FAIL: the lambda reader (1 of 72).
- M3, rebinds not derived. `hub_spellings` FAIL: the direct rebind and the rebind through a local (2 of 72). No calibration case moves. ARCH2-s1's `census_probe.py --tree proto` reads `via_live_model` seen=False under this mutant, so the finder's harness pins it too.
- M4, `event_roots` returns nothing. MOVED: `a3_hub_event_write_control` (WORSENS -> NULL), `rt_20` (NULL -> IMPROVES). `hub_spellings` FAIL: the event callback (1 of 72). `tests/arch_score_head.py` FAIL: "every listed producer is still reached", with the three event rows stale (1 of 16).

## Null control

- With the counters off (`ARCHSCORE_ABLATE=C15,C16`, the base definitions), every new case reads wrong: `a3_hub_reader_control` (BAD) IMPROVES, `a3_hub_event_write_control` (BAD) NULL, and `rt_19` and `rt_20` IMPROVES. `ARCHSCORE_ABLATE=C15` reopens only `rt_19` and the reader pair; `C16` reopens only `rt_20` and the event control.
- Honest code: no recorded corpus, planted or red-team verdict moved under the re-measured vectors. The synthetic nulls read 0 sites. ARCH2-s1's `census_probe.py --tree main` reads every probe seen at both ends; `control_hub_direct` and `via_local_alias` read seen at both ends on both trees.

## Figures

Finder's harnesses, run from their round-10 exports at the base (`git worktree` of `694120d5a`) and at the head, `PYTHONPATH=tests/hastub`, the harness directory copied into each tree, because it locates `tools/audit` from its own path:

- `$EXPORT1/dev/audit/rounds/round10/D7/arch2-s1/census_probe.py --tree proto` (`$EXPORT1` = `git archive 2c30ada11 dev/audit/rounds/round10/D7/arch2-s1`; sha1 6af1fc4923d0476ef047fe65c38bf47fd5325712): via_live_model, via_guard_reader and via_learner_reader seen=False -> seen=True. The base read 23 -> 23 for each of the three blind probes.
- `$EXPORT2/dev/audit/rounds/round10/D7/arch2-s2/event_hub_writes.py` (`$EXPORT2` = `git archive fabaf4664 dev/audit/rounds/round10/D7/arch2-s2`; sha1 fc4450097b04fcc6434adc057ee03445a1aa3bc2): event_hub_inplace_writes 3 at both ends, and 0 with `--patch P4_event_readings_published_whole.patch`. The harness roots its own census at the three named callbacks, so it reads the same at both ends by construction. The companion is the metric itself, on the same tree: `census_probe.py --tree main`'s `base hub_solve_writes` reads 38 -> 41. The three new sites are the ones `event_hub_writes.py` lists. (`score.py --diff origin/main` reads NULL, because the package is unchanged and the gate measures both sides with one instrument.)
- Calibration: `python3 tools/audit/archscore/calibrate.py` at the head. The rule: only the six new cases are not in part 1's `expected.json` (`--record` printed RECORD for those alone), every new case classifies as its label says, and no `SENSITIVE` line is printed.
- Corpus: `calibrate.py --measure-corpus --only-metric hub_solve_writes,shared_inplace_writes,footprint --jobs 4`: 87 vectors ok, 0 errors. The per-tree deltas are above.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` -- MODE: SCOPED, naming `tests/arch_score.py` (204 checks passed), `tests/arch_score_head.py` (16 passed) and `tests/entities.py` (2325 passed after the re-record below). Plus `run.sh`'s `run_always` scripts, `tests/structure.py`, and `tools/audit/seat/tmp_paths.py --check`.

Class seams (step 8). The rule is every place the role engine turns an expression into a role (`grep -n "def ev\|def step\|def _bind\|def _derive\|def callees\|def references" tools/audit/archscore/metrics/common.py`), and every root list (`grep -rn "ROOTS\|roots(" tools/audit/archscore tests/arch_score*.py`).
- `ev`'s Call branch: closed (C15).
- `_derive_aliases`: readers closed (C15); rebinds: closed (C15).
- `callees` and `references` already resolve methods and callbacks.
- `ROOTS`' two readers, `hub_solve_writes.measure` and `arch_score_head.hub_writers`, now both read `roots()`.

Residuals, each named:
- A computed attribute name (`getattr(self, name)`) stays C2b's tripwire (`rt_13` reads WORSENS as recorded).
- A nested closure handed to Home Assistant (`pump_arbiter`'s `_changed`) is not a package function, so it is not a root. It writes no hub today.
- A property returning a hub is an attribute read, which `step` does not follow.

## Raise justification

`tests/ci_budgets.json` `archscore.hub_solve_writes` 38 -> 41: only that row and `recorded_at` move, with the reason in the commit message and the `reason` field. Precedent: 4d6d329e5. Approved by the orchestrator under mandate 6175172275 before the push; a raise in a `*_budgets.json` merges only on the owner's approving review at its head (budget-raise-gate, 0013).

The cause: no package code changed. C16 makes the census count three in-place hub writes the package already makes: `_async_handle_ecl110_state_message`'s `ecl110_effective_displace` and `ecl110_displace_command`, and `_on_power_event`'s `peak_guard_active`. Measured with `ci_ratchet.archscore_metrics()`: it is the only row that grows at this head. `coord_footprint` (2580 vs 2592) and `coordinator_multiassigned_attrs` (118 vs 120) already sit under budget at main.

Payments considered, and why each lost:
1. Retire the three writes in production (ARCH2-s2's P4 prototype, "event readings published whole", 3 -> 0). That edits `coordinator.py`, which is R10-ARCH-LIVESTATE's files, so the owner's 2026-10-15 ruling forbids widening this PR to it. It is carried there instead, to lower this row by 3 in the same PR (`## Forward-carry`).
2. Count event roots in a separate metric. `ci_ratchet` derives every vector key and refuses a key with no row as growth, so this needs a new row at 3 anyway, and it splits one question (which live hub writes the runtime reaches) across two censuses.
3. Allow-list the three sites. `fixer.md` step 14 refuses it: the key would blind the census at the sites it exists to watch.

Payments tried: each of the three below was considered and measured or reasoned; none lands this change soundly inside this group.
- (1) Retire the three writes in production: R10-ARCH-LIVESTATE's files (`coordinator.py`), carried there to lower this row by 3.
- (2) A separate event-root metric: still a new budget row at 3, and one census split in two.
- (3) An allow-list of the three sites: refused by `fixer.md` step 14, because it blinds the census where it watches.

Architecture score: dS +0.0000 NULL (`python3 tools/audit/archscore/score.py --diff 25afc1c77 f687e617`, run with `f687e617`'s own instrument, against the head's merge base with origin/main)

`Architecture score: dS +0.0000 NULL` (`python3 tools/audit/archscore/score.py --diff origin/main`): the package is unchanged and the gate measures both sides with one instrument. The instrument before and after on today's tree (`census_probe.py --tree main`'s base line, or `metrics/hub_solve_writes.measure`): `hub_solve_writes` 38 -> 41, with every other vector key unchanged.

## Unpinned sites

n/a for production code: the diff touches `tools/audit/archscore/` and tests only. The new predicates are pinned by the calibration cases, `hub_spellings` and the head check (M1 to M4 killed).

## Architecture score

n/a: no package file changes; the instrument change takes effect after merge (`ABOUT.md`).

## Red checks

- `tests/entities.py`, the ci-ratchet null control "and main() passes the committed table at its own recorded count (the null control)": red locally at `880373298` (1 of 2325), before the re-record. It is the ratchet's own null control firing on the definition change this PR makes deliberately, and the re-record above answers it (2325 of 2325 pass after). No cheaper detector exists: this check is the cheapest one that sees a budget row go stale.
- `budget-raise-gate`: red by design until tvofi approves at the head, because this PR raises one cap (`tests/ci_budgets.json` `archscore.hub_solve_writes` 38 -> 41; see `## Raise justification`). The orchestrator posts the owner-gate approval under mandate 6175172275 once the reviewer returns merge. No cheaper detector exists: the gate is the owner's approval itself, and its standing cost is one review per raise.

## Forward-carry

- R10-ARCH-LIVESTATE: retire the three event-callback hub writes (ARCH2-s2 P4, "event readings published whole", 3 -> 0), and in the same PR lower `tests/ci_budgets.json` `archscore.hub_solve_writes` by 3 and drop the three event rows from `tests/arch_score_head.py`'s `CYCLE_HUB_WRITERS`. The exact carry text was sent to the orchestrator for that group's roster brief, in `dev/programme/rosters/wave-r10-groups.json`'s R10-ARCH-LIVESTATE `carry`. This PR does not merge until that carry is on main.
- R10-PARAMS-OWNER re-measures D7-s1-82's score credit on this extended census, as the roster carry requires. The catch-up judge's note says P1's delta-S was partly this blind spot. The carry is already in `dev/programme/rosters/wave-r10-groups.json`'s R10-ARCHSCORE-COVERAGE `carry`, and it is discharged when that group runs after this merges.
- For R10-BRIEFS-FOLD: the D7 brief may cite C15 and C16 (`tools/audit/archscore/ABOUT.md`'s counter table). The orchestrator owns the roster edit and was told at handoff.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)



