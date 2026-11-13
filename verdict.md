Fix review: blocked f7efa4be885e53556a6bfa02ad22a9b22c417b2a sufficiency: the ordering, the regret oracle and the install population cannot be derived from decision 0017 and the tree alone

bus-nonce: 3a4f648d09f0f438f5d5f8d9c7aa3f2d

Round 1 of this review. Measured at f7efa4be885e53556a6bfa02ad22a9b22c417b2a from a detached worktree; `git ls-remote` printed the same head for `handoff/r11-pre-objective-function` before this verdict was written. Body read: BODY.md at d578ba0b35179fa4f4bd6fc0e61672783767e850. Roster carries read at `handoff/audit-r10-roster` ec9295930700401e83d86f2e98a1648be84d7d12.

## Block

The mechanism half (the `--round` refusal, its self-test, the playbook pointer) holds and is not the block. The block is the definition's sufficiency, on the brief's fifth and seventh points. Each item names the sentence that would clear it.

1. **Three thresholds live only in the handoff body.** 0017 section 2 decides "moved" for `lead_time`, `closure_slip` and `tokens_per_change` by "the owner's percentage", and targets `product_green` at "the owner's floor" and `closure_slip` at "the owner's ceiling". No value is in 0017, `objective.json` has no field for one, and 0017 does not say where the owner's value is recorded; the values proposed (0.90, 0.2 days per day, 20%) are body Decisions 1 to 3, which a reader of the file and the tree never sees. So ordering rules 2 and 3 cannot be applied from the file for three of the four layer-2 and layer-3 terms. Clears with: a field per threshold in `objective.json`, and one sentence that an unset one makes the comparison undecided and is carded (section 1 already says this for a dimension's missing criterion, and only for that).
2. **The ordering does not say how a NO-READ compares.** "A round holds layer 1 when no term is worse" is undefined when a term is NO-READ on one or both sides, which at round 11's baseline is every layer-1 term (the body: twelve of thirteen NO-READ). Read one way nothing is ever admissible; read the other, from round 12 `first_pass` alone ranks process changes while both catchers section 5 names for its false move (`injected`, `escapes`) are NO-READ. A reader cannot tell which the owner meant. Clears with one sentence in section 2.
3. **`regret`'s information set is not defined, and as written the integration's own model error lands in the floor.** The target is "0 against the same-information oracle" for "the same prices, weather, house and comfort bounds". The file does not say whether "information" is the exogenous input at decision time (published prices, the provider's forecast, sensor readings) or the integration's own forecasts and learned house model, nor whether "house" is the measured house or the model of it. Under the second reading a wrong demand forecast or a mis-identified thermal model costs zero regret, which is savings defined against the integration's own model. The residual row adds to this: it lists "forecast error in price and weather, sensor error" as irreducible for a term whose oracle by definition shares that information, so the floor and the removable loss are not separated (the provider's forecast error is floor; the integration's own demand and house model error is removable). The measured-against-modelled gap, the one read that would catch the own-model case, is named as D0's and as a catcher in section 5 but is in no term's definition or target and has no enumerator and no builder. Clears with: the information set and "house" defined, the residual split along that line, and the gap made part of the term.
4. **The install population is not enumerable from the file.** Section 1 defines it by the configuration flow (enumerable: control kind, tank and valve layout, price source, unit system) and then makes the cells the product of axes the flow does not enumerate: climate, house and tank size, tariff and price shape have no levels, Home Assistant version has no range, and the levels are said to be "each enumerated in D12's scope", which this diff does not change (`git diff` touches no dimension brief) and which D12's brief does not carry today (`ev/tree_claims.txt`: its axes are layout and heat-pump kind). `generality`'s denominator is therefore whatever bins the reader picks. Clears with: the rule that fixes each axis's levels from tracked files (the flow's option lists, `tests/profiles.py`, the translations directory, the manifest's version floor) or the command that prints the cells.
5. **Section 1's dimension table has an end state per dimension and no distance, enumerator or floor per dimension.** The owner's first carry asks, for every dimension, the perfect result "each with the measured distance from it". The file gives distance and residual per term only; a dimension's distance is reachable only through `coverage` and `escapes`, which measure examination and reports, not the stated result. For D2, D3, D7, D8, D9, D10, D11, D14 and D15 the perfect result names no command that would print how far the code is from it and no NO-READ. Clears with: a column naming the enumerator or NO-READ and what would read it.
6. **Three product reads are NO-READ with no builder, and two of the three carries do not name what they carry.** The brief asks that every enumerator be a tracked command or name the roster group that builds it. `regret` ("none whole … no record holds realised cost per install") and `operation` ("none. The actuator-write dimension, once briefed") name no group; the same-information oracle, the realised-cost record, the write-and-hold cell ledger and D12's axes and cell ledger ("D12's brief must gain these") are carried to no brief. At ec92959307 the carries on R11-PRE-TOKEN-LEDGER and R10-DIMENSIONS-FULL-COVERAGE open "The same, for …" with no antecedent in their own group: neither names decision 0017 or its section, so the control the next stage needs is not stated where that seat reads (`fix-review.md` step 10). Only R11-PRE-ROUND-METRICS's carry is self-standing.

Also owed at the re-handoff, on this diff's own instrument, none the block by itself (`ev/probes.txt`, `ev/mutants.txt`):

- The evaluator's independence is a string compare. `evaluator: "orchestrator-r10"` and `evaluator: "the orchestrator"` with `reviewer: "Orchestrator"` are accepted (probes P1, P2); only the exact token `orchestrator` is refused. Nothing reads who dispatched the seat, whether it worked the graded round, or that the reviewer returned `approve`: `reviewer` is a name, not a verdict.
- 0017 says who may not write the owner's decision (the evaluator, `evaluator.md` last paragraph; the orchestrator "never edits them", section 5) and names nobody who does; section 6 has the orchestrator write `OBJECTIVE.json` while section 5 says it never edits a round's objective record. One of the two sentences is wrong.
- `merged` accepts any ancestor of the ref: an accepted card naming the repository's root commit passes (P3). Nothing ties the commit to the card.
- A `value` whose `enumerator` is `by hand` passes, as does a null value (P4, P5), against section 6's "per term a value with the enumerator that printed it".
- A `remove` on evidence `NO-READ: none` passes (P6), against section 3's "Never on a NO-READ".
- Section 6's "every `unowned` item, and every owner-decided result with no written criterion, yields a card" is checked by nothing: the all-keep, all-NO-READ, zero-card record passes (P0, P7). That record is what round 11's start will most cheaply be.
- Survivor of my own: with the verdict's membership in keep/change/remove untested, the self-test still passes (`ev/mutants.txt` R12). A verdict of any other word with a card is accepted under that mutant; no arm pins the set.
- The object set is the 168 guide, contract, rule, brief and workflow files. `CLAUDE.md`, `.claude/workflows/*.js` (the files that run a round, `audit-find.js` among them), `.claude/hooks/`, `.claude/skills/`, and every script with no guide under `tools/audit/seat/instruments/` (`policy_lint.mjs`, `brief_lint.mjs`, `stamp.py`, `closure.py`, `structure.py`, `mutation_table.py`, `budget_raise_gate.py`, `carry_audit.py`) get no verdict, so "every dimension, contract, rule, instrument and gate" is narrower than the machinery.
- 0017's Context cites the two pre-studies at `dev/audit/rounds/round10/`; neither is in the tree at this head (the body says they are on step refs), and `operation` is assigned to "the actuator-write dimension the coverage audit proposes". The universe is defined in the file, so the term survives, but the citation resolves to nothing.

## What holds

- End states exist: per dimension (section 1), per term and for the process (section 2's second table and "the perfect round"). The file does not define directions only.
- The function is anchored on `custom_components/` and `blueprints/` at the close; perfect code is the conjunction of every dimension's result, the completeness term `unowned`, and the three product terms.
- The chain is six links with a measure and a failure chance each, and the file states that "one round guarantees perfect code under no condition this record can check". It does not make the stronger claim; section 5 claims section 4 for no round until the held-out checks exist.
- The flat-price null control and the perfect-foresight bound are in the definition of `regret`; comfort bounds are the delegated ones, and a plan that leaves one is an `operation` defect, never a saving.
- Each process term has its residual separated from removable cost.

## The convergence argument

The inequality N' <= (1 - p(1 - q)) N + g is right under its own terms. It does not follow that the function moving the right way means fewer objective bugs. Unstated assumptions:

1. **p is an infimum over bugs and the sensor measures a mean.** The geometric rate needs the least per-bug detection chance to be positive; planted-defect recall estimates the average over kinds someone thought to plant. Survivors of each round are selected for low p, so the tail's rate is not the measured recall, and a kind the finder model cannot see has p = 0 with no sensor moving.
2. **The two-finder estimate assumes independent finders with equal catchability.** Two seats of one model on one brief are positively correlated, which biases (n1 + 1)(n2 + 1) / (m + 1) - 1 low; the "escapes are seen" sensor then reads better than the code is.
3. **Found means survived the verifier and the judge.** A real defect voided or refuted is lost with no link and no term; recall is "found / planted" without saying at which stage found is counted.
4. **q counts injection per bug removed; g counts new surface.** A refactor (D7's moves), a documentation or process fix, or a fix of a false positive injects with no bug removed and no new surface. The `injected` term's denominator covers them; the model's two parameters do not.
5. **Link 3 has no term.** "Every finding was fixed correctly" is measured "only once a re-report names the fix it follows"; nothing in the thirteen terms reads a fix that did not fix, and `injected` is defined as a new defect.
6. **The claim covers objective bugs only.** Section 1's perfect code also holds the three product terms and the owner-judged dimensions; nothing argues they converge, and `regret`'s floor means it cannot reach its stated end state. The file should say the convergence claim is not a claim about section 1.
7. **`escapes` depends on a reporting rate nobody measures.** Releases per day is beside it; installs reporting is not, and the residual row admits this.

## Gaming, term by term

Moved without improving what is measured, and not caught by a control that exists at this head:

- `first_pass`: approve weakly. Its catchers are `injected` and `escapes`, both NO-READ; real-catch incidence is beside it but in no rule.
- `coverage`: the universe is "a command the reviewer re-runs"; re-running a command that prints a narrow universe reproduces the narrow universe. The control that would catch it (planted defects over the natural universe) has no instrument.
- `generality`: the share rises when a cell is "examined" by one property test over the configuration space or a stub simulation, with nothing asserted about the result; "no defect found" is met by not finding. The term measures examination, not correctness per cell.
- `operation`: "the value written equals the documented target" moves by editing the document to match the code. No false move of this shape is listed.
- `regret`: block item 3.
- `unexamined`: "a fix names the judged finding it closes" stops a feature relabelled as a fix; it does not stop a late merge being "examined" by a pass that reports it read.
- `injected`: the cause is named by the fixing group, which is the party whose predecessor it indicts; "checked in review" is the only control.
- `lead_time`: the clock starts at the roster entry, which the orchestrator writes; entering a group when its fixer is ready moves it. "Enter the group late" is listed and its catcher restates the definition.
- `tokens_per_change`, `closure_slip`, `product_green`, `escapes`, `unowned`: I found no move beyond those section 5 lists, and each listed catcher is a stated companion figure, not a refusal.

## Items for the owner, not blocks

Where the draft limits what a mandate may approve:

1. Section 5: "no mandate scope covers" 0017, `objective.json`, `check_scopes.py`, each enumerator once built, and every round's `EVALUATION.json` and `OBJECTIVE.json` (body Decision 8). This narrows decision 0013. It is stated and not enforced: the diff adds four CODEOWNERS lines and changes nothing that reads a mandate, so under 0013's grammar a mandate scoped `code-owned` or `all` still reaches these paths.
2. Section 2 rule 1: a change moving a layer-1 term the wrong way is accepted by "only the owner … by card".
3. Section 6: "the owner decides each card", and the check refuses a round start with an undecided card. No agent under any mandate can clear a card, so a round cannot start while the owner is away and one card is open. Every `change` and `remove`, every `unowned` item and every missing criterion is a card.
4. Section 1 and section 3: the supported population, the comfort bounds, the gate and the review rule are "the owner's"; "neither is a tunable the evaluated round may loosen".
5. Section 5: "Adding a term or an object class removes one" (body Decision 17), and from round 12 a process change is kept only on a measured before and after with its null control, which removes from any approver a change whose named term is NO-READ.
6. `/tools/audit/check_scopes.py` becomes code-owned. R10-DIMENSIONS-FULL-COVERAGE owes a territory check in that file, and every closing orchestrator's `OBJECTIVE.json` needs the owner's review before the next round can start.
7. The budget entry for `evaluator.md` was pushed with no owner confirmation first; the body says so under `## Red checks` and leaves it to `budget-raise-gate`.

The model the draft assigns the evaluator seat: `evaluator.md` line 3, "One opus seat per round" (body Decision 9; its alternative is "a model at least the orchestrator's"). The owner's instruction quoted in 0017's Context asked for "a fable seat" to define the function, and this group's roster models are fable for fixer and reviewer. The reviewer of the evaluation is "a second seat" with no model named.

## Findings

- The planted-defect recall and the two-finder overlap, which sense four of section 4's six assumptions, have no instrument and no group; 0017 sends them to round 11's first evaluation as cards, so round 11 runs with the convergence claim unverifiable. Carry: R11-PRE-ROUND-METRICS
- Link 3 of the chain (a fix that did not fix) has no term and no record that would read it; a re-report must name the fix it follows. Carry: R10-DIMENSIONS-FULL-COVERAGE
- No instrument measures per-bug detection as an infimum or the correlation of two same-model finders; the overlap estimate is biased low under it. Carry: R11-PRE-ROUND-METRICS
- `scorecard.py` line `A_gate` reads the last 20 runs and 0017 defines `product_green` over the window; the proxy and the term will disagree until the window is added. Carry: R11-PRE-ROUND-METRICS

## Evidence

- No review packet exists and no CI has run: no pull request is open for this head. `## Red checks` in the body answers `budget-raise-gate` in advance; nothing was red to read.
- Merge with main: `git merge-tree --write-tree origin/main f7efa4be88` exits 0 (tree 3d6c5a2771); the merge base is origin/main e23124ff6e, so the head is 0 behind.
- `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty: my contract copy is current.
- RESULT self-test at head: 15/15 evaluation arms held, rc 0 (`ev/checks.txt`).
- RESULT `--round 11` at head: rc 1, 2 gaps naming `round10/OBJECTIVE.json` and `round11/EVALUATION.json`; without `--round` rc 0.
- RESULT the body's six mutants: each rc 1 with the arms the body's table names (`ev/mutants.txt` M1 to M6); unmutated rc 0 before and after.
- RESULT my eight further mutants over the nine arms the body left unmutated: seven killed, R12 survives (above).
- RESULT bypass probes P0 to P8: all nine accepted (`ev/probes.txt`).
- Figures re-derived: 13 terms; 168 objects (16, 19, 10, 105, 18); 0017 is 352 lines; corpus 69092 against 68618 plus band 500; `Architecture score: dS +0.0000 NULL`; `STRUCTURE RATCHET PASSED`; the check's wall clock 1.3 s here against the body's 1.8 s on its container; `rules_sync --check` ok.
- Not re-derived: `tests/entities.py` (this container's interpreter has no `homeassistant`), `prepr.sh`'s three survivors, and every round-10 hand figure in the body's worked example, whose sources are two audits on step refs outside the tree. `first_pass` 412 of 817 has an enumerator (`flow_metrics.py --window`) that I did not run, having no window bounds in the body.
- `VERSION`, release notes, `custom_components/` and `tests/golden/` are untouched by the range; both claim files are byte-identical to the merge base. No production line changes, so `mutation` on `--scope changed` draws no mutant here.
- Tracked commands 0017 names that exist: `tools/audit/seat/scorecard.py` (lines `A_gate`, `H`, `E`), `tools/audit/seat/flow_metrics.py --window`, `tools/audit/seat/review_strength.py --window`, `tools/audit/machinery_ratchet.py --measure`, `tests/ha_contract.py`, `dev/audit/config/bugclasses.json`. `governance_cost.py` exists only as `tools/audit/round4/D11/governance_cost.py`, a round-4 evidence script. Roster groups named and present, not started: R11-PRE-ROUND-METRICS, R11-PRE-TOKEN-LEDGER, R10-DIMENSIONS-FULL-COVERAGE.
- `audit-find.js` line 30 defines `round` and line 226 throws on `scopes_rc !== 0`, so the new flag reaches the existing refusal.
