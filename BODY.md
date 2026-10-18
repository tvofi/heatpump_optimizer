_Requested by **tvofi**_

O12, two seat-instrument defects that stopped the review bus. Part of #201 (mandate comment 6175172275). No issue is filed for either, so this body closes none.

**Ownership.** Every changed file is under `tools/audit/seat/`. `.github/CODEOWNERS` gives none of them an owner. No budget file changes.

What changes:

- **`bus.sh orphans` stops refusing forever after one rewritten ref.** `orphans` fetches `main`, `handoff/*`, `handoff-body/*` and `fix/*` into the private namespace `refs/hpo-orphans/`. The four refspecs had no leading `+`. So once the remote moved any of those refs non-fast-forward, git rejected the update, and every later run died with `could not fetch the refs of origin`. On 2026-10-18 the main checkout's run refused this way, and `git fetch --dry-run` with the same refspecs named `handoff/audit-r9-plan` and `handoff/r10-pump-model` as `[rejected] (non-fast-forward)`. The namespace is a mirror of the remote and never holds work, so the four refspecs are now forced. A fetch that fails for any other reason, such as network, auth or no such remote, still dies.
- **`update_pr.sh` adds a missing delivery row.** `open_pr.sh` commits the PR's own row (`dev/programme/delivery/<N>.md`) only after its first push has opened the PR, and then pushes again. When that second push's prepr refused, as it did for #2390 and #2391 (`RED UNANSWERED`), the PR existed with no row. `update_pr.sh` never wrote a row, so `bus.sh dispatch` refused the review forever (`carries no dev/programme/delivery/N.md`).
  - The row writer moves out of `open_pr.sh` into a new file, `tools/audit/seat/delivery_row.sh`, with four functions: `write_row`, `row_line`, `commit_row` and `ensure_row`.
  - `open_pr.sh` and `update_pr.sh` both source it, so the row is written in one place, with one commit identity and one message.
  - `update_pr.sh` calls `ensure_row` after its merges. The row is added only when the head lacks it, and the `## Head` note then says so. The PR number comes from `gh pr list --head <branch>` (a read), or from `PR_N`. With no open PR at the branch, `update_pr.sh` stops before it pushes.
  - `commit_row` sets the committer through `GIT_COMMITTER_*` and the author through `--author`. The old `-c user.name` form loses to an exported `GIT_COMMITTER_NAME`, so a seat's identity variables could have signed the row.
- `bus.sh --self-test`, which CI's `instrument-self-tests` runs, now also runs `delivery_row.sh --self-test`. It checks that the writer's `ROW_DIR` is the one `dispatch` reads. Without this, the writer's checks would run nowhere in CI: `open_pr.sh --self-test` has no CI step.

Alternatives considered:
1. Drop and recreate `refs/hpo-orphans/` before each fetch. That has the same effect as `+`, at the cost of refetching objects, and it adds a delete step that could fail half-applied.
2. Copy `write_row` and the commit into `update_pr.sh`. The brief rules this out (one function, not a copy), and a second copy of the identity is the shape that drifted here.
3. Have `open_pr.sh` write the row before its first push. It cannot: the row names N, and N exists only after the first push opens the PR.

## Head

`e73f506d161451c7cd2ba05ec17e5e67c476be16`, one commit on origin/main `932f5d601`. Every figure below was taken at this head unless marked base (origin/main `932f5d601`).

## Mutation proof

Each mutant was applied to the head's file, its self-test was run, and the file was restored:

- **M1: `+` dropped from the `handoff/*` refspec only.** `bash tools/audit/seat/bus.sh --self-test` prints `67 checks, 1 failed`: `FAIL a handoff ref rewritten non-fast-forward after a run is still read, at its new tip`.
- **M2: `+` dropped from all four refspecs, which is the base's form.** Same output: `67 checks, 1 failed`, the same FAIL.
- **M3: `ensure_row` always commits** (its `has_row ... && return 0` line deleted). `bash tools/audit/seat/delivery_row.sh --self-test` prints `4 checks, 1 failed`: `FAIL null control: a head that carries its row gains no commit`.
- **M4: `ensure_row` never commits** (its `commit_row` call replaced by `:`). `4 checks, 1 failed`: `FAIL a head without its row gains exactly one commit, adding only that row, as tvofi`.
- **M5: `commit_row`'s committer set by `-c user.name`, `open_pr.sh`'s old form.** `4 checks, 1 failed`, the same FAIL as M4. The helper's exported identity (`t`) signs the commit.
- **M6: `ROW_DIR` changed in `delivery_row.sh`.** `bus.sh --self-test` prints `67 checks, 1 failed`: `FAIL the shared delivery-row writer passes its self-test, at the ROW_DIR dispatch reads`.
- **Failing first.** The new rewritten-ref row was written before the fix, and against the unforced refspecs `bus.sh --self-test` printed `66 checks, 1 failed`, the FAIL being that row.

## Null control

- **An unreachable remote still refuses.** `HPO_BUS_REMOTE=<scratch>/nowhere.git bus.sh orphans` exits non-zero, prints `could not fetch the refs of`, and prints no `orphans:` summary line (`ok null control: an unreachable remote still refuses the orphans run`). M1 and M2 leave this row `ok`, so `+` does not turn a failed fetch into a pass.
- **A head that already carries its row gains no commit.** `ensure_row`'s second call leaves HEAD unchanged (`ok null control: a head that carries its row gains no commit`). M3 turns this row red.
- **The unmodified tree.** At base, the rewritten-ref row fails, as the failing-first line records. The other 66 rows of `bus.sh --self-test` pass at base and at head.

## Figures

- `bash tools/audit/seat/bus.sh --self-test` (seat venv first on PATH): `bus self-test: 67 checks, 0 failed`, rc 0. The two new rows are listed under Mutation proof.
- `bash tools/audit/seat/delivery_row.sh --self-test`: `delivery_row self-test: 4 checks, 0 failed`. `open_pr.sh --self-test` and `update_pr.sh --self-test` exec the same self-test and print the same line.
- **The live run.** The fixed `bus.sh orphans`, run from the main checkout after the refusal above, completes and prints its `orphans:` summary line. It exits 1 on two `ORPHAN ... repair=opener` lines, for `r10-earlycutoff-coverage` and `r10-pre-edit-hook`. Those are open work for the orchestrator, not part of this change. The count is a function of the remote at the moment of the run, so re-run the instrument rather than quote the number.
- **Class seams.** The rule is a refspec with a destination and no `+`, in tracked code: `git grep -nE '["'"'"' ]refs/(heads|pull|tags)/[^ "'"'"']*:(refs|\$)' <ref> -- tools tests .github`.
  - Base: 5 lines. Four are `bus.sh`'s orphans refspecs, closed in this diff.
  - The fifth is `.github/workflows/release.yml`'s `refs/tags/${TAG}:refs/tags/${TAG}`. It is already guarded: the fetch runs in a fresh runner checkout, where that local tag does not exist yet, and a stamped tag is never rewritten.
  - Head: that one line.
- **The brief's enumeration**, `grep -n 'git fetch' tools/audit/seat/*.sh`. Each hit has a disposition:
  - `bus.sh` orphans: closed here.
  - `bus.sh` `unpack`: already forced (`+refs/heads/$fam/$pr:refs/hpo-bus/...`).
  - `bus.sh` `append_commit`, and the sha fetch in `bus.sh`'s row check: no destination. They write FETCH_HEAD only, so a rewrite cannot reject them.
  - `body_push.sh`, `handoff_push.sh` (4 calls), `open_pr.sh` (2), `remerge_main.sh` and `update_pr.sh` (2): named refs with no destination. Their only ref write is git's opportunistic update of `refs/remotes/origin/*` through the clone's configured refspec, which is forced (`git config --get-all remote.origin.fetch` prints `+refs/heads/*:refs/remotes/origin/*`).
  - The remaining hits are comments, three in `bus.sh` and two in `r9_rc_bus_fetchhead.sh`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. Every changed file sits under the `tools/audit/` prefix outside every measured closure. The self-tests are graded by CI's `instrument-self-tests` (`bus.sh --self-test`), not by the scoped gate.
- **The delegated APPLY** (the brief's, with the fixed `update_pr.sh`) is reported to the orchestrator by the seat, not here. On its first real run, for #2390, `ensure_row` wrote head `5f6d8fbd7141a01c9e30afae5b6d8a28f7368088` (`record: the delivery row for #2390`, author and committer tvofi). `git show --stat` lists exactly one file for it, `dev/programme/delivery/2390.md`. The PR's `## Head` line records it, and the push passed prepr, rc 0.

## Red checks

none

## Unpinned sites

Every changed line is under `tools/audit/seat/`, outside the mutation inventory. The behaviour is pinned by the self-test rows M1 to M6 turn red, and CI runs them through `instrument-self-tests` (`bash tools/audit/seat/bus.sh --self-test`). One site is pinned by no hermetic test: `update_pr.sh`'s call of `ensure_row`. Driving it needs `gh` and `app_push.sh` against GitHub. Its evidence is the delegated run for #2390 named in Figures.

## Forward-carry

none. `tools/audit/seat/INSTRUMENTS.md` gains the `delivery_row.sh` entry, and its `update_pr.sh` entry now names the row it adds. No later stage's brief changes.

## Friction

- `fixer.md`: cost: the `update_pr.sh` call site cannot be driven hermetically, because the instrument pushes through `app_push.sh` and reads the PR number from GitHub, so its proof is a live delegated run.
