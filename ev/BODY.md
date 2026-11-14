policy: decision 0017, the objective function, and the evaluation that opens a round (R11-PRE-OBJECTIVE-FUNCTION)

Defines the function the owner asked for on 2026-11-13 as decision 0017, adds the evaluator seat that grades every dimension, contract, rule, instrument and gate against it before a round's finders, and makes `tools/audit/check_scopes.py --round N` refuse a round start whose evaluation is missing, incomplete or undecided. `audit-find.js` passes its round, so the refusal sits in the instrument that already refuses a bad scope table.

What it does not do: build an enumerator of a term. Of the thirteen terms only `first_pass` has a working one; `generality` now has its denominator (`check_scopes.py --population`) and no numerator. Decision 0017 section 4 claims convergence for no round yet, lists seven assumptions no sensor reads, and says the function moving the right way does not show fewer objective bugs.

## Repair round 3: the delta verdict answered

Verdict: `Fix review: blocked d3c536efe116fb7581c9ca80572ea5039d4991d5 sufficiency`, as the dispatch brief quotes it whole. Each answer is in `tools/audit/check_scopes.py`, `dev/audit/config/scopes.json`, `dev/audit/config/objective.json` or decision 0017, never only here.

**Block**

1. The record directory: `scopes.json`'s exclusion of round records now reads `dev/audit/{rounds,yardstick}/**`, one entry, because an entry of its own for a directory that holds no file yet is refused as naming nothing. The self-test adds round 10's objective record and round 11's evaluation to the tree and has coverage pass on the live scopes, and with the directory taken out of that entry has coverage refuse both by name (mutant R12). The verdict's own scenario at both ends is in `## Figures`. 0017 section 6, "Reads", says the records are excluded from every universe.
2. The two carries are roster-side (the dispatch seat folds them by `carry_fold.py`). Both items stand in `## Forward-carry` with their text unchanged; the landed check's result at this head is in `## Figures`.
3. The band: `objective.json` `thresholds` gains `band_model_gap` (unset, no proposal; unit a share of the cell's `C_real`), so `--round` asks for its card like every other unset threshold. 0017 section 1 defines it: a cell's model gap is inside its band when it is at most that share of the cell's `C_real`. Section 2 names the rule by which a mean over cells moved (`regret`, its floor, the model gap): two standard errors of the difference of the two means, each from the spread of its own cells and install-days; and says `band_model_gap` compares no two rounds. Decisions 19 and 20 below.

**Also owed at the re-handoff**, each built here

- The builder name: 0017 and `objective.json` name R11-INTAKE-R10-RESIDUE, the group that holds the two carries, wherever they named R10-DIMENSIONS-FULL-COVERAGE (the grep in `## Figures` finds none left). The alternative, a sentence making the roster the authority over the table, lost: a reader would still be sent to a group that holds nothing.
- The last consequence now agrees with section 2 and the check: the ruling on a card sets the value or leaves it unset, the round starts either way, and an unset value keeps what needs it undecided. An accepted card answering a threshold or a criterion that `objective.json` still leaves unset is refused (the verdict's N8; mutant R8).
- A NO-READ's builder, of a term or of a population axis, is a card of the evaluation or a group of the newest roster tracked at the ref that `roster_lib.carry_receivable` passes: the rule a carry's destination is already checked by, imported and not copied. An unknown name, a `done` group, a `carries-open` group and a sink are each refused, and so is every group name when the ref holds no roster (N1; mutants R1, R2, R10, R11). Design choice: `carries-open` is refused though `is_open` passes it, since its pull request merged and no seat is left to build; that is why the record could no longer name R10-DIMENSIONS-FULL-COVERAGE.
- A `remove` is refused when its evidence says NO-READ in any spelling: the text is compared after case folding with every non-letter dropped, anywhere in the string. Corpus: 140 generated spellings (4 casings, 7 separators, 5 wrappings and positions), all refused; a `remove` on "yield 0 in rounds 6 and 7" passes (N2, N2b; mutant R3). The alternative, a structured field on a `remove` row, lost: it widens the record the owner read and still accepts NO-READ evidence beside a filled field.
- A read's enumerator names a tracked script (`.py`, `.mjs`, `.js`, `.sh`), so `CLAUDE.md by hand` is refused (N4; R4), and a read is a finite number or a non-empty dict of them: NaN, infinity, an empty dict and a dict holding a non-number are refused (N5, the verdict's survivors R3 and R4; mutants R5 to R7). What stays unreadable is in 0017 section 6, "Cannot read": a tracked script that did not print the number beside it.
- `evaluator: "orch-r10"` still passes; 0017 section 6 now names that spelling as the limit (N3, kept as an accepted probe).
- The verdict's survivors: R3 and R4 above; R35, a NO-READ axis with no reason, has its arm (mutant R9); R48, the untracked source file, is pinned by the line it prints, `UNREADABLE a: p/none.py is not tracked at the ref`, which the other exception does not print (mutant R16).
- The optional-entity axis: traced. `CONF_WEATHER_ENTITY` is required in both steps that ask for it (`vol.Required` at setup, `required=True` in the options table), so its absent level is a cell no install has; and `CONF_AWAY_RETURN_ENTITY` is imported by the flow and named in no call, so no step presents it. The axis is now kind `name`: the identifiers the module uses outside its imports, less each one a call marks required (`X.Required(key)`, or the key beside `required=True`) and none marks optional. A key required in one step and optional in another stays, and so does one the rule cannot place. The population moves from 50 to 48 binary axes. 0017 section 1 states the rule.

## Repair round 2: the red `instrument-self-tests` step

`governance / instrument-self-tests`, step `python3 -I tools/pr/dependabot_merge.py --self-test`, was red at the pull request's head 03c26201c7 and green at its merge base: this group's commit 8eb5c160b1 owned the two round records by glob lines in `.github/CODEOWNERS`, and that reader refuses any pattern that is not an anchored path (its own arm "a glob refuses").

Fix: the objective record and the start evaluation move from a round's evidence directory to `dev/audit/yardstick/round<N>/`, owned by one anchored directory line. `check_scopes.py --round` reads them there (three path strings, the self-test's fixture included), 0017 section 6 names the directory; `dev/audit/README.md` does not, because its token cap is compared exactly and has no headroom for the layout line (it read 20 over). The reader and its refusal are not touched.

Alternatives, and why each lost: (a) teach the Dependabot reader a `*` segment: it weakens the check the step exercises, whose refusal is what keeps an auto-merge decision from resting on a pattern it mis-reads; (b) one exact line per round: a round whose line nobody added is unowned and nothing refuses it, and it enumerates cases where a directory closes the class; (c) own all of `dev/audit/rounds/`: every finder report and harness would then need the owner's review, a policy change nobody asked for; (d) drop the two lines: 0017 section 5 says the two records are code-owned.

## Repair round: the blocked verdict answered by number

Verdict: `verdict.md` on `probe/revt-r11-pre-objective-function-3a4f648d` (4ec1b989cc), `Fix review: blocked f7efa4be88 sufficiency`. Each answer is in the decision record, `dev/audit/config/objective.json` or `dev/governance/roles/evaluator.md`, never only here.

**Block**

1. Thresholds: `objective.json` `thresholds` held five fields at that round (`product_green_floor`, `closure_slip_ceiling`, `band_lead_time`, `band_closure_slip`, `band_tokens_per_change`), each `value` null with the orchestrator's `proposed` beside it, and `owner_criteria` one field per owner-decided dimension. 0017 section 2, "The owner's values are fields of `objective.json`": a null is unset, every comparison or result needing it is undecided, and the evaluation cards it. `check_scopes.py --round` refuses an unset one with no card (arms B8).
2. NO-READ in the ordering: 0017 section 2, "A NO-READ is undecided, never a tie": a term NO-READ on either side has neither moved nor held; a first read is a baseline; while any layer-1 term is NO-READ, rules 2 to 4 rank nothing and only read-building changes and owner-carded ones are kept. Rule 1 now reads "every layer-1 term is read on both sides and none is worse". This is the stricter of the two readings the verdict names; it is listed for the owner below.
3. `regret`: 0017 section 1 defines four costs. `C_same`, the same-information oracle, takes only exogenous inputs at decision time (published prices, the provider's forecast as issued, sensor readings to then, the configuration) on the measured house (the response and draw the window's sensors recorded, never the learned model). `regret = C_real - C_same` is all removable loss; the floor is `C_same - C_fore` (the provider's forecast error), reported beside it and outside it; the model gap `|C_real - C_model|` is part of the term (zero regret needs the gap inside the band). The residual rows of sections 1 and 2 are split on that line. What stays unattainable is said: the draw no history predicts lands in `regret`.
4. Population: `python3 tools/audit/check_scopes.py --repo . --population` prints every axis with its levels from the tracked source `objective.json` `population` names (the flow's option tuples, the optional entity keys of `config_flow.py` as present or absent, `translations/`, `hacs.json`'s floor, `tests/profiles.py`'s price shapes and climates). The cells are every level and every pair of levels from two axes; an interaction of three or more axes is the stated residual. Tank volume and house size have no tracked levels and are NO-READ axes with their builder. Counts in `## Figures`.
5. Dimension table: 0017 section 1 gains two columns, the enumerator of the distance (a tracked command, or NO-READ with what would read it and the group that builds it, or undecided on an unset `owner_criteria` field) and the floor, for all sixteen dimensions.
6. Builders: every NO-READ product read names a live group in 0017 (section 1 table, section 2 table, sections 4 and 5): the oracle harness, realised-cost record, model gap, the actuator-write dimension's cell ledger, D12's axes and cell ledger go to R11-INTAKE-R10-RESIDUE (renamed in repair round 3 from R10-DIMENSIONS-FULL-COVERAGE, which is not receivable); the held-out instruments and the window reads to R11-PRE-ROUND-METRICS; the ledger to R11-PRE-TOKEN-LEDGER. Each `## Forward-carry` item below names decision 0017 and its section and stands alone.

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
13. **CODEOWNERS gains four lines**: the config, `check_scopes.py`, and the record directory `dev/audit/yardstick/` (repair round 2: one anchored line where two glob lines stood, so the count of added lines is three).
14. **The supported install population** is set (Carry 4), and its cells are levels and pairs. Alternative at review: a narrower named list; or triples, at a larger denominator.
15. **The comfort bounds** are set (Carry 4). Alternative: a fixed band the owner states.
16. **Acceptance criteria**: `owner_criteria` D4, D5, D9 and D10 are null; each is a card at round 11's evaluation. D7's is decision 0015.
17. **Adding a term or an object class removes one**, after this record lands. Alternative: no such rule.
18. **A NO-READ layer-1 term stops the ordering** (block item 2). Alternative: rank on the terms that are read, which lets `first_pass` alone rank changes while its catchers are unread.
19. **The model gap's band, `thresholds.band_model_gap`: no value proposed.** It is the share of a cell's `C_real` inside which the model's predicted cost counts as agreeing with the meter. No measurement in the tree gives a basis: the meter's own error is the natural floor for it, and no record of that error exists. Alternatives: a fixed currency amount per cell, which does not scale across installs; a share of `C_same`, which needs the oracle before the gap can be judged.
20. **A mean over cells moved beyond two standard errors of the difference of the two means.** It is the share rule's analogue and needs no owner value. Alternative: a relative band as a fourth `band_` field.
21. **A NO-READ's builder must be a group a carry can still be routed to, or a card.** So a `carries-open` or `done` group named as builder refuses the round start until the record names a live group or cards the read. Alternative: any group the roster lists, which lets a finished group stand as the builder of a read it did not build.

## Head
`c8ad0cc3c1f5dd83bedbd6798ef414bcadf28f8e` merges the authored code head `ebf8e522df81ad91146684aa6eac370c2fd7b9d3`.

ebf8e522df81ad91146684aa6eac370c2fd7b9d3 (measured 2026-11-14 16:16 UTC; origin/main at 9fdba3b854; `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main is not merged in. It is the pull request's head d3c536efe1 plus repair round 3's two commits. Figures marked "round 3" in `## Figures` were taken at this head; the unmarked ones were taken at 018b520580 or 15691dbd56 and this round's diff does not reach them.)

## Mutation proof
- Repair round 3: one mutant per predicate this round added, each a unique-string change to `tools/audit/check_scopes.py` (R12: to `dev/audit/config/scopes.json`), the self-test run in place, the file restored and its sha256 compared. Driver: `$EXPORT/mutants3.py` sha1 c00da835baece78c78a8cc30eb71d0e5885d21c0 (scratch; a one-off). Unmutated: exit 0 before and after. 19 mutants, 18 killed on the first run; R19 survived, its arm was tightened (a name that only starts like the pattern) and it is killed at this head.

| mutant | predicate became | self-test arm that goes false |
|---|---|---|
| R1 a builder is carry-receivable | every group | B6 a builder the roster cannot hand a build; B8 a NO-READ axis whose builder |
| R2 a term's builder is checked | never | B6 a builder the roster cannot hand a build; B6 with no roster |
| R3 NO-READ in any spelling | the old upper-case prefix test | B7 a removal on a NO-READ is refused in every spelling |
| R4 the enumerator is a script | any tracked file | B5 a tracked document is no enumerator |
| R5 a read is finite | NaN and infinity allowed | B5 a value that is no finite number |
| R6 a dict read is non-empty | empty allowed | the same arm |
| R7 a dict read holds numbers | any values | the same arm |
| R8 an accepted card's value is set | never refused | B8 an accepted card for a value still unset |
| R9 a NO-READ axis carries its reason | only the builder checked | B8 a NO-READ axis with no reason |
| R10 an axis's builder is checked | never | B6 with no roster; B8 a NO-READ axis whose builder |
| R11 an axis's `card:` builder is a card | any `card:` | B8 a NO-READ axis whose builder |
| R12 the exclusion names the yardstick directory | `dev/audit/rounds/**` alone | the round's records are covered once written |
| R13 required keys leave the name axis | none leave | population: a name axis drops a key required everywhere or never presented |
| R14 a key optional somewhere stays | every required key leaves | the same arm |
| R15 `required=False` is not required | any `required=` keyword | the same arm |
| R16 an untracked source is named | the check deleted | population: an untracked source file is UNREADABLE by name |
| R17 `X.Required` marks its first argument | only `required=True` calls | population: a name axis |
| R18 an unmarked row call is optional | never | the same arm |
| R19 the pattern is the whole identifier | a prefix match | the same arm, after its fixture gained a longer name |
- Repair round 2: the perturbation is the two glob lines restored, which is the tree at 018b520580. There `python3 -I tools/pr/dependabot_merge.py --self-test` exits 1 with `ValueError: CODEOWNERS pattern '/dev/audit/rounds/*/EVALUATION.json' is not an anchored path; this reader refuses it`; at this head it prints `dependabot_merge self-test: 0 failure(s)` and exits 0.

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

- Round 3, `prepr.sh`'s draw over the diff's added lines (the self-test in place as its command) left two survivors. `tools/audit/check_scopes.py:43 CONST_SWAP`, the position at which the `seat` directory joins `sys.path` (0 became 1): equivalent, since `roster_lib` is the only module read from that directory and no other path entry holds one; the line itself is pinned by CI's `python3 -I tools/audit/check_scopes.py --self-test --repo .`, where isolated mode leaves the script's directory off the path and the import fails without it. `tools/audit/check_scopes.py:234 RETURN_DEL`: the fall-through return of the enumerator helper, the same equivalent the entry below records at its earlier line.

- M31, `--population`'s exit code in `main()`: no self-test arm reaches it, since the arm would need a ref whose objective file names an unreadable axis. Value check instead: in a throwaway clone with `PUMP_DUTY_MODES` renamed to a symbol that does not exist and committed, `python3 tools/audit/check_scopes.py --repo . --population` prints `UNREADABLE pump_duty_mode` and exits 1; at this head it exits 0.
- `prepr.sh`'s diff mutants left two survivors, both on the fall-through return of the enumerator helper in `tools/audit/check_scopes.py` (an enumerator that is an interpreter and no file). Killed: the arm `B5 an enumerator that is an interpreter and no file is refused` goes false with that return flipped, self-test exit 1. The re-run leaves one, `tools/audit/check_scopes.py:208 RETURN_DEL` (the same return deleted): equivalent, since the function then returns None and its one caller tests truth.

## Null control

- Round 3, the record directory: the same commit of a round-10 objective record under `dev/audit/yardstick/` makes the default run exit 1 at d3c536efe1 and 0 at this head (`## Figures`), and inside the self-test the arm's own control takes the directory out of the exclusion and has both records refused by name.
- Round 3, the new refusals do not refuse everything: the ported probe's control (every term NO-READ with a live builder, every object `keep`, a deferred card per unset value, ten at this head) returns 0 gaps at both ends, and N3 stays accepted.
- Round 3, the name axis: its fixture holds a key of each kind, and the arm states the six that stay; R13 (nothing leaves) and R14 (too much leaves) each turn it false.

- A complete record passes: the ported probe's control row (every unset owner value carded, a review at `approve`, every NO-READ with its builder) returns 0 gaps, and a real read with a tracked enumerator returns 0 gaps (row N3), so the new arms do not refuse everything.
- The reviewer's control P0 (all NO-READ, all keep, no cards), accepted at f7efa4be88, is refused at this head with 36 gaps.
- `--round 11` at this head exits 1 naming the two missing files; without `--round` the check exits 0: the refusal is the flag's.
- `--population` reads the ref, not the checkout: the clone in `## Unpinned sites` is the perturbation, and the unperturbed head prints no UNREADABLE line.
- The worked example is the null control on usefulness, and it partly fails: see "Where the function cannot rank what the audits found".

## Figures

- Round 3, the verdict's scenario at both ends. In a throwaway clone, `dev/audit/yardstick/round10/OBJECTIVE.json` committed, then `python3 tools/audit/check_scopes.py --repo .`: at d3c536efe1 it prints `FAIL coverage` with `in no universe and not excluded: dev/audit/yardstick/round10/OBJECTIVE.json` and exits 1; at this head `ok coverage` with `unclassified=0` and exit 0.
- Round 3, the finder's probes at both ends. The delta verdict's probe script is on no ref this seat can fetch (the probe ref holds round 1's evidence), so its named probes are ported from the verdict's text: `$EXPORT/probe3.py` sha1 d76742dc8767fcaafe3759de5a35ea9516c84c81, `python3 -I probe3.py . <ref>`. At d3c536efe1: control accepted, N1, N2, N2b, N4, N5 and N8 accepted (the defect), N3 accepted, R3, R4 and R35 refused. At this head: control and N3 accepted, the other nine refused, `unexpected: 0`. N6 and N7 are not ported: the verdict names them without their input.
- Round 3, the class's seams for block item 1. Rule: every path string `check_scopes.py` builds for a record it reads under `--round`, which is the one function `records()`; both of its paths are in the arm. For the builder name: `git grep -c R10-DIMENSIONS-FULL-COVERAGE -- dev/governance/decisions/0017-objective-function.md dev/audit/config/objective.json` prints nothing and exits 1.
- Round 3, self-test at this head: 47 evaluation arms and 13 population arms held, the two yardstick arms true, exit 0: `python3 tools/audit/check_scopes.py --repo . --self-test`
- Round 3, the default run at this head exits 0, and `--round 11` exits 1 with 2 gaps, each a record missing under `dev/audit/yardstick/`: `python3 tools/audit/check_scopes.py --repo . --round 11`
- Round 3, the population at this head: 31 axes of which 2 NO-READ; `LEVELS: 195`, `PAIRS: 18696`; the optional entities are 48 binary axes, `CONF_WEATHER_ENTITY` and `CONF_AWAY_RETURN_ENTITY` having left (199, 19480 and 50 at d3c536efe1): `python3 tools/audit/check_scopes.py --repo . --population`
- Round 3, thresholds, 6, each unset: `python3 -c "import json;print(len(json.load(open('dev/audit/config/objective.json'))['thresholds']))"`
- Round 3, decision 0017's length, 508 lines: `wc -l dev/governance/decisions/0017-objective-function.md`
- Round 3, policy caps, 0 errors; the corpus aggregate reads 69092 against a ceiling of 69118, unchanged by this round (0017 is uncapped), and `evaluator.md` is untouched at its caps: `node tools/policy/policy_lint.mjs --budgets`
- Round 3, `node tools/policy/policy_lint.mjs` exit 0; `node tools/policy/brief_lint.mjs` exit 0; `node tools/policy/rules_sync.mjs --check` ok; `python3 -I tools/pr/dependabot_merge.py --self-test` prints `0 failure(s)`
- Round 3, architecture score against the merge base 50373173d4, dS +0.0000 NULL: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`. Against `origin/main` itself the same command prints `dS -0.0023 WORSENS (coord_footprint 2499->2503)`: that is main's own newer commits read two-dot, since `git diff $(git merge-base origin/main HEAD)...HEAD -- custom_components` is empty.
- Round 3, structure ratchet passed: `python3 tests/structure.py`
- Round 3, the gate's scope: `MODE: SCOPED`, and `scope.run` names `tests/entities.py` alone.
- Round 3, the landed check: `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster landed --body <this body> --topic r11-pre-objective-function` prints `CARRY-LANDED: 0 missing` with the roster branch at 806bc58a1d (the delta verdict read two missing at b9719b9985; the dispatch seat folded them)

- Round 2, the red step's command at this head, exit 0, last line `dependabot_merge self-test: 0 failure(s)`: `python3 -I tools/pr/dependabot_merge.py --self-test`
- Round 2, ownership of the moved records read by the same reader's `owned()` over the tree's `.github/CODEOWNERS`, given three paths (round 10's objective record and round 11's start evaluation at their new paths under dev/audit/yardstick/, and as the null control round 6's tracked harness codeowners_gap.py under dev/audit/rounds/): it returns the first two and not the control, so the directory line owns the records and no round evidence.
- Round 2, the class's seams. Rule: every pattern of `.github/CODEOWNERS` the reader refuses, which the self-test's arm "the tree's CODEOWNERS parses" enumerates by raising on the first. At 018b520580 it raised on the first of the two glob lines; at this head it raises on none. Both seams closed in this diff; no other glob line exists (`git grep -n '[*?[]' -- .github/CODEOWNERS` prints comment lines only).
- The finder's harness at both ends. The reviewer's probe script (probe.py under ev/ on the probe ref; probes P0 to P8) reads `evaluation_gaps` with four callbacks and a string glob per class, so it does not load at this head; its port to the six-callback signature, with the same perturbations and a control that passes, is `$EXPORT/probe2.py` sha1 14996f7454856a70840d475067c546b94cfb993f. At f7efa4be88 the reviewer recorded all nine accepted (probes.txt beside it); at this head `python3 -I probe2.py` prints the control accepted, P0 to P8 and R12 each refused, and `unexpected: 0`.
- Objects the evaluation must give a verdict, 193 at this head (168 at the first handoff): the ported probe's last line, which applies `match` to every glob of `objective.json` `objects`
- Terms, 13: `python3 -c "import json;print(len(json.load(open('dev/audit/config/objective.json'))['terms']))"`

Standing cost per round is not a figure: neither seat has run. 0017 section 6 states it as a cap.

## Raise justification

The diff touches `dev/governance/config/policy_budgets.json` to record the two caps of one new file, `dev/governance/roles/evaluator.md`, at its measured size; this round rewrote that contract inside the same two caps. No existing per-file cap and no aggregate cap is raised. `budget-raise-gate` still counts the new entries as a raise and stays red until the owner approves (`## Red checks`). The corpus aggregate stands 474 above its recorded cap, of a band of 500.

Payments tried: (1) the contract's first draft put the corpus over its ceiling and was cut to 361 tokens before recording; this round's rewrite (the model sentence, the wider card list, the `ruling` clause) was paid inside the file by cutting the sentence on the orchestrator's contract as an object, which `objective.json`'s role glob already states, and three trims; (2) `CLAUDE.md`'s index row is paid by deleting the history clause of the `SEAT-BLOCK.md` sentence; (3) `dev/audit/README.md` pays for its two cell edits by replacing its three-line restatement of `check_scopes.py`'s rules with one sentence; (4) `orchestrator.md` takes one sentence inside its headroom; (5) folding the evaluator into `plan-review.md` was rejected, since that file sits at both caps; (6) the definition is a decision record, which is uncapped (Decision 11).
Architecture score: dS +0.0000 NULL

## Approval

Pending: the owner's approving review. Every changed policy path is code-owned.

## Red checks

- `governance / instrument-self-tests`, step "Show the Dependabot merge decision refusing its own fixtures": red at 03c26201c7, introduced by this group (the glob lines of 8eb5c160b1), fixed at this head as `## Repair round 2` states. Cheaper detector: the step's own command, under a second locally. No local path ran it: `python3 tools/pr/ci_predict.py --base 50373173d4 --only self-test-reads --record-self-tests` at 018b520580 prints `no closures, fast, governance or instrument red predicted` with its own caveat "a data-file read is not seen unless a changed file's own self-test makes it", though `tools/ci/selftest_closures.json` lists `.github/CODEOWNERS` among that self-test's files. Process state (c): prepr's prediction ran and could not see a self-test that reads a changed data file. The detector that would have caught it is the predictor keyed on `selftest_closures.json`'s `files`; its standing cost is the selected self-tests' seconds per prepr run. It is not built here: the predictor is outside this group's seam, and the class is `R10-SELFTEST-RED-INTRODUCED` in `dev/audit/config/bugclasses.json`, whose owner decides the barrier.
- `tests / closures` locally: repair round 2's `tools/pr/prepr.sh` ran with `PREPR_SKIP_CLOSURES=1`, by that round's brief, while #3578 (R10-HOTFIX-FEATURES-WEEKEND-CLOCK) was unmerged. Repair round 3's run set no skip: its closures step printed `skip: the diff cannot be scoped, so CI re-records every closure`, and its prediction step printed `no closures, fast, governance or instrument red predicted`.
- `budget-raise-gate / budget-raise-gate`: red at the pull request's head a5bbc5ec81 (#3575), by design until the owner's approving review. The gate reads the two new `evaluator.md` entries in `policy_budgets.json` as one raise, though no existing cap moves. Cheaper detector: `tools/pr/prepr.sh` predicts it before the handoff, at no standing cost; nothing cheaper can clear it, because what it waits for is an approval. No owner confirmation was obtained before the push: pending owner confirmation, and the gate holds the merge until it is given.
- `gate`: red at the pull request's head d3c536efe1 (two runs, 15:13 and 16:00 UTC on 2026-11-14). Its log names one failing check, `FAIL budget-raise-gate / budget-raise-gate: failure (this run)`, so it is the line above read through the aggregate: it clears with the owner's approving review and has no cheaper detector than the one that line names. Introduced by this group, by design.
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
