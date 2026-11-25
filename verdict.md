Design review: approve 25fa1f763e93dafe29de7bae8ca77fc527b67a25

Group R11-CI-CASE-SELECT, revision 2 at 25fa1f76, a fast-forward on e50b4a1f (one file, design.md, +57/-17).
Delta review under design-review.md: git diff e50b4a1f 25fa1f76, plus the three points of revise c90cde83.

1. Header fail-safe (was design.md:88): resolved. A head header_hash differing from the table's forces CASES: FULL
   on its own, independent of the blob arm; evidence 4 makes "header edit with blob = merge base gives FULL" a
   failing-first case and the header_hash arm alone a mutation target.
2. Backward-only needs (was :74/:79): resolved. Rule (iii) is now the forward closure from (i ∪ ii), rule (v) the
   backward closure over everything selected, computed to a fixed point; static needs come from the head's AST at
   plan time; in-place calls and setattr bind their target (top-level counts 116/24 confirmed at 34c7a3f610);
   stdlib state is a pseudo-binding per setter family; an unclassifiable setter or a span-level
   global/exec/globals() write forces FULL; the dynamic fingerprint adds length and content hash for containers.
3. Replay without a null (was :121): resolved. Evidence 5 is driven by >=200 seeded, stratified mutation-ledger
   pins at sample fraction 0, requiring a FAIL; null 1 (rule (i) off for the mutated file) must let >=90% pass,
   null 2 (unmutated tree) prints no FAIL; the history replay stays as a second check, and the measurement table
   names its same-runner FULL null.

Carries for the fixer (not revise points):
- Carry: R11-CI-CASE-SELECT (item rng-consume) -- an RNG consumer also advances the state, so count a consuming call
  as binding its @random family as well as reading it; otherwise an edited span that draws a different number of
  values changes later consumers without the forward closure seeing it. RNG drawn inside production code (not
  visible to the span AST) needs the same rule through the recorder, or a FULL trigger.
- Carry: R11-CI-CASE-SELECT (item pin-count) -- the note states 4229 pins killed by tests/features.py; a count of
  "killed_by" values under tests/mutation_ledger at 34c7a3f610 gives 4215 (entities 305 matches). Derive the
  number at run time and print it rather than carrying it.
Routed: none.
