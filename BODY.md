The soft cap bounded the wrong door: it refused **opening**, and opening is how work
leaves work in progress. Complete handoffs were parked unopened while the quantity
the cap exists to bound — roster groups in progress — was not measured at all. The
owner's ruling (tvofi, 2026-10-20, restated 2026-10-21): the soft cap of 6 gates
only starting or dispatching a new roster group; opening or updating a pull
request for an owed handoff is never refused by it. A new group now enters the
pipe only while fewer than `HPO_WIP_CAP` (default 6) roster groups have
`resume.stage: in-progress`.

**Behaviour change.** `pr_cap.py dispatch-gate` (new) counts WIP through
`roster_lib` at the roster ref, refuses at or over the cap and prints the WIP group
ids. `open_pr.sh` prints the open count and always proceeds; `--over-cap
"<reason>"` is still accepted, says it is advisory, and changes nothing.
`update_pr.sh` never consulted the cap and still does not. The tick's level line
becomes `WIP: N/6 (open PRs M)`. The ruling is stated in the same words in
`dev/governance/roles/orchestrator.md` §5, `tools/audit/seat/INSTRUMENTS.md`
(`open_pr.sh`, `cloud_relay.sh`, `pr_cap.py`) and `pr_cap.py`'s docstring.
**Rollback:** reverting this head restores `pr_cap.py`'s `gate`, `open_pr.sh`'s
gating call and the tick's `OPEN-PR CAP` line in one commit; `dispatch-gate` has
no other caller.

**This round (returned for repair).** `policy-docs` and `env-matrix` were red on
`FIXTURE VACUOUS: checkCitationPresence reported 1 of 2 earned exclusions`. Cause:
the §4 paragraph rewrite put decision 0010's citation on an added line under its
live path; pull-request CI restores `tools/policy/*.mjs` from the base before
running (`governance.yml`, "Restore the check source from the base commit"), and
the base's arm B elides only the canonical spelling. The previous round's edit to
`policy_lint.mjs` therefore never ran in CI. Repair: §4's paragraph is restored
byte-identical to main, so the citation stays on an unchanged line under its
canonical spelling, and the `policy_lint.mjs` edit is dropped (with no live-path
citation in the corpus it pinned nothing). `tools/policy/` is now untouched.

## Head

`5d477d6e9d3b0f71f64cbdc92d04fb3d7e79cf8f`

## Mutation proof

- **(a) opening still refused at the cap.** At this head with `pr_cap.py` replaced
  by main's (sha1 `96b81797ed9aaad0abc1ad4dc5c17278023854c2`), `bash
  tools/audit/seat/pr_args.sh --self-test` prints `pr_args self-test: 54 checks, 6
  failed`: the six open-path arms (twenty open, `--over-cap`, an unreadable count,
  the record: board, the bot board, the null control) red, every other arm green.
- **(b) the gate passes at the cap.** `if n < cap:` → `if n <= cap:`: `python3 -I
  tools/audit/seat/pr_cap.py --self-test` prints `21 checks, 1 failed`, FAIL `6 WIP
  refuses at the cap, naming the count, the groups and both ways past it`.
- **(c) the open board counted as WIP.** Tick: `n = len(cap_mod.wip_groups(roster))`
  → `n = len(prs)`: `152 checks, 2 failed`, FAIL `WIP cap: five in-progress beside
  a record: and a bot pull request: WIP: 5/6, not flagged` and `WIP cap: WIP is the
  roster's groups, not the open board: 20 open PRs still WIP: 5/6`.
- **(d) an unreadable roster treated as zero.** `roster = {"groups": []}` in place
  of the refusal: `21 checks, 3 failed`, FAIL `a roster it cannot read refuses,
  naming why: never a clean zero`, `read_roster over a checkout with no roster is a
  refusal`, `a roster file that is not JSON is a refusal, naming it`.
- The open path's own line mutants (`mut:openinfo`, `mut:overadvisory`,
  `mut:inforead`, `mut:caprecord`, `mut:capbot`) are driven inside `bash
  tools/audit/seat/pr_args.sh --self-test`, which reports `54 checks, 0 failed`
  at this head.
- **(e) the red this round repairs.** The previous head's corpus (`00118887`)
  under main's `policy_lint.mjs` prints `FIXTURE VACUOUS: checkCitationPresence
  reported 1 of 2 earned exclusions` — CI's failure, reproduced locally; this
  head's corpus under the same main lint prints `TOTAL: 0 error(s)` and `FIXTURE
  ok`.

## Null control

- 0 WIP: the gate passes (self-test arm `null control: no in-progress group is 0
  WIP, and the gate passes`).
- 20 open pull requests: `info` prints `open_pr: 20 open PRs; the cap gates
  dispatch, not opening` with rc 0, and through `open_pr.sh` the run reaches its
  push (`pr_args`' open-path null control).
- An unreadable roster is reported, not zeroed: the gate refuses and the tick
  prints no `WIP:` line for it.
- The base is the failure control for the class: the six arms of (a) fail there
  and pass here.

## Figures

- The dispatch gate against the live roster at `origin/main`: refuses at the cap
  and names the six in-progress groups — `python3 -I tools/audit/seat/pr_cap.py
  dispatch-gate --repo . --roster-ref origin/main`.
- Gate self-test tally: `python3 -I tools/audit/seat/pr_cap.py --self-test`.
- Tick self-test tally, WIP arms included: `python3
  tools/audit/seat/orchestrator_tick.py --self-test`.
- Open path, its mutants and null control: `bash tools/audit/seat/pr_args.sh
  --self-test`.
- Self-testing instruments wired: `python3 -I tools/audit/seat/selftest_wiring.py
  --check`.
- Structural ratchet: `python3 tests/structure.py`.
- Layout guard against the merge base: `python3 tests/layout.py --guard`.
- Policy corpus and its size caps: `node tools/policy/policy_lint.mjs`; generated
  rules: `node tools/policy/rules_sync.mjs --check`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main
  HEAD) --workdir <scratch dir>` selects `tests/entities.py` and
  `tests/harness_headers.py`; both need the Home Assistant feature environment,
  which is CI-only on this host, so CI's run at this head is the measurement.
  `prepr.sh` ran with `PREPR_SKIP_CLOSURES=1`: its closure recording of
  `tests/entities.py` was stopped after 18 minutes at a load average near 400,
  and recording closures is CI's heavy lane (`closures-autofix`), so this body
  carries no closure line. `run_always` ran here: `tests/env_drift.py --claims-only <merge-base>`,
  `tests/closure.py selftest`, `tests/layout.py`.
- Predicted reds: `python3 tools/pr/ci_predict.py --base $(git merge-base
  origin/main HEAD)`.

## Red checks

- `policy-docs`, `env-matrix` (at `00118887`): `FIXTURE VACUOUS:
  checkCitationPresence reported 1 of 2 earned exclusions`. Cause above: an added
  line cited 0010 under its live path, and CI grades the corpus with the base's
  `policy_lint.mjs`, which elides only the canonical spelling. Cheaper detector:
  `node tools/policy/policy_lint.mjs` run with `tools/policy/*.mjs` checked out
  from `origin/main` over the head's corpus — about 50 s locally, and it
  reproduces the failure exactly. The previous fixer ran the lint, but with the
  branch's own edited copy, which is green; no seat instrument (including
  `prepr.sh`) runs the base-restored graders, so the detector existed only as a
  manual step. Repaired by keeping the citation line byte-identical to main.
- `pr-contract` (at `00118887`): the body answered the reds of an earlier head.
  This body is re-taken whole at `5d477d6e`; its detector is `prepr.sh` on the
  body before the handoff, which ran green here.
- `nightly-status`: grades `main` — the nightly `slow` lane's `loop_cpu_ratio`
  over budget, fixed by the separate `r10-replay-cap` work. This diff touches
  nothing it reads.

## Forward-carry

none

## Friction

- ratchet-budgets: cost: `orchestrator.md` sits at its line and token caps (319
  lines, 4513 tokens on main), so the §5 rule was paid for by cutting duplicated
  prose elsewhere in the same file rather than raising a budget; restoring §4 to
  main's text this round left it at 317 lines and `policy_lint.mjs` reports 0
  errors. Carry: dismissed: paid in this pull request.
- policy-lint: contradiction: `tests/layout.py`'s guard refuses an added line that
  cites a retired `docs/decisions/` path, while the base's `checkCitationPresence`
  arm B elides only that canonical spelling, so any rewrite of the 0010 citation
  line turns `policy-docs` red; it is avoided here by not touching the
  line. Carry: dismissed: the collision is loud, not silent — arm B names itself the
  moment the line moves — and repairing the arm is a change to a pinned grader
  that takes effect only after it merges, outside this pull request's scope.

## Unpinned sites

n/a: the predictor names no `mutation` site the diff adds — `python3
tools/pr/ci_predict.py --base $(git merge-base origin/main HEAD)` prints no
`PREDICT mutation ADDED UNPINNED` line.

## Architecture score

n/a: no file in the integration changed, so no measured metric moved.

## Approval

- **Policy.** `dev/governance/roles/orchestrator.md` §5 gains the dispatch rule.
  That paragraph changes what a seat must do and merges only on an approving
  review under the owner's authority; this brief is not that approval.
- **Code-owned paths.** `tools/audit/seat/pr_cap.py`, `tools/audit/seat/open_pr.sh`
  and `tools/audit/seat/orchestrator_tick.py` are code-owned and need an approving
  review at this head (decision 0011).
