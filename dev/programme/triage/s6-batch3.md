# Proposal triage, session s6, batch 3 (P53)

One proposal, S6-T of the s6 orchestrator's out-of-tree `proposals.md` (09:35Z,
raised on an owner steer: the gate lease does not apply to cloud), ruled as P53
from `dev/governance/roles/proposal-triage.md`. Numbering continues after
`s6-batch2.md` (P45-P52, pull request #2689, unmerged at this base). GitHub
calls: 0.

A roster op citing an ACCEPT below resolves only once this file is on the
roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P53: open_pr.sh re-runs the full prepr under the gate lease, twice per open
Verdict: ACCEPT NARROWED -> R10-FLY-OPENPR-ATOMIC (new carry: the second push takes `--row-only`); candidates (a) and (b) are DEFERRED
Source: s6 proposals.md item S6-T (09:35Z).
Instances: 1 observed, 1 mechanism in the tree. The observation: at 09:30Z all
four heavy slots were held by open prepr runs and the critical-path ratio-anchor
open queued behind them (the item's own measurement; not in the tree). The
mechanism is in `tools/audit/seat/open_pr.sh`: it runs `app_push.sh` twice per
pull request, `p1` for the code head (line 58) and `p2` for the one-commit
delivery-row push (line 71), both without `--row-only`
(`rg -n 'app_push|_push' tools/audit/seat/open_pr.sh`). `update_pr.sh` passes
`--row-only` for exactly that push shape (`rg -n 'row-only' tools/audit/seat/update_pr.sh`
prints line 74), and `app_push.sh` lines 107-120 give the reason ("on a loaded
box the full prepr held a one-line row 30+ minutes") and the four conditions
(one parent, one added `delivery/<N>.md`, a one-line open row, the live body
under one new `## Head` note) under which the flag replaces prepr with the
contract and carry checks; anything else runs the full prepr. open_pr's `p2`
is built to meet those conditions (`commit_row` then a `## Head` note by
`head_note.prefix`), so it pays a full prepr, and a lease slot, for the push
the flag exists for.
Cost: XS -- `--row-only` on the second push in `open_pr.sh` (one token), a
self-test row in the style of `pr_args.sh` lines 840-854 (a row push passes the
flag; the null control: the code push does not), one mutant. `R10-FLY-OPENPR-ATOMIC`
already edits that second push (its brief: the second push of the delivery
row).
Binding: the flag halves the opener's prepr runs and lease-slot time per open
at no new surface: the four conditions are read by `app_push.sh` and fail
closed to the full prepr. CI's `gate` stays the authority. Candidate (a), skip
the local prepr on a stamp from the cloud fixer's run, is DEFERRED: the opened
head is not the tree the cloud ran (open_pr merges origin/main into the code
head and adds the row, per the `## Head` notes in lines 50-52 and 63-66), so a
stamp at "the exact code SHA" does not cover it, and a stamp protocol on the
handoff-body ref plus its verification in `app_push.sh`, a hot file of about
1000 lines, is M-L against an unmeasured saving. What would change the answer:
the queue wait of critical-path opens measured over three or more opens after
the `--row-only` carry lands (the lease log or `p1.log` and `p2.log` durations).
Candidate (b), run the opener's prepr in a cloud routine, is DEFERRED to the
same measurement: it moves the cost to a routine (tokens and a dispatch per
open) and the opener then cannot report its own refusal in line. The owner's
steer is the orchestrator's to weigh against this: if "the lease does not apply
to cloud" is meant as a ruling that the opener must not take a local slot at
all, that is the owner's decision (a) or (b) implements, not a cost/benefit one.
