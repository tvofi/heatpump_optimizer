The roster's `resume.stage` is a human claim and nothing compared it with the
repository, so a group whose pull request merged stayed `in-progress`. `roster_sync.py` is that comparison, run every
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
with `<topic>-`.

The write path is one. `roster_edit.commit_roster()` is `main()`'s own tail,
extracted and called by both, so the dump, the round-trip no-op rule and the
lint gate cannot drift apart; `roster_edit.py`'s existing ops and their no-op
behaviour are unchanged. A dry run is the default. `beat --apply` runs the
step before its memo check, because a pull request can open or merge without
moving a ref the beat watches.

This round (the opener's refusal): prepr's layout guard refused three fixture
lines seeding the retired `.claude/workflows/brief_lint.mjs`. They now seed
`tools/policy/brief_lint.mjs` -- `roster_edit.BRIEF_LINT_NEW` in
`roster_sync.py` and `state_docs.py`, the literal in the harness, which also
runs against the base tree (whose `roster_edit.py` carries the same
old-then-new fallback, so seeding the new path works at both ends).
`roster_sync.py` is now registered in `tools/audit/seat/INSTRUMENTS.md`, and
the `state_docs.py` entry names `beat --apply`. `roster_sync.py`'s `SHA_RE` is
now `roster_edit.SHA_RE`: the agreement lane refused the regex
`\A[0-9a-f]{7,40}\Z` written in both files and unregistered, and the alias
removes the second copy rather than registering a pair.

Composition with #2513 (R10-ROSTER-OPS, `roster_edit.py` set-after and
drop-carry): both touch `roster_edit.py` and `INSTRUMENTS.md`, in disjoint
hunks. This diff extracts `commit_roster()` from `main()`'s tail; #2513 adds
ops above it and dispatch arms in `main()`, and appends to the `roster_edit.py`
entry where this one adds a separate `roster_sync.py` entry after
`roster_lib.py`'s. Neither order needs a resolution: see `## Figures`.

## Head

`d87648d02b63a4c5e5f70573d1a10d2060b509a6` merges origin/main `265d3bf1a` into the authored code head `66bd5b4c80a0b2cb0ee164be456f8d7ea519b4a3` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

This round is the body alone: the code head is unchanged at `d87648d02b63a4c5e5f70573d1a10d2060b509a6`,
and only the two `Carry:` destinations below and `## Red checks` moved (see
pr-contract there).

66bd5b4c80a0b2cb0ee164be456f8d7ea519b4a3, merge base and `origin/main`
0cc148b2f80fe224ffe2c504b29fd4f0908183df at 2026-10-21T08:57Z. It merges
`origin/main` into the previous handoff tip a6d8a78ef (no conflict) and adds
three commits: the moved-path fix, the INSTRUMENTS.md registration, and
`roster_sync.py` taking `roster_edit.SHA_RE` instead of a second spelling of
the same grammar (prepr's agreement lane refused it). Every
figure below was taken at this head.

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

The moved-path fix's own proof is the layout guard read at both ends:
`python3 -I tests/layout.py --guard --base 0cc148b2f80f` printed `layout:
GUARD: 3 refusal(s)` at the merge of main (32fcfae00, the three
`new-reference: ... cites retired path .claude/workflows/brief_lint.mjs`
lines) and `GUARD: 0 refusal(s)` at the head. The SHA_RE alias likewise:
`python3 -I tools/policy/agreement_py.py --out ag.json && node
tools/policy/agreement.mjs --py-json ag.json` printed `UNREGISTERED
"\\A[0-9a-f]{7,40}\\Z" in tools/audit/seat/roster_edit.py,
tools/audit/seat/roster_sync.py` and `RESULT ... unregistered=1` at
34466347c, and `unregistered=0`, `AGREEMENT ok` at the head.

## Null control

- With no plant the mutant driver's self-test run is green: `--null` prints
  `rc=0 fails=0`.
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
- The layout guard's null control is the pre-fix commit above: the same
  command, three refusals.

## Figures

- `python3 tools/audit/seat/roster_sync.py --self-test` -> `roster_sync
  self-test: 34 checks, 0 failed`.
- `python3 tools/audit/seat/roster_edit.py --self-test` -> `64 checks, 0
  failed`; `python3 tools/audit/seat/state_docs.py --self-test` -> `all checks
  passed`.
- `python3 tools/audit/seat/r10_roster_sync_mutants.py` -> the table above, rc 0.
- `python3 dev/audit/harnesses/r10_roster_sync_base.py` -> `RESULT
  base_apply_rc=2 head_apply_rc=0`, `base_stage=in-progress head_stage=done`,
  `head_noapply_stage=in-progress`, `base_deferred=deferred
  head_deferred=deferred`, `control=PASS`.
- Moved paths, rule `python3 tools/audit/seat/moved_paths.py` over the three
  files the guard refused -> `0 hit(s) in 3 file(s)`. Over every file the
  three-dot diff names, the remaining hits are on lines this diff does not add
  (the guard keys on added lines and prints 0), each an existing
  old-then-new `test -f` fallback in `governance.yml`, a recorded path list in
  `tests/closures.json`, or `roster_edit.py`'s own `BRIEF_LINT_OLD` fallback
  and its pre-existing self-test fixtures, which are main's and #2513's file.
- Composition with #2513: a detached worktree at this head, `git merge
  origin/fix/r10-roster-ops` (716a34f28) -> `Auto-merging
  tools/audit/seat/roster_edit.py`, no conflict; on the merged tree
  `roster_edit self-test: 94 checks, 0 failed`, `roster_sync self-test: 34
  checks, 0 failed`, `state_docs self-test: all checks passed`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` -> `38
  self-testing, 38 wired, 0 unwired`.
- `python3 -I tools/audit/seat/tmp_paths.py --check` -> `0 refused`.
- Gate scope: `python3 tests/closure.py select --diff 0cc148b2f80f` -> `MODE:
  SCOPED -- 2 script(s) run, 31 scoped out`, 8 changed files; RUN
  `tests/entities.py`, `tests/harness_headers.py`.
- `run_always` lines: `tests/env_drift.py --claims-only` -> `claims hygiene:
  ... ok`; `tests/closure.py selftest` -> `ALL 124 closure shrink pins
  PASSED`; `tests/layout.py` -> `layout self-test: ok`.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` (same
  venv) -> `ALL 2363 ENTITY CHECKS PASSED`, rc 0, 407 s wall. The 46 indented
  `FAIL` lines in its output are the nested probes' planted negatives
  (`a3:roster` against a one-entity fixture, `sensor.x` with a NaN), which the
  enclosing checks expect; the summary line is the result.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` (3.13 venv from
  `tests/requirements-ci.txt`) -> `ALL 109 HARNESS HEADER CHECKS PASSED`,
  rc 0, 151 s wall.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 0cc148b2f80f` ->
  `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/audit/carry_audit.py check --body <body>` against the
  roster at origin/main 03b49e152: the previous body -> `CARRY-AUDIT: 4
  finding item(s): 2 routed, 0 unrouted, 2 bad destination(s)`, rc 1 (the
  null control: CI's refusal reproduced); this body -> `CARRY-AUDIT: 5
  finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)`, rc 0.
- The detectors the brief names do not see this refusal, measured on the
  previous (refused) body: `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh
  <old body>` at d87648d02 -> `PRE-PR: d87648d02b63...`, rc 0; `node
  tools/policy/policy_lint.mjs --pr-body <old body> --head d87648d02...
  --red nightly-status` (main's copy, as CI restores it) -> `PR-BODY: 0
  error(s)`, rc 0. On this body both again read rc 0, and
  `node tools/policy/figure_lint.mjs --pr-body` at the head refuses none of
  this body's figures (its `FIGURES:` line is the count).
- Not re-taken: the previous body's live-roster dry run (`roster_sync.py
  --checkout .` over `origin/handoff/audit-r10-roster`) and the 2-versus-47
  branch-matching count both read `gh pr list`, and `gh` is unauthenticated
  in this seat (`gh auth status`: `Failed to log in to github.com using
  token`). They are removed from this body rather than carried stale.

## Red checks

- The orchestrator's opener, refused by prepr's layout guard (`new-reference`
  on `dev/audit/harnesses/r10_roster_sync_base.py`, and on `roster_sync.py` and
  `state_docs.py`). Answered: the cheaper detector exists and is the same
  command, `python3 -I tests/layout.py --guard --base <merge-base>`, about a
  second; no step a fixer runs before handoff invoked it, and `body_push.sh`'s
  static predictor passes the refused tree (measured in `## Forward-carry`,
  carried there).
- `harness_headers` at cbc38425f, `every inlined walk matches the canonical
  helper and no depth root remains`: the new harness computed its root with
  `Path(__file__).resolve().parents[3]`. Answered: the cheaper detector is the
  same check's `inline_scan()`, about a second; the repair is the canonical
  `repo_root()` inlined verbatim (026b7250d), not a suppression.
- `pr-contract` at d87648d02, step `carry_audit.py check --body`:
  `BAD-DEST body item b79e7e68` and `00bf85b5`, `R10-ORCH-MACHINERY is not a
  group of the roster` (the design note's group name, never added to
  `wave-r10-groups.json`). Answered: both items now carry to `#201`, owned
  through `dev/programme/carries/carry-201.json`, the in-tree brief of a stage
  with no live roster group; no live group's brief names `ci_predict.py` or
  `cloud_dispatch.py`. The cheaper detector is the same command run on the
  body file before `body_push.sh`, `python3 -I tools/audit/carry_audit.py
  check --body <body.md>`, under a second; neither `policy_lint.mjs
  --pr-body` nor `prepr.sh` nor `body_push.sh`'s predictor runs it (see
  `## Forward-carry`), so the refusal cost one CI round of pr-contract and
  this body seat.
- `nightly-status` is main's, not this branch's: the replay
  `loop_cpu_ratio` budget. Carry: R10-REPLAY-CAP

## Forward-carry

- `body_push.sh`'s static predictor (`tools/pr/ci_predict.py`) does not run
  the layout guard, so a handoff whose diff adds a retired path passes it and
  is refused only at the orchestrator's prepr: at 32fcfae00, where the guard
  printed 3 refusals, `ci_predict.py --base origin/main` printed `CI PREDICT:
  no closures or fast red predicted` with rc 0. Carry: #201
- No pre-push instrument runs the body's carry audit: `grep -rn carry_audit
  tools/pr/ tools/audit/seat/*.sh .github/workflows/*.yml` names only
  `pr-contract.yml`'s `check --body` step and `governance.yml`'s self-test, so
  a body with a destination outside the roster passes `prepr.sh` and
  `body_push.sh` and is first refused by CI (this round). Carry: #201
- `ref_privacy.py --check` enforces nothing on a macOS seat: its site scan
  keys on `\b`, which the host's `git grep -E` does not honour (recorded by
  the previous round on main's own checkout). Carry: R10-POLICY-GATE-SCOPING

## Friction

- cloud_dispatch: stale: the cloud fixer payload
  (`tools/audit/seat/cloud_dispatch.py`'s setup line) states that "the toolchain (venv python, node, gh) is on PATH"; in this
  seat `python3` was the system 3.11 without `voluptuous` (so
  `tests/entities.py` died on a 3.12 f-string and `harness_headers.py` on the
  import), and `gh` was unauthenticated. A venv was built from
  `tests/requirements-ci.txt` under 3.13 for the gate runs. The payload's
  brief also names `tools/audit/seat/prepr.sh`, which does not exist; prepr
  is `tools/pr/prepr.sh`. Carry: #201
- ref_privacy: unenforced: the host's `git grep -E '\b'` finds no word
  boundary on a macOS seat, so `--check` is green-on-nothing there (see
  Forward-carry). Carry: R10-POLICY-GATE-SCOPING

## Approval

Behaviour change: `state_docs.py beat` gains `--apply`, which each pass runs
`roster_sync.py` and, on measured evidence only, writes `resume.stage`,
`resume.commit`, `resume.pr` and a destination group's `carry` through
`roster_edit.py`'s lint gate; the default (no `--apply`) is unchanged, and the
new one-shot form is a dry run unless `--apply` is given. Rollback: revert this
merge; nothing reads `resume.pr` and no other behaviour moved.

