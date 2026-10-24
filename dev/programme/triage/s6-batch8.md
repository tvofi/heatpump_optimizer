# Proposal triage, session s6, batch 8 (P66-P76)

Nine mechanisation cards from the s6 pre-study (its `cards.json` and the two
evidence scripts `verdict_classes.py` and `opener_refusals.sh` sit in the
orchestrator's out-of-tree scratch, so counts below that cite them are the
pre-study's, re-checked where a tree command is given) and two proposals from
the s6 `proposals.md` (check-wave-script for brief-only diffs; host paths in
verdicts). The owner was shown the cards and did not reply; the standing rule
is that no reply means the card's recommendation, so each recommendation is the
default and a differing ruling says why. Numbering continues after
`s6-batch7.md` (P65). GitHub calls: 0.

A roster op citing an ACCEPT below resolves only once this file is on the
roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P66: carry-not-landed, a body routes a finding to a group whose carry lacks it (card 1)
Verdict: ACCEPT NARROWED -> R10-FLY-CARRY-DISPOSITION (dispatch it first among the fly-in groups; no `open_pr.sh` call site)
Source: pre-study card 1.
Instances: 33 review blocks on 32 PRs in the carry family (carry-missing 31, carry-unrouted 1, dangling-owner 1) over verdicts 2026-10-15 to 2026-10-24 (pre-study `verdict_classes.py --list carry`); 24 of the 31 are "not carried to <GROUP|#N>" (destination named, content absent), the mechanical share. Median 3.8 h from the blocked verdict to the next verdict or merge (n=30), about 90 PR-hours for the 24. The instrument already exists as a carry: `git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json` lists, on R10-FLY-CARRY-DISPOSITION, "add `carry_audit.py landed` ... and `land-ops` ...; bus.sh dispatch refuses on rc 1".
Cost: S beyond the existing carry -- the carry's own estimate stands (about 80 lines in `carry_audit.py`, three fixtures, one refusal arm in `bus.sh dispatch`); one local git read of the roster ref per dispatch, no API call.
Binding: the pre-study's second call site, `open_pr.sh` after its second push, is DROPPED. Every one of the 24 blocks is raised by a reviewer, who exists only after dispatch, so the dispatch refusal already lands the item before the first review round; an opener-side call adds a roster writer to a file R10-FLY-OPENPR-ATOMIC edits (four carries, P64 re-cut) and inherits the two-writer class (P57/P63) for no further round saved. Dedupe on the `(items <id>)` tag, never on text; land only on a group that is not done.
Carry text (for `roster_edit.py append-carry R10-FLY-CARRY-DISPOSITION`, citing `triage: dev/programme/triage/s6-batch8.md#P66`): "Priority and shape of `carry_audit.py landed` / `land-ops` (carry 1): 24 of 33 carry-family review blocks 2026-10-15 to 2026-10-24 were 'not carried to X' with X named, 3.8 h median each. The land-ops line is `append-carry <GROUP> 'From #<N> (<topic>), body item <id>: <text>'`, tagged `(items <id>)`; dedupe on the tag, never the text. Wire it at `bus.sh dispatch` only (refusal on rc 1 prints the ops for the roster seat); add no opener call site. Controls: a body whose item id is already in the group's carry or brief yields zero ops (null); a `dismissed:` item and a `#N` item with `carries/carry-N.json` yield zero; a done destination refuses and never lands (routing invariant 1); fixtures include the #2558 pair and one already-landed body; one mutant."

## P67: red-check-unnamed, `## Red checks` omits a derived red (card 2)
Verdict: ACCEPT NARROWED -> R10-FLOW-JIDOKA (the `mutation` fill only; the `ANSWER OWED` stub and the inherited-from-main arm are not accepted)
Source: pre-study card 2.
Instances: 25 review blocks on 22 PRs (pre-study `verdict_classes.py --list red-unanswered`); on the opener side `prepr` refused 7 of 28 opens on the pr-body arm (pre-study `opener_refusals.sh`: "7 pr-body"), 5 of them "check `mutation` is red and `## Red checks` does not name it", each re-attempted after a median 49 min (17 gaps). `rg -n 'rides .--red' tools/pr/prepr.sh` prints the comment near line 777: `body_line` already derives that red from step 6d's unpinned-site file.
Cost: S -- about 25 lines in `prepr.sh`: a `--fill-red` mode that `body_push.sh` and `open_pr.sh` pass, writing the `mutation` line only when step 6d listed unpinned sites, plus two self-test rows. `prepr.sh` is a ratcheted hot file, so the lines are paid by deleting the equivalent refusal-message code, not by a raise.
Binding: the fill removes the 49 min round trip for the 5 mutation cases (about 4 h in the day) and is exact because the function that refuses already computes the red. The pre-study's `ANSWER OWED` stub is REJECTED: `pr-contract` already refuses an unnamed red, so a stub turns one refusal into another, adds a `policy_lint.mjs` rule and saves no time. The inherited-from-main arm stays deferred as the pre-study had it (its share of the 25 is unmeasured; about 3 API calls per PR to measure). Risk and bound: a `mutation` red from a survivor rather than an unpinned site would be hidden; with no unpinned site predicted the fill writes nothing, and mutation-autofix reddens the head again on a survivor.
Carry text (for `append-carry R10-FLOW-JIDOKA`, citing `triage: dev/programme/triage/s6-batch8.md#P67`): "`prepr.sh --fill-red` (passed by `body_push.sh` and `open_pr.sh`): when step 6d lists unpinned sites and `## Red checks` lacks `mutation`, insert one line naming it with the head sha and 'red by construction on the N sites under `## Unpinned sites`; mutation-autofix pins killed sites after the push'. Writes nothing otherwise. No `ANSWER OWED` stub, no inherited-from-main arm. Controls: no predicted site writes nothing and the mutation red stays refused (null); a body already naming it is untouched; one mutant; pay the lines by deleting, not by a budget raise."

## P68: body-stale / head-moved, the body describes an earlier head (card 3)
Verdict: DEFER -> R10-FLOW-BODY-ONLY (owner of the generated figure blocks)
Source: pre-study card 3.
Instances: 22 review blocks on 18 PRs plus 1 opener refusal (pre-study `verdict_classes.py --list body-stale/head`); median 1.7 h to the next verdict or merge (n=21).
Cost: M (PR template, `checkPrBody`, `brief_lint`, `body_push.sh`), plus a figure re-run per push.
Binding: the design is already carded behind R10-FLOW-BODY-ONLY; of the 22, the 5 "body-stale" blocks describe round-1 prose that no instrument can rewrite soundly, and a rewrite that flips a figure's side under unchanged prose is the claim-stronger-than-check class. Would change the answer: R10-FLOW-BODY-ONLY landing and a recount of how many of the 22 were generated-figure staleness rather than prose.

## P69: self-test site rules (throwaway_git, ref_privacy) missed at the fixer's handoff (card 4)
Verdict: DEFER -> R10-FLOW-JIDOKA (already owns both detections); the rewriting codemod is not accepted
Source: pre-study card 4.
Instances: 5 (2 prepr-refused opens at `roster_queue.py:157` and `:164`, 3 review blocks: two `ci-red`, one `root-cause-detectable`). The detection is already carried: `git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json` shows R10-FLOW-JIDOKA carrying "(b) A self-test builds any git repository through tests/throwaway_git.py ... run `python3 tests/throwaway_git.py --check` before the handoff" and the 2026-10-22 entry that its prepr replay "must include instrument-self-tests' ref_privacy --check".
Cost: codemod M; the two checks XS inside JIDOKA's existing replay.
Binding: a codemod edits proven code after the proof and needs init-vs-clone, cwd and cleanup semantics only the author holds. The sub-second checks need no new ruling: they are JIDOKA's. Would change the answer: JIDOKA landing without `throwaway_git.py --check` in `--body-check`, and a further handoff refused for it.

## P70: unpinned-site keys drift when the opener merges main (card 5)
Verdict: ACCEPT -> R10-FLY-OPENPR-ATOMIC (adds `tools/pr/ci_predict.py` to its files)
Source: pre-study card 5.
Instances: 7 prepr-refused opens on the unpinned-sites arm (pre-study `opener_refusals.sh`: "7 unpinned sites"); 4 are pure line drift (config-notices 7293/7296 against a body keyed at 7295/7298; demand-overbook 1007 to 1008 and 1011 to 1012; thermal-power-option 4878 against 4876), 3 a missing section at first open. Each cost a median 49 min plus a fixer body edit.
Cost: S -- about 50 lines in `ci_predict.py`, four self-test rows, two lines in `open_pr.sh` (and `update_pr.sh` after its main merge); one local `git diff -U0` per open, no API.
Binding: the mapping is exact (identical line text, unique, same mutant kind) and removes 4 of 7 refusals while assigning no disposition (`ci-autofix.md`: never automate survivor triage). Carried on OPENPR-ATOMIC because it owns the `open_pr.sh` call site; the group grows with P71 and P72 and the orchestrator re-sizes it.
Carry text (for `append-carry R10-FLY-OPENPR-ATOMIC`, citing `triage: dev/programme/triage/s6-batch8.md#P70`): "`ci_predict.py --rekey-body BODY --from <code-sha>`, called by `open_pr.sh` after its `git merge origin/main` and by `update_pr.sh` after its main merge: rewrite an `## Unpinned sites` key in place only when its line at `<code-sha>` maps through `git diff -U0 <code-sha> HEAD -- <file>` to exactly one line at HEAD with identical text and the same mutant kind; then add one `## Head` note (via `head_note.py`) listing old -> new. Controls (null): a key whose line text changed, a key with two identical candidate lines and a site the body never listed are left alone and `prepr` still refuses; a new site never gets a default disposition. Self-test rows: moved-and-identical rekeyed; changed text kept; duplicate text kept; unlisted site refused. One mutant."

## P71: Closes list mismatch, the opener is given no intended-issue list (card 6)
Verdict: ACCEPT -> R10-FLY-OPENPR-ATOMIC
Source: pre-study card 6.
Instances: 4 refused opens (pre-study `opener_refusals.sh`: "4 closes-list"); in all 4 the opener argv ends at the group. The roster `fixes` list holds the numbers for 2 (#2378, #2381); #2492 and #2509 appear only in `issues`.
Cost: XS/S -- 5 to 10 lines in `open_pr.sh` / `pr_args.sh` and one self-test row; one local roster read per open.
Binding: removes 2 of 4 refusals (16 to 49 min each plus a hand re-run by the dispatch seat); the other 2 are the author's call and stay refused. A wrong close needs a stale `fixes` entry and a body that also says `Closes #N`, two independent errors. The benefit is modest (about 2 a day) and the trade is clear only because the cost is under ten lines inside a file the group already edits, with no standing cost.
Carry text (for `append-carry R10-FLY-OPENPR-ATOMIC`, citing `triage: dev/programme/triage/s6-batch8.md#P71`): "With no intended-issue argument, `open_pr.sh` defaults the Closes list to the roster group's `fixes` (roster_lib at the default ref) and prints it. Controls: a `Closes #N` for a number in `issues` but not `fixes` still refuses (null: #2492, #2509); an explicit argument list is never widened. One self-test row in `pr_args.sh`'s style."

## P72: opener re-run collides with its own leftover worktree (card 7)
Verdict: ACCEPT -> R10-FLY-OPENPR-ATOMIC (no new instrument: extend the P16 carry with the refused-exit case and 8 instances)
Source: pre-study card 7.
Instances: 8 of the 10 STOPPED opens (pre-study `opener_refusals.sh`, STOPPED causes: "8 ... line 46 exited N: git worktree add -q -b"); 7 of the 8 directly follow a prepr-refused open of the same topic whose exit left the worktree and branch behind. P16 was ruled on 2 instances; this is 8 in one day.
Cost: S as P16 already estimated (10 to 20 lines, one self-test row, one mutant); the retry itself is 0 to 3 min but needs a hand and hides the real refusal behind a STOPPED line.
Binding: same cause and file as P16/P64. The P64 re-cut (detach once at the end of each opener) covers success; this adds removal on a refused or STOPPED exit when the worktree is clean and the branch never pushed. Priority: the group now holds P53, P64, P70, P71 and this; dispatch it ahead of other opener-class work.
Carry text (for `append-carry R10-FLY-OPENPR-ATOMIC`, citing `triage: dev/programme/triage/s6-batch8.md#P72`): "P16 extension, 8 instances (s6 opener logs, 'git worktree add -q -b' STOPPED at line 46, 7 after a prepr-refused open of the same topic): on a REFUSE or STOPPED exit the opener removes its worktree and deletes the local branch when the worktree is clean and the branch is absent on origin; on success it detaches once (P64). Controls (null): a worktree with an uncommitted file, or a branch present on origin, is kept and named; one self-test row, one mutant."

## P73: early-gate race, pr-contract and gate fail while CodeQL is in progress (card 8)
Verdict: REJECT a build-time instrument; P62 stands
Source: pre-study card 8.
Instances: 3 (#2698 3383fb2a, #2704 04860ee0, #2706 ea459c0b), each a hand rerun and a false "back to fixer"; ruled as P62 in `s6-batch4.md`.
Cost: not applicable.
Binding: nothing in `body_push`, `prepr`, `ci_predict` or the openers can know CI's analysis timing; the fix is the bounded poll in `codescan_wait.py` already accepted for R10-CI-LAYOUT-P2. A second instrument would duplicate it.

## P74: judgement-class blocks (card 9)
Verdict: REJECT mechanisation
Source: pre-study card 9.
Instances: 106 of 199 unique blocked verdicts (53%): harness, mutation-vacuous, class-open, mutation-survivor, metric-gamed and singletons (pre-study `verdict_classes.py`, JUDGEMENT line); median 3.2 h to the next verdict.
Cost: not applicable; no instrument is proposed.
Binding: each block says the work is wrong or the design incomplete and only the author or reviewer can supply the right version; an applied fix would be confirming evidence (a pin that kills the planted mutant but not the class, a conflict resolved silently against a fix). `ci-autofix.md` forbids automating survivor triage.

## P75: wire check-wave-script.mjs into prepr for brief-only diffs (source: #2736 at fbbd3e61)
Verdict: ACCEPT NARROWED -> R10-FLOW-JIDOKA (repoint a dead path glob; nothing new is wired)
Source: s6 `proposals.md` ("wire check-wave-script.mjs into prepr for brief-only diffs", from main 2026-10-24 via #2736 round 2).
Instances: 1 red (#2736, wave-script; `git cat-file -t fbbd3e61` prints commit) and one mechanism in the tree. `prepr.sh` already runs the check (step 4), but its trigger lists `'tools/audit/briefs/*.md'`, and `git ls-tree -r origin/main --name-only | grep -c '^tools/audit/briefs/'` prints 0, while `... | grep -cE '^dev/governance/(roles|dimensions)/.*\.md$'` prints 33, the files the checker itself reads (`briefListing()` in `tools/policy/check-wave-script.mjs`). A brief-only diff therefore prints `skip wave-script` and goes red on CI's unconditional job, the shape step 4's own comment records for #1062.
Cost: XS -- two path strings in the step-4 `git diff --quiet` list in `tools/pr/prepr.sh`, one self-test row; the node run costs seconds and only when a brief or role contract changed.
Binding: the proposal as worded (a new wiring) is unnecessary; the fault is a stale path left by the R9-RO-5 move, with 1 measured red and a one-line repair.
Carry text (for `append-carry R10-FLOW-JIDOKA`, citing `triage: dev/programme/triage/s6-batch8.md#P75`): "`tools/pr/prepr.sh` step 4 (wave-script): replace the dead `'tools/audit/briefs/*.md'` in the trigger list with `'dev/governance/roles/*.md'` and `'dev/governance/dimensions/*.md'` (tools/audit/briefs/ holds 0 files; the checker's `briefListing()` reads those two directories, 33 files); #2736 at fbbd3e61 went red on CI's wave-script after prepr skipped it. Controls: a diff touching only one role contract runs the step (null: a diff touching only `README.md` still skips); one self-test row, one mutant that restores the old glob."

## P76: verdicts quoting host paths are refused at post (S6 proposals V12)
Verdict: ACCEPT NARROWED -> R10-FLY-CARRY-DISPOSITION (countermeasure (c), widened from the first line to the whole verdict file; (a) and (b) not accepted)
Source: s6 `proposals.md`, `## V12` (2026-10-24).
Instances: 2 (#2735 verdict 5a03e901 line 15; #2741 verdict b5c2cd2a line 18), each a refusal at post for a home-directory path, each costing a full re-review (30 to 60 min of an opus seat, per the filing) and 3 wasted confirm tries. The gap is in the tree: `git show origin/main:tools/audit/seat/bus.sh` guards the pushed commit message and the first line (`ref_privacy.py guard`, #2310; self-test at "push-verdict refuses a first line naming a host path"), not lines further down the file.
Cost: XS -- a scan of the verdict file with `ref_privacy.HOME_DIR` in `push-verdict` that names the offending line and pushes nothing, plus two self-test rows; local, no API.
Binding: (c) is cheapest in total cost because the reviewer repairs in its own session in minutes, where a refusal at post forces a re-review; it uses the rule's single owner (`ref_privacy.py`). (a), relay normalisation to `~/`, is REJECTED: the path would already sit in the pushed `verdict/` blob, so the leak ref_privacy exists to stop has happened, and the posted comment would differ from the ref. (b), a prompt line, is unmeasured and optional on top of (c); not accepted alone. Carried on R10-FLY-CARRY-DISPOSITION, which already edits `push-verdict` (P40).
Carry text (for `append-carry R10-FLY-CARRY-DISPOSITION`, citing `triage: dev/programme/triage/s6-batch8.md#P76`): "`bus.sh push-verdict` refuses, and pushes nothing, when any line of the verdict file matches `ref_privacy.HOME_DIR`, naming the line number (today only the commit message and first line are guarded; #2735 and #2741 were refused at post for a path at line 15 and 18, a full re-review each). Controls: the same verdict with the path as `~/...` or removed pushes (null); a path in the first line still refuses as before; one self-test row, one mutant."
