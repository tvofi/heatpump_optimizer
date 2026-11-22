# Review packet #3843
head: e7dec855cbf1688c5c0ef97b9e53740f5e3fc0e8
base: e4c929bd1c96e8a23636d1f1f086c38de1852853

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=137054600734 success
arch-score / arch-score id=137061857194 success
arm id=137048146602 skipped
budget-raise-gate / budget-raise-gate id=137061857232 success
cancel-superseded id=137050892803 success
codeql id=137061858540 skipped
codeql / Analyze (actions) id=137051890969 success
codeql / Analyze (javascript-typescript) id=137051891059 success
codeql / Analyze (python) id=137051890992 success
gate id=137068298965 failure
governance id=137061858580 skipped
governance / env-matrix id=137051890974 success
governance / instrument-self-tests id=137051891015 success
governance / policy-docs id=137051890956 success
governance / record id=137051891845 skipped
governance / wave-script id=137051890941 success
hassfest id=137061858851 skipped
hassfest / hassfest id=137051891020 success
kernel-points id=137061858131 skipped
pr-contract id=137068300275 skipped
prelude id=137050892719 success
refresh id=137050892535 success
sweep-self id=137073729017 skipped
tests id=137061858637 skipped
tests / arch-instrument id=137061506546 success
tests / briefs id=137051891077 success
tests / browser id=137061506580 success
tests / ci-ratchet id=137077481544 skipped
tests / claims-autofix id=137069939491 skipped
tests / closure-scope id=137051891049 success
tests / closures id=137061506522 success
tests / closures-autofix id=137069585561 skipped
tests / coverage id=137061506521 success
tests / coverage-ratchet id=137077480183 queued
tests / fast (3.14) id=137061506545 success
tests / graders-head-copy id=137077480157 queued
tests / lane-proofs id=137077480176 queued
tests / mutation id=137051891002 success
tests / mutation-autofix id=137054458122 skipped
tests / mutation-pins id=137054458142 skipped
tests / nightly-ha id=137061507989 skipped
tests / nightly-status id=137051891010 success
tests / replay id=137061507366 skipped
tests / typing id=137061506563 success
validate id=137061858440 skipped
validate / validate-hacs id=137051890991 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at e7dec855cbf1688c5c0ef97b9e53740f5e3fc0e8 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item 2252fa00: R11-CLOSEOUT-CLEANUP
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/audit/rca/R11-RCA-MODEX.md b/dev/audit/rca/R11-RCA-MODEX.md
new file mode 100644
index 0000000000..7a52adfbe7
--- /dev/null
+++ b/dev/audit/rca/R11-RCA-MODEX.md
@@ -0,0 +1,211 @@
+# R11-RCA-MODEX: a PR-local ratchet row is judged by an absolute record while main moves its measure
+
+Root-cause seat (`dev/governance/roles/root-cause.md`, `dev/governance/rules/defect-root-cause.md`)
+beside #3735 (R11-SEAM-ratchet-raise, handoff `handoff/r11-seam-ratchet-raise` at `611f843468`),
+never inside it. This document lands no code. The tooling freeze holds, so the countermeasure
+is a local overlay prototype plus proposal P-R11-99 for round-end triage. Measured on
+2026-11-22 against `origin/main` `4ebd430fbf` (sections 1 to 4) and `e4c929bd1c` (run C).
+
+Trigger: the red-check trigger. `tests / fast (3.14)` and `governance / instrument-self-tests`
+went red on the merge-of-main heads of #3735, and `tests/structure.py` detects the same breach
+locally in 84 s. This is the class's third reported instance (#3736 +61, #3616 +24, #3737 with
+#3728 +61), so it is an audit class that owes a class-eliminating barrier.
+
+## 1. The defect, reproduced
+
+`045f358a4f` (2026-11-18) adds the row `module_excess_loc` to `tests/structure_budgets.json`:
+each module's span past `MODULE_LOC_LIMIT` (2000 lines), summed. Main's table does not carry
+the row (`git show origin/main:tests/structure_budgets.json | grep -c module_excess_loc` prints 0),
+so nothing bounds the measure on main.
+
+At `d4bd8ed29e` (`ci: merge main`, the bot's merge of `4ebd430fbf` into #3735), in an export
+of that tree, `python3 tests/structure.py` prints
+`FAIL module_excess_loc 21779 > 21718 (+61)` and `1 STRUCTURE BUDGET(S) BREACHED`. The tree's
+`recorded_at` is `e698fc8ac3`.
+
+**Which side moved.** The fixer's AST counter `modex.py` (the #3735 seat's local scratch, not in the tree)
+(same rule: last top-level node's `end_lineno` past 2000, per module) reads:
+
+| revision | what it is | module_excess_loc |
+|---|---|---|
+| `ae0ed64af8` | main where the row was first recorded | 21549 |
+| `e698fc8ac3` | main at the `recorded_at` of `d4bd8ed29e` | 21718 |
+| `35402f7817` | main after #3737 | 21816 |
+| `4ebd430fbf` | main after #3728 | 21779 |
+| `d4bd8ed29e` | the PR head after the merge | 21779 |
+| `611f843468` | the PR head after its re-record | 21779 |
+
+The PR head equals main at every point: no line of #3735 moves the measure. Main moved it by
++230 between `ae0ed64af8` and `4ebd430fbf`.
+
+**The class's instances on #3735.** `git log -G module_excess_loc -- tests/structure_budgets.json`
+over the branch lists the introducing commit and seven re-records. Each follows a merge of main:
+
+| merge of main | re-record | move | red window |
+|---|---|---|---|
+| `382df86816` bot, 11-19T05:51Z | `0dfa61d887` 08:31Z | 21549 -> 21536 (a gain: exit 2) | 2.67 h |
+| `011a463926` bot, 09:50Z | `ef7d2e4038` 10:30Z | -> 21571 (+35) | 0.66 h |
+| `f50a75b4f7` bot, 13:26Z | `0800f342ef` 14:43Z | -> 21633 (+62) | 1.28 h |
+| `430bc6bfad` bot, 11-20T20:08Z | `b278df39d6` 20:48Z (#3736) | -> 21694 (+61) | 0.67 h |
+| `161fc37b8f` seat, 11-21T15:28Z, and `3e1e9141e4` seat, 17:11Z | `bd58b7341e` and `21428d8202` | -> 21718 (+24, #3616 phase 3a / #3711) | about 0 h |
+| `5e4a4a6a24` bot 21:10Z, `d4bd8ed29e` bot 22:39Z | `611f843468` 23:03Z (#3737, #3728) | -> 21779 (+61) | 1.88 h |
+
+The fifth row is two seats on two branches recording the same main move 1.7 h apart. The
+red window runs from the merge commit to the re-record commit; it leaves out the repair head's
+own CI.
+
+## 2. The cause
+
+**Mechanism.** `tests/structure.py`'s `ratchet()` compares each measured value with the
+table's absolute value: `if current > budget: FAIL`, and an unrecorded gain exits 2. A merge of
+main carries main's movement of the measure into the PR, under a value recorded at an older main.
+
+**Why a PR-local row is recorded against a moving main.** The ratchet tables store absolute
+whole-tree measures, and almost all of each measure is code the PR does not own. An absolute
+comparison judges the PR's own delta only while main sits at its own record. For every row main
+carries, that holds: main's own `tests / fast` refuses growth past the record and refuses an
+unrecorded gain (exit 2), so main's measure equals its record and a merge of main cannot move
+the row. For a row main does not carry, nothing holds main still. The ratchet has no notion of
+the PR's own delta, and no branch-side measurement of the merge base exists to give it one.
+
+**Why it is not re-measured at merge.** By design: the ratchet's own text says a budget is
+re-recorded "deliberately, on a clean tree, with the reason in the COMMIT -- never to make a
+failure go away". So no bot may re-record it. `tools/pr/merge_main_bot.py` resolves driver
+conflicts and pushes; the other bots "run as they would after a seat's merge", and none of
+them re-records a ratchet. So each instance costs a seat-authored `--record
+--allow-regression` commit, which moves the head again.
+
+**The process-wide class.** This is a branch carrying an absolute snapshot of a quantity main
+owns. The repository has met that shape before, and each time built a barrier for one file:
+`tests/closures.json` and the ledgers (merge drivers plus the `UNDER-SCOPED` autofix), the
+claim files (the `claimnotes` driver), the self-test read-set table
+(`R11-RCA-SELFTEST-TABLE-DRIFT.md`), and the line-anchored mutation pins (the bot's pin-chain
+deferral). The ratchet tables have no barrier for rows main does not carry. A barrier for one
+file leaves the class open wherever a new committed snapshot of main-owned state appears.
+
+## 3. Process state: (d), the process was sound and its preconditions changed underneath it
+
+The process: the structural ratchet (`CLAUDE.md` rule 2; `tests/structure.py` `ratchet()`)
+with deliberate re-records. Its precondition, unstated in the tree: every row in a branch's
+table is a row main enforces, so main's measure sits at its record. #3735 introduced a row main
+does not carry, and the row stayed PR-local for four days. #3735 is a budget raise
+(`const_modules_over_50` 3 -> 4), so it merges only on an approving owner review at its head,
+and no approving review has landed at any head since 2026-11-19T12:31Z (`8f34cd23e0`). Each
+merge of main then breached the row.
+
+- Not (a): a process existed and handled every instance (the re-record with
+  `--allow-regression`, per the owner's 2026-11-18 ruling for this row).
+- Not (b): it was followed every time. Seven re-records each carry the measured move, its
+  source PR and the reason.
+- Not (c): each re-record produced its intended result, a green ratchet at that head. The
+  result went stale only because main moved.
+
+The countermeasure for (d) is to make the process notice the changed precondition: detect a
+row the merge base's table does not carry, and judge that row by the PR's own delta.
+
+## 4. How far the class reaches
+
+- **Open PRs, 2026-11-22.** Over all 19 open PRs and all nine `*_budgets.json` tables, rows at
+  the head that are absent on `origin/main`: #3735 `module_excess_loc`, and #3729
+  `in_function_copies` and `unloaded_package_imports` in `tests/structure_budgets.json`.
+  #3729's two rows were not moved by main in the same four days (run D below).
+- **Rows tightened below main** (11 rows on #3738, #3805, #3812, #3835, #3838) are not exposed.
+  Main sits at its record for those rows, so a merge of main cannot raise them past it. The
+  one way it can is main's own re-record upward, which is a raise and is gated separately.
+- **History.** Since 2026-10-01, 14 merges into main introduced new keys across six budget
+  tables, among them `tests/structure_budgets.json` #1838, #2340 and #2415, and `ci_budgets.json`
+  #2132, #2320, #2401, #3045 and #3169. Their branch commits touching those keys were not
+  classified per instance here: a `-G` key count also matches table rewrites, so it is only an
+  upper bound. Whether the other tables' checkers compare absolutely the same way was not
+  measured. Both questions are carried to P-R11-99.
+- **Main-side effect.** While the row is PR-local, main's growth of the measure is unpriced:
+  +230 lines past the limit in four days. Only landing the row stops that. No overlay can.
+
+## 5. The cost test, with numbers
+
+`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, per 10 days.
+
+**cost(defect), per occurrence, measured on #3735:**
+- PR-hours red: 7.18 h over six occurrences, a mean of 1.2 h (section 1).
+- CI: 12 `CI code` runs on the merge heads `382df86816`, `011a463926`, `f50a75b4f7`,
+  `430bc6bfad`, `5e4a4a6a24` and `d4bd8ed29e` (a `pull_request` and a `workflow_dispatch` run
+  each) failed `tests / fast (3.14)` and/or `governance / instrument-self-tests`. The repair
+  heads `8f34cd23e0`, `de84aa9bf9` and `20edc8b3cd` failed neither, only `budget-raise-gate`
+  and `gate`. Job time summed per run, over the 8 runs whose job times read: 1696 runner-minutes,
+  a mean of 212. The other 4 runs are re-runs whose timestamps give negative sums. That is about
+  2 runs and 7.1 runner-hours per occurrence whose verdict could not be used, plus the repair
+  head's own CI cycle.
+- Seat work: 7 re-record commits, one of them a duplicate. Each was measured by hand
+  (`modex.py`), and one carried an archscore-priced payment attempt (`21428d8202`:
+  `dS -1.5850 WORSENS`). The seat-hours were not measured.
+
+**P(recurrence):** measured as 6 occurrences in the 10 days 2026-11-13..2026-11-22, all on one
+PR-local row that reads the repository's largest modules. #3729's two PR-local rows had 0
+occurrences in 4 days. As the class's third reported instance in round 11, it owes a barrier
+whatever the rate; the test chooses the barrier's form.
+
+**cost(countermeasure, recurring), the proposed form** (`ratchet()` judges a PR-local row
+by delta):
+- A PR with no PR-local row: one `git show` of the merge base's table and a key-set difference.
+  No measurement, so under a second.
+- A PR with a PR-local row: at most two extra `measure()` runs per new merge base, 84 s each
+  measured here. The `recorded_at` one is cached per (tool blob, tree). In CI with no cache,
+  that is up to 168 s on each `tests / fast` run of such a PR. #3735 had 18 `CI code` runs:
+  about 50 runner-minutes.
+- Induced work: the loop ledger's offspring rate was not read for this record, so the term is
+  unpriced. Triage prices it. A change to `tests/structure.py` re-derives its closure entry.
+
+Per 10 days: about 7.2 PR-hours and about 42 runner-hours of defect, against about 0.8
+runner-hours and no PR-hours of countermeasure. **The test passes**, by more than 40x on
+runner time.
+
+## 6. Countermeasure
+
+It addresses state (d). Rungs in order:
+
+1. **Delete** (shorten the window): land a new ratchet row in its own pull request, ahead of
+   any raise. A new key is not a raise (`budget_raise_gate`'s `raises_between` reads no raise
+   for it, as the fixer's commits `b278df39d6` to `611f843468` record), so it needs no owner review at head. It is not sufficient alone, for two reasons.
+   A PR's time open is outside its fixer's control: #3735 has waited since 2026-11-19T12:31Z.
+   And the window between opening and merging stays exposed, at 1.5 occurrences per day on
+   this row. It is still owed as a brief line because it is the only rung that stops main's
+   unpriced growth (section 4). That line is a brief or plan change, so it is proposed and not
+   landed here.
+2. **Self-repair** (the barrier): `ratchet()` detects each row absent from the merge base's
+   table, measures the merge base's tree and the `recorded_at` tree with the head's tool, and
+   passes the row when `own_delta = head - base` is at most `allowed = recorded - at_recorded`.
+   A gain on such a row owes nothing. Every row main carries keeps its absolute check. An
+   unmeasurable base fails the row. No table is written and the head does not move. A bot
+   re-record was the alternative self-repair and is refused: it writes a budget table and
+   moves the head, and it is the "re-record to make a failure go away" that the ratchet
+   forbids.
+3. No narrowing and no new refusal are needed. The repair keeps the existing refusal and
+   corrects what it measures.
+
+**Prototype** (local overlay, tooling freeze):
+`proto/RCA-MODEX/local_rows.py` in the round-11 orchestrator's local overlay directory, demonstrated by `demo.sh`
+beside it (output `demo.txt`). Under the freeze it cannot turn CI green. In-round it replaces
+the hand measurement: it proves mechanically that the PR's own delta is zero, and gives the
+re-record value, so two seats need not measure the same move.
+
+Runs (from `demo.txt`):
+
+| run | tree | absolute `structure.py` | overlay |
+|---|---|---|---|
+| A, the defect | `d4bd8ed29e` | exit 1, `FAIL module_excess_loc 21779 > 21718` | `own_delta=+0 allowed=+0`, PASSED, rc 0 |
+| B, mutation: the PR's own growth | `d4bd8ed29e` plus 10 module-level lines at the end of `optimizer.py` | exit 1 | `module_excess_loc own_delta=+10 allowed=+0` FAIL; `dead_top_level_symbols` (not PR-local) keeps its absolute FAIL; rc 1 |
+| C, null: no PR-local row | `origin/main` `e4c929bd1c` | exit 0 | `local=none`, PASSED, rc 0 |
+| D, null: PR-local rows main did not move | #3729's head, base `35402f7817` | exit 0 | `in_function_copies` and `unloaded_package_imports` `own_delta=+0`, PASSED, rc 0 |
+| E, null: base unmeasurable | `d4bd8ed29e` with `recorded_at` set to an absent SHA | exit 1 | `LOCAL-ROWS ERROR`, rc 1: never green by skipping |
+| F, the gain instance | `382df86816` | exit 2, IMPROVED and not yet recorded | `own_delta=+0 allowed=+0`, PASSED, rc 0 |
+
+A and F pass where the absolute check failed, and B fails on the PR's own growth, so the
+detector still detects. C and D show it does not fire on a healthy tree. E shows a missing
+measurement fails rather than passing. A refusal that is not a budget row (structure.py
+exit 1 with no FAIL line), and an unrecorded gain on a row main carries (exit 2), are
+both kept. Measurement time: 84 s per `measure()` on this box at low load, several minutes
+at load average 33.
+
+**Proposal:** P-R11-99, `proposals/P-R11-99-ratchet-pr-local-row-delta.md` beside that `proto/` directory,
+listed in `R11-PROPOSALS.md`. The owner approves the self-repair and the brief line at
+round-end triage. Until then, each instance of the class is a seat re-record, as now.
diff --git a/dev/programme/delivery/3843.md b/dev/programme/delivery/3843.md
new file mode 100644
index 0000000000..c1185f53cf
--- /dev/null
+++ b/dev/programme/delivery/3843.md
@@ -0,0 +1 @@
+- [#3843](https://github.com/tvofi/heatpump_optimizer/pull/3843) — **open**, R11-RCA-MODEX: root cause of PR-local ratchet rows breaking on bot main merges (#3735) (R11-CLOSEOUT-CLEANUP)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
