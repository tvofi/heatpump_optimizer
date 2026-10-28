Fix review: blocked b0cab1fca854eb81f9ae4a9e8b21a2e752bc69ec head-moved: measured b0cab1fca854eb81f9ae4a9e8b21a2e752bc69ec, head is 5a8b029f55ea7cc893f115cbb49737ba8c9d4931

bus-nonce: 6de9d65a87b71effdf8de8f6f563485d

Round 3 review (the r3 return) of #2775, R10-LEARNER-ETA, measured at b0cab1fca854eb81f9ae4a9e8b21a2e752bc69ec from a detached worktree. `dev/governance/roles/` is the same on the merge base and on origin/main.

## Block

While this review ran, the PR head moved from b0cab1fca to 5a8b029f5. That commit is github-actions[bot] `ci: merge main`, merging main 5c0ee1093, which includes #2711 R10-STRUCTURE-ALIAS. Under fix-review.md step 12 this is `head-moved`. The move is not a clean carry under orchestrator.md section 11: it rewrites `tests/structure_budgets.json` and `tests/closures.json`, and both are in this branch's own diff. So it comes back as a resolution delta, and the delta is wrong:

- The LEDGER-MERGE driver resolved `seam_cut_total` as "710 + both deltas = 417". The bot's commit holds 417. But #2711 changed what the metric counts (710 -> 367 -> 420), and this branch's -3 was measured under the old rule. Run at 5a8b029f5, `python3 tests/structure.py` prints `seam_cut_total = 420` and `FAIL seam_cut_total 420 > 417 (+3)` (`ev/structure_new_head.txt`). Under the new rule the branch's single ring read saves nothing. The new head therefore fails the structure ratchet. CI at that head had not concluded when this verdict was written.

Everything measured at b0cab1fca stands, as Evidence shows, and would have returned `merge`. Re-measuring is offered, not owed. After the delta is fixed, only it needs judging: the budget file and the body's `seam_cut_total 710 -> 707` figure.

## Findings

- At 5a8b029f5, `tests/structure_budgets.json` says `seam_cut_total: 417`, but the tree measures 420, so `structure.py` fails. Fix: take main's 420 and `recorded_at`. That gives up the branch's -3, which does not exist under #2711's definition. Also correct the body's "re-recorded 710 -> 707" line, which the new rule makes stale. Carry: R10-LEARNER-ETA
- Instrument: `tools/merge/ledger_merge.py` adds both sides' deltas to a ratchet metric even when one side re-recorded it under a changed definition, and writes a budget the merged tree does not meet. `merge_main_bot.py` then pushed it without running `structure.py`. Any open branch that lowered `seam_cut_total` before #2711 will hit the same thing. Carry: #2711
- With a two-zone model and a lower-floor sensor, the `lower` learner reads `phase: settling, progress: 0.0` at zero samples. It has no count gate, but the module docstring says settling means "past every gate, the value is measurement", which is not true at zero samples. `progress 0.0` does state that there is no evidence, and the body never says lower counts. Carry: dismissed: the tree has no lower count gate to count toward, and progress 0.0 is truthful; a docstring nuance only

## Evidence

- Mutation proof (step 1). I ran `tests/features.py` on the named mutants, one detached worktree each at the head. Every named check went red (`ev/features_mutant_*.txt`). I killed each run once the R10 block had reported; the full run was not needed.
  - M1 (`needed > n` dropped): `no settling learner carries a day count...`, `settling progress...`, `off when disabled...` and `the ΔT and irradiance edges...` all FAIL.
  - M3: `no settling learner carries a day count...` FAIL.
  - M5 (`internal_gains_gate_open` -> `house_loss_converged`): `#2223: a heat-loss level exactly on the confidence threshold has converged` and `the gates are counted on the learners' own predicates` (`house 50 gains 50`) FAIL.
  - My own mutant RW (`blocked_by is not None and rate is None` -> `rate is None`, waiting with no weather named) is killed by five R10 checks.
- Reviewer-built probe, disclosed as mine (`ev/reviewer_probe.py`). It calls `learner_progress_view` on a grid of 25920 learner rows: counts at and around each gate (house 50, gains 114, solar 30), weather (cold or warm, sun or dark), install shape (two-zone, sensor) and snapshot sets (none, a counting window, a flat window, a window under a day). It checks the brief's invariants: phases are only off/counting/settling/waiting; `eta_days` appears only while counting and is finite and positive; `waiting_for` is set if and only if the phase is waiting; counting progress equals samples / samples_needed; lower is off unless two-zone AND sensor; no settling learner is below its gate.
  - `RESULT grid rows=25920 violations=0` at the head.
  - Null control: on a constant-rate plant, the ETA is within 0.043 d of the true days to the gate (n=8).
  - Rate-window rule: the newest snapshot at least a day old is used and a younger one skipped (`older_behind_young` eta 3.3 = 20 / 6 per day). A future stamp gives no rate. A NaN count reads 0.
  - Probe mutants (`ev/probe_mutants.txt`): M1, S4, RW and an eta-on-settling plant are all caught by the probe. M3 and S2 are outside the probe's invariants and are killed by `tests/features.py` instead.
- Finder's harness (step 2). `eta_rolling.py` (sha1 ea7de4d7…, from `git archive 4f2d513c9`) at the merge base c176ee55d and at the head prints `IDENTICAL_EXCEPT_TIMING`. It is flat by design and not regressed; pooled house `err_count` p50 is -28.7 d at both ends, as the body says.
- Companion, run at both ends; every figure in the body re-derives:
  - head: `eta_on_settling=0`, `gate_err` -0.0/+0.1/+0.1 (n=8), `settle_err` -36.2/-35.8/-35.8 (n=7), phases counting 22 / settling 1147 / waiting 7;
  - base: `field=absent`;
  - under M1: `eta_on_settling=853`;
  - E0: `gate_err` +0.1 (n=1);
  - `--alpha-scale 2`: `gate_err` -0.2 (n=1).
  - `gate_err` rests on n=8 checkpoints (n=1 for each control). The companion's `eta_on_settling` uses the view's own `samples_needed`; my probe checks the same invariant independently of it.
- Day-count consumers. Ran the body's class rule (`ev/class_rule_head.txt`, 37 hits): `learner_progress.eta_days` is the only forward day figure, matching the body's list. Grepping the card JS, translations and diagnostics for an ETA or eta_days consumer finds 0. No day-count ETA ever shipped at the base, so none needed removing. Diagnostics passes `learner_progress` through via the `LearningView` keys. The card does not render it yet; that is the R10-UX-HEALTH carry.
- Forward-carry (step 10). The R10-UX-HEALTH carry is in `dev/programme/rosters/wave-r10-groups.json` at the head and states its Precondition and Control.
- Claims (step 4). `tests/env_drift.py --all origin/main` gives `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE`. Exactly the five `coord_*` fixtures are CLAIMED, each with one leaf (`data.learner_progress: present on one side only`) (`ev/env_drift_all.txt`). The claim lines replace R10-SCORES's inline notes for the same five fixtures; R10-SCORES's paragraph is kept.
- `VERSION`, the manifest version and the RELEASE_NOTES heading are untouched (step 5).
- Merge (step 13). `git merge-tree --write-tree origin/main b0cab1fca` exits 0; LEDGER-MERGE resolves `tests/closures.json`.
- Structure at b0cab1fca: `STRUCTURE RATCHET PASSED`, `seam_cut_total 707 <= 707`. The re-record reason is in the message of `b6c2a5ab7`.
- CI at b0cab1fca: every check run concluded success or skipped, including `gate`, `tests / fast (3.14)`, `tests / mutation`, `tests / closures`, `tests / coverage` and `tests / typing`.
  - One `pr-contract` run failed with `FAIL closed: no run at this head owns a finished codeql unit for base 'main' after 600 s`, a CodeQL wait timeout; its body check printed `clean no refusal`. Later `pr-contract` runs, started 23:44Z and 23:55Z after CodeQL concluded, are green.
  - The red checks the body lists from earlier heads (mutation unpinned, typing, finite_boundary, entities/doc_claims, env_drift) are each named and answered.
- Head SHA in the body is b0cab1fca (step 7), which is the head I measured.
