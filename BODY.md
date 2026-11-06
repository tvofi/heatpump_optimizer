Root-cause records for the recurring-friction keys R10-FRICTION-REGRESSION left owed, the approved policy-tooling countermeasures of R10-RCA-FRICTION-RESIDUE, and the `instrument-self-tests` countermeasure #2865 never got. One record per key under `dev/audit/rca/`; the four existing records are judged for sufficiency and left alone.

No closing keyword: the roster lists these issues in the group's `issues` with `fixes: []`, so `pr-contract`'s intended list refuses `Closes` on them (`prepr.sh` step 7); the brief says the orchestrator wires `fixes` and the delivery closes them. One line per issue so the wiring has each:

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

#3156 (`ci-red`) is in the roster `issues` and is **not disposed** by this group: no record for the key lands here; `R10-RCA-FRICTION-SWEEP.md` section 4b says so and routes it to its own group, so the delivery must not close it from this PR. #2942 is closed and not in `issues`; its carry is in the group and landed (`R10-RCA-MUTATION-VACUOUS.md` section 6).

## Approval

This diff touches `.claude/rules/ci-autofix.md` (and its `dev/governance` canonical and generated copies) and `tools/policy/policy_lint.mjs`. The `ci-autofix.md` sentences and the two `policy_lint` families (#2429, #2436, #2437) are the countermeasures `dev/audit/rca/R10-RCA-FRICTION-RESIDUE.md` drafted, which the dispatch brief records as approved by tvofi on 2026-10-29: "All of these are approved." That is carried from the brief, not a live approval; **this pull request merges only on tvofi's approving review**. Not covered by that approval and flagged for it: **three deletions in `ci-autofix.md`'s round-0 diff are reverted except one**. The rule keeps "(kept until M-3)" (`ci.yml`, `tests.yml`, `merge-main.yml` and `HANDOVER.md` still say "until M-3") and "; the reviewer re-checks it". **The `linecache` paragraph ("A failed recording reads files a clean run never does (`linecache`): an UNDER-SCOPED beside one may be an artefact. Fix the script; a push re-records.") stays deleted: a policy change not covered by the approval.** Reason: the cap left no room once the bounded-wait and `pinned` sentences were shortened as far as they go; the paragraph's action half ("fix it first") stays in the bullet above it, only the warning that an UNDER-SCOPED beside a failed recording may be an artefact goes. Also not covered: the three spellings added to the `mutation` family (#2942) and the `ci_predict.py` `mutants` arm (#2865). The `fixer.md` sentence drafted in `R10-RCA-CLASS-OPEN.md` section 6 is not landed and waits on the owner.

## Head

fa17a2ce3e95e244f6cc02fb9b5e569d48d9d908

Repair round 1 on PR head `f676a8f55b265a656b81d6ea313dde60c4365c3c` (verdict `verdict/3255`): `origin/main` merged (`git merge`), `tools/pr/prepr.sh` rerun on the merged head.

## Mutation proof

Repair round 1 (`node tools/policy/policy_lint.mjs`, 269 pins; null control: the unmutated tree, rc 0, no `FIXTURE VACUOUS`). New pins: `statsFindings` driven over synthetic merged PRs (three untaught words on three PRs -> exactly one `verdict family` would-open for `other (untaught)`; `mutation-unpinned` + `unpinned-site` + `mutation-survivors` on three PRs -> exactly one for `mutation`; a taught-only window -> none) and a shape pin holding `cmdStats` to the shared `derivedInput`. Each mutant of `tools/policy/policy_lint.mjs`, restored byte for byte after (`cmp`): `statsFindings` passing `null` instead of the derived input -> KILLED (rc 1); `cmdStats` passing no derived list -> KILLED; `mutation-unpinned` dropped from the `mutation` family -> KILLED; all three spellings dropped -> KILLED; `unpinned-site`/`mutation-survivors` dropped -> KILLED.

Round 0:

- `policy_lint.mjs` acceptance (267 pins at round 0): with the derived family's passing-verdict exclusion removed it prints `FIXTURE VACUOUS: the derived ...`; with `root-cause-unrecorded` removed from the declared family it does too. Both restored.
- `python3 tools/pr/ci_predict.py --self-test`: with the `mutants` arm's driver-selection line replaced by `if False:` the null-control row goes red. Restored byte for byte (`cmp`).
- Not mutation-proven: the `ARMS`/`arms` registration of `mutants` (the helper is driven directly; a deleted entry in `arms` would leave the self-test green). Stated in `R10-RCA-ROOT-CAUSE-DETECTABLE.md` section 7.

## Null control

- Every taught verdict row and every friction-id row of `node tools/policy/policy_lint.mjs --stats --since v7.0.4` prints byte-identically before and after the family changes (diff of the non-family rows empty); the literal `other` row still reads 2 PRs / 3 entries.
- `mutant_preds` over a diff touching no planted target runs no driver and predicts nothing; over the real tree with `README.md` changed it returns `[]`.
- The `root-cause` family reads 0 / 0 in this window (all three members file their own line): it adds no filing here, and the record says so.

## Figures

- `node tools/policy/policy_lint.mjs --stats --since v7.0.4` (517 merges, 450 with a verdict; run at the merge base): `root-cause-detectable` 12 PRs, `class-open` 32 PRs / 56 entries, `mutation-vacuous` 31 / 38, `mutation (family)` 1 / 2 -> 6 / 7 after the three added spellings, `other (untaught)` 65 / 78, `.claude/rules/gate-scoping.md` 12 / 13.
- `python3 -I tools/audit/seat/r10_ledger_mutants.py --self-test` and its three siblings: 0.71 s, 1.13 s, 0.33 s, 0.10 s (2.28 s together).
- `node tools/policy/policy_lint.mjs --budgets`: `.claude/rules/ci-autofix.md` against caps 96 / 1469 (the `--budgets` line is the figure; it fits).

## Red checks

none: `python3 tools/audit/seat/merge_train.py classify f676a8f55b265a656b81d6ea313dde60c4365c3c --pr 3255` read `GREEN ... red: none` over all 68 check runs of the previous head on one page; CI has not run on this repair head, and no concluded red exists across any check-run page. `tools/pr/ci_predict.py` ran inside `prepr.sh`.

## Carries

The dispatch brief's carries, numbered 1-8 here (the brief's own count starts at 0).

- Carry 1 (P259, the five records): answered. #2860 landed in #3000; #2840, #2835, #2895 and #2907 are judged sufficient and left unrewritten in `R10-RCA-FRICTION-SWEEP.md` section 1, each re-measured at this base. Merges only on tvofi's approving review (the `ci-autofix.md` edit).
- Carry 2 (#2875 and #2950): answered in `R10-RCA-ROOT-CAUSE-DETECTABLE.md` and `R10-RCA-CLASS-OPEN.md`, re-derived with `node tools/policy/policy_lint.mjs --stats --since v7.0.4`. The `class-open` countermeasure is a drafted `fixer.md` sentence that waits on the owner's ruling.
- Carry 3 (R10-RCA-FRICTION-RESIDUE countermeasures): landed, with demonstrations in `R10-RCA-FRICTION-SWEEP.md` section 4 (#2436, #2437, #2429).
- Carry 4 (#2942, mutation family): answered in `R10-RCA-MUTATION-VACUOUS.md` section 6: a new cause (a stale member list), not the old countermeasure failing; three spellings added.
- Carry 5 (FLOW-ANDON cost test): answered in `R10-RCA-FRICTION-SWEEP.md` section 3; the countermeasure was already built (#2582) and stays.
- Carry 6 (#2865, instrument self-tests): answered in `R10-RCA-ROOT-CAUSE-DETECTABLE.md` sections 3-7; the `ci_predict` `mutants` arm is landed.
- Carry 7 (#2998, mutation-vacuous): answered in `R10-RCA-MUTATION-VACUOUS.md`; the tools/ refusal is re-priced at 18 PRs and stands on an unpriced number.
- Carry 8 (#2835, gate-scoping, measure first): answered in `R10-RCA-FRICTION-SWEEP.md` section 2: 12 PRs / 13 entries, the keying rule and the gate do not change.

## Forward-carry

- The `fixer.md` sentence drafted in `R10-RCA-CLASS-OPEN.md` section 6 (a generated spelling corpus for text-shape guards) is policy and **waits on tvofi's ruling**; it is not landed. Carry: dismissed: drafted for the owner, nothing in this tree consumes it until approved.
- A `tools/` mutation table (`R10-RCA-MUTATION-VACUOUS.md` section 5) is unpriced; the refusal stands until a seat prices it. Carry: dismissed: the cost number that would reverse the refusal is not produced by any group.
- The wider arm (run `--self-test` of every changed wired instrument) is deferred until a second PR beyond #3049 fails its own self-test. Carry: dismissed: one instance does not make a class.

## Friction

- `.claude/rules/ci-autofix.md`: cost: the file had 3 tokens of headroom under its 1469 cap; the two approved sentences cost 33 over and were paid by shortening them and deleting the `linecache` paragraph, named under `## Approval`. Carry: dismissed: paid in this change.
