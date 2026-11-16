R11-PRE-PARALLEL-PIPELINE part 1 of 3: carries 0-4 of the group's brief, under the approved design (`Design review: approve a21ad55901b20369a6540abdd4793f29e3eae8bb`). Carry 4 is dismissed as fixed at base (design item c4); carries 0-3 are built here.

- **Carry 3, TRAIN-WAIT-CAP-OUTAGE.** `Train.review_settle` and `Train.rejoin` count a poll toward `wait_cap_s` only through `Train.counted_poll`: the poll read its own listing, and `Train.actions_mark` moved since the previous poll. The stall signal is `actions_mark`: the newest `updated_at` among completed runs of `repos/<repo>/actions/runs?per_page=30` (one listing); two polls reading the same value mean no run in the repository completed between them. Its cost: one extra listing per poll, made only on a poll that read its own listing and found a run still open (review wait), or once per rejoin round shared by every waiting entry; an unread poll makes no extra call. An uncounted poll neither ends the wait nor counts toward the cap. The poll grain still steps from the 5-s grain to POLL_SECONDS by poll count, so an outage polls at POLL_SECONDS, not every 5 s.
- **Carry 2, the three gate-reader residuals.** (a) `orchestrator_tick.py`'s board state line in `Tick.one_pr` and the THROUGHPUT STALL in `Tick.replan` read GREEN from `Tick._classify_reading` (merge_train's `classify_at`) over the required contexts; every lane concluded green while a required context has no run is now `WAIT:<name>`, and with the ruleset unreadable `UNJUDGED`, never GREEN. (b) `Train._gate_busy` returns None on an unreadable ci.yml listing instead of minting an empty `Busy` from runs it did not read, and leaves `BUSY_MINTERS`; `Train.wait_ci` keeps its FINAL reading when no deferral reading exists. (c) `blind_sites` finds the barrier's direct spellings (a `classify(.., FINAL)` outside `FINAL_READERS`, an empty `Busy()` outside `BUSY_MINTERS`) in every module under tools/ naming merge_train, in the self-test, so CI refuses them on the pull request instead of a train at run time. The run-time barrier stays, for the alias/getattr/partial spellings a scan cannot see.
- **Carry 1, P628 pre-approval.** `Train.pre_approve`, called by `Train._batch` after any up-front recarry, posts step 6's approval at batch start for each serial entry that lands after another entry and passes `Train.pre_approval_refusal` (verdicted; live head; main inside, or a ruleset requiring no up-to-date branch so Card 5's `merges_as_is` lands it unmoved; `classify_at` GREEN; CARRY yes; no policy path; no budget raise). `approve` is once per head, so the entry's turn posts nothing; a moved head is approved afresh. Departure from the carry's step list, named: "main inside" is read as "the head will not move before its merge", because under Card 5 a head lacking main lands unmoved when `strict_update()` is False; a strict ruleset keeps the literal reading. Policy heads are left to step 6 whole, since their approval is `policy_approve`'s at the merge. The batch entries were already approved at admission (P86), so only serial entries change (design item v3).
- **Carry 0, the C9 benchmark.** `merge_throughput.py flow --bench-green <json> --bench-since <iso> --train-log <file>` prints, per landing path (train when the train log records the merge's `#N MERGED <sha>` line, else chain), the count, median merge wait in minutes from the later of the merge verdict and the recorded GREEN instant to the merge commit, wrong merges (a merge whose newest bus verdict before it is not a merge verdict) and refusals (the train log's SKIP lines; the chains log none in the tree), and the decision under the rule fixed before data in `BENCH_MIN_PRS` and `BENCH_MARGIN`. `flow_merge_wait` rows gain `verdict_at` and `wrong`; no third bus parser. The GREEN instants are an input file the benchmark's seat records: this script makes no network read, as its docstring states.

Alternatives not taken: carry 3's stall read from the review-run listing alone (it cannot tell a stalled Actions from one slow run); counting the grain by counted polls (an outage would poll every 5 s for its whole length); carry 2(a) deleting `Tick.judge` (it still feeds the lane-level running/red lists and the nonstandard-conclusion lines, which classify does not produce); carry 1 pre-approving every serial entry (a strict ruleset's recarry moves the head and wastes the review run).

## Head

`2abb0ac85babec8f3cab4d42d6988d747cfca737` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.

e8a22608613b8af93d0e7a17574c0d594d0e7812 (code), on origin/main 030a4d377f9f26f5b8befe5721d86aea454f29e0, 2026-11-16T13:45:57Z.

## Mutation proof

Each mutant applied to the head by an exact-string replacement, its self-test run, the file restored:

- `counted_poll`: delete `if not readable: return False` -> FAIL `TRAIN-WAIT-CAP-OUTAGE (1): five polls that cannot read the listing leave waited at its start value ...` (the carry's mutant: counting the failed poll turns the first arm red).
- `counted_poll`: `moved = True` -> FAIL `TRAIN-WAIT-CAP-OUTAGE (2) ...`, FAIL `TRAIN-WAIT-CAP-OUTAGE, the rejoin ...`.
- `review_settle`: `if not open_: return` (an unread poll ends the wait, base behaviour) -> FAIL `TRAIN-WAIT-CAP-OUTAGE (1) ...`.
- `rejoin`: `if runs is None or not counted:` -> `if False:` -> FAIL `TRAIN-WAIT-CAP-OUTAGE, the rejoin ...`.
- `Tick.one_pr`: `"GREEN" if True` -> FAIL `carry 2 one_pr state line: a required context with no run reads WAIT`.
- `Tick.replan`: stall gate back to `self.judge` -> FAIL `carry 2 throughput stall: a required context with no run is no stall`.
- `_gate_busy`: `return Busy()` on the unread listing -> FAIL `carry 2 (c): no module under tools/ naming merge_train holds ...` naming `Train._gate_busy Busy()`, then BlindRead at run time.
- `blind_sites`: the FINAL arm `if False:` -> FAIL `carry 2 (c): a planted direct FINAL read ... found by the scan`.
- `pre_approve`: `for a in []:` (dropping the pre-approval) -> FAIL `P628 (i)`, `P628 (iii)`, `P628 (iv)`, `REJOIN (a), serial`, `P628 (vi)`.
- `pre_approval_refusal`: the CARRY check `if False:` (pre-approving a CARRY-no entry) -> FAIL `P628 (iii)`.
- `_batch`: the `pre_approve` call replaced by a no-op -> FAIL `REJOIN (a), serial`, `P628 (vi)`.
- `flow_merge_wait`: `"wrong": False` -> FAIL `carry 0: a merge after a newer blocked verdict is a WRONG merge`.
- `BENCH_MARGIN = 0.4`, and the margin's `<` as `<=` (prepr's diff mutants) -> FAIL `carry 0 bench: chains 25% below the train clear the 20% margin; exactly 20% below does not`.
- `merge_wait_bench`: margin dropped -> FAIL `carry 0 bench null: chains only 15% below the train are retired`; GREEN start dropped -> FAIL `carry 0 bench: the wait starts at the later of verdict and GREEN ...`; minimum count dropped -> FAIL `carry 0 bench null: nine pull requests each are retired`.

## Null control

- Carry 3: `TRAIN-WAIT-CAP-OUTAGE null`: reads succeeding and Actions moving with a run still queued, the cap expires as at base (3 fast + 3 slow reads, no line not counted); the existing P331 and REJOIN null controls pass unchanged.
- Carry 2: `carry 2 one_pr state line: null` (every required context green reads GREEN); `carry 2 throughput stall: null` (verdicted, green, no train, main idle 2 h: STALL raised); `carry 2 (c) null` (registered frames and a non-empty Busy are not found).
- Carry 1: `P628 (iv) null`: a one-entry batch reads and posts nothing at batch start, so its call order is main's.
- Carry 0: the train's own rows in the same window are the chains' null (`merge_wait_bench`); `carry 0 bench null` arms for a 15% margin and for nine pull requests each.

## Figures

- merge_train self-test at base 030a4d377f: 825 checks, 0 failed; at the head: 838 checks, 0 failed (`python3 tools/audit/seat/merge_train.py --self-test`).
- orchestrator_tick self-test at the head: 372 checks, 0 failed (`python3 tools/audit/seat/orchestrator_tick.py --self-test`).
- merge_throughput self-test at the head: ok (`python3 tools/audit/merge_throughput.py --self-test`).
- Step 8, the class "a reader declaring a required conclusion without classify": enumerator `git grep -n "run_state(" -- 'tools/*.py'` outside merge_train.py returns one site, `Tick.judge`; its callers by `git grep -n "self.judge(" -- tools/audit/seat/orchestrator_tick.py`: `Tick.one_pr` (GREEN now `classify_at`'s: closed here), `Tick.main` (the required verdict `req_bad` is already `_classify_reading`'s while the ruleset reads; the lane count is display: already guarded). The stall's call in `Tick.replan` is gone (closed here). The direct `classify(.., FINAL)` and empty `Busy()` sites: enumerator `blind_sites` over every module under tools/ naming merge_train, printed by the self-test row `carry 2 (c)` (27 modules, none found).
- Finder harness: none exists for carries 0-3 (they are carried instrument findings with self-test acceptance); the acceptance arms above are the harness at both ends: each new arm fails at base by construction (the function or behaviour it reads is absent there) and passes at the head.
- Carry 1 (vi): the #3453/#3447 train.log is session-local under `$HPO_STATE_DIR` and not reachable from this seat, so (vi) is the ordering replay in the batch fixture (`P628 (vi)`): the serial entry's approval line precedes the batch entry's merge, and its turn posts nothing. The 13:38:09Z timestamps are not re-measured here.
- Machinery ratchet (design item n-d): `python3 tools/audit/machinery_ratchet.py --check` at the head passes, nonproduction_merges within cap + band; the literal is that command's output, a function of main's window, and moves with each merge.
- Structure ratchet: `python3 tests/structure.py` at the head: STRUCTURE RATCHET PASSED. Scoped gate: tests/doc_claims.py (410 checks) and tests/entities.py (2723 checks) pass at the head (`python3 tests/closure.py select`'s scope.run).
<!-- figure-block: scope-line mb=6f422812d5d8b918beace0283419c153f6df66ce head=2abb0ac85babec8f3cab4d42d6988d747cfca737 -->
~~~text
MODE: SCOPED -- 2 script(s) run, 31 scoped out.
~~~
<!-- /figure-block -->

## Unpinned sites

prepr.sh step 6d drew 40 mutants of the diff's added lines (MUTANT_CMD: the three self-tests, in place); after the margin arm above, these survive, each with its disposition:

- tools/audit/merge_throughput.py `_bench_self_test`'s fixture constants (the `t0` year, the planted `wrong` row index, the row number bases, `run(18, 20)`, `run(2, 20, n=9)`, `run(2, 20, wrong=True)`, `{101: t0}`): equivalent mutants -- each swap leaves the property the arm asserts true (another instant, another row marked wrong, chains 10% below still retired, one matched row of equal wait).
- tools/audit/merge_throughput.py `self_test`'s `_bench_self_test(check)` call deleted: a self-test cannot read its own arm's removal; the arms' names are in the self-test output a reviewer runs.
- tools/audit/merge_throughput.py `flow_merge_wait`'s `seen` filter `<=` as `<`: equivalent at the bus's one-second resolution except a verdict sharing the merge's committer second; kept identical to the existing `before` filter (`v[1] <= move["t"]`) so the wait's verdict and the wrong-merge reading read the same set.

## Red checks

- `tests / closures` (predicted by `tools/pr/ci_predict.py` at this head, UNDER-SCOPED, not yet a check run): tests/entities.py's recorded closure lacks tools/audit/seat/owed_unactioned.py, which orchestrator_tick.py's self-test reads in the child `closure._exec_record` records. The local repair `tests/derive_closures.sh --single tests/entities.py` (exit 0) records the same 578-file closure and leaves tests/closures.json byte-identical, so the read is CI's recording to make; closures-autofix records it on the pull request (ci-autofix.md). Cheaper detector: this prediction, run by prepr.sh before the handoff; none further is owed.

## Forward-carry

- Lands in dev/programme/rosters/wave-r10-groups.json, R11-PRE-PARALLEL-PIPELINE's brief, for the later TRAIN-ROUTING part (part 2 or 3): carry 1's precondition: a serial entry is worth pre-approving only if its head will not move before its merge; under a strict ruleset every serial entry behind a merge recarries, so the pre-approval pays only under `strict_update()` False or a head already containing main. Measured by `P628 (vi)` and `pre_approval_refusal`'s main-inside arm. Carry: R11-PRE-PARALLEL-PIPELINE
- Lands in dev/programme/rosters/wave-r10-groups.json, R11-PRE-PARALLEL-PIPELINE's brief, for the SHADOW part: carry 0 needs a recorder of GREEN instants (`{pr: iso}`) during the shadow; this part adds the reader only. Carry: R11-PRE-PARALLEL-PIPELINE

## Friction

none

