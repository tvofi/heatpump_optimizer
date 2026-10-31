# Proposal triage, session s9, batch 94 (P336-P344)

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
   - skips a topic that is already on main. It asks `ledger.py landed`, the classifier
     `cloud_relay.sh` (lines 99-104) and `bus.sh orphans` already use when they fold
     `handoff-no-pr`. A `git cherry` check survives only as a guard against board lag, never as
     the rule (script census, Part B row 1);
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

   One mutant: drop the `ledger.py landed` check, and the on-main topic opens.
6. **Rejected:** the `handoff-update` arm (`cloud_relay.sh` owns it).

## The script census (P338-P344)

Seven proposals filed together by the orchestrator s9's script-census seat, 2026-10-31T19:36:37Z,
under the owner's rule (tvofi, 2026-10-31, verbatim): "reusable scripts in a generalized form always
belongs on main if they are not redundant, wrong or have negative consequences on the machinery".
- **What the rule changes.** It settles where a reusable script belongs. A census proposal is
  REJECTED here only for one of the rule's three exclusions: redundant, wrong, or harmful to the
  machinery. Its cost decides its route and priority, not whether it lands.
- **Sequencing.** All seven are instrument work, and round 10 closes 2026-11-01. They queue below
  critical-path and production groups (tvofi's priority), and any of them may run in round 11.
- **The census.** `s9/script-census.md`, 687 files classified, is out of tree. Its counts are cited
  from that table. Each ruling's in-tree fact was checked at `a7dd7f50d`.

## P338: about 60 session-local ref and board watchers re-implement one loop

Verdict: ACCEPT, narrowed, as part of one new S fly-in, **R10-FLY-SEAT-WAITERS**, together with
P339. The group's files are `tools/audit/seat/seat_watch.sh` (new) and
`tools/audit/seat/proof_watch.py`.
- **Not redundant.** `bus.sh watch` reports verdict refs awaiting a post, `ci-watch.sh` reports PR
  check states, and `pulse.py` reads the board. None of them reports a moved `handoff/`,
  `handoff-body/` or `design/` ref against a baseline. `git ls-tree origin/main
  tools/audit/seat/` lists no other watcher. The census counts 60 hand copies.
- **Form.** `seat_watch.sh --refs GLOB... [--exclude REGEX] --state FILE --alive FILE --every S
  --passes N`.
  - The state lives under `$HPO_STATE_DIR`. The default interval is 240 s, with a floor of 60 s.
  - It exits 0 on the first actionable move, printing `MOVED <ref> <old> <new>`.
  - It exits 1 after N passes, printing one heartbeat line.
  - A move on a ref whose pull request is MERGED or CLOSED is counted in the state file, never
    reported. It reads one open-PR listing per pass, the same filter P332 gives the relay.
- **Narrowed.** No per-seat role logic. Which refs a role watches is the caller's `--refs` and
  `--exclude`. The seat-alive nonce stays with R10-FLY-SEAT-ALIVE-ID (`pulse.py`).

## P339: about 67 session-local waiters poll a pinned head until its checks conclude

Verdict: ACCEPT, narrowed, in R10-FLY-SEAT-WAITERS, as a `--wait-only` mode of `proof_watch.py`.
The proposal's `contains` and `--run` subcommands are REJECTED.
- **Not redundant, but an existing instrument's shortfall.** `proof_watch.py` already holds the
  rule that matters: a pinned head ("the pull request's live head must read exactly `--head`") and
  a `--budget` abort (lines 4-31 at `a7dd7f50d`). It only falls short in two ways: it waits on one
  head, and it then merges. `INSTRUMENTS.md` says a listed instrument that falls short is fixed,
  not bypassed.
- **Form.** `proof_watch.py --wait-only --head SHA [--head SHA ...] --check NAME --budget H`.
  - It exits 0 when the named check-run has completed at every pinned head, and prints each state.
  - It exits 1 on `HEAD MOVED` or when the budget runs out.
  - It never merges and never approves.
- **`--run CMD` is REJECTED.** A shell already runs `proof_watch.py --wait-only ... && cmd`. An
  exec arm inside the tool would let a pinned wait launch anything, which is a negative consequence
  on the machinery under the owner's own exclusion.
- **`contains --pr N --handoff TOPIC` is REJECTED here.** The census routes that exact predicate
  (the body names the code head, and the PR contains it) to the relay as carry census-5 on
  R10-FLY-RELAY-DELIVERED-GUARD. The relay is the consumer that needs it. A second copy in a waiter
  would be the redundancy the rule excludes.
- **Not in scope:** P331 already moved the merge train's approval-race wait into the train.

## P340: the cloud payload scripts compose by hand what cloud_dispatch.py does not

Verdict: REJECT, as redundant. The premise is false at `a7dd7f50d`. No roster op.
- **`cloud_dispatch.py` already has the proposed form.** Its options include
  `--group` ("a roster group: publish its seat to a dispatch ref"), `--roster-ref` and `--publish`
  (lines 1121-1138).
  - `group_brief` (line 409) renders the brief, the After groups and "each carry as
    `Carry <i>:`, verbatim". That landed at `aabbdff17` (2026-10-30, "a group's dispatch renders
    its After: groups and every carry").
  - Any home-directory path in the rendered text is refused through `ref_privacy.HOME_DIR`
    (lines 54-61 and 89).
  - `--publish` landed at `fc6a810eb` (2026-10-28).
  - The 27 scripts the census lists sit under w32 to w62, `pubfix*`, `pubrev*` and `repair/`.
    Their names place them in sessions s6 to s8, which ran before these commits.
- **The POOL.txt question.** The census asks whether `dispatch/pool-s6`'s `POOL.txt` convention is
  still live. It is not. `git grep -l POOL.txt origin/main -- tools` finds no tracked writer or
  reader, and cloud seats are dispatched through `cloud_dispatch.py`. The `dispatch/pool-s6` ref
  still exists (`a5c52dd4c`); deleting it is a closeout operation for the orchestrator.
- **What would change this answer:** a named shortfall of `cloud_dispatch.py --group --publish`
  measured at main, for example a stale claim it fails to delete. That would be fixed in
  `cloud_dispatch.py` itself.

## P341: six roster show and diff scripts rebuild one read-only view

Verdict: ACCEPT, as one carry on R10-ORCH-ROSTER-SCHEMA (`carries-open`, it owns
`tools/audit/seat/roster_lib.py`).
- **Not redundant.** `roster_edit.py` and `roster_lib.py` have no read-only `show` or `diff`
  command at `a7dd7f50d`. The census counts 17 rebuilt files across the reviews of #2866, #2878 and
  batches 21, 22 and 24.
- **Form.** `tools/audit/seat/roster_show.py`, reading through `roster_lib`:
  - `show GROUP --ref R` prints the group's stage, resume, after, files, carries indexed as
    `cloud_dispatch.group_brief` indexes them, and issues.
  - `diff REFA REFB` prints groups added and removed, stage and resume changes, carries added per
    group, and issue wiring.
- **Fixtures.** A diff of a ref with itself prints nothing. One added carry prints exactly that
  carry.
- **Its use now.** The merge seat's interim carries read (P335) is `roster_show.py show G` at the
  roster branch.

## P342: three sessions rebuilt a plan what-if tool

Verdict: ACCEPT, as one carry on R10-FLOW-TOOLKIT-MODEL (`not-started`, M). Its brief is to land
the projection model "on main as part of the one plan model, not beside it", and its `files` name
`tools/plan/replan.py` and `roster_lib.py`.
- **Not redundant.** `tools/plan/` holds `replan.py` and `durations.json` only. `replan.py` draws one
  plan from one roster. The census counts 24 rebuilt files: `scen.py`, `variants.py`,
  `mkfold.py`/`apply.py`, and `sim.py` with `t0`..`t9`.
- **The defect this closes.** The census found a 19 h figure (`s8/plan-opt/plan-cp.json`) drawn
  from a different roster than its base: `groups_done` 184 against 176. The tool takes ONE
  `--roster` ref and applies every variant's levers to copies of it.
- **Form.** `tools/plan/whatif.py --roster REF --start ISO --lever drop:G | split:G:SIZE |
  edge:G:-A | fold:GUEST:HOST ...`. It prints closure, batches and regain per variant beside the
  base, calling `replan.py`'s model and never re-implementing it (`tests/README.md`: a test that
  re-implements a production formula pins nothing; the same holds for a tool).
- **Fixture.** The empty lever list reproduces the base closure exactly.

## P343: policy_reread_check.py names no changed file

Verdict: REJECT. The binding cost: the saving is nil on the path that dominates.
- **The owner's rule is a full re-read after every compaction.** The proposal says so itself:
  "this narrows only the drift check, not the post-compaction read". A `--changed` list cannot
  shorten the read that the rule fixes at the whole corpus.
- **Between compactions there is already a mechanism.** The corpus reaches the session through the
  SessionStart injection, and `policy_reread_check.py` answers OWED or OK.
- **What `--changed` would buy:** naming which files moved. That is one `git diff --stat` over the
  policy paths, with no measured instance of it being missed. The benefit is unmeasured and
  marginal against about 40 lines and a self-test.
- **Not ruled here.** `policy/inject.sh`, which writes `corpus.txt`, is itself session-local. If
  the SessionStart hook depends on it, landing that script is a separate census question the
  proposal did not ask.

## P344: no instrument holds a reviewer dispatch while an autofix bot is about to move the head

Verdict: ACCEPT, as one carry on R10-ORCH-REVIEW-PACKET (`carries-open`; its files name
`tools/audit/seat/bus.sh`, and it owns review dispatch and packet semantics).
- **Measured.** Take the 305 distinct (PR, head) bus dispatches since 2026-10-24
  (`~/.zcode/bus/dispatched`). Against `git rev-list --children` over origin/main and the open
  `fix/*` branches, 12 of those heads have a `github-actions` child: 11 `ci: pin killed mutants`
  and 1 `ci: re-record closures`. They cover 11 PRs: #2872, #2873, #2887, #2912, #2917, #2919,
  #2946, #2968, #3005, #3009 and #3022.
  - In each, the reviewer was handed a head the bot then moved. Each one costs a carry check or a
    delta review.
  - The 10 `ci: merge main` children are not this class and are excluded.
- **Not redundant.** `ci-autofix.md` tells a seat to wait for the bot commit. `standing-dispatch.md`
  has no autofix text (census Part B row 6), and `bus.sh dispatch` records a dispatch at any head.
  Census carry 4 puts the rule in the contract. This puts it in the instrument (mechanise before
  policy).
- **Form.** In `bus.sh dispatch`, read the head's check-runs once through `gh_read.py`. Then:
  - refuse with rc 3, naming the job, while a check-run named `mutation-autofix`,
    `closures-autofix` or `claims-autofix` is `queued` or `in_progress`;
  - treat a completed red autofix job as "no commit coming", and dispatch;
  - `--force` overrides, writing one ledger line.
- **Fixtures.**
  - All autofix jobs completed: the head dispatches.
  - One `in_progress`: refused, rc 3.
  - A red completed autofix: dispatches.
  - Null: a head with no autofix job dispatches.
  - One mutant: drop the `in_progress` test, and the refusal row dispatches.

Cost for the batch:
- **R10-FLY-SEAT-WAITERS:** S. About 80 lines of shell, about 40 lines in `proof_watch.py`,
  self-tests over a fixture remote and a stub `gh`, and two instrument pages. The new file must be
  classified (`tests/entities.py`).
- **P341:** about 100 lines and a self-test.
- **P342:** about 150 lines and a self-test.
- **P344:** about 25 lines, plus one check-runs read per dispatch.
- None of these files has a `policy_lint.mjs --budgets` row; the `--budgets` output at
  `a7dd7f50d` names none of them. No policy file changes.

Binding: the owner's rule places each non-redundant reusable on main. The rulings above route the
four that qualify, P338, P339, P341 and P342, as narrowly as their consumers need, plus P344, which
rests on its own measured count. They reject P340 as redundant and P343 as zero-saving. Their
order is the orchestrator's, below the critical path.
