# Proposal triage, session s14, batch 161 (P574)

This batch rules `s7/triage-queue-s7.txt` line 256. The bar and the denominators are batch 141's.

Sources:
- origin/main `dbd1ab5b07`. Every line number below is at that commit.
- The tick's live output, `r10s6/tick.txt`, copied at 04:36Z (268 lines) to the triage scratch
  directory, and `r10s6/owed-unactioned.json`, copied there as the state.
- No GitHub API calls.

## P574: OWED-CHECK-UNKEYABLE-CAP-LINE

Verdict: ACCEPT. The fix is at the writer, with a pin that drives the writer's real output into the
reader. The proposal's reader-side alternative, skipping the exact literal, is REJECTED. The fix is
a carry to R10-TICK-RESIDUE (PART 2).

Source: queue line 256 (2026-11-11T04:31:55Z, orchestrator s14).

Instances:
- **The writer.** `orchestrator_tick.py` lines 2426-2429 emit a flagged line when more than
  `CAP_ORPHANS` (line 182, 20) handoffs are stranded:
  `OWED handoffs capped at {CAP_ORPHANS} of {n}; the rest print next pass once these are
  discharged`.
- **The reader.** `owed_unactioned.py` line 56 (`FAMILY`) matches `^-> (OWED|...)`, so the cap
  line is in the family.
  - The key function (lines 95-120) has no branch for it, because `OWED handoff: (\S+) ` needs
    `handoff:`. It raises `Unreadable` at line 120.
  - That raise is deliberate for an unknown owed shape: its self-test, line 336, is "an owed line
    it cannot key: exit 2".
- **Reproduced at 04:36Z, read-only**, with `python3 -I owed_unactioned.py --tick <f> --state
  st.json --no-write`:
  - The live tick (`OWED handoffs capped at 20 of 23`): rc 2, `UNREADABLE: an owed line names no
    topic or pull request: -> OWED handoffs capped at 20 of 23; ...`.
  - **Null control**, the same tick with only that line removed (`grep -v`): rc 1, `owed: 51
    key(s) on board 2026-11-11T04:27:12Z; 0 acknowledged, 2 unactioned`.
  - So while the cap holds, the cap line alone hides two unactioned owed items.
- **No other writer literal in the family is unkeyable.**
  - Every flagged `self.line` in `orchestrator_tick.py` that opens with a family prefix was
    listed: lines 729, 738, 744, 746, 752, 972, 1043, 1139, 1168, 2423 and 2427.
  - Each except 2427 has a key branch.
- **Not measured: how many passes it has held.** The beat's journal records the owed-check job as
  `outcome=ok rc=0` on every pass, so the row's UNREADABLE does not reach the journal. It holds
  whenever more than 20 handoffs are owed: 23 at 04:27Z, and 24 at 04:30Z per the queue line.

Cost:
- **(1) The writer moves the cap summary out of the owed family.**
  - The line at 2427 stops opening with `OWED`, for example `handoffs owed beyond the cap: 3 of
    23 print next pass once the first 20 are discharged`. It stays flagged.
  - The summary is not an owed item: it names no topic, and nothing can acknowledge it. The 20
    lines above it already carry the owed keys, and the remainder prints as keyed lines on a
    later pass. So nothing keyable is lost.
- **(2) Pin the writer's own output through the reader, not a copy of its literal.**
  - In `orchestrator_tick.py --self-test`, drive the orphan section with `CAP_ORPHANS + 1`
    stranded refs (a stub `bus.sh`, in the stub style already used there).
  - Feed every flagged line it emits through `owed_unactioned`'s `FAMILY` and key function.
  - Assert that each family line keys and that the run is not UNREADABLE.
  - This pins the whole emitted section, so a future family literal with no key branch fails in
    the writer's own self-test.
  - Mutation: restore the `OWED` prefix at 2427 and the pin goes red.
  - Null control: the section at `CAP_ORPHANS` exactly (no cap line) is green both before and
    after.
- **REJECTED: the reader skipping the exact literal.**
  - It couples `owed_unactioned.py` to the writer's prose. A reword of the writer then
    re-breaks the check while the reader's self-test, pinned to the old literal, stays green:
    the writer-green, reader-red shape.
  - It also adds an exception to a deliberate fail-loud rule for a line that never belonged in
    the family.
- **Size: S.** One line of writer text plus one self-test case. Neither file has a row in
  `tests/structure_budgets.json` (`git show origin/main:tests/structure_budgets.json | grep -cE
  'orchestrator_tick|owed_unactioned'` gives 0).
- **No new file, no new check, no new seat time.** The pin runs inside the existing
  `--self-test`.

Binding:
- While more than 20 handoffs are owed, the owed check is UNREADABLE on every pass and produces no
  UNACTIONED block. The orchestrator then loses the one instrument that says which owed items
  have outlived a sweep. At 04:36Z that was 2 items.
- The fix is a one-line text change plus one self-test case.
- Severity: a repair of an observed wrong behaviour in existing machinery, so the machinery bar
  is met.

Routing:
- R10-TICK-RESIDUE owns both `orchestrator_tick.py` and `owed_unactioned.py`. It is in progress
  as PR 3425, so this carry takes the PART 2 prefix.
- Carry file: `b161-P574.txt`, items (1) and (2).
