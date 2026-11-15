Group: R11-PRE-ROUND-CHECK-GATE (topic r11-pre-round-check-gate)
Cards: E11-N-NULL-REVIEWER (accepted by tvofi, "Accept both (Recommended)"); tvofi's 2026-11-15 ruling "Only the finder critical are required for finder start", with his 14:00Z correction that what is still open when the finders finish goes to the architect and planner.
Code-owned and policy: tools/audit/check_scopes.py, dev/governance/decisions/0018-objective-function.md (sections 5 and 6) and dev/governance/roles/architect-planner.md need tvofi's approving review, or one under mandate 6893738184 (issue 3394, scope all, to 2026-12-15T12:00Z).

`check_scopes.py --round N` refused round 11's start on every accepted evaluation card not yet merged, the finder-critical ones and the rest alike: 43 lines at the evaluation's approved head. The owner ruled only the finder-critical ones gate the start. This change makes that ruling a structured field and has the check read it:

- **`gates_finders`**, a boolean on each accepted card, written by the orchestrator beside `ruling`. 0018 section 5 already lets the orchestrator write the owner's ruling into a card; the field records what that ruling decided about finder gating, so it is part of the ruling. The evaluator's `finder_critical` prose stays as the evaluator's argument. It is not parsed, because four cards (E11-K-D4, D5, D9, D10) read "no as the card stands" while the owner's ruling on them is "All four before finders", so the prose does not decide. The check refuses an accepted card whose `gates_finders` is missing or not a boolean ("yes", 1 and null are all refused), so no card stops gating by accident. A rejected or deferred card needs no value.
- **At the finder start**, an accepted card with `gates_finders: false` that is not merged is not a gap. It is printed `PARALLEL <card> accepted, not merged, gates no finder: ...` because it is built while the finders run. Its unset `threshold`/`criterion` is not a gap either: it is built with the card. A non-gating card that is merged gets every check an accepted card gets (after the review, changes its file). A gating card is checked as before.
- **For P3**, `--round N --open-cards` prints `{round, ref, open_cards}` as JSON and exits. Run at the ref where P3 starts, it lists the non-gating accepted cards still unmerged then. It skips the scope verdict, so it is quick, and it exits 2 rather than printing an empty list when the evaluation is not tracked at the ref. Why a flag rather than parsing the PARALLEL lines: P3 runs at a different moment from the finder start, and the architect needs a parseable list without the 2-minute scope run.
- **The null reviewer** (E11-N-NULL-REVIEWER): `norm(ev.get("reviewer", ""))` turned JSON null into `none`, which is non-empty and so passed the two-seats rule. The evaluator and the reviewer must now each be a non-blank string before they are normalised. A null, absent, blank, `0` or `[]` value is refused for either seat.

Carry 0: this group's part-2 carry (body item 4ffa4b06, landed on the roster). It is built in part 2's own pull request (topic r11-pre-round-check-gate-p2), as the orchestrator ruled, not in this one.

## Approval

Not yet given. These policy edits are kept minimal and await tvofi's approving review at the head, or an approving review under mandate 6893738184 (issue 3394, scope all, to 2026-12-15T12:00Z), declared with the mandate id:
- 0018 section 5: the orchestrator's ruling field now includes `gates_finders` on an accepted card.
- 0018 section 6: Writes and Refuses name the field and the PARALLEL / `--open-cards` behaviour.
- architect-planner.md: Inputs now name `check_scopes.py --round <N> --open-cards` at P3's start. Step 3 places every open card in the plan once, like a finding. Paid within its token cap by dropping two duplicated phrases: "read-only on code", which "You do not write production code" already says, and the Method's "(sensitivity, tradeoff points)", which step 2 already says. The target's holdout bullet now points at step 7's list instead of repeating it.
- evaluator.md is unchanged: "never ... write a `ruling`" already covers a field that 0018 defines as part of the ruling.

## Head

fc369d59a88e5c613a445ab16f8c9a258a072674 (handoff/r11-pre-round-check-gate). It is the round-1 repair of fix review 3620 (blocked e1e3197e, tests-gap), on top of 9b6adde88a (the PR head: e1e3197e merged main, then the delivery row). Every figure under `### Repair` was measured at this commit. The figures above it were measured at 0d46ea8bd9, and they hold here because check_scopes.py's evaluation path is unchanged except for the `--open-cards` report.

### Repair (fix review 3620, round 1)

- **Block**: `--open-cards` printed `open_cards: []` and exited 0 on a record whose accepted cards carry no `gates_finders`, and nothing tested its output (M11 survived).
- **Fix**: `open_cards_report(rnd, tree, show, merged, anc, changed)` is the function main() prints. It lists the open non-gating cards and names each accepted card with no boolean `gates_finders`. It prints `UNMARKED <card>: accepted, no boolean gates_finders ...` to stderr, adds `unmarked_cards` to the JSON, and exits 1. The no-evaluation path still exits 2.
- **Tests**: the self-test drives `open_cards_report` through the same synthetic record as the other evaluation arms.
  - A non-gating unmerged card is listed: `({"round": 8, "open_cards": ["C1"], "unmarked_cards": []}, 0, [])`.
  - A complete record lists nothing, rc 0 (null control).
  - An accepted card with no `gates_finders`, or with `"no"`, is named, rc 1, whether merged or not.
  - The evaluation arms now hold 62 of 62.
- **Mutants**: `mutant_run.py --spec <scratch mutants3.json> --in-place --cmd "python3 <scratch evtest.py>"`. NULL survived and 4 of 4 were killed:
  - M11: `out` is dropped from the `evaluation_gaps` call, the reviewer's mutant.
  - M12: rc is always 0.
  - M13: no card is ever unmarked.
  - M14: only a missing value counts as unmarked, so `"no"` passes.
- **Live**: `python3 tools/audit/check_scopes.py --repo . --ref f6d35cf73f19a053c99e6627071984ff4190aa04 --round 11 --open-cards` exits 1 with `"open_cards": []` and 43 `unmarked_cards`, and prints 43 UNMARKED lines on stderr. The null control is the same evaluation with every card marked (above): no card is unmarked.
- **After the owner's values landed** (eval/r11 c6ce415b77, `gates_finders` written by the orchestrator from the rulings): the same command exits 0 with no UNMARKED line, `unmarked_cards: []`, and 12 `open_cards`. Those 12 are exactly the cards whose value is false: E11-GATE-REDS, E11-INJECTED, E11-N-GATE-CAUSE, E11-N-INSTRUMENT-YIELD, E11-N-INTAKE-BUILDER, E11-N-NULL-REVIEWER, E11-N-ROLE-CLAUSE, E11-N-RULE-YIELD, E11-R-WORKFLOWS, E11-S-SEATS, E11-SCORECARD and E11-T-product_green_floor.

## Mutation proof

Failing test first. The new self-test arms ran against the unchanged predicates, with only the parameter added: `evaluation_self_test` held 54 of 59. These five failed:
- a non-gating accepted card not merged passes and is listed beside
- a non-gating unmerged card's unset value is no gap, it builds with the card
- an accepted card with no boolean gates_finders is refused, in every shape
- an accepted card with no gates_finders is refused even unmerged, and never listed beside
- a null, absent or blank reviewer or evaluator is refused

At the head all 59 hold.

There is one mutant per new predicate, run with `python3 tools/audit/seat/mutant_run.py --spec <scratch mutants.json> --in-place --cmd "python3 <scratch evtest.py>"`. The driver calls `check_scopes.evaluation_self_test` at HEAD and exits 1 on any failing arm. NULL survived, and every mutant was killed:
- M1 `if not isinstance(gating, bool)` -> `if False`
- M2 -> `if gating is None` (accepts "yes")
- M3 `elif not gating and not (c and merged(c))` -> `elif not gating`
- M4 -> `elif False`
- M5 the `parallel.append(cid)` -> `pass`
- M6 the `continue` after it deleted
- M7 the old `norm(ev.get(k, ""))`

## Null control

The evaluation at origin/eval-review/r11-4 (f6d35cf73f) was run through `evaluation_gaps` at that ref, using a scratch driver that substitutes the card fields:
- **As written** (no `gates_finders`): 92 gaps. These are the 49 of today plus 43 "carries no boolean gates_finders", so an unrecorded card refuses and never passes silently.
- **Every accepted card `gates_finders: true`**: 49 gaps, 43 of them "accepted and not merged". This is line for line identical to `check_scopes.py --repo . --ref origin/eval-review/r11-4 --round 11` on main's code (compared as lists in the driver, printing "identical" only on equality), and 0 PARALLEL.
- **The proposed gating list** (31 true, 12 false; held outside this PR for the orchestrator to record): 36 gaps (31 not merged), 12 PARALLEL.

## Figures

- `python3 tools/audit/check_scopes.py --repo . --ref HEAD --self-test` at 0d46ea8bd9 printed `evaluation arms: 59/59 held; --round 1 rc=1; --open-cards rc=2` and `SELF-TEST passed (every perturbed scope refused)`, rc 0. The evaluation arms gained 10 (49 at main), plus one subprocess arm for `--open-cards`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and the one script is `tests/entities.py`. Locally, `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `1 of 2722 ENTITY CHECKS FAILED`. The one failure is `hb:positive_control`: on a loaded macOS host the py-spy sampler did not name a 600 ms spin in 3 tries (one sample `timed out after 0.5 seconds`). This diff touches neither the heartbeat nor tests/nightly_ha.py, so CI's run is the authority.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
<!-- figure-block: scope-line mb=b880dc914f3ba2590b7ce655d7419678b1c4968e head=fc369d59a88e5c613a445ab16f8c9a258a072674 -->
~~~text
MODE: SCOPED -- 1 script(s) run, 32 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

- Part 2, the group half of the P3 listing, is ruled by the orchestrator as this group's second pull request (topic r11-pre-round-check-gate-p2). It needs no finder start, only the end of the finders. It adds a boolean `gates_finders` on a roster group, read through roster_lib, linted by brief_lint and set by a roster_edit op. `--open-cards` gains `open_groups` (the open groups whose `gates_finders` is not true). A group with no `gates_finders` is listed and flagged `UNMARKED <group>`, and the listing exits non-zero while any open group is unmarked, so no group drops out of P3 unseen. Part 2 also builds the refusal in `audit-plan.js` of a plan that leaves an open card or group in no group. No roster group carries a structured finder-critical fact today, which is why part 1 lists cards only. Carry: R11-PRE-ROUND-CHECK-GATE


## Friction

none
