CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-introduced-reds-barrier, at head 60413046e3903f52c47cf587e9c4131fa30d74fa. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 60413046e3903f52c47cf587e9c4131fa30d74fa for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-introduced-reds-barrier before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-introduced-reds-barrier, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-introduced-reds-barrier, even with no code. Then push the code to refs/heads/handoff/r10-introduced-reds-barrier, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-introduced-reds-barrier <body.md>`, which pushes refs/heads/handoff-body/r10-introduced-reds-barrier; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-introduced-reds-barrier`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-introduced-reds-barrier and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-introduced-reds-barrier and refs/heads/handoff-wip/r10-introduced-reds-barrier-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
Fixer for roster group R10-INTRODUCED-REDS-BARRIER (topic r10-introduced-reds-barrier), size M. Group brief:

triage: dev/programme/triage/s6-batch200.md#P626 at 20439b0372

Class barrier, M, policy. The R10-RCA-PUSHER-CENSUS-ESCAPE root cause was state (d). #3425 merged with governance / instrument-self-tests red at all three of its heads. The 2026-11-07 ruling (234ff52c75) narrowed owed reds to the required set, and that job is not in it. So the body said none, classify printed GREEN, and no reviewer owed an answer. That makes 3 instances in 3.7 days (#3361 once, #3425 twice). Countermeasure C1 is accepted under the owner's mandate (policy scope). It keeps the 11-07 ruling for reds inherited from main and restores the backstop only for reds the PR introduces.

Items:
1. Introduced-red line. The review packet (tools/audit/seat/review_packet.py, beside gate_digest) and the classify command of tools/audit/seat/merge_train.py list each instrument-self-tests step whose conclusion is failure at the PR head and not at the base. Each such step prints as INTRODUCED, and the reviewer blocks on it as a finding of the PR, not as a Red checks answer.
   - The base is the latest concluded run at the PR's merge base. If there is no base run, every head red counts as introduced.
   - Exclude the push-only drift step.
   - A step skipped by scoping is not counted.
   - An unreadable job fails closed.
   - Cost: 2 job-step REST reads per packet, through the existing gh read helper.
   - Self-test arms cover all four cases, and the instrument docs are updated.
2. Correct the comment above the instrument-self-tests job in .github/workflows/governance.yml. It still says pr-contract makes the body answer a red there. Say what holds after item 1.
3. Add a dev/audit/config/bugclasses.json key for the class "a PR merges a non-required self-test red its own diff introduced", recorded as barriered by item 1 and citing this RCA.
4. Policy:
   - In dev/governance/roles/fix-review.md, add one sentence: an introduced instrument-self-tests red is a block.
   - In dev/governance/rules/defect-root-cause.md, beside "Only a red on a required check is owed an answer", add one sentence: such a red is a finding of the PR, and a red inherited from main stays unowed.
   - Regenerate .claude/rules and .cursor/rules with node tools/policy/rules_sync.mjs.
   - This PR is policy. It merges on the mandate approval (the owner's mandate, policy scope), recorded as the approving review.
5. Land the RCA document in dev/audit/rca, its file named by this RCA's id (R10-RCA-PUSHER-CENSUS-ESCAPE) with the markdown suffix. Its source is the root-cause seat's RCA for this class, under the orchestrator's state dir. Name its scratch probe in prose, not as a path.

Acceptance (the finder's harness is the RCA's head-vs-base probe over job step conclusions):
- (a) The built check reports the 4 introduced steps and a nonzero exit for #3425 head c93903f075 (job 130479299736) against main cbd23f1c8b (job 130415622883). The 4 are the sweep template render and the three pr_args census steps.
- (b) Null control: cbd23f1c8b against f24d107bd7 (job 130402966157) reports 0 introduced and passes. Both are red only on the drift step.
- (c) It passes on a fixed head: R10-HOTFIX-PUSHER-CENSUS's merge on main, or that PR's head against its base if it has not merged by the handoff.
- (d) Mutation proof: dropping the base subtraction turns (b) red, and dropping the fail-closed arm passes an unreadable job.

Out of scope: C2 (a prepr census arm), C3, C4 (making instrument-self-tests required; this conflicts with decision 0013's HPO_JOB_GRADES boundary) and C5. The RCA refuses all four.
Overlap admitted, each a distinct seam: R10-GATE-DEFER-BARRIER (gate deferral reds), R10-REVIEW-DISPATCH-RESIDUE (reviewer dispatch), R10-GH-READ-RESIDUE-P3, R10-PROCESS-SLIM (#3451) and R10-HOTFIX-RESTORE-BASE-SKEW (#3463).


Context from the dispatcher: acceptance (c) needs R10-HOTFIX-PUSHER-CENSUS's fixed head. Use the tip of refs/heads/handoff/r10-hotfix-pusher-census once its pull request head exists; at dispatch time that handoff is at 4f2a40a2f2b3 with its body not yet pushed, so say in your hand-off so if (c) could not be measured against a fixed head. This group is classed with the hotfixes (it protects main); its pull request is policy and merges on the mandate approval.
