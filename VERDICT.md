Fix review: merge 390e238754a08b29e82b2004f061e086a75b5a1b
bus-nonce: 67df5c54d141936a3ba9ecbdbe3be850

Head reviewed: `390e238754a08b29e82b2004f061e086a75b5a1b` (re-read at `git ls-remote origin refs/pull/2877/head` and `refs/heads/fix/triage-s6-batch36`, and at the API, immediately before writing: unchanged at all three).
Merge base: `67178dc6a589cf95d2ce7cff36d8bbf17343e8dc` (`git merge-base origin/main HEAD`; origin/main is now `2b45d098c`, a descendant).
Worktree: `~/hpo-seats/r10s6/review-2877-r5/wt-390e238`, detached at the head.
Evidence: `~/hpo-seats/r10s6/review-2877-r5/ev/` (files `01`–`05`, plus the body file; no file carries a host path).
Round: 5, the name this dispatch carries (`reviewer-2877-r5`). `verdict/2877` holds three blocked verdicts, the last `dd9e5dda9` at `b95d3fa`, and this dispatch passed `--past-three` with the reason logged at `~/.zcode/bus/past-three`; the re-cut was the orchestrator's call, not the fixer's omission.

## Verdict

merge. The repair changes one record file (`+32/−23`), and the head adds only the merge of that repair (the diff against its second parent is empty); F1, F2, F3 and F6's record claims re-derive exactly, and the body's `## Head` names the head measured and its commits line is exact. One body claim is stale and carried below as non-blocking.

## F1 — repaired, and its command re-derives

The annotation claim is now scoped to the window's `HOLD` lines. Re-running the record's command in the orchestrator state directory (`grep 'triage s7:' seat-ledger.md | sed -n '/08:13:15Z/,/09:38:27Z/p'`) prints 31 lines; appending `| grep -c '; main '` prints 10 and `| grep -c 'HOLD (no v7.0.5 tag)$'` prints 18, exactly as the record says. `ledger:1171` is `20:56:28Z` and `ledger:1330` is `08:12:52Z`; the plain series' largest gap is 302 s, under the stated 7 minutes. My own mutation: with one annotation removed inside the window the counts move to 9 and 19; the null control on the unmodified copy prints 31/10/18. `ev/02`.

## F2 — repaired by deletion; its conclusion rests on the re-runnable grep

`grep -rn 'HOLD (no v7' tools/audit/seat/` prints nothing, and a whole-tree `git grep` hits only this record's own quoted literals. `s7/roster-loop.sh` writes `roster s7:` lines and no `triage`/`HOLD` line; `w71/loop.pid` names 76559 and that process does not exist. No count replaced the deleted one, and "its source is unidentified" does not rest on the count's absence. `ev/03`.

## F3 — repaired

The record uses "the other writer" (four times) and no "second writer"; the arrival-order paragraph still says the order is unresolved and gives the plain cadence's `20:56:28Z` start. The body has no "second writer".

## F4 — repaired

`## Head` names `390e23875` and calls `35a165fc0` "the authored code head, not the PR head". `390e23875`'s parents are `b95d3fa` and `f6cb1a468`, and `b95d3fa` is the origin/main merge.

## F5 — the commits line is exact

`git log --oneline 524c1896b..HEAD -- dev/programme/triage/s6-batch36.md` prints exactly those five commits; lengths and stats re-derive as 78 (`+78/−0`), 85 (`+12/−5`), 89 (`+12/−8`), 89 (`+3/−3`) and 98 (`+32/−23`). `ev/04`.

## F6 — repaired

`grep -c 'older id\|DUPLICATE' tools/audit/seat/sweep_template.md` prints `0`; the record now says the P97(b) carry amends step (1b), and the roster's index 21 carry does say step (1b) "then stops the older id before anything else, and logs both ids". `ev/03`.

## Finding (non-blocking)

- The body's `## Red checks` reports `b95d3fa`'s rollup, not the head's: at `b95d3fa` the 55 runs completed by 16:53Z are 37 success, 17 skipped, 1 cancelled, 0 failed (re-derived by filtering `completed_at`), while at `390e23875` the 36 runs are 24 success, 10 skipped, 2 in progress, 0 failed, and `gate`/`pr-contract` have not started; the body promises the post-push rollup but does not state it. In the same section of `## Head`, the parenthetical reads as if `390e23875` merged `67178dc6a`, where `b95d3fa` is the commit that did. The substantive answer ("none" red) holds at the head, the section names its SHA and time, and the fixer was forbidden to push, so the post-push rollup was the push lane's to take.
  Carry: dismissed: body metadata, not a record claim; the head's checks are green, the section names its SHA and time, and the ruling is unaffected.

## What I tried to break and could not

- **The ruling and its cost.** DEFER, the two rejected arms and the surviving launch record re-read sound; `R10-ORCH-BEATD` is `not-started`, L, 34 carries; P97(b) is index 21 (carry 22) and P197 sits at carry 13 (index 12, the context-rotation paragraph); the roster holds no `P197` string. `ev/04`.
- **The gate.** `roster_edit`'s `ruling_verdict`/`triage_refusal`: committed `DEFER` gives "... is not an ACCEPT ruling (DEFER)"; mutant `ACCEPT` gives `None`; absent file gives "not on the roster branch or origin/main"; `P999` gives "(no such entry)". `ev/05`.
- **The merge and the scope.** PR scope is two files (`dev/programme/triage/s6-batch36.md`, `dev/programme/delivery/2877.md`); `git merge-tree --write-tree origin/main HEAD` exits 0 at current origin/main; `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched by the PR; `tests/structure.py` prints `STRUCTURE RATCHET PASSED`. `ev/01`.
- **The origin/main interaction and the row.** The only newer records are `s6-batch38.md` (P206/V126, the push-lane item; 0 hits for P204/duplicate/P97/BEATD) and `delivery/2881.md`; `s6-batch39.md` is absent; the roster is unchanged between `67178dc6a` and current origin/main; `dev/programme/delivery/2877.md` is present and says "**open**", accurate while the PR is open. `ev/04`.

## Could not establish

- The head's `gate` and `pr-contract` runs had not started, so there is no CI body-check at this head; `tests / coverage` and `governance / instrument-self-tests` were in progress (0 failed). My local `prepr.sh --body-check` at the head prints pr-body ok, carry ok (0 unrouted) and preflight ok, and `ci_predict.py` predicts no red. `ev/05`.
- The board's 660 s to 1800 s figures (22 beat gaps, median 57 s, max 1235 s) are the orchestrator's measurement, cited as such in the body; I did not re-derive them.

## RESULT lines

RESULT F1 pass: 31/10/18 exact; anchors 1171/1330 and 302 s max gap exact; my mutant 9/19 against a 31/10/18 null.
RESULT F2 pass: the two-process count is gone; `grep -rn 'HOLD (no v7' tools/audit/seat/` prints nothing.
RESULT F3 pass: "the second writer" appears in neither the record nor the body.
RESULT F4 pass: `## Head` names 390e23875 and calls 35a165fc0 the authored code head, not the PR head.
RESULT F5 pass: the commits line re-derives exactly — five commits, 78/85/89/89/98 lines, +78/−0, +12/−5, +12/−8, +3/−3, +32/−23.
RESULT F6 pass: `grep -c 'older id\|DUPLICATE'` prints 0; the P97(b) carry owns step (1b)'s future edit.
RESULT pass: one-file repair +32/−23, merge adds nothing beyond it, two-file PR, merge-tree 0, versions/claims untouched, structure PASSED.
RESULT pass: origin/main's batch38 and the unchanged roster do not interact; delivery/2877.md present and accurate.
RESULT finding (non-blocking): body `## Red checks` reports b95d3fa's 55 at 16:53Z, not the head's 36 (24 success/10 skipped/2 in progress/0 failed); carried as dismissed.
RESULT merge
