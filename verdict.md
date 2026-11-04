Fix review: blocked 1fca63cb1665af349fd51c57820150a280ddba09 ci-red: gate concluded cancelled because PR #3211 was closed unmerged at 2026-11-04T22:51:15Z, so no green run exists for this head

bus-nonce: 4111e3795d3a65ccd296cbe3952308c3

Round 1. Head reviewed: 1fca63cb1665af349fd51c57820150a280ddba09.

## Block

- `merge_train.py classify` printed WAIT until 22:49:57Z, then `RED ... red: gate` at 22:51:09Z (ev/classify.log).
- The check runs show the whole run 41923437389 `cancelled` at 22:50:52Z, and the PR API shows `state: closed`, `merged: false`, `closed_at 22:51:15Z`. The red is the closure cancelling the run, not a test failure.
- I cannot tell why it was closed (superseded, withdrawn or an accident), so I return no `merge` for a closed PR. Reopen or re-dispatch at the new head and the substantive review below carries over.

## Findings

- Body says "the diff is one markdown file", but the three-dot diff is two files (the ruling plus `dev/programme/delivery/3211.md`). The head note explains the row commit; the claim is only loose. Carry: dismissed: the `## Head` section discloses the row commit, no behaviour rides on it.
- Entry cites `update_pr.sh` line 128 and `open_pr.sh` lines 7 and 132 without their `tools/audit/seat/` path, and cites `app_push.sh` lines 107 to 122 correctly. A reader must guess the directory. Carry: dismissed: line numbers all resolve at origin/main `2a9cd3476`'s successor, only the path is missing.
- The ledger figure "closure-keyed skip rate 1 of 10 opens" (P250 follow-up, ledger 21:33:05Z) was not found in `s6-batch51.md#P250` and the ledger is session-local, so it is not re-derived here. Carry: dismissed: the "0 of 4 code opens" figure for P346 does resolve in `s6-batch95.md` line 140, and the ruling does not rest on the 1 of 10.
- The entry's own Instances say the reuse share of the 538 min is unmeasured, and proposal-triage.md says an unmeasured benefit is DEFER. The ACCEPT rests on the owner's directive and the entry says so; it rules routing and form only. Carry: dismissed: the owner decided whether, per the entry's first lines; triage gate is satisfied by that source.
- The entry takes P386 because P384 and P385 are in batch 120, not yet on main, so a concurrent batch could still collide on a number. Carry: dismissed: the numbering note is explicit and no P386 exists anywhere on main.

## Evidence

- RESULT: grammar. `Verdict: ACCEPT`, `Source:`, `Instances:`, `Cost:`, `Binding:` present for the one `## P386` entry; the destination R10-HANDOFF-PATH exists on `origin/handoff/audit-r10-roster` (`dev/programme/rosters/wave-r10-groups.json`: `after: []`, size M, carry folded from R10-OPENER-REUSE).
- RESULT: facts at origin/main. `prepr.sh` line 4248 prints `PRE-PR: <sha> <digest>`; `app_push.sh` lines 107-122 are the `--row-only` text; `open_pr.sh` line 103 merges origin/main, line 132 is `RO=--row-only`; `update_pr.sh` line 23 reads "A head that merges new code, or main, never asks" and line 128 gates `--row-only` on `HEAD^@ == LIVE`; #3089 and #3164 are merge commits on main; P377 names a different subject at `s6-batch115.md:253`; P346 and P250 exist.
- RESULT: merge. `git merge-tree --write-tree origin/main 1fca63cb1665af349fd51c57820150a280ddba09` rc=0, no conflict (ev/merge-tree.txt).
- RESULT: carry_audit at the head 0 finding items before this verdict (packet).
- Not re-derived: the 45 runs and 538 min, the plan's 2026-11-05T19:50Z batch 27 timing, and the per-run `p1.log` figures; they live in the dispatcher's session logs and `s7/plan-live.json`, which this seat cannot read. The no-budget-row statement is credible: the diff touches no capped file.
- Mutation proof: the body's flip-to-DEFER and absent-file controls use `roster_edit.py`'s `ruling_verdict`; not re-run, because the PR closed before CI settled.
- CI: RED by cancellation only; no individual check failed on its own.
