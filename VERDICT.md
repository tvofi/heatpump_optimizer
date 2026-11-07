Fix review: blocked a46e4d02fac4a26fa7f8713a47e73a7b8faac657 ci-red: tests/mutation refused 14 added unpinned sites and code run 42329898240 was cancelled before mutation-autofix pinned them

bus-nonce: 553fbbdd378cf456630501eaa3539218

Round: first round (fix-review.md "say which round"). I measured head a46e4d02fac4a26fa7f8713a47e73a7b8faac657 from a detached worktree. The merge base is f2a015142714383722bf49d7ab20d8398ec9674c, which is origin/main's tip, 0 commits behind. The head was unchanged when I checked at 03:41Z. The role file is current (`git diff <mb>...origin/main -- dev/governance/roles/` is empty).

## Block

- At this head, CI is RED and nothing is left running that could turn it green. `merge_train.py classify a46e4d02... --pr 3273` returns `RED a46e4d02fac4a26fa7f8713a47e73a7b8faac657 pending: none red: gate` with rc=1 (ev/classify_final.txt, ev/classify_poll_log.txt).
  - `tests / mutation` (job 128275557673, code run 42329898240) concluded failure: `MUTATION TABLE REFUSED -- 2941 unpinned site(s) against 2939 at the ratchet base f2a01514..., 14 of them added by this diff` (ev/ci_mutation_job.log, ev/ci_mutation_added_unpinned.txt). The 14 sites are exactly the 14 non-triaged entries in the body's `## Unpinned sites`, so the red was predicted and is `mutation-autofix`'s to repair (ci-autofix.md).
  - That repair never ran. `tests / mutation-pins (3)` (128275889219) was cancelled at 03:41Z in the step "Measure pins for the sites this diff added unpinned", about an hour after it started, which looks like a job timeout. Because of that, `tests / mutation-autofix` (128290222524) and the code run's `gate` (128290222579) concluded **cancelled**. The whole run 42329898240 is `completed cancelled`. Shards (1) and (2) succeeded.
  - The edit run's `gate` (128275301443, run 42329898001) failed on a pure deferral: `FAIL run(s) [42329898240] at this head are still being judged; their gate decides`. That is the open R10-HOTFIX-GATE-BUSY-DEFER. The deciding run is 42329898240. I waited for it as the brief directs, and it ended cancelled with no gate verdict, so the deferral never resolved.
  - A red CI never carries (fix-review.md step 12). What is owed: a re-run of the code run so that the pins land, through the bot's commit. Everything in `## Evidence` below holds at this head, so the next review can be confined to the bot's ledger-only delta (`review_carry.py`).

## Findings

- Body `## Red checks` / `## Head` are stale against the head's concluded checks (step 11; brief item 5). The body says "No CI has run on this head yet" and names `mutation` only as eight STALE PIN reds, already repaired. The actual concluded reds are three:
  - the `tests / mutation` refusal of 14 ADDED UNPINNED sites (a ratchet refusal, not stale pins);
  - the edit-run `gate` deferral (R10-HOTFIX-GATE-BUSY-DEFER, decided by 42329898240);
  - the code run's cancellation (mutation-pins (3), mutation-autofix and gate all cancelled).

  None of these three is named. Harness: the head's check-runs API, all pages, 55 runs (ev/check_runs_final.txt). Metric: the count of concluded red or cancelled gate-relevant runs the body leaves unnamed, which is 3. Perturbation: the body's own claim of zero CI. `pr-contract` is `skipped` at this head, so no contract run has yet judged the body after the last red. Carry: R10-CLONE-2238

- Surviving mutant at the P8 owner's clamp: `_window_partition` with `max(1, ...)` dropped (`per_window = int(round(window_minutes / max(dt_hours * 60.0, 1e-6)))`, tariff.py:545).
  - It survives `tests/dst_checks.py`, `tests/entities.py` and `tests/features.py` (ev/mutants_scored.txt O-P8-clampdrop, ev/tail_log_O-P8-clampdrop_*).
  - At the base this mutant was triaged `equivalent` (`survivor_triage/tariff.py/_window_means_batch.CLAMP_DROP.80efca0b.json`): there the modulo ran after the `per_window <= 1` return, so a zero partition fell through harmlessly. The diff correctly deletes that triage, because in the owner `int(offset_steps) % per_window` now runs **before** the return. The mutant is therefore no longer equivalent. Direct probe: with the clamp dropped, `metering_windows(np.arange(4.), 15, 1.0, 0)` raises `ZeroDivisionError`, while the unmutated owner returns the series unwindowed. A 15-min window on a 1-h step is a configuration production can reach.
  - No killer and no new triage was recorded. CI's table lists no `tariff.py:545 CLAMP_DROP` among the added unpinned sites, so the ledger does not see it either.
  - Harness: my mutant driver (ev/run2.py, ev/mutants_spec.py) run in a git worktree at the head. Metric: new FAIL lines beyond the head's unmutated baseline, which is 0. Perturbation: the sibling owner mutants O-P8-nohead and O-P8-floor are each killed (2 new FAILs), so the harness does move.
  - Owed: a check that drives a window shorter than half a step through `metering_windows` and `_window_means_batch`. Also owed: an instrument note on why the table does not enumerate the moved clamp. Carry: R10-CLONE-2238

- Surviving mutant at the P5 owner: `_n_peak_windows` with `offset_steps` replaced by `0` (optimizer.py, the `metering_windows(np.zeros(n_steps), self.config.peak_window_minutes, dt, offset_steps)` line).
  - It survives all three scripts (ev/mutants_scored.txt O-P5-off0).
  - It is not equivalent. A 60-min window on 15-min steps spans 24 windows at offset 0 and 25 at offset 1–3, so ignoring the offset sizes both the factors and `window_days` one window short of the plan's real windows.
  - The P5 sentinel check pins that both callers route through the owner. Nothing pins the owner's own count against a non-zero offset.
  - The gap predates this PR: the base's two inline copies carried the same unpinned argument. It now sits on the one owner the PR made.
  - Harness, metric and perturbation are the same as above. The sibling caller mutants C-P5-factors and C-P5-days are killed. Carry: R10-CLONE-2238

## Evidence

- Enumerator (the finder's harness, `dev/audit/rounds/round10/D14/sweep-P2/enumerate_p2.py`, sha1 9a02577e652d525e1ed23a301d9bf49ba192f5e3 at both ends): I ran my own copy on `git archive` exports of the merge base and the head (ev/enum_base.json, ev/enum_head.json, ev/enum_compare.txt).
  - RESULT F5_clone base=24 head=15 left=9 entered=0. The nine pairs that LEFT are exactly P1–P9.
  - Null control: the other 15 F5 classes are unchanged up to line numbers. F1=9, F2=8, F3=2, F4=0, F6=2 and F7=1 are equal at both ends.
  - `--fixture` reads `fixture.total=0` at base and at head.
- Before/after on unchanged behaviour (my own instrument, ev/before_after_tariff_dump.py): base and head tariff modules were driven over windows 15/30/45/60/90 min, dt 0.25/1/12/0.5/1 h, offsets 0/1/3/7, plan lengths 0–96, Stockholm and naive starts including both 2026 DST days and a fold=1 start, factor lists short/exact/long, and three thresholds. The functions driven were `metering_windows`, `_window_means_batch`, `window_factors`, `plan_window_days`, `peak_cost`, `peak_cost_batch` and `PeakTracker.from_dict`.
  - RESULT tariff_outputs_compared=72363, RESULT tariff_outputs_differing=0 (repr-equal).
  - Perturbation (ev/before_after_perturb.txt): owner mutants O-P4-zeros, O-P9-wall, O-P8-nohead and O-P7-days move it by 5708, 6062, 18649 and 29 outputs.
  - The coordinator, optimizer and sensor owners I checked by an adversarial read of the three-dot diff. Each owner is the old copy's expression moved verbatim. P2 keeps both log messages, with only the noun substituted. P6 calls `_data()` once instead of two or three times, which is the same read.
  - P2's owner now refuses a NaN residual (`not abs(nan) <= 1.0`), where the old `abs(nan) > 1.0` accepted one. Both callers return on `not np.isfinite(residual)` first (house learner before the vent CUSUM, lower-floor learner just above), so the difference cannot be reached.
- Caller mutants (each restores ONE caller's inline copy from the base, 22 in all, ev/mutants_scored.txt): all 22 are KILLED, and each is turned red by its own pair's named check (expected_check_red=True). P6's three are also caught by the P2 registry entry `evidence_attributes`.
  - The scoring counts FAIL lines beyond the head's own unmutated baseline in the same environment. The baseline has 8 environmental dst_checks FAILs, which the merge base fails identically, and 1 git-dependent features FAIL.
  - P6 and the entities scoring ran in a git worktree. In a plain export, entities.py stops at a `git diff` call before the P6 block, and I discarded those export runs.
- Owner mutants (core lines of each new owner, 19 in all): 16 KILLED, 2 SURVIVED (listed under Findings) and 1 not concluded.
  - Killed: O-P1-swap, O-P2-lt (the bound check), O-P2-never, O-P2-noabs, O-P3-nogate, O-P3-nopresence, O-P4-zeros, O-P4-ignore, O-P4-axis0, O-P6-nowait, O-P6-noreport, O-P7-days, O-P8-nohead, O-P8-floor, O-P9-wall and O-P9-noconv.
  - O-P7-peaks had not concluded when this verdict was written, so it is not counted here.
- Unmutated head in my environment: features `1 of 4883 FEATURE CHECKS FAILED` (the git-dependent `recorded_at` check; the body's 4883 count matches); entities `ALL 2650 ENTITY CHECKS PASSED` in a git worktree (matches); dst_checks 137 checks with the same 8 environmental FAILs the merge base shows at 134 checks (the body's 137 matches).
- Structure (ev/structure_base.txt, ev/structure_head.txt): class_excess_loc 17585→17561, duplication_copies 14→10, max_class_loc 7955→7934. These match the body. `tests/structure_budgets.json` only lowers those three rows, plus `recorded_at`. There is no raise.
- Architecture score (ev/archscore_diff.txt): `Architecture score: dS +4.7870 IMPROVES`, duplication_copies 28→19, coord_footprint 2491→2489, shape_copies 42→40. This matches the body.
- Probes (ev/probes_*.txt): head `probes_failed=0 probes_total=6`, `--perturb` `probes_failed=4`. The base stops with `LookupError: ('freq_control.py', 'evidence_exhausted', 'target_kw <=')`. All three match the body.
- Merge (ev/invariants.txt): `git merge-tree --write-tree origin/main HEAD` gives rc=0 with tree 8df66266. VERSION, manifest.json, RELEASE_NOTES.md, `tests/golden/` and both claim files are untouched in the three-dot diff. Two files are new: `dev/programme/delivery/3273.md` (the delivery row) and `tests/mutation_ledger/survivor_triage/tariff.py/billed_windows.CMP_BOUND.0a51dd45.json`. That triage's equivalence argument holds: at equal sizes `<=` concatenates `np.ones(0)`.
- Scope against the design note: all nine pairs are present, each with its owner, its callers and a sentinel check that drives every caller. The disclosed departures are:
  - P6's third caller, `FrequencyAdvisorSensor`, which the body's P2 registry returned. It is the same fact, so that is in scope.
  - P8's owner drops the unused `n`.
  - Extra follow-up commits beyond the nine-commit shape.

  P4 slices before it pads on `shape[-1]`, as the note directs. `_peak_window_factors` keeps its signature.
- Figures I could not re-derive: the body's per-commit F5 series (24→23→…→15) and its failing-test-first runs at the intermediate commits I did not re-run. I re-took only the two ends, the caller and owner mutants at the head, and the figures above. The golden drift-mode figures and the scoped-gate counts (27 scripts) come from the fixer's run at fdb98e24. CI's code-run gate never concluded, so CI has not confirmed them either.
- Design carries: golden-check rests on the body's drift-mode run and is unconfirmed by CI, for the reason above. bugclasses-json is left untouched with a stated reason, which the design verdict accepted. probe-reextract is confirmed (6/6 PASS, 4 FAIL perturbed).

## Friction

- The brief asks for `handoff-wip` pushes at milestones. The dispatch says to push nothing but the return ref, so I pushed only `probe/rev-3273-553fbbdd`.
- `tests/entities.py` cannot be scored in a `git archive` export, because it dies on a `git diff` call before most checks. A mutation seat must use a git worktree.
