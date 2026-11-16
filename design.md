# R11-ARCH-OBJECTIVE: the plan is ordered by decision 0018; the score is a constraint on it

Designer seat, round 1. Base b98c78e0f6144a5ea5b48a032e30bf2d085c2d61 (`origin/main` at dispatch);
no predecessor head (`after` is empty). Brief read in `dev/programme/rosters/wave-r11-groups.json`
on `handoff/audit-r10-roster` at 79b098355d954300c6017c48f6a669c8f1f274f4. No finder harness: owner
report (tvofi, 2026-11-16, quoted in that brief). No production code.

## 1. Owning seam

One owner: `tools/audit/seat/plan_audit.py`, which already owns the machine read of `PLAN.json`
(`reconcile`, its fork refusal). It gains the objective block's grammar, the P3 check and the
settlement. Callers only: `.claude/workflows/audit-plan.js`, and
`dev/governance/roles/architect-planner.md` and `dev/governance/roles/plan-review.md`, which state
the obligation and name the command, with no rule list. `tests/seam_map.json` maps coordinator
methods only. `dev/governance/decisions/0018-objective-function.md`,
`dev/audit/config/objective.json` and `tools/audit/check_scopes.py` are read, never edited: no
term, layer or threshold is added.

## 2. How the two combine: one ordering, no second target

0018 section 1 already contains the score: D7's perfect result is "the programme target of decision
0015 met with no gate metric risen" (`owner_criteria.D7`). dS is one dimension's distance inside
the function, so the plan follows 0018 section 2's order and nothing else:

1. **Layer 1 first.** A plan element predicted to move a layer-1 term the wrong way is dropped or
   goes to the owner as a card (0018 rule 1).
2. **Admissibility is the hard floor**: no scored metric or tripwire worsens end to end.
3. **dS is the stop test, never the sort key.** Moves toward the 0015 target are taken in objective
   order: the dS kept findings yield anyway; then no-finding moves by the layer-1 key they serve (an
   escape's seam, an open class, an injected cause); then by critical-chain hours added; then
   tokens. Past the target, "cheap" (`plan-review.md` step 4) means: adds no critical-chain hours
   and names its examining pass.
4. **A shortfall is stated, never bought**: a target reachable only by breaking 1 or the template
   goes to the owner with options (`architect-planner.md` step 10, unchanged).

`decision: owner`: this keeps +22.7 as a commitment, because `objective.json` names 0015 as D7's
criterion. The orchestrator's starting position (the score only "a floor no plan may worsen") would
demote it to D7's reported distance and needs an edit of 0015.

## 3. Shape

**The plan commits to** a new objective block in `PLAN.json`:
- the baseline: the previous round's record under `dev/audit/yardstick/`, path and tree SHA;
- per term of `objective.json`, a predicted direction with its basis. A term NO-READ in the
  baseline takes only "undecided" with its builder (0018: a NO-READ is undecided, never a tie);
- per group: a rank (1: closes a verified `bug` finding, an escape's owning step, an open card or
  an open class; 2: no layer-1 key), predicted hours, and **keyed effects**: rows a reader can look
  up, never an aggregate delta. Keys: the finding ids it removes; the escape rows or class id whose
  seam it closes (no new instance in the next window); for a rank-2 group, the finder pass that
  examines its diff before the close (`unexamined`). Derived for every production group, so no plan
  can omit them: no objective bug names its merge as cause (`injected`), and none of its findings is
  reported again (0018 section 4 link 3, the brief's "refix");
- round level: the removed count (derived from kept bug findings), `lead_time` p50 and p90 from the
  plan model, the forecast closure (`closure_slip`'s base), and the **floor cost**: critical-chain
  hours the rank-2 groups add, recomputed by the instrument from the per-group hours.

**Order rule.** A rank-2 group precedes a rank-1 group only on a prerequisite edge naming its ADR.

**A lagging read is credited by settlement.** At the close, and again when the next P3 opens, the
instrument reads plan N against the objective record and prints one line per effect: HELD, MISSED,
UNDECIDED (the read is NO-READ or its band unset) or NOT-DUE (cause, re-report and escape keys fall
due at N+1's close). Only a HELD keyed effect is credit. A term that improved with no keyed effect
behind it prints UNPREDICTED and is not banked, as `reconcile` refuses a dS no move explains. Plan
N+1 disposes every MISSED and newly due line of plan N (a group, or a card), or its check refuses.
Credit is the plan's, never a seat's.

```
register + record N-1 -> architect -> PLAN.json objective block -> P3 check -> plan-review -> owner
 -> P4 -> close, record N -> settle(plan N) -> P3 of N+1: settle again; MISSED lines are its input
```

**Interfaces.** `plan_audit.py` gains two subcommands: the P3 check (plan, register, baseline,
previous settlement) and the settlement (plan, record, merged bodies as `ledger` takes them); each
prints one refusal per line and exits 1 on any. `audit-plan.js`: the moves reply gains the block,
the check runs before the push, the reviewer prompt names it. **Invariants:** `ledger`, `snapshot`,
`compare` and their self-test arms are unchanged; only the new check refuses a plan with no block.

**plan-review adds:** (a) re-run the P3 check at the plan SHA; (b) attack three ranks and three
keyed effects in the code; (c) re-run the projection without the rank-2 groups against the floor
cost; (d) the previous plan's settlement is disposed.

## 4. Alternatives

- **One weighted number**: 0018 section 2 refuses a weight as a price between terms.
- **A second instrument file**: two parsers of one `PLAN.json`, plus a second CI step, guide and
  `tools/ci/selftest_closures.json` entry.
- **Aggregate deltas per group** ("escapes down 2"): the record is per term and 0018's count band
  makes a small delta a tie, so no group's prediction could be MISSED.
- **Predictions in the roster group**: `roster_edit.py` edits the roster through P4; the plan at
  `plan/r<N>` is the SHA-pinned object the review approved (`orchestrator.md` section 2b).

## 5. Sibling sites

`git grep -l -E "plan_audit|architect-planner\.md|plan-review\.md|PLAN\.json" -- . ':!dev/programme/rosters' ':!dev/archive' ':!dev/audit/yardstick'`
Changed: section 1's four files, `tools/audit/seat/instruments/plan_audit.py.md`,
`tools/policy/check-wave-script.mjs` (its prompt assertion), `dev/audit/README.md` (P3 row),
`dev/governance/config/policy_budgets.json`. Out of scope: `.github/workflows/governance.yml` (greps
the self-test tally, which new arms extend); 0015 and `tools/audit/archscore/ABOUT.md` (target
unchanged); `orchestrator.md` (2b already records deviations); the rest are records and fixtures.

## 6. Evidence, by file

Failing test first: `self_test` arms in `plan_audit.py`, each planted plan with its passing twin
(the null control), red before the subcommands exist.

| planted plan, and the number it games | refused as | passing twin |
|---|---|---|
| `bug` finding deferred, no card (`lead_time`) | deferred bug | a card id |
| no-finding group claims an unregistered finding id (`unexamined`) | unknown finding | a registered id |
| "hold" on a term NO-READ in the baseline (free credit) | NO-READ undecided | "undecided", builder |
| one finding closed by two groups (`lead_time`, `tokens_per_change`) | double closure | one group |
| rank 2 ahead of rank 1, edge with no ADR (dS first) | rank edge | the edge's ADR |
| rank-2 group, no examining pass (dS at `unexamined`'s cost) | unexamined move | the pass |
| floor cost absent or unequal to the recomputed hours (dS cost hidden) | floor cost | the figure |
| settlement over a NO-READ term | UNDECIDED, never HELD | a value: HELD |
| settlement: term improved, no keyed effect | UNPREDICTED | the keyed effect: HELD |
| plan N+1 silent on a MISSED line of plan N | undisposed | kept or carded |

- Perturbation: flipping one record value flips exactly one settlement line.
- Mutation proof targets: each new refusal's predicate and the settlement's status choice, by the
  in-file mutant pattern of `tools/audit/seat/round_metrics.py` (`--no-mutants`).
- `tools/policy/check-wave-script.mjs` asserts the prompt runs the check. No goldens, no claim
  files. `plan_audit.py` is on `inert_reads` for `tests/entities.py`, whose closure holds both
  contracts, so the scoped gate selects that script.
- Not caught: whether an escape's seam truly is the group's (review point b). Round 11 settles
  mostly UNDECIDED: `escapes`, `injected`, `coverage` and `unexamined` are NO-READ in
  `dev/audit/yardstick/round10/OBJECTIVE.json`, and `band_lead_time` is unset.

## 7. Hot files, position, carries

No `after`; merges before round 11's P3. Hot: the two contracts, `plan_audit.py`, `audit-plan.js`,
`policy_budgets.json`; none of the 15 open `design/R11-*` notes claims them. Headroom of both
contracts is what `node tools/policy/policy_lint.mjs --budgets` prints (`plan-review.md`: none), so
the text needs a raise: the owner's confirmation before the push, or mandate 6893738184 with a
`## Raise justification`.

## Notes for the fixer

- Pay the caps first: the contracts name the command and the four review checks; section 3's rules
  live in the instrument's refusals and its guide. Carry: R11-ARCH-OBJECTIVE
- The settlement needs keyed rows (finding id, class id, causing pull request) in the escapes,
  cause and re-report records, which do not exist yet; their builder must print rows, not only
  counts. Until then those lines print UNDECIDED. Carry: R11-INTAKE-R10-RESIDUE
- Do not import `round_metrics.py`: it would move the self-test step's measured closure; the
  settlement reads the record file. Carry: R11-ARCH-OBJECTIVE
- `plan_audit.py` has no `.github/CODEOWNERS` line while 0018 section 5 calls an enumerator
  code-owned. Carry: dismissed: owner decision, reported in the designer's result

Seat token count: not reported by this harness.
