# r11-tests-red-at-review: five fix reviews blocked `tests-red` in 24 h

Root-cause seat, `root-cause.md`, 2026-11-25. Measured at `origin/main`
`7aa6020f2a`. The signal is `tools/audit/seat/bottleneck_check.py`:
`block-class tests-red 33% (5/15 blocks, 24 h) vs 30%`, first-pass yield
0.38 (5/13). Each time below is a commit, check-run or dispatch-ledger
timestamp, read by the command named. Nothing was fixed or written to GitHub.
The overlay and replay files are under
`/Users/timmalmstrom/hpo-orch/r10s6/r11/proto/P-R11-DISPATCH-UNIT-REDS/`.

## 1. The five blocks

Source: the instrument's own source. `merge_throughput._bus_verdicts` reads
`review/*` and `archive/review/*` with `review_strength.VERDICT_RE`, and the
24 h window ends 2026-11-25T19:38Z. Dispatch times come from the bus ledger
`~/.zcode/bus/dispatched`. CI times come from
`gh api repos/.../commits/<head>/check-runs`.

| PR | blocked head | red at the head | how the head was made | local gate at that head | dispatched | unit red concluded | verdict |
|---|---|---|---|---|---|---|---|
| #3890 | `8d1774b5` | `stress.py` memory budgets, 10 rows (`tests / fast`) | row commit on `ae319a5f`, a merge of main | no. The fixer's own run at `db56b365` read the same 10-row FAIL, and the body declared it predicted | 08:46Z | fast 09:09Z | 09:18Z |
| #3866 | `6fb0f76a` | `entities.py` #1218 note: 182 stated, 184 derived | update_pr merge of code head `d25757cc`, itself a merge of main `f52e700d` | no. No `Prepr:` receipt for `d25757cc`, and the body says "the fixer's local prepr was not run on this head" | 10:32Z | fast 08:49Z | 10:43Z |
| #3838 | `d7029ade` | `entities.py` #1218 note, 182 vs 184 | update_pr merge of `388c1640`, a merge of main `b4a8bbd5` | no. `entities.py` ran only as a `--single` recording at `129fd0d0`, before the closures merge, and update_pr ran with `PREPR_SKIP_CODE=1` | 11:00Z | fast 10:04Z | 11:56Z |
| #3863 | `8681cc72` | `entities.py` #1218 note (182 vs 184) and `doc_claims.py` (architecture.md:306 HA-free 65 vs 66) | update_pr merge of `f2f9e3f5`, a hand-resolved merge of main `d3d66c40` | partly. The scoped gate ran at the pre-merge `875dfbc8`. After the merge only claims, shape, structure and `block_duty` ran. update_pr ran with `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1` | 12:57Z | none yet (fast started 13:46Z) | 13:35Z |
| #3841 | `b53176e2` | `tests / mutation`: five added sites survive, no autofix pin | update_pr merge of `a4123b13`, a hand-resolved merge of main `bb6377b4` | attempted. `features.py` and `entities.py` hit the 3000 s limit on the loaded host. A full prepr passed (`merge-3841.md`) | 11:13Z, again at 14:10Z | mutation 11:19Z, autofix 14:12Z | 14:52Z |

The pair counts were re-derived with `entities.py`'s `_d308_pairs` predicate
over each commit's `tests/closures.json`:

- #3866: 182 at both parents of `d25757cc`, and 184 at the merge.
- #3863: 182 at both parents of `f2f9e3f5`, and 184 at the merge.
- #3838: already 184 on the branch side, `6409098393`.

## 2. Candidates tested

- **Fixers hand off after merging main without re-running the scoped gate.**
  *Holds for 4 of 5* (#3866, #3838, #3863, #3841): see the table's "local
  gate" column. It is not a bare omission. The merge seat on #3841 ran the
  two heavy scripts and hit the 3000 s limit. #3863's seat recorded five
  host-environment reds on its pre-merge gate (load average 50-100), so a
  local red there could not be told from host noise. The rulings "Prepr runs
  scoped" (fixer.md step 5) and "CI is authoritative" make CI the gate for a
  merge head.
- **prepr runs with `PREPR_SKIP_CODE`.** *Refuted as a cause.* prepr runs no
  `tests/*.py` script in any mode. Step 2 only prints the scoped gate's MODE
  line (`tools/pr/prepr.sh`, "2. the scoped gate's MODE line, printed rather
  than inferred"). A full prepr would have missed all five reds. #3841's
  full prepr did pass.
- **Darwin vs Linux.** *Refuted.* The one platform-sensitive red, #3890's
  traced memory, was read red by the fixer's own run and declared in the
  body before the handoff. The head was handed off red so that the re-record
  could use CI's readings, which is a sequencing choice and not a missed
  detection. Host load on the local seats did make local gates
  untrustworthy (above).
- **prepr's ancestry self-test fault** (`/private/tmp/claude-501/st/prepr.sh.1`
  and `.2`: "an ancestry no commit of which carries any check run skips"
  FAIL). *Refuted.* It is a `prepr.sh --self-test` row, and it bears on
  `instrument-self-tests`, not on any `tests / fast` script. Its outputs are
  dated 20:15Z and 20:22Z, after all five verdicts.

## 3. Named cause

Two causes, one upstream of the other.

**Upstream:** a merge of main makes a tree nobody has gated. For 3 of 5 the
red is a hand-kept count that a textually clean merge leaves stale: the #1218
pair note in all three, and in #3863 also the HA-free module count. This is
the class `R11-RCA-PAIRNOTE-MERGE` already analyses, with its overlay
`pairnote_check.py`. That overlay reads STALE on `6fb0f76a`, `d7029ade` and
`8681cc72`, and OK on `b53176e2`, `8d1774b5` and the three repaired heads.
This record does not re-analyse that class.

**This record's cause:** the dispatch check meant to stop a review of a red
head cannot see a unit red. `bus.sh dispatch` refuses "a head where a
required context's latest run concluded failure" (K15 (d)) by asking
`merge_train.py classify`. `classify` judges `Train.required()`, the
ruleset's contexts, and since R10-CI-LAYOUT P2b that is `gate` alone. `gate`
is ci.yml's last job, so it concludes only when the whole run ends; the
mutation pins took 1.5-2.2 h on #3866 and #3838. Until then the head reads
`WAIT pending: gate red: none`, and a WAIT head dispatches once card C8's
three cheap checks conclude.

`gating_names()`, which adds the fixture's `gate_required` units, exists:
`owed-reds` uses it, and its docstring says "It names reds; what decides a
merge stays `required`". The dispatch read is a red reading, but it was given
the merge reading.

Evidence: the reviewer's own probe log, `probe/rev-3838-e53823c3:ev/classify.log`,
reads `11:05:44 rc=3 WAIT d7029ade… pending: gate red: none`. At that time
`tests / fast (3.14)` at that head had concluded `failure` at 10:04:16Z, 61
minutes earlier. Dispatch was at 11:00:14Z. On #3866 the pull-request run
concluded failure at 10:27:53Z (fast red since 08:49:57Z). A
`workflow_dispatch` CI run at 10:28:25Z made `gate` pending again, and the
head was dispatched at 10:32:08Z.

## 4. Process state: (c)

The process existed and was followed: `bus.sh dispatch` ran `classify` on
every one of the five dispatches. It did not produce the intended result,
because its unit reads the umbrella context and not the units the umbrella
owes. This is not (d). The refusal was written on 2026-10-29 (`9c53c107be`),
after the 2026-10-23 cut-over to `gate` (`9262e6f43d`, `0cd4cd33c5`), so its
unit was the aggregate from the start. It is not (b), because no seat skipped
a step the check asked for. The upstream half (merge heads not gated
locally) has its own record, `R11-RCA-PAIRNOTE-MERGE`, state (c).

## 5. Class reach

The overlay below was replayed over every blocked verdict with a dispatch
record since 2026-11-21: 39 verdicts, 115 h (`blocked-all.out`). It fires on
3, all `tests-red`: #3841 `b0ee904f` on 11-22 (fast red at 21:13Z, dispatched
23:11Z), #3866 and #3838. In each case `tests / fast` had concluded red 56 to
118 minutes before the dispatch. No other unit (closures, coverage, typing,
codeql, ...) was red at a dispatch.

A second shape was found and not built: C8's cheap-check wait reads only
existing check runs (`pending_checks`: `select(.status != "completed")`), so
a job not yet created reads as not pending. #3841's 11:13:54Z dispatch
preceded its `tests / mutation` job (started 11:17:43Z), and #3863's
12:57:29Z dispatch preceded its jobs (13:34Z). Making absence a wait would
have delayed those two reviews without preventing either block: mutation
concluded red with autofix still owed.

## 6. Cost test

Wall-clock on the merge path, per occurrence.

- **Defect, the part this countermeasure removes:** one review round on a
  head CI had already graded red. Dispatch to verdict was 11 min (#3866),
  56 min (#3838) and 73 min (#3841, 11-22), mean 47 min. Each is also one
  opus reviewer session. The whole block-to-merge-verdict delay is larger:
  2 h 55 m (#3866), 3 h 42 m (#3863), 5 h 21 m (#3838) and 8 h 01 m (#3890,
  which includes an owner-approval wait), median 3.7 h. Most of that is the
  repair and CI re-run, which the countermeasure does not remove, but it
  starts the repair at dispatch instead of at the verdict.
- **P(recurrence):** measured at 3 per 115 h, or 0.63 a day. That is 0.63 ×
  47 = **30 min a day** of review on red heads, plus 0.63 reviewer sessions a
  day.
- **Standing cost:** one check-runs read per dispatch, measured at 1.08 s
  (`time python3 unit_reds.py . 8681cc72…`). There were 59 dispatches in the
  24 h window, so **64 s a day**. It is 0 s when folded into
  `pending_checks`' existing read of the same endpoint. The induced work is
  one proposal, one self-test arm and the overlay; it stales no pin.
- **Verdict:** 64 s < 30 min a day. Build.

The `--mutation-arm` variant counts a `tests / mutation` red once
mutation-autofix concludes, and holds the dispatch while autofix is absent or
running. It also catches #3841 `b53176e2` (WAIT at 14:10:22Z, then RED at
14:12:56Z). It held 1 of the 20 null controls (#3869, which merged with an
answered mutation red), so it fails the null control and stays off.

## 7. Countermeasure

The rungs, in order:

- **Delete:** not possible. The dispatch refusal is the barrier; removing it
  sends every red head to review.
- **Self-repair:** the refusal's existing route, bus.sh's `REPAIR-OWED` (rc 5,
  "back to its fixer"), is reused unchanged.
- **Narrow (chosen):** the reviewability read judges
  `gating_names(required)` less `budget-raise-gate` (the APPROVAL-OWED path)
  and less `tests / mutation`, each on its latest check run. In tree terms,
  the dispatch call of `classify` passes `gating_names(req)` where it now
  passes `req`. The merge decision keeps `required`. No new refusal is added:
  an existing one reads the units it was written to read.

Demonstration (`replay.sh` → `blocked.out`, `null20.out`):

- **Fails on the defect:** `UNIT-RED tests / fast (3.14)` at #3866
  `6fb0f76a` as of 10:32:08Z, and at #3838 `d7029ade` as of 11:00:14Z.
- **Passes once fixed:** `CLEAR` at the repaired heads #3866 `086341d6` and
  #3838 `5825777c`.
- **Null control:** `CLEAR` on 20 of 20 merge-verdict dispatches,
  2026-11-25T04:01Z to 16:34Z.
- **No green by skipping:** an unreadable head prints `UNREAD` with rc 2,
  never `CLEAR`.

Mid-round, tracked tooling is frozen, so this is a proposal plus a local
overlay:

- overlay `/Users/timmalmstrom/hpo-orch/r10s6/r11/proto/P-R11-DISPATCH-UNIT-REDS/unit_reds.py <checkout> <head>`,
  run before each `bus.sh dispatch`: rc 1 means do not dispatch, rc 0 means
  dispatch.
- proposal `P-R11-DISPATCH-UNIT-REDS`, for round-end instrument triage.

**Brief text (dispatch and relay seats):** "Before `bus.sh dispatch`, run
`python3 /Users/timmalmstrom/hpo-orch/r10s6/r11/proto/P-R11-DISPATCH-UNIT-REDS/unit_reds.py <checkout> <head>`;
on rc 1 (`UNIT-RED`) do not dispatch: the head goes back to its fixer as
REPAIR-OWED with the named unit."

**Brief text (fixer and merge seats, the upstream half; carries
R11-RCA-PAIRNOTE-MERGE's overlay):** "After any merge of origin/main into a
head you hand off or update, run
`python3 /Users/timmalmstrom/hpo-seats/r10s6/rca-pairnote/pairnote_check.py --repo . --ref HEAD`
and `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` at the merged head
before the push, and repair any red in that push; a red you have measured at
the head is repaired before the handoff, never declared and handed off."

Its standing cost per merge of main is measured on this host at
`origin/main` `7aa6020f2a`. `pairnote_check.py` takes 0.27-0.48 s.
`doc_claims.py` takes 167 s wall and 52.6 s user (`time -p`, host loaded).
Together they would have caught all three count reds (#3866, #3838 and
#3863, both halves). Each of those blocks cost 2.9-5.4 h on the merge path.

The second sentence's last clause covers #3890. It is brief text only
(fixer.md step 5 already says "What `scope.run` names is green"). Any brief
that orders a CI-reading re-record after the handoff contradicts it, and the
brief should order push, read CI, re-record, then hand off.

## 8. Not done

- No issue was filed, and nothing was pushed except this record's ref.
- The pair-note class is not re-analysed (`R11-RCA-PAIRNOTE-MERGE`).
- The absent-check-run shape of C8 (section 5) is not built: it would add
  latency without preventing a block in the measured set.
