Triage batch 94 rules one proposal: the orchestrator s9's triage-queue defect of 2026-10-31T18:50:00Z. An owner-account #201 comment that pairs the revocation word with a mandate id voids that mandate in `budget_raise_gate`. This is the second instance. This is the next rolling batch after batch 93, with one ruling and one held roster op.

- **P336: ACCEPT as already carried, amended.** The barrier is R10-FLY-MANDATE-REVOKE-GUARD (`not-started`, S). Its brief already is the proposal, and it was never dispatched.
  - The amendment carry closes two gaps:
    - `gh_comment.py patch` is unguarded. The gate reads every #201 comment's current body, so an edit acts like a post.
    - The gate's whole-number id test is written inline, so a guard can only copy it. The carry factors it into `budget_raise_gate.revokes(body, cid)` and imports that one function, with the gate's behaviour byte-equal.
  - Ask: dispatch the group now, ahead of other instrument fly-ins.
  - Out of this seat's contract: the live state of the session mandate after comment 6546832523. The options are an owner re-grant, or removing or editing that comment, and the choice belongs to the orchestrator and the owner.
  - This ruling and its carry deliberately never write the mandate's id beside the word.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`da7efdc699fd92de5fa9acea979b245c7aa4915d`; the file is the whole diff against `a7dd7f50d`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P336 as `ACCEPT`. `triage_refusal` passes the carry, which cites `triage: dev/programme/triage/s6-batch94.md#P336`, and returns None.
- With P336's verdict changed to `REJECT`, the carry is refused: `dev/programme/triage/s6-batch94.md#P336 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or on origin/main.

## Figures

- `budget_raise_gate.py` at `a7dd7f50d`:
  - `MANDATE_ISSUE = 201` at line 115;
  - `MANDATE_REVOKED` at line 120;
  - the inline revocation test at lines 398-402 of `mandate_state`.
- `gh_comment.py` at `a7dd7f50d`: line 424 gives `action` the choices `post`, `patch`, `verify` and `self-test`.
- `node tools/policy/policy_lint.mjs --budgets` names neither file.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
