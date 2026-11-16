Design review: approve 4c4835e3c708190f94813ff703ff5c990fdddb0e

Design reviewer seat, round 2. Note judged at 4c4835e3c708190f94813ff703ff5c990fdddb0e against the round-1 verdict at 6ec87d8b840dfad6711a36b8edf52e82ef37447a (`git diff 588a773f..4c4835e3`, one file). Tree read at 5854e4f69e361d841d7590ae0f868eea6758655f; `git diff c82f014a 5854e4f6` over the note's hot and read files prints nothing, so the note's base and this one agree on every file below. Nothing rerun.

## Round-1 points

1. `architecture-unsound` (hours, chain, floor cost): answered. design.md:27-32 and :60-81 author no hour; `tools/plan/replan.py` stays the owner and is called as a subprocess. Checked at the base: `--roster-ref`, `--roster-path`, `--roster-file`, `--durations` and `--start` exist (`parse_args`, lines 3329-3337); the plan carries `generated.roster_blob`, `binding.critical_path_hours`, `summary.wall_hours`, `summary.closure` and per-group `after`, `start`, `finish`; a `--roster-file` plan pins no blob (`load_roster` returns ""). With no `--live-refs`, `--in-flight` or `--since-tag`, `main` reads nothing but the roster, the durations file, `VERSION` and the caps, and `build_plan` uses `roster_path` in refusal text only, so projection A against B differs by the roster alone. `plan_audit.py`'s `run_end_to_end` already runs `score.py` this way (line 116), and step `p3-move-ledger-and` of `tools/ci/selftest_closures.json` measures two files and no git read, which in-memory arms keep.
2. `class-open` (order rule, sibling sites): answered. design.md:83-88 states the rule on `after` edges of projection A and leaves `dispatch_tier` and `dispatch_key` untouched; section 5's grep now names both symbols and gives `replan.py` and `roster_lib.py` a read-only disposition. The reduced roster is closed under `after`: a kept group's predecessors are reached by the same rank-1 group, so `dependency_graph`'s "after-edge names no group" refusal cannot fire on B.
3. `class-open` (hot files): answered. Re-counted: 16 other open `design/R11-*` refs. My grep of each note for this note's files matches design.md:179-187 with one addition, carried below (dr2-e).

## Decisions, routed (no revise point)

- decision: owner — design.md:55-56, unchanged from round 1: +22.7 stays a commitment while `owner_criteria.D7` is decision 0015's path. If the owner rules the score a floor only, section 2 step 3 and the rank-2 class change with the 0015 edit.
- decision: orchestrator — design.md:20, unchanged from round 1: the roster group's `files` names the 0018 record, which this note does not edit.
- decision: orchestrator — design.md:15: rank reaches the plan through `after` edges and a priced delay only, against the starting position "the objective ranks the work". The note's reason (three owner rulings fix the tiers) holds in the tree at `replan.py:448-491`.

## Checked and held

- Seam: one owner per concern. The check and the settlement are new subcommands of `plan_audit.py`, the only machine reader of `PLAN.json`; no write path into the roster, `replan.py` or `objective.json`.
- Shape: every changed behaviour is the owner item's. No arm relies on a grader changed in the same pull request: the new check refuses a plan with no block, and `ledger`, `snapshot` and `compare` are invariant (design.md:107-108).
- 0018 section 2 (lines 222-226) says rules 2 to 4 rank nothing while a layer-1 term is NO-READ; design.md:47-52 orders by the layer-1 key only, which removes round 1's second owner decision.
- Evidence: each row of design.md:146-160 is red today (neither subcommand exists) and has a passing twin; the three rows added for point 1 (authored time, stale pin, projection differs) are checkable on dicts.
- Headroom: `policy_lint.mjs --budgets` prints `plan-review.md` at both caps and `architect-planner.md` one under each, so design.md:188-190's raise route stands.
- Cost: nine files edited, two read; fits L.

## Notes for the fixer

- design.md:76-77 computes `lead_time` as a group's finish less its start. 0018's row (line 198) starts the clock at the roster entry "because a seat chooses its first commit". Project it as finish less `generated.start`, or the prediction and the record it settles against use two clocks. Carry: R11-ARCH-OBJECTIVE (item dr2-a)
- Projection B's file must be named as the round's roster is (`roster_lib.roster_round` refuses any other basename, and `read_legacy` keys the cut-over by it). Write it in a temporary directory under that name. Carry: R11-ARCH-OBJECTIVE (item dr2-b)
- `replan.py` writes `generated.version` and `summary.closure_stamp` from the checkout's `VERSION`, and its caps from `DEFAULT_CAPS`. The projection record holds the derived figures and the pin (roster blob, durations blob, start, caps), never the two plans, and the re-run uses `replan.py` at the plan SHA; otherwise a stamp or a later edit of the model refuses a plan that did not change. Add the arm: same inputs under another `VERSION` pass. Carry: R11-ARCH-OBJECTIVE (item dr2-c)
- The subprocess layer is the one path no in-memory arm drives. The real run of design.md:166-167 needs a block written for the round-10 roster, which has none; say in the body that the block is a fixture, and include one refused real run (a pin edited by one character). Carry: R11-ARCH-OBJECTIVE (item dr2-d)
- `design/R11-PRE-PRODUCT-READS` (8daf1183, its line 110) and `design/R11-PRE-NEW-DIMENSIONS` (a9377bcf, its line 120) also read or edit `dev/audit/README.md`; design.md:186 names STANDING-SCRIPTS only. The re-apply rule there covers them. Carry: dismissed: same rule applies (item dr2-e)
- The projection record is a new tracked file once `plan/r<N>` lands on main. Classify its path in `tests/closure.py` in this pull request, or the first plan that lands forces the full suite. Carry: R11-ARCH-OBJECTIVE (item dr2-f)
- A draft roster holds only the plan's groups. State in the instrument's guide whether a group with no rank (an open group the architect did not draw) is kept in B or refuses the check; the note is silent. Carry: R11-ARCH-OBJECTIVE (item dr2-g)

Seat token count: not reported by this harness.
