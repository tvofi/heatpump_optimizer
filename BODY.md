R10-RCA-OWED-UNACTIONED: the root-cause record for tick owed lines that
stood for hours with no action. The owner corrected this class on 2026-10-28 at
19:00Z ("no pr should wait without reason, in particular not CP prs"). This
pull request also builds the countermeasure that passed the cost test,
`tools/audit/seat/owed_unactioned.py`. It runs in `sweep_template.md` step (5),
so a sweep cannot report done while an owed line stands unacknowledged.

The record is `dev/audit/rca/R10-RCA-OWED-UNACTIONED.md`. Its evidence is in
`dev/audit/rca/owed-unactioned/`, and `dev/audit/config/bugclasses.json` cites
it.

**Instances (times from git, the ledger and the orchestrator's queue).** The
standing figures are host-up hours, with the 12:42Z to 15:32Z power loss
removed.

| obligation | standing, host up |
|---|---|
| `triage-s7-batch49` | 5.7 h |
| `r10-review-carry` | 5.6 h |
| `r10-orch-beatd`, critical path, #2916 | 1.9 h |

- `triage-s7-batch49` was routed to the opener at 10:55Z. The opener first
  ran at 17:36Z and refused `BAD-DEST`. The 17:39Z wait named #2909, which had
  merged at 16:41:53Z.
- `r10-review-carry` was routed to the opener at 11:00Z. The opener refused
  it at 17:16Z. "Re-cut owed" was recorded at 17:39Z, and no fixer started.
- `r10-orch-beatd`: the relay printed `HELD-REVIEW #2916` on all 33 of its
  logged passes, while the queue said "Relay updates #2916".
- Three more lines stood past 4 h on the night's 31-sweep board log.

**Process state: (c).** The sweep ran, with 19 board reads between 10:40Z and
18:55Z, and actions were recorded against all three lines. Its unit, a board
read, cannot tell a standing line from a handled one, or from one whose
handling failed. Three things show it:

- The session board's `rc` ignores owed lines.
- Its owed view, `grep | tail -8`, shows 8 of the 26 owed-family lines, and
  none of the tick's `DISPATCH:`, `OWNER FLAG:` or `DESIGN-BUILD:` escalations.
- 15 of the 19 reads used a filter that drops the block. Eleven of them were
  `sed -n '1,/verdict refs/p' | head -40`.

It is not (b): three firmer memory instructions in eight days were each
followed by a recurrence.

**Cost test: build.**

- The countermeasure costs 0.08 s per sweep. Acknowledgements cost at most
  67 min/day: a mean of 5.6 standing keys, at about 30 s per hourly line.
- The defect cost 13.2 host-up hours of idle owed work on 2026-10-28, of which
  1.9 h were on the critical path.
- Recurrence is measured at about once per day: six instances in about 11.4
  host-up hours of observed sweeps, and six owner corrections over four days.

**Owner review at merge.** `.github/workflows/governance.yml` is code-owned. It
gains one `instrument-self-tests` step, which runs the new self-test.

**Owed by the orchestrator, outside the tree.** The orchestrator applies these;
this pull request does not touch them.

- **`orch_sweep.sh` (the session board).** Print the tool's output first and
  fold its exit code into `rc`. Delete the `-- owed (tick)` grep. Put these
  lines directly after `echo "== SWEEP $now =="`:

      echo "-- owed (owed_unactioned.py; exit 1 = an owed line stands unacknowledged)"
      python3 -I "$MAIN/tools/audit/seat/owed_unactioned.py" --tick "$S/tick.txt" \
        --state "$S/owed-unactioned.json" --acks "$S/seat-ledger.md" --acks "$S/s7/ORCH-QUEUE.md" \
        | sed 's/^/    /'
      [ "${PIPESTATUS[0]}" -eq 0 ] || rc=1

- **The split ledger home.** The standing relay writes dispositions under
  `--log <session>/cloud-relay.log`. `tick_loop.sh` was started without
  `HPO_STATE_DIR`, so the tick reads `~/.local/state/hpo`. Its
  `dispositions.tsv` lacks the 08:58Z and 09:12Z dispositions. As a result,
  `roster-b24-wip` and `r10-handoff-bodies` still print `OWNER FLAG` at
  31.2 h and 18.3 h, while `ledger.py level` on the relay's home prints
  `disposed=2` for both. The repair is to start the tick loop in
  `sweep_mech.sh` with `HPO_STATE_DIR` set to the relay log's directory.
- **V179** (triage) covers open pull requests with no owed line: #2919, #2917
  and #2906. It is not duplicated here.

## Head

`b7097883936d96a122f46b1289caf4e6767d44e8`, cut from `origin/main`
`beb570c817c4f56bb56ef0b7e5e4c46d6b1bb2b8`.

## Mutation proof

`python3 -I dev/audit/rca/owed-unactioned/mutants.py .` plants 10 mutants in
a scratch copy of `owed_unactioned.py`. The self-test kills all 10
(`dev/audit/rca/owed-unactioned/mutants_out.tsv`). The mutants, with the number
of self-test checks each one turns red:

| mutant | red |
|---|---|
| fires one sweep late (`>=` to `>`) | 5 |
| an ack never lapses | 1 |
| a stale board reads clean | 1 |
| any ack covers any tip | 1 |
| a re-read board counts a sweep | 1 |
| `DISPATCH:` lines leave the family | 3 |
| a future ack is accepted | 1 |
| an over-long ttl is accepted | 1 |
| an unkeyable line is skipped | 1 |
| an unreadable state starts fresh | 1 |

**It fires on the defect.**

- `dev/audit/rca/owed-unactioned/live_out.txt` reads the live 19:04Z and
  19:12Z boards with the session's real queue and seat ledger, which hold 0
  `OWED-ACK` lines. The first board exits 0, because all 12 keys are new.
- The second board exits 1 with all 12 UNACTIONED. Among them:
  - `r10-orch-beatd`: its `handoff-held #2916 REVIEW` and `repair=review`
    lines, as one entry;
  - `triage-s7-batch49` and `r10-review-carry`, with their `DISPATCH:` lines;
  - both hidden `DESIGN-BUILD` lines.
- `replay_out.tsv` replays the night's 31 boards. The first exits 0 and the
  other 30 exit 1.

## Null control

- With every key acknowledged at 19:13Z, the 19:12Z board exits 0
  (`live_out.txt`).
- The night replay with an acknowledgement re-taken each sweep exits 0 on 31
  of 31 boards (`replay_acked_out.tsv`).
- The self-test's all-clear board exits 0 with 0 keys.
- It never goes green by skipping. These exit 2: no provenance line, a board
  45 minutes old, an owed line it cannot key, and a corrupt state file.
- The unmodified base: `sweep_render.py --self-test` passes 21 of 21 checks on
  main and on this head, and the session overlay renders step (5) with the
  new command.

## Figures

- 21 checks, 0 failed: `python3 -I tools/audit/seat/owed_unactioned.py --self-test`
- 10 mutants, 10 killed: `python3 -I dev/audit/rca/owed-unactioned/mutants.py .`
- 12 keys, then 12 unactioned, then 0 with acknowledgements: `bash dev/audit/rca/owed-unactioned/live.sh . <session>/s7/ORCH-QUEUE.md <session>/seat-ledger.md`
- Night replay, 30 of 31 exit 1, mean 5.6 unactioned keys per sweep; acknowledged, 31 of 31 exit 0: `python3 -I dev/audit/rca/owed-unactioned/replay.py <session>/orch-sweep.log .` and the same with `--acked`
- 26 owed-family lines on the 19:04Z board, 8 shown by the session board's owed block: `grep -cE '^-> ' dev/audit/rca/owed-unactioned/boards/tick-1904.txt` and `grep -E '^-> (OWED|REVIEW OWED)' dev/audit/rca/owed-unactioned/boards/tick-1904.txt | tail -8 | wc -l`
- Owed block at line 56 of a 65-line board, mean of 32 blocks: `awk '/^== SWEEP/{if(n)print n, o; n=0; o=0} {n++} /^-- owed \(tick\)/{o=n} END{print n,o}' <session>/orch-sweep.log`
- 0.08 s per run, 5 runs: `time python3 -I tools/audit/seat/owed_unactioned.py --tick dev/audit/rca/owed-unactioned/boards/tick-1904.txt --state <tmp>/t.json --acks <session>/s7/ORCH-QUEUE.md --acks <session>/seat-ledger.md --no-write --max-board-min 600`
- 19 board reads 10:40Z to 18:55Z, 15 that drop the owed block: the orchestrator session transcript's Bash `tool_use` commands containing `orch_sweep.sh`, classified in record section 2
- 33 `HELD-REVIEW #2916` passes: `grep -c 'HELD-REVIEW #2916' <session>/cloud-relay.log`
- `disposed=2` on the relay's home: `python3 -I tools/audit/seat/ledger.py --log <session>/cloud-relay.log level <hrefs> <empty topics>`, with the two refs at their disposed shas
- 0 of those dispositions in the tick's home: `grep -c 'roster-b24-wip\|r10-handoff-bodies' ~/.local/state/hpo/dispositions.tsv`
- 100 self-testing, 100 wired: `python3 -I tools/audit/seat/selftest_wiring.py --check`

## Red checks

none

## Forward-carry

none

## Friction

none
