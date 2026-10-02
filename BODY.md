_Requested by **tvofi**_

Round-9 F10.6, built at the owner's answer to card C6 ("Commission"). Part of #201.

Before: no mutation operator touched an ordering comparison, so a bound such as D3-s1-01's lower limit in `coordinator.py`'s `_dhw_inlet_c` (`-5.0 <= value`) could tighten to `<` while the ledger still read that line as accounted for. That is residual (b) of the R9 RCA for class I1.

After: `tests/mutation_table.py` has a seventh operator, `CMP_BOUND`. It moves one bound of a one-line comparison by one step (`<` to `<=`, `<=` to `<`, and the mirrored `>`/`>=` pair). A chain gets one mutant per operator. The operator is rewritten in the gap between its two operands, so a chain's second `<=` changes and its first does not. `==`, `in` and `is` are left alone.

**It lands in list mode only.** The brief prices the operator before it joins the per-site ratchet, and that decision is tvofi's. `RATCHETED` (the six existing operators) is the default for `candidates()` and `inventory()`. `LISTED` adds `CMP_BOUND`. The inventory, the sampled pool and the ratchet are byte-identical to `main` (Null control). `--list KIND` prints every site of one operator with its unpinned count. Enabling it later is a one-word edit to `RATCHETED`. No budget file changes. The cost figures for that decision are under Figures (stock, per-merge pin burden, nightly minutes).

`tests/mutation_table.py` is code-owned, so it needs tvofi's approving review at the head.

## Head

c117c2b3c3b1e6b97a79248589abbfc946aff50c (merge base and `origin/main` 8fa06663, 2026-10-02T17:08Z)

c117c2b3 adds only `tools/audit/round9/F10/f10_6/inventory_identity.py` (INERT under `tools/audit/`) to 97fba3f0. `tests/entities.py` and `tests/harness_headers.py` ran at 97fba3f0, and every other figure ran at c117c2b3.

## Mutation proof

Failing test first: at a5f4e1c1 (checks only) the three new checks in `tests/entities.py` failed, with `CMP_BOUND` generating `[]`. Here `entities.py` imports numpy, so the block was driven alone by `/Users/timmalmstrom/hpo-seats/R9-F10.6/scratch/run_block.py` (out of tree, sha1 197776c035302459cefb42a7ab63246caa9976b0). That runner execs `entities.py` from the six-operator header to the inventory header with a stub `R`, and printed `3 failed`. At 97fba3f0 the same runner printed `0 failed`, and the whole `tests/entities.py` printed the three as `ok` (see Figures).

Each mutant below was applied in place on the committed tree, driven through the same runner, and restored with `git checkout`:

- M1 `_bound_mutants` keeps the operator (`+ gap` for `+ gap.replace(...)`): FAIL `CMP_BOUND moves each ordering bound by one, one mutant per operator`
- M2 `LISTED = RATCHETED` (operator unreachable): FAIL that check, FAIL `and it stays out of the ratcheted inventory until it is priced`, FAIL `--list counts a CMP_BOUND anchor unpinned until the ledger covers it`
- M3 `CMP_BOUND` added to `RATCHETED` (enabled without a pricing): FAIL `every operator fires on a module written to carry one of each`, FAIL `and it stays out of the ratcheted inventory until it is priced`
- M4 `listed_sites` ignores the ledger: FAIL `--list counts a CMP_BOUND anchor unpinned until the ledger covers it`

M0, the restored tree, printed `0 failed`.

The one in-memory mutant on D3-s1-01's line (tvofi's "no heavy D3" form) is `tools/audit/round9/F10/f10_6/d3s101_mutant.py` (sha1 df94303950b0dc3f634d03bd469b6a0ed8ac0776). It takes the mutant `candidates(..., LISTED)` generates for that line's lower bound and compiles `_dhw_inlet_c` from the mutated and the unmutated module text. It binds the function to the production helpers it calls (`inputs.age_of`, `temperature_c`, `state_unit`, the hastub `dt_util`), because `coordinator.py` imports numpy and the module cannot be imported here. It then calls both on a fresh inlet reading:

- `-5.0`: production `-5.0`, mutant `None` (DIFFERS)
- `0.0` and `35.0` (null controls): equal

Whether a gate check kills that mutant is for CI's mutation lane to say once the operator is enabled. No local mutation pool was run.

Survivors on the sites touched: `--scope changed` draws only from production lines, and this diff touches none.

## Null control

- The ratcheted inventory is unchanged: this head's `inventory()` and `origin/main`'s return the same site list, element for element, with the same unpinned count (the inventory-identity line in Figures). With the sets identical, the per-site ratchet and the count ratchet compare the same thing at both ends.
- The stock count has a control: an independent AST count of every ordering operator, which separates one-line comparisons (the ones `--list CMP_BOUND` must match exactly) from multi-line ones it does not reach (the stock line in Figures).
- The burden counter has two nulls: a merge diffed against itself adds nothing, and a synthetic `if x < 1:` adds exactly one `CMP_BOUND` and one `GUARD_OFF` site (`cmp_cost.py`'s `RESULT null` line).
- `--list` on a ratcheted operator is the control for the ledger lookup: it reports `ratcheted` with an unpinned count below its total (the `--list GUARD_OFF` line in Figures).

## Figures

At code head c117c2b3 (gate scripts at 97fba3f0, see Head), merge base 8fa06663, 2026-10-02.

- Stock: `python3 tests/mutation_table.py --list CMP_BOUND` -> `LIST CMP_BOUND: 946 site(s) in 55 file(s), 946 unpinned, listed only`. Rule: every ordering operator of a one-line `ast.Compare` in every production module. Control: `python3 tools/audit/round9/F10/f10_6/cmp_cost.py 1936d5ca 8fa06663` (sha1 359281f1464b34274048cb92575afdc9a565ff9f) -> `RESULT stock_sites=946 unpinned=946 anchors=805 files=55` and `RESULT control ordering_ops_all=961 one_line=946 multi_line=15`. A chain's operators share a ledger anchor, which is why 946 sites sit under 805 anchors. `pin_results` pins an anchor only when every site under it was killed, so a pinned upper bound cannot cover an unpinned lower one.
- Inventory identity: `python3 tools/audit/round9/F10/f10_6/inventory_identity.py origin/main` (sha1 064b4c50fa7a3f2111d1650b6d550671044854f0) -> `RESULT inventory head sites=4520 sha1=c141b52379cc unpinned=3909` and `RESULT inventory origin/main sites=4520 sha1=c141b52379cc unpinned=3909`. Its own perturbation is M3 (`CMP_BOUND` in `RATCHETED`, applied in place and restored), which printed `RESULT inventory head sites=5466 sha1=1ba97b4cecd5 unpinned=4855` against an unchanged `origin/main` line. That is also what enabling the operator does to the ratcheted stock.
- Ledger-lookup control: `python3 tests/mutation_table.py --list GUARD_OFF` -> `LIST GUARD_OFF: 2425 site(s) in 66 file(s), 2142 unpinned, ratcheted`.
- Per-merge pin burden: the same command -> `RESULT burden CMP_BOUND: merges=121 adding=25 total=122 mean=1.01 median=0 max=15`. The scale it is read against is the operator the ratchet already charges: `RESULT burden GUARD_OFF: merges=121 adding=36 total=192 mean=1.59 median=0 max=18`. Rule: the 121 first-parent merges on `main` from the round-9 baseline 1936d5ca to 8fa06663. A merge's burden is its sites added by content: the multiset `(file, kind, old, new)` at M minus at M^1, which is the per-site ratchet's identity plus `new`, so a chain's two bounds count twice. Nulls: under Null control.
- Nightly minutes at the current `--max`: unchanged by construction. `--max 40` caps the mutants per run for both `mutation-nightly` and `mutation-ledger`, so the operator only lengthens the drain. Measured wall time of `mutation-nightly` (`--scope full --max 40`) in the 7 most recent successful scheduled Tests runs: 33.4 to 187.6 min, mean 87.3, median 71.1. That is about 2.2 CI-minutes per mutant, baselines included. Command: `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/jobs` for runs 36109995574, 35970686263, 35497764519, 35319427309, 35196004930, 35070021587 and 34943623264, with `completed_at - started_at` on the `mutation-nightly` job (0 API failures). The drain lengthens by 946 / 40 = about 24 nights at a 100% kill rate, and more at the measured kill fraction.
- Per-PR CI cost if enabled, by rule: burden x about 2.2 min through `mutation-autofix`'s `--pin-killed`. That is a mean of about 2.2 min per merge and a maximum of about 33 min (15 sites) over this window. This is an estimate from the nightly's per-mutant rate, not a measured PR run.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` -> `MODE: SCOPED -- 2 script(s) run, 26 scoped out`, running `tests/entities.py` and `tests/harness_headers.py`.
  - `tests/entities.py` (seat venv with CI's numpy): `1 of 2074 ENTITY CHECKS FAILED`. The one failure is `no job-level if leads with always(): a cancelled run stops (CI cancel)`, naming `tests.yml:mutation-ledger` and `tests.yml:mutation-ledger-push`. It fails identically at the merge base 8fa06663 (`1 of 2071`); see Red checks. The three new checks are `ok`.
  - `tests/harness_headers.py`: `68 of 94 HARNESS HEADER CHECKS FAILED` at head and at 8fa06663, with identical check names. All of them are `tools/audit/round*/D*/` harnesses importing numpy, which the seat interpreter lacks. The new `f10_6/` harnesses are outside its `round*/D*/*.py` glob.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- Not run locally (CI's): closures (`PREPR_SKIP_CLOSURES=1`), the mutation lane, `features.py` and the solver goldens.

## Red checks

`tests/entities.py`'s `no job-level if leads with always(): a cancelled run stops (CI cancel)` is red on `main` at 8fa06663, at this branch's merge base, from the merge of #1854 (the CI-cancel pin) and #1848 (the ledger jobs). This diff touches no workflow file. No check went red on a commit this branch made.

## Forward-carry

none: there is no later round-9 stage. F10.6 is the last F10 PR. Enabling the operator is tvofi's pricing decision on the figures above. Once it is enabled, every later diff that adds a comparison owes a pin, and the ratchet itself enforces that.

## Friction

- environment: cost: `tests/entities.py` needs numpy. The seat ran it with an existing seat venv's interpreter (`R9-F10.5/venv`, Python 3.14.7, numpy 2.4.6) and drove the mutants through a block runner.
