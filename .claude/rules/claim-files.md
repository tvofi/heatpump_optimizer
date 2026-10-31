---
description: Claim-file conflicts are prevented by the claimnotes merge driver, not repaired after the fact
paths:
  - "tests/golden/**"
---
# The two claim files

`tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` take every
branch's note at one place, so `.gitattributes` routes both to the
`claimnotes` merge driver in `tests/env_drift.py`. Install it once per clone:

```
python3 tests/env_drift.py --install-merge-driver
```

It unions the notes and merges claims three-way per scenario: a side's change
or deletion (a `may-drift` line too) wins over the other's silence. It
**refuses**, naming them, where both sides rewrote one scenario's claims or
stamped differing `claims-for:`: `merge=union` would reinstate a deleted claim
the inherited-claims guard misses. Uninstalled, it falls back to the text
merge; git reads `.gitattributes` from the branch merged **into**.

**GitHub is such an uninstalled clone (#570).** Every open pull request turns
`DIRTY` the moment `main` touches a claim file, and a `DIRTY` one does not go
red, it **cannot run**. The merge-main bot (`ci-autofix.md`) merges `main` in
where the drivers can; else merge locally. Confirm a conflict first:

```
git merge-tree --write-tree origin/main HEAD
```

**So a branch that claims nothing does not touch the claim files.** A file
byte-identical to its fork point's claims nothing and cannot conflict; a line
excuses only the diff that wrote it, so `main`'s lines are inert until
`stamp.py` empties them. A may-drift fixture is claimed with its entry
suspended for this release; the stamp owes it back verbatim (R8-P3,
`MAY-DRIFT UNCOVERED`).

**Drift of one direction on a host-dependent fixture set is claimed by its
shape** (#996). Where the solve's basin picks which fixtures move, every name
list goes STALE or UNCLAIMED on some runner. One bare line claims the move:

```
shape: space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'  # why
```

It excuses only leaves on those paths moving from the from-set (`*`: any value
outside the to-set) into the to-set, in any fixture. A line that does not
parse, whose sets meet, or whose path names no key refuses the run; it is stale
on a host where no leaf, may-drift fixtures included, moved in it. So claim
what the change does on every host, never a value leaf.

`ci-autofix.md` says why no autofix job repairs this, and what `claims-autofix` does.
