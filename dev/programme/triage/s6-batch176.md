# Proposal triage, session s14, batch 176 (P593)

This batch rules queue line 272 (the orchestrator's intake), 2026-11-11.

Sources:
- origin/main `f24d107bd7`. Every line number below is at that commit.
- The roster branch `handoff/audit-r10-roster` at `988e5cf6ba`, and its history for
  R10-REVIEW-DISPATCH-RESIDUE's `carry` list.
- The `handoff-wip/<topic>` and `handoff-wip/<topic>-body` refs of the three topics, their
  `BLOCKED.md` files, the relay's `cloud-fold.out`, and `dispatch/fixer-r10-review-dispatch-residue-p3`'s
  `PROMPT.md`.

## P593: BRIEF-CARRIES-PART-SCOPE

Verdict: ACCEPT, re-scoped, as a carry on R10-REVIEW-DISPATCH-RESIDUE (stage in-progress). That
group owns `tools/audit/seat/review_packet.py`, and its own parts hit the defect.

Source: the orchestrator's queue line 272, 2026-11-11. Three fixer handoffs left a refused body on
`handoff-wip/<topic>-body` and no `handoff-body/<topic>`.

Measured: the refusal kind of each stranded body. `body_push.sh` prints `body_push: REFUSED <KIND>`
to stderr only, and the kept commit says only "refused body: <topic>". So the kind comes from each
fixer's `BLOCKED.md` or, where there is none, from the diff between the refused body and the body
that later passed.
- **r10-review-dispatch-residue-p1** (`819f39ac5b`, 07:22Z). Its `BLOCKED.md` names REVIEW-PACKET:
  `brief-carries: carry 1 ... carry 24 is not named in the body`. The part's brief assigns it Carries
  14 and 22 by their 0-based roster index. The check demands every carry of the whole group, numbered
  from 1.
- **r10-dependabot-3414-compat-p2** (`ac966c9e96`, 07:51Z). There is no `BLOCKED.md`. The body that
  passed (`handoff-body`, `767634fbd9`) differs from the refused one only by the added lines
  `Carry 1 ...` and `Carry 2 (the same text, second roster index) ...`. That is the same
  `brief-carries` refusal. The roster holds the carry twice, and the fixer had to answer the
  duplicate.
- **r10-review-dispatch-residue-p3** (`5a2a3bb4a2` and `587a30e2c0`, 08:05-08:07Z). Its `BLOCKED.md`
  names CARRY-LANDED. That missing carry is the fixer's own item `review-packet-brief-carries:
  contradiction`, which reports that the packet refused this part's body for 18 group carries the
  part's brief says to answer none of. The relay's carry-fold arm folded it and re-ran `body_push.sh`,
  which refused again (`cloud-fold.out`): `REFUSE brief-carries: carry 25 is not named in the body`.
  - **Carry 25 is this seat's P592**, appended at `4cc00eec0f`, 08:06:52Z. The group held 24 carries
    at `315a274656` (08:06:03Z), 23 when p3 was dispatched (its PROMPT says "The group's 23 carries"),
    and 25 at `4cc00eec0f`.
  - Had the count been read at dispatch, the re-run would have printed no carry-25 line.

One cause, three faces. `review_packet.py handoff` (`:720-736`) reads the group's carry count at the
roster ref's tip (`fetch_roster_ref`) and `unnamed_carries` (`:547`) demands `Carry 1..n`. So:
1. **Scope.** A split part must name every carry of the group, though its dispatch brief assigns it
   a subset (p1, and p3's contradiction item).
2. **Base.** The part brief numbers carries 0-based (`Carries 2, 3, 8, 9, 13 (0-based roster
   indexes`), and the check numbers them 1-based. A part that answers "Carry 2" as its brief names it
   satisfies a different index.
3. **Time.** A carry that triage, a fold or the roster appends after dispatch refuses every in-flight
   part at its handoff (p3, carry 25). Such a carry rides the group's next part, and the P592 carry
   says so itself.

Not the cause: the CARRY-LANDED arm. It worked for p3, and the fold landed the contradiction item.
The p2 refusal was correct on its face (it had not named its two carries), and only the duplicate
roster index was noise.

The fix, in `review_packet.py`'s handoff only:
- When `dispatch/fixer-<topic>` exists on origin, count carries at the roster commit that was the
  tip at that dispatch commit's time. Demand only the indexes its `PROMPT.md` line `This part:
  Carries <list> (0-based roster indexes` assigns, spelled as the prompt spells them.
- With no dispatch ref (a local fixer) or no part line, keep today's whole-group count at the tip.
  That is the null control.
- The refusal names the base it reads ("carry 13 (0-based, this part's brief)"), so that a fixer can
  repair it without a continuation.

Self-test:
- A part prompt assigning {2, 3} with the group at 5 carries passes a body naming Carry 2 and
  Carry 3.
- The same body is refused when Carry 3 is missing.
- A carry appended after the dispatch time is not demanded.
- Null control: with no dispatch ref, all 5 are demanded, as today.

What it costs and what it saves:
- **Cost:** about 40 lines in `review_packet.py` (one `git ls-remote`, one `git show` of
  `PROMPT.md`, and one `rev-list -1 --before` on the roster ref), plus four self-test checks.
- **Benefit:** 3 stranded handoffs in one day. Each cost a continuation fixer or a relay fold-and-retry
  pass, plus orchestrator attention. Three parts of this group (p2, p5, p6) are still to be
  dispatched, and each would meet the same check.
- It clears the 20% bar as a carry.

**Ordering:** this carry and P592 both ride the group's next dispatched part. That part should build
this one first, because every part after it is then immune.

**Immediate repair, not this ruling's to perform:** p3's kept body needs a `Carry 25:` line
(P592, not this part's, rides the next part), and a `Carry 26:` line once this carry lands. The
orchestrator or relay re-runs `body_push.sh`. Appending this carry raises the group to 26 at the tip.
p1 and p4 already hold `handoff-body` refs and are not re-checked.
