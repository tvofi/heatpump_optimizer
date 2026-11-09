CLOUD DESIGNER seat for tvofi/heatpump_optimizer, topic R10-STANDING-CONTRACTS-P2, at head b8f67a775137a8032d5c71b34ea64165c1d4613a. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render designer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/designer.md from main, and follow it exactly. The base is b8f67a775137a8032d5c71b34ea64165c1d4613a (`git fetch origin b8f67a775137a8032d5c71b34ea64165c1d4613a`); name it in the note. Write no production code.
Output: write the note as design.md in a directory of your own and run `bash tools/audit/seat/bus.sh push-design R10-STANDING-CONTRACTS-P2 <design.md>`, which pushes refs/heads/design/R10-STANDING-CONTRACTS-P2; that push is the return signal, and the design/R10-STANDING-CONTRACTS-P2 tip is the SHA you hand off. You may push only to that ref. Open no pull request, push no handoff ref and write no delivery row.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
Design P2 of design/r10-fly-standing-contracts (approved; P1 #3197 and P3 #3294 merged): the standing-*.md contract edits (Wait, Reads, autofix hold, Recycle, merge_pr.sh), the seat retirements whose beat rows already run (tick-digest, roster-drain), the orchestrator reading only the ledger and the plan page, standing.md naming the alive-file directory; plus P371's two-PR grader-first rule in fixer.md/designer.md/design-review.md. Policy: owner approval at merge; pay inside each file's cap. No new design: the approved one covers it. Created by the carries-open audit (orchestrator s13, 2026-11-09) from the carries listed in its carry entries; each carry entry names its source group and index.

After: R10-FIXER-MD-SPELLING-CORPUS

Carry 0: Moved from R10-FLY-CIPREDICT-RESTORING carry 2 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

From triage P371 (root-cause record for the base-copy grader bootstrap, orchestrator s10 2026-11-02T08:16:24Z; 4 instances in round 10: R10-DEPS-ACTIONS-BUMP, R10-MACHINERY-RATCHETS, R10-BASH-KILL-HOOK, R10-AGREEMENT-BOOTSTRAP #3166; 20 h 43 m measured delay, 62% of it BLOCKED returns awaiting the same split ruling). A pull request that teaches a pinned grader is graded by the base's copy, so no edit inside it reaches the program CI runs; decision 0013 Consequences already names the remedy (two pull requests, the grader first) but no role contract or instrument text carries it. Three parts, landing together or (a) first, since (c) cites (a):
(a) dev/governance/roles/fixer.md: a short section. When the graders arm of tools/pr/ci_predict.py refuses with the base's copy of a grader that the diff itself changes, and the head copy passes in prepr, the fixer does not return BLOCKED; it either moves the registration into an unpinned data file the grader already reads, where one exists (the dev/governance/config/corpus_excluded.json pattern, #2916), or splits: the grader hunks alone as the p1 handoff, the rest kept as a work-in-progress handoff that resumes as p2 once p1 is on main. Cite decision 0013 Consequences rather than restating it.
(b) dev/governance/roles/designer.md and dev/governance/roles/design-review.md, one line each: a design whose change set adds a file, hook, grammar or revision that a pinned grader in a restoring job must register names its p1/p2 split; a design that relies on a grader's new behaviour inside the pull request that changes that grader is revise.
(c) tools/pr/ci_predict.py, the graders arm's text only: when the refusing program appears in the line's own over-list of changed paths, append a BOOTSTRAP remedy (no change in this pull request reaches the base's copy; move the registration to unpinned data or split p1 grader / p2 artifact, per fixer.md and 0013 Consequences), and do not print "repair before the handoff" for those lines. No verdict or rc changes.
Budgets: fixer.md, designer.md and design-review.md sit at their policy_lint --budgets caps (314/315 lines and 5216/5216 words; 60/60 and 878/878; 53/53 and 778/778 at dfb4ce2b5) and the fixer role has 67 tokens of headroom: pay by moving or tightening text under ratchet-budgets.md; a raise is not granted by this carry. (a) and (b) are policy and merge on the owner's approving review or under a mandate in force.
Controls for (c), re-measured on the built arm: fires on the BASH-KILL-HOOK r1 head efada17e9 (policy_lint.mjs and field_coverage.mjs refused, both in the over-list) and on the DEPS and MACHINERY r1 diffs (codeowners_gap.py; policy_lint.mjs and field_coverage.mjs), 3 of 3; silent on a refusal by an unchanged grader (the R10-RCA-PREPR-HEAD-GRADERS plant, over tools/policy/budget_raise_gate.py refused by policy_lint.mjs); silent on a clean tree; one mutant that drops the membership test prints the remedy on the unchanged-grader plant and fails. Not in scope: moving grader registries to unpinned data under a pinned superset check (P371 part d), deferred to the owner.
triage: dev/programme/triage/s6-batch113.md#P371

Carry 1: Moved from R10-FLY-STANDING-CONTRACTS carry 0 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

Re-routed by orchestrator s9 under mandate 6329234399 (tvofi's request, 2026-10-31, slipped-proposal audit): R10-ORCH-BEATD is done (#2916) with arm (a) only, and `git grep -n -i -E "run_in_background|nothing is owed" origin/main -- dev/governance/roles/standing-tick.md dev/governance/roles/standing-merge.md` finds no Wait paragraph. (triage: dev/programme/triage/s6-batch2.md#P51) In each of dev/governance/roles/standing-tick.md, standing-merge.md, standing-dispatch.md and standing-roster.md, add a Wait paragraph of about 6 lines: a seat ends a turn only when nothing is owed; it waits with a `run_in_background` shell loop that touches its alive file every 25 s and exits on a queue change or the window's end, so its exit wakes the turn; a detached `nohup` wakes nothing. A tracked seat_loop.sh is REJECTED by P51. Basis: 4 standing seats ended their first turn on an untracked watcher in the opening 11 minutes of one session, and each needed an orchestrator SendMessage. Controls: each of the four contracts carries the paragraph; one mutant. Policy files: the owner approves the merge.

Carry 2: Moved from R10-FLY-STANDING-CONTRACTS carry 1 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

Re-routed by orchestrator s9 under mandate 6329234399 (tvofi's request, 2026-10-31, slipped-proposal audit): R10-ORCH-BEATD is done (#2916) with the carry unbuilt, and `git grep` at origin/main finds the feature absent. (triage: dev/programme/triage/s6-batch20.md#P95) In each dev/governance/roles/standing-*.md, add one 'Reads' line naming the cwd-safe instrument for every read the seat makes, and state that a hand-written pipeline (`| wc -l`, `grep -c`, a bare `git` or `gh`) is never a check result. A PR body is read with tools/policy/policy_lint.mjs --pr-body and tools/audit/carry_audit.py check --body. A PR's state is read with `gh pr view --repo tvofi/heatpump_optimizer`, printing UNREADABLE on a non-zero exit or an empty answer. Handoff refs are read with tools/audit/seat/bus.sh orphans or `git -C <worktree>`. Basis: 3 false states on 2026-10-24/25, every one from a hand-written read in a seat flow (sweep `git ls-remote`, roster `gh pr view 2>/dev/null`, dispatch's #2772 body check, a false clean 0). From a directory outside any repository, policy_lint and carry_audit still judged correctly while `git diff ... | wc -l` printed 0 with exit 0. Each Bash call starts in the seat's original directory. Controls: a review of each contract finds the Reads line, and policy_lint's corpus check passes; policy files, so the owner approves the merge under the mandate.

Carry 3: Moved from R10-FLY-STANDING-CONTRACTS carry 2 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

From the s9 script census, hand discipline in the dispatch seat with no sentence in its contract: hold a reviewer dispatch until the mutation-autofix (or closures-autofix) bot commit lands on the head, or until the pin jobs end with no commit, so the review is not voided by the bot moving the head under it. `git show origin/main:dev/governance/roles/standing-dispatch.md | grep -ni 'autofix\|bot commit'` is empty, and .claude/rules/ci-autofix.md says only to wait for the bot commit, nothing about dispatching a reviewer. Fold: a paragraph in standing-dispatch.md (and, for the merge seat, standing-merge.md) stating the predicate in checkable terms: dispatch a reviewer at head H only when no autofix job (mutation-autofix, closures-autofix, claims-autofix) at H is queued or in_progress, and either a bot commit has already moved the head (dispatch at the new head) or every autofix job concluded without a push (a red autofix job means no bot commit comes, ci-autofix.md line 28). Name the read: `failure_logs.sh` / `gh api repos/<r>/commits/<H>/check-runs`. Planted control for the prose: add the predicate as a row in the contracts' Reads line check so `tests/entities.py` (or the policy lint the group uses) fails if the sentence is removed; null control: the sentence present passes. A mechanical refusal in bus.sh dispatch is NOT folded here (no live group owns bus.sh dispatch semantics); it is filed as a triage PROPOSAL. Carry: R10-FLY-STANDING-CONTRACTS

Carry 4: Moved from R10-FLY-STANDING-CONTRACTS carry 3 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

Owner rule (tvofi, 2026-10-31, verbatim: "To be token effective, you should recycle the standing seat at a suitable frequency", then "Make that rule persistent"). Add a Recycle paragraph to each of dev/governance/roles/standing-merge.md, standing-dispatch.md, standing-roster.md and standing-tick.md, and to orchestrator.md section 5's standing-seats sentence. These are policy files, so the owner approves the merge.
- Trigger: a standing seat is recycled once its context passes about 150k tokens or it has run 4 h, whichever comes first.
- Quiet point: only when no op of its own is mid-step and no train, push or open it owns is in flight.
- During a recycle the orchestrator routes new work only to the incoming seat, after the outgoing one replied HANDED (2026-10-31: overlapping instructions minted 3 nonces at one head).
- Handoff: it writes <seat dir>/STATE-HANDOFF.md (pending waits with targets, in-flight ops, queue positions, held lines and their release conditions, next actions), stops only its own loops by PID, and ends. A fresh seat starts from its brief plus that file.
- Field figures, 2026-10-31: triage reached about 417k tokens, merge 213k, dispatch 214k and opener 174k. The fresh opener resumed at about 32k.
Control: a contract-lint row requiring the paragraph in each standing contract (the null passes, deleting one reddens). Carry: R10-FLY-STANDING-CONTRACTS

Carry 5: Moved from R10-FLY-STANDING-CONTRACTS carry 4 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

From the HANDOVER rewrite (handoff/r10-handover-s9 c2ebaeb59, 2026-10-31). dev/governance/roles/standing-merge.md still names tools/audit/seat/merge_pr.sh for a head that merges directly (a budget-file or policy head under the mandate). tvofi's 2026-10-26 ruling, "no merge outside the train", supersedes that: such heads take train.sh's serial route, where --pre-flight parks them and they merge under the mandate. Edit the contract to say so, as a policy change approved before merging. Control: a grep of the role contracts for merge_pr.sh as a merge route returns nothing at the head.

Carry 6: Moved from R10-FLY-STANDING-CONTRACTS carry 8 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

From triage P330 (queue 2026-10-31T13:24:23Z, owner-flagged: tvofi 2026-10-31 "it should queue and batch merges where possible"): in `dev/governance/roles/standing-merge.md`'s Instruments paragraph, state that a verdicted pull request on the recommended flags joins the live train (`train.sh add`) as its next batch and never waits for that train to end; only a pull request whose flags differ (a `--no-pre-flight` waiver) waits for its own train, and waivers due together share one. Paid within the file's cap (policy_lint --budgets at 0cae227c3: 36/37 lines, 501/507 tokens; e.g. replace line 9's "one live train," and shorten the `RECOMMENDED` parenthetical); no raise. Policy: owner approval at merge (or mandate 6329234399, scope all). Instance: s9 merge-seat sequencers seq3.sh/seq4.sh ran `add` only after each `TRAIN_RC`, planning #3037, #3030 and #3039 as three solo trains; a solo train ran 48-67 min (#3022, #3038). Rejected: an `add` refusal of a second train (train.sh's pidfile and merge_train's flock already allow one per state dir; a sequencer that waits for TRAIN_RC starts no concurrent train, so the refusal sees nothing). triage: dev/programme/triage/s6-batch91.md#P330

Carry 7: Moved from R10-FLY-STANDING-CONTRACTS carry 9 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

tvofi 2026-10-24 card 1 recommendation (d) (CARDS.json (prestudy-mech, r10s6 scratch, not in the tree)): R10-ORCH-BEATD folds into orchestrator.md that the orchestrator reads only the ledger and the plan page. When this group lands, make that sentence true of the plan page (the page is the single state view) and edit the one line in orchestrator.md that names the ledger digest alone. Binding constraint (owner, tvofi 2026-10-24, verbatim): 'make sure the retirement of the standing seats dont cause you to run things inline'. A seat's work moves to a daemon or beat job, never into the orchestrator's turns, and the seat stays until its replacement job is live and verified.

Carry 8: Moved from R10-FLY-STANDING-CONTRACTS carry 10 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 8 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 11; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: yes.

Why stranded: R10-ORCH-BEATD done at #2916 with arm (a) only (#2916 body: "The (b) and (c) carries stay on the roster group"); design/R10-ORCH-BEATD 32e249d2 sections 3-4 scope arms (b) and (c); `git grep -i "only the ledger|plan page" origin/main -- dev/governance/roles/orchestrator.md` is empty; R10-ORCH-PLANPAGE carry[4] presumes BEATD wrote the sentence ("R10-ORCH-BEATD folds into orchestrator.md that ..."), so nobody writes it.

Fold into: R10-ORCH-PLANPAGE (live). Its carry[4] edits the same orchestrator.md line and presumes this sentence exists.

Original text, verbatim:
tvofi 2026-10-24 card 1 recommendation (d) (CARDS.json (prestudy-mech, r10s6 scratch, not in the tree)), folded into this group's contract edit: once this group lands the orchestrator reads only the ledger and the plan page for state, and no longer re-reads the digest sources, the seats' scratch or the bus. orchestrator.md names the ledger digest now and the plan page once R10-ORCH-PLANPAGE lands; R10-ORCH-PLANPAGE carries the one-line follow-up. Binding constraint (owner, tvofi 2026-10-24, verbatim): 'make sure the retirement of the standing seats dont cause you to run things inline'. A seat's work moves to a daemon or beat job, never into the orchestrator's turns, and the seat stays until its replacement job is live and verified.

Carry: R10-ORCH-PLANPAGE

Carry 9: Moved from R10-FLY-STANDING-CONTRACTS carry 11 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 2 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-AUTOTRAIN, index 1; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: yes.

Why stranded: owner card 1 (merge seat retirement): standing-merge.md still a live seat contract; the pitch job is K17 (1) but nothing retires the seat; design arm (c) of BEATD keeps STANDING={"merge":120}; no live owner of the retirement text.

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
tvofi 2026-10-24 card 1 (owner accepted; CARDS.json (prestudy-mech, r10s6 scratch, not in the tree)): when this group lands, the standing merge seat retires: the queue builder and the train run as a daemon or beat job (train.sh and merge_train.py), their per-pitch outcome goes to the digest, and no pitch is assembled in the orchestrator's turn. Edit dev/governance/roles/standing-merge.md in this group or in R10-ORCH-BEATD's contract edit, whichever merges later, not both. Binding constraint (owner, tvofi 2026-10-24, verbatim): 'make sure the retirement of the standing seats dont cause you to run things inline'. A seat's work moves to a daemon or beat job, never into the orchestrator's turns, and the seat stays until its replacement job is live and verified. Acceptance: one real pitch is built and merged by the job, with the merge seat watching and agreeing; only then is the seat stopped.

Carry: R10-ORCH-LEDGER

Carry 10: Moved from R10-FLY-STANDING-CONTRACTS carry 12 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 6 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-ROSTER-FREEZE, index 5; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: yes.

Why stranded: owner card 1 (roster seat retirement): #2903 Forward-carry "roster_queue.py exists, but no beat job runs it. The job belongs to the beat"; BEATD [22] took it and closed unbuilt.

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
tvofi 2026-10-24 card 1 (owner accepted; CARDS.json (prestudy-mech, r10s6 scratch, not in the tree)): when this group lands, the standing roster seat retires: a daemon or beat job reads the orchestrator's roster queue file, runs each roster_edit.py op with --lint-cwd at a fresh origin/main and --push, and writes one 'roster: <op> <group> pushed <sha>' or 'refused <reason>' line per op into the digest; a refusal is never retried past the lint gate. Edit dev/governance/roles/standing-roster.md in this group or in R10-ORCH-BEATD's contract edit, whichever merges later, not both. Binding constraint (owner, tvofi 2026-10-24, verbatim): 'make sure the retirement of the standing seats dont cause you to run things inline'. A seat's work moves to a daemon or beat job, never into the orchestrator's turns, and the seat stays until its replacement job is live and verified. Acceptance: the job lands a seeded no-op-safe op on a scratch roster branch and refuses a seeded lint failure, with the seat running beside it for one cycle; only then is the seat stopped.

Carry: R10-ORCH-LEDGER

Carry 11: Moved from R10-FLY-STANDING-CONTRACTS carry 13 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 11 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 22; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: yes.

Why stranded: R10-ORCH-BEATD done at #2916 with arm (a) only (#2916 body: "The (b) and (c) carries stay on the roster group"); design/R10-ORCH-BEATD 32e249d2 sections 3-4 scope arms (b) and (c); standing-roster.md has no retirement text; no beat job runs roster_queue.py (#2903 Forward-carry: "roster_queue.py exists, but no beat job runs it"); R10-ORCH-LEDGER[22] retires the tick seat only ("reverses the 2026-10-23 ruling for the tick seat only").

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
From R10-FLOW-ROSTER-FREEZE arm (a) (carry 5, tvofi 2026-10-24 card 1): this group merges after ROSTER-FREEZE, so its contract edit owns the standing roster seat's retirement in dev/governance/roles/standing-roster.md. A beat job runs tools/audit/seat/roster_queue.py run over the orchestrator's roster queue file (roster_edit.py ops with --lint-cwd at a fresh origin/main and --push), writing one 'roster: <op> <group> pushed <sha>' or 'refused <reason>' line per op into the digest; a refusal is never retried past the lint gate. Binding (owner, verbatim): 'make sure the retirement of the standing seats dont cause you to run things inline'. The seat stays until the job lands a seeded no-op-safe op on a scratch roster branch and refuses a seeded lint failure, with the seat running beside it for one cycle.

Carry: R10-ORCH-LEDGER

Carry 12: Moved from R10-FLY-STANDING-CONTRACTS carry 14 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 12 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-DISPATCH-REG, index 5; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: yes.

Why stranded: #2865 item [5] "Not built here: the beat and its job table are R10-ORCH-BEATD's"; BEATD done arm (a) only; BEATD carries [28]/[32] stranded with it.

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
Orchestrator ruling 2026-10-24 (tvofi card 1): the dispatch half of standing-dispatch.md (open_pr and update_pr, bus dispatch, pool briefs and verdict confirm) becomes a beat job owned by this group's registry. It never moves into the orchestrator's turns. The standing dispatch seat stays until that job has run beside it for one full cycle.

Carry: R10-ORCH-LEDGER

Carry 13: Moved from R10-FLY-STANDING-CONTRACTS carry 15 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 47 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 28; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: R10-ORCH-BEATD done at #2916 with arm (a) only (#2916 body: "The (b) and (c) carries stay on the roster group"); design/R10-ORCH-BEATD 32e249d2 sections 3-4 scope arms (b) and (c); #2865 body item [5]: "Not built here: the beat and its job table are R10-ORCH-BEATD's"; no bus.sh dispatch-owed (design arm (c)); no live owner.

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
From R10-ORCH-DISPATCH-REG (handoff de66f00b): **The dispatch half of standing-dispatch.md becomes a beat job owned by this registry.** Not built here: the beat and its job table are R10-ORCH-BEATD's (concern B), which is after this group. What it needs from here exists: one writer (`bus.sh dispatch`), a registry with time and model, a reopen on a failed publish. The standing dispatch seat stays until the job has run beside it for one full cycle.

Carry: R10-ORCH-LEDGER

Carry 14: Moved from R10-FLY-STANDING-CONTRACTS carry 16 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 49 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 32; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: R10-ORCH-BEATD done at #2916 with arm (a) only (#2916 body: "The (b) and (c) carries stay on the roster group"); design/R10-ORCH-BEATD 32e249d2 sections 3-4 scope arms (b) and (c); #2865 body item [5]: "Not built here: the beat and its job table are R10-ORCH-BEATD's"; no bus.sh dispatch-owed (design arm (c)); no live owner.

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
**R10-ORCH-BEATD: carry [5], the dispatch beat job.** It calls `bus.sh dispatch` (or `dispatch_group`), never a second writer of the registry or of the `reviewer-fire` close; the standing dispatch seat stays until the job has run beside it for one full cycle. Control: one beat pass over a handoff with no live dispatch leaves one registry line and one `close reviewer-fire` in `events.tsv`, and a second pass adds neither. Carry: R10-ORCH-BEATD

Carry: R10-ORCH-LEDGER

Carry 15: Moved from R10-FLY-STANDING-CONTRACTS carry 17 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

STRANDED CARRY 41 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 14; triage id: dev/programme/triage/s6-batch2.md#P45; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: R10-ORCH-BEATD done at #2916 with arm (a) only (#2916 body: "The (b) and (c) carries stay on the roster group"); design/R10-ORCH-BEATD 32e249d2 sections 3-4 scope arms (b) and (c); sweep_template.md steps still have the orchestrator start work (step (3) launches merge_train.py sweep, sweep_template.md:61); design arm (c) section 5 "23 rewrites" is this; no live owner (FLY-SEAT-ALIVE-ID edits only step (1b)/(2)/(5)).

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
Standing-seat wiring, item 1 (triage: dev/programme/triage/s6-batch2.md#P45, merged at d2dcfed15a0c9d0bb4934f4b29cd95dbe04bbf44). Adds tools/audit/seat/sweep_template.md to the group's files. sweep_template.md steps (2), (3), (4) and (6) tell the orchestrator to do inline what decision 0015 and the owner (2026-10-23T19:42Z) give to the standing seats; rewrite each to queue a line to its seat and read its report. Control: the rendered sweep names no train launch for the orchestrator; one mutant. Policy files: the owner approves the merge.

Carry: R10-ORCH-LEDGER

Carry 16: Moved from R10-FLY-STANDING-CONTRACTS carry 19 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

Owner order (tvofi, 2026-11-01, verbatim: "Make sure judging and folding every useful standing loop into the orchestrator machinery on main is planned in the roster, including describing the hooks and a script to set them up if they are not there"). Widens STEP 1 and STEP 2 of this group's brief; the design (design/R10-FLY-STANDING-CONTRACTS) carries it.

(1) JUDGE EVERY LOOP. The live-usage review gets one row per out-of-tree loop the round ran, with a verdict of fold (into a beat job in the job table, or into the tracked instrument it wraps), keep-as-is (already tracked; name the file), or drop (with the reason it bought nothing). Fold only what is useful, measured from its log: what it caught that nothing else caught. The loops the s9 orchestrator ran on 2026-11-01, by role (ask the orchestrator for their paths; cite none in tracked text):
- the sweep runner (roster drain, pulse, cancel sweep, opener-log forward, disk floor, plan beat, owed_unactioned) — already STEP 2;
- the roster drain — already STEP 2;
- the opener driver, which acts on the tick's handoff-no-pr and handoff-update lines. Fold its 2026-11-01 retry semantics: mark a (topic, sha) done only on success; retry a failure after a backoff (30 min), at most three times; then print one STUCK line the digest carries. Before that change it marked a handoff done at start, and 7 handoffs stood stranded 1-16 h on 2026-11-01. It is the opener carry b94-P337 builds, plus these semantics;
- the standing head watcher: one line per open-PR head move to the event digest (a reviewer or relay may be owed). A one-shot watcher's exit was lost across a compaction and a reviewer went unowed;
- the orchestrator wake loop: exits, and so wakes the orchestrator, on a new sweep digest, a new event line or a new STUCK line. After a compaction nobody re-armed it, and owed lines stood unread for up to 15.8 h while every instrument had flagged them;
- the triage seat's pass loop: releases held roster lines once the batch they wait on is on main, reads back landings, and exits on a new proposal or V-entry;
- the merge seat's watch loop: polls main and the frozen hotfix heads, and touches the merge seat's alive file;
- the dispatch head-await loop, now the standing head watcher above;
- tick_loop.sh, cloud_relay.sh and state_docs.py beat — tracked already; verdict keep-as-is unless the review finds a gap.
The design names the digest and event files under $HPO_STATE_DIR that one wake reads, so no loop writes only to a private log (the 2026-11-01 class).

(2) HOOKS, DESCRIBED AND INSTALLABLE. The orchestrator's sessions depend on user-level Claude Code hooks that are not in the tree:
- a SessionStart and PostCompact liveness hook: it demands a fresh policy re-read from origin/main, prints a measured ALIVE/DEAD line for each standing loop, fresh/STALE for the alive files and the digest, and the digest itself, then instructs the orchestrator to restart anything dead, check the standing seats and re-arm the wake loop that turn (owner, 2026-11-01: in both hooks);
- a PreToolUse Bash guard that keeps the main checkout clean;
- a SessionStart seat-interpreter hook (the seat venvs; see seat_venv.sh);
- a SessionStart git-identity hook.
Deliver: (a) a tracked description of each hook (what it does, the event, why it exists), beside the instruments guide (e.g. an instruments/hooks.md indexed from INSTRUMENTS.md); (b) the hook scripts as tracked files, with machine paths taken from $HPO_STATE_DIR or arguments (tmp_paths.py and ref_privacy.py must pass); (c) one setup script under tools/audit/seat/ with --check (report which hooks are missing or differ from the tree, change nothing) and --install (idempotent: add a missing hook entry to the user's settings without touching unrelated entries, back the file up first, print what it changed), plus --self-test against a throwaway HOME (offline_spy.py) and wiring for selftest_wiring.py. The liveness hook's loop list is generated from the job table, so a new job is checked the day it lands. The tree already has project-level hooks (.claude/settings.json, .claude/hooks/session-start.sh): the design decides, per hook, whether it belongs there (binds every session in this repository, no installer needed) or at user level (host-specific), and the installer covers only the latter. Reconcile with R10-POLICY-ROLE-PACK (which owns a SessionStart policy pack) and R10-BASH-KILL-HOOK (a PreToolUse Bash hook): one settings layout, one installer; the later group adds its hook to this installer rather than shipping its own.

Controls: a planted dead loop prints DEAD and a planted stale digest prints STALE; on a healthy table the hook prints nothing actionable; --check on a fresh throwaway HOME lists every hook as missing, and --install then --check lists none; a second --install changes nothing (byte-identical settings); a mutant that drops the backup, or rewrites an unrelated entry, is killed. Re-measure the 2026-11-01 figures above from the orchestrator's ledger at this group's merge base; carry no count.

Carry 17: Moved from R10-FLY-STANDING-CONTRACTS carry 20 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

Re-routed by orchestrator s9 (tvofi 2026-10-31: "The tick seat is planned to be replaced by a script within the sweep, verify that that is planned in the roster"). R10-ORCH-BEATD carry 10 (tvofi 2026-10-24 card 1, owner accepted) was closed unbuilt when BEATD went done at #2916 with arm (a) only, and no live group carried it.
The carry: retire the standing tick seat into the beat. The beat's tick job writes a digest file of the board's actionable family, and the orchestrator reads that digest. Codify the retirement in dev/governance/roles/standing-tick.md and the standing-seats paragraph of dev/governance/roles/orchestrator.md section 5, both policy that the owner approves at merge. That edit reverses the 2026-10-23 ruling for the tick seat only; proposal triage stays an LLM seat.
Binding constraint (tvofi 2026-10-24, verbatim): 'make sure the retirement of the standing seats dont cause you to run things inline'. The seat's work moves to a daemon or beat job, never into the orchestrator's turns.
Local stand-in, live since 2026-10-31T19:32Z: ~/hpo-orch/r10s6/s9/tick-digest/the tick-digest script (out of tree; read it as the reference shape, never cite its path in the tree). Every 240 s, on a changed tick.txt, it greps the actionable family (OWED, DISPATCH, OWNER FLAG, BLOCKED-UNFIXED, DESIGN-BUILD, UNREADABLE, DESIGN OWED, REVIEW OWED, REVIEW STALLED, UNLEVELLED, APPROVAL*, MERGE-READY, code-owned-without-review, NOT REVIEWABLE, DIRTY, RED unanswered, main red) and normalises timestamps and ages. It writes digest.txt, new.txt and gone.txt, runs owed_unactioned.py (UNACTIONED lines into new.txt), and touches the tick seat's alive file. The orchestrator's background until-loop wakes only when new.stamp changes.
Build: a `tick-digest` job in the beatd job table beside this group's heartbeat and pitch jobs, either as a tools/audit/seat/ script or as an orchestrator_tick.py `--digest` mode. Write it under $HPO_STATE_DIR, with the sweep template's step (5) reading the digest in place of the tick seat. Remove tick_brief from the placeholder table, or make it optional.
Controls: an unchanged board writes no new.txt (null); a board gaining one OWED line writes exactly that line; a timestamp-only change writes nothing; an UNACTIONED exit from owed_unactioned.py lands in new.txt. Carry: R10-ORCH-LEDGER

Carry 18: Moved from R10-FLY-STANDING-CONTRACTS carry 21 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

Owner direction (tvofi, 2026-10-31, verbatim: "consider if all of the seats and their tasks are necessary LLM tasks. For example, state docs could go in your sweep script"). Orchestrator s9's classification: tick, roster drain, opener relay, record beat (replan + state_docs --plan), pulse, cancel_superseded sweep and the disk check are mechanical. Dispatch briefs and triage rulings need judgement, and merge does once #3054 (closing-stage field) and R10-FLY-TRAIN-DEFAULTS part 2 land.
Build the mechanical ones as the beatd job table jobs, beside this group's heartbeat, pitch and tick-digest jobs:
- roster-drain: roster_queue.py run over each pending non-# queue line, marking the line from its report line;
- plan-beat: replan.py --out, then state_docs.py --push --mirror --plan, every 30 min;
- pulse;
- cancel-sweep: cancel_superseded.py sweep;
- disk: worktree_gc.sh below the floor;
- opener: the open-driver script of carry b94-P337.
Every job writes into the one digest the orchestrator's single wake reads (the tick-digest carry), so an LLM seat wakes only on a refusal or a judgement.
Local stand-in, live since 2026-10-31: ~/hpo-orch/r10s6/s9/sweep-runner/the sweep-runner script (out of tree, the reference shape). Remove that seat from each standing contract only once its job is live and verified (the owner's 2026-10-24 constraint: "make sure the retirement of the standing seats dont cause you to run things inline").
Controls: each job's null (nothing owed writes nothing) and planted case (one pending queue line drains and is marked; one REFUSE line reaches the digest). Carry: R10-ORCH-LEDGER

Carry 19: Moved from R10-FLY-STANDING-CONTRACTS carry 27 (0-based) by the carries-open audit (orchestrator s13, 2026-11-09); its own pull request merged and nothing dispatched this carry. Text verbatim:

From #3294, body item 88565884: The liveness hook's alive files are read from $HPO_STATE_DIR/alive/ and the digest's freshness from digest.txt or the beat journal (digest.txt is rewritten only on a change); P2 should name the alive-file directory in standing.md. Carry: R10-FLY-STANDING-CONTRACTS (items 88565884)
