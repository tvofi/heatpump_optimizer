# R9-RO-13 handoff note (seat -> orchestrator)

head `d22172b6e504943f3b4878fb0a59b951cd75e50e` on `handoff/r9-ro-13`
(base `b2b6acd64`; three commits: `00512415e` failing-first, `bef73f43c`
gate extraction, `d22172b6e` policy_gate; body `BODY.md` on this ref).

- The PR touches `tools/policy/budget_raise_gate.py`, which CODEOWNERS pins
  @tvofi: it needs tvofi's approving review at the PR head; `--carry` cannot
  substitute for a code-owner review the ruleset demands.
- Corrections to the dispatch's facts, read back live 2026-10-09:
  - comment id 6083042222 answers 404; the recorded ruling is 6083743563;
    the grammar mandate in force is 6067089637 (scope all, until
    2026-10-11T12:00Z).
  - #2024 merged while this seat worked (16:29Z), its tvofi approval
    re-posted at `4f9d52694` at 13:01Z, so the stale-review demo the dispatch
    expected for it is instead shown on #2063's pre-recarry head, #2059's
    stale head and the closed no-approval #2036 (evidence
    `/Users/timmalmstrom/hpo-seats/ro13/evidence/null-control-1..5.txt`,
    `mandate-probe.txt`).
- Live objects moved during measurement: #2059 merged 16:27Z, #2024 16:29Z;
  #2063 and #2072 were open and LAND at the time of writing. The reviewer
  re-running a control must re-read the PR's state first.
- The gate's self-test is unchanged at 206 checks (the extraction delegates);
  merge_train's went 81 -> 92 checks, 0 failed. A mutation of the shared
  `mandate_state` window check reddens BOTH instruments (M3) -- the proof the
  reading is one, not copied.
- Evidence dir: `/Users/timmalmstrom/hpo-seats/ro13/evidence/`
  (`commit1-failing-first.txt`, `commit2-gate-green.txt`,
  `commit3-selftest.txt`, `mutations.txt`, `null-control-*.txt`,
  `mandate-probe.txt`, `prepr.txt`, `prepr-final.txt`).
- Scoped gate: `MODE: SCOPED -- 0 script(s) run` (both files inert); the two
  run_always lines were run and named in the body; `tests/structure.py`
  PASSED; claim files byte-identical; no budget or VERSION touch.
