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
        "loop, and never while a train's pidfile is live. Controls: a fixture with one verdicted "
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
        "R10-FLOW-BODY-ONLY", "instrument", "S", ["R10-UPDATE-PR-SIGNALS"],
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
        "row exists, the body contract (prepr's pr-body step and carry_audit.py check) run at the "
        "unchanged head, then app_push.sh's body PATCH with nothing pushed, and the script refuses "
        "if the head moved; (c) cloud_relay.sh's handoff arm, which today skips any topic whose "
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
        "R10-FLOW-ROSTER-FREEZE", "instrument", "S", ["R10-ROSTER-OPS"],
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
        "blocks, and fix the gate if it is a defect. Controls: a fixture body with an unrouted "
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
        "R10-FLOW-RECORD-PITCH", "instrument", "S", ["R10-CI-LAYOUT-P1", "R10-FLOW-PULL", "R10-FLOW-MQ-PROBE"],
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
        "R10-FLOW-MQ-PROBE", "study", "M", ["R10-CI-LAYOUT-P1"],
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
     "Lean study K8: the supervised beat's journal should advance the heartbeat/orchestrator ref "
     "that R10-FLOW-ANDON introduces, so the watchdog reads one liveness signal, not two."),
    ("R10-CI-LAYOUT-P2",
     "Lean flow study K9: if the owner adopts GitHub's merge queue after R10-FLOW-MQ-PROBE, the "
     "umbrella's one required check must report on merge_group as well as on the pull-request "
     "head, or it blocks every merge (HANDOVER: a required context that never reports)."),
    ("R10-CI-LAYOUT-P1",
     "Lean study K6: when D-1 moves record-autofix off the Tests push run, keep the automerge "
     "step's train-hold arm, and leave room for the pitch bound R10-FLOW-RECORD-PITCH adds "
     "after this pull request merges."),
]
