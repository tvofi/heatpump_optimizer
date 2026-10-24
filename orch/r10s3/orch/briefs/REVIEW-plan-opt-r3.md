# Fix review — `tools/plan/replan.py` (round 3)

Role: **fix reviewer**, adversarial, one pull request. Read `dev/governance/roles/fix-review.md` first and
`dev/governance/roles/COMMON.md` (the finder's contract). Repository `tvofi/heatpump_optimizer`.
**LOCAL seat only — no cloud.**

Head under review: `f031946e7fe5a3a0430b29d251119c1c46735644`.
Body under review: `9d2d8b05cff167af0ec78ec65ea6073b7ec8d207` (`BODY.md` in that commit).
Branch: `handoff/r10-plan-opt`. Merge base with main: `990e90af9bcd05f283295f90c128ef936e8ba025`.
Pull request: open, or being opened, for `handoff/r10-plan-opt` — find it with
`gh pr list --head handoff/r10-plan-opt --state open --json number,headRefOid`. If it is not open yet, do the
whole review and hold the verdict, saying so; do not review a head that moved without saying the head moved.

## What this is

The fixer added `tools/plan/replan.py`, the one schedule model behind the round-10 plan page: it reads the
roster at a ref (`origin/handoff/audit-r10-roster`), the owner's caps and a measured `tools/plan/durations.json`
and emits `plan.json`; the out-of-tree renderer now draws only what `plan.json` emits. The body's claims are
scheduled figures, so an unfalsified number is the main risk. Round 1 and round 2 verdicts are on the pull
request; read them and confirm each item is actually addressed, then look for what neither round saw.

## What to verify, with your own harness

Do not use the fixer's `~/hpo-seats/r10s3/plan-opt/compare.py`, and do not accept a figure because
`--self-test` printed it. Build your own check for every quantified claim:

1. **The schedule arithmetic.** At roster `e3010676` and start `2026-10-20T17:00Z`, the body claims closure
   `2026-10-30T03:17Z`, 226.28 h, 44 batches, 7 stamps, 5778.4 gate minutes, and a 12-link dependency chain of
   226.28 h. Recompute at least: the chain length in hours from per-group durations; that 44 × gate median
   (113.3) + stamps = the claimed gate minutes; and that no capacity queueing occurs (wall == chain). State
   which numbers you confirmed, which you could not, and with what definition.
2. **The cap and the inherited set.** Three `coordinator.py` groups are in progress against a cap of two, and
   the plan records that in `generated.inherited_coordinator` with `--check` refusing its absence. Plant the
   absence yourself and show `--check`'s exit code and message. Do the same for
   `inherited_dependency_violations`.
3. **The refusals, each in isolation.** Run the self-test; then break one invariant at a time in a copy of the
   plan (over-cap wave; dependency cycle; a group ahead of its dependency; two builds not byte-identical) and
   show each exits 1 or 2 as the body says, in a subprocess, so exit codes are real.
4. **CI measurement.** `--measure-ci` dedupes by (commit, context), keeping the first attempt. Construct a
   duplicate row (two attempts for one commit and context) and show the median is unchanged; then show a naive
   count would have moved it. Check the body's reported medians and n against `tools/plan/durations.json` and the
   named measurement instant `2026-10-20T16:52Z`; a later re-read may legitimately differ — confirm which side
   the committed file names.
5. **Classification.** `tools/plan/` must be inert: `tests/closure.py`'s INERT list and
   `tests/entities.py`'s `_INERT_TOOL_HOMES`; and no gate script opens it. Verify with `closure.is_inert` and by
   grep, not by reading the body.
6. **The body's own contract.** Run the pull request's body checks yourself from a clean checkout of the head:
   `tools/pr/prepr.sh <body> <issues...>` (no issues close) and `carry_audit.py check --body` — 0 unrouted. Check
   the two countable claims at the pinned blob: 40 of the 45 open groups store a wave and five store none;
   one pull request was open at the 16:52Z instant (`#2491`). Three-dot only:
   `git diff $(git merge-base origin/main HEAD)...HEAD`.
7. **The renderer boundary.** The renderer is out of tree. Check only what the tree can show: `plan.json` carries
   every field the renderer needs, the staleness guard (`--check` against a moved roster) exists where the body
   says, and nothing in the tree depends on the out-of-tree file.

## Verdict

Post it with `tools/audit/seat/bus.sh push-verdict <pr> <verdict file> <evidence dir>`; the evidence dir must be
absolute and hold the harness, its output and the planted-case transcripts. Grammar per `fix-review.md`; a
head that moved under the review is `blocked`. A `refute` needs a failing demonstration, not an argument.
Report under 250 words: verdict line, each numbered item confirmed/not, and anything you could not establish.
