# Class sweep I4 -- round 10 (PLAN phase D)

Class I4: two independent parsers or definitions of one concept disagree.
Status in `dev/audit/config/bugclasses.json`: `barriered` (agreement.mjs on the
PR gate, registered concept pairs only; "not reached": a second reader of a
concept nobody registered). Both round-10 findings are that unreached shape.
Measured at `handoff/audit-r10-register` 9355f107d.

## Enumerator

`python3 dev/audit/rounds/round10/D14/sweep-I4/enumerate.py [ROOT]`, from the
findings' seam rules widened to the package:

- **hist** (D13-s2-02's `grep -n 'bump(verdicts'`): every `bump(hist, key, pr)`
  call (the helper is defined once, in `tools/policy/policy_lint.mjs`). A map is
  MIXED when it receives both a parsed key and a constant key.
- **canon** (D13-s2-51's moved-path loop): every `.has/.get/in` lookup into a
  collection built from `canon()`, `policyFiles()`, `trackedFiles()` or
  `policyKeyIndex()` in each module that imports a `canon`
  (`policy_lint.mjs`, `field_coverage.mjs`, `budget_raise_gate.py`,
  `tests/entities.py`). Guarded when the argument passes through `canon()`
  directly or by up to three assignment hops.

Output: `D14/sweep-I4/seams.tsv`, 26 unique seams.

## Controls

| control | command / change | result |
|---|---|---|
| positive | real tree | `hist_mixed 2` (lines 2835, 2850 = D13-s2-02), `frictionKey` lookups 2625/2627/2631 unguarded (= D13-s2-51): both findings re-found |
| null | `enumerate.py D14/sweep-I4/fixture-clean` | `hist_mixed 0 canon_unguarded 0` |
| perturbation (null side) | fixture, one line: `INDEX.has(canon(id))` -> `INDEX.has(id)` | `canon_unguarded 0 -> 2` |
| perturbation (hist) | delete the `bump(verdicts, REWORK_CLASS, pr)` line | `hist_mixed 2 -> 0` |
| perturbation (canon) | `const bare = canon(raw.replace(...))` in frictionKey | `canon_unguarded 25 -> 18`; every frictionKey row guarded |

Second definition pair checked by hand: `tools/policy/counts.mjs:canon` and
`tests/layout.py:canon` agree on all 2684 moved tracked paths (0 disagreements).

## Dispositions

| seam (policy_lint.mjs unless named) | disposition |
|---|---|
| 2835 / 2850 `bump(verdicts, ...)` statsHistogram | **instance** -- D13-s2-02's site; probe `blocks_friction.mjs` (133 vs 4) |
| 2625, 2627, 2631 `POLICY_KEY_INDEX.has/get` in frictionKey | **instance** -- D13-s2-51's site; probe `friction_key_split.mjs` (34) |
| 2836 `bump(endpoints, origin)` | not applicable -- one population (fetch endpoint) |
| 2852 `bump(friction, id)` | not applicable as a histogram (one population); its key is frictionKey's, dispositioned above |
| 895 `measured.has(rel)` | guarded -- `rel` comes from `citedTrackedPaths(raw, trackedFiles())`, a canonical listing |
| 1110 `measured.has(k)` | guarded -- budget-file keys are canonical by `policy_budgets.json` contract and `measured` is `policyFiles()` |
| 1254 `all.has(f)` | guarded -- both sides from `trackedFiles()` / `policyFiles()` |
| 1492 `policy.has(f)` | guarded -- `f` from `canonList(...)` on the line above |
| 3418, 3419, 3455 `live` | not applicable -- a Map of rule keys, not paths |
| 4598, 4650, 4682 `*Hits.has(cls)` | not applicable -- budget class names |
| 5273 `bareInTree`, 5311 `treeExts` | not applicable -- basenames / extensions of one listing |
| 18, 19, 1023, 1638, 3482, 6458 | not applicable -- prose/comment matches of the word "in all"/"in policy" |
| budget_raise_gate.py 573 `paths` | guarded -- both sets built through `canon()` on lines 570-571 |

Instances beyond the findings: **0**. The class's barrier (agreement.mjs) holds
for registered pairs; both instances are unregistered concept pairs
(rework vs block class; real vs canonical path key). Proposed barrier: register
`friction-key` (frictionKey(f) == frictionKey(canon(f)) over the moved corpus)
and `verdict-class-row` (block-class rows count blocked verdicts only) in
`tools/policy/agreement.mjs`, and land `enumerate.py`'s hist family as an
agreement self-test arm.
