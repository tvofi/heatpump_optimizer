DESIGN REVIEW: CHANGES-REQUIRED

# Round 2 — independent adversarial review of design revision 2

Design: `handoff/orch-machinery` at `14d2ac1cded1b1ff3cf7765b581652850cdc393b`
(force-with-lease over the round-1 `2b159e46`). Round 1's verdict is at
`review/orch-machinery-design` `76b6a5be2` and is not rewritten here.
Every command re-run by this seat; output in `EVIDENCE-round2.md` (sections
R1–R18). Live state re-read 12:30Z–12:45Z.

Diff `2b159e46..14d2ac1c` touches only the two design documents (972+/1065−);
no tree file changed. The inventory's M01–M46 rows were diffed row by row: every
change is additive or corrective, none regresses a round-1 PASS.

## What this round is

Fifteen of round 1's sixteen blocking findings are **genuinely closed**. One is
not: **B10**, the obligations ledger. Two clauses of it do not reproduce, and
both are concrete enough to name numbers:

1. **The import refuses 89 of the 203 disposed refs.** §6.3 says the kind is
   "inferred from the `refs/heads/probe/` vs `handoff/` prefix". The disposed
   file holds 89 refs under `refs/heads/handoff-body/` (113 `handoff/`, 1
   `probe/`). `refs/heads/handoff-body/...` starts with neither stated prefix,
   so the literal rule refuses 89 refs and imports 114, not "203 refs". The
   relay's own `handoff-no-pr` kind covers both prefixes (`Every handoff/* or
   handoff-body/* ref ...`), so the fix is one classification arm — but as
   written the claim "203-ref import" is false and 89 obligations survive the
   migration.
2. **A live kind is missing from the schema.** The relay emits five OWED shapes;
   the ledger's kind table covers `handoff-no-pr`, `probe-ref`, `reviewer-fire`
   and the confirm-arm's `verdict-unposted`, but not `handoff-update` (10 live
   lines at this read; `approve-held-runs` and `dispatch` are code paths with 0
   live lines). Phase 1 retires the relay's OWED writes, so a failed handoff
   update stops being an obligation anywhere: the per-pass job outcome is not a
   per-topic retry obligation, and `<ledger>.handoff-failed` is not in the new
   schema.

Everything else — the sha-aware disposal figure, the gate predicate, commit
resolution, the reconciler's ownership, the absorbed-edge closure, the
derived/event split and `subject-absent`, the unreadable contract, the fixture
mutation pins, the 50 rows, the relay-post retirement, the split jobs and the
liveness migration — reproduces or is stated as a testable rule with its
supporting facts verified. Saying otherwise would be carrying a finding to look
consistent.

Verdict rationale: a design that would import 114 of 203 dispositions and drop a
live obligation kind cannot be the "single source for OWED" it claims to be. Two
clauses, both one edit wide, block.

---

## Blocking finding

### B10-R — the ledger's import and kind inventory are incomplete (blocking; B10 re-opened on these two clauses only)

**Design:** §6.3 (the kind table; "The import is one-time and idempotent: 210
lines → 203 refs ... kind inferred from the `refs/heads/probe/` vs `handoff/`
prefix ... a ref it cannot classify is refused and reported"), §8 Phase 1.

**Commands:** classify the 203 disposed refs by prefix; enumerate the live OWED
shapes in `cloud-relay.log` and in `cloud_relay.sh` (`EVIDENCE-round2.md` R3).

**Result:**

    disposed refs: 203   refs/heads/handoff-body/: 89
                         refs/heads/handoff/: 113
                         refs/heads/probe/: 1
    live OWED: handoff-no-pr 29877, handoff-update 10, probe-ref 151,
               reviewer-fire 1, approve-held-runs 0, dispatch 0, confirm-arm 0

- The import rule classifies 114 refs; the 89 `handoff-body/` refs are refused.
  "203-ref import" is not what the stated rule does. Add `refs/heads/handoff-body/`
  to the `handoff-no-pr` arm (the relay's own kind already spans both).
- `handoff-update` has no kind in the ledger. Its producer is the handoff job's
  failed update, its state is `<ledger>.handoff-failed`, and its resolution is
  the next successful update or the ref moving — all of which exist today; the
  new schema drops the visibility. Add it as a derived kind (topic has a failed
  update and the ref has not moved) with those clauses. The two zero-live code
  paths (`approve-held-runs`, `dispatch`) should be named too, or the design
  should say a relay OWED shape with no ledger kind is a refusal.

The rest of B10 is closed: the derived/event split, the named producer and
closer per kind, `subject-absent` (verified: 26 never-disposed subjects, 13 gone
/ 13 present at this read), the one-writer-module rule, and `bus.sh confirm` as
the `verdict-unposted` closer.

---

## Non-blocking residuals (all new or corrected-in-part)

### N1-R — "53 entries" is an ignored `__pycache__`, not the tree (non-blocking)

The tree at this ref (and at `a2b25bbc5`) has **52** tracked entries:
`git ls-tree --name-only HEAD tools/audit/seat/ | wc -l` → 52. The live
instrument checkout at the same HEAD returns 53 from `ls`, and the 53rd entry is
`__pycache__/` (`diff` of `ls -A` against `ls-tree`; `git status --ignored`
marks it `!!`). The design's explanation — "the reviewer measured 52 at its
read; instruments land and the count moves" — is false: no tree file changed, and
the difference is an import cache. The 37 self-testing scripts figure is right.

### N2-R — the `disposed|cloud-disposed` grep returns 1, not 0 (non-blocking)

`grep -c 'disposed\|cloud-disposed' tools/audit/seat/orchestrator_tick.py` → **1**
(the word "disposed" in `dispositions`' docstring at line 1693). The precise
pattern `grep -c 'cloud-disposed'` → **0**, so the substantive claim (the tick
never opens the disposal file) holds; use the precise pattern.

### N3-R — six gates carry the exact mandate string, not four (non-blocking)

E8b says "four carry the exact string `mandated approval under 6175172275`". At
this roster tip, **six** do (`R10-SETPOINT-BOOST`, `R10-CEILING-PROBE`,
`R10-DEMAND-OVERBOOK`, `R10-BUFFER-STORE`, `R10-COP-PARTLOAD`,
`R10-UPDATE-PR-SIGNALS`); ten name the mandate in some form, and four name
neither. The B2 conclusion (14 ready / 0 owner) is unaffected.

### N4-R — "7 duplicate lines" is 7 repeated ref entries, one exact duplicate (non-blocking)

The disposed file has 210 lines, 203 distinct refs and **209 distinct lines**:
one line is a byte duplicate; the other six repeat a ref at a different sha
(the relay's legitimate re-disposal after a move). "203 refs" is right; say
"seven repeated ref entries, one an exact duplicate line", because an idempotent
import must take the last disposition per ref, not dedupe lines.

### N5-R — §6.8 says "five proposals"; §8 lists eight (non-blocking)

§8's policy table rows i–viii are eight; §6.8's column and its closing row say
"five proposals". The list is now complete (it covers the four elements round 1
found missing), so the count is a stale literal. It is the kind of figure this
repository asks to derive, not carry.

### N6-R — the Phase 3 "land earlier and stay red" option reddens main (non-blocking)

§8 says the three instruments "may land earlier but stay unwired and red in
`instrument-self-tests` until then". A merge that turns a required check red
cannot land; the sentence is an impossible path. Strike it and keep the sound
ordering: land each instrument with its wiring, after R10-CI-LAYOUT's last PR
(or as a listed file in it).

### N7-R — `SEAT-STALLED` is not the tick's token (non-blocking)

§6.2 says a seat with no PR "prints `SEAT-STALLED`"; the existing WORKERS code
prints `<seat>: STALLED? ...` (`orchestrator_tick.py:one_worker`). Neither a
parser nor a reader will recognise the invented spelling. Use the existing
grammar or change the code and the readers in one place.

### N8-R — arm 1's fixture does not carry the pre-fix expression (non-blocking)

§6.7 says each arm carries "the pre-fix expression as a fixture (recovered from
the `.bak` files)". Defects 2, 3 and 4 are in the `.bak` files at the quoted
lines (verified: `gen.py.bak:4,89,148`). Defect 1's override is in the **live**
file (`groups["R10-ARCH-DOCS"] = {… "stage": "not-started"}`) and is
`not-started`, not the "in-review hint" the arm's fixture injects. The mutation
pin still flips, but the provenance sentence is wrong for arm 1.

### N9-R — relay-probe's 120 s bound is not measured (UNVERIFIED)

Principle 4 says every timeout is "above its measured work". The evidence
measures the handoff arm (18:40–36:50) but not a successful probe/relay pass
(fetch + grading + `push-verdict` + `confirm`). The `relay-probe` 120 s timeout
is therefore a choice, not a measured bound. Measure it or say it is a first
cut.

### N10-R — the class→scope mapping is unstated (non-blocking)

§6.4's predicate is "class × mandate coverage". The mandate grammar
(`tools/policy/budget_raise_gate.py`: `scope (code-owned|budget-raise|all)`) has
no `policy` token, so a policy gate is covered only by `all`; `budget` by
`budget-raise|all`; `code-owned` by `code-owned|all`. With the only live mandate
at scope `all` the answer is unaffected, but state the mapping or a narrower
mandate will be read wrongly.

---

## Round-1 blocking findings: disposition

| finding | status | evidence |
|---|---|---|
| B1 sha-aware disposal figure | **closed** | 203 refs/210 lines, 199 same/3 moved, 1 unowed — reproduced exactly (R3) |
| B2 gate predicate → 14/0 | **closed** | rule stated; `mandate_state` parses the scope and `covers`; live mandate is `all` (R5, R6) |
| B3 commit resolution | **closed** | `--disambiguate`: 7 unique ancestors, 1 unresolved (R7) |
| B4 second reconciler | **closed** | brief requires `roster_sync.py --apply`; file on no ref; design adds no op (R8) |
| B5 R10-CI-LAYOUT seam | **closed** | seam named; new-file wiring in tests.yml/governance.yml/ci.yml; ordering stated (N6-R on one option) |
| B6 beatd answers S4 | **closed** | seats via the existing WORKERS/`--workers-file` JSON contract (R9) |
| B7 600 s relay timeout | **closed** | `relay-probe` 120 s and `handoff` 3600 s; 3600 s > measured 2210 s, live 2543 s (R10) |
| B8 sweep liveness | **closed** | `beatd` writes `tick/alive` and the sweep template's step 5 changes in the same PR (R10) |
| B9 absorbed edge closure | **closed** | `ABSORB-EDGE-MISSING` unless every edge is on the absorber or its transitive closure (design text) |
| B10 ledger completeness | **NOT closed** | import prefix and `handoff-update` kind (B10-R) |
| B11 unreadable contract | **closed** | missing = first run; unreadable = UNREADABLE; `beatd.jobs.json` refuses to start |
| B12 plan-page arms | **closed** | fixture mutation pins; `.bak` pre-fix expressions verified (N8-R on arm 1) |
| B13 stage rule | **closed** | stated topic-suffix rule gives 10, including `-p0` (R11) |
| B14 policy list | **closed** | eight proposals, covering the four missing elements (N5-R on the count) |
| B15 inventory | **closed** | 50 contiguous rows, M47–M50, M02 names MERGE-READY/BLOCKED-UNFIXED (R12) |
| B16 relay-post | **closed** | dropped; `bus.sh confirm` closes `verdict-unposted`; relay OWED writes retired (B10-R for the kind list) |

## Round-1 non-blocking findings: disposition

N1 fixed in part (37 scripts right; 53 still wrong, N1-R). N2 fixed (E9 command
and the local-time label). N3 fixed (state-docs one-shot). N4 fixed (observable
retirement rule). N5 fixed (CI wiring named). N6 fixed in part (203 refs right;
"7 duplicate lines" wrong, N4-R). N7 fixed (board meaning stated).

---

## Per-claim verification table (round 2)

Statuses over re-run commands or, for a design rule, over the tree facts it
rests on. A quantified claim that reproduces only in the author's words is FAIL.

| # | claim | verdict | finding |
|---|---|---|---|
| 1 | B1: 203 refs / 210 lines / 199 same / 3 moved | PASS | |
| 2 | B1: the combined `disposed`/`cloud-disposed` grep = 0 | FAIL | N2-R |
| 3 | B1: the tick never opens `cloud-disposed` | PASS | |
| 4 | B2: class × parsed scope → 14 ready / 0 owner | PASS | |
| 5 | B2: "four" gates carry the exact mandate string | FAIL | N3-R |
| 6 | B3: `--disambiguate` + ancestry; only unresolvable is invalid | PASS | |
| 7 | B4: no second reconciler; `roster_sync` on no ref | PASS | |
| 8 | B6: seats via WORKERS over `workers.json` | PASS | |
| 9 | B6: `SEAT-STALLED` is the tick's token | FAIL | N7-R |
| 10 | B7: probe and handoff split; 3600 s bound | PASS | |
| 11 | B7: relay-probe's 120 s is above measured work | UNVERIFIED | N9-R |
| 12 | B8: `alive` + sweep step 5 in one PR | PASS | |
| 13 | B9: absorbed needs the edge closure | PASS | |
| 14 | B10: derived/event split with producer and closer | PASS | |
| 15 | B10: `subject-absent` (13 gone / 13 present) | PASS | |
| 16 | B10: 203-ref import, unclassifiable refused | FAIL | B10-R |
| 17 | B10: kinds cover the relay's live OWED shapes | FAIL | B10-R |
| 18 | B11: unreadable contract per store | PASS | |
| 19 | B12: five arms are fixture mutation pins | PASS | |
| 20 | B12: pre-fix expressions from the `.bak` files | PASS | |
| 21 | B12: arm 1 carries its pre-fix expression | FAIL | N8-R |
| 22 | B15: 50 rows, M47–M50, M02 MERGE-READY | PASS | |
| 23 | B16: relay-post dropped; bus closes; relay OWED retired | PASS | |
| 24 | B13: the stated stage rule gives 10 incl. `-p0` | PASS | |
| 25 | B14: the policy list is complete | PASS | |
| 26 | B14: §6.8's "five proposals" matches §8 | FAIL | N5-R |
| 27 | B5: the CI seam is named | PASS | |
| 28 | B5: "land earlier and stay red" is viable | FAIL | N6-R |
| 29 | E1: 53 entries in the tree | FAIL | N1-R |
| 30 | E1: 37 self-testing scripts | PASS | |
| 31 | E3: fold fixture unchanged | PASS | |
| 32 | E4: relay fail-open unchanged | PASS | |
| 33 | E5: cadence (149 passes, median 401, max 2,654) | PASS | |
| 34 | E6: live slot steal + null control | PASS | |
| 35 | E7: `Terminated: 15`, no timeout in the chain | PASS | |
| 36 | E8: 93 groups / 47 open / 14 gates / 8 short commits | PASS | |
| 37 | E8c: short commits resolve, 1 unresolved | PASS | |
| 38 | E9: liveness command and local-time label corrected | PASS | |
| 39 | E10: `gen.py` and `.bak` shapes | PASS | |
| 40 | E12: self-tests 150/74/4, 0 failed | PASS | |
| 41 | E14: four missing mechanisms present | PASS | |
| 42 | E16: `selftest_wiring --check` 37/37 | PASS | |
| 43 | E17: `roster_sync.py` absent on four refs | PASS | |
| 44 | E19: 26 never-disposed, 13 present / 13 gone | PASS | |
| 45 | inventory M01–M46 not regressed | PASS | |
| 46 | §6.3: "7 duplicate lines" | FAIL | N4-R |
| 47 | class→scope mapping stated for a narrower mandate | UNVERIFIED | N10-R |

**Counts: 47 rows — PASS 35, FAIL 10, UNVERIFIED 2.**

---

## What round 2 gets right

- The sha-aware correction is exactly right and independently reproduced,
   including the awkward part (199/202, 3 moved) and the surviving reason.
- The reconciler ownership is resolved cleanly: the design no longer adds an
  instrument; `roster_sync.py --apply` is R10-ROSTER-OPS's, verified on no ref,
   and the three predicates are genuinely additions to an existing requirement.
- The gate predicate is now the right predicate, backed by an existing reader
  (`budget_raise_gate.mandate_state`) that already parses the scope.
- The beat's table fixes both bounds that were wrong: the long work gets its own
  job and a timeout above the measured maximum, and the reader never runs a
  writer.
- The liveness migration is now a single PR with both halves, which is the only
  ordering that does not reintroduce the double start.
- The plan-page arms are fixtures, not pointers at a file that was repaired
  while the author read it — the correct answer to a moving measurement.

Two clauses in the ledger remain. Fix the prefix classification and add
`handoff-update`, and this design is implementable.
