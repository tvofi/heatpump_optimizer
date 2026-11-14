Fix review: blocked d712c2ba4a834afcb5d722468676d52ce3762681 ci-red: classify RED at the head, gate red; tests / fast (3.14) red on a features.py check main's own tree fails too

bus-nonce: b1a3df8bf73f585759b44a139c970262

Round 2 of the review (a delta review over the reviewed head 7c7f06081827bbf9c52da7b2345b3a5a81048649). Measured head d712c2ba4a834afcb5d722468676d52ce3762681. At 01:12Z it was still `refs/pull/3481/head`, and the body's `## Head` names it.

## Block

`python3 tools/audit/seat/merge_train.py classify d712c2ba4a834afcb5d722468676d52ce3762681 --pr 3481` printed WAIT from 00:56Z. At 01:23Z it changed to `RED d712c2ba4a834afcb5d722468676d52ce3762681 pending: none red: gate`, rc 1 (ev/classify.log). A red CI never carries a merge (fix-review.md step 12), so this verdict is a block. The code review found no defect.

The cause of the red, as far as this seat can read it:
- `tests / fast (3.14)` (job 132260951585, run 43534335461) concluded failure with `1 TEST SCRIPT(S) FAILED`. That check is in the `owed-reds` set. The job log the GitHub API returns is truncated to its last ~26 kB, so the failing script's name is not visible.
- On this container, tests/features.py at the head fails one real check: "a charge-start dip that recovers is learned as neither a draw nor usage, and a draw that does not recover keeps what main booked". It fails both in-tree (ev/features_intree_head.txt) and on a `git archive` copy (ev/features_ctl.txt).
- The same check fails the same way on a `git archive` copy of origin/main 50373173d (ev/features_main.txt). It came to main at 8fa60a926d, and this diff does not touch it (`git diff origin/main...d712c2ba -- tests/features.py | grep -c "charge-start dip"` prints 0).
- So the most likely red is main's, inherited through the merge, and not this branch's. That is not confirmed against CI's own log.
- `tests / mutation` (job 132259821824) also concluded failure. Its readable log tail shows only the shard setup (`count=2`), so the cause is unreadable here. `tests / mutation-pins (1)` was still in progress at 01:12Z.

Any one of these settles it:
- main's check is repaired and main is merged in again;
- the orchestrator confirms the fast red is main's and re-runs the lane;
- the gate goes green at this head.

A re-dispatch at an unchanged head needs only the live checks re-read. Every code finding below holds at d712c2ba.

## Findings

- main's tests/features.py check "a charge-start dip that recovers is learned as neither a draw nor usage, and a draw that does not recover keeps what main booked" fails at origin/main 50373173d on this container (3 of 5571 red on a `git archive` copy; the other two reds are copy artifacts, the #363 `recorded_at` and `_bootstrap` checks, which fail on every copy). It also fails in-tree at this head. Control to carry: run `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/features.py` at origin/main and read that title's line. A repair is shown red before it and green after. Whether CI's fast lane at this head fails on this check is not confirmed: the API log is truncated. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- Setup: `cloud-setup.sh --check` printed OK. Role pack rendered. `git diff merge-base...origin/main -- dev/governance/roles/` is empty.
- Each prior finding:
  - The block (own-group carries 128b800e and c33b6f10) is resolved. The four design items are measured in this PR by dev/audit/harnesses/r10_advisor_steady_seams.py. weekday-day is fixed; pair-other-asks, measured-fields and pv-price are disclosed in docs/dashboard-card.md. The body's carries now read 5 to R11-INTAKE-R10-RESIDUE and 1 dismissed, and none names this group. `carry_audit.py check --body` gives 5 routed, 0 unrouted, 0 bad.
  - The stale `## Head` finding is resolved: the body now states that main is merged in.
- Delta, isolated from the main merges. `git merge-tree --write-tree origin/main 7c7f0608` builds the reviewed head on today's main. Its one conflict is optimizer.py, `_held_reference` beside main's `_held_unreachable`, and the head keeps both and changes nothing else in that hunk. Diffing that tree against d712c2ba's leaves 60 files. The production part is:
  - `reference_day`: the week loop.
  - `price_tiles.take`: the `Rotation` dataclass and the 6-hour steady clock.
  - the coordinator's None-spec return.
  - `whatif.state_for` as `setdefault`.
- The production review found no defect.
  - `reference_day` now calls `_build_comfort_bounds` with no margins or floors. The function's `[0]` return (comfort_targets) reads neither, so this changes nothing.
  - The only caller of `reference_day` is `whatif.schedule_days` (whatif.py:188), which compares setpoint lists element by element, so the week-length list is consistent there.
  - The cap tile's six-hour clock and the restart cost of up to six hours with no cap refresh are disclosed in the body and docs.
  - Nothing outside this was widened.
- Merge with main: `git merge-tree --write-tree origin/main d712c2ba` exits 0 (ev/merge_tree.txt).
- Step 5: `VERSION`, the manifest, `RELEASE_NOTES.md` and tests/golden/ are untouched (three-dot diff empty).
- Step 14: `python3 tests/structure.py` printed STRUCTURE RATCHET PASSED (ev/structure.log). CI `arch-score / arch-score` and `budget-raise-gate` are success at this head.
- Step 1, mutation proof: tests/features.py whole, on `git archive` copies of the head. The control (no edit) has 3 reds: the copy's #363 `recorded_at` check, `_bootstrap`, and main's charge-start-dip check. Each mutant's extra reds over the control:
  - RESULT w1, the day offset dropped from `reference_day`'s step clock (seven copies of the asked day): +2, "#2257: with weekend temperatures the day energy is the week's average day ..." and "#2257: a weekend ask moves a setpoint on every weekday it is asked on ...".
  - RESULT w2, `reference_day` pricing the first day only (`range(1)`, divided by 1): +5, including "#2257: reference_day's setpoints open with ... a week of days", "a horizon under a day prices no day" and the two weekday checks.
  - RESULT t1, `take` not moving the stamp on a taken turn: +1, "#2257: the cap tile's steady pair is off the per-solve path ...".
  - RESULT t2, the first cap turn taken at once (stamp set 7 h back): +2, "a tile rotation: each degree tile is one solve ..." and the #2257 off-path check.
  - No survivor.
- Step 2 and the body's figures, re-derived with `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_steady_seams.py weekday fields` at the head (ev/seams_head_weekday_fields.log):
  - RESULT weekday with weekend comfort: 0 asks move with the weekday, 0 leave the schedule branch.
  - RESULT weekday null: 0 and 0.
  - RESULT weekday Friday sweep: 96 rows, 0 against the ask, 0 rounding to 0.00, 0 reading the pair.
  - RESULT fields, single-zone: holds 21.00, 0 against the ask.
  - RESULT fields, two-zone: holds 21.33, buffer moves 0.15 and 0.22.
  - RESULT fields, valve one tank: holds 19.88, 24 of 72 at 0 or against the ask.
  - RESULT fields, two-zone valve two-tank: holds 21.01, 0 against the ask.
  - Every null (same start) reads 0.00.
  - All of these match the body.
- The body's "before" figure (8 asks move with the weekday, 12 leave the branch) came from d120504a7, where this harness does not exist, so I did not re-derive it at that commit. I re-ran it on mutant w2, the head with `reference_day` restricted to the first day (ev/seams_mutant_firstday_weekday.log): 8 and 12, and the Friday sweep with 18 rounding to 0.00 and 6 reading the pair. That matches the body's before figures.
- Not re-run: the `pair` and `pv` arms, the bracket and carrier harnesses (unchanged since round 1's review, which re-ran them), tests/replay.py (CI `tests / replay` is success at this head) and card.mjs (CI fast lane).
- Step 11: `merge_train.py owed-reds` prints `tests / coverage-ratchet`, `tests / fast (3.14)`, `tests / mutation`, `tests / typing`, `validate / validate-hacs`.
  - At this head `tests / fast (3.14)` and `tests / mutation` are red. The body's Red checks section answers earlier runs of both, not these runs.
  - I make no root-cause-* call: not all of the head's workflows had concluded when I read them (`tests / mutation-pins (1)` was in progress), and the fast red reads as main's.
  - `tests / typing`, `validate / validate-hacs` and `tests / coverage-ratchet` are success.
