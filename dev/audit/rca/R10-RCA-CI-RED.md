# R10-RCA-CI-RED: one verdict word, four mechanisms, and a 0.55 s detector that only runs inside a 120 s lease (#3156)

The root-cause record for the recurring-friction key `ci-red` (#3156), which
`R10-RCA-FRICTION-SWEEP.md` section 4b left to its own group. It ran apart from
any fix. It lands this record, its evidence and one reader script, and changes
neither the keying rule nor the gate. The countermeasures it names are owed to
later groups, section 6.

**Merge base and window.** Every figure was taken on 2026-11-07 at merge base
and `origin/main` `4b5d771bdf8feb1f83d7d9443e5117b771a0ab76` (re-taken there after
`main` moved from `b4ec2f332`; the 18 entries are identical, the window grew
from 91 to 93 merged PRs); tag `v7.1.2` is
the window's start.

## 1. The count, re-derived

`node tools/policy/policy_lint.mjs --stats --since v7.1.2 --window-cache W.json`
printed `STATS: 93 merged pull request(s) in v7.1.2..origin/main` and the row
`14 / 18     ci-red   <- at or over threshold`, with the would-open line at 14
(`ci-red/stats_v7.1.2.txt`). #3156 was filed at 11 PRs / 14 entries; the window
has since taken three more PRs and four more entries. The count is **not
refuted**: it reproduces, and it grows because the window does. A control: the
same reader asked for the key `ci-redd` returns `ENTRIES 0 PRS 0`.

`--stats` lists no PRs. `ci-red/entries.py` reads the window cache's raw
comments with the histogram's rule (first line matching the wave script's
`VERDICT_RE`, key = the class word after the head sha) and prints
`ENTRIES 18 PRS 14`, equal to the histogram's two numbers
(`ci-red/entries_v7.1.2.tsv`).

## 2. The 18 entries, by PR and by the check each named

| PR | head | what the reviewer named | min to next verdict |
|---|---|---|---|
| #3167 | 7637d6634 | `tests / replay`: `cycle_cost` cpu_ratio 2.615 over budget 2.173 | 3863 |
| #3167 | 4e4bb291b | gate cancelled (run 41924350700), `fast` and `coverage` unfinished | 71 |
| #3180 | 3f7777a59 | `harness_headers.py` depth root in the new `replay.py:40` (`fast`, `closures`) | 76 |
| #3181 | bb730c1ee | `codeql / Analyze (python)` cancelled, runner terminated the job | 187 |
| #3189 | fd9c5bab5 | `harness_headers.py` depth root `ROOT = HERE.parents[3]` at `replay.py:51` | 260 |
| #3195 | 6f742a33e | `tests / typing`, 9 `no-untyped-call`; body's Red checks does not name it | 355 |
| #3195 | c383169a5 | `prelude` wait expired, 8 surviving unpinned sites; Red checks does not name `prelude` | 250 |
| #3195 | 611e1aa6f | `tests / mutation` unpinned-site refusal; the bot pin commit cures it on a new head | 60 |
| #3204 | e5381d941 | gate cancelled, `classify` exits 1; reviewer: infrastructure cancellation | 64 |
| #3208 | 327d83e73 | `harness_headers.py`: harness inlines `repo_root` (`fast`) | 184 |
| #3211 | 1fca63cb1 | run cancelled because the PR was closed; it was reopened and merged | 1583 |
| #3217 | 1c42ca3fd | `codeql / Analyze (python)` cancelled | 124 |
| #3219 | aca500910 | gate cancelled, but `tests / mutation` had already failed on an unpinned site this diff added (job 127045678304, 04:18:12Z, before the 04:32:06Z verdict); stale SHAs in the body | 132 |
| #3227 | a52354e6e | `body_patch.sh:146` bare array expansion, `instrument-self-tests` and `fast`, unanswered | 139 |
| #3240 | 79cf40f47 | gate red by cross-run deferral (a run judged early, never re-run) | 80 |
| #3242 | e836876f3 | `harness_headers.py` hand-written depth root in `critpath_fetch.sh:12` (`fast`) | 328 |
| #3244 | a25821255 | three edit-run gates deferring to one another | 111 |
| #3244 | 8bc540e05 | CodeQL alert 50 `py/jinja2/autoescape-false` on the new harness, unanswered | 442 |

"Min to next verdict" is wall-clock from the blocked verdict to the PR's next
verdict (merge or blocked), an upper bound that includes the repair and the
re-review; two rows are mostly idle time (3863, 1583).

## 3. Cause: one word, four mechanisms

The key is the reviewer's free-text class word. `ci-red` is not in
`VERDICT_CLASSES` (`.claude/workflows/web-fix-wave.js`), so `parseVerdict`
routes it to `other` while the histogram keys it raw. It names a symptom (a
required check is red), so it pools causes with nothing in common:

- **A. Run cancelled or gate deferral, no check failed on the diff: 7 entries,
  7 PRs** (#3167 second, #3181, #3204, #3211, #3217, #3240, #3244 first).
  Three are a runner killing `codeql / Analyze` or a cancelled gate, one is a
  closed PR, two are the gate deferring to a sibling
  run that never re-ran.
  Two sibling keys spell the same thing, `ci-cancelled` (2 PRs) and
  `ci-red-cancelled` (1 PR), in the same histogram.
- **B. A new harness hand-writes its repo root: 4 entries, 4 PRs** (#3180,
  #3189, #3208, #3242), every one caught by `tests/harness_headers.py` in
  `fast`.
- **C. A real red the body did not name: 4 entries, 3 PRs** (#3195 twice, #3227,
  #3244 second). This is `defect-root-cause.md`'s second trigger verbatim.
  `web-fix-wave.js`'s reviewer prompt teaches `root-cause-detectable` or
  `-unrecorded` for exactly this, which dispatches the root-cause seat; the
  reviewers wrote `ci-red` instead, so no seat was dispatched.
- **D. A red the gate is the cheapest detector for: 3 entries, 3 PRs** (#3167
  first, a replay cpu budget; #3195 third, the unpinned site the pin bot
  cures; #3219, the same unpinned-site refusal). These do not qualify for a
  countermeasure.

  **#3219 is in D, not A (re-filed after review).** At its blocked head
  `aca500910`, read with `filter=all` over every page, `tests / mutation`
  concluded `failure` at 2026-11-05T04:18:12Z (job 127045678304; log line 6869:
  `MUTATION TABLE REFUSED -- 3175 unpinned site(s) against 3174 at the ratchet
  base, 1 of them added by this diff`), 14 minutes before the 04:32:06Z
  verdict. `tests / replay` also failed (04:38:35Z, job 127046649273), after the
  verdict. The verdict named only the cancelled gate, so the reviewer's own
  words filed it under A; the checks do not. Whether its body's Red checks
  named the mutation red is not established here, so it is not moved to C.

## 4. Process state, with evidence

- **B is state (c).** `harness_headers.inline_scan()` is the static scan that
  refuses a depth root; it is called from one place, inside `harness_headers.py`.
  `prepr.sh` defers the whole script to CI because it is
  exclusive-lease (`prepr.sh`, the comment above `dq_backticks`: "`stress.py`
  and `harness_headers.py`, which measure the machine"). The fixers followed
  `fixer.md` step 5 and `prepr.sh` was green; the process ran and did not
  produce the result. It is `defect-root-cause.md`'s worked example of a
  qualifying trigger (a check that exists, in no local path). Measured:
  `python3 -c "import sys; sys.path.insert(0,'tests'); import harness_headers
  as h; print(h.inline_scan())"` takes 0.55 s and prints `0`; the whole script
  takes 1m59s (`real 1m59.330s`). The sub-check is 0.46 % of the script (0.55 / 119.3).
- **A (7 entries) is state (d).** The process (gate, `merge_train.py classify`) is sound for
  a code red and its precondition, that a cancelled run is a defect of the head,
  does not hold when the runner or a closure cancels it. #3204's reviewer says
  so in the verdict ("an infrastructure cancellation, so the body owes no
  root-cause answer"). The two deferral entries (#3240, #3244 first) are a repo
  mechanism, not a runner one; their cause is **not established here**.
- **C is state (b).** The obligation exists (`fixer.md`, "answer any check your
  branch turned red"; the reviewers' verdicts cite the unnamed red as the block), and the body did not follow it. The keying drift is
  separate: the taught word existed and the reviewer did not use it.
- **D** needs no state: the cheapest detector is the check that went red.

## 5. Class reach, and the cost test

Search for the same shape (a cheap sub-check of a lease-exclusive script, in no
local path): `prepr.sh` names two lease-exclusive scripts, `stress.py` and
`harness_headers.py`. `stress.py` measures the machine end to end; whether it has a cheap
static sub-check is **not established here**.

Cost test, `cost(countermeasure, recurring) < cost(defect) x P(recurrence)`,
per PR, wall-clock:

| group | defect cost (mean min to next verdict) | P per merged PR (entries / 93) | expected cost per PR | standing cost per `prepr` |
|---|---|---|---|---|
| B | 212 min (848 over 4) | 4 / 93 = 0.043 | 9.1 min = 547 s | 0.55 s |
| A | 106 min without #3211 (637 over 6) | 7 / 93 = 0.075 | 8.0 min | no repo countermeasure |
| C | 297 min (1186 over 4) | 4 / 93 = 0.043 | 12.8 min | 0 s (a keying change) |

A's mean without #3211 is 637 over 6 = 106.2 (71 + 187 + 64 + 124 + 80 + 111).
Null control: with #3219 left in A the same arithmetic gives 769 over 7 = 109.9,
P = 8 / 93 = 0.086 and 9.5 min, so the A row moves when the entry moves and the
earlier figures were the misfiled ones. B and C do not move.

B: 0.55 s < 547 s, by a factor of about 1000, so the countermeasure pays even
if the defect cost is a tenth of the upper bound. Null control: the figure
`P` uses is one window; a window with no harness-adding PR gives `P = 0` and the
0.55 s is then pure standing cost, which is the case the call below limits.

## 6. Countermeasures, and what this record changes

This pull request changes **neither the keying rule nor the gate**.

1. **B, owed to a later group:** a `prepr.sh` step that runs
   `harness_headers.inline_scan()` when the diff adds or edits a file under
   `dev/audit/harnesses/` (the same trigger shape as step 6g), so the 0.55 s scan
   no longer waits on the 120 s lease. It is a check, so it owes the
   demonstration `defect-root-cause.md` requires: red on the #3189 `replay.py`
   at its blocked head, green on its fixed head. Not built here: this is a
   record group, and a `prepr.sh` change carries its own self-tests and review.
2. **C, owner's call (policy):** the reviewer vocabulary. The window shows
   `ci-red` carries four entries the taught `root-cause-*` words were written
   for, and `ci-cancelled` / `ci-red-cancelled` carry the cancellation group
   under two more spellings. Teaching a class `ci-cancelled` for group A (so it
   stops counting as friction of the PR) and routing group C to
   `root-cause-detectable` / `-unrecorded` changes what a seat must do, so it is
   policy and waits for the owner's approving review. Nothing here is landed.
3. **A, recorded refusal for the runner kills:** a codeql job terminated by the
   runner is outside this repository and no countermeasure in it removes it;
   a reviewer who reads it as infrastructure (as #3204's did) has the
   right call. The deferral race (#3240, #3244) is a separate finding, not
   established here, and goes to the orchestrator as a forward-carry.
4. **D, recorded refusal:** no cheaper detector than the check that went red.

## 7. Not established here

- The cause of the cross-run gate deferral (#3240, #3244).
- Whether `stress.py` has a cheap sub-check in the same position.
- Whether a would-be teaching of the cancellation class lowers the histogram:
  the counts above are this window's.
