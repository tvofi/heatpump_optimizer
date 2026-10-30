Triage batch 64 rules the orchestrator's triage-queue line of 2026-10-30T00:33Z as P293: carry_audit's `## Evidence` arm flags a reviewer's measurements as unrouted findings, and the train parked #2969 and #2955 on them. It is the next rolling batch under V182, after batch 63 (#2974). It holds one ruling. Nothing in it is urgent: until the fix lands, the workaround is the existing `Carry: dismissed (item <id>)`.
- **P293: ACCEPT, narrowed, as one carry on R10-FLY-CARRY-DISPOSITION**, the group that owns `carry_audit.py`'s item classifier.
  - The sample is the last 30 merge verdicts (#2936 to #2974), run through `carry_audit.items(text, True)` at `043b111d0`. 7 `## Evidence` items are flagged, in 5 verdicts, and none of them is a finding.
  - Class A (4 items): a red check that is not this pull request's, worded outside `NOT_REQUIRED`'s one shape.
  - Class C (1 item): `--bump minor` inside a code span.
  - Class B (2 items): the review packet's "advisory" label.
  - Accepted: the code-span strip, and wider check-state shapes in `NOT_REQUIRED`. Together they clear 5 of the 7.
  - Rejected: counting an evidence item only when LEAD leads it. That drops #2465's shape (a defect left in place, not blocking) and the deferral arm, both pinned in the self-test.
  - Declined: freeing "advisory" by context. It is the word-level second classifier that P-G declined. The ruling sets a re-measurement on the next 30 merge verdicts.
  - The carry may be dispatched alone, ahead of the group's larger `landed` / `land-ops` carries.
  - One held roster op (`append-carry R10-FLY-CARRY-DISPOSITION`), released once this file is on main.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`52a6d97c5c9706343c80bdd0a9d93e957b62597c`; the file is the whole diff against `043b111d01c90ecb1220980df1d363c0b50bb37f`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P293 as `ACCEPT`. `triage_refusal` passes the carry text: it returns None.
- With `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same text is refused: `dev/programme/triage/s6-batch64.md#P293 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the carry's citation does not resolve, and the gate refuses it as not on the roster branch or origin/main.

## Figures

- The sample is the 30 highest-numbered remote `verdict/<pr>` refs whose `VERDICT.md` first line is `Fix review: merge`, #2936 to #2974.
- `carry_audit.items(text, True)` at `043b111d0` flags 9 items in that sample. 7 of them are under `## Evidence`, in #2937, #2939, #2955, #2959 and #2969.
- The tripping words per item come from the module's own `DEFERRED` and `NONBLOCK`, with `NOT_REQUIRED` applied first:
  - `does not block` in `19d896fa`, `f76b3ac3`, `158ad202` and `dde38e84`;
  - `minor` twice in `c21695db`, both inside `` `--bump minor` ``;
  - `advisory` in `3c055bc1` and `50a530e7`.
- With code spans removed by the module's `CODE_SPAN`, `c21695db` matches none of LEAD, DEFERRED and NONBLOCK.
- `policy_lint.mjs --budgets` at `043b111d0` names `carry_audit.py` 0 times.
- The carry was appended to a copy of the roster at the `handoff/audit-r10-roster` tip and linted: `TOTAL: 0 error(s)`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
