Fix review: blocked 5021b50def0ab7b5769239209d929125767d3636 class-open: a bare getter spelt with a leading pass, tuple(...), a [:] copy, dict(...) or a trailing None still pays the O19 plant's -2

bus-nonce: 94358461ac5f70e4c4ef041e760e2159

Round: first review of #2711 by this seat. Head measured: 5021b50def0ab7b5769239209d929125767d3636 (re-read at return, unmoved). Roles diff merge-base...origin/main: empty (contract current).

## Block

O19's getter finding is "one edge in place of k reads pays 2(k-1) with nothing encapsulated". The fix closes it for one shape only: `state_getter_reads` is a spelling enumeration (docstring, root-alias assigns, one return of a read or a tuple/list/set/dict display of reads), the #1874 shape the body itself rejects for aliases. I replayed the finder's P3 plant (`_cop_state` in learning, `_scores_view` reading through it) on the real coordinator with the fixer's own replay functions and five equivalent getter spellings. Each moves nothing in the code and each still lowers `seam_cut_total` by 2 at the head (ev/variants_head.txt; ev/variants.py is my instrument, not the finder's):

- `return self._cop_baseline, self._cop_health_cusum` (the finder's plant): 313 (closed)
- `pass` then that return: 311
- `return tuple((self._cop_baseline, self._cop_health_cusum))`: 311
- `return (self._cop_baseline, self._cop_health_cusum)[:]`: 311
- `return dict(b=self._cop_baseline, c=self._cop_health_cusum)`: 311
- that tuple plus a trailing `None`: 311

Clean head is 313; at the merge base every variant is 708 against clean 710 (ev/variants_base.txt), so these are the same plant, not new behaviour. The body's design note ("a callee that returns a constructed value stays one call edge") covers `dict(...)` and `tuple(...)` by choice, but not a `pass` or a `[:]`, and in every case nothing is encapsulated: the caller still holds both raw state objects. So the null control holds for one spelling of the plant and fails for spellings of the same plant. Pricing a callee by what it hands back (whether the reads escape through the return value), rather than by the shape of its body, would close this without a list. That design is the fixer's to choose.

## Findings

- The getter see-through is a shape list. Five spellings of the O19 getter plant still pay -2 at the head (see Block). Carry: R10-STRUCTURE-ALIAS
- Disclosure (step 9): the committed harness `dev/audit/harnesses/r10_structure_alias.py` is the fixer's. It re-anchors the finder's plants (probe/rev-2620-654004be ev/plant_p2.diff, ev/plant_p3.diff) and the body says so. I checked against the finder's own P2 diff applied to the head with `patch` (offset 167): `seam_cut_total` stays 313, and only class_excess_loc / max_class_loc fail, by +1. The finder's P3 does not apply (`_cop_watch` is gone from main), as the body says. Carry: dismissed: disclosed in the body and checked against the finder's P2 diff

## Evidence

- RESULT head harness: clean_seam_cut_total=313, alias_seam_cut_total=313, getter_seam_cut_total=313, bare_getters=5, properties_read_cross_seam=3 (ev/harness_head.txt). Base fa4dad4a7 with the harness copied in: 710 / 708 / 708, census absent (ev/harness_base.txt). Matches the body.
- `PYTHONPATH=tests/hastub python3 tests/structure.py` at the head: STRUCTURE RATCHET PASSED, seam_cut_total 313 <= 313 (ev/structure_head.txt). Census output matches the body's dispositions (5 getters, 3 cross-seam properties).
- Mutation proof re-run, each one killed: M1 getters emptied, rc=1 getter check; M2 property branch off, rc=1 getter + property checks; M3 attribute cut zeroed, rc=1 three checks (ev/mut_M*.txt). My M9 (call cut back to edge occurrences) crashed with KeyError rather than giving a figure. That is a malformed mutant on my side, not evidence.
- Budget move 710 -> 313 is a downward re-record that a counting-rule change caused (distinct pairs). No budget is raised and the archscore does not read seam_cut_total (body; not re-run).
- VERSION, manifest and RELEASE_NOTES.md are untouched in merge-base...head. No golden or claim file is touched.
- `git merge-tree --write-tree origin/main 5021b50def0ab7b5769239209d929125767d3636`: rc=0, no conflicts (ev/HEAD.txt).
- CI on the head, from the check-runs API at review time: most workflows are still queued or in progress. Only hassfest, prelude and cancel-superseded concluded success. No red has concluded yet, so step 11 has nothing to answer.
- Forward-carry: the body says n/a. Not opened, because the verdict is blocked.
