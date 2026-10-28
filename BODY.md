Triage batch 49 rules eleven proposals, V151-V161, as P237-P247. V151-V160 came from the owner's decision cards; V161 was filed by a fixer. Per the owner's correction ("triage should still do cost/benefit and is allowed to reject poor proposals"), each one was priced against code and the replanner.

Three measurements decide most of the rulings:
- the plan's own critical chain has 39.3 h of slack before R10-ARCH-DOCS;
- closure moves with slots, not seats;
- seven days of roster history show completions flat in WIP (r = 0.045).

Outcomes:
- **REJECT (six):** V151, V152, V154, V157, V159, V160.
- **DEFER (one):** V158, to the group that already owns it, R10-FLY-CARRY-DISPOSITION carry 1 (P66).
- **ACCEPT narrowed (four):**
  - V153 to R10-FLOW-TOOLKIT-MODEL: live groups by evidence, and the scheduled binding chain named;
  - V155 to R10-RECORD-HOLD-APPROVE: no reviewer for `record/autofix`, plus a forward-carry to R10-ORCH-BEATD. Policy-adjacent: that group's pull request merges only on tvofi's approving review, which mandate 6329234399 covers;
  - V156 to R10-RCA-HEADMOVED: evidence only, with no bot hold;
  - V161 to a new group, R10-FLY-MUTANT-RESTORE: a digest guard and signal-safe restore for the mutant harnesses.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`40bec0ab6c44747b9311abb80ca8220b2656b0b7`; the file is the whole diff against `6d86acc909f7fc465e5736771daf8fa45c1373a4`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate. It was driven with the five queued texts: the carries for P239, P241 (both of them) and P242, and the brief of the new P247 group, each ending in `triage: dev/programme/triage/s6-batch49.md#P<n>`.

- **Committed file:** `ruling_verdict` reads P237 REJECT, P238 REJECT, P239 ACCEPT, P240 REJECT, P241 ACCEPT, P242 ACCEPT, P243 REJECT, P244 DEFER, P245 REJECT, P246 REJECT and P247 ACCEPT. `triage_refusal` returns `None`, so all five texts land.
- **Mutant 1** (P241's `Verdict: ACCEPT narrowed` rewritten to `DEFER` in a copy): refused, `dev/programme/triage/s6-batch49.md#P241 is not an ACCEPT ruling (DEFER)`.
- **Mutant 2** (the heading `## P239:` renamed): refused, `#P239 is not an ACCEPT ruling (no such entry)`.

## Null control

- With the file absent, the same call returns `the triage ruling dev/programme/triage/s6-batch49.md is not on the roster branch or origin/main`.
- A text citing a REJECT, `#P240`, is refused: `#P240 is not an ACCEPT ruling (REJECT)`.

## Figures

**Replans.** Each is `python3 tools/plan/replan.py --start 2026-10-28T09:37:00Z`, against `origin/handoff/audit-r10-roster` `8c57b43dded6bc3ebab94b9a217d72b344ad7564` or against a counterfactual copy of it.
- Slots and seats:
  - `--slots 6` gives 128.97 h at seats 7, 14 and 20;
  - `--slots 7` gives 110.57 h;
  - `--slots 10` gives 82.2 h;
  - `--slots 14` gives 76.1 h.
- CP slack: in the plan, TOOLKIT-MODEL finishes at 10-31T01:36Z and ARCH-DOCS starts at 11-01T16:54Z, behind R10-REPLAY-REAL-DAY. That is 39.3 h.
- Counterfactuals at the live cap of 6 slots:
  - PLANPAGE pipelined: 129.48 h;
  - FREEZE and BEATD set live: 128.97 h;
  - BEATD shortened to M: 128.78 h.

**WIP history.** Seven days of roster snapshots, 27 of them 6 h apart: live groups against completions 12 h later give r = 0.045. Windows at WIP ≤ 6 closed 8.2 groups per 12 h (n = 5); windows at WIP ≥ 9 closed 7.67 (n = 15).

**Record PRs.**
- Since 2026-10-20, 101 of the 102 first-parent merges confined to `dev/programme/delivery/` came from `record/autofix`.
- One of the nine record PRs since 2026-10-25 (#2885) was given an opus review.
- `ledger.py` `review_owed` (505-522) has no record-branch skip.
- `merge_train.py` `sweep_bots` (1078-1114) never runs `app_approve.sh`.

**V156 moves.** Of the eight moves, 3 are bot commits and 5 are seat or orchestrator commits, by `git log -1 --format='%an | %s'`.

**Blocked verdicts.** First lines read from `verdict/<N>`:
- `carry-missing`: #2899, #2906 and #2896;
- `class-open`: #2887 and #2903;
- `mutation-vacuous`: #2873.

**V160 instances.** #2874 (`524c1896b`) and #2869 (`6f4434608`) merged as fix PRs, so they were not moot.

**Mutant harnesses.** 17 harnesses: 14 restore in `finally`, and 8 use no copy at all.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

- P239 ACCEPT narrowed (V153): replan.py treats a group with an open PR or a design ref as live, giving no credit for a design-only group, and names the scheduled binding chain beside `critical_path()`. Carry: R10-FLOW-TOOLKIT-MODEL
- P241 ACCEPT narrowed (V155): `review_owed` skips `record/autofix`, and `standing-dispatch.md` gets one sentence. Policy-adjacent: this group's pull request merges only on tvofi's approving review. Carry: R10-RECORD-HOLD-APPROVE
- P241 forward-carry: arm (c)4's `dispatch-owed` fixture includes a `record/autofix` PR that mints nothing. Carry: R10-ORCH-BEATD
- P242 ACCEPT narrowed (V156): eight classified head-moved instances, and the measured reason a bot hold is the wrong countermeasure. Carry: R10-RCA-HEADMOVED
- P247 ACCEPT narrowed (V161): a new S group, R10-FLY-MUTANT-RESTORE, carrying the digest guard and signal-safe restore for the in-place mutant harnesses. The group does not exist until its held `append-group` op lands, and the roster gate refuses that op until this file is on main. Carry: dismissed: registered by the held append-group op after merge

## Friction

none
