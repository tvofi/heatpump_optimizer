policy: decision 0017, the objective function, and the evaluation that opens a round (R11-PRE-OBJECTIVE-FUNCTION)

Defines the function the owner asked for on 2026-11-13 as decision 0017, adds the evaluator seat that grades every dimension, contract, rule, instrument and gate against it before a round's finders, and makes `tools/audit/check_scopes.py --round N` refuse a round start whose evaluation is missing, incomplete or undecided. `audit-find.js` passes its round, so the refusal sits in the instrument that already refuses a bad scope table.

What it does not do: build an enumerator. Of the thirteen terms only `first_pass` has a working one; `product_green` has one with no input producer; eleven have none. The two held-out checks have neither instrument nor owner, so decision 0017 section 4 claims convergence for no round yet, and says one round guarantees perfect code under no condition it can check. Round 10 scored by hand (below) is twelve NO-READ rows and one read.

## Where each owed part is

| owed | where |
|---|---|
| A. definition, units, denominators, enumerators, targets, ties; object scoring; what cannot be scored | `dev/governance/decisions/0017-objective-function.md` sections 2 and 3; machine-read half `dev/audit/config/objective.json` |
| B. convergence claim, assumptions, sensors | 0017 section 4 |
| C. the step, who runs it, the refusal and its self-test | `dev/governance/roles/evaluator.md`; 0017 section 6; `dev/audit/README.md` phases 2 and 13; `tools/audit/check_scopes.py`; `.claude/workflows/audit-find.js` step 7 |
| D. anti-gaming per term; standing cost | 0017 section 5 and section 6's last paragraph |
| E. round 10 scored by hand | this body, below |
| the roster group's four owner carries | 0017 sections 1, 2 (end states and residuals), 3 (from a distance to a change) and 4 (the chain); "Carries answered" below |

Two later obligations are built into the tree here and are not carries: round 10's objective record is owed by the closing orchestrator (`dev/audit/README.md` phase 13), and the two unowned held-out instruments go to round 11's first evaluation (0017, Consequences).

## Carries answered

- **Carry 0** (a perfect reader; the perfect round as an end state; self-contained; residuals). 0017 section 1 gives each dimension's perfect result and who decides it; section 2's second table gives every term its end state and the residual no reader can remove; section 3 ends with "From a distance to a change", the rules a reader with the record and the tree applies. The measured distance is each term's value in the closing round's objective record; round 10's is the hand score below. The perfect-reader check is below.
- **Carry 1** (anchored on the product; completeness of the dimension set; the chain). Section 1 defines perfect production code as three clauses; `unowned` is the completeness term, target none, and section 6 makes every unowned item a card. Section 4 is the chain of six links, each with its measure and its chance of failing, and states that one round guarantees perfect code under no condition the record can check: links 2 and 6 are probabilistic, so only convergence over rounds is claimed.
- **Carry 2** (generality, operation, savings). Section 1 defines `generality` (the population axes, the four ways a cell counts as examined, what D12's brief must gain), `operation` (write and hold sites times plan states; the actuator-write dimension and D8) and `regret` (same-information oracle as the target, perfect foresight as the bound; D0's race, the flat-price null, the measured-against-modelled gap). Section 2 gives each its enumerator state (none whole) and residual. The two acceptance criteria the owner must set are Decisions 14 and 15.
- **Carry 3** (the playbook stays usable; the dry read). The step is in the playbook in this pull request, at the place it runs. Dry read from `dev/audit/README.md` alone: its phase table's row 2 enters on "a baseline SHA pinned after `evaluator.md`'s evaluation" and names `tools/audit/check_scopes.py` as the instrument; `evaluator.md` is in `CLAUDE.md`'s role table and sends its reader to decision 0017; the paragraph on `check_scopes.py` under "What to reuse" names `--round`; `.claude/workflows/audit-find.js`, row 2's other instrument, runs it with its round at the baseline; row 13's artefact names the round's objective record, which the next evaluation reads. R10-ROUND-PLAYBOOK-FINAL reads `carries-open` on the roster branch while its table is on main at this base, so the pointer is in the table itself and nothing is carried to that group. The carry's two other sentences (the orchestrator picking up the previous round's carries; outside and owner findings folding into the open round) are outside this group's part of it and are not built here; `closure_slip`'s residual in 0017 already treats folded-in owner and outside work as the owner's, not as slip to remove.

- **Carry 4** (the owner's ruling delegating the supported population and the comfort bounds). 0017 section 1 states both as the carry sets them, with the ruling quoted, who set them and their basis: the population is every install the configuration flow can complete at the head, enumerated from code and fixtures; the comfort bounds are the ones the product already enforces, and savings count only among plans that hold them. Neither value is mine; they are Decisions 14 and 15, set and open to the owner's change at review.

**The perfect-reader check: what a reader with 0017 and the tree alone would change for round 11.**

1. By "A NO-READ term": build the enumerators first, to section 2's definitions, since twelve of thirteen distances are unknown.
2. By "`coverage` below 1": in each brief whose method samples or names no enumerating command (the coverage audit lists D0, D1, D2, D3, D4, D7, D9, D11, D14, D15), write the command and delete the sampling instruction; run D11 and D13 every round.
3. By "An `unowned` item": card an actuator-write dimension and a functional-correctness dimension, and the widenings of D6, D8 and D15, for round 10's seven unowned escapes.
4. By "An escape owned by a dimension": add to D1 the lifecycle paths, listeners and valid old-version stores its steps did not drive, and to D2 the model-error covariates and stated grids.
5. By section 1's `generality`: give D12 the population axes, the card and blueprints, and the cell ledger.
6. By `first_pass` at half: move the block classes a script can decide (carry, body, check state) to the script.

**What it could not decide without the owner**: the acceptance criteria for D4 beyond rendering and for D5; D9's budget; D10's target tier; every threshold in Decisions 1 to 4; and who plants the held-out defects. Each is a Decision below, and 0017 section 1 makes each missing criterion a card rather than a guess.

## Departures from the proposal the owner read

1. **"Never traded" is made operational as "not worse beyond a band".** Read as targets, the layer-1 constraints (zero escapes, zero injected) are unmet at round 10, so no change would ever be admissible and layers 2 and 3 would never be consulted. 0017 keeps the targets as direction and refuses a change that moves a layer-1 term the wrong way.
2. **No trade inside a layer either.** The proposal ordered the layers and said nothing of two terms in one layer pulling apart. One up and one down is ruled no improvement and goes to the owner.
3. **Lead time starts at the roster entry, not the first commit.** The process audit's L1 starts at the first branch commit, which the measured seat chooses.
4. **Tokens are NO-READ while any seat class is unledgered.** The local-only figure the process audit took is a partial of unknown share; printing it as the term would let work move to cloud seats and read as a gain.
5. **Held-out checks are sensors of the assumptions, not terms.** A seat scored on planted-defect recall would optimise the plants.
6. **A finding count is in no layer**, by the coverage audit's B.4(e).
7. **A card had no format in the tree.** It is defined as an entry of the evaluation file, with the owner's decision recorded on it and the file code-owned.
8. **Report-only binds the verdicts, not the step.** The evaluation must exist for round 11 to start; nothing is refused on what it says until round 12.
9. **An off-cadence dimension counts 0 coverage.** The coverage audit left D11 and D13's cadence off its necessary list; under the function it is a layer-1 miss in two rounds of three.
10. **Thirteen terms, not seven.** The owner's four carries add the product terms (`regret`, `operation`, `generality`), the completeness term (`unowned`), the late-merge link (`unexamined`) and right-first-time (`first_pass`).

## Round 10 scored by hand (the null control for usefulness)

Sources: the process convergence audit at d5d7ff81878fe9bc17ee6fcc9e3803d848cbc7f7 and the dimension coverage audit at 6ca3bfb7142be1ccb0d5275041c41d5eae3c8ddc, both under `dev/audit/rounds/round10/` on their step refs. Nothing was re-measured; every figure is theirs, and all but `first_pass` were taken by hand or by scripts outside the tree, which is why those rows are NO-READ as a record.

| term | hand figure from the audits | as 0017 reads it |
|---|---|---|
| `regret` | D0 raced under a fifth of its grid; no realised cost per install | NO-READ |
| `operation` | 3 actuator escapes; 8 write sites and 32 hold sites never enumerated by a brief | NO-READ: no dimension, no cell ledger |
| `generality` | D12 exhaustive over its declared slots, card and blueprints outside its universe | NO-READ: no population, no cell ledger |
| `unowned` | 7 of the 25 escapes | NO-READ as a record; by hand 7 |
| `escapes` | 25 product escapes against 111 verified findings removed, ratio 0.82; by owner D1 7, D2 7, D4 3, D6 1, D10/D12 1, none 7 | NO-READ: no found-by field, hand table; row 25 was caught on main, so released escapes are at most 24 |
| `injected` | at least 3 named causes over 139 production merges; proxy 10 production hotfix merges of 139 (round 9: 2 of 91) | NO-READ: no cause field; the proxy moved the wrong way beyond its band (difference 8, band 6.9) |
| `product_green` | scorecard `A_gate` printed 0/0 read; 0 of 36 concluded main runs succeeded on 2026-11-13 | NO-READ: the job listings have no producer |
| `coverage` | 2 of the 14 dimensions audited report a denominator (D10, D13); D5 and D6 not audited | NO-READ by any command; by hand at most 2 dimensions above 0 |
| `unexamined` | 26 outside groups and new features admitted mid-round | NO-READ: nothing joins a merge to a finder pass |
| `first_pass` | 412 of 817, 0.50 | read: `flow_metrics.py` over the round's window prints it |
| `lead_time` | first commit to merge, production: p50 21.7 h, p90 49.3 h (round 9: 8.1 and 49.9) | NO-READ: the roster-entry clock is printed by nothing |
| `closure_slip` | 13.6 days later over 12.9 days of plan history, 1.05 days per day | NO-READ: read from rendered pages; history starts 16 days after the register |
| `tokens_per_change` | local seats only: 368 M, 343 M, 249 M per production merge in sessions 12 to 14 | NO-READ: cloud seats unledgered |

**Round 10 against round 9**: on the one comparable read, the `injected` proxy, round 10 does not hold layer 1, so the ordering stops there. Layers 2 and 3 are not consulted, though both hand figures are also worse.

**What round 11's start evaluation would have told the owner**, the two audits' changes ranked by the ordering:

1. *Layer 1, a term moved*: pin the toolchain and split main's status (process a1, `product_green`); then the coverage audit's changes in order of escape rows: widen D1 and D2 (11), widen D4 and D2's grids (6), a functional-correctness dimension (4), an actuator-write dimension (3 to 4), widen D6, D8 and D15 (3). Cadence 1 for D11 and D13 joins this layer (departure 9).
2. *Layer 1, a term made readable*: the denominator rule (coverage 6), found-by and cause fields (coverage 7, process a6). They move nothing and every layer-1 comparison waits on them.
3. *Layer 2*: closure as data and scope frozen at the register (b3), shared files out of pull requests (b1), mechanical bookkeeping verdicts (b2), the relay arm (b4), the machinery limiter (a2), the round metrics instrument (a3).
4. *Layer 3*: the token ledger (a4); standing LLM seats for mechanical roles, the corpus re-read per compaction, the plan-page commits and the re-acks (the audit's REMOVE list).

Object verdicts it would have carded: `change` for D1, D2, D4, D6 (escapes in territory), for the dimension list (7 escapes owned by none), for D11 and D13 (cadence), for `scorecard.py` (zero yield in round 10, one round short of `remove`), for `machinery_ratchet.py` (never bound), for `standing-merge.md` and `standing-dispatch.md` (cost against a script); `keep` for D10 and D13's method; `keep` as NO-READ for every rule and nearly every instrument and gate.

**Where the function cannot rank what the audits found.** (i) Inside layer 2 and inside layer 3 it orders nothing: no change has a measured before and after, so item 3's order is the audit's, not the function's. (ii) The memory index (a5), the rulings file (a8), the alert replay (a7), reviewer drift (b5) and ack renewal (b6) move no term 0017 names; they reach `lead_time` only by argument. The function is silent on them, and the evaluation would return them as NO-READ, not as rejected. (iii) Inside layer 1 it ranks by escape rows, a count the coverage audit already had. Its own contribution to the ranking is the layering, the cadence finding and the refusal to compare what has no record.

## Decisions for the owner

Each is a recommended value, its basis, and the alternatives. 0017 leaves the numbers of 1 to 3 as "the owner's" and names no value.

1. **`product_green` floor: 0.90.** Basis: the process audit's a1 metric. Alternatives: 1.00, the target its section 7 records, unreachable as a floor from the current state; 0.95.
2. **`closure_slip` ceiling: 0.2 days per day.** Basis: the process audit's b3. Alternatives: 0; 0.5.
3. **Band for `lead_time`, `closure_slip`, `tokens_per_change`: 20%.** Basis: round 10's weekly production p50 ranged 15.4 to 27.4 h around 21.7, about 28% either way over five weeks, so a round median carries roughly 12%; 20% is near two of those and equals the existing exemption bar. Alternatives: 10%, proposal-triage's machinery bar, inside the noise; 30%.
4. **Count band: twice the square root of the two counts' sum.** Basis: two standard deviations of a difference of Poisson counts. Alternatives: any difference; three.
5. **Token unit: the raw sum of usage fields**, the unit the audit measured. Alternative: price-weighted, since over 95% of the sum is cache reads; the ledger should keep the fields apart so this can change without a new record.
6. **Lead-time clock at the roster entry** (departure 3). Alternative: first commit, comparable with the audit's figures.
7. **The refusal is live for round 11** (departure 8). Alternative: wire `--round` from round 12 and run round 11's evaluation unenforced.
8. **No mandate scope covers the yardstick** (0017 section 5). This narrows decision 0013's mandate for these files. Alternative: leave them under a mandate scoped `all`.
9. **The evaluator is "one opus seat"**, the contracts' usual wording. Alternative: require a model at least the orchestrator's.
10. **`remove` needs zero measured yield in two consecutive rounds.** Alternatives: one round; three.
11. **0017 is an uncapped file**, as decisions 0001 to 0016 are, at the line count `## Figures` gives. Alternative: a capped rule file, which costs a corpus raise of about its size.
12. **Who plants the held-out defects and who runs the overlap trial** is unowned; 0017 sends both to round 11's first evaluation as cards.
13. **CODEOWNERS gains four lines**: the config, `check_scopes.py`, and the two record files under `dev/audit/rounds/`.
14. **The supported install population** is set, not open (Carry 4): every install the configuration flow can complete at the head, enumerated from the code and the fixtures. Basis: it is what the product already accepts. Alternative the owner may take at review: a narrower named list, which would shrink `generality`'s denominator.
15. **The comfort bounds** are set, not open (Carry 4): the configured comfort range, the hot-water minimum, the mold and legionella guards and the entity's own limits. Basis: the product already enforces them. Alternative: a fixed band the owner states.
16. **Acceptance criteria where a dimension's perfect result is the owner's**: D4 beyond rendering, D5, D9's Pi-class budget, D10's target tier. No recommendation; each missing one is a card at round 11's evaluation.
17. **Adding a term removes one** (0017 section 5) now starts from thirteen. Alternative: no such rule.

## Head

f7efa4be885e53556a6bfa02ad22a9b22c417b2a (measured 2026-11-13; origin/main at e23124ff6e)

## Mutation proof

Each mutant was applied to `tools/audit/check_scopes.py` in the checkout, `python3 -I tools/audit/check_scopes.py --self-test --repo .` run, and the file restored; every one exits 1 and the unmutated file exits 0 before and after.

| mutant (predicate changed) | arms that go false |
|---|---|
| a missing evaluation returns no gap | `evaluation: a missing evaluation is refused`; `--round exits 1 with no evaluation in the tree` |
| a missing previous record is never tested | `evaluation: a missing previous record is refused`; `--round exits 1 with no evaluation in the tree` |
| a card's decision is never tested | `evaluation: an undecided card is refused` |
| an accepted card's merge is never tested | `evaluation: an accepted card not merged is refused` |
| evaluator equal to reviewer is allowed | `evaluation: one seat as evaluator and reviewer is refused` |
| `--round`'s gaps do not reach the exit code | `--round exits 1 with no evaluation in the tree` |

The first run of the third mutant died on a `KeyError` in the next branch and named no arm; the branch now reads the decision with `get`, and the row above is the re-run. The nine other arms (term rows, round identity, the orchestrator as evaluator, object verdict, evidence, card reference, object classes non-empty, the complete record) were not mutated one by one.

## Unpinned sites

`prepr.sh`'s diff mutants left 3 survivors, all constants of the self-test's own fixture in `tools/audit/check_scopes.py`, none in a rule:

- `tools/audit/check_scopes.py:233 CONST_SWAP` (a term's dummy `value` 1 to 2): equivalent. The rule tests that a value has an enumerator, never what the value is.
- `tools/audit/check_scopes.py:248 CONST_SWAP` (the term the missing-term arm drops, first to second): equivalent. Either term's absence is refused by name, and the arm asserts the name it dropped.
- `tools/audit/check_scopes.py:257 CONST_SWAP` (the wrong round planted, 9 to 10): equivalent. Any round but 8 is refused.

## Null control

- The unmodified tree: `check_scopes.py` at the merge base has no `--round` argument, so no command could ask the question; its default run exits 0 there and at this head.
- A complete record passes: the self-test's arm `a complete record passes` builds one over the live object files and gets no gap, so the refusals above are not a check that refuses everything.
- The live tree at this head with `--round 11` exits 1 naming the two missing files, and without `--round` exits 0: the refusal is the flag's.
- The worked example is the null control on usefulness, and it partly fails: see "Where the function cannot rank what the audits found".

## Figures

- Self-test at this head, 15 evaluation arms held and exit 0: `python3 -I tools/audit/check_scopes.py --self-test --repo .`
- Round 11 refused at this head with 2 gaps: `python3 -I tools/audit/check_scopes.py --repo . --round 11`
- The check's cost, 1.8 s with `--round` and 1.9 s without on this container, one run each: `python3 -I tools/audit/check_scopes.py --repo . --round 11`
- Terms in the machine-read list, 13: `python3 -c "import json;print(len(json.load(open('dev/audit/config/objective.json'))['terms']))"`
- Objects the evaluation must give a verdict, 168 at this head (dimensions 16, roles 19, rules 10, instrument guides 105, workflows 18): `git ls-files 'dev/governance/dimensions/D*.md' 'dev/governance/roles/*.md' 'dev/governance/rules/*.md' 'tools/audit/seat/instruments/*.md' '.github/workflows/*.yml'`
- Decision 0017's length, 352 lines: `wc -l dev/governance/decisions/0017-objective-function.md`
- Policy caps, 0 errors; the corpus aggregate reads 69092 against a ceiling of 69118, and `evaluator.md` 27 lines and 361 tokens: `node tools/policy/policy_lint.mjs --budgets`
- Architecture score, dS +0.0000 NULL: `python3 tools/audit/archscore/score.py --diff origin/main`
- Structure ratchet passed: `python3 tests/structure.py`

Standing cost per round is not a figure: neither seat has run. 0017 section 6 states it as a cap (one pre-study-sized context and one reviewer-sized context) and makes their tokens the first rows of round 12's ledger.

## Raise justification

The diff touches `dev/governance/config/policy_budgets.json` to record the two caps of one new file, `dev/governance/roles/evaluator.md`, at its measured size. No existing per-file cap and no aggregate cap is raised. `budget-raise-gate` still counts the new entries as a raise and stays red until the owner approves (`## Red checks`). The cost the owner should see is in the band: the corpus aggregate stood 89 tokens above its recorded cap at the merge base and stands 474 above at this head, of a band of 500, so the next policy addition has 26 tokens before it must cut or ask.

Payments tried: (1) the contract's first draft put the corpus 54 tokens over its ceiling; it was cut twice, to 375 and then 361 tokens, before recording; (2) `CLAUDE.md`'s new index row is paid inside the file by deleting the history clause of the `SEAT-BLOCK.md` sentence, and the row itself was shortened twice; (3) `dev/audit/README.md` pays for its two cell edits by replacing its three-line restatement of `check_scopes.py`'s rules with one sentence; (4) `orchestrator.md` takes one sentence inside its existing headroom; (5) folding the evaluator into `plan-review.md` was rejected, since that file sits at both caps and one file would then bind two roles; (6) the definition was written as a decision record, which is uncapped, and that choice is Decision 11 above rather than a quiet saving.
Architecture score: dS +0.0000 NULL

## Approval

Pending: the owner's approving review. Every changed policy path is code-owned (`CLAUDE.md`, `dev/audit/README.md`, `dev/governance/roles/`, `dev/governance/decisions/`, `.github/CODEOWNERS`), and the thirteen decisions above are the owner's to set before or with it.

## Red checks

- `budget-raise-gate`: red by design until the owner's approving review at this head. The gate reads the two new `evaluator.md` entries in `policy_budgets.json` as one raise, though no existing cap moves. Cheaper detector: `tools/pr/prepr.sh` predicted it before the handoff, at no standing cost; nothing cheaper can clear it, because what it waits for is an approval, not a repair. No owner confirmation was obtained before this push (`CLAUDE.md` rule 2 asks for one before a raise is pushed; the brief sent the raise to the owner with the pull request): pending owner confirmation, and the gate holds the merge until it is given.

## Forward-carry

- The three groups that build the enumerators build to 0017 section 2's definitions (clock, windows, denominators, the NO-READ rule for a partial ledger), add each enumerator to `.github/CODEOWNERS` in the pull request that lands it, and return a definition they cannot meet as a card. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R11-PRE-ROUND-METRICS
- The same, for the token ledger: fields kept apart, a seat keyed by group, role and dimension. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R11-PRE-TOKEN-LEDGER
- The same, for found-by, cause and the per-step denominator; an off-cadence dimension reads 0. Lands in `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-DIMENSIONS-FULL-COVERAGE

## Friction

ratchet-budgets: cost: an index row in `CLAUDE.md` and one sentence in each of two capped files took four lint rounds at zero per-file headroom, each paid by trimming a few tokens. Carry: dismissed: the caps worked as designed and no cheaper route exists
