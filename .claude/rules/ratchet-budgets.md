---
description: A one-sided cap may only be re-recorded down for prose that was deleted, never for prose that moved
paths:
  - ".claude/workflows/policy_budgets.json"
  - ".claude/rules/**"
  - "CLAUDE.md"
---
# Three caps, because one of them can be gamed by moving a file

`.claude/workflows/policy_budgets.json` holds one-sided caps on the governance
corpus: a policy file may shrink freely and never grow past its cap. Deliberately
not the two-sided ratchet `tests/structure.py` applies to code — an "improved and
not yet recorded" refusal on prose would charge a seat for deleting a paragraph,
and deletion is what this corpus most needs. That asymmetry has a hole only
visible when three caps are read together.

**`always_loaded_tokens` measures a session that opens nothing.** `CLAUDE.md`
plus any `.claude/rules/*.md` with no `paths:` key — what the harness loads
before a seat has read anything. Moving prose out of `CLAUDE.md` into a
`paths:`-scoped rule therefore lowers it **without deleting a line**. Across the
split that made `CLAUDE.md` an index the floor fell by more than half while
`corpus_tokens` moved a fraction of a percent; run `--budgets` for both rather
than carrying either here, which `brief-citations.md` calls an error outright.
The scoping is a real improvement — what would be dishonest is recording that
drop as the ratchet, which hands the next pull request headroom nobody earned and
prices a scoped rule at zero however far it grows.

**`corpus_tokens` does not move when prose moves — while every capped file is a
measured one.** It sums the policy files the globs match, so a split between two
leaves it flat and only prose changes it. A cap on a file no glob matches
measures nothing, which made "give it a cap" a way OUT: prose moved into a
named, capped, tracked file bought headroom in **all five** with zero deletion.
That is refused now, and no extension escapes: the scan asks whether a path is
CODE, a list bounded by the tree, rather than whether it is a document — a list
that cannot be complete.

**`roles` charges a seat for what it loads once it opens a file.** Each entry
gives an `opens` list — one representative file per surface that role touches —
and the cap is the floor plus every scoped rule whose globs match one of them.
The floor is not the cost: at the same split every role paid more than the floor,
and the record seat more than the whole floor cap that preceded it. A cap only
the empty session meets is not measuring the thing it is named for. `opens` is a
fixed sample: widening it is an edit a reviewer sees, which stops a cap being met
by re-measuring against fewer files.

## Re-recording a cap

Lowering one is free **when the prose was deleted**. Lowering
`always_loaded_tokens` because prose moved is the case this rule exists for:
record it, and check `corpus_tokens` and every `roles` cap stayed flat in the
same diff. If the floor fell and the corpus did not, the saving is a
reclassification and the body says so in those words.

**Raising a cap is the LAST RESORT, and it needs the repository owner's explicit
confirmation, obtained before the branch is pushed** — the same gate
`CLAUDE.md` rule 2 puts on the structural ratchet, and it binds here whether the
change is a production feature or governance prose. The order is an order, not a
preference:

1. **Pay for it.** Cut prose that is spent, duplicated, or now carried by a
   mechanical detector; `writing-for-agents.md`'s uniqueness test
   decides most of it.
2. **If paying would cost something load-bearing, stop and ask.** Name the cap,
   the measured number `--budgets` prints, and what the raise buys. Ask before
   the push, not after: a raise discovered in review is a raise made quietly.
3. **Raise only on that confirmation, and only to the measured value.** A padded
   cap is headroom nobody earned, and it spends the next seat's argument too.

So three things are refused and one is allowed. Refused: a raise made quietly; a
raise taken instead of a cut the seat could have made; a raise asked for after
the push. Allowed, once approved: a raise where every honest cut has been made
and the improvement is still worth more than what remains.

This paragraph used to say a raise "to make a change fit rather than cutting is
the move `CLAUDE.md` rule 2 refuses", naming no owner path at all. It was
obeyed: a seat cut prose from a rule merged an hour earlier rather than ask.

`node .claude/workflows/policy_lint.mjs --budgets` prints every file against its
cap, the floor, the corpus and each role; write that, never a cap's value — one
stated beside its file's name is checked by `counts` in the corpus and the
record. The `budgets` class is held out of the known-bad ledger: a cap recordable
as a known defect is not a ratchet.
