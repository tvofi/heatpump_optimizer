Fix review: merge 893787b084bdc088deeb43f0b2cb45f43898deaa

bus-nonce: e4c1c35f6ce241488b1657f3c4111b7b

## Round

This is the fourth fix review of #2711, the review of repair round 3. It returns `merge`, so the re-cut that `fix-review.md` makes owed from the fourth round does not arise.

## Findings

- The body's plant tally does not re-derive. "That is 50 plants" is wrong: the finder's harness at this head prints 55 plants, not counting clean, clean_again, `snapshot_attr` and the two null-control edges. "except four that read more" then lists five (three `dunder_*`, `computed_getattr`, `read_computed_getattr`). I re-derived every plant figure individually (`ev/harness_head.txt`), and none reads below 420, so no conclusion rests on the tally. Carry: dismissed: body prose count only, every plant re-derived individually at or above the clean 420
- The +1 step's attribution is narrower than what the arm prices. The commit message and the body credit it to "the three `_unsub_*` reads". The literal-name arm resolves the `setattr(self, name, None)` stores in the same loop as well. Dropping the `getattr` reads alone leaves the cut at 420 (`ev/literal_unroll.txt`), so the stores carry the same pair. The figure, 420, is unchanged either way. Carry: dismissed: wording of the attribution only, the 420 and the definition-change reading are both verified

## Evidence

- Head measured: `893787b084bdc088deeb43f0b2cb45f43898deaa` (`ev/HEAD.txt`). `git ls-remote` showed it still the head of `fix/r10-structure-alias` after CI concluded. The body names this head. The PR's base is `646dbaa65`. origin/main moved to `2636ce9e9` during the review, touching only delivery rows, a triage note, `tests/closures.json` and seat tooling. Nothing `seam_metrics` reads changed.
- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Merge: `git merge-tree --write-tree origin/main 893787b0` rc=0, tree `409412a80`. The `LEDGER-MERGE: resolved tests/closures.json` driver line is a set merge, not a conflict (`ev/merge-tree.txt`).
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden` are untouched (three-dot diff empty). The diff touches no claim file, so `env_drift.py --all` has nothing to compare.
- `tests/structure.py` at the head reads `seam_cut_total 420 <= 420` and `STRUCTURE RATCHET PASSED`, rc=0 (`ev/structure_head.txt`). The budget diff against main moves only `seam_cut_total` 710 -> 420 and `recorded_at`. That is a downward re-record against main, and `budget-raise-gate` concluded success.
- The ruling: the owner ruled 419, and the PR records 420. I re-derived the +1 as a definition change on the same tree, using my own ablation instrument (`ev/abl.py`, `ev/cut.py`; built by this seat, not the fixer's `$SCRATCH/abl/run.py`, which is out of tree). Reverse ablation from the head (`ev/ablate_chain.txt`, `ev/ablate_literal_and_computed.txt`):
  - head 420;
  - literal-name and computed-name arms off: 419;
  - plus the uncalled-reference charge off: 352;
  - plus round 2's co-argument spreading restored: 389;
  - at `b43ea541` the cut reads 367 (`ev/r2_clean.txt`).

  So the steps are +22 (367 -> 389), -37 (-> 352), +67 (-> 419) and +1 (-> 420), exactly as the body and commit `86d4dba1c` state.
- The +1 depends on the order in which the arms come off:
  - The literal arm alone off reads 436, not 419 (`ev/ablate_literal_arm.txt`), because the loop's `getattr(self, name)` then falls to the computed-name arm, priced as every stored attribute.
  - The computed arm alone off reads 420 (`ev/ablate_computed_only.txt`), because the real tree has no other computed read.
  - So the +1 is "both arms" against "neither", the order the body uses.
  - Spelling the three accesses as direct reads also reads 420 (`ev/literal_unroll.txt`). The arm prices the loop exactly as its direct spelling, so no tree change is hidden in the step.
- The 16 variants of the round-2 reviewer's instrument (`review/2711:evidence/variants.py`, copied as `ev/variants.py`): at the head, clean 420 and all 16 read 420 (`ev/variants_head.txt`). At the base, clean 710 and every variant 706 to 708 (`ev/variants_base.txt`). The round-2 `class-open` block, a getter handing out its backing object through an out-param, a callback, `type(self)`, a bound alias or a constant `getattr`, is closed at the live head. Every spelling now reads the clean figure.
- Opening the class further with 17 spellings of my own (`ev/variants2.py`, `ev/variants2_head.txt`): `operator.attrgetter`, `self.__getattribute__`, `object.__getattribute__`, `operator.methodcaller`, `self.m.__func__(self)`, `__class__.__dict__[...]`, a walrus, a starred display, `dict(...).values()`, `map`/comprehension `getattr`, a keyword-only out-param, `next()` of a generator, a contextvar, a class-attribute store and a closure cell. None reads below 420 (range 420 to 544).
- Null control: the finder's harness reads `clean_seam_cut_total=420` and `clean_again_seam_cut_total=420`. `edge_called` and `edge_referenced` read 422 each (+2, one pair counted in both seams' cuts). At the base they read 712 and 711 (`ev/harness_head.txt`, `ev/harness_base.txt`). 420 against 422 is confirmed.
- The finder's harness `dev/audit/harnesses/r10_structure_alias.py`, sha1 `cc3a57fc0ac7503db04f4ed18a8eb99b4df66b62` (matches the body; `ev/harness_sha1.txt`):
  - head: every plant at or above 420; `dunder_*` 433, `computed_getattr` 544, `read_computed_getattr` 523, `snapshot_attr` 423 (dispositioned, not below clean);
  - census: `units_returning_state=126`, `transparent_callees=77`, `units_returning_coordinator=1`, `cross_seam_calls_of_state_returners=68`, `units_leaving_state=18`, `units_raising_state=1`, `unresolved_unit_names=51`, `computed_names=1`. All match the body;
  - base (the harness copied in): every plant 706 to 709. I did not re-derive the 51 unresolved occurrences one by one.
- My own mutants, each run through the full `tests/structure.py` and then restored:
  - literal-name arm off (M22): rc=1, `FAIL a name only ever bound to literals reads exactly those attributes, no more` (`ev/mut_literal_arm_structure.txt`);
  - uncalled-reference charge off (M12): rc=1, three FAILs, the uncalled-handoff, parameter-not-self and nothing-handed-on families (`ev/mut_uncalled_structure.txt`);
  - round 2's co-argument spread restored (M18): rc=1, `FAIL the state root is the binding, not the name it is bound to` (`ev/mut_spread_structure.txt`).

  My first spread run was invalid, a race in my own script that ran an unmutated tree. It was re-run and the result above is the valid one. The body's other mutants (M1 to M23) were not re-run by this seat.
- Metric earned (step 14): the movement 710 -> 420 against main is a counting-rule change, and no production line changed. `archscore` reads `dS +0.0000 NULL` (body; the `arch-score` CI check passed). Each arm I removed moved the cut by its stated amount and in the stated direction, and no planted spelling reads cheaper than the direct reads. Under this rule the instrument now prices spellings at or above the direct form, so nothing found here is `metric-gamed`.
- CI on the head, read from the commit's check-runs API after every run concluded (`ev/check_runs.txt`, 53 runs): all success or skipped, including `gate` (120974907814, 20:09:20Z), `pr-contract` (120974909038, 20:05:11Z, after the last run to conclude), `tests / fast (3.14)`, `tests / closures`, `budget-raise-gate` and `tests / mutation`. No production line changed, so `tests / mutation` drew no mutant. No check went red on this head. The body answers the earlier `gate` red at `b43ea541` with the sweep detector, and that answer is present.
- Forward-carry: the body says n/a, since no later stage carries `seam_cut_total` or O19. Nothing found here changes a later stage.
