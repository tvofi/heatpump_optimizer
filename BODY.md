R10-GH-READ-RESIDUE part 2: Carries 4, 5 and 6 (roster numbering, from 0), and the unbuilt half of Carry 1 (the seat bin dir on the daemons' PATH). Every paged GitHub list read of the merge train walks explicit `page=N` instead of `gh api --paginate`, whose followed Link header a cloud seat's proxy answers 403. `gh_calls.py --top` names an empty window and exits 3. tick_loop's children and every beatd job, the opener driver among them, get the seat bin dir on their PATH. The seat gh shim admits any checkout's committed, unmodified gh_comment.py. Closes none.

## Head

Head measured: 1820d2d5032feab77489eb6cb5f43a5b4aebcb2a, on origin/main f24d107bd7aa170bea7419251a4b7f4f48b732f6 (2026-11-11T10:42:03Z). Merge base 45a8b828a41f8a284e73bc0c12ddb87a0370f706; nothing merged since.

- Carry 4: `gh_read.read_pages(read, path, key)` (tools/audit/seat/gh_read.py) owns the walk. It asks `gh api <path>?per_page=100&page=N --jq .<key>[]`, stops on a short page, refuses past MAX_PAGES rather than truncating, and returns a failed read's code and text verbatim. `Train.pages` runs it under the train's retried runner, so the read rule's transient retry holds per page. All 12 `--paginate` reads in merge_train.py go through it: check-runs, both workflow-run listings, ci.yml runs, jobs, reviews and comments. So does queue_pre_flight.py's `findings_gate` comments read, which the train runs. The four reads the carry names alone would leave the same 403 on the reviews and record-issue comment reads, so all 12 were converted. `runs_approved` now takes the run dicts instead of TSV.
- Carry 5: `gh_calls.top_report` prints `gh_calls: UNATTRIBUTED: no call logged since <since>; gh on PATH is <path|none> (<shim|not the shim>)` and returns rc 3. tick_loop.sh puts `${HPO_STATE_DIR:-~/.local/state/hpo}/bin` first on the exported PATH once, which a restart's exec does not repeat. Each pass whose `command -v gh` lacks the shim marker prints one `TICK-GH <utc> gh=<path|none>: not the seat gh shim ...` line.
- Carry 1 (unbuilt half): tick_loop covers orchestrator_tick.py and cloud_relay.sh, which are its children. The opener driver runs as a beatd job, so `Beat.env` builds the job PATH as `beatd_shims`, then `seat_bin()`, then the beat's own PATH. The git shim stays first, and the real git is still resolved before any prepend.
- Carry 6: the shim's second-tree admit was part 1's "a worktree git registers beside the baked tree, script tracked". It is now a rule with three predicates, all required: <root> tracks tools/audit/seat/shims/seat-gh (a checkout of this repository), tracks tools/pr/gh_comment.py, and `git diff --quiet HEAD -- tools/pr/gh_comment.py` holds. The baked gcpy stays the fast path, and every other caller is still denied by default. Part 1's registration test was dropped: carry 6 admits any checkout of this repository, and the registration added no safety the clean-and-tracked predicates lack. A registered worktree with a local edit passed under part 1 and is refused now (t6's predicate).

## Mutation proof

Hand mutants, each run on the owning self-test and then restored:
- gh_read `if len(page) < per_page:  # mut:short-page` -> `if False:`: gh_read self-test 4 failed, including "null control: a one-page (short) answer makes exactly one read"; -> `if True:`: 4 failed, including "a three-page answer reads every item".
- gh_calls `if top(lines, since, limit)[3]:` -> `if True:`: 5 failed, including "an empty log with a non-shim gh first: rc 3 and the UNATTRIBUTED line naming it".
- tick_loop `# mut:seatbin` prepend dropped: 4 failed, including "the tick's child PATH starts with the seat bin dir"; the TICK-GH printf made `true`: 1 failed ("a seat bin dir with no gh shim: one TICK-GH flag line").
- seat-gh: three in-tree mutant arms in `gh_calls.py --self-test`, all killed, each turning the stated null control to rc 7: the tracked-file predicate dropped (t5), the unmodified predicate dropped (t6), and the seat-gh `--error-unmatch` removed (t7).
- beatd: the in-tree mutant `m6_no_seat_bin` turns (6b) "job PATH: beatd_shims, then $HPO_STATE_DIR/bin" red (`beatd.py --self-test`, 123 checks, 0 failed).
- merge_train, `mutant_run.py --spec` with the null mutant first (SURVIVED NULL): `_check_runs` reverted to `--paginate` is KILLED; the verdict-comments `if code:` -> `if False:` is KILLED (the new "its comments could not be read" admit_add arm).

`mutant_run.py --diff 45a8b828a41f8a284e73bc0c12ddb87a0370f706...HEAD --path <file> --cmd '<that file's self-test>'` was run per file. The gh_read pass was re-run after the test tightening; the other passes are from the commit before it, and that commit's only production-adjacent change is the queue/verdict arm named above. Every survivor and its disposition:
- gh_read.py:213 `MAX_PAGES = 101`: equivalent. The bound's contract is to refuse rather than truncate, and the refusal is driven with `max_pages=3`; any value keeps it. PER_PAGE is now pinned ("by default a page is GitHub's maximum, 100").
- gh_read.py self-test lines (the `server` stub's 403 trap for `--paginate`/`repositories/` and its `--jq` guard; the CONST_SWAP/CALL_DEL on its own arms): test scaffolding. The 403 trap is meant never to fire on a passing tree. A `check(...)` deleted by CALL_DEL survives by construction.
- gh_calls.py:109 `return False` on OSError in `first_gh_is_shim`: moved verbatim from the pre-existing function into the `first_gh` split, and unreachable for a regular file the test can create. gh_calls.py self-test lines 616-785 (`check=False` on fixture git calls, limit 10->11, `timeout=61`, CALL_DEL of `check`): equivalent or test scaffolding.
- merge_train.py `[-160:]` -> `[-161:]` on three Stop texts: cosmetic truncation, the same width as before. Self-test fixture CONST_SWAPs (stub rc 0->1 on rows whose expectation does not read the rc, and the `_jl` helper's RETURN_DEL): test scaffolding.
- beatd.py:976 `timeout_s=61`: equivalent.
- queue_pre_flight.py: 0 survivors.

## Null control

- Carry 4, finder's harness at both ends, live in this cloud seat: `merge_train.py classify --pr 3427 381b01147f24f36f474c443406b908028ca021f2` (check-runs `total_count` 112, more than one page). At base 45a8b828 it gives `REFUSE ci: the check runs at 381b01147f24 could not be read`, rc 2. At the head it gives `GREEN ... pending: none red: none`, rc 0. Null control: `classify --main 45a8b828a41f8a284e73bc0c12ddb87a0370f706` (`total_count` 44, one page) gives `WAIT ... pending: gate`, rc 3, identically at base and head. That shows the base failure was the second page.
- Carry 4 self-test: a one-page answer makes one read. A stub that 403s any `--paginate` or `repositories/` URL still yields every item of a 2+2+1 walk in 3 reads. A full last page ends on the empty page after it.
- Carry 5: one logged call in the window gives rc 0 and exactly `render_top`'s tables. A seat bin dir holding the shim prints no TICK-GH line (the existing one-banner rows stay green). A PATH already led by the seat bin dir is not prepended twice.
- Carry 6: the baked tree's script, a registered worktree's clean script and a clone's clean script pass (rc 7, the stub gh). An untracked file outside any checkout (t4), an untracked script in a checkout (t5), a local edit (t6) and a clean tracked script in a repository without seat-gh (t7) are refused (rc 1). Part 1's spoof, basename and symlink arms are unchanged and green.

## Figures

Each command below printed its line at head 1820d2d5032feab77489eb6cb5f43a5b4aebcb2a:
- `python3 tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 611 checks, 0 failed`
- `python3 -I tools/audit/seat/gh_calls.py --self-test`: `gh_calls self-test: 215 checks, 0 failed`
- `python3 -c 'import sys; sys.path.insert(0,"tools/audit/seat"); import gh_read; sys.exit(gh_read.self_test())'`: `gh_read self-test: 146 checks, 0 failed`; `python3 tools/audit/seat/record_row.py --self-test` (which runs it in CI): all checks passed
- `bash tools/audit/seat/tick_loop.sh --self-test`: `tick_loop self-test: 30 checks, 0 failed`
- `python3 -I tools/audit/seat/beatd.py --self-test`: `beatd self-test: 123 checks, 0 failed`
- `python3 tools/audit/seat/queue_pre_flight.py --self-test`: `queue_pre_flight self-test: 53 checks, 0 failed`
- merge_train's importers: `orchestrator_tick.py --self-test` 308/0 (it was 2 failed before its pulls/<n>/reviews stub answered the paged read), `proof_watch.py` 47/0, `probe_bridge.py` 8/0, `review_packet.py` 94/0
- Agreement lane: `python3 -I tools/policy/agreement_py.py --out <f>` then `node tools/policy/agreement.mjs --py-json <f>`: `RESULT divergent=0 unregistered=0 dead=0 refused=0`. Before agreement_py's reviews stub answered the paged read (`""`, no review, in place of `[[]]`), the budget-raise pair read 43 divergent: `Train.raise_hold` stopped on `'list' object has no attribute 'get'`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 1 script(s) run`, which was `tests/entities.py`.
- Structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`; no budget was raised or re-recorded.
- Class enumeration (fixer step 8): `git grep -c -e '--paginate' -- tools tests ':!*.md'` returned 74 lines in 28 files at base and 66 in 27 at the head. The merge-train family (merge_train.py, queue_pre_flight.py) is closed: its remaining matches are docstring and self-test text only. The other files' reads are a distinct seam, dispositioned under Forward-carry.

## Red checks

none

## Forward-carry

- The other instruments' `gh api --paginate` reads (orchestrator_tick.py, proof_watch.py, outside_intake.py, body_patch.sh, bus.sh, app_approve.sh, approve_held_runs.sh, budget_raise_gate.py, replan.py and the rest the class enumeration in Figures lists) are not converted. In a cloud seat each refuses the same way once a list passes one page. `gh_read.read_pages` is the reader to convert them onto. Carry: dismissed: the roster branch's R10-GH-READ-RESIDUE-P3 group owns those reads, a group the base roster CI grades against does not yet hold
- The shim, the seat bin dir and tick_loop's prepend help only on a host where `seat_venv.sh --install-shims <$HPO_STATE_DIR/bin>` has run. The 2026-11-11 instance had no gh in the seat bin dir. From this head, the tick loop prints TICK-GH on every such pass and `gh_calls.py --top` exits 3, so the omission is visible and no longer silent. Installing the shim is a host action outside the tree. Carry: dismissed: host install step, now flagged each tick pass by TICK-GH

## Friction

none
