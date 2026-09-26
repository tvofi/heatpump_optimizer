# Round 9: what needs tvofi (after the RCA fold, 2026-09-26)

Every item below is one line, answerable in one word. The drafts are in each RCA write-up
(`/mnt/project-files/audit-r9/rca/<slug>/RCA.md`, also on `handoff/r9-rca-<slug>`), and the PR it
lands in is named. Where an RCA recommends a default it is marked **default**; silence on an item in
group (c) means the default. Nothing here blocks a PR outside the one named.

## (a) Policy edits: approve the draft? (all land in F11.5, one commit each, only once approved)

1. **A1 (P2)** `tools/audit/briefs/fixer.md` step 8: a P2 fix adds a P2 owners-registry entry in `tests/entities.py`, with census preconditions. Draft: rca/p2, "A policy change to fixer.md step 8". Approve?
2. **A2 (P2)** Should the A1 draft ride F11.5 (the policy PR) rather than F1.10? **default: F11.5.** Yes?
3. **A3 (solve-recompute)** `fixer.md` step 15: a per-row twin that fixes a recomputation finding re-measures its cost, and a parity-bound fix is a recorded partial, not a close. Draft: rca/avoidable-interpreter-bound-recomputation, "Policy proposal for tvofi". Approve?
4. **A4 (future-instant)** `tools/audit/briefs/D1.md` step 2: add the perturbation "an instant written by a clock ahead of the reader, across a restart". Draft: rca/persisted-future-instant-trusted-without-bound, "Needs tvofi" item 1. Approve?
5. **A5 (future-instant)** `fixer.md`: carry #775's rule that an age computed from a stamp ahead of the reading clock is unknowable, never 0. Same file, item 2. Approve?
6. **A6 (I5)** `tools/audit/briefs/root-cause.md` §2: an instance of an already-barriered class is not state (a); name why the barrier's unit missed it. Draft: rca/i5, "Policy proposal". Approve?
7. **A7 (I4)** `fixer.md` step 8: a fix that changes one reader of a governance concept registers the concept in `agreement.mjs` with every reader. Draft: rca/i4, "Residual, for tvofi". Approve?
8. **A8 (I4)** `tests/README.md` no-copies section: add "and one governance tool re-implementing another". Same draft. Approve?
9. **A9 (I3, optional)** `.claude/rules/defect-root-cause.md`: a check over a structured input is registered in `field_coverage.mjs`. Draft: rca/i3, "Policy: none needed … An optional proposal". Approve?

## (b) Budget raises and new budget entries (asked before the push, CLAUDE.md rule 2)

1. **B1 (F10.2, cpu-gate-blind)** A new `loop_cpu_ratio` entry in the COST budgets, value recorded on the canonical runner. Allow?
2. **B2 (F10.2, cpu-gate-blind)** New `stress_budgets.json` rows for the three throttling-valve scenarios (only if C9 is yes). Allow?
3. **B3 (F11.3, I3)** A new `files_tokens` cap in `policy_budgets.json` (a new cap at measured, not a raise). Allow?
4. **B4 (F11.5)** Raise the policy caps for fixer.md, D1.md, root-cause.md and tests/README.md by exactly what each approved draft adds, if `structure.py`/policy_lint says it must. Allow?
5. **B5 (F10.4, D7-s1-01)** Raise the coordinator structure budgets if pricing module-level helpers honestly raises them (existing plan item). Allow?

No budget raise is needed by P1, P2, P3, P5, P6, P9, P11, I1, I4 or I5.

## (c) Product and scope choices (the RCA's default in bold where it gives one)

1. **C1 (P1)** Keep out-of-domain values and blast radius (D1-s3-06, D1-s4-01, D1-s5-02, D1-s4-03) as per-seam fixes rather than commission a declared-domain barrier? **default: yes.**
2. **C2 (P3)** Narrow P3 to "a capacity floor or divisor" and move D2-s2-81-shaped instances to another class, or accept the wider reading as barriered only per sibling pair? **default: per-pair** (the plan already keeps D2-s2-81 in P3 that way). Per-pair?
3. **C3 (P6)** Keep arm S's solve (about 1-2 s) in the per-PR gate rather than nightly? **default: yes (per PR).**
4. **C4 (P11)** For hass doubles outside `tests/hastub` (D6-s1-81), accept per-instance contracts as the answer, rather than commission the harness-double refactor (every golden fixture pinned at SEK moves)? **no default.** Accept?
5. **C5 (I1)** Build a nightly writer that records the mutation kills to `main` so the 3,641-site pre-ratchet stock drains (an identity decision under 0011)? **no default.** Build?
6. **C6 (I1)** Commission a comparison-bound mutant operator (860 comparisons, cost unmeasured)? **no default.** Commission?
7. **C7 (I1)** Extend the single-line mutant format to multi-line tests, clamps and ternaries? **no default.** Extend?
8. **C8 (solve-recompute)** Production-call channel in the stress gate: subset form (pays at 2 capacity-tariff or 21 non-tariff installations) rather than the full sweep (pays at 6)? **default: subset.** Subset?
9. **C9 (cpu-gate-blind)** Sample the three throttling-valve plants at about 5,600 s per round, rather than cheaper members? **no default.** Sample?
10. **C10 (I3)** Build the derivation of the governance-check registration set (from `CHECKS`, `codeowners_gap.py` and stamp rule 4), or accept that a new check is covered only once registered? **no default.** Build?
11. **C11 (I4)** Beyond A7/A8, accept that a second reader with a different grammar for an unregistered concept stays undetected? **no default, procedural only.** Accept?
12. **C12 (I5)** For the 11 behaviour-prose findings no arm reaches: option 1 accept, 2 a reader-docs "do not restate what the code owns" rule, or 3 extend the arms (~60 test lines, drops D6-s1-02 and the D6-s2-04 count)? **no default; the RCA records no refusal.** 1, 2 or 3?
13. **C13 (future-instant, FI-sw3, F1.9)** Treat a stored `last_tick` ahead of now as an outage (#775's rule), rather than trust it? **no default in the RCA; #775 points to yes.** Outage?
14. **C14 (F11.4)** Fold the owed driver fixes into F11.4 with the I4 barrier? **default: yes (as planned).**
15. **C15 (D8-s2-01, F7.3)** Keep your A3(e) ruling (climate stays available without an indoor thermometer), so F7.3 closes as refused? Keep?
16. **C16 (D11-s1-01, F11.2)** Change the ruleset to dismiss stale approvals on push (or require last-push approval)? Change?
17. **C17 (D11-s1-04, F11.2)** A distinct delegated identity for agent-driven approvals, rather than a refusal in `budget_raise_gate.py`? Identity or refusal?
18. **C18 (D13-s1-02, F11.3)** Build the diff-equivalence verdict carry across merges-from-main (the judge weakened its saving to a few rounds)? Build?

## (d) Already decided by the orchestrator on an RCA's "tvofi's call"; object only if you disagree

1. **D1 (P9)** The card browser grid (~134 s) runs only on card-surface diffs through the scoped gate, `main` forced full. OK?
2. **D2 (P9)** The four new P9 instances went to a new F6.1b rather than enlarging F6.1. OK?
3. **D3 (P6)** F1.10 (P3 barrier) and F1.11 (P2 and P6 barriers) are not owner-gated: neither touches a code-owned or policy file (the P2 policy draft is A1, in F11.5). OK?

Counts: (a) 9, (b) 5, (c) 18, (d) 3; 35 in all.

## Orchestrator's recommendation for every item (reply "all recommended" to take them all)

- **(a)** Approve A1–A8. Skip A9 (optional; its RCA says no policy is needed).
- **(b)** Allow B1–B5, each at its measured value on the canonical runner.
- **(c)**
  - C1 yes; C2 per-pair; C3 per PR.
  - C4 accept, since the refactor would move every SEK golden fixture for three instances.
  - C5 not now: the per-site ratchet already stops the stock growing, and the drain needs an identity change and about 91 nights.
  - C6 no, because its cost is unmeasured.
  - C7 no for now.
  - C8 subset.
  - C9 sample, since the RCA shows it passes the cost test.
  - C10 accept.
  - C11 accept.
  - C12 option 3, about 60 test lines.
  - C13 outage, following #775's rule.
  - C14 yes.
  - C15 keep A3(e).
  - C16 change to dismiss stale approvals on push, as decision 0008 records.
  - C17 refusal, which is cheaper than a new identity.
  - C18 no, since the judge weakened the saving.
- **(d)** Keep D1–D3.
