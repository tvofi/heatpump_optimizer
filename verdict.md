Fix review: merge 5d093b09f4a1043f11f3d23123040481fa11fbfb

bus-nonce: b4844795302db6dc0794e3015c2d7134

Round 2, a delta review of the round-1 re-cut. Reviewed at head 5d093b09f4a1043f11f3d23123040481fa11fbfb. The merge base is c9cbe6b45. origin/main is now 8aee66b77, and its only new commits since the merge base are #2820's friction-census fix, which touches no role file. So `proposal-triage.md` and `fix-review.md` are read from main with no drift. The re-cut delta 9f76c0978..5d093b09f touches only `dev/programme/triage/s6-batch28.md` (+17/-16, ev/recut-delta.txt).

## Block items from the round-1 verdict

1. **P152-P157 ACCEPT on an unmeasured benefit: closed.** Each now reads `Verdict: DEFER. What would change the answer: ...` and names a concrete measurement, which `proposal-triage.md` accepts as a DEFER ("names what would change the answer"):
   - P152: verdict-to-merge time spent waiting on proof CI, from `train/s*/train.log`.
   - P153: recarries and proof reruns whose measured closure did not change, with their CI minutes.
   - P154: blocked verdicts of the stale-figure classes, by comment id.
   - P155: the design-level share of blocks, priced against one added review round.
   - P156: per-file SERIAL, `conflict onto` and invalidated-verdict counts from the train logs.
   - P157: one round of per-check catch data, owned by D13.

   The owner's acceptance now routes as an owner-sourced carry, not through a triage ACCEPT (preamble line 5). `roster_edit.ruling_verdict` reads P150-P157 as DEFER and P158 as None (ev/figures.txt). So `triage_refusal` would now refuse any carry that cites these rulings, which is the intended effect.
2. **P157's carry duplicates P144: closed.** P157 carries no carry text, and the preamble records that it is dropped ("P157's carry, which also restated P144's daemon, is dropped"). A search of the head file finds no carry sentence that mentions P144.
3. **P150 and P151 ACCEPT that routes nothing: closed.** Each reads `Verdict: DEFER -> owned by the carries named below (...)` and states its REJECT arm with the binding cost (P150: "a body tool has no source event to render a time from"; P151: "every rule is either vacuous or refuses correct bodies").

The body's `## Figures` now reads 8 DEFER, and `grep -oE '^Verdict: (ACCEPT|DEFER|REJECT)' ... | sort | uniq -c` at the head prints `8 Verdict: DEFER` (ev/figures.txt).

## Findings

- Preamble line 7 still reads "A roster op citing an ACCEPT below resolves only once this file is on the roster branch or origin/main". After the re-cut the file holds no ACCEPT, so the sentence is stale. It is harmless: `triage_refusal` refuses any citation of a DEFER whatever this line says. Carry: dismissed: the stale sentence is inert, and a re-cut only to delete it costs a review round for no change in behaviour
- The plan-opt figures still have no in-tree command. They are verdict-to-merge median 1.89 h (P152, which names `bin/cycle.py`, n=110), 920 s (P153), 14/14 (P154), windows B and C (P155) and 1.45 h to 2.35 h (P155). Each is now labelled out of tree and used only as motivation for the named measurement, not as the basis of a verdict, so no ruling turns on a figure I could not re-derive (fix-review.md step 8: not verified). Carry: dismissed: under DEFER these figures carry no verdict, and the measurement each DEFER names is the in-tree replacement

## Evidence

- Scope: the three-dot diff touches only `dev/programme/triage/s6-batch28.md` (+82) and `dev/programme/delivery/2828.md` (+1) (ev/diff.txt). `dev/programme/` is on `tests/closure.py`'s INERT list (line 274).
- `git merge-tree --write-tree origin/main 5d093b09f` exits 0 with tree 8a5155e1e, so there is no conflict (ev/figures.txt).
- No host or home path: a grep of the diff for home, temp and root prefixes prints nothing (ev/figures.txt).
- VERSION, the manifest and RELEASE_NOTES are untouched.
- Round-1 finding, P152's citation: closed. The citation is re-anchored to `merge_train.py:129-135`, which at c9cbe6b45 is the prove step: "Red drops the one entry whose files are in the closure of every script the red jobs name and proves the rest again". `:5435` (batch/<tag>-<n>) and `:1071` (`gh pr merge ... --match-head-commit`) re-derive (ev/citations.txt).
- Destinations, at origin/main and at handoff/audit-r10-roster 2b7fe35c6 (ev/roster.txt):
  - Open, so a DEFER may name them: R10-FLOW-JIDOKA (in-progress), R10-ORCH-ROSTER-SCHEMA, R10-ORCH-REVIEW-PACKET, R10-ROUND-PLAYBOOK and R10-FLOW-DESIGN-STAGES (each not-started), R10-ARCH-SHAPES (in-progress, PR 2819) and R10-ADVISOR-RESIDUE (not-started).
  - Done, as P157 states: R10-GATE-YIELD and R10-FLY-YIELD-GUARD.
- The cited carries resolve at both refs:
  - JIDOKA 11: P-Q, carry_audit in --body-check.
  - JIDOKA 16: P67 `--fill-red`.
  - JIDOKA 18: P78 ref_privacy.
  - ROSTER-SCHEMA 16: `is_open` and DONE_STAGES.
  - The P135 -> REVIEW-PACKET carry that P151 cites is on the roster branch (the "Refuse a reviewer dispatch on exact mechanical signals" carry), not yet on main.
- No ruling ACCEPTs, so no carry routes. No ruling duplicates another or an existing group:
  - P155 defers beside DESIGN-STAGES and does not duplicate it.
  - P156 cites P141 for its batch-27 re-cut relation, and P141 is present on origin/triage/s6-batch27 (#2827, not yet on main).
- The other code citations were re-derived in round 1 at c9cbe6b45, and the re-cut does not change them.
- CI at the head (ev/ci.txt):
  - `governance / delivery-status` is red. It grades main's record, and this diff adds only its own row, so the red is not this PR's (fix-review.md step 11). The body names it under `## Red checks` with a cheaper detector (`tests/delivery_status.py --check`, which is present on main).
  - Still running at read time: `governance / instrument-self-tests` (in_progress) and `tests / lane-proofs` (queued).
  - No `pr-contract` run yet. Every other lane is green or skipped.
- Steps 1-6 and 14 (mutation, harness, claims, class) do not apply: the diff is a ruling record with no code, fixture or budget. The null control (`ruling_verdict` on P158 returns None) re-runs.
- A ruling I would change: none.
