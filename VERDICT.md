Fix review: merge addd6f45758ff90ab862bcbe62357c1373ed7786

bus-nonce: e16feb4c527913888643bef5d6ffec67

# #2075 R9-RC-Carry-Pins, round 5 — adversarial fix review

Head reviewed: addd6f45758ff90ab862bcbe62357c1373ed7786
Reviewed from a detached worktree at that SHA, with the REVIEWER'S OWN harness
(built from scratch: /private/tmp/r5-harness-73312/harness.sh, harness2.sh).
Diff = 2 files: tools/pr/app_approve.sh (+165/-4), dev/programme/carries/carry-2075.json (+31/-0).

## 1. The round-4 seam is closed — REPRODUCED, with my own fixture

The claim: `git cat-file -e "$v:$p" 2>/dev/null && continue` in the directory
branch stops a second bot commit re-adding a path the first deleted.

- My fixture: bot commit 1 DELETES the reviewed row tests/mutation_ledger/killed_by/row.json;
  bot commit 2 RE-ADDS the same path with new bytes = net `M` on reviewed content.
  At the head: REFUSE ("the branch's own diff differs").
- Perturbation (my own, in a separate worktree at the same SHA): remove ONLY that
  line -> `--self-test` = 164 ok / 2 FAIL, and the 2 FAILs are exactly the
  H_DELREADD arm's pair ("NO CARRY: the bot's pin commit over a row the branch's
  own diff already carried" + "refused by the branch's own comparison, not the
  confinement check"). PINMOD/PINDEL/DELADD/PINGLOB and all 163 others stay green.
  No other check moves. Restored (byte-identical to head) -> 166 checks, 0 failed.
- Same fixture against a no-guard copy of the script -> my SEAM fixture flips to CARRY.

## 2. Both directions hold — pinned by my fixtures, not the fixer's

- held at `$v`, reviewed content, rewritten by a bot  -> REFUSE
- held at `$v`, reviewed content, deleted by a bot    -> REFUSE
- held at `$v`, reviewed content, delete+readd        -> REFUSE
- held at `$v`, MAIN's own row, delete+readd          -> REFUSE   (the "main owns it" arm)
- deleted then a DIFFERENT path added                 -> REFUSE
- path NEW at `$v` (fresh row) only                   -> CARRY    (positive control)
- file literally named `*` beside a rewritten row     -> REFUSE
Driving my fixtures against the no-guard copy flips BOTH the reviewed and the
MAIN-OWN delete+readd to CARRY and leaves the other five unchanged — so the guard
is load-bearing for the "main's own" direction too, and this fixture exercises the
guard, not just deletion visibility.
Driving them against a no-literal copy (:(exclude,literal) -> :(exclude)) flips
ONLY the glob fixture to CARRY — the token is load-bearing for exactly that case.

## 3. Failing-test-first — REPRODUCED

Spliced origin/main's carry() MECHANISM (verified byte-identical to main's) with
the branch's TEST-only hunks (my own splice, /private/tmp/r5-harness-73312/splice.py):
`--self-test` = 166 checks, 10 failed = the five fixtures (PINMOD, PINDEL, DELADD,
DELREADD, PINGLOB) x 2 checks. Matches the claim.
Measured, not cited.

## 4. The four body dispositions — checked, not accepted

(a) merge_train.py --self-test `81` dropped. Body now says only "passes, 0 failed"
    (no number). Underlying fact: the count IS moving — measured 95 checks, 0 failed
    here, and CI's instrument-self-tests logs "merge_train self-test: 95 checks".
(b) #2065 negative control re-quoted. Ran `--carry 3c9fe53f... 90b9e87f... origin/main`
    at BOTH the head copy and origin/main's copy: both refuse with exactly
    "90b9e87f7dece277cfbf46cbc64b2b3f816d841c is not the automatic merge of its parents".
    `a456c5ed` is now an ancestor of live main, so the round-3 reason has drifted. VERIFIED.
(c) BUDGET residual recorded in carry-2075.json. My own fixture: a bot-identity
    `ci: pin killed mutants` commit rewriting tests/mutation_budgets.json -> CARRY at
    #2075's head AND at origin/main's own copy. Control on the same fixture: a bot
    rewrite of a reviewed ledger ROW refuses at head / CARRYs at main (main's live hole).
    `node tools/policy/brief_lint.mjs dev/programme/carries/carry-2075.json` -> 0 errors,
    0 warnings, rc 0. `claims-for: 6.7.17` in both claim files == VERSION (6.7.17).
(d) counts re-taken at addd6f457, all REPRODUCED by me: self-test 166/0 (macOS);
    diffstat 2 files, 169 insertions, 4 deletions; layout "GUARD: 0 refusal(s) against
    7cd5a588cbbb"; structure.py "STRUCTURE RATCHET PASSED" rc 0; closure.py select
    "MODE: SCOPED -- 0 script(s) run, 33 scoped out" (keyed on the mode line). Also
    verified: origin/main self-test = 153 checks, 0 failed (body claims 153).

## 5. The #2010 staleness is main's, not the fixer's — AGREE

`1b72ca19f` (#2010) is an ancestor of live origin/main, and so are BOTH of its heads
`d67d8a44` and `87849cd2`. `--carry d67d8a44... 87849cd2... origin/main` CARRYs at the
head copy AND at origin/main's copy (round-4 measured REFUSE while #2010 was live).
The round-4 and round-5 code agree on this path; the change is main advancing.

## Owed by fix-review.md

- Step 11 (check-runs at the head): 42 runs, none pending, no non-success conclusions.
  All 17 required contexts of ruleset 23698884 have a run; ABSENT required contexts:
  NONE (the tip commit is authored by tvofi, so pull_request runs exist — the
  bot-tip-head no-PR-run case does not apply). `Analyze (python)` concluded success
  after ~20 min. `instrument-self-tests` logs "app_approve self-test: 168 checks,
  0 failed", matching the body's DERIVED 168. `gh pr checks` NOT used.
- Step 13: `git merge-tree --write-tree origin/main <head>` -> rc 0, no conflict.
- Hygiene: only 2 files in the three-dot diff; both claim files byte-identical to live
  main; no *_budgets.json leaf moved; VERSION / manifest / RELEASE_NOTES untouched;
  the body's named head equals the live head.

## What I cited rather than measured

- The mutation drive, features.py, optimality.py, golden.py and the heavy lanes:
  cited from check-runs (mutation success, etc.), NOT run here.
- CI's instrument-self-tests number (168): cited from the job log, not run here;
  my own macOS --self-test at the head is 166/0, measured.
- Light instruments run here: app_approve.sh --self-test, structure.py, layout.py,
  closure.py select, brief_lint, fold_ledger, merge_train --self-test, prepr --self-test
  (237 passed, 0 failed).

## Figures declined

- merge_train.py --self-test `81`: declined (moving; it is 95 now). Dropped from the body.
- The old `GUARD: 0 refusal(s) against f5fb67077eb1` and `161 checks` / `127 insertions`
  from the round-4 body: superseded; the live body carries the addd6f457 re-take.

VERDICT: merge.
