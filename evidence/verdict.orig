Fix review: blocked 22803f99bd8be29012a668ef22140dd12ae3aa5e carry-missing: not carried to the post-merge state-docs beat restart: its only destination is R10-TICK-DRIVERS.carry, and that group is resume.stage done (merged as #2390, a96f4be4a), which finding-propagation.md says is not a destination

bus-nonce: 2d07a42ae308f37da81a612d9d64244f

**Round 7.** This is the seventh `Fix review:` verdict on #2406. Rounds 1 to 6 blocked at `a7d97f55b`, `89d2b9465`, `af391637b`, `b965c4ab9`, `d1becac2b` and `2d9f20009`.

I reviewed from a detached worktree at `22803f99bd8be29012a668ef22140dd12ae3aa5e` (`ev/HEAD`). `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` was empty, so my copy of the contract is current. origin/main is `06c6f3cf2`, which is also the merge base.

## Why it is blocked: the forward-carry has no live destination (step 10)

The body's `## Forward-carry` names `R10-TICK-DRIVERS` as the destination of the beat restart. The restart is to run after this PR merges, on main's code, with no `--roster-ref` and no `--watch-ref refs/heads/main`. Its control is two SHAs in the memo, plus a roster-only commit regenerating the plan within one beat.

On `origin/handoff/audit-r10-roster` at `6c891ee6e` (`ev/carry.txt`):
- The carry text and its control are present in `R10-TICK-DRIVERS.carry`.
- That group is `resume.stage: "done"`, `commit: a96f4be4ac0a`, which is the merge of #2390 into main. #2390 is in this head through the main merge `06c6f3cf2`.
- `git grep` over both the roster branch and origin/main finds the restart nowhere else. That covers every other group's `carry` and `dev/programme/carries/`.

`finding-propagation.md` (lines 69-72): "A group at `resume.stage: done` is not a destination: nothing dispatches or lints it." So since #2390 merged this round, the beat restart has no destination a later seat reads. Without the restart, this PR's beat change does nothing on the live box (round 2 found this, and it still holds).

**Remedy: a roster or carry-file edit, with no code change.** Move the carry to a group that has not started, or to a `dev/programme/carries/carry-<N>.json` (N being the issue that receives it). Keep the control. Then re-name the destination in `## Forward-carry`. While you are there, drop the second `From R10-ROSTER-FASTPATH (#2406)` item (the CodeQL delegation) from the done group: this PR did that work, and MB17 pins it. The head does not need to move, so every measurement below carries.

## The resolution delta of the orchestrator's main merge (`22803f99b`)

- **The graph** (`ev/merges.txt`):
  - `22803f99b` has parents `82095a68d` and `06c6f3cf2`.
  - `82095a68d` has parents `2d9f20009` (round 6's head) and `26b148e5b`, and its tree equals `26b148e5b`'s.
  - `26b148e5b` has parents `2d9f20009` and `b87e8f19b`.
  - This matches the body's `## Head`.
- **No merge was resolved by hand.** Every merge on the first-parent chain from `b87e8f19b`, `22803f99b` and `82095a68d` included, has a tree equal to `git merge-tree --write-tree` of its parents.
- **No conflict with main.** `git merge-tree --write-tree origin/main(06c6f3cf2) 22803f99b` returns rc 0 (`ev/merge-tree.txt`).
- **Files both sides touched** (`ev/main-merge-delta.txt`, `ev/shared-files.diff`): `tests/closures.json`, `tools/audit/seat/INSTRUMENTS.md` and `tools/pr/prepr.sh`. All three auto-merged in disjoint regions:
  - closures: main added an `r10_tick_drivers.py` list entry, and this PR changed the `card.mjs` closure and two timings;
  - INSTRUMENTS: main changed the `fold_ledger` and `body_push` entries, and this PR changed `roster_lib` and the beat;
  - prepr.sh: main added a self-test arm for `body_push`/`ci_predict` at about line 2087, and this PR added `--no-renames` at four call sites.
- **Does #2390's prepr.sh/body_push.sh change move a figure? No.** The census stays clean after #2390 adds `tools/audit/seat/body_push.sh` and `tools/pr/ci_predict.py`, both under `RENAME_SITES`:
  - `closure.rename_sites()` returns `([], [])`;
  - `ci_predict.py:267,312` already pass `--no-renames`;
  - `bash tools/pr/prepr.sh --self-test` prints `290 passed, 0 failed`. The `AssertionError: queue-base` above that line is a planted arm's output, and the total separates it.
- **The body's `comm -12` claim** (`ev/body-comm.txt`) re-derives to `tools/policy/policy_lint.mjs` alone.

## Mutation proof, re-run at this head (step 1; `ev/mutants.txt`)

Each mutant was a single-line edit in a second worktree, restored afterwards (`git status` empty).

- **MP** (`--no-renames` dropped at `tests/closure.py:2763`):
  - closure selftest: `3 of 124 ... FAILED` (both sides of the rename, the 0-script scope, the census);
  - lane_skip: `51/54`;
  - codeql_scope: `47 checks, 2 failed`.
  - All three match the body.
- **MB19** (the flag dropped at `policy_lint.mjs:2356`, `mergeRecordClass`'s real call): `policy_lint` exits 1 with `FIXTURE VACUOUS: recordClassPaths`, and `rename_sites()` names `tools/policy/policy_lint.mjs:2356`. I re-ran this one because main's `policy_lint.mjs` came in with `b87e8f19b`. It matches.
- **MB15** (the flag dropped at `stamp.py:1708`): `policy_lint` exits 1 with `FIXTURE VACUOUS`, and `rename_sites()` names `tools/release/stamp.py:1708`. It matches.
- **M1, M3 and MS**: not re-run. `tests/entities.py` and the closure census code are byte-identical to round 6's `2d9f20009` in this PR's regions, and round 6 reproduced all three. The unmutated head passes (below).
- **M2**: not re-run, and disclosed as unpinned. The disclosure is accurate.

## Body figures re-taken at this head (`ev/figures-head.txt`, `ev/entities-head.txt`)

The body took its figures at `26b148e5b`. At `22803f99b` each matches:

| check | result at the head |
|---|---|
| `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` | `ALL 2349 ENTITY CHECKS PASSED` |
| closure selftest | `ALL 124 closure shrink pins PASSED` |
| `closure.rename_sites()` | `([], [])` |
| lane_skip | `54/54 pins passed` |
| codeql_scope `-I` | `47 checks, 0 failed` |
| roster_lib | `18 checks, 0 failed` |
| orchestrator_tick | `104 checks, 0 failed` |
| state_docs | `all checks passed` |
| stamp | `RESULT stamp_self_test=pass` |
| policy_lint | `TOTAL: 0 error(s) across 41 policy file(s)`, no `VACUOUS` |
| env_drift `--claims-only origin/main` | `claims hygiene: origin/main ok` |
| layout `--guard` | `GUARD: 0 refusal(s)` |
| structure | `STRUCTURE RATCHET PASSED` |
| throwaway_git | `0 ... refused` |
| tmp_paths | `0 refused` |
| codeowners_gap | `RESULT uncovered_files=0` |
| harness_headers | `ALL 109 HARNESS HEADER CHECKS PASSED` |
| archscore `--diff` at the merge base | `Architecture score: dS +0.0000 NULL` |
| agreement | `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok` |

`delivery_status.py --check` prints `DELIVERY STATUS OK — 138 rowed, 2 pending, 0 overdue`. The body's `136 rowed` was taken at `b87e8f19b`. The extra rows come from the main merge (#2390 and #2425's records), not from this PR, and the `0 overdue` the body relies on holds.

## Other steps

- **Checks** (step 11; check-runs API, `ev/checkruns-final.tsv`):
  - At this head, nothing has concluded `failure`.
  - `fast (3.14)`, `closures` and `Analyze (python)` were still `in_progress` when I wrote this.
  - Concluded `success`: `typing`, `browser`, `scope`, `closure-scope`, `wave-script`, `delivery-status`, `pr-contract` (both runs), `mutation`, `instrument-self-tests`, `env-matrix`, `policy-docs`, `arch-score` and `budget-raise-gate`.
  - `26b148e5b` and `82095a68d` carry no check runs, so they were never a pushed head.
  - The earlier reds in the range are named and answered in `## Red checks`.
  - My local `entities.py` pass predicts `fast` green.
- **Version, claims and budgets** (steps 4, 5, 14): `VERSION`, the manifest, the `RELEASE_NOTES.md` heading, both claim files, the goldens and every `*_budgets.json` are outside the diff. `tests/closures.json` moved through the bot's re-record (as rounds 5 and 6 found) and main's own entry.
- **Class** (step 6): the census returns nothing at the head, including over the files #2390 added.
- **Head** (steps 7, 12): `pulls/2406` reported head `22803f99bd8be29012a668ef22140dd12ae3aa5e` when I wrote this, the head named in `## Head`.
- **Rounds:** this is the seventh. The product and its pins hold, and every figure re-derives. What remains is the carry above, which is a roster edit and leaves the head as it is.
