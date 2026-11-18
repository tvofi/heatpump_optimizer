# Contributing from a fork

Pull requests in this repository are normally written, reviewed and merged by
the project's own tooling. A contributor the owner has added to the allowlist
can have a fork pull request accepted as written. This page says what such a
pull request must look like. The rule itself is decision 0017 under
`dev/governance/decisions/`.

If you are not on the allowlist, open an issue instead: a pull request from
any other account is refused by the `pr-contract` check.

## Before you open it

- **Branch name.** Letters, digits, dot, underscore, dash and slash only, at
  most 100 characters, starting with a letter or digit, and not `main`
  (for example `fix/issue-12`). Any other name is refused.
- **Target.** The base is `main` of this repository.
- **One pull request per head.** Do not open a second pull request from the
  same commit; close the old one and push a new commit first.
- **Body.** Use the headings of `.github/PULL_REQUEST_TEMPLATE.md`. Each is
  content or `n/a: <reason>`.
- **Never edit** `VERSION`, the `version` in the integration's
  `manifest.json`, or the `RELEASE_NOTES.md` heading. Versions are assigned
  after the merge.

## What you may change

| Paths | What happens |
|---|---|
| `custom_components/`, `blueprints/`, `README.md`, and `*.md`, `*.png`, `*.svg` under `docs/` (not `docs/site/`) | Accepted on CI and your review alone. |
| Other files under `tests/` and `docs/` (test scripts, `docs/index.html`, `docs/site/`, the figure scripts under `docs/img/`) | Accepted only after the owner, or the project's tooling on his behalf, has read that part of the diff and approved it at your head commit. |
| Everything else: `.github/`, `tools/`, `.claude/`, `dev/governance/`, any `*_budgets.json`, `tests/closures.json`, `tests/golden/`, `tests/mutation_ledger/`, the test runner files, files in the repository root other than `README.md`, and any new top-level directory | Refused. Open an issue; the project's own tooling makes that change. |

A fix normally adds its failing test by editing an existing test script. A fix
that needs a new tracked file outside `docs/`, a changed golden fixture or a
budget edit cannot be accepted as written.

CI runs every lane on every push from a fork; nothing is skipped.

## The review

You may run the reviewer yourself. It follows
`dev/governance/roles/fix-review.md` and publishes two things:

1. One commit on a branch of your fork holding `VERDICT.md` and a directory
   `ev/` with the evidence (plain files, at least one naming the reviewed
   commit; file names use letters, digits, dot, underscore, dash and slash).
2. A comment on the pull request, from your own account, of this shape:

   ```
   Fix review: merge <the 40-character head commit of the pull request>
   review-commit: <the 40-character commit from step 1>
   ```

The first line of `VERDICT.md` must be the first line of the comment, exactly.

After that, do not push again. The project adopts the verdict, merges `main`
into your branch itself when needed (leave "Allow edits by maintainers" on),
and merges the pull request. Any other new commit on the branch voids the
verdict and the review starts over.

## For the owner: approving the owner-read paths yourself

Approve the pull request at its head commit with a review whose body is
exactly this one line:

```
Outside read: <the 40-character head commit>
```

Write nothing else in it. In particular the words "seat", "mandate" and
"orchestrator" make the tooling treat the review as an agent's and refuse it.
A later "request changes" or a dismissal by you withdraws the approval.
