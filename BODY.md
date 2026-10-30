Triage batch 64 rules two lines from the orchestrator. The first is its triage-queue line of 2026-10-30T00:33Z, ruled as P293: carry_audit's `## Evidence` arm flags a reviewer's measurements as unrouted findings, and the train parked #2969 and #2955 on them. The second is its P294 message of 2026-10-30: the tick never names a merge verdict that is waiting on its approval. It is the next rolling batch under V182, after batch 63 (#2974). It holds two rulings. The orchestrator holds the batch until it has 8 to 10 rulings or one turns urgent. P294's ruling asks for its group to be dispatched ahead of other instrument fly-ins.
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
- **P294 (the tick's missing approval level): ACCEPT, extended, as a new S fly-in, R10-FLY-TICK-APPROVAL-OWED** (`orchestrator_tick.py`, `owed_unactioned.py`).
  - `verdict_levels` (line 653) has a MERGE-READY arm only for CLEAN or UNSTABLE (line 689). So a `merge` verdict at the head of a BLOCKED/REVIEW_REQUIRED PR prints nothing.
  - `prs()` (line 552) does not fetch `reviewDecision`, so the fix has to add that field as well as the arm.
  - `verdict/2962`, `verdict/2976` and `verdict/2977` each read `Fix review: merge <head>`. #2976 now reads APPROVED and CLEAN at that same head.
  - Accepted: the `APPROVAL-OWED: #N <head8>` level and its `FAMILY` entry.
  - Extended: a catch-all, `UNLEVELLED: #N <head8> <state>/<decision>`, for a merge verdict at the head that no level names. This is the class barrier, held by a red arm and a mutation.
  - No separate root-cause seat is owed. Neither trigger in `defect-root-cause.md` fires. The idle-PR class already has its seat, `dev/audit/rca/R10-RCA-OWED-UNACTIONED.md`, and its countermeasure acts on printed lines only. Process state (c). The catch-all is the barrier a third instance owes.
  - One held roster op (`append-group R10-FLY-TICK-APPROVAL-OWED`), released once this file is on main.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`74ce3b18cde4c5862c3f49914666e98654f97ad2`; the file is the whole diff against `043b111d01c90ecb1220980df1d363c0b50bb37f`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P293 and P294 as `ACCEPT`. `triage_refusal` passes the P293 carry text and the R10-FLY-TICK-APPROVAL-OWED brief: both return None.
- With `Verdict: ACCEPT` changed to `Verdict: REJECT`, the same text is refused: `dev/programme/triage/s6-batch64.md#P293 is not an ACCEPT ruling (REJECT)`, and the same message for `#P294`.

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
- The R10-FLY-TICK-APPROVAL-OWED group was appended to a copy of the roster at that tip and linted: `TOTAL: 2 error(s)`.
  - One is the expected one: the cited `dev/programme/triage/s6-batch64.md` is "not in the tree" until this merges.
  - The other is an existing `R10-LEARNER-DEFAULT` path:line error, which is not this batch's.
- `orchestrator_tick.py` at `1148ee635`: `verdict_levels` is at line 653, the MERGE-READY condition at line 689 and the BLOCKED-UNFIXED arm at line 691. The `prs()` `--json` field list is at lines 552-554 and has no `reviewDecision`.
- `owed_unactioned.py:53` `FAMILY` lists `MERGE-READY:` and `BLOCKED-UNFIXED:` only.
- `git log -1 --format=%cI` on `verdict/2962`, `verdict/2976` and `verdict/2977` gives 2026-10-29T20:56+01:00, 2026-10-30T03:02+01:00 and 02:18+01:00. `gh pr view 2976` gives `reviewDecision: APPROVED`, `mergeStateStatus: CLEAN`, `headRefOid` `1381df1f`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
