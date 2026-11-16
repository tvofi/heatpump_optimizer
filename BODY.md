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

81119045726e9b1dfeff11c0029ae789e9af3f61: a merge of origin/main 030a4d377f into the previous head a59eafe204 (merge base with main: 030a4d377f). Two files conflicted and are resolved by union, each read back against both parents:
- `tools/audit/check_scopes.py`: this branch's `architect_groups_report` and `p3_input` are kept beside main's `open_cards_cli` and `json_or_none`. Main's CLI arm runs `--open-cards` on a scratch repository with no roster, and this branch's group half reads one, so both of the arm's runs failed with `RosterNotFound` (`marked rc=1, unmarked rc=1 []`). The arm's two commits now carry one roster whose open group G1 is marked non-gating, and the runs pass `--roster-ref`. The arm still measures the card half's exit code and UNMARKED lines alone, and its null control also asserts `open_groups == ["G1"]`. This changes a self-test fixture only, no production line.
- `tools/policy/check-wave-script.mjs`: this branch's comment on the OPEN/MOVES stubs is kept above main's OPEN stub.

The previous head a59eafe204 repaired fix review 3633's block at 416280f5c2. It added 1 and ["x"] to the self-test arm for the evaluator and reviewer (C7, below). The mutation figures below were measured at the heads they name. Each self-test figure under Figures was measured at 8111904572.

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

brief_lint's rule is pinned by the red run above.

## Null control

- `architect_groups` on a roster whose open groups all gate returns `([], [])`.
- Live: `python3 tools/audit/check_scopes.py --repo . --ref c6ce415b77 --round 11 --open-cards` reads eval/r11 with the owner's `gates_finders` values and the roster at cfd82c7fbb. It exits 1 with:
  - `open_cards`: 12, `unmarked_cards`: 0. These are the 12 false cards.
  - `open_groups`: 41, `unmarked_groups`: 41. No group carries the field yet, so all 41 are named. The orchestrator marks them by queue op.

## Figures

- `python3 tools/audit/seat/roster_lib.py --self-test`: `roster_lib self-test: 95 checks, 0 failed`.
- `python3 tools/audit/seat/roster_edit.py --self-test`: `roster_edit self-test: 313 checks, 0 failed`.
- `node tools/policy/check-wave-script.mjs` at 8111904572: `249 passed, 0 failed` (main's grader arms added since a59eafe204 included). At a59eafe204 it printed `223 passed, 0 failed`, and the same against part 3's audit-plan.js.
- `node tools/policy/brief_lint.mjs`: rc 0 at the head; rc 1 with the vacuous pin before the rule.
- `python3 tools/audit/check_scopes.py --repo . --self-test` at 8111904572: rc 0, `SELF-TEST passed`, `evaluation arms: 66/66 held; ... --open-cards rc=2, marked rc=0, unmarked rc=1 ['UNMARKED C2', 'UNMARKED C3']`. Without the merge's roster fixture, main's two `--open-cards` CLI arms fail (rc 1, shown above): that is this fixture's null control.
- `tools/pr/prepr.sh` self-test step at 8111904572: `553 passed, 0 failed`.
<!-- figure-block: scope-line mb=98847b99d7bb3238686efd6869f805c89c6d1ff1 head=81119045726e9b1dfeff11c0029ae789e9af3f61 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Red checks

Inherited from main, not caused by this diff: `orchestrator_tick.py` raises NameError `SEAT_WINDOW_MIN` on main, and hotfix #3661 repairs it. This applies only if that check is red at 8111904572. No other red is predicted. CI's runner is the authority.

## Forward-carry

- The audit-plan.js refusal that roster carry 4ffa4b06 assigns to part 2 is split out of this pull request, **pending the orchestrator's ruling** on the split; no plan names a part 3 yet, and the orchestrator may record it in the roster instead. The split's cause: governance.yml's wave-script job restores `tools/policy/check-wave-script.mjs` from `$PINNED` before "Drive the wave script's branching", so the refusal and its grader arms cannot land in one pull request (confirmed by fix review 3633). The refusal is built at refs/heads/handoff-wip/r11-pre-round-check-gate-p3, 9fb327ecb3, as topic r11-pre-round-check-gate-p3, and is green there (check-wave-script `230 passed, 0 failed`, with 6 arms red against today's audit-plan.js). It opens once this part is on main.
  - P3's read step runs `--open-cards` at origin/main and stops on a non-zero exit or a missing listing.
  - P3 refuses an open card or group that is not a plan group, an `open_items` entry or a drop with a reason, and one placed twice.
  Carry: R11-PRE-ROUND-CHECK-GATE


## Friction

none
