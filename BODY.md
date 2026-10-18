_Requested by **tvofi**_

O12, two seat-instrument defects that stopped the review bus. Part of #201 (mandate comment 6175172275). No issue is filed for either, so this body closes none. Round 2: it answers the round-1 verdict on `3b4c0fab` (vacuous-check, class-open).

**Ownership.** Every changed file is under `tools/audit/seat/`. `.github/CODEOWNERS` gives none of them an owner. No budget file and no policy file changes.

What changes:

- **`bus.sh orphans` stops refusing forever after one rewritten ref.** `orphans` fetches `main`, `handoff/*`, `handoff-body/*` and `fix/*` into the private namespace `refs/hpo-orphans/`. The four refspecs had no leading `+`. So once the remote moved any of those refs non-fast-forward, git rejected the update, and every later run died with `could not fetch the refs of origin`. On 2026-10-18 the main checkout's run refused this way, and `git fetch --dry-run` with the same refspecs named `handoff/audit-r9-plan` and `handoff/r10-pump-model` as `[rejected] (non-fast-forward)`. The namespace is a mirror of the remote and never holds work, so the four refspecs are now forced. A fetch that fails for any other reason, such as network, auth or no such remote, still dies.
- **One writer for a PR's own row, and an update adds a missing one.** `open_pr.sh` and `handoff_push.sh` each committed the row only after their first push opened the PR, and then pushed again. When that second push's prepr refused, as it did for #2390 and #2391 (`RED UNANSWERED`), the PR had no row. Nothing added it later, so `bus.sh dispatch` refused the review forever (`carries no dev/programme/delivery/N.md`).
  - The writer is now one file, `tools/audit/seat/delivery_row.sh`, with `write_row`, `row_line`, `commit_row` and `ensure_row`. `open_pr.sh`, `update_pr.sh` and `handoff_push.sh` all source it. Neither `open_pr.sh` nor `handoff_push.sh` keeps a copy of its own.
  - `ensure_row` adds the row only when the head lacks it. `update_pr.sh` calls it after its merges and takes its output to word the `## Head` note, so `ensure_row`'s own guard is the one production decides on (round 1's M8 note). `handoff_push.sh`'s update path calls it too, so a PR whose open left no row gains one on its next update. `handoff_push.sh`'s open path calls `commit_row`.
  - `commit_row` sets the committer through `GIT_COMMITTER_*` and the author through `--author`. The old `-c user.name` form loses to an exported `GIT_COMMITTER_NAME`.
  - `row_line` with an empty group writes the title alone. `open_pr.sh` used to write `title ()`. That is a deliberate change: an empty pair of parentheses carries nothing.
  - `update_pr.sh` reads the PR number with `gh pr list --head <branch>`, a read (`PR_N` overrides it), and the title with `gh pr view`. With no open PR at the branch it stops before it pushes.
- `bus.sh --self-test`, which CI's `instrument-self-tests` runs, also runs `delivery_row.sh --self-test`. It checks that the writer's `ROW_DIR` is the one `dispatch` reads, and it refuses any seat shell script other than `delivery_row.sh` that defines `write_row` or makes a `record: the delivery row for` commit.

Alternatives considered:
1. Drop and recreate `refs/hpo-orphans/` before each fetch. That has the same effect as `+`, at the cost of refetching objects, and it adds a delete step that could fail half-applied.
2. Copy `write_row` and the commit into `update_pr.sh`. The brief ruled out a copy, and the two copies already in `open_pr.sh` and `handoff_push.sh` were the shape this fixes.
3. Retire `handoff_push.sh` instead of routing it. `dev/programme/HANDOVER.md` and `delivery-status-tracking.md` still name it, and both of them are outside this group: one is the handover and the other is policy. Routing it closes the defect without touching either.
4. Write the row before the first push. It cannot be done: the row names N, and N exists only after the first push opens the PR.

## Head

`9f3ae9fe35801b13a1471be3d2e97fe20860b106`: round 1's code head `e73f506d`, a merge of origin/main `63816b857` (git merge, 2026-10-18, no conflict), and the round-2 commit. Every figure below was taken at this head unless marked base (origin/main `63816b857`).

## Mutation proof

Each mutant was applied to the head's file, its self-test was run, and the file was restored:

- **M1: `+` dropped from the `handoff/*` refspec.** `bash tools/audit/seat/bus.sh --self-test` prints `68 checks, 1 failed`: `FAIL a handoff ref rewritten non-fast-forward after a run is still read, at its new tip`. Round 1 showed that dropping all four `+` (the base's form) fails the same row.
- **M7: `commit_row` stages with `git add -A`** (the reviewer's mutant, which survived round 1). `bash tools/audit/seat/delivery_row.sh --self-test` prints `5 checks, 2 failed`:
  - `FAIL a head without its row gains exactly one commit, adding only that row, as tvofi; the stray file and the edit stay out`
  - `FAIL null control: a head that carries its row gains no commit, and its row file is not rewritten`

  The fixture now carries a stray untracked file and an unstaged edit, which `git add -A` commits.
- **M8: `ensure_row` rewrites the row file before its guard.** `5 checks, 1 failed`: `FAIL null control: ... its row file is not rewritten`.
- **M3: `ensure_row`'s `has_row` guard deleted.** `5 checks, 1 failed`, the same null-control row.
- **M9: `handoff_push.sh` makes its own row commit again** (`commit_row` replaced by `git commit -qm "record: the delivery row for #$N"`). `bus.sh --self-test` prints `68 checks, 1 failed`: `FAIL delivery_row.sh is the one seat script that defines write_row or commits a row`. The base is the same case: the one-writer grep, run over origin/main's `tools/audit/seat/` (a `git archive` copy), prints `open_pr.sh` and `handoff_push.sh`, the two copies this diff removes.
- **M10: `row_line` writes the group's parentheses even when the group is empty.** `5 checks, 2 failed`, among them `FAIL no group writes no empty parentheses`.
- **Round 1's M5 and M6, re-run at this head.** M5, the committer set by `-c user.name`: `5 checks, 1 failed`, the "as tvofi" row. M6, a changed `ROW_DIR`: `bus.sh --self-test` `68 checks, 1 failed`, `FAIL the shared delivery-row writer passes its self-test, at the ROW_DIR dispatch reads`.

## Null control

- **An unreachable remote still refuses.** `HPO_BUS_REMOTE=<scratch>/nowhere.git bus.sh orphans` exits non-zero, prints `could not fetch the refs of`, and prints no `orphans:` summary line. M1 leaves this row `ok`, so `+` does not turn a failed fetch into a pass.
- **A head that carries its row gains no commit, and its row file is not rewritten.** The second `ensure_row` call leaves HEAD unchanged, `git diff --quiet -- dev/programme/delivery` holds, and `git status --porcelain` still reads exactly ` M x` and `?? stray`. M3, M7 and M8 each turn this row red.
- **The unmodified tree.** At base, the rewritten-ref row fails (round 1's failing-first run: `66 checks, 1 failed`), and the one-writer grep returns `open_pr.sh` and `handoff_push.sh`, as M9 records.

## Figures

- `bash tools/audit/seat/bus.sh --self-test` (seat venv first on PATH): `bus self-test: 68 checks, 0 failed`, rc 0.
- `bash tools/audit/seat/delivery_row.sh --self-test`: `delivery_row self-test: 5 checks, 0 failed`. `open_pr.sh`, `update_pr.sh` and `handoff_push.sh --self-test` exec the same self-test.
- **Class seams, fix 1.** The rule is a refspec with a destination and no `+`, in tracked code: `git grep -nE '["'"'"' ]refs/(heads|pull|tags)/[^ "'"'"']*:(refs|\$)' <ref> -- tools tests .github`.
  - Base: 5 lines. Four are `bus.sh`'s orphans refspecs, closed in this diff.
  - The fifth is `.github/workflows/release.yml`'s `refs/tags/${TAG}:refs/tags/${TAG}`. It is already guarded: the fetch runs in a fresh runner checkout, where that local tag does not exist yet, and a stamped tag is never rewritten.
  - Head: that one line.
- **The brief's enumeration**, `grep -n 'git fetch' tools/audit/seat/*.sh`. Each hit has a disposition:
  - `bus.sh` orphans: closed here.
  - `bus.sh` `unpack`: already forced.
  - `bus.sh` `append_commit`, and the sha fetch in `bus.sh`'s row check: no destination, FETCH_HEAD only.
  - `body_push.sh`, `handoff_push.sh`, `open_pr.sh`, `remerge_main.sh` and `update_pr.sh`: named refs with no destination. Their only ref write is git's opportunistic update of `refs/remotes/origin/*` through the clone's forced refspec (`git config --get-all remote.origin.fetch` prints `+refs/heads/*:refs/remotes/origin/*`).
  - The rest are comments in `bus.sh` and `r9_rc_bus_fetchhead.sh`.
- **Class seams, fix 2: writers of a PR's own `**open**` row.** The rule: `git grep -nF '**open**' -- tools .github`, with self-test fixtures and comments excluded. It returns three production sites:
  - `delivery_row.sh` `row_line`: the writer.
  - `handoff_push.sh`'s own row commit: base 1 line, head 0. It is routed through `delivery_row.sh` in this diff and pinned by the one-writer row (M9).
  - `record_row.py`'s writer: a distinct writer class, already guarded. It writes the record beat's rows for merged PRs and its own record PR's row (`--write-self-row` in `tests.yml`), never another PR's open row, and `tests/entities.py` pins it. `INSTRUMENTS.md` now names it as the other row writer, so the entry no longer says "the one writer" without qualification.
- **Documents that name `handoff_push.sh`.**
  - `dev/governance/rules/delivery-status-tracking.md` line 33 says the row is "written by the orchestrator (`tools/audit/seat/handoff_push.sh`)". Not edited. It is still true: `handoff_push.sh` writes the row, now through `delivery_row.sh`. Naming the shared writer there would be a policy edit, which needs tvofi's approving review at merge. This PR makes none, so it owes no such approval.
  - `.claude/rules/` and `.cursor/rules/` are that rule generated, so they are unchanged with it.
  - `dev/programme/HANDOVER.md` line 33 lists `handoff_push.sh` among the orchestrator's seat scripts. Still true, and not edited.
- **The live run.** The fixed `bus.sh orphans`, run from the main checkout after the refusal above, completes and prints its `orphans:` summary line. It reported two `ORPHAN ... repair=opener` lines, for `r10-earlycutoff-coverage` and `r10-pre-edit-hook`, which are open work for the orchestrator. The count is a function of the remote at the moment of the run, so re-run the instrument rather than quote it.
- **The delegated APPLY** (round 1's `update_pr.sh`). On its first real run, for #2390, `ensure_row` wrote head `5f6d8fbd7141a01c9e30afae5b6d8a28f7368088` (`record: the delivery row for #2390`, author and committer tvofi). `git show --stat` lists one file for it, `dev/programme/delivery/2390.md`, and the push passed prepr. #2391's update went to the orchestrator.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`, over the six changed files, all under `tools/audit/seat/`.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only origin/main`: `claims hygiene: origin/main ok`. Not run: `env_drift.py --all`. It timed out under box load for the round-1 reviewer and was not re-run here (load1 above 60). The diff touches no golden fixture and no claim file: `git diff --stat <merge-base> HEAD -- tests/golden` is empty.

## Red checks

none

## Unpinned sites

Every changed line is under `tools/audit/seat/`, outside the mutation inventory. Behaviour is pinned by the self-test rows M1 and M3 to M10 turn red, which CI runs through `instrument-self-tests` (`bash tools/audit/seat/bus.sh --self-test`). Two call sites are pinned by no hermetic test: `update_pr.sh`'s `ensure_row` call, and `handoff_push.sh`'s update-path `ensure_row` call. Both drive `gh` and `app_push.sh` against GitHub. The first has the live #2390 run as its evidence, and the second has no live run. The one-writer row pins that neither script makes a row commit of its own.

## Forward-carry

none. `tools/audit/seat/INSTRUMENTS.md` carries the `delivery_row.sh` entry, and its `update_pr.sh` and `handoff_push.sh` entries name the row they add. No later stage's brief changes.

## Friction

- `fixer.md`: cost: the openers' call sites cannot be driven hermetically, because they push through `app_push.sh` and read the PR number from GitHub, so their proof is a live delegated run.
