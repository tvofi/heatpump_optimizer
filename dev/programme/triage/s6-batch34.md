# Proposal triage, session s6, batch 34 (P195-)

Proposals from the s6 `proposals.md`. Numbering continues after `s6-batch33.md` (P192-P194). This batch holds 8-10 entries and merges only through the train queue (tvofi, 2026-10-25). Facts read at origin/main 510787b76.

A roster op citing an ACCEPT below resolves only once this file is on the roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P195: body_patch.sh resolves a body's cited paths against the caller's checkout, not the PR head (S6-V115)
Verdict: ACCEPT narrowed, as a carry of R10-FLOW-BODY-ONLY that is built only with that group's dispatch and closes with it. There is no standalone build.
- The arm is `trackedFiles()` at an explicit revision that `body_patch.sh` sets to the head it gates (below).
- The filing's literal per-path `git show` form is REJECTED.
- It is filed as a carry and not left as a bare DEFER on the orchestrator's ruling of 2026-10-26: under tvofi's completion grant, a finding that sits outside the roster is a finding that can be lost.
Source: s6 `proposals.md` `## V115` (orchestrator, 2026-10-26T09:11:58Z).
Instances: one.
- #2852 (R10-RCA-RATELIMIT-RECUR), body `fa8458d7` at head `6353b624`. `body_patch.sh --dry-run`, run from a checkout of main, refused with three `` `## Forward-carry` names `<path>`, which is not in the tree `` errors. They named `dev/audit/rca/ratelimit-recur.md`, `dev/audit/harnesses/enumerate_api_calls.py` and the bare `enumerate_api_calls.py`, all of which the PR adds. The verbatim refusal is in the brief at `w72/brief-2852-body2.txt` in the orchestrator's state directory.
- The same dry-run from a detached worktree at `6353b624` passed (`seat-ledger.md` lines 998-999, 09:11Z). The real patch then ran from there with the head unmoved (line 1001, 09:12:33Z). The cost was one re-pooled body-fixer brief, never fired, and about 20 min of diagnosis (V115).
- Denominator: `grep -n "body_patch\|body patch" seat-ledger.md` shows about five body patches since 2026-10-24 (#2704, #2708, #2853, #2852), and this is the only refusal of this shape in the state directory. `grep -rh "body_patch: REFUSE"` finds no other.

Mechanism, read at 510787b76:
- `body_patch.sh` runs its contract in the caller's checkout. Its header says so: the contract "runs the CALLER's checkout" (line 26), from "a worktree holding the head's objects" (line 80).
- `policy_lint.mjs` checks a Forward-carry token with `resolvePathToken` (line 6835).
- That function is `brief_lint.mjs`'s `lookupPath(trackedFiles(), token)`, and `trackedFiles()` is `git ls-files` at the lint's own ROOT, the caller's tree.
- `pr-contract` runs with the PR head's tree checked out, so CI resolves the same tokens at the head. The offline pass is the one that is wrong, and wrong in the fail-closed direction: it refused a valid body.
- The opposite direction is a path the PR deletes but main still has. That would pass offline and go red on `pr-contract`'s `edited` run, which reads the body again, so it is caught, though later. That direction has no instance.

The carried arm:
- `brief_lint.mjs` already lists a tree at a ref (`refFiles(ref)`, `git ls-tree -r --name-only`).
- A `trackedFiles()` that honours an explicit revision (an argument or environment value that `body_patch.sh` sets to `<expected-head-sha>`) makes the offline contract resolve every path at the head it gates, as `pr-contract` does. Estimate: about 10-20 lines plus a fixture.
- Controls: a body citing a file the head adds, gated from a checkout that lacks it, passes with the revision set and refuses without it (the 6353b624 shape); a file the head deletes refuses with the revision set (null for the opposite direction); one mutant drops the revision and fails the first control.
- The filing's literal form, a `git show <head>:<path>` per citation inside `body_patch.sh`, is REJECTED. Every path check is the lint's, so a second resolver in the shell script would disagree with it.

Cost:
- About 10-20 lines in `tools/policy/brief_lint.mjs` (1,344 lines). That file is outside R10-FLOW-BODY-ONLY's `files`, and it is the resolver every policy check shares.
- One argument in `body_patch.sh`, plus a self-test case in its `--self-test`.
- As a standalone group: an opus fixer and an opus review round. As a carry: the marginal lines inside a PR that already touches the same contract arm. R10-FLOW-BODY-ONLY's carry on the `--roster-ref` argument (`body_patch.sh:98`) is that kind of contract-fidelity fix.

Binding: one measured instance of about 20 min against a cross-file change to the shared path resolver.
- The workaround costs nothing: run `body_patch.sh` from a detached worktree at the expected head, as its header already says and as the orchestrator did at 09:12Z.
- As a standalone build the trade is marginal, so none is ruled.
- As a carry of the group already editing the same contract arm, its marginal cost is the 10-20 lines and one fixture, and it removes the class of false refusals. That clears the bar only riding that dispatch.
- A recurrence before the dispatch is evidence for dispatching the group, not a second ruling. A third instance is a root-cause trigger under `defect-root-cause.md`.

## P196: a claimed_drift.txt conflict parks verdicted PRs on merge-main (S6-V116)
Verdict: ACCEPT narrowed -> R10-996-RUNNER-CLAIMS (stage `queued`, M), as a carry. The `claimnotes` driver merges the bare claim list per scenario, three-way.
- A scenario whose claim lines changed on one side only takes that side's lines.
- A scenario neither side changed keeps its lines.
- A scenario deleted on one side and untouched on the other stays deleted.
- A scenario whose lines BOTH sides changed still refuses. This is the case the driver's design names: no rule says which claim describes which diff.
- The filing's two options are ruled below: "union disjoint fixture claims" is this arm, made exact. The train-side resolver was re-ruled at tvofi's request (2026-10-26). The train is the consumer: it runs this arm through the driver its recarry already calls. A separate resolver in `merge_train.py` or `remerge_main.sh` is REJECTED on placement.
Source: s6 `proposals.md` `## V116` (orchestrator, 2026-10-26T09:37:02Z).
Instances: seven refusals by the driver of `tests/golden/claimed_drift.txt` since 2026-10-17. Each was re-run with origin/main 2563e2922's `merge_claim_file` over the merge's base, branch and main texts, and each changed scenario was counted per side.
- Today, four on three PRs, each of which parked a verdicted or queued PR:
  - #2841 at 11e8075d against main f6784210c: the branch changed 5 scenarios, main 1, overlap 0. `seat-ledger.md` lines 760-761 in the orchestrator's state directory, 03:51Z; it went to a fixer round.
  - #2745 at 8d0572dc against 28800999: 41 and 1, overlap 0. Train s43's unfinished merge, line 786, 04:34Z.
  - #2745 at cc679118 against 2563e2922: 41 and 5, overlap 0. Line 1018, 09:33Z; a local opus fixer plus a delta reviewer.
  - #2834 at c38903518 against 2563e2922: 5 and 5, overlap 5 (the five `coord_*` scenarios). Lines 1023-1024, 09:36Z; train s52 stopped and the PR parked.
- Earlier, three hand-resolved merges in main's history, classified the same way:
  - 3a07c2eaa (10-17): 3 and 1, overlap 0.
  - e438816e3 (10-18): 4 and 41, overlap 0.
  - 5bf232eac (10-19): 45 and 50, overlap 42.
- `card_claimed_drift.txt` resolved in every one of them. Its changes were one-sided.
- So 5 of the 7 are disjoint and this arm resolves them; 2 overlap and still refuse.
- `claims-for:` was equal on all three sides in all seven (7.0.0 for the earlier merges, 7.0.4 today).

Why disjoint per-scenario is safe where the driver now refuses:
- The driver's refusal guards against a claim one side deleted coming back (`merge_claim_file`'s docstring; `claim-files.md`). That is a two-way-union hazard.
- A three-way per-scenario merge keeps every deletion: a scenario one side deleted and the other left alone stays deleted, so nothing is reinstated.
- Each kept line is still written by exactly one side, so "a line excuses only the diff that wrote it" holds line by line.
- Where both sides wrote the same scenario (#2834, 5bf232eac), the reasons compete, and the refusal stays.

Rejected:
- (a) A separate resolver in the train, re-ruled on tvofi's premise that every PR reaches main only through the train (orchestrator relay, 2026-10-26: "Merges should not happen outside the train so the constraint is vacuous"). The premise is accepted, and the first ruling's reason, that a train-only resolver "misses the other two paths", is withdrawn as a reason about landing. The arm still goes in the driver, for the two reasons below.
  - (1) Earlier merges meet the conflict first.
    - The merge-main bot (`.github/workflows/merge-main.yml`, `tools/pr/merge_main_bot.py`) runs after every push to main. It merges main into each DIRTY PR whose conflicts the drivers resolve, with `git merge-tree` and the driver installed (merge-main.yml line 74).
    - A seat absorbing main before a review or a handoff does the same.
    - Today, 2 of the 4 instances surfaced there, not in the train: #2841 at review (ledger line 760) and #2745 at cc679118 as DIRTY after #2841 merged (line 1018).
    - With a train-only resolver those PRs stay DIRTY until their train turn, and a DIRTY PR runs no CI at all (`claim-files.md`). The tick also keeps reporting them for a claimnotes repair (`merge_train.dirty_repair`), which is where today's #2745 fixer came from.
    - The train's recarry would resolve each one eventually, so nothing is lost. But the pre-train CI signal is lost, and the tick misroutes the PR to a fixer. Put in the driver, the bot resolves the same conflict on main's push and the PR keeps running CI. The premise makes this a cost of time, not of correctness.
  - (2) Placement.
    - The train already calls the driver. `merge_train.py` recarries through `remerge_main.sh`, whose `git merge --no-edit origin/main` runs in the train's worktree with `merge.claimnotes.driver` installed (read in train/s52/wt/2834's config, which the worktree shares with its clone). So the rule in the driver is a resolver in the train, with no train code added.
    - A resolver inside the recarry would need the same rule as a pure function of base, ours and theirs (it must read the claim list with `env_drift.parse_claim_map` either way), plus parts the driver gets free from git: catching `remerge_main.sh`'s `MERGE CONFLICT` exit, reading the three index stages, writing and staging the file, aborting cleanly on refusal, and a throwaway-git fixture for each. All of that would land in `merge_train.py` (about 5,600 lines, a hot file) or the shell script.
    - Pinning, in the driver: a mutant per rule in `merge_claim_file` (one-side-takes, deletion-wins, both-sides-refuses, claims-for equality), each failing a three-text fixture, with no git needed. The existing `K15 (c)` self-test in `merge_train.py` (lines 4330-4396), which installs the driver and merges, already pins that the train's merge reaches the driver at all.
    - Pinning, in the train: the same rule mutants, plus a mutant for each plumbing step that needs a real repository.
    - Fewer moving parts and cheaper pins: the driver.
- (b) A line union for scenarios both sides changed. That covers 2 of 7, and it is the value-bearing case the design reserves for a human. If the overlap instances keep recurring, the countermeasure is a claim grammar that does not rewrite shared `coord_*` lines on every coordinator change, which is the claim-grammar seam R10-996-RUNNER-CLAIMS already owns. Re-rule it with that group's design. Re-checked under tvofi's premise, the both-sides case is not shown safe. The candidate is that the branch's lines win for a scenario both sides wrote, since main's line is inert once merged and #2841's hand resolution kept the branch's lines. That candidate is unmeasured against the env_drift gate, and it decides a value-bearing claim, so it still refuses. The group's design measures it.

Cost:
- About 20-40 lines in `tests/env_drift.py`: `merge_claim_file`'s both-sides branch, plus `merge_claim_defect` checking the merged map against the per-scenario decision rather than one side's list.
- Fixtures: the three disjoint instance shapes resolve; the #2834 shape refuses; a scenario one side deleted and the other kept stays deleted (the reinstatement control); a `claims-for:` mismatch refuses (null); one mutant per rule.
- A sentence of `dev/governance/rules/claim-files.md` changes from "both sides rewrote the bare claim list" to "both sides rewrote the same scenario's claims". That is policy under the mandate, and the group's brief already says its claim-files.md change is.
- One fixer round and one review round.
- It does not change GitHub's `DIRTY` flag: GitHub cannot run the driver (`claim-files.md`, #570). It changes what the merge-main bot and the train's recarry do with that state: they resolve and carry on instead of parking.

Benefit: 5 of 7 measured refusals resolved mechanically. Today that is 3 of 4, each priced by V116 at one opus fixer, a verdict that no longer carries and a delta re-review, about 1-2 h on the critical path (#2745 gates the v7.0.5 stamp). That is about 3-6 h saved today alone against one S-sized round.

Binding: the value-bearing claim list. The arm is accepted only in the shape that keeps every deletion and still refuses every scenario both sides wrote.

For the orchestrator, not a carry:
- R10-996-RUNNER-CLAIMS is `queued` and sized M for its grammar work. This arm is S and independent of that design.
- It can land as the group's first PR, ahead of the grammar, and it pays off on the critical path today. The group owns `tests/env_drift.py` and the claim-files.md change, so a second group would collide on both.

## P197: the orchestrator's resume prompt is hand-kept; handover_prompt.py covers seats only (S6-V117)
Verdict: DEFER -> R10-ORCH-BEATD (stage `not-started`, L), which already owns the orchestrator's generated handover. Its carry 13, tvofi's card 2, has the orchestrator "rotate through the handover document (`tools/audit/seat/state_docs.py` plus the resume, with `handover_prompt.py` and `resume_doc.py`)", so the item is on the roster and needs no new carry.
- The filed arm, an `--orchestrator` arm that the state beat runs and that is fed by the seat ledger, the train symlink and #201's mandate, is REJECTED in the form that publishes to the state ref.
- The instance's cause is not this arm's to fix. It goes back to the root-cause class that already owns it (below).
Source: s6 `proposals.md` `## V117` (orchestrator, 2026-10-26T09:55:12Z, raised by tvofi).
Instances: one, with its cause.
- `RESUME-PROMPT.md` in the orchestrator's state directory was 12 h stale on 2026-10-26. It named the s42 train, #2817's plan and the w38 handover (V117).
- The cause, from `seat-ledger.md` there: the state beat had died at 2026-10-25 17:41Z on a fetch ref-lock race in the shared `orch-wt` (line 1038, 09:53Z). The `wt_sync` loop had been dead since 10-25 11:49Z (line 1033, 09:49Z).
- So the generated docs (`RESUME-CURRENT.md`, `NEXT-SESSION-PROMPT.md`, `PLAN-TABLE.md`) were as stale as the hand-kept prompt. A generated orchestrator arm run by that beat would have died with it.
- Earlier stops of the same beat: `pulse.py` state-beat STOPPED on 10-25 at about 09:12Z (line 484), and its relaunch after the 12:45Z crash recovery (line 514). `dev/audit/rca/R10-RCA-ORCH-CONTINUITY.md` counts more on 10-17, 10-19 and 10-21 (its table, I2-I4).

What the interim already did:
- `RESUME-PROMPT.md` (read at 10:55 local) now carries only the orchestrator's static bootstrap: the mandate id and expiry, binding-policy commands, standing seats, detached loops and the sweep cron.
- For every volatile item (seat ids, the train, verdicts, pool runs) it points at the generated docs and the ledger tails. It states it "is never hand-updated with state".
- The V117 list, a generated mandate, seat ids and handovers, live train, pool trigger ids, cron and loop liveness, is therefore split.
  - The volatile half is already read from generated or ledger sources.
  - The static half changes only when a mandate, a trigger or the cron is replaced. There is no measured staleness of that half: the 12 h staleness was volatile state and the dead beat.

Cost of the filed arm:
- S-M in `tools/audit/seat/handover_prompt.py` (280 lines) plus a self-test.
- Its inputs live outside the tree: the ledger, the train symlink, `cloud-sessions.tsv`, and a GitHub read of #201 each beat.
- `state_docs.py` pushes its outputs to the orphan state ref, and it is built "stateless ... nothing about a session or a machine is hardcoded" behind `ref_privacy` (#2310). Ledger tails, trigger ids and seat ids are exactly what that guard and tvofi's 2026-10-16 no-host-paths ruling keep off origin.
- A local-only variant, written to the beat's `--mirror` directory and never pushed, avoids that. It is the shape carry 13 implies, and it is BEATD's to design.

Binding:
- The filed arm does not remove the instance's cause: the beat died, and anything it generates died with it.
- Published, it carries host-local state onto origin.
- Local-only, its residual benefit after the interim is unmeasured. That makes it DEFER, never ACCEPT, and its owner already holds it.
- What would change the answer: a resume misled by the static half after the interim (a replaced mandate id, trigger id or cron prompt left stale in `RESUME-PROMPT.md`). Then the local-mirror arm is ruled as a BEATD carry.

For the orchestrator, not a carry:
- The 16 h undetected state-beat death is a recurrence of R10-RCA-ORCH-CONTINUITY's class. That record names `pulse.py`'s state-beat arm as the detector, wired into sweep step 5, and records the class as `detector`, not `barriered`, until the owner's call between an hourly cloud probe (A, recommended) and a CI cron (B) runs (section 6).
- A death that the wired detector did not surface for 16 h is evidence on that open barrier call. It returns to the root-cause route (`defect-root-cause.md`), as P192 did with its class, and is not a triage item.
- The ref-lock race itself, a beat fetching in the `orch-wt` the other loops share, belongs to BEATD's supervised beat (concern B, single-instance locks per job).
