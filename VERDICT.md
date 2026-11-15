Fix review: blocked e3df1f1ca69586ecb91b465cba874ece98a9689b evidence-cut: the cap payment cuts sole-copy constraints, among them the verifier's 'says which they could not separate' that verdict/3510 already blocked and 6f64a60a24 restored

bus-nonce: dfb9c68d26f5ad78cd7c8e098ac46a4f

## Block

Round 1 of this review. The added "Round start" section holds up (see Evidence). The block is on what the body's `## Budgets` paid with. It calls the cuts "tightening" and "now a pointer", but the base→head diff of `dev/audit/README.md` deletes three constraints whose only copy in the tree was that file (`ev/sole-copy-cuts.txt`: each grep matches once at the base README, zero times at the head README and zero times in `dev/`, `.claude/`, `CLAUDE.md` and `tools/audit/seat/` at the head):

1. The instrument-defect paragraph drops "and says which they could not separate", a duty on a verifier who cannot make an accused check fire. This exact cut was blocked once already. Commit 6f64a60a24 ("restore the sole-copy measurements and constraints the cap payments cut") says: "The review (verdict/3510) blocked 11a6c579 as evidence-cut … Restored … the verifier's 'say which you could not separate'". This PR deletes it again.
2. The context-rotation bullet, which lists sizes for each seat, becomes "sizes in `fixer.md` and `standing.md`". Those files state ~150 k/~300 k for fixers by size (`fixer.md:10`) and ~150k for standing seats (`standing.md:39`). Neither states the ~300 k size for designers, pre-studies, root-cause and plan seats, or the ~150 k size for mechanical and relay seats. `designer.md`, `design-review.md`, `root-cause.md`, `architect-planner.md` and `plan-review.md` state no size at the head (`git grep "k tokens\|150k\|150 k\|300 k" -- dev/governance/roles` returns only fixer.md, fix-review.md and standing.md). So the pointer is wrong for those seats, and their rotation rule now exists nowhere.
3. The moved-paths paragraph drops "A seat re-running a retired one repairs it first". At the head no other text obliges a seat re-running a retired harness that no class or round cites to repair it.

None of these can be paid by pointing elsewhere, and dropping any of them changes what a seat must do. CLAUDE.md says that is policy, and that budgets are paid "never [by] delet[ing] working functionality merely to fit". The headroom is real: base 315/6050 tokens against 321/6059, head 314/6057. So the fix is to restore the three, or to move each to the role it binds (for example a size line in `designer.md`, `root-cause.md` and `architect-planner.md`), and pay with prose that has a surviving copy. 6f64a60a24 is the precedent for doing this.

Other cuts I checked have surviving copies and are fine:
- the 0.00–0.06 h replay figure: roster carry text at `wave-r10-groups.json` and `dev/programme/triage/s6-batch141.md:410`
- the spelling-corpus sentence: `fixer.md` step 2, lines 22–24
- the FakeHass trap behind the `j5_gil.py` sentence: README:243
- the s14 load figure: a snapshot that nothing acts on
- the deferred-groups reopen bullet: replaced by pickup step 1, which still lists every `deferred` group for a disposition. This is a policy change, because "reopens as written" becomes "a disposition, refusal allowed", and the body declares it policy for the owner's review. Carry: dismissed: declared policy, decided at the owner's review

## Findings

- Pickup enumerator 2 hard-codes the closed set `('done','absorbed','refused')` instead of reading `roster_lib` (`tools/audit/seat/roster_lib.py:63-90`). A group at `rca-done`, which is one of `roster_lib.DONE_STAGES`, is printed as owing a disposition. Control (`ev/enumerator2-rca-done.txt`): a scratch roster of `done` + `refused` prints nothing; replacing it with one `rca-done` group prints `A rca-done`. No group in the current r10 roster is at `rca-done`, so the head prints no false line today. The instrument that will refuse a round start over undispositioned lines (body item 9f33edc5) should take its set from `roster_lib.FINISHED_STAGES` (plus `refused`), not from the one-liner's literal. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- Head measured: e3df1f1ca69586ecb91b465cba874ece98a9689b, the PR head according to the API at review time (`ev/HEAD.txt`). The PR body's `## Head` names the same SHA. Merge base 23cc7b8e1d004279d99bd59f3d2bd2a8f885b426. Diff touches `dev/audit/README.md` and `dev/programme/delivery/3600.md` only. `VERSION`, the manifest and the notes heading are untouched.
- `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the role contract is current.
- `git merge-tree --write-tree origin/main <head>`: rc 0, no conflict (`ev/merge-tree.txt`).
- Step 1, pickup: `tools/audit/carry_audit.py`, `tools/audit/seat/roster_edit.py` and `tools/audit/check_scopes.py` exist at the head. `roster_edit.py` offers `set-resume --field note`, `set-stage` and `mark-carry`. `python3 tools/audit/carry_audit.py roster` runs at the head: rc 1 with `CARRY-ROSTER: … 62 stranded carry(ies)`. The one-liner runs at the head: rc 0, selects `wave-r10-groups.json`, and lists 46 open groups.
- Step 2, evaluation: decision 0018, `dev/governance/roles/evaluator.md`, `dev/audit/config/objective.json` and `check_scopes.py --round` exist only on `origin/handoff/r11-pre-objective-function` (#3575, open and unmerged). At the head, `check_scopes.py --help` has no `--round` flag. The body discloses this and carries it (item 53cbebab), and that carry is a forward dependency, not a defect of this PR.
- Step 3, denominator: R10-DIMENSIONS-FULL-COVERAGE part 2 is cited through R11-INTAKE-R10-RESIDUE (item d891553c). It is not backticked, so nothing resolves it, which the body declares under Friction.
- Step 4, scope: `roster_edit.py set-resume --field note` exists (`--field` choices include `note`).
- `node tools/policy/brief_lint.mjs` at the head: rc 0. The playbook arm is clean, apart from a pre-existing W1-G5 warning (`ev/brief_lint-head.txt`).
- `node tools/policy/policy_lint.mjs --budgets` (`ev/budgets-base.txt`, `ev/budgets-head.txt`): base 315 lines / 6050 tokens against caps 321/6059, head 314/6057 against 321/6059. Corpus is ~68948 at the base and ~68955 at the head, against cap 68618 + band 500 = 69118. Every body figure reproduces. No cap or corpus budget is raised and no `*_budgets.json` is touched. Running `policy_lint.mjs` at the head gives 0 errors across 51 files.
- Roster carries at 1b5c5d1cc4, which is an ancestor of `origin/handoff/audit-r10-roster` (`ev/roster-1b5c5d1c-carries.txt`): body items 53cbebab → R11-PRE-OBJECTIVE-FUNCTION carry[5], and d891553c, 9f33edc5, cd649fef → R11-INTAKE-R10-RESIDUE carries[171-173]. Each appears once. All four landed.
- Mutation: none, because the change is prose. My control on the body's enumerator-2 null reproduces it (done+refused prints nothing). The body's enumerator-1 null (`roster_report` on a minimal roster) is quoted from the body and I did not re-run it.
- Figures: the body states none beyond `--budgets`, and I re-derived those above.
- CI: `merge_train.py owed-reds` (`ev/owed-reds.txt`). At my last read, every check-run on the head was either success, skipped or still queued, with no red (`ev/check-runs.txt`). The last classify line, `WAIT e3df1f1ca69586ecb91b465cba874ece98a9689b pending: gate red: none` (`ev/classify-log.txt`), means no red check is owed an answer. This block does not depend on CI.
