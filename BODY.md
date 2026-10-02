_Requested by **tvofi**_

R9-EG-R1: the permanent register fold. `tools/audit/fold_ledger.py` folds each audit round into `tools/audit/bugclasses.json`, `audit-verify.js` runs it after the class sweep, its `check` runs in the `wave-script` lane, and four policy clauses (decided under the programme mandate, D5) say how a class is minted, when it owes an RCA, and where the RCA lives.

Fixes #1759
Part of #201

Before: nothing in a round wrote the register. `audit-verify.js` read it and never folded into it, round 8 was never classified (its 39 survivors sat in no class), the judge could mint a class without comparing it with the nearest one, and an instance had no unit (a sweep printed "2 + 7" where the tool counted 2). R0 (#1763) landed the data; this lands the mechanism.

After:
- `fold_ledger.py fold --round N` appends `R<N> <finding id>` for each judge survivor and `R<N> sw:<file>::<symbol>` for each sweep seam marked `beyond_finding: true`, recomputes `rounds`, `per_round`, `total`, `max_per_round` and `trigger`, prints both terms of N per class, refuses a survivor with no class, a seam with no boolean `beyond_finding`, a new class without `nearest` (an existing id) and `differs`, and a survivor already in another class, and puts a new id in `finding.schema.json`'s `class_guess` enum. Two ids minted in one round with one `nearest` count as one for the trigger.
- `fold_ledger.py check` refuses an in-tree judge survivor (`tools/audit/round*/JUDGE.json`, verdict verified or weakened) in no class or two, an unparseable instance, a carried count or trigger the instances do not derive, a class that met a trigger (three in one round, three over three consecutive rounds, five while open, or any instance of a barriered class) with neither a barrier nor an `rca` whose document is in `tools/audit/rca`, a cited `rca` that `_rca` does not index, and an `in_tree_home` that is not a file. `refresh` rewrites the derived fields after a barrier PR moves a status.
- `audit-verify.js`: the sweep flags each seam and writes `sweep-<class>.json`; N is judged plus flagged seams (a sweep returning no list keeps its `instances` count); the judge reuses before minting; a `fold` step runs the script after the sweeps and stops the pass on a refusal; a `record` step opens the round-record pull request through `app_push.sh` only under `args.file`, else stops with the command (the App key is the Mac seat's, decision 0011).
- `governance.yml`: the `wave-script` lane runs `fold_ledger.py --self-test` and then `check` on the pull request's own copy, and `prepr.sh` step 3f5 runs the same two. The checker is owned (`CODEOWNERS`), not pinned: a first form restored the base's copy, and `field coverage` refused it (`pinned tools/audit/fold_ledger.py` is unregistered), because a pinned grader must be declared in the pinned `field_coverage.mjs`, so the branch adding one cannot pass (#1847's bootstrap red). Ownership is merge_fastpath.py's precedent for a grader a branch could otherwise weaken together with its data.
- Data: 10 classes' `trigger` had drifted (`barriered_any`) (a barrier PR moved `status`, nothing recomputed it); 80 of 95 `_rca` entries named a `tools/audit/rca/` file that does not exist at `origin/main`: 66 are now null, 13 point at `RCA-BULK-N.md`, and `R9-N-solve-recompute.md`, the one class RCA R0 omitted, is added byte-identical from `763b0ba4` (29 entries now name a file, 66 null).
- Policy: `judge.md` step 6 (reuse before minting, a class is a mechanism never a site, `nearest` and `differs`, two sharing a nearest count as one); `defect-root-cause.md` (the cross-round arms; an RCA is a document at `tools/audit/rca/<id>.md` and the issue keeps a short Root cause section); `D8.md` step 3 (families are the declared ones, #1760). `.cursor/rules/defect-root-cause.mdc` regenerated.

Not in this diff: R9's own survivors cannot be checked until `tools/audit/round9/JUDGE.json` lands in the tree (the round-record PR); the check reads what is in the tree. The R9 register rows are in the ledger from R0.

Design points, for the reviewer:
- The rule for an RCA citation (accepted by the coordinator): a class that met a trigger is answered by a barrier, or by a cited `rca` whose `_rca[...].in_tree_home` is an existing file under `tools/audit/rca`; every `in_tree_home` must be null or such a file, and every cited id must be indexed in `_rca`.
- `in_tree_home` was aspirational in R0's data (80 dangling). A class's RCA now counts toward its trigger only if its document is in the tree, which turned P4, P8, P10 and N-name-sort from "cited" to "documented" (their bulk documents are `RCA-BULK-1.md` and `RCA-BULK-4.md`). The 66 RCAs whose records live only in issues or PR bodies keep `in_tree_home: null`; rebuilding the 9 lost ones stays refused (RCA-BULK-2 section 3.4).
- A survivor placed in `_unclassified` with a reason counts as placed (R9 will have some); one in `_excluded` does not.
- The checker runs as the branch's own copy, so a branch that edits it and the ledger together is stopped only by ownership; CODEOWNERS now names it, and the review at the head is where that is read.

## Head

`22ebb9a9794c590f355bbd3a248b93c851fd0dbc` (a merge of `origin/main` `5f87e25a110ff0a6fad179283b21f3823d0cd1f1`, #1854, into e48202035; the three earlier commits were measured on `948671af1`, #1847, and re-measured here after the merge); commits 78f5c316 (fold_ledger.py and data), c73557bf (audit-verify.js, check-wave-script.mjs, governance.yml), 606ad289 (policy clauses and the three per-file caps), and the commits that add the prepr step and move the lane to the branch's own, owned copy.

## Mutation proof

`python3 tools/audit/fold_ledger.py --self-test` holds 28 of 28 expectations, on planted ledgers. Each predicate mutated in a copy, the self-test run (never a line past a return):

| mutant | red expectations |
|---|---|
| `UNPLACED` branch `if False` | 1: a survivor in no class |
| `OWED` predicate `if False` | 6 |
| the rca document must exist -> any cited rca answers | 1: the missing document |
| the derived-count comparison `if False` | 1: a carried total |
| `SURVIVES` gains `refuted` | 8 |
| the `nearest`/`differs` refusal `if False` | 2 |
| the `beyond_finding` boolean refusal `if False` | 1 (a crash in the mutant is reported as a failure, not as a refusal) |
| cross-round window -> `False` | 1: three over three consecutive rounds |
| sibling grouping `if False` | 1 |
| `DANGLING` check `if False` | 1 |

`node .claude/workflows/check-wave-script.mjs` (160 passed, 0 failed) against `audit-verify.js` mutants: N ignores the flag, 1 red; fold refusal does not stop the pass, 1; fold step never runs, 3; the judge prompt loses reuse-before-minting, 1; the record step opens the PR whatever `args.file` says, 1. A first run of the self-test found the fold writing `R2_sw:` for `R2 sw:` (a replace over the whole string); fixed before step 1 was committed.

## Null control

The demonstration the brief names, `check` on the register at four trees (the ledger and `round8/JUDGE.json` from each; `$S` is a scratch dir):

| register | rc | result |
|---|---|---|
| `3490cb16` (v1, the register the RCA measured) | 1 | 39 UNPLACED (all of round 8), 12 OWED, 195 violations in all |
| `9d52e5a11` (round 8's register, the first main commit carrying both the ledger and `round8/JUDGE.json`; `9fd07379` holds the JUDGE but not the ledger) | 1 | 39 UNPLACED, 159 violations |
| `948671af1` (v2 as R0 merged it; measured with the one added RCA document present, so 79 not 80 DANGLING) | 1 | 79 DANGLING, 10 DRIFT, OWED P4, P8, P10, N-name-sort: 93 violations |
| this head | 0 | 0 violations; 28 classes, 549 instances, 39 in-tree survivors (round 8), 95 rca entries |

Null control for the green row: the self-test's first expectation (a ledger placing its survivor once, nothing owed, passes), and the check prints the survivors it read (39) beside the violations, so a read that found no JUDGE file would show 0 survivors rather than a clean zero.

## Figures

- Register at head: `python3 tools/audit/fold_ledger.py check`
- Register at 3490cb16, round-8 register and v2 as merged: `python3 tools/audit/fold_ledger.py check --ledger "$S/led-<ref>.json" --judge "$S/judge-<ref>.json"`, each file from `git show <ref>:tools/audit/bugclasses.json` and `git show <ref>:tools/audit/round8/JUDGE.json`
- Self-test: `python3 tools/audit/fold_ledger.py --self-test`
- Wave script: `node .claude/workflows/check-wave-script.mjs`
- Policy: `node .claude/workflows/policy_lint.mjs`, `node .claude/workflows/policy_lint.mjs --budgets`, `node .claude/workflows/rules_sync.mjs --check`
- Structure ratchet: `python3 tests/structure.py`
- Field coverage, 0 refused: `node .claude/workflows/field_coverage.mjs`
- Agreement lane: `node .claude/workflows/agreement.mjs --self-test`
- Pinned graders and the owners surface, 0 uncovered: `bash tools/audit/prepr.sh --self-test`, `python3 -I tools/audit/round6/D11/fix/codeowners_gap.py --check`
- Scoped gate, `MODE: SCOPED`, two scripts: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`. Both run with numpy and scipy from the F11.4 venv, `PYTHONPATH=tests/hastub`, `GOLDEN_MODE=drift`: before the last merge of main (#1848) `tests/entities.py` ALL 2062 ENTITY CHECKS PASSED; at this head it reports 1 of 2071 failed, `no job-level if leads with always()` naming `tests.yml:mutation-ledger` and `mutation-ledger-push`, and `git diff origin/main -- .github/workflows/tests.yml` is empty, so that red is not from this diff's files. `tests/harness_headers.py` ALL 94 HARNESS HEADER CHECKS PASSED at this head.
- Step-8 instrument: the class is "the register decays after a round"; its seams are the places a round's result can be dropped or counted two ways. `fold_ledger.py check` enumerates the first (survivor in no class or two, derived field drift, trigger without answer, dangling rca), and `audit-verify.js`'s `classes` object enumerates the second (`judged` and `beyond_finding` printed beside `n`). Readers of the ledger checked for agreement: `agreement.mjs` (ledger ids vs `class_guess`) and `check-wave-script.mjs` (`class_guess` enum equals the ledger ids) both pass at this head.

## Red checks

none. No CI run exists for this head yet. Expected on this pull request, stated now: `budget-raise-gate` red until tvofi's approving review at the head (three per-file policy caps rise).

## Approval

Not yet given. This diff touches policy (`.claude/rules/defect-root-cause.md`, `tools/audit/briefs/judge.md`, `tools/audit/briefs/D8.md`, `.cursor/rules/defect-root-cause.mdc`), code-owned paths (`.github/workflows/governance.yml`, `.github/CODEOWNERS`, `.claude/workflows/audit-verify.js`, and `tools/audit/fold_ledger.py`, which this diff makes owned) and a budget raise (`.claude/workflows/policy_budgets.json`, per-file caps only: `defect-root-cause.md` 146 to 150 lines and 1774 to 1848 tokens, `D8.md` 55 to 56 and 789 to 808, `judge.md` 29 to 30 and 415 to 469, each the value `policy_lint --budgets` measures; the five aggregates stay inside their band; each clause was cut to its shortest form first). The four clauses were decided under the programme mandate (rev 3.1, D5: adopt as specified in RCA-BULK-2 section 3.4 and RCA-BULK-4 section 6); the raise is announced on #201 (comment 5957148777) under the programme mandate. #1856 (F11.5) also raises `defect-root-cause.md`'s caps: whichever PR merges second re-measures on the merged tree, so this PR's value for that file may need one re-record after #1856 merges. It merges only on tvofi's approving review at the head.

## Forward-carry

- The R9-RO-2 roster group (the round-9 close-out; its roster lives on the handoff/audit-r9-fixplan ref, not in this tree): the round-record PR lands the R9 register section and round9/JUDGE.json, after which `check` reads R9's survivors, and each `_unclassified` row R9 adds needs a reason (the check requires one).
- `tools/audit/README.md` names no `fold_ledger.py` step; its cap is at zero headroom, so the mechanism is described in the script's docstring and this body. R9-RO-2 (the round close-out) should add the one line when it next touches that file.

## Friction

- `gate-scoping: contradiction`: the first form of the lane (a pinned checker) passed `prepr.sh`'s pinned-graders step only after it was made locally runnable, and then failed `field coverage`, a different local step, for the same reason CI's `policy-docs` would have. Two prepr steps and one lane each knew a different half of what a new pinned grader owes.
