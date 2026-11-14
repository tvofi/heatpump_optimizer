# Proposal triage, session s12, batch 131 (P402)

The rolling batch after batch 130. Facts were read at origin/main `b8f67a775`, 2026-11-10T00:41Z, and re-derived there after a fix review found the first ruling stale: it read `be813ecd4`, which predates the change it asked for.

## P402: stamp-flush-train-hold-deadlock, the record flush waits on a train hold it never names

Verdict: REJECT, already landed. Both halves of the proposal are in the tree, so no group is created.
- **The flush half: landed.** `record_flush` takes a `held` collaborator and names a live train hold. It spends no dispatch under one and never refuses on one. That is the whole of the proposal's flush half, and it is pull request #3280 (R10-FLY-STAMP-FLUSH-HOLD, merge `aaaec2128`, 2026-11-07T18:26+01).
- **The signal half: landed.** `stop_ignored` in `tools/audit/seat/merge_train.py` drops a second TERM or HUP while the train unwinds, so the hold DELETE is issued. It came in with the same pull request (`6cc9aa30b`, "ignore a second TERM or HUP during the unwind so the hold DELETE is issued"). The probe the first ruling set as a step, a second TERM during the unwind, is its design case.
- **The train.sh trap half: REJECT, as before.** `pr_exit_trap` already TERMs `merge_train.py` first. SIGKILL and a host crash run no trap, and the beat's `HOLD_MAX_AGE_S` bound covers those.

Source: the orchestrator's queue line `s12-stamp-flush-train-hold-deadlock`, 2026-11-07.

Instances, re-read at `b8f67a775`:
- **Ancestry:** `git merge-base --is-ancestor aaaec2128 origin/main && echo anc` prints `anc`.
- **The flush:** `tools/release/stamp.py` `record_flush` has `held=train_hold` and spends no dispatch while `hold` is set (the `if not hold and count < FLUSH_MAX_DISPATCHES` line). `train_hold` is a zero-REST read (`git ls-remote`, then the fetched commit's committer date and `pid=` message). `hold_bound_s` reads `HOLD_MAX_AGE_S` off `nightly.yml`'s source, so the bound has no second literal. `git grep -c train-hold origin/main -- tools/release/stamp.py` counts the references the first ruling found absent.
- **Self-test:** the flush block of `stamp.py`'s self-test plants a live hold, a stale hold and an absent hold (the null control), and a mutant dispatching under a live hold, which is caught.
- **The unwind:** `Train.unwind` runs `release_worktrees` and `hold_release` inside `stop_ignored`. The `# mut:stopign` and `# mut:deferdeliver` markers on it are its two mutants.
- **The roster:** `origin/handoff/audit-r10-roster` already carries R10-FLY-STAMP-FLUSH-HOLD (the `rosters/wave-r10-groups.json` group, and `delivery/3280.md` reading `merged aaaec21`). The first ruling's claim that no group owns the flush was false. Batch 132's ruling orders itself after that group.

Cost: none to build. The proposal's benefit, a flush that names a live hold and recovers once it clears, is measured by the self-test arms above, not by the proposed group.

Binding: none. No new group and no new carry.
- A text citing `triage: dev/programme/triage/s6-batch131.md#P402` is refused by `roster_edit.py` `triage_refusal`, because the entry is not an ACCEPT. The roster branch's R10-FLY-STAMP-FLUSH-HOLD brief cites this entry (`git grep -n "s6-batch131" origin/handoff/audit-r10-roster -- dev/programme/rosters`), and that group is the merged #3280. Its citation now resolves to a REJECT, so its brief and the roster's ordering are the orchestrator's to reconcile; a fixer may not write the roster.
- The cause of the stale ruling: the ruling read facts at a base the stamp-flush pull request then changed, hours before the ruling merged (process state d: the process was sound and its precondition changed under it). No countermeasure is proposed in this note.
