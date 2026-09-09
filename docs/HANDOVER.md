# Handover — the open-issues programme

updated-for: a9d117c

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
of record. This file deliberately does **not** restate them — it once claimed a
"full accounting" it did not hold, which cost a session the conclusion that the
list was unrecoverable when it was one artifact call away. Lane collisions,
sequencing and the reasons E1–E3 and F wait are in
`docs/plan-2026-09-open-issues.md`, authoritative for delivery state; per-unit
stage, `after` edges and carried findings are in
`.claude/workflows/wave-ux-groups.json` (#601), the only one a linter reads.

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
- **A file reported missing was there.** A seat filed it as a programme defect
  after listing a checkout that sat on a stale branch. **Check existence with
  `git show origin/main:<path>`, never by listing a working tree.**
- **`section()` was genuinely unavailable** at the declared Home Assistant
  floor — absent from that release's `helpers/selector.py`, present at
  2025.2.0. The park was correct, and it is #514 that unblocks it.

- **The claim-file rule is conditional, and the flat form is wrong.**
  `CLAUDE.md` carries both halves and the mechanism behind them. The correction
  is that the flat "always byte-identical" form was briefed to every seat for a
  session before a reviewer refused it by measuring: PR #600 carries 33 correct
  bare claim lines because it moves 33 card states.

## Traps that cost a session

**A trap that has acquired a mechanical detector becomes a one-line pointer to
it.** Promotion, not cutting. The detector must fire when the trap would bite,
in that trap's mode — reporting where a reader is asked to look, refusing where
a wrong answer would pass unattended — and each graduation owes a mutation proof
in its own pull request.

1. **A killed agent never writes its own `state at stop:` comment.** On every
   resume the orchestrator walks the session's branches and open pull requests
   and posts the notes the dead agents owed.
2. **A stand-down note and a committed roster can disagree; origin is the
   tiebreak** — the pull request's own comments. One re-review was nearly spent
   re-deriving a verdict already posted.
3. **A gate cannot be its own witness.** When the subject is the selection
   machinery, the selection that runs is chosen by what is under test; #356
   shipped a regression its own CI could not see, because editing a gate file
   routed the change to the one path that could not reproduce the fault.
4. **A check whose failure is *visible* and one whose failure is *blocking*
   look identical in a passing run.** Two sessions each built the first
   believing they had the second; neither would have seen it in a green log.
5. **Six of this project's own instruments reported rather than measured** —
   #341, #347, #354, #350, #357 and #510 — each found by someone chasing
   something else. The pattern is the finding, not the individual bugs.
6. **A figure quoted from another artefact is not measured until you have run
   the thing that produced it.**
7. **A branch can be stale against main invisibly in its own diff**: a move
   reverting a fix that landed inside the moved lines, or a stale claim or
   budget table. Only a three-dot comparison against current main catches it.
8. **One CI runner is not the fleet** (#387). Graduated:
   `policy_lint_envmatrix.mjs`, five declared shapes and thirteen named rows.
9. **The machinery a handover depends on is code nobody ran** — `.claude/` is
   `INERT`. Graduated: `check-wave-script.mjs` and `policy_lint --hooks`.
10. **A closing keyword in a commit message links an issue just as a pull-request
    body does.** #503 acquired a false link to #457 that way and had to be
    corrected before it could merge.
11. **A shallow clone turns "commits ahead" into fiction**; four such figures
    once reached a handover. Graduated: `.claude/hooks/session-start.sh`.
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
    measured*. The countermeasure shared the class's own defect.
    The divider is **structural, not dispositional**: across every review-round
    body in the corpus at the time — 161 rounds over 97 reviewed pull requests,
    the population both percentages come from, and it grows, so re-derive rather
    than quote — the class reached no seat's *production* fix. A production fix
    is accepted by standing property-quantified instruments (CI, the ratchet,
    closures, the mutation proof); a record or policy artifact has none, so its
    acceptance test is whatever its author wrote that minute.
13. **"The pull request is open" is not a handoff.** The freeze starts at
    handoff, and a seat that has opened its pull request may still be pushing
    while it waits on CI. Six pull requests had a head moved under a live review
    in one session — more events than that, since #531 alone was moved four
    times.
14. **A record pull request cannot converge while the merge queue runs.** #531
    stayed open 20 hours over 45 commits, 25 content edits and 11 blocked
    rounds, with 31 pull requests merging underneath it — each of those a
    reading at one moment, not a tally, because every merge invalidated part of
    its content. One record per merge has a bounded truth condition and cannot
    be overtaken; live state belongs on #201, where no merge can stale it.
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
19. **A one-sided cap and a growing document collide across branches** — #608
    capped this file, #607 added 43 lines 56 minutes later, `main` went red from
    `5018e31`. Graduated: `policy-docs`'s `[budgets]`. Trap 17 on a budget.
20. **A comment bumps a pull request's `updated_at`, so it is not a body-edit
    clock.** Read as one, it had me date a body edit to what was in fact a
    reviewer's own comment timestamp. The clock is the `Governance` run list:
    the job fires on `[edited]`, so a missing run means no edit happened.
21. **Assert a mutation's occurrence count before applying it.** A control here
    reported a cap mutant NOT CAUGHT: the replacement hit the string's first
    occurrence, inside a comment, so the run was the unmutated one. "I could not
    find it" is a different result from "it is pinned". Same shape: a `case`
    glob is not anchored, so `v[0-9]*.[0-9]*.[0-9]*` accepts `v1.2.3; rm -rf /`;
    and `git remote remove` in a worktree strips it for every worktree.
22. **A subagent does not survive a session restart; its report does.** Read
    `tasks/<agentId>.output` before re-dispatching — `ListAgents` goes empty
    with no notification, and an hour was nearly spent re-running finished work.
23. **Re-pointing a branch chain by POSITION after a rebase drops a commit.**
    Map by commit subject and verify the tip's pin count: by index once shifted
    eight branches by one, and nothing but that count noticed.
24. **A citation repointed to a commit that resolves but lacks the file is
    worse than a dead one.** `git cat-file -e <sha>:<path>`, never per directory.
25. **A body's count of its own diff must come from the diff.** #621's body
    said five disposition rows; the diff added nine — the author counted what
    they remembered writing, in the branch whose subject was a document whose
    facts had gone stale for want of a second witness. Derive a body's counts
    by mutating the artefact and reading the detector: here, removing all nine
    rows and reading `--record`'s refusal.

## Owed — post-hoc reviews

**Seven pull requests merged on 2026-09-07 without an independent verdict at
their final head**, because the session's review capacity was exhausted by an
account rate limit before the round could run: **#591, #592, #596, #602, #603,
#605, #569**, and separately **#606**, merged with no review at all because
`main` was red and it was the repair.

Each squash body says so and names what a reviewer should start from.

Two of these matter more than the rest. **#603** is policy whose owner-approved
form changed twice after approval. **#596** introduces `tests/typing_budgets.json`
with a bootstrap census of 518; that file does not exist on `main` beforehand,
so nothing was loosened, but the number is the baseline four Wave 5 tranches
will be ratcheted against and no reviewer has checked it.

Also owed, and deliberately not landed because it is policy: a finding for
`tools/audit/briefs/fixer.md` — **a probe that builds its own input can build
the complement of production's input**. #591's seat drafted the text and
flagged it rather than claiming a carry it had not made.

## The machine this runs on — measure it, do not read it

This section used to describe the owner's Mac; a container seat reads it and
every line is false. Measure your own box (`nproc`, `command -v gh`, `python3
-V`). The repository facts: CI runs 3.13, #514 moves production to 3.14, CI is
the authority for the browser lane, and `git branch --show-current` beats
trusting a path.

**A 403 is not always the repository's answer.** Tag pushes and ref deletion
work from some environments and are proxy-refused in others, and the message
separates them: "Resource not accessible by integration" is a token scope,
"not permitted through this proxy" is the environment. Recording the second as
the first sends a reader to change what was never the obstacle.
