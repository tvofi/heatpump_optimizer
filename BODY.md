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

`f607a349f1a8b6336d62fb6d36394197b996cd94`, at merge base `be0cb821` (`origin/main`). This is round 3. PR head `6f3609a4` (round 1 plus its row commit) is merged in. Three commits answer round 1's block, and three answer round 2's block and the row report that followed it.

Round 2 blocked with `harness`: the carries' command `moved_paths.py tools/audit/seat/*` crashed with `IsADirectoryError` on the tracked directory `tools/audit/seat/shims/`. A directory argument is now walked: every tracked file under it is scanned, recursively, and untracked files are skipped. A self-test case covers this. A `layout.json` directory entry whose files are still tracked now counts as a planned move, not a moved one. The carry command is unchanged; its seat-wide run is in `## Figures`. That run found one functional defect, now fixed:

- `tmp_paths.py` scanned only `docs/decisions/`, so no decision record has been scanned since the governance lift.
- Its self-test case sat on the old path and stayed green.
- The scope now includes `dev/governance/decisions/`, with a self-test case at the new home. `--check` at that scope refuses nothing.

Stale comments, a reason string and a fixture path in `INSTRUMENTS.md`, `record_row.py`, `roster_lib.py`, `state_docs.py` and `tmp_paths.py` are re-pointed.

The orchestrator also reported rows for #2013 and #2014 landing at the retired `docs/delivery/<N>.md`. `7cef1c32`'s `open_pr.sh` named only `dev/programme/delivery/`, and `origin/main`'s copy names only `docs/delivery/`, so the run that wrote those rows used main's copy. Neither copy had a fallback for the row write. Both `open_pr.sh` and `handoff_push.sh` now write the row through one `write_row` function. It always targets `dev/programme/delivery/<N>.md`, and creates the directory for a branch that predates the lift. Each script gains a `--self-test` that drives that function. The old path is never written.

Round 1 blocked with `class-open`: `handover_prompt.py:78` still sent every generated prompt to `tools/audit/briefs/`, a directory the governance lift emptied into `dev/governance/roles/`. Round 1's search matched script paths only (`.sh`, `.py`, `.mjs`), so it could not find a directory. Round 2 lands that search as `tools/audit/seat/moved_paths.py`. It reads every path `tests/layout.json` marks moved: each retired file no longer tracked, its emptied parent directory, and each lifted prefix. It reports every line that names one. Re-pointed in round 2:

- `handover_prompt.py:78`, to the contracts' directory. Its self-test now requires every backticked repository path in the generated prompt to exist.
- `handoff_push.sh`: its rule citation, the `HANDOVER.md` comment on line 7, and a note filter that excused the retired `tools/audit/handoff/`.
- `merge_train.py`: four self-test fixture lines that modelled a policy path at `tools/audit/briefs/fixer.md`.

The R9-RO-8 and R9-RO-9 carries now name `moved_paths.py` in their re-measurement.

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

Round 2:

- `handover_prompt.py:78` restored to `tools/audit/briefs/`: `handover_prompt self-test: 13 checks, 1 failed`, the check `every repository path the prompt names exists (missing: tools/audit/briefs/)`. Fixed: `13 checks, 0 failed`.
- `moved_paths.py` over round 1's five files (PR head `6f3609a4`) finds the reviewer's line, `handover_prompt.py:78 [STALE?] tools/audit/briefs/ -> dev/governance/roles/`, among 20 hits. Over this head it finds 12.

Round 3:

- `moved_paths.py` as of round 2 (`7cef1c32`), over `tools/audit/seat/*`, prints `IsADirectoryError: [Errno 21] Is a directory: 'tools/audit/seat/shims'`.
- Round 3's self-test with directory walking switched off (`if p.is_dir():` replaced by `if False:`) prints `FAIL a directory argument walks its tracked files, recursively, and skips untracked ones`, then the same `IsADirectoryError`. Fixed: `9 checks, 0 failed`.
- `tmp_paths.py` with main's `docs/decisions/`-only scope restored: `tmp_paths self-test: 42 checks, 1 failed`, the check `a decision record at its lifted home citing /private/tmp is refused`. Fixed: `42 checks, 0 failed`.

- `open_pr.sh` and `handoff_push.sh` with `ROW_DIR` set back to main's `docs/delivery`: each prints `FAIL a row lands under dev/programme/delivery/<N>.md, and nothing is written under docs/` and `1 checks, 1 failed`. Fixed: `1 checks, 0 failed`.

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
- handover prompt 13 checks, 0 failed (round 2): `python3 tools/audit/seat/handover_prompt.py --self-test`
- moved-path enumeration 9 checks, 0 failed: `python3 tools/audit/seat/moved_paths.py --self-test`
- tmp paths self-test 42 checks, 0 failed: `python3 -I tools/audit/seat/tmp_paths.py --self-test`
- row write 1 check, 0 failed: `bash tools/audit/seat/open_pr.sh --self-test`
- row write 1 check, 0 failed: `bash tools/audit/seat/handoff_push.sh --self-test`
- moved-path references, 12 hits in the five instruments, every one dispositioned below: `python3 tools/audit/seat/moved_paths.py tools/audit/seat/merge_train.py tools/audit/seat/bus.sh tools/audit/seat/open_pr.sh tools/audit/seat/handoff_push.sh tools/audit/seat/handover_prompt.py`
  - 9 are FALLBACK: an old-path-first fallback with the new path on the same line. They are `merge_train.py:84` and `:85`, `bus.sh:86` and `:388`, `open_pr.sh:27` and `:44`, and `handoff_push.sh:60`, `:80` and `:95`.
  - `merge_train.py:160` (`.claude/workflows/policy_lint.mjs`) is the same fallback split across lines: `:161`–`:162` fall back to `tools/policy/policy_lint.mjs`.
  - `handover_prompt.py:14` and `:76` (`.claude/rules/`): `tests/layout.json` lists this prefix as lifted, not retired. The generated copy stays, and the harness loads it when it binds, which is what the prompt says.
- the carries' command, seat-wide, 26 hits in 25 files, every one dispositioned below: `python3 tools/audit/seat/moved_paths.py tools/audit/seat/*`
  - 14 are FALLBACK lines that name the new path. They are the 9 above, plus `merge_pr.sh` (3), `remerge_main.sh` (1) and `update_pr.sh` (1).
  - From the five files: `merge_train.py:160`, `handover_prompt.py:14` and `:76`, as above.
  - `INSTRUMENTS.md:5` and `tmp_paths.py:46` name `.claude/rules/`. That prefix is lifted and its generated copy stays, as above.
  - `roster_edit.py:31`, `:73`, `:456` and `:623` are the `BRIEF_LINT_OLD`/`BRIEF_LINT_NEW` old-first fallback, split across lines, and the self-test seeds that exercise it.
  - `tmp_paths.py:16` and `:219` name `docs/decisions/` on purpose. They are the docstring's "their home before the lift" and the self-test case for the old home, which the scope still covers.
  - `tmp_paths.py:19` is the docstring for the round-evidence exclusion, which names the retired `tools/audit/handoff/`. The exclusion of a directory that no longer exists is inert.
- gate `MODE: SCOPED -- 1 script(s) run, 30 scoped out`, the one script being `tests/entities.py`: `python3 tests/closure.py select --diff be0cb821 --workdir <dir>`
- entities `ALL 2191 ENTITY CHECKS PASSED` (Python 3.14): `PYTHONPATH=tests/hastub python3 tests/entities.py`

## Red checks

`delivery-status` is red at PR head `6f3609a4` (job 112676885167). It printed `DELIVERY STATUS UNCHECKED — 46 rowed, 3 pending, 0 overdue`. The 3 pending are #1917, #2003 and #2001, and the unread commits are main's own (`618d014`, `0a60e06` and others). None of them is #2012. The diff's one record file is #2012's own row, `dev/programme/delivery/2012.md`, which the orchestrator's row commit added. The check grades `main` and is not a required context. Cheaper detector: none. The finding is that main's record backlog is the orchestrator's to drain, and it would be red on any pull request in this window.

`nightly-status` is red at PR head `6f3609a4` (job 112676884784). It printed `NIGHTLY FAILED: record-autofix failed last night`: scheduled run 37440269774 at main `cff39da`, the `record-autofix` job. That is a main lane, and this diff does not touch it or what it runs. The diff's one record file is #2012's own row. Fixing that lane and dispatching `tests.yml` on `main` is the orchestrator's (`defect-root-cause.md`, Enforcement). Cheaper detector: none from this pull request.

## Forward-carry

`.claude/workflows/carry-1921.json` (R9-RO-8) and `dev/programme/carries/carry-1922.json` (R9-RO-9). A move re-points every seat instrument that invokes the moved path, in the move commit. Retiring an old lookup deletes only the old half of `merge_train.py`'s `TOOLS` tuples and of `bus.sh`'s fallback. Each file carries the control and the re-measurement. The roster brief copy on `handoff/audit-r9-fixplan` is the orchestrator's to update.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
