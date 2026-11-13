R10-CLOSEOUT-PREP, the grader half of the closeout-prep repair (topic r10-closeout-prep-p3). Part 2 (pull request 3553) hands off once this is on main. CI's `briefs` job grades with main's `tools/policy/brief_lint.mjs`, so part 2's data change (carry-201.json delisted from `tools/policy/legacy_control_files.json`) cannot pass until main's grader carries this hunk: `assertCarryControl` named carry-201.json literally for its legacy-narrowing example, so delisting it turned that check into a refusal. It now reads the example from `LEGACY_CONTROL_FILES` and reports an empty set as unexercised. This part changes no data, so CI grades this head's data with main's grader, which passes.

The hunk is part 2's `git diff 154dbb4c61..78325190f8 -- tools/policy/brief_lint.mjs`, applied unchanged to origin/main (applied cleanly with `git apply --check`; no re-derivation). Nothing else of part 2 is here.

## Head

c3111279442557c7f7a210012928d52f6addf404

## Mutation proof

Mutant: `const member = [...LEGACY_CONTROL_FILES].sort()[0]` replaced by `const member = 'not-a-member.json'` (a name outside the set). `node tools/policy/brief_lint.mjs` exits 1: killed, by a Node TypeError at `carryControlFindings` (`name.match(/\d+/)[0]` on a name with no digits), not by a CONTROL VACUOUS line. The empty-set branch has no mutant of its own; it is a guard that only fires on an empty set, which nothing in the tree can produce without deleting the data file. Restored; tree clean.

## Null control

Main's grader on main's data exits 0 with no VACUOUS line, and the unmodified `assertCarryControl` on part 2's data exits 1 (arm D below): the red this cures.

## Figures

Four arms, each `node tools/policy/brief_lint.mjs` (the linter's own no-arg run, which includes its self-test acceptance block and `assertCarryControl`; it is also the only step naming brief_lint.mjs in tests.yml, job `briefs`, step "Lint every wave roster's citations"), with the grader named and the data tree named:
- main's grader on main's data (origin/main 3fd9fab077f79b73509e231e064f9b852839c910): rc 0.
- this head's grader on main's data: rc 0, `grep -c VACUOUS` 0.
- this head's grader on part 2's data (tree 78325190f8): rc 0, `grep -c VACUOUS` 0: the case this exists for.
- main's grader on part 2's data (tree 78325190f8): rc 1, `CONTROL VACUOUS: carry control:` printed.
No mutant or fixture harness for `assertCarryControl` exists beyond the linter's own run; the changed lines are covered by the mutant above.

The generated scope-line block is left out of this body: update_pr.sh verifies it against its own merge head, which no body can name in advance (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH); the scope line is the gate's own MODE line at the head.

## Brief carries

This part is the grader half only (the brief's one owed pull request); it discharges none of the group's carries, and none is changed or lost here:
- Carry 0 (carry-file closure check): not discharged here. This part touches no carry file and no data; the delisting of carry-201.json and the carry files are part 2's (pull request 3553).
- Carry 1 (dev/README.md refresh against the tooling merges since R10-ARCH-DOCS): not discharged here; a docs edit outside this grader-only diff, left to the group's later part, for the orchestrator to route.
- Carry 2 (machinery caps record-down): not discharged here; it needs a re-measure at its own merge base and a budget-file edit, outside this grader-only diff, left to the group's later part, for the orchestrator to route.

## Red checks

none

## Forward-carry

none

## Friction

none
