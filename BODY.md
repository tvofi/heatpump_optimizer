R10-ROSTER-OPS. `tools/audit/seat/roster_edit.py` gains `set-after <group> <G1,G2,...|->` and `drop-carry <group> <index|--match TEXT>`, so the orchestrator applies a replan or drops a stale carry through the load-validate-dump flow instead of a string splice. Both ride the existing lint gate and no-op path unchanged.

Decisions, for the reviewer to judge:
- `set-after` replaces the edge list whole (a replan states the new set); it refuses an unknown target or after-group, a self-edge, a repeated edge, and any cycle in the resulting after-graph (a full DFS over every group's edges, so a pre-existing cycle elsewhere is refused too — the task's "cycle in the resulting DAG").
- `drop-carry` takes a 0-based index (`jq '.carry[N]'`) or `--match`, a substring that must hit exactly one entry; no match and more than one are refused, and an ambiguous match names the matching indices. Dropping the last entry deletes the `carry` key, so append-carry then drop-carry restores the roster's bytes (pinned).
- The new refusal arms assert the refusal's text through a `refuses()` helper, not only rc 2: argparse also exits 2 for an unknown op, so an rc-only arm passes on a tree without the op (the red run below shows those arms failing only once they key on text).
- Alternatives not taken: `set-after --add/--remove` deltas (two ops' worth of surface for the same result; a whole-list write is what a replan carries); exact-equality `--match` (a carry entry is long prose, a substring is what an orchestrator can type; ambiguity is refused rather than guessed).

## Head

`9969e3ca80bd6255cd1231b1b4e53410a6fbeb88`, merge base `106af95a33f89f88f948ea9c49c4632fe74b9416` (origin/main tip at 2026-10-18T18:52Z).

## Mutation proof

`python3 tools/audit/seat/r10_roster_ops_mutants.py` (new, in this diff): 19 plants, one exact replacement each in `roster_edit.py`, file restored byte for byte after each. Every plant rc=1 with at least one FAIL line, none killed by a crash:

| plant | mutates | failing self-test checks |
|---|---|---|
| A1 | set-after unknown after-group predicate → False | set-after unknown after-group refused |
| A2 | self-edge predicate → False | set-after self-edge refused |
| A3 | repeated-edge predicate → False | set-after duplicate edge refused |
| A4 | cycle predicate → False | set-after direct cycle refused; set-after indirect cycle refused; refused set-after moved nothing |
| A5 | cycle checked on the pre-edit graph | set-after direct cycle refused; set-after indirect cycle refused |
| A6 | unknown target group writes a detached dict | set-after unknown group refused |
| A7 | no-op set-after moves the key | no-op set-after reports no change and commits nothing; no-op set-after is byte-identical |
| C1 | absent-carry predicate → False | drop-carry with no carry refused |
| C2 | no match silently drops entry 0 | drop-carry absent match refused (+4 downstream) |
| C3 | ambiguous predicate → False | drop-carry ambiguous match refused (+5 downstream) |
| C4 | lower index bound removed | drop-carry negative index refused (+3 downstream) |
| C5 | non-integer index silently 0 | drop-carry non-integer index refused (+5 downstream) |
| C6 | last drop leaves `"carry": []` | drop-carry of the last entry removes the key; append-carry then drop-carry is byte-identical |
| C7 | index drops the neighbour | drop-carry by index drops that entry (+3 downstream) |
| C8 | drop-carry unknown group writes a detached dict | drop-carry unknown group refused |
| P1 | "index and --match, not both" error removed | drop-carry index and --match together refused (+3 downstream) |
| P2 | "needs an index or --match" error removed | drop-carry neither index nor --match refused |
| P3 | "--match is a drop-carry flag" error removed | set-after names no op flag; --match on another op refused (+2 downstream) |
| D1 | dump indent=2 (the round-trip) | dump round-trips the canonical bytes; no-op set-resume is byte-identical; no-op set-after is byte-identical |

Driver summary line: `plants: 19, without a FAIL line: none`.

Failing test first: the new arms run against the tree with the arms and without the ops printed `roster_edit self-test: 121 checks, 27 failed` — 94 checks; the printed total double-counts failures, a pre-existing quirk of `check()` this diff leaves alone. All 27 failures are new arms.

## Null control

`python3 tools/audit/seat/r10_roster_ops_mutants.py --null` at the head: `RESULT mutant=null rc=0 fails=0`. `python3 tools/audit/seat/roster_edit.py --self-test`: `roster_edit self-test: 94 checks, 0 failed` (the merge base: 64 checks, 0 failed).

Live roster, scratch worktree off origin/main, no `--push`, worktree and branch deleted after: `set-after R10-STORE R10-CURRENCY` (its current edge) printed `no change: ... (byte-identical)`, and `git diff --quiet origin/main -- dev/programme/rosters/wave-r10-groups.json && echo LIVE-ROSTER-BYTE-IDENTICAL` printed it; `set-after R10-CURRENCY R10-STORE` printed `REFUSED: ... closes a cycle: R10-CURRENCY -> R10-STORE -> R10-CURRENCY`. Disclosed self-correction: a first live probe named the wrong current edges for R10-STORE and so made a real local commit; nothing was pushed, and that worktree and branch were deleted before the probe above.

## Figures

- self-test count and failures: `python3 tools/audit/seat/roster_edit.py --self-test` (head and merge base, rule: the printed summary line; checks = printed total − failed).
- mutant table: `python3 tools/audit/seat/r10_roster_ops_mutants.py`; null: `python3 tools/audit/seat/r10_roster_ops_mutants.py --null`.
- gate scope: `python3 tests/closure.py select --diff 106af95a33f89f88f948ea9c49c4632fe74b9416 --workdir "$D"` → `MODE: SCOPED -- 0 script(s) run`, the three changed files all under `tools/audit/` (INERT). Run-always lines run locally, all rc=0: `tests/env_drift.py --claims-only 106af95a33f89f88f948ea9c49c4632fe74b9416`, `tests/closure.py selftest`, `tests/harness_headers.py`, `tests/layout.py`.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL ... ENTITY CHECKS PASSED`, rc=0.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- Architecture score: `python3 tools/audit/archscore/score.py --diff 106af95a33f89f88f948ea9c49c4632fe74b9416` → `Architecture score: dS +0.0000 NULL`.

## Red checks

none

## Forward-carry

none

## Friction

none
