Round-10 group R10-TICK-OWED-LEVEL. Part of #201.

**The defect.** `cloud_relay.sh pass` writes the owed LEVEL — a probe ref or a
handoff ref with no open PR, owed until `dispose` — as
`OWED <utc> probe-ref|handoff-no-pr <ref> <sha>`, appended to `cloud-relay.log`
on every pass for every undisposed ref. `orchestrator_tick.py`'s `relay_owed`
prints every OWED line of that log with no later POSTED for its key, so it
replayed every pass's copy: the orchestrator measured a 35214-line log naming
~281 distinct items and a board reading `DISPATCH LIST: 35317 finding(s)`
(2026-10-21), unreadable, which is how owed work was missed. A disposed ref's
historical lines printed too, since the reader never read `cloud-disposed`.

**The fix: the level is state, so it lives in a file that is rewritten, not a
log that is appended.** One writer owns the grammar (`cloud_relay.sh`):

- each arm collects its level lines and `level_set <kind>` makes them the whole
  of `<kind>` in `<log>.level` (`cloud-relay.log.level` by default; beside
  `--log` when given), by temp file and `mv`; the log gets no level line;
- `dispose [--log FILE]` drops the ref+sha's level line at once (not at the
  next pass), from the level beside that log (`--log` is new, matching `pass`);
- a failed listing (ls-remote, `gh pr list`) leaves the level as it was:
  unknown is not "nothing owed". The old writer reported none in that case and
  relied on the replay to keep earlier copies visible.

The reader (`relay_owed`) prints each line of `<log>.level` as is, and reads the
log for events only. Each event is keyed on its PR, the first all-digit field
in `f[1:4]`, which covers every writer the enumeration below returns. Before,
the key was `f[2]`, so `OWED <utc> handoff-update <pr> ...`,
`approve-held-runs` and `dispatch` were keyed on the kind name, and a POSTED for
their PR never cleared them. An OWED naming no PR in the log is an older
writer's per-pass level copy: it is skipped and counted on one unflagged line,
never replayed. That arm matters on the day this merges, because the live log
keeps getting level lines from main's writer until then.

Alternatives, and why each lost:
- **Reader-only dedupe** (keep the newest copy per ref+sha, read
  `cloud-disposed`): the log has no pass boundary, so a ref that was archived
  or deleted stays owed forever at its last copy. It also puts dispose
  semantics in a second file and leaves the log unbounded (34757 handoff-no-pr
  lines in 37 h).
- **Writer skips a line identical to the previous pass's**: the log still
  carries the level, and the reader still needs pass and dispose state to know
  what is current. Two owners.
- **Compacting the log in place each pass**: this races the event appends of a
  concurrent pass (`tick_loop.sh`'s pass beside a `--loop`).

`INSTRUMENTS.md`'s `cloud_relay.sh` and `orchestrator_tick.py` entries are
updated in this diff to say the same. The harness is new and **mine**: there
was no committed harness for the finding (fixer.md step 9's disclosure). It is
`dev/audit/harnesses/r10_tick_owed_level.py`. It drives a tree's own writer for
N passes over a throwaway bare origin, then a `dispose` and one more pass, then
writes five event lines. The tree's own reader reads the result. Its
repositories come from `tests/throwaway_git.py`. `tests/closures.json` gains the
new file in `tests/harness_headers.py`'s inert reads, written by
`tools/pr/ci_predict.py --apply-inert`; this is the entry prepr's CI-predict
step named.

## Head

`b38c6431af1ff171567882bf343b6d0ef05520fb`, merged on `origin/main`
`df6ca4bc6858f2796f694035e6f53e46e237e33b` (the merge base and the baseline
below), measured 2026-10-21T08:17Z.

prepr was run with `PREPR_SKIP_CLOSURES=1`. That is a deliberate skip, not an
inference: CI's `closures` context is required on every pull request, and
`closures-autofix` repairs an UNDER-SCOPED selection (owner ruling,
2026-10-20). Everything else in prepr ran.

## Mutation proof

Each mutant was applied to the committed head, its self-test was run, and the
mutant was restored with `git checkout -- <file>`.

- M1 `cloud_relay.sh` `level_set`: `awk -v k="$1" '$3 != k' "$lv"` -> `cat "$lv"`
  (the level is appended, no longer replaced). `bash tools/audit/seat/cloud_relay.sh --self-test`:
  `FAIL after three passes it is owed once (a level is rewritten, never appended)`,
  `FAIL after three passes the no-PR ref is owed once (rewritten, never appended)`;
  `81 checks, 2 failed`.
- M4 `cloud_relay.sh` `dispose`: `awk -v r="$1" -v s="$2" '!($4 == r && $5 == s)' "$lv"`
  -> `cat "$lv"` (dispose leaves the level line until the next pass).
  `FAIL and drops its level line at once, not at the next pass (rc=0, want 1)`,
  `FAIL and drops its line from the level beside that log (rc=0, want 1)`;
  `81 checks, 2 failed`.
- M2 `orchestrator_tick.py` `relay_owed`: the `if pr is None: stale += 1` branch
  is replaced by `owed.setdefault(pr or f[2], ...)` (a no-PR line is replayed again).
  `python3 tools/audit/seat/orchestrator_tick.py --self-test`:
  `FAIL relay OWED: each level-file line prints once; the log's per-pass copies print none`,
  `FAIL relay OWED: the skipped copies are counted, unflagged`; `154 checks, 2 failed`.
- M3 the PR key `f[1:4]` -> `f[2:3]` (the old position):
  `FAIL relay OWED: null control: without that POSTED both kind-first lines print`;
  `154 checks, 1 failed`.

## Null control

`--passes 1 --no-dispose`: one pass writes no repeated level line, so the
baseline and the head print the same count, `printed=8 distinct=8` at both
ends. The same harness run with three passes and a dispose separates them
(Figures). The new self-test arms carry their own: an OWED followed by its
POSTED prints nothing, and the kind-first lines print when no POSTED follows.
In `cloud_relay.sh`, a rev ref is relayed, not OWED, and the open-PR topic's
refs are not OWED.

## Figures

Each harness line is from `python3 dev/audit/harnesses/r10_tick_owed_level.py`
at this head. `--tree` is a detached worktree at the merge base (baseline) or
this head. The harness drives the TREE's `cloud_relay.sh` and
`Tick.relay_owed`. `distinct` is derived from the fixture: refs on the origin
less the disposed one, plus the three unposted events.

- baseline `--tree <merge-base>`:
  `RESULT tree=df6ca4bc6 passes=3 refs=5 disposed=1 log_lines=24 printed=22 distinct=7 match=no`
- head `--tree .`:
  `RESULT tree=b38c6431a passes=3 refs=5 disposed=1 log_lines=5 printed=7 distinct=7 match=yes`
- null control, `--passes 1 --no-dispose`: baseline
  `RESULT tree=df6ca4bc6 passes=1 refs=5 disposed=0 log_lines=10 printed=8 distinct=8 match=yes`;
  head `RESULT tree=b38c6431a passes=1 refs=5 disposed=0 log_lines=5 printed=8 distinct=8 match=yes`
- the recorded log, read-only:
  `--read-log $HPO_STATE_DIR/cloud-relay.log.archive-20261021T0750Z` (sha1
  `c9870c0c916a2bb09813d8e8cec672a41c46844d`). Baseline
  `RESULT tree=df6ca4bc6 read-log log_lines=35214 printed=35214`. Head
  `RESULT tree=b38c6431a read-log log_lines=35214 printed=15`, with the note
  `35199 OWED line(s) naming no PR skipped`. The 15 printed are the archive's 13
  `handoff-update` and 2 `reviewer-fire` events. The rule:
  `awk '$1=="OWED"' <log> | awk '{k=($2 ~ /^20/)?$3:$2; print k}' | sort | uniq -c`
  printed `34757 handoff-no-pr, 13 handoff-update, 442 probe-ref, 2 reviewer-fire`.
  The archive holds no POSTED line, so none is cleared. The level file is
  absent beside an archive, so the live level is not part of this figure.
- self-tests: `python3 tools/audit/seat/orchestrator_tick.py --self-test` prints
  `154 checks, 0 failed` (baseline `150 checks, 0 failed`).
  `bash tools/audit/seat/cloud_relay.sh --self-test` prints `81 checks, 0 failed`
  (baseline `74 checks, 0 failed`).
- seams (fixer.md step 8), enumerated by
  `git grep -n -e 'cloud-relay\.log' -e 'relay_log' -- tools tests .claude .github`.
  It returns exactly one writer (`cloud_relay.sh`) and one reader
  (`orchestrator_tick.py`, plus its hermetic self-test default), and
  `tick_loop.sh` does not read the log. The OWED writers are enumerated by
  `git grep -n -e 'logline OWED' -e 'level_line ' -e "'OWED reviewer-fire" -- tools`.
  The level kinds are `probe-ref` and `handoff-no-pr`, both moved to
  `level_line`/`level_set` and closed in this diff. The events are `owed()`
  (PR at `f[2]`), `handoff-update`, `approve-held-runs` and `dispatch` (PR at
  `f[3]`), and `reviewer-fire` (PR at `f[2]`). Each is keyed by the `f[1:4]`
  rule and closed in this diff.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff <merge-base> HEAD`:
  `Architecture score: dS +0.0000 NULL`.
- the gate scope, from `python3 tests/closure.py select --diff <merge-base>`:
  `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, naming `tests/entities.py`. The `run_always` lines, run
  with `PYTHONPATH=tests/hastub`: `tests/env_drift.py --claims-only <merge-base>`
  (`claims hygiene: ... ok`), `tests/closure.py selftest`
  (`ALL 124 closure shrink pins PASSED`), `tests/layout.py` (`ok`) and
  `tests/harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`); and `tests/entities.py`, which scope.run names (`ALL 2360 ENTITY CHECKS PASSED`).

## Red checks

none

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
