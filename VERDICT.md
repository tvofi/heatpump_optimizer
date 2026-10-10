Fix review: merge dcf0340d29617a70377f29a912d39ca312d5e5de

bus-nonce: e16feb4c527913888643bef5d6ffec67

# #2075 R9-RC-Carry-Pins — re-publication of the round-5 review at the new head

This is the round-5 verdict re-published, append-only, at the head the branch
moved to after `addd6f457`. The reviewed code is byte-for-byte the code the
round-5 review measured; only the head, the delivery row and main's merged files
changed. Nothing below weakens the round-5 findings — the re-publication section
records why the move is inert for the review.

- Round-5 head (measured): addd6f45758ff90ab862bcbe62357c1373ed7786
- Re-published head:        dcf0340d29617a70377f29a912d39ca312d5e5de
- Live head confirmed via `gh pr view 2075 --repo tvofi/heatpump_optimizer --json
  headRefOid` immediately before publishing: dcf0340d29617a70377f29a912d39ca312d5e5de (OPEN, MERGEABLE, APPROVED).

## Why `addd6f457 -> dcf0340d2` does not carry, and why a fresh verdict is right

The merge train stopped with `9d62d06658dd3962d1a0e21055ba56cfb5949bea is a
commit of the branch's own (record(#2075): the pull request's own delivery row,
per delivery-status-tracking)`. `app_approve.sh --carry` accepts only two-parent
merges of main and `ci:` commits, so the branch's own `record(#2075)` delivery-row
commit in the window blocks the carry. That is the instrument-level deadlock a
sibling session owns; the correct move here is a fresh verdict at the new head,
which is what this is. I did not treat the carry refusal as a defect in the change.

## Verified before publishing (measured at dcf0340d2)

- `git diff --name-only addd6f457 dcf0340d2`: 15 names. Exactly ONE is the
  branch's own — `dev/programme/delivery/2075.md`, and it is the whole delta of
  the branch's only commit in the window (`9d62d0665`), verified by
  `git diff --name-only addd6f457 9d62d0665`. Every other name is byte-for-byte
  origin/main's copy at `1301d7e45` (checked file by file: `CLAUDE.md`,
  `dev/governance/roles/fixer.md`, `dev/programme/carries/carry-1922.json`,
  `dev/programme/delivery/2072.md`, the nine `tests/mutation_ledger/killed_by/**`
  rows, and `tools/pr/prepr.sh`). None of them is reviewed by this PR.
- The merge `dcf0340d2` IS git's own automatic merge: `git merge-tree --write-tree
  --no-messages <p1> <p2>` reproduces its tree exactly (parents `9d62d0665` and
  `1301d7e4`).
- THE REVIEWED FILES ARE UNCHANGED. `tools/pr/app_approve.sh` at `dcf0340d2` is
  blob `8a71178f21bd9ff4a5979d12f013e280faf08510`, byte-identical to the copy the
  round-5 review measured; `dev/programme/carries/carry-2075.json` is blob
  `56bbd9ba8c29fca5a4d14e575dbfc99bc7699ab0`, byte-identical. No reviewed file
  moved by even one byte, so every round-5 measurement transfers:
  `app_approve.sh --self-test` at `dcf0340d2` = 166 checks, 0 failed (measured).
- `git merge-tree --write-tree origin/main dcf0340d29617a70377f29a912d39ca312d5e5de`
  -> rc 0 (no conflict).
- Hygiene at `dcf0340d2`: both claim files byte-identical to live main; no
  `*_budgets.json` leaf moved; VERSION / manifest / RELEASE_NOTES untouched vs main.
- Step 11, check-runs at `dcf0340d2`: 42 runs, NONE pending, no non-success
  conclusions; all 17 required contexts of ruleset 23698884 COMPLETED success;
  ABSENT required contexts: NONE (the tip commit is authored by `tvofi`, so
  `pull_request` runs exist). Confirmed, not assumed. `gh pr checks` NOT used.

## Round-5 findings, unchanged (see the round-5 evidence in this directory)

1. The round-4 seam is closed — reproduced. Removing the single
   `git cat-file -e "$v:$p" 2>/dev/null && continue` line reddens EXACTLY its two
   DELREADD checks and nothing else in the 166; restored (byte-identical) -> 166/0.
   My own fixture (bot delete-then-readd of a reviewed row) refuses at the head and
   carries against a no-guard copy of the same mechanism.
2. Both directions hold under my own fixtures: a path held at `$v` refuses (reviewed
   content rewritten/deleted/delete+readd, AND main's own row delete+readd), a path
   new at `$v` carries (positive control). The guard is load-bearing for both.
3. Failing-test-first reproduced: main's mechanism + the branch's test hunks ->
   166 checks, 10 failed (five fixtures x two).
4. Four body dispositions checked, not accepted: (a) the moving `81` dropped
   (merge_train is 95 now); (b) #2065's control re-quoted to "90b9e87f... is not the
   automatic merge of its parents", measured at both the head copy and main's;
   (c) the BUDGET residual recorded in carry-2075.json and measured as a live CARRY
   at head AND at main's own copy, brief_lint clean, `claims-for: 6.7.17` == VERSION;
   (d) 166 / 169+4 / `GUARD: 0 refusal(s) against 7cd5a588cbbb` / structure PASSED /
   `MODE: SCOPED -- 0 script(s) run` all reproduced.
5. #2010's stale REFUSE is main's advance, not the fixer's: both its heads are
   ancestors of live main and both copies now carry.

## What was cited rather than measured

- The mutation drive, features.py, optimality.py, golden.py and the heavy lanes:
  cited from check-runs (all success), NOT run here.
- CI `instrument-self-tests` `app_approve self-test: 168 checks, 0 failed`: cited
  from the job log (this is the DERIVED 168 the body names, honestly labelled
  "derived, not measured"); my own macOS `--self-test` at the head is measured 166/0.

VERDICT: merge dcf0340d29617a70377f29a912d39ca312d5e5de
