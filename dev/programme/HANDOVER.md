# Handover — the open-issues programme

updated-for: 0cc148b2f80fe224ffe2c504b29fd4f0908183df

The rule that governs this file is `dev/governance/rules/writing-for-agents.md`
(generated into `.claude/rules/`, which the harness loads on this path).
Delivery status is the frozen table in `dev/programme/plan-2026-09-open-issues.md`
plus one `dev/programme/delivery/<N>.md` per pull request (#1081), linked from
here and never restated. Chronology this file no longer carries is read at its
last pre-round-10 form, `git show a77faf30d:dev/programme/HANDOVER.md`.

## Round 10 — durable state

**Round 9 closed at v7.0.0** (#201 stays the tracking issue). Its handoff
branches are archived as tags (`git tag -l 'archive/handoff/audit-r9-*'`), so a
round-9 plan, roster or resume is read from its tag, never resumed.

**Round 10 opened 2026-10-14** under tvofi's rulings: every dimension under
`dev/governance/dimensions/`, three disjoint finder seats per dimension, one
verifier per dimension whose refute marks a finding **disputed**, one common
judge. Its stamps are read from main's first-parent line
(`git log --first-parent --format='%h %s' v7.0.0..origin/main | grep ' v7\.'`),
never listed here.

- **The plan of record is the roster**, `dev/programme/rosters/wave-r10-groups.json`
  on `origin/handoff/audit-r10-roster`, edited only through
  `tools/audit/seat/roster_edit.py`. The resume, plan table and next-session
  prompt under `handoff/round10/state/` on `origin/handoff/audit-r10-plan` are
  generated from it by `tools/audit/seat/state_docs.py`; they are volatile and
  not this file.
- **Volatile state** — running seats, open heads, the train queue, the next
  action, the critical-path set — is on #201 and nowhere here.
- **The record beat writes delivery rows; this file's `updated-for:` line stays
  manual by design.** `tools/audit/seat/record_row.py` generates each row from
  REST facts into a `record/autofix` pull request that merges with no review
  seat where `--automerge-check` passes. Expect two things and do not repair
  them: the one-beat lag (a merge's row lands on the next cycle), and no beat row
  for a closed-unmerged pull request, whose `closed, superseded` row is a manual
  record pull request. A seat's edit to a generated row takes that pull request
  off the automerge path.

## Decisions taken — do not relitigate

- **Mandate 6175172275 (#201, tvofi): `MANDATE: agents may approve as tvofi,
  scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z`.** It covers
  code-owner, policy and budget-raise approvals, so the round-10 orchestrator
  approves code-owned and policy merges under it, citing the id in the review
  body. Read it and any revocation from the API at the moment of use, as 0013's
  2026-10-02 amendment does; a raise under it also owes that decision's
  2026-10-14 amendment (`CLAUDE.md` rule 2). After `until`, decision 0007's
  per-pull-request owner review is the rule again.
- **The open-PR soft cap of 6 gates only starting a new roster group; opening or
  updating a pull request for an owed handoff is never refused** (tvofi,
  2026-10-21, refining the 2026-10-18 ruling in `tools/audit/seat/pr_cap.py`).
  The instrument predates the refinement: `open_pr.sh` calls `pr_cap.py gate` on
  every open, so until it learns the distinction an owed handoff opens with
  `--over-cap "owed handoff <topic> (tvofi 2026-10-21)"`. Owed below.
- **Cloud seats are dispatched through `tools/audit/seat/cloud_dispatch.py` and a
  remote-trigger dispatcher routine, never as interactive session cards**
  (tvofi, 2026-10-21). The payload shape, the return refs and the two driving
  traps are `tools/audit/seat/INSTRUMENTS.md`'s.
- **Model routing is Claude seats, per roster group** (`fixerModel`,
  `reviewerModel`, the `model` object). The owner's 2026-09-09 ruling: Opus for
  orchestration, architectural fixes and review, survey, judge and production
  fixes; Sonnet for tests, tooling, docs, records and read-only reporting;
  **Fable only for a very large multi-layer refactor where Opus is judged too
  risky.** A model trailer on a merge or a stamp is the session's model, not a
  routing event.
- **`main` is guarded by three rulesets**, read from
  `/repos/<owner>/<repo>/rulesets/<id>`, never from here: `main-protect`
  (22628467) holds deletion and non-fast-forward and, read 2026-10-21, no bypass
  actor; `main-protect-checks` (23698884) holds the required checks, one
  approving review and the code owner's review (0009 step 6), with `always`
  bypasses for the stamp deploy key and the `hpo-ledger` App 5094721;
  `release-tags-protect` (23937752) guards tags, deploy key bypassing. Rollback
  is one DELETE per ruleset (#1300). **Before adding a required context** confirm
  it reports on a pull-request head, not only on a push to `main`: one that
  never reports blocks every merge, a matrix change is a required-set change,
  `skipped` and `neutral` satisfy the rule (measured both arms), and a scheduled
  context made required blocks the merge that would repair it.
- **A stamp pushes over the deploy key only**: `tools/release/stamp.py --push
  --push-key <key> --known-hosts <file>`. The old admin token returns 401.
  A stamp over a red `main` takes `--allow-red` with the cause recorded in the
  release notes and on #201, and over a merge whose row is not yet written
  `--allow-rowless` likewise (v7.0.2, tvofi, 2026-10-20).
- **Merges land as merge commits** (0010); the merge body defaults to the pull
  request's title, so a closing keyword in a title reaches `main`.
- **`_helper(self, ...)` is refused** as a decomposition: it erases moved
  references at zero cost, a measurement artefact; a supplied-literal check pins
  nothing.
- **Never re-gate an unchanged head.** A terminal CI result at that head is the
  gate evidence. Local runs exist for what CI cannot produce: the mutation proof,
  the failing test at the merge base, the finder's harness at both ends.
- **#387 was fixed with the `env_drift` shape**, not by growing `alt_basins` nor
  by lowering the coverage floor: tree and merge base in one run, computed to
  computed. The coverage floor is a literal, not an environment override.
- **Every sentence earns its place** (owner, 2026-09-07); the rule is
  `writing-for-agents.md`.
- **The #1058 tie-break: a body long from disclosed self-corrections is re-cut by
  relocating them here.** `fixer.md`'s re-cut and *cutting evidence is never
  compliance* pointed opposite ways; a disclosed self-correction is a correction
  to the record, so it moves into that section below and nothing is cut.
- **A pull-request body carries `## Figures`** (#676). The detector that works
  resolves a file name to an artefact; the looser one — any number near a file
  name — was refused in review for reading a date and a line count as caps.
- **The pull-request body is one live object.** Every head's contract job reads
  the current body, so a red at a superseded head is the instrument, not the
  commit.
- **A new option key derives into `config_flow._ABSENT_FALLBACKS`** or every
  options-page visit writes it (#1107); `tests/config_flow_steps.py` derives the
  set rather than listing it.
- **A coverage ratio over an open set of mutation carriers is not a figure**; the
  denominator is unbounded, so state the class. **A figure about the document it
  lives in is derived beside it, at the head.**
- **A generalised vacuous-acceptance-arm detector is refused on cost** (#201
  comment 5720829142, #1125's reviewer ruling): the shape is three classes — a
  harness decoupled from the mutated code (W1067-G7b-1), an under-specified
  environment precondition (#1115), a false prose claim no mutation proof
  addresses (#1120) — and a detector needing different logic per class was
  judged a research project against a defect costing about one review round.
  The refusal owes its qualifier: the catch rate rests on an attentive seat, not
  a mechanism. #1126 is the instance found after it: a check carried a retyped
  copy of `VERDICT_RE` that diverged from `web-fix-wave.js`'s, and its null
  control passed on either regex; the fix executes the source's own literal. Do
  not re-propose without new information.
- **Wave 1067's three deferrals stand** (plan
  `dev/archive/plans/plan-1067-rotenso-inputs.md`): the new option keys stay
  options-page slots out of `topology._SLOTS`; no zone-2 supply slot, since the
  two-zone model carries one flow temperature and no per-zone emitter law; the
  flow-lift bias stays one-sided so the scalar and batch COP paths agree.
  **W1067-POST1** (offer the pre-fill when a heat-pump device is added) gets its
  own issue when started, none before.
- **dp 107 is read two ways and stays unresolved without a reading from the
  owner's install** (owner decision 7, W1067-G7b-2): make-all/tuya-local
  (`4551357`, `devices/fisher_water_heatpump.yaml`) reads it as the tank's
  current temperature, tvofi/tuya_heat_pump (`fda9bed`, `models/000004k4z6.py`)
  as the wired controller, tank on dp 26; both readings are pinned in
  `tests/features.py`. A DP-keyed localtuya table is refused for the same reason
  — a DP number is not identity — unless a firmware signature proves the device.

## Corrections to the record

- **This file is not policy and no budget reads its text.** It sits outside
  `POLICY_GLOBS` (owner, 2026-09-16, #201 comment 5702401684; `.github/CODEOWNERS`
  says so in its header), so a record pull request touching only it owes no
  `## Approval` and no code-owner review. `policy_budgets.json` names it in
  `roles.record.opens`, which charges the rules that path loads, not the file:
  `policy_lint.mjs --budgets` prints the same aggregates with this file grown.
  The residual is a reviewer's: prose moved here leaves the corpus.
- **The `hpo-ledger` bypass on `main-protect` is gone.** The owed item that asked
  tvofi to ratify or remove App 5094721's `always` bypass on 22628467 (#201
  comment 5902383542; 0011's 2026-10-02 setup recommends removal) is retired: a
  read of that ruleset on 2026-10-21 returns no bypass actor. 0011 still records
  the decision as the owner's to take.
- **The "34-key `data` payload" is wrong**, as is any count of it; the freeze is
  enforced by `tests/features.py`'s symmetry check and the `coord_*` goldens
  (#193).
- **#510 was blindness, not decoupling**: `tests/structure.py` did not resolve
  `getattr(self, "_ctx", self).X`; under a counter that does, Wave 4's S1 cut
  series is identical at both ends (#512).
- **A file reported missing was there**: the seat listed a checkout on a stale
  branch. Check existence with `git show origin/main:<path>`.
- **Leave both claim files exactly as you found them** (#662). "Always
  byte-identical" was refused (#600 rightly carries 33 claim lines), then "empty
  on a branch that claims nothing" — a squash applies that deletion to `main` and
  carries another lane's claims off, measured four times (#608, #635, #658,
  #746). Since #747 the guard, the bot and the stale-claim judgement ask per file
  kind.
- **The pull-request checks listing shows the latest run per check** (#669), so
  an earlier red behind a later green is invisible, and the mirror error reads a
  superseded failure as red. Read `/repos/<owner>/<repo>/commits/<sha>/check-runs`
  (`web-fragments.md`).
- **The subject enumerator missed merges and invented them, and the errors hid
  each other** (`24 = 25 - 2 + 1` over `a9d117c..8f754c9`). Compare sets, never
  totals; the API enumerator is the default since #1050.
- **The red-check refusal fires from `f605da4` (#1040) on**; `CLAUDE.md`'s "only
  the red-check trigger is enforced" is a measurement from that SHA.
- **`GET /repos/.../rules/branches/<branch>` is not bypass-aware**: emptying the
  bypass list returns an identical answer. The honest test is a probe branch
  with its own ruleset, both arms.
- **An empty diff over `tests/` and `custom_components/` does not mean no gate is
  owed** (#1122): the merge had moved files inside recorded closures. Derive scope
  from `closure.py select`, never from top-level directories.
- **Wave 1067's merged bodies carry three figures their reviewers could not
  re-derive**; the bodies stay, this is the correction. #1150's "22 other
  configs" is 21 (`comm -23`), and its empty-signature predicate returns `True`
  on `all(())` — unreachable today, a trap for a future table. #1152's "253.3 µs
  per drive" measured 72.4 µs on the reviewer's driver, unverified either way;
  the verdict holds at both. #1153's "256 production lines (218/32/6)" is 281
  (`237 + 37 + 7`) under the body's own rule, and its "0 `mypy --strict` errors"
  is unavailable, not true or false; CI's `typing` check is the answer.

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

38. **A sectioned config-flow field resolves its label ONLY at
    `step.<id>.sections.<s>.data.<field>` and `data_description`, with no
    fallback to step level.** Every label check this repository had read the
    step-level `data` map, which the HA frontend does not consult for a field
    inside a `section()`; the fields rendered as raw keys — per language, in
    both flows — from v6.3.19 (#653) and v6.4.1 (#849) until #1111 restored
    them in v6.6.2. **The class is a check and the production code agreeing
    about the wrong location**, so the check confirms the defect. Graduated:
    the schema-derived, no-fallback assertion in `tests/entities.py`, which
    walks the built schema rather than a hand-written key list. #1114 then
    fixed the same blind read in seven audit harnesses under
    `tools/audit/round3/` and `tools/audit/round4/`, none of which the gate had
    ever contradicted.
39. **`prepr.sh` gates `## Head` against the LOCAL head and `pr-contract` gates
    the pull request's REMOTE tip, so a pull request that writes its own record
    file must push twice and one `pr-contract` run necessarily fails on the
    commit being replaced** (#1116). It is a red-then-green at a superseded
    head, not a defect — `push.sh`'s `pr_arm` selects `body-then-push` once a
    pull request is open, which is what orders the two. Read it with the
    commit's `check-runs` API (correction above), and answer it in the body by
    naming the superseded head rather than re-running anything.
    **Instances: #1116, then #1121. This is a named recurrence at two, recorded
    here so the next seat knows where it stands** — at a third,
    `defect-root-cause.md`'s recurrence trigger fires and the answer is a
    root-cause seat, not a third pull-request paragraph explaining the same red.
    No countermeasure is proposed at two, and that is the decision rather than
    an omission: a check that suppressed this red would have to stop reporting a
    body genuinely stale at the head, which is what `pr-contract` is for, and
    the gap itself exists only between two API calls that `push.sh`'s own header
    says it cannot make atomic.
40. **`policy_lint.mjs --budgets` exits 0 whatever it prints — it reports, and
    never refuses.** Its handler is `if (has('--budgets')) return
    cmdBudgets(files), process.exit(0)`, unconditional; the bare
    `node tools/policy/policy_lint.mjs` is the path that refuses
    (`process.exit(errors > 0 || rc ? 1 : 0)`). A mutation proof driven against
    `--budgets` proves nothing (#1123): its own proof was driven against the
    refusing bare form instead — appending two lines turned it rc=1, naming
    both the touched file's cap and the corpus cap; restoring returned rc=0.
41. **The test for whether a repair's invariant is true by construction, or
    true only because the arm now asserts nothing, is to force the precondition
    it relies on back to false and check the arm reddens.** #1115's `--record`
    acceptance arm had asserted an invariant that held only where
    `origin/main` is reachable from `HEAD`; under a shallow clone it
    enumerated 611 merges and reddened. The repair made the window
    `mainRef()..mainRef()`, empty by construction — and the decisive check was
    not that the window is empty: reverting to `HEAD` inside the shallow clone
    had to reproduce the original red, and deleting the `requireToken` call
    had to redden the refusing arms (`FIXTURE VACUOUS`). Both did. Apply this
    test to any repair that makes a window, a set or a diff empty by
    construction, not only to this one.
42. **A main-only ratchet red hides behind per-PR grading, and two such reds deadlock each other.** Per-PR grading reads each merge commit's own checks; a red that only exists on `main` — a `main` selftest, a `main`-grading ratchet — reddens every open pull request's required verdict while the pull request's own checks stay green, and no pull request can fix it alone. Round 9 paid this twice in one day: the closure lane-balance pin was unsatisfiable for every lane plan once #2142's re-record (`282054566`) put `boost_drift_replay.py` at 3379.1 s, more than half the 6059.1 s table total, against a `2*max(loads) < sum(loads)` pin with no escape arm (#2173 added the optimality second arm: a plan whose wall equals the heaviest indivisible script is provably optimal), and the `archscore.coord_footprint` row had grown to 2592 derived against a committed 2587 (#2118 grew it without re-recording). The two fixes then deadlocked — each pull request's merge commit lacked the other's fix, so neither required-context verdict could go green while both stayed open — resolved only by cherry-picking #2175's re-record verbatim onto #2173 as `4d6d329e5` and closing #2175 as superseded. The third re-record of the same class, `script_runs_*` 63 → 68, is #2179. And the mirror error: a required context with **no run at all** at a head is not green — it is "not yet" to any completion wait (#2170, #2171, `dev/audit/rca/R9-RCA-TRAIN-WEDGE.md`), and check-runs at merge tips may not exist during saturation, so "no runs" never reads as a conclusion.

43. **A daemonized instrument with a silent log is not a dead instrument.** The wrapper's `dup2` makes stdout a file, Python block-buffers a file, and every heartbeat sat in the 8 KB buffer a SIGKILL dropped — an 8-minute healthy train (a FULL run in progress at main's tip) was read as dead and killed. #2180 (`d9e54b642`) kills the class with three one-liners: the entry reconfigures stdout line-buffered itself, batch and train announce tag/pid/base/queue as the log's first line before any blocking call, and the poll sleeps to the next beat (`HEARTBEAT_SECONDS`, not `POLL_SECONDS`) — before that, even unbuffered, the first beat was 305 s. Rehearse under the incident's exact wrapper shape before believing any launch fix.

44. **App-quota 403s arrive disguised as red lanes and as missing runs.** At saturation the shared App quota turns into arch-score/env-matrix/validate-hacs reds that are rate limits, not verdicts (#2168's body names its arch-score red as this class), and dropped workflow events leave required contexts with no run at the head. The fix is a **recarry** — a new merge commit at the live head re-fires the events, the verdict carrying via #2162's `--approval-carry` — not a rerun of the failed lane. The automated recovery is session-only and does not fire while turns are active; a manual recarry is the recovery.

45. **A sibling merge silently reverts its sibling.** #2120's branch was cut before #2119 merged; on fold, main's side of a shared region carried the sibling's newer fix and the branch's side was empty — resolving to the branch would have reverted #2119 with no conflict and no red check — and the branch's structure-budget payment had lost its hunk to the sibling's newer comment on the same spot, so the honest re-record restores main's own value rather than raising anything. The countermeasure, executed at every fold that day (#2120 at `ab2307794`, #2066 at `2f3934468`): a silent-revert sweep over every shared file (0 of main's lines lost, named budget cells excepted) and a union-with-name-set proof for add/add conflicts in `tests/features.py` (0 of main's `R.check` names lost).

46. **The recarry treadmill prices every queue move.** A queued pull request's verdict is carried to the live head by recarry; each move of `main` re-prices every queued entry. Merge fast after lanes conclude or main moves first. The working shape is the 2026-10-13T14:07Z cascade on #201: up-front recarries, admissions in queue order, machinery-touching heads held to a final pass that runs the fixed code.

47. **`merge_pr.sh` stops on `UNSTABLE` when only an optional context is red**,
    though every required context is green (#2465). `nightly-status` reports the
    last scheduled run, not the pull request; read the required set from the
    ruleset and merge at the exact head.
48. **A `CANCELLED` required context is not a verdict.** A recarry supersedes the
    run in flight; rerun it and read the conclusion (#2469, `Analyze (python)`).
49. **No detached loop survives a host reboot.** At the 2026-10-21 takeover the
    train, the tick loop, the state-docs beat and `wt_sync.sh` were all dead and
    the train had stopped mid-queue; a resuming orchestrator restarts each from
    the tree and re-reads the queue, never assumes a loop it did not start.
50. **The deploy key's SSH on port 22 can time out from the stamping host.**
    Route `github.com` to `ssh.github.com:443` in the SSH config and verify the
    host key against GitHub's published fingerprints (v7.0.2's stamp).
51. **The next-session prompt renders a group with no branch as
    `git fetch origin None`** (`tools/audit/seat/handover_prompt.py`'s in-flight
    line takes the field unguarded). That line is generator output, not a
    command: such a group starts from `main`.
52. **A cloud seat's container may not put the toolchain on `PATH`, and the
    system `python3` cannot parse the suite.** Measure `python3 -V`: on 3.11
    `tests/entities.py` fails on its own f-string before any check runs. Prepend
    `/opt/hpo/venv-ci/bin` and run with `env -u BASH_ENV
    PYTHONPATH=tests/hastub`. Through the agent proxy, `gh api --paginate`
    follows GitHub's numeric-id `Link` URL and gets 403 after page one: loop
    `?per_page=100&page=N` on the `repos/<owner>/<repo>` path instead.

## Owed

**Post-hoc reviews from 2026-09-07.** #591, #592, #596, #602, #603, #605
and #569 merged without an independent verdict at their final head (review
capacity lost to a rate limit), and #606 with no review at all as a red-`main`
repair; each squash body names where a reviewer starts. **#603** is policy whose
approved form changed twice after approval; **#596** introduced
`tests/typing_budgets.json`, the baseline every typing tranche ratchets against,
which no reviewer has checked.

**A finding for `dev/governance/roles/fixer.md`**, not landed because it is
policy: a probe that builds its own input can build the complement of
production's input (#591's seat).

**From 2026-09-09, none decidable by a seat.**

- Two one-clause policy edits carried out of #580: `fix-review.md` has no step
  for an ABSENT check (a pull request whose workflows never queued shows no red),
  and the mutation proof runs twice, fixer and reviewer, landing only in prose
  where no later seat can re-run it. Both need a cap raise or a graduation.
- `finding-propagation.md` holds a producing pull request until its carry is in
  the tree, so two branches owing a carry to the same contract cannot both
  comply under concurrency. Raised on #201; the owner breaks the tie.

**The open-PR soft-cap instrument against the 2026-10-21 ruling.** `pr_cap.py
gate` refuses any open at or over the cap; the ruling exempts an owed handoff.
Until it distinguishes the two, the `--over-cap` reason above is the route.

**An instrument over the plan's open-issue dispositions, or a decision not to
build one.** `recordRegion` reads the plan's `## Delivery status`, the delivery
rows and this file; `## Open friction issues — dispositions` is read by no
check, while `delivery-status-tracking.md` obliges a disposition for every open
issue. A detector must not disposition an issue by mere mention — the shape #658
narrowed the region to escape.

**A stale-pin sweep** (cited from `.github/workflows/codeql.yml`). #960
SHA-pinned every mutable `uses:`; no lane reads a workflow ref for staleness, so
an upstream fix arrives only when a seat re-pins deliberately.

**`tools/policy/policy_lint_envmatrix.mjs`'s `okRef` row still drives
`--record --since HEAD`** on the assumption that `HEAD..origin/main` is empty in
its clone — the defect #1115 fixed for `--record`'s acceptance arm. For whoever
next touches the env matrix.

**`tests/typing_ruler.py`'s docstring still says the pinned toolchain is one
"which no gate lane has"** (grep that phrase); #1122 established it false —
`HPO_TYPING_PYTHON` re-execs the pinned mypy half through `run.sh`.

## The machine this runs on — measure it, do not read it

A seat's box is not the owner's. Measure your own (`nproc`, `command -v gh`,
`python3 -V`); `tests.yml` matrixes both declared interpreters, CI is the
authority for the browser lane, and `git branch --show-current` beats trusting
a path.

**A 403 is not always the repository's answer.** "Resource not accessible by
integration" is a token scope; "not permitted through this proxy" is the
environment. Recording the second as the first sends a reader to change what was
never the obstacle.
