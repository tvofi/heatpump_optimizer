Fix review: blocked 1ea3a2429ff03b904dacddd1fe7bfcb6485618c2 ci-red: gate 128949537164 (edit run 42551664155) is a deferral no sweep re-judged, gate-sweep.yml is disabled_manually, so classify reads RED

bus-nonce: 417100b4bd29d4200b018d65ddb7fffc

Round: first fix review of #3348 at this head.

## Evidence

- Head measured: 1ea3a2429ff03b904dacddd1fe7bfcb6485618c2 (ev/HEAD.txt). Its tree a71823e5 equals b6c6a067's tree, the SHA the body measured (`git diff --quiet b6c6a067 1ea3a2429`), so every figure the body took at b6c6a067 applies to this head.
- Role contracts: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Merge: `git merge-tree --write-tree origin/main 1ea3a242` exits 0, and origin/main 6457496a is an ancestor of the head (ev/merge-tree.txt).
- Self-tests at the head (ev/selftests-head.txt): gate 81 checks, 0 failed; sweep 71 checks, 0 failed; prelude 76 checks, 0 failed; r10_codescan_wait_race --selftest 15 checks, 0 failed. Each matches the body.
- Sweep self-test counts re-derived per SHA (ev/sweep-counts.txt): daf8b349 52, 25811b2e 62, 6457496a 60, b6c6a067 71. Each matches the body's rule (52 + 10 + 8 + 1).
- Gate mutants: `r10_ci_gate_core.py mutants` reads `RESULT mutants=22 survivors=0`; M27 and M28 are KILLED by the named source-order cases (ev/gate-core-mutants.txt).
- RCA replay, the finder's harness for this group (ev/rca-replay-head.txt, ev/rca-replay-base-pin.txt):
  - at the head: `3244-triple: DECIDED`, `3252-nosource: DECIDED` PASS, `defects=no`.
  - at main 6457496a: `3252-nosource: MISREAD` (`FAIL pr-contract / pr-contract: failure (run 42387066581)`), `3244-triple: DECIDED`, `defects=yes`.
  - at the pin 9cbd7dd0: `3244-triple: DEADLOCK`, as recorded live.
- Own mutants (ev/reviewer-mutants.txt, driver $HOME/mut.py, which is mine and not the fixer's; it copies `tools/` out of tree, so prelude's C7a and gate's missing `.github/workflows/ci.yml` fail on every row from the copy's location, not from a mutant). Each mutant is read on its owning suite:
  - R1, the lagging-own-unit sentinel `"~"` changed to `""`: gate fails `source order null` (got PASS). KILLED.
  - R2, `run_jobs` not filling `starts`: gate fails `source order: a LOWER-id edit run's red arch-score ...` (got PASS). KILLED. This pins the prelude half of the change.
  - R3, the stale branch in `judge()` off: sweep has 8 failed. KILLED.
  - R4, the fresh-run guard off: sweep has 3 failed. KILLED.
  - R5, the 300-file cap clause dropped: sweep has 1 failed. KILLED.
  - R6, the event filter dropped: sweep has 1 failed. KILLED.
  - R7, the `.py` suffix test dropped: sweep has 1 failed. KILLED.
  - R8, the settle loop's `judge` called without `runs` (the body's C1): sweep has 1 failed. KILLED.
- Class rule (the body's grep, ev/class-rule.txt): at the merge base it returns 9 lines, including `gate.gate`'s `sorted(..., key=lambda r: r["id"], reverse=True)` at gate.py:196. At the head it returns 8. Every remaining line is dispositioned in the body's `## Figures` (busy x2, undecided x2, run and settle sort, prelude waits_on and defer_to). No seam is open.
- Ratchet: `tests/structure.py` reads STRUCTURE RATCHET PASSED; `archscore --diff 6457496a` reads `dS +0.0000 NULL` (ev/structure.txt, ev/archscore.txt).
- VERSION, the manifest, RELEASE_NOTES.md, both claim files and every `*_budgets.json` show no three-dot diff (ev/untouched.txt is empty), so claims are unchanged and no fixture drift is owed.
- Forward-carry: the body states `none`; no finding here changes a later stage.
- Red checks at this head:
  - `gate` 128951765188 (edit run, KIND edit) logs `FAIL run(s) [42551663943] at this head are still being judged; their gate decides`. It is a deferral to the code run, read under the pinned 6457496a programs.
  - `governance / delivery-status` 128948848462 is OVERDUE on #3318's row (main's batch), not this PR's row. The check prints that it is not a required context.
  - Neither owes this body a root-cause answer. The deferral is the gate's design; the body answers the earlier heads' deferrals in `## Red checks`.
- Figures I could not re-derive:
  - the 1821-run / 5-ORDERED / 3-narrowed codescan counts (carry 11's build threshold);
  - the `19 of 19 SAME` pin census;
  - the 73-mutant diff-mutant table.
  
  The first two rest on the fixer's scratch probes (probe10.sh, pincheck.sh), which are not in the tree; the third is a 15.8 s prepr step I did not re-run. None of them decides the verdict: the fix is pinned by the self-tests, the replay scenes and the mutants above.
- CI on this head:
  - `merge_train.py classify 1ea3a242 --pr 3348` read WAIT from 02:50Z to 04:27Z, then `RED ... pending: none red: gate` on every poll from 04:28:42Z to 04:52:30Z (ev/classify-log.txt). That is exit 1.
  - The three `gate` check runs at the head:
    - 128964286912 (code run 42551663943, started 04:00:07Z): success.
    - 128972978867 (edit run 42552152069, attempt 2, re-run by tvofi, started 04:23:31Z): success.
    - 128949537164 (edit run 42551664155, attempt 1, started 02:38:22Z): failure. Its log reads `FAIL run(s) [42551663943] at this head are still being judged; their gate decides`, under programs restored from 6457496a.
  - `latest_runs` keeps the worst of each suite's latest gate (A5), so that red stands behind the two greens.
  - Every non-gate unit of the code run is green, and `pr-contract / pr-contract` 128960506848 is success.
- Why that red was never re-judged: `gate-sweep.yml` (workflow 394687477) reads `state=disabled_manually`, updated 2026-11-08T11:54Z, and its last run is 42479944954 at 2026-11-08T12:22:30Z (ev/gate-sweep-state.txt, ev/edit-runs.txt). So no `settle` ran at this head.

## Block

- ci-red: classify exits 1 at this head. The only red is the deferral gate 128949537164 of edit run 42551664155, which nothing re-judged because `gate-sweep.yml` is disabled.
  - It is not a unit failure. The code it deferred to, run 42551663943, has a green gate (128964286912), and the sibling edit gate re-run by tvofi is green (128972978867).
  - One re-run of job 128949537164's gate, or re-enabling the sweep, should decide it. That is the orchestrator's action: this seat re-runs and approves nothing.
  - On the work itself every check I ran holds: mutants, replays, self-test counts, class rule, merge-tree, ratchet and untouched files (`## Evidence`). If that gate goes green with the head unchanged, this review's measurements stand for the patch at 1ea3a242. Carry: dismissed: this block is cleared by one re-judge of that gate at the unchanged head; the disabled sweep behind it is carried under ## Findings

## Findings

- `gate-sweep.yml` is `disabled_manually` (since 2026-11-08T11:54Z). Both this PR's stale-pin countermeasure (`sweep.py` `stale_pin`/`fresh`) and #3287's `settle` live in that workflow. The body's statements that the sweep re-judges deferrals with no human (carries 3, 8, 10) and that "the manual 5.3 dispatch is retired once this merges" (carry 6) hold only while it is enabled. At this head a deferral red stood until a human re-ran it, and the second one still stands. Carry: R10-HOTFIX-GATE-BUSY-DEFER
- The carry-11 counts (1821 runs, 5 ORDERED, 3 narrowed) and the null control's `19 of 19 SAME` pin census rest on the fixer's scratch probes `probe10.sh` and `pincheck.sh`, which are not in the tree (fix-review step 9 and fixer step 18), so I could not re-derive them. Carry: dismissed: the counts gate the decision to build, not the fix; the fix is pinned by in-tree self-tests, the recorded replay scenes and the mutants I re-ran

## Friction

- review-packet-required-red: cost: the packet refused on `required-red` at render, and CI then sat in WAIT for about 1.6 h behind a queued gate runner. Carry: dismissed: the wait is the brief's prescribed classify loop, and the cost is runner queueing, not a missing mechanism
