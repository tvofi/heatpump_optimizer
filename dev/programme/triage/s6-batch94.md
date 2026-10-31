# Proposal triage, session s9, batch 94 (P336, P337)

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

## P337: the opener's loop is a session-local instrument, in its fourth hand-written copy

Verdict: ACCEPT, narrowed. The ruling is one carry on R10-FLY-OPENPR-ATOMIC (`carries-open`, S,
`files: tools/audit/seat/open_pr.sh`). That group owns the instrument this loop drives, and a driver
of `open_pr.sh` belongs in the same seam. The `handoff-update` arm is REJECTED: `cloud_relay.sh`
already owns that write.
- **Decision 0013 decides the home.** It says a reusable instrument lands in the tree, never only
  in a scratch directory. This loop is reused all session.
  - The s9 opener directory holds `driver.py` to `driver4.py`: 83, 95, 96 and 107 lines.
  - `driver4.py` reads `prio.txt`, `cap.txt` and `titles.json` from its own scratch directory, with
    a hard-coded `PRIO0` fallback.
  - The orchestrator reports that its priority list went stale twice today, which held the
    critical-path and hotfix opens behind instrument opens.
  - No later session can run it, test it or review it.
- **Narrowed to the open arm.** `driver4.py` also runs `update_pr.sh` on `handoff-update` lines.
  But `cloud_relay.sh`'s handoff arm (lines 86-92 at `a7dd7f50d`) already runs `update_pr.sh` for
  every open pull request whose handoff is not an ancestor of its head. It then approves held runs
  and dispatches the reviewer. Two writers of one PR update race each other, and the relay's run
  is the one that also dispatches. A relay `handoff-update` owed line names why the relay failed.
  The repair belongs to the relay, not to a second updater.
- **Liveness by its own children, not `pgrep -f`.** `driver4.py` counts live runs with
  `pgrep -fl 'open_pr.sh|update_pr.sh|remerge_main.sh'` (line 20). That reads every seat's runs,
  and pattern matches a process list that includes waiters. The tree instrument counts the runs
  it started, by PID, from its own state file.

Source: the orchestrator s9's triage-queue line of 2026-10-31T19:25:00Z (slip, recurring;
session-local instrument).

Instances:
- The four driver copies in the s9 opener scratch directory, measured with `wc -l`.
- `driver4.py` lines 20, 74 and 78-81: the `pgrep` count, the `PRIO0` literal, and the scratch
  `cap.txt` / `prio.txt` reads.
- The orchestrator's report of two stale priority lists today.

Cost:
- About 120 lines in a new `tools/audit/seat/open_driver.py`, plus its self-test and an
  `instruments/open_driver.py.md` page.
- The file must be classified, by closure or `INERT` (`tests/entities.py`).
- No policy file changes. Neither `open_pr.sh` nor the new file has a `policy_lint.mjs --budgets`
  row.
- Standing cost: one read of the tick board and one `ls-remote` per candidate per pass, at the
  opener's existing cadence.
- Payback inside round 10 is short, because the round closes 2026-11-01. The cost is decision
  0013's to pay in any case. The benefit carries into every later session that runs an opener
  seat.

Binding:
- Decision 0013 already requires the move.
- The four copies, and two stale priority lists in one day that held critical-path opens, measure
  the cost of not making it.
- Narrowing to the open arm avoids a second writer of the relay's update.

The carry:
1. **The tool and its candidates.** Add `tools/audit/seat/open_driver.py`. Each pass, it reads the
   tick board's `OWED ... handoff-no-pr refs/heads/handoff/<topic> <sha>` lines (the format in
   `driver4.py`'s `LINE`) from a board path it is given. For each line it:
   - skips a topic whose `handoff/<topic>` has moved off the sha;
   - skips a topic with no `handoff-body/<topic>`;
   - skips a topic whose `git cherry origin/main <sha>` lines are all `-` (already on main);
   - skips a topic for which a `fix/<topic>` or `fix/<topic>-pr` branch exists (board lag:
     an update, not an open).
2. **Order and cap.** Read them from `$HPO_STATE_DIR/open-priority.txt` and
   `$HPO_STATE_DIR/open-cap.txt` on every pass.
   - With no priority file, the default order is a group on `roster_lib.critical_path`, then
     `R10-HOTFIX-*`, then record topics (`triage-*`, `roster-*`), then the rest.
   - The default cap is 2 live runs.
3. **Titles and groups.** Read them from `$HPO_STATE_DIR/open-titles.json`. Map `triage-s<N>-batch<M>`
   to the round's triage group by rule. Otherwise, use a topic whose uppercase is a roster group.
   Anything else is logged `NEEDS-TITLE` and is not opened.
4. **Runs.** Launch `open_pr.sh <topic> <sha> <title> <group>` detached, and record its PID in the
   state dir. Count live runs only from those PIDs: no `pgrep`, no pattern. Log `START`, `RESULT
   rc=<n> <PR=/REFUSE lines>` and `SKIP <reason>`, in the line format the opener seat greps today.
5. **Fixtures**, over a fixture board and a throwaway repository:
   - a CP topic opens before an instrument topic;
   - a topic already on main is skipped;
   - the cap holds at 2;
   - null: an empty board starts nothing;
   - null: a `handoff-update` line is ignored, because the relay owns it.

   One mutant: drop the cherry check, and the on-main topic opens.
6. **Rejected:** the `handoff-update` arm (`cloud_relay.sh` owns it).
