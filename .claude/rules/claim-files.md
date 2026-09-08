---
description: Claim-file conflicts are prevented by the claimnotes merge driver, not repaired after the fact
paths:
  - "tests/golden/**"
---
# The two claim files

Every branch writes a note into `tests/golden/claimed_drift.txt` and
`tests/golden/card_claimed_drift.txt` at the same place, so every branch that
merged `main` after another branch merged conflicted in both — five branches,
ten conflicts, in one session. `.gitattributes` now routes both files to the
`claimnotes` merge driver in `tests/env_drift.py`. Install it once per clone;
a worktree shares its checkout's config, so one install covers every worktree:

```
python3 tests/env_drift.py --install-merge-driver
```

The driver unions the note comments and **refuses** — leaving ordinary conflict
markers and a non-zero exit — when both sides rewrote the bare claim list. The
refusal is the point. A claim is value-bearing, and git's free `merge=union`
would silently reinstate a claim the branch deleted, where the inherited-claims
guard cannot see it: that guard fires only on a list *exactly* equal to the
baseline's, and a unioned list carries the branch's own claim too.

Two limits, both measured. Git never clones config, so an uninstalled driver
falls back to the ordinary text merge — the same conflict as today, never worse.
And git reads `.gitattributes` from the branch being merged **into**, so a branch
cut before it landed conflicts once more before it is covered.

**GitHub is one of those uninstalled clones, and that one is not free (#570).**
`mergeStateStatus` is computed on GitHub's side, where the driver cannot run, so
every open pull request flips to `DIRTY` the moment `main` touches a claim file.
GitHub will not build a merge commit for a `DIRTY` pull request, and the
`pull_request` workflows never fire — such a PR does not go red, it **cannot
run**. A run already in flight survives; no new one queues. Merge `main` locally,
where the driver does run, and push. Before treating any conflict as real,
confirm it:

```
git merge-tree --write-tree origin/main HEAD
```

**So a branch that claims nothing does not touch the claim files at all.** The
note is a convention, not a requirement: `inherited_claims_error` compares the
parsed claim map, an empty list always passes, and no check anywhere reads a
note. A branch that leaves both files byte-identical to `main` cannot conflict,
and inherits whatever `stamp.py` last wrote to `claims-for:` — which is also how
you stop hand-editing that line wrong. Edit these files only when you are
actually claiming drift; there a conflict is meaningful, and rare.

Why no third autofix job repairs this, and what the `claims-autofix` job does
instead, are in `ci-autofix.md`.
