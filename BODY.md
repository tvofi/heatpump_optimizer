Triage batch 68 rules the orchestrator's queue proposal of 2026-10-30T09:33:31Z (`s7/triage-queue-s7.txt` line 13). A standing seat's alive file stayed fresh while no seat existed: a 41 h-old orphaned loop, pid 29401, touched `merge.alive`, and the board printed `ok merge seat beat 50s ago` across the s7 to s8 handover. This is the next rolling batch under V182, after batch 67 (#2983). It holds one ruling and one held roster op.
- **P299: ACCEPT narrowed.**
  - (a) One carry on R10-ORCH-BEATD amends its P97 `--seat-alive` per-seat-id arm in `pulse.py`. The per-role file alone never makes a role live. A fresh per-role file with no fresh id entry, or a fresh id that is not the newest unstopped launch for the role, prints `FOREIGN`.
  - (b) The out-of-tree half goes to the orchestrator and is not carried (P236 precedent): seats write their launch nonce into the alive file, and `orch_sweep.sh` compares it.
  - It is the fourth instance of the class in round 10 (P188 twice, P204, this one), so it is an audit class and owes a barrier. The in-tree barrier was already owned (P46, P97, P63). This closes P97's one gap: a fresh per-role file with no id entry.
  - Narrowed from the filing: the comparison is with the newest launch that has no stop line, not "the live launch". `seat-launch.sh --dup` reads DUPLICATE for merge and triage today, because the dead s7 nonces were never stopped.
  - Recorded limit: a nonce does not tell a seat from its own orphaned loop. P63 and P51 own that case.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`1670b98d7a55c947ec3449c47c871f084406be07`; the file is the whole diff against `b646e8306`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P299 as `ACCEPT`. `triage_refusal` passes the carry text, which cites `triage: dev/programme/triage/s6-batch68.md#P299`: it returns None.
- With `Verdict: ACCEPT narrowed` changed to `Verdict: REJECT narrowed`, the same carry is refused: `dev/programme/triage/s6-batch68.md#P299 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve: `the triage ruling dev/programme/triage/s6-batch68.md is not on the roster branch or origin/main`.

## Figures

- `seat-ledger.md:2463`: `orch s8: stopped orphan beat loop pid 29401 (touched merge.alive with no seat); launched merge seat e9e6d824886e8e82` (09:33:22Z).
- `awk '$3=="merge"' s7/launch-ledger.txt`: the last s7 merge launch is `8741ed6aeec213f0` at 2026-10-28T21:31:35Z, and the s8 launch `e9e6d824886e8e82` is at 2026-10-30T09:33:16Z. A loop 41 h old at 09:33Z predates `8741ed6a`.
- The merge seat's last own line is `seat-ledger.md:2454`, after 08:29:43Z. The handover is about 09:20Z (`HANDOVER-s8.md`). In that window, `git log --first-parent origin/main` shows #2982 merged at 09:22:58Z, #2981 at 09:23:38Z and #2983 at 09:32:03Z.
- `seat-launch.sh --dup merge` prints `DUPLICATE: 2 live launches for role 'merge'` (8741ed6a, e9e6d824). `--dup triage` prints the same (25222de4, ef0ff4b2).
- `git ls-files | grep -c 'orch_sweep\|seat-launch'` = 0.
- `policy_lint.mjs --budgets`: `standing-merge.md` 37/37, `standing-roster.md` 27/27, `standing-dispatch.md` 39/39, `proposal-triage.md` 36/36. None is touched.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
