Fix review: blocked 9ef51b8215dd7216950f177386fb2f5a8f010a47 raise-unjustified: the raise justification rejects payment 1 as hiding growth, yet that payment is tighter than the band; it dismisses payment 2 by mistaking spread for headroom

bus-nonce: de774e283b26fc790fb40c74a9cd6ac6

This is round 3 of this fix review. The delta is in the body only, and the head has not moved. I measured head 9ef51b8215dd7216950f177386fb2f5a8f010a47 from a detached worktree at that SHA. Just before posting, `git ls-remote` shows that `fix/r10-hotfix-ci-critpath-2` still resolves to this head. The body is the one edited at 2026-10-31T21:37:16Z. origin/main has moved to f3c9144b8, and the merge base is still a7dd7f50d.

## Block

The round-2 block is repaired. The body now states `Architecture score: dS +0.0000 NULL` in `## Figures`, in `## Architecture score` and in `## Raise justification`. It withdraws the coord_footprint clause, and the figure reproduces (see Evidence).

The brief's item 3 asks for more. A raise justified as a null movement owes an honest statement of why no payment that improves the architecture exists (CLAUDE.md rule 2, decision 0013, fix-review step 14: "judge each payment the body lists"). Judged on the body's own figures, two of its three payment judgements do not hold:

- **Payment (1) is rejected on a false comparison.** The body rejects the re-record of critical_path_minutes 34.267 -> 35.317 because it "would hide the 1.2-min center growth inside the cap". The band it chose instead lets the graded 8-run median pass up to 34.267 + 1.3 = **35.567**. That is 0.25 min looser than the 35.317 it rejected, on the same statistic.
  - Under the band, the center stays flap-free up to 34.267, the budget itself. Under the re-record with no band, it stays flap-free only up to 35.317 - 1.3 = 34.017.
  - Viewed either way, the rejected payment is the tighter instrument, so "hides growth" cannot be the reason to prefer the band.
  - The owner's ruling ("increase the variance band") is a sufficient reason on its own. The body may rest on it, but it may not add a technical reason that inverts the comparison.
- **Payment (2) is dismissed by mistaking spread for headroom.** The body says "no reduction makes an 8-sample median ... stay within 0.5 min of its center, so that payment cannot fix a variance red". The 0.5 is headroom (budget - center = 34.267 - 33.767), not a property of the spread. Reducing the work moves the center down and widens the headroom. The body's own `Cause` paragraph says the red is "spread larger than the headroom", not spread alone.
  - On the body's figures, a critical-path reduction of 33.767 + 1.300 - 34.267 = **0.800 min** fits the worst measured |dev| under a zero band.
  - With the current window's own max |dev| 0.851, the reduction needed is **0.351 min**.
  - The body itself records 2.36 min of growth in `fast (3.14)` (29.47 -> 31.83) since the recording.
  - So a pay-down is not impossible in kind. The honest statement is that one was not found, or that its cost was judged against the red-main critical path, or that the owner ruled the band instead. The body says none of these.
- I hunted for a missed payment and did not find one I can demonstrate. My only access to CI timing is per job, and I have no `gh` to profile which lane work could be removed without loss. So this block does not claim a payment exists. It blocks on the justification's reasoning, which the mandated approval rests on.

The repair is to the body only and does not move the head:

- Restate (1) as rejected by the owner's ruling, and drop "would hide the center growth", or state that the band admits a 0.25-min higher graded median than (1) would.
- Restate (2) with the headroom arithmetic: a reduction of about 0.35 to 0.80 min on both critical lanes would clear the red at zero band. Then say why it was not taken: not found within hotfix scope, the owner's ruling, or both.
- Keep the `Architecture score: dS +0.0000 NULL` line.

A re-verdict needs only the edited body, the post-edit `pr-contract` and `budget-raise-gate` runs, and the approval at this head. Every other check below passes.

## Findings

- Instrument finding (rounds 1 and 2): budget_raise_gate checks the shape of the `Architecture score:` line, never its value against the arch-score job. The body now carries it. The carry is in group R10-FLY-MANDATE-REVOKE-GUARD's brief in dev/programme/rosters/wave-r10-groups.json, at roster SHA 697a0154f74b8873e681479a8e742eade69d06bf, which is an ancestor of origin/handoff/audit-r10-roster. It starts "From the #3045 round-1 fix review" and states its controls: "a planted false IMPROVES must read red, and the true figure must pass (null control)" (ev/carry.txt). Carry: R10-FLY-MANDATE-REVOKE-GUARD
- budget_raise_gate's MAX0 typing calls removing the band (1.3 -> absent) a raise. It fails closed. The body dismisses this with a reason, and that reason holds. Carry: dismissed: a fail-closed false positive that opens no gate weakness, and only the owner can decide that removal should be routine
- Instrument observation from the step-14 plant, a neighbouring rule and pre-existing at the merge base, not this diff's shape. A planted `archscore.unused_boundary_imports_band: 5` row passes `ci_ratchet.budget_problems` and is not a raise to `budget_raise_gate.file_raises`, because any `archscore.*` key reads as a new cap. It is inert: compare() treats it as an ungraded, underived metric and loosens nothing (ev/plant.txt). The same plant spelled `script_runs_per_push_band` or `critical_path_minutes_tolerance` is refused by the ratchet and typed a raise by the gate. Carry: dismissed: the planted row grants no tolerance (compare() applies a band only through BAND_KEYS), so no gate or grading weakness opens

## Evidence

- Round-2 points re-checked against the new body:
  - The metric-gamed block is answered. The body's three dS statements now read `+0.0000 NULL`, and the IMPROVES figure is withdrawn.
  - The instrument finding is answered by the forward-carry (above). Round 2 found no roster SHA. The body now names 697a0154f, and the carry is there.
  - The MAX0 point is answered as dismissed. The head code is unchanged (`(("critical_path_minutes_band",), MAX0)`).
  - The head code is byte-for-byte what round 2 measured, because the head is unmoved.
- archscore, re-taken with the body's command at the head (ev/archscore.txt):
  - `score.py --diff a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0 9ef51b8215dd7216950f177386fb2f5a8f010a47` gives `Architecture score: dS +0.0000 NULL`. This is the three-dot comparison, because a7dd7f50d is the merge base.
  - Against current origin/main f3c9144b8 it also gives `dS +0.0000 NULL`.
  - CI arch-score 124664943246 succeeded. The body's NULL is honest.
  - Step 14 removal: the diff writes no code archscore reads, so there is no movement to earn and none survives.
- Mutation proof at the head, `env -u BASH_ENV python3 -I <script> --self-test` summary lines (ev/mutants.txt; the mutants are mine, in ev/mut.py):
  - Baseline: `ci-ratchet self-test: 45 checks, 0 failed`; `budget_raise_gate self-test: 240 checks, 0 failed`.
  - M1, band ignored: 45 checks, 2 failed.
  - M2, band on every row: 1 failed.
  - M3, MAX for MAX0: 240 checks, 1 failed.
  - M3b, gate row deleted: 1 failed.
  - M4, bounds dropped: 1 failed.
  - M5, `>=`: 4 failed.
  - M6, record carry-over deleted from `record_table()`: 1 failed. This is the record_table() check.
  - M8, mine, the band `continue` dropped: 1 failed.
  - All killed. The worktree is clean after each.
- Null control (ev/null-control.txt), head budgets vs the same table without the band:
  - 34.467 and 35.567: ok with the band, GREW without.
  - 35.568 and 35.777: GREW both ways.
  - script_runs_per_push 55: GREW both ways.
  - archscore.unused_boundary_imports 1: GREW both ways.
  - compare() applies the band to critical_path_minutes only. The counters stay at zero tolerance. budget_problems(head) is [].
- budget_raise_gate treats a missing band as zero. CI 124664943224 prints `RAISE tests/ci_budgets.json: critical_path_minutes_band: None -> 1.3`.
- Band 1.3 was not re-derived this round. This seat has no `gh` for `--gather-runs` (GitHub CLI use is limited to search here). Round 1 re-derived it from the body's 86-run query (`max|dev|=1.300`). The band value, run_minutes and the inputs are unchanged since then. I rely on that measurement and do not re-certify it. The 0.800, 0.351 and 35.567 figures in the Block are arithmetic on the body's own stated figures. Their null control is the body's own 34.267 - 33.767 = 0.5 headroom, which the same arithmetic reproduces.
- CI at this head: `merge_train.py classify 9ef51b8215dd7216950f177386fb2f5a8f010a47` exited 1 at 2026-10-31T21:53:01Z with `RED ... pending: none red: gate` (ev/classify-log.txt).
  - gate 124665332374 names one failure: `FAIL budget-raise-gate / budget-raise-gate: failure (this run)`.
  - budget-raise-gate 124664943224: `REFUSED: tvofi's approval is on b02ffd170d50, not this head 9ef51b8215dd`. This red is EXPECTED until the approval at this head (P345). The body names it under `## Red checks` and says it is red by design. It is not a block.
  - The main-side `tests / ci-ratchet` red is named and answered there too.
  - pr-contract 124665193958 succeeded at 21:39Z, after budget-raise-gate concluded at 21:38Z. It prints `CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted`.
  - Every other check in the packet's digest is success or skipped (ev/review-packet.md).
- Merge: `git merge-tree --write-tree origin/main 9ef51b8215dd7216950f177386fb2f5a8f010a47` against f3c9144b8 gives tree b3f7b3cef at exit 0 (ev/merge-tree.txt).
- Claim files: tests/golden/claimed_drift.txt and card_claimed_drift.txt are byte-identical to both the merge base and origin/main. VERSION, the manifest and RELEASE_NOTES.md are untouched three-dot.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Scoped-gate MODE line: not read. That is CI's heavy run, and this seat does not re-run it.
- Roles: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Head line: the body's `## Head` names 9ef51b8215dd7216950f177386fb2f5a8f010a47, the head I measured.
- Harness: the body names no finder harness (this is a red-main hotfix). The mutants, the null-control snippet and the plant are mine (ev/mut.py, ev/null.py, ev/plant.txt).
