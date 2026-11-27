Fix review: merge 3f7c5c524ec9baf808e09fb6b8e6b3b344544428
bus-nonce: 363ab6c1258b81e0ba730083c1ca36dd

Scope: full, first round, three-dot over 7b0ddc205f...3f7c5c524e (6 files, no custom_components line).

Harness: the packet names no finder's harness; this group's judge is its approved design (revision 5, design-verdict 4ee63e99aa). I drove the design's three refusal conditions on the live tree with my own perturbations, not the fixer's entities.py controls:
- one line appended to tests/features.py: `lines` refusal, 104574 > 104573, rc 1;
- one section title renamed (`Input staleness watchdog (item 12b)`): `span` refusal by name;
- a new tests/features_plan.py whose only span imports thermal_model: `seam` refusal naming tests/features_model.py; the same text as tests/features_model.py: HOLDS;
- unperturbed tree: `FEATURES FREEZE: HOLDS (0 refusal(s))`. The manifest equals the tree (104573 lines, 252 spans); origin/main has not touched tests/features.py since the merge base.
Seam table: no module listed under two seams; every listed module exists in the package. Home counts sum to 252.
tests/closures.json: tests/entities.py's closure adds exactly the harness and the manifest and already holds tests/features.py, so an edit to the frozen file selects the freeze check.

Raise (mandate 6893738184, scope all): sound. The raise is the creation of a new FROZEN manifest; no existing cap moves, and the new file only tightens. The body's `## Raise justification` lists three payments tried (a non-budget manifest name, constants in entities.py, the split itself), each refused for a stated reason, and carries `Architecture score: dS +0.0000 NULL`, which I reproduce at the head. The only payment that would improve the architecture is the split, refused on a priced cost; that decision is recorded as pending owner confirmation, as it must be.

CI at the head: budget-raise-gate red by design (two RAISE lines, both this manifest); tests / mutation red on the inherited flow_lift 04143c3f stale pin (main's, #3939); nightly-status red on last night's nightly. tests / fast 1-4 all success on Linux, `ALL 2800 ENTITY CHECKS PASSED`: the two Darwin timing failures the fixer reported do not reproduce on CI.

Note: carry-residual: Carry 0's part for R11-PRE-SHARED-FILES, R11-OWNER-CARD-EXTERNAL-HEAT and R11-SEAM-learners is not built and is recorded honestly as kept on this group's carry, with roster_edit.py's refusal quoted; it must be written to those briefs when they leave carries-open. Carry: R11-OWNER-FEATURES-SPLIT
Note: seam-closure: tests/entities.py reads tests/features_*.py by glob, so a later PR that edits only a seam script selects that script, not tests/entities.py, until entities.py's closure is re-measured with the seam script present; the brief text for the appending groups names only the new script's own closure. Carry: R11-OWNER-FEATURES-SPLIT
