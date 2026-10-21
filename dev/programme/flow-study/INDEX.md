# Round-10 Lean flow study (2026-10-21)

The owner commissioned this study. Its rulings are posted as #201 comment 6318002897. **This branch is a reading copy for the orchestrator and the flow-group seats. It is not a pull request and is not meant for `main`.** If any of it is ever proposed for `main`, every new file must first be classified (a measured closure, or `tests/closure.py`'s INERT list), or `tests/entities.py` refuses it, and the prose must pass `writing-for-agents.md`.

| file | what it is | who reads it |
|---|---|---|
| `FUTURE-STATE.md` | demand (a round in about 100 h), current state measured, root causes, future state, redundancy, projection, groups, rulings, guardrails | owner, orchestrator |
| `SHADOW-PLAN.md` | the drain-first phasing against today's PR congestion, lanes, the projected schedule, model assumptions, the round-11 template | orchestrator |
| `STUDY.md` | one pre-study per flow group: anchors, budgets, seams, controls; §0 is the shared finder's harness | the fixer and reviewer seats |
| `ORCHESTRATOR-PROMPT.md` | the final handover prompt | orchestrator |
| `RULINGS-201.md` | the text posted on #201 (the record of R1–R9) | everyone |
| `roster/shadow-r10-groups.json` | the live roster at 2c76c3128 (rebuilt at commit time), plus the 16 FLOW groups and 6 carries; `brief_lint` `TOTAL: 0` | orchestrator |
| `roster/groups/*.json` | each FLOW group, ready for `roster_edit.py append-group` | orchestrator |
| `tools/` | `build_shadow.py` rebuilds the shadow roster from any roster ref; `simulate.py` and `gen_plan.py` re-run the projection | anyone re-deriving |

**Re-derive:**

```
HPO_REPO=<clone> python3 tools/build_shadow.py origin/handoff/audit-r10-roster
python3 tools/simulate.py shadow-r10-groups.json 300
```

The scenario switches are in the header of `simulate.py`. `gen_plan.py` renders the schedule. Run the commands from `tools/`, or copy the scripts next to each other.

The figures are the study's measurements at the refs named in each file. Re-take them with STUDY §0's enumerators before quoting any of them in the record.
