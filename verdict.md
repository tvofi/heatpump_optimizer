Fix review: merge a27666c2a7387107ddf2b77faec71924fdd74fb5

bus-nonce: 3268cff34c64ca838ffe40cf46c40248
pending-ci: gate

## Round

Second round, a delta review over the reviewed head ec9645014c773759edfbf632829c7cbef272ba33 (previous verdict: `Fix review: merge`, pending-ci gate). Measured head: a27666c2a7387107ddf2b77faec71924fdd74fb5, which is still `refs/pull/3580/head` when this verdict was written. The role contracts are current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty with origin/main at 82fa3884c2.

## Evidence

- RESULT delta shape: a27666c2 has the parents ec9645014c (the reviewed head) and cbc42e0924 (main). `git merge-tree --write-tree cbc42e0924 ec9645014c` exits 0 with tree 2545cf3850, which is byte-identical to a27666c2's own tree. The merge is therefore the clean automatic merge with no hand resolution, and every line of `git diff ec96450 a27666c2` is main's own (ev/remerge-cbc42e-ec9645.txt, ev/merge-shape.txt).
- RESULT why the PR's own diff changed: main merged #3576 (part 1, d051cb3edf) between 513a07dfdc and cbc42e0924. Part 1's commit c79e44e2 is now an ancestor of main. Main's range overlaps this PR's files in away.py, strings.json, de, en and sv.json, docs/configuration.md and docs/how-it-works.md. The PR's own patch went from 11 files to 9: away.py and how-it-works.md now carry only part 1's lines, which main already has.
- RESULT no reviewed line changed: I compared the PR's own +/- lines before the merge (`513a07dfdc..ec9645014c`) and after it (`cbc42e0924..a27666c2a7`) over the 9 files the PR still touches.
  - The new patch is a strict subset of the old one: 38 lines dropped and 0 added (ev/own-patch-old-vs-new.txt).
  - Every dropped line belongs to part 1: `space_setpoint_unit`, `away_dhw_min_temperature`, `dhw_free_disinfection_enabled`, `vvc_pump_entity` and the matching configuration.md rows.
  - 18 of the 19 dropped `+` lines are present verbatim on main. The 19th, sv `space_setpoint_unit`, was reworded on main by #3576's own later commit 5604d6eb ("Say entity, not unit"). It was reviewed under #3576, not here.
  - Every line of carries 5 to 13 is unchanged.
- RESULT previous findings: the Follow-up (part 1 #3576 had to merge before this PR) is resolved, because #3576 merged as d051cb3edf and its commits are on main. The prior dismissed note on carry 6's unbilled-window omission stays dismissed: the main_fuse_amperes text is unchanged at this head.
- RESULT production delta and whether it widens the review (step 12): main's production changes in the delta are duty_switch.py (`Direction.decay` clamps to N_CAP), ledger.py (`REFERENCE_BASIS` 1 to 2) and optimizer.py (`_apportion_by_steady_demand` removed), plus the sv.json `börvärdesentiteten` label. The only reviewed text they bear on is carry 9 and carry 11's savings sentences in docs/dashboard-card.md.
  - The pricing (`spot + fee_per_kwh`) is unchanged.
  - The "first month with a booked saving" gate is unchanged: the bump only re-stamps which months state a saving (ledger.py: a row whose stamp is not `REFERENCE_BASIS` states no saving).
  - Neither sentence becomes false, and `tests/doc_claims.py` still pins both at this head. There is no non-obvious risk, so the review was not widened.
- RESULT mutation (step 1), my own mutants at this head, each one replacement restored afterwards, with `git diff --quiet` clean:
  - MA puts the en `config.step.user` name description back to "Shown in front of every sensor this integration creates.": `2 of 380 checks FAILED` (ev/mutant-A-en-name.log).
  - MB sets topology.py `_ADVISOR_DUTY_FRACTION` 0.5 to 0.4: `2 of 380 checks FAILED` (ev/mutant-B-duty-fraction.log).
  - No mutant survived.
- RESULT figures at this head, cheap checks re-run:
  - `tests/doc_claims.py`: `ALL 380 checks PASSED` (ev/doc_claims.log).
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED` (ev/structure.log).
  - `tests/entities.py`: `ALL 2713 ENTITY CHECKS PASSED` (ev/entities-tail.log).
  - The body's 2711 was measured at 3047b48a, and the body says so.
- RESULT merge with main (step 13): `git merge-tree --write-tree origin/main a27666c2` exits 0, tree 0f508ca965, no conflict (origin/main 82fa3884c2; ev/merge-tree-origin-main.txt).
- RESULT step 7: the PR body's `## Head` names a27666c2a7387107ddf2b77faec71924fdd74fb5 and describes it as the orchestrator's automatic merge of main cbc42e0, which matches the measurement above.
- RESULT step 5: VERSION, manifest.json and RELEASE_NOTES.md are not in the delta, and they are not in the PR's own diff (`git diff --name-only cbc42e0924 a27666c2a7`).
- RESULT red checks (step 11): `tests / fast (3.14)` is in the `merge_train.py owed-reds` set. It went red at the earlier head b7238087, and the body's `## Red checks` names and answers it: main's weekend-clock defect, with the root cause in R10-RCA-FEATURES-WEEKEND-CLOCK (PR 3583). The trigger is answered. At this head, classify reports `red: none`.
- RESULT figures not re-derived: the scoped-gate line and the env_drift run against origin/main are CI's heavy runs (fix-review.md 11). The carry-12 PNG `cmp` needs a recording host, as the previous round already said.
- RESULT CI: `merge_train.py classify a27666c2 --pr 3580` was polled about every 70 s from 13:25Z to 14:12Z, 40 runs. Every run printed `WAIT a27666c2a7387107ddf2b77faec71924fdd74fb5 pending: gate red: none` (rc 3; ev/classify.log), so this merge verdict is returned with `pending-ci: gate`. The head was re-read at 14:13Z and is unchanged.

## Findings

none

## Friction

none
