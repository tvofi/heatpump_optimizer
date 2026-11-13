# Proposal triage, session s14, batch 189 (P611)

The bar and the denominators are batch 141's.

Record note (P610): the text P610 ruled on, roster-branch writer concurrency, reached this seat in its
seat brief from the orchestrator. It was never a line of the triage queue file. Physical queue line 289
is this proposal, appended at 11:32:33Z.

Sources:
- origin/main `ee64358be7`. Every line number below is at that commit.
- The origin refs `dispatch/fixer-*`, `handoff/*`, `handoff-body/*` and `handoff-wip/*`, fetched at 11:37Z.
- The relay's `tick-loop.log`, `tick.txt.relay.log` and `cloud-folded`, under the r10s6 state directory.

## P611: CLOUD-STOP-BEFORE-BODY

Verdict: ACCEPT narrowed, as a new group R10-RELAY-NOBODY-STALL. Arm (a) is accepted as a defect fix to
the relay's existing fold arm. Arm (b) is accepted with a measured threshold of 60 min, not 25 min. Arm
(c) is rejected. The class owes a root-cause seat.

Source: queue line 289, 2026-11-11T11:32:33Z, orchestrator s14.

Measurements:
- **Share of fires that return code without a body.** The harness is `s14-16/nobody.py`, run over the
  bare fetch of the four ref families.
  - A fire is one commit on `dispatch/fixer-<topic>`; commits less than 10 min apart count as one
    fire. A fire's window runs to the next fire on the same topic, or to now.
  - A fire is classed by what its window holds:
    - `body`: a `handoff-body/<topic>` commit at or after the first `handoff/` or `handoff-wip/`
      commit.
    - `code-no-body`: a code commit and no body.
  - 2026-11-04 to 11-11: 628 fires over 212 topics.
    - 460 fired with a body.
    - 124 (19.7%) returned code without a body. 113 of those were re-fired, and 11 are still open.
      50 of the 124 had no body at any earlier fire.
    - 20 pushed a body before code; 24 returned nothing.
  - From a code-without-body fire to its re-fire: median 174 min where a body existed earlier, 196 min
    where none did.
  - If the claim were false, `code-no-body` would be near zero, and the four named topics would class
    as `body`. All four class as `code-no-body`.
- **Arm (a) already exists, and is broken for some blocks.** The relay's carry-fold arm landed in
  `67a823c2e7` (2026-11-08, `cloud_relay.sh` `carry_fold_arm`, `:805`).
  - It folds the carries and re-runs `body_push.sh` from the kept body. `cloud-folded` holds 6 folds.
  - It reads the refusal with `sed -n 's/^body_push: REFUSED .../p'` (`:819`), anchored at column 0.
  - The handoff-wip refs hold 8 BLOCKED.md files naming CARRY-LANDED. 3 of the 8 have the line
    indented: r10-combi-tank-pr, r10-rca-dependabot-stale-hash and r10-standing-contracts-p2.
  - Each of those 3 printed "BLOCKED.md names no refusal line ... nothing folded" at every pass.
    `tick-loop.log` holds that line for r10-standing-contracts-p2 at `878695f8158c`, the critical-path
    case in this proposal.
  - Null control: the 5 blocks with the line at column 0 are the ones folded.
- **Arm (b) needs a different threshold.** For the 460 fires with a body, the delay from the last code
  commit to the body is median 10 min, p75 28 min, p90 48 min.
  - At 25 min, the owed line would fire on more than a quarter of healthy fires. At 60 min it fires
    on fewer than 10%.
  - Two detectors exist today, and neither covers this class:
    - The relay's `noreturn_arm` counts any moved code ref as a return.
    - The ledger's `no body ref` escalation (`ledger.py:609`) waits `AGING_DEFAULT` 4 h (`:127`).
- **Three of the four named stops wrote no BLOCKED.md at all.** r10-relay-arm-order,
  r10-gh-read-residue-p2 and r10-hotfix-combi-census-main-red each have a wip tip and no BLOCKED.md.
  - No repair arm can act on them. They can only be detected.

Disposition:
- **(a) ACCEPT narrowed: RELAY-FOLD-INDENT.** `carry_fold_arm` reads a `body_push: REFUSED <KIND>`
  line with leading whitespace exactly as it reads one at column 0.
  - Self-test: an indented CARRY-LANDED-only block is folded.
  - Self-test: an indented block naming a second kind is not folded.
  - Self-test: the column-0 cases stay as they are.
- **(b) ACCEPT narrowed: RELAY-NOBODY-OWED.** Extend `noreturn_arm` (`cloud_relay.sh`) so a fire still
  owes when `handoff/<topic>` or `handoff-wip/<topic>` moved after the fire, no `handoff-body/<topic>`
  moved after it, and the newest code commit is older than `HPO_RELAY_NOBODY_SECS`, default 3600.
  - The owed line names the topic, the code tip, its age, and the fire it owes: a continuation.
  - For a CARRY-LANDED-alone BLOCKED.md, the line instead names the fold already pending.
  - Self-test: a fire with a body at 30 min is silent.
  - Self-test: code without a body at 61 min owes.
  - Self-test: a body older than the fire does not count as a return for the fire.
- **(c) REJECT.** Landing carries relay-side is arm (a), so (c) adds nothing beyond it.
  - Letting `body_push` write the roster from a cloud fixer would add a roster writer the seat
    contract withholds. That is a policy change, and it is not taken here.
- **Root cause: owed.** With 124 instances in 7 days, this is far past the third. Arms (a) and (b)
  detect and repair the stop; they do not name its cause.
  - A root-cause seat (`root-cause.md`) owes a named cause for silent stops between code and body,
    with a process state, a cost test and a countermeasure or a recorded refusal.
  - Its inputs: the 50 never-body fires, and the 3 silent stops of 2026-11-11.
  - The orchestrator dispatches it. It is not a carry.

Group R10-RELAY-NOBODY-STALL: size S, instrument. Files: `tools/audit/seat/cloud_relay.sh`. It runs after
R10-RELAY-ARM-ORDER, whose fixer is live on the same file (re-fired 11:31Z).
