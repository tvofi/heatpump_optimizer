# 0013 — Fix-review verdicts post as the `hpo-approver` App; policy and budget files are the owner's, and graders run from the base

Status: recorded 2026-09-24 from the repository owner's ruling of that date,
given by `tvofi` to the orchestrator and relayed in this record's dispatch.
Amends 0011's three-identity model in one role; 0011 stands otherwise.

## Context

0011 made verdicts, merges and closes `tvofi`'s: the reviewer seat hands its
verdict text to the orchestrator, who posts it as `tvofi`, and
`tools/audit/app_approve.sh` approves only on a `Fix review: merge <sha>` from
that login. So the owner's account carried two voices — its own approving
review on a code-owned path, and every seat's verdict on every other one —
and a reader could not tell from the login which it was.

## Decision

The owner's ruling of 2026-09-24, in two parts:

1. **Review verdicts and approvals come from the approver identity, the
   `hpo-approver` App, not from `tvofi`.** The orchestrator still holds the
   credential — seats stay LOCAL-ONLY (0011) — and posts the reviewer seat's
   verdict with `tools/audit/app_comment.sh`, which reads it back
   byte-identical through `.claude/workflows/gh_comment.py verify` and
   refuses a post that lands as anyone but `hpo-approver[bot]`.
   `app_approve.sh`'s allowlist becomes that App alone.
2. **Only policy and budget files belong to the code owner `tvofi`.** The
   ratchet caps (`*_budgets.json`, named one by one) join the policy set in
   `.github/CODEOWNERS`.

What stays from 0011:

- **A verdict never posts as the author App** (#1233's defect: GitHub refuses
  an author's approval of its own pull request, and an author-App verdict
  blurs which identity owes the review). `app_comment.sh` reads only the
  approver's key files; both scripts' self-tests refuse the author App.
- **Merges and closes stay `tvofi`'s.** The ruling names verdicts and
  approvals only, and nothing in the record moves the merge: the
  orchestrator merges with `--match-head-commit` as `tvofi` (orchestrator.md
  section 11), and the approver App is not on the ruleset's bypass list.
- The owner's approving review is still the only one that satisfies
  `require_code_owner_review`; an App cannot be a code owner.

Measured, 2026-09-24: the App's login is `hpo-approver[bot]`, type `Bot`,
id `330097732` (`GET /users/hpo-approver%5Bbot%5D`); its ten reviews on
#1489-#1557 all carry `author_association` `NONE`. So the old allowlist's
association guard (OWNER, MEMBER or COLLABORATOR) would refuse every App
verdict; `app_approve.sh` pins the login, the `Bot` type and the numeric id
instead, which no user account can hold.

## The enforcement surface: pinned where a pin holds, owned where it cannot

Part 2 read literally drops `@tvofi` from the required-check enforcement
surface (#1402, #1515, #1558). The owner's further words that day, relayed to
this record's seat: "I want CI changes to be able to be done without human
approval", beside the earlier "Don't reopen the 1558 CI trust holes." Owning
the surface was #1558's barrier against a pull request grading itself, so a
file leaves it only where a mechanical barrier replaces it:

- **Pinned, so the owner can go** (in a second pull request; see below): the
  governance instruments — `.claude/workflows/*.mjs`, `gh_comment.py`,
  `vendor/`, `tools/audit/*.sh`, `tools/audit/record-predicate/` and
  `codeowners_gap.py`. Every job a pull request reaches that grades with them
  (`pr-contract`, `policy-docs`, `env-matrix`, `wave-script`, `briefs`)
  restores the base commit's copies as its first step after checkout, and
  runs no unowned program of the pull request's before its graders — a step
  running the pull request's code can write `$GITHUB_ENV` (`BASH_ENV`,
  `NODE_OPTIONS`) and so reach every later step of its job. The self-tests
  that used to precede the restore moved to `instrument-self-tests`, a job
  that grades nothing. `codeowners_gap.py --check` now counts a surface file
  covered when it is owned or pinned in every such job, `.py` under
  `python3 -I`.
- **Kept owned, and why:**
  - `.github/workflows/`. A `pull_request` run uses the pull request's own
    workflow file, so an edit changes its own grading. `pull_request_target`
    runs the base's file, but the test jobs execute the pull request's code,
    which there shares the base's cache scope (the documented pwn-request
    shape); and a pull request can add a workflow that reports a
    required context's name, whose effect on the ruleset's verdict this
    record's seat could not measure without a live write. A barrier that
    could hold is a base-pinned guard whose context the ruleset requires
    from one App's `integration_id` — a ruleset change and a secret, both
    the owner's.
  - The test harness (`tests/run.sh`, `harness.py`, `closure.py` and the rest
    of the `tests/` block): the suite must run the pull request's code, so a
    base checkout cannot apply (#1515's root cause).
  - `web-fix-wave.js`, `audit-find.js`, `audit-verify.js`: graded artifacts
    that a grader evaluates in its own process.
  - `.claude/hooks/` and `.claude/settings.json`: no job grades them.

**Bootstrapping.** `policy-docs` runs the base's `codeowners_gap.py --check`,
which on this record's base still demands an owner for every surface file, so
the owner lines leave in a second pull request once this one is on `main`.
Measured over the 55 first-parent merges since 2026-09-20 whose base carried
the surface block, 17 were owner-reviewed only because of it; under the
second pull request's CODEOWNERS, 6 of those 17 would touch no owned path.

## Consequences

- The reviewer seat hands verdict text to the orchestrator, who posts it
  with `tools/audit/app_comment.sh` (`fix-review.md`); `orchestrator.md`
  section 5's identity line names the App for verdicts.
- `app_approve.sh` refuses a `tvofi` verdict. A pull request whose only
  verdict is `tvofi`'s is re-verdicted by re-posting the same text through
  `app_comment.sh`; nothing else changes about it.
- A path not in the web session's reach: `.claude/workflows/web-fix-wave.js`
  has the reviewer post its own verdict through the MCP identity, which is
  not the App, so such a verdict is re-posted the same way before approval.
- Owning the budget files puts the owner's review on every pull request that
  re-records one — including `tests/mutation_budgets.json`'s line pins after
  a line shift. Measured over the 105 first-parent merges since 2026-09-20,
  13 touched a budget file and no owned path.
- An instrument's own self-test now fails a non-required job; `pr-contract`
  still makes the body answer that red, so it is not silent, but it no
  longer blocks a merge by itself.
- `docs/decisions/` is `@tvofi`'s; this record needs the owner's approving
  review before it merges.

## Amendment, 2026-09-24: the test-side graders are pinned too

The owner's direction of 2026-09-24, answering whether the check scripts
should stay code-owned: "I want fully autonomous". The bullet above that kept
"the rest of the `tests/` block" owned is narrowed to the files where a pin
cannot hold. The rule is unchanged: a file leaves the owner only where a base
restore replaces the owner as the barrier.

**When a pin holds.** Only when no step of the job runs a program the pull
request carries before the grader starts. After one, the job belongs to the
pull request. That program can overwrite the restored file. It can set
`BASH_ENV`, `LD_PRELOAD` or `PATH` for every later step through
`$GITHUB_ENV`. It can use the runner's passwordless sudo to replace `git` or
`python3`. So no restore that comes after it can be trusted, however close it
sits to the grader. An install counts as such a program: it runs build code
that the pull request's lock chooses, and it drops `.pth` files. Round 1 of
#1589's review showed the ordering break in `coverage`: the suite overwrote
the restored ratchet before the ratchet ran. `codeowners_gap.py --check` now
refuses any grader that runs after such a step, in the same job.

- **Pinned, so the owner goes:**
  - `tests/coverage_ratchet.py` runs in `coverage-ratchet`, a job of its own
    that grades the JSON `coverage` measured.
  - `tests/nightly_status.py` runs in `nightly-status`.
  - `tests/delivery_status.py` runs in `delivery-status`.

  Each imports only the standard library. The step that runs it first
  restores it from the base, then checks it byte-identical to the base's
  object, then runs it under `-I -S`, so no `.pth` file and no sibling module
  loads. The pull request's own copy runs in `graders-head-copy`, which is
  not required. It runs only when the diff touches that grader, and its red
  still blocks the merge.
- **No pull-request job runs them:** `tests/nightly_ha.py` and
  `tests/replay.py` run on the schedule only, so they grade no pull request
  and carry no owner. `codeowners_gap.py` tags them `NO-PR-JOB`.
- **Kept owned, and why, file by file:**
  - `tests/mutation_table.py` and `tests/typing_ruler.py`. Their jobs install
    the pull request's requirement locks before the grader runs, and
    `mutation_table.py` runs the pull request's tests itself.
  - The suite: `tests/run.sh`, `env_drift.py`, `golden.py`, `harness.py`,
    `profiles.py`, `stress.py`, `plan_view.py` and `card_browser.mjs`. `fast`
    and `browser` must run the pull request's code, and a test that changes
    with the behaviour it pins would be refused by the base's copy.
  - `tests/closure.py` and `tests/derive_closures.sh`. Their INERT,
    NOT_A_TEST and lane rosters are edited by the same pull request that adds
    a test script or makes a test read a new file. The base's copy refuses
    that pull request (`closure.py check`: "selectable script(s) with NO
    recording").
- **What a pin does not reach:**
  - A pinned grader reads what the pull request's code produced: the
    coverage JSON, and the tree it reports on. A suite that misreports is
    left to review.
  - The base is `pull_request.base.sha`, the base branch's tip when the
    event fired. A stricter grader that lands on `main` afterwards reaches
    an open pull request only when that request is re-run against the newer
    base.
  - A change that must move a pinned grader and its caller together lands in
    two pull requests, the grader's tolerant form first.
