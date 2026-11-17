Fix review: merge ba0a43950c363becde31704e62552b449920b484

bus-nonce: 00cbb98464c5fe12017bb65ff348f2e7
pending-ci: gate

## Scope

Round 1 of review for #3693 (the review packet: full scope, no reviewed head). Tests and harness only: `git diff --quiet origin/main...ba0a43950c -- custom_components VERSION RELEASE_NOTES.md tests/golden` exits 0, so step 5 (VERSION, manifest, notes heading) and step 4 (claim files, no golden moves) hold trivially, and steps 15 and 16 have no production line to judge. Role contract current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Findings

none

## Evidence

- Head: `ba0a43950c363becde31704e62552b449920b484` (`ev/HEAD.txt`), the PR's head at review and at return. Its own three-dot diff equals the body's measured `dbc806ce5f`'s apart from the delivery row (`dev/programme/delivery/3693.md`), so the body's figures at `dbc806ce5f` and `f7146ba6bd` read this head's code.
- Merge: `git merge-tree --write-tree origin/main ba0a43950c` exits 0, no conflict (`ev/merge_tree.txt`); the merge base is origin/main `38bf516bdd`.
- Mutation proof, step 1, re-run at this head: CMD A (`ev/cmdA.sh`, the group's block bounded by the `#3616` marker) on the unedited head prints `ALL 57 FEATURES BLOCK PASSED`, exit 0 (`ev/cmdA_head.txt`). `tools/audit/seat/mutant_run.py --spec ev/six_spec.json --cmd 'bash cmdA.sh'` in its default `git archive` copy: `SURVIVED NULL`, `KILLED` for all six of `REV_HEATS_HALF_FLOOR`, `REV_NO_POLISH`, `REV_STAGE_BOX_TANK_ROOM`, `REV_ONE_RESOLVED`, `REV3_TIE_NOT_ASKED_SIDE_OFF`, `REV3_TIE_ASKED_SIDE_OFF`, rc 0 (`ev/mutants_head.txt`). Each mutant's `old` text occurs exactly once in its file at this head.
- Adversarial check of the `REV_ONE_RESOLVED` kill: the check's first clause reads the constant `_RESOLVED_CANDIDATES == 2` directly, which would kill that mutant with no behaviour read. With the mutant applied and that clause replaced by `True`, the check still fails on behaviour (`as it stands [13.53, 12.87, 17.93]; shipped ...`, `1 of 57 FEATURES BLOCK FAILED`, rc 1: `ev/one_resolved_behavioural.txt`). The kill is earned by the behaviour, not the constant.
- Spec: `dev/audit/harnesses/r11_honest_starts_runs_mutants.json` holds 54 entries at this head, as the body states.
- Harness, `identity` (seed 0) at this head, exit 0: 2215, 1801, 1427, 0, 1958 of 3000 for the five arms, the zero arm moving no mask and its perturbation (`_TIE_BREAK` at 0) moving 1958: every figure in the body re-derived (`ev/identity_head.txt`).
- Harness, `stage` (seed 1, 140 cells) at this head, exit 0: descents cells 12 solves, 20 engaged, 20 calls with two plans, below 6, equal 14, above 0; generated cells 140 solves, 149 engaged, 64 calls, below 16, equal 48, above 0; realizable first plan in 18 calls, changed 13 (11 priced), unchanged 5 (5 priced); unpriced changed plans clip 1.374 and 0.600 kW; the two priced gains 15.3964 and 15.4278 clip 3.062 and 2.359 kW, edges 11 to 10. Every figure in the body re-derived (`ev/stage_head.txt`).
- Stage null control, step 3, re-run: the spec's `UNPRICED_DESCENT` applied to a `git archive` copy of this head, `stage 1 0`: `descents cells: 12 solves, 22 engaged stage calls; ... 0 calls, below 0, equal 0, above 0`, exit 0, against 20 calls unmutated (`ev/stage_null_unpriced_descent.txt`). The body's line re-derived.
- Harness, `descents` at this head (item r2): mild cell `duty-cycle price phase 30 outdoor 2.0` both 26.1997, operand 26.2715; cold cell `... outdoor -4.0` both 37.4775, unpriced 37.8683, exit 0 (`ev/descents_head.txt`): the body's figures and the cells test 5 now names.
- Step 2, both ends: the base and the head share every production line, so the group harness's modes read the base's code too; the two new modes do not exist at the base, as the body says. The packet names no finder's harness: the finding is the round-3 fix review's surviving mutants, whose instrument is the committed spec and driver re-run above.
- Step 6, class: the class is the parent review's four survivors plus the two tie-break halves of the owner's ruling; all six are in the diff and killed. The full 54-entry spec and the mutation table were not re-run here (CI's heavy runs are cited, tvofi 2026-09-30).
- Step 10, carries: both `Carry: R11-OUTSIDE-HONEST-STARTS-RUNS-P3` items are in that group's entry of `dev/programme/rosters/wave-r11-groups.json` on `handoff/audit-r10-roster` at `3524ff1d31` (the `median_off_s` item and the three live fork checks); the packet's carry_audit at the head: `4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)`.
- Step 14: no budget, closure, golden, claim, ledger or score file moves; the spec gains six entries, earned by the six checks.
- Owed reds: the set is `ev/owed_reds.txt`.
- Not verified here: the body's Friction claim that the single-marker CMD A now raises `NameError` in `_ssg_cycles` (paperwork; the bounded command it uses instead was re-run above), and the tie-halves counts 87 and 61 of 129, which the body itself marks quoted from out-of-tree evidence.
- CI at this head: `merge_train.py classify ba0a43950c --pr 3693` printed `WAIT ... pending: gate red: none` from 01:35 to 02:04 UTC (`ev/classify_log.txt`), then exit 2, unreadable, at 02:08 and 02:10: `REFUSE selftests: the base's governance / instrument-self-tests job 133732070457 is in_progress, which reads no step: an introduced red cannot be ruled out (fail closed)`. No check had gone red at this head when read; the verdict carries `pending-ci: gate`, so the relay posts it only once the head is green and refuses it over a red.
