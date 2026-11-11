# R9-I3 root cause: a governance check reads the fields its motivating defect varied, and nothing else

Seat: round-9 RCA, class I3 (N=7), beside F11.1; barrier for F11.3. Baseline `1936d5ca`; prototype on
`handoff/r9-rca-i3`, cut from `origin/main` `db878b29`. `.claude/` and `tools/` are byte-identical between
the two (`git diff --stat 1936d5ca db878b29 -- .claude/ tools/` prints nothing), so every run below
at `db878b29` is a run at the baseline for the files it reads. Evidence: `tools/audit/round9/rca/i3/` on
the branch.

## Root cause

### Cause

Every governance check in the class reads a strict subset of its input's fields: the ones the defect
that motivated it varied. The fields the policy asserts but no defect has varied yet are read by no
check, and each audit round finds one. The fix then adds that one field and nothing else.

Reproduced at the baseline, each by running the real check on a perturbed input
(`node .claude/workflows/field_coverage.mjs --ruleset-json ruleset-23698884.json`, output `fc-A.out`,
exit 1):

- **D11-s2-02.** `policy_lint.mjs --hooks` stays `HOOKS ok` with `PreToolUse[0].matcher` set to a
  value that matches no tool. Its own comment records the pattern: deleting an entry, then re-pointing
  `PreToolUse` at `session-start.sh`, each passed until a review found it (`#614 round 3`), and each fix
  added the one field.
- **D11-s2-01.** `checkBudgets` compares `r.lines > cap`. The row `sizes()` returns also carries
  `bytes`, and no per-file arm compares it. All 40 capped files (every `files{}` key except the fixture)
  grow in bytes at a constant line count with the per-file check green.
- **D11-s1-01.** The only reader of the live ruleset, `counts.mjs:liveRequiredContexts`, carries rule
  types and bypass modes "whether or not anything compares it yet" (its comment, added for #1192).
  `requiredContextsDrift` compares context names and ruleset ids and nothing else. Flipping
  `dismiss_stale_reviews_on_push` leaves `required-contexts` green.
- **D11-s1-02** (cited, `direct_push_detectors.py`, not re-run here). `stamp.py:rule4_problem` reads
  a first-parent commit's parent count and subject, never its file set: `nonstamp_direct_reported=0`
  of 2 injected. **D11-s1-03** (cited, `privileged_pr_code.py`). `codeowners_gap.py` counts a file as
  covered when it is owned *or* pinned, and never reads the job's `permissions:`. That is 3 jobs.

Not this cause: **D11-s1-04** (the approving review carries no field that separates the owner from an
agent driving the owner's token; it is an identity decision) and **D13-s1-03** (pr-contract is not
re-run when the reds it lists finish; that is a trigger, not an input field). Both stay F11.2's
instance fixes and tvofi's decisions.

**Class search beyond the sweep** (same run, `fc-A.out`). There are 26 blind fields, and the sweep
named 3 of them:

- `hooks.{SessionStart,PreToolUse,Stop}[0].hooks[0].type`: 3 new seams. `--hooks` never reads `type`,
  and the harness runs only a `command` hook as a script.
- The ruleset has 21 blind fields. Besides `dismiss_stale_reviews_on_push` there are
  `require_code_owner_review`, `required_approving_review_count`, `enforcement`, `target`,
  `conditions.ref_name.include/exclude`, `bypass_actors[0].actor_type/actor_id/bypass_mode`,
  `rules[pull_request].type`, `require_last_push_approval`, `required_reviewers`,
  `required_review_thread_resolution`, `require_extra_approval_for_unattributed_changes`,
  `allowed_merge_methods[*]`, `strict_required_status_checks_policy`, `do_not_enforce_on_create`, and a
  context's `integration_id`. So the whole owner-review boundary (`require_code_owner_review: false`,
  or `enforcement` off) can be turned off with the tree's only ruleset reader green.
- Across classes: D11-s1-02 (I3) and D13-s1-01 (I4) share one line of
  `policy_lint.mjs:enumerateMerges`, which skips "a commit with no entry is a stamp". Neither class's
  fix alone removes it.

### Process state: (c), and (d) for D11-s1-01 alone

The process is `defect-root-cause.md`: "Any countermeasure that is a check … is **demonstrated failing
on the defect it was written for, and passing once the defect is fixed.**" It was followed. The
`cmdHooks` comment records its "Nine ALLOW controls" and the refusals that caught the heredoc bug. The
`liveRequiredContexts` comment records #1192's byte-identical control. The budget comment records the
`if (false)` witnesses. It did not produce the intended result, because its unit is the defect: one
failing demonstration per motivating instance proves the check reads that instance's field, and says
nothing about the others. This is decision 0003's shape ("an enumeration of what you must catch cannot
be completed") applied to a check's read-set, which no process enumerates. A firmer instruction would
treat this (c) as (b).

D11-s1-01 is (d). Decision 0008 step 3(d) PUTs `"dismiss_stale_reviews_on_push": true` onto ruleset
22628467. Live today, 22628467 carries `['deletion', 'non_fast_forward']` only, `updated_at`
2026-09-19T14:34:49+02:00, 8 s after 23698884 `main-protect-checks` was created (14:34:41+02:00). The
`pull_request` rule moved into 23698884 with `false`. The fixture learned the move (`f4d071dd`,
2026-09-22), and it compares ruleset ids, not parameters. The barrier below is also (d)'s
countermeasure: the comparison notices its own precondition changing.

### Cost test

`cost(countermeasure, recurring) < cost(defect) × P(recurrence)`, wall-clock per audit round.

- **P(recurrence) is measured.** `tools/audit/bugclasses.json` I3 lists 18 instances over rounds 2 to 7.
  Round 8 has 5 (R8-I3's #1514, #1515, #1516 and #1547, plus #1548). Round 9 has 7. That is 30 in
  8 rounds, and 8 of 8 rounds hold at least one, so the mean is 3.75 per round.
- **Defect cost is measured on the fix side only; audit discovery is excluded, which is conservative.**
  From the first commit to the merge, #1558 (R8-I3, 4 issues) took 382 min (96 per issue) and #1567
  (#1548) took 310 min. That gives 96 to 310 min per instance.
- **Reach is 3 of 7 round-9 instances demonstrated** (s1-01, s2-01, s2-02). Two more can be reached by
  registration and are not demonstrated here. The prevented cost per round is therefore
  3.75 × 3/7 × 96..310 = **154..498 min**.
- **Standing cost is measured.** A full run is 17.5 s CPU (hooks 10.4, ruleset 7.0, budgets 0.14),
  with wall time of 29.0 + 20.8 + 0.4 s on this box at load1 20 to 28 on 4 vCPU. Each arm is a
  deterministic function of tree files plus the ruleset's key set, so the barrier runs when its inputs
  change, and nightly. `v6.5.0..1936d5ca` spans 11.5 days and rounds 8 and 9, so one round is
  about 150 merges and 5.75 days. In that span, 55 of 300 merges touch those inputs
  (`.claude/settings.json`, `.claude/hooks/`, `policy_lint.mjs`, `counts.mjs`,
  `required-contexts.json`, `policy_budgets.json`), so the cost per round is
  150 × 55/300 × k × 50 s + nightly 50 s × 5.75 days ≈ **23 min × k + 5 min**. Here k is CI runs per
  merge, which was not measured.
- **Verdict: it passes for k < 6.5 at the lower bound of defect cost, and k < 21 at the upper.** If
  every arm ran unscoped on every run, the cost would be about 125 min × k, which passes only for
  k < 1.2 at the lower bound. Scoping is therefore part of the barrier, not an optimisation.

### Barrier: field coverage of every governance check's input

`.claude/workflows/field_coverage.mjs` (287 lines, sha1 `6ecb86af67f8c73efc71287e32f37ddcc46ad051`)
enumerates every leaf of a registered check's input from the artifact itself. It perturbs each leaf to
a property-violating value and runs the real check. A leaf the check stays green on is **BLIND**
unless IGNORE names it with a reason. An IGNORE key that matches no leaf is **DEAD**. A healthy input
that is already red, a load failure, a skip or an error is **REFUSED**, never a detection. A field
GitHub or `settings.json` adds later is enumerated on the next run without anyone listing it; that is
decision 0003's bounded direction. The ruleset IGNORE list is the comparator's own `RULESET_VOLATILE`,
imported. It is not a second copy, which would be an I4 instance.

| run | tree | result |
|---|---|---|
| fail | `db878b29` = baseline for these files (`fc-A.out`) | exit 1, `blind=26` (hooks 4, ruleset 21, budgets `bytes` 40 of 40 files) |
| fail, D11-s1-01 | fixed tree, live ruleset as fetched (`fc-B.out`) | exit 1: the unperturbed ruleset is red, with the message "`rules[0].parameters.dismiss_stale_reviews_on_push` is false live, true recorded" |
| pass | fixed tree, live ruleset after the owner's setting (`fc-C.out`) | exit 0, `read=49 blind=0 dead=0 refused=0` |
| mutant | fixed tree with the matcher read deleted | exit 1, BLIND `hooks.PreToolUse[0].matcher` |
| null: healthy | fixed tree, real `settings.json`: `policy_lint.mjs --hooks` | `HOOKS ok: 3 wired hook(s)` |
| null: skip | no `--ruleset-json`, no `gh` | REFUSED `cannot load … spawnSync gh ENOENT`, exit 1 |
| null: dead | IGNORE entry `permissionz` added | DEAD, exit 1 |

"Fixed tree" is `fixed-demo.patch` on `db878b29`, and it is the instance fixes as a fixer would write
them:

- `cmdHooks` reads `type` and the PreToolUse `matcher` against Edit, Write, MultiEdit and NotebookEdit
  (the `policy_lint.mjs` +14 covers this and the budgets arm).
- `counts.mjs` returns the ruleset objects, exports `RULESET_VOLATILE` and `rulesetLeaves`, and
  `requiredContextsDrift` compares every non-volatile leaf against `ruleset_objects` in
  `required-contexts.json` (+34).
- The fixture records 23698884 as decision 0008 asserts it (+104 data).
- `checkBudgets` compares a per-file `files_tokens` cap. `policy_budgets.json` records
  `files_tokens` at measured (+44 data).

Structural ratchet: `python3 tests/structure.py` on the branch prints `STRUCTURE RATCHET PASSED`. The
ratchet measures `custom_components/` only, and nothing here touches it.

Residual, for tvofi: a **new** governance check is covered only once it is registered. Closing that
means deriving the registration set from `policy_lint.mjs`'s `CHECKS` table plus `codeowners_gap.py`
and `stamp.py` rule 4 (every entry registers its input or declares none). That is not built.

## Plan fold

- **Landing PR: F11.3, as planned.** It must follow F11.2, because the ruleset fixture records tvofi's
  D11-s1-01 decision, which F11.2 makes. It also needs **F11.1's hooks fix to read `type` as well as
  `matcher`** (the 3 new seams above). That is a carry into F11.1's brief, for the orchestrator to write.
- **Files beyond F11.3's list:**
  - `.claude/workflows/field_coverage.mjs` (new; a program in `.claude/workflows/`, so governance.yml's
    restore pins it; `codeowners_gap.py --check` must read it as pinned).
  - `.claude/workflows/counts.mjs` (pinned, not owned).
  - `.claude/workflows/fixtures/required-contexts.json`.
  - A run step in `.github/workflows/governance.yml` (**code-owned**), scoped to the inputs above, plus
    a nightly run.
  - `tests/entities.py`, which must classify the new file (closure or INERT) or it fails.
  - `policy_budgets.json` gains `files_tokens`. That is a new cap, not a raise, but F11.3's own note
    makes any budget change tvofi's before the push.
- **Deviations from the prototype the fixer owes:**
  - The ruleset arm's load failure prints the `required-contexts` `UNCHECKED this run, not confirmed`
    skip, and does not refuse: policy-docs is a required context and must not block on an API outage.
    The other arms still refuse on a skip.
  - Export `checkBudgets`, `sizes` and `policyBudgets` rather than the prototype's temp-module import.
- **Estimated lines** (prototype, measured with `wc`/numstat): barrier 287; instance fixes +62 code,
  +148 data; workflow step and entities classification not estimated.
- **No change to the PR set or `after` edges.**
- **Policy: none needed for the barrier.** An optional proposal addresses state (c) and is for tvofi,
  not landed: `defect-root-cause.md` "A detector must be shown to detect" would gain "a check over a
  structured input is registered in `field_coverage.mjs`".

## Figures

| figure | enumerator |
|---|---|
| blind=26, read=23, ignored=16 | `node .claude/workflows/field_coverage.mjs --ruleset-json tools/audit/round9/rca/i3/ruleset-23698884.json` at `db878b29` |
| read=49 blind=0 | same, with `fixed-demo.patch` applied and `ruleset-flipped.json` |
| 30 instances / 8 rounds | `bugclasses.json` `I3.instances` (18) + R8-I3 `issues` in `wave-r8-groups.json` (4) + #1548 + `CLASSES-DRAFT.json` I3 `n` (7) |
| 382 / 310 min | `git log` first own commit to merge commit, #1558 `e2e8c3bf`, #1567 `7af2a261` |
| 55 of 300 merges | `git rev-list --first-parent --merges v6.5.0..1936d5ca`, diff names matched against the input set above |
| i3_instance_seams=40 | `PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/I3/enumerate.py` at `1936d5ca` (sweep export `b2e3560671`) |
