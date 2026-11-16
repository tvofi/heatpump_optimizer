# R11-ARCH-OBJECTIVE: decision 0018 ranks the plan's work; the score is a constraint; the cost is disclosed

Designer seat, round 2, on top of 588a773f0348889af2812fe79348f7adf7501b6d, answering
`design-verdict/R11-ARCH-OBJECTIVE` at 6ec87d8b840dfad6711a36b8edf52e82ef37447a. Base
c82f014a639954b0f8930f29cf30fed3f0b20a6a (`origin/main`); no predecessor head (`after` is empty).
Brief read in `dev/programme/rosters/wave-r11-groups.json` on `handoff/audit-r10-roster` at
c3440f9949bf3f1c53e58734cda4881309f7be11. No finder harness: owner report (tvofi, 2026-11-16, quoted
in that brief). No production code.

## 0. The verdict, point by point

| point | answer | where |
|---|---|---|
| 1 `architecture-unsound` | No hours are authored. `tools/plan/replan.py` stays the one owner of hours, the critical path and the closure; the plan pins the roster blob it was projected from and every time figure is read from two projections | 1, 3 |
| 2 `class-open` | Rank does **not** reach dispatch order: `dispatch_tier` and `dispatch_key` are untouched. The title narrows to "no rank-1 group waits on a rank-2 group through an `after` edge without an ADR", plus the disclosed cost | 3, 5 |
| 3 `class-open` | The count is 16 other open `design/R11-*` refs; the shared files and their re-measure rule are named | 7 |
| decision: layer 2 and 3 keys before layer 1 is read | Designed out: while any layer-1 term is NO-READ, no-finding moves are ordered by the layer-1 key only; hours and tokens are disclosed, never sort keys | 2 |
| decision: rank reorders the owner's tiers | Moot under point 2's answer | 3 |
| decision: +22.7 commitment or floor | Still the owner's | 2 |
| decision: the roster's `files` | Still the orchestrator's: this note edits no decision record; the set is section 5's | 5 |

## 1. Owning seam

One owner per concern, none new:
- `tools/audit/seat/plan_audit.py` owns the machine read of `PLAN.json` (`reconcile`, its fork
  refusal). It gains the objective block's grammar, the P3 check and the settlement.
- `tools/plan/replan.py` owns hours (`group_hours`, from `tools/plan/durations.json`), the critical
  chain (`critical_path`), the closure and the dispatch order. **Read-only here, and called**: the
  check's command-line layer runs it as a subprocess, as `run_end_to_end` runs `score.py`, and the
  check function takes the two resulting plans as dicts. The self-test arms pass in-memory dicts,
  so nothing is imported and the step `p3-move-ledger-and` of `tools/ci/selftest_closures.json`
  keeps its measured closure.
- `tools/audit/seat/roster_lib.py` (`is_hotfix`, `is_outside`) is read by `replan.py` only.
Callers: `.claude/workflows/audit-plan.js`, `dev/governance/roles/architect-planner.md`,
`dev/governance/roles/plan-review.md` (the obligation and the command, no rule list). Read, never
edited: `dev/governance/decisions/0018-objective-function.md`, `dev/audit/config/objective.json`,
`tools/audit/check_scopes.py`. `tests/seam_map.json` maps coordinator methods only.

## 2. How the two combine: one ordering, no second target

0018 section 1 holds the score already: D7's criterion is decision 0015's path
(`owner_criteria.D7`). The plan follows 0018 section 2:

1. **Layer 1 first.** An element predicted to move a layer-1 term the wrong way is dropped or goes
   to the owner as a card (rule 1).
2. **Admissibility is the hard floor**: no scored metric or tripwire worsens end to end.
3. **dS is the stop test, never the sort key.** Toward the 0015 target: the dS kept findings yield;
   then no-finding moves ordered by the layer-1 key they serve (an escape's seam, an open class, an
   injected cause). 0018 says rules 2 to 4 rank nothing while a layer-1 term is NO-READ, and
   `dev/audit/yardstick/round10/OBJECTIVE.json` reads only `first_pass`, so hours and tokens order
   nothing: among moves with equal layer-1 keys the existing "cheap" test of `plan-review.md` step 4
   decides, and section 3's disclosed cost is what the owner reads it against.
4. **A shortfall is stated, never bought** (`architect-planner.md` step 10, unchanged).

`decision: owner`: +22.7 stays a commitment because `owner_criteria.D7` is 0015's path; the
orchestrator's starting position (the score only a floor) needs an edit of 0015.

## 3. Shape

**The plan commits to** an objective block in `PLAN.json`:
- the baseline: the previous round's record under `dev/audit/yardstick/`, path and tree SHA;
- **the projection pin**: the draft roster's path and blob at the plan SHA, the `--start` instant
  and the blob of `tools/plan/durations.json`. No hour, chain or date is written by the architect;
- per term of `objective.json`, a predicted direction with its basis; a term NO-READ in the
  baseline takes only "undecided" with its builder;
- per group: a **rank** (1: closes a verified `bug` finding, an escape's owning step, an open card
  or an open class; 2: no layer-1 key) and **keyed effects**: the finding ids it removes; the escape
  rows or class id whose seam it closes; for rank 2, the finder pass that examines its diff before
  the close (`unexamined`). Derived for every production group: no objective bug names its merge as
  cause (`injected`), and none of its findings is reported again (0018 section 4 link 3).

**The time figures are projections, computed by the check.** It runs `replan.py` twice at the pin:
(A) `--roster-ref <plan SHA> --roster-path <draft>`, whose `generated.roster_blob` must equal the
pin (the rule of `stale_reason`); (B) `--roster-file` on the same roster less every rank-2 group
that no rank-1 group reaches through `after` (entries filtered by name; edges are read from A's
`groups`, so no roster grammar is re-declared). From A: `lead_time` p50 and p90 over production
groups (finish less start), the forecast `summary.closure`. From A against B, the **floor cost**:
the differences in `binding.critical_path_hours` and `summary.wall_hours`, and per rank-1 group the
finish delay. The workflow commits these beside `PLAN.json` as a generated projection record; a
re-run that differs from the committed record refuses, so the reviewer and the settlement read the
same model as the architect.

**Order rule, in plan data.** A rank-1 group whose `after` closure in A holds a rank-2 group needs
that edge's ADR in the plan's moves, or the check refuses. That is the whole rule. Slot and
`hot_files` turns stay `dispatch_key`'s (owner rulings 2026-10-30, 2026-11-07, 2026-11-08): a rank-2
group taking a slot ahead of a rank-1 group is not refused; it is **priced** in the per-group delay
above, which the owner sees before approving. The hot-file order of step 8 is prose in the plan
and is checked by the reviewer, not the instrument.

**A lagging read is credited by settlement.** At the close, and again when the next P3 opens, the
instrument prints one line per effect: HELD, MISSED, UNDECIDED (NO-READ, or the band unset) or
NOT-DUE (cause, re-report and escape keys fall due at N+1's close). Only a HELD keyed effect is
credit; a term that improved with no keyed effect prints UNPREDICTED and is not banked. Plan N+1
disposes every MISSED and newly due line (a group or a card), or its check refuses; a first plan,
with no previous block, passes that arm. Credit is the plan's, never a seat's.

```
register + record N-1 -> architect -> PLAN.json block (ranks, effects, pin)
  -> P3 check: replan.py A, B -> projection record -> plan-review -> owner -> P4 (dispatch_key, unchanged)
  -> close, record N -> settle(plan N) -> P3 of N+1: settle again; MISSED lines are its input
```

**Interfaces.** `plan_audit.py` gains two subcommands: the P3 check (plan, register, baseline,
previous settlement; `--json` writes the projection record) and the settlement (plan, record,
merged bodies as `ledger` takes them); one refusal per line, exit 1 on any. `audit-plan.js`: the
moves reply gains the block, the check runs before the push, the reviewer prompt names it.
**Invariants:** `ledger`, `snapshot`, `compare`, `replan.py` and the roster are unchanged; only the
new check refuses a plan with no block.

**plan-review adds:** (a) re-run the P3 check at the plan SHA (this is step 5's projection re-run,
now one model); (b) attack three ranks and three keyed effects in the code, taking the rank-1
groups with the most predicted dS per finding; (c) read the floor cost against the "cheap" test;
(d) the previous plan's settlement is disposed.

## 4. Alternatives

- **Hours in `PLAN.json`, chain summed in `plan_audit.py`** (round 1): a second owner of
  `group_hours` and `critical_path`, and an authored duration `replan.py` refuses by rule.
- **Rank as a `dispatch_tier` input**: a new write path from the plan into the roster or the tier
  rule, reordering tiers three owner rulings fixed; the edge rule plus a priced delay needs neither.
- **Import `replan.py`**: moves the self-test step's measured closure by `replan.py` and
  `roster_lib.py`; a subprocess behind a dict-taking function moves nothing.
- **One weighted number**: 0018 section 2 refuses a weight as a price between terms.
- **Aggregate deltas per group**: 0018's count band makes a small delta a tie, so none could be
  MISSED.
- **Predictions in the roster group**: `roster_edit.py` edits the roster through P4; the plan is
  the object `plan-review.md` approves "at that SHA".

## 5. Sibling sites

`git grep -l -E "plan_audit|architect-planner\.md|plan-review\.md|PLAN\.json|dispatch_tier|critical_path" -- . ':!dev/programme/rosters' ':!dev/archive' ':!dev/audit/yardstick'`
Changed: `plan_audit.py`, `audit-plan.js`, the two contracts,
`tools/audit/seat/instruments/plan_audit.py.md`, `tools/audit/seat/INSTRUMENTS.md` (its row),
`tools/policy/check-wave-script.mjs` (a new arm on the moves prompt, with its failing twin),
`dev/audit/README.md` (P3 row), `dev/governance/config/policy_budgets.json`. Read-only, with the
reason: `tools/plan/replan.py` and `tools/audit/seat/roster_lib.py` (rank does not reach dispatch);
`tools/audit/seat/plan_page.py` (renders `replan.py`'s plan, not the block). Out of scope:
`.github/workflows/governance.yml` (greps the self-test tally); 0015, 0018 and
`tools/audit/archscore/ABOUT.md` (no target, term or threshold changes); the rest are records.

## 6. Evidence, by file

Failing test first: `self_test` arms in `plan_audit.py` on in-memory fixtures, each planted plan
with its passing twin (the null control), red before the subcommands exist.

| planted plan, and the number it games | refused as | passing twin |
|---|---|---|
| `bug` finding deferred, no card (`lead_time`) | deferred bug | a card id |
| no-finding group claims an unregistered finding id (`unexamined`) | unknown finding | a registered id |
| "hold" on a term NO-READ in the baseline (free credit) | NO-READ undecided | "undecided", builder |
| one finding closed by two groups (`lead_time`, `tokens_per_change`) | double closure | one group |
| rank 1 after rank 2 in A's edges, no ADR (dS first) | rank edge | the edge's ADR |
| rank-2 group, no examining pass (dS at `unexamined`'s cost) | unexamined move | the pass |
| an hours, chain or closure key authored in the block (cost hidden) | authored time | the pin alone |
| projection A's `roster_blob` unequal to the pin (cost of another roster) | stale pin | equal blobs |
| committed projection record unequal to the re-run (cost edited) | projection differs | the re-run's bytes |
| B keeps a rank-2 group no rank-1 group reaches (floor cost shrunk) | reduced roster | it is dropped |
| settlement over a NO-READ term | UNDECIDED, never HELD | a value: HELD |
| settlement: term improved, no keyed effect | UNPREDICTED | the keyed effect: HELD |
| plan N+1 silent on a MISSED line of plan N | undisposed | kept or carded; no previous block |

- Perturbation: one record value flipped flips exactly one settlement line; one rank-2 group's size
  raised in the roster fixture moves the floor cost and nothing else.
- Mutation proof targets: each new refusal's predicate, the reduced-roster filter and the
  settlement's status choice. `plan_audit.py` has no mutant machinery today; the fixer builds it.
- One real run, outside the self-test: the check against the round-10 roster at the base, both
  projections, in the pull-request body.
- No goldens, no claim files. `plan_audit.py` is on `inert_reads` for `tests/entities.py`, whose
  closure holds both contracts, so the scoped gate selects that script.
- Not caught: whether an escape's seam truly is the group's (review point b); a slot or hot-file
  turn `replan.py` does not model. Round 11 settles UNDECIDED on every term but `first_pass`, and
  `band_lead_time` is unset.

## 7. Hot files, position, carries

No `after`; merges before round 11's P3, first among the notes below. Of the 16 other open
`design/R11-*` refs, none touches the two contracts' text, `plan_audit.py`, `audit-plan.js` or
`PLAN.json`. Shared:
- `dev/governance/config/policy_budgets.json`: R11-PRE-NEW-DIMENSIONS (a9377bcf),
  R11-PRE-PRODUCT-READS (8daf1183), R11-PRE-SECURITY-PRIVACY (8f527838), R11-PRE-STANDING-SCRIPTS
  (375ce7ff). This group changes only the two contracts' entries. Rule for whichever merges later:
  merge main, re-run `node tools/policy/policy_lint.mjs --budgets`, re-record only its own entries.
- `tools/policy/check-wave-script.mjs`: R11-PRE-SECURITY-PRIVACY edits it, R11-PRE-NEW-DIMENSIONS
  runs its base copy. This group adds one arm in the P3 block; the later merge re-runs the script.
- `tools/audit/seat/INSTRUMENTS.md` (PRODUCT-READS, STANDING-SCRIPTS, R11-PRE-PARALLEL-PIPELINE
  a21ad559, R11-PRE-SHARED-FILES 20cafac7) and `dev/audit/README.md` (STANDING-SCRIPTS): one row
  each, re-applied after a merge of main; after SHARED-FILES the index row is its generator's.
Headroom of both contracts is what `--budgets` prints (`plan-review.md`: none), so the text needs a
raise: the owner's confirmation before the push, or mandate 6893738184 with a
`## Raise justification`.

## Notes for the fixer

- Pay the caps first: the contracts name the command and the four review checks; section 3's rules
  live in the instrument's refusals and its guide. Carry: R11-ARCH-OBJECTIVE
- Pass both `replan.py` runs the pinned `--start` and durations file, or they are not byte-stable;
  projection B is a `--roster-file` plan, which pins no blob by design. Carry: R11-ARCH-OBJECTIVE
- `audit-plan.js` defaults the draft to `.claude/workflows/`, while `roster_path` looks under
  `dev/programme/rosters/`: the check passes the draft's path explicitly. Carry: R11-ARCH-OBJECTIVE
- Verdict items dr1-a (mutants), dr1-b (in-memory arms), dr1-c (first plan), dr1-d (review picks),
  dr1-e (index row, new arm) are taken into sections 3, 5 and 6. Carry: R11-ARCH-OBJECTIVE
- The settlement needs keyed rows (finding id, class id, causing pull request) in the escapes,
  cause and re-report records; `dev/audit/rounds/round10/objective/escapes_hand.tsv` is keyed by
  roster group and causing pull request only. Until the builders print rows, those lines print
  UNDECIDED, as do the round-level `lead_time` and closure lines. Carry: R11-INTAKE-R10-RESIDUE
- `plan_audit.py` has no `.github/CODEOWNERS` line while 0018 section 5 calls an enumerator
  code-owned. Carry: dismissed: owner decision, reported in the designer's result

Seat token count: not reported by this harness.
