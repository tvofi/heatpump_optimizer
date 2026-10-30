Triage batch 77 rules the orchestrator s8's proposal of 2026-10-30T22:16Z. The train's pre-flight parked HOTFIX #3013 on review `6533404333` item `fccf8846`, a `## Summary` line saying `away.py` is code-owned and needs tvofi's approval at merge. That is an approval precondition, not a finding. This is the next rolling batch under V182, after batch 76. It holds one ruling and one held roster op.

- **P314: ACCEPT narrowed, an amendment to P308 on R10-FLY-RELAY-REVIEW-FF (same carry, same pull request).**
  - In a merge verdict, P308's structural rule (a finding only with a LEAD, under a lead, or with a `Carry:` marker) covers every section except `## Findings`, `## Friction` and a block heading, not `## Evidence` alone.
  - Blocked verdicts and `## Findings` keep today's reading.
  - REJECTED: a keyword exclusion for approval or code-owner lines. It is a predicate shaped by one failure, it would free a real finding naming code ownership, and it adds a third word list to a predicate whose lists have not converged (P293, P306).
  - Not needed: a reviewer-side lead, which would be a policy edit to a capped contract.
  - Counted from the live train log: 21 `PARK #N findings` lines on 16 PRs. The approval-precondition shape is 1 (#3013). Two are bad destinations (P296's class), two are in `## Findings`, two are blocked verdicts, and the rest are measurement bullets, P308's class.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`2c78e0c29e284b839bb20ef6a92a7891c4d182ac`; the file is the whole diff against `a6e4a5afe`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P314 as `ACCEPT`. `triage_refusal` passes the carry text, which cites `triage: dev/programme/triage/s6-batch77.md#P314`: it returns None.
- With `Verdict: ACCEPT narrowed` changed to `Verdict: REJECT narrowed`, the same carry is refused: `dev/programme/triage/s6-batch77.md#P314 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or origin/main.

## Figures

- `python3 -I tools/audit/carry_audit.py pr 3013` at `437f1ba9b` gives `UNROUTED #3013 review 6533404333 item fccf8846 (## Summary) [non-blocking]`.
- `grep -cE '^PARK #[0-9]+ findings'` over the orchestrator's live `merge_train/train.log` gives 21. The distinct PR count from the same lines is 16.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
