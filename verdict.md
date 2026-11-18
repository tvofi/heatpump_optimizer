Fix review: blocked bdf096245858f5a381b67719c4174d7a2880974d tests-red: tests/doc_claims.py fails at this head (2 of 411) and passes at the base; the added lower-bound start makes the optimizer run 5 starting points while how-it-works.md still states four

bus-nonce: 52ad522da9fdbc591c3200100caa48da

## Block

- The diff appends `_lower_bound_start(bounds)` to every space-only start set (`_space_only_starts`), so the start count `tests/doc_claims.py` measures moves from 4 to 5. The corpus was not updated. At this head the script reads `2 of 411 checks FAILED`:
  - `FAIL ...and the number it does state matches what the optimizer runs (anchor + D6-s2-04)  [doc states 'four', measured 5]`
  - `FAIL every starting-point count the corpus states is the count the optimizer runs (I5, measured 5)  [[('how-it-works.md', 4), ('how-it-works.md', 4)]]`
- At the base 9fe63d00b59f100aea67267ddddc95522e164aa1 the same script reads `ALL 411 checks PASSED` (ev/base-doc_claims.log). The failure is this diff's, not inherited from main.
- `doc_claims.py` is in the scoped gate CI ran (wall-clock list in `tests / fast (3.14)`), which reports `4 TEST SCRIPT(S) FAILED`, so the required `gate` is red. A head still red takes no merge verdict (C8).
- Repair: state the new count in both how-it-works.md sentences (or word them so they do not fix a number), then re-run `tests/doc_claims.py` (11 s). Mutation-proof the doc-claims anchor in the same pass.

## Red checks

- `tests / fast (3.14)` (owed-reds set): red, and the body's `## Red checks` does not name it. Note: root-cause-detectable: tests/doc_claims.py runs locally in about 11 s and is in this diff's measured closure, so a scoped prepr run before the handoff would have shown it.
- `tests / mutation` (owed-reds set): answered in the body (unpinned added-line sites, `prepr.sh` ci-predict named as the cheaper detector). `tests / mutation-autofix` is also red at this head, so the pins the body attributes to it have not landed. That lane is outside the owed-reds set.
- `gate` is the required aggregate of the above. `pr-contract / pr-contract` is red; review_packet reports both as not named in `## Red checks`. Neither is in the owed-reds set (ev/owed-reds.txt).

## Evidence

- Head reviewed: bdf096245858f5a381b67719c4174d7a2880974d (ev/HEAD.txt). `git ls-remote` of fix/r11-seam-solver re-read at verdict time: same head.
- Round: first (review packet scope: full, no reviewed head).
- `merge_train.py classify bdf096245858f5a381b67719c4174d7a2880974d --pr 3736`: `RED bdf096245858f5a381b67719c4174d7a2880974d pending: none red: gate`, rc=1, read twice (ev/classify.txt).
- `git merge-tree --write-tree origin/main bdf096245858f5a381b67719c4174d7a2880974d`: rc=0, no conflict (ev/merge-tree.txt).
- VERSION, manifest.json and RELEASE_NOTES.md: untouched in the three-dot diff.
- I ran the PR's features block (`features_block.py`, marker `# --- R11-SEAM-solver: the start set brackets`, prelude from `--emit-prelude`) at the head: rc=0 (ev/block-head.log).
- Mutant M2 (`_Horizon.money_prices` returns `self.prices`): block rc=1, killed (ev/block-mutant-M2.log). I did not re-run M1 and M3-M6 because the head is blocked on the red gate. They are owed on the next round.
- Local cheap scripts at the head (ev/local-quick.txt): structure.py, block_duty.py, manual_plan.py, guard_pins.py, plan_view.py, deployment_shape.py, layout.py and `env_drift.py --claims-only` at the base: all rc=0. doc_claims.py: rc=1.
- Not verified: CI reports 4 failing scripts in `tests / fast (3.14)`. This seat identified only doc_claims.py. The job log could not be grepped from this seat (blob download refused by the proxy, and `failure_logs.sh` needs `gh`). The other three are unnamed here and owed on the next round.
- Not re-derived: the harness figures in the body's `## Figures` (offstart, wood_seeds, m3_risk, slot_reason_hashseed) and the `start_below_band` kernel-class claim, which the body itself rests on an out-of-tree driver. The finder's harness is named only from the plan export; review_packet reports `Finder's harness: none named`.
