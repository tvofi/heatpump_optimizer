Fix review: blocked 1dbf3f6741e8507556dd5d6e0b6829ae5dc925dd body-stale: this head prints roster_sync 64 checks, 1 failed and R10-TRAIN-OVERLAP-GRADE stage "done --at-sha 4db1d3e28...", while the body claims 0 failed and in-progress
bus-nonce: 90ccced14f4b9fae9b224c60d7fe14af

# Fix review — PR #2878 at `1dbf3f6741e8507556dd5d6e0b6829ae5dc925dd`

Round 3. The last verdict was `blocked body-stale` at `0e370d603`; this reviews the repair at the head the PR now carries. Worktree `~/hpo-seats/r10s6/review-2878-r3/wt`, detached at the head; the main checkout is untouched. Head at publish time is still `1dbf3f674`. Delta since the last reviewed head: `git rev-list --count 0e370d603..1dbf3f674 --not origin/main` = 4 commits, one of them the new `12fd86e13 roster_edit set-stage R10-TRAIN-OVERLAP-GRADE`. Evidence: `~/hpo-seats/r10s6/review-2878-r3/evidence/`.

RESULT blocked body-stale (B1). B2, B3 and B4 pass; the block is the body's own figures against this head, plus the roster value that makes one of them false.

## B1 — the body must describe this head: FAILS

- The commit enumeration now describes this branch: `--no-merges origin/main..b0920b94a` = 27, `..cfacd3800` = 70, their union = 71 (intersection 26), `--no-merges origin/main..HEAD` = 71, and the 27 are exactly the 26 `roster_edit`/`roster_sync` ops in `3b78b44a0`..`a9c7555ad` plus the record `b0920b94a`. That part re-derives.
  Carry: R10-ROSTER-BATCH24
- `roster_sync --self-test` does NOT pass at this head. The head's own command prints `FAIL every stage the tree's rosters carry is classified (derivable or protected) (got: {'done --at-sha 4db1d3e28f0dff50f6916e39d52efed0ce856d0a': 'wave-r10-groups.json'})` and `roster_sync self-test: 64 checks, 1 failed`; the null control at `origin/main` prints `64 checks, 0 failed`, so the failure is this branch's roster. The body (lines 19 and 42) states `64 checks, 0 failed` at the merged tree. `governance / instrument-self-tests` runs exactly that command (`.github/workflows/governance.yml:761`) and greps `^roster_sync self-test: [1-9][0-9]* checks, 0 failed$` (line 762), so the head cannot go green: reproduction is `env -u BASH_ENV python3 -I tools/audit/seat/roster_sync.py --self-test`.
  Carry: R10-ROSTER-BATCH24
- The value behind that failure is `R10-TRAIN-OVERLAP-GRADE resume.stage = "done --at-sha 4db1d3e28f0dff50f6916e39d52efed0ce856d0a"`, not a `roster_lib.STAGES` value (`is_open()` reads it OPEN). The body (line 15) says the group moves to `in-progress`. It arrived in `12fd86e13`, newer than the last reviewed head, and is present on the current roster tip `32b938f3e`; the repair ops for it are still un-marked in `~/hpo-orch/r10s6/s7/roster-queue-s7.txt:35-36`.
  Carry: R10-TRAIN-OVERLAP-GRADE
- The null control's roster blobs do not re-derive. Body line 27 says "this head `cc64745e`, the roster tip `4b136c3e`, the merged tree `adff8318`". Actual: `origin/main` `582f75be3`, roster tip `cfacd3800` `e5cf37ba8` (which the body's own Figures line 40 states), `b0920b94a` `cc64745e`, this head `2740d0909`. `4b136c3e` is `f318f7014` (the previous authored head) and `adff8318` is `0e370d603` (the previous merged head), so both values were carried forward from the head the last verdict reviewed.
  Carry: R10-ROSTER-BATCH24

## B2 — delivery rows: PASSES

- `git diff --stat origin/main...1dbf3f674 -- dev/programme/delivery/` is `dev/programme/delivery/2878.md | 1 +`; the row added is the one line for #2878, and the body claims exactly that one (no flipped rows, no #2866 row).
  Carry: dismissed: no defect found

## B3 — forward-carry: PASSES

- The three append-carry ops the previous body ordered are already present, in this head and on `origin/main`: `82db76ffe`, `d052b8d78`, `2f63ddb60` (merge `72da5ffa1`). The body's `## Forward-carry` says `none`, which matches; the un-marked queue lines are the next lane's pending work, not carries this body owes.
  Carry: dismissed: no defect found

## B4 — R10-REVIEW-CARRY: PASSES

- The body cites the owner's ruling verbatim — "if there are no code changes, the previous review can be carried" — and names the group; the group's own `carry[0]` carries the same words.
  Carry: R10-REVIEW-CARRY
- Registration holds: `roster_edit.py --self-test` prints `124 checks, 0 failed`; `roster_edit.dump(load(file))` reproduces the file bytes exactly; 212 groups, 212 unique names; `after: []` and `files` (`fix-review.md`, `orchestrator.md`, `tools/audit/seat/`) are well formed; `brief_lint` prints `TOTAL: 0 error(s)`. `resume.stage: fixing` with `next_step` describing the helper and the two contract sentences — work to be done, not claimed done, which is correct for a policy group at `fixing`.
  Carry: R10-REVIEW-CARRY

## The three backwards rows

- `R10-DIAG-AGES` fixing→in-progress: explained — its fixer is blocked; the body says in-progress, and the head agrees.
  Carry: R10-DIAG-AGES
- `R10-FLOW-BOARD` not-started→in-progress: explained — `roster_lib.STAGES` places `in-progress` after `not-started`, so only a ranking that omits `in-progress` reads the move backwards. Head and body agree.
  Carry: R10-FLOW-BOARD
- `R10-RCA-BODY-LINT` done→fixing: the reopen is the documented route (`~/hpo-orch/r10s6/s7/roster-queue-s7.txt:24`), but the append it was opened for is absent — 0 carries, and the b39-P208 text ("Check the body's `## Head` before the expensive steps") is nowhere in the roster (`grep -c P208` = 0) though the queue marks that op `#done`. The group is left at `fixing` for a carry that never landed. A finding for this group, not a block on this PR.
  Carry: R10-RCA-BODY-LINT

## Arms run

- `bash tools/pr/prepr.sh --body-check ~/hpo-seats/r10s6/review-2878-r3/body.md`: `pr-body ok: PR-BODY: 0 error(s)`, `carry ok: 1 routed, 0 unrouted, 0 bad destination(s)`, `preflight ok`. Not run, per the brief's cost discipline and because the diff is roster data only: full `prepr.sh`, the gate, the mutation table, `env_drift`, `card_drift`.
  Carry: dismissed: no defect found

## Could not establish

- `governance / instrument-self-tests` and six other jobs were still `in_progress`/`queued` at publish, so I reproduced that job's own command locally rather than citing its conclusion; I did not wait for the run to conclude.
  Carry: dismissed: measurement incomplete
