R11-PRE-HANDOFF-BOOKKEEPING part 2 of 4 (owner ruling 2026-11-13 on card P10): roster carries 5-9, numbered 0-based as the roster and the brief number them. Part 1 (#3664) built carries 0-4; carries 10-20 are later parts, and none is answered here.

- Carry 5: built here (S14-DRAIN-REFUSAL-NOT-DURABLE, `beat_jobs.roster_drain`). A refused op used to go into `roster-done.json` beside the applied ones, and its line lived only in `digest/jobs/roster-drain`, which `write_job` replaces on the next pass that runs an op. Now each refusal (the lint gate's `#refused` mark, or a malformed `hold` line) goes to `state/roster-refused.json` and appends `<utc> ROSTER-REFUSED #<occurrence> <line>` to `digest/events.txt` through the existing `event()`. The occurrence key keeps a re-queued identical op distinct. A refusal is still never retried, and the CASCADE and no-op-attempted arms are unchanged.
- Carry 6: built here (POSTMERGE-STAGE-VIA-DRAIN, `postmerge.enqueue`). The design keeps the direct `roster_sync.py --apply` first, and queues on a refused or raced sync only. The drain is backlogged at exactly the moments the race is lost, and the direct push still lands whenever the drain is idle. A refused sync appends `set-stage <GROUP> done --at-sha <merge>` to `<state dir>/roster-drain.queue` and prints `stage QUEUED <line>` after `stage refused rc N: <detail>` (the P435 ERROR line is kept). `set-stage done` already writes `carries-open` over a pending carry (`roster_lib.closing_stage`), so the queued op needs no second rule. Every appended line ends `# postmerge <merge sha>`, which `roster_queue`'s grammar drops. A line already in the queue, marked `#done`/`#refused` or not, is not appended again, which makes a rerun for one merge queue nothing. A queued stage is no longer owed. The ledger event stays for no group, and for a queue that cannot be written. `roster_sync.py` is unchanged: it reconciles every group per pass and never sees one merge's body, so the per-merge derivation belongs to `postmerge.py`.
- Carry 7: built here (ROSTER-PUSH-LEASE, `roster_lib.writer_lease`). This is the lease form, a flock on `$HPO_STATE_DIR/roster-writer.lease`. The drain takes it for each op without waiting, and while it is held starts no further op that pass and writes no line. `carry_fold.py` takes it around its fold, waiting up to `LEASE_WAIT_S` (600 s, two drain ops' worth), and refuses with rc 1 and nothing written past that. flock is released with the holder's process, so no stale lease outlives a killed holder. The lease lives in `roster_lib.py`, the module both writers already import; `roster_edit.py` is unchanged, so the carry's "adds roster_edit.py to this group's files" does not arise.
- Carry 8: built here (POSTMERGE-DERIVES-CARRY-MARKS, `postmerge.derive_marks`). `record_beat.facts` now also reads the merged body. Each body line `Carry N: built here (<KEY>, ...)` becomes `mark-carry <GROUP> --match <KEY> implemented <merge>`, and each `Carry N: dismissed (<KEY>, <reason>)` becomes `... dismissed <reason>`. KEY is the first comma-separated field in the parentheses and must be contained in exactly one carry of the group. N is never read, because the body counts from 1 and the roster from 0. A line with no key, a key hitting zero or two carries, or a dismissal with no reason prints `OWED mark: ...` and queues nothing for that line. A carry already marked is skipped. The marks go on the drain on every merge, before the stage op when that is queued too, so `set-stage done` reads them. This body's own five lines use that grammar, and `derive_marks` over the round-10 roster file's entry for this group returns 5 ops and nothing owed (`## Figures`).
- Carry 9: built here (CARRY-FOLD-SUPERSEDED, `cloud_relay.sh fold_superseded`). `carry_fold_arm`'s `ls-remote` now also lists `refs/heads/handoff-body/*`. A wip ref is skipped, with no level line, no fold and no memo, in two cases. The first is a `handoff-body/<topic>` whose committer time is later than the wip commit's. The second is `fix/<topic>` or `fix/<topic>-pr` named by a `Merge pull request #N from <owner>/fix/...` subject in a local `git log --merges origin/main`. `dispose` is not widened.

Alternatives not taken, and why each lost:
- Carry 6, queue always and drop the direct push. Every stage would then wait out the drain's backlog (one batch measured at about 90 min, triage sweep line 1520), where today the direct push lands within the pass whenever the drain is idle.
- Carry 6/8, putting the derivation in `roster_sync.py`. Its `--apply` pass reconciles every group from the PR list and reads no single merged body. A per-merge path there would be a second entry point beside the one `postmerge.py` already is for both merge paths.
- Carry 7, carry_fold enqueueing at the head of the queue and waiting for its line. The queue is append-only (QUEUE-SHRANK refuses a rewrite), and a head insert needs a second queue or a priority grammar. The lease needs neither.

## Head

`044d63ce50b849dfc05490150a91b052886984c9` is this PR's head. It is one commit on the previous head `475e001874041628b919539bfdac006ba495da37`, answering the review's block (`review/3701` `e82640d464`). The merge base is `4ecca4cc580b1065e366bf12bd5a917d40d03c0e`. `git merge-tree --write-tree origin/main 044d63ce50b849dfc05490150a91b052886984c9` exited 0, so no merge of main was made. Every self-test this diff touches, the scoped gate, `structure.py` and `prepr.sh` were re-run at this head (`## Figures`), measured 2026-11-17.

Block answers:

1. code-defect, a clean no-group merge owed a mark. `postmerge`'s stage arm now skips to the next step when nothing is queued (a clean sync and no mark), before the no-group check. Failing test first: the new row `a clean sync with no roster group owes nothing, queues nothing and opens no ledger event` failed at `475e0018` with `['main classify said', 'OWED mark: queue: no group to queue']` and passes at this head. The new mutant `empty_queue_owed` (the guard made `if False:`) is killed by that row. The reviewer's `harness_nogroup.py` at this head: sync rc 0 prints `rc 0`, `nothing owed`, `ledger-open False`. The null control in the same harness, sync rc 1, still prints `set-stage owed no-group`, `OWED stage: rc 1: synced` and `ledger-open True`, as at both reviewed ends.
2. mutation-vacuous, three survivors. Each now has a row that turns it red:
   - M9 (`carry_fold.main` folding without the lease): the self-test now runs `main()` itself with `LEASE_WAIT_S` set to 0 against a lease the test holds, and checks `main folds holding the lease: a lease the drain holds refuses before any roster read` (rc 1 and the `REFUSED the roster writer lease` line). Its null control, `with the lease free, main goes on to read the roster`, runs the same argv with the lease released.
   - M10 and M11 (`record_beat.facts` dropping `body` from its return or from the `--json` fields): the self-test's fake `gh pr view` answers a `body` only when `body` is in the requested field list, and the new row `the merged body is asked of gh and returned (postmerge derives its marks from it)` checks `facts()` returns it.

The reviewer's driver `mutants.py`, run at this head in place with each file's own self-test, prints KILLED for all 16 rows M0-M15. M9: `carry_fold self-test: 11 checks, 1 failed`. M10: `record_beat self-test: 18 checks, 1 failed`. M11: `record_beat self-test: 18 checks, 1 failed`. M12: 2 failed. M13: 1 failed. M14: 2 failed. M15: 1 failed. M0, M3: 2 failed. M1: 5 failed. M2: crashed on the self-test's `TypeError`. M4: 3 failed. M5: 6 failed. M6, M7: `FAIL writer_lease: a held lease refuses a second holder, at once or after its wait`. M8: `carry_fold self-test: 11 checks, 4 failed`. The `cloud_relay` `fold_superseded` mutants are untouched by this commit and were not re-run.

The review's note (stale `## Head`) is answered by this section.

## Mutation proof

Each mutant is a row of the named self-test's own mutant table, run in a temp copy; the failing row is named.

- `beat_jobs.py --self-test`:
  - `roster_refusal_no_event` (the `event(...)` call in `refuse` -> `pass`): FAIL `roster-drain: a refused op writes one events line that survives a following applied pass`.
  - `roster_refused_as_done` (`refused.add(key)` -> `done.add(key)`): FAIL `roster-drain: a refused key is remembered apart from the applied ones`.
  - `roster_refused_retried` (`if key in done or key in refused:` -> `if key in done:`): FAIL the events-line row (the op runs twice).
  - `roster_malformed_hold_retried` (the hold arm's `refuse(key)` deleted): FAIL `roster-drain: a malformed hold line is refused once and marked, never re-printed`.
  - `roster_lease_ignored` (a held lease replaced by a `/dev/null` fd): FAIL `roster-drain: no op starts while an out-of-queue writer holds the roster lease; the next pass runs them`.
  - `roster_lease_released_early` (the lease closed before the op runs): FAIL the same row, through its in-op probe.
- `postmerge.py --self-test` (its new mutant table; a `null` copy with no edit passes whole):
  - `no_newline` and `stage_not_queued`: FAIL `(i) a refused or raced stage queues exactly one terminated line for the merge, owing nothing`.
  - `no_idempotence_key`: FAIL `(ii) a second postmerge run for that merge queues nothing, the first line marked or not`.
  - `marks_by_index` (the carry picked by the body's N): FAIL `(i) #3470's body yields exactly the two marks batch 236 queued by hand, keyed on text`.
  - `empty_queue_owed` (the empty-queue guard -> `if False:`): FAIL `a clean sync with no roster group owes nothing, queues nothing and opens no ledger event`.
  - `two_hits_taken` (`len(hits) != 1` -> `not hits`): FAIL `a key hitting two carries, none, or no key is OWED and queues nothing; a marked carry is skipped`.
- `cloud_relay.sh --self-test` with the `fold_superseded ... && continue` line's `continue` replaced by `false` (`mut:foldsuperseded`), in place at the head and restored by `git checkout`: `521 checks, 4 failed`. The failing rows are `a stop with a later handoff-body/<topic> leaves the carry-fold level (P642)`, `... and prints no OWED line`, `a stop whose fix/<topic>-pr merged into origin/main leaves the level` and `... and folds nothing, though its stop is CARRY-LANDED alone with a kept body`. Both null rows stay green.
- Failing test first, `beat_jobs`: the head's `beat_jobs_selftest.run` against main's `beat_jobs.py` (no mutants) fails 5 rows. They are the three carry-5 rows, the lease row, and the malformed-hold row, which now reads `roster-refused.json`. The lease null row passes there.

## Unpinned sites

`prepr.sh`'s diff mutant step ran with `MUTANT_IN_PLACE=1` and `MUTANT_CMD="bash -c '<postmerge --no-mutants && beat_jobs --no-mutants && carry_fold && roster_lib self-tests>'"`. The `bash -c` wrapper is needed because `mutant_run` splits the command with `shlex` and runs no shell, so a bare `&&` chain fails its own baseline (`BASELINE FAILS`, the first two runs of this seat). The step was first run alone at `61521793`, where 10 of the 40 drawn mutants survived. Three of those are answered at this head:

- `beat_jobs.py` `refuse`'s `key.split("\t", 1)` -> `2` is equivalent unless an op's text holds a tab. The site is gone: the line is now `key.partition("\t")`.
- `beat_jobs.py` `writer_lease(ctx.state, 0)` -> `1` (the drain would wait a second before yielding) is now killed. The lease row also asserts that the yielding pass returns within 0.5 s.
- `beat_jobs.py` `holds.pop(key, None)` deleted (the block moved under the new refusal arm) is now killed. The released-hold row also asserts that `roster-hold.json` is empty after the op applies.

Both kills were run by hand, each mutant in a temp copy through `beat_jobs_selftest.cases`, and each failed exactly the named row. At this head `prepr.sh` prints `8 survivor(s)`, all of them dispositioned here:

- `beat_jobs.py:191` `sys.path.insert(0, ...)` -> `insert(1, ...)`: equivalent. `roster_lib` resolves from the seat directory at either position, and the `-I` entry point puts that directory first. A value check.
- `beat_jobs_selftest.py` 323, 324, 342, 343, 347 and 349: the lease rows' own scaffolding. These are the probe's and the fold stand-in's `os.close`, the probe's `if fd is not None` guard, the stand-in's `writer_lease(..., 0)` constant and its release. Each bends cleanup of the test's own lease fds, not production behaviour. The production sites are pinned by `roster_lease_ignored` and `roster_lease_released_early`.
- `beat_jobs_selftest.py:350` `< 0.5` -> `<= 0.5`: equivalent on a measured float. The bound it guards (a 1 s wait) is killed, as above.

`--list` enumerates 271 diff mutants, and the step draws the first 40 in file order, which are all in `beat_jobs.py` and its self-test. The added lines of `postmerge.py`, `carry_fold.py`, `roster_lib.py` and `record_beat.py` were not drawn by this step. They are pinned by the mutant tables and rows in `## Mutation proof` and by the review's 16 mutants, all killed at this head (`## Head`); `cloud_relay.sh` is pinned by its `mut:foldsuperseded` run.

## Null control

- Carry 5: `roster-drain null: an applied op writes no events line; a malformed hold writes one` (the applied op writes nothing to `events.txt`). The pre-existing rows for drain-once, CASCADE, UNRUN, budget, hold and QUEUE-SHRANK all pass unchanged.
- Carry 6: `(iii) null control: a sync that landed queues nothing and creates no queue`. For the no-group fix, the reviewer's harness with sync rc 1 still owes the stage (`## Head`).
- Carry 7: `roster-drain null: with no fold pending every op runs, and the lease is free after the pass`, carry_fold's `null control: a free lease runs the fold once` and `null control: with the lease free, main goes on to read the roster`, and roster_lib's `writer_lease: a released lease is taken (null control)`.
- Carry 8: `(iii) null control: a body with no built or dismissed line yields no op and owes nothing` (the input holds `left for a later part` and `not built here` lines).
- Carry 9: `null control: a handoff-body older than the stop keeps its OWED line` and `null control: a stop with no handoff-body and no merge keeps its OWED line`.

## Figures

- `python3 -I tools/audit/seat/beat_jobs.py --self-test`: `beat_jobs self-test: 291 checks, 0 failed` (main: 281).
- `python3 -I tools/audit/seat/postmerge.py --self-test`: `postmerge self-test: 40 checks, 0 failed`.
- `python3 -I tools/audit/seat/carry_fold.py --self-test`: `carry_fold self-test: 11 checks, 0 failed`.
- `python3 -I tools/audit/seat/roster_lib.py --self-test`: `roster_lib self-test: 103 checks, 0 failed`.
- `python3 -I tools/audit/seat/record_beat.py --self-test`: `record_beat self-test: 18 checks, 0 failed`.
- `bash tools/audit/seat/cloud_relay.sh --self-test`: `cloud_relay self-test: 521 checks, 0 failed`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, against `4ecca4cc58`. With `PYTHONPATH=tests/hastub`, `tests/doc_claims.py` printed `ALL 410 checks PASSED` and `tests/entities.py` printed `ALL 2725 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Carry 8, this body's own lines. `derive_marks` (imported from `tools/audit/seat/postmerge.py` at this head, through the review's `marks.py`) over this body's five `Carry N: built here` lines against `dev/programme/rosters/wave-r10-groups.json`, group `R11-PRE-HANDOFF-BOOKKEEPING`, returns 5 ops and an empty owed list at `0c8313fd16` and at `origin/handoff/audit-r10-roster` `b7f7819eaf`. The control is the self-test's two-hit, no-hit and no-key rows, which return owed lines.
- Carry 6 (v), the #3447 replay: `enqueue` of `set-stage R10-OUTSIDE-DIAG-REDACT-LOCATION done --at-sha ceb3070ccb49fe6dfc9d403458e8a3cc03c5595e` parses through `roster_queue.parse_line` to `("set-stage", "R10-OUTSIDE-DIAG-REDACT-LOCATION", "done", ["--at-sha", <sha>])`, and `replay_unsafe` returns `None`. This is a self-test row.
- `PREPR_SKIP_CLOSURES=1 MUTANT_IN_PLACE=1 MUTANT_CMD=<the bash -c chain above> bash tools/pr/prepr.sh <this body>` at `044d63ce50b849dfc05490150a91b052886984c9` printed `PRE-PR: 044d63ce50b849dfc05490150a91b052886984c9 ... rc=0`. Its `ci predict` step printed `no closures, fast, governance or instrument red predicted against 4ecca4cc580b`, and `merged structure` printed `STRUCTURE RATCHET PASSED` with HEAD merged with origin/main. Its only WARN is the same 8 survivors listed under `## Unpinned sites`. The closures step was skipped by `PREPR_SKIP_CLOSURES` (tvofi, 2026-11-15).

prepr: passed rc=0 at 044d63ce50b849dfc05490150a91b052886984c9

## Red checks

`governance / instrument-self-tests` is red at `475e0018` and at the merge base (`merge_train.py introduced`: `introduced: 0`, head job 133816487439 failure, base job 133799884479 failure, from the review's evidence). It is inherited from main (`tools/ci/selftest_closures.json` misses reads added by recent merges; a re-record hotfix is in flight) and is not repaired here.

## Forward-carry

none

## Friction

none

## Architecture score

n/a: no budget or gate rise.
