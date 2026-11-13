R10-REVIEW-DISPATCH-RESIDUE part 5: Carry 17 (the carry-fold memo recognises an unchanged refused body by its BODY.md blob), Carry 20 (`landed()` reads an empty net diff as landed), Carry 11 (a mechanical-only block is exempt from the three-round rule), Carry 28 (`dispatch-handoff` re-keys a known PR). Measured at the head below, 2026-11-13T06:40Z.

## Head

f71c5e6933496cf6a1b04ff2796b63802fbf5463

## Policy

`dev/governance/roles/fixer.md`, "Past three rounds" section, one paragraph appended (Carry 11, owner directive tvofi 2026-11-09 18:35Z, "the split should never apply when the gap is mechanical only"). It names the exemption `bus.sh dispatch` now applies: the latest blocked verdict's class being mechanical (`ci-red`, `red-unanswered`, body or contract, `conflict`, `head-moved`, carry, ungated step) dispatches past the third round with no `## Re-cut` note. It also states the ruling carried here from a dismissed carry: a CI-only block (`ci-red`, `ci-wait`, `ci-pending`, a cancelled run) is mechanical and does not count toward the three-round rule. Judgement classes, unknown classes and an unreadable log refuse as before. For approval at the merge under the owner's mandate. No change to `standing-dispatch.md`: the dispatcher's command is unchanged (`--pr` is optional; a known PR is read from `<bus>/rekeyed`).

Budget payment, no raise: fixer.md sits at its line and token caps, so the paragraph is paid for by deleting nine parenthetical issue and measurement citations of resolved incidents from steps 1, 3, 8, 9, 10, 15 and 17 (the `#948`, `#1713`, `#1506`, `#373`, `#386`, `#539`, `#1874` tags and the "~12%" figure). No rule sentence was removed. `node tools/policy/policy_lint.mjs` printed `TOTAL: 0 error(s) across 51 policy file(s)`.

## Approval

Pending: the owner's approving review at this head, which `main-protect-checks` requires for a code-owned path, and the merge-time approval of the `fixer.md` edit named under `## Policy`. No budget leaf is raised.

## What changed, and which seam it extends

- Carry 17, `tools/audit/seat/cloud_relay.sh` `carry_fold_arm`/`fold_judge`. body_push.sh keeps each refused body as a new parentless commit, so the landed `cloud-fold-judged` memo, keyed on the kept commit, never hit (r10-train-residue: four kept commits, one blob). The memo line gains the BODY.md blob and the handoff/<topic> tip (`<topic> <wip> <body|-> <outcome> <epoch> <blob|-> <tip|-> [OWED]`); a fold-failed or push-failed record now also stands for a later kept body with the same stop, blob and tip, prints `OWED carry-fold <topic> unchanged since <utc>: <line>`, keeps its first epoch (so the 3600 s retry bound runs from the first failure) and its OWED level line is set again. A record in the old shape (no blob field) is judged again. Extended the one memo rather than the separate `cloud-fold-failed` file the carry proposes: a second state file would need its own TTL, level-line replay and old-record handling beside a memo that already has all three. P546 (handoff-wip `dispose()`) is dismissed per P580 and not built; `dispose()`/`disposed()` are untouched.
- Carry 20, `tools/audit/seat/ledger.py`: `empty_net()` (merge-base ok and `diff --name-status` rc 0 and empty) and a named reason `empty` in `landed()`, ahead of `content`; rc != 0 stays not-landed. No "head newer than BLOCKED" rule.
- Carry 11, `tools/audit/seat/bus.sh`: `mechanical_block()` reads the class of the latest blocked verdict's first line (`Fix review: blocked <head> <class>:`) against `MECHANICAL_CLASSES`, and `three_rounds()` returns 0 on it. Unknown class or failed read: refuses as before.
- Carry 28, `tools/audit/seat/bus.sh` `dispatch_handoff`: after recording, calls the existing `rekey` when `--pr N` was given or `<bus>/rekeyed` holds a `<topic> <sha> <pr>` line. No API call, no `fix/<topic>` derivation. The sibling self-test region edit is limited to `36..40` added to the delivery-row fixture list.

## Mutation proof

Every mutant applied in place to the handoff head, the named self-test run, then restored (`git status --short` empty). Null mutants append ` null` to the marker comment.

- Carry 17 relay: R1 kept-commit key (`&& false`) KILLED, 6 failed ("... is not pushed again", "the tick line says OWED, unchanged since the first failure", "a changed BODY.md blob runs body_push.sh again", "null control: the edited body kept again ...", "a moved handoff/<topic> tip ...", "a record an hour old ..."); R2 tip comparison dropped KILLED, 2 failed ("a moved handoff/<topic> tip with the same blob runs body_push.sh again", "a record an hour old ..."); R3 blob comparison dropped KILLED, 4 failed; R4 TTL dropped KILLED, 2 failed ("... and retried once it is", "a record an hour old ..."); R5 old-format guard dropped: survived the first arm set, then KILLED by the added arm ("a memo record from before the blob and tip fields is judged again, not read with shifted fields"); R0 null SURVIVED (462 checks, 0 failed).
- Carry 20 ledger: L1 `if False:` KILLED ("landed: an add-then-remove tip with an empty net diff lands as empty (carry 20)"); L2 diff rc dropped KILLED ("null control: a failing diff read (rc != 0) is not empty (carry 20)"); L0 null SURVIVED (105 checks, 0 failed).
- Carry 11 bus: B1 exemption removed KILLED (2 failed: ci-red, ci-wait dispatch arms); B2 class read oldest not latest KILLED (3 failed, incl. "only the LATEST block's class is read"); B3 `harness` added to the mechanical set KILLED (4 failed, incl. the existing re-cut refusals); B4 `ci-wait` dropped KILLED ("a CI-only wait block (ci-wait) is mechanical too"); B0 null SURVIVED (188 checks, 0 failed).
- Carry 28 bus: B5 rekey call dropped KILLED (2 failed); B6 rekeyed lookup deleted KILLED ("a second dispatch-handoff for a topic already re-keyed to #55 ..."); B7 `--pr` ignored KILLED ("--pr 57 keys a fresh topic at dispatch").

## Null control

Reds at the base: production lines reverted in a scratch copy of the handoff head, with the new self-test arms kept, `bash tools/audit/seat/bus.sh --self-test` printed `bus self-test: 188 checks, 4 failed`, `python3 -I tools/audit/seat/ledger.py --self-test` printed `ledger self-test: 105 checks, 1 failed`, `bash tools/audit/seat/cloud_relay.sh --self-test` printed `cloud_relay self-test: 462 checks, 6 failed`. Greens at the handoff head: `bus self-test: 188 checks, 0 failed`, `ledger self-test: 105 checks, 0 failed`, `cloud_relay self-test: 462 checks, 0 failed`. Per-carry nulls inside those: a stop with no record runs body_push.sh (17); a tip with one real uncovered line stays None and a failing diff read is not empty (20); a fourth round after a proof-class block, and after an unknown class, still refuses (11); a topic with no PR and no `--pr` stays `topic:`-only so HELD-NOPR is unchanged (28).

## Figures

- `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED` at the handoff head; budgets flat, none re-recorded.
- Mutant counts above are the lines each self-test printed (instrument: the three `--self-test` commands, scope: the files named).

## Red checks

none

## Forward-carry

none

## Friction

none
