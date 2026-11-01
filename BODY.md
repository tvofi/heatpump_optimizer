Triage batch 96 rules two proposals the orchestrator s9 sent by message on 2026-10-31. The first, an addendum to batch 95's P349, would land the sweep runner's session-local handoff-orphan detector as a tick arm. The second asks for a barrier against unanswered red checks found only at the end of a long prepr. It is the rolling batch after batch 95, which was pushed first and left at its head.

- **P350: ACCEPT narrowed, as one carry on R10-FLY-OPENPR-ATOMIC**, amending P337's open driver (batch 94).
  - A topic the priority file omits sorts by P337's default order, never last.
  - A critical-path topic is never behind a non-critical one.
  - A board topic unstarted for more than 2 h prints `STARVED <topic> <sha8> <h>h`.
  - The basis: r10-996-runner-claims (critical path, handoff 18:41:52Z) and r10-fly-train-defaults-p2 (19:45:17Z) both sat on the tick board as `handoff-no-pr` (`tick.txt` lines 72 and 66) while the session-local `prio.txt` omitted them.
  - REJECTED: landing the stand-in, or an equivalent arm in `orchestrator_tick.py` or `owed_unactioned.py`. It restates the tick's existing `handoff-no-pr` line without its `ledger.py landed` test.
    - Its second instance, r10-cop-gate-r4-merge (`9db842127`), is a false positive. `git cherry` shows 0 `+`, `ledger.py landed` answers `merges-only`, and its content is #2975's, merged as `507a9ec`, with `_cg_aged` on main (5 matches).
  - Owed by the orchestrator now: put r10-996-runner-claims at the head of the opener's `prio.txt`, and retire the stand-in or teach it `ledger.py landed`.

- **P351: ACCEPT narrowed, as one carry on R10-PREPR-CAP.** `prepr.sh`'s ancestry red-check arm (`reds_line`, step 7c, line 3980) runs before step 1b's heavy slot (line 3555), and `body_push.sh`'s `--body-check` gains `--pr-branch fix/<topic>` to reuse it.
  - 9 update runs in two days were refused at 7c: `governance / instrument-self-tests` 7, `prelude` 3, `budget-raise-gate` 2, `tests / fast` 1, and CodeQL alert 46 twice.
  - #3049's run held slot 1 for 57 min (taken 21:47:44Z, then the mutants and the 431-check self-test) before that refusal at 22:44:59Z.
  - The fixer's own prepr skips the arm because its branch is not the PR's head ref, and `--body-check` is offline by design. So the update is the first reader today.
  - This is the fourth instance of one class, so a barrier is owed. It moves an existing self-tested arm and adds no new check or API call.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`14f0d67b01053ff396b9c421fa9f3b179a2ced06`; the file is the whole diff against `2b6bef745`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P350 and P351 as `ACCEPT`.
- `triage_refusal` returns None for both carries (#P350, #P351).
- Against `origin/handoff/audit-r10-roster`, `op_append_carry` accepts the P350 carry on R10-FLY-OPENPR-ATOMIC and the P351 carry on R10-PREPR-CAP.
- With P350's verdict changed to `REJECT`, its carry is refused: `dev/programme/triage/s6-batch96.md#P350 is not an ACCEPT ruling (REJECT)`. The same change on P351 refuses its carry: `...#P351 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it: `the triage ruling dev/programme/triage/s6-batch96.md is not on the roster branch or origin/main`.

## Figures

- `tick.txt` at 21:53:36Z: `handoff-no-pr` for r10-fly-train-defaults-p2 (line 66) and r10-996-runner-claims (line 72).
- `handoff/r10-cop-gate-r4-merge` = `9db842127`; `git cherry origin/main 9db842127`: 0 `+`; `ledger.py landed`: `merges-only`.
- `git show origin/main:dev/programme/delivery/2975.md`: "merged `507a9ec`".
- `ct` values: 1793472112 = 18:41:52Z and 1793475917 = 19:45:17Z (`date -u -r`).
- `pr/upd-fix-r10-fly-gh-call-log.log`: `taken slot=1 label=prepr-33638 expires_at=2026-10-31T22:17:44Z` (taken 21:47:44Z, `LEASE_SECONDS` 1800); `self-test  431 passed`; refused at 7c; mtime 22:44:59Z.
- No capped file is touched: the carry's destination is a new file P337 adds.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
