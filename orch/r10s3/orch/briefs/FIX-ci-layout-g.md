# Fixer — R10-CI-LAYOUT, **PR G only**

Role: **fixer** for one pull request, PR G of the CI-consolidation group. Repository `tvofi/heatpump_optimizer`.
**LOCAL seat only — cloud dispatch is forbidden in this session.**
Read `dev/governance/roles/fixer.md` before you start: failing test first, mutation proof, the finder's harness at both
ends, a null control for every quantified claim, `GATE_SCOPE=auto`, `tests/structure.py` before the push, and the
handoff freezes the branch.

## Read these first, from the refs, never from memory

- **Your own roster entry**: `git -C /Users/timmalmstrom/heatpump_optimizer show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json` then `jq '.groups[]|select(.group=="R10-CI-LAYOUT")'`. Its `brief` and `carry` list are the specification; this file only narrows them to PR G.
- **The approved design**: `probe/design-ci-rev4` at `1371a0a6`, approved by `probe/design-ci-review5` at `afc00bfe` (its REVIEW.md under *Non-blocking*). The plan addendum A1–A6 and its review are approved too; if the design text and the roster brief disagree, the roster brief wins and you say so in the body.
- **PR 0** is merged (`#2464`): the umbrella stub and the three ci-ratchet payments are on main. Do not redo them.

## What PR G is

Cut from fresh `origin/main` (after `#2444` and `#2464`). Scoped CI. **Code-owned** (`governance.yml`), so the owner
approves at the merge; write the body for that reader.

1. **Wire the unwired self-tests into CI.** `#2444` found seven self-tests outside `tools/audit/seat/` that no workflow
   runs: `check_scopes.py`, `merge_throughput.py`, `worktree_gc.sh`, `tools/coverage/partition.py`,
   `tools/policy/record-predicate/row_files_replay.py`, `pr/approve_held_runs.sh`, `pr/head_note.py`. **Derive the
   set with the carry's own command — do not carry the seven from this brief** (the roster's carry gives the `git grep`
   rule and its expected 24 wired / 7 unwired split at `#2444`'s head; re-take it at your base). Then widen
   `tools/audit/seat/selftest_wiring.py` to those directories so the wiring cannot lapse again, wire the files into
   `governance.yml` (or its successor), and give the lane a **planted failing case** (a self-testing file with no
   workflow mention must make the check exit 1) and a **null control** (the files that already run in CI stay green
   and keep their names, so the required-check list is unchanged).
2. **Give the unpinned push and merge lines their own offline seams.** `#2444` measured four lines pinned by nothing:
   `handoff_push.sh`'s three push lines (75, 94, 108 at that head) and `merge_pr.sh` line 169 (`gh pr merge …`). Build
   offline seams so each mutant turns its self-test red where today it stays green. The carry states the exact
   mutant → expected `rc` table and the null control; **re-find the line numbers with `grep -n` at your base** and
   re-take every `rc` before relying on it. `open_pr.sh` line 44 and `update_pr.sh` line 58 are already pinned — do not
   build seams for those.
3. **Derive the wave-script restore list from the importers' closure of `agreement_py`.** `governance.yml`'s wave-script
   job restores a hand-listed set of base readers that omits `tools/release/stamp.py` and `tests/delivery_status.py`,
   so a head with a consistent agreement read `divergent=2`. Derive the list (not by hand) from every importer of the
   agreement reader, add what is missing, and show with a **planted divergence** in one of them that the job turns
   red; the unplanted head is the null control.
4. **Re-run `#2444`'s own checks at your head**: `python3 tools/audit/seat/selftest_wiring.py --check`, and its mutant
   harness. Its results are a precondition, not a formality.

## Environment

- Scratch: **`/Users/timmalmstrom/hpo-seats/r10s3/ci-layout-g`** (absolute; create it). Worktree under it:
  `git -C /Users/timmalmstrom/heatpump_optimizer worktree add /Users/timmalmstrom/hpo-seats/r10s3/ci-layout-g/wt -B handoff/r10-ci-layout-g origin/main`.
- `export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH` so the seat python is the pinned 3.14.
- Instruments: `/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/` and `tools/pr/`. Do not hand-roll a loop, relay, queue or watcher — the inventory is `INSTRUMENTS.md`.
- The box is shared: take wall-clock numbers with `load1` beside them, prefer counts and structural facts, and let CI be the authority for anything heavy.

## Handoff

- Push the code head to `handoff/r10-ci-layout-g` and the body to `handoff-body/r10-ci-layout-g` with `body_push.sh`.
  The orchestrator opens the pull request — **you write no GitHub**.
- The body owes the template's sections (`## Head`, `## Mutation proof`, `## Null control`, `## Figures`,
  `## Red checks`, `## Forward-carry`, `## Friction`), every figure with the command that printed it, and every
  finding a `Carry: <dest>` marker. `carry_audit.py check --body <body>` must print 0 unrouted.
- **No host path anywhere** in a ref name, commit message or body (#2310): write `~/…`, never the absolute path.
- Report back: both ref SHAs, the derived wiring set with its command, each mutant's `rc` before and after, the
  derived restore list and the planted-divergence result, and anything you could not establish.
