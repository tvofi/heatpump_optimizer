DESIGN REVIEW: APPROVE

# Round 3 — independent adversarial review of design revision 3

Design: `handoff/orch-machinery` at `09174d94e24faa0a02cda531164ec55ac2c49577`
(force-with-lease over `14d2ac1c`). Rounds 1 and 2 remain at
`review/orch-machinery-design` (`76b6a5be2`, `46cd9d444`); this file is the
round-3 review and rewrites neither. Every command re-run by this seat; output in
`EVIDENCE-round3.md` (R1–R12). Live state re-read 14:40Z–14:55Z.

Diff `14d2ac1c..09174d94` touches only the two design documents (176+/44−); no
tree file changed and no section was restructured. The inventory stays at 50
contiguous rows; the M01–M50 rows are not touched.

## B10-R is genuinely closed

**B10-R.1, the import.** The rule now has three arms: `refs/heads/probe/` →
`probe-ref`; `refs/heads/handoff/` **and `refs/heads/handoff-body/`** →
`handoff-no-pr`; anything else refused. Re-run against the disposed file:

    89 refs/heads/handoff-body/
    113 refs/heads/handoff/
    1 refs/heads/probe/
    210 lines, 203 distinct refs, 209 distinct lines
    repeated refs: audit-r10-roster ×2, r10-rca-worktree-vanish ×6,
                   probe/cloud-seat-20261018 ×2  (7 repeated entries)

All 203 refs classify (89 + 113 + 1); the "last disposition per ref" rule matches
the seven repeated entries (one exact duplicate line, six same-ref re-disposals).
The claim reproduces exactly.

**B10-R.2, the missing kind.** The schema now has a `handoff-update` row:
derived, producer the handoff job, closed by a successful update removing the
topic's `handoff-failed.tsv` entry, by a moved `handoff/<topic>` (the next pass
retries at the new sha), or by `subject-absent`; `approve-held-runs` and
`dispatch` are reasons on it, not kinds; an OWED shape with no ledger kind is a
refusal. Re-run:

    OWED shapes: handoff-no-pr 29890, handoff-update 10, probe-ref 151,
                 reviewer-fire 1   (five shapes once the confirm arm is counted)
    relay source: approve-held-runs and dispatch lines exist; 0 live lines
    cloud-handoff-failed: 10 lines, format `<topic> <code-sha>`

The live kind (10) is covered with a closer that matches the relay's skip rule
(`cloud_relay.sh` retries only when the stored entry's sha no longer matches the
handoff tip). The two zero-live folded reasons do not block; see N11-R.

**Nothing regressed.** E3 (the fold fixture: 2 findings, 2 after disposal), E4
(rc 0, two "will retry"), E6 (live slot stolen, null control blocks), E12
(150/74/4 checks, 0 failed), and the roster counts (93 groups, 47 open, 14
gates, 8 short commits) all reproduce. The six residual figures revision 3
claims to have corrected — 52 tracked entries, the precise `cloud-disposed`
grep, six exact mandate strings, 210/203/209, eight proposals, the live
defect-1 shape — reproduce as stated.

The reservations below are non-blocking and new. None changes a mechanism, a
bound, a seam or a policy element, and none was carried from round 2.

---

## Non-blocking residuals

### N11-R — the folded `approve-held-runs`/`dispatch` reasons have no state, and the `why` has no field (non-blocking)

**Design:** §6.3's `handoff-update` row ("Its `why` carries the relay's failure
reason, including the two zero-live code paths (`approve-held-runs`, `dispatch`)"),
E20 ("state is `handoff-failed.tsv` (`<topic> <code-sha>`)"). **Command:** read
the relay's failure path and the live state file (R5, R12).

**Result:** the relay appends `<topic> <sha>` to `cloud-handoff-failed` **only**
when the update fails; the approve and dispatch failures happen *after* a
successful update and write nothing there. The live file is `<topic> <code-sha>`
with no reason field, so a `why` cannot carry which step failed. As written, the
two folded shapes have no producer state and no closer distinct from the
update's. Fix one of: give the file a third field and write it on any chain-step
failure, or make the two zero-live shapes their own derived kinds (they are 0
live, so nothing is lost today). The live `handoff-update` (10) is unaffected.

### N12-R — `instrument-self-tests` is not a required check (non-blocking)

**Design:** §8 Phase 3, §11 row N6-R ("`instrument-self-tests` is a required
check and a merge that reddens it cannot land"). **Command:** read the live
ruleset and the workflow (R6).

**Result:** ruleset 23698884's required contexts are 17 — `fast (3.14)`,
`browser`, `briefs`, `closure-scope`, `closures`, `typing`, `hassfest`,
`validate-hacs`, `policy-docs`, `wave-script`, `pr-contract`, `env-matrix`,
`Analyze (actions|javascript-typescript|python)`, `mutation`,
`budget-raise-gate`. `instrument-self-tests` is not among them, and no required
job `needs:` it. What the tree actually says (`governance.yml` above the job,
`pr-contract.yml`): a red there is "a red check at the head, which `pr-contract`
makes the body answer". So a red does not by itself block the merge; the body
must answer it. The ordering revision 3 chose — land each instrument with its
wiring — is still the right one; the justification should say that, not "a
required check".

### N13-R — E20's `approve-held-runs`/`dispatch` grep returns 3, not 2 (non-blocking)

**Command:** `grep -c 'logline OWED "approve-held-runs\|logline OWED "dispatch'`.
**Result:** 3 lines (one `approve-held-runs`, two `dispatch`). "2" is the number
of code paths, not the grep's output. The claim (both paths exist, 0 live)
holds; the evidence line should say 3 or count paths explicitly.

### N14-R — §11 says "nine figures"; the table has ten (non-blocking)

**Command:** count the §11 data rows. **Result:** 12 rows — the two B10-R
clauses plus ten N-residuals (N1-R through N10-R). The prose "two ledger clauses
and nine figures" undercounts by one. It is a count about the document it lives
in, the class this repository asks to derive.

### N15-R — E22 quotes `MANDATE_COVERS_POLICY` at line 121; it is line 123 (non-blocking)

**Command:** `grep -n 'MANDATE_COVERS' tools/policy/budget_raise_gate.py`.
**Result:** `116: MANDATE_COVERS_RAISE`, `123: MANDATE_COVERS_POLICY = ("all",)`.
The quoted comment block (117–121) and the mapping are right; only the constant's
line number is off.

### N16-R — the per-relay ~7 s derivation is not exposed by the self-test (non-blocking, UNVERIFIED)

**Design:** E21 ("74 checks in 56.5 s … ~8 relay fixtures => ~7 s per relay").
**Command:** re-run the anchors (R9). **Result:** my `ls-remote` took 0.55 s and
the self-test 37.87 s at a different load; the fixture count is not printed, so
the per-relay figure is inferred. The design already labels the 120 s bound a
first cut, so this changes nothing.

---

## Per-claim verification table (round 3)

Statuses over re-run commands or the tree facts a rule rests on.

| # | claim | verdict | finding |
|---|---|---|---|
| 1 | B10-R.1: three import arms classify all 203 refs | PASS | |
| 2 | B10-R.1: 7 repeated entries, last disposition per ref | PASS | |
| 3 | B10-R.2: `handoff-update` derived kind with closers | PASS | |
| 4 | B10-R.2: 10 live `handoff-update` lines | PASS | |
| 5 | B10-R.2: approve/dispatch reasons; unknown shape refuses | PASS | N11-R |
| 6 | N1-R: 52 tracked entries; `ls` 53 is `__pycache__` | PASS | |
| 7 | N2-R: `cloud-disposed` 0; loose `disposed` 1 | PASS | |
| 8 | N3-R: six exact mandate strings, ten naming | PASS | |
| 9 | N4-R: 210 lines / 203 refs / 209 distinct lines | PASS | |
| 10 | N5-R: eight proposals | PASS | |
| 11 | N6-R: the red-merge option is struck | PASS | |
| 12 | N6-R: `instrument-self-tests` is a required check | FAIL | N12-R |
| 13 | N7-R: `STALLED?`/`DONE?`, no new token | PASS | |
| 14 | N8-R: defect 1's live `not-started` shape | PASS | |
| 15 | N9-R: relay-probe 120 s is a stated first cut | PASS | |
| 16 | N9-R: the ~7 s per-relay derivation | UNVERIFIED | N16-R |
| 17 | N10-R: class→scope mapping from the gate grammar | PASS | |
| 18 | inventory: 50 rows, contiguous | PASS | |
| 19 | diff: only the two documents; no restructuring | PASS | |
| 20 | E3: fold fixture unchanged | PASS | |
| 21 | E4: fail-open unchanged | PASS | |
| 22 | E6: live slot steal + null control | PASS | |
| 23 | E12: self-tests 150/74/4, 0 failed | PASS | |
| 24 | roster: 93 groups / 47 open / 14 gates / 8 short | PASS | |
| 25 | E20: live OWED kinds 29890/10/151/1 | PASS | |
| 26 | E20: prefix split 89/113/1 | PASS | |
| 27 | E20: the approve/dispatch grep count | FAIL | N13-R |
| 28 | E22: mandate constants and mapping | PASS | N15-R |
| 29 | §11: "nine figures" | FAIL | N14-R |

**Counts: 29 rows — PASS 25, FAIL 3, UNVERIFIED 1.**

---

## What this revision gets right

- The import's three arms are the right classification and the right
  idempotency: last disposition per ref, with the relay's own move rule kept as
  legitimate re-disposals rather than deduped away.
- `handoff-update` is added at the right altitude — derived, not stored — and its
  closer matches the relay's actual skip rule rather than an idealised one.
- The residual figures were corrected at the source: E1 now derives 52 from
  `git ls-tree` and explains the `ls` 53; the gate count, the repeated-entry
  count, the proposal count and the pre-fix provenance are all re-derived, not
  restated.
- N6-R changed the migration ordering, not just the words: an instrument now
  lands with its wiring.
- Nothing passed in round 2 was restructured, weakened, or turned into a
  different mechanism.

The two clauses that blocked round 2 are closed on re-run. The residuals above
are one-line evidence corrections and one small schema question on two
zero-live shapes; none is a reason to withhold approval.
