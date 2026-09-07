# Handover — the open-issues programme

updated-for: 6438406

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

- **Fix, then verify, then file** (owner, 2026-09-07). Each step is a fallback
  for the one before, not an alternative. An issue propagates further than a
  wrong pull request because nothing gates it: a pull request meets a reviewer,
  an issue meets a seat that treats it as a brief. A **recurring** error is an
  RCA, not a third issue — the trigger is roughly the third instance.
- **The orchestrator is bound by every contract it enforces.**
  `tools/audit/briefs/orchestrator.md` exists because it did not: every auditor
  of the resumability review had to be *told* what to fetch.
- **Every sentence earns its place** (owner-directed, 2026-09-07). The rule,
  its scope and its controls are in `CLAUDE.md`; recorded here so that the
  decision to adopt it is not relitigated.

### The UX programme

**Every item lives on #558**, with the *Optimizer UX Docket* artifact as source
of record. This file deliberately does **not** restate them — it previously
claimed to hold the "full accounting" and did not, which cost a session the
conclusion that the list was unrecoverable when it was one artifact call away.

The lane collision table, the three in-lane sequencing rules and the reasons
E1–E3 and F wait live in `docs/plan-2026-09-open-issues.md`, which is
authoritative for delivery state; per-unit stage, `after` edges and carried
findings are in `.claude/workflows/wave-ux-groups.json` (#601), the in-tree
destination the lanes had none of and the only one a linter reads.

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

- **The claim-file rule is conditional, and the flat form is wrong.**
  `CLAUDE.md` carries both halves and the mechanism behind them. The correction
  is that the flat "always byte-identical" form was briefed to every seat for a
  session before a reviewer refused it by measuring: PR #600 carries 33 correct
  bare claim lines because it moves 33 card states.

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
12. **A fix gets verified against the instance that was demonstrated, not the
    property that was stated.** The demonstration displaces the specification,
    the verification is built from the demonstrated instance's *form*, and any
    sibling carrying the property in a different form survives — including one
    the same commit creates. Established by root-cause analysis over #531, #569
    and #591: **3.1% of reviewed pull requests, 11.2% of all review rounds.**
    A check cannot close it — `tools/audit/preflight.sh`, written against this
    very class, catches **0 of 3**. The reason is not the shape of those figures —
    rewriting all three with digits leaves them just as clean. A grep can only
    ask *is there a figure here*, while the defect is *was the right thing
    measured*. The countermeasure shared
    the class's own defect.
    The divider is **structural, not dispositional**: the class reaches no seat
    pull request across every review-round body in the corpus at
    the time (161 rounds over 97 reviewed pull requests — the population the two
    percentages above come from, and it grows, so re-derive rather than quote), because a seat's production
    fix is accepted by standing property-quantified instruments — CI, the
    ratchet, closures, the mutation proof — and a record or policy artifact has
    none, so its acceptance test is whatever its author wrote that minute.
13. **"The pull request is open" is not a handoff.** The freeze starts at
    handoff, and a seat that has opened its pull request may still be pushing
    while it waits on CI. Six pull requests had a head moved under a live review
    in one session — more events than that, since #531 alone was moved four
    times.
14. **A record pull request cannot converge while the merge queue runs.** #531
    was still open after 20 hours, 45 commits — 19 of them merges of main —
    25 content edits and 11 blocked rounds, with 31 pull requests merged
    underneath it. Every one of those is a reading at that moment rather than
    a final tally: it kept moving, which is the point and each
    invalidated part of its content. The rule already says *the same session or
    an immediate record pull request*: one record per merge has a bounded truth
    condition and cannot be overtaken. Live state belongs on #201, where a
    comment cannot go stale under a merge.
15. **`date -jf '%Y-%m-%dT%H:%M:%SZ'` parses a UTC stamp as local time.** Every
    age computed that way is wrong by the offset; it once made a queue aged
    8 minutes to 20 hours read as a flat "2h", hiding which pull request was
    actually the outlier. Use Python's `datetime.fromisoformat` with an explicit
    UTC now.
17. **A citation and its referent can live on two branches, and the relation
    between them is invisible to every branch-scoped check.** Two green branches
    merged to a red `main` with no conflict and no shared file: one landed a
    brief citing `configuration_url`, the other deleted the tracked tree's only
    occurrence of that string, and git reported nothing because they touch
    different files. Not the move-PR silent-revert shape — nothing was
    overwritten and both changes survived intact; the failure is purely
    relational. `CLAUDE.md` rule 1's asymmetry is what caught it: a push to
    `main` forces `GATE_SCOPE=full`, and that argument, written about closures,
    paid out for something nobody had in mind. **The preventable half is that
    the citation was anchored to one English sentence. Prose is not a pin** —
    restoring the sentence would have greened the gate and reproduced the
    defect, so the repair was to re-anchor.
18. **A clean merge is evidence of no textual overlap and nothing else.** Twice
    in one session two sides appended at the same insertion point and shared a
    trailing bracket, so `--ours` or `--theirs` would have dropped a whole block
    with no marker and no failing test. Verify a merge by parsing the result and
    naming the checks that run, never by reading the hunk.
16. **Backticks inside a double-quoted shell string are command substitution.**
    Three review comments were posted with their SHAs silently missing. Write
    the body to a file with a quoted heredoc and pass `-F body=@file`.
19. **A one-sided size cap and a growing document collide across branches, and
    nothing branch-scoped holds both ends.** #608 recorded `docs/HANDOVER.md`'s
    cap in `.claude/workflows/policy_budgets.json` at the length that file then
    had; #607, cut from the same commit and already in review, added 43 lines to
    it and merged 56 minutes later. Both prefixes are INERT, so the `Governance`
    workflow is the only thing that measures this, and it was green on each
    branch alone. `main` was red on `policy-docs` from `5018e31` until this
    record paid the lines back. Trap 17's shape on a budget rather than a
    citation.

## Owed

- **A never-scoped CI job for `node .claude/workflows/check-wave-script.mjs`**,
  shaped like `tests.yml`'s `browser` and `briefs` jobs. It is the last file in
  that position still running by hand only.

## Owed — post-hoc reviews

**Seven pull requests merged on 2026-09-07 without an independent verdict at
their final head**, because the session's review capacity was exhausted by an
account rate limit before the round could run: **#591, #592, #596, #602, #603,
#605, #569**, and separately **#606**, merged with no review at all because
`main` was red and it was the repair.

Each squash body says so and names what a reviewer should start from. Every
change since the last verdict answers a named block and was verified by
measurement rather than assertion, but that is the author verifying his own
work, which is the arrangement the fix-review contract exists to prevent.

Two of these matter more than the rest. **#603** is policy whose owner-approved
form changed twice after approval. **#596** introduces `tests/typing_budgets.json`
with a bootstrap census of 518; that file does not exist on `main` beforehand,
so nothing was loosened, but the number is the baseline four Wave 5 tranches
will be ratcheted against and no reviewer has checked it.

Also owed, and deliberately not landed because it is policy: a finding for
`tools/audit/briefs/fixer.md` — **a probe that builds its own input can build
the complement of production's input**. #591's seat drafted the text and
flagged it rather than claiming a carry it had not made.

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
