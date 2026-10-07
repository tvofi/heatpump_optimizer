This is the root-cause seat's analysis of #1990, the `head-moved` friction key.
The key has now been filed seven times in fourteen days (#1498, #1501, #1574,
#1600, #1706, #1807, #1990). The analysis is `dev/audit/rca/R9-RCA-1990.md`,
indexed as `_rca["R9-RCA-1990"]` in `tools/audit/bugclasses.json`.

The count is correct: 11 PRs / 20 entries over `v6.7.16..origin/main`. The
seat classified every entry by the commits between the two verdicted heads, and
re-ran `app_approve.sh --carry` with the script version and `main` each head
actually merged:

| class | entries |
|---|---|
| RO-wave sibling repairs | 11 |
| other own commits | 2 |
| carry refused by design (main moved the diff's context lines) | 2 |
| carry-eligible at the time | 3 (one of these re-reviews found a real defect) |
| reviewer-written `head-moved` | 2 |

**Cause and process state:**

- **The recurrence is (c).** The filer keys sanctioned re-review under the same
  word as the reviewer's breach verdict. So it re-files on every active window,
  and every seat that disposes it finds the process working.
- **The RO siblings are (c).** R9-RO-4, -5, -6 and -7 were parallel in the
  roster. All four write `tests/closure.py` and `tests/closures.json`.
- **The carry instrument is (d).**
  - R9-RO-6 moved `app_approve.sh` and `preflight.sh` to `tools/pr/`. R9-RO-5
    lifted the rows to `dev/programme/delivery/`.
  - `merge_train.py` still ran the old paths and required `docs/delivery/<N>.md`.
    Every carry stopped with `No such file or directory`.
  - Its stubbed self-test stayed `43 checks, 0 failed`.

**Countermeasure built (CM-1).**

- `merge_train.py` resolves every script it runs through one `TOOLS` table,
  old path first, the move's own convention.
- `ROW_DIR` is `dev/programme/delivery`.
- Six self-test checks read the real tree instead of the stub.

The same moves left the following pointing at missing paths, and each is
re-pointed:

- `bus.sh`'s default verdict poster (its pin now matches the whole line and
  needs the file to exist);
- `open_pr.sh`'s and `handoff_push.sh`'s row write;
- `handover_prompt.py`'s text.

**Refused on the cost test:**

- A sibling write-set lint (CM-2): one reorg wave in nine rounds against a new
  field on every roster group.
- Widening `carry` to accept a row-only commit: 1 in 57 merges.

**For the owner, not built (CM-3).** Should the rework arm stop bumping
`head-moved`? `STATS ROUNDS` already prints that count, and a reviewer-written
`head-moved` would keep filing. This is the question open since #1498.

- It reverses the keying that #1405 and #1549 pinned in `tests/entities.py`.
- It changes what the owner-approved filer (#959 B) files, so it is policy and
  needs the owner's approval. The orchestrator holds the round-9 mandate for
  it. Until it is decided, the key re-files on every active window.

No file in this diff is policy (`policy_lint.mjs --corpus-filter` returns
nothing for it) or a budget. Closes #1990: the count stands, and the
disposition names which of the two it changes. It changes neither the keying
nor the bodies: CM-1 removes future carry-eligible entries, and CM-3 is the
owner's.

## Head

`277cc786bc5820086eeadce901818225ab7d1bba`, at merge base `3910026e` (`origin/main`).

## Mutation proof

Each arm restores main's defect into the fixed tree and runs the self-test:

- **`TOOLS`/`ROW_DIR` restored to main's locations** (old paths only,
  `docs/delivery`): `merge_train self-test: 49 checks, 3 failed`. The failing
  checks:
  - `the train's app_approve script is in the tree (tools/audit/app_approve.sh)`
  - `the train's preflight script is in the tree (tools/audit/preflight.sh)`
  - `the delivery-row directory the train requires, docs/delivery/, is in the tree`
- **The carry argv restored to main's bare `"tools/audit/app_approve.sh"`**:
  `1 failed`, the check
  `every script the train runs resolves through TOOLS, none by a bare path (bare: tools/audit/app_approve.sh)`.
- **`bus.sh`'s default poster (line 86) restored to `tools/audit/app_comment.sh`**:
  `bus self-test: 45 checks, 1 failed`, the check
  `a verdict posts as a comment through app_comment.sh, never as an approving review`.
  The old pin was `grep -q` on a substring, which matched the pin's own line,
  so it could not fail. The new pin is `grep -qxF` on the whole default line.

Functional arm, on #1980's pair `569e0e63` → `356eb015`:

- Main's carry argv prints `bash: tools/audit/app_approve.sh: No such file or directory` and no `CARRY` line.
- The fixed `tool("app_approve")` resolves to `tools/pr/app_approve.sh` and prints `CARRY: yes`.

## Null control

- `origin/main`'s own `merge_train.py` self-test prints
  `merge_train self-test: 43 checks, 0 failed` on the broken tree. That green
  is the detector gap this fixes.
- The fixed tree prints `49 checks, 0 failed`. Each new check is a direct file
  or directory test on the tree, so it cannot pass by being skipped.
- Timing is within run-to-run noise: main 0.91–2.13 s, fixed 1.27–1.83 s,
  3 runs each.

## Figures

- `head-moved` at 11 PRs / 20 entries: `GITHUB_TOKEN=$(gh auth token) node tools/policy/policy_lint.mjs --stats --since v6.7.16`
- merge train 49 checks, 0 failed: `python3 tools/audit/seat/merge_train.py --self-test`
- verdict bus 45 checks, 0 failed: `bash tools/audit/seat/bus.sh --self-test`
- handover prompt 12 checks, 0 failed: `python3 tools/audit/seat/handover_prompt.py --self-test`
- ledger 0 violations, 97 rca entries: `python3 tools/audit/fold_ledger.py check`
- tmp paths 0 refused: `python3 -I tools/audit/seat/tmp_paths.py --check`
- gate `MODE: SCOPED -- 0 script(s) run, 31 scoped out`: `python3 tests/closure.py select --diff 3910026e --workdir <dir>`

## Red checks

none

## Forward-carry

`.claude/workflows/carry-1921.json` (R9-RO-8) and `dev/programme/carries/carry-1922.json` (R9-RO-9). A move re-points every seat instrument that invokes the moved path, in the move commit. Retiring an old lookup deletes only the old half of `merge_train.py`'s `TOOLS` tuples and of `bus.sh`'s fallback. Each file carries the control and the re-measurement. The roster brief copy on `handoff/audit-r9-fixplan` is the orchestrator's to update.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
