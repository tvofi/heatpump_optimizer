The root-cause record for the recurring `nightly-ha (stable)` red: `hb:positive_control` fails when the heartbeat's one `py-spy dump --nonblocking` call times out after 30 s. It adds `dev/audit/rca/nightly-ha-pyspy-timeout.md` and changes nothing else. The seat ran beside any fix, never as the fixer.

- **Cause.** `check_hb_positive_control` needs a single racy sample to pass: py-spy's `rc=0` section naming `_hb_spin`, taken during a 0.6 s spin. Against CPython 3.14.6, py-spy 0.4.2 intermittently does not return within 30 s. It is CPU-bound while it runs: 28.7 s of CPU in 29 s of wall time, 74% of it in the kernel.
- **How far it reaches.** 8 of 120 `stable` jobs since 2026-10-08. 0 of 120 on the 3.13 floor. Same image digest and same runner on green runs, so it is a race. All 8 are `workflow_dispatch` runs of PR branches; none reached `main`. Reproduced in the lane's own heartbeat container: 1 of 60 runs.
- **Process state: (c).** The `rc=0` pin was validated on one real-HA run. Each later red was answered inside one PR as an isolated event.
- **Cost test.**
  - Countermeasure A: retry py-spy while the spin is held. Costs about 2 s a day, against 1 to 2.5 seat-hours per cycle. It passes the test; it is carried to a fixer and not built here.
  - Countermeasure B: a false-red-rate rule. Refused: 2.25 runner-hours per check, and the class has P = 1 in the lane's history.
  - Countermeasure C: a cross-run count before an answer of "not a recurrence". Proposed; it is policy, so it is for tvofi.

## Head

`202cb8874ef72b82d9db49a6ecd77f28ad22838a` merges origin/main `0c298f6b5` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`202cb8874ef72b82d9db49a6ecd77f28ad22838a` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2479.md`. The authored code head is `0b7145312480e83c46665876ff5ade670125c900`.

`f81d96c4604ae5669c30d09d6f915342e35459d3` merges origin/main `0c298f6b5` into the authored code head `0b7145312480e83c46665876ff5ade670125c900` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`93647bfd9b4c2d940bc87b162bf4159ad2dd6b1e` merges origin/main `0c298f6b5` into the authored code head `0b7145312480e83c46665876ff5ade670125c900` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`0b7145312480e83c46665876ff5ade670125c900`: one commit on `origin/main` `106af95a3`.

## Mutation proof

n/a: no check, test or production line changes. Countermeasure A's demonstration is owed by its fixer (RCA section 5): a staged py-spy that hangs on its first call should go red at the base and green at the fix.

## Null control

- The green `stable` runs on the same digest (`33afb065`) and the same runner (`20261012.601`) read `py-spy rc=0` naming the spin. 117746567958 and 117731855696 are two of them. So the image alone does not cause it.
- Local lane: 59 of 60 runs `ok`.
- Synthetic on host glibc CPython 3.14.7: 105 dumps, 0 failures.

## Figures

- Class counts (RCA section 3): the GitHub REST API, `actions/workflows/tests.yml/runs`, then `runs/<id>/jobs?filter=all`, then `jobs/<id>/logs` grepped for `py-spy did not run`.
- Lane reproduction (RCA section 1): `nightly_ha._stage(…, two_zone_dhw=True)` and `docker_command(…, ["--heartbeat-only"], ("SYS_PTRACE",))` against `ghcr.io/home-assistant/home-assistant:stable`, digest `sha256:33afb0659d78…`, 60 times.
- Gate: `python3 tests/closure.py select --diff origin/main` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` The file sits under the inert `dev/audit/` prefix.

## Red checks

- `pr-contract`: red at the earlier head 202cb8874, `CARRY-AUDIT: 5 finding item(s): 0 routed, 5 unrouted` — the `## Forward-carry` and `## Friction` items named no `Carry:` destination. Answered at this body: each item now ends in `Carry: <group>` or `Carry: dismissed: <reason>`, and `tools/audit/carry_audit.py check --body` reads `4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)`. Cheaper detector: `carry_audit.py check --body` runs locally in under a second; prepr did not run it on this body before the first push, so the standing cost is one local run per body.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Forward-carry

- Countermeasure A, for a fixer group: `dev/audit/rca/nightly-ha-pyspy-timeout.md` section 5. It names the sites, the `tests/entities.py` pins and the demonstration owed. Carry: #201 (landed: `dev/programme/carries/carry-201.json`, on `handoff/audit-r10-roster` at `606aaca86`; no live roster group lists `tests/nightly_ha.py`, so the carry file is the stage's brief).
- Countermeasure C: a draft for tvofi, RCA section 4. Carry: dismissed: an owner proposal recorded in the RCA, not a work item.
- Not added to `dev/audit/config/bugclasses.json`. This is a CI-lane race, not an audit class. Carry: dismissed: not an audit class; the RCA section 2 states why.



## Friction

- defect-root-cause: unenforced: a red-check answer is written per PR, with no cross-run count. #2379 and #2411 each read a 6- to 8-instance class as one event (RCA section 2). Carry: R10-RCA-FRICTION (landed: the group's roster carry on `handoff/audit-r10-roster` at `3a9d79531`).
