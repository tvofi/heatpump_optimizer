Conflict resolution for #3384: main merged #3397 and #3341, which left `dev/governance/roles/fixer.md` conflicting in the "Before you hand off" paragraph. The resolution is a union of both parents' clauses in that file and nothing else. Reviewer: read the resolution delta only (`git diff 4ac47e9b5 7d3c52b79 -- dev/governance/roles/fixer.md`).

## Head

7d3c52b79c72de161350a2c4728aa84779758a24: the merge of origin/main (04dfcafcc) into 4ac47e9b5 (`2615e6010`), plus one commit that rewords one clause (below).

## Resolution

Branch parent (4ac47e9b5):

> `defect-root-cause.md`'s second trigger fires on your own PR: name each red in `merge_train.py owed-reds`' set, and no other, in the body and answer it there: the cheaper detector and its standing cost, or a recorded finding that none exists. `UNDER-SCOPED` and `INHERITED CLAIMS` are answered by naming them (`ci-autofix.md`); the analysis is `root-cause.md`'s seat.

Main parent (04dfcafcc):

> `defect-root-cause.md`'s second trigger fires on your own PR: name each check that went red in the body and answer it there — the cheaper detector and its standing cost, or the finding that none exists. `UNDER-SCOPED` and `INHERITED CLAIMS` are answered by naming them (`ci-autofix.md`). You name the trigger; analysing it is `root-cause.md`'s seat.

Union as merged:

> `defect-root-cause.md`'s second trigger fires on your own PR: name each red in `merge_train.py owed-reds`' set, and no other, in the body and answer it there: the cheaper detector and its standing cost, or a recorded finding that none exists. `UNDER-SCOPED` and `INHERITED CLAIMS` are answered by naming them (`ci-autofix.md`). You name the trigger; analysing it is `root-cause.md`'s seat.

Branch's clauses kept: the `owed-reds` set and "no other". Main's clauses kept: "You name the trigger; analysing it is `root-cause.md`'s seat." and the sentence form. Main's "name each check that went red" is superseded by the branch's narrower set, which is this PR's purpose. The first union draft used main's "or the finding that none exists", which `policy_lint` refused as `[duplicates]` against `.github/PULL_REQUEST_TEMPLATE.md`; the branch's "a recorded finding" avoids it. Read back: both phrases are present in the merged file and no conflict marker remains.

## Mutation proof

n/a: prose-only merge resolution, no behaviour changed. The one detector that bore on it is `policy_lint.mjs`: the first union draft turned it red (the `[duplicates]` error above), the reworded one passes.

## Null control

Before the reword, `policy_lint.mjs` on the first union draft reported 1 error; after, 0.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

Pending: this body does not record an approval. The diff touches policy files (`dev/governance/roles/fixer.md` here, and the PR's own policy edits), so the owner's approving review at head 7d3c52b79c72de161350a2c4728aa84779758a24 is required before merge (`main-protect-checks`'s code-owner rule). The resolution touches no policy beyond a union of two clauses already on the two parents.
