Design review: approve b83de87857f47db68df2a33cb64d2570cd8d1235

Group R11-OWNER-FEATURES-SPLIT, round 3. Note at design/r11-owner-features-split b83de87857f47db68df2a33cb64d2570cd8d1235 (revision 3 of the orphan design.md). Delta reviewed: git diff f4c840caf0 b83de87857. Base re-read at origin/main ef797d794017c98f7fb2d8a168d7de63d435ef3b, the note's stated base. Spike read at dab20b60ec. No full re-review: the delta changes sections 1-4 and leaves the seam, order and budgets as revision 2 stated them.

Re-measured at the base and confirmed: the enumerator piped through the spike's refclass.py exits 0 and prints 1151 lines in 199 files, split R 34/9, T 15/7, L 185/53, S 55/8, H 55/12, B 4/4, P 13/10, D 790/112. That matches section 3. `git grep` counts 23 lines in 16 custom_components files. `DhwPlanner._build_dhw_requirements = _lg_build_spy` is at tests/features.py:40855. The spike's p0.diff is the two-line P0, and d_p0.txt prints "differing spans 0" over 252 spans and 6409 lines. Sibling design/R11-CI-CASE-SELECT is unchanged at 25fa1f763e.

Prior points:
- V1: resolved. In section 1, the gate is the swap run's difference set for both --check and --port. The T5 edge list is advisory, and non-load-bearing edges remain by design. The measured P0 is 2 spans, and one edit makes the set empty. A planted three-family positive control and a one-part null back it.
- V2: resolved with option (a). Rule-1 rows are driven with a --plan. The note states the cost and adds the sample-and-report gate. The cross-part perturbation is a planted save in part X whose value is checked in part Y, and the X drive must print not killed.
- V3: resolved. Every enumerator line falls in one of eight classes, each with a disposition. The instruments (verify_eight, features_block, prepr, shards, entities censuses) are retargeted. Live citations are rewritten, and dated records are excluded. The production comment edits are in the group, with an ast and wc check, and the note states the full-run consequence.

## Notes for the fixer

C1 design.md section 4 rule 1 and section 5 "Pins and kills". The rule lets a lost kill be "reported" and the parts' total come out "less the lost kills". The owner's brief is to keep every mutation kill. A killed_by row removed or left pointing at a deleted script also grows the derived unpinned-site count that tests/mutation_budgets.json ratchets. Restore every lost kill inside its part, by moving or copying the reading check or by seeding it in part. The kill null is then exact equality. An irreducible lost kill goes to the owner before push. decision: owner. Carry: R11-OWNER-FEATURES-SPLIT (item C1)

C2 design.md section 4 rule 2. The figure 100948 CPU-s is a floor (the first candidate kills every row), not a ceiling. The real ceiling is 2166480. "Both ceilings together are 187840" understates the worst case. The 100000 CPU-s sample-and-report gate covers this. Extrapolate from the sample's measured candidates-per-kill, not from the floor. Carry: R11-OWNER-FEATURES-SPLIT (item C2)

C3 spike refclass.py RUN and TABLE_LINES. R and T are keyed by (file, line) at ef797d79, so they drift as main moves. The committed --check must classify by content or anchor, not by line number. Otherwise it refuses lines that merely moved. Carry: R11-OWNER-FEATURES-SPLIT (item C3)

N1, N4, N6, static-ceiling and swap-limits stay carried as the note states them. Carry: dismissed: already carried in the note (items N1 N4 N6 static-ceiling swap-limits)
