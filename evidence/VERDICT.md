Fix review: blocked f92442065832f5ccbe397882b73c79c173ab4dd7 other: the body's ## Figures still asserts R10-ORCH-BEATD "already carries P197" — the exact claim round 1 blocked and 996eb1df1's own message calls false (0 P197 in the roster); the repair landed in s6-batch36.md but not in the body — and the ruling's cost reads one of the destination group's 34 carries, missing P97(b) at index 21 which already carries the per-instance alive entry, the sweep arm and the DUPLICATE print it prices as new
bus-nonce: 985f4ae3abf1885e15383bef6f809549

Head reviewed: `f92442065832f5ccbe397882b73c79c173ab4dd7` (re-read at the PR and at `git rev-parse origin/fix/triage-s6-batch36` before writing: unchanged).
Base: `524c1896b6943b3da03d6cad61420ced31e14c9c` (the batch's stated base; merge base).
Worktree: `/Users/timmalmstrom/hpo-seats/r10s6/rev-2877`, detached at the head.
Evidence: `/Users/timmalmstrom/hpo-seats/r10s6/rev-2877-ev/` (`EVIDENCE.md` and the numbered files it lists).
Round: 1 at this head; the prior verdict is at `b8c62d10…` (head `6d58fa0bc`).

## Verdict

blocked. The DEFER decision and every count that supports it reproduce exactly, as does the `roster_edit.py` gate. What fails is the same false tree-fact round 1 blocked, still standing in the body after a commit that repaired only the batch file, plus a destination-group read that prices already-carried work as new.

## F1 (blocking) — the body's `## Figures` still says BEATD "already carries P197"

- **Claim.** The PR body's `## Figures`, bullet 3: "`R10-ORCH-BEATD` is `not-started`, size L, and **already carries P197**: `git show origin/main:dev/programme/rosters/wave-r10-groups.json`, filtered to that group."
- **Evidence.** The body's own enumerator prints nothing matching P197: `git show origin/main:dev/programme/rosters/wave-r10-groups.json | grep -c P197` = **0**, and the same at the batch's stated base `524c1896b` = **0**; all three files under `dev/programme/rosters/` = **0**. The batch file at this head says the opposite (lines 10-13: "P197 is deferred to that group and sits in its carry 13 (index 12) … the roster holds no `P197` string"). Commit `996eb1df1`'s message says so in terms: "The ruling **and its figures** claimed R10-ORCH-BEATD 'already carries P197'. The roster holds no P197 string at origin/main …". The correction changed `s6-batch36.md` (+12/−5, 78→85 lines) and did not touch the body. See `01-p197-body-vs-roster.txt`.
- **Harness.** The body names its own instrument — the `git show … filtered to that group`. Run alone, it prints no P197. Round 1 re-derived the same absence over every roster branch; I reran the base and the head.
- **Metric.** Occurrences of `P197` in R10-ORCH-BEATD's object: **0** (also 0 across every roster file). The corpus uses "carries P<n>" literally: `s6-batch34.md:102` says P197 is "deferred" and needs "no new carry".
- **Perturbation.** Insert the literal `P197` into one carry string of a copy of the roster; the grep count moves 0→1 and the body's sentence becomes true. At this head it is false, and the command beside it refutes it.
- **Why this blocks.** `fix-review.md` step 8: a quoted figure that does not re-derive is not verified. Round 1 gave this as one of two one-line repairs (batch and body); only the batch half landed. The body describes a different tree than the diff does.

## F2 (blocking) — the cost/coverage read takes 1 of the destination group's 34 carries

- **Claim.** `s6-batch36.md:57-64` prices the item "as filed" as "one file per seat instance plus a renewal on every pass, an arm in the sweep and its self-tests, and a second liveness source (renewal age)", and lines 14-16 conclude "The one element that survives is a launch record". The ruling reads the group only for the P197 string (lines 12-13) and its carry 13 (line 11).
- **Evidence.** At the batch's own base `524c1896b`, R10-ORCH-BEATD has **34** carries; index 21 (1-indexed 22) is P97(b): "read standing-seat liveness from **one alive entry per seat id under each role** … print `DUPLICATE seat <role>: <id> <id>` when two ids of one role are fresh", accepted at `s6-batch21.md:9-11`, with its self-test and mutation proof written into the carry. That is the per-instance file, the sweep arm, and the duplicate print the cost line prices as new. The batch file names neither `P97` nor `DUPLICATE` anywhere. See `05-beatd-carries.txt`.
- **Harness.** `git show 524c1896b:dev/programme/rosters/wave-r10-groups.json`, enumerate the group's carry list; `git grep -nE 'P97|DUPLICATE' dev/programme/triage/s6-batch36.md`.
- **Metric.** Carries in R10-ORCH-BEATD: 34; relevant already-carried: 1 (index 21); mentions of P97/DUPLICATE in the batch: 0.
- **Perturbation.** Remove index 21 from a copy of the roster; the cost line then describes new work and the claim holds. At this base it does not. The DEFER can survive, but the ruling must say the seat-side per-instance entry and its sweep arm are already accepted (P97b) and that only the launch-side record and the extra fields are new.
- **Why this blocks.** The brief's live-risk class: a general claim whose support is a read over a subset of the sites. The batch read one of 34 carries and generalised about the group's contents and the item's cost.

## F3 (finding) — "the two running" loop scripts is a false enumeration

- **Claim.** `s6-batch36.md:52-55`: "the two running (`tick_loop.sh`, pid 7716, and `roster-loop.sh`, pid 99863) … and w71's `loop.sh`/`watch.sh` have no process at all".
- **Evidence.** At review time four persistent loop-like processes were live: 7716 `tick_loop.sh`, 7727 `bash -c 'while :; do … wt_sync.sh …; sleep 900; done'`, 92999 `state_docs.py beat`, 99863 `roster-loop.sh`; 76559 is gone. `wt_sync.sh` is a tree script (`tools/audit/seat/wt_sync.sh`), so "not one of the loop scripts in the tree" is not established by "the two running". The conclusion still stands: no tree file writes the plain HOLD line (`git grep 'no v7.0.5 tag'` hits only the batch), and neither omitted loop writes the ledger. See `06-loops.txt`.
- **Metric.** Running loop-like processes: 4, not 2.
- **Perturbation.** Stop 7727/92999 and the sentence is true; the writer remains unidentified either way.

## F4 (finding) — "This seat's ledger lines carry a `; main <sha>` annotation" is over-broad

- **Claim.** `s6-batch36.md:33-34`.
- **Evidence.** From the snapshot: 45 lines carry `; main <sha>`, first at 08:12:52 (line 1330); 20 of the seat's non-plain lines carry none (its RULED/PUSHED/ESCALATED/ACK/RECONCILED lines, e.g. 09:22:53, 09:33:26, 09:51:38), and one HOLD carries "; main moved …" in another form. True of its periodic HOLD cadence in the cited window; false as written of "this seat's ledger lines". See `04-ledger-classification.txt`.
- **Metric.** 45 of the seat's 65 identified lines; first main-sha line 08:12:52.
- **Perturbation.** Annotate the 20 lines and the sentence becomes true.

## F5 (finding) — the body's `## Red checks` premise is false at the head

- **Claim.** "A ref with no pull request has no checks".
- **Evidence.** The head is PR #2877 and carries **55** check-runs: 38 success, 17 skipped, **0** non-success (`02-check-runs.txt`). The conclusion "`none`" is right; the stated reason is stale and a reader could take it as "nothing ran".
- **Metric.** 55 runs; 0 red.
- **Perturbation.** File a red run and the premise is irrelevant while the conclusion turns false.

## F6 (finding) — the body's `## Head` misstates the branch

- **Claim.** "this seat's commit `1b84be41` is the whole of its diff against `524c1896b`, and `6d58fa0bc` adds only the opener's delivery row" and the head "then merges origin/main `524c1896b`".
- **Evidence.** Two commits touch the batch file: `1b84be415` (78 lines) and `996eb1df1` (85 lines, +12/−5). The head's parents are `6d58fa0bc` and `996eb1df1`; `524c1896b` is `1b84be415`'s parent, i.e. the base, and is not merged at the head. See `03-head-topology-and-body.txt`.
- **Metric.** 2 commits; 78→85 lines; parents ≠ 524c1896b.
- **Perturbation.** Drop `996eb1df1` and the sentence becomes true.

## F7 (unsettled) — "this seat's first line" in the corrected arrival-order paragraph

- **Claim.** `s6-batch36.md:36-40`: "a plain-`HOLD` cadence starting before this seat's first line with no gap over 7 minutes".
- **What I could verify.** "No gap over 7 minutes" is true: 222 plain lines, 20:56:28Z→15:19:15Z, largest gap **302 s**. But the plain cadence's first line (20:56:28, ledger:1171) is *after* the first `triage s7:` line (20:53:33, ledger:1150); the sentence is true only if "this seat's first line" means the seat instance's first *annotated* line (08:12:52), and nothing fixes when `a1c1b98c` started — the launch ledger was backfilled (ORCH-QUEUE.md:1507). The batch also still calls the plain writer "the second writer" while the same correction says the arrival order is unresolved (round 1's F2, non-blocking). Say which referent is meant, or drop the label.
- **Metric.** First plain line 20:56:28 vs first triage-s7 line 20:53:33; first annotated line 08:12:52.

## What I tried to break and could not

- R1 — the 18 plain lines, their 5:00–5:01 spacing and the four in the 21-minute stall: exact (`04-ledger-classification.txt`).
- R2 — `seat-ledger.md:1149` and `:1334`: exact (three seats at 21:15Z; merge RESTART 08:19:56Z, dead since 22:16Z).
- R3 — `roster_edit.py`: the body's mutation proof and null control reproduce exactly, including the absent-file and P999 refusals.
- R4 — R10-ORCH-BEATD: `resume.stage` = `not-started`, `size` = `L`; 208 roster groups at the base.
- R5 — P197 absence: 0 everywhere, at the base and at origin/main (this is F1's fact).
- R6 — check-runs, scope: 55 runs, 0 non-success; the diff is the batch file and the delivery row, nothing outside the seam.
- R7 — pids 7716/99863 live, 76559 gone, `roster-loop.sh` has no `triage`/`HOLD` write, w71's scripts have no process.

## Could not establish

- The dispatch record for this review's nonce. `$S/dispatched` has one #2877 line, at `6d58fa0bc` with nonce `f5ca16fa…`; no line names `f92442065` or `4c58667c…`, so `bus.sh push-verdict` cannot bind it (the exact refusal is in the report).
- `a1c1b98c`'s start time; the plain writer's identity and its output outside the ledger.

## RESULT lines

RESULT F1 blocking: body ## Figures "already carries P197" false — 0 P197 in wave-r10-groups.json at origin/main, at 524c1896b and in every roster file; repaired in s6-batch36.md, not in the body.
RESULT F2 blocking: R10-ORCH-BEATD already carries P97(b) at index 21 (per-seat alive entry, sweep arm, DUPLICATE print); the cost line and "the one element that survives" read 1 of 34 carries; 0 mentions of P97 in the batch.
RESULT F3: "the two running" loop scripts — 4 loop-like processes live (7716, 7727 wt_sync while-loop, 92999 state_docs beat, 99863); conclusion (writer unidentified) still holds.
RESULT F4: "this seat's ledger lines carry a `; main <sha>`" — 45 of 65; 20 without; first main-sha line 08:12:52.
RESULT F5: body ## Red checks premise false at head — PR #2877 has 55 check-runs (38 success, 17 skipped, 0 red); conclusion "none" correct.
RESULT F6: body ## Head — 2 commits touch the batch (78→85 lines); parents 6d58fa0bc + 996eb1df1, so 524c1896b is the base, not merged at the head.
RESULT F7 unsettled: plain cadence 222 lines 20:56:28Z..15:19:15Z, max gap 302 s; "this seat's first line" has no fixed referent (launch ledger backfilled).
RESULT pass: 18 plain lines 08:13:15..09:38:27, four in the 21-min stall; seat-ledger 1149/1334 exact; roster_edit gate and controls exact; stage/size exact; 208 groups; 0 red check-runs; diff scope 2 files.
