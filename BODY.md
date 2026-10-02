_Requested by **tvofi**_

Round-9 F10.6, built at the owner's answer to card C6 ("Commission"). Part of #201.

Before: no mutation operator touched an ordering comparison, so a bound such as D3-s1-01's lower limit in `coordinator.py`'s `_dhw_inlet_c` (`-5.0 <= value`) could tighten to `<` while the ledger still read that line as accounted for. That is residual (b) of the R9 RCA for class I1.

After: `tests/mutation_table.py` has a seventh operator, `CMP_BOUND`. It moves one bound of a one-line comparison by one step (`<` to `<=`, `<=` to `<`, and the mirrored `>`/`>=` pair). A chain gets one mutant per operator. The operator is rewritten in the gap between its two operands, so a chain's second `<=` changes and its first does not. `==`, `in` and `is` are left alone.

**Enabled, at tvofi's ruling.** The brief required the operator's cost to be measured in list mode before it joined the per-site ratchet. The figures below were reported to the orchestrator, and tvofi ruled "enable now" (2026-10-02, in chat to the orchestrator).

`CMP_BOUND` is now in `RATCHETED`, so the deterministic inventory, the sampled pool and the per-site ratchet all carry it. `LISTED` remains the set `--list KIND` reports: today it equals `RATCHETED`, and it is where a future operator can be priced before it is enabled.

From this merge on, every diff that adds or edits a one-line ordering comparison owes a pin, which `mutation-autofix`'s `--pin-killed` records when a driver kills it. Comparisons spanning several lines stay out of the operator: that is card C7's residual, which tvofi ruled "Not now" and F10.3 recorded.

`tests/mutation_budgets.json` changes only in its `_comment`, where "the six operators" is now "the ratcheted operators". No cap, no `last_measured` value and no ledger row moves. `tests/mutation_table.py` is code-owned, so it needs tvofi's approving review at the head.

## Head

cd04771a17bdc6df6c91e9d9a852f211fec63de0 (merge base and `origin/main` 8fa06663, 2026-10-02)

The list-mode head that was priced is c117c2b3. cd04771a enables the operator on top of it.

## Mutation proof

Failing test first: at a5f4e1c1 (checks only) the three new checks in `tests/entities.py` failed, with `CMP_BOUND` generating `[]`. The checks are named in the list below.

The mutants below were applied in place on the committed tree cd04771a and driven through `/Users/timmalmstrom/hpo-seats/R9-F10.6/scratch/run_block.py` (out of tree, sha1 1cc0dcf8b4a1aa92e17bef72a64fe5b5e773d4e1). That runner execs `tests/entities.py` from the seven-operator header to the inventory header with a stub `R`. Each file was restored with `git checkout`.

- E1 `CMP_BOUND` removed from `RATCHETED` (the enabling undone): FAIL `every operator fires on a module written to carry one of each`, FAIL `CMP_BOUND moves each ordering bound by one, one mutant per operator`, FAIL `and, priced and ruled in (tvofi 2026-10-02), it is in the ratcheted inventory`, FAIL `--list counts a CMP_BOUND anchor unpinned until the ledger covers it`
- M1 `_bound_mutants` keeps the operator (`+ gap` for `+ gap.replace(...)`): FAIL `CMP_BOUND moves each ordering bound by one, one mutant per operator`
- M4 `listed_sites` ignores the ledger: FAIL `--list counts a CMP_BOUND anchor unpinned until the ledger covers it`

M0, the restored tree, printed `0 failed`.

The ratchet itself was perturbed too. A new production line `_late = age > timedelta(minutes=1)` was added in `_dhw_inlet_c` (in place, restored), and `python3 tests/mutation_table.py --scope changed --base origin/main` printed `ADDED UNPINNED custom_components/heatpump_optimizer/coordinator.py:1734 CMP_BOUND` and `MUTATION TABLE REFUSED -- 4856 unpinned site(s) against 4855 at the ratchet base 8fa06663...`.

The one in-memory mutant on D3-s1-01's line (tvofi's "no heavy D3" form) is `tools/audit/round9/F10/f10_6/d3s101_mutant.py` (sha1 df94303950b0dc3f634d03bd469b6a0ed8ac0776). It takes the operator's mutant for that line's lower bound and compiles `_dhw_inlet_c` from the mutated and the unmutated module text. It binds the function to the production helpers it calls (`inputs.age_of`, `temperature_c`, `state_unit`, the hastub `dt_util`), because the module imports numpy, and calls both on a fresh inlet reading:

- `-5.0`: production `-5.0`, mutant `None` (DIFFERS)
- `0.0` and `35.0` (null controls): equal

Whether a gate check kills that mutant is for CI's mutation lane (`--pin-killed` or the nightly drain) to measure. No local mutation pool was run.

Survivors on the sites touched: `--scope changed` draws only from production lines, and this diff touches none (`MUTATION TABLE PASSED (empty scope)`).

## Null control

- The enabling head does not trip its own ratchet. The count at the ratchet base is taken with this head's operators: unchanged files reuse this tree's sites, and changed files are re-enumerated with this head's `candidates()`. That base count equals this tree's, and no site is added (the ratchet line in Figures). The perturbation under Mutation proof is the arm that shows the same ratchet refusing one new comparison.
- The list-mode head c117c2b3 left the inventory byte-identical to `origin/main`'s. Enabling moves it by exactly the listed `CMP_BOUND` stock and nothing else: the head count less `origin/main`'s equals the `--list CMP_BOUND` count, for sites and for unpinned alike (the lines in Figures).
- The stock count has a control. An independent AST count of ordering operators separates the one-line comparisons the operator must match exactly from the multi-line ones (C7) it does not reach (`cmp_cost.py`'s `RESULT control` line).
- The burden counter has two nulls. A merge diffed against itself adds nothing. A synthetic `if x < 1:` adds exactly one `CMP_BOUND` and one `GUARD_OFF` site (`cmp_cost.py`'s `RESULT null` line).

## Figures

At code head cd04771a, merge base 8fa06663, 2026-10-02. The pricing figures were taken at the list-mode head c117c2b3 over the same production tree; the production tree is identical between the two heads.

- Ratchet at the enabling head: `python3 tests/mutation_table.py --scope changed --base origin/main` -> `4855 unpinned site(s) of 5466 candidate sites, 4855 at the ratchet base 8fa06663cf64a32cf19a3a2f2742ce3225f06e3a; the ledger agrees with the deterministic inventory`, then `MUTATION TABLE PASSED (empty scope)`. No `ADDED UNPINNED` line was printed.
- Inventory, both ends: `python3 tools/audit/round9/F10/f10_6/inventory_identity.py origin/main` (sha1 064b4c50fa7a3f2111d1650b6d550671044854f0) -> `RESULT inventory head sites=5466 sha1=1ba97b4cecd5 unpinned=4855` and `RESULT inventory origin/main sites=4520 sha1=c141b52379cc unpinned=3909`. At c117c2b3 the head line read `sites=4520 sha1=c141b52379cc unpinned=3909`.
- Stock: `python3 tests/mutation_table.py --list CMP_BOUND` -> `LIST CMP_BOUND: 946 site(s) in 55 file(s), 946 unpinned, ratcheted`. Rule: every ordering operator of a one-line `ast.Compare` in every production module. Control: `python3 tools/audit/round9/F10/f10_6/cmp_cost.py 1936d5ca 8fa06663` (sha1 359281f1464b34274048cb92575afdc9a565ff9f) -> `RESULT stock_sites=946 unpinned=946 anchors=805 files=55` and `RESULT control ordering_ops_all=961 one_line=946 multi_line=15`. A chain's operators share a ledger anchor, which is why the sites sit under fewer anchors. `pin_results` pins an anchor only when every site under it was killed, so a pinned upper bound cannot cover an unpinned lower one.
- Per-merge pin burden: the same command -> `RESULT burden CMP_BOUND: merges=121 adding=25 total=122 mean=1.01 median=0 max=15`. The scale it is read against is the operator the ratchet already charges: `RESULT burden GUARD_OFF: merges=121 adding=36 total=192 mean=1.59 median=0 max=18`. Rule: the first-parent merges on `main` from the round-9 baseline 1936d5ca to 8fa06663. A merge's burden is its sites added by content: the multiset `(file, kind, old, new)` at M minus at M^1, so a chain's two bounds count twice.
- Nightly minutes at the current `--max`: unchanged by construction, because `--max 40` caps the mutants per run for both `mutation-nightly` and `mutation-ledger`. Measured wall time of `mutation-nightly` (`--scope full --max 40`) in the 7 most recent successful scheduled Tests runs: 33.4 to 187.6 min, mean 87.3, median 71.1. That is about 2.2 CI-minutes per mutant, baselines included. Command: `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/jobs` for runs 36109995574, 35970686263, 35497764519, 35319427309, 35196004930, 35070021587 and 34943623264, with `completed_at - started_at` on the `mutation-nightly` job (0 API failures). The drain lengthens by the stock over 40 sites a night: about 24 nights at a 100% kill rate, more at the measured one.
- Per-PR CI cost, by rule: burden x about 2.2 min through `mutation-autofix`'s `--pin-killed`. That is a mean of about 2.2 min per merge and a maximum of about 33 min over this window. This is an estimate from the nightly's per-mutant rate, not a measured PR run.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` -> `MODE: SCOPED -- 2 script(s) run, 26 scoped out`, running `tests/entities.py` and `tests/harness_headers.py`. Both ran at cd04771a under `~/hpo-seats/R9-F11.4-venv/bin/python3` with `PYTHONPATH=tests/hastub`.
  - `tests/entities.py`: `1 of 2074 ENTITY CHECKS FAILED`, where the one failure is `main`'s (Red checks). The three new checks are `ok`.
  - `tests/harness_headers.py`: `ALL 94 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py` (same venv) -> `STRUCTURE RATCHET PASSED`.
- Not run locally (CI's): closures (`PREPR_SKIP_CLOSURES=1`), the mutation lane's drives, `features.py` and the solver goldens.

## Red checks

`tests/entities.py`'s `no job-level if leads with always(): a cancelled run stops (CI cancel)` (`tests.yml:mutation-ledger`, `tests.yml:mutation-ledger-push`) is red on `main` at this branch's merge base 8fa06663 (`1 of 2071` there). It comes from the merge of #1854 and #1848, and the hotfix is #1859. This diff touches no workflow file, and no check went red on a commit this branch made.

## Forward-carry

none: there is no later round-9 stage, because F10.6 is the last F10 PR. The obligation it creates, a pin for every new one-line ordering comparison, is enforced by the ratchet itself on every later diff.

## Friction

- environment: cost: `tests/entities.py` needs numpy. The list-mode round used an existing seat venv. This round used `~/hpo-seats/R9-F11.4-venv` (SEAT-BLOCK item 12), under which `tests/harness_headers.py` also passes in full.
