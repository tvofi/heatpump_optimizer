R11-ARCH-OBJECTIVE (owner item, tvofi 2026-11-16): decision 0018's objective ranks P3's work and the architecture score stays its floor. The build follows the approved design `design/R11-ARCH-OBJECTIVE` at 4c4835e3c708190f94813ff703ff5c990fdddb0e (`Design review: approve`, `design-verdict/R11-ARCH-OBJECTIVE` e3f5676a). No finder harness: this is an owner report.

- `tools/audit/seat/plan_audit.py` gains `objective-check` (the P3 check on `PLAN.json`'s `objective` block) and `settle`. Each refusal is a predicate on in-memory dicts; the command-line layer runs the plan SHA's `tools/plan/replan.py` twice as a subprocess (A: the pinned draft; B: A less every rank-2 group no rank-1 group reaches through `after`). `replan.py`, `roster_lib.py`, `ledger`, `snapshot` and `compare` are unchanged.
- `architect-planner.md` names the objective as the ranking and the target as its floor. `plan-review.md` step 5 now re-runs `objective-check` and attacks three ranks and three keyed effects. The grammar and every refusal live in `tools/audit/seat/instruments/plan_audit.py.md`.
- `.claude/workflows/audit-plan.js`: the moves reply returns the block, the read step settles the previous plan, the publish runs `objective-check --write` and then the check alone before any push, and a non-zero `objective_rc` stops P3.

Design verdict items, each built here (`Carry: R11-ARCH-OBJECTIVE` in the verdict):
- dr2-a: lead time is a group's finish less the pinned `--start` (`projection_record`). The self-test arm "lead time runs from the plan's start" pins it, with a fixture group carrying its own `start`.
- dr2-b: B is written under the draft's basename in a temporary directory (`run_projections`).
- dr2-c: `PROJECTION.json` holds the derived figures, the pin and `caps`, never the plans, `generated.version` or `closure_stamp`, and the re-run uses the plan SHA's `replan.py` (`_worktree(ref)`). Arm: "the same inputs under another VERSION give the same record". Real run: below.
- dr2-d: the block in the real run is a fixture, not a plan. The refused real run is below.
- dr2-f: no `tests/closure.py` edit is owed. `dev/audit/` is already on `INERT`, and `closure.is_inert` returns True for `dev/audit/rounds/round11/PLAN/PROJECTION.json` and for `PLAN.json` (command in Figures).
- dr2-g: an open group that projection A schedules and the plan gives no rank refuses (`UNRANKED open group`). A done group is kept in B unranked. The guide states both.
- dr2-e was dismissed by the verdict. `dev/audit/README.md` takes one cell edit on the P3 row.

Alternatives not taken, as the design rules them out (section 4): hours authored in the block; rank as a `dispatch_tier` input; importing `replan.py` (that would move the `p3-move-ledger-and` self-test closure); one weighted number; per-group aggregate deltas; predictions in the roster group. Within the build:
- `production` is derived by loading `machinery_ratchet.is_product` at the plan SHA inside the command-line path, never imported at module level, so the self-test closure is unchanged.
- `BETTER` (0018 section 2's direction column) encodes a design choice: `objective.json` carries no direction. The arm "BETTER names exactly objective.json's terms" refuses the day a term is added without one.

## Review round 1 (Fix review: blocked 2eee862d2d61b2fe2431c979048360d1b4392cfa), each item answered

1. **Every rank-1 key now names a registered id.** One table, `REGISTERED`, maps `escapes`, `cards` and `classes` to a register; `derived_rank` reads its keys and `check_block` refuses an id its register lacks (`UNKNOWN card|escape|class <group> <id>`), so a rank-1 key cannot be added without a check. Cards: `check_scopes.py --open-cards --round N` at the plan SHA (`open_cards`). Escapes: the `in` rows of the escapes ledger the baseline record names (`terms.escapes.by_hand.ledger`, `escape_rows`). Failing arms first: "a rank-1 `cards` id no register holds is refused by name" and the `escapes` twin both fail with the old loop restored (mutant f1 below). The real-run attack `fake-card` (the reviewer's) now refuses every relabelled group, and `fake-escape` does the same.
2. **The baseline is derived.** `baseline_refusals` refuses a `baseline.record` other than `BASELINE` for round N-1, a record whose `round` is not N-1, and a record that is not one blob at the plan SHA, at `baseline.tree` and at the merge base of the plan SHA and `--main` (default `origin/main`). The check reads the record at the fixed path, never at the plan's chosen one. Both attacks refuse: `doctored-baseline` (the reviewer's) and `doctored-baseline-in-place` (the doctored copy written over the real path on the plan's branch). `settle` reads the same derived path.
3. **Each settlement status choice is pinned by value.** New arms: an `up`/`down` prediction met by the opposite move is MISSED; the perturbation arm now also asserts the flipped line's status (HELD to MISSED), not only that it differs; `hold` is MISSED on a worse move and HELD on a tie and on a credited better move; `undecided` stays UNDECIDED on a read term; an unread band is UNDECIDED with its detail; `examined_by` is UNDECIDED without rows, HELD and MISSED with them, and only for a rank-2 group; `escapes` and `classes` keys settle at the next close on their own rows; the next close prints no term line; `injected` only for a production group; the band widths and the share's four-place read; the rank-edge guards (`SHAPE` on a non-object entry, rank-2 after rank-2 and rank-1 after rank-1 owe no edge); `kept_in_floor` with a rank-2 to rank-2 edge; lead time over production groups only. `check-wave-script.mjs` gains "and the moves schema requires the objective block" (reviewer m3: `254 passed, 1 failed` with `'objective'` dropped, `255 passed, 0 failed` restored).
4. **A ranked done group is refused by name, and B keeps every done group.** `kept_in_floor` keeps a group projection A marks `done` whatever its rank, so `replan.py` no longer refuses B, and `check_block` prints `RANKED done group <name>: a done group is kept unranked, and B keeps it`. The reviewer's `done-ranked` fixture now ends in those named refusals, rc 1, with no `replan.py` refusal.

Alternatives not taken: escapes validated against a hand-copied id list in `objective.json` (a second register for the same ledger); `baseline.tree` kept as the read ref (the attack's own route); `objective-check` refusing a done group before projecting (the projections would still crash on the reviewer's fixture first).

## Head

`24f6fe48b565131b596bf420a46269136e91208a`, merge base `ada9da5c7bf542b8cdedb2d5fbe878edd1b3a8ae`, measured with `origin/main` at 8f39313a44a4baec18b239ba925f6e164eb26bd2, 2026-11-17T11:54Z.

## Mutation proof

Driver: the reviewer's `driver-mut.py` (`review/3703` 024f41cf, `evidence/driver-mut.py`), patterns re-anchored where this diff moved them (r06 now mutates the `REGISTERED` loop's predicate, b13 the new `kept_in_floor` return), plus nine reverts of this fix, each run against `python3 tools/audit/seat/plan_audit.py --self-test`: **59 of 59 KILLED** (b01-b21, r01-r29, f1-f9), `survivors: []`. The reverts:

| mutant | edit | killed by |
|---|---|---|
| f1 classes only | the `REGISTERED` loop reads `classes` alone | "a rank-1 `cards` id no register holds is refused by name" and the `escapes` twin |
| f2 cards unread | `derived_rank` reads `escapes`/`classes` only | "a card alone makes a group rank 1" |
| f3 baseline path | `if got != want:` -> `if False:` | "a baseline path the plan chose is refused" |
| f4 baseline round | round predicate -> `False` | "a record of another round is refused" |
| f5 baseline blobs | blob predicate -> `False` | "a record edited on the plan's branch, or at its tree, is refused" |
| f6 done ranked | `elif g.get("done") and name in entries:` -> `elif False:` | "a ranked done group is refused by name" |
| f7 floor keeps done | `e.get("done") or` removed | "and the floor keeps a done group whatever its rank" |
| f8 escape ruling | `and row[r] == "in"` removed | "the escapes ledger yields its `in` rows' groups" |
| f9 escape header | header test reduced to `if not rows:` | the same arm |

In-tree driver over every added line: `python3 tools/audit/seat/mutant_run.py --diff ada9da5c7bf542b8cdedb2d5fbe878edd1b3a8ae...HEAD --path tools/audit/seat/plan_audit.py --max-mutants 2000 --in-place --cmd "python3 tools/audit/seat/plan_audit.py --self-test"`. Every survivor the verdict names in `check_block`, `term_reading`, `moved` and `settle` (its lines 620 to 782) is now killed. What survives above the command-line layer is under `## Unpinned sites`.

`audit-plan.js`: the reviewer's m1 to m4 re-run with `node tools/policy/check-wave-script.mjs`: each prints `254 passed, 1 failed` on its named arm (m3 now on "and the moves schema requires the objective block"); restored, `255 passed, 0 failed`.

## Unpinned sites

- `moved`'s `return "up" if now > was else "down"` (CMP_BOUND `>=`): equivalent. It runs only when `abs(now - was) > width >= 0`, so `now != was` there.
- `OBJECTIVE_CONFIG` and `BUGCLASSES` (STMT_DEL): read only by the command-line layer.
- The command-line layer, `_show` through `objective_settle` (run by no in-tree check, as the design's "one real run, outside the self-test" allows): disposed by the real runs in `## Figures`, which drive `open_cards`, the derived baseline read, `run_projections` and the done-group path to their named refusals and to the PASS twin. `_blob` is pinned in the self-test ("a blob reads off the checkout, and an absent path reads None"). The rest of the driver's survivors are the self-test's own lines and `main`.

## Null control

- Every planted plan keeps its passing twin: "a plan with a sound objective block passes the P3 check", "an escape row ruled `in` makes a group rank 1", "the baseline is the previous round's record, one blob everywhere: passes".
- Real run: the base fixture (below) prints `OBJECTIVE PASS`, rc 0; the `real-escape-control` twin, one group ranked 1 by a real `in` row of the round-10 ledger, prints `OBJECTIVE PASS`, rc 0, `dropped 42` (one fewer than 43, the group now kept as rank 1). So the escape refusal is the id, not the key.
- At the merge base `objective-check` is argparse's "invalid choice", so every arm is red there.

## Figures

- `python3 tools/audit/seat/plan_audit.py --self-test`: `plan_audit self-test: 112 checks, 0 failed` (2eee862d: 76).
- `node tools/policy/check-wave-script.mjs`: `255 passed, 0 failed`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff ada9da5c7bf542b8cdedb2d5fbe878edd1b3a8ae HEAD`: `Architecture score: dS +0.0000 NULL`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s)`; `--budgets` rc 0, `architect-planner.md` 89/89 lines and 1325/1325 words, unchanged by this round.
- Scope: `python3 tests/closure.py select --diff ada9da5c7bf542b8cdedb2d5fbe878edd1b3a8ae`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`; `scope.run` names `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2725 ENTITY CHECKS PASSED`. The `run_always` lines: `tests/closure.py selftest` prints `ALL 118 closure shrink pins PASSED`; `tests/env_drift.py --claims-only` exits 1 with `RECORD PR CLAIMS: three-dot touches neither card nor solver fixtures, so both claim lists must be empty` (see `## Red checks`).
- Real run, a fixture off this head (the reviewer's `driver-mkfix.py`, with the open groups only and the card `E11-GATE-REDS` from `check_scopes.py --open-cards --round 11`, roster `wave-r11-groups.json` from `handoff/audit-r10-roster` cfafa28d3edf8169db080d1cccd7970e3fa8bf41). Command: `python3 tools/audit/seat/plan_audit.py objective-check --ref <fixture> --plan dev/audit/rounds/round11/PLAN/PLAN.json --register dev/audit/rounds/round10/JUDGE.json --main origin/main`, after `--write` and a commit of the record.
  - base: `projection A: critical path 88.7 h, wall 90.7 h`, `dropped 43`, `OBJECTIVE PASS`, rc 0 (the reviewer's figures at 2eee862d).
  - `fake-card` (every rank-2 group relabelled `{"rank": 1, "cards": ["NO-SUCH-CARD"]}`, edges emptied): `FAIL UNKNOWN card <group> NO-SUCH-CARD: not in the round's open cards, check_scopes.py --open-cards` per group, rc 1. At 2eee862d: `OBJECTIVE PASS`, rc 0.
  - `fake-escape`, the same with `escapes`: `FAIL UNKNOWN escape <group> NO-SUCH-ROW`, rc 1.
  - `doctored-baseline` (the reviewer's): `FAIL BASELINE 'dev/audit/rounds/round11/PLAN/doctored.json': the baseline is the previous round's record, dev/audit/yardstick/round10/OBJECTIVE.json` and the 12 `NO-READ` refusals, rc 1. At 2eee862d: `OBJECTIVE PASS`.
  - `doctored-baseline-in-place` (the same values written over the real record on the plan's branch): `FAIL BASELINE edited: ... is not one blob at the plan SHA, its tree and main's merge base`, rc 1.
  - `done-ranked` (every roster group ranked, done ones too): `FAIL RANKED done group R10-COP-LEARNER-DRAW-FLOOR` among the named lines, rc 1, no `replan.py` refusal. At 2eee862d: `replan.py refused (rc=2): ... after-edge names no group`.
<!-- figure-block: scope-line mb=ada9da5c7bf542b8cdedb2d5fbe878edd1b3a8ae head=24f6fe48b565131b596bf420a46269136e91208a -->
~~~text
MODE: SCOPED -- 1 script(s) run, 32 scoped out.
~~~
<!-- /figure-block -->

prepr: passed rc=0 at 24f6fe48b565131b596bf420a46269136e91208a (`PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh`, `MUTANT_CMD="python3 tools/audit/seat/plan_audit.py --self-test" MUTANT_IN_PLACE=1`).

## Architecture score

Architecture score: dS +0.0000 NULL

## Raise justification

`dev/governance/config/policy_budgets.json`: `architect-planner.md` lines 85 -> 89 and words 1261 -> 1325; `plan-review.md` lines 24 -> 27 and words 304 -> 360. Raised under mandate 6893738184 (scope all, until 2026-12-15T12:00Z). The reason is in the commit message.

Payments tried: four, each below with its disposition.
- Every rule moved out of the contracts into the instrument's refusals and its guide (design note, "Pay the caps first"). The contracts name only the command, the floor relation and the four review attacks. This is taken: it is why the architect-planner addition is 4 lines, not the 8 of the first draft (93 lines measured, then 89).
- `plan-review.md`'s time check folded into the new step, since `objective-check` is the projection re-run, rather than added beside it. Taken: it saves 2 lines over a separate step.
- Deleting existing contract prose. Not taken: no sentence in either contract is superseded by this change. Step 8's "Project it with the plan model" still binds the roster projection the template is read against.
- A reflow of the `**Method:**` lines. Not taken: it moves a count and improves nothing (`fixer.md` step 17).

Architecture score: dS +0.0000 NULL

## Approval

Pending. This changes what the architect and the plan reviewer must do (`architect-planner.md`, `plan-review.md`, `dev/audit/README.md`'s P3 row) and raises two contract caps. It merges on the owner's approving review at the head, or an approval under mandate 6893738184 (scope all, until 2026-12-15T12:00Z), as the roster group's `owner_gate: policy` states.

## Red checks

Every red check run on a commit of this branch, by name (read at 2eee862d with `pull_request_read get_check_runs`, 2026-11-17T12:10Z):

- `budget-raise-gate / budget-raise-gate`: red at 2eee862d by design while the raise in `dev/governance/config/policy_budgets.json` has no approving review at the head (decision 0013); it clears on the approval `## Raise justification` asks for. Cheaper detector: none exists; the gate is the approval it waits for, and `node tools/policy/policy_lint.mjs --budgets` measured the raise locally before the push.
- `gate`: red at 2eee862d only because it aggregates `budget-raise-gate / budget-raise-gate` (`merge_train.py classify --pr 3703`: `APPROVAL-OWED`, the verdict's `ev/classify.txt`). Cheaper detector: none beyond the one above.
- `governance / instrument-self-tests`: red at 2eee862d, inherited from main (step "Refuse a self-test read set the committed table misses": `tools/ci/selftest_closures.json` misses reads added by recent merges; a re-record hotfix is in flight). Outside the `owed-reds` set; classify printed no INTRODUCED line at 2eee862d. Not repaired here.
- `tests / nightly-status`: red at 2eee862d; it grades `main`'s nightly lane, is outside the `owed-reds` set, and this diff does not touch its reporter inputs. Cheaper detector: none; the orchestrator's lane.
- `governance / env-matrix` and `governance / policy-docs`: red on an earlier commit of this branch, `success` at 2eee862d (run 44025584323). Neither is in the `owed-reds` set. Cheaper detector for `governance / policy-docs`: `node tools/policy/policy_lint.mjs`, about a minute, run before this push (`TOTAL: 0 error(s)`); for `governance / env-matrix`: none runs locally, CI is its only runner here.
- INHERITED CLAIMS (`tests/env_drift.py --claims-only` exits 1 locally): both claim files are byte-identical to the merge base ada9da5c, whose lists name `cycling_cost` and `everything_on`; `origin/main` has since emptied them. This branch claims nothing (`git diff ada9da5c7bf542b8cdedb2d5fbe878edd1b3a8ae...HEAD -- tests/golden` is empty), so the red is main's, repaired by the train's merge, not here (`fixer.md` step 5).
- Code-scanning alerts were not read by `prepr.sh` (HTTP 403 on `code-scanning/analyses`); `pr-contract` reads them and fails closed.

## Forward-carry

- Carry 0 (the 0018 record shape). The settlement reads keyed rows from an objective record's `keyed.<kind>` (`escapes` rows by `key`, `classes` by `class`, `injected` by `group`, `rereport` by `finding`, `examined_by` by `group`). `dev/audit/yardstick/round10/OBJECTIVE.json` has none, so those lines settle UNDECIDED: the self-test arm "at the next close they settle on keyed rows, and with none they are UNDECIDED". Decision 0018 section 6's record shape would have to name those rows, or the settlement credits nothing. The approved design leaves 0018 unedited and routes "the roster's files name the 0018 record" to the orchestrator (design verdict, `decision: orchestrator`). No live group after this one can receive it: `carry_audit.py check --pr-group R11-ARCH-OBJECTIVE` prints "valid targets: none live after R11-ARCH-OBJECTIVE". So it stays with this group, pending that ruling. Carry: R11-ARCH-OBJECTIVE
- `plan_audit.py` has no `.github/CODEOWNERS` line while 0018 section 5 calls an enumerator code-owned. Carry: dismissed: owner decision, reported in the designer's result

## Friction

none
