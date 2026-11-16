Group: R11-PRE-ROUND-CHECK-GATE, part 2 (topic r11-pre-round-check-gate-p2), stacked on part 1 (handoff/r11-pre-round-check-gate)
Ruling: tvofi 2026-11-15, "All groups that are not finder critical and not closed by cutover goes tho the architect and planner in the same way", corrected: "i meant cutover as when the finders are finished". The orchestrator ruled that this part is not finder-critical and that, for a group, an absent mark must not count as gating.
Code-owned and policy: tools/audit/check_scopes.py and dev/governance/roles/architect-planner.md need tvofi's approving review, or one under mandate 6893738184 (issue 3394, scope all, to 2026-12-15T12:00Z).

Part 1 lists the open non-gating evaluation cards for P3. This part adds the roster groups. The refusal of a plan that loses an open card or group moves to part 3, for the reason under the bootstrap bullet below:

- **A roster group's `gates_finders`** (true or false) is the same field as on a card, read through `roster_lib.finder_gate`, which returns None unless the value is a boolean. It is written by `roster_edit.py set-field <group> gates_finders true|false`, an existing queue-lane op, so there is no new op. `brief_lint.mjs`'s shape check refuses a non-boolean value. Absent is allowed, so no existing roster goes red.
- **`roster_lib.architect_groups(roster)`** returns `(listed, unmarked)`. `listed` is every open group (`is_open`, the module's one open rule) whose `gates_finders` is not true. `unmarked` is those of them with no boolean. An unmarked group is listed and never read as gating, so it cannot drop out of the architect's plan unseen.
- **`check_scopes.py --round N --open-cards`** now prints `{round, open_cards, unmarked_cards, open_groups, unmarked_groups, ref, roster_ref}`. `p3_input` joins part 1's `open_cards_report` (the card half, repaired for fix review 3620) with `architect_groups_report` (the group half). The roster is read through `roster_lib.reader_ref`/`show_roster`, or `--roster-ref`, never a fixed path. Each unmarked card or group gets an `UNMARKED <id>: ...` line, and the listing exits 1 while either half has one.
- **Bootstrap split**: in CI, `check-wave-script.mjs` runs the base's copy (`ci_predict.py` predicted this BOOTSTRAP red at 9fb327ecb3). Main's copy drives audit-plan.js with stubs that carry no `--open-cards` listing, so the refusal and its grader arms cannot land in one pull request. This part lands only the grader's stubs: the read reply carries `open`/`open_rc`, and the plan carries `open_items`/`dropped`. Today's audit-plan.js ignores them, and part 3's refusal (built and green at refs/heads/handoff-wip/r11-pre-round-check-gate-p3, 9fb327ecb3) passes against them. Measured: this head's grader against part 3's audit-plan.js printed `223 passed, 0 failed`.
- **Policy, minimal, for tvofi's review**: architect-planner.md Inputs now say "the cards and roster groups open at P3's start" and step 3 says "Every finding, open card and open group appears in the plan exactly once". Paid within its token cap by four trims, all in the three-dot diff from part 1's commit 0d46ea8bd9:
  - "; none is dropped silently" is dropped; "exactly once" already says it.
  - "(sensitivity, tradeoff points)" is dropped from **Method**; step 2 still names the sensitivity and tradeoff points.
  - The holdout list "structure budgets, the tripwires, the behaviour inventory, mutation kill rate and change coupling" becomes "the first five fitness functions step 7 names", the same five.
  - **"read-only on code" is deleted from the seat's description** ("One opus seat, read-only on code, writing only the plan" becomes "One opus seat, writing only the plan"). This one changes what the seat may do, and it awaits the owner's approving review with the rest of the edit.

A design choice to say: `is_open` counts `refuted` as open and `deferred` as closed, so a refuted group is listed and a deferred one is not. The listing reads the module's one open rule rather than a second one of its own.

Carry 0: built here, except for its last clause. This is part 1's carry 4ffa4b06: the roster groups in P3's listing and UNMARKED with rc 1. Its audit-plan.js refusal moves to part 3, see Forward-carry.

## Approval

Not yet given. The architect-planner.md edit awaits tvofi's approving review at the head, or an approving review under mandate 6893738184 (issue 3394, scope all, to 2026-12-15T12:00Z), declared with the mandate id.

## Head

2cb653f2dddc258386bddd7dc097bb9c0e323c17. Fix review 3633 blocked 2061e87b06 as merge-conflict (verdict ba10e32638): tools/audit/seat/roster_edit.py conflicted with origin/main (#3657's CONVERGENCE_FIELDS against this part's gates_finders in set-field). Answered: this head is 2061e87b06 with origin/main 30f9caac90 merged in (merge 26b20a7faa), plus one self-test commit 2cb653f2dd. Merge base with main: 30f9caac90. Every figure below was measured at this head.

prepr: passed rc=0 at 2cb653f2dddc258386bddd7dc097bb9c0e323c17

### The merge resolution, by side

Read back from the merged `tools/audit/seat/roster_edit.py`:
- This part contributes `"gates_finders"` inside the `SET_FIELDS` tuple, `|gates_finders` on the `set-field` usage line, and the `op_set_field` branch `elif field in ("hotfix", "gates_finders")`.
- Main (#3657) contributes `+ roster_lib.CONVERGENCE_FIELDS` after the tuple, the usage continuation line `|found_by|owned_by|caused_by|family|cm_kind|parent|follows`, and the `op_set_field` branch `elif field in roster_lib.CONVERGENCE_FIELDS`.
- `grep -c` finds each of the two `op_set_field` branches exactly once (1 and 1). No other file conflicted; `roster_lib.py` auto-merged.

New self-test row "set-field gates_finders and a convergence field in one run: both read back, both in the usage line" sets `gates_finders true` and `found_by reviewer` on one group in the same self-test run, reads both back, and checks every field of `("gates_finders",) + roster_lib.CONVERGENCE_FIELDS` appears as `|<field>` in the module usage text. Each mutant applied alone to the merged file and restored (`cmp` against the saved copy matched):
- M1, main's side dropped (`+ roster_lib.CONVERGENCE_FIELDS` removed): `318 checks, 5 failed`, the new row among them.
- M2, this part's side dropped (`"gates_finders"` removed from the tuple): `318 checks, 3 failed`, the new row among them.
- M3, `|gates_finders` removed from the usage line: `318 checks, 1 failed`, the new row.
- M4, main's usage continuation line removed: `318 checks, 1 failed`, the new row.
- NULL, the merged file unchanged: `318 checks, 0 failed`.

## Mutation proof

Failing tests first; each ran red before its implementation:
- roster_lib self-test: NameError `finder_gate`.
- `evaluation_self_test`: NameError `architect_input`.
- brief_lint: `FIXTURE VACUOUS: [gates-not-bool] shape: \`gates_finders\` is present but is not true or false`.

Mutants (roster half, at 9fb327ecb3): `python3 tools/audit/seat/mutant_run.py --spec <scratch mutants2.json> --in-place --cmd "bash <scratch p2test.sh>"`, where the command runs the roster_lib self-test and `evaluation_self_test`. NULL survived and 5 of 5 were killed:
- P1: `finder_gate` returns any value.
- P2: an unmarked group is read as gating (`is False`).
- P3: unmarked is never flagged.
- P4: the listing's rc is always 0.
- P5: closed groups are listed (`groups_of` for `open_groups`).

Mutants (the joined listing, at b15449f38a): `--spec <scratch mutants4.json>`, same command. NULL survived and 5 of 5 were killed:
- G1: the group half's rc is always 0.
- G2: the joined rc is the card half's only.
- G3: the joined rc is the group half's only.
- M11: the reviewer's mutant of #3620.
- G4: the group half's UNMARKED lines are dropped. This one first survived; the whole-listing arm now asserts the line.

Fix review 3633's mutants C7 and C7b, run with the reviewer's driver (verdict/3633 `evidence/mut.py`, worktree path changed only), each applied alone and restored. The command is `python3 tools/audit/check_scopes.py --repo . --self-test`:
- C7, `norm(str(ev.get(k) or ""))`, accepts a truthy non-string evaluator or reviewer. At b15449f38a it SURVIVED (rc 0). At a59eafe204 it is KILLED (rc 1). The only change between the two runs is the arm "a null, absent, blank or non-string reviewer or evaluator is refused", which now also tries `1` and `["x"]`.
- C7b, `norm(ev.get(k, ""))`, restores the base's line. It is KILLED (rc 1) at both heads.

prepr's diff-mutants step skipped because MUTANT_CMD was unset. This delta adds no production line, only two values in a self-test arm. The C7/C7b runs above are its mutation proof.

At this head prepr's diff-mutants step again skipped (MUTANT_CMD unset). The repair delta adds no production line of its own: the merged `SET_FIELDS` and usage line are the union of two already-reviewed lines, and the rest is one self-test row. Its mutation proof is M1-M4 under `## Head`.

brief_lint's rule is pinned by the red run above.

## Null control

- `architect_groups` on a roster whose open groups all gate returns `([], [])`.
- Live: `python3 tools/audit/check_scopes.py --repo . --ref c6ce415b77 --round 11 --open-cards` reads eval/r11 with the owner's `gates_finders` values and the roster at cfd82c7fbb. It exits 1 with:
  - `open_cards`: 12, `unmarked_cards`: 0. These are the 12 false cards.
  - `open_groups`: 41, `unmarked_groups`: 41. No group carries the field yet, so all 41 are named. The orchestrator marks them by queue op.

## Figures

All at 2cb653f2dddc258386bddd7dc097bb9c0e323c17:
- `python3 tools/audit/seat/roster_lib.py --self-test`: `roster_lib self-test: 101 checks, 0 failed` (95 at the previous head; main's #3657 brought the rest).
- `python3 tools/audit/seat/roster_edit.py --self-test`: `roster_edit self-test: 318 checks, 0 failed` (313 at the previous head, plus main's arms and the new row).
- `node tools/policy/check-wave-script.mjs`: `249 passed, 0 failed`. With part 3's `.claude/workflows/audit-plan.js` (from 9fb327ecb3) copied over this head's and restored afterwards, it printed `249 passed, 0 failed` too. The earlier body's 223 was measured at a59eafe204, before the main merges.
- `node tools/policy/brief_lint.mjs`: rc 0.
- `python3 tools/audit/check_scopes.py --repo . --self-test`: rc 0, `evaluation arms: 66/66 held`.
<!-- figure-block: scope-line mb=6f422812d5d8b918beace0283419c153f6df66ce head=2cb653f2dddc258386bddd7dc097bb9c0e323c17 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Red checks

none. Fix review 3633 read CI at 2061e87b06 as `WAIT ... pending: gate red: none` (`merge_train.py classify`), with no owed red. At this head, `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` exited rc 0. Its ci predict step (`ci_predict.py --record-self-tests`) predicted no closures, fast, governance or instrument red. CI's runner is the authority.

## Forward-carry

- The audit-plan.js refusal that roster carry 4ffa4b06 assigns to part 2 is split out of this pull request, **pending the orchestrator's ruling** on the split; no plan names a part 3 yet, and the orchestrator may record it in the roster instead. The split's cause: governance.yml's wave-script job restores `tools/policy/check-wave-script.mjs` from `$PINNED` before "Drive the wave script's branching", so the refusal and its grader arms cannot land in one pull request (confirmed by fix review 3633). The refusal is built at refs/heads/handoff-wip/r11-pre-round-check-gate-p3, 9fb327ecb3, as topic r11-pre-round-check-gate-p3, and is green there (check-wave-script `230 passed, 0 failed`, with 6 arms red against today's audit-plan.js). It opens once this part is on main.
  - P3's read step runs `--open-cards` at origin/main and stops on a non-zero exit or a missing listing.
  - P3 refuses an open card or group that is not a plan group, an `open_items` entry or a drop with a reason, and one placed twice.
  Carry: R11-PRE-ROUND-CHECK-GATE


## Friction

none
