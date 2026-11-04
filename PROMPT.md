CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-fly-standing-contracts, at head c3a279e3252a8b57bb00b5a677318cd4fe20387f. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name seat && git config user.email seat@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch c3a279e3252a8b57bb00b5a677318cd4fe20387f for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-fly-standing-contracts before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-fly-standing-contracts, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-fly-standing-contracts, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-fly-standing-contracts <body.md>`, which pushes refs/heads/handoff-body/r10-fly-standing-contracts; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-fly-standing-contracts`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-fly-standing-contracts. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
INTERIM TOOLCHAIN: this environment's cached venvs are behind the locks (numpy, scipy, homeassistant, measured 2026-11-04). Before any measurement or golden run: `bash tools/audit/seat/cloud-setup.sh` and then `bash tools/audit/seat/cloud-setup.sh --check`; also confirm `python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'` against tests/requirements-ci.txt. If it cannot be refreshed say so in the body; CI remains the authority for goldens. Medium effort.

Fixers return only by refs, handoff/<topic> and body_push.sh; open no PR, post no comment; no Claude footers; no host paths.

Standing-seat mechanisation, made permanent (owner, tvofi 2026-10-31, verbatim: "Fold in making this mechanisation/updated sweep and contracts permanent in a suitable group. The group should also review the live usage of the sweep so for when it starts, and fix any gaps"). The owner also ruled: "consider if all of the seats and their tasks are necessary LLM tasks", "the tick seat is planned to be replaced by a script within the sweep" and "recycle the standing seat at a suitable frequency ... Make that rule persistent". Re-scoped by orchestrator s9 from the two contract edits this group held (carries 0-1, from R10-ORCH-BEATD), which stay in scope. Size L (tvofi 2026-11-01, at 20 carries): a designer writes design/R10-FLY-STANDING-CONTRACTS per dev/governance/roles/designer.md, and it passes design review (design-review.md), before any fixer starts. The four contracts are policy, so the owner approves the merge.
STEP 1, before any code: a live-usage review. Read how the sweep and its local stand-ins ran in the session that dispatches you, and list every gap before building. Sources:
- the orchestrator's seat ledger and its OWED-ACK lines;
- the stand-ins' logs: the tick digest (the tick-digest script, its digest log and new/gone files), the sweep runner (the sweep-runner script, the roster-drain script and the runner log), and the opener driver's log;
- the rendered sweep and its overlay;
- cloud_relay's level file;
- the tick board.
Ask the orchestrator for their absolute paths; they are out of tree, so read them and never cite them in tracked text. Compare each against tools/audit/seat/sweep_template.md step by step, and against the four standing contracts. Each gap is a row in the body's `## Live-usage review` with its evidence. Gaps recorded in the field on 2026-10-31:
- owed_unactioned.py counts every run as a sweep, so it must run once per sweep, never per tick pass;
- the tick can read a PR between open_pr's two pushes, so a NOT REVIEWABLE or RED line at an intermediate merge head is transient;
- a blind touch loop on a seat's alive file defeats liveness;
- a sweep step that fast-forwards the checkout the tick loop and relay run from corrupts them, because bash reads its scripts incrementally;
- during a recycle, sending work to both the outgoing and incoming seat minted three nonces at one head;
- hold-file lines never expire.
STEP 2, build: the tracked forms of the mechanised seats, as tools/audit/seat/ jobs in the beat's job table, which does not exist yet (create it if R10-ORCH-LEDGER has not, and its heartbeat and pitch rows add to it):
- tick-digest (its carry, re-routed here);
- roster-drain (roster_queue.py over pending lines with exact-line marking; census-10's loop if it has landed);
- plan-beat (replan.py, then state_docs.py --push --mirror --plan, every 30 min);
- pulse;
- cancel-sweep;
- disk;
- the opener, through the opener driver carry b94-P337 builds, once it lands, else a job invoking the tracked opener.
Every job writes only actionable lines to one digest under $HPO_STATE_DIR, the file the orchestrator's single wake reads.
STEP 3, the template and contracts:
- sweep_template.md: steps (1b) and (5) read the digest; the tick-seat restart becomes a tick-digest job check; tick_brief drops out of the placeholder table, or becomes optional.
- standing-tick.md and standing-roster.md: mark the seat retired into its job, with the owner's 2026-10-24 constraint ('make sure the retirement of the standing seats dont cause you to run things inline'). Remove a seat only once its job is live and verified.
- All four contracts: the Recycle paragraph (carry s9-seat-recycle) plus carries 0-1's Wait and Reads paragraphs.
- orchestrator.md section 5's standing-seats sentence: name which seats remain LLM seats (dispatch, triage; merge until closing-stage field and the approval-race fix land) and that the rest are beat jobs.
Controls:
- each job's null (nothing owed writes nothing) and a planted case;
- the digest reproduces a recorded board's actionable set;
- a contract-lint row per paragraph;
- a mutant per job's predicate.

After: none

Carry 0: Re-routed by orchestrator s9 under mandate 6329234399 (tvofi's request, 2026-10-31, slipped-proposal audit): R10-ORCH-BEATD is done (#2916) with arm (a) only, and `git grep -n -i -E "run_in_background|nothing is owed" origin/main -- dev/governance/roles/standing-tick.md dev/governance/roles/standing-merge.md` finds no Wait paragraph. (triage: dev/programme/triage/s6-batch2.md#P51) In each of dev/governance/roles/standing-tick.md, standing-merge.md, standing-dispatch.md and standing-roster.md, add a Wait paragraph of about 6 lines: a seat ends a turn only when nothing is owed; it waits with a `run_in_background` shell loop that touches its alive file every 25 s and exits on a queue change or the window's end, so its exit wakes the turn; a detached `nohup` wakes nothing. A tracked seat_loop.sh is REJECTED by P51. Basis: 4 standing seats ended their first turn on an untracked watcher in the opening 11 minutes of one session, and each needed an orchestrator SendMessage. Controls: each of the four contracts carries the paragraph; one mutant. Policy files: the owner approves the merge.

Carry 1: Re-routed by orchestrator s9 under mandate 6329234399 (tvofi's request, 2026-10-31, slipped-proposal audit): R10-ORCH-BEATD is done (#2916) with the carry unbuilt, and `git grep` at origin/main finds the feature absent. (triage: dev/programme/triage/s6-batch20.md#P95) In each dev/governance/roles/standing-*.md, add one 'Reads' line naming the cwd-safe instrument for every read the seat makes, and state that a hand-written pipeline (`| wc -l`, `grep -c`, a bare `git` or `gh`) is never a check result. A PR body is read with tools/policy/policy_lint.mjs --pr-body and tools/audit/carry_audit.py check --body. A PR's state is read with `gh pr view --repo tvofi/heatpump_optimizer`, printing UNREADABLE on a non-zero exit or an empty answer. Handoff refs are read with tools/audit/seat/bus.sh orphans or `git -C <worktree>`. Basis: 3 false states on 2026-10-24/25, every one from a hand-written read in a seat flow (sweep `git ls-remote`, roster `gh pr view 2>/dev/null`, dispatch's #2772 body check, a false clean 0). From a directory outside any repository, policy_lint and carry_audit still judged correctly while `git diff ... | wc -l` printed 0 with exit 0. Each Bash call starts in the seat's original directory. Controls: a review of each contract finds the Reads line, and policy_lint's corpus check passes; policy files, so the owner approves the merge under the mandate.

Carry 2: From the s9 script census, hand discipline in the dispatch seat with no sentence in its contract: hold a reviewer dispatch until the mutation-autofix (or closures-autofix) bot commit lands on the head, or until the pin jobs end with no commit, so the review is not voided by the bot moving the head under it. `git show origin/main:dev/governance/roles/standing-dispatch.md | grep -ni 'autofix\|bot commit'` is empty, and .claude/rules/ci-autofix.md says only to wait for the bot commit, nothing about dispatching a reviewer. Fold: a paragraph in standing-dispatch.md (and, for the merge seat, standing-merge.md) stating the predicate in checkable terms: dispatch a reviewer at head H only when no autofix job (mutation-autofix, closures-autofix, claims-autofix) at H is queued or in_progress, and either a bot commit has already moved the head (dispatch at the new head) or every autofix job concluded without a push (a red autofix job means no bot commit comes, ci-autofix.md line 28). Name the read: `failure_logs.sh` / `gh api repos/<r>/commits/<H>/check-runs`. Planted control for the prose: add the predicate as a row in the contracts' Reads line check so `tests/entities.py` (or the policy lint the group uses) fails if the sentence is removed; null control: the sentence present passes. A mechanical refusal in bus.sh dispatch is NOT folded here (no live group owns bus.sh dispatch semantics); it is filed as a triage PROPOSAL. Carry: R10-FLY-STANDING-CONTRACTS

Carry 3: Owner rule (tvofi, 2026-10-31, verbatim: "To be token effective, you should recycle the standing seat at a suitable frequency", then "Make that rule persistent"). Add a Recycle paragraph to each of dev/governance/roles/standing-merge.md, standing-dispatch.md, standing-roster.md and standing-tick.md, and to orchestrator.md section 5's standing-seats sentence. These are policy files, so the owner approves the merge.
- Trigger: a standing seat is recycled once its context passes about 150k tokens or it has run 4 h, whichever comes first.
- Quiet point: only when no op of its own is mid-step and no train, push or open it owns is in flight.
- During a recycle the orchestrator routes new work only to the incoming seat, after the outgoing one replied HANDED (2026-10-31: overlapping instructions minted 3 nonces at one head).
- Handoff: it writes <seat dir>/STATE-HANDOFF.md (pending waits with targets, in-flight ops, queue positions, held lines and their release conditions, next actions), stops only its own loops by PID, and ends. A fresh seat starts from its brief plus that file.
- Field figures, 2026-10-31: triage reached about 417k tokens, merge 213k, dispatch 214k and opener 174k. The fresh opener resumed at about 32k.
Control: a contract-lint row requiring the paragraph in each standing contract (the null passes, deleting one reddens). Carry: R10-FLY-STANDING-CONTRACTS

Carry 4: From the HANDOVER rewrite (handoff/r10-handover-s9 c2ebaeb59, 2026-10-31). dev/governance/roles/standing-merge.md still names tools/audit/seat/merge_pr.sh for a head that merges directly (a budget-file or policy head under the mandate). tvofi's 2026-10-26 ruling, "no merge outside the train", supersedes that: such heads take train.sh's serial route, where --pre-flight parks them and they merge under the mandate. Edit the contract to say so, as a policy change approved before merging. Control: a grep of the role contracts for merge_pr.sh as a merge route returns nothing at the head.

Carry 5: Re-routed by orchestrator s9 under mandate 6329234399 (tvofi's request, 2026-10-31, slipped-proposal audit): R10-ORCH-BEATD is done (#2916) and its carries do not name P103, and `git grep` at origin/main finds the feature absent. (triage: dev/programme/triage/s6-batch22.md#P103) In tools/audit/seat/pulse.py, make the verdict arm name every unconsumed verdict, not only the oldest: `judge_verdict` prints one line per owed verdict (PR, verdict word, head, age), and the standing-seat routing names the merge seat when any owed verdict is a merge and dispatch when any is not. Self-test: a blocked verdict older than a merge verdict names both PRs and both seats; the null control, one owed verdict, prints one line. Mutation proof: restoring the oldest-only summary fails the two-verdict case. Basis: #2749's MERGE verdict sat unqueued for 3.8 h behind #2780's blocked verdict on 2026-10-25.

Carry 6: Re-routed by orchestrator s9 under mandate 6329234399 (tvofi's request, 2026-10-31, slipped-proposal audit): R10-ORCH-BEATD is done (#2916) with the carry unbuilt, and `git grep` at origin/main finds the feature absent. (triage: dev/programme/triage/s6-batch20.md#P94) tools/audit/seat/sweep_template.md step (2): pin the handoff listing to the orchestrator's checkout, `git -C {{orch_checkout}} ls-remote --heads origin 'handoff/r{{round}}-*'`, as step (0) already does with `-C {{orch_checkout}}`. Evidence: the 2026-10-24 23:49Z sweep ran it from the state directory, got "'origin' does not appear to be a git repository", and read no probe or handoff refs that sweep. Controls: a tools/audit/seat/sweep_render.py fixture row asserting that every `git ` command in the rendered sweep carries `-C` (null: the old step (2) text fails the row); one mutant drops the `-C`.

Carry 7: Re-routed by orchestrator s9 under mandate 6329234399 (tvofi's request, 2026-10-31, slipped-proposal audit): R10-ORCH-BEATD is done (#2916) with the carry unbuilt, and `git grep` at origin/main finds the feature absent. (triage: dev/programme/triage/s6-batch32.md#P190) Sweep step (5) reads the whole tick board (V110). In `tools/audit/seat/sweep_template.md` step (5), replace 'Act on the newest actionable lines of {{tick_log}}' with: act on every `-> ` line of {{tick_log}}, the board `tick_loop.sh --out` writes. OWED lines are a level re-printed every pass, not a diff. Print `grep -c '^-> ' {{tick_log}}` and `grep -c 'OWED' {{tick_log}}` beside the actions taken, and read the file untruncated. A disposition that defers an OWED line to a seat names that seat's ledger id or PID, and the next sweep re-checks it; one naming no seat is not a disposition. Document `tick_log` in the template's placeholder table as that board, never the retired tick seat's `tick-owed.txt`. Observed 2026-10-25/26: the overlay's tick_log named `tick-owed.txt`, frozen since 15:33 local. `reviewer-fire 2836` was line 107 of 131 on `tick.txt` and went unrendered 1 h 53 min. mq-probe was disposed at 18:12Z as 'local seat covers' with no seat named, and sat 4.5 h. Controls: `sweep_render.py` over a fixture overlay renders step (5) naming the board path and both counts; a mutant restoring 'newest actionable lines' fails the render check; the rendered text names no `tick-owed` (null: other steps unchanged).

Carry 8: From triage P330 (queue 2026-10-31T13:24:23Z, owner-flagged: tvofi 2026-10-31 "it should queue and batch merges where possible"): in `dev/governance/roles/standing-merge.md`'s Instruments paragraph, state that a verdicted pull request on the recommended flags joins the live train (`train.sh add`) as its next batch and never waits for that train to end; only a pull request whose flags differ (a `--no-pre-flight` waiver) waits for its own train, and waivers due together share one. Paid within the file's cap (policy_lint --budgets at 0cae227c3: 36/37 lines, 501/507 tokens; e.g. replace line 9's "one live train," and shorten the `RECOMMENDED` parenthetical); no raise. Policy: owner approval at merge (or mandate 6329234399, scope all). Instance: s9 merge-seat sequencers seq3.sh/seq4.sh ran `add` only after each `TRAIN_RC`, planning #3037, #3030 and #3039 as three solo trains; a solo train ran 48-67 min (#3022, #3038). Rejected: an `add` refusal of a second train (train.sh's pidfile and merge_train's flock already allow one per state dir; a sequencer that waits for TRAIN_RC starts no concurrent train, so the refusal sees nothing). triage: dev/programme/triage/s6-batch91.md#P330

Carry 9: tvofi 2026-10-24 card 1 recommendation (d) (CARDS.json (prestudy-mech, r10s6 scratch, not in the tree)): R10-ORCH-BEATD folds into orchestrator.md that the orchestrator reads only the ledger and the plan page. When this group lands, make that sentence true of the plan page (the page is the single state view) and edit the one line in orchestrator.md that names the ledger digest alone. Binding constraint (owner, tvofi 2026-10-24, verbatim): 'make sure the retirement of the standing seats dont cause you to run things inline'. A seat's work moves to a daemon or beat job, never into the orchestrator's turns, and the seat stays until its replacement job is live and verified.

Carry 10: STRANDED CARRY 8 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 11; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: yes.

Why stranded: R10-ORCH-BEATD done at #2916 with arm (a) only (#2916 body: "The (b) and (c) carries stay on the roster group"); design/R10-ORCH-BEATD 32e249d2 sections 3-4 scope arms (b) and (c); `git grep -i "only the ledger|plan page" origin/main -- dev/governance/roles/orchestrator.md` is empty; R10-ORCH-PLANPAGE carry[4] presumes BEATD wrote the sentence ("R10-ORCH-BEATD folds into orchestrator.md that ..."), so nobody writes it.

Fold into: R10-ORCH-PLANPAGE (live). Its carry[4] edits the same orchestrator.md line and presumes this sentence exists.

Original text, verbatim:
tvofi 2026-10-24 card 1 recommendation (d) (CARDS.json (prestudy-mech, r10s6 scratch, not in the tree)), folded into this group's contract edit: once this group lands the orchestrator reads only the ledger and the plan page for state, and no longer re-reads the digest sources, the seats' scratch or the bus. orchestrator.md names the ledger digest now and the plan page once R10-ORCH-PLANPAGE lands; R10-ORCH-PLANPAGE carries the one-line follow-up. Binding constraint (owner, tvofi 2026-10-24, verbatim): 'make sure the retirement of the standing seats dont cause you to run things inline'. A seat's work moves to a daemon or beat job, never into the orchestrator's turns, and the seat stays until its replacement job is live and verified.

Carry: R10-ORCH-PLANPAGE

Carry 11: STRANDED CARRY 2 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-AUTOTRAIN, index 1; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: yes.

Why stranded: owner card 1 (merge seat retirement): standing-merge.md still a live seat contract; the pitch job is K17 (1) but nothing retires the seat; design arm (c) of BEATD keeps STANDING={"merge":120}; no live owner of the retirement text.

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
tvofi 2026-10-24 card 1 (owner accepted; CARDS.json (prestudy-mech, r10s6 scratch, not in the tree)): when this group lands, the standing merge seat retires: the queue builder and the train run as a daemon or beat job (train.sh and merge_train.py), their per-pitch outcome goes to the digest, and no pitch is assembled in the orchestrator's turn. Edit dev/governance/roles/standing-merge.md in this group or in R10-ORCH-BEATD's contract edit, whichever merges later, not both. Binding constraint (owner, tvofi 2026-10-24, verbatim): 'make sure the retirement of the standing seats dont cause you to run things inline'. A seat's work moves to a daemon or beat job, never into the orchestrator's turns, and the seat stays until its replacement job is live and verified. Acceptance: one real pitch is built and merged by the job, with the merge seat watching and agreeing; only then is the seat stopped.

Carry: R10-ORCH-LEDGER

Carry 12: STRANDED CARRY 6 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-ROSTER-FREEZE, index 5; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: yes.

Why stranded: owner card 1 (roster seat retirement): #2903 Forward-carry "roster_queue.py exists, but no beat job runs it. The job belongs to the beat"; BEATD [22] took it and closed unbuilt.

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
tvofi 2026-10-24 card 1 (owner accepted; CARDS.json (prestudy-mech, r10s6 scratch, not in the tree)): when this group lands, the standing roster seat retires: a daemon or beat job reads the orchestrator's roster queue file, runs each roster_edit.py op with --lint-cwd at a fresh origin/main and --push, and writes one 'roster: <op> <group> pushed <sha>' or 'refused <reason>' line per op into the digest; a refusal is never retried past the lint gate. Edit dev/governance/roles/standing-roster.md in this group or in R10-ORCH-BEATD's contract edit, whichever merges later, not both. Binding constraint (owner, tvofi 2026-10-24, verbatim): 'make sure the retirement of the standing seats dont cause you to run things inline'. A seat's work moves to a daemon or beat job, never into the orchestrator's turns, and the seat stays until its replacement job is live and verified. Acceptance: the job lands a seeded no-op-safe op on a scratch roster branch and refuses a seeded lint failure, with the seat running beside it for one cycle; only then is the seat stopped.

Carry: R10-ORCH-LEDGER

Carry 13: STRANDED CARRY 11 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 22; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: yes.

Why stranded: R10-ORCH-BEATD done at #2916 with arm (a) only (#2916 body: "The (b) and (c) carries stay on the roster group"); design/R10-ORCH-BEATD 32e249d2 sections 3-4 scope arms (b) and (c); standing-roster.md has no retirement text; no beat job runs roster_queue.py (#2903 Forward-carry: "roster_queue.py exists, but no beat job runs it"); R10-ORCH-LEDGER[22] retires the tick seat only ("reverses the 2026-10-23 ruling for the tick seat only").

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
From R10-FLOW-ROSTER-FREEZE arm (a) (carry 5, tvofi 2026-10-24 card 1): this group merges after ROSTER-FREEZE, so its contract edit owns the standing roster seat's retirement in dev/governance/roles/standing-roster.md. A beat job runs tools/audit/seat/roster_queue.py run over the orchestrator's roster queue file (roster_edit.py ops with --lint-cwd at a fresh origin/main and --push), writing one 'roster: <op> <group> pushed <sha>' or 'refused <reason>' line per op into the digest; a refusal is never retried past the lint gate. Binding (owner, verbatim): 'make sure the retirement of the standing seats dont cause you to run things inline'. The seat stays until the job lands a seeded no-op-safe op on a scratch roster branch and refuses a seeded lint failure, with the seat running beside it for one cycle.

Carry: R10-ORCH-LEDGER

Carry 14: STRANDED CARRY 12 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-DISPATCH-REG, index 5; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: yes.

Why stranded: #2865 item [5] "Not built here: the beat and its job table are R10-ORCH-BEATD's"; BEATD done arm (a) only; BEATD carries [28]/[32] stranded with it.

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
Orchestrator ruling 2026-10-24 (tvofi card 1): the dispatch half of standing-dispatch.md (open_pr and update_pr, bus dispatch, pool briefs and verdict confirm) becomes a beat job owned by this group's registry. It never moves into the orchestrator's turns. The standing dispatch seat stays until that job has run beside it for one full cycle.

Carry: R10-ORCH-LEDGER

Carry 15: STRANDED CARRY 47 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 28; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: R10-ORCH-BEATD done at #2916 with arm (a) only (#2916 body: "The (b) and (c) carries stay on the roster group"); design/R10-ORCH-BEATD 32e249d2 sections 3-4 scope arms (b) and (c); #2865 body item [5]: "Not built here: the beat and its job table are R10-ORCH-BEATD's"; no bus.sh dispatch-owed (design arm (c)); no live owner.

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
From R10-ORCH-DISPATCH-REG (handoff de66f00b): **The dispatch half of standing-dispatch.md becomes a beat job owned by this registry.** Not built here: the beat and its job table are R10-ORCH-BEATD's (concern B), which is after this group. What it needs from here exists: one writer (`bus.sh dispatch`), a registry with time and model, a reopen on a failed publish. The standing dispatch seat stays until the job has run beside it for one full cycle.

Carry: R10-ORCH-LEDGER

Carry 16: STRANDED CARRY 49 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 32; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: R10-ORCH-BEATD done at #2916 with arm (a) only (#2916 body: "The (b) and (c) carries stay on the roster group"); design/R10-ORCH-BEATD 32e249d2 sections 3-4 scope arms (b) and (c); #2865 body item [5]: "Not built here: the beat and its job table are R10-ORCH-BEATD's"; no bus.sh dispatch-owed (design arm (c)); no live owner.

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
**R10-ORCH-BEATD: carry [5], the dispatch beat job.** It calls `bus.sh dispatch` (or `dispatch_group`), never a second writer of the registry or of the `reviewer-fire` close; the standing dispatch seat stays until the job has run beside it for one full cycle. Control: one beat pass over a handoff with no live dispatch leaves one registry line and one `close reviewer-fire` in `events.tsv`, and a second pass adds neither. Carry: R10-ORCH-BEATD

Carry: R10-ORCH-LEDGER

Carry 17: STRANDED CARRY 41 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 14; triage id: dev/programme/triage/s6-batch2.md#P45; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: R10-ORCH-BEATD done at #2916 with arm (a) only (#2916 body: "The (b) and (c) carries stay on the roster group"); design/R10-ORCH-BEATD 32e249d2 sections 3-4 scope arms (b) and (c); sweep_template.md steps still have the orchestrator start work (step (3) launches merge_train.py sweep, sweep_template.md:61); design arm (c) section 5 "23 rewrites" is this; no live owner (FLY-SEAT-ALIVE-ID edits only step (1b)/(2)/(5)).

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
Standing-seat wiring, item 1 (triage: dev/programme/triage/s6-batch2.md#P45, merged at d2dcfed15a0c9d0bb4934f4b29cd95dbe04bbf44). Adds tools/audit/seat/sweep_template.md to the group's files. sweep_template.md steps (2), (3), (4) and (6) tell the orchestrator to do inline what decision 0015 and the owner (2026-10-23T19:42Z) give to the standing seats; rewrite each to queue a line to its seat and read its report. Control: the rendered sweep names no train launch for the orchestrator; one mutant. Policy files: the owner approves the merge.

Carry: R10-ORCH-LEDGER

Carry 18: From R10-ORCH-REVIEW-PACKET carry 12 (lever L5, #201 comment 6527969942): "Measure before and after: count the mechanical block classes over the next 10 verdicts; no improvement means revert." The count runs after #3061 (fix/r10-orch-review-packet-2, open) merges, when R10-ORCH-REVIEW-PACKET goes done, so no live group owns it. R10-FLOW-BOARD, the flow-measurement group, is being set done by the s9 carry-routing queue. Measured: the baseline is in that carry and in carry 15 (35 of 68 blocked verdicts mechanical over round 10; 34 of 80 blocked over 253 verdicts since 2026-10-30T07Z). Fix: once #3061 merges, take the next 10 fix-review verdicts after its merge commit, classify each blocked one by the same mechanical classes (carry missing, CI red, body stale, figure, head-moved, other), post the before/after table on #201, and, if the mechanical share does not fall, open the revert of #3061's dispatch refusal as this group's change. Failing test first: none (this is a measurement); the classification is scripted from verdict comments so a re-run reproduces it. Null control: classify the 10 verdicts before #3061's merge with the same script; it must reproduce the carry's baseline share within one verdict. Carry: R10-FLY-STANDING-CONTRACTS

Carry 19: Owner order (tvofi, 2026-11-01, verbatim: "Make sure judging and folding every useful standing loop into the orchestrator machinery on main is planned in the roster, including describing the hooks and a script to set them up if they are not there"). Widens STEP 1 and STEP 2 of this group's brief; the design (design/R10-FLY-STANDING-CONTRACTS) carries it.

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

Carry 20: Re-routed by orchestrator s9 (tvofi 2026-10-31: "The tick seat is planned to be replaced by a script within the sweep, verify that that is planned in the roster"). R10-ORCH-BEATD carry 10 (tvofi 2026-10-24 card 1, owner accepted) was closed unbuilt when BEATD went done at #2916 with arm (a) only, and no live group carried it.
The carry: retire the standing tick seat into the beat. The beat's tick job writes a digest file of the board's actionable family, and the orchestrator reads that digest. Codify the retirement in dev/governance/roles/standing-tick.md and the standing-seats paragraph of dev/governance/roles/orchestrator.md section 5, both policy that the owner approves at merge. That edit reverses the 2026-10-23 ruling for the tick seat only; proposal triage stays an LLM seat.
Binding constraint (tvofi 2026-10-24, verbatim): 'make sure the retirement of the standing seats dont cause you to run things inline'. The seat's work moves to a daemon or beat job, never into the orchestrator's turns.
Local stand-in, live since 2026-10-31T19:32Z: ~/hpo-orch/r10s6/s9/tick-digest/the tick-digest script (out of tree; read it as the reference shape, never cite its path in the tree). Every 240 s, on a changed tick.txt, it greps the actionable family (OWED, DISPATCH, OWNER FLAG, BLOCKED-UNFIXED, DESIGN-BUILD, UNREADABLE, DESIGN OWED, REVIEW OWED, REVIEW STALLED, UNLEVELLED, APPROVAL*, MERGE-READY, code-owned-without-review, NOT REVIEWABLE, DIRTY, RED unanswered, main red) and normalises timestamps and ages. It writes digest.txt, new.txt and gone.txt, runs owed_unactioned.py (UNACTIONED lines into new.txt), and touches the tick seat's alive file. The orchestrator's background until-loop wakes only when new.stamp changes.
Build: a `tick-digest` job in the beatd job table beside this group's heartbeat and pitch jobs, either as a tools/audit/seat/ script or as an orchestrator_tick.py `--digest` mode. Write it under $HPO_STATE_DIR, with the sweep template's step (5) reading the digest in place of the tick seat. Remove tick_brief from the placeholder table, or make it optional.
Controls: an unchanged board writes no new.txt (null); a board gaining one OWED line writes exactly that line; a timestamp-only change writes nothing; an UNACTIONED exit from owed_unactioned.py lands in new.txt. Carry: R10-ORCH-LEDGER

Carry 21: Owner direction (tvofi, 2026-10-31, verbatim: "consider if all of the seats and their tasks are necessary LLM tasks. For example, state docs could go in your sweep script"). Orchestrator s9's classification: tick, roster drain, opener relay, record beat (replan + state_docs --plan), pulse, cancel_superseded sweep and the disk check are mechanical. Dispatch briefs and triage rulings need judgement, and merge does once #3054 (closing-stage field) and R10-FLY-TRAIN-DEFAULTS part 2 land.
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

Carry 22: STRANDED CARRY 43 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 18; triage id: dev/programme/triage/s6-batch5.md#P63; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: P63 generation token: no tools/audit/seat/seat_gen.py on main; R10-FLY-SEAT-ALIVE-ID brief says "Not in scope: P63's generation token (stranded on R10-ORCH-BEATD; the orchestrator re-routes or drops it)".

Fold into: R10-FLY-SEAT-ALIVE-ID (live). Owner of the standing-seat identity and liveness seam (pulse.py, sweep_template.md).

Original text, verbatim:
Single writer per standing seat (triage: dev/programme/triage/s6-batch5.md#P63, S6-V4, third instance: roster w5/w6, #2698 fixer vs update, dispatch w14/w15). A generation token, not a kill helper. tools/audit/seat/seat_gen.py: `bump <seat>` writes <orch>/<seat>.gen (monotonic integer + epoch) and prints it, run by the orchestrator when it starts a replacement; `check <seat> <gen>` exits 1 and prints SUPERSEDED when the file holds a higher number. The tracked code that applies a seat's queue lines (roster apply, dispatch fire, merge_train queue read) calls `check` with the generation its seat prompt carries before each write and stops on SUPERSEDED, so a superseded seat's lingering background job cannot write. The tick flags a seat whose .gen moved while its old pass still touches the report file. Measure first: which tracked writers exist per standing seat at main; wire only those. Controls: a lower-generation check exits 1 (null control: the current generation exits 0); a writer given a superseded generation writes nothing; one mutant on the comparison. Out of scope: killing the old task (TaskStop is an agent tool, not scriptable from a shell).

Carry: R10-FLY-SEAT-ALIVE-ID

Carry 23: STRANDED CARRY 51 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 35; triage id: dev/programme/triage/s6-batch48.md#P236; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: P236: no session lock at origin/main (`git grep -i "session.*lock"` over tools/audit/seat/*.py and sweep_template.md empty); live grep "P236" empty.

Fold into: R10-FLY-SEAT-ALIVE-ID (live). Owner of the standing-seat identity and liveness seam (pulse.py, sweep_template.md).

Original text, verbatim:
From triage P236 (V150, orchestrator s10, 2026-10-28): extend this group's single-instance lock to the orchestrator session itself. On resume, before its first dispatch, the session takes a lock record holding its own long-lived pid (the session binary, never the calling shell's $PPID, which dies with the call) and its start time. A second session that finds the lock held by a live pid whose command is the session binary refuses to dispatch, logs both pids, and stops; a holder pid that is gone, or names another command, is stale and is taken over. Liveness is read from the pid (`ps -p <pid> -o command=`), never from stop lines, because a reboot leaves none. The in-tree resume steps (`tools/audit/seat/handover_prompt.py` "Resume steps", `tools/audit/seat/sweep_template.md`) name the step; `handover_prompt.py` is not in this group's files (edit-brief is the roster seat's call). Self-test: a live other holder refuses; null controls: a dead holder pid and a reused pid naming another command are both taken over, and the session's own pid is not a duplicate. Mutation proof: dropping the command match makes the reused-pid null control refuse. Basis: after the 2026-10-28 ~07:07Z reboot, sessions 10472 (08:16Z) and 21371 (08:19Z) resumed one round; 10472 dispatched seats at ~08:38Z; it was killed on the owner's instruction and nine seats were relaunched at 08:44:41Z. triage: dev/programme/triage/s6-batch48.md#P236

Carry: R10-FLY-SEAT-ALIVE-ID

Carry 24: Folded from R10-SEAT-SINGLE-WRITER into R10-FLY-STANDING-CONTRACTS (shared owning seam; s11 replan). BRIEF: One writer per standing seat and per orchestrator session: a generation token a superseded seat's lingering job checks before it writes, and a session lock keyed on the session binary's own pid that a second resumed session refuses on. Measure first which tracked writers exist per standing seat; wire only those. Stranded on R10-ORCH-BEATD, re-routed through R10-FLY-SEAT-ALIVE-ID, which #3070 closed. Every carry was moved verbatim by the s9 carry-routing pass (2026-11-01) from a carries-open source group; each names its own controls. Re-measure every figure a carry states at this group's own merge base; carry no count. A carry that says it waits on an owner or orchestrator ruling waits for that ruling, and the body says so.

DESIGN APPROVED: refs/heads/design/r10-fly-standing-contracts at 21210036507fd53d3aab69e840bcdd141bc11e75 passed design review, verdict refs/heads/design-verdict/r10-fly-standing-contracts at 2d0ac2c0b53f107a204d19778b9a3f07d7a2d34e (`Design review: approve 21210036507fd53d3aab69e840bcdd141bc11e75`). Build the design's parts serially as it orders them, one commit series per part; read the note and the verdict (VERDICT, including its two Notes for the fixer, items 28 and 29: orchestrator.md sits at zero token headroom under tools/audit/briefs/orchestrator.md in policy_budgets.json, and pulse.py:246 is the DUPLICATE seat line) in full first. The four contracts are policy: the owner approves the merge, say so in the body. Size L, fixer sonnet per the roster; stop and ask rather than raise any budget.
