The roster's `resume.stage` is a human claim and nothing compared it with the
repository: twelve complete handoffs sat unopened for up to 96 h while the
roster recorded stale stages. `roster_sync.py` is that comparison, run every
pass by `state_docs.py beat --apply`. Part of #2496.

It derives only what a read measures: a group whose pull request is MERGED is
`done` at the merge commit; one whose pull request is OPEN is `in-progress`
with its number in `resume.pr`; a branch with no pull request, or only a
closed-unmerged one, makes no change -- absence is not evidence. A merged
body's `Carry: <GROUP>` items are appended to the destination group's `carry`
array through `carry_audit.py`'s own parser, and a destination that is done is
refused. A human disposition is never overwritten: `deferred`, `refused`,
`refuted`, `absorbed`, `rca-done`, and any wording neither tuple classifies,
and the self-test refuses an unclassified stage the tree's rosters carry.

Branch matching is the design's B13 rule (`handoff/orch-machinery` 09174d94,
6.4): the topic is the basename of `resume.branch` (else the lowercased group
id), and a pull request's head matches when its name, minus a `handoff-body/`,
`handoff/` or `fix/` prefix and a trailing `-pr`, equals the topic or starts
with `<topic>-`. An exact-name rule finds 2 of the live roster's 48 merged
groups; this rule finds 47.

The write path is one. `roster_edit.commit_roster()` is `main()`'s own tail,
extracted and called by both, so the dump, the round-trip no-op rule and the
lint gate cannot drift apart; `roster_edit.py`'s existing ops and their no-op
behaviour are unchanged. A dry run is the default. `beat --apply` runs the
step before its memo check, because a pull request can open or merge without
moving a ref the beat watches.

## Head

a6d8a78ef832228a702070bc86c307319babcdcc.
Live figures below were taken at roster ref `origin/handoff/audit-r10-roster`
96f38ff88830 and `origin/main` efc0e67332d0, 2026-10-20T18:37Z.

## Mutation proof

`python3 tools/audit/seat/r10_roster_sync_mutants.py` (null first:
`--null` prints `RESULT mutant=NULL_no_plant rc=0 fails=0`) applies one
one-occurrence replacement to `roster_sync.py`, runs its self-test, and
restores the file. Every plant is red with a named check, never a crash:

| arm | mutant | rc | fails | failing check |
|---|---|---|---|---|
| a deferred overwritten | `M1_deferred_overwritten` | 1 | 2 | `a deferred stage is never overwritten` |
| open PR not in-progress | `M2_open_not_in_progress` | 1 | 2 | `open PR: stage in-progress with its number` |
| merged PR not done at the merge commit | `M3_merged_without_commit` | 1 | 2 | `merged PR: stage done at its merge commit` |
| Carry: to a done group appended | `M4_carry_to_done_appended` | 1 | 2 | `a Carry: to a done group is refused, not appended` |
| a second parser used | `M5_second_parser` | 1 | 2 | `carry_audit's parser is used: a quoted marker in a code span routes nothing` |
| `--apply` absent yet bytes written | `M6_dry_run_writes` | 1 | 1 | `dry run creates no roster branch (no --apply writes nothing)` |

## Null control

- A dry run writes nothing: `roster_sync.py` against the live roster prints
  `dry run: 6 stage change(s), 8 carry append(s) would be written` and the
  roster branch's tip is unchanged before and after the run.
- A read with no pull requests derives nothing: the same command with an
  empty `--pr-state` prints `no derived change on handoff/audit-r10-roster;
  nothing written`.
- A no-op pass reproduces the roster's bytes exactly: the self-test's second
  `--apply` returns 0, moves no tip and compares the bytes.
- A refused push is recoverable: the self-test rejects a push with a
  pre-receive hook, requires the local branch back at its base (no
  unpushed commit), then clears the hook and requires the retry to land.
- At the merge base the property fails: `r10_roster_sync_base.py` prints
  `base_stage=in-progress` with `base_apply_rc=2` (`--apply` does not exist
  there) and `head_stage=done` with `head_apply_rc=0`; a plain beat at the
  head still leaves `in-progress`, and the deferred group reads `deferred`
  at both ends.

## Figures

`none` below is only for a claim this body does not make.

- `python3 tools/audit/seat/roster_sync.py --self-test` -> 34 checks, 0 failed;
  the whole run 4.9 s wall at load1 33.4 (`uptime`), 2.0 s user.
- `python3 dev/audit/harnesses/r10_roster_sync_base.py` -> `RESULT
  base_apply_rc=2 head_apply_rc=0`, `base_stage=in-progress head_stage=done`,
  `head_noapply_stage=in-progress`, `base_deferred=deferred
  head_deferred=deferred`, `control=PASS`; 20.0 s wall at load1 134.1.
- `python3 -I tools/audit/seat/roster_sync.py --checkout .` -> `6 stage
  change(s), 8 carry append(s)` over the live roster: four `not-started`/
  `in-progress` rows become `done` (`R10-SENSOR-PAYLOAD` #2379,
  `R10-DEEPLINK-HANDLERS` #2452, `R10-HANDOFF-ARCHIVE` #2488,
  `R10-DEPENDABOT-AIOHTTP` #2487) and two `in-progress` rows record their open
  number (`R10-SAV-REASONS` #2511, `R10-ROSTER-OPS` #2513). 15.5 s wall at
  load1 117.2; the roster tip is byte-identical before and after.
- The same command with an empty `--pr-state`: `no derived change ... nothing
  written` (the null control for that count).
- `python3 -I tools/audit/seat/roster_edit.py --self-test` -> 64 checks, 0
  failed; `python3 -I tools/audit/seat/state_docs.py --self-test` -> all
  checks passed. These are the pre-existing write path and the new beat arm.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` -> `38 self-testing,
  38 wired, 0 unwired`.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`, 1:41 wall at
  load1 188.4.
- `python3 tests/harness_headers.py` (under the exclusive gate lease) -> 109
  checks, 14 failed: two are this diff's depth seam, repaired in 026b7250d and
  re-checked by the same scan (`inline_scan` rc 0); eleven are
  `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py` killed at its own
  900 s wall limit (rc 124, so each RESULT printed None) and one is that
  harness's D9 neighbour `h7_memory_gate.py`'s `inject2x` probe -- files this
  diff does not touch, run at load1 111-133.
- `python3 tests/entities.py` was started and left to CI: 46 min wall and
  5:53 CPU at load1 60-190 without completing, against its own 324.8 s
  recording (`tests/closures.json`). The one arm in it that reads a changed
  file -- `tools/audit/seat/state_docs.py --self-test passes, beat arms
  included` -- is `run_self_test()`, run directly here and green.

## Red checks

- `harness_headers` at cbc38425f, `every inlined walk matches the canonical
  helper and no depth root remains`: the new harness computed its root with
  `Path(__file__).resolve().parents[3]`. Answered: the cheaper detector is the
  same check's child, `python3 -c "import sys; sys.path.insert(0,'tests');
  import harness_headers; raise SystemExit(harness_headers.inline_scan())"`,
  which runs in about a second where the enclosing 109-harness run took 9-15
  minutes; it prints rc 0 at this head. The repair is the canonical
  `repo_root()` inlined verbatim, not a suppression.

## Forward-carry

- `ref_privacy.py --check` enforces nothing on a macOS seat: its site scan
  keys on `\b`, and the host's `git grep -E '\bpush\b'` matches no line while
  `[[:<:]]push[[:>:]]` matches 1529 (`git grep -n -I -E` over `tools
  .claude/workflows .github/workflows` at HEAD). Reproduced on main's own
  checkout, so it is not this branch. Carry: R10-POLICY-GATE-SCOPING

## Friction

- ref_privacy: unenforced: the host's `git grep -E '\b'` finds no word
  boundary (0 lines where `[[:<:]]` finds 1529), so `--check` refuses 16
  registered pushers as holding no push site and a local #2310 guard is
  green-on-nothing on every macOS seat; the same refusal prints on main's
  checkout. Carry: R10-POLICY-GATE-SCOPING

## Approval

Behaviour change: `state_docs.py beat` gains `--apply`, which each pass runs
`roster_sync.py` and, on measured evidence only, writes `resume.stage`,
`resume.commit`, `resume.pr` and a destination group's `carry` through
`roster_edit.py`'s lint gate; the default (no `--apply`) is unchanged, and the
new one-shot form is a dry run unless `--apply` is given. Rollback: revert this
commit; nothing reads `resume.pr` and no other behaviour moved.
