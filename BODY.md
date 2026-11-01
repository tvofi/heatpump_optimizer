Triage batch 95 rules five proposals from the orchestrator s9 on 2026-10-31, four from its triage queue and one by message. The first (20:40:47Z): K15 (d) reads a budget-raise PR as not reviewable in the state every raise is in before its review, because the approval `budget_raise_gate` waits for follows the verdict. This batch has five entries (four rulings and one owner order) and one new group, which carries one carry. It is cut separately from batch 94, whose refs were pushed while its opener was in flight, so that head was not moved.

- **P345: ACCEPT, as a new S fly-in, R10-FLY-RAISE-REVIEWABLE.**
  - The mechanism: `budget_raise_gate.approval` refuses until an approval names the head, and `tools/ci/gate.py` line 76 makes `budget-raise-gate` a required unit of `gate`. As a result, `merge_train.classify` reads RED. `orchestrator_tick.one_pr` then prints NOT REVIEWABLE (back to its fixer), and `bus.sh dispatch` refuses the reviewer on rc 1, a refusal live since `9c53c107b` (2026-10-29).
  - Instances: #3045 at `9ef51b82` (OWED-ACK ttl=3, hand override) and the critical-path #3006 at `979797ad` (pre-approval budget-raise-gate reds at 17:01, 18:32 and 18:34Z).
  - The build: one `merge_train.approval_owed` that reuses `Train.raise_hold`, and with it the gate's own `raises_between` and `approval`. A `classify --pr N` arm exits 4, APPROVAL-OWED, and is reviewable. `bus.sh` dispatches on rc 4, and the tick prints RAISE APPROVAL OWED instead of NOT REVIEWABLE. `classify` itself, and so the merge state, is unchanged.
  - REJECTED in part: the proposal's alternative of rolling the gate up as "approval owed, not red". `gate` must stay non-green to hold an unapproved raise off `main`.
  - Ask: dispatch it ahead of other instrument fly-ins.

- **P346: OWNER-ORDERED (not ruled).** A fixer-recorded prepr receipt lets `open_pr.sh` skip its prepr. The owner ordered it directly (tvofi, 2026-10-31), and the orchestrator withdrew the queue line before this seat ruled. `proposal-triage.md` gates proposals, and an owner order is not one, so the entry records no verdict. An earlier draft's REJECT does not stand. The group is R10-FLY-OPEN-PREPR-REUSE.
  - The entry keeps the evidence, which the orchestrator carries to that group's fixer as constraints:
    - `open_pr.sh` always gates a merge of origin/main into the code head (lines 103-105).
    - On today's five opens, main moved under a selected closure on 4 of 4 code opens (2, 2, 3 and 1 closures).
    - The open-time cross-main prediction refused `r10-fly-mutant-restore` at 18:34Z (`pr-contract` predicted red against `c3a47e5656ef`).
  - The slot half is owner-ordered too (tvofi, "do all of them"). `prepr.sh` takes its heavy slot at step 1b (line 3555), before step 2 (line 3598) knows the scope. The orchestrator carries it to R10-PREPR-CAP, held until #3051's verdict. The entry records its evidence: of 35 completed prepr logs, 29 were light (median 0.9 min in the slot), and the 8 light waits with an exact start had a median of 11.4 min (max 39.1).

- **P347: REJECT, as redundant** (prepr step 3h runs only when the diff touches prepr.sh or its self-test inputs).
  - That is the rule in force: `selftest_owed` (`prepr.sh` lines 1508-1538) over 56 derived inputs gates step 3h (lines 3737-3746).
  - At the open, `BASE=$(git merge-base origin/main HEAD)` (line 3525) is main's tip after `open_pr.sh` merges it, so main's merge already cannot trigger 3h.
  - Run over today's ten opens: five owe 3h through their own files (`tests/entities.py`, `tests/features.py`, `tests/closure.py`, `carry_audit.py`, `prepr.sh`), and five owe nothing. The proposal selects the same set and saves 0 h.
  - What would change it: a measured per-row input map for the 431-check self-test.

- **P348: ACCEPT, as a carry on R10-FLY-RAISE-REVIEWABLE** (the group P345 creates; the carry is in its JSON's `carry` list).
  - `bus.sh dispatch`'s review-carry refusal (lines 484-494) answers from the commit range alone, so it carries a BLOCKED verdict too. It refuses the re-review a body-only answer needs.
  - Instances: #3045 round 3 at `9ef51b82`, dispatched only by omitting `--reviewed-head`.
  - Of the 1184 verdicts across all 493 `verdict/<pr>` refs, 97 sit at a head an earlier verdict on the same PR had blocked, 38 of them since the refusal landed (`6f905c40f`, 2026-10-27).
  - The carry: the refusal fires only when the latest verdict naming the reviewed head is `merge` (a `verdict_at` beside `blocked_rounds`), with one clause amended in `orchestrator.md` line 172.

- **P349: REJECT** (a group's second handoff after its first PR merged is invisible to the opener).
  - On all four instances the guarded state does not exist. `fix/<topic>` is gone for each merged PR (`git ls-remote`), and topics have opened twice before (#2870, then #2939; #2882, then #2978).
  - The tick already prints `handoff-no-pr` for all four (`tick.txt` lines 72-85).
  - The "push onto merged #2939" is a `p2.log` from 2026-10-28, when #2939 was open. r10-orch-review-packet's open is in flight now on `fix/r10-orch-review-packet-2`.
  - The other three wait because they are not in the opener's `prio.txt`, and slots are 4/4 held with 4 queued. That includes the critical-path r10-996-runner-claims. The owed action is the orchestrator's priority entry.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`4b75dbeefd247286498e476078d35ea1193a94b3`; the file is the whole diff against `a7dd7f50d`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P345 and P348 as `ACCEPT`, P347 and P349 as `REJECT`, and P346 as `unreadable` (no verdict line, by design: nothing may cite it as an ACCEPT).
- `triage_refusal` returns None for the new group's brief, its `resume.note` and its P348 carry.
- Against `origin/handoff/audit-r10-roster` (`dc16091d6`), `op_append_group` accepts the group with the durations sizes.
- `brief_lint.mjs` over that roster plus the group reports `TOTAL: 0 error(s)`, with an error set identical to the base's and no warning naming the group.
- With P345's verdict changed to `REJECT`, the group's text is refused: `dev/programme/triage/s6-batch95.md#P345 is not an ACCEPT ruling (REJECT)`. With P348's changed the same way, its carry is refused: `dev/programme/triage/s6-batch95.md#P348 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it: `the triage ruling dev/programme/triage/s6-batch95.md is not on the roster branch or origin/main`.

## Figures

- `budget_raise_gate.py` at `a7dd7f50d`: "no decisive review" at lines 490-492; "approval is on <sha>, not this head" at lines 503-505.
- `tools/ci/gate.py` at `a7dd7f50d`: line 76 lists `budget-raise-gate` among the `pr` event's units.
- `merge_train.py` at `a7dd7f50d`:
  - `gating_names` at lines 386-394;
  - `classify` at line 434;
  - `Train.raise_hold` at lines 1531-1588;
  - the `classify` subcommand at line 6631.
- `orchestrator_tick.py` at `a7dd7f50d`: the NOT REVIEWABLE line at lines 876-882.
- `bus.sh` at `a7dd7f50d`: the classify refusal at lines 462-473; the K15 (d) self-test rows at lines 1439-1453.
- `node tools/policy/policy_lint.mjs --budgets` names none of the group's five files. `tests/structure.py` measures `custom_components/` only.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

- `open_pr.sh` at `a7dd7f50d`: the merge of origin/main at lines 103-105; the `app_push.sh` push with `PREPR_SKIP_CLOSURES=1` at line 118.
- `app_push.sh` at `a7dd7f50d`: the full prepr at lines 469-475.
- `prepr.sh` at `a7dd7f50d`: the heavy slot at step 1b (line 3555); the scope's MODE line at step 2 (line 3598).
- P346's table: each row's C from `driver4.log`, the open's main read as the second parent of the PR head's parent, and the closure test over `tests/closures.json`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
