Root-cause records for the recurring-friction keys R10-FRICTION-REGRESSION left owed, the policy-tooling countermeasures of R10-RCA-FRICTION-RESIDUE, and the `instrument-self-tests` countermeasure #2865 never got. One record per key under `dev/audit/rca/`; the four existing records are judged for sufficiency and left alone.

No closing keyword: the roster lists these issues in the group's `issues` with `fixes: []`, so `pr-contract`'s intended list refuses `Closes` on them (`prepr.sh` step 7); the orchestrator wires `fixes` and the delivery closes them. One line per issue so the wiring has each:

Disposes #2875
Disposes #2950
Disposes #2998
Disposes #2436
Disposes #2437
Disposes #2429
Disposes #2840
Disposes #2835
Disposes #2895
Disposes #2907
Disposes #2860

#3156 (`ci-red`) is in the roster `issues` and is **not disposed** by this group: no record for the key lands here; `R10-RCA-FRICTION-SWEEP.md` section 4b says so and asks the orchestrator to re-route it to its own group, so the delivery must not close it from this PR. #2942 is closed and not in `issues`; its carry is in the group and landed (`R10-RCA-MUTATION-VACUOUS.md` section 6).

## Approval

This diff touches `dev/governance/rules/ci-autofix.md` (with its generated `.claude/rules/` and `.cursor/rules/` copies) and `tools/policy/policy_lint.mjs`'s family map, which decides what the cron files. **It merges only on tvofi's approving review at the head**; that review is the approval of record. The dispatch brief carries an earlier approval ("All of these are approved.", 2026-10-29) of the countermeasures `dev/audit/rca/R10-RCA-FRICTION-RESIDUE.md` drafted; it is carried from the brief, not a live approval.

Covered by that drafted text, landed verbatim:

- #2429, `ci-autofix.md`: "If `mutation-pins` has not concluded by `tests / mutation`'s conclusion, the pin is owed by the handoff and the body says `unmeasured`;" and "`pinned` only if `--pin-killed` ran on this head." This is the bound as the reviewer quoted it from the draft (record section 7 words it "the next `tests / mutation` conclusion"). "(kept until M-3)" and "; the reviewer re-checks it" are byte-identical to base.
- #2436, the derived `other (untaught)` verdict family, and #2437, the declared `root-cause` family over `root-cause-unanswered`, `-detectable` and `-unrecorded`, in `policy_lint.mjs`.

**Changed policy sentences the approval does not cover**, each for tvofi's review:

- **Removed from `ci-autofix.md`:** "A failed recording reads files a clean run never does (`linecache`): an UNDER-SCOPED beside one may be an artefact. Fix the script; a push re-records." Reason: the file had 3 tokens of headroom under its 1469 cap, and the two approved sentences need the paragraph's tokens; with them in, `--budgets` reads 1469 / 1469. The action half ("fix it first") stays in the bullet above; the warning that an UNDER-SCOPED beside a failed recording may be an artefact goes.
- **Three new `mutation` family members** in `policy_lint.mjs`: `mutation-unpinned`, `unpinned-site`, `mutation-survivors`. Reason: #2942 measured these spellings splitting the `mutation` family below threshold (`R10-RCA-MUTATION-VACUOUS.md` section 6, a stale member list).
- Not policy, disclosed for completeness: the `ci_predict.py` `mutants` arm (#2865).

The `fixer.md` sentence drafted in `R10-RCA-CLASS-OPEN.md` section 6 is not landed and waits on the owner.

## Head

9ca25bb8dedb81fffc74b65c176e5a07aa9b01c7

Repair round 3 (the third review's block on `a8d19cf1950250e378b3cf0dfd4f8c5c29e01255`, `verdict/3255`): `origin/main` merged at `80016a71f567d936450d8708abcbb79d9e8071d7` (`git merge`, clean), then three commits. `origin/main` read `80016a71f567d936450d8708abcbb79d9e8071d7` at 2026-11-06T23:08Z, unmoved since the merge, so `tools/pr/prepr.sh` ran once on this head.

## Mutation proof

Each mutant applied with `sed`, run, and restored from a saved copy; the unmutated tree is the null control.

- `tools/policy/policy_lint.mjs` `statsFindings`: `kind === 'verdict family' ? derivedInput(blocks, passing) : null` -> `derivedInput(blocks, passing)` (the derived family also applied to friction rule ids). **KILLED**, rc 1: `FIXTURE VACUOUS: statsFindings did not file the families end to end (... 3 untaught friction ids -> 1 friction-family would-open(s), want none)`. Null control: rc 0, `FIXTURE ok: 93 error(s) hold 269 pins`. The pin is a new friction-id row in the wiring block: three untaught friction ids on three PRs, expecting no `friction family` would-open.
- `tools/pr/ci_predict.py` `mutant_preds`: `(quoted | {rel}) & changed` -> `quoted & changed` (a diff touching only a driver would not run that driver's self-test). **KILLED**, rc 1: `FAIL a diff touching only the driver runs it: the driver is its own target`. Null control: `python3 -I tools/pr/ci_predict.py --self-test` rc 0. The pin is a new row in `mutant_self_test`.
- Earlier rounds, unchanged code and still pinned by the same self-tests: `statsFindings` passing `null` (killed); `cmdStats` passing no derived list (killed); each of `mutation-unpinned`, `unpinned-site`, `mutation-survivors` dropped and all three dropped (killed); the derived family's passing-verdict exclusion removed (killed); `root-cause-unrecorded` removed (killed); the `mutants` arm's selection replaced by `if False:` (killed). Not mutation-proven: the `ARMS` registration of `mutants`; stated in `R10-RCA-ROOT-CAUSE-DETECTABLE.md` section 7.
- `tests/mutation`: `python3 tests/mutation_table.py --scope changed --base origin/main --max 10 --jobs 3` reads `MUTATION TABLE PASSED (empty scope)` ("no production code line added or modified against the base"), rc 0. `python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3` ran on this head: `PIN KILLED: nothing to pin` (0 new unpinned sites), rc 0. The mutation lane mutates `custom_components/` only, so the tools/ kills above are pinned by those in-tree self-test rows. `mutation`: pinned.

## Null control

- Both kills above: the unmutated tree, rc 0 (lines quoted there).
- `mutant_preds` over a diff touching no planted target runs no driver and predicts nothing (the self-test's null-control row, ok).
- The friction-id row's control is the verdict-family rows beside it: three untaught verdict words still yield exactly one `other (untaught)` would-open at the head, so the friction row reads none because the derived family is the verdict table's, not because the window files nothing.
- Earlier rounds' `--stats` control (taught and friction-id rows byte-identical before and after the family changes) is a record figure in `R10-RCA-FRICTION-SWEEP.md` section 4, not re-taken this round: this round changes no counting code.

## Figures

- `node tools/policy/policy_lint.mjs --budgets`: the `.claude/rules/ci-autofix.md` row reads 88 / 96 lines and 1469 / 1469 tokens, rc 0 (the approved bound restored).
- `node tools/policy/policy_lint.mjs --self-test`: `FIXTURE ok: 93 error(s) hold 269 pins`, rc 0 (the friction-id row joins an existing pin block, so the pin count is flat).
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`, rc 0.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/mutation_table.py --scope changed --base origin/main --max 10 --jobs 3`: empty scope, rc 0.
- The `--stats --since v7.0.4` figures in the records (`root-cause-detectable` 12 PRs, `class-open` 32 / 56, `mutation-vacuous` 31 / 38, `mutation (family)` 6 / 7, `other (untaught)` 65 / 78, `gate-scoping.md` 12 / 13) and the driver timings are unchanged record figures from round 1, re-derived there; not re-taken this round.

## Red checks

none: no check run exists for `9ca25bb8dedb81fffc74b65c176e5a07aa9b01c7` yet, because it is not the PR head until the handoff moves it, so no concluded red of this head exists on any check-run page. `tools/pr/ci_predict.py` ran inside `prepr.sh` and predicted none. If `governance / instrument-self-tests` is cancelled at its 30-minute job timeout on this head, that is the owner's standing line, main-wide and not this diff (class: timeout; cheaper detector: none that runs before CI; cure R10-PROCESS-SLIM, #3245).

## Carries

The dispatch brief's carries, numbered 1-8 here (the brief's own count starts at 0).

- Carry 1 (P259, the five records): answered. #2860 landed in #3000; #2840, #2835, #2895 and #2907 are judged sufficient and left unrewritten in `R10-RCA-FRICTION-SWEEP.md` section 1.
- Carry 2 (#2875 and #2950): answered in `R10-RCA-ROOT-CAUSE-DETECTABLE.md` and `R10-RCA-CLASS-OPEN.md`. The `class-open` countermeasure is a drafted `fixer.md` sentence that waits on the owner's ruling.
- Carry 3 (R10-RCA-FRICTION-RESIDUE countermeasures): landed, with demonstrations in `R10-RCA-FRICTION-SWEEP.md` section 4 (#2436, #2437, #2429); #2429 is the approved bound verbatim.
- Carry 4 (#2942, mutation family): answered in `R10-RCA-MUTATION-VACUOUS.md` section 6: a new cause (a stale member list); three spellings added, listed under `## Approval` as not covered.
- Carry 5 (FLOW-ANDON cost test): answered in `R10-RCA-FRICTION-SWEEP.md` section 3; the countermeasure was already built (#2582) and stays.
- Carry 6 (#2865, instrument self-tests): answered in `R10-RCA-ROOT-CAUSE-DETECTABLE.md` sections 3-7; the `ci_predict` `mutants` arm is landed, and a driver-only diff now runs its driver (pinned).
- Carry 7 (#2998, mutation-vacuous): answered in `R10-RCA-MUTATION-VACUOUS.md`; the tools/ refusal stands on an unpriced number.
- Carry 8 (#2835, gate-scoping, measure first): answered in `R10-RCA-FRICTION-SWEEP.md` section 2: the keying rule and the gate do not change.

## Forward-carry

- The `fixer.md` sentence drafted in `R10-RCA-CLASS-OPEN.md` section 6 (a generated spelling corpus for text-shape guards) is policy and waits on tvofi's ruling; it is not landed. Carry: dismissed: drafted for the owner, nothing in this tree consumes it until approved.
- A `tools/` mutation table (`R10-RCA-MUTATION-VACUOUS.md` section 5) is unpriced; the refusal stands until a seat prices it. Carry: dismissed: the cost number that would reverse the refusal is not produced by any group.
- The wider arm (run `--self-test` of every changed wired instrument) is deferred until a second PR beyond #3049 fails its own self-test. Carry: dismissed: one instance does not make a class.
- #3156 needs its own group before `fixes` is wired from this group's `issues`. Carry: #3156

## Friction

- `.claude/rules/ci-autofix.md`: cost: the file had 3 tokens of headroom under its 1469 cap; the two approved sentences were paid by deleting the `linecache` paragraph and then fill the cap exactly, named under `## Approval`. Carry: dismissed: paid in this change.
