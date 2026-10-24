# Fix review — R10-SAV-REASONS, round 2 (revenue attribution)

Role: **fix reviewer**, adversarial. Read `dev/governance/roles/fix-review.md` and `dev/governance/roles/COMMON.md`
first. Repository `tvofi/heatpump_optimizer`. **LOCAL seat only — no cloud.**

Pull request: **#2511**, live head `3449af66` at dispatch — the handoff `4706031025ab4c8652daa252e87ff312114ba19f`
plus CI's mutation-autofix pin commit and the delivery row. Body ref `handoff-body/r10-sav-reasons`.
**The head may move once more** (a recarry): poll `gh pr view 2511 --json headRefOid`, re-run only what the delta
touches, measure at the final head, and **hold the verdict** for a `bus-nonce`.

Work in a detached worktree at the head you measure, under `/Users/timmalmstrom/hpo-seats/r10s3/r10-sav-reasons-review/wt`
(absolute paths). `export PATH=/Users/timmalmstrom/.local/state/hpo/bin:$PATH` — and note the typing ruler needs
`~/.local/state/hpo/venv-ha/bin/python tests/typing_ruler.py --mypy`, because `.venv-typing` does not exist here.
The box is loaded: prefer counts, state load1 beside any wall-clock figure, long runs behind
`tools/audit/seat/daemonize.py --log`.

## What changed since the first handoff

- **The `typing` red is repaired, not suppressed.** `ledger.py` had 2 mypy errors (`arg-type`, `index`) against a
  recorded 0. `explain_metered` now reads its predicate as two branches so the truthiness test narrows `str | None`
  before the share is keyed — no `# type: ignore`, `type_ignores` still 0. Verify the ruler yourself and confirm
  `type_ignores` did not move.
- **The mutation pins landed**: `8d22c38c4` (`ci: pin killed mutants`), merged into the branch rather than main.
- **The ADVISOR carry is already in the roster** — `REASON_LABELS` covering `boost`, `comfort_mode` and
  `system_identification`, carried at handoff `84eb9c1a`. Do not treat its absence from the diff as a gap.

## What to verify

1. **The finding itself.** The booking harness flips a plan-idle step with a 0.4 kWh meter read from
   `reason:idle` to `reason:untagged`, and the classification from `space_reason 'idle'` to `'boost'`. Re-run
   `dev/audit/harnesses/sav_reasons_booking.py` at the merge base and at the head and confirm the flip; a harness
   that does not move under its own perturbation is void.
2. **The typing repair** — the ruler's own output, plus that the change is a narrowing and not a widened type.
3. **The two reds the fixer attributes to this box**: `optimality.py` `1 of 84` (`one|summer_negative|shoulder`)
   and `stress.py` `shoulder: cheaper than holding the setpoint [4.67 vs 3.96]`. The fixer claims both reproduce
   identically at the merge base in a detached worktree. Reproduce that claim yourself; if either does not
   reproduce at the base, the diff owns it and the verdict is `blocked`.
4. **The body's red answers.** `ancestry reds` green means every red this branch pushed is answered: `mutation`,
   `nightly-status`, `typing`. Check each is named and each answer is true at this head.
5. **The rule the fixer asks you to attack first**: a channel whose reason says the plan drew nothing books
   `untagged`, but a channel the plan *was* running keeps its reason at any meter magnitude, on the
   `thermal_model.planned_draw_runs` argument that sub-floor steps are duty cycling within the step. Exhibit a
   draw on a running channel that is not the pump cycling within the commanded step — if one exists, the rule
   mislabels it and the original complaint reproduces at a smaller scale.

## The body and the merge

`prepr.sh` on the body; `carry_audit`; `figure_lint`; the `## Head` names the head and records the closures skip
under the owner's ruling (CI's `closures` context covers it). `tests/stress.py` in the diff means this PR is
**code-owned** — say so; the owner's review approves it at merge.

Post the verdict with `tools/audit/seat/bus.sh push-verdict 2511 <verdict file> <evidence dir>` once the nonce
arrives; a head that moved under the review is `blocked`. No host path in the verdict (#2310) — write `~/…`.
Report under 250 words: verdict line, each item confirmed/not, what you could not establish.
