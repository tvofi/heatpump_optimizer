# Proposal triage, session s10, batch 112 (P370)

The rolling batch after batch 111. Facts were read at origin/main `8247a1ed1`, at the round's
roster branch `origin/handoff/audit-r10-roster` (`5dc16bbe1`), in the session-local opener's log,
and in the session's seat ledger.

## P370: the opener maps a split-part topic to no roster group (a re-file of P363)

Verdict: DEFER. The item is already owned: R10-OPENER-REUSE carry 10, routed from P363
(`s6-batch106.md#P363`, ACCEPT). No new carry and no group. The answer changes only if that
group is closed without building the rule, or if the rule it builds still misses a part topic.

Source: the orchestrator s10's queue line of 2026-11-02T03:29:40Z. It proposes stripping a
trailing `-p<N>` before the roster lookup, so the group is the base group and the title names the
part.

Instances:
- **The new instance.** Opener log `driver4.log` at 03:24Z:
  `NEEDS-TITLE/GROUP (no roster group for topic) r10-deps-actions-bump-p1`. The seat ledger at
  03:29:40Z records it as opened by hand with group R10-DEPS-ACTIONS-BUMP.
  - Its handoff head `99835eadc` changes one file against its merge base,
    `dev/audit/rounds/round6/D11/fix/codeowners_gap.py`. Nothing is under `custom_components/`.
- **The same mechanism P363 ruled on.** P363's instances were the part topics
  `r10-fly-train-defaults-p2`, `r10-roster-ops-2-p1` and `r10-sav-comfort-p2`.
  - Today's line is the fourth part topic to miss.
  - `grep -c NEEDS-TITLE driver4.log` prints 8, against 88 `RESULT` lines.
- **The rule is routed and has landed.** On roster `5dc16bbe1`, R10-OPENER-REUSE holds 10 carries.
  - Carry 10 opens "From triage P363", and amends rule (3) of P337's open driver, which is carry 8.
  - P363's rule tries an exact match first, then the base group with the part suffix stripped.
    That is this proposal's remedy, with the exact-match guard P363 found it needs: five roster
    names already end in such a suffix, among them R10-ROSTER-OPS-2.
  - The group's `resume` reads stage `not-started`, next step "dispatch a fixer". No pull request
    is open on its branch.

Cost:
- A duplicate carry would cost a second copy of the same text on R10-OPENER-REUSE. Its brief would
  then hold two specifications of one rule, which its fixer must reconcile.
- No capped file is touched by this ruling.

Binding:
- **Why DEFER.** The ruling's destination already exists and holds this exact remedy. What this
  instance adds is a count: 4 part topics have missed since 2026-10-31, each opened by hand.
- **Not ruled under the LOG class.** The rule is already ACCEPTed. Its delivery waits on
  R10-OPENER-REUSE's dispatch, which is the orchestrator's queue decision, not a triage one.
