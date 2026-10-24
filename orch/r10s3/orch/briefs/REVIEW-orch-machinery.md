# Design review — the orchestration machinery (adversarial, independent)

You review a **design**, not a fix. Repository `tvofi/heatpump_optimizer`. LOCAL seat; no cloud.
Read `dev/governance/roles/fix-review.md` for the stance (a design that looks right and is wrong is the
failure mode) and `dev/governance/rules/defect-root-cause.md` for what a countermeasure owes.

## What you review

- Design ref: **`handoff/orch-machinery` at `2b159e4662f87e4cbfdb96c6b00bdffa9bc49ed1`**
  (`dev/audit/design/orch-machinery/DESIGN.md`, `EVIDENCE.md`).
- Fetch it and work from a detached worktree at that SHA:
  `git -C /Users/timmalmstrom/heatpump_optimizer fetch origin handoff/orch-machinery`
  then `git -C /Users/timmalmstrom/heatpump_optimizer worktree add --detach /Users/timmalmstrom/hpo-seats/r10s3/rev-orch-machinery 2b159e4662f87e4cbfdb96c6b00bdffa9bc49ed1`
- Your scratch: `/Users/timmalmstrom/hpo-seats/r10s3/rev-orch-machinery-ev` (create it).
- `export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH`.

## What the design claims, and what you must do to each

Its author states three load-bearing changes:

1. **One obligations ledger** keyed `(kind, subject, sha)`, disposal written by the producer, replacing
   the relay's log scan + `cloud-disposed` + `bus.sh orphans`' separate print. Claim: today's board is
   30,006 OWED lines over ~229 subjects because `relay_owed` keys the fold on the wrong field and never
   reads `cloud-disposed`.
2. **One supervised beat**, per-job timeouts, single-instance locks, a journal written by the runner as
   the liveness contract; the relay's handoff arm becomes its own job. Claims measured: six launches of
   one logical tick loop; `alive` has no writer process; `cloud_relay.sh pass` returns rc 0 with both
   remote reads failing while the loop prints `relay=ok`; two preprs ran 15+ min with no progress line
   then logged `Terminated: 15`; a heavy slot is stolen from a live holder at lease expiry.
3. **A reconciler over every record that is a claim**: roster `resume.stage`, `owner_gate`, `resume.commit`
   shape; an explicit `absorbed` disposition; `STAGE-MISMATCH` / `GATE-READY` / `RECORD-INVALID`.

For each: **re-run the evidence's commands yourself** and record PASS or what you got instead. A command
you cannot re-run (it would write a live ref, restart an instrument, or needs state that has moved) is
**UNVERIFIED** — say so and say why; do not mark it PASS.

## Attack it

- **Completeness of the inventory.** It claims 46 rows on a stated composition rule. Name any mechanism it
  missed — the test is the tree and the live processes, not the ask's list. Check specifically: the
  record beat (`record_row.py`) and its autofix job, `wt_sync.sh`'s snapshot loop, `daemonize.py`'s
  lifetime, the state mirror (`~/hpo-orch/state`), `handoff_push.sh`/`delivery_row.sh`, the tick's OWED/
  MERGE-READY arms, `proof_watch.py`, `codeql-triage-poll.sh`.
- **The design's own failure modes.** For every proposed mechanism: what does it do when its input is
  unreadable; can it print a pass it did not earn; can a disposal silently widen (the real risk in
  change 1 and in the reconciler's `absorbed` — a slip recorded as `absorbed` is a slip lost); does it
  add a **second** mechanism where one exists (the repo refuses parallel mechanisms); what is its
  standing cost per pass, in seconds and lines of policy.
- **Policy.** Any element that changes how a seat must work is policy and needs the owner's approval
  before merge. List every such element separately (`CLAUDE.md`'s policy set), with what it changes.
- **Seams with work already in the plan.** It must not redesign the CI restructure (R10-CI-LAYOUT) or
  `roster_edit`'s ops (R10-ROSTER-OPS). Check the named seams are real and that the design does not
  duplicate either. `roster_edit.py` has no `set-after` op — verify that claim in the tree.
- **The plan-page half.** The design lands `plan_page.py` sharing a model builder with `plan_table.py`,
  with five named defects as self-test arms. Verify each of the five is a real, reproducible defect of
  the current scratch `gen.py` (`~/hpo-orch/r10s3/plan/gen.py`, read-only), and that the proposed
  failing-then-passing arms would actually fail on the pre-fix behaviour.
- **Migration.** Is the order sound and does each step leave the programme runnable? What breaks on the
  first crash in the middle of it?

## Deliverable

1. `REVIEW.md`: a first line `DESIGN REVIEW: APPROVE`, `DESIGN REVIEW: CHANGES-REQUIRED` or
   `DESIGN REVIEW: REJECT`; then numbered findings, each with severity (blocking / non-blocking), the
   design section it names, your command, and what you got. Then a per-change PASS/FAIL/UNVERIFIED table.
2. `EVIDENCE.md`: the commands and their output.
3. Push both: commit under `dev/audit/design/orch-machinery/review/` in your detached worktree on a new
   branch and `git push origin HEAD:review/orch-machinery-design`. Refs only; no pull request, no GitHub
   write.
4. Report back: the verdict line, the review ref SHA, your PASS/FAIL/UNVERIFIED counts, and every finding
   you would block on.

Do not soften a finding because the design is otherwise good; and do not invent one to look rigorous. A
design review whose verdict does not move when a load-bearing claim is wrong is void — state in the
verdict which claim you perturbed and what it did.
