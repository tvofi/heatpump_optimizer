Triage batch 52 rules the ten owner-approved "regain time" cards (V168-V177, the research seat's P1-P10) as P254-P263. The rulings are ACCEPT 7 (four of them narrowed), DEFER 2 and REJECT 1. The owner approved the cards on 2026-10-28T17:47Z, but approval does not exempt any of them from `proposal-triage.md`'s bar.

- **P254 (V168) ACCEPT -> R10-FLOW-TOOLKIT-MODEL.** `replan.py:188` `is_done` does not count `absorbed`, so four absorbed groups are scheduled as open work. The carry adds an advisory for an absorbed group whose note names no absorber.
- **P255 (V169) ACCEPT, as practice.** Findings become carries on not-started groups that share a file or seam. This is the owner's existing-groups-first rule.
- **P256 (V170) ACCEPT narrowed -> R10-ORCH-REVIEW-PACKET.**
  - The handoff runs the packet's offline refusals that prepr lacks, plus a new `brief-carries` count.
  - The CI-dependent refusals stay at dispatch, because the owner rejected waiting for the gate (card 5, `review_packet.py` line 12).
  - The `fixer.md` line is policy: the group's PR merges only on tvofi's approving review.
- **P257 (V171) DEFER.** The saving is assumed. Most fixers now run on cloud seats, which SendMessage cannot reach, and the relay hop is the identity that posts the verdict. What would change it: the 2.3 h turnaround split at the dispatch.
- **P258 (V172) REJECT.** Main lands about every 50 min against a 2.13 h median wait, so an early recarry's CI is spent twice in about 92 % of cases. `--overlap` already recarries the queue up front.
- **P259 (V173) ACCEPT -> R10-FRICTION-REGRESSION, which absorbs the other four friction RCAs.**
  - One seat writes five records in one PR.
  - The body carries one `Closes` line per issue.
  - `root-cause.md` has no one-seat-per-trigger clause.
- **P260 (V174) ACCEPT narrowed to part (b), as practice.** #2923 merges first, and the opener refreshes its checkout before every open.
  - With the App key local, part (a) leaves nothing beyond P251.
  - #2923 has no roster group yet.
- **P261 (V175) ACCEPT narrowed -> R10-ARCH-DOCS.**
  - Arm A, the checker and resolver, can be dispatched now under the owner's override.
  - Arm B is the delta at the true merge base.
  - The re-run on every main merge is not carried.
- **P262 (V176) DEFER.** CodeQL is the pole at 33.3 min, so shards shorten nothing. The tail trim is unmeasured. What would change it: a per-step timeline of `gate` and the paired edit run.
- **P263 (V177) ACCEPT narrowed to the measurement**, which this seat re-takes once load1 stays below 20. It needs n of 8 or more windows, at least 3 on each side. The cap stays the owner's call.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`43577796eccf36d93b6943b061413f377899983a`; the file is the whole diff against `beb570c817c4efcae0d5f6f4bba52f3383baf8db`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate.
- On the committed file, `ruling_verdict` reads P254, P255, P256, P259, P260, P261 and P263 as `ACCEPT`, P257 and P262 as `DEFER`, and P258 as `REJECT`.
- Each of the four queued carry texts (citing `#P254`, `#P256`, `#P259` and `#P261`) passes the gate.
- Mutant (P259's verdict rewritten to `DEFER` in a copy): its carry is refused, `#P259 is not an ACCEPT ruling (DEFER)`, so the gate reads this line.

## Null control

With the file absent, the P254 carry returns `the triage ruling dev/programme/triage/s6-batch52.md is not on the roster branch or origin/main`.

## Figures

- `tools/plan/replan.py:188` `def is_done`; line 232 builds the done set from it.
- Stage `absorbed` on roster `2ce021c6f`: R10-ORCH-MACHINERY, R10-ROUTING-INVARIANTS, R10-FLY-POOL-INSTRUMENT, R10-FLY-RECORD-BEAT.
- `refs/pull/2923/head` `b04f9e93bd4ec068436a90f000a98851ed44318c`; no roster group names R10-FLY-ROWONLY-BASE.
- R10-ARCH-DOCS: 81 after-edges and 7 carries.
- `HPO_WIP_CAP` default 6 (`pr_cap.py:54`).
- The research seat's figures, each with its own command in its report and not re-run by this seat:
  - 71 blocked verdicts since 10-25.
  - +4.3 h per blocked round.
  - 2.13 h median from first merge verdict to merged.
  - A 50 min median gap between landings.
  - CodeQL at 33.3 min on run 40728676573.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

- P254 ACCEPT (V168): `replan.py` `is_done` counts `absorbed`, with an advisory for an absorbed group whose note names no existing absorber. Carry: R10-FLOW-TOOLKIT-MODEL
- P256 ACCEPT narrowed (V170): the handoff runs the review packet's offline refusals and a `brief-carries` count; one `fixer.md` sentence, so this group's PR merges only on tvofi's approving review. Carry: R10-ORCH-REVIEW-PACKET
- P259 ACCEPT (V173): one root-cause seat and one PR write the five friction records, absorbing four groups by held ops. Carry: R10-FRICTION-REGRESSION
- P261 ACCEPT narrowed (V175): arm A (the wiring-test checker and the target-marker resolver) is dispatchable now; arm B is the delta at the true merge base. Carry: R10-ARCH-DOCS

## Friction

none
