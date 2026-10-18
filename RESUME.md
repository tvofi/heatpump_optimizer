# RESUME: #2404 round-5 fixer (cloud seat)

- Code: `handoff/r10-carry-enforce` fast-forwarded to 6f20f78a3e1d8ae387cd227fa05131f0856ed6e3 (on 312f31923, plus a merge of origin/main 176851e95, with no conflict).
- Body: re-cut to the template headings, per fixer.md's past-three-rounds rule. Every figure was re-taken in this pass, and the round history is removed.
- The round-4 block (M15b, M16 surviving alone) is answered. Each mutant now dies alone, killed by its own row in the self-test's marker-grammar table.
- Sweep: `dev/audit/harnesses/r10_carry_parser_mutants.py` covers the whole parser (items(), the marker grammar, the routing, the ledger key, and every regex alternative). Result: sites=152 unmapped=0 mutants=190 survived=0. Its first run found 47 survivors in items() and 39 regex-vocabulary survivors. Each one was either pinned by a row or deleted as dead code; the commit message of 6f20f78a3 lists the deletions.
- Behaviour changes a reviewer should judge:
  - Routing by reference is now the union of every marker that names an item, and each destination must hold. It was first-wins before.
  - A code span may now cross a line ending, as in CommonMark.
- Not re-run here: the `--ledger` figure, because SEATS.md is outside the tree, so the body drops it. The O-brief destinations print UNVERIFIED, because no briefs dir is available in this container.
- No hook or refusal was worked around.
