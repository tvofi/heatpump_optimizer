# Wave-1 drain plan: 16 open PRs (orchestrator, 2026-10-18)

Goal: get the board to ≤4 open PRs, then stamp, then open wave 2 under the soft cap (6 open, ≤2 on coordinator.py).
Re-plan on every verdict, merge and red. The order is: merges, then red repairs, then owed openers, then reviewers.

## Principles

1. **Batch by merge mechanism, not by group.** Every PR that has a merge verdict at its head and needs nothing else rides one train with `--overlap --approval-carry --pre-flight --free-holders --skip-bad`. Post a #201 note before each batch.
2. **Recarry only inside the train**, at merge time. Never rebase a PR while it is under review: a moved head throws the verdict away.
3. **Carry verdicts for main-only moves.** A head that moved only by merging main gets a carry verdict, not a full re-review.
4. **Serialise coordinator.py**: #2368, then #2411, then #2391 (oldest edge first). The next one's fixer folds the previous merge in before its reviewer runs, so it is reviewed once.
5. **Fold, don't add.** Every roster edit goes into #2417, so it gets one delta review; #2415 rides behind it. No new roster PR.
6. **Instruments first.** raise-hold, openpr-silent/cap, cloud-shape (#2419) and roster-ops each remove a manual stop from every later batch. Their reviewers go out first.

## Batches

| batch | PRs | mechanism | gate | blocks on |
|---|---|---|---|---|
| A | #2394, #2416 | t16 train (running) | in progress | — |
| B | #2379, #2373, #2401 | budget, non-raise: mandate review at head, then direct `merge_pr.sh` in p4→p5 order; once raise-hold lands, the train instead | #2379 approved; #2373 and #2401 need recarry plus a mandate review at the new head | after A (same base move) |
| C | #2418 | record automerge | record check | none, any time |
| D (instruments) | #2419, raise-hold PR, openpr-silent PR, roster-ops PR | one train batch as their verdicts land | cloud reviewers on return | #2419 fixer round 4 |
| E (roster) | #2417 (+ all roster edits), then #2415 | the train, in that order | delta review of #2417 at the roster tip | roster-ops in D |
| F (returned fixers) | #2390, #2404, #2406, #2408, #2399 | reviewer per head, then one train batch per ≥2 merge verdicts | verdict at head | their fixers or reviewers (all out) |
| G (coordinator.py) | #2368, then #2411, then #2391 | single-PR train each, in that order | verdict at head; #2368 is a raise and needs `budget-raise-gate` green | serial |

The batches overlap. While A runs, the reviewers for D, F and G work in the cloud (no cap). The train never sits idle while one PR waits.

## Dynamic rules

- **On a merge verdict:** if any other PR is merge-ready, batch them; otherwise launch a single train only when nothing will be ready within about 20 min.
- **On a blocked verdict:** resume the original fixer at once; re-plan its batch slot.
- **A head moved after its verdict:** if only main moved, ask for a carry verdict; otherwise re-dispatch the reviewer at the new head (bus dispatch on every head).
- **Red on an untouched file class:** check main first; if main is red, that becomes a red repair and jumps the queue.
- **Board ≤4:** stamp, then open the waiting handoffs in critical-path order up to the cap.

## Expected wall clock

A and C: under an hour. B: about 1–2 h (three direct merges with recarry). D and E: about 3–4 h, bounded by the fixers. F and G: about 4–8 h, bounded by the #2368 raise and the coordinator.py serial chain. Target: the board at ≤4 within about 8 h, then stamp.

## Folded follow-ups (21:58Z)
- orchestrator.md "never pass --subject on a merge" -> fold into R10-RCA-FRICTION (already a policy-line PR, parked under cap); its fixer adds the line before open. Mandate review at merge.
- tick MERGE_PR misses "<title> (#N)" merges -> fold into #2422 (R10-OPENPR-SILENT, owns orchestrator_tick.py); its fixer adds it in the post-main-fix recarry pass, same reviewer.
- delivery-status OVERDUE (#2413/#2412/#2407 rowless) -> #2420 update with probe/rec-2420, first after MERGE-SUBJECT merges.
- 22:20Z TRUST-RELATIVE handoff CODE 06bbc1ec BODY 054467c8 -> touches coordinator.py (comment) => joins batch G coordinator.py serial after #2391; tests/closures.json inert_reads conflicts with #2368/#2391/#2411 resolved by the merge driver -> train recarry does the local main-merge (GitHub can't). Part of #2252 (stays open).
- New finding (no defer): HOUSE_LOSS_MAX_STEP rate limit can no longer bind -> new group R10-DEAD-RATE-LIMIT (coordinator.py two call sites + 3 harnesses), roster fold; dispatch after TRUST-RELATIVE merges.
- 22:25Z tvofi: return detection belongs in the tick (via cloud_relay #2419). Gap found: #2419 covers probe/rev-* and open-PR handoffs, NOT other probe/* returns (design/repair seats) nor handoffs with no PR yet. Fold into #2419's post-main-fix recarry pass: ONE probe arm scanning all probe/* (rev-* -> relay+confirm, everything else -> OWED until disposed; level not diff) replacing the rev-only scan, plus PR-less handoff refs + self-test. Stopgap until merged: orch/cloud/ref_watch.sh (pid 98589) -> owed.log REF-MOVED; retire it when #2419 lands.
