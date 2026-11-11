R10-GH-READ-RESIDUE part 2: Carries 4, 5 and 6 (roster numbering, from 0), and the unbuilt half of Carry 1 (the seat bin dir on the daemons' PATH). Every paged GitHub list read of the merge train walks explicit `page=N` instead of `gh api --paginate`, whose followed Link header a cloud seat's proxy answers 403. `gh_calls.py --top` names an empty window and exits 3. tick_loop's children and every beatd job get the seat bin dir on their PATH. The seat gh shim admits any checkout's committed, unmodified gh_comment.py. Closes none.

## Head

`01164518380caf4c65bd7ee098ebf0a5f23e6bf4` is this PR's head: round 2, one commit on the round-1 head 588d1a4dfe607bc990fb3ced410a1df98005b9cf. Base origin/main is ee64358be7eeccaec5178a923cb3b83a18a924a0 and had not moved; no merge was needed. `tools/pr/prepr.sh` at this head: rc=0, `STRUCTURE RATCHET PASSED`, no budget touched.

Numbering: carries are named 0-based, as the brief asks. Part 1 (#3427) built Carry 0, Carry 2, Carry 3 and Carry 1's tracked-file half; this part builds Carry 1's PATH half and Carries 4, 5 and 6. review_packet counts from 1, so its Carry 2, Carry 3 and Carry 7 are this body's Carry 1, Carry 2 and Carry 6.

- Carry 4: `gh_read.read_pages(read, path, key)` owns the walk: `gh api <path>?per_page=100&page=N --jq .<key>[]`, stop on a short page, refuse past MAX_PAGES, a failed read's code and text verbatim. `Train.pages` runs it under the retried runner. All 12 `--paginate` reads in merge_train.py and queue_pre_flight.py's comments read go through it.
- Carry 5: `gh_calls.top_report` prints `gh_calls: UNATTRIBUTED: ...` and returns rc 3; tick_loop.sh puts the seat bin dir first on PATH once and prints `TICK-GH` when the shim is absent.
- Carry 1 (unbuilt half): `Beat.env` builds the job PATH as `beatd_shims`, then `seat_bin()`, then the beat's own PATH.
- Carry 6: the shim admits a checkout that tracks seat-gh and gh_comment.py with `git diff --quiet HEAD -- tools/pr/gh_comment.py`; every other caller stays denied.

## Round 2 repair

Round 1 was blocked `mutation-vacuous`: the merge_train self-test stubs ignored `--jq`, so `Train.pages` with its key dropped and each call site's key (`check_runs`, `workflow_runs` x2, `jobs`) survived 611/0. This head adds `_jq_checked` in merge_train.py, applied by `Train.__init__` to an injected runner only while `_self_test` has set `_JQ_CHECK`: a paged read (`page=N` in the path) whose `--jq` is not `.<key>[]` for the key the path serves (check-runs: check_runs, `/jobs?`: jobs, `actions/`: workflow_runs) answers rc 1. Production behaviour is unchanged (the flag is false outside the self-test).

Mutants on the self-test (`python3 tools/audit/seat/merge_train.py --self-test`), each restored after:
- Null control, correct keys: `611 checks, 0 failed`.
- `Train.pages` `read_pages(self.run, path, key)` -> `(self.run, path)`: KILLED (the self-test dies on `Stop: ci: the check runs at aaaaaaaaaaaa could not be read`).
- `_check_runs` and the `sha` check-runs read `"check_runs"` -> `"checkruns"`: KILLED (same Stop).
- `bot_head` `"workflow_runs"` -> `"workflow_run"`: KILLED (1 failed).
- `_gate_busy` ci.yml runs `"workflow_runs"` -> `"runs"`: KILLED (7 failed).
- infra re-run `"jobs"` -> `"job"`: KILLED (5 failed).

queue_pre_flight's only paged read is the key-less comments listing (`.[]`), and orchestrator_tick has no `pages`/`read_pages` call, so neither has a keyed read to pin; their stubs are unchanged.

## Mutation proof

Round-1 mutants stand (gh_read short-page and truncation arms, gh_calls `--top` rc 3, tick_loop seat-bin prepend and TICK-GH, the seat-gh t5/t6/t7 arms, beatd `m6_no_seat_bin`, merge_train `_check_runs` reverted to `--paginate`, verdict-comments `if code:`), plus the five above. Survivors from round 1 are unchanged: `MAX_PAGES = 101` (equivalent), test scaffolding, cosmetic `[-160:]` widths, `timeout_s=61`.

## Null control

- Carry 4, finder's harness at both ends: `merge_train.py classify --pr 3427 381b01147f24f36f474c443406b908028ca021f2` (check-runs `total_count` 112) is `REFUSE ci: ... could not be read`, rc 2 at base and `GREEN`, rc 0 at the head; `classify --main ee64358b` stays `WAIT ... pending: gate`, rc 3. The round-2 change is self-test only and does not alter this.
- Carries 5 and 6 null controls as in round 1 (one logged call gives rc 0; a seat bin dir holding the shim prints no TICK-GH; the baked, registered-worktree and clone scripts pass, an untracked, edited or seat-gh-less one is refused).

## Figures

- `python3 tools/audit/seat/merge_train.py --self-test`: `merge_train self-test: 611 checks, 0 failed` at this head.
- `tools/pr/prepr.sh`: `PRE-PR: 01164518380caf4c65bd7ee098ebf0a5f23e6bf4 ... rc=0`.
- The other self-tests (gh_calls 215/0, gh_read 146/0, tick_loop 30/0, beatd 123/0, queue_pre_flight 53/0, orchestrator_tick 312/0) are untouched by this commit, which edits only merge_train.py (22 lines).
- Class enumeration (`git grep -c -e '--paginate' -- tools tests ':!*.md'`): 74 lines in 28 files at base, 66 in 27 at the head; unchanged by round 2.

## Red checks

none

## Forward-carry

- The other instruments' `gh api --paginate` reads (orchestrator_tick.py, proof_watch.py, outside_intake.py, body_patch.sh, bus.sh, app_approve.sh, approve_held_runs.sh, budget_raise_gate.py, replan.py and the rest of the class enumeration) are not converted. Carry: dismissed: the roster branch's R10-GH-READ-RESIDUE-P3 group owns those reads, a group the base roster CI grades against does not yet hold
- The shim, the seat bin dir and tick_loop's prepend help only on a host where `seat_venv.sh --install-shims <$HPO_STATE_DIR/bin>` has run. Carry: dismissed: host install step, now flagged each tick pass by TICK-GH

## Friction

none
