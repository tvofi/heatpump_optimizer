# Handover — the open-issues programme

updated-for: b6a21f1

This is the only handover. There is no dated series: a second
`docs/handover-*.md` is refused by `tests/entities.py`, and the policy it
enforces is in `CLAUDE.md` under "One living handover". The file that replaced
the series existed because every copy but the newest gave confident, wrong
instructions to the next session.

**What lives here** is durable: decisions and the measurement behind them,
corrections to the record, traps that cost a session, and owed work.

**What does not**: which seats are running, which branches are unpushed, what a
resumer does next. That is volatile, it goes on **#201** — whose newest comment
is the live state — and it survives an abort, which an unpushed in-tree edit
does not. Nothing belongs in both places.

Two things are deliberately *not* restated here, because restating them is how
they go wrong: delivery status, which is
`docs/plan-2026-09-open-issues.md`'s Delivery-status table and authoritative
there, and budget values, which are `tests/structure_budgets.json`. Name the
metric, never its number — twenty-one out-of-tree briefs once carried a
`coordinator_loc` that was stale by two hundred lines.

This file is updated **in the same pull request as the merge it records**,
riding the per-merge record obligation in `.cursor/rules/delivery-status-tracking.mdc`
so it costs no extra pull request, and `updated-for:` names that merge.

## Decisions taken — do not relitigate

- **Model routing is Claude seats.** Opus 5: orchestrator, architectural fixer
  and reviewer, survey, judge, production fixer. Sonnet 5: tests, tooling, docs,
  records, read-only reporting, stamp drafting. Fable 5.1 is routed nowhere,
  deliberately. The roster tokens `opus` / `sonnet` map literally.
- **The decomposition stage criterion (Wave 4, S3–S8).** A stage proceeds if it
  can reduce its own cut by inside-extraction **or** reduce `coordinator_loc`
  with nothing rising, and it records which. It halts when neither exists, and
  every halt records the cut's decomposition — owned versus read-by-others — so
  S12 inherits a measured brief rather than a fresh survey.
- **A seam move is sequenced to S12, not forbidden.** The judge's #193
  measurement is the reason: no component of size greater than one detaches at
  any k. Never write "forbidden" without that number behind it.
- **`_helper(self, ...)` is refused** — it erases moved references at zero cost,
  which is a measurement artefact rather than a decomposition. A
  supplied-literal check pins nothing; that was proven with a null control.
- **A ratchet raise may be proposed, never worked around** (owner, 2026-09-06).
  The order is: pay for the lines elsewhere, then a deliberate re-record with
  the reason in the commit message, then ask. An agent that wants a raise stops
  and asks before pushing.
- **Never re-gate an unchanged head.** A terminal CI result at that head *is*
  the gate evidence. Local runs exist for what CI structurally cannot produce:
  the mutation proof, the failing test at the merge base, and the finder's own
  harness at both ends.
- **#387 was fixed with the `env_drift` shape**, not by growing `alt_basins` and
  not by lowering the coverage floor. Solver work is captured twice in one run —
  tree and merge base — and computed is compared against computed, so there is
  no cross-machine assumption and no table to re-record. Two consequences were
  ruled on separately: the WORK channel's stale-cheap rule is a printed report
  rather than a failure, because that channel's baseline can no longer go stale
  and the failure would turn a genuine optimisation red; and the coverage floor
  is a literal, not an environment override, because an override could be
  reached in CI without ever appearing in a pull-request body.

### The UX programme

**Every item lives on #558**, with the *Optimizer UX Docket* artifact as source
of record. This file deliberately does **not** restate them — it previously
claimed to hold the "full accounting" and did not, which cost a session the
conclusion that the list was unrecoverable when it was one artifact call away.

Thirty-four items in five lanes. Three dropped and two reshaped so they stop
being breaking changes; both recorded on #558 with reasons.

**Lanes run concurrently with the waves — but independence is by FILE, not
only by budget.** The docket measured against the ratchet, which was true and
incomplete. Measured 2026-09-07:

| lane | collides with | on | sequence |
|---|---|---|---|
| B docs, C card | — | — | now |
| D ha | W5-G2 | `sensor.py` | now — Wave 5 unstarted, W5-G2 re-measures |
| E flow | **W4 S11 (#223)**, W5-G3 | `config_flow.py` | E1–E3 **after S11**; E4 (#516) now |
| F post-W4 | S12/S13, W5-G4, W5-G7 | `coordinator.py` | **last work of the programme**, after #412 |

**E1–E3 wait** because S11 rewrites `config_flow.py` as a settings registry:
landing them first means S11 restructures work that just landed; after, each
is one registry row instead of three separate edits.

**F is last** because it is the only lane adding lines to `coordinator.py`,
where `coordinator_loc` and `max_class_loc` sit at zero headroom.

**Three in-lane rules**, each costing a red main or a wasted PR: C4 runs last
(extended today it fails on four measured ratios); C1 is one PR, not four
(same state list); B5 needs B4 landed.

Issues exist for the items a lane is working now — #559–#563 (B1–B5), #564
(C1), #565–#566 (D2–D3) — and #516 (E4). The rest stay as #558 rows until
their lane reaches them, so the tracker holds work someone is doing rather
than a backlog nobody has started.

## Corrections to the record

- **The "34-key `data` payload" is wrong.** Measured: **157** top-level keys. No
  rule reproduces 34, and it traces to a lost session tool. The freeze is
  enforced by `tests/features.py`'s symmetry check and the `coord_*` goldens,
  not by a count. Corrected on #193.
- **#510 — a recorded cut drop that was blindness.** `tests/structure.py`
  matched `ast.Attribute` on `ast.Name("self")`, so `getattr(self, "_ctx", self).X`
  was invisible to it. Wave 4's S1 cut series is identical at both ends under a
  counter that resolves the idiom. #500's other results stand — `CoordinatorContext`
  itself, the attribute migration, the facades, #377 closed — and nothing is
  reverted. S2 is unaffected and S3's reduction is genuine.
- **#511 — v6.3.15 cannot produce a plan on any install.** The process-solve
  worker cannot unpickle a job under Home Assistant's module naming.
  **#513 is why the suite did not see it**: the suite runs a module name and a
  filesystem layout that no installation uses.
- **#457 / 3L-G6 was not spec-blocked.** Nothing shipped, and the owner closed
  it `COMPLETED` by hand on 2026-09-06. Recorded as discharged.
- **`.cursor/rules/ci-autofix.mdc` exists.** A seat filed it as a programme
  defect because the main checkout at `/Users/timmalmstrom/heatpump_optimizer`
  sits on a stale branch and a directory listing there reports current files as
  missing. **Check any file's existence with `git show origin/main:<path>`,
  never by listing that checkout.**
- **`section()` was genuinely unavailable** at the declared Home Assistant
  floor — absent from that release's `helpers/selector.py`, present at
  2025.2.0. The park was correct, and it is #514 that unblocks it.

## Traps that cost a session

1. **A killed agent never writes its own `state at stop:` comment.**
   Reconciliation is therefore the orchestrator's job on every resume: walk the
   session's branches and open pull requests and post the notes the dead agents
   owed.
2. **A stand-down note and a committed roster can disagree, and origin is the
   tiebreak** — the pull request's own comments, not the roster and not the
   note. One re-review was nearly spent re-deriving a verdict already posted.
3. **A gate cannot be its own witness.** When the thing under test is the
   test-selection machinery, the selection that runs is chosen by the machinery
   being tested; #356 shipped a regression its own CI could not see, because
   editing a gate file routed the change to the one path that could not
   reproduce the fault.
4. **A check whose failure is *visible* and a check whose failure is *blocking*
   look identical in a passing run.** Two sessions each built the first
   believing they had the second, and neither would have found it from a green
   log.
5. **Five of this project's own instruments reported rather than measured** —
   #341, #347, #354, #350, #357 — each found by someone chasing something else.
   The pattern is the finding, not the individual bugs. #510 above is the sixth.
6. **A figure quoted from another artefact is not measured until you have run
   the thing that produced it.**
7. **A branch can be stale against main in a way invisible in its own diff**:
   a move pull request reverting a fix that landed inside the moved lines, or a
   stale claim or budget table. Neither is catchable by reading the diff or
   re-running CI — only by comparing against current main, three-dot.
8. **One CI runner is not the fleet.** #387 exists because a property was
   measured on a single runner and generalised, and the reviewer had asked
   exactly the right question.
9. **The machinery a handover depends on is code nobody ran.** `.claude/` is on
   `tests/closure.py`'s `INERT` list by design, so orchestration scripts ship
   untested unless something pins them by hand. `node
   .claude/workflows/check-wave-script.mjs` pins the resume control flow;
   **re-run it after any edit to `web-fix-wave.js`**, because no CI job will.
10. **A closing keyword in a commit message links an issue just as a pull-request
    body does.** #503 acquired a false link to #457 that way and had to be
    corrected before it could merge.
11. **Check `git rev-parse --is-shallow-repository` before believing a
    divergence figure.** A shallow clone silently turns every "commits ahead"
    count into fiction; four such figures once reached a handover.

## Owed

- **The record pull request for #512** landed the four corrections this entry
  used to ask for: the roster and Delivery-status entry naming Wave 4 S1's
  138-point drop as instrument blindness (#510), not decoupling; the S3
  ruling text in `.claude/workflows/wave-4-groups.json` extended so the
  `getattr`/alias forms are *counted* rather than refused, for S6–S8 and S12;
  W4-G5's halt-premise recount; and #516 sequenced as a follow-up gated on
  #514. **One correction to this bullet itself**: the recount was guessed
  here as "23 of 115 is now 23 of 132" without running the thing that
  produces it (trap 6 below, caught by the same rule it names). Measured
  directly against `tests/structure.py`'s own `seam_metrics` at head
  `b6a21f1`: cut_fetch's addressable-from-inside share is **40 of 132**, not
  23 — the whole +17 from #512's fix is fetch's own newly-visible reads of
  attributes it does not own (17→34), not other seams reading more of
  fetch's, so the "92 other-seams-reaching-in" share holds at 92 in absolute
  count but drops from 80% to 70% of the (now larger) total. The halt's
  actual basis — the judge's #193 finding that no component of size>1
  detaches at any k — does not move either way; see the roster's W4-G5 note
  for the full recount.
- **A never-scoped CI job for `node .claude/workflows/check-wave-script.mjs`**,
  shaped like `tests.yml`'s `browser` and `briefs` jobs. It is the last file in
  that position still running by hand only.

## The machine this runs on

- The owner's Mac, with the `gh` CLI, 8 cores and 8.6 GB, shared with at most
  one other gate-running agent. Branch pushes, tag pushes and branch deletion
  all work here. The `refs/tags` and ref-deletion 403s an older container
  recorded were properties of that container and are **not** properties of this
  repository; do not plan around them.
- Python 3.11.5 is the default interpreter (3.13.1 is also present), CI runs
  3.13, and #514 moves the production target to 3.14.
- Playwright is not installed, so `tests/card_browser.mjs` runs in CI only —
  which is the authority for that lane anyway.
- Worktrees live under `/Users/timmalmstrom/wt/<branch>`. Never commit in the
  main checkout: it sits on a stale branch. `git merge origin/main`, never
  rebase.
