# R10-STANDING-CONTRACTS-P2 design note: P2 of design/r10-fly-standing-contracts (round 2)

- **Base:** 45adb0c3b425dc44e72fd9ce4ef51f480b5a3af6; every line cited below is at it unless the line says "at main". origin/main is d08ed31049 when this note is written, and §8 lists what moved between the two.
- **Predecessor:** R10-FIXER-MD-SPELLING-CORPUS. Its handoff head is handoff/r10-fixer-md-spelling-corpus 925ade0cf. It touches fixer.md only and has no pull request.
- **Approved design:** design/r10-fly-standing-contracts 21210036507f (round 2), approved at design-verdict/r10-fly-standing-contracts 2d0ac2c0b. P1 is #3197 (b707d8932) and P3 is #3294 (8a4cf2618).
- **Roster:** origin/handoff/audit-r10-roster 25ef6cb31. The group is size L, with carries 0-20.
- **Revises** design/R10-STANDING-CONTRACTS-P2 5bcd069c5 against design-verdict/R10-STANDING-CONTRACTS-P2 1764024c1 (`revise`, `class-open`). Answers: point 1 in §4 and §5 (second enumerator, pulse.py re-base); point 2 in §2 and §5 row (b) (five anchors, the predicate pinned); point 3 in §1, §2, §5 and §6 (carry 20 is built here). The routed decisions are answered in §6.
- **No new design.** This note binds the approved note's §6 "P2 (policy)" to the base, and folds in P371 (carry 0) and carry 20.

## 1. Owning seam

**Owner:** one new contract, dev/governance/roles/standing.md (absent at the base), as the approved note §1 rules.
- It holds the Wait, Reads, Autofix hold, Recycle and Alive files terms once.
- Every standing contract's opener cites it, and so does proposal-triage.md's.

**Retired:** standing-tick.md and standing-roster.md become retirement stubs. Each names the beat row that replaced it and keeps its file, so CLAUDE.md and the playbook fixtures still resolve.

**Callers, edited:** orchestrator.md §5, CLAUDE.md's role table, INSTRUMENTS.md, the pulse.py STANDING map with its docstring and self-test, sweep_template.md, and decision 0015 item 5 (an amendment clause).

**P371 seam:** owner fixer.md, the seat that returns BLOCKED today. designer.md and design-review.md each gain one line citing it. tools/pr/ci_predict.py is not edited: part (c) is on main at e566f7e02, and its BOOTSTRAP text (ci_predict.py:656-657) cites a fixer.md section that does not exist yet.

**Carry 20 seam:** owner tools/audit/seat/cloud_dispatch.py, the one writer of a designer's payload (`_prompt`, :200; the designer branch, :282). designer.md step 1 gains the read. No second owner: tests/seam_map.json names neither instrument, and bus.sh is not edited.

## 2. Shape

**standing.md.** Five headings, in these words, which §5 row (b) checks: **Wait**, **Reads**, **Autofix hold**, **Recycle**, **Alive files**.
- **Wait** (carry 1, approved item 1). A seat ends a turn only when nothing is owed. Otherwise it waits in a `run_in_background` shell loop that:
  - touches its alive file every 25 s, and its `FILE.d/<id>` entry, only while the seat's pid answers `kill -0`;
  - exits on a queue change or at the end of the window.
  A detached `nohup` wakes nothing. No tracked loop script is allowed (P51). The loop writes no pid into the alive file (approved item 27).
- **Reads** (carry 2). A table of each read and its cwd-safe instrument:
  - PR body: `policy_lint.mjs --pr-body` and `carry_audit.py check --body`;
  - PR state: `gh pr view --repo tvofi/heatpump_optimizer`, which prints UNREADABLE on a non-zero exit or an empty answer (see fixer note item 17);
  - handoff refs: `bus.sh orphans`, or `git -C <worktree>`.
  A hand-written pipeline (`| wc -l`, `grep -c`, a bare `git` or `gh`) is never a check result. Each Bash call starts in the seat's original directory.
- **Autofix hold** (carry 3), its own heading and no longer a row of Reads. Dispatch a reviewer at a pull request's head H, or start a merge at H, only when:
  - no `mutation-autofix`, `closures-autofix` or `claims-autofix` job at H is queued or in_progress; and
  - either a bot commit has moved the head (then act at the new head), or every autofix job concluded with no push. A red autofix job pushes nothing (ci-autofix.md).
  Read it with `failure_logs.sh` or `gh api repos/<r>/commits/<H>/check-runs`. A dispatch at the handoff, before a pull request exists, has no check-runs and is outside the hold (§8).
- **Recycle** (carry 4):
  - Trigger: the seat's context passes about 150k tokens or the seat has run 4 h.
  - Timing: only at a quiet point, with no op of its own mid-step and no train, push or open that it owns in flight.
  - Handoff: it writes `<seat dir>/STATE-HANDOFF.md` (pending waits with targets, in-flight ops, queue positions, held lines and their release conditions, next actions), stops only its own loops by PID, and replies HANDED.
  - The field figures stay in the triage record, not in the contract.
- **Alive files** (carry 19): `$HPO_STATE_DIR/alive/`, the directory the liveness hook reads (tools/audit/seat/hooks/liveness.py:91). Staleness is set by `HPO_ALIVE_STALE_MIN` (:90).

**Stubs.** Each is about 4 lines:
- standing-tick.md is "retired into the `tick-digest` and `owed-check` rows of `beatd.jobs.json` (tools/audit/seat/beatd.jobs.json:6, :26); read the digest".
- standing-roster.md is "retired into `roster-drain` (:46): queue ops for it; a refusal is never retried past the lint gate".
- Both quote the owner's constraint "make sure the retirement of the standing seats dont cause you to run things inline" once each.

**standing-merge.md** (carry 5):
- Line 12's "`merge_pr.sh` merges a budget-file or policy head directly." becomes "a budget-file or policy head takes the train's serial route; `--pre-flight` parks it and it merges under the mandate" (tvofi 2026-10-26, "no merge outside the train").
- Line 3's "One of the four standing seats" becomes "One of the two standing seats (`standing.md`)". Carry 6 has landed at lines 8-11.

**standing-dispatch.md:** line 3 changes as standing-merge.md's does, and the `git ls-remote` block goes. standing.md's Reads row names `bus.sh orphans`, so the cut loses no read (§8).

**orchestrator.md** (carries 4, 7 and 8; approved items 10, 11 and 28):
- §5's sentence at :106-109 becomes one bullet:
  - two standing seats, standing-merge.md and standing-dispatch.md, under standing.md;
  - tick and roster are beat rows;
  - you read state only from the plan page and the ledger's digest under `$HPO_STATE_DIR/digest/`, and no longer re-read the digest's sources, the seats' scratch or the bus;
  - during a recycle, you route new work only to the incoming seat, and only after the outgoing one replied HANDED;
  - the sweep restarts a seat that is absent or stopped with work owed.
- The Routing clause lives here and not in standing.md, because it binds the orchestrator, who does not read standing.md (verdict note item 18). Carry 7's words "the ledger and the plan page" are both in the bullet.
- §10b at :224 ("Through the roster seat, on `standing-roster.md`'s terms") becomes "Through the `roster-drain` queue; `roster_edit.py`'s lint gate binds".

**Decision 0015**, item 5 at dev/governance/decisions/0015-the-architects-plan-seam-grouping-and-standing-seats.md:48: the ruling's text stays, and one dated clause is appended: tick and roster retired into beat rows (tvofi 2026-10-24 card 1), two seats remain. A decision is a record, so it is amended and never rewritten.

**P371, three lines of policy (carry 0 parts a and b):**
- fixer.md gets a short paragraph near the handoff steps. When `ci_predict.py` prints BOOTSTRAP (the base's copy of a grader this diff changes refuses, and the head copy passes in prepr), do not return BLOCKED. Choose one of:
  - move the registration into unpinned data the grader already reads (dev/governance/config/corpus_excluded.json, #2916);
  - split: the grader hunks alone as the p1 handoff, and the rest as a work-in-progress handoff that resumes as p2 once p1 is on main.
  Cite decision 0013 Consequences (dev/governance/decisions/0013-verdicts-post-as-the-approver-app.md:102-105) and do not restate it.
- designer.md step 7 gains: "a change set that adds what a pinned grader in a restoring job must register names its p1/p2 split (`fixer.md`)".
- design-review.md step 2 gains: "a design that relies on a grader's new behaviour inside the pull request that changes that grader is `revise` (`architecture-unsound`)".

**Carry 20, the revise route:**
- cloud_dispatch.py, in `dispatch_group` (:487), for the designer role only: read the tip of `design-verdict/<group>` the way `design_approved` (:473) already does (ls-remote on origin, then the fetched verdict.md's first line). When the ref exists, pass its 40-hex tip and that first line to `render` (:319) and `_prompt` through one new keyword, empty by default.
- `_prompt`'s designer branch (:282) then appends one sentence: the design reviewer's verdict is at design-verdict/<topic>, commit <sha>, first line quoted; read it first, answer every point in a new design.md pushed on top of design/<topic>, and do not restart. With the keyword empty the designer text is byte-identical to today's.
- Data flow before: verdict ref -> nobody; the orchestrator hand-queues a roster carry. After: verdict ref -> `dispatch_group` -> PROMPT.md -> designer. The pin is the commit, not the ref name, so a verdict that moves after the dispatch cannot change what the designer was told to answer.
- Invariants: the reviewer payload and the fixer's approve gate do not change; no new ref is written; an unreadable origin refuses the dispatch as `_git` already does, and never renders a payload that silently omits the verdict.
- Not built: the round count and the "third revise is a re-cut" rule stay the orchestrator's (design-review.md).
- designer.md step 1 gains: "on a revise, first the verdict your payload pins at `design-verdict/<group>`".
- tools/audit/seat/instruments/cloud_dispatch.py.md, the design-roles paragraph at :77-88 at main, gains the sentence.

**Invariants of the whole change:**
- No behaviour moves into the orchestrator's turns.
- Merge, dispatch and triage stay LLM seats.
- No beat row changes; P1's rows are only cited.
- ci_predict.py's verdicts and rc do not change.

**Dog-food check.** This change set is registered only in data (policy_budgets.json, tests/closures.json), so no pinned grader should need a p1. The fixer confirms by running `ci_predict.py` before the handoff. If it prints BOOTSTRAP, the new fixer.md paragraph applies to this group too.

## 3. Alternatives

- **Copy each term into all four contracts (carries 1-4 as written).** Lost: each cap in §6 is within 4 tokens of its measure, so four copies need four raises against one new cap, and finding-propagation.md says to write a rule "once". `decision: owner`.
- **Put P371(a) in decision 0013 rather than fixer.md.** Lost: the BOOTSTRAP line already cites fixer.md, and a seat reads its contract, not decisions.
- **Retire tick and roster by deleting their files.** Lost: the playbook fixtures (tools/policy/fixtures/playbook-null.md:9) and the CLAUDE.md rows resolve the paths. The stubs are cheaper than those edits.
- **Carry 20 as a designer.md step alone.** Lost: the round-2 designer would still have to find the ref and choose a tip itself, and a verdict pushed after the dispatch would change its target. One call in `dispatch_group` pins it once.
- **Carry 20 in bus.sh (push-design refusing a note that does not name the verdict).** Lost: it adds a second owner of the verdict read, and it refuses after the work is done instead of routing before it.
- **Carry 20 routed to another group.** Lost: no live group owns the designer payload, and this group already pays designer.md's cap for P371(b); two groups tightening one file at 878/878 tokens would collide.

## 4. Sibling sites (enumerated at the base)

**Enumerator 1:** `git grep -n -E "standing-(tick|merge|dispatch|roster)\.md" 45adb0c3b -- ':!dev/archive' ':!dev/programme' ':!dev/audit/rounds'`.
- CLAUDE.md:122-125: edited. Two rows merge into one retired row, and a standing.md row is added.
- orchestrator.md:107-108 and :224: edited. :88, :113 and :148 name merge and dispatch, and stay.
- tests/closures.json:1606-1609 and tools/ci/selftest_closures.json:5948-5951: re-derived, not hand-edited.
- tools/audit/seat/ledger.py:649 (a docstring): it cites "the ancestor-recarry test of standing-tick.md", which is standing-tick.md:15. The stub drops that text, so the docstring cites ledger.py's own `recarry` (P90) instead.
- dev/audit/README.md:40, :61-62 and the policy fixtures: already true, or recorded snapshots. Out of scope.
- `git grep -n merge_pr.sh 45adb0c3b -- dev/governance/roles` finds standing-merge.md:12 (edited) and nudge.md:89 (a postmerge caller, out of scope).

**Enumerator 2** (the class by its words, verdict point 1): `git grep -n -i -E "four standing|standing (tick|roster) seat|tick_(alive|brief|stale_min)|seat-(tick|roster)" 45adb0c3b -- ':!dev/archive' ':!dev/programme' ':!dev/audit/rounds'`. Every hit:
- orchestrator.md:106: edited (§2).
- standing-merge.md:3 and standing-dispatch.md:3: edited to "two" (§2). standing-tick.md:3 and standing-roster.md:3: replaced by the stubs.
- Decision 0015:48: amended (§2).
- INSTRUMENTS.md:43 (the paragraph :43-47): edited to two seats plus the two beat rows. :106 and tools/audit/seat/instruments/roster_queue.py.md:3: "the standing roster seat's queue runner" becomes "the `roster-drain` beat row's queue runner".
- pulse.py:44 (the docstring paragraph from :44): edited to two seats, with tick and roster named as beat rows that `beatd status` judges. :114 STANDING loses tick and roster; the comment at :110-113 follows.
- pulse.py:590-618, the self-test: re-based, case by case, in §5.
- sweep_template.md:41, :43 and :45: `tick_alive`, `tick_brief` and `tick_stale_min` all leave the placeholder table; step (5) at :83 is the only consumer of the third. :67 (1b) names two seats; :83 (5), the tick restart, goes (approved item 21).
- dev/audit/rca/R10-RCA-ORCH-CONTINUITY.md:54: a dated root-cause record of the state it analysed. Out of scope.
- tools/policy/policy_lint.mjs:2806: "Four standing rules", a different noun. Out of scope.

## 5. Evidence, by file

There is no finder harness: the evidence is the owner's rulings, the triage records P51, P95 and P371, the s9 census and the s13 carry. Every figure is re-measured at the merge base.

**tests/entities.py, one check, rows a-c:**
- (a) standing-merge.md, standing-dispatch.md, both stubs and proposal-triage.md cite standing.md.
- (b) standing.md carries the five heading words of §2, the string `$HPO_STATE_DIR/alive/`, and the autofix-hold predicate itself: all three job names, `mutation-autofix`, `closures-autofix` and `claims-autofix`.
- (c) The file that ci_predict.py's BOOTSTRAP constant cites (fixer.md) contains `BOOTSTRAP` and `0013`.
- Failing first: (c) fails on the base, because fixer.md lacks both (`git grep -n -E "BOOTSTRAP|0013" -- dev/governance/roles/fixer.md` is empty). That is P371's dangling citation, and it is the "detector shown to detect" run.
- Null: the edited tree passes.
- Mutants, each red alone: delete any one heading; delete the autofix-hold predicate sentence while keeping its heading (the three names go, row (b) fails; this is carry 3's control); delete one job name; delete the fixer.md paragraph.

**pulse.py --self-test**, re-based on the two seats that remain (dispatch at 60 min, merge at 120 min):
- Contract check (:584-585): the `standing-*.md` glob equals STANDING plus a retired pair (tick, roster), and the two sets are disjoint.
- Idle null (:587-591): both idle seats are dispatch and merge; the asserted description is "seat dispatch: idle, nothing queued"; the arm count stays `len(ARMS) + 2`.
- STOPPED control (:592-597): dispatch holds a 61 min and a 5 min entry and reads STOPPED, "seat dispatch: 1 queued input(s) past its 60 min cadence, oldest 61 min".
- Under-cadence control (:598): merge holds one entry of 119 min, one minute under its cadence as tick's 69 was under 70, and reads ok.
- Override (:599-600): dispatch at 61 min with a 90 min override reads ok. Clock-ahead (:603-604): moves to merge. The UNREADABLE case (:601-602) is already on merge.
- read_queue (:605-613) and the subprocess control (:614-619): the seat names become dispatch and merge; the asserted line is "PULSE seat-dispatch STOPPED seat dispatch:" with "pulse: 5 arms, 1 stopped" unchanged.
- New retirement control beside the janitor case (:620-622): `--seat-queue` naming roster or tick exits 2. Mutant: restoring either seat to STANDING fails this case and the contract check.

**cloud_dispatch.py --self-test**, in `_group_checks` (:588):
- Null, at the existing designer case (:669), where R10-BIG has no verdict ref: the rendered designer text contains no `design-verdict/`.
- Failing first, after the `revise` verdict is published at :684: a designer dispatch for R10-BIG renders that verdict commit's 40-hex SHA and its first line. On the base this fails, because the designer branch never reads the ref.
- Mutants: appending the sentence unconditionally fails the null; dropping the read fails the failing-first case; pinning the design tip in place of the verdict commit fails it too, since the case compares against the verdict ref's own tip.

**sweep_render.py fixture:** the rendered sweep names none of the three tick placeholders. A mutant that restores step (5) fails.

**Control for carry 5:** `git grep -n merge_pr.sh -- dev/governance/roles/standing-*.md` prints nothing at the head.

**policy_lint --budgets:** every row is at or below its cap (approved item 28's control).

**Goldens and claim files:** none move.

## 6. Gate, budget, hot files, serial position

**Gate** (`decision: orchestrator`, routed by the verdict). The orchestrator records two things in the PR body before merge, and the fixer cannot produce them from a cloud seat. The stubs do not merge without them:
- `beatd status` showing every P1 row `ok` from main for one cycle beside the live seats;
- for the roster retirement, the roster-drain job landing a seeded no-op-safe op on a scratch roster branch and refusing a seeded lint failure, with the seat beside it for one cycle.

**Budget** (`node tools/policy/policy_lint.mjs --budgets` at main d08ed31049; re-measure at the merge base):

| file | lines / cap | tokens / cap |
|---|---|---|
| fixer.md (key tools/audit/briefs/fixer.md) | 315/315 | 5180/5216 |
| designer.md | 60/60 | 878/878 |
| design-review.md | 53/53 | 778/778 |
| orchestrator.md (key tools/audit/briefs/orchestrator.md) | 292/295 | 4234/4251 |
| proposal-triage.md | 36/36 | 489/489 |
| standing-merge.md | 36/37 | 504/507 |
| standing-dispatch.md | 36/39 | 508/509 |
| standing-tick.md | 25/26 | 326/330 |
| standing-roster.md | 27/27 | 368/368 |
| CLAUDE.md (always loaded) | 213/221 | 3605/3605 |

- No cap in this table rises. The P371 lines, carry 20's designer.md clause, proposal-triage.md's citation and the CLAUDE.md rows are each paid inside their file by tightening.
- designer.md takes two additions at zero headroom in both measures. Each goes into an existing sentence (steps 1 and 7), and the "A note, not a stop" bullets are the tightening candidates. Measure before writing anything else.
- standing.md's tokens are paid by the two stubs and dispatch's ls-remote block, so the corpus line ends at or below its cap.
- standing.md's new per-file cap and the lowered tick and roster caps go in policy_budgets.json. The new cap is a `capfile` raise under `budget-raise-gate`. CLAUDE.md rule 2 binds it: the owner's explicit confirmation is obtained before the branch is pushed, or a mandate scoped `budget-raise` or `all` is in force with `## Raise justification`. With neither, the fixer stops and asks, and does not push. `decision: owner`.

**Serial position:** after R10-FIXER-MD-SPELLING-CORPUS, because both edit fixer.md and its cap is shared. The fixer starts from the predecessor's merged fixer.md.

**Hot files:**
- orchestrator.md is in the roster's hot_files.
- standing-dispatch.md and cloud_dispatch.py were both edited on main by R10-DISPATCH-AT-HANDOFF after the base (§8). R10-TICK-LEVELS still shares standing-dispatch.md; re-check its state at dispatch.

**Roster `files`** lacks standing.md, proposal-triage.md, CLAUDE.md, policy_budgets.json, INSTRUMENTS.md, roster_queue.py.md, decision 0015, ledger.py, cloud_dispatch.py and its instrument page, tests/entities.py and the two closure files. Adding them is `decision: orchestrator`, as a roster op through roster-drain.

**Policy:** every edited contract, decision 0015, CLAUDE.md and policy_budgets.json. The owner's approving review at merge, or mandate 6329234399.

## 7. Carries

- Carry: R10-STANDING-CONTRACTS-P2 (item 1): P371(a) and (b) go in fixer.md, designer.md and design-review.md as §2 states.
- Carry: dismissed: already on main (item 2): P371(c) landed at e566f7e02, and its controls are in that PR.
- Carry: R10-STANDING-CONTRACTS-P2 (item 3): Wait, Reads, the autofix hold and Recycle go in standing.md, written once. Carries 1-4 ask for a copy in each contract; that is `decision: owner`.
- Carry: R10-STANDING-CONTRACTS-P2 (item 4): merge_pr.sh gives way to the train route (carry 5).
- Carry: dismissed: already landed at base (item 5): carry 6's train-join wording is at standing-merge.md:8-11.
- Carry: R10-STANDING-CONTRACTS-P2 (item 6): §5's bullet on reading only the plan page and the ledger's digest, which covers carries 7 and 8.
- Carry: R10-ORCH-LEDGER (item 7): the merge-seat retirement (carry 9) and the dispatch beat job (carries 12-14) are unbuilt, as the approved items 12 and 15-17 state. Merge and dispatch stay seats here.
- Carry: R10-STANDING-CONTRACTS-P2 (item 8): roster retirement (carries 10 and 11) and tick retirement (carry 17), behind §6's gate.
- Carry: dismissed: built by P1 #3197 (item 9): carries 15, 16 part (1) and 18 are the job table and sweep rewrites; P2 only cites them.
- Carry: dismissed: built by P3 #3294 (item 10): carry 16 part (2), the hooks.
- Carry: R10-STANDING-CONTRACTS-P2 (item 11): standing.md names `$HPO_STATE_DIR/alive/` (carry 19).
- Carry: R10-STANDING-CONTRACTS-P2 (item 19): carry 20, the designer payload's verdict pin and designer.md's read step, as §2 and §5 state.

## 8. Moved between the base and main

Read at d08ed31049; R10-DISPATCH-AT-HANDOFF merged in between.
- standing-dispatch.md was rewritten inside its caps. The sentence "`bus.sh orphans` answers every ref at once" is gone at main, so the 5bcd069c5 note's reason for cutting the ls-remote block ("line 34 already names it") no longer holds there. standing.md's Reads row is now the only place the dispatch seat is told to use `bus.sh orphans`, and row (b) of §5 gains that string.
- The same file now dispatches a reviewer at the handoff, before a pull request exists, and `review_carry.py` carries that verdict to the pull request's head. No check-run exists at a handoff tip, so the autofix hold is worded for a pull request's head and for the merge start only (§2).
- cloud_dispatch.py moved by about 40 lines: at main `_prompt` is :220, the designer branch :317, `design_tip` :506, `design_approved` :512, `dispatch_group` :526 and `_group_checks` :632. The shape in §2 is unchanged by the move; the fixer re-anchors.

## Notes for the fixer

- Carry: R10-STANDING-CONTRACTS-P2 (item 12): ledger.py:649 cites the ancestor-recarry test of standing-tick.md:15, which the stub drops. Check whether the tick-digest row (beat_jobs.py) or ledger.py itself now owns that test. Cite whichever does, and do not move the prose into standing.md.
- Carry: R10-STANDING-CONTRACTS-P2 (item 13): read fixer.md at the predecessor's merge before choosing what to tighten. Its step-6 tightening (925ade0cf) may already have spent the obvious lines.
- Carry: R10-STANDING-CONTRACTS-P2 (item 14): standing.md is new and tracked. Confirm `tests/entities.py` classifies it, under the dev/governance/ INERT prefix (tests/closure.py) or a measured closure, before pushing.
- Carry: R10-STANDING-CONTRACTS-P2 (item 15): proposal-triage.md is at both caps; its standing.md citation is paid by tightening inside the file.
- Carry: R10-STANDING-CONTRACTS-P2 (item 16): CLAUDE.md has zero always-loaded headroom; measure the role-table edit with `--budgets` before anything else is written.
- Carry: R10-STANDING-CONTRACTS-P2 (item 17): tools/audit/seat/gh_read.py is the read rule for seat instruments' GitHub reads (tools/audit/seat/instruments/gh_read.py.md) and classes `gh pr view` as a read. If it offers a command-line read a seat can run, the Reads table's PR-state row names it; if it is a library for instruments only, the row keeps `gh pr view --repo` and says so. This note did not read its `main`.
- Carry: R10-STANDING-CONTRACTS-P2 (item 18): the Recycle routing clause is in orchestrator.md §5's bullet (§2), in words the orchestrator acts on; do not move it to standing.md to save tokens.
- Carry: R10-STANDING-CONTRACTS-P2 (item 20): sweep_render.py may hold its own list of required placeholders. Drop the three tick names there in the same commit as the template, or the render refuses a missing key. This note did not read it.
- Carry: R10-STANDING-CONTRACTS-P2 (item 21): `design_approved` reads `FETCH_HEAD` after its fetch, which bus.sh's header warns is per-worktree state. The new read takes the SHA that ls-remote answered and shows verdict.md at that SHA, never at `FETCH_HEAD`.
