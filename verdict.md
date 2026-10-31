Fix review: blocked e5cbb1a9aa2099efd7d9237ef1069d2f81996047 class-open: stateless lexicon passes four change-history passages left in docs/how-it-works.md and docs/dashboard-card.md

bus-nonce: 2575a5e88b8ba60162e8a76ef793eb73

Round 1. Measured at head e5cbb1a9aa2099efd7d9237ef1069d2f81996047 (still the branch head when this verdict was written), from a detached worktree; merge base 7539d1675d7fc8b5020f90b395f4bb0c3485d5b3; origin/main 9a9659c4f. Contract dev/governance/roles/fix-review.md at origin/main; its roles diff against the merge base is empty.

## Block

The brief's stateless item reads "no change history, round, PR or version-diff references in the user docs (grep them)", and the body states "the change history is gone from all seven". A grep at the head finds four passages that describe how the integration came to be, not what it does. Each one was already present at the merge base and is left as it was:

- `docs/how-it-works.md:172-177`: "Earlier versions added explicit anticipation terms on top. … Removing both made shoulder-season plans 4–6% cheaper …"
- `docs/how-it-works.md:1084-1087`: "Its upper clamp is now 1.0 rather than 1.05 … An existing learned derate survives the upgrade …"
- `docs/dashboard-card.md:519-524`: "Earlier versions sized the dialog from a fixed guess at how tall the surrounding chrome would be. …"
- `docs/dashboard-card.md:973-975`: "… or the older `space_heating_plan` / `dhw_heating_plan` (for installs upgraded from before the ids moved, and for integration versions older than 2.6.1)."

`check_stateless` passes all four. `stateless_findings` returns `[]` on both pages at the head and on each sentence planted alone (ev/stateless-survivors.txt). The arm's lexicon (`_HISTORY`, the design section 4 list) has no term for "earlier versions", "now X rather than Y", "upgraded from before" or a bare version number without a `v` prefix ("older than 2.6.1"). The class the brief names is wider than the rule the arm enforces, and the arm being green is not evidence that the pages are stateless. Repair: rewrite the four passages as statements of current behaviour, and widen the lexicon to cover these shapes (for example `\bearlier versions?\b`, `\bversions? older than\b`, `\bupgraded from\b` and a bare `\b\d+\.\d+\.\d+\b` outside the requirements and badge lines, with any literal use placed in `STATELESS_EXEMPT` with a reason), each with a red fixture and its null control. The arm then decides the rewrite, as carry udf-rewrite-list requires.

## Findings

- The four change-history passages listed under Block, and the stateless lexicon that passes them, are this group's to repair before the next handoff: the passages rewritten, the lexicon widened with a red fixture per new term and a null control. Carry: R10-USER-DOCS-FINAL
- R10-USER-DOCS-VERIFY reuses `check_stateless` unchanged (carry udf-method). Until this group widens the lexicon, a green stateless arm at VERIFY's base proves only the listed phrases absent. VERIFY's run has to read the widened arm, not the one at this head. Carry: R10-USER-DOCS-VERIFY
- Design departure, raised in the body: there is no `<!-- [target: R10-WOOD-NOTIFY] -->` marker on the Wood Cheaper Than Heat Pump row. I confirmed the cause: `dev/programme/rosters/wave-r10-groups.json` holds 0 `"R10-WOOD-NOTIFY"` entries at the head and at origin/main, while the group is in the roster at handoff/audit-r10-roster (f7572e88a, groups[248]). A marker there would be red under `marker_placement_findings`. So the stale-attribute signal the design wanted rests on that group's own carry udf-wood-homes (present at groups[248], carries 0 and 1), which tells it to document the window attributes. Its "resolve the marker" clause now finds no marker. Carry: R10-WOOD-NOTIFY

## Evidence

- RESULT doc_claims head: `ALL 277 checks PASSED`, rc 0 (ev/doc_claims-head.out).
- RESULT surfaces head: `--surfaces` rc 0; by class blueprint 4, card_option 10, card_view 6, entity 82, event 5, option 205, option_page 23, repair 26, service 14, setup_field 102, setup_step 15, 492 in all, matching the body's figures. The only `home-found 0` row is `option building_preset[questionnaire]`, the single `SURFACE_EXEMPT` entry, and its reason is a full sentence (ev/surfaces-head.tsv).
- RESULT disabled entities: 20 at the head. With the `entity_census` read reverted to the fork form, 9, and the suite goes red on the Wood Cheaper Than Heat Pump home. Both match the body (ev/entity-census-mutant.txt).
- RESULT planted wrong default (`Lowest compressor frequency` 20 Hz to 25 Hz, an option the fixture does not use): suite rc 1, `1 of 277 checks FAILED` on the coverage check naming `compressor_freq_min_hz`; `--surfaces` rc 1. The same holds for `Hot water minimum while away` 20.0 to 25.0 °C.
- RESULT planted undocumented service (`zz_probe_undocumented` in services.yaml): suite rc 1 on the coverage check; `--surfaces` rc 1.
- RESULT planted "This mode is new in v9." and "The card previously showed the price." in docs/setup.md: suite rc 1 on the stateless check each time. Null control "The price of the previous day is shown.": rc 0. Unmutated tree: rc 0.
- RESULT checker mutants (my own, on the mutation targets the body names): `_in_comment` returning False gives 4 of 277 FAILED; `default_agrees` numeric arm reduced to `m is not None` gives 1 FAILED; the `used to` purpose guard skipping every match gives 1 FAILED; the stateless exemption-once check `if False` gives 1 FAILED. Each is red on the checks the body names. The body's counts are mine plus its two export artifacts.
- RESULT `--markers --user`: `4 user-doc marker(s), 0 due`, rc 1 while N > 0, as the design specifies. The markers sit on the headings the design names (COP-GATE/COP-PARTLOAD, CEILING-PROBE, ARCH-SHAPES-CLASSIFIER, UX-HEALTH).
- Round-10 coverage: away mode and recovery (`docs/configuration.md` `### Away and holiday mode`, `docs/how-it-works.md` `## Away and holiday mode`, `set_away`); learner reset (`reset_heat_loss_learners` and the Learning Reset Heat Loss button in `### The house heat loss coefficient`, matching `_void_heat_loss_learners`, which resets both learners to their 1.0 defaults); the heat-loss learner's inputs and the estimated power reading (same section). The factory reset service and the wood blueprint and window attributes are not in the tree at this head (services.yaml has 14 services, blueprints/automation has 4 files), so they are in-flight surfaces under the design's section 3 and the carries udf-reset-homes and udf-wood-homes.
- Claim table samples resolved: `QUICK_SETUP_BUFFER_VOLUME = 500.0` (quick_setup.py:83); the reset path as above.
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 (tree 34cb8f65f), with no conflict.
- Claim files: `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are byte-identical to origin/main. VERSION, the manifest and RELEASE_NOTES.md are untouched in the three-dot diff.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. Scoped gate: `MODE: SCOPED -- 6 script(s) run, 27 scoped out.`
- Delivery row: `dev/programme/delivery/3048.md` is added in the three-dot diff.
- Forward carries: udf-method and udf-surfaces-cwd (R10-USER-DOCS-VERIFY, groups[254]), udf-wood-homes and udf-blueprint-closure (R10-WOOD-NOTIFY), udf-reset-homes (R10-FACTORY-RESET), udf-marker-scope (R10-ARCH-DOCS) and udf-strings-history are all present on handoff/audit-r10-roster f7572e88a, which descends from the body's 315cd0441.
- CI: `merge_train.py classify` printed `GREEN e5cbb1a9aa2099efd7d9237ef1069d2f81996047 pending: none red: none` (rc 0). No check on this head went red, so step 11 owes nothing (ev/classify.txt).
- Finder's harness: the packet names none. This is a feature group; the design's arms are the instrument, and I re-ran them as above.
- The body's base-export figures (181 unhomed and 51 stateless hits on 460d7754f) were not re-derived here; I verified only the head figures.
