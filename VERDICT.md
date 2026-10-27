Fix review: blocked b95d3faf8d1ebf1a03d26d39a593ad91e410b891 prior: round 2's F3 and F4 are unrepaired at this head — "the two running" is four live loop-like processes and "this seat's ledger lines carry a `; main <sha>` annotation" is false of its own ESCALATED/ACK/RECONCILED/RULED/PUSHED lines — so two wrong claims remain in a record whose only product is the truth of its claims
bus-nonce: 040a5a18f0d96ae5692e5eaa9182c7bc

Head reviewed: `b95d3faf8d1ebf1a03d26d39a593ad91e410b891` (re-read at `git ls-remote origin refs/pull/2877/head` and `refs/heads/fix/triage-s6-batch36` before writing: unchanged at both).
Base: `524c1896b6943b3da03d6cad61420ced31e14c9c` (the batch's stated base; `git merge-base 524c1896b 35a165fc0` prints it). origin/main is now `67178dc6a`, merged at the head.
Worktree: `~/hpo-seats/r10s6/review-2877/wt-b95d3fa`, detached at the head.
Evidence: `~/hpo-seats/r10s6/review-2877/ev/` (files `01`–`15`, named below).
Round: 3 at this head. Prior verdicts: `a310c3cf6` (round 1, head `6d58fa0bc`) and `5bad54533` (round 2, head `f92442065`).

## Verdict

blocked. The ruling is sound and most of the record re-derives exactly: the DEFER, its P97(b) cost, the P197 absence, the ledger cadence, the roster_edit gate. What blocks is that two round-2 findings are untouched at this head and are still wrong claims, in a record whose only product is the truth of its claims; plus the body still calls an ancestor "the head" and its `## Red checks` describes an earlier head.

## F1 (blocking) — round 2's F4 stands: "this seat's ledger lines carry a `; main <sha>` annotation" is false

- **Claim.** `dev/programme/triage/s6-batch36.md:33-34` — "This seat's ledger lines carry a `; main <sha>` annotation and stopped for 21 minutes (last line before the stall 08:54:25Z, next 09:15:38Z) ...".
- **Evidence.** In `~/hpo-orch/r10s6/seat-ledger.md` only **32** `triage s7:` lines contain the literal `; main ` (first at ledger:1330, `08:12:52Z`). The seat's own operational lines carry none: ESCALATED `09:22:53Z` (ledger:1372), ACK `09:33:26Z` (1380), RECONCILED `09:34:28Z` (1382), RULED V124 `09:51:38Z` (1387), PUSHED (1388), CONTROLLED (1394), #2877 bookkeeping (1399), RULED V125 (1430), batch-37 HOLD/ruling (1436, 1439), PUSHED batch 37 (1442). See `15-ledger-annotation.txt`.
- **Metric.** 32 lines with `; main `; **11** of the seat's own non-plain lines without it.
- **Perturbation.** Add `; main` to those 11 and the sentence becomes true; at this head it is false.
- **Why this blocks.** Round 2's F4 named this sentence; the `35a165fc0` repair changed the arrival-order paragraph and left it. Brief item 5 (each prior finding answered or blocked) and item 2 (a wrong claim is a blocking finding).

## F2 (blocking) — round 2's F3 stands: "the two running" is four live loop-like processes

- **Claim.** `s6-batch36.md:51-55` — "It is not one of the loop scripts in the tree either: the two running (`tick_loop.sh`, pid 7716, and `roster-loop.sh`, pid 99863) write `tick.txt` and `roster s7:` lines respectively ...".
- **Evidence.** `ps -eo pid,etime,command` at review time matches **four** loop-like processes: 7716 `tick_loop.sh`; 7727 `bash -c 'while :; do bash .../wt_sync.sh --scratch ...; sleep 900; done'` (a tree script in a loop); 92999 `state_docs.py beat --apply --push --watch-ref main` (a tree script in a watch loop); 99863 `roster-loop.sh`. `wt_sync.sh` and `state_docs.py` write no ledger line (grep: none), so the conclusion "its source is unidentified" still holds, but the count does not. See `12-process-and-cadence.txt`.
- **Metric.** 4 loop-like processes, not 2.
- **Perturbation.** Stop 7727 and 92999 and the sentence becomes true.
- **Why this blocks.** Round 2's F3, unrepaired; same rule as F1.

## F3 (blocking) — "the second writer" asserts an order the record itself calls unresolved

- **Claim.** `s6-batch36.md:29-30` calls the plain writer "the second writer"; `:36-40` says "Arrival order is unresolved" and puts a plain-`HOLD` cadence starting at `20:56:28Z`, before this seat's first `; main`-annotated line at `08:12:52Z`.
- **Evidence.** 238 exact plain `HOLD (no v7.0.5 tag)` lines, first ledger:1171 `2026-10-26T20:56:28Z`, last ledger:1594 `2026-10-27T16:39:25Z`, largest gap **302 s** (one continuous cadence). The annotated seat's first `; main` line is ledger:1330 `08:12:52Z`, **11 h 16 m later**. The label copies the seat's own `09:22:53Z` line ("second writer started 08:13:15Z"), written before it measured the span. Round 1's F2 and round 2's F7 residual asked for this label to be fixed or dropped; `35a165fc0` fixed the other referent only.
- **Metric.** Plain cadence starts 11 h 16 m before the annotated seat; max gap 302 s.
- **Why this blocks.** A wrong ordering claim, and the record contradicts itself on the same page.

## F4 (finding) — the body's `## Head` still calls `35a165fc0` "the head"

- **Claim.** Body `## Head`, line 9 — "`35a165fc06f3be19d9f51e95348fc014bac6be9f` is the head; `git cat-file -p 35a165fc0 | head -3` prints its single parent `7c5cb7aeb` ...".
- **Evidence.** The PR head is `b95d3faf...` (line 7 says so; `git ls-remote refs/pull/2877/head` agrees). `35a165fc0` is the authored-code/handoff head (`refs/heads/handoff/triage-s6-batch36`), reaching the head through `6a7eb805`. See `01-head.txt`, `03-head-graph.txt`, `11-topology2.txt`. `fix-review.md` step 7 asks the body's head SHA to be the head measured; the first sentence is right, this one is not.

## F5 (finding) — the body's `## Red checks` reports `f92442065`, not this head

- **Claim.** "At `f92442065` this PR carries 55 check-runs — 38 success, 17 skipped, 0 non-success ... `35a165fc0` is unpushed at the time of writing, so it has no runs of its own".
- **Evidence.** The 55 at `f92442065` re-derive exactly. At this head `b95d3fa` the rollup had **43** entries at 16:37Z: 30 success, 11 skipped, 2 in progress, **0 non-success**; `gate` and `pr-contract` had not started at this head. `35a165fc0` has 0 check-runs but is **not unpushed**: it is the pushed `handoff/triage-s6-batch36` head. See `13-checkruns.txt`.
- **Metric.** 55 at f92442065; 0 red at b95d3fa; gate/pr-contract absent at 16:37Z.

## F6 (finding) — the sweep step (1b) sentence is the carry's future edit, not the template's present

- **Claim.** `s6-batch36.md:60-61` — "the sweep arm that acts on it (step (1b) of `tools/audit/seat/sweep_template.md` stops the older id and logs both)".
- **Evidence.** The template's step (1b) restarts an absent or stopped seat and logs the restart; `grep -n 'older\|DUPLICATE' tools/audit/seat/sweep_template.md` prints nothing. The sentence is the P97(b) carry text's own wording about the arm it will add (verified: `s6-batch21.md#P97` says "then stops the older id ... and logs both ids"). True of the carry; the tree today does not do it. Say "will stop".
- **Metric.** 0 occurrences of an older-id stop or `DUPLICATE` in the template.

## What I tried to break and could not

- **The ruling.** DEFER is the right cost/benefit: the motivating writer emits one fixed line, so a convention it does not implement cannot bind it; per-pass renewal and the sweep flag are refused on sound grounds (disagreement with P199's death detection, restart noise on the board); the surviving launch record at dispatch is what the orchestrator adopted at 09:55Z. The seat's own ledger:1387 says the same.
- **The central claim and the instances.** The batch names **one** instance, a real duplicate pair: two independent cadences on one role, one annotated and stalling 21 minutes while the other holds `5:00-5:01`. It is distinct from P97's four 2026-10-25 pairs (tick, roster, merge, dispatch), and it is **not counted twice**: P97(b) is cited only as already-carried cost (index 21), never as a second instance. See `14-central-and-roster.txt`, `06-batch21-p97.txt`.
- **P97(b) and the 34 carries.** `R10-ORCH-BEATD` is `not-started`, `L`, **34** carries (origin/main and `524c1896b`); index 21 (carry 22) is P97(b) with the per-instance alive entry, step (1b), its self-test and mutation proof, and `DUPLICATE seat <role>: <id> <id>`; `s6-batch21.md#P97` is ACCEPT in two parts. See `04-beatd.json.txt`.
- **P197.** **0** occurrences in `wave-r10-groups.json` at origin/main and at `524c1896b`, 0 in every roster file; `s6-batch34.md#P197` DEFERs it to BEATD's carry 13 (index 12), the context-rotation paragraph, and says it "needs no new carry". See `05-p197-and-carry13.txt`, `09-p197-p199-p201.txt`.
- **The ledger figures.** 18 exact plain lines in `08:13:15Z..09:38:27Z` at 300-301 s, four inside the `08:54:25Z..09:15:38Z` stall; 238 plain lines total, first ledger:1171 `20:56:28Z`, largest gap 302 s; `seat-ledger.md:1149` (three seats at 21:15Z) and `:1334` (merge RESTART `08:19:56Z`, dead since 22:16Z) are exact. See `12-process-and-cadence.txt`.
- **The roster_edit gate.** Reproduced the body's mutation proof and both controls: committed P204 = `DEFER`, refusal `... is not an ACCEPT ruling (DEFER)`; mutant ACCEPT → `None`; absent file → `... is not on the roster branch or origin/main`; P999 → `... (no such entry)`. See `10-roster-edit.txt`.
- **Head, scope, conflict, versions.** The head is `b95d3fa` at the PR and the branch; the diff is the batch file and the delivery row and nothing else; `merge-tree --write-tree origin/main HEAD` exits 0; `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched; `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. See `01`–`03`, `11`.
- **The body's `f92442065` figures.** 55 check-runs, 38 success, 17 skipped, 0 non-success, exact. The four batch-file commits: 78/85/89/89 lines with +78/−0, +12/−5, +12/−8, +3/−3, exact; `f92442065`'s parents are `6d58fa0bc` and `996eb1df1`, and `6d58fa0bc` is the delivery row +1. See `11-topology2.txt`, `13-checkruns.txt`.

## Could not establish

- "Both writers `touch` `s7/triage.alive`" (`s6-batch36.md:41`): the file's mtime is advancing, but I cannot attribute a touch to the unidentified writer.
- The head's `gate` and `pr-contract` runs had not started at 16:37Z, so the current body has no CI body-check at this head (it had one at `f92442065`).
- The V124 relay text itself is out of tree; the session state agrees `V124/P204` (ledger:1387 `RULED V124 DEFER (P204, batch 36)`; `s6-batch37` continues V125/P205), and `proposals.md` still has no V124 entry, as the batch discloses.

## RESULT lines

RESULT F1 blocking: round 2's F4 unrepaired — only 32 triage lines carry `; main `; 11 of the seat's own non-plain lines carry none.
RESULT F2 blocking: round 2's F3 unrepaired — four loop-like processes live (7716, 7727 wt_sync, 92999 state_docs beat, 99863), not two.
RESULT F3 blocking: "the second writer" contradicts the record's own unresolved order; the plain cadence starts 11h16m before the annotated seat.
RESULT F4 finding: body ## Head calls 35a165fc0 "the head"; the head is b95d3fa.
RESULT F5 finding: body ## Red checks reports f924420's 55; b95d3fa has 0 non-success but gate/pr-contract have not started; 35a165fc0 is pushed, not unpushed.
RESULT F6 finding: sweep_template step (1b) contains no older-id stop or DUPLICATE; it is the carry's future edit.
RESULT pass: ruling sound (DEFER; launch record); one instance, distinct from P97's four, not double-counted.
RESULT pass: P97(b) index 21 and 34 carries exact; P197 0 everywhere; carry 13 index 12 exact.
RESULT pass: 18 plain lines/300-301 s/four in stall; 238 plain lines first 20:56:28, max gap 302 s; ledger 1149/1334 exact.
RESULT pass: roster_edit mutation proof and controls exact; head matches PR; diff 2 files; merge-tree 0; versions/claims untouched; structure PASSED; f924420 55 (38/17/0) exact.
