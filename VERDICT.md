Fix review: merge 99edcf9f59cefa159594d18b8bbb5dbf8ae3eb95

bus-nonce: ea29f5498642e3e3f5685e95e776a28c

Re-published at the record-commit move from `c32e90ddd730ae1a2fc85a44a52cdbe159fff08f` (my first verdict) to
**`99edcf9f59cefa159594d18b8bbb5dbf8ae3eb95`**, the PR's live `headRefOid` at the time of writing. Detached worktree at
`c32e90ddd`, merge base `origin/main` = `7cd5a588c`. Evidence: `/Users/timmalmstrom/hpo-seats/r9-review-2083/evidence-99edcf9f/`.

## The move — judged as the delta, not re-opened

`git diff --name-only c32e90ddd… 99edcf9f…` → **`dev/programme/delivery/2083.md` alone** (`+1`); one single-parent commit,
`record(#2083): the pull request's own delivery row, per delivery-status-tracking`. The row is the shape
`delivery-status-tracking.md` prescribes (`- [#N](…/pull/N)` and its state, written by the orchestrator) and matches
`open_row_line()`. **The three reviewed files are byte-identical at both heads and against the reviewed worktree** —
`INSTRUMENTS.md` `1276f4944a58…`, `ci-watch.sh` `3f9a224fecf8…`, `merge_train.py` `c1c728215ac6…`, all SAME on all three
sides, `git diff` over them empty (`delta.txt`). Nothing I measured is invalidated; the mutation proof, the two-ends null
control and bash sha1s reproduce on these bytes, since they are these bytes.

## Head state of the new head (API, not `gh pr checks`)

- 37 distinct check-run names; **all 17 required contexts of ruleset `23698884` PRESENT**, none absent, none red.
- Two runs were still `in_progress` at this reading: `coverage` and `Analyze (python)` (**`Analyze (python)` is a required
  context**), with the `Tests` and `CodeQL` workflow runs in progress; **this head is not yet settled**. Nothing here
  turns on it — the head's own CI is what the train's `wait_ci` waits for before it merges at exactly this sha — but I
  will not report a settled head that is not one.
- `git merge-tree --write-tree origin/main HEAD` → clean; `VERSION` 6.7.17 both ends; claim files byte-identical to main.

## Carried forward from the first review (unchanged; re-derivable from these bytes)

- **Mutation proof.** ci-watch MW1/MW2/MW3 → exactly the named W1/W3/W4, `8 checks, 1 failed` each; merge_train M1/M2/M3 →
  the named checks, M3 both and only those two, `2 failed`; restored 98/0 and 8/0. Baseline at `origin/main`: **95**.
- **Two-ends null control, re-run by me** on the real input (`checkruns-63084989.tsv`, sha1 `7656ef0d4f42cb7490de31a3c9410ad04e89a725`):
  arm A — v2 prints only `RED: mutation nightly-ha (stable)`, v3 adds the five `ABSENT`; arm B (all forced `success`) — v2
  prints nothing and is still looping at a 6 s bound, v3 exits 1 naming the five.
- **Figures re-derived:** 17 contexts; both bot heads (4 dispatch runs, 0 `pull_request`, 30 names, same 5 absent) and
  recovery `386b7e2f` (9 `pull_request`, 39 names, none absent); 8 h 52 m; 26 pin commits; `STRUCTURE RATCHET PASSED`;
  `MODE: SCOPED -- 0 script(s) run, 33 scoped out`; `0 refused`; `FIELD COVERAGE ok`; `workflow_dispatch` at
  `governance.yml:44`; both Fig-15 sha1s. `PRESENT12` = `required ∩ names@63084989`.

## Reported, not blocking (unchanged)

1. Premise-table row `386b7e2f…`, column *latest-per-name not green*, reads `—`; it is `mutation`. That one cell only.
2. The two-ends companion driver lived only in scratch (`fixer.md` 18), disclosed by the body; I rebuilt the run so
   nothing rests on it.
3. Forward-carry: item 1 is in the tree at its destination (R9-CI-1's roster brief, `6a2ab7968`) with its control and its
   precondition; items 2–4 are routed to the orchestrator/owner and are written nowhere — they must be picked up at merge
   or they evaporate with the body.

## Not measured

`tests/env_drift.py --all` (heavy) — derived from the three-file diff plus byte-identical claim files and `VERSION`.
`prepr.sh` (Fig 9) not re-run; `pr-contract` green evidences its contract half.
