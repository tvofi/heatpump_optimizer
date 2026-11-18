Part 3 of R11-OUTSIDE-HONEST-STARTS-RUNS, the default start price for a clamped install. The finding is from Bankaifan's outside pull request 3529. Since 38c254f3fb, an install with `clamp_planned_levels` on and no configured start price prices no start. Its committed plan can then hold more starts than the duty-cycle plan it replaced: on the parent's grid cell, 2 starts became 5. From this change, such an install plans at 0.1 per start.

## Owner's decision

- **Ruling Q2, step 1** (tvofi, 2026-11-15, verbatim choice: "Yes, measure then build (Recommended)"): measure first, then build only at the value the owner picks. Step 1's measured ladder is the `defaults` mode of `dev/audit/harnesses/r11_honest_starts_runs.py`, published in BLOCKED.md at 88b8618ef6 on `handoff-wip/r11-outside-honest-starts-runs-p3`.
- **The value, 0.1.** The orchestrator decided it under the owner's delegation for the night, recorded 2026-11-16T23:08Z in this seat's dispatch. The owner may overrule it at review. The ruling's text: "the default start price for a clamped install with no configured start price is 0.1, the smallest measured value that restores both regressed rows (grid 5->2, everything_on 5->4 starts) with the lowest room unchanged."

### The brief's carries

- **Carry 0** (whether a clamped install that prices no start should carry a default start price): answered by the ruling above, and built here. It is `OptimizationConfig.start_price` at `CLAMPED_DEFAULT_START_PRICE` 0.1.
- **Carry 1** (owner ruling Q2: measure candidate defaults with the 2-to-5 grid row as the failing case and a priced install as the null control, then build at the picked value):
  - The measurement is step 1, at 88b8618ef6.
  - The build is this head, at 0.1.
  - The failing case and the null controls are re-run at both ends under `## Null control` and `## Figures`.

### Where the default lives, and which installs it reaches

The default lives in `OptimizationConfig.start_price` in `custom_components/heatpump_optimizer/optimizer.py`, the one value every solve prices.
- **The rule.** It returns the configured `cycling_cost`. On a clamped install (`clamp_planned_levels`) whose configured price is not above zero, it returns `CLAMPED_DEFAULT_START_PRICE` (0.1) instead.
- **Readers.** All seven optimizer readers that read `opt.config.cycling_cost` now read it.
- **Why not the alternatives:**
  - *The coordinator's `_effective_cycling_cost`*: the coordinator orchestrates and does not compute. The optimizer's own comment on `cycling_cost` requires that the objective a harness builds directly is the objective that ships, and goldens, harnesses and `tests/validate.py` build the optimizer without the coordinator.
  - *The options field default* (`DEFAULT_CYCLING_COST` in `const.py`, read by the `config_flow.py` field and `entry_config.py`): it reaches only entries whose options lack the key. It would also reach unclamped installs. And it needs a migration that cannot tell an install that chose 0 from one that kept the default.
  - The option default stays 0; `const.py`'s comment says so and names the exception.

Which installs it reaches:
- **Reached:** every install whose solve is clamped and whose effective price is zero, existing ones included. The coordinator passes `max(configured, wear price)` under the wear autotune, so a wear price above zero is used as it stands, even below 0.1. The clamp is set by `levels_clamped`: the `clamp_planned_levels` option, or the install probe when that is absent.
- **Not reached:** an install with a configured price above zero, below or above 0.1 (the null rows below), and an unclamped install at zero.

**User action and migration: none owed.** No option, default or stored value changes.
- What changes for users: on an install that cannot duty-cycle, a configured 0 now plans at 0.1 per start, and a true zero is no longer available there (the field's minimum is 0). This is user-visible, so it goes first in the release notes, under "Action needed": "None. An install that cannot run below its minimum power and prices no compressor start now plans each start at 0.1, so committing its plan to whole runs (pull request 3602, from Bankaifan's pull request 3529) no longer plans more starts than before; set Cost of one compressor start above 0 to choose another price."
- `docs/configuration.md` and `docs/how-it-works.md` state the rule.

### What was deleted

`_commit_runs` returned the relaxed plan unchanged for an engaged solve with no start price whose projection changed nothing. That case is now unreachable: `_engaged` is a start price above zero or a clamp, and a clamp now implies a start price above zero. The early return and its docstring clause are deleted.
- **`_engaged` keeps its `or clamp_planned_levels` arm** even though it is now redundant. A future default of 0 must not stop clamped installs from being committed to runs.
- **Two existing checks that used the clamped, unpriced cell as a fixture are re-anchored:**
  - The realizable-plan selection fixture is now the plan the same house ships with the default patched to zero.
  - The null control's identity arm is now an unengaged solve. An engaged one has no identity left.

## Head

1b76f567ea07bba3ef0840c2307ad4751248f1b4, merge base b425502da8d15c43f9494412e686a3d852b74358. origin/main tip 2d7161a4b70923da910f9997e18db632c0d4ec2d at 2026-11-17T00:23:03Z (`date -u`).

## Mutation proof

The mutant deletes the fix's two production lines in `OptimizationConfig.start_price`:

```
if self.clamp_planned_levels and not self.cycling_cost > 0:
    return CLAMPED_DEFAULT_START_PRICE
```

Command: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py 'R.section("R11-OUTSIDE-HONEST-STARTS-RUNS: the start count' '# --- #3616: an implausible slab seed'`. Result: 2 of 54 failed.
- `FAIL the start price a solve plans with: the configured price, except that a clamped install configured at zero plans at the clamped default 0.1; ...`, with `(0.0, True): 0.0`.
- `FAIL failing case: the grid cell clamped at no configured price ships the plan it ships configured at the clamped default, with no more than the 2 starts ...`, with `[edges 5, at the default 2, default patched to zero 5]`.

Restored, the same command prints `ALL 54 FEATURES BLOCK PASSED`.

**Diff mutants (prepr step 6d).** `MUTANT_CMD` was `env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py 'from types import SimpleNamespace as _DspNS' '# --- #3616: an implausible slab seed'`, which runs the duty-switch section and the honest-starts section. Result: no `SURVIVED` line.
- Null control: with the honest-starts block alone as the command, 7 survived, all in the duty-switch lines: 248 GUARD_OFF, CMP_BOUND and CONST_SWAP; 450 GUARD_OFF, CMP_BOUND and CONST_SWAP; 363 STMT_DEL. The duty-switch section is what kills them.

**Failing test first.** The same command on the base tree (b425502da8) with only `tests/features.py` changed fails 3 of 54:
- the two checks above: `start_price` is absent, and `[edges 5, at the default 2]`;
- `every optimizer reader of the start price reads start_price ...` with `[7 raw readers]`.

## Null control

On the unmodified tree, the harness's `defaults` mode applies the measured rule itself. At the head, it patches `om.CLAMPED_DEFAULT_START_PRICE` to each candidate and the tree's own rule applies it. So at the head the null rows test the shipped rule and do not hold by construction.

At both ends, each null pair is solved with the default at 0 and at 10.0:

| install | starts at both defaults | array-equal |
|---|---|---|
| priced clamped grid (0.25) | 2 | True |
| priced clamped `cycling_cost` (1.5) | 4 | True |
| priced clamped `everything_on` (0.5) | 4 | True |
| unpriced unclamped grid | 3 | True |
| unpriced unclamped `cycling_cost` | 7 | True |
| unpriced unclamped `everything_on` | 4 | True |

The harness prints `null pairs that differ 0`, and would print a non-zero count and exit 1 on any difference.

In `tests/features.py`, the `start_price` check pins the configured price kept at 0.05 and at 0.25, clamped and unclamped, and zero kept unclamped.

## Figures

The harness is `dev/audit/harnesses/r11_honest_starts_runs.py`, sha1 02db0c09c2a54545f840c23d8a7a4de69275aecf, the same file run at both ends.
- Command: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_honest_starts_runs.py grid|defaults`.
- Starts are off-to-on edges of the combined draw.

**`grid`, the clamped, unpriced row (p_min 1.1, loss 0.4):**
- Base b425502da8: edges 5, energy_kwh 2.93, objective 7.6826.
- Head: edges 2, energy_kwh 2.75, objective 7.8664. This objective includes 2 starts at 0.1, so it is not comparable with the base's.
- Null: the priced clamped row (0.25) reads edges 2, energy_kwh 2.75, objective 8.1664 at both ends. The unpriced duty-cycle cells entering the stage number 0 at both ends.

**`defaults`, the clamped install configured at zero.** Head and base print the same ladder; the head's default 0.0 row is the base tree's behaviour.

| candidate | grid: starts / energy / pcost / room | everything_on | cycling_cost |
|---|---|---|---|
| 0.0 | 5 / 2.93 / 1.4128 / 20.19 | 5 / 69.57 / 63.2857 / 17.91 | 7 / 42.04 / 32.0354 / 16.87 |
| 0.1, shipped | 2 / 2.75 / 1.3980 / 20.22 | 4 / 69.94 / 63.4567 / 17.97 | 7 / 42.04 / 32.0354 / 16.87 |

**Class enumeration (`fixer.md` step 8).** Rule: `git grep -n "\.cycling_cost\b\|cycling_cost=" -- custom_components/`. It returns 3 sites:
- `coordinator.py`, `cycling_cost=self._effective_cycling_cost()`: the writer of the configured value. Disposition: by design, upstream of `start_price`.
- `optimizer.py`, `OptimizationConfig.start_price`'s two reads: the property itself.

No solve reads the raw field. The `tests/features.py` check `every optimizer reader of the start price reads start_price` pins that over `inspect.getsource(optimizer)`: 7 raw readers at the base, 0 at the head.

**Scoped gate.** Command: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=b425502da8d15c43f9494412e686a3d852b74358 ./tests/run.sh`, at 6413c94c08.
- Result: 1 failed, `tests/features.py`, with 2 of 5783 checks. Both were duty-switch fixtures that needed a clamped install at a zero start price: `fixed-speed: what pricing a start adds ...` read `[1.1999999999999993 vs 1.8]`, and `beside a hot-water charge, at a zero price ...` read `{'zero price': 60, ...}`.
- Fixed at 1b76f567ea by patching the default to zero for those two fixtures.
- `env_drift.py --all` against the merge base passed, so no golden moves and both claim files stay byte-identical.

<!-- figure-block: scope-line mb=b425502da8d15c43f9494412e686a3d852b74358 head=1b76f567ea07bba3ef0840c2307ad4751248f1b4 -->
~~~text
MODE: SCOPED -- 30 script(s) run, 3 scoped out.
~~~
<!-- /figure-block -->

## Unpinned sites

Every site is disposed of as pinned by `mutation-autofix` after the push; the kill is in `tests/features.py`.
- **Re-pinned sites.** Ten pins on the same operator at the same predicate, reading `cycling_cost`, are deleted in this diff as stale (ci_predict's STALE PIN repair). Each recorded `killed_by: tests/features.py`, and the predicate is unchanged apart from the name.
- **New sites in `start_price`.** Killed by the block's `start_price` check: each mutant moves a row of its table, as the mutation proof shows for the two lines removed.

- `custom_components/heatpump_optimizer/optimizer.py:201 CMP_BOUND`: pinned by `mutation-autofix`. `>= 0` engages the unpriced duty-cycle solve, and `the fixture has something to commit` goes red (its old pin).
- `custom_components/heatpump_optimizer/optimizer.py:201 RETURN_DEL`: pinned by `mutation-autofix` (its old pin).
- `custom_components/heatpump_optimizer/optimizer.py:248 BOOLOP`: pinned by `mutation-autofix` (its old pin).
- `custom_components/heatpump_optimizer/optimizer.py:248 CMP_BOUND`: pinned by `mutation-autofix` (its old pin).
- `custom_components/heatpump_optimizer/optimizer.py:248 GUARD_OFF`: pinned by `mutation-autofix` (its old pin).
- `custom_components/heatpump_optimizer/optimizer.py:450 CMP_BOUND`: pinned by `mutation-autofix` (its old pin).
- `custom_components/heatpump_optimizer/optimizer.py:450 GUARD_OFF`: pinned by `mutation-autofix` (its old pin).
- `custom_components/heatpump_optimizer/optimizer.py:2754 BOOLOP`: pinned by `mutation-autofix`. `or` returns 0.1 unclamped at 0, and the `(0.0, False)` row moves.
- `custom_components/heatpump_optimizer/optimizer.py:2754 CMP_BOUND`: pinned by `mutation-autofix`. `>= 0` returns 0.0 clamped at 0, and the `(0.0, True)` row moves.
- `custom_components/heatpump_optimizer/optimizer.py:2754 GUARD_OFF`: pinned by `mutation-autofix`. Every price becomes 0.1, and the priced rows move.
- `custom_components/heatpump_optimizer/optimizer.py:2756 RETURN_DEL`: pinned by `mutation-autofix`. Priced rows read `None`.

## Red checks

- `mutation` at 1b76f567ea07: red by construction on the 11 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push. Cheaper detector: prepr step 6d already predicted it locally, at no added standing cost; no other detector is owed, since the red is the pin mechanism's own design.
- `tests / mutation` at cf10d01c (the clean merge of 1b76f567 and main 38bf516b): `MUTATION TABLE REFUSED -- 2176 unpinned site(s) against 2165 at the ratchet base 38bf516b, 11 of them added by this diff`, all in `custom_components/heatpump_optimizer/optimizer.py` (lines 201, 248, 450, 2754, 2756), each listed under `## Unpinned sites`. `mutation-autofix` pins the killed sites once the pull request is open; it never ran on the first open because the pull request closed on this refusal. Cheaper detector: prepr step 6d's mutant prediction, already run by the fixer on 1b76f567, at no added standing cost; none cheaper exists.
- `governance / instrument-self-tests`: inherited from main, not introduced here: the `product_reads` self-test against #3672's per-state cells is red on main itself, and its hotfix is in flight. This diff does not touch the self-test or the product_reads instrument.
- `tests / fast (3.14)`, `slow`, `tests / nightly-status`: inherited from main, not introduced here. They stand on main's own commits that the merge of main 38bf516b brought into this branch's ancestry: `tests / fast (3.14)` was cancelled at 66dcb415 and c716a4a1, `slow` failed at 38bf516b, and `tests / nightly-status` reports main's nightly state and is red on main's commits as on cf10d01c. Nothing on 1b76f567 or 6413c94c ran red on these; no cheaper detector is owed for a red this diff did not cause.

## Forward-carry

none

## Friction

none
