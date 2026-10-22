Design revision: R10-ARCH-DOCS-FIRST r2 f122a1cb5d6aea08bb57840721e646c87f3c51fd

Ref refs/heads/design/r10-arch-docs-first, one fast-forward commit on 16954f0c8e7243004a6adcf69c9f28acbca23607. Note: dev/programme/designs/R10-ARCH-DOCS-FIRST.md. The new "Revision 2" section maps each item.

- R1: (c) is report-only (`note:` lines, never a finding). "No marker names a done group" is R10-ARCH-DOCS's end-of-round predicate. Carry: R10-ARCH-DOCS (item R1)
- R2: (a) exempts `retired-by` paths too. The state-tolerance invariant (every predicate holds before and after the named group lands) sits beside the grammar in §3, and §6 restates it per predicate, with a state-tolerance control fixture.
- R3: work order audit → [design → design review, L/XL] → fix → fix review → train → merge → record → stamp in §1. §4's handoff path opens with the design-verdict read-back for L/XL.
- C1: local `mermaid.parse` (npm ci in tools/site) before handoff, result recorded in the PR body (item T1a).
- C2: red fixtures added for an unknown diagram type (`pie`) and `%%{init`. The roster is an inline stub, never the live file (item T2).
- C3: "declared" is defined: a shaped appearance, or a bare id used at least twice. A once-only bare id is red. If the real-tree arm cannot pass, the arm is dropped in favour of T1a (item T3).
- C4: D2 is rerouted to R10-PLAN-ARTIFACT (owner by §2.3). ORCH-MACHINERY confirms its builder extends that one model.
- C5: D5 is corrected (REPLAY-LANE is on tests/replay.py and nightly.yml). It is decision: orchestrator, with Carry: R10-FLOW-BOARD and notice to R10-REPLAY-SCOPED.
- C6: §5 states the closure growth (roster, dev/README.md, workflows read). (b) accepts only groups in main's roster (item B1).
- C7: §4 maps the ORCHESTRATOR-PROMPT shape rules: ruleset cut-over owner step with read-back and rollback, head-SHA/blocked verdict, pitch gap rule, and 0 open PRs as the end state (item O2).
- C8: Sibling sites lists the two dev/ mermaid hits, and (e) is scoped to the reader docs plus dev/README.md (item S1).
- C9: §4 notes that dev/README.md figures get GitHub themes only. R10-ARCH-DOCS confirms both renderers (item V2).
- C10: Hot files lists dev/README.md, tests/doc_claims.py, tests/layout.json, tests/closure.py, tests/closures.json and tools/site/build_docs.mjs for the fixer's PR body (item F2, dismissed: orchestrator owns roster files).
- C11: I1 is replaced by the O-2/C7 mapping (dismissed: superseded by O-2 decision).

All earlier carry lines are kept (M1, V1, T1, D1, D3, D4, F1). D2 and D5 are re-targeted as the verdict asks.
