# Proposal triage, session s7, batch 46 (P232-P234)

Three entries: V146-V148, written by the orchestrator s8 on 2026-10-28 and quoted from
`proposals.md` as they stand (V146 is a reviewer's report and V148 a fixer's, both routed by the
orchestrator). Facts read at origin/main `53c4b9cb0`; roster at `origin/handoff/audit-r10-roster`
`5704c4048` (213 groups). Headings carry no proposal id (P219); the `Source:` line is the one place
an id is written. The owner's standing order for this cut is critical path first, then production,
then instruments by time and tokens saved, and no item may be deferred outside round 10.

## P232: `carry_audit` reads 0 finding items on verdicts whose findings end in `Carry:`

Verdict: REJECT.

Source: `proposals.md` V146 (reviewer s8 report, routed by orchestrator s8, 2026-10-28).

Instances: none of the defect. The figure behind it is real but is not the guard's read.
- The 0 is the review packet's line. `tools/audit/seat/review_packet.py:327` runs
  `carry_audit.py check --body {BODY}` on the pull-request body alone, as its refusal list says
  (`:31`, "returns 1 on the body"), and prints it under `## carry_audit at the head` (`:308`).
  A body whose `## Forward-carry` and `## Friction` are `none` has 0 finding items by design
  (`carry_audit.py` docstring, "A FINDING item": body items come from those two sections or a
  LEAD). That is the line in #2900's round-2 packet (`ev/packet.md:52` of its review,
  `CARRY-AUDIT: 0 finding item(s)`).
- The merge guard reads the comments. `queue_pre_flight.py`'s `findings_gate` (`:176`) fetches
  the body and every issue comment, and calls `carry_audit.finding_rows(body, comments)` (`:192`),
  which parses each comment whose first line matches `VERDICT` (`carry_audit.py:91`).
  On #2900's live body and its two `hpo-approver` verdicts (comments 6458631147 and 6459350190,
  fetched to a scratch `--from-dir`): `carry_audit.py --roster-ref origin/main sweep --prs 2900
  --from-dir <dir>` prints `CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted`. Three of the
  seven named verdicts are on this host, and `check --comments` on each reads finding items:
  2900 1, 2891 2, 2899 2, all routed.
- The blocking findings are not items on purpose: in a `blocked` verdict a finding outside a
  non-blocking heading is the block, owed in this pull request (`items()`, the `blocked_verdict`
  branch at `carry_audit.py:189`). So `F1 (blocking)` is not counted, and `F2 (non-blocking)` is.

Cost: a parser change in `carry_audit.py`, a code-owned file (`.github/CODEOWNERS:89`), plus a
self-test fixture, against a parser that already reads this verdict shape.

Binding: the premise is false. The guard is on and reads these verdicts, and the 0 comes from the
packet's body-only check, which is correct for these bodies. Relabelling the packet heading to say
"on the body" would prevent this one misreading, and one misreading is a marginal trade. It is not
carried.

## P233: the relay updates a pull request from a handoff whose body has not been pushed yet

Verdict: ACCEPT narrowed -> a carry of **R10-FLOW-BODY-ONLY** (`resume.stage` `not-started`, 13
carries, owns `tools/audit/seat/cloud_relay.sh`, `update_pr.sh` and `pr_args.sh`). It is the live
group on the relay's handoff-to-update seam, and its carries 3 and 5 already shape that arm. The
carry also edits `tools/audit/seat/body_push.sh`, which is not in the group's `files`. Widening
`files` is the roster seat's call, made with `edit-brief`, as for P227.

Source: `proposals.md` V147 (orchestrator s8, 2026-10-28).

Instances: three races and one failure with no recorded reason.
- The order is forced. `body_push.sh:40` refuses a body unless `handoff/<topic>` is already the
  checkout's HEAD ("push the code, then the body"). The relay's handoff arm acts on any open
  pull request whose `handoff/<topic>` is not an ancestor of its head, using whatever tip
  `handoff-body/<topic>` has (`cloud_relay.sh:409-428`). So every re-cut opens a window, between
  the code push and the body push, in which the relay updates with the previous body.
- #2890 and #2891 (triage batches 41 and 42, 2026-10-27): the relay re-bodied each from the stale
  `handoff-body` tip after the code moved. This seat's state file records it ("it did for #2890
  and #2891").
- #2894 (orchestrator s8): a relay update ran about 30 min holding the branch lock (pid 18235) and
  then failed. Its `cloud-handoff-failed` entry records `<topic> <sha>` with no reason.
- #2887: posted with a stale body (orchestrator s8's filing).
- Reason lost, measured today. At 03:43:15Z the relay's update of #2900 at
  `handoff/triage-s6-batch45` `2d296452f` refused with `update_pr: REFUSE: STALE CHECKOUT
  44013081419a behind origin/main 53c4b9cb0de4 by 13 commit(s)`. The reason reached only the
  loop's stdout log. `<state>/cloud-handoff-failed` (`cloud_relay.sh:392`) line 115 reads
  `triage-s6-batch45 2d296452f6db74afc8f8dd590f34daf27cb0d6dc`, and the level line is written
  without its `why` (`cloud_relay.sh:444`, though `level_line` takes one at `:165`).

Cost: one trailer line in `body_push.sh`'s `commit-tree` message (`:73`). In the handoff arm, one
`git log -1 --format=%B` of a commit it already fetches, one comparison, and the refusal's last
line passed to an existing argument. Plus four self-test rows. No new API call, file or check.

Binding: the race recurs on every re-cut, because `body_push.sh` forces the order that opens it.
It costs a wrong body (posted twice in one instance) and, when the update then fails, a held
branch lock and a failed-list entry that blocks retries until the code moves again. Narrowed
against the filing: "newer than" is replaced by the body naming the exact code sha it was
linted against. `body_push.sh` already proves that equality at `:40`, so no clock is compared.

Carry text (for `roster_edit.py append-carry R10-FLOW-BODY-ONLY`, citing `triage:
dev/programme/triage/s6-batch46.md#P233`): "A handoff updates only with the body pushed for it
(V147). (a) `tools/audit/seat/body_push.sh` adds a trailer line `Code: <40-hex>` to the body
commit's message (`commit-tree -m`, :73). The sha is `handoff/<topic>`'s tip, which :40 has just
proved equal to the checkout's HEAD. A result body with no `handoff/<topic>` writes no trailer.
(b) In `cloud_relay.sh`'s `handoff_arm`, after it fetches `handoff-body/<topic>` and before it
runs `update_pr.sh`, it reads that tip's message. If the message has a `Code:` line naming a sha
other than `hs`, it does not update: it writes `level_line handoff-body-stale
refs/heads/handoff/<topic> <hs>` with why `body names <sha12>` and retries on the next pass, with no
`cloud-handoff-failed` entry. A body commit with no `Code:` line (refs pushed before this change)
updates as today. (c) A failed update records why: the last line of `update_pr.sh`'s output that
contains `REFUSE`, else its last line, goes into the `handoff-update` level line's `why` (the 4th
argument of `level_line`, :165, at :444). `cloud-handoff-failed`'s `<topic> <sha>` lines are
unchanged, since :421 matches them whole. Instances: #2890 and #2891 re-bodied stale (2026-10-27);
#2894's failed update with no reason (pid 18235, about 30 min on the lock); #2887's stale body;
#2900 at 03:43:15Z on 2026-10-28, `STALE CHECKOUT` in stdout only, and `cloud-handoff-failed`
holding `triage-s6-batch45 2d296452f...` bare. Controls (the self-test's bare-origin fixture at
cloud_relay.sh:711-749): handoff moved and the body's `Code:` names the old sha, so no
`update_pr` call and one `handoff-body-stale` level line; then the body names the new sha, so the
update runs with that body; a body with no `Code:` line updates as today; a stub update printing
`update_pr: REFUSE: X` and exiting 1 leaves a `handoff-update` level line ending in that line.
Mutant: an arm that ignores `Code:` fails the first control."

## P234: prepr's no-copies step runs the first `python3` on PATH, which cannot parse the tree

Verdict: ACCEPT narrowed -> a carry of **R10-PREPR-CAP** (`resume.stage` `done`, 1 carry, owns
`tools/pr/prepr.sh` and `tests/gate_lock.py`, the group that holds prepr's run-time environment).
The group is reopened first (the P196 route). It is chosen over `R10-FLY-NO-FOOTERS`, the one live
`prepr.sh` owner, because that group's seam is attribution footers. Owner order: critical path,
since every pull request's handoff runs this step.

Source: `proposals.md` V148 (fixer s8, #2894, 2026-10-28).

Instances: one reported, and the trap is standing.
- `tools/pr/prepr.sh:1034` (`copies_line`, the filing's `:875` before main moved) runs
  `PYTHONPATH=tests/hastub python3 tests/closure.py no-copies`, with a bare `python3`.
  Reproduced at `53c4b9cb0`: under Python 3.11.5 the step prints `SyntaxError: f-string:
  f-string: expecting '}'`, which is a false refusal. Under the seat venv (Python 3.14.7) it
  prints `closure: no test file defines a symbol production also defines`.
- A clean environment resolves `python3` to `/usr/bin/python3` (3.9.6) on this host
  (`env -i PATH=/usr/bin:/bin:... command -v python3`).
- The interpreter resolver already exists: `recorder_python` (`prepr.sh:519-533`) tries
  `$HPO_RECORDER_PYTHON`, then the seat venv, then the ambient `python3`, and keeps the first that
  parses the tree. Its self-test fixtures are at `:2383-2392`. Step 6a uses it (`:716`), but
  `copies_line` does not.
- The standing cost: every seat brief carries a PATH workaround for this step. The s7 preamble's
  item 3 says that without the venv first, "prepr's no-copies dies on a PEP 701 f-string
  SyntaxError".

Cost: a few lines in `copies_line` and two self-test rows reusing the `recorder_python` fixtures,
in the 3,927-line hot file. One `recorder_parses` run takes 5.30 s here (`/usr/bin/time -p`, seat
venv, `53c4b9cb0`). The step pays it once per prepr run, and only when the diff touches a `.py`
under `tests/` or `custom_components/`. It pays nothing when step 6a has already resolved the
interpreter.

Binding: a false refusal on the critical path, a resolver that already exists, and a brief trap
that every seat pays to read. The trade is clear. Narrowed against the filing: this step only.
The rest of `prepr.sh`'s bare `python3` calls are not in the instance and are not carried.

Carry text (for `roster_edit.py append-carry R10-PREPR-CAP`, citing `triage:
dev/programme/triage/s6-batch46.md#P234`): "no-copies runs an interpreter that parses the tree
(V148). In `tools/pr/prepr.sh`'s `copies_line` (:1034), replace the bare `python3` with the
interpreter `recorder_python` (:519) prints, the resolver step 6a already uses (:716). Resolve it
once per prepr run and share the result with step 6a, since one `recorder_parses` costs 5.30 s
here. When
`recorder_python` finds none, the step returns 1 with its remedy line, so a missing interpreter
is never read as a copy or as a skip. Instance: #2894 (fixer s8, 2026-10-28), a false `no-copies`
refusal under the system Python 3.11 that was clean under the seat venv's 3.14.7. Reproduced at
`53c4b9cb0`: 3.11.5 prints `SyntaxError: f-string: f-string: expecting '}'`. Controls, reusing
the `recorder_python` fixtures (:2383-2392): a PATH whose first `python3` cannot parse the tree,
plus a parsing seat venv, means `copies_line` runs the venv and returns 0 on a clean tree; with no
parsing interpreter it returns 1 and its line names `seat_venv.sh`; null control: with
`HPO_RECORDER_PYTHON` set to a parsing interpreter, that one runs. Mutant: restoring the bare
`python3` fails the first control. Out of scope: prepr.sh's other bare `python3` calls."
