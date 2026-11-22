Fix review: merge c4766c3270b938ad6810d78548e967f371003029

bus-nonce: dfc6dc400c5ec8ba87e1290b5512e229
pending-ci: gate

## Scope

Round after the merge verdict at e9ad13fa58e02965bb5eb772b19535c09c9523c6 (probe/rev-3734-b737a95d). review_carry.py e9ad13fa -> c4766c32 prints FRESH-REVIEW: fa5de93aa3 is not the automatic merge of its parents. So this round is the delta (fix-review.md step 12): the merge resolution in fa5de93aa3 and the commit c4766c3270. The production delta is one line, open_meteo.py:239, and this round widens to exactly that line.

## Evidence

- Merge resolution (ev/merge_resolution_remerge.diff): the only conflict is in wood_fuel.py's imports. Both sides are kept: main's drift.utc_instant joins the branch's utc_elapsed_seconds, and the branch's entry_config.EntryConfig is kept. Nothing else differs from the automatic merge.
- c4766c3270 changes the _parse_block floor from datetime.min.replace(tzinfo=timezone.utc) to utc_instant(datetime.min). drift.utc_instant returns value.replace(tzinfo=timezone.utc) for a naive value, so both give the same instant. open_meteo.py imports utc_instant from .drift and no longer imports timezone.
- Body control re-derived (ev/open_meteo_at_fa5de93aa3.log, ev/open_meteo_at_head.log). At fa5de93aa3, tests/open_meteo.py exits rc=1 with NameError: name 'timezone' is not defined. At the head it reads ALL OPEN-METEO CHECKS PASSED, rc=0.
- Mutants on the repaired line, check tests/open_meteo.py (ev/mutants_head.txt). All 4 are killed: the pre-repair spelling, the floor without + resolution, >= loosened to >, and a naive floor. After each, the file was restored, git diff was clean and the check passed again.
- tests/wood_advisor.py at the head reads ALL 28 wood-advisor checks PASSED.
- tests/entities.py naive_instant_zone: the rule at the head matches the .replace(tzinfo=timezone.utc) call shape, with owners ["drift.py::utc_instant"]. That agrees with the body's claim that the rule named the pre-repair site. I did not re-run entities.py myself; CI's gate runs it.
- merge-tree: git merge-tree --write-tree origin/main c4766c3270b938ad6810d78548e967f371003029 exits 0, with no conflict (ev/merge_tree.txt).
- Step 7: the PR body names c4766c3270b938ad6810d78548e967f371003029 as the head. Its figures are stated as e9ad13fa's, and the two-commit delta is described. Step 5: the delta touches no VERSION, manifest version or notes heading.
- CI at the head (ev/classify_polls.txt): merge_train.py classify polled from 00:02 to 00:29 UTC and printed WAIT every time ("pending: gate red: none"). Still in progress at the last read: tests / fast (3.14), tests / closures, tests / coverage, tests / mutation. governance / instrument-self-tests concluded success. The early gate failure (job 137028581061, 23:54Z) was an aggregate taken before those units concluded; classify reads it as pending, with no red.
- Owed reds: none at this head while classify reports no red. The earlier reds are answered in the body's ## Red checks, unchanged since the e9ad13fa round.
