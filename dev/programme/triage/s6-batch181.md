# Proposal triage, session s14, batch 181 (P600)

This batch rules `s7/triage-queue-s7.txt` line 279. The bar and the denominators are batch 141's.

Sources:
- origin/main `cbd23f1c8b`. Every line number below is at that commit.
- The roster at `origin/handoff/audit-r10-roster`, read at 09:55Z.
- The live board `$HPO_STATE_DIR/tick.txt`, measured from main at 2026-11-11T09:45:32Z, and a copy
  of `owed-unactioned.json`. Every `owed_unactioned.py` run here used `--no-write`.
- No GitHub API calls beyond one `gh pr list` for #3425's state.

## P600: OWED-CAP-BLINDS-UNACTIONED

Verdict: ACCEPT. The ruling has two arms. It opens the not-started group R10-TICK-RESIDUE-P2 with
`after: [R10-TICK-RESIDUE]`.

Source: queue line 279, 2026-11-11T09:49:37Z, orchestrator s14.

### Measured

**The cap line is unreadable.** The current board's cap line is
`-> OWED handoffs capped at 20 of 46; ...`.
- `orchestrator_tick.py:2427` prints that line, flagged, so it matches `owed_unactioned.FAMILY` (`:56`).
- `key_of` has no pattern for it, so it reaches `raise Unreadable` (`:120`).
- On the live board, `owed_unactioned.py --tick tick.txt --state <copy> --no-write` exits **rc 2**
  `UNREADABLE`.
- That one line blinds all 85 keys on the board.

**Null control.** The same board with only the cap line removed (`grep -v '^-> OWED handoffs capped
at'`) exits **rc 1**. It reads 85 keys and reports 2 UNACTIONED:
- `audit-r10-roster`, 37 sweeps, 110.7 h;
- `r10-process-slim`, a handoff stranded for 47.2 h, `repair=update`.

Both have been standing unflagged while the check was blind.

**Held triage refs crowd the cap.** The 20 `OWED handoff:` lines printed under the cap
(`CAP_ORPHANS = 20`, `:182`) are dominated by triage refs:
- 14 of the 20 (70%) are `triage-s14-batch*` refs. By ruling these open no PR until the stamp sweep.
- Only 6 are fixer or record work.
- 26 more orphans are hidden "next pass". That pass never comes while the held refs stay.

### Bar

- **(a) It removes a recurring slip class.** This is the owed-but-unactioned detector itself. It
  has been dead on every sweep since at least 08:21Z, which is more than 1.5 h at the beat cadence.
  On the blinded board it hides 2 real items, one of them 110 h old.
- **(b) It is a >20% improvement on the owed-work signal.** 70% of the capped OWED-handoff slots go
  to refs that are owed nothing until the stamp sweep. Listing them last returns those 14 of 20
  slots to actionable lines.
- **Cost.** A one-pattern change in `key_of` and a sort key in `orphans()`. The runtime cost is
  under 1 ms per sweep.

### Carry (for R10-TICK-RESIDUE-P2)

R10-TICK-RESIDUE owns both files and is carry_receivable. Its PR #3425 holds a `merge` verdict at
`c93903f075` (09:34Z) and is heading to the train. A carry there would re-open a merge-ready PR, so
this ruling opens a not-started sibling that runs after it instead.

1. **`tools/audit/seat/owed_unactioned.py`, `key_of`.** Read the tick's level line
   `OWED handoffs capped at <n> of <m>` as a non-obligation and skip it. The individual
   `OWED handoff:` lines carry the obligations. Do not raise on it.
   - The self-test gains that board line: before the fix it gives rc 2 UNREADABLE, after it a
     computed result.
   - Mutation proof: deleting the new pattern returns rc 2.
2. **`tools/audit/seat/orchestrator_tick.py`, `orphans()`.**
   - Order `stranded` so that held triage and record batch handoffs come after every other topic
     before the `[:CAP_ORPHANS]` slice. Held batches are topics `triage-*` and the record batches
     the stamp sweep opens.
   - Keep them listed: never exclude them, because `bus.sh orphans --exclude-topic` would hide them
     for good.
   - Print the held count in the cap line.
   - Self-test: a 25-line `stranded` holding 14 held refs prints all 11 others within the cap.

### Local workaround, until the group merges (verified)

Run the unactioned check on the board with the one cap line filtered out:
`grep -v '^-> OWED handoffs capped at' tick.txt > tick-nocap.txt`, then
`owed_unactioned.py --tick tick-nocap.txt --state owed-unactioned.json`.

Measured with `--no-write`: rc 1, 85 keys, 2 UNACTIONED.

The two other forms do not work:
- **An acks-file form.** `key_of` raises before any ack is read.
- **`cloud_relay.sh dispose` on the held refs.** It writes the relay ledger's `dispositions.tsv`.
  `bus.sh orphans` never reads that ledger, so the refs stay stranded and still fill the cap.
