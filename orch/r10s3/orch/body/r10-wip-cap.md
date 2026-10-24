The soft cap bounded the wrong door: it refused **opening**, and opening is how work
leaves work in progress. Complete handoffs were parked unopened while the quantity
the cap exists to bound — roster groups in progress — was not measured at all (the
round-10 orphaned-handoff RCA, landing separately). A new group now enters the pipe
only while fewer than `HPO_WIP_CAP` (default 6) roster groups have
`resume.stage: in-progress`; opening and merging are never refused.

**Behaviour change.** `pr_cap.py dispatch-gate` (new) counts WIP through
`roster_lib` at the roster ref, refuses at or over the cap and prints the WIP group
ids. `open_pr.sh` prints the open count and always proceeds; `--over-cap
"<reason>"` is still accepted, says it is advisory, and changes nothing. The
tick's level line becomes `WIP: N/6 (open PRs M)`. **Rollback:** reverting this
head restores `pr_cap.py`'s `gate`, `open_pr.sh`'s gating call and the tick's
`OPEN-PR CAP` line in one commit; `dispatch-gate` has no other caller.

## Head

`80fe9ac08ef9e8b9f90baf814d79a38d56d4041a`

`prepr.sh` ran with `PREPR_SKIP_CLOSURES=1` by the owner's ruling (2026-10-20,
relayed by the orchestrator): the closures recording step was skipped, so this
body carries no closure line — the gate's `MODE: SCOPED` line and `scope.run`
above are the scope measurement, and CI's closures lane is the recording. The
earlier in-flight run was stopped for the re-run after `git status --porcelain`
printed nothing at this head.

## Mutation proof

- **(a) opening still refused at the cap.** The new `pr_args.sh` arms run against
  main's `pr_cap.py` (sha1 `96b81797ed9aaad0abc1ad4dc5c17278023854c2`, read from
  `origin/main` at `efc0e6733`) fail: `pr_args self-test: 54 checks, 6 failed`, the
  six open-path arms red (twenty open, `--over-cap`, an unreadable count, the
  record: board, the bot board, and the null control) and every other arm green.
  Directly, on a 20-PR stub board, main's `gate` prints `open_pr: REFUSE: open-PR
  cap: 20 open >= 6; drain before opening (HPO_OPEN_PR_CAP, --over-cap <reason>)`,
  rc 1. On the base, `dispatch-gate` does not exist (usage, rc 2).
- **(b) the gate passes at the cap.** `if n < cap:` → `if n <= cap:`: rc 1 on
  `python3 -I tools/audit/seat/pr_cap.py --self-test`, FAIL `6 WIP refuses at the
  cap, naming the count, the groups and both ways past it`.
- **(c) the open board counted as WIP.** Tick: `n = len(cap_mod.wip_groups(roster))`
  → `n = len(prs)`: rc 1, FAIL `WIP cap: five in-progress beside a record: and a
  bot pull request: WIP: 5/6, not flagged` and `WIP cap: WIP is the roster's
  groups, not the open board: 20 open PRs still WIP: 5/6`.
- **(d) an unreadable roster treated as zero.** `if roster is None: roster =
  {"groups": []}`: rc 1, FAIL `a roster it cannot read refuses, naming why: never a
  clean zero`, `read_roster over a checkout with no roster is a refusal`, and `a
  roster file that is not JSON is a refusal, naming it`.
- The open path's own mutants are each red under `bash
  tools/audit/seat/pr_args.sh --self-test`: `mut:openinfo`, `mut:overadvisory`,
  `mut:inforead`, `mut:caprecord`, `mut:capbot`.
- **(e) the moved-citation fixture keyed on one spelling.** `policy_lint.mjs`'s
  arm B now elides a cited document under every spelling the move map knows;
  with `spellings = (k) => [k]` (canonical only) `node
  tools/policy/policy_lint.mjs` exits 1 with `FIXTURE VACUOUS:
  checkCitationPresence reported 1 of 2 earned exclusions`. The fix is visible
  only because §4's citation now names the live path: `layout.py`'s guard
  refuses a new line citing the retired one, so the two checks disagreed about
  the spelling a policy file may use, and this arm resolves it in the guard's
  favour.

## Null control

- 0 WIP: the gate passes and prints `dispatch: WIP 0/6: may dispatch a new group
  ()`, rc 0 (self-test arm `null control: no in-progress group is 0 WIP`).
- 20 open pull requests: `info` prints `open_pr: 20 open PRs; the cap gates
  dispatch, not opening` with rc 0, and through `open_pr.sh` the run reaches its
  push (`pr_args`' open-path null control).
- An unreadable roster is reported, not zeroed: the gate refuses and the tick
  prints `UNREADABLE: roster …` with no `WIP:` line (arm `a roster it cannot read
  is UNREADABLE, never WIP: 0/6`).
- The base is the failure control for the class: the same six arms fail there and
  pass here.

## Figures

- The dispatch gate against the live roster at `origin/main` `10d423c28073`:
  refuses at the cap and names the six groups — `python3 -I
  tools/audit/seat/pr_cap.py dispatch-gate --repo . --roster-ref origin/main`.
- Gate self-test tally: `python3 -I tools/audit/seat/pr_cap.py --self-test`.
- Tick self-test tally, WIP arms included: `python3 -I
  tools/audit/seat/orchestrator_tick.py --self-test`.
- Open path, its mutants and null control: `bash tools/audit/seat/pr_args.sh
  --self-test`.
- Self-testing instruments wired: `python3 -I tools/audit/seat/selftest_wiring.py
  --check`.
- Structural ratchet: `python3 tests/structure.py`.
- Layout guard and its self-test: `python3 tests/layout.py`.
- Policy corpus and its size caps: `node tools/policy/policy_lint.mjs`.
- Gate scope: mode line and the scripts it selects — `python3 tests/closure.py
  select --diff $(git merge-base origin/main HEAD) --workdir <workdir>`; run
  `tests/entities.py` and `tests/harness_headers.py`, plus `run_always`
  (`tests/env_drift.py --claims-only <merge-base>`, `tests/closure.py selftest`,
  `tests/layout.py`).
- Base arm: `git show origin/main:tools/audit/seat/pr_cap.py`, sha1 above.

## Red checks

- `tests/harness_headers.py` went red once, at `3af8d082` (12 of 109), with
  every failure in `dev/audit/rounds/round4/D7/sysid_estimator_frontier.py`:
  the harness hit its own 900 s wall limit (`rc=124 cpu=168.0s`) on a box at
  load average 170. It passes at this head (`ALL 109 HARNESS HEADER CHECKS
  PASSED`, load 65). Its inputs are `dev/audit/rounds/` and the integration — no
  file this diff touches. The cheaper detector is the harness's own wall/CPU
  bound, which is what refused it (its 50% CPU bound did not fire); CI runs it
  in `lane_stress`, sized for a co-runner.
- `tests/entities.py` is red at this head on one of its 2359 checks: `and on an
  idle loop it ticks, reports no such gap and dumps nothing` (`ticks=7`, needs
  `> 10`; idle `max_gap=0.090s`). The heartbeat's 1 ms tick chain starved on the
  same load (60-90); the check's own tick counter is the detector and it fired.
  The same check passed on the earlier run at `3af8d082` (all 2359), and the
  code it measures — `LoopHeartbeat` on an asyncio loop — is untouched here.

## Forward-carry

none

## Friction

- ratchet-budgets: cost: `orchestrator.md` sat at its exact line and token caps
  (319 lines, 4513 tokens), so the new §5 rule was paid for by cutting six lines of
  duplicated prose in the same file (a "Generalised:" label, a repeated clause, a
  repeated example, and a merge-queue example the next paragraph already names)
  rather than raising a budget. Carry: dismissed: paid in this pull request.
- layout: stale: the same rewrite put the base's retired
  `docs/decisions/...` citation on an added line, and `tests/layout.py`'s guard
  reported it as a new reference; the citation now names
  `dev/governance/decisions/0010-merge-commits-on-main.md`, and the guard reports
  0 refusals against the merge base. Carry: dismissed: corrected in this pull
  request.

## Unpinned sites

n/a: the predictor names no `mutation` site the diff adds — `python3
tools/pr/ci_predict.py --base $(git merge-base origin/main HEAD)` prints no
`PREDICT mutation ADDED UNPINNED` line.

## Architecture score

n/a: no file in the integration changed, so no measured metric moved.

## Approval

- **Policy.** `dev/governance/roles/orchestrator.md` §5 gains the dispatch rule.
  That paragraph changes what a seat must do and merges only on tvofi's approving
  review; this brief is not that approval.
- **Code-owned paths.** `tools/audit/seat/pr_cap.py`, `tools/audit/seat/open_pr.sh`
  and `tools/audit/seat/orchestrator_tick.py` are code-owned and need tvofi's
  review at this head (decision 0011).
