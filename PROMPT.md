CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-friction-records, at head 7e8939d38cedb2976acc80a4ad7875cb545bd588. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name seat && git config user.email seat@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 7e8939d38cedb2976acc80a4ad7875cb545bd588 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-friction-records before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-friction-records, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-friction-records, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-friction-records <body.md>`, which pushes refs/heads/handoff-body/r10-friction-records; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-friction-records`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-friction-records and refs/heads/handoff-wip/r10-friction-records-body. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
Root-cause records for the recurring-friction keys R10-FRICTION-REGRESSION left owed (its PR #3000 landed the #2860 record only), plus two record items stranded on done groups. One root-cause seat, one pull request, one record per key under dev/audit/rca/, each with its named cause, process state, cost test with numbers, and a countermeasure or a recorded refusal (dev/governance/roles/root-cause.md, dev/governance/rules/defect-root-cause.md). Records already present for some keys (R10-RCA-MUTATION-SURVIVOR.md, R10-FRICTION-GATE-SCOPING.md, R10-RCA-FIXER-MD-KEY.md, R10-RCA-FRICTION-CLAIM-FALSE.md) are judged for sufficiency first, not rewritten. The body carries one Closes line per issue it answers, because a multi-issue Closes line closes only the first; the group's fixes list is empty until the orchestrator wires it. Every carry was moved verbatim by the s9 carry-routing pass (2026-11-01) from a carries-open source group; each names its own controls. Re-measure every figure a carry states at this group's own merge base; carry no count. A carry that says it waits on an owner or orchestrator ruling waits for that ruling, and the body says so.

After: none

Carry 0: From triage P259 (V173, report P4, owner approved the shape change 2026-10-28T17:47Z): this group absorbs R10-FRICTION-MUTATION-SURVIVOR (#2840), R10-FRICTION-GATE-SCOPING (#2835, also dev/governance/rules/gate-scoping.md), R10-FRICTION-FIXER-MD (#2895, also dev/governance/roles/fixer.md) and R10-FRICTION-CLAIM-FALSE (#2907); their briefs are read from their roster entries and carried whole. One root-cause seat, one pull request, five records: each a separate file under dev/audit/rca/ with its own cause, process state, cost test and countermeasure or recorded refusal (root-cause.md, defect-root-cause.md). The body carries one 'Closes #N' line per issue (#2860, #2840, #2835, #2895, #2907): a multi-issue Closes line closes only the first. The reviewer may return a per-file blocked list in one round. POLICY: two records touch gate-scoping.md and fixer.md, so the PR merges only on tvofi's approving review. Sizing: five S records on one S entry; the work is M-sized. triage: dev/programme/triage/s6-batch52.md#P259

Carry 1: Two further verdict-class recurring-friction keys filed by the governance cron belong to this root-cause seat (orchestrator routing 2026-10-29, owner request): #2875 root-cause-detectable and #2950 class-open. Same product per key as the brief's: named cause, process state (a-d), cost test with numbers, countermeasure or recorded refusal, re-derived at your merge base with node tools/policy/policy_lint.mjs --stats --since v7.0.4.

Carry 2: Land the drafted countermeasures of dev/audit/rca/R10-RCA-FRICTION-RESIDUE.md (#2896) that are policy tooling. tvofi approved them on 2026-10-29, verbatim: "All of these are approved." (1) #2436, section 4: a derived `other (untaught)` family in policy_lint's statsFamilies (every histogram key not in VERDICT_CLASSES, members computed at read time, the #2410 subtraction applied); control: every taught row prints byte-identically, and a window with no untaught word prints no row. (2) #2437, section 5: declare the `root-cause` family {root-cause-unanswered, root-cause-detectable, root-cause-unrecorded}; control as recorded there (union 6 PRs, family 3 after subtraction). (3) #2429, section 7: in ci-autofix.md, a bound on the wait (if mutation-pins has not concluded by the next tests / mutation conclusion, the pin is owed by the handoff and the body says unmeasured), and a body says pinned only when --pin-killed ran on this head. Re-measure each demonstration at your merge base with node tools/policy/policy_lint.mjs --stats --since v7.0.4; the record's figures are snapshots. Policy edits obey the caps in dev/governance/config/policy_budgets.json (ratchet-budgets.md). Closes #2436, #2437 and #2429 when landed.

Carry 3: STRANDED CARRY 7 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FRICTION-MUTATION-SURVIVOR, index 1; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: yes.

Why stranded: #2961 answers #2840 (mutation-survivor) only; #2942 (mutation family) open and listed only by this closed group; the carry asked for the same-cause-or-new answer.

Fold into: R10-FLY-LEDGER-SAMPLE (live). #2961 carried the loud-survivor countermeasure there; #2942 is the same mutation family.

Original text, verbatim:
Issue #2942, the recurring-friction key mutation (family), refiled by the governance cron after #2410 closed with R10-RCA-FRICTION-RESIDUE (#2896), belongs to this seat beside #2840 (orchestrator routing 2026-10-29, owner request). Read dev/audit/rca/R10-RCA-FRICTION-RESIDUE.md first: state whether the refiling is the same cause (then the countermeasure there failed: process state c) or a new one, and answer it in this group's record.

Carry: R10-FLY-LEDGER-SAMPLE

Carry 4: STRANDED CARRY 46 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 26; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: dev/audit/rca/R10-RCA-ORCH-CONTINUITY.md records no FLOW-ANDON cost test (`git grep -i andon origin/main -- dev/audit/rca/` empty); no live owner.

Fold into: R10-ORCH-LEDGER (live). It holds the beat jobs by K17 (carry[1] item (1)) and the tick-seat retirement re-routed from BEATD carry 10 (carry[22]); one owner of the beatd job table. Alternative the orchestrator may take: reopen R10-ORCH-BEATD (set-stage carries-open), which holds the approved design for arms (b) and (c).

Original text, verbatim:
From R10-RCA-ORCH-CONTINUITY (rerouted to R10-ORCH-BEATD, orchestrator ruling 2026-10-26): Lean flow study: R10-FLOW-ANDON (a pushed heartbeat ref and an off-host watcher, 20-minute bound) is a ready countermeasure candidate; run the cost test against it rather than designing a second one, and record the decision.

Carry: R10-ORCH-LEDGER

Carry 5: From #201 comment 6426952359 (orchestrator s7, 2026-10-26: "root-cause seat for prepr running instrument plant self-tests (#2865)"), never routed; re-verified by the s9 residual sweep at origin/main 92588d581 (2026-11-01). The red-check trigger (defect-root-cause.md): #2865 (R10-ORCH-DISPATCH-REG) went red on `governance / instrument-self-tests` (run 40368808901, job 121733907279: `FAIL T3_review_owed_silent: anchor occurs once in tools/audit/seat/orchestrator_tick.py`) because an edit to a planted file moved a seat mutant's anchor; the body named the cheaper detector (`python3 tools/audit/seat/r10_ledger_mutants.py --self-test`, about 2 s) and process state (a), and the fix review dismissed the countermeasure to the orchestrator's root-cause routing, which never happened. Measured at main: governance.yml's instrument-self-tests runs r10_roster_ops_mutants, r10_stamp_round_mutants, r10_ledger_mutants and r10_mandate_guard_mutants --self-test (lines 767-796); tools/pr/prepr.sh calls none of them, and tools/pr/ci_predict.py's `instrument` arm predicts only selftest_wiring.py --check and ref_privacy.py --check (wiring_preds, privacy_preds). Owed: one root-cause record (cause, process state, cost test with P(recurrence) and defect cost against the ~2 s per run standing cost, countermeasure or recorded refusal). Candidate countermeasure, if the cost test passes: a ci_predict instrument arm that runs each seat mutant self-test whose plant targets a file the diff changes. Failing test first: a planted diff that moves a T3-style anchor in a mutant's target is predicted red. Null control: a diff touching no planted target runs no mutant self-test.

Carry 6: Issue #2998, the recurring-friction key mutation-vacuous (verdict class), refiled by the governance cron after #2660 closed with R10-RCA-FRICTION-RESIDUE (#2896) (orphan-issue disposition, orchestrator s9, 2026-11-01). Belongs to this root-cause seat beside #2875 and #2950.

From: #2998 (governance cron, window v7.0.5..origin/main); prior record dev/audit/rca/R10-RCA-FRICTION-RESIDUE.md section 6, which recorded #2660 as "held: 7/8 before 662a380, 1/1 after"; dev/audit/rca/R10-RCA-MUTATION-SURVIVOR.md (#2961), which refused building anything for tools/ hand mutants on two instances.

Measured at origin/main 92588d581 (2026-11-01): `node tools/policy/policy_lint.mjs --stats --since v7.0.5` reads mutation-vacuous 10 PRs / 12 entries (threshold 3); `--since v7.1.0` reads 4 / 6. Every one of the 10 merged after 662a380 (2026-10-25), so section 6's "held" reading over a 5.2-day window does not hold over this one. An independent rescan of each window PR's `Fix review:` first lines reproduces the 10: #2873, #2916, #2919, #2920, #2937, #2968, #2978, #3004, #3016, #3042. Six of the ten (#2916, #2920, #2937, #2978, #3004, #3042) change no file under custom_components/: their surviving mutants are reviewer hand mutants on tools/ self-tests, outside mutation_table.py and mutation-autofix, which is the population R10-RCA-MUTATION-SURVIVOR refused on a 2-PR count. The other four (#2873, #2919, #2968, #3016) change custom_components/.

Owed (dev/governance/roles/root-cause.md): a named cause for each population, a process state (a-d), a cost test with numbers, and a countermeasure or a recorded refusal, under dev/audit/rca/. State whether #2660's countermeasure (662a380, fixer.md wording) failed (state c) or whether this is a new cause. For the custom_components/ four: countermeasure C (mutation-autofix reddens on a site left alive, #3059 merged 42b23e493 on 2026-11-01) is in force from that SHA; count only entries on heads pushed after it before crediting or refusing it. For the tools/ six: the earlier refusal's cost test priced 2 PRs; re-price it at 6.

Failing test first (if a check-shaped countermeasure is built): it is red on one of the six window instances' reviewed head with the reviewer's surviving mutant applied, and green on its merged head (defect-root-cause.md's demonstration).

Null control: the same rescan over a class with no instance in the window (e.g. `version`) must count 0, and the rescan must equal policy_lint's figure (10/12 here). A countermeasure is credited only on a window starting after it lands.

Re-measure at your merge base: the figures above are a snapshot at 92588d581. Moved from R10-FRICTION-REGRESSION (done, #3000 delivered only the #2860 record) by orchestrator s10, 2026-11-01: verified NOT-DELIVERED, no root-cause record for the mutation-vacuous key exists under dev/audit/rca/.

Carry 7: STRANDED CARRY 24 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-FLOW-JIDOKA, index 21; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: #2853 Forward-carry: "Carry 22, the gate-scoping friction measurement. Not taken"; #2835 open.

Fold into: R10-PREPR-CAP (live). Owner of tools/pr/prepr.sh among live groups (the only other is R10-FLY-NO-FOOTERS); PR #3051 is open, so this rides its next PR, not #3051.

Original text, verbatim:
Measure first (#2835, main ruling under mandate 6329234399, 2026-10-26): recurring friction on .claude/rules/gate-scoping.md across 6 distinct PRs over v7.0.4..main. Name the 6 PRs and the rule hit each made (`node tools/policy/policy_lint.mjs --stats --since v7.0.4`, with a token), then decide whether the keying rule or the gate changes. Fix the cause in this group or record a decision not to, with the numbers. Part of #2835.

Carry: R10-PREPR-CAP


IDENTITY AND PATHS: use repo-relative paths only; no host paths in any file, commit or body. RESTART NOTE: push handoff-wip after every green step, and never end a turn on a background job without a Monitor armed.

Before any commit run: git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com. Never commit as 'seat'.


TIME: you have hours, not minutes. A gate, prepr or recording may run an hour: wait with Monitor windows of up to 60 min and re-arm them. Never end the session waiting on a choice: take the option that keeps coverage and the architecture sound, say so in the body, and go on. Push handoff-wip at each milestone, so your liveness can be read. If truly blocked, push BLOCKED.md on handoff-wip naming the question.
