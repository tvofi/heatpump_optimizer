# Handover — the open-issues programme

updated-for: 598ad6df36214a6d847683f19d08b424db55afd7

The rule that governs this file is `.claude/rules/writing-for-agents.md`, which
the harness loads on this very path. Delivery status is the frozen table in
`docs/plan-2026-09-open-issues.md` plus one `docs/delivery/<N>.md` per pull
request (#1081), linked from here and never restated.

## Decisions taken — do not relitigate

- **Model routing is Claude seats.** Opus 5: orchestrator, architectural fixer
  and reviewer, survey, judge, production fixer. Sonnet 5: tests, tooling, docs,
  records, read-only reporting, stamp drafting. **Fable 5.1 is only for a very
  large multi-layer refactoring where Opus 5 is judged too risky** (owner,
  2026-09-09). Roster tokens `opus` and `sonnet` map literally.
  **A Fable trailer on a merge or a stamp is the session's model, not a routing
  event.** Scrape trailers and the roster `fixerModel` / `reviewerModel` keys
  separately; do not restate a count.
- **The decomposition stage criterion (Wave 4, S3–S8):** proceed only by cutting
  the stage's own cut by inside-extraction or `coordinator_loc` with nothing
  rising; halt otherwise, recording the cut's owned-versus-read-by-others split.
- **A seam move was sequenced to S12, S12 halted (#637); W5-G9 and W5-G10 own it**
  (owner, 2026-09-10). The learner went first because a `seam_metrics` simulation
  lowered every budget row; the guard needed #753 first, since a cohesive
  extraction removes more intra- than cross-seam edges and a ratio cannot see it.
- **`_helper(self, ...)` is refused** — it erases moved references at zero cost, a
  measurement artefact, not a decomposition; a supplied-literal check pins nothing.
- **A ratchet raise may be proposed, never worked around** (owner, 2026-09-06).
  The order — pay, re-record with the reason, then ask — is `CLAUDE.md` rule 2's.
- **Never re-gate an unchanged head.** A terminal CI result at that head *is*
  the gate evidence. Local runs exist for what CI structurally cannot produce:
  the mutation proof, the failing test at the merge base, and the finder's own
  harness at both ends.
- **#387 was fixed with the `env_drift` shape**, not by growing `alt_basins`
  and not by lowering the coverage floor. Tree and merge base are captured in
  one run and compared computed-to-computed. The WORK channel's stale-cheap
  rule is a printed report, not a failure; the coverage floor is a literal,
  not an environment override.
- **Every sentence earns its place** (owner-directed, 2026-09-07). The rule, its
  scope and its controls are in `.claude/rules/writing-for-agents.md`; recorded
  here so that the decision to adopt it is not relitigated.
- **A body long from disclosed self-corrections is re-cut by relocating them
  here** (PR #1058 `## Friction`, seen by the owner). `fixer.md`'s fourth-round
  re-cut and `writing-for-agents.md`'s *cutting evidence is never compliance*
  pointed opposite ways and neither said which wins. The tie-break: `CLAUDE.md`
  gives this file *corrections to the record*, and a disclosed self-correction
  is one — move them into that section and re-cut the body with nothing cut.
- **A policy merge needs the owner's approval, per pull request** (owner,
  2026-09-09, ADR 0007), given since 0009 step 6 as the owner's approving
  GitHub review on a pull request touching a `.github/CODEOWNERS` path; an
  approval given in session no longer stands in for it. A **session grant** of
  the 0001/0006 shape is the option, not the default: it names the session, restates the six
  preconditions, and lapses when that session ends. Do not infer a standing
  grant from the fact that one existed. The ruleset and `pr-contract` are the
  floor either way, never the substitute — they check that a change is
  well-formed, not that it is wanted.
- **`main` is guarded, and this is the first thing about the merge boundary
  that is enforced rather than asserted.** Ruleset **`main-protect`, id
  `22628467`**, active on the default branch: deletion, non-fast-forward
  and the required checks its endpoint returns, never a count from here.
  GitHub refuses the merge rather than a
  policy asking you not to. Since 0009 step 6 (2026-09-17 04:58Z) it also
  carries a `pull_request` rule: one approving review, and the code owner's
  review on a path `.github/CODEOWNERS` names. **The one bypass is the deploy
  key `hpo-stamp`, `always`**; the admin role no longer bypasses, so the rule
  binds the orchestrator's merges as `tvofi` too. **The merge flow**: seats
  author as `tvofi-seat-author`; an ordinary pull request merges after an
  adversarial `merge` verdict and the App `hpo-approver`'s approving review
  (first: #1100); a policy one needs the owner's approving review on GitHub
  (first: #1098), which a seat cannot obtain for itself — open it, surface it,
  and wait. That bypass and the rollback below are the owner's levers, not a
  seat's. One DELETE to that ruleset reverses it all.
  **Before adding a required context**, confirm it reports on a *pull-request
  head*, not merely on a push to `main`: the two shapes differ, `CodeQL`
  reports on one and not the other, and a context that never reports blocks
  every merge permanently — **in either direction**, as retiring `fast`'s 3.13
  leg proved: a matrix change is a required-set change. A `skipped` or `neutral` required check satisfies
  the rule; that was measured on an isolated probe, both arms. A **scheduled**
  context is the other half of the same trap: make a nightly required and one
  failing night blocks every merge, the merge that repairs the nightly included.
- **A stamp pushes to `main` only over the deploy key**, and only from the
  local box: `tools/release/stamp.py --push --push-key ~/.zcode/stamp-deploy.key
  --known-hosts ~/.zcode/github_known_hosts`. The admin token that used to push
  was revoked and returns 401 (#201 comment 5704702814). Step 5's probe, on a
  throwaway branch under a throwaway ruleset with an `update` rule and the same
  bypass list (comment 5704665628), refused an API ref update as `tvofi` and as
  `tvofi-seat-author`, and landed a push over the deploy key.
- **A pull-request body carries `## Figures`** (#676). Its companion rule left
  this file for `writing-for-agents.md` at #724; the measurement it was written
  from stays, since that file lacks it: twenty-one out-of-tree briefs held a
  `coordinator_loc` stale by two hundred lines. The detector shape that works
  resolves a *file name* to an artefact; the looser one — any number near a file
  name — was built and **refused in review** for reading a date and a line count
  as caps, and `preflight.sh`'s figure advisory stays advisory for #581's reason.
- **The pull-request body is one live object.** Every head's contract job reads
  the current body, so only that head's result is a result. A red at a
  superseded head is the instrument, not the commit. The root-cause seat is
  the issue this property opened; do not skip to writing a check.
- **A coverage ratio over an open set of mutation carriers is not a figure.**
  The denominator is unbounded. State the class.
- **A figure about the document it lives in is derived beside it, at the head.**
  Carrying one is how it goes stale on every review of the artifact that states it.

### The UX programme

**Every item lives on #558**, with the *Optimizer UX Docket* artifact as source
of record. This file deliberately does **not** restate them — it once claimed a
"full accounting" it did not hold, which cost a session the conclusion that the
list was unrecoverable when it was one artifact call away. Per-unit stage,
`after` edges and carried findings are in `.claude/workflows/wave-ux-groups.json` (#601).

- **Two instruments, two questions.** `tests/coverage_ratchet.py` floors package
  coverage under a 96 % ceiling and caps `# pragma: no cover` downward — the
  pragma is the one cheap way past a floor. `tests/mutation_table.py` asks
  whether a check would FAIL, scoped to the files a diff tested, full-package
  nightly; its cap is a FRACTION because the pool is a seeded sample, so an
  exact count would redden clean branches at random. #195's bar: 96 %.

## Corrections to the record

- **The seven open `[policy] recurring friction:` issues were filed by a
  histogram that keyed on the spelling a seat typed, and counted entries rather
  than pull requests.** Both are fixed; the issues are not re-titled. So
  #1095 (`gate-scoping`) and #1093 (`gate-scoping.md`) are one rule, and
  #1094 (`orchestrator`) reached its count from 2 pull requests with 3 of its 4
  entries in one body -- under recurrence it would not have been filed. The key
  is now the policy FILE an id names, so new issues are titled
  `[policy] recurring friction: .claude/rules/<rule>.md`; a seat disposing one
  of the seven re-derives with
  `node .claude/workflows/policy_lint.mjs --stats --since <newest tag>` and reads
  the `PRs / entries` column, not the old count in the issue body. The filing
  lane re-measures every open one on each beat and comments when its key is
  below threshold in the current window; it never closes, so the disposition is
  still a seat's. Two keys that had never surfaced at all, because their
  spellings split, are `.claude/rules/defect-root-cause.md` and (below
  threshold on distinct PRs, not entries) `.claude/skills/steward/SKILL.md`.
- **The "34-key `data` payload" is wrong**, and so is any count of it: no rule
  reproduces 34, and it traces to a lost session tool. The freeze is enforced by
  `tests/features.py`'s symmetry check and the `coord_*` goldens, never by a
  number. Corrected on #193.
- **#510 — a recorded cut drop that was blindness**, not decoupling.
  `tests/structure.py` matched `ast.Attribute` on `ast.Name("self")`, so
  `getattr(self, "_ctx", self).X` was invisible to it; under a counter that
  resolves the idiom Wave 4's S1 cut series is identical at both ends. Fixed by
  #512, nothing is reverted, and what still stands is the Wave 4 row's to say.
- **#511 and #513 are closed and the shape outlived them**: the suite ran a
  module name and a filesystem layout no installation uses. Graduated:
  `tests/deployment_shape.py`, in `tests/closures.json`.
- **A file reported missing was there.** A seat filed it as a programme defect
  after listing a checkout that sat on a stale branch. **Check existence with
  `git show origin/main:<path>`, never by listing a working tree.**
- **Leave both claim files exactly as you found them** (#662). Two earlier forms
  were each briefed to every seat for a session before a reviewer refused them by
  measuring. "Always byte-identical": PR #600 carries 33 correct bare claim lines
  because it moves 33 card states. Then one demanding an *empty* claim list on a
  branch that claims nothing — the same thing only when the baseline claims
  nothing too. It is not: a squash then applies that deletion to `main` and
  carries another lane's claims off with it. Measured four times — #608 took
  33 of #569's lines, #635 the same to #633's, #658 was stopped on the way to
  #653's, #746 took #735's six. Since #747 the guard, the bot and the stale-claim
  judgement ask per file kind: never write a list for a kind you cannot move.
- **The pull-request checks listing is not a faithful instrument** (#669). It
  shows the latest run per check, so an earlier red behind a later green is
  invisible —
  and the mirror error is just as easy, reading "any failure" as "red" when a
  later run passed. Read `/repos/<owner>/<repo>/commits/<sha>/check-runs`,
  which returns every run. `web-fragments.md` carries the invocation; every
  file that instructs a seat, that table included, is refused for naming the
  lossy form — which is why this bullet describes it instead.
- **The subject enumerator misses merges AND invents them, and the two errors
  hide each other.** It reads a trailing `(#N)`; over `a9d117c..8f754c9` it
  counted 24 where `/commits/<sha>/pulls` answers 25, and **that gap of one is a
  net, not a miss**: #640 carries no suffix and #655 ends `(#587)`, so both are
  invisible, while #587 is a phantom the check then demands a disposition for.
  `24 = 25 - 2 + 1`, and the first reading blamed #640 alone because the
  arithmetic looked confirmed. **Compare the sets, never the totals**, and treat
  a suffix as a claim about a number rather than a fact. The API enumerator is
  the default now and this regex is its fallback — a marked one since #1050, so
  what survives here is the method, not a live defect.
- **The red-check refusal fires; it never had until #1040 (`f605da4`).** The
  entry that stood here — that the list `checkPrBody` iterates was empty on
  every pull request this repository had run — was true when written and is
  not. **Date it by the SHA, not by a day**: run `34903020012` concluded
  `failure` at 2026-09-14T22:15:44Z, two hours BEFORE that merge, being
  #1040's own demonstration on a throwaway branch. `CLAUDE.md`'s "only the
  red-check trigger is enforced" is a measurement from `f605da4` on.
- **`GET /repos/.../rules/branches/<branch>` is not bypass-aware.** It lists
  the rules configured for the branch, not the rules that would apply to you:
  emptying the bypass-actors list and re-reading returns an identical list. Reading it
  as "the bypass does not apply to me" nearly produced a false alarm that the
  release stamp was about to break. The only honest test is a probe branch with
  its own ruleset and **both** arms — with the admin bypass the push lands,
  without it GitHub answers *push declined due to repository rule violations*.

## Traps that cost a session

**A trap that has acquired a mechanical detector becomes a one-line pointer to
it.** Promotion, not cutting. The detector must fire when the trap would bite,
in that trap's mode — reporting where a reader is asked to look, refusing where
a wrong answer would pass unattended — and each graduation owes a mutation proof
in its own pull request.

1. **A killed agent never writes its own `state at stop:` comment.** On resume
   the orchestrator walks the session's branches and open pull requests and
   posts the notes the dead agents owed.
2. **A stand-down note and a committed roster can disagree; origin is the
   tiebreak** — the pull request's own comments. One re-review nearly
   re-derived a verdict already posted.
3. **A gate cannot be its own witness.** When the subject is the selection
   machinery, the selection that runs is chosen by what is under test; #356
   shipped a regression its own CI could not see, because editing a gate file
   routed it to the one path that could not reproduce the fault.
4. **A check whose failure is *visible* and one whose failure is *blocking*
   look identical in a passing run.** Two sessions each built the first
   believing they had the second.
5. **Six of this project's own instruments reported rather than measured** —
   #341, #347, #354, #350, #357, #510 — each found by someone chasing something
   else. The pattern is the finding, not the individual bugs.
6. **A figure from another artefact is not measured until you run the thing
   that produced it.**
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
11. **A shallow checkout fails a driver on the clone, not the tree.** Graduated:
    `entities.py` refuses a history-reading driver at depth 1 (#901).

12. **A shallow clone turns "commits ahead" into fiction**; four such figures
    once reached a handover. Graduated: `.claude/hooks/session-start.sh`.
13. **A fix gets verified against the instance that was demonstrated, not the
    property that was stated.** The demonstration displaces the specification,
    the verification is built from the demonstrated instance's *form*, and any
    sibling carrying the property in a different form survives — including one
    the same commit creates. Established by root-cause analysis over #531, #569
    and #591: **3.1% of reviewed pull requests, 11.2% of all review rounds.**
    A check cannot close it — `tools/audit/preflight.sh`, written against this
    very class, catches **0 of 3**: a grep asks *is there a figure here* while
    the defect is *was the right thing measured*. The divider is **structural,
    not dispositional**: across every review-round body in the corpus at the
    time — 161 rounds over 97 reviewed pull requests, and it grows, so
    re-derive — the class reached no seat's *production* fix. A production fix
    is accepted by standing property-quantified instruments (CI, the ratchet,
    closures, the mutation proof); a record or policy artifact has none.
14. **"The pull request is open" is not a handoff.** The freeze starts at
    handoff, and a seat that has opened one may still be pushing while it waits
    on CI. Six pull requests had a head moved under a live review in one
    session, #531 four times by itself.
15. **A record pull request cannot converge while the merge queue runs.** #531
    stayed open 20 hours over 45 commits, 25 content edits and 11 blocked
    rounds, with 31 pull requests merging underneath it, each merge
    invalidating part of its content. One record per merge has a bounded truth
    condition and cannot be overtaken; live state belongs on #201, where no
    merge can stale it.
16. **`date -jf '%Y-%m-%dT%H:%M:%SZ'` parses a UTC stamp as local time.** Every
    age computed that way is wrong by the offset; it once made a queue aged
    8 minutes to 20 hours read as a flat "2h". Use Python's
    `datetime.fromisoformat` with an explicit UTC now.
17. **Backticks inside a double-quoted shell string are command substitution.**
    Three review comments were posted with their SHAs silently missing. Write
    the body to a file with a quoted heredoc and hand it to `gh_comment.py
    --body-file`.
18. **A citation and its referent can live on two branches, and the relation
    between them is invisible to every branch-scoped check.** Two green branches
    merged to a red `main` with no conflict and no shared file: one landed a
    brief citing `configuration_url`, the other deleted the tracked tree's only
    occurrence of that string, and git reported nothing because they touch
    different files. Nothing was overwritten and both changes survived intact;
    the failure is purely relational. `CLAUDE.md` rule 1's asymmetry caught it:
    a push to
    `main` forces `GATE_SCOPE=full`, and that argument, written about closures,
    paid out for something nobody had in mind. **The preventable half is that
    the citation was anchored to one English sentence. Prose is not a pin** —
    restoring the sentence would have greened the gate and reproduced the
    defect, so the repair was to re-anchor.
19. **A clean merge is evidence of no textual overlap and nothing else.** Twice
    in one session two sides appended at the same insertion point and shared a
    trailing bracket, so `--ours` would have dropped a whole block silently.
    Verify a merge by parsing the result and naming the checks that run.
20. **A one-sided cap and a growing document collide across branches** — #608
    capped this file, #607 added 43 lines 56 minutes later and `main` went red.
    Graduated: `policy-docs`'s `[budgets]`. Trap 17 on a budget.
21. **A comment bumps a pull request's `updated_at`, so it is not a body-edit
    clock.** Read as one, it dated a body edit to a reviewer's comment. The
    clock is the `Governance` run list: the job fires on `[edited]`, so a
    missing run means no edit happened.
22. **Assert a mutation's occurrence count before applying it.** A control
    reported a cap mutant NOT CAUGHT: the replacement hit the string's first
    occurrence, inside a comment, so the run was unmutated. "I could not find
    it" differs from "it is pinned". Same shape: an unanchored `case` glob
    accepts `v1.2.3; rm -rf /`.
23. **A subagent does not survive a session restart; its report does.** Read
    `tasks/<agentId>.output` before re-dispatching — `ListAgents` goes empty
    with no notification, and an hour nearly went on finished work.
24. **Re-pointing a branch chain by POSITION after a rebase drops a commit.**
    Map by commit subject and verify the tip's pin count: by index once shifted
    eight branches by one, and only that count noticed.
25. **A citation repointed to a commit that resolves but lacks the file is
    worse than a dead one.** Graduated for the corpus and the rosters:
    `citations` refuses a tag-cited path the tag does not carry. Elsewhere,
    `git cat-file -e <sha>:<path>`, not per directory.
26. **A body's count of its own diff must come from the diff.** #621's body
    said five disposition rows; the diff added nine, because the author counted
    what they remembered writing. Derive a body's counts by mutating the
    artefact and reading the detector: here, removing all nine rows and reading
    `--record`'s refusal.
27. **A figure in prose whose referent is a function of `origin/main` is stale
    by construction, not by neglect.** It was the single largest source of
    blocked rounds under the 2026-09-09 grant, and `claims` outnumbered every
    other block class together. **No count is given here, and that is the trap
    demonstrating itself**: the first draft carried one, it went stale on every
    round of the review that landed it because its referent was that review's
    own history, and the replacement count of how many times it had gone stale
    went stale too. Derive it — scrape `Fix review: blocked <sha> <class>:`
    across the grant's pull requests and count the classes.
    Partly graduated: `COUNT_RULES` in `.claude/workflows/counts.mjs` refuses
    prose disagreeing with a figure derived from the artefact that answers it,
    and `brief_lint.mjs` runs that set less `modules` over roster briefs (#672).
    Quote neither count — #676 added a rule while this said eight, the trap
    firing on itself. **The other half does not graduate**, per #581 — a rule
    refusing a *bare figure* was built and driven, and reported 20 on the live
    briefs of which five were the defect: three wrong reports per right one, on
    a corpus whose authors mostly did anchor. Write `58.6 % at 4b6e0765`.
28. **A blank line ends a markdown table, and every row below it renders as
    literal text while the source still looks like a table.** Not reduced to a
    pointer, although its detector exists: the check catches the defect, and
    what survives here is the method for settling a render question at all. 26 of the plan's
    36 disposition rows were not in a table, for an unknown number of sessions,
    in the most-read document here. Graduated: `policy_lint --record`'s
    `table` check over both disposition documents. Ground truth for a render
    question is GitHub's own `/markdown` endpoint, not the CommonMark spec —
    how #686 established that a row's *leading* pipe is optional in GFM, so
    deleting one is correctly not reported. The blank line is the defect.
29. **A replacement that matches a prefix leaves both halves in one line, and
    an anchor that matches the first occurrence lands your insertion in the
    wrong section.** Both happened in one pull request. The row became five
    cells wide in a three-column table with its old half still contradicting
    the new one, and a governance-queue entry was appended under an earlier
    heading of nearly the same name. Neither is visible to a check: `--record`
    matches a number anywhere in its region and has no idea about placement.
    Assert the *whole* construct you meant to replace, and anchor on a string
    you have counted.
30. **A verdict that does not parse loses its routing class, not just its text.**
    `web-fix-wave.js`'s `VERDICT_RE` anchors on `^Fix review:`, reads only the
    first line, and takes `<class>` from the closed `VERDICT_CLASSES` list — so
    backticks around that line and an invented class both make the dispatcher
    report no verdict on a pull request that has one, and the result is recorded
    as an undifferentiated non-merge. The class is what dispatches a repair
    round rather than a root-cause seat, so losing it costs the routing. Both
    halves have fired: four of the fifteen grant merges were wrapped, and
    `revise` — which is not a class — was written into every review brief and
    cost six verdicts before it was caught. Post the first line bare, and read
    the class list out of the file rather than from memory.
31. **In zsh, assigning to a variable named `path` destroys `PATH`.** A
    `while read -r path branch` loop over `git worktree list` left the shell
    unable to find `basename`, `git` or `df`. Same reserved-variable family as
    `GID`. Rename the loop variable.
32. **A record's own fields are checked by almost nothing** (#687). An
    unrecognised `resume.stage` is refused by `check-wave-script.mjs`, but a dead
    path in `resume.note` is invisible to `brief_lint.mjs` while the same path in
    `brief` is an error. A roster `resume` a record seat truths has one guarded
    field and a reader for the rest.
33. **A worktree shares the repository's config and its refs with every other
    worktree.** A seat ran `git remote remove origin` inside one while building
    a fixture; the main checkout's `origin` was repointed at a local path and
    every remote-tracking ref went with it. A throwaway git experiment goes in a
    standalone clone under the seat's own `mktemp -d`, never in a worktree here.
34. **A detached worktree can be collected while a seat is still using it.**
    `tools/audit/worktree_gc.sh --apply` removes a detached, clean worktree over
    an hour old that is not an open pull request's head. A fix-review seat is
    protected by that last criterion; a root-cause or audit seat detached at
    `main` is not. **Claim it with `git worktree lock`**: `classify()` keeps
    `locked` ahead of every criterion, as it does `main`, `current` and
    `missing` — none named in its header, none pinned by a `--self-test` case.
    **Not an untracked marker at the root**: criterion 2 keeps it, and
    `closure.py select` then turns `MODE: SCOPED` into `MODE: FULL` naming it.
35. **A coverage check can run a guard's line and pin nothing.** Four shapes
    found by mutation across W5-G7, none visible to an instrument that sees the
    line run either way. An EARLIER guard rejected the input (eight checks). The
    exception ESCAPES and ends the script instead of failing the check named for
    it (eleven; worst on an event-bus `@callback` whose helper swallows it). The
    f-string DETAIL is eager, so a `sorted` over a mixed set aborts in place of
    the failure. And the value the mutation leaves UNTOUCHED equals the asserted
    one, so a push or a coercion is invisible when the constructed value already
    agrees. **Only-arm inputs, a catcher on every call, details by `repr`, state
    edited before the call.** And never assert EQUALITY against a production
    structure: a second declaration cannot learn the original moved (#851).
    Fifth shape: a mutant that cannot PARSE reports a pass, which here reads as
    a finding about production. Assert it parses.
36. **The leftover sweep reads part of a row; a stale row hides its state in
    the rest.** #690's rule — the row's own verdict, quoted prose excluded —
    applied literally reads the first `**…**` span. #678's row opened on its
    root-cause verdict, carried `**IN REVIEW as #715**` later in that cell, and
    ended `governance, in review` unbolded; it stood five days of record beats
    after #715 merged. **The rule that holds both ends: in a table
    row every cell, in a bullet the leading verdict, both dropping quoted and
    backticked text first** — 12 table rows here before the repair, 0 after.
    Without it the bullet arm fires on already-repaired prose, and #582's row
    on its own leftover; **count those with your own vocabulary.**
37. **A read-back that checks an id and a URL passes a body the API rewrote.**
    PR #1058's provenance comment published a script whose field separator was
    a JSON unicode escape for the unit separator; the API converted the escape
    to the control character, so the published script was not the script that
    ran — `identical=False`, 6505 bytes against 6508. The correcting paragraph
    failed the same way, because describing the escape writes it; words, on the
    third attempt, passed. Byte-identity against the sent file
    (`comment-readback.md`) is the only read-back that fails all three.

## Owed — post-hoc reviews

**Seven pull requests merged on 2026-09-07 without an independent verdict at
their final head**, because the session's review capacity was exhausted by an
account rate limit before the round could run: **#591, #592, #596, #602, #603,
#605, #569**, and separately **#606**, merged with no review at all because
`main` was red and it was the repair. Each squash body says so and names what a
reviewer should start from.

Two of these matter more than the rest. **#603** is policy whose owner-approved
form changed twice after approval. **#596** introduces `tests/typing_budgets.json`
and its bootstrap census; the file does not exist on `main` beforehand, so
nothing was loosened, but it is the baseline every Wave 5 tranche ratchets
against and no reviewer has checked it. Read the census from the file.

Also owed, and deliberately not landed because it is policy: a finding for
`tools/audit/briefs/fixer.md` — **a probe that builds its own input can build
the complement of production's input**. #591's seat drafted the text and
flagged it rather than claiming a carry it had not made.

**Owed from 2026-09-09, and none of it decidable by a seat.**

- **Two one-clause policy edits carried out of #580's closure**, which the
  judge merged into #588 leaving them named only in a comment on a closed
  issue. First: `fix-review.md` has **no step for an ABSENT check** — step 11
  obliges an answer for a check that went *red*, and a pull request whose
  workflows never queued shows a reviewer no red checks at all. That is #669's
  defect from the other side. Second: **the mutation proof is executed twice**,
  by the fixer and by the reviewer, and lands in prose both times, so a proof
  that a check can fail exists in two pull-request bodies and never where a
  later seat could re-run it. Both need a cap raise or a graduation to pay for
  their lines.
- **Two rules are jointly unsatisfiable under concurrency, and the owner has to
  break the tie.** `finding-propagation.md` sends a finding that constrains
  every seat to its role contract under `tools/audit/briefs/` **once**, and
  holds the producing pull request from merging until the carry is in the tree.
  Two branches owing a carry to the same contract therefore cannot both comply.
  Raised on #201; no seat may decide it.
- **#680 (0008, #756): account, switch, verified login, then the rule, never
  first (0005). Lane F follows Wave 5. #303 at zero: stubs pinned, `max_cc`
  48 → 50 bought a narrowing (owner, 2026-09-11).** **0008's approver design was
  revised on 2026-09-14 and `docs/decisions/0009-*` is the live one; 0008 alone
  reads as its opposite** — agent identities author and approve, no human in
  the loop; the order above is unchanged. #954 closes at that verification.

**Owed from 2026-09-14: a stale-pin sweep.** #960 SHA-pinned every mutable
`uses:` in `.github/workflows/` (the frozen tag rides each pin as a trailing
comment). No lane sweeps refs for staleness -- `--sunset` reads policy
markers, and nothing under `.claude/workflows/` or `tests/` reads a workflow
ref (grep at merge base `c62210e`) -- so until the weekly `record` beat
(#959) grows one, an upstream fix reaches this repository only when a seat
re-pins deliberately.

## The machine this runs on — measure it, do not read it

A seat's box is not the owner's, and a container seat reading a description of
someone else's reads a page of false lines. Measure your own (`nproc`,
`command -v gh`, `python3 -V`). The repository facts: `tests.yml` matrixes both declared interpreters
(#514, closed), CI is the authority for the browser lane, and `git branch
--show-current` beats trusting a path.

**A 403 is not always the repository's answer.** Tag pushes and ref deletion
work from some environments and are proxy-refused in others, and the message
separates them: "Resource not accessible by integration" is a token scope,
"not permitted through this proxy" is the environment. Recording the second as
the first sends a reader to change what was never the obstacle.
