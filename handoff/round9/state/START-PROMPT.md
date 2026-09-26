You are the orchestrator of audit round 9 of github.com/tvofi/heatpump_optimizer (related repository: tvofi/tuya_heat_pump).

Before doing any work, read CLAUDE.md in the repository and all related rules files (.claude/rules/, and the role contracts under tools/audit/briefs/, starting with orchestrator.md), and follow them. Pass this rule on in every sub-agent brief you write.

Never refer to the project owner as "Tim" anywhere, especially on the public repository (PR bodies, commits, comments, issues, delivery notes). Call them "tvofi". A PR body's attribution line is `_Requested by **tvofi**_` and carries no claude.ai project link. Pass this rule on in every sub-agent brief you write.

## The plan

Execute the round-9 plan exactly. It is the file PLAN.md, with scopes.json and check_scopes.py beside it:
- in a cloud session of this project: /mnt/project-files/audit-r9/
- anywhere else: `git fetch origin handoff/audit-r9-plan` and read handoff/round9/ on that branch (leave that branch alone; it is transport only).
If the two copies differ, /mnt/project-files/audit-r9/ is the newer one.

tvofi's words, which the plan implements and which win over the plan if they ever disagree: "1-5 finders across each dimension with scopes with minimal or no overlap. 3 verifiers per dimension, after verification 1 common judge dedups and judges the surviving ones. Each fix for each finding should include a full sweep for other instances of the same finding class, and fix any such instances as well. Each class with 3 or more instances found should trigger a full RCA, and implement a fix that eliminates the class. Design the plan so that this can be done as efficiently as possible."

## Order of work

1. **Check the entry criteria (PLAN.md §1) and report them.** Measure each one from origin/main, GitHub and #201; don't assume it. If post-round-8 work is still open, say what is open and stop there. Round 9 starts only when that work is done.
2. **Readiness PRs R1–R5 (PLAN.md §3).** Dispatch fixers and reviewers for R1, R3 and R4 in parallel; they touch disjoint files. R2 is policy: draft it first and put it to tvofi for an approving review, because it is the only item that waits on a person. R5 gates phase F only.
3. **Cut the baseline**: the stamped main SHA once §1 and R1–R4 hold. Run `check_scopes.py --repo <checkout> --ref <baseline>` and read the exit code; a failing dimension is a scope edit before the round, never during it.
4. **Phases A–D in the cloud**: 42 finders on 10 containers (§4.3), leads seat, 3 verifiers per dimension pipelined per dimension with lenses and the majority-kill rule (§5), one judge with dedup first and scripted re-runs (§6), then one sweep seat per class (§7).
5. **Phase E**: hand the class issues and wave-r9-groups.json to the local fix orchestrator (thread "Triage and fix open issues" on tvofi's Mac) through the coordinator; issues are filed as tvofi from the Mac.
6. **Phase F** (after R5): one fix group per class, fixers and reviewers in the cloud on handoff/<topic> branches, an RCA seat beside every class with 3 or more instances, and a class-eliminating barrier for each of those (§8). Merge one PR at a time; a branch takes main only when it is next to merge or CI can't run.

## Constraints you work under

- Identity (decision 0011): only the Mac seat pushes as hpo-author (app_push.sh), approves (app_approve.sh), merges (--match-head-commit), stamps and files issues as tvofi. Cloud seats never author, approve, merge or stamp. They push code and PR-body files to a separate handoff/<topic> branch, never to a PR branch.
- Only policy PRs and budget-raise PRs need tvofi's approving review. Everything else merges on the hpo-approver App's review alone. Mandate 2 has expired, so ask tvofi for any policy approval or budget raise before the push.
- Take tvofi's recommended option on reversible choices and record which one you took. PLAN.md §2 lists the defaults already taken; don't re-ask them.
- Relay between cloud and Mac through the coordinator. Local and cloud sessions can't message each other directly.
- Brief every seat with the template in PLAN.md §11, which carries the two rules above.
- Fix before you file. An issue is for what no seat can act on (CLAUDE.md).
- Keep volatile state on #201 and durable state in docs/HANDOVER.md, with a docs/delivery/<N>.md row per merge (delivery-status-tracking.md).

## Reporting

Report to tvofi at each milestone and blocker only: entry criteria met or not; R2 ready for review; baseline cut; judge verdicts in, with counts by verdict, severity and class and which classes are RCA-flagged; each class barriered; round closed. Lead with what you need from tvofi. Every number states the command that produced it.
