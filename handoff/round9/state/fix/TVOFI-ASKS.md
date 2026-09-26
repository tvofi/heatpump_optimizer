# Round 9: tvofi's decisions on the fix-plan asks (2026-09-26)

## DECISIONS

tvofi answered all 35 asks on decision cards at 19:16Z (message
`cmsg_01EL5jLi4rokGBbkaevYXSJV6CQVMDN96YfVMTcN5QGSx2`: "answer all cards, then file the issues and start
fixing"; the superseded card `cmsg_01EL5jLi4rokGBbkaevYXSJVJ2dpNicWumFP91ncYqNNqz` is ignored). Each row is
the card's answer as recorded in `CARDS.json`, the orchestrator's recommendation it answered, and where
the plan applies it (`FIX-PLAN.md` section 13; the roster and lane briefs carry each into its PR).
Where the answer differs from the recommendation, it is applied as given: A9, C1, C5, C6, C9, C10, C16, C18, D2.

| item | tvofi's answer | recommended | differs | applied in | card |
|---|---|---|---|---|---|
| A1 | Approve | Approve | no | F11.5 (fixer.md step 8) | `cmsg_01EL5jLi4rokGBbkaevYXSJV4ikQ1SRT574DCLeCBLAmDT` |
| A2 | F11.5 | F11.5 | no | F11.5 carries A1 | `cmsg_01EL5jLi4rokGBbkaevYXSJVTwq4eyvmahmTXVayR65x92` |
| A3 | Approve | Approve | no | F11.5 (fixer.md step 15) | `cmsg_01EL5jLi4rokGBbkaevYXSJVXYTmHYSyg1bFHaRnwqzXng` |
| A4 | Approve | Approve | no | F11.5 (D1.md step 2) | `cmsg_01EL5jLi4rokGBbkaevYXSJVUpJv89y6CKjM9kNbUCZCng` |
| A5 | Approve | Approve | no | F11.5 (fixer.md, #775) | `cmsg_01EL5jLi4rokGBbkaevYXSJVYAs7RfxLW6dcoscqMFEDBM` |
| A6 | Approve | Approve | no | F11.5 (root-cause.md section 2) | `cmsg_01EL5jLi4rokGBbkaevYXSJVVL6WPZ5kb4DrAgQVR3yDE5` |
| A7 | Approve | Approve | no | F11.5 (fixer.md step 8) | `cmsg_01EL5jLi4rokGBbkaevYXSJV2H1MQrFCSVrzTP4xTZsHBf` |
| A8 | Approve | Approve | no | F11.5 (tests/README.md) | `cmsg_01EL5jLi4rokGBbkaevYXSJVT82cWLF6677T3YAMkJc1bf` |
| A9 | Approve (overrode Skip) | Skip | **yes** | F11.5 (defect-root-cause.md), clause aligned to C10's derived set | `cmsg_01EL5jLi4rokGBbkaevYXSJVXsijNLpDQVpFp96zQzv296` |
| B1 | Allow | Allow | no | F10.2 | `cmsg_01EL5jLi4rokGBbkaevYXSJVP4Wc9sVcBrwWv2ng6E7bcm` |
| B2 | Allow | Allow | no | F10.2, rows only for the cheaper members C9 picks | `cmsg_01EL5jLi4rokGBbkaevYXSJV5abXUwm9tYDVSmcBoHPgTi` |
| B3 | Allow | Allow | no | F11.3 | `cmsg_01EL5jLi4rokGBbkaevYXSJV1YFogEjbTZzHLuEQznLmJE` |
| B4 | Allow | Allow | no | F11.5 | `cmsg_01EL5jLi4rokGBbkaevYXSJVVywdYaqLosWchfKhTdcQW7` |
| B5 | Allow | Allow | no | F10.4 | `cmsg_01EL5jLi4rokGBbkaevYXSJVG53fL5E9FGCjNZdQki6xnJ` |
| C1 | Domain table (overrode Per seam): new declared-domain barrier PR | Per seam (yes) | **yes** | new F9.3: P1 declared-domain barrier, strongest model, after F1.6; covers D1-s3-06, D1-s4-01, D1-s5-02, D1-s4-03; F3.2, F3.3 and F1.6 briefs carry it | `cmsg_01EL5jLi4rokGBbkaevYXSJVVXhePMyoUc3pPdRop8HcF7` |
| C2 | Per pair | Per pair | no | F1.10 (P3 arm b), unchanged | `cmsg_01EL5jLi4rokGBbkaevYXSJV9WKhBboD8wpb6K86j9saqS` |
| C3 | Per PR | Per PR | no | F1.11 (P6 arm S in the per-PR gate) | `cmsg_01EL5jLi4rokGBbkaevYXSJVV42AX1wSBrgthYQtcuYAZq` |
| C4 | Per case | Accept (per case) | no | F8.3 (D6-s1-81 per-instance contract); F1.7 unchanged | `cmsg_01EL5jLi4rokGBbkaevYXSJVRPPjq98RiLL6A1Wx3ufepJ` |
| C5 | Build (overrode Not now): nightly mutation-kill ledger writer, new identity under 0011 | Not now | **yes** | new F10.5: nightly kill-ledger writer, tvofi-gated; the writer App and credential are a Mac/tvofi action | `cmsg_01EL5jLi4rokGBbkaevYXSJVKz4c3Uv4wxAESnyYKwn8zS` |
| C6 | Commission (overrode No): comparison-bound mutation operator, own PR | No | **yes** | new F10.6: comparison-bound operator, cost measured before it is enabled | `cmsg_01EL5jLi4rokGBbkaevYXSJVA5vdGfkcvpCAdPKYbqzHmg` |
| C7 | Not now | Not now | no | F10.3 records the multi-line residual | `cmsg_01EL5jLi4rokGBbkaevYXSJV2qWadk7uqGzKVpn9xs2jcf` |
| C8 | Subset | Subset | no | F10.2 | `cmsg_01EL5jLi4rokGBbkaevYXSJVWjJo2HYWnqvxhiNQrUwMJh` |
| C9 | Cheaper (overrode Sample): sample cheaper valve-axis members; B2 rows only for those | Sample | **yes** | F10.2 samples cheaper valve-axis members and records the residual blind spot | `cmsg_01EL5jLi4rokGBbkaevYXSJV2T2vQzRzHFqyJynUj9xTn4` |
| C10 | Derive (overrode Registration): derive governance-check set from CHECKS/CODEOWNERS/stamp rules | Accept (registration) | **yes** | F11.3 derives the check set from CHECKS, codeowners_gap.py and stamp rule 4 | `cmsg_01EL5jLi4rokGBbkaevYXSJVRgFei78G7gFRS46fC8Wv8y` |
| C11 | Accept | Accept | no | F11.4 records the residual as accepted | `cmsg_01EL5jLi4rokGBbkaevYXSJV8FhCX1di3H5eDemLXSwSNK` |
| C12 | Extend checks | Option 3 (extend) | no | F10.4 (I5 arms) | `cmsg_01EL5jLi4rokGBbkaevYXSJVPFww7Bwv5xKH96BASQ7ebh` |
| C13 | Outage | Outage | no | F1.9 (FI-sw3 treated as an outage) | `cmsg_01EL5jLi4rokGBbkaevYXSJVHS9Tz1wcyspjWJhosPggfJ` |
| C14 | Fold in | Fold in | no | F11.4 carries the driver fixes | `cmsg_01EL5jLi4rokGBbkaevYXSJV6ZxrK3iKgGM7KGGKpZRhYo` |
| C15 | Keep (A3(e) stands; D8-s2-01 refused; F7.3 dropped) | Keep | no | D8-s2-01 refused against A3(e); F7.3 dropped; #1689 closed as not planned | `cmsg_01EL5jLi4rokGBbkaevYXSJVAkqktP4mjxo5JEYMQUD7Uu` |
| C16 | Leave | Change | **yes** | D11-s1-01 refused by tvofi, recorded in #1648; F11.2 drops the decision-0008 edit; no policy edit | `cmsg_01EL5jLi4rokGBbkaevYXSJVJwW4gJaJ8i35S9yrhrH3dc` |
| C17 | Refusal | Refusal | no | F11.2 (budget_raise_gate.py) | `cmsg_01EL5jLi4rokGBbkaevYXSJVMMwonNSMUDhJ2Hzc5tPcXt` |
| C18 | Build | No | **yes** | new F11.6: diff-equivalence verdict carry (D13-s1-02), split from F11.3 | `cmsg_01EL5jLi4rokGBbkaevYXSJVDxWrZvQCUnNr94c4mrQd4B` |
| D1 | Card diffs only | Keep | no | F6.3, unchanged | `cmsg_01EL5jLi4rokGBbkaevYXSJVDqUyXgpZpHQ1Gc9caHysYe` |
| D2 | Enlarge F6.1 | Keep F6.1b | **yes** | F6.1b merged into F6.1, over the five-item cap by recorded exception | `cmsg_01EL5jLi4rokGBbkaevYXSJVVeftpSQbxtudLTGkdZE6Ds` |
| D3 | Ungated | Keep (ungated) | no | F1.10, F1.11 ungated, unchanged | `cmsg_01EL5jLi4rokGBbkaevYXSJV7gLYYDp953i9jWVUP2TM4x` |

Counts: (a) 9, (b) 5, (c) 18, (d) 3; 35 answered, 0 open; 9 differ from the recommendation.

**Correction to the ask as put.** C15's parenthetical read "climate stays available without an indoor
thermometer". A3(e) is the opposite: the `tests/entities.py` A3(e) pin keeps the climate entity
unavailable with no thermometer, which is what D8-s2-01 reports. "Keep" keeps the tree's behaviour and
refuses D8-s2-01; nothing in the tree changes.

**What the answers leave to a person.** F10.5's writer identity (decision 0011) needs its App created,
installed and its credential stored: a Mac/tvofi action, not a fixer's. Every allowed budget raise
(B1-B5) and every approved policy draft (A1-A9) still merges only on tvofi's approving review at the PR's
head (budget-raise-gate, decision 0013; code ownership).

## The asks as put (2026-09-26, before the answers)

The drafts are in each RCA write-up (`/mnt/project-files/audit-r9/rca/<slug>/RCA.md`, also on
`handoff/r9-rca-<slug>`).

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
