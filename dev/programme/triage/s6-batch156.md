# Proposal triage, session s14, batch 156 (P568)

This batch rules `s7/triage-queue-s7.txt` line 251, which arrived after batch 155. The bar and the
denominators are batch 141's.

Sources:
- origin/main `444cf62fab` (`tools/audit/seat/review_packet.py` is unchanged from `63bcdcaad8`);
- the dispatch seat outputs under `S/s13/seat/` and `S/s14/seat/dispatch/`;
- `merge_train.py classify` and the check runs at PR 3404's and PR 3429's live heads, read at
  about 02:50Z.

## P568: S14-PACKET-REFUSES-DEFERRAL-RED

Verdict: ACCEPT, at a narrowed fix site. It repairs an observed wrong behaviour, and the instances
form a class (at least 3). The permanent form reuses the classify answer the packet already
gathers. It does not add a second read.

Source: queue line 251 (2026-11-11T02:34:53Z, the dispatch seat, PRs 3404 and 3429).

Instances:
- **Reproduced on both named heads.**
  - `merge_train.py classify 561edf4c8f --pr 3404` printed
    `WAIT 561edf4c8f... pending: gate red: none`. The head's one `gate` check-run, from run
    42945740958 (`CI edit`), is `completed failure`.
  - `classify 498c2ab042 --pr 3429` printed `WAIT ... pending: gate red: none`, beside two
    `completed failure` gate check-runs (42946500173 and 42946386595).
  - The dispatch outputs `s14/seat/dispatch/bus3404.out` and `bus3429.out` each hold exactly
    `review_packet: REFUSE red-unanswered: concluded red check \`gate\` is not named in ## Red
    checks`, then `bus: REFUSE: dispatch`.
  - A false premise would have looked like classify reading RED, which would make the refusal
    right, or like a different refusal signal.
- **How often it happens.**
  - `grep -rlF 'red-unanswered: concluded red check \`gate\`'` over the state directory finds 14
    files.
  - 3 of them are today's dispatches, `bus3424d.out`, `bus3404.out` and `bus3429.out`, from
    01:51Z to 02:33Z (file modification times).
  - 7 are from session 13 (PRs 3415, 3416, 3417 and 3419, 2026-11-10).
- **The cause, read in the code.** `review_packet.main` gathers
  `read = required_reading(a.pr, head)` whenever a required context is red (line 602). That is
  `merge_train.py classify --pr`, the same answer `bus.sh dispatch` uses.
  - `build` already turns a WAIT or GREEN read into a `required-wait` or `required-green` advisory
    for the `required-red` arm (lines 544-557, #3379).
  - But the `red-unanswered` arm runs first, at lines 542-543, over
    `unanswered_reds(..., gate[2], ...)`. It refuses the same `gate` red without consulting the
    read.
  - So one red reaches two arms, and only one of them defers.
  - The self-test at line 784 passes only because its facts set `red_unanswered` to `[]`.

Cost: in `build`, an entry of `facts["red_unanswered"]` that is in `REQUIRED` gets no
`red-unanswered` refusal when `facts["required_read"]`'s word is WAIT or GREEN. Its `required-wait`
or `required-green` advisory already names it.
- A RED, an APPROVAL-OWED or an unreadable read keeps today's refusal. A red outside `REQUIRED`
  keeps today's refusal.
- There is no new read. The classify call already made at line 602 is the one that decides.
- The local version, commit 572755fb70 on `s14-tools-63bcdcaa` (never pushed, +35/-1 in
  `build`), already reads the gathered `facts["required_read"]` and makes no second read. It is a
  valid base for the permanent form. (Correction: this ruling's first text said the local fix
  called `Train.classify_at` a second time. That rested on the queue line's description, written
  before the fix existed. I read the commit afterwards.)
- Self-test, in `review_packet.py`:
  - the 3404 shape (`red_unanswered=["gate"]`, `required_read=("WAIT", "pending: gate red: none")`)
    renders with one `required-wait` advisory and no refusal;
  - the same with `("RED", ...)` refuses `red-unanswered` and `required-red`;
  - the null control: a non-required red (`tests / fast`) with a WAIT read still refuses
    `red-unanswered`;
  - a mutant that drops the WAIT/GREEN condition fails the first case.
- `review_packet.py` has no row in `tests/structure_budgets.json`.

Binding: a reviewer is owed when the fixer pushes, not when CI settles (orchestrator.md section 5).
Each instance today cost 20 to 40 minutes of reviewer latency plus a seat polling and re-running
(the source's figure). The fix is one condition in an existing arm, using the answer the arm
already holds.

Routing: one carry goes to R10-REVIEW-DISPATCH-RESIDUE, which owns `review_packet.py` and holds
P559's and P564's carries on the same file. It is `not-started`, so the carry is plain. Carry file:
`b156-P568.txt`.
