Fix review: merge f3f77f8e6b59313ef9afe704142558a40fd813a0

bus-nonce: 9ea0d664d2ae219d69c8727b789f07f7

Round 1. Record PR (triage s8 batch 79, P316); the diff is two files under dev/programme, no production code, so no mutation, claim-file, version or budget movement applies.

## Findings

- P316's DEFER leaves one read-only measure-first probe (sensitivity replay with a flat-price null control, plus an owner-only field comparison) to be dispatched by the orchestrator; the record itself defines the probe and its decision rule, and no roster op is added. Carry: dismissed: the probe is defined in dev/programme/triage/s6-batch79.md with its decision rule, and a DEFER adds no roster op by contract

## Evidence

- Head measured: f3f77f8e6b59313ef9afe704142558a40fd813a0 (the head named in the brief; three-dot diff is delivery/3023.md and triage/s6-batch79.md only).
- Cited rule re-read at origin/main: thermal_model.py:1342 `measured_power=bool(cfg.get(const.CONF_POWER_ENTITY))`; :1481 `heat_loss_basis`, :1488 returns HEAT_LOSS_BASES[1] when measured_power. Matches the record.
- Fixer's basis arms re-read at 746894afe:BODY.md lines 51-53: no power entity -> commanded; revenue meter -> metered; pump's own estimate -> metered. Forward-carry item 2 (line 101) is dismissed there with the reason the record quotes.
- The record names the unmeasured benefit, the probe (a: scaled power replay 0.8/0.9/1.1/1.2 with flat-price null control; b: 7-day field comparison), and a decision rule (ACCEPT as new group, else REJECT with the reset action as remedy).
- merge-tree against origin/main: exit 0, no conflict, no claim-file driver involvement (ev/merge-tree.txt).
- Role-file drift (merge base vs origin/main, dev/governance/roles/): empty.
- carry_audit at head: 0 finding items; figure_lint: 1 resolved, 2 not verified (git show refs, re-read by hand above), 0 refused.
- CI: merge_train classify returned GREEN at this head (rc 0), pending none, red none (ev/cls.txt).
