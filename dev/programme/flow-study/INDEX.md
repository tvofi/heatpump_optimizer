# Round-10 Lean flow study (2026-10-21)

The owner commissioned this study. Its rulings are posted as #201 comment 6318002897. **This branch is a reading copy for the orchestrator and the flow-group seats. It is not a pull request and is not meant for `main`.** If any of it is ever proposed for `main`, every new file must first be classified (a measured closure, or `tests/closure.py`'s INERT list), or `tests/entities.py` refuses it, and the prose must pass `writing-for-agents.md`.

| file | what it is | who reads it |
|---|---|---|
| `FUTURE-STATE.md` | demand (a round in about 100 h), current state measured, root causes, future state, redundancy, projection, groups, rulings, guardrails | owner, orchestrator |
| `SHADOW-PLAN.md` | the drain-first phasing against today's PR congestion, lanes, the projected schedule, model assumptions, the round-11 template | orchestrator |
| `STUDY.md` | one pre-study per flow group: anchors, budgets, seams, controls; §0 is the shared finder's harness | the fixer and reviewer seats |
| `ORCHESTRATOR-PROMPT.md` | the final handover prompt | orchestrator |
| `RULINGS-201.md` | the text posted on #201 (the record of R1–R9) | everyone |
| `roster/shadow-r10-groups.json` | the live roster at 2c76c3128 (rebuilt at commit time), plus the 17 FLOW groups and 6 carries; `brief_lint` `TOTAL: 0` | orchestrator |
| `roster/groups/*.json` | each FLOW group, ready for `roster_edit.py append-group` | orchestrator |
| `tools/` | `build_shadow.py` rebuilds the shadow roster from any roster ref; `simulate.py` and `gen_plan.py` re-run the projection; `review_baseline.py` re-measures the review-strength baseline | anyone re-deriving |

**Re-derive:**

```
HPO_REPO=<clone> python3 tools/build_shadow.py origin/handoff/audit-r10-roster
python3 tools/simulate.py shadow-r10-groups.json 300
```

The scenario switches are in the header of `simulate.py`. `gen_plan.py` renders the schedule. Run the commands from `tools/`, or copy the scripts next to each other.

The figures are the study's measurements at the refs named in each file. Re-take them with STUDY §0's enumerators before quoting any of them in the record.

**Revision 10 (2026-10-21):**
- The roster base is f424d993d: 19 flow groups (with the two toolkit groups) and 8 carries.
- The model gained EFF, EFFX, PAR, PRIO, RESERVE and CUT. The revision-10 projection is `EFF=1 PAR=1 PRIO=1 RESERVE=1 CUT=gap python3 simulate.py ../roster/shadow-r10-groups.json 300`.
- FUTURE-STATE §12 holds the cost-of-delay ranking.

**Design-seat pre-study (2026-10-21):** `design-seats/` holds the following.
- `STUDY.md`: the report. Its answer: neutral at best for round 10, and a narrow pipelined pilot in round 11.
- `designer.md` and `design-review.md`: the draft contracts.
- `model-grid.txt`: the scenario grid.
- `tools/review_rounds.py`: first-pass yield and block classes per reviewed PR.

The model's design switches are in `tools/simulate.py`'s header.

**Revision 12 (2026-10-21):**
- The design seats are adopted (`RULINGS-201-3.md` is the text to post on #201).
- The prompt opens with an adoption plan.
- The roster has 21 flow groups and 23 carries.
- The projection adds `DESIGN=pipe DTH=L`.

**Revision 13 (2026-10-21):**
- The architect/planner pre-study: `architect-planner/STUDY.md` and the draft contracts `architect-planner/architect-planner.md`.
- Two round-10 groups prepare the seat for round 11.
- The roster has 23 flow groups; its base is 23ef06dc6.

**Revision 14 (2026-10-21):**
- Standing rules 21–23 (roster edits wait, red checks, review-ref retries).
- A designer cloud role through R10-FLOW-DESIGN-STAGES.
- The designer's owner-report note.
- R16–R19 cited as comment 6322679091.

**Revision 15 (2026-10-21):**
- `tools/roster_delta.py` classifies a roster delta against a verdict.
- Rule 21 is amended.
- Three fly-ins: CARRY-DISPOSITION, OPENPR-ATOMIC and RELAY-REVIEW-FF.
- The hygiene adds ref_privacy and red checks.

**Revision 16 (2026-10-21):**
- The carry marker grammar matches `carry_audit.py`.
- Design review routes decisions, with three notes at most.
- The relay reports the review ref's tip.
- #2567's red is answered in its body.
