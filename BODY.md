Triage batch 68 rules two orchestrator queue proposals of 2026-10-30 (`s7/triage-queue-s7.txt` lines 13 and 14). It is the next rolling batch under V182, after batch 67 (#2983). It holds two rulings and three held roster ops.

- **P299: ACCEPT narrowed. A standing seat's alive file was fresh while no seat existed.** A 41 h-old orphaned loop, pid 29401, kept `merge.alive` fresh, and the board printed `ok merge seat beat 50s ago` across the s7 to s8 handover.
  - This is the fourth instance of the class in round 10 (P188 twice, P204, this one), so it is an audit class and owes a barrier.
  - The barrier's owner, R10-ORCH-BEATD, is `done` on the roster branch (#2916, arm (a) only). It left P46 (`--seat-alive`) and P97 (per-seat-id entries) unbuilt: `pulse.py` has no `seat-alive` at main.
  - (a) A new S fly-in, **R10-FLY-SEAT-ALIVE-ID**, re-routes P46 and P97 and adds P299's `FOREIGN` arms. The per-role file alone never makes a role live. A fresh id that is not the newest unstopped launch for its role reads FOREIGN.
  - (b) The out-of-tree half goes to the orchestrator and is not carried (P236 precedent): the nonce check in `orch_sweep.sh`, `--stop` lines for the dead s7 nonces, and the stranded P63.
  - Narrowed from the filing: the comparison is with the newest launch that has no stop line. `seat-launch.sh --dup` reads DUPLICATE for merge and triage today.
- **P300: ACCEPT, two carries on R10-ORCH-ROSTER-SCHEMA. The roster queue runner passes a trailing comment as arguments, and marks no line it applies.**
  - (a) The comment fix was already carried on 2026-10-25 and never built. The filing's `shlex.split(..., comments=True)` is REJECTED: it truncates a `#` inside a word (`@/p/b#1.txt` -> `@/p/b`). The carry adds null rows for that.
  - (b) `run --mark` rewrites each applied line as `#done` or `#refused`, through an atomic re-read and replace that keeps a concurrent append. It retires two untracked session wrappers (90 and 111 lines).

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`b40577dde489a9f3844697708ab215a2f1c85b4c`; the file is the whole diff against `b646e8306`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`, run with its own `ruling_reader`.
- On the committed file, `ruling_verdict` reads P299 and P300 as `ACCEPT`. `triage_refusal` passes the R10-FLY-SEAT-ALIVE-ID group brief, which also cites P46 and P97 on main, and both P300 carry texts: each returns None.
- With P299's `Verdict: ACCEPT` changed to `Verdict: REJECT`, the group brief is refused: `dev/programme/triage/s6-batch68.md#P299 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve: `the triage ruling dev/programme/triage/s6-batch68.md is not on the roster branch or origin/main`.

## Figures

- `seat-ledger.md:2463`: `orch s8: stopped orphan beat loop pid 29401 (touched merge.alive with no seat); launched merge seat e9e6d824886e8e82` (09:33:22Z).
- `awk '$3=="merge"' s7/launch-ledger.txt`: the last s7 merge launch is `8741ed6aeec213f0` at 2026-10-28T21:31:35Z.
- `seat-launch.sh --dup merge` and `--dup triage` each print `DUPLICATE: 2 live launches`.
- In the masked window, `git log --first-parent origin/main` shows #2982 at 09:22:58Z, #2981 at 09:23:38Z and #2983 at 09:32:03Z.
- Roster branch `4c91e6877`: R10-ORCH-BEATD `resume` is `{'stage': 'done', 'pr': 2916}`. At origin/main, `git grep 'seat-alive\|DUPLICATE seat' -- tools/audit/seat/pulse.py` finds nothing.
- `roster_queue.parse_line('set-stage G done  # #2955 merged aced2589')` returns `('set-stage', 'G', 'done', ['#', '#2955', 'merged', 'aced2589'])`.
- `shlex.split('append-carry G @/p/b#1.txt', comments=True)` returns `['append-carry', 'G', '@/p/b']`.
- `s7/roster-queue-s7.txt`: 374 lines, 181 `#done` and 136 `#refused`. Of these, 16 `#done` and 3 `#refused` lines carry a trailing ` # `.
- `git ls-files | grep -c 'orch_sweep\|seat-launch'` = 0.
- `policy_lint.mjs --budgets`: `standing-merge.md` 37/37, `standing-roster.md` 27/27, `standing-dispatch.md` 39/39, `proposal-triage.md` 36/36. None is touched.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
