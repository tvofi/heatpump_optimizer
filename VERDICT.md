Fix review: blocked 6d58fa0bc404485ca96f543b0c894d6ea8e72a59 other: the ruling and body assert R10-ORCH-BEATD "already carries P197"; origin/main's roster holds 0 P197 hits and the body's own git-show enumerator prints none, so the routing's stated evidence does not exist

bus-nonce: f5ca16fa7384a88e59e0b3877c49e680

Head reviewed: 6d58fa0bc404485ca96f543b0c894d6ea8e72a59 (this head; re-checked at post time)
Merge base: 524c1896b6943b3da03d6cad61420ced31e14c9c
Authored code head: 1b84be415587523f0e26ebbbf274b2e871ef2334
Round: 1

## Verdict

blocked, on one false tree-fact. The DEFER decision, its route, and every figure that supports the decision reproduce exactly (R3, and the two controls in R5/R6). What fails is a claim about a second party's roster: the ruling and the body both assert that R10-ORCH-BEATD "already carries P197", and it does not. The repair is one line in `dev/programme/triage/s6-batch36.md:10` and one line in the body's `## Figures`; the decision does not need re-cutting.

## F1 (blocking) — "already carries P197" is false, and the body's own enumerator refutes it

- **Claim.** `s6-batch36.md:10` — "(`not-started`, L; the sweep/beat is its surface, and it already carries P197)" — and the body's `## Figures` — "`R10-ORCH-BEATD` is `not-started`, size L, and already carries P197: `git show origin/main:dev/programme/rosters/wave-r10-groups.json`, filtered to that group."
- **Evidence.** P197 appears nowhere in the roster: `grep -c P197 dev/programme/rosters/wave-r10-groups.json` = 0, and the same for V117 (0). It is absent on every roster branch including `origin/handoff/audit-r10-roster` (`git grep` = no hits). The only P197 strings in the tree are the two batch files themselves. See `evidence/01-p197-absence.txt`.
- **Harness.** The body names its own harness — `git show origin/main:dev/programme/rosters/wave-r10-groups.json` filtered to that group. Run alone, it prints nothing matching P197. I did not have to build a definition to check this; the body's stated instrument is the check.
- **Metric.** Occurrences of `P197` in R10-ORCH-BEATD's object: **0**. The corpus uses "carries P<n>" literally, not as a synonym for "is routed to": `s6-batch2.md:21` says R10-ORCH-BEATD "carries P45, P46 and P51", and `grep -c` finds each of P45/P46/P51 once in the same roster file. A reader will take batch36 the same literal way.
- **Perturbation.** Remove the claim and nothing about the ruling changes; add the true statement and the routing still holds. The truthful form is: P197 is **deferred** to R10-ORCH-BEATD (batch34), and its item is covered by BEATD's carry 13 (1-indexed; index 12), the orchestrator context-rotation paragraph — which is exactly what `s6-batch34.md` says ("Its carry 13 ... so the item is on the roster and needs no new carry"). So the destination is right and the sentence describing it is wrong.
- **Why this blocks rather than notes.** The body's `## Figures` exists so a reviewer can re-derive each figure, and this one is refuted by the command printed beside it. `fix-review.md` step 8: a quoted figure that does not re-derive is not verified. The fix is one line in each of two places; no decision changes.
- **Carry:** repair on this branch (F1); the DEFER itself is sound.

## F2 (non-blocking note) — the plain writer is the OLDER cadence, and its 14-hour span is undisclosed

- **Claim.** `s6-batch36.md:24-33` calls the plain `HOLD (no v7.0.5 tag)` writer "the second writer", reports "18 of them" from 08:13:15Z to 09:38:27Z, and concludes "it is a separate timer or process."
- **Evidence.** The "separate timer" conclusion is right: the annotated seat stalls 08:54:25Z→09:15:38Z and the plain cadence continues through it (four lines at 08:58:22, 09:03:22, 09:08:23, 09:13:24). But the plain writer is **one continuous cadence from 2026-10-26T20:56:28Z to 2026-10-27T10:58:39Z — 170 lines, no gap over 7 min** — and the annotated seat's first line is 08:12:52Z, so the plain writer predates it by 11.3 hours. The *annotated* seat is the later arrival. See `evidence/02-plain-writer-span.txt`.
- **Harness.** Same ledger and grep the ruling cites; I enumerated the whole plain series and its inter-line gaps rather than the cited 86-minute window.
- **Metric.** Plain-writer lines in the whole ledger: **170** (cited: 18). First plain line 20:56:28Z; first annotated line 08:12:52Z.
- **Perturbation.** Restrict the series to the 08:13–09:38 window and the count is 18 and the four-in-stall control holds (R3) — which is why the DEFER stands either way: a fixed-line shell loop implements no convention whether it started at 20:56 or 08:13. But the "second writer" label inverts the chronology and does not disclose that the writer has run 14 hours, and the orchestrator's 09:30:39Z ruling (which this batch reports) orders the **older** party to stand down on the strength of "first seen 08:13:15Z".
- **Carry:** R10-ORCH-BEATD (owns the duplicate-seat class and the sweep/beat surface).

## What I tried to break and could not

- **R1 — P197 presence.** Failed to find P197 anywhere in the roster, on any branch. (This is F1.)
- **R2 — roster_edit gate.** Reproduced the body's mutation proof and null control exactly: `ruling_verdict(committed,"P204")` = DEFER; `triage_refusal` on the committed file = "is not an ACCEPT ruling (DEFER)"; mutant ACCEPT → None; absent file → "the triage ruling ... is not on the roster branch or origin/main"; P999 → "no such entry". The gate is sensitive to the verdict line, so a DEFER cannot be laundered as a carry. See `evidence/04-roster-edit-controls.txt`.
- **R3 — the decision's counts.** 18 plain lines 08:13:15..09:38:27 at 5:00-5:01; four inside the 21-minute stall; the stall bounds 08:54:25→09:15:38. All exact. See `evidence/03-window-figures.txt`.
- **R4 — the destination.** R10-ORCH-BEATD exists, `resume.stage` = `not-started`, `size` = `L`. Both true.
- **R5 — the launch ledger is not claimed to exist.** `seat-launch.sh` and `launch-ledger` are absent from `git ls-files`; the text says it "needs no repository change" and that repository work "is a separate proposal". The description matches the tree.
- **R6 — the exclusion of the known loops.** `tools/audit/seat/tick_loop.sh` writes `tick.txt` (not the ledger) and neither it nor the out-of-tree `roster-loop.sh` writes a `triage`/`HOLD` line; `roster-loop.sh` writes only `roster s7:` lines. Pids 7716 and 99863 are both live. "Its source is unidentified" holds — I could not identify it either.
- **R7 — classification.** Both new files are `is_inert`=True under `dev/programme/`; `closure.orphan_files()` = 0. A push to main would not go red on `tests/entities.py`.
- **R8 — checks, conflict, versions.** All 55 check-runs on the head are `success` or `skipped`; `gate`, `pr-contract`, `governance / delivery-status`, `tests / closure-scope` all green, so `## Red checks: none` is the check-runs' own answer, not the body's account. `merge-tree --write-tree origin/main <head>` exits 0 (mergeable; the `BLOCKED` state is the draft + required review, not a conflict). `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched; the diff is the two markdown files and nothing else.
- **R9 — the stale-brief disclosure.** The body's claim that V119–V123 were already ruled in batch35 ("merged `c73d8984a`") is true: `c73d8984a` is an ancestor of origin/main, and `s6-batch35.md` holds P199–P203. The seat reconciled rather than re-ruling — correct.
- **R10 — no policy binding.** The ruling routes a DEFER and records prose for a group's carry text; it edits no roster and changes what no seat must do. It explicitly leaves repository work to a separate, separately-costed proposal. Nothing here needs the owner's approving review.

## RESULT lines

RESULT F1 blocking: "already carries P197" false — 0 P197 occurrences in wave-r10-groups.json at origin/main and every roster branch; body's own git-show enumerator prints none.
RESULT F2 note: plain HOLD writer is one continuous cadence 2026-10-26T20:56:28Z..2026-10-27T10:58:39Z, 170 lines, no gap >7min; annotated seat first line 08:12:52Z — "second writer" is the later one.
RESULT pass: DEFER decision and route sound; decision counts (18 at 5:00-5:01; 4 inside the 21-min stall; bounds 08:54:25/09:15:38) reproduce exactly.
RESULT pass: roster_edit mutation proof and null control reproduce exactly (DEFER refused as a carry; ACCEPT mutant passes; absent file and P999 both refused).
RESULT pass: classification holds — dev/programme/ INERT, orphan_files()==0; all 55 head check-runs success/skipped; merge-tree exit 0; VERSION/manifest/notes/claims untouched.
