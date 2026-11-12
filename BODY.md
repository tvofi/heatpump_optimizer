R10-OUTSIDE-CONTRIBUTOR-CYCLE, part 1 of 2: an allowlisted outside contributor's fork pull request is adopted on our machine from main's copy of the contract. Built to the design note at `design/R10-OUTSIDE-CONTRIBUTOR-CYCLE` 142e70df1b77cf9e7f63d6675b9ad560941e20c9 and its approval at `design-verdict/R10-OUTSIDE-CONTRIBUTOR-CYCLE` fb36c832b6eeb3307bb07502d9a2529b36474535. No finder harness: owner report (tvofi, 2026-11-12, triage batch 238, entry P714). `tools/audit/seat/merge_train.py`, `remerge_main.sh` and `merge_pr.sh` are part 2's and are not edited.

**Three things a reader must know first.**

1. **This pull request raises one budget, and the owner has not confirmed it in person.** `files_tokens` for `dev/governance/roles/fix-review.md`, see `## Raise justification`. It rests on `CLAUDE.md` rule 2's mandate exception and merges only if `budget-raise-gate` admits it.
2. **Three checks the design owes were not run, because this seat holds no owner credential and no test fork:** the two live checks (design items 8 and 20) and the account behind `secrets.CLOSURES_PUSH_TOKEN` (design item 19). Decision 0017 lists them under "Before the first allowlist entry" and the allowlist's own comment points there. Class O's condition 3 is written to both answers GitHub can give and to the intermediate-commit case (verdict item 25), so no answer of the live check changes the code; which answer GitHub gives is not recorded here.
3. **The mechanism is inert at merge:** the allowlist merges empty and the owner adds the entry after part 2.

What was built, by file:

- `tools/pr/outside.py` (new): admission, the three path classes with default deny, the manifest version, class O in both forms, and `approve`, the one writer of the mandated class-O approval.
- `dev/governance/config/outside_contributors.json` (new, empty) and two `.github/CODEOWNERS` lines (the allowlist, `outside.py`).
- `tools/audit/seat/bus.sh`: `adopt <pr> <comment id>`.
- `tools/pr/app_approve.sh`, `carry` only: a head that is no branch tip of origin carries only the automatic merge of main; verdict item 21's merge arm. `--carry` now asks origin for its branch heads whenever the range holds a commit, so a carry test of a local head never pushed refuses every non-merge commit in it; the instrument guide says so.
- `tools/policy/policy_lint.mjs`: `--outside-author` (adoption's form), `--outside-pull` with `--outside-ref` (pr-contract's, spawning `outside.py`).
- `.github/workflows/pr-contract.yml`: the pulls answer saved to a file and two arguments on the `policy_lint.mjs` line. `.github/workflows/tests.yml`: the head ref name through `env:` and the same-repository conjunct on the `laneskip` step (verdict item 22). `.github/workflows/governance.yml` and `tools/ci/selftest_closures.json`: the `outside-contract` self-test step, measured.
- `tools/pr/ci_predict.py`: the predictor's tree holds the round roster refs (part 2's carry 5, below).
- Decision 0017, `docs/CONTRIBUTING.md`, two paragraphs in `dev/governance/roles/fix-review.md`, the instrument guides.

**Departures from the note, each raised here for the reviewer rather than made silently:**

- **Main's copy is a throwaway worktree of the fetched main commit, not six `git show` files.** `policy_lint.mjs --pr-body` and `carry_audit.py` import siblings and read the tree, so single files do not run. `adopt` then re-runs main's own `bus.sh` (`adopt-from-main`), which refuses unless its tree is the commit just fetched: the adoption logic itself, and every `push-verdict` gate, is main's too. The data (allowlist, CODEOWNERS) is still read with `git show <main sha>:<path>`.
- **Class R is tested before class F.** The note's table lists F first. The self-test holds, over the tracked tree, that no R path lies under an F rule, so no answer differs today and a later R rule cannot be shadowed.
- **pr-contract gets no new step: `policy_lint.mjs --pr-body` spawns the pinned `outside.py` itself** (`--outside-pull`, `--outside-ref`), over the pulls API's answer saved as a file, with no token and no API call. The note asked for four values through `env:` and one flag; this passes the whole answer as a file, so no contributor-named value reaches a shell either. Two earlier cuts were refused by the tree's own checks and are why: a step holding the job's token (`tests/entities.py`: "every pinned grader given a token runs its own copy under the Actions token on the pull request"), then a tokenless step whose shell broke `codeowners_gap.py`'s proof that the job runs `policy_lint.mjs` pinned (nine files read uncovered; back to zero now). Consequence, stated: the early signal reads neither the reviews (class O prints `PENDING:`) nor the other pull requests at the head, and reads `GATE_FILES` from the head's `tests/closure.py`, which pr-contract does not restore; adoption reads all three from main.
- **The allowlist is `dev/governance/config/outside_contributors.json`, one directory below the path the note and the dispatch name.** `tests/layout.json` places a governance data file under `config/` and refuses one beside it, and `policy_lint.mjs` already excludes that directory's JSON from the prose corpus, so the base's copy of the linter accepts the file with no edit.
- **The pull request's author and the verdict comment's author must be the SAME allowlist entry.** The note says "match one entry"; the stricter reading is taken.
- **fix-review.md gains two paragraphs, not a headed section:** the file sits at its line cap.
- **`adopt` reads the body lint and carry audit through `HPO_BUS_BODYLINT` and `HPO_BUS_CARRYAUDIT` in the self-test,** the file's existing stub convention (`HPO_BUS_CLASSIFY`, `HPO_BUS_PACKER`). The self-test therefore proves they are called and that a refusal refuses, not that main's real `policy_lint.mjs` passes a real body from a worktree.

Carries answered (design note items, then verdict items):

- 1, 10: the allowlist id is data; the head ref name is matched with `re.fullmatch` and reaches no shell string. 2: the review commit is read with `ls-tree` and `cat-file` only. 5, 6: `setpr` pushes a branch ref; `ls-remote` goes through `retry_with` and an unreadable one refuses. 7: `check --comment` refuses a comment that is not an issue comment of that pull request. 9: `checkPrBody` reads commits only in its Dependabot branch; the flag changes the author arm alone, and the in-file test compares the refusal count of another fixture with and without it. 12, 13: decision 0017 corrects 0011's citation and states three autofix jobs. 14: `approve` writes "mandate comment <id>" and the self-test proves `MANDATE_CITE` reads exactly that id. 15: the review list is read with `--paginate --slurp` and a non-list refuses. 17: the gate module is the running tree's (main's at adoption), loaded by path. 18, 27: fix-review.md's second paragraph.
- Round-2 verdict 14, 15: `adopt` runs main's `policy_lint.mjs --pr-body` and `carry_audit.py` over the live body, fetches main itself, and `check` refuses a base that is not `main` of ours. 16, 26: `check` refuses another pull request of any state at the head (the commit's associated pulls, and the head branch's pulls with `state=all`). 17: a manifest `version` diff refuses; the `docs/img/` scripts class O. 18, 19: latest decisive review; a review at L is accepted when L carries to the head.
- Verdict 21, 22, 24, 25, 28, 29: built, each with a self-test case named under `## Mutation proof`.
- Not this part's: 11, 16 (design), 23 (verdict). Part 2 imports `outside.py` by path; if that moves the recorded closure of the train's self-test, the verdict's Build parts already give part 2 the re-record.

## Carries received from part 2

Part 2 (`r10-outside-contributor-cycle-p2`) was built before this part published anything and left seven carries on this group's roster entry. Each, by its index there:

- Carry 0 (item d4703cd1, the interface to this module): built. What part 2 reconciles `Train.fork_head`, `Train.outside_contract` and merge_pr.sh's `head_is_ours` to, in `tools/pr/outside.py`: `pull_facts(repo, pr)` reads the pull request; `cross_repository(facts, repo)` is the one definition of a cross-repository head; `check(repo, pr, ref)` returns `(rc, lines)` with rc 0 admitted, 1 refused, 3 not an outside pull request, and is the whole contract with class O (verdict item 23's call at the landing head); `Rules(ref).classify(path, pr)` answers F, R or O; a shell caller runs `outside.py cross --repo O/R --pr N` (rc 0 cross-repository, 3 ours, 1 unread). Every read that fails raises `Refuse` or answers rc 1, never a default.
- Carry 1 (item 8da136bb, the self-test closure re-record): not this head's. This part records `outside-contract` and re-records `verdict-bus` and `app-approval`; at this head the train does not import `outside.py`, so its two steps cannot be traced reading it. Part 2 re-records them once this is on main, as the design verdict's Build parts say.
- Carry 2 (item 53108d53, the live checks): built as a written precondition. Decision 0017, "Before the first allowlist entry", lists the fork-head merge and its identity, the end-to-end approval of an adopted verdict, and the `commit_id` read; none was run by either part.
- Carry 3 (item aa80140a, the guides and decision 0017): built in part. Carry 29's sentence is in decision 0017 and in the guides of `outside.py` and `app_approve.sh`; decision 0017 point 7 says the train merges main into the fork branch itself or parks naming the fork. Not written here: remerge_main.sh's head-repository flag and the train's outside block class. Neither exists at this head, and a guide naming a flag the tree does not hold is a false claim; they go into those two instruments' guide pages with the code, in part 2's pull request.
- Carry 4 (item f7754778, the train's approval body under a bare mandate id): not this part's change. `tools/audit/seat/merge_train.py` is not this part's to edit; `outside.py approve` writes "mandate comment <id>" and its self-test proves `MANDATE_CITE` reads exactly that id, and its case "class O REFUSE: _agent_approval_body under a bare mandate id" is the control that the train's body cites nothing. Whether our own heads' approvals should cite "mandate comment <id>" goes to the live group owning that file's seam. Carry: R10-GATE-DEFER-BARRIER
- Carry 5 (item cc5c19fe, the predictor's missing roster fetch): built here, because the audit leaves a finding with no live owner to its producing group. Confirmed first: this seat's `prepr.sh` at b521aec6dcdf printed the same `CI PREDICT: 1 predicted red(s) on pr-contract` for four carries to this group that the same run's own carry step routed. `tools/pr/ci_predict.py`'s `ci_tree_run` now gives its clone each round roster ref the checkout has fetched (`round_roster_refs`), as `pr-contract.yml`'s fetch gives the job.
- Carry 6 (item 3518898b, the dispatch gave no interface): answered by Carry 0.

## Head

`8e6e94427f86b0c15ecdbbe1ed639acc716737ee`

Merge base with `origin/main`: fc2a7edcf2be8847037d9e8dc5bde460977befa8.

## Mutation proof

Each mutant was applied to the production line, the self-test run, and the file restored.

`tools/pr/app_approve.sh --self-test`:

- the branch-tip test (`|| ours=0` to `|| ours=1`): "NO CARRY on a fork head: a closures bot commit", and the ledger, empty-own, empty-`ci:` and delivery-row arms.
- the non-merge refusal (`elif [ "$ours" = 0 ]` to `elif false`): the same five arms.
- item 21's comparison (`git diff --quiet "$ms" "$c" -- "$p"` to `true`): "NO CARRY on a fork head: a main merge whose merge-driver file is not main's".
- the no-main-side refusal (to `ms=$2`): "NO CARRY on a fork head: a merge that is not of main, though it adds no commit".
- the `ls-remote` refusal (`|| true ||`): "NO CARRY: origin's branch heads unreadable, even for an automatic merge of main (fail closed)".
- Failing first: the base's `carry` under this head's self-test fails 20 checks, the fork-head arms above and "REFUSE: the same head when it is only refs/pull/7/head (a fork's)".

`tools/audit/seat/bus.sh --self-test`, mutated in place (the fixture's main is a copy of this tree's `tools/`):

- the fetch (to a ref of the seat's stale HEAD): "adopt: an allowlisted contributor's merge verdict on a class-F head is proposed on review/7".
- main's copy (run `$0` and drop the own-tree check): "adopt refuses by MAIN's copy of outside.py, not this checkout's (which admits)"; the own-tree check alone: "adopt-from-main refuses to run from a tree that is not the main it was handed".
- the head comparison: "adopt refuses a verdict naming a commit that is not the live head"; the first-line comparison: "adopt refuses a VERDICT.md whose first line is not the comment's".
- the `outside.py` gate: every "class-R path" arm; the body lint: "adopt refuses a body main's policy_lint refuses"; the plumbing filter: "adopt refuses a review commit holding a file beside VERDICT.md and ev/".
- the three-dot range in `outside.py` (`{base}...{head}` to `{ref}..{head}`): the success case, because the fixture's main moves on in `tools/` after the fork point.

`tools/policy/policy_lint.mjs --self-test`: admitting on exit 1, staying silent on exit 2, and spawning for a Dependabot author each print a `FIXTURE VACUOUS: outsideAdmission ...` line; dropping `author === outsideAuthor` prints "the author check passed an outside login with no flag, another login under the flag, or an empty one"; dropping the whole conjunct prints "the author check fired on an admitted outside author under its own flag".

`tools/pr/ci_predict.py --self-test`: deleting the `update-ref` loop in `ci_tree_run` fails "the predictor's tree holds the round roster ref this checkout fetched (CI fetches it before the carry check)"; dropping the `ROSTER_REF.fullmatch` filter fails "and no other handoff ref (null control)".

`tools/pr/outside.py --self-test`, failing first: at the base's `tests.yml` it fails "no workflow expands a contributor-named value (head ref, title, body) inside a run: block" (naming line 1807) and "tests.yml's laneskip step carries the same-repository conjunct". **Not done by hand for `outside.py`'s own predicates:** the note's mutation targets there (the id comparison, each of conditions 1 to 4, each conjunct of the machinery's form, the covering constant, the instant of the mandate) each have a refusing case and a null control in the self-test. `prepr.sh`'s mutant draw over that self-test at e216e6c09878 reported no survivor among the diff's first 40 mutants, after its first draw's eleven survivors in the git and `gh` plumbing were each given a killing check over a throwaway repository; the final draw at this head is under `## Unpinned sites`.

## Null control

- Admission: with the allowlist entry removed, the admitted pull request answers rc 3, not outside.
- Class O, the machinery's form: the admitted body with the mandate comment removed (404) refuses; a revocation by another account revokes nothing and stays admitted.
- Class O, latest against any: an approval after the owner's change request stands; a later COMMENTED review and the contributor's own change request void nothing.
- `carry`: every arm that refuses on a fork head carries on the same head pushed as a branch of origin; the automatic merge of main carries both ways.
- `adopt`: the head that the refusing-main case refuses is the head the success case adopts.
- The flag: the App (both spellings) and an absent author stay silent, as before.

## Figures

- app_approve self-test summary line: `bash tools/pr/app_approve.sh --self-test`
- bus self-test summary line: `bash tools/audit/seat/bus.sh --self-test`
- outside self-test summary line: `python3 -I tools/pr/outside.py --self-test`
- policy cap table, the row for fix-review.md: `node tools/policy/policy_lint.mjs --budgets`
- architecture score against the merge base: `python3 tools/audit/archscore/score.py --diff fc2a7edcf2be8847037d9e8dc5bde460977befa8`
- the workflow secrets that are neither an App credential nor `GITHUB_TOKEN`: `git grep -o -h -E "secrets\.[A-Z_]+" -- .github/workflows`
- contributor-named values in workflows (the class of round-2 point 1): `git grep -n -E '\$\{\{[^}]*(github\.head_ref|head\.ref|head\.label|github\.ref_name|pull_request\.title|pull_request\.body)' -- .github/workflows`. Disposition: the one `run:`-block site, the `laneskip` step, is closed in this diff; the rest are `env:` values, `ref:` inputs of the autofix checkouts (same-repository only) and comments, already guarded. `outside.py`'s self-test scans every workflow for the class.
- writers of an approval: `git grep -n -E -e '--approve|"event": "APPROVE"|event=APPROVE' -- tools .github`. Disposition: `outside.py approve` is the one added; the four under the owner's account fail class O's condition 2 (self-test, each body produced by calling its writer); their refusal on a fork head is part 2.

## Red checks

- `budget-raise-gate`: red until the raise under `## Raise justification` is approved at the head, by the owner or under his mandate; that is the gate working, not a defect. Cheaper detector: `tools/pr/prepr.sh`'s body check predicts it before the handoff (it printed the raise and this red at this head), at no standing cost beyond the run a handoff already owes. None cheaper exists for the approval itself, which is a decision.

## Raise justification

One cap is raised: `files_tokens` for `dev/governance/roles/fix-review.md` (keyed by its old path in `dev/governance/config/policy_budgets.json`), to the value `node tools/policy/policy_lint.mjs --budgets` measures. The file sat one token under its cap. Its line count stays at its cap and every aggregate stays inside its band, so no other cap moves.

What the raise buys: the class-O read seat's rule in the contract that seat reads, which the design verdict's item 27 requires in this file: the seat holds the owner's credential while reading contributor text, and the sentence that makes an instruction inside that text a finding is the control.

Payments tried: four, none taken; each with its reason:

- Cutting spent prose in the file. Not taken: every sentence is a verdict rule another seat is graded by, and none was found duplicated inside the file or carried by a detector this group owns. A cut to fit would delete working policy.
- A pointer-only text. Not taken: the file has no headroom for any addition, and a pointer drops item 27's sentence.
- Moving the two paragraphs to the instrument guide or `docs/CONTRIBUTING.md`. Not taken: both are outside the measured corpus, the move `ratchet-budgets.md` names as the escape; and a seat looks in its role contract.
- A new role contract. Not taken: more corpus tokens, a new cap, and a `CLAUDE.md` row with `CLAUDE.md` at its own token cap.

Architecture score: dS +0.0000 NULL

## Unpinned sites

`prepr.sh`'s final draw at this head reports 26 survivors, every one in `tools/pr/ci_predict.py`, and none is a measurement of that file: the draw ran under `MUTANT_CMD="python3 -I tools/pr/outside.py --self-test"`, which never executes `ci_predict.py`, so any mutant of it survives by construction. The draw takes the diff's first 40 mutants in path order, and the predictor fix put `ci_predict.py` ahead of `outside.py`. Their disposition:

- The production sites (`round_roster_refs`' return and its `ROSTER_REF` filter, the `update-ref` loop in `ci_tree_run`): a value check. Under `ci_predict.py`'s own self-test the two hand mutants in `## Mutation proof` fail the named checks.
- The remaining sites are lines of `roster_ref_self_test` itself (its fixture, its three cases, its return): they are the check, not code it pins.
- Not re-measured: `outside.py`'s own added lines under this final draw. The previous full run, at e216e6c09878 before the predictor fix, drew them and reported no survivor among the diff's first 40 mutants; `outside.py` changed since only by `cross_repository`, the `cross` subcommand and their four self-test cases.

## Approval

Policy in this diff: decision 0017, `dev/governance/roles/fix-review.md`, `dev/governance/config/outside_contributors.json`, `dev/governance/config/policy_budgets.json`. Code-owned: `.github/workflows/`, `.github/CODEOWNERS`, `tools/ci/selftest_closures.json`. They merge on the owner's approving review at the head, which under the owner's ruling of 2026-11-12 quoted in the design note ("a mandate made by me is valid for my machinery") may be the programme's mandate approval. Decision 0017 records three owner defaults; his approval of this pull request is his ruling on each: `docs/index.html` and `docs/site/` are class O with docs images class F; the covering mandate scope is `all`; the four further features are not built.

## Forward-carry

- The live check of design items 8 and 20 was not run: it needs the owner's credential and a fork, which this seat does not hold. Lands in `dev/governance/decisions/0017-outside-contributors-are-adopted-on-our-machine.md`, section "Before the first allowlist entry", and in the `_comment` of `dev/governance/config/outside_contributors.json`, the two places an owner adding the first entry reads. Carry: dismissed: built in this diff as a written precondition on the first allowlist entry, not left to a later stage
- Design item 19, the account `secrets.CLOSURES_PUSH_TOKEN` authenticates, cannot be read from the tree; what the tree shows (the three autofix jobs on same-repository heads, `merge-main.yml` on main, the reusable Tests call where GitHub withholds secrets from a fork run) lands in the same section of decision 0017, with the owner naming the account. Carry: dismissed: built in this diff as a written precondition on the first allowlist entry, not left to a later stage

## Friction

- defect-root-cause: cost: `tools/pr/app_approve.sh` and `tools/pr/outside.py` each hold a CODEOWNERS matcher (the first inline Python inside shell, which nothing can import), beside the ones in `dependabot_merge.py` and `budget_raise_gate.py`; a shared reader would be one concept in one place. Carry: dismissed: outside this group's seam; the existing readers refuse non-anchored patterns or live inside a shell heredoc, and folding them is its own change
- gate-scoping: cost: the frugal routing guard of this seat's harness refuses a sixth inline read per prompt, so every code read for this build went through a subagent and its report. Carry: dismissed: a harness setting of the dispatching session, not a repository rule
