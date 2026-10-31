Triage batch 94 rules nine proposals from the orchestrator s9's triage queue of 2026-10-31: a defect (18:50Z), a slip (19:25Z) and seven script-census proposals (19:36Z). The first: An owner-account #201 comment that pairs the revocation word with a mandate id voids that mandate in `budget_raise_gate`. This is the second instance. This is the next rolling batch after batch 93, with nine rulings, one new group and five held carries.

- **P336: ACCEPT as already carried, amended.** The barrier is R10-FLY-MANDATE-REVOKE-GUARD (`not-started`, S). Its brief already is the proposal, and it was never dispatched.
  - The amendment carry closes two gaps:
    - `gh_comment.py patch` is unguarded. The gate reads every #201 comment's current body, so an edit acts like a post.
    - The gate's whole-number id test is written inline, so a guard can only copy it. The carry factors it into `budget_raise_gate.revokes(body, cid)` and imports that one function, with the gate's behaviour byte-equal.
  - Ask: dispatch the group now, ahead of other instrument fly-ins.
  - Out of this seat's contract: the live state of the session mandate after comment 6546832523. The options are an owner re-grant, or removing or editing that comment, and the choice belongs to the orchestrator and the owner.
  - This ruling and its carry deliberately never write the mandate's id beside the word.

- **P337: ACCEPT narrowed**, as one carry on R10-FLY-OPENPR-ATOMIC.
  - The opener's loop is session-local, in four hand copies (`driver.py` to `driver4.py`, 83 to 107 lines). Decision 0013 puts it in the tree.
  - The carry adds `tools/audit/seat/open_driver.py`, the open arm only. Each pass re-reads priority, cap and titles from `$HPO_STATE_DIR`, and the default order is CP > hotfix > record > the rest.
  - It skips a topic that is already on main or that already has a PR branch. The on-main test is `ledger.py landed`, the classifier `cloud_relay.sh` and `bus.sh orphans` already use (census Part B row 1); `git cherry` survives only as a guard against board lag.
  - It counts live runs by its own PIDs, never `pgrep`.
  - REJECTED: the `handoff-update` arm. `cloud_relay.sh`'s handoff arm already runs `update_pr.sh` and dispatches the reviewer.

- **Script census, P338-P344.** These follow the owner's rule (tvofi, 2026-10-31): "reusable scripts in a generalized form always belongs on main if they are not redundant, wrong or have negative consequences on the machinery".
  - P338 and P339: ACCEPT narrowed, as a new S fly-in, **R10-FLY-SEAT-WAITERS**.
    - A `seat_watch` ref watcher. A move on a merged or closed PR is counted, never reported.
    - `proof_watch.py --wait-only` over several pinned heads.
    - REJECTED: a `--run` exec arm, and a `contains` predicate, which census carry 5 gives to the relay.
  - P340: REJECT, as redundant. `cloud_dispatch.py --group --roster-ref --publish` already renders every carry and refuses home paths (`aabbdff17`, `fc6a810eb`). The POOL.txt convention has no tracked writer.
  - P341: ACCEPT, `roster_show.py show|diff`, as a carry on R10-ORCH-ROSTER-SCHEMA.
  - P342: ACCEPT, `tools/plan/whatif.py` on ONE roster ref, as a carry on R10-FLOW-TOOLKIT-MODEL.
  - P343: REJECT. The owner's full re-read after a compaction makes a `--changed` list save nothing on the dominant path.
  - P344: ACCEPT, as a carry on R10-ORCH-REVIEW-PACKET: `bus.sh dispatch` refuses while an autofix check-run is queued or in progress. Measured: of 305 dispatches since 10-24, 12 heads then got a bot autofix child, across 11 PRs.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`e6bb16255561390043b6db82087de51357c357c5`; the file is the whole diff against `a7dd7f50d`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P336-P339, P341, P342 and P344 as `ACCEPT`, and P340 and P343 as `REJECT`.
- `triage_refusal` returns None for all five carries (#P336, #P337, #P341, #P342, #P344) and for the new group's brief and note (#P338).
- The roster's own validators, run against `origin/handoff/audit-r10-roster`, accept every op: `op_append_carry` on each carry, and `op_append_group` with the durations sizes.
- `brief_lint.mjs` over that roster plus the six additions reports `TOTAL: 0 error(s)`, the same as the base.
- With P336's verdict changed to `REJECT`, its carry is refused: `dev/programme/triage/s6-batch94.md#P336 is not an ACCEPT ruling (REJECT)`. The same change on P337 refuses its carry the same way.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or on origin/main.

## Figures

- `budget_raise_gate.py` at `a7dd7f50d`:
  - `MANDATE_ISSUE = 201` at line 115;
  - `MANDATE_REVOKED` at line 120;
  - the inline revocation test at lines 398-402 of `mandate_state`.
- `gh_comment.py` at `a7dd7f50d`: line 424 gives `action` the choices `post`, `patch`, `verify` and `self-test`.
- `cloud_relay.sh` at `a7dd7f50d`: lines 86-92 document the handoff arm's `update_pr.sh` run.
- `cloud_dispatch.py` at `a7dd7f50d`:
  - `--group`, `--roster-ref` and `--publish` at lines 1121-1138;
  - `group_brief` at line 409.
- `git grep -l POOL.txt origin/main -- tools`: no match.
- `node tools/policy/policy_lint.mjs --budgets` names none of the files these rulings touch.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
