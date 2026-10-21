R10-ROSTER-OPS. `tools/audit/seat/roster_edit.py` gains `set-after <group> <G1,G2,...|->` and `drop-carry <group> <index|--match TEXT>`, so the orchestrator applies a replan or drops a stale carry through the load-validate-dump flow instead of a string splice. Both ride the existing lint gate and no-op path unchanged.

Decisions, for the reviewer to judge:
- `set-after` replaces the edge list whole (a replan states the new set); it refuses an unknown target or after-group, a self-edge, a repeated edge, and any cycle in the resulting after-graph (a full DFS over every group's edges, so a pre-existing cycle elsewhere is refused too — the task's "cycle in the resulting DAG").
- `drop-carry` takes a 0-based index (`jq '.carry[N]'`) or `--match`, a substring that must hit exactly one entry; no match and more than one are refused, and an ambiguous match names the matching indices. Dropping the last entry leaves `"carry": []` and never deletes the key: 27 of the 91 live groups carry that empty shape, 64 carry entries, and none omits the key, so deleting it would rewrite the 27 groups' bytes. Append-carry then drop-carry of the appended entry therefore restores the bytes of every group the roster has, pinned on a fixture group that starts with `"carry": []` (the live shape, not the key-less one the earlier arm used).
- The new refusal arms assert the refusal's text through a `refuses()` helper, not only rc 2: argparse also exits 2 for an unknown op, so an rc-only arm passes on a tree without the op (the red run below shows those arms failing only once they key on text).
- Alternatives not taken: `set-after --add/--remove` deltas (two ops' worth of surface for the same result; a whole-list write is what a replan carries); exact-equality `--match` (a carry entry is long prose, a substring is what an orchestrator can type; ambiguity is refused rather than guessed).
- Ownership: `.github/workflows/governance.yml` is under `/.github/workflows/ @tvofi` in `CODEOWNERS`, so landing this pull request needs tvofi's approving review. `tools/audit/seat/roster_edit.py` and `tools/audit/seat/r10_roster_ops_mutants.py` carry no owner; `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` classifies both `NO-PR-JOB`. The delivery row `dev/programme/delivery/2513.md` is carried by the head (`514ea584b`); this diff adds no second one.

## Head

`cf0a823108a655216c5208314a0267581085a3c5`, merge base `df6ca4bc6858f2796f694035e6f53e46e237e33b` (origin/main tip `0cc148b2f80fe224ffe2c504b29fd4f0908183df` at 2026-10-21T08:55Z). This head merges the PR head `716a34f28`, the handoff tip `4e2223a57` (the `instrument-self-tests` wiring commit `cf90776b5` and the drop-carry fix `4e2223a57`) and origin/main; the only conflict was the delivery row `dev/programme/delivery/2513.md`, both sides one line, resolved to the PR head's (the CI-written one). `git diff origin/handoff/r10-roster-ops HEAD -- tools/audit/seat/roster_edit.py tools/audit/seat/r10_roster_ops_mutants.py .github/workflows/governance.yml tools/audit/seat/INSTRUMENTS.md` prints nothing, so those four files are the handoff's byte for byte. Figures below were measured at the merge before the last origin/main merge, which touches none of this diff's five files.
The local `prepr` ran with `PREPR_SKIP_CLOSURES=1` (owner ruling, 2026-10-20), as before.

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
| C6 | the last drop deletes the `carry` key | drop-carry of the last entry leaves the key empty; append-carry then drop-carry is byte-identical |
| C7 | index drops the neighbour | drop-carry by index drops that entry (+3 downstream) |
| C8 | drop-carry unknown group writes a detached dict | drop-carry unknown group refused |
| P1 | "index and --match, not both" error removed | drop-carry index and --match together refused (+3 downstream) |
| P2 | "needs an index or --match" error removed | drop-carry neither index nor --match refused |
| P3 | "--match is a drop-carry flag" error removed | set-after names no op flag; --match on another op refused (+2 downstream) |
| D1 | dump indent=2 (the round-trip) | dump round-trips the canonical bytes; no-op set-resume is byte-identical; no-op set-after is byte-identical |

Driver summary line, one full run at this tree: `plants: 19, without a FAIL line: ['A5', 'A6']`; those two printed `crash tail` (`git ... failed to insert into database`, `unable to index file`), not a surviving mutant, while the volume under the throwaway repositories sat at 99% (`df -h /var/folders`, 1.9Gi free) and load1 was ~190. Re-run alone, `r10_roster_ops_mutants.py A4 A5 A6` printed `plants: 3, without a FAIL line: none` (A4 had also crashed in an earlier full run under the same conditions). Every plant therefore has a FAIL line in a run whose host could write; the driver correctly reports a crash as not-killed, which is why the first two runs read red.

Failing test first: the new arms run against the tree with the arms and without the ops printed `roster_edit self-test: 121 checks, 27 failed` — 94 checks; the printed total double-counts failures, a pre-existing quirk of `check()` this diff leaves alone. All 27 failures are new arms.

## Null control

`python3 tools/audit/seat/r10_roster_ops_mutants.py --null` at this tree: `RESULT mutant=null rc=0 fails=0`. `python3 tools/audit/seat/roster_edit.py --self-test`: `roster_edit self-test: 94 checks, 0 failed` at the head and `64 checks, 0 failed` at `df6ca4bc` (a detached worktree there).

Round-trip on the live shape. A throwaway repository is seeded with `dev/programme/rosters/wave-r10-groups.json` and a bare origin; then `python3 -I tools/audit/seat/roster_edit.py append-carry R10-UPDATE-PR-LOCK 'probe round-trip' --checkout . --roster-ref main --branch edit-1 --worktree ../wt --push`, then the same command with `drop-carry R10-UPDATE-PR-LOCK 0`. The group before: `"carry": []`; after: `"carry": []`; sha256 `99274ddc4108bbce88f9aa7453ecd7830bc1c3fd6e0b4b57fec95e2ad750ca37` at both ends and `cmp` clean. Control at `514ea584b`'s `roster_edit.py` (the delete-key behaviour this diff removes): the same pair leaves the key absent and `cmp` differs at line 4853.

The live shape census, rule `carry` key presence and value in `dev/programme/rosters/wave-r10-groups.json`: 91 groups; 64 carry entries, 27 carry `"carry": []`, 0 omit the key.

Live roster, scratch worktree off origin/main, no `--push`, worktree and branch deleted after: `set-after R10-STORE R10-CURRENCY` (its current edge) printed `no change: ... (byte-identical)`, and `git diff --quiet origin/main -- dev/programme/rosters/wave-r10-groups.json && echo LIVE-ROSTER-BYTE-IDENTICAL` printed it; `set-after R10-CURRENCY R10-STORE` printed `REFUSED: ... closes a cycle: R10-CURRENCY -> R10-STORE -> R10-CURRENCY`. Disclosed self-correction: a first live probe named the wrong current edges for R10-STORE and so made a real local commit; nothing was pushed, and that worktree and branch were deleted before the probe above.

## Figures

- self-test count and failures: `python3 tools/audit/seat/roster_edit.py --self-test` at the head and at `df6ca4bc` (rule: the printed summary line; checks = printed total − failed).
- mutant table: `python3 tools/audit/seat/r10_roster_ops_mutants.py`; null: `python3 tools/audit/seat/r10_roster_ops_mutants.py --null`; the harness's own preconditions: `python3 -I tools/audit/seat/r10_roster_ops_mutants.py --self-test` → `r10_roster_ops_mutants self-test: 63 checks, 0 failed`.
- wiring: `python3 -I tools/audit/seat/selftest_wiring.py --check` → `38 self-testing, 38 wired, 0 unwired`.
- round-trip probe and the live-shape census: commands under `## Null control`; before/after sha256 `99274ddc41…`.
- gate scope: `python3 tests/closure.py select --diff df6ca4bc6858f2796f694035e6f53e46e237e33b --workdir "$D"` → `MODE: SCOPED -- 2 script(s) run`, 5 changed files (the two seat instruments, `INSTRUMENTS.md`, the workflow, the delivery row).
- `python3 tests/structure.py` at this head: `STRUCTURE RATCHET PASSED`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- Architecture score: `python3 tools/audit/archscore/score.py --diff df6ca4bc6858f2796f694035e6f53e46e237e33b` → `Architecture score: dS +0.0000 NULL`.

## Red checks

- `instrument-self-tests` at `716a34f2` (the PR head): `UNWIRED tools/audit/seat/r10_roster_ops_mutants.py: no workflow run line names its self-test`, `selftest_wiring: 38 self-testing, 37 wired, 1 unwired`. Answer: the cheaper detector exists, `python3 -I tools/audit/seat/selftest_wiring.py --check` (under a second, no standing cost beyond that); it ran on no local path of this branch. The wiring line is in `governance.yml` at this head and the check now prints `38 self-testing, 38 wired, 0 unwired`, rc 0. The PR head lacked the wiring commit because the handoff and the PR were pushed apart (the fixer's host rebooted between them); this head carries both.
- `nightly-status` at `716a34f2`: grades `main` (the nightly `slow` lane's `loop_cpu_ratio` over budget, fixed by the separate `r10-replay-cap` work); this diff touches none of what it reads (its scripts, `tests.yml`, `governance.yml`'s nightly jobs, the plan, `HANDOVER.md`) -- the one `governance.yml` hunk adds a step to `instrument-self-tests`. Not this PR's.

## Forward-carry

none

## Friction

none
