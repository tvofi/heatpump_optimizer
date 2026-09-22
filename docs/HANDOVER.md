# Handover — the open-issues programme

updated-for: 4bcfcf2030eee29edf27ec1ce167d29707751c98

Taken at this record seat's own merge base off `origin/main`. W1067-G8
re-pointed this line to `a53fc75` (origin/main's tip) as it closed wave 1067
out; the merges since the prior stamp `25696f8` (#1147) are #1142 `da63bbb`,
#1149 `7b4071c`, #1152 `69a0896`, #1150 `582d2ee` and #1153 `a53fc75`. Re-derive
rather than trust this line if it reads stale against `origin/main` HEAD.

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
  that is enforced rather than asserted.** Two rulesets are active on the
  default branch. **`main-protect`, id `22628467`**, carries the push guards:
  deletion and non-fast-forward. **`main-protect-checks`, id `23698884`**
  (created 2026-09-19), carries the merge guards: the required checks its
  endpoint returns, never a count from here, the `pull_request` rule — one
  approving review and the code owner's review on a path `.github/CODEOWNERS`
  names (0009 step 6, 2026-09-17 04:58Z) — and the one bypass, the deploy key
  `hpo-stamp`, `always`. The admin role no longer bypasses, so the rule binds
  the orchestrator's merges as `tvofi` too; GitHub refuses the merge rather
  than a policy asking you not to. **The merge flow**: seats author as
  `tvofi-seat-author`; an ordinary pull request merges after an adversarial
  `merge` verdict and the App `hpo-approver`'s approving review (first:
  #1100); a policy one needs the owner's approving review on GitHub (first:
  #1098), which a seat cannot obtain for itself — open it, surface it, and
  wait. That bypass and the rollback below are the owner's levers, not a
  seat's. **The rollback is one DELETE per ruleset, not one**: deleting
  `main-protect-checks` drops the required checks, the review rule and the
  bypass; deleting `main-protect` drops the push guards. Deleting either alone
  leaves the other half of the boundary standing (#1300).
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
- **A setting the entry never stored is no longer written when the options page
  posts its default** (#1107, released v6.6.1). `config_flow._ABSENT_FALLBACKS`
  is the set whose absence already IS the shipped default, and
  `tests/config_flow_steps.py` derives it — *"`_ABSENT_FALLBACKS` is exactly the
  proven set"* — rather than letting it be listed by hand. **Constraint on a new
  option key**: it derives into that set, or every page visit writes it.
- **A coverage ratio over an open set of mutation carriers is not a figure.**
  The denominator is unbounded. State the class.
- **A figure about the document it lives in is derived beside it, at the head.**
  Carrying one is how it goes stale on every review of the artifact that states it.
- **A generalised vacuous-acceptance-arm detector is refused on cost, not
  owed.** Dispatched at the fourth instance (#201 comment 5720829142): the
  shape is not one class but three — a harness structurally decoupled from the
  mutated code (#1117, W1067-G7b-1), an under-specified environment
  precondition (#1115), and a false claim in prose that no mutation proof
  addresses (#1120) — and the root-cause seat's own asymmetry claim ("only
  reviewers catch this") was refuted: W1067-G7b-1 was caught by its own
  mutation proof and `RELEASE_NOTES.md` records a prior self-caught instance,
  3 of 4 rather than 4 of 4. Neither of `defect-root-cause.md`'s two
  enforcement triggers fires on any of the four (none reached a release, none
  turned a required check red); the mandate is `CLAUDE.md`'s separate
  recurring-error clause. The seat's cited figures — 37 historical instances of
  this named shape, effectively 100% caught before `main` — are that seat's
  own measurement, not independently re-derived here. A generalised detector
  needing different logic per shape was judged a research project against a
  defect costing roughly one extra review round, and refused. One narrow
  `fixer.md` sentence is proposed and explicitly NOT pushed: it needs a cap
  raise or a cut and neither owner grant in hand covers it; it waits on the
  owner's sign-off. Do not re-propose a generalised detector without new
  information. **The refusal stands (#1125's reviewer ruling, accepted) but
  owes this qualifier: the ~100% catch rate it cites rests on an attentive
  seat noticing, not on a mechanism that guarantees noticing.** A fifth
  instance of the same shape surfaced after the refusal was written and was
  not caught by any check, until [#1126](https://github.com/tvofi/heatpump_optimizer/pull/1126)
  (merged `2296de3`) fixed it: `.claude/workflows/check-wave-script.mjs`'s
  verdict-grammar block carried its own hand-rebuilt copy of `VERDICT_RE`
  instead of deriving it from `.claude/workflows/web-fix-wave.js`'s source,
  the two silently diverged (production tightened its SHA capture to
  `[0-9a-f]{40}` while the local copy kept `\S+`), and the block's own
  null control — a bare `merge deadbeef`-shaped verdict, meant to catch an
  extraction that accepts anything — stayed green throughout on either
  regex, proving nothing about which one the artifact actually used. It was
  caught only because a seat stopped to reason about why its own control
  passed, the same route as the other four, not a mechanism. #1126's fix is
  to execute the literal `VERDICT_RE` text out of `web-fix-wave.js`'s own
  source (via `new Function`) rather than retype it, so the two cannot
  diverge again by omission. Cite this instance by what it was, not by a
  line number: line numbers in a fixed file are exactly the rot
  `brief-citations.md` exists to catch, and this paragraph predicting that
  condition is not a reason to leave it unmoved once the condition occurs.
- **dp 107 is read two ways and neither reading is resolved** (owner decision 7,
  W1067-G7b-2). make-all/tuya-local (`2026.9.1`, commit `4551357`,
  `devices/fisher_water_heatpump.yaml`) reads dp 107 as its `water_heater`'s
  current temperature; tvofi/tuya_heat_pump (`fda9bed`,
  `models/000004k4z6.py`) reads the same DP as the wired controller (T6) and
  keeps the tank on dp 26. Each pre-fill source table follows its own source,
  the disagreement is pinned at both generated fixtures in `tests/features.py`,
  and **do not resolve it in either direction without a reading from the
  owner's install**. The same session refused a DP-keyed table for localtuya
  on the same ground: its records are a device id, a DP number and the user's
  own names, and a DP number is not identity — across that corpus's 1746 device
  configs at `4551357`, dp 101 is configured in 826 of them and dp 107 in 407,
  in 488 and 314 distinct (domain, entity name, DP name) readings respectively.
  A DP-keyed localtuya table ships only behind a firmware signature that
  proves the device — none was found — and the fuzzy fallback carries the
  platform instead.

### Wave 1067 — closed out (#1067)

**The wave landed in full. #1067 closes with the pull request that writes this
note (W1067-G8); the Delivery-status row in `docs/plan-2026-09-open-issues.md`
is the record of which merge carried each group — linked there, never restated
here.** The plan of record is `docs/plan-1067-rotenso-inputs.md`. Its status
block overrides the G2 brief: the lift-aware efficiency reference was built,
measured to double-count the lift, and reverted, so the credited COP is
unchanged from `main`; only G3's pricing of the lift stops the walk. The same
block records two deviations from the plan as written — the wave ran as
sequential commits on one branch with one pull request per repository, so the
per-group branches never existed, and the **per-group roster file was
deliberately not committed**, because `brief_lint.mjs` refuses a carry filed at
an issue a roster already covers; `carry-1067.json` is the mechanism kept. The
only carry that outlives the wave is **W1067-POST1**, the post-wave follow-on
(offer the pre-fill when a heat-pump device is added): outside #1067, and it
gets its own issue or tracking entry when it is started, none before then.

Three deferrals taken during the wave — do not relitigate them:

- **Card assignment of the new option keys is deferred.** They are options-page
  slots, not card slots: they stay out of `topology._SLOTS` on the
  `CONF_COMPRESSOR_FREQ_ENTITY` precedent, so `ASSIGNABLE_KEYS` stays at 21 and
  the documented count and its live harness are untouched (plan § Design
  decisions).
- **No zone-2 supply slot (the C4 deferral).** The two-zone model carries one
  flow temperature (`thermal_model.py:1952`) and no per-zone emitter law, so a
  zone-2 supply slot would feed nothing (plan § W1067-G8).
- **The flow-lift bias stays one-sided** (above the plan's curve only), kept so
  the scalar and batch COP paths agree; the docstring records the trade-off
  (plan § W1067-G3, `compute_cop`).

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
  histogram that keyed on the spelling a seat typed and counted entries rather
  than pull requests.** Both are fixed (#1119). **The corrected rule RE-KEYS
  these issues; it does not retract them** — at `e467026`, over
  `v6.5.1..origin/main`, 52 merged pull requests, six of the seven are over the
  threshold under their new key: #1070 9/9, #1095 7/9, #1078 5/7, #1079 5/5,
  #1069 4/5, #1087 4/4, as PRs / entries. Nothing here says the friction was not
  real, and the issues are not re-titled. **Every count in this entry carries the
  head it was taken at, because they move with nobody editing them** — #1070 read
  7/7 at `c71c53c` and 9/9 one day of merges later.
- **#1094 is the one that changes character, and the reason is worth the
  paragraph.** Its title key, `orchestrator`, is a ROLE NAME, and a role name
  designates a seat as readily as that seat's contract. Every entry behind it
  records friction with a **dispatch brief** — the lease tool named as
  `tools/audit/gate_lock.py` when the tree has `tests/`, a G3 premise that
  cannot hold on the stock house, a G4 derate range, a claim-files
  contradiction — and none with `tools/audit/briefs/orchestrator.md`, which does
  not govern any of it. `.github/PULL_REQUEST_TEMPLATE.md` offers one field,
  `<rule_id>`, and no field for a brief, which is why the two subjects arrive
  under one shape. So `tools/audit/briefs/*.md` resolves only from an id that
  names it as a FILE, and a bare or suffix-qualified role name stays verbatim.
  At `e467026` the dispatch key reads 2/4 and the contract key 2/2, and neither
  clears the threshold in that window. **Its two controls, because a disposition
  has to state both its key and its window:** the same key over
  `v6.6.0..origin/main` reads 1 distinct pull request, and `main`'s
  un-normalised classifier splits the same entries into `orchestrator` 4 and
  `orchestrator.md` 2. A count that moves under either is a count whose key and
  window were never stated. An earlier draft of this entry said recurrence did
  not support #1094; that was written about the raw key and is **withdrawn** —
  the rule re-keys the issue, it does not retract it.
- **Do not carry any of those counts.** `<ref>..origin/main` is enumerated
  against `origin/main`'s tip at the moment of the run, so every one of them is
  a sliding figure; seven merges landed during #1119's own review and moved all
  of them. A seat disposing one of the seven re-derives with
  `node .claude/workflows/policy_lint.mjs --stats --since <newest tag>`, reads
  the `PRs / entries` column, and resolves its own key with
  `--normalize-friction-keys` rather than assuming the title is the key. The
  filing lane re-measures every open issue on each beat and comments when its
  key is below threshold in the current window; it never closes, so the
  disposition is still a seat's. A key below threshold in one window is not a
  fixed problem — the window moved when the last tag was cut, and the friction
  may be older than it.
- **This file is NOT policy for the budget and approval machinery, and seats are
  still being briefed that it is.** `docs/HANDOVER.md` sits in `CORPUS_EXCLUDED`
  and matches no `POLICY_GLOBS` pattern (owner, 2026-09-16, #201 comment
  5702401684); `.github/CODEOWNERS` says in its own header that it is
  deliberately absent. So a record pull request whose diff is this file owes no
  `## Approval` section and no code-owner review, and its growth spends no cap —
  `--budgets` does not list it. The residual the exclusion names is real and is
  a reviewer's job, not a check's: prose moved into this file leaves the corpus.
- **`tests/mutation_budgets.json`'s stated reason is stale.** It says the cap
  waits on a full-package run that "cannot happen until mutation-nightly is on
  main"; the `mutation-nightly` job is in `.github/workflows/tests.yml` and
  `last_measured.full` is still `null`. **`mutation` is not a required check** —
  read the contexts from the `main-protect-checks` ruleset endpoint, never a
  count from here; `coverage`, `mutation-nightly`, `slow` and `nightly-status`
  are absent
  from it too, and `/branches/main/protection` answers 404, so the ruleset
  endpoint is the only reader. With `max_survivor_fraction` at 1.0 in both
  scopes and the refusal written `if rate > cap`, the lane cannot fail on a
  survivor: every red it carried in the retained window was its baseline guard
  re-reporting a red `fast` already reported by `fast`.
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
- **An "empty diff over `tests/` and `custom_components/`" does not mean no
  gate is owed.** #1122's fixer argued the post-absorb diff over those two
  trees was empty, so no re-run was needed; the reviewer upheld the judgement
  but refuted the reason — the merge had also moved
  `.claude/workflows/policy_lint.mjs` and `friction_issues.mjs`, both inside
  recorded closures. `python3 tests/closure.py select --diff <merge-base>`
  still selects `tests/entities.py`, which passed in 34 s (`ALL 1508 ENTITY
  CHECKS PASSED`). No full re-run was owed, but the stated reason was wrong
  and must not be reused: derive the gate's scope from `closure.py select`,
  never from which top-level directories a diff appears to touch.

- **Wave 1067's merged bodies carry three figures their reviewers could not
  re-derive. The bodies are merged and are not edited; this is the correction.**
  Each was a non-blocking disclosure inside a `merge` verdict, and each pull
  request's conclusion holds at the corrected figure.
  - **#1150's "the 22 other configs that hold 'Outlet temperature' alone" is off
    by one** (comment 5735932097). `comm -12` returns the Fisher config inside
    the 22, so the count *other than* it is **21** (`comm -23`); the word
    "other" was the error. No test and no acceptance claim rested on it. **The
    same review found #1150's new empty-signature predicate inverts the old
    skip: `all(group & matched.keys() for group in signature)` returns
    `all(())` = `True`,** so an empty signature would apply a table
    unconditionally — unreachable today, because both registered sources carry
    non-empty signatures and nothing in the tree builds an empty one, so no test
    covers it: a latent trap for a future table, worth a comment rather than a
    defect in that change.
  - **#1152's standing-cost figure, "253.3 µs per drive over 2000 runs", is not
    re-derivable** (comment 5736026666): the reviewer's own 2000-run driver,
    same loop, warm, measures **72.4 µs/drive** — 3.5× lower — and is stated as
    unverified rather than confirmed. It does not threaten the conclusion: at
    either figure the standing cost is a fraction of a millisecond against a
    fixer seat cycle of hours, so the cost test's verdict (build it) holds a
    fortiori.
  - **#1153's "production code delta, 256 lines (218 `name_match`, 32
    `device_prefill`, 6 `config_flow`)" is not re-derivable** (comment
    5737708367): under the rule the body itself states — non-blank lines less
    `#` comments less module/class/function docstrings, counted with `ast` at
    each end — the reviewer's instrument gives **281** (`237 + 37 + 7`) at every
    commit carrying the final files, and no rule yields 218/32/6. The body
    *understates* its own delta; the material claim (most of the 529 added lines
    are prose) stands at 281. The same review reproduced **#1153's "0 `mypy
    --strict` errors" as *unavailable*, not as true or false** —
    `homeassistant-stubs==2026.2.3` is not on the index that seat's pip reaches
    and `tests/typing_ruler.py --mypy` refuses to measure an unpinned tool
    (#504); the authoritative answer is CI's green `typing` check at the head.

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
    `node .claude/workflows/policy_lint.mjs` is the path that refuses
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

**Owed: an instrument over the plan's open-issue dispositions, or a decision
not to build one.** `recordRegion` reads the plan's `## Delivery status`
section, `docs/delivery/` and this file; every other `##` in the plan is outside
it. So `## Open friction issues — dispositions` (#1121) is unread by any check —
deleting it whole leaves `--record` byte-identical, `RENDER` included — while
`delivery-status-tracking.md` section 5 obliges a disposition for every open
issue. The obligation is real and the coverage is a seat's grep. **What the
detector would have to avoid** is the shape #658 already narrowed the record
region to escape: a check that accepts an issue number mentioned anywhere
dispositions it by mention, which is the defect, not the fix.

**Owed from #1116, two items its merged body left open.**

- **Its body says `--list` "lists nine of the ten" corpus checks; re-measured at
  `c71c53c`, that is wrong in both halves.** `cmdList` iterates a separate
  fifteen-class registry, not `CORPUS_CHECKS`, so the overlap is a property of
  two lists: seven of the ten wired in `CORPUS_CHECKS` have a `--list` class and
  three do not — `orphan-caps`, `row-freeze` and `rule-binding`. Derive it by
  intersecting the two rather than reading a count here.
- **The `--list` discoverability fix landed (#1137), closing the hole above.**
  Every entry in `policy_lint.mjs`'s `CHECKS` registry that lists a corpus check
  now names the wired function it stands for, and `assertAcceptance` holds both
  directions against `CORPUS_CHECK_NAMES`: a wired check with no `--list` entry,
  an entry naming an unwired function, and a duplicated entry each turn the
  acceptance red. `orphan-caps`, `row-freeze` and `rule-binding` are now listed.

**Owed from 2026-09-14: a stale-pin sweep.** #960 SHA-pinned every mutable
`uses:` in `.github/workflows/` (the frozen tag rides each pin as a trailing
comment). No lane sweeps refs for staleness -- `--sunset` reads policy
markers, and nothing under `.claude/workflows/` or `tests/` reads a workflow
ref (grep at merge base `c62210e`) -- so until the weekly `record` beat
(#959) grows one, an upstream fix reaches this repository only when a seat
re-pins deliberately.

**Owed from #1115, flagged for whoever next touches the env matrix, not this
pull request's to fix.** `policy_lint_envmatrix.mjs:238`'s `okRef` row still
drives `--since HEAD` on the assumption that `HEAD..origin/main` is empty in
that clone — structurally the same defect #1115's `--record` acceptance-arm
fix addressed, and now load-bearing because a fixture token was added to this
row since. Pre-existing before #1115 and green everywhere it has been
driven.

**Owed from #1122, named as incomplete rather than false.** `tests/typing_ruler.py:33`
and `.github/workflows/tests.yml:427` still carry "which no gate lane has,"
the exact sentence #1122 established as false — `HPO_TYPING_PYTHON` re-execs
the pinned mypy half locally via `run.sh` — and repairs at those two sites
(`run.sh`, `gate-scoping.md`) but not at `tests/typing_ruler.py:33` or
`.github/workflows/tests.yml:427`. #1122's own body names this as owed and
does not claim to have repaired it.

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

## 2026-09-19 — the authoring identity moved to the hpo-author App; nine merges; v6.6.5

The seat USER account is spam-flagged with the worst measured shape: writes
return 201 and vanish (phantom PR #1256 within ~60s), branch names wedge
(fix/d11-gov still refuses any PR), and its artifacts purge RETROACTIVELY
(~11 merged PRs 404; in-tree delivery rows are the surviving audit trail).
Decision 0011 (PR #1261, owner-reviewed): **hpo-author App authors**
(orchestrator-centralized minting, app_push.sh, PRs #1259/#1261/#1264/#1265/
#1268 are its first flights), **hpo-approver approves**, **verdicts/merges/
closes post as tvofi only**; app_approve requires every merge verdict to cite
an existing non-empty evidence dir naming the head SHA (#1233 closed on that
gate; the unprovable residual is accepted on the record). Retired account
makes no GitHub write even if support restores it; the ticket asks for the
purged PRs' conversations back.

Main went red for four push runs (INHERITED CLAIMS: a claim carried forward
by claim-untouched merges, made invisible by parse_claim_map's same-scenario
collapse) — repaired by #1253's claim rewrite, the v6.6.5 stamp (claims
emptied), and #1265's multi-value parse; the JS twin is #1266/#1268.

Process lessons recorded: an owner approval that landed at 20:18Z was merged
37 minutes later (20:18:54Z → 20:56:10Z; first misreported as hours) — poll review
state on every PR awaiting the owner; pushes
over ~1 MiB die chunked without http.postBuffer (#1267); a PR body figure
stale at a moved head is corrected by a head-unmoving body edit, then
pr-contract re-runs (#1264 round 2). Merged pull requests' worktrees now go
at the merge itself: the orchestrator's standing per-merge call is
`tools/audit/worktree_gc.sh <owner/repo>` (briefs/orchestrator.md section 11)
— API-verified merged branch or detached-at-merged-head only, `git worktree
lock` honoured, evidence*/ev-* moved to /tmp/hpo-ev before seat scratch goes —
and the trap that shaped its self-test: an early fixture bug (redirect
variables assigned but not exported, age-guard polarity inverted) made the
test's own sweep walk the REAL /tmp/hpo-orch and remove live seat
directories — this session's fixer worktree twice and fixer-history,
recoverable only because the branch was committed — so the sweep now carries
a null control refusing any mention of /tmp/hpo-orch, and an uncommitted
worktree is one `git commit` from unrecoverable.

## 2026-09-20/21 — the final wave: every D0 economics finding shipped, the CI pipeline fully self-driving

**Twenty-eight merges across the two sessions**, two releases (v6.6.6, v6.6.7), and the board now holds only
#201 (programme tracking). The economics programme is complete: #1210 (exact billed top-k), #1208
(polish-every-candidate under owner-directed budget raises: CPU floor 1482, work factor 1.80), #1207 (the
keep-gate at 2e-5, optimality re-recorded 0.999) — worst-cell gaps of 0.9-1.4% closed to 0.0000-0.0003%.

**The #996 fleet-variance saga, resolved by owner rulings:** the may-drift machinery now carries three
allow-sets (SENSITIVE 5, RUNNER_CONDITIONAL_1208 three, RUNNER_CONDITIONAL_1207 twelve), each entry with
removal conditions, each set pinned by entities set-equality (a further name is an unruled widening), judged
keys still failing. The stress coverage floor gained a ruling-cited override entry (may-only-lower, fail-safe
to the stricter literal, dropped by the next re-record) — the #387 literal untouched.

**The CI pipeline is fully self-driving:** the hpo-runs App (Actions-only, blast-radius-narrowed) approves
held runs in-CI; the approve race (#1283) is fixed by SHA-keyed polling; approve_held_runs.sh backs the
orchestrator; worktree_gc.sh (with its own honest post-merge blocked verdict and the #1289 repair) cleans
merged worktrees under the §11 protocol step. Two incidents recorded: the GC seat's early self-test swept
real seat dirs (guard now pinned), and #1287 merged before its review concluded (the verdict-gate lesson).

**Standing state for successors:** the identity model (hpo-author authors, hpo-approver approves, hpo-runs
approves runs, tvofi posts verdicts and merges); the §11 GC step is policy, the cron was stopped by the
owner 2026-09-20 — run `worktree_gc.sh --apply` after each merge; the cross-session coordination ledger
lives at /tmp/audit-5/COORDINATION.md (the audit-5 round's part-3 full gate has quiet windows by
agreement); the resume file carries the session-by-session state.
