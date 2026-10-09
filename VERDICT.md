Fix review: blocked 250c1564795a187334205f006d7bb055163fb102 harness: class-open a delete-then-readd of a reviewed ledger row across two `ci: pin killed mutants` commits still carries at this head; one line inside the same mechanism closes it and passes all 161 of the PR's own checks

bus-nonce: 3707092c4403c1dcc5d987b7bc22c91b

**This is round 4**, so `fixer.md` owes a re-cut, not a repair. Evidence:
`/Users/timmalmstrom/hpo-seats/review-2075-r4/evidence/` (head.txt, matrix.txt,
delreadd.txt, selftests.txt, ci.txt, red-history.txt, hygiene.txt, harness/).
Instruments are this reviewer's own, disclosed per `fix-review.md` step 9 in
`evidence/harness/README.txt`: the finding below has **no committed harness in
the tree** — `--self-test` builds no two-commit delete-then-readd.

## Head discipline

`gh pr view 2075 --json headRefOid` read at start and again immediately before
this push: `250c1564795a187334205f006d7bb055163fb102` both times, non-draft,
open, base `main`. Review ran from a detached worktree at that SHA
(`review-2075-r4/head`), left clean (`git status --porcelain` empty).
`origin/main` = `23d354970`, merge-base = `f5fb67077` — the base the body names,
still current. `dev/governance/roles/` diff merge-base...origin/main: empty.

## The block ground

`carry()`'s new accumulation excludes, per bot commit, the paths that commit
**ADDED** under a `bot_paths` directory. The exclusions are unioned across the
whole `v..h` range. So a range of two bot commits — the first **DELETES** a row
the verdict head's own diff reviewed, the second **RE-ADDS the same path** with
different content — puts that reviewed path back into the exclusion, and the
comparison below stops seeing it. Neither commit is a rewrite; the pair is one.

RESULT DELREADD fixture V=46811fe11132c7b607922840659be4004b2040a9 row=tests/mutation_ledger/killed_by/row.json reason@V="reviewed" reason@head="delete then readd" net=`M` — both commits `ci: pin killed mutants`, both `41898282+github-actions[bot]@…`, both confined to `tests/mutation_ledger`
RESULT DELREADD at 250c15647 `CARRY: yes … only automatic merges from origin/main, ci: commits and the autofix bot's own, and the branch's own diff compares equal` rc=0
RESULT DELREADD at origin/main's copy CARRY rc=0 (main carries it too — this is a hole the fix does not close, not one it opens)
RESULT DELADD control (delete the reviewed row, then add a DIFFERENT row) at 250c15647 REFUSE rc=1 `the branch's own diff differs` — so the bypass is exactly "the later commit's addition re-covers the path an earlier commit deleted", not deletions in general

This falsifies the body's own load-bearing sentence, read at the head rather
than at the commit: *"`carry` must not accept a head whose only change over the
verdicted head is a `ci: pin killed mutants` commit that REWROTE or DELETED a
ledger row the reviewer already measured"*, and *"An entry that is a DIRECTORY
… contributes only what the commit ADDED beneath it -- never a rewrite or a
deletion, which stays visible to the comparison below and refuses."* The
deletion does not stay visible when a later commit in the same range re-adds the
path. `mutation-autofix` pushes one commit per run and re-dispatches
`tests.yml`, so a range holding two pin commits is the normal shape, not an
exotic one; the forge required is the one this file already assumes ("Anyone who
can push can write the subject", "git metadata anyone can write").

**It is one line short, inside the mechanism it already has.** Skip an added path
that existed at the verdict head — that is what makes it reviewed content rather
than new bot content:

```
-              case "$p" in "$e"/*) bots="$bots$p"$'\n' ;; esac
+              case "$p" in "$e"/*) ;; *) continue ;; esac
+              git cat-file -e "$v:$p" 2>/dev/null && continue
+              bots="$bots$p"$'\n'
```

RESULT vbase (that one line) DELREADD REFUSE rc=1 `the branch's own diff differs`
RESULT vbase `bash tools/pr/app_approve.sh --self-test` → `app_approve self-test: 161 checks, 0 failed` — the closure is a drop-in: it breaks no arm the PR has, so it is not a trade against anything the fixer built
RESULT vbase over the whole matrix: identical to the head on all nine other attacks (A2/A3/A9/DELADD/OUTSIDE/FORGE REFUSE, BUDGET/OKADD/OKGLOB CARRY) — the perturbation moves exactly the one seam, so the finding is not void (`judge.md`)

## Measured matrix — `carry` at V, ten attacks, five copies

Full reasons in `evidence/matrix.txt`. Fixtures are this reviewer's, built by
`evidence/harness/build_fixtures.sh`; the runner reports any rc>1 as
`HARNESS-ERROR`, never as REFUSE (a first take silently recorded rc=127 as a
refusal and was re-run).

| attack (all bot-authored `ci: pin killed mutants` unless noted) | origin/main | **250c15647** | no_literal | no_narrow | vbase |
|---|---|---|---|---|---|
| A2 rewrite the reviewed row | CARRY | **REFUSE** | REFUSE | CARRY | REFUSE |
| A3 delete the reviewed row | CARRY | **REFUSE** | REFUSE | CARRY | REFUSE |
| A9 add a file named `*` beside a rewrite | CARRY | **REFUSE** | **CARRY** | CARRY | REFUSE |
| DELREADD delete + re-add the same path | CARRY | **CARRY ← seam** | CARRY | CARRY | **REFUSE** |
| DELADD delete reviewed row + add another | CARRY | **REFUSE** | REFUSE | CARRY | REFUSE |
| BUDGET rewrite `tests/mutation_budgets.json` | CARRY | CARRY | CARRY | CARRY | CARRY |
| OUTSIDE reach past the subject's paths | REFUSE | REFUSE | REFUSE | REFUSE | REFUSE |
| FORGE the rewrite under a seat's author | REFUSE | REFUSE | REFUSE | REFUSE | REFUSE |
| OKADD add one fresh row (positive control) | CARRY | CARRY | CARRY | CARRY | CARRY |
| OKGLOB add only the file named `*` (positive control) | CARRY | CARRY | CARRY | CARRY | CARRY |

Both positive controls carry at the head, so the narrowing does not over-tighten
the legitimate pin commit; the two confinement/author refusals are unchanged.

## What reproduced, from the body's own claims

RESULT `bash tools/pr/app_approve.sh --self-test` at 250c15647 → `app_approve self-test: 161 checks, 0 failed` — body's figure
RESULT `--self-test` at the merge base f5fb67077 (main's own copy, own worktree) → `153 checks, 0 failed` — body's figure, and the 8-check difference is the four arms plus their paired reason-greps
RESULT null control, main's mechanism + the head's test-only hunks spliced (`evidence/selftests.txt` records the splice verified two ways: first 450 lines byte-identical to main, self-test section byte-identical to head) → `161 checks, 6 failed`, the six names the body lists — the failing-test-first run reproduces
RESULT `no_narrow` (body's mutant 1) → `161 checks, 6 failed`, the same six names
RESULT `no_literal` (body's mutant 2) → `161 checks, 2 failed`, only the `*` arm ×2 — the glob defect is separated from the narrowing, as claimed
RESULT round-2 defect 2 closed: no `command not found` anywhere in the 161-check log; the arm is `NO CARRY: a path named '*' is not a wildcard, it is one added file`, its `*` intact, quoted with `'` not a backtick, and it is live — it is one of the 161 and one of the two `no_literal` reddens
RESULT round-2 defect 3a closed: no `all four` claim survives in the body; it now says four arms added, three reddened, 6 checks = 3 fixtures × 2 assertions, and `H_PIN_BADMSG` green at base. All of that measures as stated
RESULT round-2 defect 3b closed: both mutants are now specified as edits in the body, and both reproduce byte-for-byte against the behaviour described
RESULT round-2 defect 3c closed: `git diff --quiet origin/main HEAD -- tools/policy/policy_lint.mjs` clean; the file is not in the three-dot diff, and the body says so
RESULT reframe honest: A2/A3/A9 reproduce `origin/main's copy=CARRY / 250c15647=REFUSE` on this reviewer's own fixtures, and the REFUSE baseline for a bare added row is stated by SHA (`b2b6acd64`, pre-#2059) rather than as "main"
RESULT #2071 `6aaba97f…` → `7843b799…`: CARRY at main's copy and at 250c15647 (main ref f5fb67077)
RESULT #2070 `3ecb86ad…` → `a9ba0b88…`: CARRY at both
RESULT #2010 `d67d8a44…` → `87849cd2…`: REFUSE at both, `the branch's own diff differs`
RESULT #2010 `norm()` re-derived with carry's own pipeline (`evidence/harness/norm2010.sh`): left 16965 lines, right 16965 lines, `diff` prints 4 lines of which one `<` and one `>`, both leading-space context, zero `+`/`-` lines — the body's figures exactly, and identical against f5fb67077 and against live origin/main
RESULT `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`, rc 0
RESULT `PYTHONPATH=tests/hastub python3 tests/layout.py` → `layout: GUARD: 0 refusal(s) against f5fb67077eb1`
RESULT `python3 tests/closure.py select --diff f5fb67077 --workdir <head>` → `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` (keyed on the mode line, per CLAUDE.md rule 1)
RESULT `git diff --numstat f5fb67077 HEAD` → `96 4 tools/pr/app_approve.sh`, `31 0 dev/programme/carries/carry-2075.json`; 2 files, 127 insertions, 4 deletions — the body's figures
RESULT `node tools/policy/brief_lint.mjs` → `== dev/programme/carries/carry-2075.json ==  -- 0 error(s), 0 warning(s)`, exit 0; `effect` is `narrows`, and `control`/`remeasure`/`brief` are all present and carry the control, not only the claim (step 10)
RESULT both claim files byte-identical to live origin/main; no `*_budgets.json` leaf in the diff, so none moved up; `VERSION` (6.7.17), the manifest and `RELEASE_NOTES.md` untouched
RESULT step 13: `git merge-tree --write-tree origin/main 250c15647…` → exit 0, tree `00f3cc472…`, nothing on stderr. No conflict on any path, so no `MERGE-CLAIM: refused` line to report either
RESULT step 14: the diff moves no budget, ledger, closure, `INERT` entry, golden or claim file, and no architecture score — the only figures it earns are `--self-test` counts, every one of which is re-derived above

## Step 11 — CI, read off the head's own check-runs

42 runs at `250c15647…`; **all 17 of ruleset 23698884's required contexts have
a `completed/success` run, none is ABSENT, none is pending, and no run at this
head has a conclusion other than success/skipped/neutral** (`evidence/ci.txt`,
fetched 2026-10-09T23:54+0200). `budget-raise-gate` and `pr-contract` each have
two runs, both success — no red-then-green hidden by a one-run-per-check listing.
`governance`-family contexts the dispatch brief asked about are all present and
green: `pr-contract`, `policy-docs`, `env-matrix`, `budget-raise-gate`,
`wave-script`.

The range, not just the head (#1144): of the 8 commits in
`pulls/2075/commits`, only the first head `094f2c0d2` has any red —
`pr-contract` (id 113894588362) and `fast (3.14)` (id 113892203905), the exact
two ids the body names. Both are answered in `## Red checks` with the cheaper
detector (`tests/layout.py`'s retired-path guard, standing cost nothing further
— it already runs on every pull request) and the fix is deletion of the dead
fallback rather than an allowance over it. This review independently measured
`GUARD: 0 refusal(s)` at the head, so the answer is not taken on trust. No red
is left unanswered.

## Two figures I could not re-take — stated plainly, not carried

RESULT `python3 tools/audit/seat/merge_train.py --self-test` → **84 checks, 0 failed** at the head AND at the merge base f5fb67077 in its own worktree. The head's `merge_train.py` is byte-identical to the base's, so both readings are the same file. **The body's 81 does not reproduce and I could not establish its provenance.** Not load-bearing: the claim it supports (that all three of merge_train's first `TOOLS` candidates are gone) I verified directly — `find tools/audit -maxdepth 2 \( -name app_approve.sh -o -name app_push.sh -o -name preflight.sh \)` returns nothing.
RESULT #2065 negative control: the conclusion reproduces (REFUSE at main's copy and at 250c15647) but the **reason does not**. The body quotes `… merges a456c5ed…, which is not on origin/main`; I measured `90b9e87f… is not the automatic merge of its parents`, because `git merge-base --is-ancestor a456c5ed origin/main` is now true — live main moved past it. A stale quoted reason against an advanced main, not a defect in the fix; the arm still refuses for an unrelated reason, which is all the body uses it for.
RESULT the dispatch brief's `claims-for:` item does not apply: `carry-2075.json` has no such key and `brief_lint.mjs` does not ask one of a carry file (no match for `claims-for` in it). That rule is `env_drift.py`'s, for the two claim files, which this diff leaves byte-identical.

## A second seam, lower, already half-dispositioned

RESULT BUDGET — a bot commit rewriting `tests/mutation_budgets.json`, the single **file** `bot_paths` names, whose content the branch's own diff reviewed: CARRY at 250c15647, at origin/main, and at every variant including vbase, because the file branch (`grep -qxF "$e"`) excludes it whole. The body names the behaviour ("excluded whole, as before") but not the residual risk, and `carry-2075.json` does not mention it. Two things lower it below a block of its own: it is main's behaviour unchanged by this diff, and a hidden budget raise still reddens `budget-raise-gate` at the new head, since that required context re-runs on the pushed SHA. If the re-cut touches this, the carry file is where the disposition belongs.

## One instrument trap this review hit, worth carrying

`python3 tests/closure.py select --workdir <dir>` **writes** `scope.json`,
`scope.run`, `scope.skip` and `scope.txt` into `<dir>`. A second run in the same
workdir reads those four untracked files as changed and prints
`MODE: FULL -- every test script runs, nothing is scoped out. reason: no
recorded closure mentions scope.json, scope.run, scope.skip, scope.txt`. That is
CLAUDE.md rule 1's exact ambiguity — the two mode lines print the same zero and
mean opposite things — reached without touching the PR. My first take read FULL
and was wrong; the figure above is the clean-workdir re-take, and the worktree
was left clean. Any seat re-deriving a `MODE:` line owes a `git status` before
it trusts the mode.

## What the re-cut owes

The one-line `vbase` closure (or a sounder equivalent) plus an arm for the
two-commit delete-then-readd, so the seam is pinned by the tree and not only by
this verdict; and, if the fixer judges the BUDGET seam out of scope, its
disposition in `carry-2075.json` rather than only in the body. Everything else
in the body measured as written.
