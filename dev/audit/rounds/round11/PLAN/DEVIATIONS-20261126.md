# Deviations from the plan, 2026-11-26

Recorded under `orchestrator.md` section 2b. Revisions 4 and the deviations of
`DEVIATIONS-20261125.md` stand for everything not named here.

| deviation | before | after | reason |
|---|---|---|---|
| (e) D3 wave folded in: seven groups added | no D3 survivor-pin groups | `R11-D3-PINS-actuation`, `-fabric`, `-inputs`, `-money`, `-plant`, `-solver`, `-sysid`; the D3 findings fold into `R11-SEAM-store-p2` and `R11-SEAM-cycle-reporting-p2` (S to L), and `R11-SEAM-tests` carries the judge-gate and judge-linux records | plan revision 5 (`CHANGES-R5.md`, `ADR-011-survivor-pins.md`), plan review approve f49167e9 on `plan-verdict/r11-d3-amend`, plan A, all 401 pins, adopted under mandate 6893738184 |
| (f) edges added | none on the D3 groups | actuation after `R11-SEAM-actuation-writes`, `R11-OWNER-FAULT-HOLD`; fabric after `R11-ARCH-fabric-learner`, `R11-SEAM-cycle-reporting`, `R11-OUTSIDE-START-APPROACH`; inputs after `R11-SEAM-inputs-freshness`; solver after `R11-OUTSIDE-START-APPROACH`, `R11-SEAM-cycle-reporting`; sysid after `R11-SEAM-learners`; money and plant edge-free; `R11-SEAM-cycle-reporting-p2` after `R11-SEAM-actuation-writes`, `R11-SEAM-learners` | the hot file `tests/guard_pins.py` and the ledger order, as in `CHANGES-R5.md` |
| (g) closure and critical path | closure 2026-12-04T22:01Z, critical path 119.23 h | unchanged: closure 2026-12-04T22:01Z, critical path 119.23 h | the last D3 group finishes before `R11-SEAM-docs`; no scenario moves either |

## Lint state at the amendment

`node tools/policy/brief_lint.mjs` reports one error, in
`dev/programme/carries/carry-3881.json`: issue 3881 already has a live roster
group, `R11-CARRY-D0-CONTINUATION`. It was already on
`handoff/audit-r11-roster` at 694d2fad07, before this amendment, and is owned
by `handoff/r11-roster-land-3881`. The amendment adds no error.
