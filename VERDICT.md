Fix review: blocked b43ea5411dde498afea692247c6b53d651f4e6f3 class-open: a getter that hands state out through an argument, or is called other than as self.m(...), still lowers seam_cut_total with nothing moved

bus-nonce: 3d4feedbc0095b02431b4e62e4c3f414

## Round

This is the fix review of repair round 2. Round 1's review returned `blocked class-open` on `5021b50de`. This is the second review. A third would put the PR in `fixer.md`'s re-cut territory from the fourth.

## Block

The class is O19: an equivalent spelling of the same reads lowers `seam_cut_total` with nothing encapsulated. The body says the return-value rule closes it ("Any spelling nobody enumerated carries by default"). It does not close it. The rule prices only state escaping through a callee's **return value**, and only from a call spelt `<root>.m(...)`, a property read or a helper handed the root (`callee_of`). It misses two seams. Neither is in the diff, and the body dispositions neither.

1. **Out-parameter and callback getters.** The callee hands its reads to the caller through an argument it was handed. The callee is non-transparent (it stores), so it costs the one edge, and nothing escapes. Read by the PR's own plant (`_cop_state` in learning, read from `_scores_view`), `ev/variants.py`:
   - head: clean 367; `outparam_dict` 363, `outparam_append` 363, `outparam_attr` 363, `outparam_extend` 363, `callback` 363 (**-4 each**).
   - merge base `73b69fe0a`: clean 710; the same five read 708 (-2).
   - So the head **doubles** the gain these spellings pay. The plant drops the two reads from `_scores_view`, and with them the transitive charge the new rule puts on `_scores_view`'s cross-seam callers. Here the transitive charge amplifies the gaming.
2. **A unit call spelt other than `<root>.m(...)`.** For `type(self)._cop_state(self)` and for a bound-method alias `g = self._cop_state; g()`, the call is opaque. It carries no edge, and nothing escapes. Head: 361 each (**-6**). Merge base: 706 (-4).

Both seams reproduce at both ends, so they are older than this PR. But the PR claims the class closed, and this review's round-1 block was the same shape: the escape rule is again an enumeration, now of call shapes and of the return channel. The census rule the body names (`returned_state`, and calls crossing into those units) cannot return either seam: an out-param callee has an empty `returned_state`, and the census's syntactic `.name` scan is never compared with what `seam_metrics` actually prices.

## Findings

- A callee that stores state into an argument it is handed (`out[...] =`, `out.x =`, `out.append/extend`, or calling a handed callback) passes that state to its caller unpriced, and costs one edge in place of k reads. Head -4 against the clean tree, merge base -2 (`ev/variants_head.txt`, `ev/variants_base.txt`). Close it in `seam_metrics`, either by charging a unit call with what the callee stores into its parameters, or by disposing of it in the body with a rule. Carry: R10-STRUCTURE-ALIAS
- A unit call spelt `type(self).m(self)`, or through a bound-method alias (`g = self.m; g()`), is neither an edge nor an escape: head -6, merge base -4. `callee_of` should resolve these, or the body should disposition them. Carry: R10-STRUCTURE-ALIAS
- `getattr(self, '_cop_state')()` (head 361, -6) and `getattr(self, '<const>')` reads in a getter body (head 363, -4) are covered by the body's computed-name disposition ("invisible to the cut in both trees, not a return-value seam"). With a constant string, though, the name is not computed, and the head's gain is larger than the base's (-4/-2 there). The fixer should decide whether a constant-name `getattr` is resolved or the disposition is widened to say "constant" explicitly. Carry: R10-STRUCTURE-ALIAS

## Evidence

- Head measured: `b43ea5411dde498afea692247c6b53d651f4e6f3` (`ev/HEAD.txt`). `git ls-remote` showed it still the head of `fix/r10-structure-alias` when the verdict was written. Merge base with origin/main: `73b69fe0a9fa9e45736cd1cdbc2077d3958b41ec` (main's tip).
- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Merge: `git merge-tree --write-tree origin/main b43ea54` rc=0, tree `856c3ac7e`, no conflict (`ev/merge-tree.txt`).
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (three-dot diff empty). The diff touches no golden or claim file (5 files: harness, delivery row, closures.json, structure.py, structure_budgets.json), so the `env_drift.py --all` comparison has nothing to compare.
- `tests/structure.py`: head `STRUCTURE RATCHET PASSED`, `seam_cut_total 367 <= 367`; merge base 710 <= 710 (`ev/structure_*.txt`). The budget diff moves only `seam_cut_total` 710 -> 367 and `recorded_at`. This is a downward re-record.
- Finder-plant harness `dev/audit/harnesses/r10_structure_alias.py`, sha1 `0f6a9978a77e7cf8486009949fcf0f9a8756cfbf` (it matches the body). Head: clean 367, all 9 plants 367. Base (harness copied in): clean 710, all plants 708. Census at head: `units_returning_state=125`, `transparent_callees=76`, `units_returning_coordinator=2`, `cross_seam_calls_of_state_returners=68`. All match the body (`ev/harness_*.txt`).
- Seam table and per-seam cuts: read from `ev/structure_*.txt` and consistent with the totals. I did not re-derive the 68-pair disposition pair by pair.
- My own mutants (`ev/mut_*.txt`), each run against the full `tests/structure.py` and then restored:
  - R1, transparency off: rc=1, the getter and root-getter checks are red.
  - R2, escapes not charged: rc=1.
  - R3, yield not a return: rc=1.
  - R4, AnnAssign not an alias: rc=1.
  - R5, occurrences back: rc=1.
  - The mutation proof holds for what the PR prices. The block is on what it does not price.
- `ev/variants.py` is my own instrument, not the finder's. It uses the PR harness's `planted`/`seam_cut` and adds 16 spellings. The 9 body-shape spellings (nested def, lambda call, dict unpack, `+=`, try/finally, if/else, plain, among others) read 367 at the head, so the return rule covers those.
- CI on the head, read from the check-runs API at about 16:30Z: no check concluded red. Still running: `tests / arch-instrument`, `codeql / Analyze (python)`, `tests / graders-head-copy` and one `prelude`. `tests / mutation` is green. This PR writes no production code line, so the green mutation run evaluated no production mutant. There is no red check, so the root-cause trigger does not apply at this reading.
- Forward-carry: the body says n/a. Accepted for the merged figure. The findings above stay with this group's repair.
