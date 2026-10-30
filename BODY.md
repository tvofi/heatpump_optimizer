Triage batch 75 rules the three proposals of the root-cause probe R10-RCA-JIDOKA-YIELD, filed by the orchestrator s8 on 2026-10-30. The report is the body at `handoff-body/r10-rca-jidoka-yield` `c8f3acd99`. This is the next rolling batch under V182, after batch 74. It holds three rulings and two held roster ops. Both of the probe's measurements were re-run here, detached.

- **P309 (M1): ACCEPT narrowed, a new S group R10-RCA-JIDOKA-YIELD.** One pull request lands three things:
  - the RCA document under `dev/audit/rca/`, which is already an INERT prefix at `tests/closure.py:321`, so it needs no new closure classification;
  - the owed-carry arm on `carry_audit.py`'s body branch;
  - the correction of the WHY comment at `prepr.sh:974-978`.

  It is reproduced on the #3010 r1 body: 0 finding items at main, then `UNROUTED ... c78ecb78 [owed carry]` with rc 1, then rc 0 once routed. Over all 223 `handoff-body/*` tips, the arm flips 10 bodies: the probe's 9 real catches, plus the probe's own report, which quotes the defect in double quotes and a code span. So it is narrowed: text inside code spans and quotes is not read.
- **P310 (M2): ACCEPT as already carried, flagged for priority dispatch.** It is CARRY 0 of R10-FLY-RELAY-REVIEW-FF: `carry_audit.py landed`, `land-ops`, and `bus.sh dispatch` refusing on rc 1. It is unbuilt; `carry_audit.py` has only `check`, `pr`, `sweep` and `owners` at main. It is widened to accept the source topic as well as the item id, because the id is a text hash that a reword re-mints.
  - The policy part was approved by the orchestrator s8 under mandate 6329234399, recorded as the orchestrator's mandate approval, not tvofi's review.
  - The probe's enumerator, re-run over 1330 verdict commits, reproduces 21 carry-missing of 125 blocked since #2838 exactly. Shape A is 14 of the 21, about 252 min/day.
- **P311 (shape B): DEFER.** Six blocks split over five distinct liveness rules, none with three instances. The done-or-absorbed destination rule is already owned by R10-ORCH-ROSTER-SCHEMA (#2733 remainder, P305).

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`17356e1ca1bfcd26e05bdd587e394a53a65465e5`; the file is the whole diff against `437f1ba9b`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P309 and P310 as `ACCEPT` and P311 as `DEFER`. `triage_refusal` passes the R10-RCA-JIDOKA-YIELD group brief and the P310 carry; each returns None. A citation of P311 is refused: `dev/programme/triage/s6-batch75.md#P311 is not an ACCEPT ruling (DEFER)`.
- With P309's `Verdict: ACCEPT` changed to `Verdict: REJECT`, the group brief is refused: `dev/programme/triage/s6-batch75.md#P309 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and `brief_lint.mjs` over the live roster plus the new group reports exactly that one path error (`dev/programme/triage/s6-batch75.md: not in the tree`). That is why both ops stay held until this file is on main.

## Figures

- `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body` on `da4e6e9ea:BODY.md` gives `CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)` at main.
- The probe's appendix enumerator, re-run over `git log` of every `refs/remotes/origin/verdict` and `refs/tags/archive/verdict` ref (1330 commits), gives `all PRs post-2838 21 125 19 73 168` and `all PRs pre-2838 50 334 45 199 390`.
- The null control over every `refs/remotes/origin/handoff-body/*` tip gives `bodies=223 main_rc0=165 m1_rc0=155`, with 10 `FLIP` lines.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
