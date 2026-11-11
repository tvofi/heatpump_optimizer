# Proposal triage, session s7, batch 52 (P254-P263)

Ten entries, V168-V177. They are the research seat's "regain time" proposals P1-P10, and the owner
approved them as decision cards in chat at 2026-10-28T17:47Z. The research report is quoted from
the orchestrator's scratch copy (`s7/regain-time-proposals.md`). Mapping: V168=P1, V169=P2,
V170=P3, V171=P6, V172=P5, V173=P4, V174=P9, V175=P7, V176=P8, V177=P10. The owner narrowed V174
(the App key stays local, and FLY-ROWONLY-BASE goes first). The owner's approval makes each one
worth triaging, but it does not exempt any of them from `proposal-triage.md`. The owner's
correction of the same day still governs: "triage should still do cost/benefit and is allowed to
reject poor proposals".

Facts were read at origin/main `beb570c817c4efcae0d5f6f4bba52f3383baf8db` and at the live roster,
`origin/handoff/audit-r10-roster` `2ce021c6f19c4c4069d50994a271fd1e7b872834`.

**Which figures are the research seat's and which are this seat's.** The report's replan
counterfactuals, PR-wall sizes, review-round counts and CI timings are its own, with the commands
it names. This seat did not re-run them. The code and roster facts below were read by this seat at
the refs above. A ruling never rests only on a figure this seat did not check: where a benefit
exists only as the report's assumption ("assume 0.5 h"), the ruling says so.

## P254: replan.py counts an absorbed group as done

Verdict: ACCEPT, into **R10-FLOW-TOOLKIT-MODEL**, which owns `tools/plan/replan.py`. P239 already
routes a replan carry there.

Source: `proposals.md` V168 (report P1).

Instances:
- **The defect is real.** `tools/plan/replan.py:188`: `is_done` returns true only for the stages
  `done` and `rca-done`. The done set at line 232 is built from it.
- **Four absorbed groups are scheduled as open work.** They are R10-ORCH-MACHINERY (L),
  R10-ROUTING-INVARIANTS, R10-FLY-POOL-INSTRUMENT and R10-FLY-RECORD-BEAT (all S), with stage
  `absorbed` on the roster ref above.
- **Their notes name their absorbers in free text**, for example "absorbed into
  R10-ORCH-ROSTER-SCHEMA". R10-ORCH-MACHINERY's note reads "Closed, superseded by the re-cut" and
  names no single group.
- **The report's measurement:** 140.82 h becomes 132.55 h, so the forecast is 8.3 h earlier.
  Nothing is delivered sooner.
- **The risk the report names has already happened once.** A blocked verdict this round
  (`blocked 0f9a29e14`, carry-missing) found #2733's items carried only to R10-ORCH-ROSTER-SCHEMA
  (done) and R10-ROUTING-INVARIANTS (absorbed). An absorbed group can hide work that its absorber
  closed without carrying.

Carry (narrowed):
- `is_done` includes `absorbed`.
- The plan prints each absorbed group with the absorber its note names (`absorbed into <G>`), and
  flags as an advisory one whose note names no existing group. It does not refuse: the
  consolidation notes are prose, and ORCH-MACHINERY's is legitimately a re-cut.
- Controls: an absorbed fixture group is not scheduled; a mutant that drops `absorbed` schedules
  it; a fixture with a note naming no group prints the advisory; null: today's roster minus the
  four reproduces the plan.

Cost: one line plus about 10 for the advisory, in a group already rewriting replan.py.

Binding: a forecast 8.3 h wrong in a file whose owner is not started, against a near-zero cost.

## P255: new findings land as carries on not-started groups, not as new groups

Verdict: ACCEPT, as routing practice. There is no tree change and no roster op.

Source: `proposals.md` V169 (report P2).

Instances:
- **The report's intake figures:** 26 groups added in 72 h (23 of them S), and over 48 h intake (15)
  matched closures (14).
- **This is already the owner's standing rule.** The consolidation notes on the three absorbed
  groups cite "tvofi existing-groups-first", 2026-10-25. `finding-propagation.md` already routes a
  finding into the stage's own brief.

Accepted, as the report narrows it:
- A new finding, fly-in or friction key becomes a carry on a **not-started** group that shares a
  file or seam with it.
- Never onto a group in review or fixing. Carry-missing is the report's top block class.
- Root-cause seats that `defect-root-cause.md` requires keep their own seat (see P259 for the
  friction RCAs).

Not accepted: re-pricing triage and record batch groups in the plan. That is a plan-model input,
and the report gives no measured counterfactual for it. If wanted, it belongs to
R10-FLOW-TOOLKIT-MODEL with a figure.

Cost: none in the tree. Larger briefs on host groups can raise review rounds, which the
not-started-only limit bounds.

Binding: the measured intake is equal to the burn, and the practice is the owner's own.

## P256: the fixer runs the review packet's mechanical refusals before handoff

Verdict: ACCEPT, narrowed, into **R10-ORCH-REVIEW-PACKET** (stage `carries-open`), which owns
`review_packet.py` and `bus.sh`. The `fixer.md` line is policy: the owner approved the card, and
the group's pull request merges only on tvofi's approving review.

Source: `proposals.md` V170 (report P3).

Instances:
- **The packet's refusals already exist and are mechanical** (`tools/audit/seat/review_packet.py`
  docstring): carry-audit, head-note, structure (merged with main), red-unanswered, required-red,
  host-path and hot-file. Today `bus.sh dispatch` renders them, at review time.
- **Part of this is already at handoff.** R10-FLOW-JIDOKA (`done`) added the carry audit with
  `--roster-ref` to prepr. prepr also runs ref privacy (host paths) and the pr-body lint.
- **The report's block classes** (71 blocked verdicts since 10-25): carry-missing 19, red-check
  classes 9, mutation 6, head-moved or conflict 3. This seat sampled the carry-missing verdicts on
  the verdict refs. They are of two kinds:
  - a forward carry not on its destination's roster entry (for example `blocked 64d33242`: "not
    carried to R10-COP-GATE and R10-UX-HEALTH");
  - a brief carry neither implemented nor dispositioned (`blocked 5e83e3d8`: "carry 6 ... is neither
    implemented at the head nor dispositioned in the body, which answers only carries 1-5").

  The second kind can be counted mechanically. The first is what the carry audit with
  `--roster-ref` reads, but only once the roster op has landed.
- **The CI-wait half contradicts an owner ruling.** The report would hold review dispatch until CI
  completes at the head. The same docstring (line 12) records that "the owner rejected waiting for
  the gate, card 5". The head of a new handoff also has no checks yet, because CI runs on the
  `fix/` branch after the open.

Carry (narrowed):
1. Before `handoff_push.sh` pushes, it runs the packet's offline refusals that prepr does not
   already run: structure merged with main, head-note and hot-file. A refusal stops the handoff
   with the packet's signal.
2. A new offline count, `brief-carries`: every carry index on the group's roster entry is named in
   the body, either answered or with a `Carry N:` disposition. A missing index refuses.
3. The CI-dependent refusals (red-unanswered, required-red) stay at dispatch, as card 5 rules.
4. One `fixer.md` sentence: the handoff runs these, and a refusal is answered before the push.
- Controls: a fixture body that answers carries 1-5 of 6 is refused naming carry 6, and passes with
  carry 6 dispositioned; a mutant that skips the count passes the 1-5 body and fails the arm; null:
  a group with no carries passes.

Cost: about 30 lines in a group already editing these files; one policy sentence; and the
handoff's prepr time plus a packet render (seconds, with no CI wait).

Binding: the benefit is the report's estimate (removing 22 of 71 blocks at 4.3 h each is an
assumption, not a measurement). But the narrowed carry costs a few lines and moves refusals that
already exist from after an open to before it. Even a single avoided round, at a +4.3 h OLS
slope, clears the cost. The CI wait is excluded because it costs about 42 min on every PR and an
owner ruling forbids it.

## P257: standing fixer-reviewer pairs, with the blocked verdict relayed straight to the warm fixer

Verdict: DEFER. The saving is assumed, and the direct-relay half cannot work for the seats most
fixers now run on.

Source: `proposals.md` V171 (report P6).

Instances:
- **The report's figure:** fix turnaround from a blocked verdict to the next verdicted head has a
  median of 2.3 h (p75 4.2 h, n=65). The saving of 0.5 h per round is stated as an assumption
  ("Assume 0.5 h saved").
- **The fixer is mostly not warm.** Since P251 and the owner's answer at 17:25Z, fixers go to cloud
  seats under high load, including L/XL and critical-path fixers. A cloud run is one-way: nothing
  reaches it by SendMessage, and it ends when its session does. The owner gave that as the reason
  to keep large groups local on 2026-10-24.
- **The verdict cannot skip the relay.** A reviewer pushes its verdict to a probe ref, and only
  `cloud_relay.sh` posts it as hpo-approver; the train's `app_approve` refuses a verdict posted any
  other way (seat preamble, item 4). So the orchestrator hop is the posting identity, not a sweep
  delay that can be removed.
- **The same-reviewer half is already practice.** It is done ad hoc ("same reviewer takes r2"), and
  the three-round rule makes a fresh reviewer the default at round 3.

What would change the answer: the 2.3 h split into its parts, from the orchestrator's own logs. The
parts are the verdict post (comment `createdAt`) to the repair dispatch (`cloud-sessions.tsv`),
and the dispatch to the repaired handoff. If the post-to-dispatch median is 0.5 h or more, accept
an instrument that dispatches the repair from the relay's post, which is the hop that can be
mechanised.

## P258: recarry and start CI as soon as the merge verdict posts

Verdict: REJECT. Main nearly always moves between the verdict and the landing, so the early CI run
is usually spent twice.

Source: `proposals.md` V172 (report P5).

Instances (the report's own figures):
- **The wait is long.** The median from first merge verdict to merged is 2.13 h.
- **Main lands often.** Train landing events have a median gap of 50 min. That gives about 2.5
  landings inside the median wait. Treating landings as a Poisson process (an approximation),
  the chance that main does not move is about e^-2.5 = 8 %.
- **Only that 8 % saves anything.** When main moves, the train must re-carry and re-run CI at the
  head it merges, because it grades that head. The early run buys nothing, and in the other 92 % of
  cases it is a wasted run.
- **`--overlap` already recarries the queue up front** (the train-overlap ruling), so the train's
  per-entry recarry is already pipelined for every queued entry.

Cost: a second App-pushed CI run on most merge-verdicted PRs (about 42 min of runners each), plus
changes in `merge_train.py`.

Binding: the expected saving, about 8 % of 1.4 h per PR (roughly 7 min), is marginal against a
doubled CI spend on most PRs. An even or marginal trade is REJECT.

## P259: one seat and one pull request for the five friction RCAs

Verdict: ACCEPT, into **R10-FRICTION-REGRESSION**, which absorbs the other four.

Source: `proposals.md` V173 (report P4; the owner approved the shape change).

Instances:
- **All five are not-started, size S, and share one directory.** On the roster ref:
  - R10-FRICTION-REGRESSION, #2860, files `dev/audit/rca/`.
  - R10-FRICTION-MUTATION-SURVIVOR, #2840, `dev/audit/rca/`.
  - R10-FRICTION-GATE-SCOPING, #2835, `gate-scoping.md` plus `dev/audit/rca/`.
  - R10-FRICTION-FIXER-MD, #2895, `fixer.md` plus `dev/audit/rca/`.
  - R10-FRICTION-CLAIM-FALSE, #2907, `dev/audit/rca/`.
- **Two of them touch policy files.** So those two PRs would each need tvofi's approving review
  anyway. One PR needs that review once.
- **No contract forbids it.** `dev/governance/roles/root-cause.md` has no one-seat-per-trigger
  clause: a grep for "one seat", "per trigger", "each trigger" and "single" returns nothing. Its
  binding shape is beside a fix and never inside one, and these five are recurring-friction keys,
  not fixes.
- **The report's measurement:** 132.55 h becomes 123.38 h at 6 slots, so 9.2 h. Most of that comes
  from the model counting each S separately. The real saving is four opens (13-30 min of prepr each
  at today's load, P249), four reviews and four train entries.

Ops (held until this file is on main):
- `append-carry R10-FRICTION-REGRESSION`: the four other briefs are carried, and each record
  stays its own file with its own cause, process state, cost test and countermeasure or refusal.
- `wire-issue R10-FRICTION-REGRESSION` for #2840, #2835, #2895 and #2907.
- For each of the four: `set-stage ... absorbed` and `set-resume --field note` "absorbed into
  R10-FRICTION-REGRESSION (triage P259)".
- The carry states that the body carries one `Closes #N` line per issue, because a multi-issue
  `Closes #A #B` closes only #A.
- The carry states that the reviewer may block per file in one round.

Cost: one blocked record holds all five. The reviewer's per-file verdict bounds it to one round.
The group is now M-sized work on an S entry, and there is no size op, so the plan under-prices it
by about the S/M difference until it is re-sized.

Binding: four PR cycles saved on one shared corpus. The cost is a larger single review, against a
shape the contract does not forbid.

## P260: take the local box off the hot path; land FLY-ROWONLY-BASE first

Verdict: ACCEPT, narrowed to part (b), as orchestrator practice. Part (a), as the owner narrowed
it, leaves nothing to route beyond P251.

Source: `proposals.md` V174 (report P9). The owner narrowed it: the App key stays local, and
FLY-ROWONLY-BASE (#2923) goes first.

Instances:
- **With the App key local, opens and updates stay local.** `open_pr.sh` and `update_pr.sh` push
  through `app_push.sh` and run prepr inside that push, so their prepr stays local too. Moving a
  fixer's own runs to cloud is P251, which already applies. Skipping the open's prepr is P250,
  which is deferred.
- **#2923 is open** (`refs/pull/2923/head` `b04f9e93bd4ec068436a90f000a98851ed44318c`), but no
  roster group named R10-FLY-ROWONLY-BASE exists on the roster ref above. Ordering it first in the
  train needs it on the roster, because every pull request needs a roster row.
- **The report's figures:** four rowless opens today (#2912, #2913, #2915, #2917) each owe a full
  prepr update plus CI, about 1 h each, and stale-checkout refusals hit #2910, #2909 and #2896.

Accepted (b):
- #2923 merges first, as critical-path-exempt.
- The opener refreshes its main checkout before every open, which is already authorized. This is
  the default, not a new rule.

Not accepted (a): there is nothing left to route once the key stays local.

Cost: none in the tree. The roster row for #2923 is an orchestrator registration.

Binding: four 1 h reworks today, against a train-order choice and a `git fetch`.

## P261: build ARCH-DOCS' checker now; the final stage resolves only the delta. The REPLAY export is requested now

Verdict: ACCEPT, narrowed, into **R10-ARCH-DOCS**. The continuous re-run on every main merge is not
accepted. The owner approved overriding the 2026-10-17 last-stage ruling for the early arm.

Source: `proposals.md` V175 (report P7).

Instances:
- **ARCH-DOCS is L, not started, with 81 after-edges and 7 carries** on the roster ref. Its brief
  (owner, 2026-10-22) is to verify, adjust and wiring-test what R10-ARCH-DOCS-FIRST (`done`) landed.
- **The report's 4.8 h is mostly a resizing artifact.** The counterfactual re-sizes ARCH-DOCS from
  L to S without adding an early seat's slot-hours. Pulling the checker forward does not reduce
  total work, so at 6 slots most of the gain disappears. The real gain is moving work off the tail,
  and that counts only when ARCH-DOCS is the last group to finish. That is the case in the report's
  combined schedule (finish 11-01T15:14Z), not today. The report's upper bound there is about 14 h.
- **REPLAY-REAL-DAY's only serial step is the owner's.** Its carry 1 on the roster names the
  owner-side command (`python3 tools/replay/export.py --config-dir /config --days 1 --out ...`),
  and its after-edges, R10-REPLAY-SCOPED and R10-DIAG-REDACT, are satisfied (`done`).

Carry (narrowed) on R10-ARCH-DOCS:
- Arm A is dispatchable now, past the after-edges, by the owner's override. It builds the
  wiring-test checker and the target-marker resolver against ARCH-DOCS-FIRST's docs, each with its
  red fixture and null control. It is one pull request, and it counts against the WIP cap only from
  its open.
- Arm B stays last. It is opened at the true merge base after every after-group, and it runs arm
  A's checker and resolves the delta.
- A re-run on every main merge is not carried. That is standing CPU at a merge about every 50 min,
  for a result only arm B's run decides. Arm A's PR is re-run when it is updated, as any PR is.

Cost: an early S-sized seat; possible rework if a late group changes the shape (the brief expects
named departures); one WIP slot from arm A's open.

Binding: worth taking as insurance for the tail at low cost, now that the owner has lifted the
ordering constraint. The modelled hours are not the reason.

## P262: shard coverage and mutation, and trim the CI tail

Verdict: DEFER. The shard half buys nothing on the critical path, and the tail half is unmeasured.

Source: `proposals.md` V176 (report P8).

Instances (the report's run 40728676573, #2873):
- **CodeQL python is the pole** at 33.3 min, and it is kept as is. coverage (30.2), mutation (25.7)
  and closures (24.7) already finish under it, so sharding them shortens no PR's wait. It also costs
  re-derived closures on Linux and ratchet input changes in code-owned `.github/`.
- **The tail is the only lever.** pr-contract takes 1.2 min and gate 6.6 min (60 s polls), and the
  paired edit run ends 11.5 min after the last test job. The report's 10 min saving assumes the tail
  falls to about 2 min, but it does not break the 6.6 min of gate or the edit run's repeat into
  parts that can be removed.

What would change the answer: a per-step timeline of `gate` and the paired edit run over the last
12 PR runs, naming the removable minutes. The jobs listing is already taken per run. If 5 min or
more is removable without changing a required context, accept it as a tail-only carry. Shards stay
rejected while CodeQL is the pole.

## P263: re-measure WIP against throughput once the box is cooler; raise the cap to 8 only if it moves

Verdict: ACCEPT, narrowed to the measurement, which this seat takes. There is no tree change and no
roster op. The cap stays the owner's call, on the result.

Source: `proposals.md` V177 (report P10).

Instances:
- **The baseline is P240's method:** 27 roster snapshots 6 h apart, live groups against groups done
  or absorbed 12 h later, r = 0.045, under loads of 60-350.
- **The cap is an environment default.** `HPO_WIP_CAP` defaults to 6 (`tools/audit/seat/pr_cap.py:54`
  and line 85; `orchestrator.md` line 98), so a raise is a setting, not code. **WIP already
  exceeded 6 routinely:** P240 measured a range of 6-20.

Accepted (narrowed):
1. This seat re-takes the measurement with P240's exact method, over a window that starts once load1
   has stayed below 20. Load fell to 10.8-20.3 at the report's 17:32Z reading.
2. It needs n ≥ 8 windows in all, and at least 3 at WIP ≤ 6 and 3 at WIP ≥ 8. Fewer than that is
   reported as insufficient, not as a result.
3. The report's bar stands: r > 0.3, and closures per 12 h at WIP ≥ 8 beat those at WIP ≤ 6.
4. Caveat for the reading: since WIP already ran above 8 under the cap of 6, a "raise to 8" mostly
   changes what the dispatch gate refuses, not what runs.

Cost: one measurement pass, using git only.

Binding: a free measurement under a changed condition, against a high-risk setting change that
stays the owner's.
