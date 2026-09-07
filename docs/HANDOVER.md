# Handover — the open-issues programme

updated-for: af47c96

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
- **Every sentence earns its place** (owner-directed). Governs the development
  record — pull-request bodies, issues, comments, commit messages, briefs,
  roster entries, reports and this file — never `README.md` or the rest of
  `docs/`. **Precision outranks concision**, and cutting evidence is never
  compliance with it.

### The UX programme

Thirty-four items in five lanes, selected by the owner from a forty-two item
survey. Three were **dropped**: a static icon override defeating `device_class`,
config entities creating a second source of truth, and a hand-kept table of
contents duplicating GitHub's outline. Two were **reshaped so they stop being
breaking changes**: `ScheduleSensor` adds a numeric entity and deprecates rather
than renames, and `DeviceInfo` gains `configuration_url` and a manufacturer with
no rename.

Three sequencing rules, each of which costs something if ignored: the contrast
witness runs **last** in the card lane — extended, it fails on four measured
ratios below 3:1; the drift-state lane is **one** pull request, not four,
because all four share a drift state list; and the docs lane's fifth item needs
its fourth landed first.

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

- **The ratchet has 24 metrics.** `structure_budgets.json` keys less
  `recorded_at`. `CLAUDE.md` said 22 for a long time and a pull-request body
  said 29 — that 29 is the count of `ok` lines, which includes the counting-rule
  check and four `const.py` symbol checks. **Derive it; never carry it.**
- **The claim-file rule is conditional, and the flat form is wrong.** A branch
  that claims **no** drift must not touch `claimed_drift.txt` /
  `card_claimed_drift.txt` — GitHub cannot run the `claimnotes` merge driver, a
  gratuitous note makes the pull request DIRTY, and CI then never queues
  (absent, not failing). A branch that **does** move goldens must write its
  claims, and those bare lines are then the correct state. The flat "always
  byte-identical" form was briefed to every seat for a session before a reviewer
  refused it by measuring: PR #600 carries 33 correct bare lines because it
  moves 33 card states.

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
    very class, catches **0 of 3**, because it matches digit-shaped figures and
    all three instances spell the quantity as a word. The countermeasure shared
    the class's own defect.
    The divider is **structural, not dispositional**: the class reaches no seat
    pull request across all 154 review-round bodies, because a seat's production
    fix is accepted by standing property-quantified instruments — CI, the
    ratchet, closures, the mutation proof — and a record or policy artifact has
    none, so its acceptance test is whatever its author wrote that minute.
13. **"The pull request is open" is not a handoff.** The freeze starts at
    handoff, and a seat that has opened its pull request may still be pushing
    while it waits on CI. Six head-moves under review in one session.
14. **A record pull request cannot converge while the merge queue runs.** #531
    took 20 hours, 45 commits — 19 of them merges of main — 25 content edits and
    11 blocked rounds, because 31 pull requests merged underneath it and each
    invalidated part of its content. The rule already says *the same session or
    an immediate record pull request*: one record per merge has a bounded truth
    condition and cannot be overtaken. Live state belongs on #201, where a
    comment cannot go stale under a merge.
15. **`date -jf '%Y-%m-%dT%H:%M:%SZ'` parses a UTC stamp as local time.** Every
    age computed that way is wrong by the offset; it once made a queue aged
    8 minutes to 20 hours read as a flat "2h", hiding which pull request was
    actually the outlier. Use Python's `datetime.fromisoformat` with an explicit
    UTC now.
16. **Backticks inside a double-quoted shell string are command substitution.**
    Three review comments were posted with their SHAs silently missing. Write
    the body to a file with a quoted heredoc and pass `-F body=@file`.

## Owed

- **The record pull request for #512**, carrying four corrections it is the
  first thing able to make: the roster and Delivery-status entry that still
  describes Wave 4 S1 as a 138-point cut drop, when #510 establishes it as an
  attribute migration with no measured cut change; the S3 ruling text in
  `.claude/workflows/wave-4-groups.json`, which names only `_helper(self, ...)`
  as refused when the `getattr` and alias forms are now *counted* rather than
  refused; W4-G5's halt premise, whose "23 of 115" is now 23 of 132 and
  therefore stronger; and #516 sequenced as a follow-up gated on #514.
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
