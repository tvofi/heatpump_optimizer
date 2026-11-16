Group: R11-PRE-ROUND-CHECK-GATE (topic r11-pre-round-check-gate)
Cards: E11-N-NULL-REVIEWER (accepted by tvofi, "Accept both (Recommended)"); tvofi's 2026-11-15 ruling "Only the finder critical are required for finder start", with his 14:00Z correction that what is still open when the finders finish goes to the architect and planner.
Code-owned and policy: tools/audit/check_scopes.py, dev/governance/decisions/0018-objective-function.md (sections 5 and 6) and dev/governance/roles/architect-planner.md need tvofi's approving review, or one under mandate 6893738184 (issue 3394, scope all, to 2026-12-15T12:00Z).

`check_scopes.py --round N` refused round 11's start on every accepted evaluation card not yet merged, the finder-critical ones and the rest alike: 43 lines at the evaluation's approved head. The owner ruled only the finder-critical ones gate the start. This change makes that ruling a structured field and has the check read it:

- **`gates_finders`**, a boolean on each accepted card, written by the orchestrator beside `ruling`. 0018 section 5 already lets the orchestrator write the owner's ruling into a card; the field records what that ruling decided about finder gating, so it is part of the ruling. The evaluator's `finder_critical` prose stays as the evaluator's argument. It is not parsed, because four cards (E11-K-D4, D5, D9, D10) read "no as the card stands" while the owner's ruling on them is "All four before finders", so the prose does not decide. The check refuses an accepted card whose `gates_finders` is missing or not a boolean ("yes", 1 and null are all refused), so no card stops gating by accident. A rejected or deferred card needs no value.
- **At the finder start**, an accepted card with `gates_finders: false` that is not merged is not a gap. It is printed `PARALLEL <card> accepted, not merged, gates no finder: ...` because it is built while the finders run. Its unset `threshold`/`criterion` is not a gap either: it is built with the card. A non-gating card that is merged gets every check an accepted card gets (after the review, changes its file). A gating card is checked as before.
- **For P3**, `--round N --open-cards` prints `{round, open_cards, unmarked_cards, ref}` as JSON and exits, rc 1 with an `UNMARKED <card>` line on stderr for each accepted card with no boolean `gates_finders` (see `### Repair`). Run at the ref where P3 starts, it lists the non-gating accepted cards still unmerged then. It skips the scope verdict, so it is quick, and it exits 2 rather than printing an empty list when the evaluation is not tracked at the ref. Why a flag rather than parsing the PARALLEL lines: P3 runs at a different moment from the finder start, and the architect needs a parseable list without the 2-minute scope run.
- **The null reviewer** (E11-N-NULL-REVIEWER): `norm(ev.get("reviewer", ""))` turned JSON null into `none`, which is non-empty and so passed the two-seats rule. The evaluator and the reviewer must now each be a non-blank string before they are normalised. A null, absent, blank, `0` or `[]` value is refused for either seat.

Carry 0: this group's part-2 carry (body item 4ffa4b06, landed on the roster). It is built in part 2's own pull request (topic r11-pre-round-check-gate-p2), as the orchestrator ruled, not in this one.

## Approval

Not yet given. These policy edits are kept minimal and await tvofi's approving review at the head, or an approving review under mandate 6893738184 (issue 3394, scope all, to 2026-12-15T12:00Z), declared with the mandate id:
- 0018 section 5: the orchestrator's ruling field now includes `gates_finders` on an accepted card.
- 0018 section 6: Writes and Refuses name the field and the PARALLEL / `--open-cards` behaviour.
- architect-planner.md: Inputs now name `check_scopes.py --round <N> --open-cards` at P3's start. Step 3 places every open card in the plan once, like a finding. Paid within its token cap by dropping two duplicated phrases: "read-only on code", which "You do not write production code" already says, and the Method's "(sensitivity, tradeoff points)", which step 2 already says. The target's holdout bullet now points at step 7's list instead of repeating it.
- evaluator.md is unchanged: "never ... write a `ruling`" already covers a field that 0018 defines as part of the ruling.

## Head

8ad98806e4c824491455b50f05f16eaa09ac7ac9 (handoff/r11-pre-round-check-gate), the merge of the PR branch origin/fix/r11-pre-round-check-gate (691aa86b1e, the relay's tree-neutral merges of 07f969bf3d and fc369d59) into 89f08b6d46; its tree is 89f08b6d46's, byte for byte (`git rev-parse HEAD^{tree}` equal before and after the merge), so every figure taken at 89f08b6d46 describes it. 89f08b6d46 is one commit on 07f969bf3d (the round-2 repair of fix review 3620): the grader stubs part 2 needs, moved here by the orchestrator's route (a) for part 2's bootstrap question. The diff since 07f969bf3d is `tools/policy/check-wave-script.mjs` only, test code, so every figure under the two `### Repair` sections still describes this head: none of them reads that file.

### Delta: the P3 grader stubs for part 2 (#3633)

- **Why**: part 2 (#3633, ec058220b5) restores `audit-plan.js`'s refusal of a plan that leaves an open card or group in no group. main's `check-wave-script.mjs` drives `audit-plan.js` with `plan/read` and `plan/moves` stubs that carry no `--open-cards` listing, so it cannot grade that `audit-plan.js`: `ci_predict.py` reads that as a bootstrap (the base's grader refuses the head's workflow).
- **What moved**: exactly the stub hunks of `git diff origin/main ec058220b5 -- tools/policy/check-wave-script.mjs` (8 added, 4 removed lines): the `OPEN` listing (`open`: one open card E11-X, one open group R11-G, none unmarked; `open_rc` 0) spread into the default `plan/read` stub and the two triage `pthrows` reads; and `MOVES()`, the default `plan/moves` stub, which accounts for both items (E11-X in group A's `open_items`, R11-G in `dropped` with a reason). The refusal's own tests (the five new `pthrows`, the kept-group null control, the `--open-cards` read-prompt assertion) stay in part 2: they fail against an `audit-plan.js` without the refusal. Compared line for line: the delta's `+`/`-` lines are a subset of that diff's, and the remainder is exactly those seven tests.
- **Failing first** (the null control): main's grader, unchanged, against ec058220b5's `audit-plan.js` failed 7: the six `pthrows` named `a triage that drops a verified finding stops P3`, `a triage that keeps one finding twice stops P3`, `a group with no move entry stops P3`, `a publish that is not a 40-hex commit stops P3`, `a reviewer answering for another tree stops P3`, `a recorded verdict that is not a 40-hex commit stops P3`, and `the P3 plan workflow threw`, each with `check_scopes.py --open-cards exited undefined, not 0`.
- **Mutation**: the delta adds no `.py` line, so prepr's step 6d draws no mutant from it. The mutant that matters is the delta's removal, which is the null control above: 7 failures.

### Repair (fix review 3620, round 2)

- **Block**: main()'s `sys.exit(rc)` and its `print(line, file=sys.stderr)` were reached by no arm; M17 (exit 0) and M18 (no UNMARKED line) survived the full self-test.
- **Fix** (the reviewer's first option, at the command line): `open_cards_cli()` builds a scratch git repository in a temp directory with `tests/throwaway_git.py`'s `throwaway_git_init` (7248e2b3's raw `git init` was refused by prepr.sh's throwaway-git step; 07f969bf runs the repository and the subprocess under its environment) with two commits of a round-8 record (minimal objective and round-7 record) and runs `check_scopes.py --repo <tmp> --ref <commit> --round 8 --open-cards` as a subprocess on each. The two records differ only in `gates_finders` on C2 and C3: booleans in the first; absent on C2 and the string `"true"` on C3 in the second. C1 is accepted, `gates_finders: false`, unmerged; C4 is rejected.
- **Arms** (two, in `--self-test`'s coverage table):
  - null control: the all-boolean record exits 0, its stderr carries no `UNMARKED`, and its JSON `open_cards` is `["C1"]`;
  - the unmarked record exits 1, the stderr `UNMARKED` lines are exactly `UNMARKED C2`, `UNMARKED C3` (text before the colon, in order), and its JSON `unmarked_cards` is `["C2", "C3"]`.
- Rejected: moving main()'s print-and-exit into a function the self-test calls; the brief requires the CLI run as a subprocess, and a function arm would leave the `sys.exit` line itself unpinned.

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

### Round 2 (fix review 3620, at 07f969bf3d)

The reviewer's driver (`verdict/3620:evidence/mut_driver.py`), with M20 and M21 added and M11, M13-M15 (judged in round 1) dropped: each mutant is applied to `tools/audit/check_scopes.py` in place, `python3 tools/audit/check_scopes.py --repo . --ref HEAD --self-test` is run whole, and a mutant is KILLED on a non-zero rc. The file was compared byte for byte with its copy afterwards (`cmp`, printed RESTORED).
- NULL: rc 0, SURVIVED, `marked rc=0, unmarked rc=1 ['UNMARKED C2', 'UNMARKED C3']`.
- M17 main's `sys.exit(rc)` -> `sys.exit(0)`: KILLED (the CLI's unmarked rc reads 0).
- M18 main's `print(line, file=sys.stderr)` -> `pass`: KILLED (no UNMARKED line).
- M20 that print -> `print(line)` (to stdout): KILLED (no UNMARKED line on stderr, stdout no longer JSON).
- M21 main's `sys.exit(rc)` -> `sys.exit(1)`: KILLED by the null control alone (marked rc reads 1).
- M12 and M16 (round 1's function mutants): KILLED, now by the CLI arms as well.
- M19 `"open_cards": sorted(out)` -> unsorted: SURVIVED, an equivalent mutant: `evaluation_gaps` appends to `parallel` while iterating `sorted(cards.items())`, so `out` is already sorted and the `sorted()` is a no-op on every input. No arm can kill it; the reviewer's follow-up is disposed here rather than carried.

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

- Delta, the grader matrix. Command: `node tools/policy/check-wave-script.mjs` from the tree root, with `.claude/workflows/audit-plan.js` replaced by `git show <rev>:.claude/workflows/audit-plan.js` and restored after (`git checkout`); the result line is the script's `N passed, M failed` and its rc. Every run also prints `FAIL (probe, expected) threw: deliberate`, the script's own block-harness probe, counted in neither number.
  - main 6aa7ddc712 grader, unchanged, x ec058220b5 `audit-plan.js`: `209 passed, 7 failed`, rc 1 (the null control).
  - main grader unchanged x 416280f5 `audit-plan.js` (blob 0a06aa738b, the same as main's and this head's): `223 passed, 0 failed`, rc 0.
  - main grader plus these stubs x ec058220b5: `223 passed, 0 failed`, rc 0; x 416280f5: `223 passed, 0 failed`, rc 0.
  - this head's grader x ec058220b5: `223 passed, 0 failed`, rc 0; x 416280f5: `223 passed, 0 failed`, rc 0.
  - The brief's 230/230 is part 2's grader: ec058220b5's `check-wave-script.mjs` x ec058220b5's `audit-plan.js`, on main's tree, printed `230 passed, 0 failed`. With the stubs alone the count is 223 at both revisions; the seven tests left in part 2 are the difference.
- Round 2, at 07f969bf3d: `python3 tools/audit/check_scopes.py --repo . --ref HEAD --self-test` printed `evaluation arms: 62/62 held; --round 1 rc=1; --open-cards rc=2, marked rc=0, unmarked rc=1 ['UNMARKED C2', 'UNMARKED C3']` and `SELF-TEST passed (every perturbed scope refused)`.
- Round 2 scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, the script `tests/entities.py`, and `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `ALL 2723 ENTITY CHECKS PASSED`, rc 0; `git merge-tree --write-tree origin/main HEAD` reported no conflict; `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

- `python3 tools/audit/check_scopes.py --repo . --ref HEAD --self-test` at 0d46ea8bd9 printed `evaluation arms: 59/59 held; --round 1 rc=1; --open-cards rc=2` and `SELF-TEST passed (every perturbed scope refused)`, rc 0. The evaluation arms gained 10 (49 at main), plus one subprocess arm for `--open-cards`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and the one script is `tests/entities.py`. Locally, `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `1 of 2722 ENTITY CHECKS FAILED`. The one failure is `hb:positive_control`: on a loaded macOS host the py-spy sampler did not name a 600 ms spin in 3 tries (one sample `timed out after 0.5 seconds`). This diff touches neither the heartbeat nor tests/nightly_ha.py, so CI's run is the authority.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
<!-- figure-block: scope-line mb=b880dc914f3ba2590b7ce655d7419678b1c4968e head=8ad98806e4c824491455b50f05f16eaa09ac7ac9 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Unpinned sites

`prepr.sh` step 6d, run at 07f969bf3d with `MUTANT_IN_PLACE=1 MUTANT_CMD="python3 tools/audit/check_scopes.py --repo . --ref HEAD --self-test"`, drew the diff's added lines against b880dc914f and printed 7 SURVIVED lines. Every one is a constant in self-test fixture code or a no-op, swapped to a value in the same class, so no check can tell the two apart; none is a production line of `--open-cards`:
- `tools/audit/check_scopes.py:444 CONST_SWAP` (`open_cards_cli`, C1's `merged` `"0" * 40` -> `* 41`): equivalent; any sha the scratch repository lacks leaves C1 unmerged.
- `tools/audit/check_scopes.py:458 CONST_SWAP` (the scratch record's `"round": 8` -> 9): equivalent for what `--open-cards` prints; by design it reports `open_cards` and `unmarked_cards`, never `evaluation_gaps`' gap lines, so a round mismatch changes neither stream nor the exit code.
- `tools/audit/check_scopes.py:472 RETURN_DEL` (`json_or_none`'s `return None` -> `pass`): equivalent; the function returns None either way.
- `tools/audit/check_scopes.py:669 CONST_SWAP` (round 1, "a non-gating merged card is checked as any accepted card": `gates_finders=False` -> `True`): equivalent by the property the arm states; a merged card is checked identically whether it gates or not.
- `tools/audit/check_scopes.py:672 CONST_SWAP` (round 1, the refused spellings `0` -> `1`): equivalent; `1` is as much a non-boolean as `0`, and it is already in the list.
- `tools/audit/check_scopes.py:685 CONST_SWAP` (round 1, "refused even unmerged", `lambda sha: True` -> `False`): equivalent; the arm states that merged and unmerged give the same refusal, so swapping one input for the other leaves that refusal unchanged.
- `tools/audit/check_scopes.py:688 CONST_SWAP` (round 1, the null-reviewer values `0` -> `1`): equivalent; `1` is a non-string like `0` and is refused the same way.

## Red checks

none

## Forward-carry

- Part 2, the group half of the P3 listing, is ruled by the orchestrator as this group's second pull request (topic r11-pre-round-check-gate-p2). It needs no finder start, only the end of the finders. It adds a boolean `gates_finders` on a roster group, read through roster_lib, linted by brief_lint and set by a roster_edit op. `--open-cards` gains `open_groups` (the open groups whose `gates_finders` is not true). A group with no `gates_finders` is listed and flagged `UNMARKED <group>`, and the listing exits non-zero while any open group is unmarked, so no group drops out of P3 unseen. Part 2 also builds the refusal in `audit-plan.js` of a plan that leaves an open card or group in no group. No roster group carries a structured finder-critical fact today, which is why part 1 lists cards only. Carry: R11-PRE-ROUND-CHECK-GATE


## Friction

none
