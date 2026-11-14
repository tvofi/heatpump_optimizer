policy: decision 0017, the objective function, and the evaluation that opens a round (R11-PRE-OBJECTIVE-FUNCTION)

Defines the function the owner asked for on 2026-11-13 as decision 0017, adds the evaluator seat that grades every dimension, contract, rule, instrument and gate against it before a round's finders, and makes `tools/audit/check_scopes.py --round N` refuse a round start whose evaluation is missing, incomplete or undecided. `audit-find.js` passes its round, so the refusal sits in the instrument that already refuses a bad scope table.

What it does not do: build an enumerator of a term. Of the thirteen terms only `first_pass` has a working one; `generality` now has its denominator (`check_scopes.py --population`) and no numerator. Decision 0017 section 4 claims convergence for no round yet, lists seven assumptions no sensor reads, and says the function moving the right way does not show fewer objective bugs.

## Repair round: the blocked verdict answered by number

Verdict: `verdict.md` on `probe/revt-r11-pre-objective-function-3a4f648d` (4ec1b989cc), `Fix review: blocked f7efa4be88 sufficiency`. Each answer is in the decision record, `dev/audit/config/objective.json` or `dev/governance/roles/evaluator.md`, never only here.

**Block**

1. Thresholds: `objective.json` `thresholds` holds five fields (`product_green_floor`, `closure_slip_ceiling`, `band_lead_time`, `band_closure_slip`, `band_tokens_per_change`), each `value` null with the orchestrator's `proposed` beside it, and `owner_criteria` one field per owner-decided dimension. 0017 section 2, "The owner's values are fields of `objective.json`": a null is unset, every comparison or result needing it is undecided, and the evaluation cards it. `check_scopes.py --round` refuses an unset one with no card (arms B8).
2. NO-READ in the ordering: 0017 section 2, "A NO-READ is undecided, never a tie": a term NO-READ on either side has neither moved nor held; a first read is a baseline; while any layer-1 term is NO-READ, rules 2 to 4 rank nothing and only read-building changes and owner-carded ones are kept. Rule 1 now reads "every layer-1 term is read on both sides and none is worse". This is the stricter of the two readings the verdict names; it is listed for the owner below.
3. `regret`: 0017 section 1 defines four costs. `C_same`, the same-information oracle, takes only exogenous inputs at decision time (published prices, the provider's forecast as issued, sensor readings to then, the configuration) on the measured house (the response and draw the window's sensors recorded, never the learned model). `regret = C_real - C_same` is all removable loss; the floor is `C_same - C_fore` (the provider's forecast error), reported beside it and outside it; the model gap `|C_real - C_model|` is part of the term (zero regret needs the gap inside the band). The residual rows of sections 1 and 2 are split on that line. What stays unattainable is said: the draw no history predicts lands in `regret`.
4. Population: `python3 tools/audit/check_scopes.py --repo . --population` prints every axis with its levels from the tracked source `objective.json` `population` names (the flow's option tuples, the optional entity keys of `config_flow.py` as present or absent, `translations/`, `hacs.json`'s floor, `tests/profiles.py`'s price shapes and climates). The cells are every level and every pair of levels from two axes; an interaction of three or more axes is the stated residual. Tank volume and house size have no tracked levels and are NO-READ axes with their builder. Counts in `## Figures`.
5. Dimension table: 0017 section 1 gains two columns, the enumerator of the distance (a tracked command, or NO-READ with what would read it and the group that builds it, or undecided on an unset `owner_criteria` field) and the floor, for all sixteen dimensions.
6. Builders: every NO-READ product read names a live group in 0017 (section 1 table, section 2 table, sections 4 and 5): the oracle harness, realised-cost record, model gap, the actuator-write dimension's cell ledger, D12's axes and cell ledger go to R10-DIMENSIONS-FULL-COVERAGE; the held-out instruments and the window reads to R11-PRE-ROUND-METRICS; the ledger to R11-PRE-TOKEN-LEDGER. Each `## Forward-carry` item below names decision 0017 and its section and stands alone.

**Also owed at the re-handoff**

- Independence: evaluator and reviewer are compared under case and punctuation, and either containing `orchestrator` is refused (B1; the verdict's P1, P2). `review` is a verdict: `approve` at a commit in the ref's history whose `EVALUATION.json` holds the same `objects` (B2). What no record can read (whether the seat worked the graded round, who dispatched it) is stated in 0017 section 6, "Cannot read", with R11-PRE-TOKEN-LEDGER as builder.
- Who writes the owner's decision: 0017 section 5. The orchestrator writes a closing round's objective record once, and the owner's ruling into a card with where he gave it (`ruling`, B3); the evaluator writes the rest and never a ruling. Section 5's "never edits them" is gone; sections 5 and 6 now agree.
- Merged-commit tie: an accepted card's `merged` must be on the baseline, after the review's sha, and change the card's `object` or one of its `paths` (B4; P3 refused).
- By-hand and null values: a read is a number (or a dict of numbers) with an enumerator naming a file tracked at the ref (B5; P4, P5 refused).
- A `remove` on NO-READ evidence is refused (B7; P6).
- The zero-card all-NO-READ record is refused: a NO-READ names `would_read` and `builder` (B6), an unset owner value needs its card (B8), an `unowned` count needs that many cards (B9) (P0, P7 refused).
- Verdict set: arm B10 (`retain` refused) pins it; the verdict's surviving mutant R12 is M21 below, killed.
- Object set: `objective.json` `objects` now maps a class to a list of globs and adds `CLAUDE.md`, `AGENTS.md`, `.claude/workflows/*.js`, `.claude/hooks/*`, `.claude/skills/*/SKILL.md` and the eight unguided scripts the verdict lists. An evaluation row for a file outside the set is refused (B11; P8).
- Citations: 0017's Context no longer gives the pre-studies a path; `governance_cost.py` is gone and runner seconds per merge is NO-READ with its builder; the actuator-write dimension is defined in the record and assigned.

**The convergence section**: 0017 section 4, "What the inequality assumes and no sensor above reads", states the verdict's seven points (infimum against mean recall; correlated finders; found counted after the judge; injection with no bug removed; no term for a fix that did not fix; the claim covers objective bugs only; the unmeasured reporting rate) and closes on what the function does not show.

**The gaming section**: 0017 section 5's table marks each control live, beside or NO-READ with its builder, and adds the verdict's moves: the narrow-universe re-run (`coverage`), the run that asserts nothing (`generality`), the document edited to match the code (`operation`: the target is the plan's computed value), the pass that only says it read (`unexamined`), the cause named by the indicted party (`injected`), the late roster entry (`lead_time`: the clock is the commit that added the group), and the weak approval (`first_pass` ranks nothing until its two catchers are read).

## Where each owed part is

| part | where |
|---|---|
| A. definition, units, denominators, enumerators, targets, ties; object scoring | 0017 sections 1 to 3; `dev/audit/config/objective.json` |
| B. convergence claim, assumptions, sensors, what is not shown | 0017 section 4 |
| C. the step, who runs it, the refusal and its self-test | `dev/governance/roles/evaluator.md`; 0017 section 6; `dev/audit/README.md` phases 2 and 13; `tools/audit/check_scopes.py`; `.claude/workflows/audit-find.js` step 7 |
| D. anti-gaming per term; standing cost | 0017 section 5 and section 6's last paragraph |
| E. round 10 scored by hand | this body, below |

## Carries answered

- **Carry 0** (a perfect reader; the end state; self-contained; residuals): 0017 section 1 gives each dimension its perfect result, who decides it, the enumerator of its distance and its floor; section 2 gives each term its end state and residual; section 3 ends with "From a distance to a change".
  What a reader with 0017 and the tree alone would change for round 11: (1) by "A NO-READ is undecided", build the missing reads first, in the groups the record names, since nothing else can be ranked; (2) by section 1's table, write the census or list each NO-READ dimension lacks (D1, D2, D8, D11, D15's bundle set) into its brief; (3) by `generality`, make `--population` D12's universe and start the cell ledger at the levels, then the pairs; (4) by `operation`, draft the actuator-write dimension over the write sites the record's grep lists; (5) by `regret`, add the oracle step to D0 and the realised-cost step to D15; (6) by "`coverage` below 1", delete each brief's sampling instruction (D1, D3 and D11 carry one) and write the enumerating command.
  What it could not decide without the owner: the five thresholds, the criteria of D4, D5, D9 and D10, the evaluator's model, and the two open decisions below.
- **Carry 1** (anchored on the product; completeness; the chain): section 1's three clauses; `unowned` is the completeness term and every unowned item a card (B9); section 4 is the six-link chain, link 3 now stated as NO-READ and in no term, and "one round guarantees perfect code under no condition this record can check".
- **Carry 2** (generality, operation, savings): section 1 as answered under block items 3 and 4; D12's owed brief changes are named there; the acceptance criteria are Decisions 14 and 15.
- **Carry 3** (the playbook stays usable; the dry read): unchanged from the first handoff and held by the verdict. From `dev/audit/README.md` alone: phase 2 enters on "a baseline SHA pinned after `evaluator.md`'s evaluation" and names `tools/audit/check_scopes.py`; `evaluator.md` sends its reader to decision 0017; `.claude/workflows/audit-find.js` runs `--round` at the baseline; phase 13's artefact names the round's objective record. R10-ROUND-PLAYBOOK-FINAL reads `carries-open` on the roster branch while its table is on main, so the pointer is in the table and nothing is carried to that group.
- **Carry 4** (the delegated population and comfort bounds): kept as the last commit recorded them, with the ruling quoted, and each now enumerable: the population by `--population`, the bounds as the four the product enforces (0017 section 1, `regret`).

## Departures from the proposal the owner read

1. "Never traded" is "not worse beyond a band", and from this round "read on both sides" (block item 2).
2. No trade inside a layer either: one term up and one down is no improvement.
3. Lead time starts at the roster entry, not the first commit, which the measured seat chooses.
4. Tokens are NO-READ while any seat class is unledgered; a local-only figure is a partial of unknown share.
5. Held-out checks are sensors of the assumptions, not terms: a seat scored on recall would optimise the plants.
6. A finding count is in no layer.
7. A card is an entry of the evaluation file, with the owner's ruling recorded on it.
8. Report-only binds the verdicts, not the step: the evaluation must exist for round 11 to start.
9. An off-cadence dimension counts 0 coverage.
10. Thirteen terms, not seven: the owner's carries add `regret`, `operation`, `generality`, `unowned`, `unexamined` and `first_pass`.
11. The population's cells are levels and pairs, not the full product, which no seat can walk (block item 4).

## Round 10 scored by hand (the null control for usefulness)

Sources: the process convergence audit at d5d7ff81878fe9bc17ee6fcc9e3803d848cbc7f7 (ref `handoff-wip/r10-process-convergence-audit`) and the dimension coverage audit at 6ca3bfb7142be1ccb0d5275041c41d5eae3c8ddc (ref `handoff-wip/r10-dimension-coverage-audit`); neither is in the tree. Nothing was re-measured: every figure is theirs, taken by hand or by scripts outside the tree, so every row but `first_pass` is NO-READ as a record, and under block item 2's rule round 10 ranks nothing.

| term | what the audits hold | as a record |
|---|---|---|
| `regret` | D0 raced under a fifth of its grid; no realised cost per install | NO-READ |
| `operation` | 3 actuator escapes; write and hold sites never enumerated by a brief | NO-READ: no dimension, no cell ledger |
| `generality` | D12 exhaustive over its declared slots; card and blueprints outside its universe | NO-READ: denominator now printed, no cell ledger |
| `unowned` | 7 of the 25 escapes | NO-READ; by hand 7 |
| `escapes` | 25 product escapes against 111 verified findings removed | NO-READ: no found-by field |
| `injected` | at least 3 named causes over 139 production merges; proxy 10 hotfix merges of 139 (round 9: 2 of 91) | NO-READ: no cause field |
| `product_green` | scorecard `A_gate` printed 0/0 read | NO-READ: the job listings have no producer |
| `coverage` | 2 of the 14 dimensions audited report a denominator | NO-READ by any command |
| `unexamined` | 26 outside groups and features admitted mid-round | NO-READ |
| `first_pass` | 412 of 817 | read: `tools/audit/seat/flow_metrics.py --window` |
| `lead_time` | first commit to merge, production: p50 21.7 h, p90 49.3 h | NO-READ: the roster-entry clock is printed by nothing |
| `closure_slip` | 13.6 days later over 12.9 days of plan history | NO-READ: read from rendered pages |
| `tokens_per_change` | local seats only | NO-READ: cloud seats unledgered |

Where the function cannot rank what the audits found: inside layers 2 and 3 no change has a measured before and after; the memory index, the rulings file, the alert replay, reviewer drift and ack renewal move no term 0017 names; inside layer 1 it ranks by escape rows, a count the coverage audit already had. Its own contribution is the layering, the cadence finding and the refusal to compare what has no record.

## Open decisions for the owner (not decided in this pull request)

Two items the brief reserves for the owner. Neither is decided by the diff; each quotes the sentence it would change.

- **(a) What a mandate in force may approve about the yardstick files.** The owner ruled on 2026-11-13 that the mandate stays as is, so the first handoff's "no mandate scope covers them" is removed. 0017 section 5 now reads: "Nobody edits this record, `objective.json`, the check or an enumerator but by a pull request reviewed as decision 0013 requires of a code-owned path". A limit would change that sentence. Three other sentences bear on what an approver under a mandate may do and are left as first written, for the owner to keep or strike: section 2 rule 1, "only the owner accepts one, by card"; section 6, "the owner decides each card"; section 2, "the only process changes kept are the ones that build a missing read to this section's definition, and the ones the owner accepts by card". Under the last two a round cannot start, and from round 12 a process change cannot be kept, on an agent's approval alone.
- **(b) The model the evaluator seat runs on.** `evaluator.md` no longer says "One opus seat": it reads "One seat per round, on the model `objective.json`'s `seats` names (unset: ask the owner)", and `seats.evaluator_model` and `seats.reviewer_model` are null. Setting either changes those two fields and nothing else.

## Decisions for the owner

Each is a recommended value, its basis and the alternatives. Decisions 1 to 3 are now the `proposed` fields of `objective.json` `thresholds`; the owner sets one by moving it to `value`.

1. **`product_green` floor: 0.90.** Basis: the process audit's a1 metric. Alternatives: 1.00; 0.95.
2. **`closure_slip` ceiling: 0.2 days per day.** Basis: the process audit's b3. Alternatives: 0; 0.5.
3. **Band for `lead_time`, `closure_slip`, `tokens_per_change`: 20%**, as three fields. Basis: round 10's weekly production p50 ranged about 28% either way over five weeks. Alternatives: 10%; 30%.
4. **Count band: twice the square root of the two counts' sum.** Alternatives: any difference; three.
5. **Token unit: the raw sum of usage fields.** Alternative: price-weighted.
6. **Lead-time clock at the roster entry**, read from the commit that added the group. Alternative: first commit.
7. **The refusal is live for round 11.** Alternative: wire `--round` from round 12.
8. Withdrawn: see open decision (a).
9. Withdrawn: see open decision (b).
10. **`remove` needs zero measured yield in two consecutive rounds.** Alternatives: one; three.
11. **0017 is an uncapped file**, as decisions 0001 to 0016 are. Alternative: a capped rule file, at a corpus raise of about its size.
12. **The held-out instruments** (planted defects, the overlap trial) are assigned to R11-PRE-ROUND-METRICS by this round. Alternative: a group of their own.
13. **CODEOWNERS gains four lines**: the config, `check_scopes.py`, and the two record files under `dev/audit/rounds/`.
14. **The supported install population** is set (Carry 4), and its cells are levels and pairs. Alternative at review: a narrower named list; or triples, at a larger denominator.
15. **The comfort bounds** are set (Carry 4). Alternative: a fixed band the owner states.
16. **Acceptance criteria**: `owner_criteria` D4, D5, D9 and D10 are null; each is a card at round 11's evaluation. D7's is decision 0015.
17. **Adding a term or an object class removes one**, after this record lands. Alternative: no such rule.
18. **A NO-READ layer-1 term stops the ordering** (block item 2). Alternative: rank on the terms that are read, which lets `first_pass` alone rank changes while its catchers are unread.

## Head

018b520580cfd80b828687418f13672a4c03051d (measured 2026-11-13 23:37 UTC; origin/main at 50373173d4, which this head contains: it is the merge of the pull request's branch a5bbc5ec81, itself main merged in plus the delivery row, into this round's commits; every figure below was re-taken on the merge)

## Mutation proof

One mutant per arm of this round, each a unique-string change to a production predicate of `tools/audit/check_scopes.py`, the self-test run, the file restored and its sha256 checked. Driver: `$EXPORT/mutants.py` sha1 c21ce80cdef33a8551a57156f62f0bb96f311bc9 (scratch; a one-off). Unmutated: exit 0 before and after.

| mutant | predicate became | self-test arm that goes false |
|---|---|---|
| M1 role names normalised | raw compare | B1 a disguised orchestrator or the same seat respelled |
| M2 `orchestrator` substring | dropped | the orchestrator as evaluator; B1 |
| M3 review verdict | any verdict | B2 a review that is no approve verdict |
| M4 review sha in history | not consulted | B2 a review sha outside the ref's history |
| M5 reviewed objects equal the record's | never differs | B2 a review that graded other objects |
| M6 decided card needs `ruling` | never refused | B3 |
| M7 merged after the review | never refused | B4 an accepted commit that predates the review |
| M8 accepted card names a file | never refused | B4 an accepted card naming no file |
| M9 merged commit changes the card's file | never refused | B4 |
| M10 read value numeric | null allowed | B5 a null value |
| M11 enumerator tracked | never refused | B5 an enumerator naming no tracked file |
| M12 NO-READ needs `would_read` | only builder checked | B6 |
| M13 NO-READ needs `builder` | only would_read checked | B6 (the arm was tightened to kill it) |
| M14 `card:` builder is a card | never refused | B6 a builder card the evaluation lacks |
| M15 remove on NO-READ | never refused | B7 |
| M16 unset threshold carded | never refused | B8 |
| M17 unset criterion carded | never refused | B8 |
| M18 criterion path tracked | never refused | B8 |
| M19 NO-READ axis names its builder | never refused | B8 |
| M20 unowned count carded | never refused | B9 |
| M21 verdict in the set of three | any truthy verdict | B10 (the verdict's survivor R12) |
| M22 row outside the object set | never refused | B11 |
| M23 object globs as a list | first glob only | every object class has a file (tightened to kill it) |
| M24 tuple name through `const.py` | not consulted | population: tuple, starred, hand count |
| M25 dict axis reads keys | values | population: dict, hand count |
| M26 binary axis two levels a capture | one | population: regex binary, hand count |
| M27 glob stems | file names | population: glob |
| M28 compare axis | Eq not read | population: compare, hand count |
| M29 pairs formula | no halving | population: hand count |
| M30 UNREADABLE fails the run | ok stays true | population: missing symbol, call-built symbol, empty glob |
| M31 `--population` exit follows ok | always 0 | SURVIVED: see `## Unpinned sites` |

(`ev/mutants.txt` on the probe ref is the reviewer's record.) The first handoff's six mutants (missing evaluation, missing previous record, undecided card, unmerged accepted card, one seat in both roles, `--round`'s exit code) were re-run by the reviewer and hold (its rows M1 to M6).

## Unpinned sites

- M31, `--population`'s exit code in `main()`: no self-test arm reaches it, since the arm would need a ref whose objective file names an unreadable axis. Value check instead: in a throwaway clone with `PUMP_DUTY_MODES` renamed to a symbol that does not exist and committed, `python3 tools/audit/check_scopes.py --repo . --population` prints `UNREADABLE pump_duty_mode` and exits 1; at this head it exits 0.
- `prepr.sh`'s diff mutants left two survivors, both on the fall-through return of the enumerator helper in `tools/audit/check_scopes.py` (an enumerator that is an interpreter and no file). Killed: the arm `B5 an enumerator that is an interpreter and no file is refused` goes false with that return flipped, self-test exit 1. The re-run leaves one, `tools/audit/check_scopes.py:208 RETURN_DEL` (the same return deleted): equivalent, since the function then returns None and its one caller tests truth.

## Null control

- A complete record passes: the ported probe's control row (every unset owner value carded, a review at `approve`, every NO-READ with its builder) returns 0 gaps, and a real read with a tracked enumerator returns 0 gaps (row N3), so the new arms do not refuse everything.
- The reviewer's control P0 (all NO-READ, all keep, no cards), accepted at f7efa4be88, is refused at this head with 36 gaps.
- `--round 11` at this head exits 1 naming the two missing files; without `--round` the check exits 0: the refusal is the flag's.
- `--population` reads the ref, not the checkout: the clone in `## Unpinned sites` is the perturbation, and the unperturbed head prints no UNREADABLE line.
- The worked example is the null control on usefulness, and it partly fails: see "Where the function cannot rank what the audits found".

## Figures

- The finder's harness at both ends. The reviewer's probe script (probe.py under ev/ on the probe ref; probes P0 to P8) reads `evaluation_gaps` with four callbacks and a string glob per class, so it does not load at this head; its port to the six-callback signature, with the same perturbations and a control that passes, is `$EXPORT/probe2.py` sha1 14996f7454856a70840d475067c546b94cfb993f. At f7efa4be88 the reviewer recorded all nine accepted (probes.txt beside it); at this head `python3 -I probe2.py` prints the control accepted, P0 to P8 and R12 each refused, and `unexpected: 0`.
- Self-test at this head, 38 evaluation arms and 11 population arms held, exit 0: `python3 tools/audit/check_scopes.py --repo . --self-test`
- The population at this head: 31 axes of which 2 NO-READ (tank volume, house size); `LEVELS: 199`, `PAIRS: 19480`; the optional entities are 50 binary axes (48, 195 and 18696 before main was merged in: two entity keys main added moved the population with no edit to the objective file): `python3 tools/audit/check_scopes.py --repo . --population`
- Round 11 refused at this head with 2 gaps: `python3 tools/audit/check_scopes.py --repo . --round 11`
- Objects the evaluation must give a verdict, 193 at this head (168 at the first handoff): the ported probe's last line, which applies `match` to every glob of `objective.json` `objects`
- Terms, 13: `python3 -c "import json;print(len(json.load(open('dev/audit/config/objective.json'))['terms']))"`
- Decision 0017's length, 491 lines: `wc -l dev/governance/decisions/0017-objective-function.md`
- Policy caps, 0 errors; the corpus aggregate reads 69092 against a ceiling of 69118, unchanged by this round, and `evaluator.md` 27 lines and 361 tokens at its recorded caps: `node tools/policy/policy_lint.mjs --budgets`
- `node tools/policy/policy_lint.mjs` 0 errors; `node tools/policy/brief_lint.mjs` exit 0; `node tools/policy/rules_sync.mjs --check` ok
- Architecture score, dS +0.0000 NULL: `python3 tools/audit/archscore/score.py --diff origin/main`
- Structure ratchet passed: `python3 tests/structure.py`

Standing cost per round is not a figure: neither seat has run. 0017 section 6 states it as a cap.

## Raise justification

The diff touches `dev/governance/config/policy_budgets.json` to record the two caps of one new file, `dev/governance/roles/evaluator.md`, at its measured size; this round rewrote that contract inside the same two caps. No existing per-file cap and no aggregate cap is raised. `budget-raise-gate` still counts the new entries as a raise and stays red until the owner approves (`## Red checks`). The corpus aggregate stands 474 above its recorded cap, of a band of 500.

Payments tried: (1) the contract's first draft put the corpus over its ceiling and was cut to 361 tokens before recording; this round's rewrite (the model sentence, the wider card list, the `ruling` clause) was paid inside the file by cutting the sentence on the orchestrator's contract as an object, which `objective.json`'s role glob already states, and three trims; (2) `CLAUDE.md`'s index row is paid by deleting the history clause of the `SEAT-BLOCK.md` sentence; (3) `dev/audit/README.md` pays for its two cell edits by replacing its three-line restatement of `check_scopes.py`'s rules with one sentence; (4) `orchestrator.md` takes one sentence inside its headroom; (5) folding the evaluator into `plan-review.md` was rejected, since that file sits at both caps; (6) the definition is a decision record, which is uncapped (Decision 11).
Architecture score: dS +0.0000 NULL

## Approval

Pending: the owner's approving review. Every changed policy path is code-owned.

## Red checks

- `budget-raise-gate / budget-raise-gate`: red at the pull request's head a5bbc5ec81 (#3575), by design until the owner's approving review. The gate reads the two new `evaluator.md` entries in `policy_budgets.json` as one raise, though no existing cap moves. Cheaper detector: `tools/pr/prepr.sh` predicts it before the handoff, at no standing cost; nothing cheaper can clear it, because what it waits for is an approval. No owner confirmation was obtained before the push: pending owner confirmation, and the gate holds the merge until it is given.
- `tests / closures`, `tests / fast (3.14)`, `tests / mutation`: red on no commit of this group. The pull request's branch carries main merged in (82fdfd6d99), and with it the commits of #3531 and #3557, where these runs failed: `tests / closures` at cb8e4bb5, `tests / fast (3.14)` at 6ac5807a, a06dc2fe, feb0f3f4, a35771fa and main's merge 50373173d4, `tests / mutation` at 10d8f043, 7bd0caac, abf3b4f9, 6ac5807a, a06dc2fe, feb0f3f4, a35771fa and cb8e4bb5. This group's seven commits before this round (a50010a19e to f7efa4be88) carry no failed run. Rule: for each commit of `git rev-list e23124ff6e..origin/fix/r11-pre-objective-function`, the check runs whose conclusion is `failure`, read from the commit's check-runs listing. Cheaper detector: none exists for this diff, which did not cause them; each is answered in the pull request that turned it red.

## Forward-carry

- The three groups that build the enumerators build to 0017 section 2's definitions (clock, windows, denominators, the NO-READ rule for a partial ledger), add each enumerator to `.github/CODEOWNERS` in the pull request that lands it, and return a definition they cannot meet as a card. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R11-PRE-ROUND-METRICS
- Decision 0017 (`dev/governance/decisions/0017-objective-function.md`) sections 4 and 5 assign this group the two held-out instruments: planted-defect recall, counted after the judge so a plant lost at the verifier or the judge is a miss, with the plants spread over the natural universe and the configuration space and written by a seat that is neither finder, orchestrator nor evaluator; and the two-finder overlap estimate, reported with the two seats' models because same-model seats bias it low. Section 2 and section 5's table also owe from it: `product_green` over the round's window with `gate`'s check count beside it, the `lead_time` clock read from the commit that added the group to the roster, and runner seconds per merge. Control for each: an empty input prints unread, never a value. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R11-PRE-ROUND-METRICS
- Decision 0017 (`dev/governance/decisions/0017-objective-function.md`) section 2 defines `tokens_per_change` for the token ledger this group builds: every usage field kept apart, a seat keyed by group, role and dimension, and the term printed NO-READ, never a partial, while one seat class is unledgered. Section 6, "Cannot read", owes from the same ledger a refusal in `tools/audit/check_scopes.py --round`, with its self-test arm, of an evaluator or reviewer seat that appears in the graded round's ledger. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R11-PRE-TOKEN-LEDGER
- Decision 0017 (`dev/governance/decisions/0017-objective-function.md`) sections 2 and 4 owe from this group's convergence records: found-by and owning dimension per escape (`none` is a value), the cause of an injected bug named by the root-cause seat and never the fixer, the per-step denominator with an off-cadence dimension reading 0, an examining pass over a late merge reporting its denominator, and a re-report naming the fix it follows (link 3, a fix that did not fix, has no other read). Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R11-INTAKE-R10-RESIDUE
- Decision 0017 (`dev/governance/decisions/0017-objective-function.md`) section 1 owes these brief edits from this group. D12: its universe is `python3 tools/audit/check_scopes.py --repo . --population` plus the card and the blueprints; it declares the levels of the two NO-READ axes (tank volume, house size) in `dev/audit/config/objective.json` `population`; it keeps a cell ledger printing each level and pair with its source, its asserting test or `not run`, where a run that asserts nothing examines nothing. The actuator-write dimension draft: a cell ledger over write and hold sites times plan states, the target being the plan's computed value and never a document. D0 and D15: the same-information oracle step (exogenous inputs at decision time, the measured house), the realised-cost record per install-day and the model gap beside both. D1, D2, D8, D11 and D15: the census or list section 1's table marks NO-READ. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R11-INTAKE-R10-RESIDUE
- Decision 0017 (`dev/governance/decisions/0017-objective-function.md`) section 1's table reads D6's distance from `tests/doc_claims.py` only for the claims it registers; a claim outside its register is NO-READ, and this group's full-scope step owes the enumeration of claims the register does not hold. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-D5-D6-FULL-SCOPE

n/a: Orchestrator ruling 2026-11-14: items 36086213 and 916aff2d re-routed from R10-DIMENSIONS-FULL-COVERAGE (carries-open, not receivable) to R11-INTAKE-R10-RESIDUE.

## Friction

- frugal-guard: cost: the cloud container's read guard refused every inline file read after the fifth, so the checker's code was written and mutated by subagents to a written spec and verified by its self-test, the ported probes and the mutant table, not by reading. Carry: dismissed: the guard worked as configured and the brief prescribes the route
- step-ref: cost: `handoff-wip/r11-pre-objective-function` still held the first handoff's resolved BLOCKED commits, so this round's step is a merge on top of them (BLOCKED.md removed) and the linear head goes to `handoff/`. Carry: dismissed: one-off residue of the first handoff
