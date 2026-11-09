R10-TICK-LEVELS part 2 (part of #201). Part 1 (#3200) is merged; this part builds the carries origin/main did not yet hold and gives the rest a one-line disposition. Six items were built: carries 13, 14 (tick), 7 (topic grammar, RCA, bugclasses), 15 (open cap, opener), 16 (owed_unactioned) and 17 (dispatch text). The two carries that touch the same tick seat as the settled ones (6, 7's RED-UNOWNED reader) are extended in place.

This head also repairs `tests / closures`, red in both suites at `a9827ca3e8ff950e64f129a0e7e436b5fdb68376` (run 42511447807, job 128825445404: `UNDER-SCOPED: tests/entities.py really reads 1 file(s) the committed closure does not list: tools/audit/seat/topic_grammar.py`). closures-autofix read `skip-merge-failed` (job 128834461453), so the repair is manual (ci-autofix.md). Cause: `tools/audit/seat/roster_sync.py`, already on `INERT_EXCEPT`, now imports `topic_grammar` in-process at its top level, so `tests/entities.py`'s load of it opens the file; the `tools/audit/` prefix kept it INERT, and an in-process read of an INERT file lands in the recording's `files` (`closure._load_recording`'s docstring), where only leaving INERT can list it. Repair: `tools/audit/seat/topic_grammar.py` joins `INERT_EXCEPT` in `tests/closure.py` (the `plan_page.py` route, reason recorded beside the entry), and `./tests/derive_closures.sh --single tests/entities.py` re-recorded the one affected closure. No other script's closure moved.

## Head

`977fd0033ba82b61fbb82aefe5687e7e95510588`, one commit on the pull request head `0942168880c7c1cd0c91e9bdf5bba79b64425aa2`. Resolution delta for the reviewer, against the blocked head `fd973e035d6044ac55a105a7156af5b46ce5838f`:

- **The merge of main.** `0942168880c7c1cd0c91e9bdf5bba79b64425aa2` is the merge-main bot's `ci: merge main`, origin/main `631ac4df34c9d31f2ca2c6bcf7aeb4097ad5e941` (#3353) into `fd973e035`. This seat re-did the same merge locally with the drivers installed (`python3 tests/env_drift.py --install-merge-driver`; `merge.ledgermerge.driver` set) and compared: `git diff --quiet HEAD 0942168880c7c1cd0c91e9bdf5bba79b64425aa2` exited 0, so the bot's merge is taken as the merge rather than a second commit with the same tree. origin/main read at `631ac4df34c9d31f2ca2c6bcf7aeb4097ad5e941`, 2026-11-09T13:37:49Z.
- **Driver-resolved hunks.** The files both parents changed since their base `806e952cadde68bec637a491b4646dd6fb5281d0` (`comm -12` of the two `git diff --name-only` lists) are `dev/audit/config/bugclasses.json` and `tests/closures.json`, both `ledgermerge`; no file was hand-resolved. Read back leaf by leaf (each JSON flattened to key paths, each merged leaf compared against the three-way rule over base, `fd973e035` and `631ac4df3`): bugclasses.json, the branch changed 33 leaves (`R10-TOPIC-FAMILY` and its `_rca` key), main 12 (`_rca` keys), 0 changed by both, 0 merged leaves differing from the rule; closures.json, the branch 2 leaves (`closures`, `inert_reads`), main 1 (`inert_reads`), 0 by both, 0 differing. A leaf both sides changed, or a list both sides edited, would have printed as `both`; none did.
- **The selftest_scope fix** (the reviewer's `semantic-conflict`). The branch added the step `Show the topic grammar refusing a bare number and a prefix as family members` with `if: ${{ !cancelled() }}` before main's R10-CI-SELFTEST-SCOPE (#3315) reached it; at the merged head `python3 -I tools/ci/selftest_scope.py static` refuses it (`UNGATED step ...: its if: does not read steps.scope.outputs.<its own id>`), which is the `instrument-self-tests` red. Commit `977fd0033` gives the step `id: topic-grammar` and `if: ${{ !cancelled() && steps.scope.outputs.topic-grammar == 'true' }}`, and adds its entry to `tools/ci/selftest_closures.json` by the file's own re-record, `python3 tools/ci/selftest_scope.py record --step topic-grammar` on this Linux container with strace (the entry is measured, not written: files `tools/audit/seat/topic_grammar.py`, probe `.`, no index, no objects). Alternative not taken: leaving the step ungated and adding its id to `UNGATED` would silence the wiring check for a step that only reads its own file, which that tuple reserves for the steps that choose, trace, start and audit.

## Dispositions of carries

The review packet numbers carries 1-18; the brief's own headings run "Carry 0" to "Carry 17", so packet N is the brief's heading N-1. Each was re-checked at 5bc009bc8 by reading the named symbol.

Already on origin/main (`[implemented: 6777ec33]` or read at the symbol), not rebuilt:
- Carry 1 (brief 0, approval-owed, review-stalled, record-branch skip, owed buckets): settled in `owed_levels`/`_bucket`.
- Carry 2 (brief 1, `ledger.review_owed` `skip_branch`, standing-dispatch.md sentence): settled.
- Carry 3 (brief 2, per-PR buckets with one OWED line, critical path first): settled.
- Carry 4 (brief 3, train-parked is owed): settled (`_parked`).
- Carry 6 (brief 5, BODY-AHEAD, RED-UNOWNED, FIRE-OWED): settled; its last clause (reconcile the fired-session ledger against the cloud run list, RETURN-MISSING) is not built: it needs a cloud run list this instrument cannot read. Destination: the dispatch seat's owner, by this note.
- Carry 8 (brief 7 is Carry 7 below; brief 6 = packet 7): the packet-7 definition of "a seat is on it" (FIRED line naming number, topic or payload file, or a moved handoff-wip/handoff/handoff-body ref) is `_seat_on`/`_fire_names`: settled.
- Carry 9 (brief 8, roster-group tick lines): settled.
- Carry 10 (brief 9, gate-race line instead of NOT REVIEWABLE): settled in `one_pr`.
- Carry 11 (brief 10, the line names `GATE_WAIT_MAX_S`): settled.
- Carry 12 (brief 11, a reviewer's `merge_train.py --self-test` is no merge race): settled in `_seat_procs`.
- Carry 18 (brief 17, fixer and reviewer text on a moved main): built here; fixer.md and fix-review.md step 13 already say merge-tree only, so no policy file changed.

Appended to the group's roster entry on `origin/handoff/audit-r10-roster` after this part was authored (`f641f97bd`, 2026-11-08T07:15:54Z) and after this repair was dispatched (`29175b619`, 2026-11-08T19:43:15Z): roster_edit `append-carry` commits `fcc9a1933` (carry 19, 20:18:24Z) through `24ab0b1df` (carry 25, 21:12:29Z), each from `handoff/r10-rca-tick-blind`. Not built in part 2; each stays owed by R10-TICK-LEVELS's next part, which reads it from the roster entry:
- Carry 19 (item 2a35d4b3, NOT REVIEWABLE names deferral-only and real; the board flags a disabled Gate sweep): not built here. Carry: R10-TICK-LEVELS (item 2a35d4b3)
- Carry 20 (item 42c659b5, OUTSIDE-CHAIN-IDLE walks after-edges for outside-sourced groups): not built here. Carry: R10-TICK-LEVELS (item 42c659b5)
- Carry 21 (item c4fd2112, probe-refused classified by reason and ranked by critical path): not built here. Carry: R10-TICK-LEVELS (item c4fd2112)
- Carry 22 (item f7f2f31d, unrecorded-merge query; the HANDOVER line stops naming state_docs): not built here. Carry: R10-TICK-LEVELS (item f7f2f31d)
- Carry 23 (item 2acc909a, the repair-discharges-line self-test barrier per flagged line kind): not built here. Carry: R10-TICK-LEVELS (item 2acc909a)
- Carry 24 (item bfa71add, postmerge / record_beat posts nothing when issue 201 already carries the sha40): not built here. Carry: R10-TICK-LEVELS (item bfa71add)
- Carry 25 (item 471e3cd3, OWED handoff lines carry the opener's last result; OPENER ABSENT; triage held-by-ruling; counted, never silently capped): not built here. Carry: R10-TICK-LEVELS (item 471e3cd3)
- Carry 26 (item d3df9924, the roster's copy of this body's Carry 21 line, appended after the previous push): a duplicate of Carry 21, not built here. Carry: R10-TICK-LEVELS (item d3df9924)
- Carry 27 (item becd0c23, the roster's copy of this body's Carry 26 line): a duplicate of Carry 26, not built here. Carry: R10-TICK-LEVELS (item becd0c23)

Appended to the roster entry after the previous body push, from triage batch 137 (`dev/programme/triage/s6-batch137.md`), read at `origin/handoff/audit-r10-roster` `b03fd2f9e` (2026-11-09T10:00:51Z). This repair seat's brief is the merge of main and the body; none is built in part 2, and each stays owed by R10-TICK-LEVELS's next part, which reads it from the roster entry:
- Carry 28 (P438, UNBLOCKED-UNDISPATCHED: a carries-open or not-started group with its after-groups done and no dispatch, handoff or PR ref prints `UNDISPATCHED`): not built here. Carry: R10-TICK-LEVELS (triage P438)
- Carry 29 (P445, CI-ATTEMPT-ALARM: a `beat_jobs.py` row flags a ci.yml run at attempt 20 or more): not built here. Carry: R10-TICK-LEVELS (triage P445)
- Carry 30 (P455, RED-UNOWNED-OVERFIRES: the red-unowned level reads `merge_train.py classify` instead of the gate conclusion): not built here. Carry: R10-TICK-LEVELS (triage P455)
- Carry 31 (P456, OWED-UNACTIONED-CAP-LINE: the cap notice prints outside the OWED prefix; an UNREADABLE line still lists every key it read): not built here. Carry: R10-TICK-LEVELS (triage P456)

Built here: Carry 7 (brief 6's reader, the tick's `_seat_on` reads `family`) and brief 7 (topic_grammar, packet carry 8, below), carries 13 (brief 12 is settled: `STUCK_FACTOR`, null started_at), 14, 15, 16, 17 as listed next.

## Built here

- Carry 14 (brief 13): `Tick._disposed` reads `lg.dispositions`; BODY-AHEAD does not owe when `refs/heads/handoff-body/<topic>` holds a disposition at the ref's sha; an older sha still owes.
- Carry 15 (brief 14): `blocked_stops` prints `OWED blocked-stop <topic> <sha12> <Question line>` for a `handoff-wip/<topic>` tip holding BLOCKED.md with no newer `dispatch/fixer-<topic>` and no disposition at the sha; `_seat_on` does not count such a tip; ledger.py gains the `blocked-stop` kind and the `handoff-wip/` arm; the fixer brief gains the BLOCKED.md sentence.
- Carry 8 (brief 7): tools/audit/seat/topic_grammar.py (`pr_topic`, `family`, `family_refs`, `group_of`, `owner_topic`, CLI `pr-topic` and `family-refs`); `noreturn_arm` counts a moved full-matching family member as a return; `open_driver.resolve` and `roster_sync.matches` call the moved rules unchanged; cloud_relay.sh calls `pr-topic`; `_seat_on` reads `family` for handoff-wip; dev/audit/rca/topic-family.md and the R10-TOPIC-FAMILY class with its `_rca` entry are landed (also registered in finding.schema.json and CLASS_GUESS, which the agreement lane requires).
- Carry 16 (brief 15): `pr_cap.counted` skips `triage:` and `roster:` titles; the opener skips `triage-` and `roster-` topics (`batched`).
- Carry 17 (brief 16): `owed_unactioned.key_of` keys the tick's `OWED <kind> #<n> <head12>` lines (every bucket kind), `OWED fire-owed <payload>` and `OWED blocked-stop <topic> <sha12>`.
- Carry 18 (brief 17): the rendered fixer text hands off at the first clean prepr.sh head and merges main only on a `git merge-tree --write-tree origin/main HEAD` conflict; the reviewer text blocks on main only on a merge-tree conflict.
- Carry 5 (brief 4, third blocked verdict owes a re-cut), Carry 13 (brief 12): settled as above (`RECUT_BLOCKED`; `Tick.stuck`).

## Mutation proof

At this head, each mutant asserted to match exactly once before it was applied, its check run, the file restored from a copy; `git diff --quiet` exited 0 after the set:
- G1, the gating predicate: `.github/workflows/governance.yml`'s `if: ${{ !cancelled() && steps.scope.outputs.topic-grammar == 'true' }}` back to `if: ${{ !cancelled() }}`. `python3 -I tools/ci/selftest_scope.py static` exits 1: `UNGATED step 'Show the topic grammar refusing a bare number and a prefix as family members'` and `STALE ... extra ['topic-grammar']`.
- G2, the measured entry: the table key `topic-grammar` renamed `topic-grammarX`. The same command exits 1: `STALE tools/ci/selftest_closures.json: its steps differ from the workflow's: missing ['topic-grammar'], extra ['topic-grammarX']`.
- T1, `family_refs`'s `fam.fullmatch` (the `mut:tgprefix` site) to `fam.match`: `python3 tools/audit/seat/topic_grammar.py --self-test` fails 4 rows (a part ref belongs to its base's family; a part topic reaches the base and its siblings; a bare -<N> is not a family member; a sibling topic is not matched by prefix).
- T2, `family`'s suffix `(?:-p\d+)?` to `(?:-p?\d+)?` (a bare `-<N>` counted as a member): the same self-test fails `a bare -<N> is not a family member`.

main's merge changed no file this branch's tick-levels code edits (the only both-sides files are the two ledgers above), so the earlier mutants below were not re-taken past T1 and T2; their self-tests pass at this head (`## Figures`).

Earlier heads:

The merge into `1c29e5ab`, re-taken at this head where main changed a file this branch edits: `tools/audit/seat/cloud_dispatch.py` (Mutant A, deleting the fixer text's `first push \`BLOCKED.md\` with a \`Question:\` line` clause, fails "the fixer is told to push BLOCKED.md with a Question line before stopping on a question"; Mutant B, deleting the reviewer text's `, never on a head that is behind main but merges cleanly` clause, fails "the reviewer blocks on main only for a merge-tree conflict, never a clean head behind main"; each 132 checks, 1 failed), `tools/audit/seat/ledger.py` (deleting the `("refs/heads/handoff-wip/", "blocked-stop")` arm makes the self-test exit 2 with `ledger: refused: 'refs/heads/handoff-wip/x' matches no ledger arm`). Each mutation was asserted to match exactly once before it was applied (a first run of Mutant B asserted two matches, found one, applied nothing, and is discarded as vacuous), the file restored from a copy, and `git diff --quiet` held after the set. `tests/closure.py`: origin/main's change there adds one `INERT_EXCEPT` entry (`tools/policy/budget_raise_gate.py`) and does not touch this branch's `topic_grammar.py` entry, so that pin is not re-taken. `tools/audit/seat/cloud_relay.sh`: its self-test passes at this head; no mutant re-taken.

Earlier heads:

The merge: `python3 tools/audit/seat/cloud_dispatch.py --self-test` passes at this head (the count its last line prints, 0 failed). Mutant A deletes this branch's predicate, the `first push `BLOCKED.md` with a `Question:` line` sentence of the fixer text: the self-test fails "the fixer is told to push BLOCKED.md with a Question line before stopping on a question". Mutant B deletes origin/main's predicate, the reviewer's `never on a head that is behind main but merges cleanly` clause: it fails "the reviewer blocks on main only for a merge-tree conflict, never a clean head behind main". Each was applied to the merged file, run, and the file restored from a copy.

The closures repair: deleting the one `INERT_EXCEPT` line `"tools/audit/seat/topic_grammar.py",` from `tests/closure.py` at this head and running `python3 tests/closure.py check --in-dir <D> --partial` over the head's `entities.py` recording exits 1 with `closure: files on the INERT list are inside a recorded closure (committed tests/closures.json): tools/audit/seat/topic_grammar.py` (#357's refusal); restored, the same command exits 0. Restore checked with `git diff --quiet` before the next step.

The tick-levels code, each mutated in place at `f641f97bd`, the named self-test run, the file restored (command: /tmp mutation script, one `sed`-equivalent replacement per row):
- orchestrator_tick.py: drop `and not disposed` fails "carry 13"; drop the disposition read in `blocked_stops`, the dispatch comparison (`if newer`), the `_seat_on` BLOCKED.md exclusion, or the family wip read fails "carry 14" / "carry 7" (one check each).
- pr_cap.py: `("record:",)` fails the triage/roster row. open_driver.py: dropping the `SKIP_TOPIC_PREFIXES` test fails both batched rows. owed_unactioned.py: dropping the `OWED <kind> #n` arm raises Unreadable in the self-test.
- topic_grammar.py: counting a bare `-<N>` as a member fails 2 rows; matching by prefix fails 5. cloud_dispatch.py: restoring the unconditional merge sentence fails the first-clean-head row.
- cloud_relay.sh self-test: new rows r10-agreement-bootstrap (not reported), r10-roster-ops and r10-deeplink (reported), r10-quiet (null: reported).

## Null control

The selftest_scope fix: `python3 -I tools/ci/selftest_scope.py static` at origin/main `631ac4df3` prints `106 gated step(s), 0 problem(s)`; at `0942168880c7c1cd0c91e9bdf5bba79b64425aa2` (the merge, before the fix) `106 gated step(s), 1 problem(s)`, the UNGATED line; at this head `107 gated step(s), 0 problem(s)`. Selection, the step's own file against an unrelated one: `python3 -I tools/ci/selftest_scope.py select --change M:tools/audit/seat/topic_grammar.py` prints `  run topic-grammar`, `--change M:docs/x.md` does not (`grep -cx '  run topic-grammar'` reads 1 and 0).

Earlier heads:

The closures repair: at `6327ea346` (the previous head with main merged, before the repair), `PYTHONPATH=tests/hastub ./tests/derive_closures.sh --single tests/entities.py --record-only --out-dir <D>` then `python3 tests/closure.py check --in-dir <D> --partial` exits 1 with the line CI printed: `UNDER-SCOPED: tests/entities.py really reads 1 file(s) the committed closure does not list: tools/audit/seat/topic_grammar.py`. At this head the same check exits 0 (`closure: committed closures cover every file this run touched`) over both that recording and the head's own. `--partial` is the scoped arm's argument; the full arm adds only the roster check, which a one-script recording fails by construction, and the under-approximation comparison is the same code on both arms (`closure.check`'s docstring).

The tick-levels code: at the merge base (5bc009bc8) the same arms read: a body ref with a disposition still owes; a BLOCKED.md tip prints nothing; `noreturn_arm` fires on a seat that returned on `handoff/<topic>-p1`; a triage: title counts toward the cap; the fixer text instructs the merge on a moved main. The null rows above (older-sha disposition, newer dispatch, tip without the file, a family that moved nothing, a production title) keep the old behaviour.

## Figures

At this head (`977fd0033`), origin/main `631ac4df3` read 2026-11-09T13:37:49Z:
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <D>`: `MODE: FULL` (`tests/closure.py changes the gate itself`), so the suite is CI's.
- `python3 -I tools/ci/selftest_scope.py select --base 631ac4df3`: `MODE: FULL` (a gate file changed: `.github/workflows/governance.yml`, `tools/ci/selftest_closures.json`), and its list carries `  run topic-grammar`, so the step runs on this diff.
- `python3 -I tools/ci/selftest_scope.py static`: 0 problem(s); `python3 -I tools/ci/selftest_scope.py --self-test`: 0 failed.
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`, `python3 tools/audit/seat/topic_grammar.py --self-test`, `python3 -I tools/audit/seat/owed_unactioned.py --self-test`, `python3 -I tools/audit/seat/open_driver.py --self-test`, `python3 tools/audit/seat/pr_cap.py --self-test`, `python3 tools/audit/seat/cloud_dispatch.py --self-test`, `python3 tools/audit/seat/ledger.py --self-test`, `bash tools/audit/seat/cloud_relay.sh --self-test`, `python3 tests/closure.py selftest`: each exits 0, 0 failed on its last line.
- `python3 tools/audit/fold_ledger.py check`: 0 violations.
- `governance / instrument-self-tests` green on this head is CI's to show once the head reaches the pull request; it is not claimed here.

Earlier heads:
- `python3 tests/closure.py check --in-dir <D> --partial`: exit 1 at `6327ea346` and exit 0 at this head, over a recording `./tests/derive_closures.sh --single tests/entities.py --record-only --out-dir <D>` took on this Linux container; the mutation above exits 1.
- `./tests/derive_closures.sh --single tests/entities.py`: the closure gains `tools/audit/seat/topic_grammar.py` and nothing else; the run before the repair and the run after differ in `files` by `tests/golden/card_claimed_drift.txt` alone (the run after did not open it; merge keeps it, over-scoped and safe).
- `tests/entities.py`, run by that recording at `31efd7b94`: its result line reads all checks passed. The first `--single` run after the `INERT_EXCEPT` edit failed one check alone, the orphan check (`these force the FULL suite when touched: tools/audit/seat/topic_grammar.py`), because the table did not yet list the file; it was merged with `merge --partial --allow-failures` after its FAIL lines were diffed against the run before the repair, and the second run, on the committed table, passed.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <D>`: `MODE: FULL` (`tests/closure.py changes the gate itself`), so the suite is CI's.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED at this head.
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: all checks pass at `f641f97bd`.
- `python3 tools/audit/seat/topic_grammar.py --self-test`, `python3 -I tools/audit/seat/owed_unactioned.py --self-test`, `python3 -I tools/audit/seat/open_driver.py --self-test`, `python3 tools/audit/seat/pr_cap.py --self-test`, `python3 tools/audit/seat/cloud_dispatch.py --self-test`, `python3 tools/audit/seat/ledger.py --self-test`, `bash tools/audit/seat/cloud_relay.sh --self-test`: pass at `f641f97bd`.
- `python3 tools/audit/fold_ledger.py check`: 0 violations at `f641f97bd`.
- Diff-mutant run (`tools/audit/seat/mutant_run.py --diff <base>...HEAD --max-mutants 40`, MUTANT_CMD the five tick/opener/cap/grammar self-tests named in the line above, chained with `&&`) at `f641f97bd`: wall time 4m24s, 20 survivors (listed under Unpinned sites).

## Unpinned sites

The closures repair adds no predicate (one list entry and the recorded table). The tick-levels code's 20 survivors, each dispositioned:
- cloud_dispatch.py:1056-1058 (4), open_driver_selftest.py:154-158 (4), open_driver.py:256 (1): mutations of test-side `find` bounds and `pass` call-deletes in the self-test lines themselves; the production predicates they test are killed by the mutation proof above. Value checks, no pin owed.
- orchestrator_tick.py:866 (`age <= SEAT_WINDOW_MIN` boundary): a minute-boundary value, same class as the existing window arms; not pinned.
- orchestrator_tick.py:933-947 (`_dispatch_newer`'s failed-read arms and its equal-timestamp edge, 12): the read-failure arms return None (the caller names it UNREADABLE) and the strict `>` is the stated rule (a dispatch committed in the same second as the tip is not newer). A tools/ site: mutation-autofix's lane mutates custom_components/ only, so these stay unpinned here and are the disposition-by-triage of this body; no behaviour change is claimed for them.


## Red checks

Only reds in the set `python3 tools/audit/seat/merge_train.py owed-reds --repo tvofi/heatpump_optimizer` prints (read 2026-11-09T13:35Z) are answered here (owner ruling, 2026-11-09). `governance / instrument-self-tests`, the reviewer's block, is not in that set; its cause and fix are under `## Head`. At the pull request head `0942168880c7c1cd0c91e9bdf5bba79b64425aa2` no check in the set had concluded red when read (2026-11-09T13:35Z).

- `tests / closures` and `tests / closures-autofix` again at `8f7ef132540bd70b9b1020f6212b929ae6aebcd1` (closures job 128856975668, run 42519444840: the same `UNDER-SCOPED: tests/entities.py ... tools/audit/seat/topic_grammar.py`; closures-autofix job 128857585863 red in run 42518975323 and skipped in run 42519444840; gate job 128867402310 `FAIL tests / closures`): the same cause as the entry below. The repair commits `8b57a66f4` and `31efd7b94` were on `handoff/r10-tick-levels-p2` only, never on the pull request's branch, because the previous repair's body push did not land; `8f7ef132` does not contain them. This head carries them, so no new repair is owed. Cheaper detector: none beyond the one named below; the miss was a return that did not complete, not a check.
- `pr-contract / pr-contract` (jobs 128861160559 and 128866861693: `check \`tests / closures-autofix\` is red and \`## Red checks\` does not name it`; `FIGURES 10 resolved, 1 not verified`): the pull request still carried the previous body, which named neither; this body names `tests / closures-autofix` and states the diff-mutant command without the inline `bash -c` the figure linter cannot resolve. Cheaper detector: `tools/pr/prepr.sh`'s body check, which runs the same linters offline and ran clean on this body.
- `tests / closures` (UNDER-SCOPED `tests/entities.py`: `tools/audit/seat/topic_grammar.py`, run 42511447807, job 128825445404) and `tests / closures-autofix` (`skip-merge-failed -- THE REPAIR DID NOT HAPPEN`, job 128834461453: its merge of CI's recording refused the file as INERT and read, so no bot commit could land): one cause, repaired in this diff; the autofix job has nothing to repair once `tests / closures` is green. Root-cause answer: a cheaper detector exists and ran: `tools/pr/ci_predict.py` (prepr.sh step 6d, seconds, offline). At `8cd4d4162~1`, before the previous repair, `python3 tools/pr/ci_predict.py --base 5bc009bc8` predicted `tests / closures INERT READS tests/entities.py: tools/audit/seat/topic_grammar.py (a new file beside 43 it lists)`. That is the `inert_siblings` arm, which keys on directory and suffix and cannot tell an in-process import from a child's read. It prescribed `--apply-inert`, which writes only the `inert_reads` entry. The previous head carried that entry (`8cd4d4162`), and CI went UNDER-SCOPED, because an in-process read of an INERT file is filed in `files` too. `--only under-scoped`, the arm that follows new top-level import edges, predicted nothing at the same tree. Process state: the detector existed and was run; its arm mislabelled the class and named a repair that cannot clear it. Countermeasure, not built in this repair (out of its scope): `ci_predict`'s top-level-import arm should predict UNDER-SCOPED with an `INERT_EXCEPT` repair for an INERT target that a closure script's in-process import reaches, and `inert_siblings` should yield to it for the same file. Its standing cost is one arm in a step that already runs. Carried below.
- `governance / wave-script` (AGREEMENT DIVERGENT `finding-class-id "R10-TOPIC-FAMILY"` and the class_guess GRADER line), predicted by `ci_predict.py`: the base's copy of the agreement lane grades an edit to the lane's own enum, so it cannot see the registration this head carries in finding.schema.json and audit-find.js (RCA R10-RCA-2671-WAVE-SCRIPT cause 3); the head's copy has no local repair. No cheaper detector exists: the base-copy grading is the lane's design.
- `pr-contract / pr-contract` at the pull request head `1c29e5ab7733d9c72d1773b649c97291b8b5dfb2` (job 128991793032, run 42554702764): its pr-body step refused a body that left a red outside the owed set unnamed (`PR-BODY: 1 error(s)`); figure lint `18 resolved, 0 not verified, 0 refused`, carry_audit `3 routed, 0 unrouted`. Under the 2026-11-07 ruling `policy_lint.mjs --pr-body` reads only the owed set, so that refusal does not recur on this body. Cheaper detector: `tools/pr/prepr.sh --body-check` (offline, seconds), which body_push.sh runs.
- `gate` at `1c29e5ab`, the aggregate: job 128992861873 prints `FAIL pr-contract / pr-contract: failure (run 42554910265)` and no other context, so its cause is the `pr-contract` entry at `1c29e5ab` above; jobs 128986545477 and 128968140821 print `FAIL run(s) [...] at this head are still being judged; their gate decides`, the aggregate deferring to the later gate, not a check of its own. Cheaper detector: the same as the entry above.

## Forward-carry

- `tools/pr/ci_predict.py` mislabels an in-process top-level import of an INERT file as INERT READS (the `inert_siblings` arm, with no UNDER-SCOPED prediction from the import arm) and prescribes `--apply-inert`, which cannot clear CI's UNDER-SCOPED; evidence: `## Red checks` above, `tests / closures` on this PR at `a9827ca3e`.

  Carry: R10-FLY-CIPREDICT-RESTORING

## Friction

none
