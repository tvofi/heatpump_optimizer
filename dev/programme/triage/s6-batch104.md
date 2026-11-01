# Proposal triage, session s10, batch 104 (P361)

The rolling batch after batch 103. Facts were read at origin/main `ca6333333`, at the round's
roster branch `origin/handoff/audit-r10-roster`, and in the orchestrator's sweep-runner directory
and seat ledger.

## P361: promote the session-local gantt-drift stand-in to a tracked instrument

Verdict: ACCEPT, as a new fly-in group R10-FLY-GANTT-DRIFT (size S). It does not go on
R10-PLAN-REAL-DURATIONS.

Source: the orchestrator s10's queue line of 2026-11-01T17:49:18Z. It quotes the owner (tvofi,
2026-11-01): "Each time the plan html is updated, compare the real state against the gantt,
mechanically if possible, and have slips surfaced to you to act on, defer or accept".

Instances:
- **The stand-in runs today, from scratch.** The orchestrator's `sweep_runner.sh` (lines 34-38)
  calls the session-local `gantt_drift.py` after each replan and plan_page render, then forwards
  its `GANTT-SLIP` and `GANTT-BASELINE` lines to the orchestrator's new-items file.
  `dev/governance/roles/orchestrator.md` section 13 reads: "An instrument the programme runs is a
  tracked, self-tested file; a session-local copy is a defect". The stand-in is 191 lines
  (`wc -l`), with no host path in it (`grep -c '/Users\|~/'` prints 0).
- **Its first run, read from the acks file the orchestrator wrote at 17:48Z.** Three IDLE slips,
  each acknowledged:
  - R10-FLY-STANDING-CONTRACTS, `act` (designer dispatched);
  - R10-FRICTION-RECORDS, `defer` (the 16-open-PR dispatch cap);
  - R10-GRADE-DRIVERS, `defer` (the same cap).
  The proposal reports 0 LATE and 0 CLOSURE for that run.
- **The miss it would have caught.** The proposal names the critical-path head R10-SAV-COMFORT,
  idle while the plan had started it. The seat ledger's line of 2026-11-01T17:08:35Z records its
  part-2 fixer being fired then. That shows the gap the instrument would close, not one it was
  measured closing.
- **The stand-in's self-test.** `python3 -I gantt_drift.py --self-test` prints `gantt_drift
  self-test: 9 checks passed` in 0.04 s real time.
  - Its checks are bare `assert`s, which `python -O` strips, and no mutant pins them. The tracked
    form needs `check()` counting and a mutant per arm, as the group brief says.

Cost:
- **One S fixer on the sonnet row, with an opus reviewer.** The files are the new
  `tools/audit/seat/gantt_drift.py` (about the stand-in's size), its
  `tools/audit/seat/instruments/` entry and `INSTRUMENTS.md` index line, and one run line in
  `.github/workflows/governance.yml`.
- **Capped files.** `tests/structure_budgets.json` measures only `custom_components/` (`PACKAGE_DIR`,
  `tests/structure.py` line 241), so a file under `tools/` moves no structure key.
- **CI.** The self-test costs well under a second inside `governance.yml`'s existing job.
  `critical_path_minutes` in `tests/ci_budgets.json` is a median of whole runs, which a
  sub-second step does not move measurably.
- **Standing cost: none new.** The sweep already runs the stand-in, so promotion swaps a path and
  adds no run.

Binding:
- **Why ACCEPT clears the bar.** The behaviour is owner-ordered and already running. Section 13
  makes its session-local form a defect. Promotion adds no new run, and one S fixer buys a
  self-test CI enforces through `selftest_wiring.py --check`, in place of a 191-line file only one
  session can see.
- **Why a new group.** R10-PLAN-REAL-DURATIONS is in progress with #3097 in flight (r2 handoff
  `4d6244659`), so a carry would refuse its review packet (`brief-carries`). Its files are
  `tools/plan/` and `plan_page.py`, the duration model and the render, a different seam from
  slip detection. R10-ORCH-PLANPAGE is done.
- **What stays out.** The proposal's thresholds (60 min grace, 6 h LATE, 2 h CLOSURE) are the
  stand-in's constants, not a ruling. The fixer keeps them as named constants, and changing them
  is not part of this group.

New group (R10-FLY-GANTT-DRIFT, JSON `groups/R10-FLY-GANTT-DRIFT.json` in the session state),
brief:

> From triage P361 (orchestrator s10, 2026-11-01; tvofi: "Each time the plan html is updated,
> compare the real state against the gantt, mechanically if possible, and have slips surfaced to
> you to act on, defer or accept"). The orchestrator's sweep runs a session-local Gantt-drift
> stand-in after each replan and plan_page render, and orchestrator.md section 13 makes a
> session-local instrument a defect. Build it as a tracked, self-tested instrument in
> tools/audit/seat/, keeping the stand-in's name, from that stand-in, which the orchestrator hands over at dispatch. It
> reads the plan JSON tools/plan/replan.py writes, an accepted baseline, an acks file, the round
> roster, the open pull requests, the handoff refs and the dispatch ledger's FIRED lines, each as
> an argument and never a host path. It prints one GANTT-SLIP line per unacknowledged slip: IDLE,
> a not-done group the plan starts by now plus a grace that no open pull request, handoff ref or
> FIRED line names (a critical-path group tagged CP and listed first); LATE, a group whose planned
> finish moved past the baseline's by more than a threshold; CLOSURE, the plan's closure moved
> past the baseline's by more than a threshold. An ack is act or defer, silencing its key until a
> time, or accept, silencing it and re-baselining that key. The self-test counts checks through a
> check() helper, not assert, which python -O strips. It covers each slip kind and its null (a
> FIRED line or a handoff ref silences IDLE; a finish inside the threshold is not LATE), each ack
> kind, and accept's re-baseline, and each arm has a mutant. Wire --self-test into a
> governance.yml run line so selftest_wiring.py --check passes, add the entry file and its
> INSTRUMENTS.md index line, and classify every new file for tests/entities.py. Out of scope:
> replan.py's duration model (R10-PLAN-REAL-DURATIONS) and plan_page rendering. triage:
> dev/programme/triage/s6-batch104.md#P361

Its `files` are the new instrument and its entry file under `tools/audit/seat/` and `tools/audit/seat/instruments/`,
`tools/audit/seat/INSTRUMENTS.md` and `.github/workflows/governance.yml`. It has no `after`, and
its `resume.note` cites `triage: dev/programme/triage/s6-batch104.md#P361`.

Roster op (queued `#held` until this file is on origin/main):
1. `append-group R10-FLY-GANTT-DRIFT <groups/R10-FLY-GANTT-DRIFT.json>`

Rule run on the instance. The stand-in was run at 2026-11-01T17:54Z on the live plan
(`plan-live.json`, plan start `2026-11-01T17:51:00Z`), a copy of the accepted baseline, and the
17:48Z acks, roster, open-PR, handoff and FIRED inputs the sweep wrote. It exits 0 and prints no
`GANTT-SLIP` line, because all three IDLE keys are acked. The tracked instrument must keep that
behaviour, and its self-test pins it.
