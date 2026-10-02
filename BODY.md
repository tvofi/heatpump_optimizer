_Requested by **tvofi**_

Round-9 F10.6, built at the owner's answer to card C6 ("Commission"). Part of #201.

Before: no mutation operator touched an ordering comparison, so a bound such as D3-s1-01's lower limit in `coordinator.py`'s `_dhw_inlet_c` (`-5.0 <= value`) could tighten to `<` while the ledger still read that line as accounted for. That is residual (b) of the R9 RCA for class I1.

After: `tests/mutation_table.py` has a seventh operator, `CMP_BOUND`. It moves one bound of a one-line comparison by one step (`<` to `<=`, `<=` to `<`, and the mirrored `>`/`>=` pair). A chain gets one mutant per operator. The operator is rewritten in the gap between its two operands, so a chain's second `<=` changes and its first does not. `==`, `in` and `is` are left alone.

**Enabled, at tvofi's ruling.** The brief required the operator's cost to be measured in list mode before it joined the per-site ratchet. The figures below were reported to the orchestrator, and tvofi ruled "enable now" (2026-10-02, in chat to the orchestrator).

`CMP_BOUND` is in `RATCHETED`, so the deterministic inventory, the sampled pool and the per-site ratchet all carry it. `LISTED` remains the set `--list KIND` reports: today it equals `RATCHETED`, and it is where a future operator can be priced before it is enabled.

From this merge on, every diff that adds or edits a one-line ordering comparison owes a pin, which `mutation-autofix`'s `--pin-killed` records when a driver kills it. The ratchet's refusal text now names comparison bounds.

Comparisons spanning several lines stay out of the operator. That is card C7's residual, which tvofi ruled "Not now"; a check now holds it.

**Equivalent mutants, disclosed.** The #1861 fix review's scan found two production sites where the operator's mutant is provably equivalent: the max/min idiom, whose two arms agree at equality.

- `away.py` `_holiday_span`: `if last < first:` then `last = first`, over `date` values.
- `dhw_planner.py` `DhwPlanner._dhw_planner_draws` (in `optimizer.py` until #1858 moved it unchanged): `idx = i if i <= last else last`, over ints.

No driver can kill either one, so each is recorded here as a `survivor_triage` `equivalent` row in `tests/mutation_ledger/survivor_triage/`. Each row is measured by `tools/audit/round9/F10/f10_6/equiv_probe.py`. It counts ties inside the compiled production function, by an append in the comparison itself. No input separates head from mutant. A tie-only control on the same line, an edit that changes the result only when the two sides are equal, shows the grid can see a difference at the one place a `<`/`<=` mutant could differ. The tie counter and both controls are the #1861 review's own (`~/hpo-seats/1861-review/own/rv_equiv_probe.py`, sha1 6f7aee1d6f4e01b0d637d5cb91f64b6694b0e725).

The scan behind this list covers two patterns only: the max/min idiom, and an integer compared against a fractional constant (0 hits). It does not prove that no other equivalent `CMP_BOUND` mutant exists. Any further one surfaces as a survivor in `--pin-killed` or the nightly drain and needs the same verdict.

**What else changes.**
- `tests/mutation_budgets.json`: only its `_comment`, where "the six operators" is now "the ratcheted operators". No cap and no `last_measured` value moves.
- The ledger gains only the two triage rows above.
- `tests/mutation_table.py` is code-owned, so it needs tvofi's approving review at the head.

## Head

bdc14972515b7bbca4175159acb644860928e5c9 (merge base and `origin/main` 68b8cb97, 2026-10-02)

Round 3 answers the #1861 review's round 2 (blocked: null-control). There, `equiv_probe.py`'s controls differed only off the tie, 0 of 17 and 0 of 11 tied cases, so they did not cover the arm the equivalence claim is about. bdc14972 gives the probe tie-only controls and re-quotes both triage rows.

edac88f4 merges `origin/main` 68b8cb97 (#1856, #1857, #1858) into round 2's code head 307ecf6c. #1858 moved `_dhw_planner_draws` unchanged from `optimizer.py` to `dhw_planner.py`, which left that row's anchor naming no site (`completeness_problems` refused). bdc14972 re-keys the row to the moved site, with the same `old` pin and verdict.

## Mutation proof

Failing test first: at a5f4e1c1 (checks only) the original three checks in `tests/entities.py` failed, with `CMP_BOUND` generating `[]`.

Round 2's repairs are pinned by the review's own mutants. They were re-run at bdc14972 (results identical to 307ecf6c) with the reviewer's `~/hpo-seats/1861-review/own/mutants.py` (sha1 e32144cf47af3f55dd9b0c3154979a67e9a29403). It applies each mutant in place, drives `tests/entities.py`'s operator block through `/Users/timmalmstrom/hpo-seats/R9-F10.6/scratch/run_block.py` (out of tree, sha1 1cc0dcf8b4a1aa92e17bef72a64fe5b5e773d4e1), and restores the file.

- R8 (`<` flips to `>`): `fails=1`, FAIL `CMP_BOUND moves each ordering bound by one, one mutant per operator`. At round 1 it printed 0.
- R5 (the one-line restriction dropped): `fails=3`, including FAIL `a comparison spanning more than one line yields no CMP_BOUND site (C7)`. At round 1 it printed 0.
- E1 (`CMP_BOUND` removed from `RATCHETED`): `fails=4`.
- M1 (operator not flipped): `fails=1`.
- M4 (`listed_sites` ignores the ledger): `fails=1`.
- R2 (chain not advanced): `fails=2`.
- R3 (no `>`/`>=`): `fails=2`.
- R7 (bounds never generated): `fails=3`.
- R10 (`LISTED` empty): `fails=3`.
- M0 (no mutant): `fails=0`.
- R6 (gap check dropped) and R9 (kinds filter dropped) still print 0. The review measured both as equivalent today: R6 leaves the production inventory identical, because the one-line rule already bounds the gap. R9 is a no-op while `LISTED == RATCHETED`.

The ratchet itself was perturbed at round 1's head. A new production line `_late = age > timedelta(minutes=1)` was added in `_dhw_inlet_c` (in place, restored), and `python3 tests/mutation_table.py --scope changed --base origin/main` printed `ADDED UNPINNED custom_components/heatpump_optimizer/coordinator.py:1734 CMP_BOUND` and `MUTATION TABLE REFUSED -- 4856 unpinned site(s) against 4855`. The review repeated this in another file (`away.py`), with a `==` null control.

The one in-memory mutant on D3-s1-01's line (tvofi's "no heavy D3" form) is `tools/audit/round9/F10/f10_6/d3s101_mutant.py` (sha1 df94303950b0dc3f634d03bd469b6a0ed8ac0776). At a reading of `-5.0`, production returns `-5.0` and the mutant returns `None` (DIFFERS). At `0.0` and `35.0` they agree. Whether a gate check kills that mutant is for CI's mutation lane to measure. No local mutation pool was run.

Survivors on the sites touched: `--scope changed` draws only from production lines, and this diff touches none (`MUTATION TABLE PASSED (empty scope)`).

## Null control

- The enabling head does not trip its own ratchet. The count at the ratchet base is taken with this head's operators, and the head's count is at or below it with no site added (the ratchet line in Figures). The perturbation under Mutation proof is the arm that shows the same ratchet refusing one new comparison.
- Enabling moves the inventory by exactly the listed `CMP_BOUND` stock: the head's site count less `origin/main`'s equals the `--list CMP_BOUND` count. The unpinned difference is that count less the two triage rows (the lines in Figures).
- Each equivalence verdict has a reached tie and a differing control (`equiv_probe.py`'s `RESULT` lines). A grid that never tied would be vacuous, and a control that never differed would show a blind probe.
- The stock count has a control. An independent AST count of ordering operators separates the one-line comparisons the operator must match exactly from the multi-line ones (C7) it does not reach (`cmp_cost.py`'s `RESULT control` line).
- The burden counter has two nulls. A merge diffed against itself adds nothing. A synthetic `if x < 1:` adds exactly one `CMP_BOUND` and one `GUARD_OFF` site (`cmp_cost.py`'s `RESULT null` line).

## Figures

At code head bdc14972, merge base 68b8cb97, 2026-10-02.

- Ratchet at the head: `python3 tests/mutation_table.py --scope changed --base origin/main` -> `4853 unpinned site(s) of 5466 candidate sites, 4855 at the ratchet base 68b8cb97d911339a206fde141ecfdf0f57c6ccc4; the ledger agrees with the deterministic inventory`, then `MUTATION TABLE PASSED (empty scope)`. No `ADDED UNPINNED` line was printed.
- Inventory, both ends: `python3 tools/audit/round9/F10/f10_6/inventory_identity.py origin/main` (sha1 064b4c50fa7a3f2111d1650b6d550671044854f0) -> `RESULT inventory head sites=5466 sha1=3f04779a430a unpinned=4853` and `RESULT inventory origin/main sites=4520 sha1=fe4c90319eb3 unpinned=3909`. The digests moved with #1858's file move, and the counts did not. At the list-mode head c117c2b3 the head line equalled `origin/main`'s.
- Stock: `python3 tests/mutation_table.py --list CMP_BOUND` -> `LIST CMP_BOUND: 946 site(s) in 56 file(s), 944 unpinned, ratcheted`. Rule: every ordering operator of a one-line `ast.Compare` in every production module.
  - Control: `python3 tools/audit/round9/F10/f10_6/cmp_cost.py 1936d5ca 8fa06663` (sha1 359281f1464b34274048cb92575afdc9a565ff9f) -> `RESULT stock_sites=946 unpinned=944 anchors=805 files=56` and `RESULT control ordering_ops_all=961 one_line=946 multi_line=15`.
  - A chain's operators share a ledger anchor, which is why the sites sit under fewer anchors. `pin_results` pins an anchor only when every site under it was killed, so a pinned upper bound cannot cover an unpinned lower one.
- Equivalents: `PYTHONPATH=tests/hastub python3 tools/audit/round9/F10/f10_6/equiv_probe.py` (sha1 8acccbc63a035b8226de2dcf1708130ecbc8e33a, run with numpy) ->
  - `RESULT _holiday_span cases=49 ties=17 mutant_differs=0 control_differs_at_tie=17 control_differs_untied=0`
  - `RESULT _dhw_planner_draws cases=16 ties=11 mutant_differs=0 control_differs_at_tie=6 control_differs_untied=0`
  - `RESULT _dhw_planner_draws tied_cases_with_last_0=5`: in those 5 tied cases `last == 0`, where the tie-only control (`last - 1 if i == last and last > 0`) cannot move. So it covers 6 of the 11 tied cases there, and all 17 in `_holiday_span`.
  - Round 2's probe used off-tie controls (`if False:`; `idx = last`), which the review measured moving 0 tied cases. They are replaced.
  - The review's scan, `python3 ~/hpo-seats/1861-review/own/rv_equiv.py` (sha1 beb4a3e17b7afeb4a7b68633a246b4a0ef8ab5eb), at 307ecf6c -> `RESULT rv_equiv candidates=2`: away.py:558 and optimizer.py:4742 (now dhw_planner.py:679).
  - Its scope is the max/min idiom and the integer-against-fraction shape. It is not proven exhaustive.
- Generation, the review's instrument: `python3 ~/hpo-seats/1861-review/own/rv_check.py` (sha1 1ba7dcf847a4bff65022a3605a9443d6eb8e9ecf) -> `RESULT rv sites=946 expected=946 line_mismatch=0 bad=0`.
- Per-merge pin burden: `python3 tools/audit/round9/F10/f10_6/cmp_cost.py 1936d5ca 8fa06663` -> `RESULT burden CMP_BOUND: merges=121 adding=25 total=122 mean=1.01 median=0 max=15`. The scale it is read against is the operator the ratchet already charges: `RESULT burden GUARD_OFF: merges=121 adding=36 total=192 mean=1.59 median=0 max=18`.
  - Rule: the first-parent merges on `main` from the round-9 baseline 1936d5ca to 8fa06663, the window priced for tvofi's ruling.
  - A merge's burden is its sites added by content: the multiset `(file, kind, old, new)` at M minus at M^1, so a chain's two bounds count twice.
- Nightly minutes at the current `--max`: unchanged by construction, because `--max 40` caps the mutants per run for both `mutation-nightly` and `mutation-ledger`.
  - Measured wall time of `mutation-nightly` (`--scope full --max 40`) in the 7 most recent successful scheduled Tests runs: 33.4 to 187.6 min, mean 87.3, median 71.1. That is about 2.2 CI-minutes per mutant, baselines included.
  - Command: `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/jobs` for runs 36109995574, 35970686263, 35497764519, 35319427309, 35196004930, 35070021587 and 34943623264, with `completed_at - started_at` on the `mutation-nightly` job (0 API failures).
- Drain nights, corrected:
  - **Lower bound.** The nightly drain drives at most 40 sites a night, so the 944 unpinned `CMP_BOUND` sites need at least 944 / 40, about 24 nights. That holds only if every driven site is killed and pinned.
  - **Why it is longer.** A survivor stays in the stock until a human verdict: an equivalent mutant (the two above are already triaged out) or a gap.
  - **At a measured kill rate.** At the one kill fraction measured for this drain (37 of 40 in F10.5's demonstration slice) it is about 944 / 37, roughly 26 nights.
  - **Not measured.** The real figure depends on the survivor rate of these sites, which is unmeasured.
- Per-PR CI cost, by rule: burden x about 2.2 min through `mutation-autofix`'s `--pin-killed`. That is a mean of about 2.2 min per merge and a maximum of about 33 min over the window. This is an estimate from the nightly's per-mutant rate, not a measured PR run.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` -> `MODE: SCOPED -- 2 script(s) run, 26 scoped out`, running `tests/entities.py` and `tests/harness_headers.py`. Both ran at bdc14972 under `~/hpo-seats/R9-F11.4-venv/bin/python3` with `PYTHONPATH=tests/hastub`.
  - `tests/entities.py`: `ALL 2078 ENTITY CHECKS PASSED`.
  - `tests/harness_headers.py`: `ALL 94 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py` (same venv) -> `STRUCTURE RATCHET PASSED`.
- Not run locally (CI's): closures (`PREPR_SKIP_CLOSURES=1`), the mutation lane's drives, `features.py` and the solver goldens.

## Red checks

The review's CI reads at round 1's head 2c8f2bac and round 2's 5009fe47 found one red, `nightly-status`, which reported `mutation-ledger` and `mutation-ledger-push` absent from the scheduled run. That is `main`'s `always()` defect, fixed by #1859 (aa7a8119, merged into this branch). This diff does not touch what that reporter reads. No check went red on a commit this branch made.

## Forward-carry

none: there is no later round-9 stage, because F10.6 is the last F10 PR. The obligation it creates, a pin or a triage verdict for every new one-line ordering comparison, is enforced by the ratchet itself on every later diff.

## Friction

- environment: cost: `tests/entities.py` and `equiv_probe.py` need numpy. They ran under `~/hpo-seats/R9-F11.4-venv` (SEAT-BLOCK item 12).
