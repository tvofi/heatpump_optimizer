# R10-RCA-HEADMOVED: heads that move under a review, after the round-10 flow fixes

This is the root-cause seat for issue **#2389** (`[policy] recurring friction:
head-moved (rework)`). It follows the root-cause seat's contract
(`root-cause.md`, under `dev/governance/roles/`) and
`dev/governance/rules/defect-root-cause.md`. It ran at `origin/main` `6d86acc9`
on 2026-10-28.

The owner asked for this write-up on 2026-10-18 (#2389, comment 6249068534).
Since then, three countermeasures from the Lean flow study have landed:

- `fixer.md`'s absorb rule (K5, R10-POLICY-FIXER-MD, `2788ce34`, 2026-10-24): a
  fixer merges `origin/main` before handoff only on a conflict or a `DIRTY`
  head.
- The relay freeze (R10-FLOW-ROSTER-FREEZE arm (a), #2792, merged
  2026-10-25T07:38Z): `HELD-REVIEW`, `HELD-VERDICT` and `HELD-UNREAD` in
  `cloud_relay.sh`.
- The merge queue was ruled out for round 10 (tvofi, 2026-10-25; #2826).

So this record measures **what remains**. It splits the window at
2026-10-25T07:38Z, when #2792 merged.

Evidence lives in `dev/audit/rca/headmoved/`. Each script reads the previous
script's output. Run them in this order, from a directory that holds the checkout
as `wt/` and the two carry scripts as `aa_base.sh` (main's) and `aa_fixed.sh`
(this branch's):

1. `hm.py` enumerates the entries.
2. `hm2.py` classifies each move against main at the time, and runs the carry
   of that time.
3. `hm3.py` checks whether the branch's own patch moved.
4. `hm4.py` sorts entries into buckets.
5. `hm5.py` applies section 11's whole predicate.
6. `hm6.py` runs the fixed carry.

## 1. The count, reproduced

- **Bus harness.** `hm.py` reads the `VERDICT.md` history of all 588
  `verdict/*` and `review/*` bus refs. An entry is a verdict whose predecessor
  on the same pull request was `merge` at a different head. This is the same
  rule as `policy_lint.mjs`'s rework arm.
- **Entries.** There are **75 entries on 55 pull requests**, from 2026-10-15 to
  2026-10-28:
  - 54 entries fall before the split, against 467 PR merges on main from
    2026-10-14.
  - 21 entries, on 12 pull requests, fall after it, against 87 merges.
  - Per merge, that is 0.116 before and 0.241 after.
- **`policy_lint.mjs`'s count.** `node tools/policy/policy_lint.mjs --stats
  --since v7.0.0` (about 20 minutes) prints:
  - `59 re-verified a head that moved after a merge (44 PR(s))`, over 354
    merged pull requests that carry a verdict;
  - `5 / 7 head-moved`, the reviewer-written breach row.

  The bus count is higher because the bus also holds pull requests that are
  still open, and verdicts that were never posted to the pull request.
- **Breach verdicts.** These are verdicts that say `blocked <sha> head-moved`,
  matched in the first five lines of `VERDICT.md`. There are 10 such verdict
  commits:
  - **Before the split: 6.** #2465 is a fixer push. #2559 ×3 is the roster pull
    request on 2026-10-21. #2775 ×2 is one bot `ci: merge main`.
  - **After the split: 4, covering 2 moves.**
    - #2830: the orchestrator account pushed `d4f71c00` ("triage: batch 30,
      answer verdict ... findings") onto the head under review.
    - #2853: the orchestrator account merged main by hand (`25a6f0e8`) while
      the review was in flight.

## 2. What moved the head

`hm2.py` to `hm5.py` classify the first-parent delta of each entry. They use
`origin/main` as it stood at the verdict (`rev-list --before`), not today's.
Today's main holds every merged branch, so a check against it reads all 75 as
"merges from main". The same mistake also makes today's carry say `yes` for 64
of the 75, where the carry of the time said `yes` for 19. This is the trap
R9-RCA-1990 named.

In the table, **lag** runs from the head's commit to the verdict that
re-measured it. It is an upper bound on review cost, because it includes CI and
queue time.

| bucket | entries | after split | blocked | lag median (min) | lag sum (min) | what it is |
|---|---|---|---|---|---|---|
| 1 carry unused | 6 | 1 | 0 | 52.5 | 291 | `orchestrator.md` §11's whole predicate held at the time (`CARRY: yes`, moved files miss the own diff, claim files equal main's), and a reviewer was dispatched anyway |
| 2 handed-off main merge | 6 | 2 | 0 | 48.5 | 362 | a seat merged main into the head and handed that off as a code head. `update_pr.sh:62` merged it, then `:64` merged main again. The own patch is unchanged, but `carry()` refused: "merges `<code head>`, which is not on main" |
| 2b context only | 4 | 1 | 1 | 54 | 241 | own patch equal at `-U0`, refused: context lines differ at `-U3` for #2547 (`INSTRUMENTS.md`), #2636 (`.mjs`) and #2753 (`.py`); #2609 is one own commit |
| 3 overlap | 13 | 4 | 1 | 51 | 912 | `CARRY: yes`, but main's move touched a file in the branch's own diff, so §11 sends it to the reviewer as a resolution delta |
| 4 registry | 23 | 4 | 1 | 11 | 737 | the own patch moved only in shared registries: `tests/features.py`, `closures.json`, `structure_budgets.json`, claim files, `mutation_ledger/`, roster JSON, seat-mutant harnesses |
| 5 substantive | 23 | 9 | 8 | 61 | 1585 | the own patch moved in production, tool or policy code. This is real rework |

Two notes on the blocked column:

- In buckets 1, 2 and 2b, re-review yield was **1 blocked in 16**. That one
  (#2753 at `45d08312`) was a body-figure defect, not a code defect.
- In bucket 3 it was 1 in 13 (#2753, a red nightly the body did not name). In
  bucket 5 it was 8 in 23.

A move limited to the PR's own `dev/programme/delivery/<N>.md` row occurs **zero**
times in the 75.

## 3. Cause

Five causes sit under the count. Each owns a bucket.

1. **Bucket 5, and most of bucket 4: the process working.** `fix-review.md` step
   12 owes a reviewer turn for a head that is not a carry. In 8 of bucket 5's 23
   entries, that turn found a defect.
2. **Bucket 2: `carry()` reads one hop of history.**
   - `tools/pr/app_approve.sh` refuses any merge whose second parent is not on
     main, before the own-diff comparison at line 317 runs.
   - K5 sanctions a seat's own main merge on a `DIRTY` head. For example,
     #2876's `179572ef` merged main at 01:25 +01, two hours after the v7.0.5
     stamp (`e8cb7e68`). Why that head was absorbed was not established here.
   - `update_pr.sh` then merges that head as the authored code head. The result
     is a merge of a merge whose own patch is byte-identical, and the carry
     cannot see through it.
   - The fixed carry turns 5 of bucket 2's 6 entries to `CARRY: yes`. The
     sixth, #2645, also differs in `INSTRUMENTS.md` context lines. It turns 3
     more entries in buckets 4 and 5 (#2368, #2745, #2819) to `yes`. There,
     the own patch moved only in files the carry already excludes:
     merge-driver files and the bot's ledger rows.
3. **Bucket 3: §11's file-disjointness clause.** `carry()` already proves two
   things: the own patch is byte-equal with context, and every merge is git's
   automatic result. §11 adds that the moved files must miss the branch's own
   diff. Most heads in this round touch the shared registries main also moves,
   so the clause sends 13 heads to review that `carry()` would carry. This is a
   deliberate conservatism, not a malfunction.
4. **Bucket 1: carry not run before dispatch.** `nudge.md` §2 says: "A head
   that moved since a merge verdict goes to `tools/pr/app_approve.sh --carry`
   first, and gets a reviewer only when the carry refuses." Six times, a
   reviewer was dispatched where it would have carried. Why the orchestrator chose a review was not established here.
5. **Breach verdicts after the split: moves outside the relay.** The freeze
   (#2792) holds the relay's handoff arm only. Both post-split breaches were
   pushed by the orchestrator account directly: one repair commit, one hand
   merge.

## 4. Process state

- **Bucket 2: (c).** The carry predicate existed and was run. On the merge of a
  handed-off main merge, it gave the wrong answer.
- **Bucket 3: no defect state.** The clause is obeyed and does what it says.
  Whether it should still apply once `carry()` proves byte-equality is the
  owner's question; see section 6.
- **Bucket 1: (b).** `nudge.md` §2 existed and was not followed. Six cases in
  14 days; 1 after the split.
- **Bucket 2b: (c).** This is the same shape R10-FLY-CARRY-DOC-CONTEXT (P17) is
  dispatched to carry. Its `.md` arm reaches #2547 here and #2645 in bucket 2,
  both before the split. The `.py` and `.mjs` context cases stay
  refused under its own rule ("code files strict").
- **Post-split breaches: (a) for non-roster heads.** No rule or freeze stops the
  orchestrator's own account from moving a head while a review of it is in
  flight. `fixer.md` lists the orchestrator among those who may move a head.
  The ROSTER-FREEZE carry names R10-ORCH-MACHINERY's beat as where that freeze
  generalises.
- **The recurrence of the issue: (c), unchanged from R9-RCA-1990.** The rework
  arm counts sanctioned re-verifications. Buckets 4 and 5 alone, at 46 of 75,
  cross the threshold of 3 on every active window. R9-RCA-1990's CM-3, which
  would stop proposing on the rework arm, is still the owner's decision.

## 5. Cost test

`cost(countermeasure, recurring) < cost(defect) × P(recurrence)`, in
wall-clock.

**CM-1, built: `carry()` carries a second parent off main when that parent
carries in its turn.** The change is one recursive call at
`tools/pr/app_approve.sh:239`. The own-diff comparison at line 317 still runs
over the whole head.

- **Standing cost.** It runs only on the path that refused before, and costs a
  few `git` calls.
  - `app_approve.sh --self-test`, 3 runs each, from `tools/pr/`: main took
    38.3, 37.7 and 37.1 s for 254 checks; the fix took 38.3, 37.5 and 37.1 s
    for 258 checks.
  - The difference is within noise. A copy run from outside `tools/pr/` cannot
    find `tests/throwaway_git.sh` and prints 25 failures, so time it in place.
- **Defect cost and measured frequency.**
  - 8 entries in 554 merges flip from `CARRY: no` to `CARRY: yes` (`hm6_out.tsv`).
  - None of the 8 was blocked by its re-review.
  - Under §11's whole predicate as written, only #2673 skips its reviewer turn
    outright (lag 48 min). The other 7 still fail the overlap or claim clause.
  - Even so, the train's carry step (`merge_train.py` step 3) and the reviewer
    now get the true carry answer rather than a refusal about history shape.
- **Verdict.** It passes: a standing cost of about 0 s against about 48 min of
  reviewer time per round. If section 6's owner question is answered yes, it
  reaches 7 more entries.

**CM-2, refused: the brief's narrow candidate, a carry predicate covering
autofix pin commits.**

- It is already in the tree: `bot_author` and `bot_paths` (`app_approve.sh`
  lines 203-219).
- 9 of the 10 entries whose delta held a bot commit carried at the time.
- The tenth (#2772) is an empty delta.
- Nothing is left for it to pay for.

**CM-3, owner's decision, not built: drop or narrow §11's file-disjointness
clause.**

- **Standing cost:** none at run time.
- **Defect cost:** 13 entries, 912 min of lag, and 1 blocked in 13. That one
  block was for a body omission the clause does not guard.
- **Why it is not built:** it changes `orchestrator.md` §11, which is policy,
  and it weakens what a head must satisfy to merge without a reviewer.

**Bucket 1, no countermeasure.**

- A dispatch gate that runs `--carry` first would cost about 2 s per dispatch.
- The defect is 291 min in 14 days, and 1 instance (52 min) after the split.
- It is state (b), and the rule is already in the orchestrator's turn. Its
  instances fall as K5 and the freeze reduce the heads that move.
- Recorded, not built.

**Post-split breaches, no countermeasure.**

- There are 2 moves in 87 merges, both by direct pushes from the orchestrator
  account.
- An `update_pr.sh` freeze would not reach either, because neither went through
  it.
- Generalising the freeze to every head is R10-ORCH-MACHINERY's beat handoff
  job, recorded on ROSTER-FREEZE's carry. Nothing is built here.

## 6. CM-1 as built, with its arms

- **Failing first.**
  - These self-test cases were added before the fix:
    - "a merge of a handed-off head that is itself a carried main merge
      (#2876's shape)", expecting 0;
    - "a merge of a handed-off head whose main merge changed a byte",
      expecting 1;
    - "a merge of a handed-off head whose own main merge was hand-resolved",
      expecting 1, refused as "not the automatic merge".
  - With the cases added and main's `carry()`: `app_approve self-test: 258
    checks, 2 failed`. The #2876
    shape got 1 and wanted 0. The hand-resolved reason was missing: got 0,
    wanted 1.
- **Fixed:** `258 checks, 0 failed`.
- **Mutant: the inner carry's answer ignored** (`e=$(carry ...; true)`). Result:
  `258 checks, 3 failed`.
  - The hand-resolved hop carries.
  - Its reason is missing.
  - The existing `NO CARRY: a merge of a branch that is not main` carries.

  The hand-resolved arm is the one the outer own-diff comparison cannot see, so
  the recursion is the only guard there.
- **Null control.**
  - Over all 75 historical pairs, the fixed carry changes no `yes` to `no`. It
    turns 8 `no` into `yes`, all of them shaped as a merge of a handed-off main
    merge.
  - For each of the 8, the own patch moved only in carry-excluded paths:
    - for #2368, a claim file;
    - for #2745, `structure_budgets.json`;
    - for #2819, `mutation_ledger` rows.
  - The other 48 refusals stand.
- **What it does not catch.** A merge of a handed-off head that holds a
  branch-own commit is still refused, by design: that is new content, and it
  owes a review.

## 7. The groups that list #2389, and what each still reaches

| group | state at `6d86acc9` | measured share of the residue |
|---|---|---|
| R10-FLOW-ROSTER-FREEZE | arm (a) merged (#2792). The close-out #2903 is open; its b2 change is the `carry_audit` roster read and the R1 kill, with no head-move arm | roster-PR breaches: 3 before (#2559, 2026-10-21), 0 after. Roster-only registry re-verifications: 6 before, 1 after (#2844) |
| R10-FLOW-BODY-ONLY | not started. `update_pr.sh:64` still merges `origin/main` on every call, including a body-only `-` | not separable from the train's recarry in git history: both write `Merge remote-tracking branch 'origin/main'`. Not measured here |
| R10-FLY-ROW-HEAD-CARRY | not started | verdict side: 0 of the 75 are row-only moves. Its CI-result carry is not measured here |
| R10-FLY-CARRY-DOC-CONTEXT | not started | 2 of the 75 (#2547, #2645), both before the split. It edits `carry()`'s final comparison, a different hunk from CM-1 |

## 8. Which of the two the count changes

**Neither.** The count is correct under its keying and over the window's
bodies. CM-1 lowers future bucket-2 entries. CM-3, like R9-RCA-1990's CM-3,
would change what the rework arm files, and both are the owner's call.
