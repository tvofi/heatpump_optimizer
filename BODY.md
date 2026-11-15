Group: R11-PRE-ROUND-CHECK-GATE, part 2 (topic r11-pre-round-check-gate-p2), stacked on part 1 (handoff/r11-pre-round-check-gate)
Ruling: tvofi 2026-11-15, "All groups that are not finder critical and not closed by cutover goes tho the architect and planner in the same way", corrected: "i meant cutover as when the finders are finished". The orchestrator ruled that this part is not finder-critical and that, for a group, an absent mark must not count as gating.
Code-owned and policy: tools/audit/check_scopes.py and dev/governance/roles/architect-planner.md need tvofi's approving review, or one under mandate 6893738184 (issue 3394, scope all, to 2026-12-15T12:00Z).

Part 1 lists the open non-gating evaluation cards for P3. This part adds the roster groups. The refusal of a plan that loses an open card or group moves to part 3, for the reason under the bootstrap bullet below:

- **A roster group's `gates_finders`** (true or false) is the same field as on a card, read through `roster_lib.finder_gate`, which returns None unless the value is a boolean. It is written by `roster_edit.py set-field <group> gates_finders true|false`, an existing queue-lane op, so there is no new op. `brief_lint.mjs`'s shape check refuses a non-boolean value. Absent is allowed, so no existing roster goes red.
- **`roster_lib.architect_groups(roster)`** returns `(listed, unmarked)`. `listed` is every open group (`is_open`, the module's one open rule) whose `gates_finders` is not true. `unmarked` is those of them with no boolean. An unmarked group is listed and never read as gating, so it cannot drop out of the architect's plan unseen.
- **`check_scopes.py --round N --open-cards`** now prints `{round, open_cards, unmarked_cards, open_groups, unmarked_groups, ref, roster_ref}`. `p3_input` joins part 1's `open_cards_report` (the card half, repaired for fix review 3620) with `architect_groups_report` (the group half). The roster is read through `roster_lib.reader_ref`/`show_roster`, or `--roster-ref`, never a fixed path. Each unmarked card or group gets an `UNMARKED <id>: ...` line, and the listing exits 1 while either half has one.
- **Bootstrap split**: in CI, `check-wave-script.mjs` runs the base's copy (`ci_predict.py` predicted this BOOTSTRAP red at 9fb327ecb3). Main's copy drives audit-plan.js with stubs that carry no `--open-cards` listing, so the refusal and its grader arms cannot land in one pull request. This part lands only the grader's stubs: the read reply carries `open`/`open_rc`, and the plan carries `open_items`/`dropped`. Today's audit-plan.js ignores them, and part 3's refusal (built and green at work/r11-pre-round-check-gate-p3-draft 9fb327ecb3) passes against them. Measured: this head's grader against part 3's audit-plan.js printed `223 passed, 0 failed`.
- **Policy, minimal, for tvofi's review**: architect-planner.md Inputs now say "the cards and roster groups open at P3's start" and step 3 says "Every finding, open card and open group appears in the plan exactly once". Paid within its token cap by dropping "; none is dropped silently", which "exactly once" already says.

A design choice to say: `is_open` counts `refuted` as open and `deferred` as closed, so a refuted group is listed and a deferred one is not. The listing reads the module's one open rule rather than a second one of its own.

Carry 0: built here, except for its last clause. This is part 1's carry 4ffa4b06: the roster groups in P3's listing and UNMARKED with rc 1. Its audit-plan.js refusal moves to part 3, see Forward-carry.

## Approval

Not yet given. The architect-planner.md edit awaits tvofi's approving review at the head, or an approving review under mandate 6893738184 (issue 3394, scope all, to 2026-12-15T12:00Z), declared with the mandate id.

## Head

b15449f38ac4ecd2787a70cb80f02050d2a4e0ba. It is part 1's repaired head fc369d59a8 merged in (merge 5519adfdce; the `--open-cards` block conflicted and is resolved into `p3_input`), plus one self-test arm. Merge base with main: b3831ff64e. The roster_lib and roster_edit self-tests ran at 9fb327ecb3; neither file changed since. Every check_scopes figure below was measured at this head.

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

brief_lint's rule is pinned by the red run above.

## Null control

- `architect_groups` on a roster whose open groups all gate returns `([], [])`.
- Live: `python3 tools/audit/check_scopes.py --repo . --ref c6ce415b77 --round 11 --open-cards` reads eval/r11 with the owner's `gates_finders` values and the roster at cfd82c7fbb. It exits 1 with:
  - `open_cards`: 12, `unmarked_cards`: 0. These are the 12 false cards.
  - `open_groups`: 41, `unmarked_groups`: 41. No group carries the field yet, so all 41 are named. The orchestrator marks them by queue op.

## Figures

- `python3 tools/audit/seat/roster_lib.py --self-test`: `roster_lib self-test: 95 checks, 0 failed`.
- `python3 tools/audit/seat/roster_edit.py --self-test`: `roster_edit self-test: 313 checks, 0 failed`.
- `node tools/policy/check-wave-script.mjs` at this head: `223 passed, 0 failed`. Against part 3's audit-plan.js it also printed `223 passed, 0 failed`.
- `node tools/policy/brief_lint.mjs`: rc 0 at the head; rc 1 with the vacuous pin before the rule.
- `check_scopes.evaluation_self_test` at the head: 66 of 66 held (part 1's repaired 62 plus 4).
<!-- figure-block: scope-line mb=b880dc914f3ba2590b7ce655d7419678b1c4968e head=b15449f38ac4ecd2787a70cb80f02050d2a4e0ba -->
~~~text
MODE: SCOPED -- 2 script(s) run, 31 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none. `prepr.sh` at b15449f38a predicted 2 reds on governance / instrument-self-tests, and neither is caused by this diff: both are timeouts (rc 124) on a host running several prepr runs at once.
- "Show the roster editor refusing its own fixtures": rc 124 at the head, 0 at the base. Run untimed, `python3 tools/audit/seat/roster_edit.py --self-test` printed `roster_edit self-test: 313 checks, 0 failed`. That was at 9fb327ecb3, and roster_edit.py has not changed since.
- "Show the CI predictor (tools/pr/ci_predict.py) predicting pr-contract's carry refusal": rc 124 at the head, 0 at the base. Run untimed, `python3 -I tools/pr/ci_predict.py --self-test` printed `ci_predict self-test: 0 failed` at 25dabf079a.
- CI's runner is the authority on both.

## Forward-carry

- The audit-plan.js refusal is part 3 of this group (topic r11-pre-round-check-gate-p3), built at work/r11-pre-round-check-gate-p3-draft 9fb327ecb3 and green there (check-wave-script `230 passed, 0 failed`, with 6 arms red against today's audit-plan.js). It opens once this part is on main.
  - P3's read step runs `--open-cards` at origin/main and stops on a non-zero exit or a missing listing.
  - P3 refuses an open card or group that is not a plan group, an `open_items` entry or a drop with a reason, and one placed twice.
  Carry: R11-PRE-ROUND-CHECK-GATE


## Friction

none
