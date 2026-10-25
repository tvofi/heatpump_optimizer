Design review: approve f122a1cb5d6aea08bb57840721e646c87f3c51fd

Delta review of dev/programme/designs/R10-ARCH-DOCS-FIRST.md, `git diff 16954f0c8 f122a1cb5`. Read at main c1e1967bc (0b162da1a or later) and roster ref handoff/audit-r10-roster. Points the first review accepted are not re-opened.

## Revise points 1-3

- R1 (predicate c): fixed soundly. (c) prints `note:` lines and returns no finding at any roster state (§6 line 134). "No target or retired-by marker names a done group" moves to R10-ARCH-DOCS's end-of-round predicate, as a stated carry (§3 line 90), and the resolution text says it goes red "there, and only there" (line 88). A roster-sync PR that marks a group done cannot turn doc_claims red through (c). Carry: R10-ARCH-DOCS (item R1)
- R2 (predicate a): fixed soundly. (a) exempts `retired-by` paths as well as `target` paths (line 132). The invariant sits beside the grammar (line 78) and is restated per predicate (line 138). I checked each predicate for state tolerance:
  - (a): a marked path passes whether present or absent.
  - (b): reads a roster key, never a stage. On main's first-parent history no group key has ever left wave-r10-groups.json; the drops seen on side branches never reached main. Today the roster ref has no group that main lacks.
  - (c): report-only.
  - (d) and (e): read no roster at all.
  Carry: dismissed: fixed as asked
- State-tolerance control (line 142): sound. A marker naming a stub-`done` group, and a `retired-by` path absent from the stub tree, must both yield no finding. The mutation-proof line (145) requires that control to kill a mutant that makes (c) refuse. The same absent-`retired-by` case also kills a mutant that drops the (a) exemption. The two remaining states are covered by the real-tree arm: a `retired-by` path that is still present (`.github/workflows/pr-contract-rerun.yml` today), and an absent `target` path. Carry: dismissed: control adequate as specified
- R3 (work order): fixed. §1 (line 42) reads audit → [design → design review, L/XL] → fix → fix review → train → merge → record → stamp. That matches dev/governance/roles/orchestrator.md:128-131, designer.md:7 and design-review.md:26: the fixer dispatches only after `Design review: approve <sha>` is read back. §4 (line 99) opens the one-handoff sequence with designer → design review and makes the approve read-back the step that dispatches the fixer. Carry: dismissed: consistent with roles

## C1-C9, C11 folded; C10

- C1: folded, item T1a (line 146). Carry: R10-ARCH-DOCS-FIRST (item T1a)
- C2: folded (line 141). The red fixtures add `pie` and `%%{init: ...}%%`, and the roster is an inline stub. Carry: R10-ARCH-DOCS-FIRST (item T2)
- C3: folded (line 135). "Declared" means a shaped appearance or a bare id used twice or more. I checked the real-tree arm against main:
  - docs/architecture.md's `flowchart LR` passes. Every edge endpoint is shaped, and the subgraph ids are shaped once.
  - README.md's `sequenceDiagram` (line 788) declares every endpoint with `participant`, so it passes too.
  The fallback that drops the arm is kept. Carry: R10-ARCH-DOCS-FIRST (item T3)
- C4: folded. D2 is rerouted to R10-PLAN-ARTIFACT, and ORCH-MACHINERY confirms that its builder extends the one model. Carry: R10-PLAN-ARTIFACT (item D2)
- C5: folded. REPLAY-LANE is corrected, it is a decision: orchestrator, and the notice also goes to R10-REPLAY-SCOPED. Carry: R10-FLOW-BOARD (item D5)
- C6: folded (line 127). The closure grows by the roster, dev/README.md and the workflows read, and (b) accepts main's roster only. Carry: R10-ARCH-DOCS-FIRST (item B1)
- C7: folded (lines 101-105). The four ORCHESTRATOR-PROMPT shape rules each appear as a node or marker. Carry: R10-ARCH-DOCS-FIRST (item O2)
- C8: folded (line 159). Both dev/ hits are listed, and the scope of (e) is explicit. Carry: R10-ARCH-DOCS (item S1)
- C9: folded (line 120). Carry: R10-ARCH-DOCS (item V2)
- C10: folded (line 167). The hot-file list names dev/README.md, tests/doc_claims.py, tests/layout.json, tests/closure.py, tests/closures.json and tools/site/build_docs.mjs, for the PR body. Carry: dismissed: orchestrator owns roster files
- C11: folded. I1 is replaced by the O-2 mapping (line 178). Carry: dismissed: superseded by O-2 decision

## New observations (none blocking)

- N1. Roster archival, a state the invariant at line 78 claims to cover ("at every roster state"). Earlier waves' rosters were moved to dev/archive/rosters/ (wave-4, wave-5, wave-r8, ...), so wave-r10-groups.json is likely to move after programme end. (b) and (c) read that fixed path. If the function opens it unconditionally, the archiving PR turns doc_claims red, and doc_claims' closure includes the roster. Fix wanted: read the roster only when at least one marker is present, so a resolved tree reads no roster, and add a null-control case with no markers and no roster file. This is a fixer-level detail, not a design defect: R10-ARCH-DOCS resolves every marker before any archive move. Carry: R10-ARCH-DOCS-FIRST (item B1)
- N2. Hot files (line 167) lists tools/site/build_docs.mjs twice: once as already in the roster's files per O-1, and again as "beyond" them. This is cosmetic, and the fixer's PR body should list it once. Carry: dismissed: cosmetic duplicate listing
- N3. (d) now requires `participant`/`actor` declarations in a sequenceDiagram, although mermaid allows implicit participants. This is stricter than the renderer, but every block it governs is authored by this fixer, and the README block already declares all of its participants. The one-handoff figure must therefore declare its participants. Carry: R10-ARCH-DOCS-FIRST (item T3)
- N4. The roster now sits in doc_claims' closure, so every roster-sync PR runs doc_claims. With (b) reading keys only and (c) report-only, that cost buys a correct check and cannot go red on a done mark. Carry: dismissed: accepted gate cost
