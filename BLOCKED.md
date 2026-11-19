# BLOCKED: R11-SEAM-comments-tests fixer, base 1723f9fdc9d8a6e6987190d2887686297a621dd4

Question: Which group writes the shared 40-word comment ratchet script, R11-SEAM-comments-tests p1 or R11-SEAM-comments-production p1? The approved design (design.md at a2823ffea00a570b2cba42ba6f65e3965ea96942, section 7, "Routed, decision: orchestrator") holds both p1s until the orchestrator confirms one writer and lands the carry in that group's roster brief. The design verdict at 1c8074afc1 restates it as still open.

What was checked:
- Roster `origin/handoff/audit-r10-roster` at 83ef6bc324: `R11-SEAM-comments-tests` has `carry: []`, and `R11-SEAM-comments-production` has `carry: []`. Neither brief names a writer.
- `git grep -i "ratchet-lands-in-tests"` over that roster ref and over origin/main under `dev/programme` and `.claude/workflows` finds nothing.
- The dispatch payload (dispatch/fixer-r11-seam-comments-tests at e975d44c5c) states no ruling.

Parts p2 and p3 are not gated by the routed decision, but the design's per-part evidence (section 6) reads each part's files at 0 in the ratchet, so they need p1 first.

To unblock: land the ruling as a carry in the chosen group's roster brief. If the writer is this group, the fixer builds p1 as section 3 A specifies. If the writer is comments-production, this group's p1 shrinks to the tests scope addition and is dispatched after that part merges.

No code was written.
