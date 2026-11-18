# BLOCKED: r11-carry-drawmap, part 1 of 3 (carries 0-4)

Question: Do owner rulings S1-S4 of 2026-11-14 (design/R10-DRAW-MAP-EVIDENCE 9aa450f5) still stand at origin/main 7938522854 — S1 sweep allowed on a flat price, S2 trace text columns in the diagnostics download, S3 the ceiling probe armed before the fit where the pump's top is unlearned, S4 the D15.md line prepared in the part F pull request?

Why the build stops here: the group brief says "Owner rulings S1-S4 (carry 2) gate the build: ask before the first part", and the approved note (design/R11-CARRY-DRAWMAP a1688d8d6a, decisions routed: owner) has the fixer confirm them before part A pushes. This seat has no owner channel. The dispatch does not record a confirmation. RULINGS.md at origin/main says the 2026-11-14 rulings are retired into the group's roster entry. A search of issues and pull requests for CARRY-DRAWMAP and the S3 wording finds only #3659 (closed). Under either reading of the gate (before the build, or before the first push), no code can land on a step ref before the answer. The verdict (design-verdict/R11-CARRY-DRAWMAP 2e7c39a4d9) also routes the "before build" against "before push" wording to the orchestrator.

State: no code built. The seat is set up: cloud-setup --check OK, unshallowed, base origin/main 7938522854d4ffb6be3c42bb227caab87b4ec66b.

On a yes, part A is re-dispatched on the note's plan: port archive/handoff/r10-draw-map-evidence-a cc335482ae with B's typing narrowing 8b4c27bb52 (carry 12), and point the null mutant at the sweep exclusion in draw_range.fold (verdict note null-mutant-site).
