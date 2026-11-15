CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r11-pre-machinery-limiter, at head 26dbf7c43ec3742101398b098dbdcc61bbee8f19. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 26dbf7c43ec3742101398b098dbdcc61bbee8f19 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r11-pre-machinery-limiter before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r11-pre-machinery-limiter, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r11-pre-machinery-limiter, even with no code. Then push the code to refs/heads/handoff/r11-pre-machinery-limiter, then write the PR body and run `bash tools/audit/seat/body_push.sh r11-pre-machinery-limiter <body.md>`, which pushes refs/heads/handoff-body/r11-pre-machinery-limiter; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r11-pre-machinery-limiter`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r11-pre-machinery-limiter and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r11-pre-machinery-limiter and refs/heads/handoff-wip/r11-pre-machinery-limiter-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
Owner ruling 2026-11-13 on decision card P2 (declining cap, one in one out, severity route narrowed): the machinery ratchet becomes a target that declines over a round instead of a record of the status quo; a new gate enters only when one leaves; and a machinery proposal may skip the cost-benefit bar on severity only for a red required check on main or a blocked production pull request. Evidence: the process convergence audit at commit d5d7ff81878fe9bc17ee6fcc9e3803d848cbc7f7 on the ref handoff-wip/r10-process-convergence-audit, section 6 row a2. Policy pull request for the owner s review; state the schedule and its enumerator. Must merge before round 11 finders start.

After: none

Carry 0: Owner statement 2026-11-13 on the round 11 instrument freeze (card P11), his words: "Under the round 11 instrument freeze, my intension is that all instrument fixes should be done locally, all proposals consolidated and triaged at round end, and those with good cost/benefit fixed in the beginning of round 12". The policy this group writes states that shape for every round from 11 on: during a round an instrument fault is worked around locally by the orchestrator or a seat (the workaround recorded with its id, onset and cost each time it is used); the permanent fix is written as a numbered proposal and is not built during the round; at the round s end all proposals are consolidated (duplicates merged, each with its measured occurrences and cost from the workaround records) and triaged once against the cost-benefit bar; the accepted ones are built at the start of the next round, before its finders, and the rest are refused with their numbers. State the exceptions exactly as the owner ruled them on card P11 (production defects, owner orders, a red required check on main) and what a local workaround may never do (change production code, loosen a gate or a budget, skip a review).

Carry 1: Owner instruction 2026-11-13, his words: "Make sure the future rounds can use the audit playbook even with the addition of the objective function and the improved audit dimension. It should also make the round orchestrator pick up the carries and pre-finder carries from the previous round. Also, related to scope during a round, outside and owner filed findings and requests should always fold into the ongoing round if not explicitly deferred by the owner or outsider". For the freeze policy this group writes (card P11): the exceptions to the freeze are production defects, owner orders, a red required check on main, and every finding or request filed by the owner or by an outside user, which folds into the ongoing round unless the owner or that outside user explicitly defers it. This replaces the 2026-11-12 handling that sent non-critical outside items to the next round when they moved closure. State how a deferral is recorded (who, when, their words) and that silence is never a deferral.

Carry 2: Owner ruling 2026-11-13 (tvofi, verbatim: "This should be the shape for instrument fixes, prototype local fixes in-round, file proposal permanent fixes for consolidation and cost/benefit that is carried to the start of next round"): the freeze policy this group writes states this as the shape for every round. In the round, an instrument fix is a local prototype (out of tree, kept runnable, named in the proposal); its permanent form is filed as a proposal citing the prototype and its measured effect; proposals are consolidated and cost/benefit-triaged once, at round end; the accepted ones are carried to the start of the next round and built before its finders. The exceptions are the freeze s own (a red required check on main, production defects, owner orders, owner and outside items). State where the proposals file and the prototypes live so the next orchestrator finds them from the playbook.

Carry 3: Moved from R11-INTAKE-R10-RESIDUE carry 15 (0-based at roster f6ff22c373) by the round-10 round-end triage (triage: dev/programme/triage/r10-round-end.md#P742 at 2e17928032; ratified by tvofi 2026-11-15). Text verbatim:

Moved from R10-CLOSEOUT-PREP carry 2 (0-based) by the orchestrator s14 carry triage 2026-11-13 under the owner's 2026-11-12 ruling (self-fed work that moves closure goes to round 11). Text verbatim:

MACHINERY-CAPS-RECORD-DOWN (triage: dev/programme/triage/s6-batch218.md#P663 at bb3a0e5b92), line numbers at 61afd4f2db. `python3 tools/audit/machinery_ratchet.py --measure --head origin/main` read nonproduction_merges 498 at 61afd4f2db, against a cap of 521 with a band of 5 in dev/governance/config/machinery_budgets.json. That is more than the band below, and the file's `_comment` says to "re-record a cap down when the measurement falls more than its band below it". churn_per_kilo_product_lines read 12299 against 14797 with a band of 3636, within the band. At this group's merge base, re-measure both, record down every cap that sits more than its band above the measurement, and update `_recorded` with the command and the sha. Record the measured value only, never a target, because a later raise needs tvofi's review (budget-raise-gate). A cap within its band stays. Check: the same command reads within the band below each cap. Carry no count from here; re-measure.

Carry 4: Moved from R11-INTAKE-R10-RESIDUE carry 22 (0-based at roster f6ff22c373) by the round-10 round-end triage (triage: dev/programme/triage/r10-round-end.md#P742 at 2e17928032; ratified by tvofi 2026-11-15). Text verbatim:

Moved from R10-ROUND-PLAYBOOK-FINAL carry 17 (0-based) by the orchestrator s14 carry triage 2026-11-13 under the owner's 2026-11-12 ruling (self-fed work that moves closure goes to round 11). Text verbatim:

Brief carry 20's code half: `pr_cap.py` reserving production slots and printing open PRs by class on every tick. The README states the rule. Carry: R10-ROUND-PLAYBOOK-FINAL

Carry 5: Moved from R11-INTAKE-R10-RESIDUE carry 23 (0-based at roster f6ff22c373) by the round-10 round-end triage (triage: dev/programme/triage/r10-round-end.md#P742 at 2e17928032; ratified by tvofi 2026-11-15). Text verbatim:

Moved from R10-ROUND-PLAYBOOK-FINAL carry 25 (0-based) by the orchestrator s14 carry triage 2026-11-13 under the owner's 2026-11-12 ruling (self-fed work that moves closure goes to round 11). Text verbatim:

`policy_budgets.json`: stale: the README's caps are keyed `tools/audit/README.md`, a path the tree no longer has, and are matched through the move map. A reader grepping the new path finds no cap. Carry: R10-ROUND-PLAYBOOK-FINAL

Carry 6: Moved from R11-INTAKE-R10-RESIDUE carry 41 (0-based at roster f6ff22c373) by the round-10 round-end triage (triage: dev/programme/triage/r10-round-end.md#P742 at 2e17928032; ratified by tvofi 2026-11-15). Text verbatim:

From r10-round-playbook-final-p2, body item 9502b215: The README cites the census directory, not its CENSUS.md file: policy_lint's named-docs check refuses a named file with no cap or exclusion, and dev/governance/config/corpus_excluded.json is outside this part's files. The brief asked for the file path. Carry: R11-INTAKE-R10-RESIDUE (items 9502b215)

Carry 7: Loop-study card L2 (owner: yes; card O2: its policy text is approved under the mandate if sound), routed here by the round-10 round-end triage (triage: dev/programme/triage/r10-round-end.md#P742 at 2e17928032; ratified by tvofi 2026-11-15). Re-measure every figure at this group's own base. Source text, verbatim:

**L2. Order of countermeasures: delete, then self-repair, then narrow, and a new refusal last.**
- **Change:** `root-cause.md` section 5 and `proposal-triage.md` require a countermeasure to state why each earlier rung is not possible before proposing a later one. A new refusal prints its own repair command. It also shows its refusal count on the last 20 healthy heads (a shadow run) before it gates anything.
- **Evidence:** 48 of 76 analyses add or widen a detector and 21 heal, delete or narrow. 45 of 51 machinery hotfixes are repeats, most of them over-refusals. Refusal words tripled.
- **Effect on k:** lowers D x p, the use-driven inflow, and h for new checks.
- **Cost:** two policy paragraphs; a shadow run per new refusal.
- **Risk:** a real defect class left undetected. Mitigation: product checks are exempt from the ordering.
- **Replaces:** nothing. **Touches:** `mechanise-before-policy` (10-24) stays, read as repair before refuse.

Carry 8: Loop-study card L4 (owner: yes; card O2: its policy text is approved under the mandate if sound), routed here by the round-10 round-end triage (triage: dev/programme/triage/r10-round-end.md#P742 at 2e17928032; ratified by tvofi 2026-11-15). Re-measure every figure at this group's own base. Source text, verbatim:

**L4. Price induced work in the cost test.**
- **Change:** `defect-root-cause.md` and `proposal-triage.md` add two terms to the cost side. One is expected follow-up items: the instrument's own measured offspring rate from L1, times the mean cost of an item. The other is the number of generated artifacts or pins the change stales in open branches. Until L1 has a round of data, use this round's figures: 2.9 follow-up items per RCA and 0.22 hotfixes per machinery merge.
- **Evidence:** 67 of 76 analyses carry a numeric cost test and 51 of 76 are repeats; none priced its follow-ups.
- **Effect on k:** lowers a for changes to instruments that breed.
- **Cost:** two sentences and one lookup.
- **Risk:** a needed fix priced out. Mitigation: the existing exceptions (red required check on main, production defect, owner order).
- **Replaces:** the "standing seconds only" reading. **Touches:** sharpens the 20% bar; does not change it.

Carry 9: Loop-study card L5 (owner: yes; card O2: its policy text is approved under the mandate if sound), routed here by the round-10 round-end triage (triage: dev/programme/triage/r10-round-end.md#P742 at 2e17928032; ratified by tvofi 2026-11-15). Re-measure every figure at this group's own base. Source text, verbatim:

**L5. Triage by instrument, not by proposal; the third accepted change to one instrument in a round owes a redesign decision.**
- **Change:** at the round-end consolidation the triage seat groups proposals by the instrument they name and rules once per instrument: retire it, simplify it, redesign it (a designer note), or leave it. A fourth patch is not an option.
- **Evidence:** `merge_train.py` took 58 accepted proposals. 169 accepted proposals hit an instrument with ten or more earlier accepts. The gate-deferral analysis is titled "the producer of a deferral was fixed three times, its reader never".
- **Effect on k:** replaces many small changes, each with offspring 0.3 to 0.5, by one designed change.
- **Cost:** a designer seat for perhaps six instruments at round end.
- **Risk:** a redesign larger than the patches; #3315 was one such. Mitigation: L6's reversal, and promotion one change at a time.
- **Replaces:** per-proposal rulings for instruments past the threshold. **Touches:** gives the 11-13 freeze shape its unit of consolidation.

Carry 10: Loop-study card L7 (owner: yes; card O2: its policy text is approved under the mandate if sound), routed here by the round-10 round-end triage (triage: dev/programme/triage/r10-round-end.md#P742 at 2e17928032; ratified by tvofi 2026-11-15). Re-measure every figure at this group's own base. Source text, verbatim:

**L7. A kill criterion for the loops.**
- **Change:** two thresholds read from the L1 enumerator each week: k at or above 0.8, or machinery-own hotfixes above 15% of code merges. When either holds for two consecutive weeks, RCA seats record cause and state only and build nothing, and proposals are logged only, until the next round start. The owner sets the numbers.
- **Evidence:** k was 0.76, 0.74, 0.71 and 0.95 in w2 to w5, and the hotfix share 20% then 30%, with no rule responding until the owner's ruling on day 30.
- **Effect on k:** a ceiling.
- **Cost:** two lines in the round playbook.
- **Risk:** a real barrier delayed by a round. Mitigation: product defects and barriers for product classes are exempt.
- **Replaces:** nothing; it is the backstop once the freeze lifts. **Touches:** `audit-class-barrier`, for machinery classes only.

Carry 11: Loop-study card L8 (owner: yes; card O2: its policy text is approved under the mandate if sound), routed here by the round-10 round-end triage (triage: dev/programme/triage/r10-round-end.md#P742 at 2e17928032; ratified by tvofi 2026-11-15). Re-measure every figure at this group's own base. Source text, verbatim:

**L8. Root-cause analysis of machinery friction by family at round end; per defect only for the product and for outages.**
- **Change:** a product defect, a release defect or an outage keeps its own RCA seat at once. Repeated machinery friction is counted during the round (family and occurrences, by L1) and analysed once per family at round end, feeding L5.
- **Evidence:** 67 of 76 analyses were about machinery and 42 were triggered by recurring friction. Each produced 2.9 follow-up items. The friction family alone has at least seven analyses.
- **Effect on k:** removes the largest generator of follow-up items and gives the analysis the whole family at once.
- **Cost:** negative; fewer seats.
- **Risk:** a machinery cause forgotten by round end. Mitigation: the count is mechanical and the family list is the triage input.
- **Replaces:** per-event RCA seats for machinery friction. **Touches:** the owner's "RCA dispatch immediately" ruling and the third-instance rule, for machinery only. This card reverses part of a standing ruling.

Carry 12: Finder-start condition (a) and the pickup commands (policy, `dev/audit/README.md`, by this group's policy pull request or the next playbook edit), routed here by the round-10 round-end triage (triage: dev/programme/triage/r10-round-end.md#P795 at 2e17928032; ratified by tvofi 2026-11-15). Re-measure every figure at this group's own base. Source text, verbatim:

Condition (a) reads: every line the two pickup commands print, run against `origin/handoff/audit-r<N>-roster`, has a disposition: a stage the round schedules (`not-started`, `design`, `in-progress`, `carries-open` with a named next step), `done` or `refused`; `deferred` is not a disposition at a round start. `carry_audit.py` gains `--roster-ref origin/handoff/audit-r<N>-roster` and the one-liner reads `git show <ref>:dev/programme/rosters/wave-r<N>-groups.json`. (The batch's own words, entry P795.)

Part 1 of 3: build carries 0-4; the others are later parts dispatched at this part's handoff; answer none of them
