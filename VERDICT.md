Fix review: blocked 091fc3bf30c0d4e20d637c07dc0c99d8c53a6ee4 ci-red: merge_train classify reads RED, red gate (two deferred edit-run gates beside a green code-run gate)

bus-nonce: 0111a5ee74d534022fdb7847f9a5895e

## Block

`python3 tools/audit/seat/merge_train.py classify 091fc3bf30c0d4e20d637c07dc0c99d8c53a6ee4 --pr 3360` exited 1 (RED) at 05:58:50Z, and again at 06:00:22Z, 06:02:05Z and after 06:10Z: `RED 091fc3bf30c0d4e20d637c07dc0c99d8c53a6ee4 pending: none red: gate`. The brief counts exit 1 as RED, and `fix-review.md` step 12 says a red CI never carries, so this verdict cannot be `merge`.

What the red is. Run 42564424236 is the code run. Its `gate` job, 129004669021, concluded success at 05:54:46Z, and every unit of that run concluded success or skipped. The one exception is `governance / delivery-status`, which `NOT_GATING` excludes. The red comes from two other suites' `gate` jobs, both of which deferred: 128993021658 (run 42564632076) and 128991614023 (run 42564424310). Each failed at once with `FAIL run(s) [42564424236] at this head are still being judged; their gate decides`. `classify` reads the worst gate across suites, as the ruleset does, and no gate-sweep re-run of the deferred gates appeared in the 15 minutes after the green gate. Carry: dismissed: evidence, not a finding

The work itself does not cause this block. Every review step below found nothing else that would block. Once those two gates are re-run green, the head needs only its classify re-read. This head was measured at 091fc3bf30c0d4e20d637c07dc0c99d8c53a6ee4, and the head was unchanged when I wrote this (`git ls-remote`).

## Findings

- The `tests/stress.py` memory probe is bimodal at the PR's base too, not only at the head. The body says "Merge base, same command in a real worktree: 0 of 13". I ran `PYTHONPATH=tests/hastub python3 tests/stress.py --memory-probe '{"season":"shoulder","building":"heavy_old"}'` 5 times each in `git archive` copies. At base 19865e5a8 it read 5.29 MiB once and 3.46 or 3.47 MiB four times. At the head it read 5.3 MiB three times and 3.46 MiB twice (`ev/stress_probe.txt`). So the 5.3 MiB mode does not come from this diff's `payload.py` edit. That refutes the body's account, though it does not refute the code. CI's `tests / fast (3.14)` passed at this head. The flake belongs on main. Carry: dismissed: pre-existing on the base (1 of 5 at 19865e5a8), not this PR's change, and CI's stress run is green at this head; the orchestrator owns the stress-budget flake, which needs its own root-cause seat
- On ratchet payment (step 14): `max_class_loc` 7933 -> 7932 nets the coordinator's two added lines (`wood_heated`) against a 4-line to 1-line fold of `interval_h`. The fold is a formatting change, not a structural one. I judge it a sound simplification of a needlessly split expression, not a game. Removing the fold would leave the coordinator 2 lines over budget, so the payment is real. Carry: dismissed: the fold is a genuine simplification; a lower budget only tightens the ratchet

## Evidence

- Round: first fix review of this head.
- Roles currency: `git diff 19865e5a8...origin/main -- dev/governance/roles/` printed nothing.
- Merge: `git merge-tree --write-tree origin/main 091fc3bf3` gave rc 0, tree 179c4ffb0. Stderr read `LEDGER-MERGE: resolved dev/audit/config/bugclasses.json`, with no MERGE-CLAIM line and no conflict (`ev/merge_tree.txt`).
- Step 5: the three-dot diff leaves `VERSION`, `manifest.json` and `RELEASE_NOTES.md` untouched.
- Step 4: the diff leaves both claim files and `tests/golden/` untouched. `node tests/card_drift.mjs 19865e5a8` printed `card_drift: identical in all 45 states`, rc 0 (`ev/carddrift.log`). I did not run env_drift `--all`: the diff moves no solver code, and CI's lanes are green.
- Step 1, mutation proof: each mutant was run in a `git archive` copy of the head with `PYTHONPATH=tests/hastub python3 tests/features.py`. In an archive, the `#363 recorded_at` check fails on every run, so the null shows the baseline (`ev/mutant_*.txt`).
  - NULL: `1 of 4988 FEATURE CHECKS FAILED`, #363 only.
  - `applied_calibration` returns `max(1.0, measured)` instead of `wood_free`: 4 failed. Three wood-free checks went red: "publishes that calibration, not the floor's 1.0", "still corrected up", "flat price ... volume difference alone".
  - `below_meter_floor` returns `False`: 3 failed, "a booked reference under the meter floor ... says why" and "the meter floor's two bounds".
  - `heating()` drops its displacement and free-heat legs: 2 failed, "the pending snapshot carries wood_heated ..." (displacing and free-heat read False).
  - The coordinator sets `wood_heated` to None always: 2 failed, the same check, all legs None.
  - In the card, the table drops `${floor}`: `node tests/card.mjs` showed 1 failed, "a month under the meter floor states no saving and says why ..." (`ev/card_mut1.log`).
  - The card drops `${floorNote}`: the same check failed (`ev/card_mut2.log`).
  - At the head: `ALL CARD CHECKS PASSED`.
- Step 2: the finder's harness is `dev/audit/harnesses/r10_sav_wood_reference.py`, committed by R10-SAV-WOOD-HEAT, with arms extended by this PR. I ran the `wood-plant` arm at both ends, each from its own tree.
  - Base 19865e5a8: `RESULT wood_plant_error_m0.8: mean +0.00 %`, `m1.0: mean +0.00 %`, `m1.2: mean -1.95 % min -4.50 max +0.00 sd 1.47 over 9 fires`. The no-fire m 0.8 row was `calibration 1.0 error +25.00 %`.
  - Head: all three m read `mean +0.00 % ... sd 0.00 over 9 fires`, and the no-fire m 0.8 row read `calibration 0.8 (wood_free) error +0.00 %`.
  - These match the body's figures.
- Step 3, null control: at the head, `--no-wood-flag wood-plant` reproduces the base's lines and RESULTs exactly: +25.00 % at m 0.8, `-1.95 %` at m 1.2, with basis `wood_floor`. The flat pct values 7.588885569166417 and 7.593865152873221 are the same at both ends for m >= 1.0 (`ev/*woodplant.log`).
- `meter-floor` arm at the head:
  - All the closed-loop and wood-plant rows published, with the body's percentages: valve-flat 0.556, valve-vary 25.264, wood-unforeseen 39.802, wood-cold 0.467, wood-full 92.987, wood-fire 37.371, wood-stale 4.070, wood-coast 19.336.
  - Zeroed reference: withheld. With the check dropped: published.
  - Under `MIN_CALIBRATION_KWH`: published.
  - Immersion share: 0.5 False, 1.0 False, 1.5 True.
  - The run was stopped at my background time limit before share 2.0 and its `SOUND` line, so those two figures are not re-derived (`ev/head_meterfloor.log`).
- Step 6, class seams: `git grep -n "savings_sek\|savings_pct" custom_components/` returns ledger.py (5), notifier.py (2), payload.py (3), sensor.py (1) and the card (9). Those are the five places the body names. `sensor.py` reads the row's `savings_sek`, which is None when withheld. No seam is left open.
- Step 7: the body's `## Head` names 091fc3bf30c0d4e20d637c07dc0c99d8c53a6ee4, the head I measured.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out`, which includes `RUN tests/stress.py`. That matches the body.
- `python3 tools/audit/fold_ledger.py check`: `50 classes ... 0 violation(s)`.
- Structure budgets: only decreases (`class_excess_loc` 17558 -> 17555, `duplication_copies` 10 -> 9, `max_class_loc` 7933 -> 7932). No `*_budgets.json` raises anything.
- Step 10, forward-carry: the body's two `## Forward-carry` items are both `dismissed:`, with reasons, and the packet's carry_audit reads `2 routed, 0 unrouted`. Carry 0's 2026-11 ratio cannot be re-derived: the owner's export is on no ref. I accept that dismissal.
- Step 11, red checks:
  - The body answers `tests / mutation`, `tests / mutation-autofix` (earlier heads), `tests/typing_ruler.py` and `tests/stress.py`. Each answer names a cheaper detector, or says none could be named.
  - At this head, `tests / mutation` concluded success, and `pr-contract` (129004482294, 05:53:34Z) concluded success after the last red. I treat that run as the evidence.
  - `governance / delivery-status` is red, but it is `NOT_GATING`, and the diff only adds its own row `dev/programme/delivery/3360.md`. So it is not this PR's red.
- Heavy CI lanes cited, not re-run: `tests / fast (3.14)`, `tests / closures`, `tests / coverage`, `tests / replay`, `tests / browser`, `tests / typing`, `tests / mutation` and `codeql` all concluded success at this head.
- Figure I did not re-derive: the body's "Merge base ... 0 of 13" stress count. My own runs contradict it (see Findings).
