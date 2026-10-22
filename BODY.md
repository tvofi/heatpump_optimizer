# design-r10-arch-docs-first: designer result

Design SHA: 16954f0c8e7243004a6adcf69c9f28acbca23607 on refs/heads/design/r10-arch-docs-first.
- One commit; its parent is 8a4c438e7d9a6e2c492a1733d658d96b7b1eedcf.
- File: dev/programme/designs/R10-ARCH-DOCS-FIRST.md.
- Roster read at b93ece169acfa8c97b469bbb18df06267aa14f6f.
- `node tools/policy/brief_lint.mjs`, run over the note wrapped as a one-group roster: 0 errors.

The six points:
1. **Document map.**
   - `docs/architecture.md` keeps its tree-exact counted sections, because `tests/entities.py` pins them. The seed's four-region diagram is re-derived at base (the seed is 2437 commits behind and states 77 modules against the tree's 81). A new marked section describes the shape at programme end.
   - A new `dev/README.md` holds the onboarding, requirements, CI job graph, refusal order (folding the seed's CI-GATE.md), machinery components, one handoff's path, who decides, and a by-command harness index (the O9 fold).
   - `README.md` gets a one-line pointer.
   - `tests/layout.json` gets a `dev` category.
   - Carry: R10-ARCH-DOCS (item M1)
2. **Final shape.** The inputs are:
   - every group whose stage is not done, with its brief, after, carry and architect note, enumerated by jq on the roster;
   - the design refs: orch-machinery 09174d94e §6.2 and §6.3, review 0bd5d12f0, CI-LAYOUT-P2's DESIGN-P2.md at 1371a0a6, open `design/*` refs;
   - the plan page, from replan.py and plan_page.py, plus the plan of record.

   What is on main is written from the tree; the rest is written from the owning group's brief and marked. A disagreement is drawn the way its owning group's brief states it and routed by a Carry. The note routes five: D1 (as-built vs final shape), D2 (four claimants of the plan page/model), D3 (one shared path checker with R10-ROUND-PLAYBOOK), D4 (ruleset to a single gate as an owner step), D5 (REPLAY-SCOPED, REPLAY-LANE and FLOW-BOARD edit workflow files with no after edge to CI-LAYOUT-P2).
   - Carry: R10-ORCH-MACHINERY (item D2)
   - Carry: R10-REPLAY-SCOPED (item D5)
3. **Marker grammar.**
   ```
   "[target: R10-X(, R10-Y)*(; owner step)?]" | "[retired-by: R10-X]"
   ```
   - One regex finds markers in prose and mermaid labels alike.
   - Marked text states no numeral, because doc_claims and entities read numerals against the tree.
   - Example: `R[("ruleset requires only gate<br/>[target: R10-CI-LAYOUT-P2; owner step]")]`.
   - Carry: R10-ARCH-DOCS (item M1)
4. **Diagrams.**
   - The set: architecture flowchart, CI umbrella job graph, refusal order, machinery components, and one handoff's path as a sequenceDiagram.
   - Format: GitHub mermaid with no hex and no `%%{init}`. Meaning is carried by node shape (seat, script or detached job, decision, ref or store, dashed planned edge), so it reads in both themes.
   - Colour comes from the renderer. The one tree read is a token map from docs/site/docs.css into build_docs.mjs's mermaid theme. build_docs.mjs is outside this group's files: decision: orchestrator.
   - Committed SVGs lost because mermaid is installed only by the Pages job.
   - Carry: R10-ARCH-DOCS (item V1)
5. **Budgets.**
   - Nothing written matches POLICY_GLOBS, and no CLAUDE.md row is added, because `--budgets` reports always-loaded already above its cap and inside its band. No raise.
   - The structure budgets are code-only and untouched.
   - `tests/doc_claims.py`'s closure grows by `dev/README.md`. Re-record it with `--single` or through the UNDER-SCOPED autofix.
   - Carry: dismissed: no payment needed (item B1)
6. **Fixer's test and control plan.**
   - One new findings function in tests/doc_claims.py checks: paths resolve or carry a marker; markers are well formed and name a roster group that is not done; mermaid edges refer to declared nodes and blocks open with a known type; no hex or init.
   - Red fixture: inline strings with a renamed path, `R10-NOPE`, a marker naming the done group R10-CI-LAYOUT-P1, an undeclared node, and a hex fill.
   - Null control: the same strings, corrected.
   - Real-tree arm: the committed docs.
   - Mutation proof: the path-resolution and done-group predicates.
   - A real mermaid.parse is deferred to R10-ARCH-DOCS.
   - Carry: R10-ARCH-DOCS (item T1)

Stops and refusals: none.
- The Lean flow study's ORCHESTRATOR-PROMPT is on no ref this seat can read. Carry: dismissed: orchestrator supplies it (item I1)
- O9 resolves to no file in the tree, so the harness index is drawn from the deleted `tools/audit/harnesses/README.md` (72826387f) and the directory itself. Carry: R10-ARCH-DOCS-FIRST (item O9)

Seat token count: not reported by this harness.
