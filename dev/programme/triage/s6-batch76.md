# Proposal triage, session s8, batch 76 (P312-P313)

The rolling batch (V182) after batch 75 (handoff `triage-s8-batch75`). Two proposals from the
orchestrator s8 (2026-10-30T21:40Z and 21:45Z). Facts were read at origin/main `437f1ba9b`, on the
roster branch, in the orchestrator's `seat-ledger.md`, in the live merge-train log
(`merge_train/train.log`), and in the verdict and `handoff-body/*` refs on origin. The long run
(`brief_lint.mjs`, 73 s) ran detached.

## P312: the train cannot put a hotfix or critical-path entry first in its next batch

Verdict: ACCEPT narrowed, a carry on **R10-TRAIN-OVERLAP-GRADE** (`carries-open`). It owns the
train's admission and drain (`already_held`, `Train.queue_take`; P129, P189, P291). It may be
dispatched alone, ahead of the group's other carries.
- **Narrowed to the drain, not a new verb.** `Train.queue_take` (`merge_train.py:2892`) moves the
  whole spool into one new batch. It now stable-sorts that batch by priority:
  - a HOTFIX entry first (an explicit `add --priority N` stored on the spooled entry);
  - then a critical-path entry (the train's own `_critical`, line 1273, the roster's
    critical-path set that `tools/pr/gate_priority.py` also derives from);
  - then the rest in arrival order.
- **REJECTED: a `train.sh prioritise/move` subcommand.** It would be a second writer of the spool
  beside `add` and `queue_take`, under the same lock, and it re-orders by hand what the priority
  can derive.
- **REJECTED: reading `gate_priority.py` itself at `add`.** That script reads a worktree's
  `.gate-priority` and `$HPO_GATE_PRIORITY` for the gate lease, neither of which a spooled entry
  has. The train already holds the one derivation that applies, `_critical`.

Source: the orchestrator s8's message of 2026-10-30T21:40Z.

Instances (`seat-ledger.md`):
- `:2718`, 2026-10-30T21:35:52Z: "merge s8: per the orchestrator (no train restart), reordered the
  live train's spool queue-add.jsonl under the train's own queue.lock flock, atomic replace: next
  batch order #3013, #2968, #3009". HOTFIX #3013 was moved first by hand, which bypasses the
  instrument (`orchestrator.md` section 13).
- `:1770`, 2026-10-27T20:23Z: "spool reads 2853 ..., 2888, 2876; no reorder/remove verb and I will
  not hand-edit under the live lock, so #2876 waits behind #2888's gate". The same gap, answered
  that time by waiting.
- **Queue depth, from the train log.** Of 41 `ADDED ... batch K of this train` lines, 16 joined at
  batch 3 or later (11 at 3, 4 at 4, 1 at 5). So an entry spooled mid-train often waits behind one
  or more formed batches. Within its own batch, its order decides the merge sequence and who
  recarries.

Cost:
- About 10 lines in `queue_take` and `train_add`/`train.sh add` (a `--priority` integer, default
  0, stored on the spool line), plus three fixture rows.
- No new file, lock, writer or API call. `merge_train.py` is a hot file (6703 lines); the seam is
  the drain, which this group already owns.

Binding:
- Two instances in four days. One was a production hotfix moved by hand under the train's lock,
  a bypass the orchestrator's own contract calls a defect. Against a stable sort in the one
  function that forms the batch, the trade is clearly positive.
- The host's three-round risk (21 carries, its stage flipped six times since 2026-10-28) is why
  this carry may be dispatched alone, as a small PR.

Carry text (for `roster_edit.py append-carry R10-TRAIN-OVERLAP-GRADE`, citing
`triage: dev/programme/triage/s6-batch76.md#P312`): "P312 (orchestrator 2026-10-30T21:40Z). May be
dispatched alone, ahead of this group's other carries.
- `train.sh add` / `train_add` accept `--priority N` (an integer, default 0), stored on the spooled
  entry.
- `Train.queue_take` (`merge_train.py:2892` at 437f1ba9b) stable-sorts the batch it forms from the
  spool by: priority descending, then critical path (`Train._critical`, line 1273) first, then
  arrival order.
- No reorder or move verb, and no second writer of the spool.
- Observed: `seat-ledger.md:2718` (2026-10-30T21:35:52Z), where the merge seat hand-edited
  `queue-add.jsonl` under `queue.lock` to put HOTFIX #3013 first; and `:1770` (2026-10-27T20:23Z),
  where #2876 waited behind #2888 for want of a verb. In the train log, 16 of 41 mid-train adds
  joined at batch 3 or later.
- Self-test rows:
  - A spool of [plain, critical, plain, priority 2] drains as [priority 2, critical, plain, plain].
  - Null: an all-plain spool keeps arrival order exactly.
  - A priority entry already held (`already_held`) is still ALREADY, never re-run.
- One mutant: drop the sort, and the first row fails."

## P313: prepr runs brief_lint only when a pinned path changed, so a line shift breaks a cited anchor

Verdict: DEFER. The benefit is one confirmed instance in round 10 (two mentions), and the cheapest
fully-specified option costs more than that.
- The filing's two options are (i) run step 3f when the diff touches any file a carry or roster
  brief cites by `path:line`, and (ii) run a citation-only fast pass every time.
- (ii) does not exist yet: `brief_lint.mjs` has no citation-only mode.
- The full run that (i) would trigger costs 73 s of one core, measured here. That cost lands on the
  many instrument PRs that touch a widely cited file (`merge_train.py`, `prepr.sh`,
  `carry_audit.py` ...).

Source: the orchestrator s8's message of 2026-10-30T21:45Z, from the #3011 round-2 fixer.

Instances:
- **#3011, confirmed.** Verdict `08765983a`: "blocked 75b30a4e... gate-red: tests / briefs fails at
  this head because the two imports added to tests/doc_claims.py move carry-1645.json's cited
  anchor tests/doc_claims.py:476 out of brief_lint's one-line window, and the body says Red checks:
  none". One review round lost.
- **One more mention.** The `handoff-body/r10-roster-lint` body quotes a brief_lint line, `path:line:
  const.py:1149: 'heatpump_optimizer' not found near custom_components/heatpump_optimizer/const.py:1149;
  found at line 10 instead`. That is a line-shifted citation in a roster brief, read by a lint run,
  not a blocked review.
- **Searched for others.** The subjects of every `verdict/*` and `archive/verdict/*` commit since
  2026-10-18 hold one tests/briefs line-shift block (#3011). The other `briefs` hits are
  carry-missing blocks about the R10-BRIEFS-FOLD group, a different class. Of the 223
  `handoff-body/*` tips, two mention a "not found near" or "found at line N instead" result
  (r10-arch-docs-wiring, which is #3011's own round 2, and r10-roster-lint).
- **Cost of the full run.** `node tools/policy/brief_lint.mjs` at `437f1ba9b`, detached: rc 0 in
  73 s.

Binding:
- One blocked round (a median 84 min block, per P310's enumerator) in about five days, about
  17 min/day. Option (i) charges 73 s of a core on every handoff that touches a cited file, plus an
  S build of the cited-file set.
- The CI `tests / briefs` job already catches the shift at the PR, as it did on #3011. The lost
  round came from the body's "Red checks: none" against a red job, a body-truth slip that
  `prepr`'s red-check arm and the reviewer own, not from a missing detector.
- Marginal at best, so DEFER, never ACCEPT.

What would change the answer:
- A third line-shift `tests / briefs` block at review in round 10.
- Or a `brief_lint.mjs --changed <files>` citation-only mode that checks only the `path:line`
  anchors whose file the diff touches, measured at a few seconds. That makes option (ii) cheap
  enough to run always.
- Its natural host is the group that owns `brief_lint.mjs`, as an addition to step 3f.
