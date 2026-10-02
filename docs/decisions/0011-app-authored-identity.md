# 0011 — Pull requests are authored by the `hpo-author` App; the retired account never writes again

Status: recorded 2026-09-19 from the repository owner's decision, #201
comment 5744682317. Amended by 0013 (2026-09-24): verdicts post as the
`hpo-approver` App, not `tvofi`. Amended by R9-F10.5 (last section): a
fourth App, the ledger writer, pushes nightly `killed_by` rows to `main`.

## Context

The author identity 0009 built the programme on — the seat user account
`tvofi-seat-author` — is spam-flagged by GitHub. Measured on 2026-09-18/19:

- its pull request **#1256** returned `201 Created` and then `404` within
  about sixty seconds, and the branch it pushed (`fix/d11-gov`) was left
  wedged;
- **about eleven of its merged pull requests now return 404 retroactively** —
  the conversations vanished after the merges, with no event to read;
- the in-tree `docs/delivery/` rows for those pull requests survive, which is
  how the purge is enumerable at all.

A second measured fact shapes the model beside it: **a verdict must never
post as an author App** (#1233's defect — GitHub refuses an author's approval
of their own pull request, so an author-App verdict cannot carry, and one
posted anywhere near that role blurs which identity owes the review). The
approver side of 0009 needs no repair: `hpo-approver` has approved pull
requests since 0009's step 6 landed.

## Decision

The owner's words, #201 comment 5744682317 — **the three-identity model**:

- **author** = the `hpo-author` App (orchestrator-centralized minting — seats
  stay LOCAL-ONLY, hand off, orchestrator pushes);
- **approver** = the `hpo-approver` App;
- **verdicts/merges/closes = `tvofi`.** (Verdicts: `hpo-approver` since 0013.)

Measured properties of the App this rests on: slug `hpo-author`, id `5003531`,
owner `tvofi`, installation `163073454`; the repository is readable through
its installation token, which carries `contents`, `pull_requests` and
`workflows` read & write. The tool is `tools/audit/app_push.sh` (branch
`fix/app-push-tool`): it runs `tools/audit/prepr.sh` on the body before
anything is minted (#678's ordering), pushes over https through a file-fed
credential helper so the token never sits on a command line, opens or re-bodies
the pull request as the App, and reads the body back byte-identical. Seats hold
no App credential: the id file and private key live with the orchestrator and
are never printed. `tools/audit/app_approve.sh`'s verdict allowlist narrows to
`tvofi` (the approver App since 0013) and requires a `merge` verdict to cite an evidence directory that
exists, is non-empty, and names the head SHA.

**The retired account makes no GitHub write.** Its writes can vanish (phantom)
and its artifacts purge retroactively, so nothing may depend on one landing.

## What does not change

0005/0009's machinery is untouched: the approving review is still required
before a merge, and the owner is still the sole code-owner reviewer — an App
cannot be a code owner (0009's amendment of 2026-09-16), so neither
`hpo-approver` nor `hpo-author` can satisfy an owner review.

## Consequences

- **Apps are never code owners**: only `@tvofi`'s approving review satisfies
  `require_code_owner_review` on an owned path, which `.github/CODEOWNERS` and
  its header now state outright.
- **The retired account stays retired even if support restores it.** The
  support ticket seeks restoration of the **purged pull-request
  conversations**, not the account's write role; no tool, brief or brief
  change re-grants it one.
- The reviewer seat hands verdict text to the orchestrator, who posts it as
  `tvofi` — as `hpo-approver` since 0013 (`tools/audit/briefs/fix-review.md`); the fixer hands the branch and
  body off locally (`tools/audit/briefs/fixer.md` step 5); every brief names
  the three-identity model (`tools/audit/briefs/orchestrator.md` section 5).
- `tools/audit/push.sh` remains in the tree for a seat that legitimately
  pushes with its own `GH_TOKEN`; it is no longer the fixer's path to a pull
  request.

## Amendment: the ledger-writer App (R9-F10.5)

The owner chose to build it (round-9 card C5, "Build"). The mutation ratchet's
pre-ratchet stock had no path to a disposition: `mutation-nightly` records
nothing and `--pin-killed` reaches only the sites a diff adds (R9 RCA I1,
residual (a)). `mutation-ledger` now drives a slice of that stock nightly and
`mutation-ledger-push` commits what it killed to `main`. That push needs an
identity, and none of the existing ones may carry it:

- **Not `hpo-author`**: it authors pull requests, and a direct push to `main`
  would give the author a path around review.
- **Not `hpo-approver`**: an approver that writes the tree it approves blurs
  the role #1233 separated.
- **Not `hpo-runs`**: it approves held Actions runs, and a write grant would
  widen an App every autofix job already mints.
- **Not `GITHUB_TOKEN`**: its pushes trigger no workflow, so the push to
  `main` would never run the forced `full` gate.

So the writer is a **fourth App, `hpo-ledger`**. What the workflow does with
it and what the credential itself can do are two different grants, and only
the second bounds a misuse; both are stated.

**What the workflow does** (`.github/workflows/tests.yml`, pinned in
`tests/entities.py`):

- **Reach**: `mutation-ledger` and `mutation-ledger-push` run only when
  `github.ref` is `refs/heads/main`, on `schedule` or a non-recheck
  `workflow_dispatch`. A dispatch on any other ref would drive that ref's tree
  and kill rule and push the kills to `main` (#1848 review, B1).
- **Write set**: new files under `tests/mutation_ledger/killed_by/` and
  nothing else, checked twice before the push: on the working tree
  (`mutation_table.drain_write_set_problems`) and on the commits sent
  (`mutation_table.drain_push_problems`: exactly one commit, on `main`'s tip,
  under the subject below, adding rows only). A survivor is never written
  (`ci-autofix.md`).
- **Subject**: `ci: record nightly kills` (`mutation_table.DRAIN_SUBJECT`),
  the `ci:` prefix every bot commit carries. The measuring job runs on
  `schedule` and `workflow_dispatch` alone, so a push of rows cannot start
  another drain: the loop guard is the trigger, not the subject.
- **Target**: `main` only, fast-forward, never forced; a refused push is a
  red job, not a retry loop (three tries against a moving `main`, then red).
- **Token**: minted with `contents: write` alone, masked before it is written
  to a step output; the measuring job holds no secret and no write grant
  (D11-s1-03).

**What the credential can do**, which is what a leaked secret or a workflow
edit would get:

- `HPO_LEDGER_PEM` and `HPO_LEDGER_APPID` mint an installation token with the
  App's full installation grant, `contents` read & write on this repository,
  for any path and any branch. Nothing in the App narrows it to the rows.
- Who can read the secrets is set by where they are stored, not by the YAML.
  A **repository** secret is handed to every same-repository workflow run, on
  any branch, so any branch -- including one `hpo-author` pushes -- could
  mint the token; that is the path around review this amendment refuses
  `hpo-author`. The push job therefore declares `environment: ledger`, and
  the secrets must live **only** in that environment, whose deployment
  branches are `main` alone. GitHub still hands repository-level secrets to an
  environment job, so the code cannot tell the two scopes apart: only
  deleting the repository-level copies confines the credential. Until then
  the push job still works, bounded by the `refs/heads/main` guard alone,
  and any branch's workflow can read the secrets. After it, a job with no
  credential from the environment is red (`skip-no-writer` is outside
  `DRAIN_QUIET`), never green.
- The App's bypass on `main-protect-checks` (23698884) lets its push skip the
  required checks and the pull-request rule, which is what a direct row
  commit needs. Its `always` bypass on `main-protect` (22628467) grants
  something else: that ruleset holds only the `deletion` and
  `non_fast_forward` rules, which a fast-forward push never meets, so that
  entry lets the credential **force-push or delete `main`** and buys this
  workflow nothing. It should be removed unless a reason is recorded here.

**The owner's setup, not any seat's.** Done by the owner on 2026-10-02:
`hpo-ledger` is App 5094721, installed, an `always` bypass actor on both
rulesets (22628467, where it already stood on 2026-09-30, `docs/HANDOVER.md`;
and 23698884, recorded in `.claude/workflows/fixtures/required-contexts.json`),
with `HPO_LEDGER_APPID` and `HPO_LEDGER_PEM` set as repository secrets. Owed
by the owner (#1848): create the `ledger` environment with deployment branches
restricted to `main`, store the two secrets there, delete the repository-level
copies, and decide on the 22628467 bypass (the recommendation above is to
remove it). A ruleset read cannot prove the 23698884 bypass admits the push
(the rules endpoint is not bypass-aware), so the first nightly
`ci: record nightly kills` push is its live test.

The App is no code owner (above), and a row it writes merges no policy: the
ledger rows are dispositions the ratchet reads, not caps
(`budget-raise-gate` grades `tests/mutation_budgets.json`, which the write set
excludes).
