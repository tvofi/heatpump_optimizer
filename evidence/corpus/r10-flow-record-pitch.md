R10-FLOW-RECORD-PITCH: record pull requests come in batches, a pitch bounds when they merge, the record chain is cut, and a stamp flushes the batched beat before it tags.

This is Lean study K6, together with roster carries [5], [6] and the owner directive [7] of 2026-10-25. The diff touches the record-autofix job, which R10-CI-LAYOUT-P1 moved into `.github/workflows/nightly.yml` (its D-1), `tools/audit/seat/record_row.py` and, in round 2, `tools/release/stamp.py`. Nothing in the old place in `tests.yml` changes.

Round 2 answers the round-1 block (carry [6]'s stamp flush was not built) and the orchestrator's rulings (mandate 6329234399):

- **Ruling (1), the stamp flush, is built in `tools/release/stamp.py`.** It is a new rule, "flush", between rules 3 and 4, on the default path. `--no-flush` opts out. It does not go through `stampPrompt`: no fragment, cap or `web-stamp.js` wording changes.
- **Ruling (2), directive [7]: the head already admits a record pull request to the train on the guard alone.** Round 2 moves the pitch so that the admission works against main's ruleset.
- **Ruling (3):** the `--batch-due` / `--pitch-check` exit mapping is pinned by two mutants that drive `main()`.
- **Ruling (4):** the after-merge overdue count and the margin's tail are body notes.

## Carries, item by item

- **[0] Merge queue.** Not triggered: R10-FLOW-MQ-PROBE is `not-started` in the roster at this base. If the owner adopts the queue, the probe's fixer removes the pitch (one block in the automerge step plus `pitch_wait`) and leaves the batch. Carry: R10-FLOW-MQ-PROBE.
- **[1] Pre-study K6.** The pitch is `PITCH_S` = 3600 s, with the two-pitch override, in nightly.yml's automerge step.
  - Round 2 moved the pitch arm. It now sits after the train hold, the guard and the approver App's review, and before the green wait and the merge (see [7]).
  - The decision is `record_row.py --pitch-check` (`pitch_wait`).
- **[2] One record per merge (HANDOVER trap 15).** Batching times the merge, not the rows: `plan_merges` still writes one row per merge, and the batch only decides when the record pull request opens. Nothing in round 2 changes that.
- **[3] Self-test hygiene.**
  - (a) The new mutants take per-file ids inside their instrument's block: `record_row-4` and `record_row-5` in the `record_row.py` block, and `stamp-3` and `stamp-4` in the stamp block, after `stamp-2`.
  - (b) The new CLI arm builds its repository through `tests/throwaway_git.py`: `python3 tests/throwaway_git.py --check` reports 0 refused.
  - (c) The diff adds no git push site: the flush fetches and checks out, and it dispatches over the REST API. `ref_privacy.py --check` reports 0 refused.
  - (d) The Red checks section below answers every check that is red on main.
- **[4] Card 4.** This group is still held behind R10-FLOW-MQ-PROBE by its after-edge, and [0]'s close-if-adopted clause still stands.
- **[5] The record chain.** Measured first: `plan_merges` at 102f74975, right after record merge #2795, returned `[2795]`. That is the record pull request's own `**open**` self-row, read as stale. `tests/delivery_status.py`'s `classify` read it the same way. So every record merge owed the next record pull request a row (`chain` under Figures).
  - Now the planner (`plan_merges(..., self_disposing=)`) and the ledger (`collect`/`classify`, `record_class`) ask the stamp's own question. `delivery_status.self_disposing` calls `merge_is_record_class` rather than copying it.
  - Controls: right after a record-only merge the plan owes nothing, and right after a real merge it still owes that row (Null control). Mutant `record_row-1`.
- **[6] The batch, and the stamp flush.**
  - **The batch.** A push opens or updates the record pull request only when either:
    - `BATCH_FLOOR_ROWS` = 8 merges are owed, or
    - the oldest owed merge has `BATCH_AGE_COMMITS` = 8 first-parent commits after it.

    That is `STALE_AFTER_COMMITS` (12) minus `BATCH_MARGIN_COMMITS` (4). `schedule` and `workflow_dispatch` flush at any count. The age arm overrides the pitch. Controls are the `batch:` arms; mutant `record_row-2` drops the event check.
  - **The flush (round 2).** Before rule 4 reads the window, `stamp.py` takes `owed_rows`: rule 5's rowless merges, less the record-class ones it exempts. If any are owed, `record_flush` runs:
    1. It dispatches `nightly.yml`. A dispatch flushes at any count and never waits the pitch.
    2. It waits for a record-class merge on origin/main, polling every `FLUSH_POLL_S` = 60 s for up to `FLUSH_TIMEOUT_S` = 7200 s. The round-10 record-head wait is p90 6129 s (`wait_s`).
    3. It dispatches again only once the open record pull request passes the beat's own `--automerge-check --require-green`, and only after `FLUSH_REDISPATCH_S` = 900 s. That is above record-autofix's `timeout-minutes: 10`. There are at most `FLUSH_MAX_DISPATCHES` = 3 dispatches: open, merge and one retry.
    4. After the merge, `adopt_main` moves the detached checkout to that main and re-asserts rule 1.
    5. `notes_with_flush` names the record pull request in the new notes section, so rule 4 sees it.
    6. `wait_gate` waits for the new head's ci.yml `gate`, for up to `FLUSH_GATE_TIMEOUT_S` = 5400 s. Rule 2 then reads that head's verdict.

    If the dispatch is refused (no token), or no record merge lands in time, nothing changes, and rule 5 refuses as before. Its output carries the flush's line. `--dry-run` dispatches nothing. It prints what the real run would flush and reads those merges as deferred, so a dry run does not refuse a stamp that the real run would flush.
  - **Flush controls** (`stamp.py --self-test`, the `flush:` arms):
    - A window owing a row dispatches first, then polls and returns the record merge that landed. The null control: nothing owed dispatches nothing and polls nothing.
    - A refused dispatch waits for nothing.
    - A merge that never lands times out after exactly `FLUSH_MAX_DISPATCHES` dispatches, spaced `FLUSH_REDISPATCH_S` apart, and a pull request that is not ready is never re-dispatched.
    - `flush_before_tag` runs flush, adopt, notes and gate in that order on the default path. It runs none of them for a window that owes nothing, for a dry run or under `--no-flush`.
    - Mutants `stamp-3` (nothing owed still dispatches) and `stamp-4` (the default path never flushes).
- **[7] Owner directive.**
  - **Admission (ruling 2).** `merge_train.py --bot-prs` (`sweep_bots`) admits the open record pull request on `record_row.py --automerge-check --require-green` alone. It reads no review verdict and no carry, and it does not call `app_approve.sh`. The control is the new `merge_train.py --self-test` check `--bot-prs admits the record PR with no review verdict: app_approve.sh runs for the queued #7, never for #9`. Its null control: the queued #7 still pays `app_approve.sh`.
  - **What round 2 fixed.** The sweep posts no review, and main's ruleset requires one approving review (`required_approving_review_count: 1`, `dev/audit/rounds/round5/D11/fixtures/api/rules-branches-main.json`). In round 1 the pitch skipped before the approver App's review, so a pitched record pull request reached the train unapproved and the sweep's merge would have been refused. The pitch now waits after the guard and the review. A pitched head is therefore guard-passed and approved, and the train merges it inside its own sequence. That is "record pull requests ride trains rather than race them".
  - **The running-train reading** stands as written: the beat never merges under a live train hold, which is unchanged and answers first. Between trains it merges under the pitch.
  - **Batch size.** The floor is 8. A floor of 10 is not safe at the p90: 9 + 3 = 12 is OVERDUE. The ceiling is `BATCH_CEILING_ROWS` = 27, the title bound, and the `ceiling:` arm pins it. The controls are the batch arms: a batch below the floor waits, a full batch opens, and a stale backlog opens regardless.
  - **Exit mapping (ruling 3).** The `cli:` arms run `record_row.py`'s `main()` over a plan file and a throwaway repository with one owed merge and one record merge:
    - `--batch-due` exits `WAIT_RC` on a push and 0 on a dispatch;
    - `--pitch-check` exits `WAIT_RC` on a push and 0 on the nightly.

    `record_row-4` swaps `return 0 if why else WAIT_RC`, and `record_row-5` swaps its inverse. Both are killed.

Alternatives (fixer.md step 17):
- **The flush in `stampPrompt`** lost: the ruling forbids it, and the fragment sits at its token cap.
- **Refusing after the flush and asking for a re-run** (rule 1 refuses a moved main) lost. It would wait for the merge and still not tag, so every stamp over a batch would cost two web-stamp runs.
- **Loosening rule 2 to the pre-flush head's gate** lost. A record-class merge changes only row files, but the gate also judges those files, so `wait_gate` waits for the real verdict instead.
- **Loosening rule 4 to exempt record pull requests** lost: it would change what the notes must name. `notes_with_flush` writes the one line instead.
- **The pitch in front of the guard** (round 1) lost: it made the train's sweep merge an unreviewed head, which main's ruleset refuses.
- **Round 1's alternatives still hold:**
  - a branch-name predicate for the chain (a second predicate keyed on a name);
  - a raised `STALE_AFTER_COMMITS` (it hides a stalled batch);
  - a bash `git log` pitch probe (the module that owns the beat's decisions is driven by its own `--self-test`).

## Head

`9830a48986b68172628e78e2a24883cd15545b48`. It continues `handoff/r10-flow-record-pitch` c24adf58 with PR #2836's head 2d4a45e59 merged in (a fast-forward), plus two round-2 commits. The base is origin/main `f3ffb1c635327365841ad430ce8fad7488a02d61` (2026-10-25T21:45Z). `git merge-tree --write-tree origin/main HEAD` reports no conflict. VERSION, the manifest, the RELEASE_NOTES heading and both claim files are untouched.

## Mutation proof

The seat-selftest harness (`dev/audit/harnesses/r10_seat_selftests_mutants.py S19 record_row-1 record_row-2 record_row-3 record_row-4 record_row-5 stamp-1 stamp-2 stamp-3 stamp-4`) printed `RESULT survivors=0`:

| mutant | killed by |
|---|---|
| S19 (baseline) | `failed_required ...` (5 checks) |
| `record_row-1` | `chain: a record-class merge's own open row owes nothing` |
| `record_row-2` | `batch: a dispatch with 1 row flushes`, `cli: --batch-due exits WAIT_RC for 1 young row on a push, 0 on a dispatch` |
| `record_row-3` | `pitch: a record merge one pitch old proceeds` |
| `record_row-4` (`--batch-due` mapping swapped) | `cli: --batch-due exits WAIT_RC for 1 young row on a push, 0 on a dispatch` |
| `record_row-5` (`--pitch-check` mapping swapped) | `cli: --pitch-check exits WAIT_RC behind a young record merge on a push, 0 on the nightly` |
| `stamp-3` (nothing owed still dispatches) | `flush: nothing owed dispatches nothing and waits for nothing (null control)` |
| `stamp-4` (the default path never flushes) | `flush: the stamp's default path flushes an owed window ...`, `flush: a dry run dispatches nothing ...`, `flush: --no-flush, and a flush that saw no record merge ...` |
| a third stamp mutant, run by hand: the re-dispatch spacing dropped | `flush: a window owing a row dispatches nightly.yml first, then waits ...` |

Notes on how these were scored:
- The stamp step's harness line ends with `LEDGER-MERGE: tests/closures.json: text merge ...`. That is the step's last stderr line, not its verdict. The same step run unmutated through `run_step` exits 0, so the kills are the step's exit (1 against a baseline of 0). The kill names above are from `stamp.py --self-test` run directly on each mutant.
- **The moved pitch arm** was scored by the whole `PYTHONPATH=tests/hastub python3 tests/entities.py` in a detached worktree of the head, with nightly.yml restored to 2d4a45e59's (the pitch before the guard): see Figures. Round 1's entities mutants (the `classify` record-class arm, the event in the batch gate) stand as recorded there.

## Null control

- **The chain:** right after a real (non-record) merge the planner still owes rows. At ce3a77c5f the head plans `[2790, 2792, 2793]`; only record merge #2791 drops out of the base's `[2790, 2791, 2792, 2793]`. At 102f74975 the base plans `[2795]` and the head plans `[]`.
- **The batch:**
  - 7 rows on a push wait, and 8 open.
  - 1 row on a dispatch or on the nightly opens.
  - 2 rows whose oldest merge is 8 commits old open.
  - The `cli:` arms read the same both ways through `main()`.
- **The pitch** (the step's harness, executed):
  - With a passing guard and the approver App's token, a pitch of 4 reports `skip-pitch`, after a POST of the approver's review to `/pulls/42/reviews` and with no call to `/merge`.
  - A pitch of 0, or a crashed check (1), reaches the green wait (`refused`).
  - A head the guard refuses reports `refused` even under a pitch of 4.
  - A live train hold answers `skip-train-hold` first.
- **The flush:** a window that owes nothing dispatches nothing and polls nothing. A cleared window owes nothing. A record-class rowless merge is not owed.
- **The admission:** the queued #7 pays `app_approve.sh`, and the record pull request #9 does not.
- **The harness:** `record_batch_measure.py origin/main origin/main` (an empty range) prints `record merges: 0` and `tail: 0/0`.

## Figures

- **Round-10 record figures:** `python3 dev/audit/harnesses/record_batch_measure.py db71fe47a origin/main`, with origin/main at f3ffb1c63. db71fe47a is the commit that added the round-10 roster. Rule: a first-parent two-parent commit is a merge, and a record merge's subject ends `/record/autofix`.
  - record merges: 174
  - rows: median 3, p90 5, max 21
  - wait_c: median 1, p90 3, max 10
  - wait_s: median 2629, p90 6129, max 17215
  - age: median 3, p90 7, max 20
  - **tail** (new in round 2: record merges whose `wait_c` reached `BATCH_MARGIN_COMMITS`): 11/174
  - chain: 170/173
  - conflicts: 0/174
  - moved: 73/174
- **The STALE_AFTER_COMMITS margin, stated honestly (ruling 4).** The margin holds at the p90, not at the tail. When the age arm opens a batch, the oldest owed merge has 8 commits after it, and it reads OVERDUE at 12. The wait from the record head's base to its merge is p90 3, so 8 + 3 = 11 < 12. But that wait reaches 4 or more on 11 of 174 round-10 record merges (the `tail` line), and its maximum is 10, so an age-arm batch that waits that long can read OVERDUE (8 + 10 = 18) before it merges. A count-floor batch (8 rows) opens with its oldest merge at 7 or more, so its tail is no better.
  - The pitch never adds to that wait past 8 commits, because the age arm overrides it.
  - On a quiet main the wait is bounded by the beat and train cadence, not by commits.

  So the margin bounds the typical wait, not the worst one. The after-merge measurement below counts what the tail costs.
- **Main's ruleset:** `required_approving_review_count: 1` in `dev/audit/rounds/round5/D11/fixtures/api/rules-branches-main.json`, a recorded API read, not re-read live in this round.
- **Gate scope:** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: FULL`, because `.github/workflows/nightly.yml changes the gate itself`. CI runs the full suite. These ran locally at the head:
  - `PYTHONPATH=tests/hastub python3 tests/entities.py`: `2 of 2448 ENTITY CHECKS FAILED`. They are the same two that fail at the base, as in round 1: `gate-sweep.yml: on CI's completion ...` and `graders-head-copy's delivery_status step ...`. This diff does not touch either. The two pitch checks read `ok`.
  - The moved-pitch mutant (nightly.yml at 2d4a45e59, the rest at the head) printed `4 of 2448 ENTITY CHECKS FAILED`: the same two base failures plus both pitch checks, `nightly.yml's automerge waits the pitch ... after the train hold, the guard and the approver App's review, before the merge (executed)` (`pitch 4 -> ('skip-pitch', False), reviewed=False`) and `... a head the guard refuses never waits the pitch (null controls)`.
  - `record_row.py --self-test` (also under `-I`): all checks passed.
  - `tools/release/stamp.py --self-test` (also under `-I`): `RESULT stamp_self_test=pass`.
  - `tools/audit/seat/merge_train.py --self-test`: `319 checks, 0 failed`.
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `tests/layout.py`: `layout self-test: ok`.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `tests/env_drift.py --claims-only <merge base>`: `claims hygiene: f3ffb1c6... ok`.
  - `tests/throwaway_git.py --check`, `tools/audit/seat/tmp_paths.py --check`, `tools/audit/seat/ref_privacy.py --check`: 0 refused each.
  - `node tools/policy/rules_sync.mjs --check`: ok.
  - `tools/pr/ci_predict.py`: `no closures, fast, wave-script or instrument red predicted against f3ffb1c63532`.
  - `python3 -I tools/policy/agreement_py.py --out F; node tools/policy/agreement.mjs --py-json F`: `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`.

## Unpinned sites

- **`stamp.py`'s `dispatch_record_beat`, `record_merges_since`, `record_pr_green`, `adopt_main`:** network and git edges with no in-tree mutant harness. The flush logic they feed (`record_flush`, `flush_before_tag`, `wait_gate`, `owed_rows`, `notes_with_flush`) is pinned by the `flush:` arms and by `stamp-3`/`stamp-4`. Disposition: a written triage here. Each edge fails toward "no flush": a refused dispatch, an unreadable log, no token or no open pull request leaves rule 5 to refuse exactly as at the base. `adopt_main` re-asserts rule 1 and refuses a dirty tree, so it cannot stamp a tree that rule 1 would refuse.
- **`merge_age` / `oldest_owed`:** now driven end to end by the `cli:` arms over a real throwaway repository. A failed git read still proceeds (the pre-fix path).
- **The rest is pinned as in round 1:** the batch gate's wiring and the pitch arm in nightly.yml (entities), and `plan_merges`'s skip and `classify`'s arm (`record_row-1`, entities).

## Architecture score

`python3 tools/audit/archscore/score.py --diff origin/main HEAD`: `Architecture score: dS +0.0000 NULL`.

## Red checks

- **nightly-status:** grades `main`. This diff changes nightly.yml's record-autofix job only, which `REQUIRED_LANES` excludes, and nothing that `tests/nightly_status.py` executes. A red here is main's latest scheduled run, not this pull request's. The cheaper detector is `tests/nightly_status.py` itself on every pull request; its standing cost is one API read.
- **governance / delivery-status:** main reads OVERDUE (`python3 tests/delivery_status.py` printed `7 overdue` at 2026-10-25T21:45Z, a sliding figure). This diff touches what it reads (`tests/delivery_status.py`'s `classify` and the record beat in nightly.yml), and the change moves it toward green: a record merge's own open self-row now rows it, so the record chain's share of the overdue rows is cut. The rest are real rowless merges the beat had not yet landed. The batch can add OVERDUE rows only at the tail measured under Figures (11 of 174 round-10 waits past the margin), which the after-merge overdue count reads. The cheaper detector is `python3 tests/delivery_status.py` run locally, which costs one git read and is what produced the figure above; none cheaper exists for main's own ledger.
- **ci-ratchet:** red on main's push runs (the repo-wide artifacts listing returns 0 bytes); a hotfix is in flight. This diff does not touch `tests/ci_ratchet.py`.

## Forward-carry

- **R10-FLOW-MQ-PROBE.** If the queue is adopted, carry [0] closes the pitch arm (one block plus `pitch_wait`); the batch and the flush stay. Carry: R10-FLOW-MQ-PROBE
- **After merge (ruling 4)**, three measurements. The null control for each is the same command over the day before the merge.
  - One UTC day's record merges by `record_batch_measure.py`'s per-day table, against 2026-10-24's 21 of 56.
  - The same day's **overdue count**: `python3 tests/delivery_status.py`'s `overdue` figure at main, sampled at each record merge and at the day's end. It is the count, not only the rate, because the margin above holds at the p90 and not at the tail.
  - The `tail` line over that day, which says how many batches waited past `BATCH_MARGIN_COMMITS`.

  Carry: R10-FLOW-RECORD-PITCH
- **The first stamp after merge** exercises the flush live. Its log should show `record flush: record merge(s) #N landed ...`, or rule 5's refusal carrying the flush's reason. A web-stamp seat runs `stamp.py` in the foreground, so a flush that waits up to `FLUSH_TIMEOUT_S` + `FLUSH_GATE_TIMEOUT_S` needs the command run as a background task. That is the stamp seat's to know, and `web-stamp.js` stays as it is under the ruling. Carry: R10-FLOW-RECORD-PITCH

## Friction

- tests/entities.py: cost: one full run takes about 11 minutes in this container, and the moved-pitch mutant needed a second full run in its own worktree. Carry: dismissed: the pitch harness executes the real step, and that is what made the round-1 ordering defect visible.
- tools/policy/agreement.mjs: cost: run bare, it reports `refused=6` (`no --py-json FILE`); CI first writes `agreement_py.py --out`. Carry: dismissed: the governance lane runs both, and run that way it reads ok (Figures).
