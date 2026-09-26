_Requested by **tvofi**_

Readiness PR R1 of audit round 9 (the round-9 plan, section 3, row R1; section 4 is the spec). R1a (#1633, merged `c9453921`) taught the pinned `check-wave-script.mjs` the scoped shape; this branch has merged `origin/main` at `c9453921`, so `wave-script` grades it with that checker.

`.claude/workflows/audit-find.js` now dispatches from `tools/audit/scopes.json` instead of `planSeats`:
- **Seats.** One finder per seat of `args.scopes` (the parsed committed file; the runtime has no filesystem), id `<dim>-s<n>`; every step its blocks name is a deep focus, since the scopes are disjoint within a dimension. `planSeats` and `WAVES` are gone; `ISOLATED`, `API_DIMS` and `LEDGER_DIMS` are unchanged, and an isolated seat gets its own worktree.
- **Round 9 runs all fifteen dimensions** (`EVERY_DIM_ROUNDS`, the plan's section 2 default 1); the cadence is otherwise unchanged.
- **Boxes.** The `DISPATCH` block places every seat on the plan's section 4.3 box. `boxGaps` refuses a seat on no box or two, a box naming a seat the scopes lack, more than three compute-heavy seats on a box, or anything beside the Chromium seat, and the driver throws on any gap before Prepare. `args.box` runs one container's seats and pushes their evidence to `handoff/audit-r<round>-find-<box>`; `args.from: "intake"` gathers every box; with neither, every box runs in turn here.
- **Prepare** also compares `args.scopes` with the committed file and runs `tools/audit/check_scopes.py --repo <repo> --ref <baseline>`. The round is refused before any finder unless the returned exit status is the integer `0`: an absent or textual rc is refused too.
- **Finder prompt**: its seat's blocks, the `check_scopes.py --seat <id>` command that resolves them, the scope wall and the `leads` field (`COMMON.md`, merged in #1627), `scope` and `class_guess` on every finding. The runtime schema requires every field `finding.schema.json` requires.
- **Leads** go to one leads seat on B10 after the fan-out. The plan's "to the owning seat if it is still running" has no form in `agent()`, which takes no input once dispatched, so every lead waits for the fan-out; the leads seat first reads the owner's report so a measured lead is closed, not re-measured.
- **Intake replaces Dedup**: the script rejects a finding whose `scope` is not the seat that returned it, whose id is not numbered under that seat, or whose `class_guess` is neither a ledger id nor `new`. The intake agent validates against `finding.schema.json` and writes one register row per finding, never merging; dedup is the judge's (`judge.md`).
- **Quiet window**: the timing re-takes leave for the judge's batch re-runner (plan section 6.2, R3). D3's full-gate confirmation stays here, once per round before intake, because `tools/audit/briefs/D3.md` step 3 makes a D3 mutant a finding only through it.
- **`rotation.json`** keeps recording per dimension `coverage` and `unfinished`, plus `returned` (findings accepted per seat) and `leads` (raised, converted), the plan's section 10 record; `yield` stays the verification pass's. Its `_rule` names `returned` and `leads` and no longer says the driver dispatches from it; `_seeded` no longer says round 9 dispatches on step order. In a `from: "intake"` run the leads seat is told the owners' reports are on the `handoff/audit-r<round>-find-<box>` branches.

`check-wave-script.mjs` drops R1a's `planSeats` arm. `audit-wave.js` loses a comment naming `WAVES`.

**Code-owned**: `.claude/workflows/audit-find.js` carries `@tvofi` in `CODEOWNERS` (a graded artifact the checker evaluates), so this needs an approving review as tvofi. It is not policy under `CLAUDE.md`. The delivery row `docs/delivery/<N>.md` is written by the Mac seat once the pull request number exists.

## Head

`2b1ddd10`

## Mutation proof

Tests first: this head's checker against the base driver (`git show 81f2c18c:.claude/workflows/audit-find.js`) exits 1 with `the dispatch block is delimited in audit-find.js no DISPATCH:BEGIN..END block`.

Each one-line mutant of `audit-find.js` at this head was applied one at a time and restored. Each exits 1 with the named check; the restored tree prints rc 0, 0 failed.
- The scopes rc refusal removed → `Prepare refuses the round when check_scopes.py exits non-zero, before any finder`.
- `scopes_rc !== 0` changed to `> 0` → `...and when the exit status was not read at all (an absent rc is not a pass)`, and `...and when it came back as text rather than the integer the shell returned`.
- The `scopes_ok` refusal removed → `a scopes table that is not the committed file stops the round before any finder`.
- `EVERY_DIM_ROUNDS` emptied → `round 9 runs all fifteen dimensions (the round-9 plan, section 2 default 1)`.
- `seatsFromScopes` drops a dimension's last seat → `one seat per scopes.json seat, id <dim>-s<n>, nothing added or dropped`.
- `args.box` ignored → `box B8 runs exactly its seats, collects, and does not run intake`.
- The heavy cap raised from 3 to 4 → `the check fires: a fourth heavy seat on a box is refused (positive control)`.
- The placement refusal removed → `scopes the boxes do not match are refused before Prepare`.
- **The review's three**, each now killed by a fixture that is wrong in one way only:
  - `boxGaps` `n !== 1` changed to `n === 0` → `the check fires: a seat listed on two boxes is refused (positive control)`, and `the check fires: a seat listed twice in one box is refused (positive control)`.
  - The intake id predicate deleted → `a finding scoped to its own seat but numbered under another seat's id is rejected (D1-s1-03 returned by D1-s2)`.
  - `workdir` always returning the export → `an isolated seat works in its own worktree, and an export seat in the export (D0-s2 and D14-s3 vs D5-s1)`. The stubbed Prepare now returns one worktree per isolated seat.
- The intake scope predicate removed → `a finding carrying another seat as scope, or an unknown class guess, is rejected at intake; its sibling is registered`.
- `CLASS_GUESS` loosened to `/./`, its `$` dropped, or its `^` dropped → `class_guess is anchored at both ends (P3x and xP3 rejected)`.
- The intake refusal on a missing seat removed → `a seat that never reports (null after one retry) refuses intake and is named missing`.
- The converted-lead owner check removed, or its id-under-owner check removed → `a converted lead must carry a seat as scope and an id under it: D1-51 and D1-s4-51 rejected, D1-s3-51 registered from the lead`.
- The `box`/`from` exclusivity removed → `box and from "intake" together are refused before Prepare`.
- The per-round box filter removed → `a round that runs a subset places only the active seats (round 10, box B3: D0-s3 and D3-s3, no D11 or D13)`.
- The seat's blocks dropped from the finder prompt → `each finder's prompt carries its own seat's blocks from scopes.json`.
- The box-branch note dropped from the leads prompt → `in a from "intake" run the leads seat is told the reports live on the box evidence branches, and a box run is not (null control)`.
- `leads` dropped from the finder's return schema → `the finder's return schema requires every field finding.schema.json requires`.
- The D3 confirmation skipped → `D3's survivors are confirmed by a full gate under the lease before intake (D3.md step 3), once per round`.

24 of 24 killed.

The script's `CLASS_GUESS` checks shape only, because the runtime has no filesystem to read the ledger from. Membership (`P99` refused) is the schema enum's, which the intake agent validates against.

## Null control

Each refusal test is paired with the unperturbed drive. The committed `scopes.json`, `scopes_rc: 0` and `scopes_ok: true` dispatch every seat and reach intake. The intake fixture rejects exactly its five wrong findings while `D1-s2-01` registers. A round with no lead calls no leads seat, a box run calls no quiet window, and a box-run leads prompt names no box branch. Every finder other than D14's keeps the earlier-findings wall. The `boxGaps` controls end with `boxGaps({}, [])` refused.

## Figures

- `node .claude/workflows/check-wave-script.mjs` at `2b1ddd10`: rc 0, `N passed, 0 failed` (the instrument's tally line; the deliberate `(probe, expected)` FAIL is discounted by it).
- `main`'s checker (`git show origin/main:.claude/workflows/check-wave-script.mjs`, at `c9453921`) against this driver: rc 0, 0 failed. That is the copy `wave-script` restores.
- `python3 tools/audit/round6/D11/fix/codeowners_gap.py --check` at `2b1ddd10`: rc 0, `RESULT uncovered_files=0`.
- `python3 tools/audit/check_scopes.py --repo . --ref HEAD` at `2b1ddd10`: rc 0, one `ok` per dimension, 0 `FAIL`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 0 script(s) run`.
- `python3 tests/structure.py`: rc 0. `node .claude/workflows/policy_lint.mjs`: rc 0, `TOTAL: 0 error(s)`.

## Red checks

none. The fix review's `blocked vacuous-pins` is a verdict, not a check, and it is answered in Mutation proof above. The `codeowners_gap` finding on R1a's fixture is answered in #1633's body; this head carries its fix, and `--check` is clean here.

## Forward-carry

none

## Friction

- decision-0013: cost: a pinned grader that pins a graded artifact's shape makes any change to that shape two pull requests; this is the second of them.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
