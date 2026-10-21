"""The flow groups (FLOW-*) and the carries folded into existing groups.

Imported by build_shadow.py. Briefs cite only paths that exist at main 22615537a
and name planned symbols in prose, per .claude/rules/brief-citations.md.
"""

MANDATE = "mandated approval under 6175172275"
POLICY_GATE = ("Policy: tvofi's approving review before merge (CLAUDE.md); the mandate "
               "6175172275 covers it until 2026-10-28T18:14Z, after which a fresh grant is needed.")
STUDY = "dev/programme/flow-study/STUDY.md"  # on branch claude/dazzling-gauss-7l3u2b, not on main


def model(fixer, reviewer):
    return {"fixer": fixer, "reviewer": reviewer, "rca": None, "runner": "haiku", "record": "sonnet"}


def group(name, kind, size, after, files, hot, brief, carry, fixer="opus", reviewer="opus",
          owner_gate=MANDATE, severity="high", lane="IN", wave=4, effort="medium"):
    return {
        "group": name, "lane": lane, "kind": kind, "class": kind, "issues": [], "fixes": [],
        "findings": [], "severity": severity, "size": size, "wave": wave, "files": files,
        "hot_files": hot, "fixerModel": fixer, "reviewerModel": reviewer,
        "model": model(fixer, reviewer), "effort": effort, "fixture": False,
        "owner_gate": owner_gate, "rca": [], "after": after, "carry": carry,
        "architect_note": "", "brief": brief,
        "resume": {"stage": "not-started", "branch": "handoff/" + name.lower(), "commit": None,
                   "last_step": None, "next_step": "dispatch a fixer once every after group is done",
                   "note": "Lean flow study 2026-10-21 (owner-adopted)"},
    }


GROUPS = [
    group(
        "R10-FLOW-BOARD", "instrument", "S", ["R10-PLAN-ARTIFACT"],
        ["tools/audit/merge_throughput.py", "tools/audit/seat/state_docs.py",
         "tools/audit/seat/INSTRUMENTS.md", ".github/workflows/governance.yml"],
        ["tools/audit/seat/state_docs.py"],
        "Flow board (Lean study K1). Today nothing measures throughput against the owner's demand "
        "of one roster group merged per hour, so no flow change can show it worked. Extend "
        "tools/audit/merge_throughput.py with a flow subcommand rather than adding a file: read the "
        "first-parent log of origin/main, the review and verdict bus refs (tools/audit/seat/bus.sh "
        "publishes one commit per verdict, subject 'verdict: #N Fix review: merge|blocked <sha> "
        "<class>: ...'), and the roster through tools/audit/seat/roster_lib.py. Print per rolling "
        "hour and per 24 h: roster groups closed against takt 1.0; fly-ins closed; main moves split "
        "into group-carrying, record, roster-edit and fly-in; work in progress by flow lane "
        "(A critical path, B product, C process, F fly-in); first-pass yield of fix review and the "
        "blocked-class mix; lead time per size. Add it to tools/audit/seat/state_docs.py's "
        "generator list so the beat publishes it beside the plan table, and print UNAVAILABLE, "
        "never zeros, when a source is unreadable. Wire its self-test into governance.yml's "
        "instrument-self-tests job. Controls: a fixture with one merge, one blocked then merged "
        "verdict and one record merge gives exact counts; a null control (an unchanged fixture) "
        "reads identical before and after; its mutants fail named arms.",
        ["Pre-study: the Lean flow pre-study, section K1 (shadow plan).",
         "Seam: R10-PLAN-ARTIFACT builds the plan page; share its model, do not build a second one."],
        fixer="sonnet", reviewer="opus"),
    group(
        "R10-FLOW-AUTOTRAIN", "instrument", "M", ["R10-FLOW-PULL", "R10-TICK-RELAY-DECOUPLE"],
        ["tools/audit/seat/merge_train.py", "tools/audit/seat/train.sh",
         "tools/audit/seat/tick_loop.sh", "tools/audit/seat/INSTRUMENTS.md"],
        ["tools/audit/seat/merge_train.py"],
        "The merge pitch as a mechanism, not an agent's turn (Lean flow study, mechanisation). "
        "Today the orchestrator builds every train queue by hand: merge_train.py documents the queue "
        "schema in its docstring and nothing writes one, so a pitch happens only when an agent's "
        "turn assembles pull request numbers, verdict heads and comment ids. Every input is already "
        "machine-readable: the confirmed verdict on the verdict bus ref, the pull request's head, "
        "and tools/pr/app_approve.sh --carry, which decides whether a merge verdict on one head "
        "carries to another (only main merges whose tree equals merge-tree's result, or driver-file "
        "bot commits, and an identical branch diff). Add a queue builder to merge_train.py that "
        "writes the queue from the open non-record pull requests whose newest verdict is merge at "
        "the head or carries to it, oldest first, and leaves budget and policy paths to the "
        "serial route the batch admit already applies. Then run tools/audit/seat/queue_pre_flight.py, "
        "then train.sh with --bot-prs --approval-carry --pre-flight, once per pitch, from the tick "
        "loop, and never while a train's pidfile is live. Every merge goes through merge_pr.sh or the "
        "train, which approve (app_approve.sh, or tvofi's review under the mandate on a code-owned path) "
        "before merging; a posted merge verdict is not a GitHub approval. Controls: a fixture with one verdicted "
        "head, one carried head, one head the carry refuses, one blocked verdict and one budget "
        "file builds exactly the expected queue; an empty queue starts no train; a live pidfile "
        "starts none; mutants of each admission rule fail named arms. The first live pitch runs "
        "with the orchestrator watching.",
        ["Pre-study: the Lean flow pre-study, section K10.",
         "Seam: R10-ORCH-MACHINERY's supervised beat later hosts this job; the job is written so "
         "it can move there unchanged."]),
    group(
        "R10-FLOW-POSTMERGE", "instrument", "S", ["R10-ROSTER-OPS"],
        ["tools/audit/seat/merge_pr.sh", "tools/audit/seat/merge_train.py",
         "tools/audit/seat/INSTRUMENTS.md"],
        ["tools/audit/seat/merge_pr.sh"],
        "After-merge bookkeeping without an agent (Lean flow study, mechanisation). nudge.md step 12 "
        "has the orchestrator run four mechanical things after every merge: the worktree "
        "collector, one #201 comment through tools/pr/gh_comment.py with a byte-identical read-back, "
        "the roster stage, and the state docs. merge_pr.sh already runs tools/audit/worktree_gc.sh "
        "and merge_train.py runs it after each merge; nothing runs the other three. Make both merge "
        "paths finish the job: post the #201 line from a fixed template (pull request, merge sha, "
        "group, issues closed by the merge, and the words Leaves #201 open), with the body file "
        "under the state directory, since gh_comment.py refuses a shared root; let R10-ROSTER-OPS's "
        "roster-sync set the stage; and run tools/audit/seat/state_docs.py once with its push flag. "
        "A failure in any of them is printed as OWED and never undoes the merge. Controls: a "
        "dry-run fixture prints the exact comment and commands; a refused comment prints OWED and "
        "exits non-zero after the merge line; each step's deletion fails a named arm.",
        ["Pre-study: the Lean flow pre-study, section K11."],
        fixer="sonnet", reviewer="opus"),
    group(
        "R10-FLOW-BODY-PATCH", "instrument", "S", [],
        ["tools/audit/seat/INSTRUMENTS.md", "tools/pr/app_push.sh"],
        ["tools/pr/app_push.sh"],
        "Repair a pull request's body without moving its head (Lean flow study K14; expedite, it "
        "repairs the line). Ruling R4 forbids moving a clean head, and update_pr.sh merges main on "
        "every run, but no tool PATCHes a body alone: app_push.sh mints, pushes, then PATCHes, and "
        "has no body-only flag. Bodies that pr-contract or carry_audit refuse therefore stay red or "
        "get a head move. (#2560's 111 to 113 figure, cited in revision 3, was not a live case: the "
        "live body already said 113 from the round-3 recount; corrected in revision 4.) Add one seat instrument that "
        "takes a pull request number, the expected head sha and a body file; refuses unless the "
        "live head equals the expected sha; runs the body contract offline at that head (the "
        "policy_lint.mjs --pr-body arm prepr runs, and carry_audit.py check --body); PATCHes the "
        "body as the hpo-author App through the same mint app_push.sh uses, factored out rather "
        "than copied; reads the body back byte-identical; and re-reads the head to show it did not "
        "move. pr-contract re-runs on the edited event. Controls: a fixture where the head moved "
        "refuses before any write; a body the contract refuses is never sent; a dry-run prints the "
        "exact request; mutants for the head check, the contract arm and the read-back. Revision 8: run "
        "only the body contract, never the full prepr (the interim dry run through app_push.sh costs "
        "about 3 min because prepr runs; target under 30 s); and run carry_audit.py with --roster-ref "
        "naming the freshly fetched round roster branch, because an offline check reads the roster from "
        "the worktree and passes a carry that is not on the roster branch, which only fix-review step 10 "
        "would catch.",
        ["Interim, until this lands: app_push.sh run from a clean worktree checked out at the pull "
         "request's exact head, with the corrected body and no new commit, should push nothing and "
         "PATCH the body (read from the code, never yet run). Its first real test is the first "
         "block at an unchanged head whose repair is body-only; at revision 4 that is #2561 "
         "(carry-missing at 1019d18d), unless #2559's merge clears its bad destinations first. "
         "Run --dry-run, then live, and confirm the head sha unchanged.",
         "Pre-study: the Lean flow pre-study, section K14."],
        fixer="sonnet", reviewer="opus"),
    group(
        "R10-FLOW-MAIN-GATE", "instrument", "M", [],
        ["tools/audit/seat/merge_train.py", "tools/audit/seat/INSTRUMENTS.md"],
        ["tools/audit/seat/merge_train.py"],
        "The train's main-green gate tells pending from failed (Lean flow study K15; expedite, it "
        "misleads the operator today). At main e7c66485 on 2026-10-21, 30 checks had concluded and "
        "7 were in flight; the only failures were record and record-autofix, red because the "
        "record beat was owed; yet the --overlap gate logged that main is not green and should be "
        "reverted. Judge main on the latest run of each context only; a queued or in-progress run "
        "is wait, never red; count only the contexts the ruleset main-protect-checks requires, "
        "read live, never record, record-autofix, nightly-status or delivery-status. One owner for "
        "'is main red': share the classifier the open #2570 gives the tick's MAIN section rather "
        "than writing a second. Controls: the e7c66485 shape (pending plus record reds) reads wait "
        "or green, not red; a failed required context reads red; an unreadable ruleset is a "
        "refusal, never green; mutants for each arm. Revision 7 widens it into the one owner of state "
        "classification for the train, the merge seat and the tick: (b) a check-run whose status is "
        "in_progress or queued while its workflow run has completed is stale, not pending: re-run that "
        "run once and re-read (2026-10-21: #2559's budget-raise-gate check-run 119308796140 stayed "
        "in_progress over a completed successful run, mergeStateStatus read BLOCKED, and the merge seat "
        "burned 8 attempts; it recurred on #2567, and one re-run cleared each), applied by merge_pr.sh and "
        "the train before their merge attempt, each instance logged with its run id so a third recurrence "
        "goes to a root-cause seat; (c) a pull request reported DIRTY is classified from git merge-tree "
        "--write-tree origin/main <head>: the conflicted files are named first, and the claimnotes "
        "repair is offered only when every conflicted file is a claim file; a content conflict returns "
        "to the owning fixer and its verdict does not carry (2026-10-21: the tick told #2569 to absorb "
        "main with the claimnotes driver while the conflict was content in roster_edit.py); (d) a head "
        "is reviewable only when no required context's latest run there has concluded failure. If the "
        "fixer has already started on (a), (b) to (d) are its second pull request.",
        ["Sequence after #2570 (the tick's MAIN-section fix) and share its classifier.",
         "Pre-study: the Lean flow pre-study, section K15."]),
    group(
        "R10-FLOW-DISPATCH", "instrument", "S", [],
        ["tools/audit/seat/cloud_dispatch.py", "tools/audit/seat/INSTRUMENTS.md"],
        ["tools/audit/seat/cloud_dispatch.py"],
        "One call per cloud seat (Lean flow study K16; expedite since revision 4: the repo half has no "
        "dependency on any other flow group, and its cost recurs for every seat). Today each cloud seat costs a rendered "
        "payload plus two trigger bodies pasted whole, and the renderer needs environment, model "
        "and repo flags and refuses host paths. Make cloud_dispatch.py take only role, group and "
        "model, derive the rest from the roster and the seat environment it already knows, write "
        "the rendered brief to a ref the seat fetches, and print the one short line the trigger "
        "needs (the ref name), so a standing trigger per role can be fired with that line alone. "
        "Whether the trigger tool can take a file or a ref is the owner's harness, not this repo; "
        "the group builds the repo half. Controls: a fixture dispatch renders the same payload as "
        "today's three-step path, byte for byte; a host path still refuses; the printed line "
        "round-trips to the brief. The dispatcher refuses a reviewer dispatch for a head where a "
        "required context's latest run has concluded failure (revision 7: #2563 was dispatched for "
        "review at 9851d39d with two required checks red), reading R10-FLOW-MAIN-GATE's classifier.",
        ["Owner ruling (R15): the orchestrator drafts the three standing trigger prompts (Opus fixer, "
         "Opus reviewer, Sonnet fixer) once this lands; the owner creates them in the harness.",
         "Pre-study: the Lean flow pre-study, section K16."],
        fixer="sonnet", reviewer="opus", severity="medium"),
    group(
        "R10-FLOW-YIELD-PROBE", "study", "S", [],
        ["dev/governance/dimensions/D13.md"],
        [],
        "Explain the fall in review strength before any guardrail relies on it (Lean flow study, "
        "owner ruling R13). Real-catch blocked verdicts per reviewed pull request fell from 0.52 "
        "over round 10's first six days (112 pull requests) to 0.15 in the 48 h before the flow "
        "plan's adoption (47 pull requests), before any flow change merged; bookkeeping blocks held "
        "near 0.6 per pull request. Measure, on the review and verdict bus refs and the merged "
        "pull requests, which of these moves the rate: the mix of pull requests reviewed (product "
        "against instrument and process, size), the reviewer seat's model and agent kind (nudge.md "
        "replaced dead Opus seats with other models), fixer quality (first-pass merge share by "
        "fixer model), the verdict carries that replace re-reviews, and the real-catch classes "
        "themselves. Each candidate is a stratified rate with its own count, and a null control "
        "stratum whose rate must not move. Deliver the explanation and a recommended threshold "
        "for the review-strength guardrail; until it lands the guardrail reports the rate and "
        "trips on nothing. Follow D13's required outputs where they apply.",
        ["Owner ruling: investigate the 0.52 to 0.15 fall first (R13).",
         "Pre-study: the Lean flow pre-study, guardrail baselines (classes and enumerator)."],
        fixer="opus", reviewer="opus", severity="high"),
    group(
        "R10-FLOW-BODY-ONLY", "instrument", "S", ["R10-UPDATE-PR-SIGNALS", "R10-FLOW-BODY-PATCH"],
        ["tools/audit/seat/update_pr.sh", "tools/audit/seat/cloud_relay.sh",
         "tools/audit/seat/pr_args.sh", "tools/audit/seat/INSTRUMENTS.md"],
        ["tools/audit/seat/update_pr.sh"],
        "Make ruling R4 true in the tool (Lean flow study K12). update_pr.sh merges origin/main into "
        "the head unconditionally, in the step after it takes the handoff code head, and has no "
        "flag to skip it; app_push.sh has no body-only mode. So every body fix moves a clean head: "
        "observed 2026-10-21 on #2513, #2544, #2548, #2529 and #2549, each then carried by "
        "app_approve.sh --carry or re-reviewed. Change: (a) merge origin/main only when the "
        "pull request is DIRTY or git merge-tree --write-tree origin/main HEAD reports a conflict; "
        "(b) a body-only mode, taken when the code sha argument is the dash and the pull request "
        "head already contains the handoff tip: no worktree commit, no delivery-row commit when the "
        "row exists, and the body handed to R10-FLOW-BODY-PATCH's instrument, which runs the body "
        "contract at the unchanged head and PATCHes without a push; (c) cloud_relay.sh's handoff arm, which today skips any topic whose "
        "code tip the head already contains and so never propagates a body-only move, calls the "
        "body-only mode when the handoff-body tip changed. pr-contract re-runs on the edited event, "
        "so the body is re-gated without a push. Controls: with main ahead and a clean merge-tree, "
        "the head sha is identical before and after; a DIRTY fixture still absorbs; a body-only run "
        "on a moved head refuses; the relay fixture calls body-only exactly once per body move; each "
        "rule has a mutant. Sequence with the open row-only change #2567 and #2560 (update_pr lock), "
        "which touch the same script.",
        ["Pre-study: the Lean flow pre-study, section K12.",
         "Until this lands the orchestrator carries verdicts with app_approve.sh --carry (#1667)."]),
    group(
        "R10-FLOW-RELAY-HOLD", "instrument", "S", [],
        ["tools/audit/seat/cloud_relay.sh", "tools/audit/seat/INSTRUMENTS.md"],
        ["tools/audit/seat/cloud_relay.sh"],
        "A hold list the relay honours, so a frozen pull request's head stays put while its handoff "
        "branch keeps moving (Lean flow study K13a; expedite since revision 5). cloud_relay.sh's "
        "handoff arm updates every open pull request whose handoff/<topic> tip is ahead of its head, "
        "and has no hold or exclusion option. The round's roster pull request takes its topic from "
        "handoff/audit-r10-roster, the branch every roster_edit.py push lands on, so the roster "
        "freeze had to stop all roster pushes, forward-carries included; finding-propagation.md "
        "needs a fixer's carry on that branch before its pull request merges, and fix-review.md "
        "step 10 checks it at the body's handoff/audit-r<N>-roster sha (2026-10-21: #2567 blocked "
        "carry-missing behind the freeze). Add a hold file under the relay's state directory: a "
        "pull request number listed there is skipped by the handoff arm with one HELD line per pass, "
        "naming the handoff tip it did not apply; removing the number resumes it. The orchestrator "
        "writes and removes it; nothing else does. With a pull request held, roster pushes, "
        "forward-carries included, continue on the handoff branch and are taken up by the next "
        "roster pull request after the held one merges. Controls: a held pull request whose "
        "handoff tip moved is not updated and prints HELD; an unheld one is updated as today; a "
        "malformed hold file is a refusal for that pass, never a silent hold-all or hold-none; "
        "mutants for each arm.",
        ["Pre-study: the Lean flow pre-study, section K13a.",
         "Seam with R10-ORCH-MACHINERY: the beat's handoff job honours the same hold file, and "
         "R10-FLOW-ROSTER-FREEZE writes it automatically while a reviewer is live."],
        fixer="sonnet", reviewer="opus"),
    group(
        "R10-FLOW-ROSTER-FREEZE", "instrument", "S", ["R10-ROSTER-OPS", "R10-FLOW-RELAY-HOLD"],
        ["tools/audit/seat/cloud_relay.sh", "tools/audit/carry_audit.py",
         "tools/audit/seat/INSTRUMENTS.md"],
        ["tools/audit/carry_audit.py"],
        "The roster pull request as a frozen head, and carries that can name the round's roster "
        "(Lean flow study K13). Every roster_edit.py push lands on handoff/audit-r10-roster and the "
        "relay carries it into the open roster pull request, so a review of that pull request comes "
        "back head-moved or body-stale: #2559 lost five reviewer rounds that way on 2026-10-21. And "
        "carry_audit.py check resolves carry destinations against main's roster only, so a carry to "
        "a group that exists only on the handoff roster fails as a bad destination until the roster "
        "pull request merges: #2529, #2547 and #2561 were blocked by it. Change: (a) the relay "
        "does not move an open roster pull request's head while a review of it is in flight (a "
        "review worktree or an undisposed review dispatch for that number), the freeze fixer.md "
        "already gives a fix head; roster edits accumulate on the handoff ref and land between "
        "reviews; (b) carry_audit.py also reads the round's handoff roster ref "
        "(roster_lib.round_ref) as a destination source, naming which ref resolved each carry, so "
        "a destination on the handoff roster passes and one on neither still fails. carry_audit.py "
        "is code-owned: tvofi's review under the mandate. Controls: a fixture carry to a "
        "handoff-only group passes and names the handoff ref; a carry to a group on neither fails; "
        "the relay fixture with a review in flight leaves the roster head unchanged and moves it "
        "once the review posts; mutants for both arms.",
        ["Pre-study: the Lean flow pre-study, section K13."]),
    group(
        "R10-FLOW-JIDOKA", "instrument", "S", ["R10-PREPR-CAP"],
        ["tools/pr/prepr.sh", "tools/policy/fixtures/policy-rot/prepr"],
        ["tools/pr/prepr.sh"],
        "Error-proofing before handoff (Lean study K2). Of 133 blocked fix reviews in round 10, 25 "
        "were carry-missing: a finding with no destination, a fact tools/audit/carry_audit.py "
        "checks offline with its check subcommand and --body, and which pr-contract.yml already runs "
        "after the push. Add one prepr step that runs that same check on the body the fixer hands "
        "off, so the refusal lands before review instead of after it. Run the existing checker; add "
        "no new rule (decision 0012). Also report why the red-check answer arm of prepr (reds_line, "
        "gated before its call site) did not fire on the round's root-cause-unanswered and ci-red "
        "blocks, and fix the gate if it is a defect. Revision 8: pass carry_audit.py --roster-ref with the "
        "freshly fetched round roster branch (roster_lib.round_ref); the worktree's roster is not where "
        "fix-review step 10 looks, so an offline check passes a carry that is not on the roster branch. "
        "Controls: a fixture body whose carry exists only in the worktree roster is refused; a fixture "
        "body with an unrouted "
        "Forward-carry item is refused at the new step and passes once routed; the prepr self-test "
        "count rises by exactly the new arms; the step's mutant (step deleted) fails the self-test.",
        ["Owner ruling owed first: whether running an existing checker earlier counts as a new "
         "lint class under decision 0012 (it is undefined there).",
         "Pre-study: the Lean flow pre-study, section K2."],
        fixer="sonnet", reviewer="opus"),
    group(
        "R10-FLOW-PULL", "policy", "S", [],
        ["dev/governance/roles/nudge.md", "dev/governance/roles/orchestrator.md"],
        ["dev/governance/roles/nudge.md"],
        "Pull, pitch and classes of service in the orchestrator's turn (Lean study K3 and K10). "
        "nudge.md sits at its cap of 115 lines and 3814 tokens, measured by node "
        "tools/policy/policy_lint.mjs --budgets, so every sentence added is paid by a sentence cut. "
        "Change: step 16 dispatches by pull, ordered by critical-path depth, within flow-lane caps "
        "A4 B4 C3 F2 (the dispatch gate in tools/audit/seat/pr_cap.py enforces the total); a fly-in "
        "is registered on the roster at dispatch with roster_edit.py append-group under a name "
        "starting R10-FLY- (no new kind, no schema change), and "
        "an expedite item (red main, quota exhaustion, outage, security) bypasses the caps, one at a "
        "time. Steps 3 and 7: the train loads on an hourly pitch with --bot-prs, so record pull "
        "requests merge as part of the pitch, not between pitches. Step 2: the reviewer still starts "
        "at handoff; the verdict posts once required checks have concluded at that head; a head that "
        "moved since a merge verdict is first put to app_approve.sh --carry, and gets a reviewer only "
        "when the carry refuses. Step 6 shrinks to its exceptions, since the record beat merges its "
        "own pull request when its approver token is present. Step 12 shrinks to its exceptions "
        "once R10-FLOW-POSTMERGE lands. Step 9: "
        "absorb main into an open head only when it is DIRTY or merge-tree reports a conflict. "
        "orchestrator.md's sentence that dispatches the reviewer at push stays; reconcile its "
        "DIRTY sentence with step 9 in the same pull request. In orchestrator.md section 5, which every "
        "architect note cites but which holds no chain rule today, state the rule: a serial chain "
        "orders groups whose owning seams overlap, not groups that share a file. And the round's "
        "scope freezes at its register: a finding made mid-round goes to the next round's register "
        "unless it is expedite or a fly-in of size S. " + POLICY_GATE,
        ["Owner rulings owed: takt and pitch, lane caps, records in the pitch, the absorb trigger, "
         "the fly-in and expedite rule (the Lean flow pre-study, section R).",
         "Pre-study: the Lean flow pre-study, section K3."],
        owner_gate=POLICY_GATE, lane="RP"),
    group(
        "R10-FLOW-WIP", "instrument", "S", ["R10-FLOW-PULL"],
        ["tools/audit/seat/pr_cap.py", "tools/audit/seat/orchestrator_tick.py",
         "tools/audit/seat/INSTRUMENTS.md"],
        ["tools/audit/seat/pr_cap.py"],
        "Lane caps and the work the cap cannot see (Lean study K4). pr_cap.py's dispatch-gate counts "
        "roster groups whose resume stage is in-progress against HPO_WIP_CAP. It does not see an "
        "open pull request no roster group owns (a fly-in), nor a handoff no pull request carries "
        "(bus.sh orphans prints those). Add both to the count, and add per-lane caps derived from "
        "fields the roster already has, with no schema change: lane F is a group named R10-FLY-* or an "
        "open pull request no group owns; lane A is a group on the longest chain of not-done after edges or "
        "with coordinator.py in hot_files; lane C is kind instrument, policy, rca, record or docs; "
        "lane B is the rest. The tick prints one line, CONWIP n/cap with each lane, and a next subcommand prints the "
        "ranked dispatch list per lane (longest remaining chain first, then smallest), which the "
        "tick does not rank today. Controls: a "
        "fixture roster plus open-PR list plus orphan list gives exact lane counts; an unreadable "
        "orphan list is a refusal, never zero; each counting rule has a mutant that fails a named "
        "arm.",
        ["Pre-study: the Lean flow pre-study, section K4.",
         "Seam: R10-ORCH-MACHINERY's obligations ledger will own handoff-no-pr; read it when it "
         "lands rather than re-deriving orphans."],
        fixer="opus", reviewer="opus"),
    group(
        "R10-FLOW-RECORD-PITCH", "instrument", "S", ["R10-CI-LAYOUT-P2", "R10-FLOW-PULL", "R10-FLOW-MQ-PROBE"],
        [".github/workflows/tests.yml", "tools/audit/seat/record_row.py"],
        [".github/workflows/tests.yml"],
        "Records in the pitch (Lean study K6). In round 10, record pull requests were about half of "
        "every merge to main, and each one moves main under every open head. The record-autofix "
        "beat merges its own pull request whenever record_row.py --automerge-check passes and no "
        "young train-hold ref exists. Add a pitch bound to that automerge step: skip when the last "
        "record merge on main is younger than one pitch (3600 s), unless the oldest unrowed merge is "
        "older than two pitches (bounded staleness, so one record per merge stays the truth "
        "condition). The train's --bot-prs sweep then lands it inside the pitch. Land it where "
        "R10-CI-LAYOUT-P1 moves record-autofix off the Tests push run (its D-1), not in the old "
        "place. Controls: the step's harness shows a young record merge skips and a stale backlog "
        "proceeds; the existing train-hold arm is unchanged. Code-owned workflow: tvofi's review "
        "under the mandate.",
        ["Conditional: if the owner adopts GitHub's merge queue after R10-FLOW-MQ-PROBE, heads no longer absorb main and a record merge no longer stales them; close this group as not needed instead of building it.",
         "Pre-study: the Lean flow pre-study, section K6.",
         "HANDOVER trap 15 binds: one record per merge; batching the merge time, not the rows."]),
    group(
        "R10-FLOW-RECHAIN", "instrument", "S", ["R10-ROSTER-OPS"],
        ["dev/programme/rosters/wave-r10-groups.json"],
        ["dev/programme/rosters/wave-r10-groups.json"],
        "Apply the re-chain the decision seat ruled (Lean flow study K7). The seat examined all 15 "
        "after edges between two not-done coordinator.py groups against the code at main 5d433771a "
        "and roster 2c76c3128: 8 drop, 7 keep, and the drops need 3 replacement edges, or groups "
        "that edit the same functions end up unordered. Critical depth goes from 11 to 8. Drop: "
        "RATIO-ANCHOR after NIGHT-FOLDS, INPUT-STALENESS after RATIO-ANCHOR, CURRENCY after "
        "INPUT-STALENESS, LOOP-CPU after FREQ-DEFROST, CONFIG-NOTICES after LIVESTATE, PARAMS-OWNER "
        "after CONFIG-NOTICES, ARCH-SHAPES after PARAMS-OWNER, LEARNER-ETA after ARCH-SHAPES. "
        "Required, in the same burst: PARAMS-OWNER after LIVESTATE; ARCH-SHAPES after LIVESTATE; "
        "HEAT-METER after PARAMS-OWNER and ARCH-SHAPES. Recommended, each at no depth cost: "
        "LIVESTATE after LOOP-CPU; LOOP-CPU after NIGHT-FOLDS; PARAMS-OWNER after NIGHT-FOLDS and "
        "RATIO-ANCHOR; ARCH-SHAPES after INPUT-STALENESS; and, from this study, HEAT-METER after "
        "R10-THERMAL-POWER-OPTION, which shares flow_meter.py, config_flow.py and const.py with it "
        "and has no edge today. Apply with roster_edit.py set-after (R10-ROSTER-OPS) in the one "
        "roster burst after the open roster pull request merges, together with the architect-note "
        "and brief text the decision file lists per group. Do not apply the drops without the "
        "required edges. Land the seat's decision, drops and adds files as this burst's evidence "
        "in the tree, never only on a host. Controls: brief_lint TOTAL 0; roster_lib depth_of and "
        "critical_path at the new head print depth 8 and the path ADVISOR, SCORES, LIVESTATE, "
        "PARAMS-OWNER, HEAT-METER, COP-GATE, UX-HEALTH, ARCH-DOCS; no edge outside coordinator.py "
        "changes except the THERMAL-POWER-OPTION addition.",
        ["The decision is made: this group applies it. K7's first proposal (10 drops) was wrong on "
         "four edges the seat showed coupled in code; the seat's file is the authority.",
         "Pre-study: the Lean flow pre-study, section K7."],
        fixer="opus", reviewer="opus"),
    group(
        "R10-FLOW-ANDON", "instrument", "S", ["R10-TICK-RELAY-DECOUPLE"],
        ["tools/audit/seat/tick_loop.sh", "tools/audit/seat/INSTRUMENTS.md"],
        ["tools/audit/seat/tick_loop.sh"],
        "Make an orchestrator stop visible within 20 minutes (Lean study K8). In round 10, two "
        "stops went unnoticed for 6 h and 16 h (R10-RCA-ORCH-CONTINUITY). No loop writes a liveness "
        "signal anyone outside the host can read: tick_loop.sh writes a local board, state_docs.py's "
        "beat pushes only when main moves, and wt_sync.sh only when a tree is dirty. Each tick pass "
        "updates one ref, heartbeat/orchestrator, to a commit whose message carries the pass time "
        "and the relay and tick return codes, pushed with the seat's existing credential. A watcher "
        "outside the host (an owner-scheduled cloud task) reads the ref's committer date and alerts "
        "the owner when it is older than 20 minutes. Controls: the loop's self-test shows a pass "
        "moves the ref and a failed push is printed, never silent; a stale-ref fixture makes the "
        "watcher command alert and a fresh one does not.",
        ["This is a countermeasure for R10-RCA-ORCH-CONTINUITY: cite that record, do not redo it.",
         "Pre-study: the Lean flow pre-study, section K8."],
        fixer="sonnet", reviewer="opus"),
    group(
        "R10-FLOW-MQ-PROBE", "study", "M", ["R10-CI-LAYOUT-P2"],
        [".github/workflows/tests.yml", ".github/workflows/pr-contract.yml"],
        [],
        "Probe GitHub's merge queue (Lean study K9). The workflows already carry merge_group: "
        "tests.yml refuses a queue commit with no second parent and pins its base to the queue base, "
        "and pr-contract.yml derives the pull request from the queue ref. A queue would test the "
        "merged result once per pitch while the reviewed head stays unchanged, which removes the "
        "head-moved re-reviews and most main absorbs. Probe on a throwaway branch under a throwaway "
        "ruleset (the pattern HANDOVER records for the stamp's step 5): merge method merge, per "
        "decision 0010. Record, for every context main-protect-checks requires, whether it reports "
        "on merge_group, in both arms. Never touch main-protect-checks: the probe's report goes to "
        "the owner, who decides.",
        ["HANDOVER trap: a required context that never reports blocks every merge, in either "
         "direction.",
         "Pre-study: the Lean flow pre-study, section K9."],
        owner_gate="owner decision after the probe; the probe ruleset itself under 6175172275",
        severity="medium"),
    group(
        "R10-FLOW-TOOLKIT-MEASURE", "instrument", "M", [],
        ["tools/audit/seat/INSTRUMENTS.md"],
        [],
        "Land the Lean flow study's measuring tools on main, generalised for any round (owner, "
        "2026-10-21: the study's tools belong on main for future programmes; decision 0013: "
        "reusable instruments land in the tree, never only in /tmp). Three new instruments under "
        "tools/audit/seat/, each with --self-test on a recorded fixture and an INSTRUMENTS.md row. "
        "(1) A critical-path instrument (working name ci_critpath): from one workflow run's job and "
        "step timestamps, the critical path, and a counterfactual that drops a job edge or deletes a "
        "job and charges a stated bare cost; over the last N runs of a workflow, median and p90. "
        "Reuse the method behind the critical-path measurement in the CI design archive (tag "
        "archive/probe/design-ci-rev4 at 1371a0a6, its measure directory, phase 2) rather than "
        "writing a second one. (2) A review-strength instrument (working name review_strength): the "
        "study's baseline enumerator, real-catch and bookkeeping blocks per reviewed pull request "
        "over the review/<N> bus refs in a window [start, end), with the verdict-class sets read "
        "from VERDICT_CLASSES rather than copied. (3) A flow-metrics instrument (working name "
        "flow_metrics): the study's section 0 enumerators (groups closed and added per hour, "
        "records' share of merges, first-pass yield, main absorbs per fix branch, merge-to-merge "
        "re-reviews of unchanged code, share of hours with a merge). No round constant in code: "
        "repository, round prefix and window are arguments. API reads are paged, cached per run id "
        "and bounded by a stated maximum.",
        ["Null control: each instrument reproduces the study's figure from the same input: the "
         "critical-path one on runs 39625218966 and 39619839750 (48.6 and 47.8 min; the W1 "
         "counterfactual about 27-30 and about 41 min); review strength 0.52 and 0.15 on the "
         "study's two windows; the flow metrics the FUTURE-STATE section 2 figures.",
         "Round-10 use: R10-CI-LAYOUT-P1's fixer runs the critical-path instrument for its body's "
         "figure, and each #201 state comment runs the review-strength one (R13).",
         "Classify every new file (a measured closure or tests/closure.py's INERT list) or "
         "tests/entities.py refuses the pull request.",
         "Pre-study: the Lean flow pre-study, section K18."],
        fixer="sonnet", reviewer="opus", severity="medium"),
    group(
        "R10-FLOW-TOOLKIT-MODEL", "instrument", "M",
        ["R10-ORCH-MACHINERY", "R10-FLOW-TOOLKIT-MEASURE"],
        ["tools/plan/replan.py", "tools/audit/seat/roster_lib.py", "tools/audit/seat/roster_edit.py",
         "tools/audit/seat/INSTRUMENTS.md"],
        [],
        "Land the Lean flow study's projection model on main as part of the one plan model, not "
        "beside it (owner, 2026-10-21). Extend the plan model R10-ORCH-MACHINERY part (3) extracts "
        "(plan_model(), from R10-PLAN-ARTIFACT's code) with: (1) --project: an hourly simulation "
        "of the roster with lanes and caps, a lead per size ramping to a target, the merge pitch, "
        "the drain hold, merge-order-only edges, a tail after a predecessor, a cut-over that waits "
        "for a gap in the critical chain, a reserved slot for the next chain link, enabler "
        "effects credited pro rata to groups in flight, and fly-in and scope-creep arrivals; "
        "(2) --rank: the CD3 order of a stated set of enablers (round hours saved per hour "
        "earlier, divided by size); (3) a shadow overlay: roster_edit.py --dry-run --out applies "
        "a pack of group files and carries to a roster ref in memory, for brief_lint; (4) the "
        "schedule table rendered as a section of the plan page. The critical chain comes from "
        "roster_lib.critical_path; every scenario figure (caps, leads, effects, edges) is read "
        "from a per-round JSON file under dev/programme/<round>/, never from code.",
        ["Null control: on the study's pinned input (shadow roster at base f424d993d and its "
         "simulate_rules.py) the in-tree model reproduces the study's out-of-tree simulate.py "
         "outputs: 86, 91 and 97 h at in-progress lead factors 1, 2 and 3 with effects on, and "
         "92 h with effects off. A rule perturbation (drop the chain reservation) must move the "
         "figure where the study says it does (75 to 77 h at effects x2).",
         "Seam with R10-ORCH-MACHINERY and R10-FLOW-BOARD: one plan model and one page.",
         "Due before round 11's planning phase (SHADOW-PLAN section 6, P3); it saves no round-10 "
         "time, so it takes a normal lane-K pull.",
         "Pre-study: the Lean flow pre-study, section K18."],
        fixer="sonnet", reviewer="opus", severity="medium"),
]

# Carries folded into existing groups: (group, text).
CARRIES = [
    ("R10-RCA-HEADMOVED",
     "Rescope (Lean flow study): the countermeasure is already proposed, so this seat records, it "
     "does not design. Measured over round 10: 30 merge-to-merge re-reviews of unchanged code on "
     "the review bus refs, and a median of 4 main absorbs per fix branch (40% of its commits). Name "
     "the process state and run the cost test against R10-FLOW-PULL (step 9 absorb trigger), the "
     "K5 carry on R10-POLICY-FIXER-MD and R10-FLOW-MQ-PROBE as the countermeasure; keep this "
     "brief's own narrow candidate (a carry predicate covering autofix pin commits) only if the "
     "cost test still pays after those."),
    ("R10-RCA-ORCH-CONTINUITY",
     "Lean flow study: R10-FLOW-ANDON (a pushed heartbeat ref and an off-host watcher, 20-minute "
     "bound) is a ready countermeasure candidate; run the cost test against it rather than "
     "designing a second one, and record the decision."),
    ("R10-POLICY-FIXER-MD",
     "Lean study K5, folded here rather than a second fixer.md edit: before handoff, absorb "
     "origin/main only when git merge-tree --write-tree reports a conflict or the head is DIRTY "
     "(claim files); a clean merge-tree means leave the head, since the hourly batch proves the "
     "combined result. In round 10, 40% of fix-branch commits were main absorbs, each re-running "
     "steps 2-8. Also fix-review.md step 11: where a pr-contract run that started after the head's "
     "last workflow concluded is green at that head, it is the evidence that every red check is "
     "answered, and the reviewer does not re-derive it (HANDOVER: never re-gate an unchanged "
     "head); the mutation proof of step 1 stays the reviewer's, since CI cannot produce it. "
     "fixer.md is at its line cap (315/315), so pay by cutting. Reconcile steward S2 "
     "and nudge step 9 in the same pull request, or state why not. Pre-study: "
     "the Lean flow pre-study, section K5."),
    ("R10-ORCH-MACHINERY",
     "Lean flow study alignment (STUDY K17), binding on the build. The flow groups add work the "
     "approved design's beat and ledger must own, and they land first, so build them in: "
     "(0) The beat and every job it runs are detached processes, never an agent loop: in the live run of "
     "2026-10-21, agent-based relay and tick loops ended their turns twice and had to be re-armed. "
     "beatd.py runs under daemonize.py and an operating-system supervisor that restarts it (launchd on "
     "the orchestrator's Mac, a user systemd unit elsewhere); an agent only reads beatd status and the "
     "journal, and never hosts a job. "
     "Jobs run concurrently: one job's run never delays another job's schedule, so a long handoff "
     "update (9 min observed on 2026-10-21) never leaves the tick board stale; the tick reads "
     "independently of the relay, as R10-TICK-RELAY-DECOUPLE (#2549) already does for tick_loop.sh. "
     "The handoff job honours R10-FLOW-RELAY-HOLD's hold file. "
     "(1) beatd.jobs.json gains two jobs: heartbeat (R10-FLOW-ANDON's job script; interval 300 s, "
     "timeout 60 s; its ref message carries beatd status, so a timed-out job alerts the owner, "
     "not only a dead host) and pitch (R10-FLOW-AUTOTRAIN's job script; on the hour or when the "
     "previous train ends; it only launches a detached train and reads the train-stop "
     "obligation, never waits on CI). (2) The ledger gains one event kind, postmerge-owed "
     "(producer: R10-FLOW-POSTMERGE's after-merge step; closer: that step's later success or an "
     "orchestrator disposition), because the design refuses an OWED shape with no ledger kind. "
     "(3) The handoff job carries R10-FLOW-BODY-ONLY's body-only path unchanged and writes a "
     "disposition for the handoff-body ref it applies; it also does not move any pull request "
     "head while that pull request has a live reviewer in workers.json, which generalises "
     "R10-FLOW-ROSTER-FREEZE's predicate from the roster pull request to every head (fixer.md's "
     "freeze, made mechanical). (4) The seats job reads the dispatch records R10-FLOW-DISPATCH "
     "writes through bus.sh dispatch, which also gives the folded dispatch reason the round-3 "
     "review's N11-R found has no backing state. (4b) The ledger's verdict-unposted obligation closes "
     "only on a read-back: the posted pull request comment fetched and its first line matching the "
     "verdict and head, as comment-readback.md requires; a relayed claim that a verdict was posted is "
     "not a close (revision 8, observed live). (5) Is-main-red has one owner, the classifier "
     "#2570 and R10-FLOW-MAIN-GATE share; the tick and the sweep do not grow a third. (6) The "
     "plan page: if R10-PLAN-ARTIFACT (#2558) merges first, part (3) extracts plan_model() from "
     "its code rather than building a second page, keeps the UNAVAILABLE page and the five "
     "mutation fixtures, and renders R10-FLOW-BOARD's flow section from the same model. "
     "(7) Inventory row M43 is stale: pr_cap.py gates dispatch, not opening, since #2525. "
     "Owner rulings (2026-10-21): the amendments are approved in this brief and the fix reviewer checks "
     "them against STUDY K17 at build (R12); the stranded-handoff aging defaults are 4 h to a DISPATCH "
     "line and 12 h to an owner flag (R14), built behind the switch the brief already asks for."),

    ("R10-ARCH-DOCS",
     "Owner (2026-10-21): next to the CI shape, document and draw the orchestration machinery's "
     "shape, as built at this stage's merge base. In the developer onboarding, beside the CI "
     "shape: (a) the components: the beat and its jobs, the obligations ledger and its event "
     "kinds, the review and verdict bus refs, the relay's handoff arm, the merge train and its "
     "pitch, dispatch records, the heartbeat and its watcher, the hold list, the roster branch, "
     "the plan page and the flow toolkit; which run detached (daemonize.py) and which are seats; "
     "(b) one handoff's path: handoff, pull request, reviewable head, review, verdict read back, "
     "train, merge, record, stamp, with the ledger obligation each step opens or closes; (c) "
     "where a person or an agent decides and where a script does. Draw (a) and (b) as mermaid "
     "diagrams in the same visual language as the CI diagrams, and check every box and arrow "
     "against the tree: the job and event-kind tables R10-ORCH-MACHINERY lands, read at the "
     "merge base, never the design ref alone. The approved design is handoff/orch-machinery "
     "09174d94e; the Lean flow study's ORCHESTRATOR-PROMPT names the rules the shape must show."),
    ("R10-ORCH-MACHINERY",
     "Lean flow study revision 10 (owner, 2026-10-21): R10-ARCH-DOCS documents and draws this "
     "machinery beside the CI shape. Land the beat's job table and the ledger's event-kind table "
     "as data the tree holds (each self-test asserts the code matches it), so the diagram is "
     "checked against the tree, not against the design."),
    ("R10-CI-LAYOUT-P2",
     "Lean flow study K9: if the owner adopts GitHub's merge queue after R10-FLOW-MQ-PROBE, the "
     "umbrella's one required check must report on merge_group as well as on the pull-request "
     "head, or it blocks every merge (HANDOVER: a required context that never reports)."),
    ("R10-CI-LAYOUT-P1",
     "Lean study K6: when D-1 moves record-autofix off the Tests push run, keep the automerge "
     "step's train-hold arm, and leave room for the pitch bound R10-FLOW-RECORD-PITCH adds "
     "after this pull request merges."),
]

# Seams with R10-ORCH-MACHINERY's approved design (STUDY K17): each flow group that builds
# something the design's beat or ledger will own says how it moves there.
SEAMS = {
    "R10-FLOW-ANDON": "Seam with R10-ORCH-MACHINERY: write the heartbeat as a standalone job script with --once, called by tick_loop.sh now and registered as the beat's heartbeat job later; do not entrench it in tick_loop.sh, which the design retires. The script runs detached (daemonize.py), never as an agent loop.",
    "R10-FLOW-AUTOTRAIN": "Seam with R10-ORCH-MACHINERY: write the pitch as a standalone job script with --once (the design's job table has no train job); the beat hosts it as the pitch job; read the ledger's train-stop obligation when it exists. The script runs detached (daemonize.py), never as an agent loop.",
    "R10-FLOW-POSTMERGE": "Seam with R10-ORCH-MACHINERY: once the obligations ledger exists, record a failed step as the event kind postmerge-owed through ledger.py, not as a free OWED line, which the design refuses; until then the tick's OWED grammar.",
    "R10-FLOW-BODY-ONLY": "Seam with R10-ORCH-MACHINERY: the relay handoff arm becomes the beat's handoff job; keep the body-only path a function the job can call unchanged, and write a ledger disposition for the handoff-body ref when ledger.py exists.",
    "R10-FLOW-ROSTER-FREEZE": "Seam with R10-ORCH-MACHINERY: read a live reviewer from the design's workers.json when it exists (else the review worktree heuristic); the beat's handoff job generalises this freeze to every head.",
    "R10-FLOW-DISPATCH": "Seam with R10-ORCH-MACHINERY: dispatch through bus.sh dispatch so the ledger's reviewer-fire close is written, and add the seat to workers.json, which the seats job reads.",
    "R10-FLOW-WIP": "Seam with R10-ORCH-MACHINERY: when ledger.py lands, count stranded handoffs from its handoff-no-pr fold, not from bus.sh orphans.",
    "R10-FLOW-BOARD": "Seam with R10-ORCH-MACHINERY part (3) and R10-PLAN-ARTIFACT: one plan model; the flow board is a section of that page, not a third page.",
    "R10-FLOW-MAIN-GATE": "Seam with R10-ORCH-MACHINERY: the beat's tick and the sweep read this classifier; no third is-main-red rule."
}
for _g in GROUPS:
    if _g["group"] in SEAMS:
        _g["carry"].append(SEAMS[_g["group"]])

# Self-test hygiene (revision 11, from the orchestrator's live findings of 2026-10-21): every flow
# group that builds an instrument carries it, and so do the carries on groups that add self-tests.
HYGIENE = ("Self-test hygiene: (a) a new seat-selftest mutant in "
           "dev/audit/harnesses/r10_seat_selftests_mutants.py takes a per-file id (for example "
           "cloud_relay-1), never a new S number (the P6 convention); on 2026-10-21 three pull "
           "requests (R10-FLOW-RELAY-HOLD, R10-FLOW-YIELD-PROBE, R10-CI-LAYOUT's PR G) each lost a "
           "code round to a content conflict there when main gained tick_loop mutants S31-S34. "
           "(b) A self-test builds any git repository through tests/throwaway_git.py, never a "
           "hand-built git init (a pusher-reap handoff was refused for exactly that in "
           "tools/audit/seat/pr_args.sh); run python3 tests/throwaway_git.py --check before the "
           "handoff.")
for _g in GROUPS:
    if _g["kind"] == "instrument":
        _g["carry"].append(HYGIENE)
CARRIES += [("R10-CI-LAYOUT-P2", HYGIENE), ("R10-ORCH-MACHINERY", HYGIENE)]
