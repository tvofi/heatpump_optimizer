R10-FLOW-RECORD-PITCH: record pull requests come in batches, a pitch bounds when they merge, and the record chain is cut, so a record merge stops owing the next record pull request a row.

This is Lean study K6, together with roster carries [5], [6] and the owner directive [7] of 2026-10-25. The diff touches the record-autofix job, which R10-CI-LAYOUT-P1 moved into `.github/workflows/nightly.yml` (its D-1), and `tools/audit/seat/record_row.py`. Nothing in the old place in `tests.yml` changes.

- **The record chain (carry [5]), measured first.** After a record-only merge, the planner at main owed a row: `plan_merges` at 102f74975 (right after record merge #2795) returned `[2795]`. That row is the record pull request's own `**open**` self-row, read as a stale open row. `tests/delivery_status.py`'s `classify` read it the same way (pending, then OVERDUE). So every record merge owed the next record pull request a row: 170 of 173 round-10 record merges rowed the previous record merge (`chain` under Figures). The fix uses a mechanism that already exists. `policy_lint --record` (`mergeRecordClass`) and the stamp's rule 5 (`merge_is_record_class`) already treat a record-class merge as self-disposing. Now the planner (`plan_merges(..., self_disposing=)`) and the ledger (`collect`/`classify`, `record_class`) ask the same question. `delivery_status.self_disposing` calls the stamp's `merge_is_record_class` rather than copying it: policy_lint's acceptance pins the stamp copy to the JS copy, and a third copy would be a reader nothing compares. HANDOVER trap 15 (one record per merge) still holds for every real merge.
- **The batch (carries [6], [7]).** A push beat opens or updates the record pull request only when either (a) `BATCH_FLOOR_ROWS` = 8 merges are owed, or (b) the oldest owed merge has `BATCH_AGE_COMMITS` = 8 first-parent commits after it on main. `schedule` and `workflow_dispatch` flush at any count. Waiting reports a green `batching` status. A crashed gate reports `skip-batch-gate`, which the report step turns red. Both numbers are derived from `delivery_status.STALE_AFTER_COMMITS` (12) minus `BATCH_MARGIN_COMMITS` (4). The margin covers the commits main gains while an open record pull request waits for its checks and merge: p90 3 over round 10. One bound covers both the opening wait and the merge wait.
- **The batch size: 8 to 27 rows.** The owner asked for at least 8-10 and whether batches above 10 are safe. The answer has two parts:
  - **Floor 8; 10 is not safe.** At a floor of F, the oldest row is F-1 commits old when the pull request opens. Add the p90 wait of 3: F = 8 gives 7 + 3 = 10, inside 12. F = 10 gives 9 + 3 = 12, which is OVERDUE at the p90. The null control: under the old one-per-beat regime, `age` already reached a maximum of 20.
  - **Ceiling 27; above 10 is safe.** `pr_title` names every row, and GitHub refuses a title over 256 characters. With five-digit numbers the title is 34 + 8n characters, so n <= 27 (31 with four-digit numbers). The plan is capped at the oldest `BATCH_CEILING_ROWS` = 27, and the rest wait for the next batch. Three other measurements do not bind below that:
    - Record pull requests do not conflict: 0 of 174 had a row file that main also changed while they were open.
    - Merge wait grows only mildly with size: median 2363 s at 2 rows, 2779 s at 3-4 and 3111 s at 5 or more. The wait is set by the beat and gate cadence, not by row count.
    - The API cost per row is one `/pulls/<N>` read per guard pass, on the App token. At 27 rows a beat makes at most about 122 reads (three guard passes plus the train sweep, each 1 + 1 + 27 + 2 at most), against an installation-token budget of at least 5000 per hour. The enumeration, the GITHUB_TOKEN cost that R10-RECORD-API-BUDGET measured, reads the whole window whatever the batch size. Batching cuts the pushes to main, and each push costs Governance's `record` job W + 3P reads.
- **The pitch (the brief).** It is a new arm in the automerge step, after the train hold, which is unchanged, and before the guard. A push beat skips the merge (status `skip-pitch`) while the last record merge on main is younger than `PITCH_S` = 3600 s. It does not skip once the oldest owed merge is 2 x `PITCH_S` old or `BATCH_AGE_COMMITS` commits old: that is bounded staleness, the arm carry [6] asked for. The decision is `record_row.py --pitch-check` (`pitch_wait`), read from the enumerated merges and git. The nightly and a dispatch never wait for the pitch. If the check fails, no pitch is applied (the pre-fix path), just as an unreadable train hold is.
- **"Never merge under a running train" (directive [7]).** The beat's merge stays behind the train hold, which is unchanged, and now also behind the pitch. During the pitch window the record pull request is left to the train's `--bot-prs` sweep (`AUTO_TRAIN_FLAGS`), which merges it inside the train's own sequence. The directive's "they join the train queue / --bot-prs sweep only" is read as covering a running train. Outside one, the beat still merges, under the pitch, because nothing else would land the rows on a quiet main. Removing the beat's merge entirely was the alternative. It lost because the stamp, and any day without a train, would then leave rows unmerged until the next train, and `stamp.py` rule 5 refuses those. If the owner meant the stricter reading, it is a one-arm follow-up (`say skip-train-only` before the guard).
- **The stamp is not changed here.** With batching, a stamp can meet up to 7 rowless merges. `stamp.py` rule 5 then refuses with its own message, and nothing is orphaned. A `workflow_dispatch` of `nightly.yml` drains the backlog: it flushes at any count and never waits for the pitch. Building that dispatch into the stamp prompt was drafted and withdrawn. `stampPrompt` is a canonical fragment in `.claude/workflows/web-fragments.md` (policy), and its per-file token cap (2427) has no headroom: the shortest wording read 2497. Paying would mean cutting another fragment's instructions, a policy rewrite outside this group. The flush is carried to R10-FLOW-POSTMERGE below. Stamps are rare (4 `v*` tags since 2026-10-15).
- **Harnesses.** `dev/audit/harnesses/record_batch_measure.py` (new) prints every round-10 figure below. `tests/entities.py` gains:
  - the pitch arm, executed over the train hold's stubbed API;
  - the batch gate's wiring and its two null controls;
  - the record-class ledger check.
  `r10_seat_selftests_mutants.py` gains `record_row-1` to `record_row-3`, each inside the `record_row.py` block.

Alternatives (fixer.md step 17):
- **The chain, alternatives that lost.** Keying the skip on the `record/autofix` branch name would be a second predicate beside record-class, keyed on a name rather than the diff. Writing the self-row as final is impossible, because the merge sha does not exist before the merge.
- **The batch, alternatives that lost.** Raising `STALE_AFTER_COMMITS` to fit a floor of 10 hides a stalled batch: that file's own docstring makes any change a deliberate edit with its own measurement, and the owner did not ask for it. Updating an already-open record pull request with newer rows would restart its checks, which is what the hold exists to stop.
- **The pitch, alternatives that lost.** A bash `git log` probe inside the step would need a git repository in the step's harness. A function in `record_row.py`, the module that owns the beat's decisions, is driven by its own `--self-test`.

Carry [0] (close this group if the merge queue is adopted) has not triggered: R10-FLOW-MQ-PROBE is `not-started` in the roster at this base.

## Head

`c24adf589888ef1f50436066d8943c6cf302d9fe`, cut from origin/main `dfcd8d9be1dab28cfe52f684764befd1e19291de`, which is the dispatched base (`git rev-list --count dfcd8d9b..origin/main` read 0 at 2026-10-25T18:38Z). `tests/entities.py` was measured at `7a97a021d`. Its only differences from the head are `dev/audit/harnesses/record_batch_measure.py` (the canonical `repo_root` helper inlined) and one comment in `record_row.py`. `entities.py` executes neither; `harness_headers.py`, `record_row.py --self-test` and `prepr.sh` were re-run at the head.

## Mutation proof

Each mutant was applied in a detached worktree of the head and scored by the whole `PYTHONPATH=tests/hastub python3 tests/entities.py`, or by the seat-selftest harness:

| mutant | scored by | red check |
|---|---|---|
| `classify`'s `or m.get("record_class")` deleted (`tests/delivery_status.py`) | entities | `a record-class merge's open self-row rows it; an ordinary merge's open row does not (null control)`, states `['pending', 'pending']` |
| the pitch arm's `say skip-pitch; exit 0` replaced by `true` (`nightly.yml`) | entities | `nightly.yml's automerge waits the pitch when record_row.py says so, after the train hold and before the guard (executed)`, `pitch 4 -> ('refused', False)` |
| the batch gate's `--event "$EVENT"` replaced by `--event schedule` (`nightly.yml`) | entities | `nightly.yml's record-autofix job: main-only, its own environment, loop-guarded ci: subject, guarded write set` |
| `record_row-1`: `plan_merges`'s self-disposing skip turned into `if False:` | `r10_seat_selftests_mutants.py record_row-1` | KILLED: `chain: a record-class merge's own open row owes nothing` |
| `record_row-2`: `batch_due`'s event check turned into `if False:` (the carry's "drops the event check") | `r10_seat_selftests_mutants.py record_row-2` | KILLED: `batch: a dispatch with 1 row flushes` |
| `record_row-3`: `pitch_wait`'s `< PITCH_S` dropped | `r10_seat_selftests_mutants.py record_row-3` | KILLED: `pitch: a record merge one pitch old proceeds` |

The same seat-selftest run killed S19 (`RESULT survivors=0`), its baseline.

## Null control

- **The chain:** right after a real (non-record) merge, the planner still owes rows. At ce3a77c5f the head plans `[2790, 2792, 2793]`. In the base plan's `[2790, 2791, 2792, 2793]`, only the record merge #2791 drops out. At 102f74975 the base plans `[2795]` and the head plans `[]`.
- **The batch:** 7 rows on a push wait, 8 open, and 1 on a dispatch or the nightly opens. 2 rows whose oldest merge is 8 commits old open. These are `record_row.py --self-test`'s `batch:` arms.
- **The pitch:** a young record merge with a fresh backlog waits. A backlog two pitches old, an oldest merge 8 commits old, a record merge one pitch old, no record merge in the window, one dated ahead of the clock, and a non-push event all proceed (`pitch:` arms). In the step's harness, a pitch check answering 0 or crashing (1) reaches the guard (`refused`). A live train hold answers first (`skip-train-hold`), and the train hold's own arms read as before.
- **The harness:** `record_batch_measure.py origin/main origin/main` (an empty range) prints `record merges: 0`.

## Figures

- **Round-10 record figures:** `python3 dev/audit/harnesses/record_batch_measure.py db71fe47a origin/main` (sha1 6e1490fcbbcc). db71fe47a is the commit that added the round-10 roster. origin/main was at dfcd8d9be. Rule: a first-parent two-parent commit is a merge, and a record merge's subject ends `/record/autofix`.
  - record merges: 174
  - rows: median 3, p90 5, max 21
  - wait_c: median 1, p90 3, max 10
  - wait_s: median 2629, p90 6129
  - age: median 3, p90 7, max 20
  - chain: 170/173
  - conflicts: 0/174
  - moved: 73/174
  - per UTC day, record merges out of all merges: 2026-10-24 21 of 56. The brief's 19 is the same `--grep` rule on local dates.
- **Merge wait by size:** median `wait_s` by row-count bucket (2 rows: 62 merges, 2363 s; 3-4 rows: 86 merges, 2779 s; 5 or more: 26 merges, 3111 s). This is the same rule, bucketed by an ad hoc read of the harness's `rows` and `wait_s`, not a committed command.
- **The chain at a merge:** `record_row.py --plan` over the first-parent merges since `v7.0.4`, at the tree of each named commit, with the base's and the head's `record_row.py` (scratch driver `plan_at.py`, not committed). Results are under Null control.
- **The ledger on today's main:** `python3 tests/delivery_status.py` printed `146 rowed, 12 pending, 2 overdue` at the base and `147 rowed, 12 pending, 1 overdue` at the head. The overdue merge that drops out is record merge #2795. This is a sliding figure: re-run it at your own main.
- **Stamps:** `git for-each-ref 'refs/tags/v*'` created since 2026-10-15: 4 (one on 10-19, one on 10-20, two on 10-22).
- **Title bound:** `record_row.py --self-test`'s `ceiling:` arm: 27 five-digit rows fit in 256 characters and 28 do not.
- **Gate scope:** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: FULL`, because `.github/workflows/nightly.yml changes the gate itself`. So CI runs the full suite, and the following ran locally:
  - `tests/entities.py`: 2 of 2448 failed at the head; 2 of 2445 failed at the base. Both runs fail the same two checks, `gate-sweep.yml: on CI's completion ...` and `graders-head-copy's delivery_status step is red only when ...`, which this diff does not touch (both stub their programs). CI is the authority for both.
  - `record_row.py --self-test`: all checks passed.
  - `tools/release/stamp.py --self-test`: `RESULT stamp_self_test=pass`.
  - `tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `tests/layout.py`: `layout self-test: ok`.
  - `tests/closure.py selftest`: `ALL 117 closure shrink pins PASSED`.
  - `tests/env_drift.py --claims-only <merge base>`: `claims hygiene: ... ok`.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `tests/throwaway_git.py --check`: 0 refused.
  - `tools/audit/seat/tmp_paths.py --check`: 0 refused.
  - `tools/audit/seat/ref_privacy.py --check`: 0 refused, with no new push site.
  - `node tools/policy/rules_sync.mjs --check`: ok.
  - `tools/pr/ci_predict.py`: no red predicted, after `--apply-inert` classified the new harness into `tests/harness_headers.py`'s closure.
  - `node tools/policy/agreement.mjs`: `unregistered=0`. The first draft's copied merge-subject grammar was refused and replaced by `delivery_status.subject_number`.

## Unpinned sites

- **`nightly.yml` record step's batch gate:** pinned by the wiring check in `tests/entities.py` and its null controls. `batch_due` itself is pinned by `record_row.py --self-test` (`record_row-2`).
- **`nightly.yml` automerge step's pitch arm:** pinned by the executed harness (`skip-pitch`, ordering, crash). `pitch_wait` is pinned by `record_row-3`.
- **`plan_merges`'s self-disposing skip:** `record_row-1`. `classify`'s record-class arm: the entities check above.
- **`merge_age` / `oldest_owed` / the `--batch-due` / `--pitch-check` CLI glue:** git reads with no in-tree mutant harness. Disposition: a written triage here. A failed git read returns `None`, which proceeds, the pre-fix path, so a mutant that broke them would read as no batch or no pitch, never as a stranded row. The decisions they feed are pinned above.

## Architecture score

`python3 tools/audit/archscore/score.py --diff origin/main HEAD`: `Architecture score: dS +0.0000 NULL`.

## Red checks

- **nightly-status:** grades `main`. This diff changes `.github/workflows/nightly.yml` (the record-autofix job only, which `REQUIRED_LANES` excludes) and nothing `tests/nightly_status.py` executes. A red here is main's latest scheduled run, not this pull request's. The cheaper detector is `tests/nightly_status.py` itself on every pull request; its standing cost is one API read.
- **delivery-status:** main reads OVERDUE at the base (2 overdue, `python3 tests/delivery_status.py`). One of the two is the record chain this diff cuts (#2795); the other is a real rowless merge the beat has not yet landed. The detector is the check that fired; this diff is the countermeasure for the chain share.

## Forward-carry

- **R10-FLOW-MQ-PROBE.** If the owner adopts the merge queue, carry [0] closes the pitch arm. The pitch is one block in the automerge step plus `pitch_wait`, so the probe's fixer removes both and leaves the batch. Carry: R10-FLOW-MQ-PROBE
- **The stricter reading of directive [7]** (the beat never merges, only the train sweep does) is a one-arm change that needs the owner's ruling, because the stamp flush then has to merge another way. Carry: R10-FLOW-RECORD-PITCH
- **After merge:** one UTC day's record merges by `record_batch_measure.py`'s per-day table, against 2026-10-24's 21 of 56. The null control is the day before the merge at the old rate. Carry: R10-FLOW-RECORD-PITCH

- **The stamp flush.** With batching, the stamp must drain the record beat before tagging (`stamp.py` rule 5): a `workflow_dispatch` of `nightly.yml` opens the record pull request at any count, and a second dispatch after its checks pass merges it. Wording it into `stampPrompt` needs about 70 tokens that `web-fragments.md`'s cap (2427, zero headroom) does not have, so it is the owner's call to raise the cap or pay. Carry: R10-FLOW-POSTMERGE

## Friction

- tests/entities.py: cost: one full run took about 11 minutes in this container, and the train-hold harness executes the whole automerge step under `set -u`, so a new env var the step reads (`EVENT`) silently emptied every hold arm's status until the harness env carried it. Carry: dismissed: the harness now passes EVENT; the shape is the step's own `set -u`, which is right
