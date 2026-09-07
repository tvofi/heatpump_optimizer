---
description: A one-sided cap may only be re-recorded down for prose that was deleted, never for prose that moved
paths:
  - ".claude/workflows/policy_budgets.json"
  - ".claude/rules/**"
  - "CLAUDE.md"
---
# Three caps, because one of them can be gamed by moving a file

`.claude/workflows/policy_budgets.json` holds one-sided caps on the governance
corpus: a policy file may shrink freely and may never grow past its cap. They
are deliberately not the two-sided ratchet `tests/structure.py` applies to code
— an "improved and not yet recorded" refusal on prose would charge a seat for
deleting a paragraph, and deletion is what this corpus most needs.

That asymmetry has a hole, and it is only visible when three caps are read
together.

**`always_loaded_tokens` measures a session that opens nothing.** `CLAUDE.md`
plus any `.claude/rules/*.md` with no `paths:` key — what the harness loads
before a seat has read anything. Moving prose out of `CLAUDE.md` into a
`paths:`-scoped rule therefore lowers it **without deleting a line**. Measured
across the split that made `CLAUDE.md` an index: the floor fell from 6800 to
3198 while `corpus_tokens` moved from 57398 to 57325 — a 53% drop against 0.13%
of actual deletion. Nothing about that is dishonest, and the scoping is a real
improvement; what would be dishonest is recording the 53% as the ratchet, which
hands the next pull request headroom nobody earned and prices a scoped rule at
zero however far it grows.

**`corpus_tokens` does not move when prose moves.** It sums every capped policy
file, scoped or not. A split leaves it flat; only a deletion lowers it and only
new prose raises it. It is the cap that makes a re-record of the floor safe.

**`roles` charges a seat for what it loads once it opens a file.** Each entry
gives an `opens` list — one representative file per surface that role touches —
and the cap is the floor plus every scoped rule whose globs match one of them.
The floor is not the cost: measured at the same split, a fixer pays 5645 and a
policy seat 9424 against a floor of 3198, and a record seat pays 6819, which is
**above the 6800 floor cap that existed before the split**. A cap that only the
empty session meets is not measuring the thing it is named for.

`opens` is a fixed sample, not an exhaustive list. Widening it is an edit to the
budget file that a reviewer sees, which is the point: it stops a cap being met
by quietly re-measuring against fewer files.

## Re-recording a cap

Lowering one is free and needs no ceremony **when the prose was deleted**.
Lowering `always_loaded_tokens` because prose moved is the case this rule
exists for: record it, and check that `corpus_tokens` and every `roles` cap
stayed flat in the same diff. If the floor fell and the corpus did not, the
saving is a reclassification and the pull-request body says so in those words.

Raising any of the three is a deliberate edit visible in the diff, and the body
carries the case. Raising one to make a change fit, rather than cutting, is the
move `CLAUDE.md` rule 2 refuses for the structural ratchet and this rule refuses
here.

`node .claude/workflows/policy_lint.mjs --budgets` prints every file against its
cap, the floor, the corpus and each role. The refusal is the `budgets` check
class, which `.claude/workflows/policy_lint.mjs` holds out of the known-bad
ledger by name: a cap that can be recorded as a known defect is not a ratchet.
