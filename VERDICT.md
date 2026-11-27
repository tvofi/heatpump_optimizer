Design review: revise f4c840caf05e739f89403eff425402fff8b41f5c

Class: architecture-unsound (V1), harness (V2), class-open (V3).

Group R11-OWNER-FEATURES-SPLIT, round 2. Note at design/r11-owner-features-split f4c840caf05e739f89403eff425402fff8b41f5c (revision 2 of the orphan design.md). Delta reviewed: git diff 7b9c5331fe f4c840caf0. Base re-read at origin/main ef797d794017c98f7fb2d8a168d7de63d435ef3b, the note's stated base. Worktrees: /tmp/hpo-dr2-features-split/{wt,base}. No full re-review.

Re-measured at the base and confirmed: `case_select.split` gives 252 spans; tests/case_closures.json holds 248 (recorded_at f184477ba8). The 4 unrecorded ids are the #3616 room lift, the #3862 override switch and the two R11-SEAM-learners spans. Needs edges total 10241. A union-find over all recorded needs gives one component of 248, which supports the note's case that joining collapses to one part. `case_select.run(script, plan=...)` and the `run <script> [--plan FILE]` CLI exist (tests/case_select.py:5, :362). `Recorder`, `_aliases` and `INPLACE` exist as the note cites them. Sibling ref design/R11-CI-CASE-SELECT is at 25fa1f763e, as stated.

Prior points:
- R1: resolved in direction. Sever, with the swap run as instrument, replaces join, and every edge is typed and placed. One defect remains in the refusal criterion (V1).
- R2: partly resolved. case_select SCRIPTS, the case_closures re-record, DRIVEN_BY_OTHERS and shards READERS are now listed correctly. The enumerator's own output is not covered (V3).
- R3: resolved. The manifest is committed, and --port/--classify keep existing assignments. Its T5 refusal inherits V1.
- R4: resolved in cost. The note gives per-part seconds, line reach, the sample-and-report gate, the shards and the regenerate rule. Rule 1's soundness is V2.
- D1: answered by the ruling (§0).

## Revise points

V1 (architecture-unsound) design.md §1 step C and §2. The gate is defined on edges, but P0 is defined on load-bearing edges. Step C says "--check refuses to write while one [cross-part T5 edge] remains" and that every cross-part T5 edge "is removed". The same section then says P0 "edits only those" whose swap-run lines differ, and that the 7199 crossing edges are "an upper bound". The Notes item static-ceiling adds that `np.sort(...)` registers as a mutation of `np`. Such an edge is never load-bearing and never removed, so `--check` can never pass at the base. The same holds for a recorded module-moved store key that a P0-seeded consumer still reads. §2 has the same problem: "A branch that adds a cross-part T5 edge is refused". Any new section that touches the stub store records a module-moved edge from up to 72 producers in other parts, so it would be refused even when it seeds its own store. Fix wanted: make the refusal in both --check and --port the swap run's difference set being empty. That is the whole split for --check, and the new sections against their manifest parts for --port. Print the edge list as advisory. State that non-load-bearing cross-part T5 edges remain by design. Carry: dismissed: revise point, owned by the designer's next note

V2 (harness) design.md §4 rule 1 and §5 "Pins and kills". Re-keying a single-reaching-part row "with no drive" assumes the monolith's kill came from a section in that part. A mutant on a line that only part X executes can be killed in the monolith by a section of part Y through cross-part state, such as a stub-store save, a patched attribute or an RNG draw. The split removes that path in two ways. P0 deliberately reseeds load-bearing consumers. Edges that carry no load at the baseline but do under the mutant stay unswapped in the parts. The row is then keyed `killed_by` to X with no evidence that X kills it. The listed perturbation (re-key to a part that does not reach the line) does not exercise this path. Fix wanted: choose one of two options.
(a) Drive rule-1 rows with `case_select run <X> --plan <reaching sections and their in-part needs>` and state the cost. 556 rows on one part each is small next to rule 2.
(b) Restrict no-drive to rows where no reaching section produces a cross-part T5 edge in the monolith, and drive the rest.
In either case, add a perturbation: a row the monolith kills only through a consumer in another part must come out not-killed. Carry: dismissed: revise point, owned by the designer's next note

V3 (class-open) design.md §3. The note's enumerator (`git grep -n 'features\.py' -- ':!dev/audit/rounds' ':!tests/mutation_ledger' ':!tests/features.py'`) prints 1151 lines in 199 files at the base. "--check refuses a hit in none of the three classes", but most hits fall in none of them:
- Instruments that open or run the script: tools/audit/seat/features_block.py:2/:156/:195 (default `path="tests/features.py"`) and tools/audit/seat/verify_eight.py:92 (`subprocess.run([PY, "tests/features.py"])`).
- The user command in tests/README.md:346, plus its cost table at :102-:118.
- Prose citations "tests/features.py pins ..." in 16 custom_components/heatpump_optimizer files. Examples are device_prefill.py:12, modbus_prefill.py:12, name_match.py:39/:176/:262 and optimizer.py:1526/:1673/:3663. Others are in tests/*.py comments, tools/coverage/coverage_tree.sh, .github/workflows/codeql.yml:48/:142/:150 and tests.yml:993.
- Historical records under dev/archive, dev/programme and dev/audit.
Fix wanted: add the missing classes with a disposition each. Retarget the instruments to a part, or to the manifest. Rewrite live citations to the owning part. Leave dated records unchanged and exclude them from the enumerator. State whether the custom_components comment edits are in this group, since they put production in the diff and the push to main then runs `full`. Carry: dismissed: revise point, owned by the designer's next note

## Notes for the fixer

N6 design.md §1 swap run. A section whose ok/FAIL lines are identical under the swap can still be weakened, for example a check that passes because it now reads an empty store. V2's drive is the instrument that catches this; the line diff is not. Carry: R11-OWNER-FEATURES-SPLIT (item N6)

N1, N4 and static-ceiling stay carried as the note states them. N2 and N3 are folded into §5 and §1 step A, and are confirmed. Carry: dismissed: already carried or resolved in the note (items N1 N2 N3 N4)
