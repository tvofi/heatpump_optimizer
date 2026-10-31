# Proposal triage, session s9, batch 94 (P336)

The rolling batch after batch 93. Facts were read at origin/main `a7dd7f50d` and at the round's
roster branch, `origin/handoff/audit-r10-roster`.

## P336: an owner-account comment pairing the revocation word with a mandate id voids the mandate

Verdict: ACCEPT as already carried, amended. The barrier is R10-FLY-MANDATE-REVOKE-GUARD
(`not-started`, size S, `files: tools/pr/gh_comment.py`). Its brief already is the proposal: import
the gate's pattern and grammar, refuse the post, and post a real revocation only through
`--withdraw-mandate <id>`. It was registered after the first instance and never dispatched. One
amendment carry closes two gaps the brief leaves:
- `gh_comment.py patch` is not guarded, only posts are;
- the brief imports the gate's regexes, not its predicate.
- **The gate's predicate** (`tools/policy/budget_raise_gate.py` at `a7dd7f50d`):
  - `MANDATE_ISSUE = 201` (line 115) and `MANDATE_REVOKED = re.compile(r"revok", re.I)`
    (line 120).
  - In `mandate_state`, lines 398-402: for every comment in the #201 thread, if the user is the
    owner, `MANDATE_REVOKED.search(body)` matches, and `re.search(rf"(?<!\d){cid}(?!\d)", body)`
    finds the id, the mandate "was revoked by tvofi's comment <id>".
  - It reads the comment's current body. So an owner-account edit (`gh_comment.py patch`) that
    adds the word revokes exactly as a new post does.
- **Instances: two, so this is the class.**
  - Comment 6322712314 (2026-10-21) is the one that cost "about 6 h of frozen mandated raise" (the
    group's brief).
  - Comment 6546832523 (2026-10-31) is a #201 state comment. It named the group
    R10-FLY-MANDATE-REVOKE-GUARD in the same text as the session mandate's id. #3006's
    `budget-raise-gate` read it at 18:43Z: "mandate <id> was revoked by tvofi's comment 6546832523"
    (the id is withheld here on purpose).
  - The second instance was written by a seat that holds the memory rule. A rule a seat must
    remember did not run, which is what a barrier is for.
- **Why the brief's form needs the amendment.**
  - **Patch.** A patch to an earlier #201 comment can add the word to a body that already names
    the id. The gate reads every thread comment, edited or not. A guard on `post` alone leaves the
    edit path open.
  - **One predicate, not two copies.** The brief imports `MANDATE_REVOKED` and `MANDATE_GRAMMAR`,
    but the whole-number id test (`(?<!\d){cid}(?!\d)`) is written inline in `mandate_state`. A
    guard that copies that test can drift from the gate in the one direction that matters: the
    guard passes what the gate revokes. Factor the test into `budget_raise_gate.revokes(body,
    cid)`, use it in `mandate_state`, and import that function into `gh_comment.py`.
- **Not ruled here: the live consequence.** The session mandate reads revoked to the gate for as
  long as comment 6546832523 stands on #201 with that text. That is a decision for the
  orchestrator and the owner. The options are an owner re-grant, or removing or editing the
  comment. An edit is itself read live, so the edited body must not still pair the word with the
  id. It is outside this seat's contract.

Source: the orchestrator s9's triage-queue line of 2026-10-31T18:50:00Z (defect, recurring, second
instance).

Instances:
- The two comments above.
- The gate's message on #3006 at 18:43Z.
- `git show origin/main:tools/policy/budget_raise_gate.py`, lines 115, 120 and 398-402.
- `git show origin/main:tools/pr/gh_comment.py`, line 424: `action` has the choices `post`,
  `patch`, `verify` and `self-test`, and line 442 handles `post` and `patch` together.

Cost: S, inside the existing group.
- About 15 lines: a `revokes(body, cid)` function in `budget_raise_gate.py`, used by
  `mandate_state`; the import and the refusal in `gh_comment.py` for both `post` and `patch`; and
  the self-test rows.
- Neither file has a `policy_lint.mjs --budgets` row; the `--budgets` output at `a7dd7f50d` names
  neither.
- `budget_raise_gate.py` is the pinned gate program. Moving its predicate into a function must
  leave the gate's own self-test green and its behaviour byte-equal, and the same diff must prove
  that.
- The group already carries the #3045 dS-value carry (`d8f1c951d`) on the same gate file, so one
  fixer takes both.

Binding:
- Each instance froze every mandated budget raise until a human acted, about 6 h the first time.
  The second instance froze #3006 at 18:43Z.
- The barrier is already designed and sized S, and it was never dispatched.
- The amendment closes the edit path and makes the guard read the gate's own test, at about five
  more lines.
- Dispatch it now, ahead of other instrument fly-ins. Do not wait for this batch to merge: the
  group's brief already authorises the build, and this carry lands when the batch does.

The carry:
1. **One predicate.** In `tools/policy/budget_raise_gate.py`, factor the revocation test into
   `revokes(body: str, cid: int) -> bool`, which is `MANDATE_REVOKED.search(body)` and the
   whole-number id match. `mandate_state` calls it, with behaviour unchanged, and the gate's
   self-test still passes.
2. **Guard both writes.** In `tools/pr/gh_comment.py`, apply the group's refusal to `patch` as
   well as `post`, for any target that is issue #201 (`MANDATE_ISSUE`). Read the body that would
   result: the new text for a post, the replacement text for a patch. Refuse it when
   `budget_raise_gate.revokes(body, cid)` holds for the id of a live MANDATE-grammar comment, unless
   `--withdraw-mandate <cid>` names that id.
3. **Fixtures.** Keep the brief's five rows, and add:
   - the field text of 6546832523 is refused on `post`;
   - the same text is refused on `patch`;
   - null: the same text without the word posts;
   - a mutant that re-implements the id test without the `(?<!\d)` guard fails a row where the
     id is a substring of a longer number.
